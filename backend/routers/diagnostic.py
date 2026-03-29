from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import sqlite3
from pathlib import Path

router = APIRouter()

@router.get("/diagnostic/users")
async def diagnostic_users():
    """Diagnostic des utilisateurs pour débugger Render"""
    try:
        db_path = Path(__file__).parent.parent / "database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier la structure de la table
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Vérifier les données
        cursor.execute("""
            SELECT id, email, nom, prenom, telephone, date_naissance, role, date_creation 
            FROM users 
            ORDER BY id
        """)
        users = cursor.fetchall()
        
        # Statistiques
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE nom IS NOT NULL AND prenom IS NOT NULL")
        valid = cursor.fetchone()[0]
        
        conn.close()
        
        return JSONResponse({
            "status": "success",
            "columns": columns,
            "total_users": total,
            "valid_users": valid,
            "users": [
                {
                    "id": u[0],
                    "email": u[1],
                    "nom": u[2],
                    "prenom": u[3],
                    "telephone": u[4],
                    "date_naissance": u[5],
                    "role": u[6],
                    "date_creation": u[7]
                } for u in users
            ]
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@router.post("/diagnostic/fix-users")
async def fix_users():
    """Fix automatique des utilisateurs sur Render"""
    try:
        from fix_render_users import fix_render_users
        fix_render_users()
        return JSONResponse({
            "status": "success",
            "message": "Utilisateurs corrigés avec succès"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error", 
            "message": str(e)
        }, status_code=500)
