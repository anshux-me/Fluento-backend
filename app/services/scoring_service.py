"""
Scoring service for pronunciation and spelling evaluation.
Uses phonemizer for phoneme conversion and Levenshtein distance for scoring.
"""

from phonemizer import phonemize
from phonemizer.backend import EspeakBackend
from Levenshtein import distance as levenshtein_distance
import re


class ScoringService:
    """Service for scoring pronunciation and spelling."""
    
    def __init__(self):
        self._backend = None
    
    def _get_backend(self):
        """Get or create the espeak backend."""
        if self._backend is None:
            self._backend = EspeakBackend(
                language="en-us",
                preserve_punctuation=False,
                with_stress=False
            )
        return self._backend
    
    def text_to_phonemes(self, text: str) -> str:
        """
        Convert text to phoneme representation.
        
        Args:
            text: Input text
            
        Returns:
            Phoneme string
        """
        if not text:
            return ""
        
        # Clean the text
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        
        try:
            phonemes = phonemize(
                text,
                language="en-us",
                backend="espeak",
                strip=True,
                preserve_punctuation=False,
                with_stress=False
            )
            return phonemes.strip()
        except Exception as e:
            print(f"Error converting to phonemes: {e}")
            return text
    
    def calculate_pronunciation_score(
        self, 
        recognized_text: str, 
        target_word: str
    ) -> dict:
        """
        Calculate pronunciation score based on phoneme similarity.
        
        Args:
            recognized_text: Text recognized from speech
            target_word: The target word to compare against
            
        Returns:
            Dict with score and feedback
        """
        # Get phonemes
        target_phonemes = self.text_to_phonemes(target_word)
        recognized_phonemes = self.text_to_phonemes(recognized_text)
        
        # Calculate Levenshtein distance
        if not target_phonemes:
            return {
                "score": 0,
                "target_phonemes": target_phonemes,
                "recognized_phonemes": recognized_phonemes,
                "feedback": "Could not process target word"
            }
        
        dist = levenshtein_distance(target_phonemes, recognized_phonemes)
        max_len = max(len(target_phonemes), len(recognized_phonemes), 1)
        
        # Convert to 0-100 score
        similarity = 1 - (dist / max_len)
        score = max(0, min(100, int(similarity * 100)))
        
        # Generate feedback
        feedback = self._get_pronunciation_feedback(score, recognized_text, target_word)
        
        return {
            "score": score,
            "target_phonemes": target_phonemes,
            "recognized_phonemes": recognized_phonemes,
            "feedback": feedback
        }
    
    def calculate_spelling_score(
        self, 
        user_text: str, 
        target_word: str
    ) -> dict:
        """
        Calculate spelling score based on character similarity.
        
        Args:
            user_text: User's spelling attempt
            target_word: The correct spelling
            
        Returns:
            Dict with score and feedback
        """
        # Normalize texts
        user_text = user_text.lower().strip()
        target_word = target_word.lower().strip()
        
        # Exact match
        if user_text == target_word:
            return {
                "score": 100,
                "feedback": "Perfect! You spelled it correctly!"
            }
        
        # Calculate Levenshtein distance
        dist = levenshtein_distance(target_word, user_text)
        max_len = max(len(target_word), len(user_text), 1)
        
        # Convert to 0-100 score
        similarity = 1 - (dist / max_len)
        score = max(0, min(100, int(similarity * 100)))
        
        # Generate feedback
        feedback = self._get_spelling_feedback(score, user_text, target_word)
        
        return {
            "score": score,
            "feedback": feedback
        }
    
    def _get_pronunciation_feedback(
        self, 
        score: int, 
        recognized: str, 
        target: str
    ) -> str:
        """Generate feedback for pronunciation attempt."""
        recognized_clean = recognized.lower().strip()
        target_clean = target.lower().strip()
        
        # Check for exact match
        if recognized_clean == target_clean:
            return "Perfect pronunciation! Great job!"
        
        # Check if the word is contained in the recognized text
        if target_clean in recognized_clean:
            return f"Good! You said the word correctly. Score based on clarity."
        
        if score >= 90:
            return "Excellent pronunciation! Almost perfect!"
        elif score >= 75:
            return "Great pronunciation! Minor differences detected."
        elif score >= 60:
            return "Good attempt! Some sounds need work."
        elif score >= 40:
            return "Keep practicing! Focus on individual sounds."
        elif score >= 20:
            return f"The word '{target}' sounds quite different. Try again slowly."
        else:
            if not recognized:
                return "Could not detect speech. Please try again."
            return f"We heard '{recognized}'. The target word is '{target}'. Try again!"
    
    def _get_spelling_feedback(
        self, 
        score: int, 
        user_text: str, 
        target: str
    ) -> str:
        """Generate feedback for spelling attempt."""
        if score >= 90:
            return "Almost perfect! Just a small typo."
        elif score >= 75:
            return "Good try! A few letters are off."
        elif score >= 50:
            return "Keep going! You got some letters right."
        else:
            return f"The correct spelling is '{target}'. Try again!"


# Singleton instance
scoring_service = ScoringService()
