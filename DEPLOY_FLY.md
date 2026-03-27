# 🚀 GUIDE RAPIDE - DÉPLOIEMENT SUR FLY.IO

## Étape 1️⃣ - Installation de Fly CLI

```bash
# MacOS/Linux
brew install flyctl

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Ou télécharger depuis: https://fly.io/docs/hands-on/install-flyctl/
```

## Étape 2️⃣ - Login Fly.io

```bash
flyctl auth login
# Suivre les instructions (créer un compte si nécessaire)
```

## Étape 3️⃣ - Initialiser l'app

```bash
flyctl launch
```

Répondre aux questions:
- **App Name**: Votre choix (ex: `formulaires-contact`)
- **Region**: `cdg` (France) ou autre proche de vous
- **Deploy now?**: Répondre `no` (on va configurer d'abord)

## Étape 4️⃣ - Configurer les secrets Gmail

⚠️ **IMPORTANT**: Générer un "mot de passe d'application" depuis:
https://myaccount.google.com/apppasswords

```bash
# Remplacer par VOS identifiants Gmail
flyctl secrets set GMAIL_USER=votre_email@gmail.com
flyctl secrets set GMAIL_PASSWORD=xxxx xxxx xxxx xxxx
flyctl secrets set RECIPIENT_EMAIL=votre_email@gmail.com
```

Vérifier:
```bash
flyctl secrets list
```

## Étape 5️⃣ - Déployer!

```bash
flyctl deploy
```

⏳ Attendre 2-3 minutes...

## Étape 6️⃣ - Accéder à l'app

```bash
flyctl open
```

Ou manuellement: https://VOTRE_APP_NAME.fly.dev

## 📊 Commandes utiles

```bash
# Voir les logs en direct
flyctl logs

# Voir le statut de l'app
flyctl status

# Redéployer après modifications
flyctl deploy

# Accéder au shell de l'app (debug)
flyctl ssh console

# Arrêter/Démarrer l'app
flyctl apps stop formulaires-contact
flyctl apps start formulaires-contact

# Voir les variables d'environnement
flyctl secrets list

# Mettre à jour un secret
flyctl secrets set GMAIL_USER=nouveau_email@gmail.com
```

## 🐛 Dépannage

### "Erreur lors de l'envoi du email"

1. Vérifier que Gmail 2FA est ACTIVÉ
2. Vérifier le mot de passe d'application (https://myaccount.google.com/apppasswords)
3. Vérifier les secrets: `flyctl secrets list`
4. Voir les logs: `flyctl logs`

### "Port déjà utilisé"

La configuration Fly.io gère automatiquement les ports. Pas de souci!

### "Build échoue"

Vérifier les logs du build:
```bash
flyctl logs
```

Souvent c'est un problème de dépendance. Vérifier `backend/requirements.txt`

## 📝 Modifier l'app après déploiement

1. Modifier les fichiers localement
2. Exécuter: `flyctl deploy`
3. C'est tout!

## 💾 Sauvegarde des formulaires

⚠️ Cette app n'enregistre PAS les formulaires. Elle les envoie directement par email.

Si vous voulez garder un dossier des envois:
- Les emails reçus par Gmail les enregistrent automatiquement
- Option future: ajouter une base de données PostgreSQL gratuitement sur Fly.io

## 🎯 Prochaines étapes

- Tester les formulaires
- Personnaliser les couleurs dans `frontend/index.html`
- Ajouter des champs personnalisés
- Configurer un domaine personnalisé (optionnel)

---

**Besoin d'aide?** → [Documentation Fly.io](https://fly.io/docs)
