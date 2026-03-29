import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Vérifier les réponses synchronisées
cursor.execute('SELECT id, nom, email, reponse_admin, date_reponse FROM contact_messages WHERE reponse_admin IS NOT NULL ORDER BY id DESC LIMIT 3')
results = cursor.fetchall()

print("Réponses synchronisées:")
for r in results:
    id, nom, email, reponse, date_rep = r
    print(f"#{id} - {nom} ({email})")
    print(f"  Réponse: {reponse[:100]}...")
    print(f"  Date: {date_rep}")
    print("---")

conn.close()
