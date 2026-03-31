import os
import sys

# Forcer l'encodage UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from fastapi import FastAPI
    from fastapi.templating import Jinja2Templates
    app = FastAPI()
    templates = Jinja2Templates(directory='templates')
    
    # Test templates
    templates_to_test = [
        'sync_desktop.html',
        'base_desktop.html',
        'login_desktop.html',
        'contact_desktop.html'
    ]
    
    for template_name in templates_to_test:
        try:
            template = templates.get_template(template_name)
            print(f'✅ {template_name} - OK')
        except Exception as e:
            print(f'❌ {template_name} - Erreur: {e}')
            
except Exception as e:
    print(f'Erreur générale: {e}')
