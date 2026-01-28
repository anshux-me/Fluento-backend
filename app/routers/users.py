"""
Users router for managing user profiles and stats.
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.models.schemas import (
    UserProfileResponse, 
    UserStatsResponse, 
    UpdateStatsRequest, 
    UpdateStatsResponse,
    UserCreateRequest
)
from app.database import (
    get_or_create_user, 
    get_user, 
    update_user_stats,
    update_best_score,
    log_practice_session
)

router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/sync")
async def sync_user(request: UserCreateRequest):
    """
    Sync or create a user from Firebase Auth.
    Called after successful Firebase login.
    """
    user = get_or_create_user(
        firebase_uid=request.firebase_uid,
        email=request.email,
        display_name=request.display_name
    )
    
    if not user:
        raise HTTPException(
            status_code=500,
            detail="Failed to sync user"
        )
    
    return {"message": "User synced successfully", "user_id": user.get("id")}


@router.get("/profile")
async def get_profile(x_firebase_uid: str = Header(..., description="Firebase UID")):
    """
    Get user profile with stats and badges.
    Requires Firebase UID in header.
    """
    user = get_user(x_firebase_uid)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please sync your account first."
        )
    
    stats = user.get("stats", {})
    
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "display_name": user.get("display_name"),
        "stats": {
            "total_xp": stats.get("total_xp", 0),
            "level": stats.get("level", 1),
            "streak": stats.get("streak", 0),
            "pronunciation_sessions": stats.get("pronunciation_sessions", 0),
            "spelling_sessions": stats.get("spelling_sessions", 0),
            "best_pronunciation_score": stats.get("best_pronunciation_score", 0),
            "best_spelling_score": stats.get("best_spelling_score", 0),
        },
        "badges": user.get("badges", [])
    }


@router.get("/stats")
async def get_stats(x_firebase_uid: str = Header(..., description="Firebase UID")):
    """
    Get user stats only.
    Requires Firebase UID in header.
    """
    user = get_user(x_firebase_uid)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    stats = user.get("stats", {})
    
    return UserStatsResponse(
        total_xp=stats.get("total_xp", 0),
        level=stats.get("level", 1),
        streak=stats.get("streak", 0),
        pronunciation_sessions=stats.get("pronunciation_sessions", 0),
        spelling_sessions=stats.get("spelling_sessions", 0),
        best_pronunciation_score=stats.get("best_pronunciation_score", 0),
        best_spelling_score=stats.get("best_spelling_score", 0)
    )


@router.post("/stats", response_model=UpdateStatsResponse)
async def update_stats(
    request: UpdateStatsRequest,
    x_firebase_uid: str = Header(..., description="Firebase UID")
):
    """
    Update user stats after a practice session.
    Requires Firebase UID in header.
    
    - **xp_earned**: XP earned in this session (0-100)
    - **mode**: "pronunciation" or "spelling"
    """
    result = update_user_stats(
        firebase_uid=x_firebase_uid,
        xp_earned=request.xp_earned,
        mode=request.mode
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )
    
    return UpdateStatsResponse(
        total_xp=result["total_xp"],
        level=result["level"],
        streak=result["streak"],
        xp_earned=result["xp_earned"],
        badges=result["badges"]
    )


@router.post("/log-session")
async def log_session(
    word: str,
    mode: str,
    score: int,
    x_firebase_uid: str = Header(..., description="Firebase UID")
):
    """
    Log a practice session and update best score if applicable.
    """
    # Update best score
    update_best_score(x_firebase_uid, mode, score)
    
    # Log the session
    log_practice_session(
        firebase_uid=x_firebase_uid,
        mode=mode,
        word=word,
        score=score
    )
    
    return {"message": "Session logged successfully"}
