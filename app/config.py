"""
Configuration settings for the LinguaAI backend.
Uses environment variables with sensible defaults.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App settings
    APP_NAME: str = "Fluento"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS - stored as comma-separated string in .env
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://*.vercel.app"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
    AUDIO_CACHE_DIR: Path = DATA_DIR / "audio_cache"
    MODELS_DIR: Path = DATA_DIR / "models"
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = os.getenv(
        "FIREBASE_CREDENTIALS_PATH", 
        str(BASE_DIR / "firebase-credentials.json")
    )
    
    # Whisper settings
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    
    # TTS settings
    TTS_MODEL: str = os.getenv("TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
    
    # Audio constraints
    MAX_AUDIO_DURATION_SECONDS: int = 5
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_AUDIO_TYPES: list[str] = ["audio/wav", "audio/webm", "audio/mp3", "audio/mpeg", "audio/ogg"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
