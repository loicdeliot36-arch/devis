import sqlite3

# Mettre à jour le premier utilisateur admin
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Mettre à jour avec des valeurs de test
cursor.execute("""
    UPDATE users 
    SET nom = 'Test', prenom = 'Admin' 
    WHERE email = 'nathanratte702@gmx.fr'
""")

conn.commit()

# Vérifier
cursor.execute("SELECT id, nom, prenom, email, role FROM users WHERE email = 'nathanratte702@gmx.fr'")
user = cursor.fetchone()

if user:
    user_id, nom, prenom, email, role = user
    print(f"Utilisateur mis à jour: #{user_id} - {prenom} {nom} ({email}) - {role}")
else:
    print("Utilisateur non trouvé")

conn.close()
