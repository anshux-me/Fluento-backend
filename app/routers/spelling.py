"""
Spelling router for evaluating typed spelling attempts.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.schemas import SpellingEvaluateRequest, SpellingEvaluateResponse, TTSGenerateRequest
from app.services.scoring_service import scoring_service
from app.services.tts_service import tts_service

router = APIRouter(prefix="/spelling", tags=["Spelling"])


@router.post("/evaluate", response_model=SpellingEvaluateResponse)
async def evaluate_spelling(request: SpellingEvaluateRequest):
    """
    Evaluate spelling of a word.
    
    - **user_text**: The user's spelling attempt
    - **target_word**: The correct word
    
    Returns score (0-100) and feedback.
    """
    if not request.user_text:
        raise HTTPException(
            status_code=400,
            detail="User text cannot be empty"
        )
    
    if not request.target_word:
        raise HTTPException(
            status_code=400,
            detail="Target word cannot be empty"
        )
    
    result = scoring_service.calculate_spelling_score(
        user_text=request.user_text,
        target_word=request.target_word
    )
    
    return SpellingEvaluateResponse(
        user_text=request.user_text,
        correct_word=request.target_word,
        score=result["score"],
        feedback=result["feedback"]
    )


@router.post("/tts")
async def generate_tts(request: TTSGenerateRequest):
    """
    Generate text-to-speech audio for a word.
    
    - **word**: The word to convert to speech
    
    Returns the audio file.
    """
    if not request.word:
        raise HTTPException(
            status_code=400,
            detail="Word cannot be empty"
        )
    
    try:
        audio_path = tts_service.get_audio_path(request.word)
        
        if audio_path is None or not audio_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Failed to generate audio"
            )
        
        return FileResponse(
            path=str(audio_path),
            media_type="audio/mpeg",
            filename=f"{request.word}.mp3"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating audio: {str(e)}"
        )


@router.get("/tts/{word}")
async def get_tts(word: str):
    """
    Get text-to-speech audio for a word (GET method).
    
    - **word**: The word to convert to speech
    
    Returns the audio file.
    """
    try:
        audio_path = tts_service.get_audio_path(word)
        
        if audio_path is None or not audio_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Failed to generate audio"
            )
        
        return FileResponse(
            path=str(audio_path),
            media_type="audio/mpeg",
            filename=f"{word}.mp3"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating audio: {str(e)}"
        )
