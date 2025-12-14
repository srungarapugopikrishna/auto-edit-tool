FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    torch \
    openai-whisper \
    librosa \
    pydub \
    sentence-transformers \
    numpy \
    scipy

# Copy application code
COPY . /app

# Set Python path
ENV PYTHONPATH=/app

# Default command (can be overridden)
CMD ["python", "run.py"]

