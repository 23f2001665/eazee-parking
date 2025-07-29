import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env')

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "application"
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = APP_DIR / "templates"
INSTANCE_DIR = BASE_DIR / "instance"
LOGS_DIR = BASE_DIR / "logs"


class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE_DIR / 'database.sqlite3'}"
    SECRET_KEY = os.environ.get("SECRET_KEY")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"