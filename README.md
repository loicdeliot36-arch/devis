# Formulaires de Contact & Devis avec Gmail

Application web minimaliste pour gérer les demandes de contact et devis via formulaires HTML, avec envoi d'emails via Gmail.

## 🚀 Démarrage Local

### Prérequis
- Python 3.11+
- pip

### Configuration

1. **Cloner/Télécharger le projet**
```bash
cd formulaires-contact
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r backend/requirements.txt
```

4. **Configurer Gmail** (IMPORTANT)

   a. Activer l'authentification 2FA sur votre compte Google
   
   b. Générer un "mot de passe d'application" :
      - Aller sur : https://myaccount.google.com/apppasswords
      - Sélectionner "Mail" et "Windows"
      - Copier le mot de passe généré
   
   c. Créer un fichier `.env` à la racine du projet :
   ```env
   GMAIL_USER=votre_email@gmail.com
   GMAIL_PASSWORD=xxxx xxxx xxxx xxxx
   RECIPIENT_EMAIL=votre_email@gmail.com
   ```

5. **Lancer l'application**
```bash
cd backend
python main.py
```

Ouvrir : http://localhost:8000

## 📦 Déploiement sur Fly.io

### Prérequis
- Compte [Fly.io](https://fly.io)
- CLI Fly.io installée : `brew install flyctl` (Mac) ou [installer depuis le site](https://fly.io/docs/hands-on/install-flyctl/)

### Déploiement

1. **Configurer les secrets**
```bash
flyctl secrets set GMAIL_USER=votre_email@gmail.com
flyctl secrets set GMAIL_PASSWORD=xxxx_xxxx_xxxx_xxxx
flyctl secrets set RECIPIENT_EMAIL=votre_email@gmail.com
```

2. **Déployer**
```bash
flyctl launch
# Suivre les instructions (app name, region, etc.)
# Répondre "no" si asked to deploy now
```

3. **Déployer l'app**
```bash
flyctl deploy
```

4. **Voir les logs**
```bash
flyctl logs
```

5. **Accéder à l'app**
```bash
flyctl open
```

## 🔧 Architecture

```
.
├── backend/
│   ├── main.py           # API FastAPI + serveur statiques
│   └── requirements.txt   # Dépendances Python
├── frontend/
│   └── index.html        # Formulaires (HTML/CSS/JS)
├── Dockerfile            # Configuration Docker
├── fly.toml             # Configuration Fly.io
└── .env.example         # Template des variables d'env
```

## 📝 Endpoints API

### POST /api/contact
```json
{
  "nom": "Dupont",
  "prenom": "Jean",
  "telephone": "+33612345678",
  "email": "jean@example.com",
  "message": "Texte du message"
}
```

### POST /api/quote
```json
{
  "nom": "Dupont",
  "prenom": "Jean",
  "telephone": "+33612345678",
  "email": "jean@example.com",
  "message": "Description du projet"
}
```

## 🎨 Customisation du Frontend

Modifier `frontend/index.html` pour :
- Changer les couleurs (variables CSS en haut)
- Ajouter/modifier les champs du formulaire
- Changer les labels et messages

## 🐛 Dépannage

### "Erreur lors de l'envoi du email"
- Vérifier les identifiants Gmail dans `.env`
- Vérifier que l'authentification 2FA est activée
- Vérifier que le mot de passe d'application est correct
- Attendre quelques secondes après la génération du mot de passe

### "Port 8000 déjà utilisé"
Modifier `main.py` ligne 104:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Emails ne s'envoient pas en production
- Vérifier les logs : `flyctl logs`
- Vérifier les secrets : `flyctl secrets list`

## 📧 Configuration Gmail Alternative : OAuth2 (Optionnel)

Si vous avez besoin de plus de sécurité, utiliser OAuth2 au lieu de mots de passe d'application.
Contactez pour un guide détaillé.

## 📄 Licence

MIT - Libre d'utilisation

## 🤝 Support

Besoin d'aide ? Vérifiez les logs ou consultez la documentation de Fly.io.
