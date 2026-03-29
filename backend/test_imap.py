import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_imap_search():
    """Test de recherche IMAP pour trouver votre réponse"""
    try:
        # Connexion IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        mail.select('inbox')
        
        print("Test de recherche dans BOITE DE RECEPTION...")
        
        # 1. Chercher les emails envoyés par vous
        status, messages = mail.search(None, 'FROM', '"nathantechniquerd@gmail.com"')
        if status == 'OK' and messages[0]:
            email_ids = messages[0].split()
            print(f"{len(email_ids)} emails trouvés de votre part")
            
            # Prendre les 5 plus récents
            for email_id in email_ids[-5:]:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        import email
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        subject = msg.get('Subject', '')
                        from_addr = msg.get('From', '')
                        to_addr = msg.get('To', '')
                        date = msg.get('Date', '')
                        
                        print(f"Sujet: {subject}")
                        print(f"De: {from_addr}")
                        print(f"A: {to_addr}")
                        print(f"Date: {date}")
                        print("---")
                except Exception as e:
                    print(f"Erreur lecture email {email_id}: {e}")
        else:
            print("Aucun email trouvé de votre part dans la boîte de réception")
        
        # 2. Chercher dans MESSAGES ENVOYÉS
        print("\nTest de recherche dans MESSAGES ENVOYES...")
        try:
            mail.select('"[Gmail]/Sent Mail"')
            status, messages = mail.search(None, 'FROM', '"nathantechniquerd@gmail.com"')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"{len(email_ids)} emails trouvés de votre part dans Messages envoyés")
                
                # Prendre les 5 plus récents
                for email_id in email_ids[-5:]:
                    try:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        if status == 'OK':
                            import email
                            raw_email = msg_data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            
                            subject = msg.get('Subject', '')
                            from_addr = msg.get('From', '')
                            to_addr = msg.get('To', '')
                            date = msg.get('Date', '')
                            
                            print(f"Sujet: {subject}")
                            print(f"De: {from_addr}")
                            print(f"A: {to_addr}")
                            print(f"Date: {date}")
                            print("---")
                    except Exception as e:
                        print(f"Erreur lecture email {email_id}: {e}")
            else:
                print("Aucun email trouvé de votre part dans Messages envoyés")
        except Exception as e:
            print(f"Erreur accès Messages envoyés: {e}")
        
        # 3. Chercher les emails avec sujet "test" dans les deux dossiers
        print("\nTest de recherche avec sujet 'test'...")
        
        # Dans la boîte de réception
        mail.select('inbox')
        status, messages = mail.search(None, 'SUBJECT', 'test')
        if status == 'OK' and messages[0]:
            email_ids = messages[0].split()
            print(f"{len(email_ids)} emails trouvés avec sujet 'test' dans la boîte de réception")
        else:
            print("Aucun email trouvé avec sujet 'test' dans la boîte de réception")
        
        # Dans Messages envoyés
        try:
            mail.select('"[Gmail]/Sent Mail"')
            status, messages = mail.search(None, 'SUBJECT', 'test')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"{len(email_ids)} emails trouvés avec sujet 'test' dans Messages envoyés")
                
                for email_id in email_ids[-3:]:
                    try:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        if status == 'OK':
                            import email
                            raw_email = msg_data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            
                            subject = msg.get('Subject', '')
                            from_addr = msg.get('From', '')
                            to_addr = msg.get('To', '')
                            
                            print(f"Sujet: {subject}")
                            print(f"De: {from_addr}")
                            print(f"A: {to_addr}")
                            print("---")
                    except Exception as e:
                        print(f"Erreur lecture email {email_id}: {e}")
            else:
                print("Aucun email trouvé avec sujet 'test' dans Messages envoyés")
        except Exception as e:
            print(f"Erreur recherche 'test' dans Messages envoyés: {e}")
        
        # 4. Chercher avec sujet RD MENAGE
        print("\nTest de recherche avec sujet '[RD MENAGE]'...")
        
        # Dans la boîte de réception
        mail.select('inbox')
        status, messages = mail.search(None, 'SUBJECT', 'RD MENAGE')
        if status == 'OK' and messages[0]:
            email_ids = messages[0].split()
            print(f"{len(email_ids)} emails trouvés avec 'RD MENAGE' dans la boîte de réception")
            
            for email_id in email_ids[-3:]:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        import email
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        subject = msg.get('Subject', '')
                        from_addr = msg.get('From', '')
                        to_addr = msg.get('To', '')
                        
                        print(f"Sujet: {subject}")
                        print(f"De: {from_addr}")
                        print(f"A: {to_addr}")
                        print("---")
                except Exception as e:
                    print(f"Erreur lecture email {email_id}: {e}")
        else:
            print("Aucun email trouvé avec 'RD MENAGE' dans la boîte de réception")
        
        # Dans Messages envoyés
        try:
            mail.select('"[Gmail]/Sent Mail"')
            status, messages = mail.search(None, 'SUBJECT', 'RD MENAGE')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"{len(email_ids)} emails trouvés avec 'RD MENAGE' dans Messages envoyés")
                
                for email_id in email_ids[-3:]:
                    try:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        if status == 'OK':
                            import email
                            raw_email = msg_data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            
                            subject = msg.get('Subject', '')
                            from_addr = msg.get('From', '')
                            to_addr = msg.get('To', '')
                            
                            print(f"Sujet: {subject}")
                            print(f"De: {from_addr}")
                            print(f"A: {to_addr}")
                            print("---")
                    except Exception as e:
                        print(f"Erreur lecture email {email_id}: {e}")
            else:
                print("Aucun email trouvé avec 'RD MENAGE' dans Messages envoyés")
        except Exception as e:
            print(f"Erreur recherche 'RD MENAGE' dans Messages envoyés: {e}")
        
        mail.logout()
        
    except Exception as e:
        print(f"Erreur IMAP: {e}")

if __name__ == "__main__":
    test_imap_search()
