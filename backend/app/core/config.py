from pathlib import Path
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "vk-lip"
    debug: bool = True
    database_url: str = "sqlite:///./database/app.db"

    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"
        env_file_encoding = "utf-8"

settings = Settings()
