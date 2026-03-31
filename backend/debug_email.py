import os
from dotenv import load_dotenv
from email_utils import EmailService

def test_email_config():
    """Test la configuration email"""
    print("=== CONFIGURATION EMAIL ===")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier les variables d'environnement
    env_vars = {
        'SMTP_HOST': os.getenv("SMTP_HOST"),
        'SMTP_PORT': os.getenv("SMTP_PORT", "587"),
        'SMTP_USER': os.getenv("SMTP_USER"),
        'SMTP_PASS': os.getenv("SMTP_PASS"),
        'ADMIN_EMAIL': os.getenv("ADMIN_EMAIL")
    }
    
    print("Variables d'environnement:")
    for key, value in env_vars.items():
        if key == 'SMTP_PASS':
            print(f"{key}: {'***' if value else 'MANQUANT'}")
        else:
            print(f"{key}: {value or 'MANQUANT'}")
    
    # Tester la connexion SMTP
    try:
        print("\n=== TEST CONNEXION SMTP ===")
        email_service = EmailService()
        print("EmailService initialisé avec succès")
        
        # Tester l'envoi d'un email test
        print("\n=== TEST ENVOI EMAIL ===")
        success = email_service.send_contact_notification(
            nom="Test",
            email="test@example.com",
            telephone="0123456789",
            message="Ceci est un message de test"
        )
        
        if success:
            print("Email envoyé avec succès !")
        else:
            print("Echec de l'envoi de l'email")
            
    except Exception as e:
        print(f"Erreur: {e}")
        print("\n=== SOLUTIONS POSSIBLES ===")
        print("1. Vérifier que le mot de passe Gmail est un mot de passe d'application")
        print("2. Activer l'authentification en 2 étapes sur Gmail")
        print("3. Générer un nouveau mot de passe d'application")
        print("4. Vérifier que l'email admin est correct")

if __name__ == "__main__":
    test_email_config()
