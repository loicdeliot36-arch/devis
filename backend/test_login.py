import sqlite3
import bcrypt
from pathlib import Path

def test_login():
    """Test la connexion avec les identifiants existants"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Vérifier les utilisateurs existants
    cursor.execute("SELECT email, password_hash, nom, prenom, role FROM users")
    users = cursor.fetchall()
    
    print("=== UTILISATEURS EXISTANTS ===")
    for user in users:
        email, password_hash, nom, prenom, role = user
        print(f"Email: {email}")
        print(f"Nom: {nom} {prenom}")
        print(f"Rôle: {role}")
        print("---")
    
    # Test de connexion avec l'admin
    admin_email = "nathanratte702@gmx.fr"
    admin_password = "Nathan24@"
    
    cursor.execute("SELECT password_hash FROM users WHERE email = ?", (admin_email,))
    result = cursor.fetchone()
    
    if result:
        stored_hash = result[0]
        print(f"\n=== TEST CONNEXION ADMIN ===")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        
        if bcrypt.checkpw(admin_password.encode('utf-8'), stored_hash.encode('utf-8')):
            print("Connexion reussie !")
        else:
            print("Mot de passe incorrect")
            
            # Test avec un autre mot de passe
            test_passwords = ["admin", "password", "123456", "test", "Nathan24@"]
            for pwd in test_passwords:
                if bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8')):
                    print(f"Le bon mot de passe est: {pwd}")
                    break
            else:
                print("Aucun des mots de passe testés ne fonctionne")
    else:
        print(f"Utilisateur {admin_email} non trouve")
    
    conn.close()

if __name__ == "__main__":
    test_login()
