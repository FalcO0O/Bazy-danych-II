from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str #hash

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr

class UserDB(BaseModel):
    id: str
    name: str
    email: EmailStr
    password_hash: str
    refresh_tokens: List[str] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str