@echo off
:: Change to the directory where the .bat file is located
cd /d "%~dp0"

:: Check if venv folder exists
if not exist "venv\Scripts\activate" (
    echo "L'environnement virtuel n'existe pas. Création..."
    :: Create the virtual environment
    python -m venv venv
    if errorlevel 1 (
        echo "Erreur lors de la création de l'environnement virtuel."
        pause
        exit /b 1
    )
)

:: Try to activate the virtual environment
echo "Activation de l'environnement virtuel..."
call venv\Scripts\activate

:: Check if activation succeeded
if errorlevel 1 (
    echo "Erreur lors de l'activation de l'environnement virtuel."
    pause
    exit /b 1
)

:: Update pip to the latest version
echo "Mise à jour de pip..."
python -m pip install --upgrade pip
if errorlevel 1 (
    echo "Erreur lors de la mise à jour de pip."
    pause
    exit /b 1
)

:: Install dependencies from requirements.txt if they are not installed
if exist "requirements.txt" (
    echo "Installation des dépendances à partir de requirements.txt..."
    pip install -r requirements.txt
    if errorlevel 1 (
        echo "Erreur lors de l'installation des dépendances."
        pause
        exit /b 1
    )

    :: Check and update each package in requirements.txt
    for /f "delims=" %%p in (requirements.txt) do (
        echo "Vérification des mises à jour pour %%p..."
        pip install --upgrade %%p
    )
) else (
    echo "Le fichier requirements.txt est introuvable."
)

:: Go to the application directory if needed
if exist "myflaskapp" (
    cd myflaskapp
)

:: Run the Flask application
python wsgi.py

:: Keep the window open
pause
