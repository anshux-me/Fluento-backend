"""
Whisper service for speech-to-text transcription.
Uses OpenAI's open-source Whisper model.
"""

import whisper
import tempfile
import os
from pathlib import Path
from typing import Optional
import numpy as np

from app.config import settings


class WhisperService:
    """Service for speech-to-text using Whisper."""
    
    def __init__(self):
        self.model = None
        self._loaded = False
    
    def load_model(self):
        """Load the Whisper model into memory."""
        if self._loaded:
            return
        
        print(f"Loading Whisper model: {settings.WHISPER_MODEL}")
        
        # Download to models directory
        download_root = str(settings.MODELS_DIR / "whisper")
        os.makedirs(download_root, exist_ok=True)
        
        self.model = whisper.load_model(
            settings.WHISPER_MODEL,
            download_root=download_root
        )
        
        self._loaded = True
        print("Whisper model loaded successfully")
    
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        if not self._loaded:
            self.load_model()
        
        # Transcribe with Whisper
        result = self.model.transcribe(
            audio_path,
            language="en",
            task="transcribe",
            fp16=False,  # Use FP32 for CPU compatibility
        )
        
        text = result.get("text", "").strip()
        return text
    
    def transcribe_bytes(self, audio_bytes: bytes, suffix: str = ".webm") -> str:
        """
        Transcribe audio from bytes.
        
        Args:
            audio_bytes: Raw audio bytes
            suffix: File suffix for the temp file
            
        Returns:
            Transcribed text
        """
        # Write to temporary file
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            return self.transcribe(temp_path)
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)


# Singleton instance
whisper_service = WhisperService()
