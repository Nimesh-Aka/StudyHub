from datetime import datetime

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

database_models.Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_function():
    database_models.Base.metadata.drop_all(bind=test_engine)
    database_models.Base.metadata.create_all(bind=test_engine)


def test_homepage():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == "Hello!!!"


def test_get_all_notes_initially_empty():
    response = client.get("/notes")

    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_note():
    note_data = {
        "title": "CI Test Note",
        "description": "Testing the real StudyHub API",
        "date": "2026-10-19",
    }

    create_response = client.post("/notes", json=note_data)

    assert create_response.status_code == 200
    created_note = create_response.json()
    assert created_note["title"] == note_data["title"]
    assert created_note["description"] == note_data["description"]
    assert created_note["id"] is not None

    get_response = client.get(f"/notes/{created_note['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == note_data["title"]


def test_update_note():
    note_data = {
        "title": "Original Note",
        "description": "Original description",
        "date": "2026-10-19",
    }

    created = client.post("/notes", json=note_data).json()

    updated_data = {
        "title": "Updated Note",
        "description": "Updated description",
        "date": "2026-10-20",
    }

    response = client.put(
        f"/notes/{created['id']}",
        json=updated_data,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Note"
    assert response.json()["description"] == "Updated description"


def test_delete_note():
    note_data = {
        "title": "Note to delete",
        "description": "Temporary note",
        "date": "2026-10-19",
    }

    created = client.post("/notes", json=note_data).json()

    response = client.delete(f"/notes/{created['id']}")

    assert response.status_code == 200
    assert response.json()["message"] == "Note deleted successfully"

    get_response = client.get(f"/notes/{created['id']}")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Note not found"}
