from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth import get_user_from_token
import sqlite3
from pathlib import Path
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db_stats():
    """Récupérer les statistiques pour le dashboard"""
    conn = sqlite3.connect(Path(__file__).parent.parent / "database.db")
    cursor = conn.cursor()
    
    # Statistiques des messages
    cursor.execute("SELECT COUNT(*) FROM contact_messages")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE statut = 'traite'")
    treated_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE statut = 'non_traite'")
    pending_messages = cursor.fetchone()[0]
    
    # Taux de traitement
    treatment_rate = round((treated_messages / total_messages * 100) if total_messages > 0 else 0)
    
    # Statistiques utilisateurs
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    # Messages récents
    cursor.execute("""
        SELECT COUNT(*) FROM contact_messages 
        WHERE date_creation >= date('now')
    """)
    today_messages = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM contact_messages 
        WHERE date_creation >= date('now', '-7 days')
    """)
    week_messages = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM contact_messages 
        WHERE date_creation >= date('now', '-30 days')
    """)
    month_messages = cursor.fetchone()[0]
    
    # Dernières synchronisations
    cursor.execute("""
        SELECT COUNT(*) FROM contact_messages 
        WHERE reponse_admin IS NOT NULL 
        AND date_reponse IS NOT NULL
    """)
    synced_count = cursor.fetchone()[0]
    
    # Dernier message
    cursor.execute("""
        SELECT nom, date_creation FROM contact_messages 
        ORDER BY date_creation DESC 
        LIMIT 1
    """)
    last_message = cursor.fetchone()
    last_message_sender = last_message[0] if last_message else "Aucun"
    last_message_date = last_message[1] if last_message else "Aucun"
    
    conn.close()
    
    return {
        'total_messages': total_messages,
        'treated_messages': treated_messages,
        'pending_messages': pending_messages,
        'treatment_rate': treatment_rate,
        'total_users': total_users,
        'today_messages': today_messages,
        'week_messages': week_messages,
        'month_messages': month_messages,
        'synced_count': synced_count,
        'last_message_sender': last_message_sender,
        'last_message_date': last_message_date,
        'last_sync_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'current_date': datetime.now().strftime('%d/%m/%Y'),
        'current_time': datetime.now().strftime('%H:%M')
    }

def get_user_activities(user_email):
    """Récupérer les activités d'un utilisateur"""
    conn = sqlite3.connect(Path(__file__).parent.parent / "database.db")
    cursor = conn.cursor()
    
    # Messages de l'utilisateur
    cursor.execute("""
        SELECT COUNT(*) FROM contact_messages 
        WHERE email = ?
    """, (user_email,))
    user_messages_count = cursor.fetchone()[0]
    
    # Devis de l'utilisateur
    cursor.execute("""
        SELECT COUNT(*) FROM contact_messages 
        WHERE email = ? AND message LIKE '%devis%'
    """, (user_email,))
    user_quotes_count = cursor.fetchone()[0]
    
    # Dernier contact
    cursor.execute("""
        SELECT date_creation FROM contact_messages 
        WHERE email = ? 
        ORDER BY date_creation DESC 
        LIMIT 1
    """, (user_email,))
    last_contact = cursor.fetchone()
    last_contact_date = last_contact[0] if last_contact else None
    
    # Messages détaillés
    cursor.execute("""
        SELECT nom, message, date_creation, statut FROM contact_messages 
        WHERE email = ? 
        ORDER BY date_creation DESC 
        LIMIT 5
    """, (user_email,))
    user_messages = cursor.fetchall()
    
    conn.close()
    
    return {
        'user_messages_count': user_messages_count,
        'user_quotes_count': user_quotes_count,
        'last_contact_date': last_contact_date,
        'user_messages': user_messages
    }

@router.get("/desktop", response_class=HTMLResponse)
async def desktop_home(request: Request):
    """Page d'accueil optimisée pour desktop"""
    user = get_user_from_token(request)
    stats = get_db_stats()
    
    return templates.TemplateResponse("index_desktop.html", {
        "request": request,
        "user": user,
        **stats
    })

@router.get("/desktop/contact", response_class=HTMLResponse)
async def desktop_contact(request: Request):
    """Page de contact optimisée pour desktop"""
    user = get_user_from_token(request)
    
    return templates.TemplateResponse("contact_desktop.html", {
        "request": request,
        "user": user
    })

@router.get("/desktop/profile", response_class=HTMLResponse)
async def desktop_profile(request: Request):
    """Page de profil optimisée pour desktop"""
    user = get_user_from_token(request)
    if not user:
        return templates.TemplateResponse("login_desktop.html", {
            "request": request
        })
    
    # Récupérer les activités de l'utilisateur
    activities = get_user_activities(user['email'])
    
    return templates.TemplateResponse("profile_desktop.html", {
        "request": request,
        "user": user,
        **activities
    })

@router.get("/desktop/dashboard", response_class=HTMLResponse)
async def desktop_dashboard(request: Request):
    """Dashboard optimisé pour desktop"""
    user = get_user_from_token(request)
    if not user:
        return templates.TemplateResponse("login_desktop.html", {
            "request": request
        })
    
    stats = get_db_stats()
    
    if user['role'] == 'admin':
        return templates.TemplateResponse("dashboard_desktop.html", {
            "request": request,
            "user": user,
            **stats
        })
    else:
        # Pour les utilisateurs non-admin
        activities = get_user_activities(user['email'])
        return templates.TemplateResponse("dashboard_desktop.html", {
            "request": request,
            "user": user,
            **stats,
            **activities
        })

@router.post("/desktop/profile")
async def desktop_update_profile(request: Request):
    """Mise à jour du profil pour desktop"""
    user = get_user_from_token(request)
    if not user:
        return {"error": "Non authentifié"}
    
    try:
        form_data = await request.form()
        
        conn = sqlite3.connect(Path(__file__).parent.parent / "database.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET nom = ?, prenom = ?, telephone = ?, date_naissance = ?
            WHERE email = ?
        """, (
            form_data.get('nom'),
            form_data.get('prenom'),
            form_data.get('telephone'),
            form_data.get('date_naissance'),
            user['email']
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Profil mis à jour avec succès"}
        
    except Exception as e:
        return {"error": f"Erreur lors de la mise à jour: {str(e)}"}

@router.post("/desktop/profile/change-password")
async def desktop_change_password(request: Request):
    """Changement de mot de passe pour desktop"""
    user = get_user_from_token(request)
    if not user:
        return {"error": "Non authentifié"}
    
    try:
        form_data = await request.form()
        
        current_password = form_data.get('current_password')
        new_password = form_data.get('new_password')
        confirm_password = form_data.get('confirm_password')
        
        if new_password != confirm_password:
            return {"error": "Les mots de passe ne correspondent pas"}
        
        if len(new_password) < 8:
            return {"error": "Le mot de passe doit contenir au moins 8 caractères"}
        
        # Vérifier le mot de passe actuel
        import bcrypt
        conn = sqlite3.connect(Path(__file__).parent.parent / "database.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (user['email'],))
        result = cursor.fetchone()
        
        if not result or not bcrypt.checkpw(current_password.encode('utf-8'), result[0].encode('utf-8')):
            conn.close()
            return {"error": "Mot de passe actuel incorrect"}
        
        # Mettre à jour le mot de passe
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash.decode('utf-8'), user['email']))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Mot de passe changé avec succès"}
        
    except Exception as e:
        return {"error": f"Erreur lors du changement: {str(e)}"}

@router.get("/desktop/login", response_class=HTMLResponse)
async def desktop_login(request: Request):
    """Page de connexion optimisée pour desktop"""
    return templates.TemplateResponse("login_desktop.html", {
        "request": request
    })

@router.post("/desktop/login")
async def desktop_login_post(request: Request):
    """Traitement du formulaire de connexion desktop"""
    try:
        form_data = await request.form()
        email = form_data.get('email')
        password = form_data.get('password')
        
        if not email or not password:
            return templates.TemplateResponse("login_desktop.html", {
                "request": request,
                "error": "Email et mot de passe requis"
            })
        
        # Authentification (utiliser la logique existante)
        from auth import authenticate_user, create_access_token
        user = authenticate_user(email, password)
        
        if not user:
            return templates.TemplateResponse("login_desktop.html", {
                "request": request,
                "error": "Email ou mot de passe incorrect"
            })
        
        # Créer le token et rediriger
        access_token = create_access_token(data={"sub": user["email"]})
        
        response = RedirectResponse(url="/desktop", status_code=303)
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=1800,  # 30 minutes
            expires=1800,
            path="/",
            samesite="lax",
            httponly=True
        )
        
        print(f"Utilisateur connecté: {user['email']} (rôle: {user['role']})")
        return response
        
    except Exception as e:
        print(f"Erreur connexion desktop: {e}")
        return templates.TemplateResponse("login_desktop.html", {
            "request": request,
            "error": f"Erreur de connexion: {str(e)}"
        })

@router.get("/desktop/register", response_class=HTMLResponse)
async def desktop_register(request: Request):
    """Page d'inscription optimisée pour desktop"""
    return templates.TemplateResponse("register_desktop.html", {
        "request": request
    })

@router.post("/desktop/register")
async def desktop_register_post(request: Request):
    """Traitement du formulaire d'inscription desktop"""
    try:
        form_data = await request.form()
        email = form_data.get('email')
        password = form_data.get('password')
        nom = form_data.get('nom', '')
        prenom = form_data.get('prenom', '')
        
        if not email or not password:
            return templates.TemplateResponse("register_desktop.html", {
                "request": request,
                "error": "Email et mot de passe requis"
            })
        
        # Vérifier si l'utilisateur existe déjà
        import sqlite3
        from pathlib import Path
        from auth import get_password_hash
        
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return templates.TemplateResponse("register_desktop.html", {
                "request": request,
                "error": "Cet email est déjà utilisé"
            })
        
        # Créer l'utilisateur
        hashed_password = get_password_hash(password)
        cursor.execute("""
            INSERT INTO users (email, password_hash, role, nom, prenom, date_creation)
            VALUES (?, ?, 'user', ?, ?, ?)
        """, (email, hashed_password, nom, prenom, datetime.now().isoformat()))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"Utilisateur créé: {email} (ID: {user_id})")
        
        # Rediriger vers la page de connexion
        return templates.TemplateResponse("login_desktop.html", {
            "request": request,
            "success": "Compte créé avec succès. Vous pouvez maintenant vous connecter."
        })
        
    except Exception as e:
        print(f"Erreur inscription desktop: {e}")
        return templates.TemplateResponse("register_desktop.html", {
            "request": request,
            "error": f"Erreur lors de l'inscription: {str(e)}"
        })
