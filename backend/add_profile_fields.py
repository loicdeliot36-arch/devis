import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Ajouter les colonnes manquantes si elles n'existent pas
try:
    # Vérifier si les colonnes existent
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'date_naissance' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN date_naissance DATE")
        print("Colonne date_naissance ajoutee")
    
    if 'telephone' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN telephone TEXT")
        print("Colonne telephone ajoutee")
    
    if 'date_creation' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN date_creation DATETIME")
        print("Colonne date_creation ajoutee")
    
    conn.commit()
    print("Base de données mise à jour avec succès!")
    
except Exception as e:
    print(f"Erreur: {e}")
finally:
    conn.close()
