from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Formulaires de Contact")

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

# Gmail config
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", GMAIL_USER)

def send_email(subject: str, body: str, sender_email: str):
    """Envoie un email via Gmail"""
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject
        
        html_body = f"""
        <html>
            <body>
                <h2>{subject}</h2>
                <p><strong>De:</strong> {sender_email}</p>
                <hr>
                {body.replace(chr(10), '<br>')}
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, "html"))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erreur email: {e}")
        return False

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/contact")
def contact(data: FormSubmission):
    """Reçoit et envoie un formulaire de contact"""
    body = f"""
Nouveau formulaire de contact:

Nom: {data.nom} {data.prenom}
Téléphone: {data.telephone}
Email: {data.email}

Message:
{data.message}
    """
    
    if send_email(f"Nouveau contact - {data.nom} {data.prenom}", body, data.email):
        return {"success": True, "message": "Formulaire envoyé avec succès!"}
    else:
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi du email")

@app.post("/api/quote")
def quote(data: FormSubmission):
    """Reçoit et envoie une demande de devis"""
    body = f"""
Nouvelle demande de devis:

Nom: {data.nom} {data.prenom}
Téléphone: {data.telephone}
Email: {data.email}

Description du projet:
{data.message}
    """
    
    if send_email(f"Demande de devis - {data.nom} {data.prenom}", body, data.email):
        return {"success": True, "message": "Demande de devis envoyée!"}
    else:
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi du devis")

# Servir les fichiers statiques (frontend)
public_path = Path(__file__).parent.parent / "frontend"
if public_path.exists():
    app.mount("/", StaticFiles(directory=str(public_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
