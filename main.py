from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Note, User
from database import session, engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://studyhub-frontend-7fp6.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def get_note_by_id(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(database_models.Note).filter(database_models.Note.id == note_id).first()
    if db_note:
        return db_note
    return {"error": "Note not found"}

@app.post("/notes")
def create_note(note: Note, db: Session = Depends(get_db)):
    note_data = note.model_dump(exclude={"id"})
    db_note = database_models.Note(**note_data) # Create a new Note instance
    db.add(db_note) # Add the new note to the database session
    db.commit() # Commit the changes to the database
    db.refresh(db_note)
    return db_note # Return the newly created note

@app.put("/notes/{note_id}")
def update_note(note_id: int, updated_note: Note, db: Session = Depends(get_db)):
    db_note = db.query(database_models.Note).filter(database_models.Note.id == note_id).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db_note.title = updated_note.title
    db_note.description = updated_note.description
    db_note.date = updated_note.date

    db.commit()
    db.refresh(db_note)

    return db_note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(database_models.Note).filter(database_models.Note.id == note_id).first()

    if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")

    db.delete(db_note)
    db.commit()

    return {"message": "Note deleted successfully"}

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