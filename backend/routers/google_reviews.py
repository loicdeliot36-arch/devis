import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
import json
from datetime import datetime

router = APIRouter()

@router.get("/api/google-reviews")
async def get_google_reviews():
    """Récupérer les avis Google (statiques pour l'instant)"""
    try:
        # Pour l'instant, retourne des avis statiques
        # Plus tard, pourra être connecté à l'API Google Places
        reviews = [
            {
                "id": 1,
                "name": "Marie Dupont",
                "rating": 5,
                "text": "Excellent service de ménage ! Très professionnel et ponctuel. Je recommande vivement !",
                "date": "2024-03-15",
                "relative_time": "Il y a 2 semaines"
            },
            {
                "id": 2,
                "name": "Jean Martin",
                "rating": 5,
                "text": "RD Ménage a transformé mon appartement. Travail impeccable et équipe très sympathique.",
                "date": "2024-03-01",
                "relative_time": "Il y a 1 mois"
            },
            {
                "id": 3,
                "name": "Sophie Bernard",
                "rating": 5,
                "text": "Service de qualité, très satisfait de prestation. Rapport qualité/prix excellent.",
                "date": "2024-03-01",
                "relative_time": "Il y a 1 mois"
            },
            {
                "id": 4,
                "name": "Pierre Durand",
                "rating": 5,
                "text": "Professionnalisme et efficacité au rendez-vous. Je fais appel à eux régulièrement.",
                "date": "2024-02-15",
                "relative_time": "Il y a 2 mois"
            },
            {
                "id": 5,
                "name": "Isabelle Petit",
                "rating": 5,
                "text": "Équipe sérieuse et travail soigné. Ma maison est toujours impeccable après leur passage.",
                "date": "2024-02-01",
                "relative_time": "Il y a 3 mois"
            },
            {
                "id": 6,
                "name": "Thomas Robert",
                "rating": 5,
                "text": "Bon service de ménage, fiable et discret. Je suis client depuis plus d'un an.",
                "date": "2024-02-01",
                "relative_time": "Il y a 3 mois"
            }
        ]
        
        # Calculer la moyenne - TOUS à 5 étoiles = 5.0
        total_rating = sum(review["rating"] for review in reviews)
        average_rating = round(total_rating / len(reviews), 1)  # Doit être 5.0
        
        return {
            "success": True,
            "reviews": reviews,
            "average_rating": average_rating,  # 5.0
            "total_reviews": len(reviews),     # 6
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Erreur get_google_reviews: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/api/google-rating")
async def get_google_rating():
    """Récupérer uniquement la note moyenne Google"""
    try:
        reviews_response = await get_google_reviews()
        
        if reviews_response["success"]:
            return {
                "success": True,
                "rating": reviews_response["average_rating"],
                "count": reviews_response["total_reviews"],
                "stars": "⭐" * int(reviews_response["average_rating"])
            }
        else:
            return reviews_response
            
    except Exception as e:
        print(f"Erreur get_google_rating: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/google-reviews/sync")
async def sync_google_reviews():
    """Synchroniser les avis Google (placeholder pour futur API)"""
    try:
        # Pour l'instant, simule une synchronisation
        # Plus tard, pourra appeler l'API Google Places
        
        return {
            "success": True,
            "message": "Synchronisation simulée - API Google Places à intégrer",
            "sync_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Erreur sync_google_reviews: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/google-reviews/add")
async def add_google_review(review_data: dict):
    """Ajouter un avis manuellement (pour testing)"""
    try:
        # Pour l'instant, juste une simulation
        # Plus tard, pourra être connecté à une base de données
        
        return {
            "success": True,
            "message": "Avis ajouté avec succès (simulation)",
            "review": review_data
        }
        
    except Exception as e:
        print(f"Erreur add_google_review: {e}")
        return {
            "success": False,
            "error": str(e)
        }
