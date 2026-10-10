from fastapi import FastAPI
from models import Note

app = FastAPI()

@app.get("/")
def greet():
    return "Hello!!!"

notes =[
    Note(id=1, title="Note 1", description="This is note 1", date="2024-06-01"),
    Note(id=2, title="Note 2", description="This is note 2", date="2024-06-02"),
    Note(id=3, title="Note 3", description="This is note 3", date="2024-06-03"),
    Note(id=4, title="Note 4", description="This is note 4", date="2024-06-04"),
]

@app.get("/notes")
def get_all_notes():
    return notes

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