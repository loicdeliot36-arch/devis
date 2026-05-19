# StreamVault

Application de **streaming personnelle** : ajoutez films et séries depuis l’interface en recherchant par nom sur **IMDB** (via l’API OMDb), puis associez vos fichiers vidéo locaux.

## Fonctionnalités

- Recherche par titre (film / série) → métadonnées IMDB : synopsis, acteurs, affiche, note, genre…
- Bibliothèque type Netflix (accueil, détail, lecteur vidéo)
- Upload de fichiers ou liaison d’un chemin local (`C:\Videos\…`)
- Séries : gestion par saison / épisode
- Streaming avec reprise (HTTP Range)

## Prérequis

- [Node.js](https://nodejs.org/) 18+ (aucun Python ni outil de compilation requis)
- Clé API OMDb gratuite : https://www.omdbapi.com/apikey.aspx

## Installation

```bash
cd streamvault
copy .env.example .env
# Éditez .env et mettez votre OMDB_API_KEY

npm run setup
```

## Version simple (ouvrir un port sur la box)

C’est **exactement** ça : vous ouvrez un port sur la box → il pointe vers votre PC → le site tourne sur ce port.

1. **Une fois** : `npm run setup` + fichier `.env` avec `ADMIN_PASSWORD=...`
2. **Quand vos potes veulent regarder** : double-cliquez `demarrer.bat` (ou `npm run share`) — **laissez la fenêtre ouverte**
3. **Box** : redirection **port externe** (ex. 8193) → **IP du PC** + **même port que dans `.env`** (ex. `PORT=3001`)
4. **Potes** : `http://VOTRE_IP_PUBLIQUE:8193`

`npm run share` n’est pas un truc bizarre : ça **construit le site** et le **lance sur un seul port**. Sans ça, rien n’écoute sur votre PC.

---

## Deux modes — pourquoi les ports changent

| Mode | Commande | Ports | Usage |
|------|----------|-------|--------|
| **Développement** | `npm run dev` | **5173** = site, **3001** = API | Chez vous pour coder |
| **Partage / potes** | `npm run share` | **Un seul port** (défaut 3001) = site + API + vidéos | Internet / box |

En `npm run share`, le serveur envoie **l’interface React et l’API** sur le **même port** (comme Netflix en production). Ce n’est pas « 3001 = API seulement ».

Vous pouvez mettre `PORT=5173` dans `.env` si vous voulez que ce port soit « le site » — redirigez alors la box vers **5173** en interne.

## Lancement (vous seul)

```bash
npm run dev
```

- Vous : http://localhost:5173 → **Connexion admin** avec `ADMIN_PASSWORD`

## Partager avec vos potes (réseau local)

1. Dans `.env` :
   ```
   ADMIN_PASSWORD=votre_mot_de_passe
   HOST=0.0.0.0
   ```

2. Lancez en mode partage (tout sur un seul port) :
   ```bash
   npm run share
   ```

3. Le terminal affiche une adresse **Réseau**, ex. `http://192.168.1.42:3001`  
   → Envoyez ce lien à vos potes (même Wi‑Fi).

4. **Vous** : ouvrez le lien → **Connexion admin** → ajoutez les films.  
   **Vos potes** : ouvrent le même lien → badge **Invité** → regardent seulement.

Les potes ne peuvent pas ajouter, supprimer ni uploader (bloqué côté serveur).

### Pare-feu Windows

Autorisez Node.js sur le réseau privé si Windows demande.

## Amis à distance (pas chez vous)

Deux méthodes. **Le mode `npm run share` est obligatoire** (un seul port, ex. 3001).

### Méthode A — Tunnel (le plus simple, sans toucher à la box)

1. Terminal 1 :
   ```bash
   npm run share
   ```
2. Terminal 2 :
   ```bash
   npm run tunnel
   ```
3. Localtunnel affiche une URL du type `https://xxxx.loca.lt` → **envoyez ce lien** à vos potes.
4. Votre PC doit rester allumé avec les deux commandes qui tournent.

Pas d’ouverture de port sur la box. Gratuit, mais l’URL change à chaque fois (sauf compte payant).

### Méthode B — Ouvrir un port sur la box (redirection NAT)

1. `.env` : `ADMIN_PASSWORD=...` et `HOST=0.0.0.0`
2. `npm run share`
3. **IP locale du PC** (PowerShell) : `ipconfig` → ex. `192.168.1.42`
4. **Pare-feu Windows** : autoriser le port **3001** entrant pour Node.js
5. **Box internet** (Freebox, Livebox, SFR…) :
   - Paramètres → NAT / Redirection de ports / Port forwarding
   - Créer une règle : **TCP**, port externe **3001** → IP locale **192.168.1.42**, port interne **3001**
6. **IP publique** : cherchez « mon ip » sur Google → ex. `88.123.45.67`
7. Lien pour vos potes : `http://88.123.45.67:3001`

Si ça ne marche pas : votre FAI utilise peut‑être la **CGNAT** (pas d’IP publique directe) → utilisez la **méthode A (tunnel)** ou **Tailscale**.

### Sécurité (important sur Internet)

- Mettez un **mot de passe admin fort** dans `.env` — ne le donnez **jamais** à vos potes
- Seuls les invités ont besoin du lien ; ils ne peuvent pas ajouter de films
- C’est du HTTP (pas HTTPS) : ne partagez pas de données bancaires sur ce serveur
- Coupez `npm run share` quand vous n’en avez plus besoin

### Tailscale (alternative très fiable)

Installez [Tailscale](https://tailscale.com/) sur votre PC et chez chaque pote : ils accèdent à `http://100.x.x.x:3001` (IP Tailscale de votre PC) sans ouvrir la box. Gratuit pour usage perso.

## Utilisation

1. Cliquez sur **+ Ajouter**
   - **Lien IMDB** : `https://www.imdb.com/title/tt1375666/` ou l’id `tt1375666`
   - **Recherche** : tapez le nom du film ou de la série
2. Sur la fiche du média, associez la vidéo :
   - upload de fichier
   - chemin local : `C:\Videos\mon-film.mkv`
   - **URL directe** : `https://serveur.com/video.mp4` (fichier vidéo accessible en HTTP, pas YouTube)
3. Pour une série, renseignez saison / épisode avant chaque source
4. Lancez la lecture depuis l’accueil ou la fiche détail

## Structure

```
streamvault/
├── server/          # API Express + SQLite + streaming
├── client/          # Interface React (Vite)
├── data/            # Bibliothèque JSON (créée au 1er lancement)
└── uploads/         # Vidéos uploadées via l’interface
```
