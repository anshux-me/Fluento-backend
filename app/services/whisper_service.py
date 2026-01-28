"""
Whisper service for speech-to-text transcription.
Uses Faster Whisper for optimized CPU inference.
"""

from faster_whisper import WhisperModel
import tempfile
import os
from pathlib import Path
from typing import Optional

from app.config import settings


class WhisperService:
    """Service for speech-to-text using Faster Whisper."""
    
    def __init__(self):
        self.model = None
        self._loaded = False
    
    def load_model(self):
        """Load the Faster Whisper model into memory."""
        if self._loaded:
            return
        
        model_size = settings.WHISPER_MODEL
        print(f"Loading Faster Whisper model: {model_size}")
        
        # Download to models directory
        download_root = str(settings.MODELS_DIR / "whisper")
        os.makedirs(download_root, exist_ok=True)
        
        # Use CPU with int8 quantization for efficiency
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            download_root=download_root
        )
        
        self._loaded = True
        print("Faster Whisper model loaded successfully")
    
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
        
        # Transcribe with Faster Whisper
        segments, info = self.model.transcribe(
            audio_path,
            language="en",
            beam_size=5,
            vad_filter=True,  # Filter out silence
        )
        
        # Combine all segments
        text = " ".join([segment.text for segment in segments]).strip()
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
