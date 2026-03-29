import sqlite3

# Vérifier les utilisateurs
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("Utilisateurs dans la base:")
cursor.execute("SELECT id, nom, prenom, email, role FROM users")
users = cursor.fetchall()

for user in users:
    user_id, nom, prenom, email, role = user
    print(f"#{user_id}: {prenom} {nom} ({email}) - {role}")

print(f"\nTotal: {len(users)} utilisateurs")

conn.close()
