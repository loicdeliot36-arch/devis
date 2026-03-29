from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_user_from_token

def require_admin(user_dict):
    """Vérifie si l'utilisateur est admin"""
    if not user_dict or user_dict.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_dict

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Tableau de bord utilisateur"""
    user = get_user_from_token(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    print("=== DASHBOARD ===")
    print(f"Utilisateur dans dashboard: {user}")
    print(f"Cookies dans dashboard: {dict(request.cookies)}")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user
    })

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Espace d'administration"""
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    # Récupérer tous les messages de contact
    db_path = Path(__file__).parent.parent / "database.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM contacts 
        ORDER BY date DESC
    ''')
    contacts = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "contacts": contacts
    })

@router.post("/admin/mark-treated/{contact_id}")
async def mark_treated(contact_id: int, request: Request):
    """Marquer un message comme traité"""
    try:
        user = get_user_from_token(request)
        if not user or user.get("role") != "admin":
            return RedirectResponse(url="/login", status_code=303)
        
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Mettre à jour dans la NOUVELLE table
        cursor.execute('''
            UPDATE contact_messages 
            SET statut = 'traite' 
            WHERE id = ?
        ''', (contact_id,))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/admin/messages", status_code=303)
    except Exception as e:
        print(f"Erreur dans mark-treated: {e}")
        return RedirectResponse(url="/admin/messages", status_code=303)

@router.post("/admin/delete/{contact_id}")
async def delete_contact(contact_id: int, request: Request):
    """Supprimer un message"""
    try:
        user = get_user_from_token(request)
        if not user or user.get("role") != "admin":
            return RedirectResponse(url="/login", status_code=303)
        
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Supprimer de la NOUVELLE table
        cursor.execute('''
            DELETE FROM contact_messages 
            WHERE id = ?
        ''', (contact_id,))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/admin/messages", status_code=303)
    except Exception as e:
        print(f"Erreur dans delete: {e}")
        return RedirectResponse(url="/admin/messages", status_code=303)
