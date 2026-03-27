#!/usr/bin/env python
"""
Script de setup pour développement local
Crée virtualenv et installe les dépendances
"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, shell=True):
    """Exécute une commande"""
    print(f"\n▶ {cmd}")
    result = subprocess.run(cmd, shell=shell)
    if result.returncode != 0:
        print(f"❌ Erreur lors de l'exécution de: {cmd}")
        return False
    return True

def main():
    root = Path(__file__).parent
    
    print("=" * 60)
    print("🚀 SETUP - Formulaires de Contact & Devis")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ est requis")
        sys.exit(1)
    
    print("✓ Python", sys.version.split()[0])
    
    # Create virtualenv
    venv_path = root / "venv"
    if not venv_path.exists():
        print("\n📦 Création de l'environnement virtuel...")
        if not run_command(f"{sys.executable} -m venv venv"):
            sys.exit(1)
    else:
        print("\n✓ Environnement virtuel existe déjà")
    
    # Install dependencies
    pip_cmd = str(venv_path / ("Scripts" if os.name == 'nt' else "bin") / ("pip" if os.name == 'nt' else "pip"))
    if not run_command(f'"{pip_cmd}" install -r backend/requirements.txt'):
        sys.exit(1)
    
    # Create .env if not exists
    env_file = root / ".env"
    if not env_file.exists():
        print("\n📝 Création du fichier .env...")
        example = root / ".env.example"
        if example.exists():
            env_file.write_text(example.read_text())
        else:
            env_file.write_text("""GMAIL_USER=votre_email@gmail.com
GMAIL_PASSWORD=votre_mot_de_passe_app
RECIPIENT_EMAIL=votre_email@gmail.com
""")
        print("⚠️  Veuillez configurer .env avec vos identifiants Gmail")
    
    print("\n" + "=" * 60)
    print("✅ SETUP TERMINÉ!")
    print("=" * 60)
    print("\n📝 Prochaines étapes:")
    print("1. Configurez .env avec vos identifiants Gmail")
    print("2. Exécutez: python backend/main.py")
    print("3. Ouvrez: http://localhost:8000")
    print()

if __name__ == "__main__":
    main()
