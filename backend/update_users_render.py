import sqlite3
from pathlib import Path

def update_users_for_render():
    """Mettre à jour les utilisateurs existants avec des valeurs par défaut"""
    db_path = Path(__file__).parent / "database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Mise à jour des utilisateurs pour Render...")
    
    # Mettre à jour les utilisateurs avec nom/prenom vides
    cursor.execute("""
        UPDATE users 
        SET nom = 'Utilisateur', prenom = 'Test' 
        WHERE nom IS NULL OR prenom IS NULL
    """)
    
    # Ajouter les colonnes manquantes si besoin
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN telephone TEXT")
        print("✅ Colonne telephone ajoutée")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN date_naissance DATE")
        print("✅ Colonne date_naissance ajoutée")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN date_creation DATETIME DEFAULT CURRENT_TIMESTAMP")
        print("✅ Colonne date_creation ajoutée")
    except:
        pass
    
    # Mettre à jour les dates de création
    cursor.execute("""
        UPDATE users 
        SET date_creation = datetime('now') 
        WHERE date_creation IS NULL
    """)
    
    # Vérifier les utilisateurs
    cursor.execute("SELECT id, email, nom, prenom, role FROM users")
    users = cursor.fetchall()
    
    print("\nUtilisateurs mis à jour:")
    for user in users:
        user_id, email, nom, prenom, role = user
        print(f"#{user_id}: {email} - {prenom} {nom} ({role})")
    
    conn.commit()
    conn.close()
    print("\n🎉 Mise à jour terminée!")

if __name__ == "__main__":
    update_users_for_render()
