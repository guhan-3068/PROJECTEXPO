import os
import json
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from pathlib import Path

# Base backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_STORAGE_ROOT = BACKEND_DIR.parent / "storage"

class Settings(BaseSettings):
    APP_NAME: str = "QUBIX"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]

    # Database (Clean POSIX path for Windows SQLite URI)
    DATABASE_URL: str = f"sqlite:///{BACKEND_DIR.as_posix()}/docverify.db"

    # Security
    SECRET_KEY: str = "docverify-ai-secure-secret-key-replace-in-production-minimum-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AES Encryption (Fernet / AES-256)
    # Default 32-byte urlsafe base64 key for development
    ENCRYPTION_KEY: str = "ZXhhbXBsZS1mZXJuZXQta2V5LTMyLWJ5dGVzLWxvbmctMTI="

    # Storage
    STORAGE_ROOT: Path = DEFAULT_STORAGE_ROOT
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    ALLOWED_MIME_TYPES: List[str] = ["application/pdf", "image/jpeg", "image/png"]
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".jpg", ".jpeg", ".png"]

    # Verification Rules
    EXPIRY_WARNING_DAYS: int = 60
    SIMILARITY_THRESHOLD: float = 0.82  # Name similarity matching threshold

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.STORAGE_ROOT / "uploads", exist_ok=True)
os.makedirs(settings.STORAGE_ROOT / "encrypted", exist_ok=True)
os.makedirs(settings.STORAGE_ROOT / "ela_cache", exist_ok=True)
os.makedirs(settings.STORAGE_ROOT / "reports", exist_ok=True)
