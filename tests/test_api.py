
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database_models
from sqlalchemy.orm import Session


# Create a separate in-memory test database
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


app = FastAPI()


@app.get("/")
def greet():
    return "Hello!!!"


@app.get("/notes")
def get_all_notes(db: Session = Depends(override_get_db)):
    return db.query(database_models.Note).all()


client = TestClient(app)


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Hello!!!"


def test_get_all_notes_initially_empty():
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []
