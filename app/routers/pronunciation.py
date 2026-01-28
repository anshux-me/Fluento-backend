"""
Pronunciation router for evaluating spoken words.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.schemas import PronunciationEvaluateResponse
from app.services.whisper_service import whisper_service
from app.services.scoring_service import scoring_service
from app.config import settings

router = APIRouter(prefix="/pronunciation", tags=["Pronunciation"])


@router.post("/evaluate", response_model=PronunciationEvaluateResponse)
async def evaluate_pronunciation(
    audio_file: UploadFile = File(..., description="Audio file of pronunciation"),
    target_word: str = Form(..., description="The target word to match")
):
    """
    Evaluate pronunciation of a word.
    
    - **audio_file**: Audio recording (WAV, WebM, MP3, OGG)
    - **target_word**: The word the user was trying to pronounce
    
    Returns recognized text, phoneme comparison, score (0-100), and feedback.
    """
    # Validate file type
    content_type = audio_file.content_type or ""
    if not any(t in content_type for t in ["audio", "webm", "wav", "mp3", "ogg"]):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {content_type}. Allowed: audio/wav, audio/webm, audio/mp3, audio/ogg"
        )
    
    # Read audio content
    audio_content = await audio_file.read()
    
    # Check file size
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(audio_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Get file extension
    filename = audio_file.filename or "audio.webm"
    suffix = "." + filename.split(".")[-1] if "." in filename else ".webm"
    
    try:
        # Transcribe audio
        recognized_text = whisper_service.transcribe_bytes(audio_content, suffix=suffix)
        
        # Calculate score
        result = scoring_service.calculate_pronunciation_score(
            recognized_text=recognized_text,
            target_word=target_word
        )
        
        return PronunciationEvaluateResponse(
            recognized_text=recognized_text,
            target_word=target_word,
            score=result["score"],
            target_phonemes=result["target_phonemes"],
            recognized_phonemes=result["recognized_phonemes"],
            feedback=result["feedback"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )
