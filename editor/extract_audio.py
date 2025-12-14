"""
Audio extraction module.
Extracts audio from video files using FFmpeg.
"""

import subprocess
import os
from pathlib import Path


def extract_audio(video_path: str, output_path: str = None) -> str:
    """
    Extract audio from video file.
    
    Args:
        video_path: Path to input video file
        output_path: Optional path for output WAV file
        
    Returns:
        Path to extracted audio file
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_audio.wav"
    else:
        output_path = Path(output_path)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract audio using FFmpeg: mono, 16kHz, WAV format
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-ac", "1",  # Mono
        "-ar", "16000",  # 16kHz sample rate
        "-y",  # Overwrite output file
        str(output_path)
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    
    if not output_path.exists():
        raise RuntimeError(f"Audio extraction failed: {result.stderr}")
    
    return str(output_path)

