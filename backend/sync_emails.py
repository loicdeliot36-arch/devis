#!/usr/bin/env python3
"""
Script de synchronisation des emails
À exécuter périodiquement pour synchroniser les réponses par email
"""

import schedule
import time
from email_sync import sync_email_responses

def main():
    print("🚀 Démarrage du service de synchronisation des emails...")
    
    # Planifier la synchronisation toutes les 5 minutes
    schedule.every(5).minutes.do(sync_email_responses)
    
    # Exécuter une fois au démarrage
    sync_email_responses()
    
    print("⏰ Synchronisation programmée toutes les 5 minutes")
    print("🔄 En attente des prochains cycles...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt du service de synchronisation")

if __name__ == "__main__":
    main()
