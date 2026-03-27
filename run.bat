@echo off
cls
echo ========================================
echo  Formulaires de Contact - Demarrage
echo ========================================
echo.

if not exist ".env" (
    echo ERREUR: Fichier .env non trouve
    echo.
    echo ACTION: Copiez .env.example en .env et remplissez-le
    echo.
    pause
    exit /b 1
)

REM Supprime un venv potentiellement cassé et en recrée un propre
if exist "venv" rmdir /s /q venv

echo Creation de l'environnement virtuel avec Python 3.12.9...
py -3.12 -m venv venv
if errorlevel 1 (
    echo ERREUR: Impossible de creer le virtualenv avec Python 3.12
    pause
    exit /b 1
)

echo Activation de l'environnement...
call venv\Scripts\activate.bat
if not exist "venv\Scripts\python.exe" (
    echo ERREUR: venv invalide, Python non trouve dans venv.
    pause
    exit /b 1
)

echo Installation des dependances...
pip install -q -r backend\requirements.txt

echo.
echo ========================================
echo  Demarrage de l'application...
echo ========================================
echo.
echo Ouvrez: http://localhost:8000
echo.

cd backend
python main.py

pause
