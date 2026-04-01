from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from auth import get_user_from_token

router = APIRouter()

@router.get("/test-auth")
async def test_auth(request: Request):
    """Page de test pour vérifier l'authentification"""
    user = get_user_from_token(request)
    
    if user:
        return {
            "success": True,
            "user": {
                "id": user.get("id"),
                "email": user.get("email"),
                "role": user.get("role"),
                "nom": user.get("nom"),
                "prenom": user.get("prenom")
            },
            "message": "Authentification réussie"
        }
    else:
        return {
            "success": False,
            "error": "Non authentifié",
            "message": "Veuillez vous connecter",
            "cookies": list(request.cookies.keys())
        }
