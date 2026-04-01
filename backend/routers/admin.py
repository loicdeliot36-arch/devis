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

@router.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    """Page de gestion des messages (interface desktop)"""
    print("=== ADMIN MESSAGES PAGE ===")
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        print("Utilisateur non admin ou non connecté")
        return RedirectResponse(url="/login", status_code=303)
    
    print(f"Utilisateur admin connecté: {user}")
    
    # Récupérer tous les messages
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, nom, email, telephone, message, date_creation, 
               statut, reponse_admin, date_reponse
        FROM contact_messages 
        ORDER BY date_creation DESC
    """)
    messages = cursor.fetchall()
    
    print(f"Messages récupérés: {len(messages)}")
    
    # Statistiques
    cursor.execute("SELECT COUNT(*) FROM contact_messages")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE statut = 'traite'")
    treated_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE statut = 'non_traite'")
    pending_messages = cursor.fetchone()[0]
    
    treatment_rate = round((treated_messages / total_messages * 100) if total_messages > 0 else 0)
    
    conn.close()
    
    print(f"Stats: total={total_messages}, treated={treated_messages}, pending={pending_messages}")
    
    # Formater les messages
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
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
    
    print(f"Template utilisé: messages_desktop.html")
    
    return templates.TemplateResponse("messages_desktop.html", {
        "request": request,
        "user": user,
        "messages": formatted_messages,
        "total_messages": total_messages,
        "treated_messages": treated_messages,
        "pending_messages": pending_messages,
        "treatment_rate": treatment_rate
    })

@router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    """Page de gestion des utilisateurs (interface desktop)"""
    print("=== ADMIN USERS PAGE ===")
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        print("Utilisateur non admin ou non connecté")
        return RedirectResponse(url="/login", status_code=303)
    
    print(f"Utilisateur admin connecté: {user}")
    
    # Récupérer tous les utilisateurs
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, email, nom, prenom, telephone, role, date_creation
        FROM users 
        ORDER BY date_creation DESC
    """)
    users = cursor.fetchall()
    
    print(f"Utilisateurs récupérés: {len(users)}")
    
    # Statistiques
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
    regular_users = cursor.fetchone()[0]
    
    # Nouveaux utilisateurs ce mois
    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE date_creation >= date('now', '-30 days')
    """)
    new_users_month = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Stats: total={total_users}, admin={admin_users}, regular={regular_users}")
    
    # Formater les utilisateurs avec statistiques
    formatted_users = []
    for user_data in users:
        user_id = user_data[0]
        
        # Compter les messages de cet utilisateur
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE email = ?", (user_data[1],))
        message_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM contact_messages 
            WHERE email = ? AND message LIKE '%devis%'
        """, (user_data[1],))
        quote_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT MAX(date_creation) FROM contact_messages 
            WHERE email = ?
        """, (user_data[1],))
        last_contact = cursor.fetchone()[0]
        
        conn.close()
        
        formatted_users.append({
            'id': user_id,
            'email': user_data[1],
            'nom': user_data[2],
            'prenom': user_data[3],
            'telephone': user_data[4],
            'role': user_data[5],
            'date_creation': user_data[6],
            'message_count': message_count,
            'quote_count': quote_count,
            'last_contact': last_contact
        })
    
    print(f"Template utilisé: users_desktop.html")
    
    return templates.TemplateResponse("users_desktop.html", {
        "request": request,
        "user": user,
        "users": formatted_users,
        "total_users": total_users,
        "admin_users": admin_users,
        "regular_users": regular_users,
        "new_users_month": new_users_month
    })

@router.get("/messages/{message_id}/details")
async def get_message_details(message_id: int, request: Request):
    """Récupérer les détails d'un message"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nom, email, telephone, message, date_creation, 
                   statut, reponse_admin, date_reponse
            FROM contact_messages 
            WHERE id = ?
        """, (message_id,))
        message = cursor.fetchone()
        conn.close()
        
        if message:
            return {
                'id': message[0],
                'nom': message[1],
                'email': message[2],
                'telephone': message[3],
                'message': message[4],
                'date_creation': message[5],
                'statut': message[6],
                'reponse_admin': message[7],
                'date_reponse': message[8]
            }
        else:
            return {"error": "Message non trouvé"}
            
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.delete("/messages/{message_id}/delete")
async def delete_message(message_id: int, request: Request):
    """Supprimer un message"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Vérifier si le message existe
        cursor.execute("SELECT nom, email FROM contact_messages WHERE id = ?", (message_id,))
        message_info = cursor.fetchone()
        
        if not message_info:
            conn.close()
            return {"error": "Message non trouvé"}
        
        # Supprimer le message
        cursor.execute("DELETE FROM contact_messages WHERE id = ?", (message_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            return {
                "success": True, 
                "message": f"Message de {message_info[0]} ({message_info[1]}) supprimé avec succès"
            }
        else:
            return {"error": "Aucun message supprimé"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.post("/messages/{message_id}/reply")
async def reply_to_message(message_id: int, request: Request):
    """Répondre à un message"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        data = await request.json()
        reply_message = data.get('message')
        mark_treated = data.get('mark_treated', True)
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Récupérer les infos du message pour l'email
        cursor.execute("SELECT nom, email FROM contact_messages WHERE id = ?", (message_id,))
        message_info = cursor.fetchone()
        
        if not message_info:
            conn.close()
            return {"error": "Message non trouvé"}
        
        client_name = message_info[0]
        client_email = message_info[1]
        
        # Envoyer l'email au client
        try:
            from email_utils import get_email_service
            email_service = get_email_service()
            
            email_sent = email_service.send_response_to_client(
                client_email=client_email,
                client_name=client_name,
                response=reply_message
            )
            
            if email_sent:
                print(f"✅ Email de réponse envoyé à {client_email}")
            else:
                print(f"❌ Échec envoi email à {client_email}")
                
        except Exception as email_error:
            print(f"Erreur email réponse: {email_error}")
        
        # Mettre à jour le message avec la réponse
        cursor.execute("""
            UPDATE contact_messages 
            SET reponse_admin = ?, date_reponse = datetime('now'), statut = ?
            WHERE id = ?
        """, (reply_message, 'traite' if mark_treated else 'non_traite', message_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True, 
            "message": "Réponse envoyée avec succès",
            "email_sent": email_sent if 'email_sent' in locals() else False
        }
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.post("/messages/{message_id}/mark-treated")
async def mark_message_as_treated(message_id: int, request: Request):
    """Marquer un message comme traité"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE contact_messages 
            SET statut = 'traite', date_reponse = datetime('now')
            WHERE id = ?
        """, (message_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Message marqué comme traité"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.post("/messages/{message_id}/mark-pending")
async def mark_message_as_pending(message_id: int, request: Request):
    """Marquer un message comme en attente"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE contact_messages 
            SET statut = 'non_traite'
            WHERE id = ?
        """, (message_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Message marqué comme en attente"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.get("/users/{user_id}/details")
async def get_user_details(user_id: int, request: Request):
    """Récupérer les détails d'un utilisateur"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, nom, prenom, telephone, role, date_creation, date_naissance
            FROM users 
            WHERE id = ?
        """, (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return {
                'id': user_data[0],
                'email': user_data[1],
                'nom': user_data[2],
                'prenom': user_data[3],
                'telephone': user_data[4],
                'role': user_data[5],
                'date_creation': user_data[6],
                'date_naissance': user_data[7]
            }
        else:
            return {"error": "Utilisateur non trouvé"}
            
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.post("/users/{user_id}/promote")
async def promote_user_to_admin(user_id: int, request: Request):
    """Promouvoir un utilisateur en administrateur"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET role = 'admin'
            WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Utilisateur promu avec succès"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.post("/users/{user_id}/demote")
async def demote_user_to_user(user_id: int, request: Request):
    """Rétrograder un administrateur en utilisateur"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET role = 'user'
            WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Utilisateur rétrogradé avec succès"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(user_id: int, request: Request):
    """Réinitialiser le mot de passe d'un utilisateur"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Générer un nouveau mot de passe aléatoire
        import random
        import string
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Hasher le mot de passe
        import bcrypt
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Mettre à jour le mot de passe
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        """, (password_hash, user_id))
        
        # Récupérer l'email de l'utilisateur
        cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        user_email = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return {
            "success": True, 
            "message": "Mot de passe réinitialisé avec succès",
            "new_password": new_password,
            "email": user_email
        }
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.delete("/users/{user_id}/delete")
async def delete_user(user_id: int, request: Request):
    """Supprimer un utilisateur"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Supprimer l'utilisateur
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Utilisateur supprimé avec succès"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.post("/users/add")
async def add_user(request: Request):
    """Ajouter un nouvel utilisateur"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        form_data = await request.form()
        
        email = form_data.get('email')
        nom = form_data.get('nom')
        prenom = form_data.get('prenom')
        password = form_data.get('password')
        telephone = form_data.get('telephone')
        role = form_data.get('role', 'user')
        
        # Vérifier si l'utilisateur existe déjà
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return {"error": "Cet email est déjà utilisé"}
        
        # Hasher le mot de passe
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insérer le nouvel utilisateur
        cursor.execute("""
            INSERT INTO users (email, password_hash, nom, prenom, telephone, role, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (email, password_hash, nom, prenom, telephone, role))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Utilisateur ajouté avec succès"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.get("/real-reviews", response_class=HTMLResponse)
async def admin_real_reviews_page(request: Request):
    """Page d'administration pour gérer les vrais avis Google"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return templates.TemplateResponse("login_desktop.html", {
            "request": request,
            "info": "Accès administrateur requis"
        })
    
    return templates.TemplateResponse("admin_real_reviews.html", {
        "request": request,
        "user": user
    })

@router.post("/real-reviews")
async def admin_add_real_reviews(request: Request):
    """Endpoint POST pour ajouter les vrais avis Google"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        # Récupérer les données du formulaire
        form_data = await request.json()
        reviews = form_data.get('reviews', [])
        
        if not reviews:
            return {"error": "Aucun avis fourni"}
        
        # Valider les avis
        valid_reviews = []
        for i, review in enumerate(reviews):
            if not all(key in review for key in ['name', 'rating', 'text', 'date']):
                return {"error": f"L'avis {i+1} est incomplet. Chaque avis doit avoir: name, rating, text, date"}
            
            if not isinstance(review['rating'], int) or review['rating'] < 1 or review['rating'] > 5:
                return {"error": f"L'avis {i+1} a une note invalide. La note doit être entre 1 et 5."}
            
            valid_reviews.append({
                'id': i + 1,
                'name': review['name'],
                'rating': review['rating'],
                'text': review['text'],
                'date': review['date'],
                'relative_time': review['date'],
                'source': 'manual_google_maps'
            })
        
        # Calculer la moyenne
        total_rating = sum(review['rating'] for review in valid_reviews)
        average_rating = round(total_rating / len(valid_reviews), 1)
        
        # Stocker en base de données
        import sqlite3
        from pathlib import Path
        from datetime import datetime
        
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer les tables si elles n'existent pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS real_google_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rating INTEGER NOT NULL,
                text TEXT NOT NULL,
                date TEXT NOT NULL,
                relative_time TEXT NOT NULL,
                source TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS real_google_stats (
                id INTEGER PRIMARY KEY,
                average_rating REAL NOT NULL,
                total_reviews INTEGER NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Vider et insérer les nouveaux avis
        cursor.execute("DELETE FROM real_google_reviews")
        
        for review in valid_reviews:
            cursor.execute("""
                INSERT INTO real_google_reviews (name, rating, text, date, relative_time, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (review['name'], review['rating'], review['text'], review['date'], review['relative_time'], review['source']))
        
        # Mettre à jour les stats
        cursor.execute("""
            INSERT OR REPLACE INTO real_google_stats (id, average_rating, total_reviews, last_updated)
            VALUES (1, ?, ?, ?)
        """, (average_rating, len(valid_reviews), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"{len(valid_reviews)} avis Google ajoutés manuellement avec succès",
            "average_rating": average_rating,
            "total_reviews": len(valid_reviews),
            "reviews": valid_reviews
        }
        
    except Exception as e:
        print(f"Erreur add_real_reviews: {e}")
        return {"error": f"Erreur: {str(e)}"}

@router.post("/users/{user_id}/edit")
async def edit_user(user_id: int, request: Request):
    """Modifier un utilisateur"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        form_data = await request.form()
        
        nom = form_data.get('nom')
        prenom = form_data.get('prenom')
        telephone = form_data.get('telephone')
        role = form_data.get('role')
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET nom = ?, prenom = ?, telephone = ?, role = ?
            WHERE id = ?
        """, (nom, prenom, telephone, role, user_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Utilisateur modifié avec succès"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.get("/users/export")
async def export_users(request: Request):
    """Exporter la liste des utilisateurs"""
    user = get_user_from_token(request)
    if not user or user['role'] != 'admin':
        return {"error": "Accès non autorisé"}
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT nom, prenom, email, telephone, role, date_creation
            FROM users 
            ORDER BY date_creation DESC
        """)
        users = cursor.fetchall()
        conn.close()
        
        # Créer le contenu CSV
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-tête
        writer.writerow(['Nom', 'Prénom', 'Email', 'Téléphone', 'Rôle', 'Date de création'])
        
        # Données
        for user_data in users:
            writer.writerow(user_data)
        
        # Retourner le fichier CSV
        from fastapi.responses import Response
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=users.csv"}
        )
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

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
        
        cursor.execute("""
            UPDATE contact_messages 
            SET statut = 'traite', date_reponse = datetime('now')
            WHERE id = ?
        """, (contact_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Message marqué comme traité"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.get("/sync", response_class=HTMLResponse)
async def sync_page(request: Request):
    """Page de synchronisation des données"""
    print("=== ADMIN SYNC PAGE ===")
    user = get_user_from_token(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    # Récupérer les statistiques
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Statistiques des messages
    cursor.execute("SELECT COUNT(*) FROM contact_messages")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE statut = 'traite'")
    treated_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE statut = 'non_traite'")
    pending_messages = cursor.fetchone()[0]
    
    # Statistiques des utilisateurs
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    conn.close()
    
    # Heure actuelle
    from datetime import datetime
    current_time = datetime.now().strftime('%H:%M:%S')
    
    return templates.TemplateResponse("sync_desktop.html", {
        "request": request,
        "user": user,
        "total_messages": total_messages,
        "treated_messages": treated_messages,
        "pending_messages": pending_messages,
        "total_users": total_users,
        "current_time": current_time
    })

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
        
        cursor.execute("DELETE FROM contact_messages WHERE id = ?", (contact_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Message supprimé"}
        
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}
