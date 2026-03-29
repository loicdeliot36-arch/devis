import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Vérifier les infos de l'utilisateur
cursor.execute("SELECT id, nom, prenom, email, telephone, date_naissance FROM users WHERE email = 'nathanratte702@gmx.fr'")
user = cursor.fetchone()

if user:
    user_id, nom, prenom, email, telephone, date_naissance = user
    print("Informations actuelles de l'utilisateur:")
    print(f"ID: {user_id}")
    print(f"Nom: {nom}")
    print(f"Prenom: {prenom}")
    print(f"Email: {email}")
    print(f"Telephone: {telephone}")
    print(f"Date de naissance: {date_naissance}")
else:
    print("Utilisateur non trouvé")

conn.close()
