#!/usr/bin/env python3
"""
Script pour tester la configuration SMTP
"""

import os
from dotenv import load_dotenv
from email_utils import get_email_service

# Charger les variables d'environnement
load_dotenv()

def test_smtp_connection():
    """Tester la connexion SMTP"""
    print("Test de la configuration SMTP...")
    print(f"SMTP_HOST: {os.getenv('SMTP_HOST')}")
    print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
    print(f"SMTP_USER: {os.getenv('SMTP_USER')}")
    print(f"ADMIN_EMAIL: {os.getenv('ADMIN_EMAIL')}")
    
    # Créer l'instance du service et tester
    try:
        email_service = get_email_service()
        if email_service.test_connection():
            print("Connexion SMTP reussie !")
            return True
        else:
            print("Connexion SMTP echouee !")
            return False
    except ValueError as e:
        print(f"Erreur de configuration: {e}")
        return False

def test_email_sending():
    """Tester l'envoi d'email"""
    print("\nTest d'envoi d'email...")
    
    try:
        email_service = get_email_service()
        
        # Envoyer un email de test
        success = email_service.send_contact_notification(
            nom="Test Utilisateur",
            email="test@example.com",
            telephone="06 12 34 56 78",
            message="Ceci est un message de test pour verifier que l'envoi d'email fonctionne correctement."
        )
        
        if success:
            print("Email de test envoye avec succes !")
            print(f"Verifiez votre boite mail : {os.getenv('ADMIN_EMAIL')}")
            return True
        else:
            print("Echec de l'envoi de l'email de test !")
            return False
    except ValueError as e:
        print(f"Erreur de configuration: {e}")
        return False

if __name__ == "__main__":
    print("=== Test du système d'emails ===\n")
    
    # Vérifier les variables d'environnement
    required_vars = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "ADMIN_EMAIL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Variables d'environnement manquantes : {', '.join(missing_vars)}")
        print("Creez un fichier .env base sur .env.example")
        print("\nExemple de fichier .env :")
        print("SMTP_HOST=smtp.gmail.com")
        print("SMTP_PORT=587")
        print("SMTP_USER=votre-email@gmail.com")
        print("SMTP_PASS=votre-mot-de-passe-app")
        print("ADMIN_EMAIL=racheldemange702@gmail.com")
        exit(1)
    
    # Tester la connexion
    connection_ok = test_smtp_connection()
    
    if connection_ok:
        # Tester l'envoi
        test_email_sending()
        print("\nTous les tests sont termines !")
    else:
        print("\nCorrigez la configuration SMTP avant de continuer.")
        print("\nConseils pour Gmail :")
        print("1. Activez l'acces moins securise OU utilisez un mot de passe d'application")
        print("2. Pour mot de passe d'application : https://myaccount.google.com/apppasswords")
        print("3. Pour acces moins securise : https://myaccount.google.com/lesssecureapps")
