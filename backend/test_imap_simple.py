import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_imap_folders():
    """Test simple pour voir les dossiers disponibles"""
    try:
        # Connexion IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        
        print("=== LISTE DES DOSSIERS DISPONIBLES ===")
        status, folders = mail.list()
        if status == 'OK':
            for folder in folders:
                print(folder.decode('utf-8'))
        
        print("\n=== TEST BOITE DE RECEPTION ===")
        try:
            mail.select('inbox')
            status, messages = mail.search(None, 'ALL')
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"Emails dans la boîte de réception: {len(email_ids)}")
                
                # Prendre les 3 plus récents
                for email_id in email_ids[-3:]:
                    try:
                        status, msg_data = mail.fetch(email_id, '(BODY[HEADER])')
                        if status == 'OK':
                            import email
                            raw_email = msg_data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            
                            subject = msg.get('Subject', '')
                            from_addr = msg.get('From', '')
                            date = msg.get('Date', '')
                            
                            print(f"  Sujet: {subject}")
                            print(f"  De: {from_addr}")
                            print(f"  Date: {date}")
                            print("  ---")
                    except Exception as e:
                        print(f"  Erreur lecture email {email_id}: {e}")
            else:
                print("Aucun email dans la boîte de réception")
        except Exception as e:
            print(f"Erreur boîte de réception: {e}")
        
        mail.logout()
        
    except Exception as e:
        print(f"Erreur IMAP: {e}")

if __name__ == "__main__":
    test_imap_folders()
