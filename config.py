import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Clé secrète pour les sessions
    DEBUG = True
    SESSION_COOKIE_SAMESITE = 'None'  # None pour permettre le cookie dans tous les contextes
    SESSION_COOKIE_SECURE = True  # Assure que le cookie est uniquement envoyé via HTTPS
