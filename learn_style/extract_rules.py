"""
Rule extraction module.
Aggregates editor behavior into numeric rules for style JSON.
"""

from typing import List, Dict
import json
import numpy as np


def extract_rules(
    classified_segments: List[Dict[str, any]],
    raw_audio_path: str
) -> Dict:
    """
    Extract editing rules from classified segments.
    
    Args:
        classified_segments: List of classified segments from classify_removals
        raw_audio_path: Path to raw audio file
        
    Returns:
        Style JSON dictionary:
        {
            "silence": {"min_ms": 460},
            "fillers": {
                "words": ["అంటే", "అదే", "so"],
                "min_pause_ms": 280
            },
            "retakes": {
                "strategy": "keep_last",
                "similarity_threshold": 0.85
            },
            "cuts": {
                "padding_ms": 90,
                "crossfade_ms": 80
            }
        }
    """
    # Analyze silence removals
    silence_cuts = [
        seg for seg in classified_segments
        if seg.get("type") == "silence" and seg.get("action") == "cut"
    ]
    
    min_silence_ms = 400  # Default
    if silence_cuts:
        silence_durations = [
            (seg["end"] - seg["start"]) * 1000
            for seg in silence_cuts
        ]
        min_silence_ms = int(np.percentile(silence_durations, 25))  # 25th percentile
    
    # Analyze filler removals
    filler_cuts = [
        seg for seg in classified_segments
        if seg.get("type") == "filler" and seg.get("action") == "cut"
    ]
    
    filler_words = set()
    filler_pause_durations = []
    
    # Extract filler words and pause patterns
    # This would need transcription data - simplified here
    common_fillers = ["అంటే", "అదే", "so", "um", "uh"]
    
    # Analyze retake patterns
    retake_cuts = [
        seg for seg in classified_segments
        if seg.get("type") == "retake" and seg.get("action") == "cut"
    ]
    
    # Default style profile
    style = {
        "silence": {
            "min_ms": min_silence_ms,
            "threshold_db": -35.0
        },
        "fillers": {
            "words": common_fillers,
            "min_pause_ms": 280,
            "max_duration_ms": 2000
        },
        "retakes": {
            "strategy": "keep_last",
            "similarity_threshold": 0.85,
            "max_gap_seconds": 10.0
        },
        "cuts": {
            "padding_ms": 90,
            "crossfade_ms": 80,
            "min_segment_ms": 100
        }
    }
    
    return style

