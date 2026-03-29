#!/usr/bin/env python3
"""
Script de synchronisation pour Render
Exécuté toutes les 5 minutes via cron job
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from email_sync import sync_email_responses

def main():
    """Synchronisation pour Render"""
    print("🔄 Début synchronisation Render...")
    
    try:
        success = sync_email_responses()
        if success:
            print("✅ Synchronisation Render terminée avec succès")
        else:
            print("❌ Erreur lors de la synchronisation Render")
    except Exception as e:
        print(f"❌ Erreur critique Render: {e}")
    
    print("🏁 Fin synchronisation Render")

if __name__ == "__main__":
    main()
