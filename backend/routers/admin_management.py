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

from auth import get_user_from_token
from email_sync import sync_email_responses

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    """Gestion des utilisateurs administrateurs"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    # Récupérer tous les utilisateurs
    db_path = Path(__file__).parent.parent / "database.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users ORDER BY email')
    users = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "user": user,
        "users": users
    })

@router.post("/admin/users/add")
async def add_admin_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    nom: str = Form(...),
    prenom: str = Form(...)
):
    """Ajouter un nouvel utilisateur"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si l'email existe déjà
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return RedirectResponse(url="/admin/users?error=email_exists", status_code=303)
        
        # Créer le nouvel utilisateur
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute('''
            INSERT INTO users (email, password_hash, role, nom, prenom)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, password_hash, role, nom, prenom))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/admin/users?success=1", status_code=303)
        
    except Exception as e:
        print(f"Erreur ajout utilisateur: {e}")
        return RedirectResponse(url="/admin/users?error=1", status_code=303)

@router.post("/admin/users/{user_id}/delete")
async def delete_user(request: Request, user_id: int):
    """Supprimer un utilisateur"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        # Empêcher la suppression de soi-même
        if user_id == user["id"]:
            return RedirectResponse(url="/admin/users?error=cant_delete_self", status_code=303)
        
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/admin/users?deleted=1", status_code=303)
        
    except Exception as e:
        print(f"Erreur suppression utilisateur: {e}")
        return RedirectResponse(url="/admin/users?error=1", status_code=303)

@router.post("/admin/users/{user_id}/toggle-role")
async def toggle_user_role(request: Request, user_id: int):
    """Changer le rôle d'un utilisateur"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        # Empêcher la modification de son propre rôle
        if user_id == user["id"]:
            return RedirectResponse(url="/admin/users?error=cant_change_own_role", status_code=303)
        
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer le rôle actuel
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return RedirectResponse(url="/admin/users?error=user_not_found", status_code=303)
        
        current_role = result["role"]
        new_role = "user" if current_role == "admin" else "admin"
        
        # Mettre à jour le rôle
        cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/admin/users?role_changed=1", status_code=303)
        
    except Exception as e:
        print(f"Erreur changement rôle: {e}")
        return RedirectResponse(url="/admin/users?error=1", status_code=303)

@router.get("/admin/sync", response_class=HTMLResponse)
async def admin_sync(request: Request):
    """Page de synchronisation des emails"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("admin_sync.html", {
        "request": request,
        "user": user,
        "sync_status": "inactive",
        "last_sync": "Jamais",
        "synced_count": "0"
    })

@router.post("/admin/sync/manual")
async def manual_sync(request: Request):
    """Synchronisation manuelle des emails"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        print("🔄 Lancement synchronisation manuelle...")
        success = sync_email_responses()
        
        if success:
            return RedirectResponse(url="/admin/sync?success=1", status_code=303)
        else:
            return RedirectResponse(url="/admin/sync?error=1", status_code=303)
            
    except Exception as e:
        print(f"Erreur synchronisation manuelle: {e}")
        return RedirectResponse(url="/admin/sync?error=1", status_code=303)

@router.post("/webhook/gmail-sync")
async def gmail_webhook(request: Request):
    """Webhook pour synchronisation Gmail (optionnel)"""
    try:
        # Vérifier si c'est bien une requête de Gmail
        body = await request.body()
        
        print("📧 Webhook Gmail reçu")
        
        # Lancer la synchronisation
        success = sync_email_responses()
        
        if success:
            return {"status": "success", "message": "Synchronisation effectuée"}
        else:
            return {"status": "error", "message": "Erreur synchronisation"}
            
    except Exception as e:
        print(f"Erreur webhook: {e}")
        return {"status": "error", "message": str(e)}
