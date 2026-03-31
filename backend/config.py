# Configuration centralisée de l'application
import os
from pathlib import Path

# Configuration JWT
SECRET_KEY = "votre_cle_secrete_tres_securisee_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration base de données
DATABASE_PATH = "database.db"

# Configuration SMTP
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Configuration application
APP_NAME = "RD Ménage à Domicile"
APP_VERSION = "1.0.0"
DEBUG = True

# Configuration fichiers
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"
