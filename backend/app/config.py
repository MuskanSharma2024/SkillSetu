import os
import shutil
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

def get_database_url() -> str:
    env_db = os.getenv("DATABASE_URL")
    if env_db:
        return env_db
    
    db_file = BASE_DIR / "skillsetu.db"
    # If running on Vercel or read-only filesystem, copy pre-seeded database to /tmp
    if os.getenv("VERCEL") or not os.access(BASE_DIR, os.W_OK):
        tmp_db = Path("/tmp") / "skillsetu.db"
        if not tmp_db.exists() and db_file.exists():
            try:
                shutil.copyfile(db_file, tmp_db)
            except Exception:
                pass
        return f"sqlite:///{tmp_db}"
    
    return f"sqlite:///{db_file}"

def get_upload_dir() -> Path:
    env_upload = os.getenv("UPLOAD_DIR")
    if env_upload:
        return Path(env_upload)
    if os.getenv("VERCEL"):
        return Path("/tmp/uploads")
    return BASE_DIR / "uploads"

class Settings:
    PROJECT_NAME: str = "SkillSetu"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "skillsetu-super-secret-production-grade-key-2026-sih-bridge")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Database URL - default to SQLite in the backend folder (or /tmp on Vercel)
    DATABASE_URL: str = get_database_url()

    # Document storage directory
    UPLOAD_DIR: Path = get_upload_dir()
    MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg"]

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
    ]

settings = Settings()
# Ensure upload directory exists
try:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

