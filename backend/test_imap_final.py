import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_imap_final():
    """Test final dans le bon dossier Messages envoyés"""
    try:
        # Connexion IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        
        print("=== TEST DANS MESSAGES ENVOYES ===")
        try:
            mail.select('"[Gmail]/Messages envoy&AOk-s"')
            status, messages = mail.search(None, 'ALL')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"Emails dans Messages envoyés: {len(email_ids)}")
                
                # Prendre les 5 plus récents
                for email_id in email_ids[-5:]:
                    try:
                        status, msg_data = mail.fetch(email_id, '(BODY[HEADER])')
                        if status == 'OK':
                            import email
                            raw_email = msg_data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            
                            subject = msg.get('Subject', '')
                            from_addr = msg.get('From', '')
                            to_addr = msg.get('To', '')
                            date = msg.get('Date', '')
                            
                            # Décoder le sujet si nécessaire
                            if subject.startswith('=?'):
                                import email.header
                                decoded_subject = email.header.decode_header(subject)
                                subject = ''
                                for part, encoding in decoded_subject:
                                    if isinstance(part, bytes):
                                        subject += part.decode(encoding or 'utf-8', errors='ignore')
                                    else:
                                        subject += part
                            
                            print(f"  Sujet: {subject}")
                            print(f"  De: {from_addr}")
                            print(f"  A: {to_addr}")
                            print(f"  Date: {date}")
                            print("  ---")
                    except Exception as e:
                        print(f"  Erreur lecture email {email_id}: {e}")
            else:
                print("Aucun email dans Messages envoyés")
        except Exception as e:
            print(f"Erreur Messages envoyés: {e}")
        
        print("\n=== RECHERCHE SUJET 'test' ===")
        try:
            mail.select('"[Gmail]/Messages envoy&AOk-s"')
            status, messages = mail.search(None, 'SUBJECT', 'test')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"Emails avec sujet 'test': {len(email_ids)}")
                
                for email_id in email_ids:
                    try:
                        status, msg_data = mail.fetch(email_id, '(BODY[HEADER])')
                        if status == 'OK':
                            import email
                            raw_email = msg_data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            
                            subject = msg.get('Subject', '')
                            from_addr = msg.get('From', '')
                            to_addr = msg.get('To', '')
                            
                            print(f"  Sujet: {subject}")
                            print(f"  De: {from_addr}")
                            print(f"  A: {to_addr}")
                            print("  ---")
                    except Exception as e:
                        print(f"  Erreur lecture email {email_id}: {e}")
            else:
                print("Aucun email avec sujet 'test' trouvé")
        except Exception as e:
            print(f"Erreur recherche 'test': {e}")
        
        print("\n=== RECHERCHE VOS EMAILS ===")
        try:
            mail.select('"[Gmail]/Messages envoy&AOk-s"')
            status, messages = mail.search(None, 'FROM', '"nathantechniquerd@gmail.com"')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"Vos emails envoyés: {len(email_ids)}")
                
                for email_id in email_ids[-3:]:
                    try:
                        status, msg_data = mail.fetch(email_id, '(BODY[HEADER])')
                        if status == 'OK':
                            import email
                            raw_email = msg_data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            
                            subject = msg.get('Subject', '')
                            from_addr = msg.get('From', '')
                            to_addr = msg.get('To', '')
                            date = msg.get('Date', '')
                            
                            print(f"  Sujet: {subject}")
                            print(f"  De: {from_addr}")
                            print(f"  A: {to_addr}")
                            print(f"  Date: {date}")
                            print("  ---")
                    except Exception as e:
                        print(f"  Erreur lecture email {email_id}: {e}")
            else:
                print("Aucun email de vous trouvé")
        except Exception as e:
            print(f"Erreur recherche vos emails: {e}")
        
        mail.logout()
        
    except Exception as e:
        print(f"Erreur IMAP: {e}")

if __name__ == "__main__":
    test_imap_final()
