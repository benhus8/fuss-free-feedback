from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent

ROOT_DIR = APP_DIR.parent

ENV_FILE_PATH = ROOT_DIR / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    TRIPCODE_SALT: str = "default_salt_change_me"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, 
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()