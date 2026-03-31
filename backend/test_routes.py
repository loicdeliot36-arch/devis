from fastapi import FastAPI
from routers.admin import router
from routers import public

app = FastAPI()

# Inclure les routers comme dans main.py
app.include_router(public.router, tags=["public"])
app.include_router(router, tags=["admin"], prefix="/admin")

print("=== Toutes les routes ===")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"{list(route.methods)[0] if route.methods else 'GET'} {route.path}")

print("\n=== Routes admin ===")
for route in app.routes:
    if hasattr(route, 'path') and '/admin/' in route.path:
        print(f"{list(route.methods)[0] if route.methods else 'GET'} {route.path}")
