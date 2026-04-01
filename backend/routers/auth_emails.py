from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
from auth import get_password_hash
from models import ResetRequest, ResetPassword, generate_reset_code, is_token_valid
from email_utils import EmailService

router = APIRouter()

def init_db():
    """Initialiser la table reset_tokens si elle n'existe pas"""
    db_path = Path(__file__).parent.parent / "database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            used BOOLEAN DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()

@router.post("/auth/register")
async def register_with_email(request: Request):
    """Inscription avec envoi d'email de confirmation"""
    try:
        init_db()
        
        # Récupérer les données du formulaire
        form_data = await request.form()
        email = form_data.get('email')
        password = form_data.get('password')
        nom = form_data.get('nom', '')
        prenom = form_data.get('prenom', '')
        
        if not email or not password:
            return JSONResponse(
                {"success": False, "error": "Email et mot de passe requis"},
                status_code=400
            )
        
        # Vérifier si l'utilisateur existe déjà
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return JSONResponse(
                {"success": False, "error": "Cet email est déjà utilisé"},
                status_code=400
            )
        
        # Créer l'utilisateur
        hashed_password = get_password_hash(password)
        cursor.execute("""
            INSERT INTO users (email, password_hash, role, nom, prenom, date_creation)
            VALUES (?, ?, 'user', ?, ?, ?)
        """, (email, hashed_password, nom, prenom, datetime.now().isoformat()))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Envoyer l'email de confirmation
        try:
            email_service = EmailService()
            email_content = f"""
Bonjour {prenom or nom},

Bienvenue sur RD Menage !

Votre compte a ete cree avec succes avec l'adresse email : {email}

Vous pouvez maintenant vous connecter et profiter de nos services :
- Demander des devis en ligne
- Suivre vos demandes
- Gerer vos informations

Vos identifiants :
Email : {email}
Mot de passe : [celui que vous avez choisi]

Pour toute question, n'hesitez pas a nous contacter.

Cordialement,
L'equipe RD Menage
---
RD Menage a Domicile
contact@rdmenage.fr
www.rdmenage.fr
            """
            
            success = email_service.send_email(
                to_email=email,
                subject="Bienvenue - Votre compte RD Menage a ete cree",
                content=email_content
            )
            
            if success:
                print(f"Email de confirmation envoye a {email}")
            else:
                print(f"❌ Erreur envoi email à {email}")
                
        except Exception as e:
            print(f"Erreur envoi email confirmation: {e}")
        
        return JSONResponse({
            "success": True,
            "message": "Compte créé avec succès. Un email de confirmation vous a été envoyé.",
            "user_id": user_id
        })
        
    except Exception as e:
        print(f"Erreur inscription: {e}")
        return JSONResponse(
            {"success": False, "error": f"Erreur lors de l'inscription: {str(e)}"},
            status_code=500
        )

@router.post("/auth/request-reset")
async def request_password_reset(request: ResetRequest):
    """Demander une réinitialisation de mot de passe"""
    try:
        init_db()
        
        email = request.email
        
        # Vérifier si l'utilisateur existe
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nom, prenom FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            # Ne pas révéler si l'email existe ou pas pour des raisons de sécurité
            conn.close()
            return JSONResponse({
                "success": True,
                "message": "Si cet email existe dans notre base, vous recevrez un code de réinitialisation."
            })
        
        # Générer et stocker le token
        token = generate_reset_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Marquer les anciens tokens comme utilisés
        cursor.execute("UPDATE reset_tokens SET used = 1 WHERE email = ?", (email,))
        
        # Insérer le nouveau token
        cursor.execute("""
            INSERT INTO reset_tokens (email, token, expires_at)
            VALUES (?, ?, ?)
        """, (email, token, expires_at))
        
        conn.commit()
        conn.close()
        
        # Envoyer l'email avec le code
        try:
            email_service = EmailService()
            email_content = f"""
Bonjour {user[2] or user[1]},

Vous avez demande la reinitialisation de votre mot de passe RD Menage.

Voici votre code de reinitialisation :
{token}

Ce code est valide pendant 10 minutes.

Pour reinitialiser votre mot de passe :
1. Retournez sur la page de connexion
2. Cliquez sur "Mot de passe oublie"
3. Entrez votre email et ce code
4. Choisissez votre nouveau mot de passe

Securite :
- Ne partagez jamais ce code
- Le code expire apres 10 minutes
- Si vous n'avez pas demande cette reinitialisation, ignorez cet email

Cordialement,
L'equipe RD Menage
---
RD Menage a Domicile
contact@rdmenage.fr
www.rdmenage.fr
            """
            
            success = email_service.send_email(
                to_email=email,
                subject="Reinitialisation de votre mot de passe RD Menage",
                content=email_content
            )
            
            if success:
                print(f"Email de reinitialisation envoye a {email}")
            else:
                print(f"❌ Erreur envoi email réinitialisation à {email}")
                
        except Exception as e:
            print(f"Erreur envoi email reset: {e}")
        
        return JSONResponse({
            "success": True,
            "message": "Si cet email existe dans notre base, vous recevrez un code de réinitialisation."
        })
        
    except Exception as e:
        print(f"Erreur demande reset: {e}")
        return JSONResponse(
            {"success": False, "error": f"Erreur: {str(e)}"},
            status_code=500
        )

@router.post("/auth/reset-password")
async def reset_password(request: ResetPassword):
    """Réinitialiser le mot de passe avec un code"""
    try:
        init_db()
        
        email = request.email
        token = request.token
        new_password = request.new_password
        
        # Vérifier le token
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, used, expires_at 
            FROM reset_tokens 
            WHERE email = ? AND token = ?
            ORDER BY created_at DESC 
            LIMIT 1
        """, (email, token))
        
        token_obj = cursor.fetchone()
        
        if not token_obj:
            conn.close()
            return JSONResponse(
                {"success": False, "error": "Code de réinitialisation invalide"},
                status_code=400
            )
        
        # Créer un objet token pour validation
        from datetime import datetime
        token_data = {
            'used': bool(token_obj[1]),
            'expires_at': datetime.fromisoformat(token_obj[2]) if isinstance(token_obj[2], str) else token_obj[2]
        }
        
        if not is_token_valid(type('TokenObj', (), token_data)):
            conn.close()
            return JSONResponse(
                {"success": False, "error": "Code expiré ou déjà utilisé"},
                status_code=400
            )
        
        # Mettre à jour le mot de passe
        hashed_password = get_password_hash(new_password)
        cursor.execute("""
            UPDATE users 
            SET password_hash = ? 
            WHERE email = ?
        """, (hashed_password, email))
        
        # Marquer le token comme utilisé
        cursor.execute("""
            UPDATE reset_tokens 
            SET used = 1 
            WHERE id = ?
        """, (token_obj[0],))
        
        conn.commit()
        conn.close()
        
        print(f"Mot de passe reinitialise pour {email}")
        
        return JSONResponse({
            "success": True,
            "message": "Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter."
        })
        
    except Exception as e:
        print(f"Erreur reset password: {e}")
        return JSONResponse(
            {"success": False, "error": f"Erreur: {str(e)}"},
            status_code=500
        )
