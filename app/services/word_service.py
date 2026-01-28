"""
Word service for loading and filtering the WordNet-derived dataset.
"""

import json
import random
from pathlib import Path
from typing import Optional, List
from app.config import settings


class WordService:
    """Service for managing the word dataset."""
    
    def __init__(self):
        self.words: List[dict] = []
        self.words_by_difficulty: dict = {
            "easy": [],
            "medium": [],
            "hard": [],
        }
        self._loaded = False
    
    def load_words(self, words_file: Path = None):
        """Load words from JSON file and index by difficulty."""
        if self._loaded:
            return
        
        if words_file is None:
            words_file = settings.DATA_DIR / "words.json"
        
        # Also check for wordnet_full.json
        if not words_file.exists():
            words_file = settings.BASE_DIR.parent / "wordnet_full.json"
        
        if not words_file.exists():
            print(f"Warning: Words file not found at {words_file}")
            # Create some sample words for testing
            self._create_sample_words()
            self._loaded = True
            return
        
        with open(words_file, "r", encoding="utf-8") as f:
            self.words = json.load(f)
        
        # Index words by difficulty
        for word in self.words:
            difficulty = word.get("difficulty", "Medium").lower()
            if difficulty in self.words_by_difficulty:
                self.words_by_difficulty[difficulty].append(word)
        
        print(f"Loaded {len(self.words)} words:")
        for diff, words in self.words_by_difficulty.items():
            print(f"  {diff}: {len(words)} words")
        
        self._loaded = True
    
    def _create_sample_words(self):
        """Create sample words for testing if dataset is missing."""
        sample_words = [
            {"word": "cat", "pos": "n", "difficulty": "Easy", "definitions": ["a small domesticated carnivorous mammal"], "examples": ["The cat sat on the mat"], "synonyms": ["feline", "kitty"]},
            {"word": "dog", "pos": "n", "difficulty": "Easy", "definitions": ["a domesticated carnivorous mammal"], "examples": ["The dog barked loudly"], "synonyms": ["canine", "hound"]},
            {"word": "happy", "pos": "a", "difficulty": "Easy", "definitions": ["feeling or showing pleasure"], "examples": ["She was happy to see him"], "synonyms": ["joyful", "cheerful"]},
            {"word": "beautiful", "pos": "a", "difficulty": "Medium", "definitions": ["pleasing the senses or mind aesthetically"], "examples": ["A beautiful sunset"], "synonyms": ["gorgeous", "stunning"]},
            {"word": "eloquent", "pos": "a", "difficulty": "Hard", "definitions": ["fluent or persuasive in speaking or writing"], "examples": ["An eloquent speaker"], "synonyms": ["articulate", "expressive"]},
            {"word": "ephemeral", "pos": "a", "difficulty": "Hard", "definitions": ["lasting for a very short time"], "examples": ["Ephemeral pleasures"], "synonyms": ["transient", "fleeting"]},
            {"word": "ubiquitous", "pos": "a", "difficulty": "Hard", "definitions": ["present, appearing, or found everywhere"], "examples": ["Smartphones are now ubiquitous"], "synonyms": ["omnipresent", "pervasive"]},
            {"word": "run", "pos": "v", "difficulty": "Easy", "definitions": ["move at a speed faster than a walk"], "examples": ["He ran to catch the bus"], "synonyms": ["sprint", "dash"]},
            {"word": "comprehend", "pos": "v", "difficulty": "Medium", "definitions": ["grasp mentally; understand"], "examples": ["I cannot comprehend his motives"], "synonyms": ["understand", "grasp"]},
            {"word": "ameliorate", "pos": "v", "difficulty": "Hard", "definitions": ["make something bad or unsatisfactory better"], "examples": ["Steps to ameliorate the situation"], "synonyms": ["improve", "enhance"]},
        ]
        
        self.words = sample_words
        for word in sample_words:
            difficulty = word.get("difficulty", "Medium").lower()
            if difficulty in self.words_by_difficulty:
                self.words_by_difficulty[difficulty].append(word)
    
    def get_random_word(self, difficulty: str = None, mode: str = "pronunciation") -> Optional[dict]:
        """Get a random word, optionally filtered by difficulty."""
        if not self._loaded:
            self.load_words()
        
        if difficulty:
            difficulty = difficulty.lower()
            words = self.words_by_difficulty.get(difficulty, [])
            if not words:
                words = self.words
        else:
            words = self.words
        
        if not words:
            return None
        
        word_data = random.choice(words)
        
        return {
            "word": word_data.get("word", ""),
            "pos": word_data.get("pos", ""),
            "difficulty": word_data.get("difficulty", "Medium"),
            "definition": word_data.get("definitions", [""])[0] if word_data.get("definitions") else "",
            "examples": word_data.get("examples", []),
            "synonyms": word_data.get("synonyms", []),
        }
    
    def get_word_count(self, difficulty: str = None) -> int:
        """Get the count of words, optionally filtered by difficulty."""
        if not self._loaded:
            self.load_words()
        
        if difficulty:
            return len(self.words_by_difficulty.get(difficulty.lower(), []))
        return len(self.words)


# Singleton instance
word_service = WordService()
