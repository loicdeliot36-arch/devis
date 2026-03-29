from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    
    class Config:
        from_attributes = True

class ContactCreate(BaseModel):
    nom: str
    email: EmailStr
    telephone: Optional[str] = None
    message: str

class ContactResponse(BaseModel):
    id: int
    nom: str
    email: str
    telephone: Optional[str]
    message: str
    date: str
    traite: bool
    
    class Config:
        from_attributes = True
