"""
Audio alignment module for style learning.
Aligns raw and edited audio to detect removed segments.
"""

import numpy as np
from pydub import AudioSegment
from typing import List, Dict


def align_audio(
    raw_audio_path: str,
    edited_audio_path: str,
    window_size: float = 0.5
) -> List[Dict[str, any]]:
    """
    Align raw and edited audio to detect removed segments.
    
    Args:
        raw_audio_path: Path to raw audio file
        edited_audio_path: Path to edited audio file
        window_size: Window size in seconds for alignment (default: 0.5)
        
    Returns:
        List of segments with actions:
        [
            {"start": 0.0, "end": 1.8, "action": "keep"},
            {"start": 1.8, "end": 2.9, "action": "cut"},
            ...
        ]
    """
    # Load audio files
    raw_audio = AudioSegment.from_file(raw_audio_path)
    edited_audio = AudioSegment.from_file(edited_audio_path)
    
    raw_duration = len(raw_audio) / 1000.0  # Convert to seconds
    edited_duration = len(edited_audio) / 1000.0
    
    # Convert to numpy arrays for comparison
    raw_samples = np.array(raw_audio.get_array_of_samples())
    edited_samples = np.array(edited_audio.get_array_of_samples())
    
    # Normalize
    if len(raw_samples) > 0:
        raw_samples = raw_samples.astype(np.float32) / np.max(np.abs(raw_samples))
    if len(edited_samples) > 0:
        edited_samples = edited_samples.astype(np.float32) / np.max(np.abs(edited_samples))
    
    # Simple alignment: compare energy in windows
    window_samples = int(window_size * raw_audio.frame_rate)
    segments = []
    
    raw_pos = 0
    edited_pos = 0
    current_start = 0.0
    
    while raw_pos < len(raw_samples) and edited_pos < len(edited_samples):
        # Extract windows
        raw_window = raw_samples[raw_pos:raw_pos + window_samples]
        edited_window = edited_samples[edited_pos:edited_pos + window_samples]
        
        # Calculate energy
        raw_energy = np.mean(np.abs(raw_window)) if len(raw_window) > 0 else 0
        edited_energy = np.mean(np.abs(edited_window)) if len(edited_window) > 0 else 0
        
        # Threshold for matching
        energy_threshold = 0.1
        
        if abs(raw_energy - edited_energy) < energy_threshold and raw_energy > 0.01:
            # Match found - keep segment
            if segments and segments[-1]["action"] == "keep":
                # Extend existing keep segment
                segments[-1]["end"] = (raw_pos + window_samples) / raw_audio.frame_rate
            else:
                # Start new keep segment
                segments.append({
                    "start": raw_pos / raw_audio.frame_rate,
                    "end": (raw_pos + window_samples) / raw_audio.frame_rate,
                    "action": "keep"
                })
            raw_pos += window_samples
            edited_pos += window_samples
        else:
            # No match - cut segment
            if segments and segments[-1]["action"] == "cut":
                # Extend existing cut segment
                segments[-1]["end"] = (raw_pos + window_samples) / raw_audio.frame_rate
            else:
                # Start new cut segment
                if segments:
                    segments[-1]["end"] = raw_pos / raw_audio.frame_rate
                segments.append({
                    "start": raw_pos / raw_audio.frame_rate,
                    "end": (raw_pos + window_samples) / raw_audio.frame_rate,
                    "action": "cut"
                })
            raw_pos += window_samples
    
    # Handle remaining raw audio
    if raw_pos < len(raw_samples):
        if segments and segments[-1]["action"] == "cut":
            segments[-1]["end"] = raw_duration
        else:
            segments.append({
                "start": raw_pos / raw_audio.frame_rate,
                "end": raw_duration,
                "action": "cut"
            })
    
    # Merge adjacent segments with same action
    merged_segments = []
    for seg in segments:
        if merged_segments and merged_segments[-1]["action"] == seg["action"]:
            merged_segments[-1]["end"] = seg["end"]
        else:
            merged_segments.append(seg)
    
    return merged_segments

