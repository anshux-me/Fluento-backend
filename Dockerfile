# LinguaAI Backend Dockerfile
# Using bullseye for FFmpeg 4.x compatibility with PyAV

FROM python:3.11-slim-bullseye as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For audio processing
    ffmpeg \
    libsndfile1 \
    # For phonemizer (espeak)
    espeak-ng \
    # Build tools (required for faster-whisper/PyAV)
    build-essential \
    git \
    pkg-config \
    # FFmpeg dev libraries (required for PyAV)
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Create data directories
RUN mkdir -p /app/data/audio_cache /app/data/models && \
    chown -R app:app /app/data

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
