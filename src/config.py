from pathlib import Path

from dotenv import load_dotenv
import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings

"""
Файл для конфигурации миграции баз данных
Получаем информацию из файла .env (Файл окружения)
И передаем после в env.py (dir migrations)
"""

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

SECRET = os.environ.get("SECRET")
SECRETUM = os.environ.get("SECRETUM")
BASE_DIR = Path(__file__).parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt_private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt_public.pem"
    algorithm: str = "RS256"


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()