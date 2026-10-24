from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Note, User
from database import session, engine
import database_models
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from datetime import datetime 
import logging
import os
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    send_default_pii=False,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/sentry-debug")
async def sentry_debug():
    division_by_zero = 1 / 0
    return {"result": division_by_zero}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://studyhub-frontend-docker.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def greet():
    return "Hello!!!"

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "ok"}

notes =[
    Note(id=1, title="Note 1", description="This is note 1", date="2024-06-01"),
    Note(id=2, title="Note 2", description="This is note 2", date="2024-06-02"),
    Note(id=3, title="Note 3", description="This is note 3", date="2024-06-03"),
    Note(id=4, title="Note 4", description="This is note 4", date="2024-06-04"),
]

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = session()
    try:
        count = db.query(database_models.Note).count()

        if count == 0:
            for note in notes:
                db.add(
                    database_models.Note(
                        id=note.id,
                        title=note.title,
                        description=note.description,
                        date=note.date,
                    )
                )
            db.commit()
    finally:
        db.close()


def initialize_database():
    database_models.Base.metadata.create_all(bind=engine)
    init_db()


@app.get("/notes")
def get_all_notes(db: Session = Depends(get_db)):
    db_notes = db.query(database_models.Note).all()
    return db_notes
 
@app.get("/notes/{note_id}")
def get_note_by_id(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(database_models.Note).filter(
        database_models.Note.id == note_id
    ).first()

    if not db_note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return db_note


@app.post("/notes")
def create_note(note: Note, db: Session = Depends(get_db)):
    try:
        note_data = note.model_dump(exclude={"id"})
        note_data["date"] = datetime.fromisoformat(note.date)

        db_note = database_models.Note(**note_data)
        db.add(db_note)
        db.commit()
        db.refresh(db_note)

        logger.info("Note created successfully. Note ID: %s", db_note.id)
        return db_note

    except Exception:
        db.rollback()
        logger.exception("Failed to create note")
        raise



@app.put("/notes/{note_id}")
def update_note(
    note_id: int,
    updated_note: Note,
    db: Session = Depends(get_db)
):
    try:
        db_note = db.query(database_models.Note).filter(
            database_models.Note.id == note_id
        ).first()

        if not db_note:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )

        db_note.title = updated_note.title
        db_note.description = updated_note.description
        db_note.date = datetime.fromisoformat(updated_note.date)

        db.commit()
        db.refresh(db_note)

        logger.info("Note updated successfully. Note ID: %s", note_id)
        return db_note

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        logger.exception("Failed to update note. Note ID: %s", note_id)
        raise


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    try:
        db_note = db.query(database_models.Note).filter(
            database_models.Note.id == note_id
        ).first()

        if not db_note:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )

        db.delete(db_note)
        db.commit()

        logger.info("Note deleted successfully. Note ID: %s", note_id)
        return {"message": "Note deleted successfully"}

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        logger.exception("Failed to delete note. Note ID: %s", note_id)
        raise


@app.get("/users")
def get_all_users(db: Session = Depends(get_db)):
        db_users = db.query(database_models.User).all()
        return db_users

@app.post("/users")
def create_user(user: User, db: Session = Depends(get_db)):
    db_user = database_models.User(**user.model_dump()) # Create a new User instance
    db.add(db_user) # Add the new user to the database session
    db.commit() # Commit the changes to the database
    db.refresh(db_user)
    return db_user # Return the newly created user

@app.get("/users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(database_models.User).filter(database_models.User.id == user_id).first()
    if db_user:
        return db_user
    return {"error": "User not found"}

@app.put("/users/{user_id}")
def update_user(user_id: int, updated_user: User, db: Session = Depends(get_db)):
    db_user = db.query(database_models.User).filter(database_models.User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.name = updated_user.name
    db_user.email = updated_user.email
    db_user.password = updated_user.password

    db.commit()
    db.refresh(db_user)

    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(database_models.User).filter(database_models.User.id == user_id).first()

    if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()

    return {"message": "User deleted successfully"} 