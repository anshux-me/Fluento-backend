"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============== Word Schemas ==============

class WordResponse(BaseModel):
    """Response schema for word endpoints."""
    word: str
    pos: str
    difficulty: str
    definition: str
    examples: List[str] = []
    synonyms: List[str] = []


# ============== Pronunciation Schemas ==============

class PronunciationEvaluateResponse(BaseModel):
    """Response schema for pronunciation evaluation."""
    recognized_text: str
    target_word: str
    score: int = Field(ge=0, le=100)
    target_phonemes: str
    recognized_phonemes: str
    feedback: str


# ============== Spelling Schemas ==============

class SpellingEvaluateRequest(BaseModel):
    """Request schema for spelling evaluation."""
    user_text: str
    target_word: str


class SpellingEvaluateResponse(BaseModel):
    """Response schema for spelling evaluation."""
    user_text: str
    correct_word: str
    score: int = Field(ge=0, le=100)
    feedback: str


# ============== TTS Schemas ==============

class TTSGenerateRequest(BaseModel):
    """Request schema for TTS generation."""
    word: str


# ============== User Schemas ==============

class UserStatsResponse(BaseModel):
    """Response schema for user stats."""
    total_xp: int
    level: int
    streak: int
    pronunciation_sessions: int
    spelling_sessions: int
    best_pronunciation_score: int
    best_spelling_score: int


class UserProfileResponse(BaseModel):
    """Response schema for user profile."""
    id: str
    email: str
    display_name: str
    stats: UserStatsResponse
    badges: List[dict]


class UpdateStatsRequest(BaseModel):
    """Request schema for updating user stats."""
    xp_earned: int = Field(ge=0, le=100)
    mode: str = Field(pattern="^(pronunciation|spelling)$")


class UpdateStatsResponse(BaseModel):
    """Response schema for stats update."""
    total_xp: int
    level: int
    streak: int
    xp_earned: int
    badges: List[dict]


# ============== Auth Schemas ==============

class UserCreateRequest(BaseModel):
    """Request schema for creating/syncing a user."""
    firebase_uid: str
    email: str
    display_name: Optional[str] = None
