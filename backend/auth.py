import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends, Request
from jose import JWTError, jwt
import sqlite3
from pathlib import Path

# Configuration
SECRET_KEY = "votre-secret-key-tres-securisee-a-changer-en-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Génère un hash pour le mot de passe"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_from_token(request: Request):
    """Récupère l'utilisateur depuis le token JWT"""
    try:
        # Récupérer le token depuis les cookies
        token = request.cookies.get("access_token")
        if not token:
            return None
            
        # Décoder le token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
            
        # Récupérer l'utilisateur depuis la base de données
        db_path = Path(__file__).parent / "database.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user is None:
            return None
            
        return dict(user)
    except Exception as e:
        print(f"Erreur get_user_from_token: {e}")
        return None

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authentifie un utilisateur et retourne ses infos"""
    db_path = Path(__file__).parent / "database.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return None
    
    if not verify_password(password, user["password_hash"]):
        return None
    
    return dict(user)
