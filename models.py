from pydantic import BaseModel

class Note(BaseModel):
    id: int | None = None
    title: str
    description: str
    date: str

class User(BaseModel):
    name: str
    email: str
    password: str