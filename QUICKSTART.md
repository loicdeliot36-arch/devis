# ⚡ DÉMARRAGE RAPIDE (5 MINUTES)

## 🎯 Objectif
Application web avec 2 formulaires (Contact + Devis) qui envoient des emails via Gmail.

## 📋 Prérequis
- ✅ Python 3.11+ (vérifier: `python --version`)
- ✅ Compte Gmail avec 2FA activé

## 🚀 Étape 1 : Setup (2 min)

### Windows
```powershell
python setup.py
```

### Mac/Linux
```bash
python3 setup.py
```

## 🔐 Étape 2 : Configuration Gmail (2 min)

1. Aller sur: https://myaccount.google.com/apppasswords
2. Dans la popup:
   - **Sélectionner une app**: Mail
   - **Sélectionner un appareil**: Windows (ou votre OS)
3. Cliquer "Générer"
4. Copier le mot de passe généré (ex: `xxxx xxxx xxxx xxxx`)

5. Ouvrir le fichier `.env` à la racine du projet
6. Remplir:
```env
GMAIL_USER=votre_email@gmail.com
GMAIL_PASSWORD=xxxx xxxx xxxx xxxx
RECIPIENT_EMAIL=votre_email@gmail.com
```

7. Sauvegarder

## ▶️ Étape 3 : Lancer (1 min)

### Windows
```powershell
.\run.ps1
```

### Mac/Linux
```bash
source venv/bin/activate
cd backend
python main.py
```

## 🌐 Étape 4 : Tester (30 sec)

Ouvrir votre navigateur: **http://localhost:8000**

Vous devriez voir 2 formulaires côte à côte:
- ✉️ Formulaire de Contact
- 📋 Demande de Devis

Remplissez et cliquez "Envoyer" → un email doit arriver dans votre boîte Gmail!

## 🎨 Customisation rapide

Fichier à modifier: `frontend/index.html`

### Changer les couleurs
Au début du `<style>`:
```css
:root {
    --primary: #2563eb;        /* Bleu principal */
    --success: #16a34a;        /* Vert */
    --error: #dc2626;          /* Rouge */
}
```

### Ajouter des champs
Dans le formulaire, copier:
```html
<div class="form-group">
    <label for="contact-nom">Mon Champ *</label>
    <input type="text" id="contact-nom" name="mon_champ" required>
</div>
```

Puis dans `backend/main.py`, ajouter au `FormSubmission`:
```python
class FormSubmission(BaseModel):
    nom: str
    prenom: str
    mon_champ: str  # ← AJOUTER ICI
```

## 📦 Déployer sur Fly.io

Lire: [DEPLOY_FLY.md](DEPLOY_FLY.md)

Commande rapide:
```bash
flyctl auth login
flyctl launch
flyctl secrets set GMAIL_USER=...
flyctl secrets set GMAIL_PASSWORD=...
flyctl deploy
```

## ❌ Dépannage rapide

### "Python command not found"
→ Installer Python depuis https://www.python.org
→ Cocher "Add Python to PATH"
→ Redémarrer le terminal

### "Email error"
→ Vérifier 2FA Gmail est activé
→ Vérifier mot de passe d'application
→ Vérifier le fichier `.env` est correct

### "Virtualenv not found"
→ Exécuter: `python setup.py`

### "Port 8000 already in use"
→ Modifier `backend/main.py` ligne ~104:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Changer 8000 en 8001
```

## 📁 Structure du projet

```
formulaires-contact/
├── backend/
│   ├── main.py               # Votre API
│   └── requirements.txt
├── frontend/
│   └── index.html            # Les formulaires
├── .env                      # Vos identifiants (⚠️ PRIVÉ)
├── .env.example              # Template
├── Dockerfile                # Pour déployer
├── fly.toml                  # Config Fly.io
└── README.md                 # Documentation complète
```

## 🔗 Ressources

| Lien | Description |
|------|-------------|
| http://localhost:8000 | Votre app locale |
| http://localhost:8000/docs | API documentation (Swagger) |
| https://myaccount.google.com/apppasswords | Générer mot de passe app |
| https://fly.io/docs | Documentation Fly.io |

## ✅ Checklist

- [ ] Python 3.11+ installé
- [ ] Gmail 2FA activé
- [ ] Mot de passe d'application généré
- [ ] Fichier `.env` rempli
- [ ] `python setup.py` exécuté
- [ ] `.\run.ps1` lance l'app
- [ ] Formulaires chargent sur http://localhost:8000
- [ ] Un email reçu après soumission

## 🎉 Bravo!

Votre application de formulaires est prête! 

**Prochaines étapes:**
1. Tester les formulaires
2. Customiser les couleurs/champs au besoin
3. Déployer sur Fly.io (voir DEPLOY_FLY.md)

---

Besoin d'aide? Vérifiez [README.md](README.md)
