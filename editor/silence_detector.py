"""
Silence detection module.
Detects silence segments in audio using energy-based detection.
"""

import numpy as np
from pydub import AudioSegment
from typing import List, Dict


def detect_silences(
    audio_path: str,
    threshold_db: float = -35.0,
    min_silence_ms: int = 400
) -> List[Dict[str, float]]:
    """
    Detect silence segments in audio file.
    
    Args:
        audio_path: Path to audio file
        threshold_db: Silence threshold in dB (default: -35)
        min_silence_ms: Minimum silence duration in milliseconds (default: 400)
        
    Returns:
        List of silence segments: [{"start": 1.2, "end": 2.0}, ...]
    """
    # Load audio file
    audio = AudioSegment.from_file(audio_path)
    
    # Convert to mono if stereo
    if audio.channels > 1:
        audio = audio.set_channels(1)
    
    # Convert threshold from dB to linear scale
    threshold_linear = 10 ** (threshold_db / 20.0)
    
    # Get raw audio data as numpy array
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    
    # Normalize to [-1, 1]
    if len(samples) > 0:
        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples = samples / max_val
    
    # Calculate window size (use 10ms windows)
    sample_rate = audio.frame_rate
    window_size_ms = 10
    window_size_samples = int(sample_rate * window_size_ms / 1000.0)
    
    # Calculate RMS energy for each window
    silence_segments = []
    current_silence_start = None
    
    for i in range(0, len(samples), window_size_samples):
        window = samples[i:i + window_size_samples]
        if len(window) == 0:
            break
        
        # Calculate RMS energy
        rms = np.sqrt(np.mean(window ** 2))
        
        # Check if below threshold
        is_silent = rms < threshold_linear
        
        window_start_ms = (i / sample_rate) * 1000.0
        window_end_ms = ((i + len(window)) / sample_rate) * 1000.0
        
        if is_silent:
            if current_silence_start is None:
                current_silence_start = window_start_ms
        else:
            # End of silence segment
            if current_silence_start is not None:
                silence_duration = window_start_ms - current_silence_start
                if silence_duration >= min_silence_ms:
                    silence_segments.append({
                        "start": current_silence_start / 1000.0,
                        "end": window_start_ms / 1000.0
                    })
                current_silence_start = None
    
    # Handle silence at the end
    if current_silence_start is not None:
        silence_duration = (len(samples) / sample_rate * 1000.0) - current_silence_start
        if silence_duration >= min_silence_ms:
            silence_segments.append({
                "start": current_silence_start / 1000.0,
                "end": len(samples) / sample_rate
            })
    
    return silence_segments

