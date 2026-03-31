import sqlite3
import jwt
from datetime import datetime, timedelta

# Importer la configuration centralisée
from config import SECRET_KEY, ALGORITHM

def create_test_token():
    """Créer un token de test"""
    token_data = {"sub": "nathanratte702@gmx.fr"}
    expire = datetime.utcnow() + timedelta(hours=1)
    token_data.update({"exp": expire})
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def test_token_decode():
    """Test le décodage du token"""
    token = create_test_token()
    print(f"Token créé: {token}")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Payload décodé: {payload}")
        print(f"Email: {payload.get('sub')}")
        print("Token valide !")
        return True
    except Exception as e:
        print(f"Erreur de décodage: {e}")
        return False

def test_user_db():
    """Test la récupération de l'utilisateur en base"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, nom, prenom, role FROM users WHERE email = ?", 
                   ("nathanratte702@gmx.fr",))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_dict = {
            "id": user[0],
            "email": user[1], 
            "nom": user[2],
            "prenom": user[3],
            "role": user[4]
        }
        print(f"Utilisateur trouvé: {user_dict}")
        return user_dict
    else:
        print("Utilisateur non trouvé")
        return None

if __name__ == "__main__":
    print("=== TEST SESSION ===")
    
    # Test token
    token_ok = test_token_decode()
    
    # Test utilisateur
    user = test_user_db()
    
    if token_ok and user:
        print("\nSession fonctionnelle !")
    else:
        print("\nProblème de session détecté")
