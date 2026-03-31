import jwt
from datetime import datetime, timedelta

SECRET_KEY = "votre_cle_secrete_tres_securisee_2024"

def create_access_token(data: dict):
    """Créer un token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def test_token():
    """Test la création et décodage de token"""
    print("=== TEST TOKEN ===")
    
    # Créer un token
    token_data = {"sub": "nathanratte702@gmx.fr"}
    token = create_access_token(token_data)
    print(f"Token créé: {token}")
    
    # Décoder le token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(f"Payload: {payload}")
        print(f"Email: {payload.get('sub')}")
        print("Token valide !")
    except Exception as e:
        print(f"Erreur de décodage: {e}")

if __name__ == "__main__":
    test_token()
