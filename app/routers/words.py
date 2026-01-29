"""
Word router for fetching words based on mode and difficulty.
"""

from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import WordResponse
from app.services.word_service import word_service

router = APIRouter(prefix="/word", tags=["Words"])


@router.get("/daily")
async def get_daily_words():
    """
    Get the 5 words of the day.
    Returns 2 easy, 2 medium, 1 hard word with meanings.
    Same words are returned for the entire day.
    """
    words = word_service.get_daily_words()
    return {"words": words}


@router.get("/stats")
async def word_stats():
    """Get word count statistics by difficulty."""
    return {
        "total_words": word_service.get_word_count(),
        "easy": word_service.get_word_count("easy"),
        "medium": word_service.get_word_count("medium"),
        "hard": word_service.get_word_count("hard")
    }


@router.get("/{mode}/{difficulty}", response_model=WordResponse)
async def get_word(
    mode: str,
    difficulty: str
):
    """
    Get a random word for practice.
    
    - **mode**: "pronunciation" or "spelling"
    - **difficulty**: "easy", "medium", or "hard"
    """
    # Validate mode
    if mode not in ["pronunciation", "spelling"]:
        raise HTTPException(
            status_code=400,
            detail="Mode must be 'pronunciation' or 'spelling'"
        )
    
    # Validate difficulty
    if difficulty.lower() not in ["easy", "medium", "hard"]:
        raise HTTPException(
            status_code=400,
            detail="Difficulty must be 'easy', 'medium', or 'hard'"
        )
    
    word = word_service.get_random_word(difficulty=difficulty, mode=mode)
    
    if not word:
        raise HTTPException(
            status_code=404,
            detail=f"No words found for difficulty: {difficulty}"
        )
    
    return WordResponse(
        word=word["word"],
        pos=word["pos"],
        difficulty=word["difficulty"],
        definition=word["definition"],
        examples=word["examples"],
        synonyms=word["synonyms"]
    )


@router.get("/count")
async def get_word_count(
    difficulty: str = Query(None, description="Filter by difficulty")
):
    """Get the total count of words in the dataset."""
    count = word_service.get_word_count(difficulty)
    return {"count": count, "difficulty": difficulty}
