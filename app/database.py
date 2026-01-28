"""
Firestore database integration for LinguaAI.
Handles connection and provides helper functions for user data.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
from typing import Optional
import os

from app.config import settings


# Initialize Firebase Admin SDK
_firebase_app = None
_db = None


def init_firebase():
    """Initialize Firebase Admin SDK with credentials."""
    global _firebase_app, _db
    import json
    
    if _firebase_app is not None:
        return _db
    
    cred = None
    
    # Option 1: Check for inline JSON credentials (preferred for cloud deployments)
    cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if cred_json:
        try:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            print("Using inline Firebase credentials from environment variable")
        except Exception as e:
            print(f"Warning: Could not parse FIREBASE_CREDENTIALS_JSON: {e}")
    
    # Option 2: Check for credentials file
    if cred is None:
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                print(f"Using Firebase credentials from file: {cred_path}")
            except Exception as e:
                print(f"Warning: Could not load credentials file: {e}")
    
    # Initialize Firebase if credentials found
    if cred:
        try:
            _firebase_app = firebase_admin.initialize_app(cred)
            _db = firestore.client()
            print("Firebase initialized successfully")
            return _db
        except Exception as e:
            print(f"Warning: Could not initialize Firebase: {e}")
            print("Running in mock mode - no data will be persisted")
            return None
    else:
        print("Warning: No Firebase credentials found")
        print("Set FIREBASE_CREDENTIALS_JSON env var or provide firebase-credentials.json file")
        print("Running in mock mode - no data will be persisted")
        return None


def get_db():
    """Get Firestore database client."""
    global _db
    if _db is None:
        init_firebase()
    return _db


# ============== User Operations ==============

def get_user(firebase_uid: str) -> Optional[dict]:
    """Get user by Firebase UID."""
    db = get_db()
    if db is None:
        return None
    
    doc = db.collection("users").document(firebase_uid).get()
    if doc.exists:
        return {"id": doc.id, **doc.to_dict()}
    return None


def create_user(firebase_uid: str, email: str, display_name: str = None) -> dict:
    """Create a new user with initial stats."""
    db = get_db()
    if db is None:
        return {"id": firebase_uid, "email": email, "display_name": display_name}
    
    now = datetime.now(timezone.utc)
    
    user_data = {
        "email": email,
        "display_name": display_name or email.split("@")[0],
        "created_at": now,
        "updated_at": now,
        "stats": {
            "total_xp": 0,
            "level": 1,
            "streak": 0,
            "last_practice_date": None,
            "pronunciation_sessions": 0,
            "spelling_sessions": 0,
            "best_pronunciation_score": 0,
            "best_spelling_score": 0,
        },
        "badges": [],
    }
    
    db.collection("users").document(firebase_uid).set(user_data)
    return {"id": firebase_uid, **user_data}


def get_or_create_user(firebase_uid: str, email: str, display_name: str = None) -> dict:
    """Get existing user or create new one."""
    user = get_user(firebase_uid)
    if user:
        return user
    return create_user(firebase_uid, email, display_name)


def update_user_stats(firebase_uid: str, xp_earned: int, mode: str) -> dict:
    """Update user stats after a practice session."""
    db = get_db()
    if db is None:
        return {"error": "Database not available"}
    
    user_ref = db.collection("users").document(firebase_uid)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        return {"error": "User not found"}
    
    user_data = user_doc.to_dict()
    stats = user_data.get("stats", {})
    
    now = datetime.now(timezone.utc)
    today = now.date()
    
    # Update XP and level
    new_total_xp = stats.get("total_xp", 0) + xp_earned
    new_level = (new_total_xp // 500) + 1
    
    # Update streak
    last_practice = stats.get("last_practice_date")
    current_streak = stats.get("streak", 0)
    
    if last_practice:
        if hasattr(last_practice, 'date'):
            last_date = last_practice.date()
        else:
            last_date = last_practice
        
        days_diff = (today - last_date).days
        
        if days_diff == 0:
            # Same day, streak unchanged
            new_streak = current_streak
        elif days_diff == 1:
            # Consecutive day, increment streak
            new_streak = current_streak + 1
        else:
            # Streak broken
            new_streak = 1
    else:
        new_streak = 1
    
    # Update session counts
    if mode == "pronunciation":
        stats["pronunciation_sessions"] = stats.get("pronunciation_sessions", 0) + 1
    elif mode == "spelling":
        stats["spelling_sessions"] = stats.get("spelling_sessions", 0) + 1
    
    # Update stats
    stats["total_xp"] = new_total_xp
    stats["level"] = new_level
    stats["streak"] = new_streak
    stats["last_practice_date"] = now
    
    # Check for new badges
    badges = user_data.get("badges", [])
    new_badges = check_for_badges(stats, badges)
    
    user_ref.update({
        "stats": stats,
        "badges": new_badges,
        "updated_at": now,
    })
    
    return {
        "total_xp": new_total_xp,
        "level": new_level,
        "streak": new_streak,
        "badges": new_badges,
        "xp_earned": xp_earned,
    }


def update_best_score(firebase_uid: str, mode: str, score: int):
    """Update best score if new score is higher."""
    db = get_db()
    if db is None:
        return
    
    user_ref = db.collection("users").document(firebase_uid)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        return
    
    user_data = user_doc.to_dict()
    stats = user_data.get("stats", {})
    
    field = f"best_{mode}_score"
    current_best = stats.get(field, 0)
    
    if score > current_best:
        stats[field] = score
        user_ref.update({"stats": stats})


def check_for_badges(stats: dict, current_badges: list) -> list:
    """Check if user has earned any new badges."""
    badges = current_badges.copy()
    
    total_sessions = stats.get("pronunciation_sessions", 0) + stats.get("spelling_sessions", 0)
    
    badge_conditions = [
        # Immediate/Beginner badges
        ("first_session", total_sessions >= 1, "🎯 First Session", "Completed your first practice!"),
        ("getting_started", stats.get("total_xp", 0) >= 10, "🚀 Getting Started", "Earned 10 XP"),
        ("first_steps", stats.get("total_xp", 0) >= 100, "👣 First Steps", "Earned 100 XP"),
        ("xp_500", stats.get("total_xp", 0) >= 500, "⭐ XP Hunter", "Earned 500 XP"),
        
        # Session badges
        ("five_sessions", total_sessions >= 5, "🎮 Dedicated", "Completed 5 sessions"),
        ("ten_sessions", total_sessions >= 10, "🔥 On Fire", "Completed 10 sessions"),
        ("century", total_sessions >= 100, "💯 Century", "Completed 100 sessions"),
        
        # Streak badges
        ("streak_3", stats.get("streak", 0) >= 3, "📅 3 Day Streak", "3 day practice streak"),
        ("streak_week", stats.get("streak", 0) >= 7, "🗓️ Week Warrior", "7 day streak"),
        ("streak_month", stats.get("streak", 0) >= 30, "📆 Monthly Master", "30 day streak"),
        
        # Level badges
        ("level_2", stats.get("level", 1) >= 2, "🌱 Level 2", "Reached level 2"),
        ("level_5", stats.get("level", 1) >= 5, "🌟 Rising Star", "Reached level 5"),
        ("level_10", stats.get("level", 1) >= 10, "👑 Expert", "Reached level 10"),
        
        # Mode-specific badges
        ("pronunciation_first", stats.get("pronunciation_sessions", 0) >= 1, "🎤 Voice Activated", "First pronunciation practice"),
        ("spelling_first", stats.get("spelling_sessions", 0) >= 1, "📝 Wordsmith", "First spelling practice"),
        ("perfect_pronunciation", stats.get("best_pronunciation_score", 0) >= 100, "🏆 Perfect Pronunciation", "100% pronunciation score"),
        ("perfect_spelling", stats.get("best_spelling_score", 0) >= 100, "🏅 Spelling Bee", "100% spelling score"),
    ]
    
    for badge_id, condition, name, description in badge_conditions:
        if condition and badge_id not in [b.get("id") for b in badges]:
            badges.append({
                "id": badge_id,
                "name": name,
                "description": description,
                "earned_at": datetime.now(timezone.utc),
            })
    
    return badges


# ============== Practice Session Logging ==============

def log_practice_session(firebase_uid: str, mode: str, word: str, score: int, details: dict = None):
    """Log a practice session for analytics."""
    db = get_db()
    if db is None:
        return
    
    session_data = {
        "user_id": firebase_uid,
        "mode": mode,
        "word": word,
        "score": score,
        "details": details or {},
        "created_at": datetime.now(timezone.utc),
    }
    
    db.collection("practice_sessions").add(session_data)
