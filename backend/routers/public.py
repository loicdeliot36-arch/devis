from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import sqlite3
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Page d'accueil"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Page de contact (existe déjà)"""
    return templates.TemplateResponse("contact.html", {"request": request})

@router.post("/api/contact")
async def contact_form(
    nom: str = Form(...),
    email: str = Form(...),
    telephone: str = Form(...),
    message: str = Form(...)
):
    """Traitement du formulaire de contact"""
    try:
        # Sauvegarder en base de données
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contact_messages (nom, email, telephone, message, date_creation, statut)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nom, email, telephone, message, datetime.now().isoformat(), "non_traite"))
        
        conn.commit()
        conn.close()
        
        # Envoyer l'email avec notre système SMTP
        from email_utils import get_email_service
        email_service = get_email_service()
        email_sent = email_service.send_contact_notification(nom, email, telephone, message)
        
        print(f"Email envoye via SMTP: {email_sent}")
        
        return {"success": True, "message": "Message envoyé avec succès!"}
            
    except Exception as e:
        print("Erreur contact:", e)
        raise HTTPException(status_code=500, detail="Erreur lors du traitement du formulaire")

@router.post("/api/quote")
async def quote_form(
    nom: str = Form(...),
    email: str = Form(...),
    telephone: str = Form(...),
    message: str = Form(...)
):
    """Traitement du formulaire de devis"""
    try:
        # Sauvegarder en base de données
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contacts (nom, email, telephone, message, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (nom, email, telephone, f"DEMANDE DE DEVIS: {message}", datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Envoyer l'email
        from dotenv import load_dotenv
        import resend
        import os
        
        load_dotenv()
        RESEND_API_KEY = os.getenv("RESEND_API_KEY")
        RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
        
        if RESEND_API_KEY and RECIPIENT_EMAIL:
            resend.api_key = RESEND_API_KEY
            
            html_body = f"""
            <html>
                <body>
                    <h2>Nouvelle demande de devis - {nom}</h2>
                    <p><strong>Email :</strong> {email}</p>
                    <p><strong>Téléphone :</strong> {telephone}</p>
                    <hr>
                    <p><strong>Description du projet :</strong></p>
                    <p>{message.replace(chr(10), '<br>')}</p>
                </body>
            </html>
            """
            
            params = {
                "from": "RD Ménage <onboarding@resend.dev>",
                "to": [RECIPIENT_EMAIL],
                "subject": f"Demande de devis - {nom}",
                "html": html_body,
            }
            
            try:
                resend.Emails.send(params)
            except Exception as e:
                print("Erreur email:", e)
        
        return {"success": True, "message": "Demande de devis envoyée!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
