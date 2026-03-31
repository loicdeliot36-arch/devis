import os
from pathlib import Path

def check_template_files():
    """Vérifier si les templates desktop existent"""
    templates_dir = Path("templates")
    
    required_templates = [
        "messages_desktop.html",
        "users_desktop.html",
        "base_desktop.html",
        "dashboard_desktop.html",
        "profile_desktop.html",
        "contact_desktop.html",
        "index_desktop.html",
        "login_desktop.html",
        "register_desktop.html"
    ]
    
    print("=== Vérification des templates ===")
    for template in required_templates:
        template_path = templates_dir / template
        exists = template_path.exists()
        size = template_path.stat().st_size if exists else 0
        print(f"{template}: {'OK' if exists else 'MANQUANT'} ({size} octets)")
    
    # Vérifier le contenu des templates desktop
    print("\n=== Contenu des templates desktop ===")
    
    messages_template = templates_dir / "messages_desktop.html"
    if messages_template.exists():
        with open(messages_template, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"messages_desktop.html: {len(content)} caractères")
            print(f"Contient 'messages-stats': {'messages-stats' in content}")
            print(f"Contient 'user-card': {'user-card' in content}")
            print(f"Contient 'modal': {'modal' in content}")
    
    users_template = templates_dir / "users_desktop.html"
    if users_template.exists():
        with open(users_template, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"users_desktop.html: {len(content)} caractères")
            print(f"Contient 'users-stats': {'users-stats' in content}")
            print(f"Contient 'user-card': {'user-card' in content}")
            print(f"Contient 'modal': {'modal' in content}")

if __name__ == "__main__":
    check_template_files()
