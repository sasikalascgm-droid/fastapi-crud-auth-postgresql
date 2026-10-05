from pydantic import BaseModel
from typing import Optional


class StudentCreate(BaseModel):
    name: str
    age: int
    year: str


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    year: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str