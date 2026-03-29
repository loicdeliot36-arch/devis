import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Vérifier les messages récents
cursor.execute('SELECT id, nom, email, statut, reponse_admin FROM contact_messages ORDER BY id DESC LIMIT 5')
results = cursor.fetchall()

print("Messages récents:")
for r in results:
    id, nom, email, statut, reponse = r
    print(f"#{id} - {nom} ({email}) - {statut} - Rep: {'Oui' if reponse else 'Non'}")

conn.close()
