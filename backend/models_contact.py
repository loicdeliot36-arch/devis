from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ContactMessageCreate(BaseModel):
    nom: str
    email: EmailStr
    telephone: str
    message: str

class ContactMessageResponse(BaseModel):
    id: int
    nom: str
    email: EmailStr
    telephone: str
    message: str
    date_creation: str
    statut: str
    reponse_admin: Optional[str] = None
    date_reponse: Optional[str] = None

class AdminResponse(BaseModel):
    reponse: str
