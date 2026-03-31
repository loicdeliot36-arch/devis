from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import sqlite3
import bcrypt
import jwt
import sys
import os
from pathlib import Path

# Importer les fonctions d'authentification centrales
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import get_user_from_token, create_access_token
from config import SECRET_KEY, ALGORITHM

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Page de profil utilisateur"""
    user = get_user_from_token(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })

@router.post("/profile")
async def update_profile(
    request: Request,
    nom: str = Form(...),
    prenom: str = Form(...),
    date_naissance: str = Form(""),
    telephone: str = Form("")
):
    """Mise à jour du profil utilisateur"""
    user = get_user_from_token(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        import sqlite3
        from pathlib import Path
        
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Mettre à jour les informations
        cursor.execute('''
            UPDATE users 
            SET nom = ?, prenom = ?, date_naissance = ?, telephone = ?
            WHERE id = ?
        ''', (nom, prenom, date_naissance if date_naissance else None, telephone if telephone else None, user["id"]))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/profile?success=1", status_code=303)
        
    except Exception as e:
        print(f"Erreur mise à jour profil: {e}")
        return RedirectResponse(url="/profile?error=1", status_code=303)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Page de connexion principale (interface desktop)"""
    # Vérifier si déjà connecté
    user = get_user_from_token(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse("login_desktop.html", {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Login principal avec redirection vers dashboard desktop"""
    print(f"Tentative de connexion pour: {email}")
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            print("Utilisateur non trouvé")
            return templates.TemplateResponse("login_desktop.html", {
                "request": request,
                "error": "Aucun compte trouvé avec cet email"
            })
        
        if not bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            print("Mot de passe incorrect")
            return templates.TemplateResponse("login_desktop.html", {
                "request": request,
                "error": "Mot de passe incorrect. Veuillez réessayer."
            })
        
        print("Utilisateur authentifié avec succès")
        
        # Créer le token
        token = create_access_token({"sub": email})
        print(f"Token créé: {token[:50]}...")
        
        # Définir le cookie
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=False,  # Pour le debug
            secure=False,  # Mettre True en production avec HTTPS
            samesite="lax",
            max_age=1800,  # 30 minutes
            path="/"  # Ajout du path
        )
        print("Cookie défini avec path=/")
        return response
        
    except Exception as e:
        print(f"Erreur lors de la connexion: {e}")
        return templates.TemplateResponse("login_desktop.html", {
            "request": request,
            "error": f"Erreur technique: {str(e)}"
        })

@router.post("/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...), 
                   nom: str = Form(...), prenom: str = Form(...), telephone: str = Form(None),
                   date_naissance: str = Form(None)):
    """Inscription principale avec redirection vers login desktop"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Vérifier si l'utilisateur existe déjà
    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        return templates.TemplateResponse("register_desktop.html", {
            "request": request,
            "error": "Cet email est déjà utilisé"
        })
    
    # Hasher le mot de passe
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Insérer l'utilisateur
    cursor.execute("""
        INSERT INTO users (email, password_hash, nom, prenom, telephone, date_naissance, role)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (email, password_hash.decode('utf-8'), nom, prenom, telephone, date_naissance, 'user'))
    
    conn.commit()
    conn.close()
    
    return templates.TemplateResponse("login_desktop.html", {
        "request": request,
        "message": "Inscription réussie ! Vous pouvez maintenant vous connecter"
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Page de connexion principale (interface desktop)"""
    return templates.TemplateResponse("login_desktop.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Page d'inscription principale (interface desktop)"""
    return templates.TemplateResponse("register_desktop.html", {"request": request})

@router.get("/logout")
async def logout():
    """Déconnexion"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token", path="/")
    return response
