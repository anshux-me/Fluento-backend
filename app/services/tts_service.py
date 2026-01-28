"""
TTS service for text-to-speech using gTTS (Google Text-to-Speech).
Generates audio files for words in the spelling game.
"""

import hashlib
from pathlib import Path
from typing import Optional
from gtts import gTTS

from app.config import settings


class TTSService:
    """Service for text-to-speech using gTTS (Google Text-to-Speech)."""
    
    def __init__(self):
        self._loaded = True
        self.language = "en"  # English
        self.tld = "com"  # Use .com for US accent
        # Alternative TLDs for different accents:
        # "co.uk" - British English
        # "com.au" - Australian English
        # "co.in" - Indian English
    
    def load_model(self):
        """No model loading needed for gTTS."""
        print("TTS service ready (using gTTS)")
        self._loaded = True
    
    def _get_cache_path(self, word: str) -> Path:
        """Get the cache file path for a word."""
        # Create a hash of the word for the filename
        word_hash = hashlib.md5(word.lower().encode()).hexdigest()[:12]
        safe_word = "".join(c if c.isalnum() else "_" for c in word.lower())[:20]
        filename = f"{safe_word}_{word_hash}.mp3"
        return settings.AUDIO_CACHE_DIR / filename
    
    def generate_audio(self, word: str, force_regenerate: bool = False) -> Optional[Path]:
        """
        Generate audio for a word.
        Uses cached version if available.
        
        Args:
            word: The word to generate audio for
            force_regenerate: If True, regenerate even if cached
            
        Returns:
            Path to the generated audio file, or None if generation fails
        """
        cache_path = self._get_cache_path(word)
        
        # Return cached version if exists and not empty
        if not force_regenerate and cache_path.exists() and cache_path.stat().st_size > 0:
            return cache_path
        
        # Remove old empty/corrupted cache files
        if cache_path.exists():
            try:
                cache_path.unlink()
            except:
                pass
        
        try:
            # Generate speech using gTTS
            tts = gTTS(text=word, lang=self.language, tld=self.tld, slow=False)
            tts.save(str(cache_path))
            
            # Verify file was created and is not empty
            if cache_path.exists() and cache_path.stat().st_size > 0:
                return cache_path
            else:
                return None
                
        except Exception as e:
            print(f"gTTS error for '{word}': {e}")
            # Clean up any partial file
            if cache_path.exists():
                try:
                    cache_path.unlink()
                except:
                    pass
            return None
    
    def get_audio_path(self, word: str) -> Optional[Path]:
        """
        Get the audio file path for a word, generating if needed.
        
        Args:
            word: The word to get audio for
            
        Returns:
            Path to the audio file, or None if generation fails
        """
        try:
            return self.generate_audio(word)
        except Exception as e:
            print(f"Error generating audio for '{word}': {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached audio files."""
        for file in settings.AUDIO_CACHE_DIR.glob("*.mp3"):
            try:
                file.unlink()
            except Exception as e:
                print(f"Error deleting {file}: {e}")


# Singleton instance
tts_service = TTSService()
