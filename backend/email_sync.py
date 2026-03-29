import imaplib
import email
from email.header import decode_header
import re
import sqlite3
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class EmailSync:
    def __init__(self):
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.imap_server = "imap.gmail.com"
        
    def connect_to_imap(self):
        """Connexion au serveur IMAP Gmail"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.smtp_user, self.smtp_pass)
            return mail
        except Exception as e:
            print(f"Erreur connexion IMAP: {e}")
            return None
    
    def decode_subject(self, subject):
        """Décoder le sujet de l'email"""
        if subject:
            decoded_parts = decode_header(subject)
            subject = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    subject += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    subject += part
        return subject
    
    def extract_client_info(self, subject, body, from_email):
        """Extraire les informations du client depuis l'email"""
        client_email = None
        client_name = None
        
        # 1. Chercher dans le sujet (réponses à nos emails)
        match = re.search(r'\[RD MENAGE\] Réponse: (.+?) <(.+?)>', subject)
        if match:
            client_name = match.group(1).strip()
            client_email = match.group(2).strip()
            return client_name, client_email
        
        # 2. Chercher dans le sujet (nouveau message)
        match = re.search(r'\[RD MENAGE\] Nouveau message de (.+?) \((.+?)\)', subject)
        if match:
            client_name = match.group(1).strip()
            client_email = match.group(2).strip()
            return client_name, client_email
        
        # 3. Chercher dans le corps de l'email
        email_patterns = [
            r'Client\s*:\s*([^\s<]+@[^\s>]+)',
            r'Email\s*:\s*([^\s<]+@[^\s>]+)',
            r'([^\s<]+@[^\s>]+)'
        ]
        
        for pattern in email_patterns:
            email_match = re.search(pattern, body)
            if email_match:
                client_email = email_match.group(1)
                break
        
        # 4. Extraire le nom depuis le sujet ou le corps
        if not client_name:
            # Chercher dans le sujet
            name_match = re.search(r'Nouveau message de (.+?) \(', subject)
            if name_match:
                client_name = name_match.group(1).strip()
            else:
                # Extraire depuis l'email si trouvé
                if client_email:
                    client_name = client_email.split('@')[0].replace('.', ' ').title()
        
        # 5. Utiliser l'email de l'expéditeur comme dernier recours
        if not client_email and from_email:
            client_email = from_email
            if not client_name:
                client_name = client_email.split('@')[0].replace('.', ' ').title()
        
        return client_name, client_email
    
    def find_original_message(self, client_email, client_name):
        """Trouver le message original non traité dans la base de données"""
        try:
            db_path = Path(__file__).parent / "database.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Chercher le message le plus récent NON TRAITE pour ce client
            cursor.execute('''
                SELECT id FROM contact_messages 
                WHERE (email = ? OR nom LIKE ?) AND statut != 'traite'
                ORDER BY date_creation DESC
                LIMIT 1
            ''', (client_email, f"%{client_name}%"))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            else:
                # Si aucun message non traité, chercher le plus récent (même traité)
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM contact_messages 
                    WHERE email = ? OR nom LIKE ?
                    ORDER BY date_creation DESC
                    LIMIT 1
                ''', (client_email, f"%{client_name}%"))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    print(f"Aucun message non traité trouvé pour {client_email}, utilisation du plus récent: #{result[0]}")
                    return result[0]
                else:
                    return None
            
        except Exception as e:
            print(f"Erreur recherche message original: {e}")
            return None
    
    def save_response(self, message_id, response_text):
        """Sauvegarder la réponse dans la base de données"""
        try:
            db_path = Path(__file__).parent / "database.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE contact_messages 
                SET reponse_admin = ?, date_reponse = ?, statut = 'traite'
                WHERE id = ?
            ''', (response_text, datetime.now().isoformat(), message_id))
            
            conn.commit()
            conn.close()
            
            print(f"Réponse synchronisée pour le message #{message_id}")
            return True
            
        except Exception as e:
            print(f"Erreur sauvegarde réponse: {e}")
            return False
    
    def check_responses(self):
        """Vérifier les réponses par email et les synchroniser"""
        print("Verification des reponses par email...")
        
        mail = self.connect_to_imap()
        if not mail:
            return False
        
        try:
            # Sélectionner la boîte de réception
            mail.select('inbox')
            
            # Chercher les emails de réponse (réponses à nos emails)
            # Chercher dans Messages envoyés où vos réponses se trouvent
            try:
                mail.select('"[Gmail]/Messages envoy&AOk-s"')
                search_criteria = 'FROM "nathantechniquerd@gmail.com"'
                status, messages = mail.search(None, search_criteria)
                
                if status != 'OK' or not messages[0]:
                    print("Aucun email trouvé de votre part dans Messages envoyés")
                    # Chercher dans la boîte de réception aussi
                    mail.select('inbox')
                    search_criteria = 'FROM "nathantechniquerd@gmail.com"'
                    status, messages = mail.search(None, search_criteria)
            except Exception as e:
                print(f"Erreur sélection Messages envoyés: {e}")
                mail.select('inbox')
                search_criteria = 'FROM "nathantechniquerd@gmail.com"'
                status, messages = mail.search(None, search_criteria)
            
            if status != 'OK' or not messages[0]:
                print("Aucun email trouvé, recherche de tous les emails")
                search_criteria = 'ALL'
                status, messages = mail.search(None, search_criteria)
            
            if status != 'OK' or not messages[0]:
                print("Aucun email trouvé")
                return True
            
            email_ids = messages[0].split()
            print(f"{len(email_ids)} emails trouvés au total")
            
            # Limiter aux 50 derniers emails pour analyse (les plus récents)
            # Les emails sont triés du plus ancien au plus récent, donc on prend les 50 premiers de la fin
            recent_ids = email_ids[-50:]
            print(f"Analyse des {len(recent_ids)} emails les plus récents")
            
            synced_count = 0
            
            for email_id in recent_ids:  # Analyser les 50 derniers emails
                try:
                    # Récupérer l'email
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parser l'email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extraire les informations
                    subject = self.decode_subject(msg.get('Subject', ''))
                    from_email = msg.get('From', '')
                    
                    # Nettoyer l'email de l'expéditeur
                    if '<' in from_email and '>' in from_email:
                        from_email = from_email.split('<')[1].split('>')[0]
                    
                    # Extraire le corps de l'email
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            body = str(msg.get_payload())
                    
                    print(f"Email analysé: {subject[:50]}...")
                    print(f"De: {from_email}")
                    
                    # Extraire les infos du client
                    client_name, client_email = self.extract_client_info(subject, body, from_email)
                    
                    # Si c'est une réponse envoyée par vous, extraire le destinataire
                    if "nathantechniquerd@gmail.com" in from_email:
                        # C'est une réponse que vous avez envoyée
                        to_emails = msg.get('To', '').split(',')
                        cc_emails = msg.get('Cc', '').split(',') if msg.get('Cc') else []
                        
                        # Chercher l'email du client dans les destinataires
                        for email_addr in to_emails + cc_emails:
                            if email_addr and 'gmail.com' not in email_addr and 'googlemail.com' not in email_addr:
                                to_email = email_addr.strip()
                                break
                        
                        # Nettoyer l'email
                        if '<' in to_email and '>' in to_email:
                            to_email = to_email.split('<')[1].split('>')[0]
                        
                        print(f"Destinataire de votre réponse: {to_email}")
                        
                        # Utiliser le destinataire comme email client
                        if to_email and '@' in to_email:
                            client_email = to_email
                            client_name = client_email.split('@')[0].replace('.', ' ').title()
                            print(f"Client extrait depuis destinataire: {client_name} - {client_email}")
                        else:
                            print("Impossible de trouver le destinataire")
                            continue
                    
                    # Afficher les infos trouvées
                    print(f"Sujet: {subject}")
                    print(f"De: {from_email}")
                    print(f"Client trouvé: {client_name} - {client_email}")
                    
                    if not client_email:
                        print("Email client non trouvé, email suivant...")
                        continue
                    
                    # Chercher seulement les emails qui contiennent "RD MENAGE" OU les emails récents de vous
                    is_rd_menage = "RD MENAGE" in subject
                    is_from_you = "nathantechniquerd@gmail.com" in from_email
                    
                    if not is_rd_menage and not is_from_you:
                        print(f"Pas un email RD MENAGE ou de votre part, email suivant...")
                        continue
                    
                    # Trouver le message original
                    original_message_id = self.find_original_message(client_email, client_name)
                    
                    if not original_message_id:
                        print(f"Message original non trouvé pour: {client_email}")
                        continue
                    
                    # Sauvegarder la réponse
                    if self.save_response(original_message_id, body):
                        synced_count += 1
                        
                        # Marquer l'email comme lu (optionnel)
                        mail.store(email_id, '+FLAGS', '\\Seen')
                
                except Exception as e:
                    print(f"Erreur traitement email {email_id}: {e}")
                    continue
            
            print(f"{synced_count} réponses synchronisées")
            return True
            
        except Exception as e:
            print(f"Erreur générale: {e}")
            return False
        finally:
            mail.logout()

def sync_email_responses():
    """Fonction principale pour synchroniser les réponses"""
    sync = EmailSync()
    return sync.check_responses()

if __name__ == "__main__":
    sync_email_responses()
