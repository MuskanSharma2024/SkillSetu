from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillSetu"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "skillsetu-super-secret-production-grade-key-2026-sih-bridge"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database URL - default to SQLite in the backend folder
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/skillsetu.db"
    
    # Document storage directory
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg"]
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
