from fastapi import Request
from fastapi.templating import Jinja2Templates
from auth import get_user_from_token
import sqlite3

# Simuler une requête avec token
class MockRequest:
    def __init__(self):
        self.cookies = {"token": "test_token"}

# Test direct de récupération utilisateur
def test_user_data():
    # Récupérer depuis la base directement
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = 'nathanratte702@gmx.fr'")
    user_data = cursor.fetchone()
    
    if user_data:
        columns = [desc[0] for desc in cursor.description]
        user_dict = dict(zip(columns, user_data))
        
        print("Données utilisateur brutes:")
        for key, value in user_dict.items():
            print(f"  {key}: {value}")
        
        print("\nDonnées formatées pour template:")
        formatted_user = {
            "id": user_dict.get("id"),
            "nom": user_dict.get("nom"),
            "prenom": user_dict.get("prenom"),
            "email": user_dict.get("email"),
            "telephone": user_dict.get("telephone"),
            "date_naissance": user_dict.get("date_naissance"),
            "role": user_dict.get("role")
        }
        
        for key, value in formatted_user.items():
            print(f"  {key}: {value}")
    
    conn.close()

test_user_data()
