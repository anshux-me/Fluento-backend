# LinguaAI Backend

FastAPI backend for the LinguaAI language learning platform.

## Features

- **Whisper STT**: Speech-to-text using OpenAI Whisper
- **Coqui TTS**: Text-to-speech for spelling practice  
- **Phonemizer**: Pronunciation scoring with phoneme analysis
- **Firestore**: User data and gamification stats

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt install espeak-ng ffmpeg

# Copy environment file
cp .env.example .env

# Run server
uvicorn app.main:app --reload --port 8000
```

## API Docs

Once running, visit: http://localhost:8000/docs

## Docker

```bash
docker build -t linguaai-backend .
docker run -p 8000:8000 linguaai-backend
```
