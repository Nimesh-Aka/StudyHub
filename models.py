from pydantic import BaseModel, ConfigDict, EmailStr, Field

class Note(BaseModel):
    id: int | None = None
    title: str
    description: str
    date: str

class User(BaseModel):
    name: str
    email: str
    password: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr