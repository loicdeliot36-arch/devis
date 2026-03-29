from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import authenticate_user, create_access_token, get_password_hash, get_user_from_token
from models import UserCreate, UserLogin

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Page de connexion"""
    # Vérifier si déjà connecté
    user = get_user_from_token(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Traitement du formulaire de connexion"""
    print(f"Tentative de connexion pour: {email}")
    user = authenticate_user(email, password)
    
    if not user:
        print("Échec d'authentification")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email ou mot de passe incorrect"
        })
    
    print("Utilisateur authentifié avec succès")
    # Créer le token
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=30)
    )
    
    print(f"Token créé: {access_token[:50]}...")
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,  # Pour le debug
        secure=False,  # Mettre True en production avec HTTPS
        samesite="lax",
        max_age=1800,  # 30 minutes
        expires=1800,
        path="/"
    )
    print("Cookie défini avec path=/")
    return response

@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Traitement du formulaire d'inscription"""
    
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Les mots de passe ne correspondent pas"
        })
    
    if len(password) < 6:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Le mot de passe doit contenir au moins 6 caractères"
        })
    
    # Vérifier si l'utilisateur existe déjà
    import sqlite3
    from pathlib import Path
    
    db_path = Path(__file__).parent.parent / "database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Cet email est déjà utilisé"
        })
    
    # Créer le nouvel utilisateur
    password_hash = get_password_hash(password)
    cursor.execute('''
        INSERT INTO users (email, password_hash, role)
        VALUES (?, ?, ?)
    ''', (email, password_hash, 'user'))
    
    conn.commit()
    conn.close()
    
    # Rediriger vers la page de connexion
    return RedirectResponse(url="/login?message=Inscription réussie", status_code=303)

@router.get("/logout")
async def logout():
    """Déconnexion"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token", path="/")
    return response
