# RD Ménage à Domicile - V2

Application web complète pour les services de ménage à domicile avec authentification et administration.

## 🚀 Fonctionnalités

### Pages publiques
- **Page d'accueil** : Présentation des services avec design inspiré du flyer
- **Page de contact** : Formulaire de contact et demande de devis (existante)

### Authentification
- **Inscription** : Création de compte utilisateur
- **Connexion** : Accès sécurisé avec JWT
- **Déconnexion** : Session sécurisée

### Espace utilisateur
- **Dashboard** : Accueil personnel avec liens utiles
- **Espace admin** : Gestion des messages de contact (réservé aux admins)

### Base de données
- **SQLite** : Base de données locale
- **Tables** : users, contacts
- **Admin par défaut** : nathanratte702@gmx.fr / Nathan24@

## 🎨 Design

Le site reprend les couleurs du flyer :
- **Bleu principal** : #2a4d8f
- **Blanc** : #ffffff  
- **Gris clair** : #f5f7fb
- **Style** : Propre, carré, professionnel

## 📁 Structure du projet

```
backend/
├── main.py              # Application FastAPI principale
├── database.py          # Configuration de la base de données
├── models.py            # Modèles Pydantic
├── auth.py              # Logique d'authentification
├── requirements.txt     # Dépendances Python
├── render.yaml          # Configuration Render
├── routers/
│   ├── __init__.py
│   ├── public.py        # Routes publiques
│   ├── auth.py          # Routes d'authentification
│   └── admin.py         # Routes d'administration
├── templates/
│   ├── base.html        # Template de base
│   ├── index.html       # Page d'accueil
│   ├── login.html       # Page de connexion
│   ├── register.html    # Page d'inscription
│   ├── dashboard.html   # Dashboard utilisateur
│   └── admin.html       # Espace admin
└── static/
    └── style.css        # Styles CSS
```

## 🛠️ Installation locale

### Prérequis
- Python 3.11+
- pip

### Installation
```bash
# Cloner le projet
cd devis-main/backend

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Accès
- **Site web** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Health check** : http://localhost:8000/health

## 🔑 Comptes

### Admin par défaut
- **Email** : nathanratte702@gmx.fr
- **Mot de passe** : Nathan24@
- **Rôle** : admin

### Créer un compte utilisateur
1. Aller sur http://localhost:8000/register
2. Remplir le formulaire d'inscription
3. Se connecter sur http://localhost:8000/login

## 🌐 Déploiement sur Render

### Prérequis
- Compte Render
- Repository GitHub avec le code

### Configuration
1. **Créer un nouveau Web Service** sur Render
2. **Connecter le repository** GitHub
3. **Configuration** :
   - Runtime : Python 3
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Variables d'environnement** :
   - `RESEND_API_KEY` : Clé API Resend
   - `RECIPIENT_EMAIL` : Email de réception des formulaires

### Déploiement automatique
Chaque push sur la branche principale déclenche un redéploiement automatique.

## 📧 Configuration Email

Le site utilise Resend pour l'envoi d'emails (compatible Render) :

1. **Créer un compte Resend** : https://resend.com
2. **Générer une clé API**
3. **Configurer les variables d'environnement** :
   - `RESEND_API_KEY` : Votre clé API Resend
   - `RECIPIENT_EMAIL` : Email où recevoir les messages

## 🔧 Routes API

### Publiques
- `GET /` : Page d'accueil
- `GET /contact` : Page de contact (existante)
- `POST /api/contact` : Soumission formulaire contact
- `POST /api/quote` : Soumission demande de devis

### Authentification
- `GET /login` : Page de connexion
- `POST /login` : Traitement connexion
- `GET /register` : Page d'inscription
- `POST /register` : Traitement inscription
- `GET /logout` : Déconnexion

### Protégées
- `GET /dashboard` : Tableau de bord utilisateur
- `GET /admin` : Espace administration (admin uniquement)
- `POST /admin/mark-treated/{id}` : Marquer message comme traité
- `POST /admin/delete/{id}` : Supprimer un message

## 🎯 Fonctionnalités principales

### Page d'accueil
- Présentation de Rachel Demange
- Services de ménage à domicile
- Mise en avant : "50% de réduction d'impôt"
- Bouton "Demander un devis"
- Design professionnel aux couleurs du flyer

### Espace admin
- Liste des messages de contact
- Statuts (traité/non traité)
- Actions (marquer traité, supprimer)
- Statistiques en temps réel

### Sécurité
- Tokens JWT sécurisés
- Hash des mots de passe (bcrypt)
- Protection des routes par rôle
- Sessions via cookies sécurisés

## 🐛 Dépannage

### Erreur de base de données
```bash
# Supprimer la base de données pour la recréer
rm database.db
# Relancer l'application
uvicorn main:app --reload
```

### Problème d'imports
```bash
# Vérifier la structure des dossiers
ls -la routers/
# Le fichier __init__.py doit exister
```

### Emails non envoyés
- Vérifier les variables d'environnement
- Valider la clé API Resend
- Consulter les logs Render

## 📄 Licence

MIT - Libre d'utilisation

## 🤝 Support

Pour toute question ou problème :
- Consulter les logs de l'application
- Vérifier la configuration des variables d'environnement
- Tester localement avant le déploiement
