import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# BASE_DIR : dossier INSCRIPTIBLE, toujours à côté du .exe réel (ou de config.py en dev).
# C'est ici que vit le dossier instance/ (base SQLite), qui doit persister
# entre les lancements et ne JAMAIS être à l'intérieur du bundle PyInstaller.
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

# RESOURCES_DIR : dossier en LECTURE SEULE contenant les fichiers bundlés
# par PyInstaller (templates, static...). En mode "onedir", PyInstaller peut
# les placer dans un sous-dossier _internal/ different de BASE_DIR, d'où
# l'utilisation de sys._MEIPASS qui pointe toujours au bon endroit.
if getattr(sys, 'frozen', False):
    RESOURCES_DIR = Path(sys._MEIPASS)
else:
    RESOURCES_DIR = Path(__file__).resolve().parent

INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)

DB_PATH = INSTANCE_DIR / 'bulletins.db'


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH.as_posix()}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}