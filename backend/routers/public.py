from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import sqlite3
import sys
import os
import jwt
from pathlib import Path

# Importer les fonctions d'authentification
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import get_user_from_token, create_access_token
from config import SECRET_KEY, ALGORITHM

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db_stats():
    """Récupérer les statistiques pour le dashboard"""
    conn = sqlite3.connect('database.db')
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
    conn = sqlite3.connect('database.db')
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

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Page d'accueil principale (interface desktop)"""
    print("=== HOME ACCESS ===")
    print(f"Cookies reçus: {dict(request.cookies)}")
    
    user = get_user_from_token(request)
    print(f"Utilisateur: {user}")
    
    stats = get_db_stats()
    
    return templates.TemplateResponse("index_desktop.html", {
        "request": request,
        "user": user,
        **stats
    })

@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    """Page de contact principale (interface desktop)"""
    user = get_user_from_token(request)
    
    return templates.TemplateResponse("contact_desktop.html", {
        "request": request,
        "user": user
    })

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    """Page de profil principale (interface desktop)"""
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

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal (interface desktop)"""
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

@router.post("/profile")
async def update_profile(request: Request):
    """Mise à jour du profil principal (interface desktop)"""
    user = get_user_from_token(request)
    if not user:
        return {"error": "Non authentifié"}
    
    try:
        form_data = await request.form()
        
        conn = sqlite3.connect('database.db')
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

# Configuration
SECRET_KEY = "votre_cle_secrete_tres_securisee_2024"

def get_user_from_token(request: Request):
    """Récupérer l'utilisateur depuis le token"""
    token = request.cookies.get("access_token")
    if not token:
        print("Aucun token trouvé dans les cookies")
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            print("Email non trouvé dans le token")
            return None
        
        # Récupérer l'utilisateur depuis la base de données
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, nom, prenom, role FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            user_dict = {
                "id": user[0],
                "email": user[1], 
                "nom": user[2],
                "prenom": user[3],
                "role": user[4]
            }
            print(f"Utilisateur trouvé: {user_dict}")
            return user_dict
        else:
            print("Utilisateur non trouvé en base de données")
            return None
            
    except jwt.ExpiredSignatureError:
        print("Token expiré")
        return None
    except jwt.InvalidTokenError:
        print("Token invalide")
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur: {e}")
        return None

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal (interface desktop)"""
    print("=== DASHBOARD ACCESS ===")
    print(f"Cookies reçus: {dict(request.cookies)}")
    
    user = get_user_from_token(request)
    if user:
        print(f"Utilisateur authentifié: {user}")
        stats = get_db_stats()
        
        return templates.TemplateResponse("dashboard_desktop.html", {
            "request": request,
            "user": user,
            **stats
        })
    else:
        print("Utilisateur non authentifié - redirection vers login")
        return templates.TemplateResponse("login_desktop.html", {
            "request": request,
            "info": "Veuillez vous connecter pour accéder au dashboard"
        })

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    """Page de profil principale (interface desktop)"""
    print("=== PROFILE ACCESS ===")
    print(f"Cookies reçus: {dict(request.cookies)}")
    
    user = get_user_from_token(request)
    if user:
        print(f"Utilisateur authentifié: {user}")
        activities = get_user_activities(user['email'])
        
        return templates.TemplateResponse("profile_desktop.html", {
            "request": request,
            "user": user,
            **activities
        })
    else:
        print("Utilisateur non authentifié - redirection vers login")
        return templates.TemplateResponse("login_desktop.html", {
            "request": request,
            "info": "Veuillez vous connecter pour accéder à votre profil"
        })

@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    """Page de contact principale (interface desktop)"""
    print("=== CONTACT ACCESS ===")
    print(f"Cookies reçus: {dict(request.cookies)}")
    
    user = get_user_from_token(request)
    print(f"Utilisateur: {user}")
    
    # Récupérer les statistiques pour la page contact
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Statistiques des messages
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE statut = 'traite'")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages")
    all_messages = cursor.fetchone()[0]
    
    treatment_rate = round((total_messages / all_messages * 100) if all_messages > 0 else 0)
    
    conn.close()
    
    return templates.TemplateResponse("contact_desktop.html", {
        "request": request,
        "user": user,
        "total_messages": total_messages,
        "treatment_rate": treatment_rate
    })

@router.post("/profile/change-password")
async def change_password(request: Request):
    """Changement de mot de passe principal (interface desktop)"""
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

@router.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    """Page des messages principale (interface desktop)"""
    print("=== MESSAGES ACCESS ===")
    
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        print("Utilisateur non admin ou non authentifié - redirection vers login")
        return templates.TemplateResponse("login_desktop.html", {
            "request": request,
            "info": "Veuillez vous connecter en tant qu'admin pour accéder aux messages"
        })
    
    try:
        # Récupérer tous les messages
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nom, email, telephone, message, date_creation, statut, reponse_admin, date_reponse
            FROM contact_messages 
            ORDER BY date_creation DESC
        """)
        
        messages_data = cursor.fetchall()
        conn.close()
        
        # Formater les messages
        messages = []
        for msg in messages_data:
            messages.append({
                'id': msg[0],
                'nom': msg[1],
                'email': msg[2],
                'telephone': msg[3],
                'message': msg[4],
                'date_creation': msg[5],
                'statut': msg[6],
                'reponse_admin': msg[7],
                'date_reponse': msg[8]
            })
        
        print(f"Messages récupérés: {len(messages)}")
        
        return templates.TemplateResponse("messages_simple.html", {
            "request": request,
            "user": user,
            "messages": messages
        })
        
    except Exception as e:
        print(f"Erreur messages page: {e}")
        return templates.TemplateResponse("login_desktop.html", {
            "request": request,
            "error": f"Erreur lors du chargement des messages: {str(e)}"
        })

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Page de connexion principale (interface desktop)"""
    return templates.TemplateResponse("login_desktop.html", {
        "request": request
    })

@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    """Page d'inscription principale (interface desktop)"""
    return templates.TemplateResponse("register_desktop.html", {
        "request": request
    })

@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Page de contact (existe déjà)"""
    from auth import get_user_from_token
    user = get_user_from_token(request)
    
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "user": user
    })

@router.post("/api/contact")
async def contact_form(request: Request):
    """Traitement du formulaire de contact avec synchronisation améliorée"""
    print("=== CONTACT FORM SUBMISSION ===")
    
    try:
        form_data = await request.form()
        
        nom = form_data.get('nom')
        email = form_data.get('email')
        telephone = form_data.get('telephone')
        sujet = form_data.get('sujet')
        message = form_data.get('message')
        urgent = form_data.get('urgent') == 'on'
        newsletter = form_data.get('newsletter') == 'on'
        
        print(f"Données reçues: nom={nom}, email={email}, sujet={sujet}, urgent={urgent}")
        
        # Validation des données
        if not all([nom, email, sujet, message]):
            return {"success": False, "detail": "Tous les champs obligatoires doivent être remplis"}
        
        # Connexion à la base de données
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Insertion du message avec les nouveaux champs
        cursor.execute("""
            INSERT INTO contact_messages 
            (nom, email, telephone, message, date_creation, statut, sujet, urgent, newsletter)
            VALUES (?, ?, ?, ?, datetime('now'), 'non_traite', ?, ?, ?)
        """, (nom, email, telephone, message, sujet, urgent, newsletter))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"Message inséré avec ID: {message_id}")
        
        # Synchronisation email améliorée
        try:
            from email_utils import EmailService
            email_service = EmailService()
            
            # Préparation du sujet email
            email_subject = f"📋 {sujet.replace('_', ' ').title()} - {nom}"
            if urgent:
                email_subject = "🚨 URGENT - " + email_subject
            
            # Préparation du contenu email
            email_content = f"""
📋 NOUVEAU MESSAGE DE CONTACT

👤 Client: {nom}
📧 Email: {email}
📞 Téléphone: {telephone or 'Non spécifié'}
📌 Sujet: {sujet.replace('_', ' ').title()}
🚨 Urgence: {'Oui - Traitement prioritaire' if urgent else 'Non'}
📬 Newsletter: {'Oui - Inscrit' if newsletter else 'Non'}

💬 Message:
{message}

📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
🆔 Référence: MSG{message_id:06d}

---
Ce message a été envoyé via le formulaire de contact du site RD Ménage
"""
            
            # Envoi de l'email
            success = email_service.send_contact_notification(
                nom=nom,
                email=email,
                telephone=telephone or '',
                message=message
            )
            
            if success:
                print("✅ Email envoyé avec succès")
                
                # Mise à jour du statut du message
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE contact_messages 
                    SET email_sent = 1, email_sent_date = datetime('now')
                    WHERE id = ?
                """, (message_id,))
                conn.commit()
                conn.close()
                
                return {
                    "success": True, 
                    "message": "Message envoyé avec succès",
                    "message_id": message_id,
                    "reference": f"MSG{message_id:06d}"
                }
            else:
                print("❌ Échec de l'envoi email")
                return {
                    "success": True, 
                    "message": "Message reçu mais email pas envoyé",
                    "message_id": message_id,
                    "reference": f"MSG{message_id:06d}"
                }
                
        except Exception as email_error:
            print(f"Erreur email: {email_error}")
            return {
                "success": True, 
                "message": "Message enregistré (erreur email)",
                "message_id": message_id,
                "reference": f"MSG{message_id:06d}"
            }
        
    except Exception as e:
        print(f"Erreur traitement formulaire: {e}")
        return {"success": False, "detail": f"Erreur lors du traitement: {str(e)}"}

@router.post("/api/quote")
async def quote_form(request: Request):
    """Traitement du formulaire de devis avec synchronisation améliorée"""
    print("=== QUOTE FORM SUBMISSION ===")
    
    try:
        form_data = await request.form()
        
        nom = form_data.get('nom')
        email = form_data.get('email')
        telephone = form_data.get('telephone')
        service_type = form_data.get('service_type')
        surface = form_data.get('surface')
        frequency = form_data.get('frequency')
        message = form_data.get('message')
        
        print(f"Données devis: nom={nom}, email={email}, service={service_type}")
        
        # Validation
        if not all([nom, email, service_type, surface]):
            return {"success": False, "detail": "Champs obligatoires manquants"}
        
        # Connexion base de données
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Insertion de la demande de devis
        cursor.execute("""
            INSERT INTO contact_messages 
            (nom, email, telephone, message, date_creation, statut, sujet, service_type, surface, frequency)
            VALUES (?, ?, ?, ?, datetime('now'), 'non_traite', 'demande_devis', ?, ?, ?)
        """, (nom, email, telephone, message, service_type, surface, frequency))
        
        quote_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"Devis inséré avec ID: {quote_id}")
        
        # Synchronisation email
        try:
            from email_utils import EmailService
            email_service = EmailService()
            
            email_subject = f"📋 DEMANDE DE DEVIS - {nom}"
            email_content = f"""
📋 NOUVELLE DEMANDE DE DEVIS

👤 Client: {nom}
📧 Email: {email}
📞 Téléphone: {telephone or 'Non spécifié'}

🏠 Type de service: {service_type}
📐 Surface: {surface} m²
🔄 Fréquence: {frequency}

💬 Message complémentaire:
{message or 'Aucun message complémentaire'}

📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
🆔 Référence: DEV{quote_id:06d}

---
Cette demande de devis a été envoyée via le site RD Ménage
"""
            
            success = email_service.send_contact_notification(
                nom=nom,
                email=email,
                telephone=telephone or '',
                message=f"[DEVIS] {service_type} - {surface}m² - {frequency}\n\n{message or ''}"
            )
            
            if success:
                print("✅ Email devis envoyé")
                return {
                    "success": True,
                    "message": "Demande de devis envoyée avec succès",
                    "quote_id": quote_id,
                    "reference": f"DEV{quote_id:06d}"
                }
            else:
                print("❌ Échec email devis")
                return {
                    "success": True,
                    "message": "Devis enregistré (erreur email)",
                    "quote_id": quote_id,
                    "reference": f"DEV{quote_id:06d}"
                }
                
        except Exception as email_error:
            print(f"Erreur email devis: {email_error}")
            return {
                "success": True,
                "message": "Devis enregistré (erreur email)",
                "quote_id": quote_id,
                "reference": f"DEV{quote_id:06d}"
            }
        
    except Exception as e:
        print(f"Erreur traitement devis: {e}")
        return {"success": False, "detail": f"Erreur: {str(e)}"}
