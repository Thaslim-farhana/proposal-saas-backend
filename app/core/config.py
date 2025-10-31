import os
from pydantic import BaseSettings, AnyUrl

class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    DATABASE_URL: AnyUrl | None = os.getenv("DATABASE_URL", None)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")

settings = Settings()
