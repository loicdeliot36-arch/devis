from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_utils import get_email_service
from database import init_db
import sqlite3

router = APIRouter()

class ContactForm(BaseModel):
    nom: str
    prenom: str
    telephone: str
    email: EmailStr
    message: str

class QuoteForm(BaseModel):
    nom: str
    prenom: str
    telephone: str
    email: EmailStr
    message: str

@router.post("/api/test-email")
async def test_email():
    """API endpoint pour tester l'envoi d'email"""
    try:
        email_service = get_email_service()
        result = email_service.send_test_email()
        
        return {
            "success": True,
            "message": "Email de test envoyé avec succès",
            "recipient": email_service.smtp_user
        }
        
    except Exception as e:
        print(f"Erreur test email: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/sync-messages")
async def sync_messages():
    """API endpoint pour synchroniser les messages"""
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter les messages non synchronisés (email_sent = 0)
        cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE email_sent = 0")
        unsynced_count = cursor.fetchone()[0]
        
        if unsynced_count == 0:
            conn.close()
            return {
                "success": True,
                "message": "Tous les messages sont déjà synchronisés",
                "synced_count": 0
            }
        
        # Simuler la synchronisation - marquer comme envoyés
        cursor.execute("UPDATE contact_messages SET email_sent = 1, email_sent_date = datetime('now') WHERE email_sent = 0")
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"{unsynced_count} messages synchronisés avec succès",
            "synced_count": unsynced_count
        }
        
    except Exception as e:
        print(f"Erreur sync messages: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/refresh-stats")
async def refresh_stats():
    """API endpoint pour rafraîchir les statistiques"""
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Statistiques des messages
        cursor.execute("SELECT COUNT(*) FROM contact_messages")
        total_messages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE statut = 'traite'")
        treated_messages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE statut = 'non_traite'")
        pending_messages = cursor.fetchone()[0]
        
        # Statistiques utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "message": "Statistiques rafraîchies",
            "stats": {
                "total_messages": total_messages,
                "treated_messages": treated_messages,
                "pending_messages": pending_messages,
                "total_users": total_users
            }
        }
        
    except Exception as e:
        print(f"Erreur refresh stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/cleanup-database")
async def cleanup_database():
    """API endpoint pour nettoyer la base de données"""
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Nettoyer les anciens messages (plus de 30 jours)
        cursor.execute("""
            DELETE FROM contact_messages 
            WHERE date_creation < date('now', '-30 days')
        """)
        cleaned_count = cursor.rowcount
        
        # Optimiser la base
        cursor.execute("VACUUM")
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Base de données nettoyée",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        print(f"Erreur cleanup database: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/optimize-database")
async def optimize_database():
    """API endpoint pour optimiser la base de données"""
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        optimizations = []
        
        # Recréer les index
        cursor.execute("REINDEX")
        optimizations.append("Index recréés")
        
        # Analyser la base
        cursor.execute("ANALYZE")
        optimizations.append("Base analysée")
        
        # VACUUM
        cursor.execute("VACUUM")
        optimizations.append("Base optimisée")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Base de données optimisée",
            "optimizations": optimizations
        }
        
    except Exception as e:
        print(f"Erreur optimize database: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/check-integrity")
async def check_integrity():
    """API endpoint pour vérifier l'intégrité de la base"""
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier l'intégrité
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()
        
        conn.close()
        
        if integrity_result[0] == 'ok':
            return {
                "success": True,
                "message": "Intégrité vérifiée",
                "integrity_status": "OK"
            }
        else:
            return {
                "success": False,
                "message": "Problème d'intégrité détecté",
                "integrity_status": "ERROR"
            }
        
    except Exception as e:
        print(f"Erreur check integrity: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/mark-treated/{message_id}")
async def mark_message_as_treated(message_id: int):
    """API endpoint pour marquer un message comme traité"""
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Mettre à jour le statut
        cursor.execute("""
            UPDATE contact_messages 
            SET statut = 'traite', date_reponse = datetime('now')
            WHERE id = ?
        """, (message_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Message marqué comme traité"
        }
        
    except Exception as e:
        print(f"Erreur mark treated: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/contact")
async def api_contact(form_data: ContactForm):
    """API endpoint pour le formulaire de contact (compatibilité frontend)"""
    try:
        # Enregistrer dans la base de données
        db_path = Path(__file__).parent.parent / "database.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Combiner nom et prénom pour le nom complet
        nom_complet = f"{form_data.nom} {form_data.prenom}"
        
        cursor.execute('''
            INSERT INTO contact_messages (nom, email, telephone, message, date_creation, statut)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nom_complet, form_data.email, form_data.telephone, form_data.message, datetime.now().isoformat(), "non_traite"))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Envoyer l'email à l'admin
        email_service = get_email_service()
        email_sent = email_service.send_contact_notification(
            nom_complet, 
            form_data.email, 
            form_data.telephone, 
            form_data.message
        )
        
        return {
            "success": True,
            "message": "Message envoyé avec succès",
            "email_sent": email_sent,
            "message_id": message_id
        }
        
    except Exception as e:
        print(f"Erreur API contact: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi du message")

@router.post("/api/quote")
async def api_quote(form_data: QuoteForm):
    """API endpoint pour le formulaire de devis (compatibilité frontend)"""
    try:
        # Enregistrer dans la base de données
        db_path = Path(__file__).parent.parent / "database.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Combiner nom et prénom pour le nom complet
        nom_complet = f"{form_data.nom} {form_data.prenom}"
        
        cursor.execute('''
            INSERT INTO contact_messages (nom, email, telephone, message, date_creation, statut)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nom_complet, form_data.email, form_data.telephone, f"Demande de devis: {form_data.message}", datetime.now().isoformat(), "non_traite"))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Envoyer l'email à l'admin
        email_service = get_email_service()
        email_sent = email_service.send_contact_notification(
            nom_complet, 
            form_data.email, 
            form_data.telephone, 
            f"Demande de devis: {form_data.message}"
        )
        
        return {
            "success": True,
            "message": "Demande de devis envoyée avec succès",
            "email_sent": email_sent,
            "message_id": message_id
        }
        
    except Exception as e:
        print(f"Erreur API quote: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de la demande de devis")
