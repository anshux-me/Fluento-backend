"""
Fluento Backend - Main Application

An AI-powered language learning API with:
- Pronunciation practice (Whisper STT + Phonemizer)
- Spelling from audio (Coqui TTS)
- Gamification (XP, levels, streaks, badges)
- Firestore database
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_firebase
from app.services.word_service import word_service
from app.services.whisper_service import whisper_service
from app.services.tts_service import tts_service
from app.routers import words, pronunciation, spelling, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for startup and shutdown.
    Load models on startup to avoid cold-start latency.
    """
    print("=" * 50)
    print("Starting Fluento Backend...")
    print("=" * 50)
    
    # Initialize Firebase
    print("\n[1/4] Initializing Firebase...")
    init_firebase()
    
    # Load word dataset
    print("\n[2/4] Loading word dataset...")
    word_service.load_words()
    
    # Load Whisper model
    print("\n[3/4] Loading Whisper model...")
    try:
        whisper_service.load_model()
    except Exception as e:
        print(f"Warning: Could not load Whisper model: {e}")
    
    # Load TTS model
    print("\n[4/4] Loading TTS model...")
    try:
        tts_service.load_model()
    except Exception as e:
        print(f"Warning: Could not load TTS model: {e}")
    
    print("\n" + "=" * 50)
    print("Fluento Backend Ready!")
    print("=" * 50)
    
    yield
    
    # Cleanup on shutdown
    print("Shutting down Fluento Backend...")


# Create FastAPI app
app = FastAPI(
    title="Fluento API",
    description="AI-powered language learning API with pronunciation practice and spelling games",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(words.router)
app.include_router(pronunciation.router)
app.include_router(spelling.router)
app.include_router(users.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": settings.APP_NAME,
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "words": word_service._loaded,
            "whisper": whisper_service._loaded,
            "tts": tts_service._loaded,
        },
        "word_count": word_service.get_word_count()
    }
