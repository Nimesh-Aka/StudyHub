
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database_models
from main import app, get_db


# Create an isolated in-memory test database
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_function():
    """Give each test a fresh database."""
    database_models.Base.metadata.drop_all(bind=test_engine)
    database_models.Base.metadata.create_all(bind=test_engine)


def create_user_and_token(name="Test User", email="test@example.com"):
    """Register a user and obtain an access token."""
    password = "TestPassword123!"

    register_response = client.post(
        "/users",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code in (200, 201)

    user = register_response.json()

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    return user, headers


def make_note(title="Test Note", description="Test description"):
    return {
        "title": title,
        "description": description,
        "date": "2026-10-19",
    }


def test_homepage():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == "Hello!!!"


def test_registration_and_login():
    user, headers = create_user_and_token()

    assert user["id"] is not None
    assert user["email"] == "test@example.com"

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == user["id"]
    assert response.json()["email"] == user["email"]


def test_notes_require_authentication():
    """Requests without a token must be rejected."""
    responses = [
        client.get("/notes"),
        client.get("/notes/1"),
        client.post("/notes", json=make_note()),
        client.put("/notes/1", json=make_note()),
        client.delete("/notes/1"),
    ]

    for response in responses:
        assert response.status_code == 401


def test_get_all_notes_initially_empty():
    _, headers = create_user_and_token()

    response = client.get("/notes", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_note():
    _, headers = create_user_and_token()

    create_response = client.post(
        "/notes",
        json=make_note(
            title="CI Test Note",
            description="Testing the authenticated StudyHub API",
        ),
        headers=headers,
    )

    assert create_response.status_code == 200

    created_note = create_response.json()

    assert created_note["title"] == "CI Test Note"
    assert created_note["description"] == (
        "Testing the authenticated StudyHub API"
    )
    assert created_note["id"] is not None

    get_response = client.get(
        f"/notes/{created_note['id']}",
        headers=headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "CI Test Note"


def test_update_note():
    _, headers = create_user_and_token()

    created_response = client.post(
        "/notes",
        json=make_note("Original Note", "Original description"),
        headers=headers,
    )

    assert created_response.status_code == 200
    note_id = created_response.json()["id"]

    updated_data = make_note(
        "Updated Note",
        "Updated description",
    )

    response = client.put(
        f"/notes/{note_id}",
        json=updated_data,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Note"
    assert response.json()["description"] == "Updated description"


def test_delete_note():
    _, headers = create_user_and_token()

    created_response = client.post(
        "/notes",
        json=make_note("Note to delete", "Temporary note"),
        headers=headers,
    )

    assert created_response.status_code == 200
    note_id = created_response.json()["id"]

    response = client.delete(
        f"/notes/{note_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Note deleted successfully"

    get_response = client.get(
        f"/notes/{note_id}",
        headers=headers,
    )

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Note not found"}


def test_users_cannot_access_each_others_notes():
    """A user must not read, update, or delete another user's note."""
    _, user_a_headers = create_user_and_token(
        name="User A",
        email="usera@example.com",
    )

    _, user_b_headers = create_user_and_token(
        name="User B",
        email="userb@example.com",
    )

    create_response = client.post(
        "/notes",
        json=make_note("User A private note", "Private description"),
        headers=user_a_headers,
    )

    assert create_response.status_code == 200
    note_id = create_response.json()["id"]

    # User B cannot read User A's note.
    response = client.get(
        f"/notes/{note_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 404

    # User B cannot update User A's note.
    response = client.put(
        f"/notes/{note_id}",
        json=make_note("Unauthorized update", "Should not be saved"),
        headers=user_b_headers,
    )
    assert response.status_code == 404

    # User B cannot delete User A's note.
    response = client.delete(
        f"/notes/{note_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 404

    # User A's note remains unchanged.
    response = client.get(
        f"/notes/{note_id}",
        headers=user_a_headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "User A private note"


def test_users_only_see_their_own_notes():
    _, user_a_headers = create_user_and_token(
        name="User A",
        email="usera@example.com",
    )

    _, user_b_headers = create_user_and_token(
        name="User B",
        email="userb@example.com",
    )

    client.post(
        "/notes",
        json=make_note("User A note", "Belongs to A"),
        headers=user_a_headers,
    )

    client.post(
        "/notes",
        json=make_note("User B note", "Belongs to B"),
        headers=user_b_headers,
    )

    user_a_response = client.get("/notes", headers=user_a_headers)
    user_b_response = client.get("/notes", headers=user_b_headers)

    assert user_a_response.status_code == 200
    assert user_b_response.status_code == 200

    assert len(user_a_response.json()) == 1
    assert user_a_response.json()[0]["title"] == "User A note"

    assert len(user_b_response.json()) == 1
    assert user_b_response.json()[0]["title"] == "User B note"
