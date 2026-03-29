import sqlite3
from auth import get_user_from_token
from fastapi import Request

# Simuler une requête avec un token
class MockRequest:
    def __init__(self, token):
        self.cookies = {"token": token}

# Test avec un token réel
print("Test de récupération utilisateur...")

# Récupérer le dernier utilisateur créé
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("SELECT id, nom, prenom, email FROM users ORDER BY id DESC LIMIT 1")
user_data = cursor.fetchone()
conn.close()

if user_data:
    user_id, nom, prenom, email = user_data
    print(f"Dernier utilisateur: {prenom} {nom} ({email})")
    
    # Créer un token test
    import jwt
    token = jwt.encode({"user_id": user_id}, "secret", algorithm="HS256")
    
    # Tester la récupération
    mock_request = MockRequest(token)
    user = get_user_from_token(mock_request)
    
    print(f"Utilisateur récupéré: {user}")
else:
    print("Aucun utilisateur trouvé")
