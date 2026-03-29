from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import sys
import os
from pathlib import Path
import bcrypt

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Page d'inscription publique"""
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_user(
    request: Request,
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Inscription d'un nouvel utilisateur"""
    try:
        # Vérifier que les mots de passe correspondent
        if password != confirm_password:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Les mots de passe ne correspondent pas"
            })
        
        # Vérifier la longueur du mot de passe
        if len(password) < 6:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Le mot de passe doit contenir au moins 6 caractères"
            })
        
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si l'email existe déjà
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Cet email est déjà utilisé"
            })
        
        # Créer le nouvel utilisateur (toujours en tant que 'user')
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute('''
            INSERT INTO users (email, password_hash, role, nom, prenom)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, password_hash, 'user', nom, prenom))
        
        conn.commit()
        conn.close()
        
        return templates.TemplateResponse("register_success.html", {
            "request": request,
            "email": email
        })
        
    except Exception as e:
        print(f"Erreur inscription: {e}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Une erreur est survenue lors de l'inscription"
        })
