from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_utils import get_email_service

router = APIRouter()

class ContactForm(BaseModel):
    nom: str
    prenom: str
    telephone: str
    email: EmailStr
    message: str

class QuoteForm(BaseModel):
    nom: str
    prenom: str
    telephone: str
    email: EmailStr
    message: str

@router.post("/api/contact")
async def api_contact(form_data: ContactForm):
    """API endpoint pour le formulaire de contact (compatibilité frontend)"""
    try:
        # Enregistrer dans la base de données
        db_path = Path(__file__).parent.parent / "database.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Combiner nom et prénom pour le nom complet
        nom_complet = f"{form_data.nom} {form_data.prenom}"
        
        cursor.execute('''
            INSERT INTO contact_messages (nom, email, telephone, message, date_creation, statut)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nom_complet, form_data.email, form_data.telephone, form_data.message, datetime.now().isoformat(), "non_traite"))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Envoyer l'email à l'admin
        email_service = get_email_service()
        email_sent = email_service.send_contact_notification(
            nom_complet, 
            form_data.email, 
            form_data.telephone, 
            form_data.message
        )
        
        return {
            "success": True,
            "message": "Message envoyé avec succès",
            "email_sent": email_sent,
            "message_id": message_id
        }
        
    except Exception as e:
        print(f"Erreur API contact: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi du message")

@router.post("/api/quote")
async def api_quote(form_data: QuoteForm):
    """API endpoint pour le formulaire de devis (compatibilité frontend)"""
    try:
        # Enregistrer dans la base de données
        db_path = Path(__file__).parent.parent / "database.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Combiner nom et prénom pour le nom complet
        nom_complet = f"{form_data.nom} {form_data.prenom}"
        
        cursor.execute('''
            INSERT INTO contact_messages (nom, email, telephone, message, date_creation, statut)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nom_complet, form_data.email, form_data.telephone, f"Demande de devis: {form_data.message}", datetime.now().isoformat(), "non_traite"))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Envoyer l'email à l'admin
        email_service = get_email_service()
        email_sent = email_service.send_contact_notification(
            nom_complet, 
            form_data.email, 
            form_data.telephone, 
            f"Demande de devis: {form_data.message}"
        )
        
        return {
            "success": True,
            "message": "Demande de devis envoyée avec succès",
            "email_sent": email_sent,
            "message_id": message_id
        }
        
    except Exception as e:
        print(f"Erreur API quote: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de la demande de devis")
