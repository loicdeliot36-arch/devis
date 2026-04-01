from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import random
import string

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

class ResetRequest(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    token: str
    new_password: str

def generate_reset_code():
    """Générer un code de réinitialisation à 6 chiffres"""
    return ''.join(random.choices(string.digits, k=6))

def is_token_valid(token_data):
    """Vérifier si un token est valide et non expiré"""
    if not token_data:
        return False
    if token_data.get('used', False):
        return False
    if datetime.utcnow() > token_data.get('expires_at'):
        return False
    return True

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
