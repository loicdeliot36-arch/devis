import os
from pathlib import Path
from dotenv import load_dotenv
import resend

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr

# Import des routers
from routers import public, auth, admin, messages, api, admin_management, auth_public, diagnostic, desktop, google_reviews, sync_google, real_google_reviews, test_auth, auth_emails

# Import de la base de données
from database import init_db
from auth import get_user_from_token

load_dotenv()

# Initialisation de la base de données
init_db()

# Init FastAPI
app = FastAPI(
    title="RD Ménage à Domicile",
    description="Services de ménage à domicile",
    version="2.0"
)

# Configuration des templates
templates = Jinja2Templates(directory="templates")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model
class FormSubmission(BaseModel):
    nom: str
    prenom: str
    telephone: str
    email: EmailStr
    message: str

# Resend config (pour les emails)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Inclusion des routers
app.include_router(public.router, tags=["public"])
app.include_router(auth.router, tags=["auth"])
app.include_router(admin.router, tags=["admin"], prefix="/admin")
app.include_router(messages.router, tags=["messages"])
app.include_router(api.router, tags=["api"])
app.include_router(admin_management.router, tags=["admin_management"])
app.include_router(auth_public.router, tags=["auth_public"])
app.include_router(diagnostic.router, tags=["diagnostic"])
app.include_router(google_reviews.router, tags=["google_reviews"])
app.include_router(sync_google.router, tags=["sync_google"])
app.include_router(real_google_reviews.router, tags=["real_google_reviews"])
app.include_router(test_auth.router, tags=["test_auth"])
app.include_router(auth_emails.router, tags=["auth_emails"])
app.include_router(desktop.router, tags=["desktop"])
# Le router desktop est maintenant intégré dans public.py

# Servir les fichiers statiques
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Servir le frontend pour compatibilité avec les appels API
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


def send_email(subject: str, body: str, sender_email: str):
    """Envoie un email via Resend (compatible Render)"""
    try:
        html_body = f"""
        <html>
            <body>
                <h2>{subject}</h2>
                <p><strong>De :</strong> {sender_email}</p>
                <p><strong>Téléphone :</strong> inclus dans le message</p>
                <hr>
                {body.replace(chr(10), '<br>')}
            </body>
        </html>
        """

        params = {
            "from": "Formulaire <onboarding@resend.dev>",
            "to": [RECIPIENT_EMAIL],
            "subject": subject,
            "html": html_body,
        }

        resend.Emails.send(params)
        return True

    except Exception as e:
        print("Erreur email (Resend):", e)
        return False


# Page de contact existante (conservée pour compatibilité)
@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Page de contact (version existante)"""
    user = get_user_from_token(request)
    print(f"Utilisateur trouvé sur contact: {user}")
    
    # Utiliser le template du backend avec la logique de connexion
    return templates.TemplateResponse("contact.html", {"request": request, "user": user})

@app.get("/health")
def health():
    """Health check pour Render"""
    return {"status": "ok", "app": "RD Ménage à Domicile V2"}

# Route par défaut
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Page d'accueil"""
    print("=== PAGE D'ACCUEIL ===")
    user = get_user_from_token(request)
    print(f"Utilisateur trouvé: {user}")
    
    # Utiliser le template du backend avec la logique de connexion
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

# Gestion des erreurs
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
