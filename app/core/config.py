# app/core/config.py

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """
    Central configuration for the entire application.
    Values are loaded from the .env file automatically.
    """

    # App
    APP_NAME: str = "ResumeJobMatcher"
    MAX_FILE_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads"

    # AI
    GEMINI_API_KEY: str = ""

    # Job Search
    ADZUNA_APP_ID: str = ""
    ADZUNA_API_KEY: str = ""
    ADZUNA_COUNTRY: str = "in"           # "in" for India
    ADZUNA_RESULTS_PER_PAGE: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()