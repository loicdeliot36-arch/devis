# Script de démarrage pour Windows
param(
    [switch]$setup = $false
)

$ErrorActionPreference = "Stop"

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 Démarrage - Formulaires de Contact & Devis" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Fichier .env non trouvé!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ACTION REQUISE:" -ForegroundColor Yellow
    Write-Host "1. Ouvrez le fichier .env.example"
    Write-Host "2. Remplissez vos identifiants Gmail"
    Write-Host "3. Sauvegardez il comme '.env'"
    Write-Host ""
    Write-Host "Ensuite, exécutez à nouveau ce script"
    exit 1
}

# Activate venv
$venvPath = ".\venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvPath)) {
    Write-Host "❌ Environnement virtuel non trouvé" -ForegroundColor Red
    Write-Host "Exécutez d'abord: python setup.py" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Activation de l'environnement virtuel..."
& $venvPath

# Start the app
Write-Host ""
Write-Host "✓ Démarrage de l'application..." -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Ouvrez http://localhost:8000 dans votre navigateur" -ForegroundColor Green
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur CTRL+C pour arrêter" -ForegroundColor Yellow
Write-Host ""

cd backend
python main.py
