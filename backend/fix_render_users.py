import sqlite3
from pathlib import Path

def fix_render_users():
    """Corriger les utilisateurs sur Render avec des valeurs par défaut"""
    db_path = Path(__file__).parent / "database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== CORRECTION DES UTILISATEURS SUR RENDER ===")
    
    # Vérifier les colonnes existantes
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    print(f"Colonnes existantes: {columns}")
    
    # Ajouter les colonnes manquantes
    if 'telephone' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN telephone TEXT")
        print("✅ Colonne telephone ajoutée")
    
    if 'date_naissance' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN date_naissance DATE")
        print("✅ Colonne date_naissance ajoutée")
    
    if 'date_creation' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN date_creation DATETIME DEFAULT CURRENT_TIMESTAMP")
        print("✅ Colonne date_creation ajoutée")
    
    # Mettre à jour tous les utilisateurs avec des valeurs par défaut
    cursor.execute("""
        UPDATE users 
        SET 
            nom = COALESCE(nom, 'Utilisateur'),
            prenom = COALESCE(prenom, 'Test'),
            date_creation = COALESCE(date_creation, datetime('now'))
        WHERE nom IS NULL OR prenom IS NULL OR date_creation IS NULL
    """)
    
    # Vérifier les mises à jour
    cursor.execute("""
        SELECT id, email, nom, prenom, telephone, date_naissance, role 
        FROM users 
        ORDER BY id
    """)
    users = cursor.fetchall()
    
    print("\n=== UTILISATEURS APRÈS CORRECTION ===")
    for user in users:
        user_id, email, nom, prenom, telephone, date_naissance, role = user
        print(f"ID: {user_id}")
        print(f"  Email: {email}")
        print(f"  Nom: {nom}")
        print(f"  Prénom: {prenom}")
        print(f"  Téléphone: {telephone or 'Non défini'}")
        print(f"  Date naissance: {date_naissance or 'Non définie'}")
        print(f"  Rôle: {role}")
        print("  ---")
    
    # Statistiques
    cursor.execute("SELECT COUNT(*) FROM users WHERE nom IS NOT NULL AND prenom IS NOT NULL")
    valid_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    print(f"\n=== STATISTIQUES ===")
    print(f"Utilisateurs valides: {valid_users}/{total_users}")
    print(f"Taux de succès: {(valid_users/total_users)*100:.1f}%")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 CORRECTION TERMINÉE AVEC SUCCÈS!")
    print("📱 Le profil devrait maintenant fonctionner sur Render")

if __name__ == "__main__":
    fix_render_users()
