from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_user_from_token
from email_utils import get_email_service
from models_contact import ContactMessageCreate, ContactMessageResponse, AdminResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Page de contact"""
    user = get_user_from_token(request)
    
    return templates.TemplateResponse("contact_new.html", {
        "request": request,
        "user": user
    })

@router.post("/contact")
async def submit_contact(
    request: Request,
    nom: str = Form(...),
    email: str = Form(...),
    telephone: str = Form(...),
    message: str = Form(...)
):
    """Soumettre un message de contact"""
    try:
        # Enregistrer dans la base de données (nouvelle table)
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contact_messages (nom, email, telephone, message, date_creation, statut)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nom, email, telephone, message, datetime.now().isoformat(), "non_traite"))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Envoyer l'email à l'admin
        email_service = get_email_service()
        email_sent = email_service.send_contact_notification(nom, email, telephone, message)
        
        # Afficher la page de confirmation
        return templates.TemplateResponse("contact_confirmation.html", {
            "request": request,
            "success": True,
            "email_sent": email_sent,
            "message": "Votre message a été envoyé avec succès!"
        })
        
    except Exception as e:
        print(f"Erreur soumission contact: {e}")
        return templates.TemplateResponse("contact_new.html", {
            "request": request,
            "error": "Une erreur est survenue. Veuillez réessayer."
        })

@router.get("/admin/messages", response_class=HTMLResponse)
async def admin_messages(request: Request):
    """Liste des messages pour l'admin"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    # Récupérer seulement les messages de la nouvelle table
    db_path = Path(__file__).parent.parent / "database.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM contact_messages 
        ORDER BY date_creation DESC
    ''')
    messages = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("admin_messages.html", {
        "request": request,
        "user": user,
        "messages": messages
    })

@router.get("/admin/messages/{message_id}", response_class=HTMLResponse)
async def admin_message_detail(request: Request, message_id: int):
    """Détail d'un message pour l'admin"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    # Récupérer le message
    db_path = Path(__file__).parent.parent / "database.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM contact_messages WHERE id = ?', (message_id,))
    message = cursor.fetchone()
    conn.close()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    
    return templates.TemplateResponse("admin_message_detail.html", {
        "request": request,
        "user": user,
        "message": dict(message)
    })

@router.post("/admin/messages/{message_id}/respond")
async def admin_respond_message(
    request: Request,
    message_id: int,
    reponse: str = Form(...)
):
    """Répondre à un message"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        # Récupérer le message
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM contact_messages WHERE id = ?', (message_id,))
        message = cursor.fetchone()
        
        if not message:
            conn.close()
            raise HTTPException(status_code=404, detail="Message non trouvé")
        
        # Mettre à jour avec la réponse
        cursor.execute('''
            UPDATE contact_messages 
            SET reponse_admin = ?, date_reponse = ?, statut = ?
            WHERE id = ?
        ''', (reponse, datetime.now().isoformat(), "traite", message_id))
        
        conn.commit()
        conn.close()
        
        # Envoyer l'email au client
        email_service = get_email_service()
        success = email_service.send_response_to_client(
            message["email"], 
            message["nom"], 
            reponse
        )
        
        return RedirectResponse(url="/admin/messages?success=1", status_code=303)
        
    except Exception as e:
        print(f"Erreur réponse message: {e}")
        return templates.TemplateResponse("admin_message_detail.html", {
            "request": request,
            "user": user,
            "message": dict(message),
            "error": "Une erreur est survenue lors de l'envoi de la réponse."
        })

@router.post("/admin/messages/{message_id}/delete")
async def admin_delete_message(request: Request, message_id: int):
    """Supprimer un message"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM contact_messages WHERE id = ?', (message_id,))
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/admin/messages?deleted=1", status_code=303)
        
    except Exception as e:
        print(f"Erreur suppression message: {e}")
        return RedirectResponse(url="/admin/messages?error=1", status_code=303)
