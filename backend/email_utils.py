import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from typing import Optional

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.admin_email = os.getenv("ADMIN_EMAIL")
        
        # Vérifier les variables d'environnement
        if not all([self.smtp_host, self.smtp_user, self.smtp_pass, self.admin_email]):
            raise ValueError("Variables d'environnement SMTP manquantes")
    
    def _connect(self) -> smtplib.SMTP:
        """Methode interne pour etablir la connexion SMTP avec handshake complet"""
        try:
            print(f"Connexion a {self.smtp_host}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            
            # Handshake SMTP complet pour Gmail
            print("Envoi EHLO...")
            server.ehlo()
            
            print("Demarrage TLS...")
            server.starttls()
            
            print("Envoi EHLO apres TLS...")
            server.ehlo()
            
            print("Authentification...")
            server.login(self.smtp_user, self.smtp_pass)
            
            print("Connexion SMTP etablie avec succes")
            return server
            
        except Exception as e:
            print(f"Erreur de connexion SMTP: {e}")
            raise e
    
    def send_contact_notification(self, nom: str, email: str, telephone: str, message: str) -> bool:
        """Envoie une notification au admin pour un nouveau contact"""
        try:
            # Essayer d'envoyer l'email
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.admin_email
            msg['Subject'] = f"[RD MENAGE] Nouveau message de {nom}"
            
            body = f"""
Nouveau message de contact reçu :

Nom : {nom}
Email : {email}
Téléphone : {telephone}
Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}

Message :
{message}

---
Cet message a été envoyé depuis le formulaire de contact du site RD Ménage à Domicile.
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = self._connect()
            server.send_message(msg)
            server.quit()
            
            print("Email de notification envoyé avec succès")
            return True
            
        except Exception as e:
            print(f"Erreur envoi email notification: {e}")
            # Ne pas lever d'exception pour ne pas bloquer le formulaire
            return False
    
    def send_response_to_client(self, client_email: str, client_name: str, response: str) -> bool:
        """Envoyer la réponse de l'admin au client"""
        server = None
        try:
            print(f"📧 Envoi de réponse au client: {client_email}")
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = client_email
            msg['Subject'] = f"Réponse à votre demande - RD Ménage à Domicile"
            
            body = f"""
Cher/Chère {client_name},

Nous avons bien reçu votre message et voici notre réponse :

{response}

Cordialement,
L'équipe RD Ménage à Domicile
07 82 71 41 55
racheldemange702@gmail.com

---
Cette réponse a été envoyée suite à votre demande de contact sur notre site.
RD Ménage à Domicile - Services de ménage professionnels
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Se connecter et envoyer
            server = self._connect()
            server.send_message(msg)
            print(f"✅ Email de réponse envoyé avec succès à {client_email}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur envoi email réponse client: {e}")
            return False
        finally:
            if server:
                try:
                    server.quit()
                    print("🔌 Connexion SMTP fermée")
                except:
                    pass
    
    def send_test_email(self) -> bool:
        """Envoyer un email de test"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.admin_email
            msg['Subject'] = "[RD MENAGE] Test Email SMTP"
            
            body = f"""
Test de configuration SMTP réussi !

Email de test envoyé le : {datetime.now().strftime('%d/%m/%Y %H:%M')}

Configuration SMTP :
- Host : {self.smtp_host}
- Port : {self.smtp_port}
- User : {self.smtp_user}

Ceci est un email de test pour vérifier que la configuration fonctionne correctement.

---
RD Ménage à Domicile
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = self._connect()
            server.send_message(msg)
            server.quit()
            
            print("Email de test envoyé avec succès")
            return True
            
        except Exception as e:
            print(f"Erreur envoi email test: {e}")
            return False

    def test_connection(self) -> bool:
        """Tester la connexion SMTP"""
        server = None
        try:
            server = self._connect()
            print("Test de connexion SMTP reussi")
            return True
        except Exception as e:
            print(f"Test de connexion SMTP echoue: {e}")
            return False
        finally:
            if server:
                try:
                    server.quit()
                    print("Connexion test fermee")
                except:
                    pass

# Instance globale du service (créée à la demande)
email_service = None

def get_email_service():
    """Créer l'instance du service email avec variables chargées"""
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service
