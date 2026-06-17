# app/core/config.py

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """
    Ce
    ntral configuration for the entire application.
    Values are loaded from the .env file automatically.
    """

    APP_NAME: str = "ResumeJobMatcher"
    MAX_FILE_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads"
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"         # tells pydantic WHERE to read from
        env_file_encoding = "utf-8"


# Single instance — imported everywhere
settings = Settings()