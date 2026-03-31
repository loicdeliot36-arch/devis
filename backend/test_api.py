import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from routers import api
    print('✅ Module api importé avec succès')
    
    # Vérifier les routes
    routes = [route.path for route in api.router.routes]
    print(f'Routes disponibles: {routes}')
    
except Exception as e:
    print(f'❌ Erreur import api: {e}')
