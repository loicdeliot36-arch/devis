import sqlite3
import os
from pathlib import Path

# Chemin de la base de données
DB_PATH = Path(__file__).parent / "database.db"

def get_db():
    """Connexion à la base de données"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialisation de la base de données avec les tables et l'admin par défaut"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Table users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            nom TEXT,
            prenom TEXT
        )
    ''')
    
    # Ajouter les colonnes nom et prenom si elles n'existent pas
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN nom TEXT')
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN prenom TEXT')
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    
    # Table contacts (ancienne)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT NOT NULL,
            telephone TEXT,
            message TEXT NOT NULL,
            date TEXT NOT NULL,
            traite INTEGER DEFAULT 0
        )
    ''')
    
    # Nouvelle table contact_messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT NOT NULL,
            telephone TEXT,
            message TEXT NOT NULL,
            date_creation TEXT NOT NULL,
            statut TEXT DEFAULT 'non_traite',
            reponse_admin TEXT,
            date_reponse TEXT
        )
    ''')
    
    # Vérifier si l'admin existe déjà
    cursor.execute('SELECT id FROM users WHERE email = ?', ('nathanratte702@gmx.fr',))
    admin_exists = cursor.fetchone()
    
    if not admin_exists:
        # Importer bcrypt ici pour éviter les imports circulaires
        import bcrypt
        password_hash = bcrypt.hashpw('Nathan24@'.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute('''
            INSERT INTO users (email, password_hash, role)
            VALUES (?, ?, ?)
        ''', ('nathanratte702@gmx.fr', password_hash.decode('utf-8'), 'admin'))
    
    conn.commit()
    conn.close()

# Initialiser la base de données au démarrage
if not DB_PATH.exists():
    init_db()
else:
    # Vérifier que les tables existent
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    if 'users' not in tables or 'contacts' not in tables:
        init_db()
    
    conn.close()
