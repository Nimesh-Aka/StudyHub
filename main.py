from fastapi import Depends, FastAPI
from models import Note
from database import session, engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def greet():
    return "Hello!!!"

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
    count = db.query(database_models.Note).count()
    if count == 0:
        for note in notes:
            db.add(database_models.Note(**note.model_dump()))
        db.commit()

init_db()

@app.get("/notes")
def get_all_notes(db: Session = Depends(get_db)):
    db_notes = db.query(database_models.Note).all()
    return db_notes

@app.get("/notes/{note_id}")
def get_note_by_id(note_id: int):
    for note in notes:
        if note.id == note_id:
            return note
    return {"error": "Note not found"}

@app.post("/notes")
def create_note(note: Note):
    notes.append(note)
    return note 

@app.put("/notes/{note_id}")
def update_note(note_id: int, updated_note: Note):
    for index, note in enumerate(notes):
        if note.id == note_id:
            notes[index] = updated_note
            return updated_note
    return {"error": "Note not found"}

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    for index, note in enumerate(notes):
        if note.id == note_id:
            deleted_note = notes.pop(index)
            return deleted_note
    return {"error": "Note not found"}