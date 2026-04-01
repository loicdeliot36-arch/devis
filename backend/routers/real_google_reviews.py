import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
import json
from datetime import datetime
import requests
import time

router = APIRouter()

# Configuration pour l'API Google Places (nécessite une clé API)
GOOGLE_PLACES_API_KEY = None  # À configurer si vous avez une clé API
PLACE_ID = "ChZDSUhNMG9nS0VJQ0FnSURienUzMFV3EAE"  # ID potentiel pour RD Menage

@router.get("/api/real-google-reviews")
async def get_real_google_reviews():
    """
    Récupérer les vrais avis Google Maps.
    Pour l'instant, retourne un message car nécessite l'API Google Places payante.
    """
    try:
        # Vérifier si on a une clé API
        if not GOOGLE_PLACES_API_KEY:
            return {
                "success": False,
                "message": "API Google Places non configurée - Nécessite une clé API payante",
                "info": "Pour intégrer les vrais avis Google, vous devez:",
                "steps": [
                    "1. Créer un projet Google Cloud",
                    "2. Activer l'API Google Places",
                    "3. Obtenir une clé API",
                    "4. Configurer la clé dans ce fichier",
                    "5. Les vrais avis seront alors synchronisés automatiquement"
                ],
                "alternative": "En attendant, vous pouvez ajouter manuellement les vrais avis ci-dessous"
            }
        
        # Si on a une clé API, faire l'appel (code commenté pour l'instant)
        """
        url = f"https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'place_id': PLACE_ID,
            'fields': 'name,rating,reviews,user_ratings_total',
            'key': GOOGLE_PLACES_API_KEY,
            'language': 'fr'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') == 'OK':
            place = data.get('result', {})
            reviews = place.get('reviews', [])
            
            formatted_reviews = []
            for review in reviews:
                formatted_reviews.append({
                    'name': review.get('author_name', 'Anonyme'),
                    'rating': review.get('rating', 5),
                    'text': review.get('text', ''),
                    'date': review.get('relative_time_description', 'Date inconnue'),
                    'profile_photo': review.get('profile_photo_url', '')
                })
            
            return {
                "success": True,
                "reviews": formatted_reviews,
                "average_rating": place.get('rating', 0),
                "total_reviews": place.get('user_ratings_total', 0),
                "source": "Google Maps API"
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {data.get('status', 'Unknown')}"
            }
        """
        
    except Exception as e:
        print(f"Erreur get_real_google_reviews: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/api/manual-add-reviews")
async def manually_add_real_reviews(reviews_data: dict):
    """
    Permet d'ajouter manuellement les vrais avis Google.
    Utilisez cette endpoint pour entrer les vrais avis que vous avez sur Google Maps.
    """
    try:
        reviews = reviews_data.get('reviews', [])
        
        if not reviews:
            return {
                "success": False,
                "error": "Aucun avis fourni"
            }
        
        # Valider les avis
        valid_reviews = []
        for i, review in enumerate(reviews):
            if not all(key in review for key in ['name', 'rating', 'text', 'date']):
                return {
                    "success": False,
                    "error": f"L'avis {i+1} est incomplet. Chaque avis doit avoir: name, rating, text, date"
                }
            
            if not isinstance(review['rating'], int) or review['rating'] < 1 or review['rating'] > 5:
                return {
                    "success": False,
                    "error": f"L'avis {i+1} a une note invalide. La note doit être entre 1 et 5."
                }
            
            valid_reviews.append({
                'id': i + 1,
                'name': review['name'],
                'rating': review['rating'],
                'text': review['text'],
                'date': review['date'],
                'relative_time': review['date'],
                'source': 'manual_google_maps'
            })
        
        # Calculer la moyenne
        total_rating = sum(review['rating'] for review in valid_reviews)
        average_rating = round(total_rating / len(valid_reviews), 1)
        
        # Stocker en base de données
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer les tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS real_google_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rating INTEGER NOT NULL,
                text TEXT NOT NULL,
                date TEXT NOT NULL,
                relative_time TEXT NOT NULL,
                source TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS real_google_stats (
                id INTEGER PRIMARY KEY,
                average_rating REAL NOT NULL,
                total_reviews INTEGER NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Vider et insérer les nouveaux avis
        cursor.execute("DELETE FROM real_google_reviews")
        
        for review in valid_reviews:
            cursor.execute("""
                INSERT INTO real_google_reviews (name, rating, text, date, relative_time, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (review['name'], review['rating'], review['text'], review['date'], review['relative_time'], review['source']))
        
        # Mettre à jour les stats
        cursor.execute("""
            INSERT OR REPLACE INTO real_google_stats (id, average_rating, total_reviews, last_updated)
            VALUES (1, ?, ?, ?)
        """, (average_rating, len(valid_reviews), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"{len(valid_reviews)} avis Google ajoutés manuellement avec succès",
            "average_rating": average_rating,
            "total_reviews": len(valid_reviews),
            "reviews": valid_reviews
        }
        
    except Exception as e:
        print(f"Erreur manually_add_real_reviews: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/api/get-real-reviews")
async def get_real_reviews_from_db():
    """Récupérer les vrais avis stockés en base de données"""
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer les avis
        cursor.execute("SELECT name, rating, text, date, relative_time, source FROM real_google_reviews ORDER BY date DESC")
        reviews_data = cursor.fetchall()
        
        # Récupérer les stats
        cursor.execute("SELECT average_rating, total_reviews, last_updated FROM real_google_stats WHERE id = 1")
        stats_data = cursor.fetchone()
        
        conn.close()
        
        # Formater les avis
        reviews = []
        for row in reviews_data:
            reviews.append({
                "name": row[0],
                "rating": row[1],
                "text": row[2],
                "date": row[3],
                "relative_time": row[4],
                "source": row[5]
            })
        
        # Stats
        stats = {
            "average_rating": stats_data[0] if stats_data else 0,
            "total_reviews": stats_data[1] if stats_data else 0,
            "last_updated": stats_data[2] if stats_data else None
        }
        
        return {
            "success": True,
            "reviews": reviews,
            "stats": stats
        }
        
    except Exception as e:
        print(f"Erreur get_real_reviews_from_db: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/api/reviews-setup-guide")
async def get_reviews_setup_guide():
    """Guide pour configurer les vrais avis Google"""
    return {
        "success": True,
        "title": "📋 Guide pour intégrer les vrais avis Google Maps",
        "steps": [
            {
                "step": 1,
                "title": "🔑 Obtenir une clé API Google Places",
                "description": "1. Allez sur https://console.cloud.google.com",
                "details": [
                    "Créez un nouveau projet ou utilisez un existant",
                    "Activez l'API 'Places API'",
                    "Créez une clé d'API",
                    "Limitez la clé à l'API Places uniquement"
                ]
            },
            {
                "step": 2,
                "title": "📍 Trouver votre Place ID",
                "description": "2. Cherchez votre entreprise sur Google Maps",
                "details": [
                    "Allez sur Google Maps",
                    "Cherchez 'RD Menage a domicile'",
                    "Copiez le Place ID depuis l'URL",
                    "Exemple: /place/PLACE_ID/"
                ]
            },
            {
                "step": 3,
                "title": "⚙️ Configurer le système",
                "description": "3. Ajoutez vos clés dans le code",
                "details": [
                    "Éditez le fichier routers/real_google_reviews.py",
                    "Ajoutez votre GOOGLE_PLACES_API_KEY",
                    "Ajoutez votre PLACE_ID",
                    "Redémarrez le serveur"
                ]
            },
            {
                "step": 4,
                "title": "✅ Alternative manuelle",
                "description": "4. Entrez manuellement vos vrais avis",
                "details": [
                    "Utilisez l'endpoint POST /api/manual-add-reviews",
                    "Copiez-collez vos vrais avis de Google Maps",
                    "Le système les affichera automatiquement"
                ]
            }
        ],
        "warning": "⚠️ N'utilisez jamais de faux avis - c'est illégal et nuit à votre crédibilité !",
        "example_manual_entry": {
            "reviews": [
                {
                    "name": "Nom réel du client",
                    "rating": 5,
                    "text": "Texte exact de l'avis Google",
                    "date": "Il y a 2 semaines"
                }
            ]
        }
    }
