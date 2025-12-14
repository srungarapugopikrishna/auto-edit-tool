"""
Removal classification module.
Classifies removed segments as silence, filler, retake, or noise.
"""

from typing import List, Dict
from editor.speech_to_text import SpeechToText
from editor.silence_detector import detect_silences
import numpy as np


def classify_removals(
    raw_audio_path: str,
    cut_segments: List[Dict[str, any]],
    stt: SpeechToText
) -> List[Dict[str, any]]:
    """
    Classify removed segments by type.
    
    Args:
        raw_audio_path: Path to raw audio file
        cut_segments: List of segments marked as "cut" from alignment
        stt: SpeechToText instance for transcription
        
    Returns:
        List of classified segments:
        [
            {
                "start": 1.8,
                "end": 2.9,
                "action": "cut",
                "type": "silence" | "filler" | "retake" | "noise"
            },
            ...
        ]
    """
    # Get silence segments
    silence_segments = detect_silences(raw_audio_path)
    
    # Get transcription
    transcription = stt.transcribe(raw_audio_path, language="te")
    words = transcription.get("words", [])
    
    # Common filler words (Telugu + English)
    filler_words = [
        "అంటే", "అదే", "అవును", "అలాగే", "అంతే",
        "so", "um", "uh", "like", "you know", "actually"
    ]
    
    classified = []
    
    for seg in cut_segments:
        if seg["action"] != "cut":
            classified.append(seg)
            continue
        
        start = seg["start"]
        end = seg["end"]
        duration = end - start
        
        # Check if it's silence
        is_silence = False
        for silence in silence_segments:
            # Check overlap
            if (start <= silence["end"] and end >= silence["start"]):
                overlap_start = max(start, silence["start"])
                overlap_end = min(end, silence["end"])
                overlap_ratio = (overlap_end - overlap_start) / duration
                if overlap_ratio > 0.5:
                    is_silence = True
                    break
        
        if is_silence:
            classified.append({
                **seg,
                "type": "silence"
            })
            continue
        
        # Check if it contains filler words
        segment_words = [
            w for w in words
            if start <= w["start"] < end or start < w["end"] <= end
        ]
        
        is_filler = False
        if segment_words:
            segment_text = " ".join([w["text"] for w in segment_words]).lower()
            for filler in filler_words:
                if filler.lower() in segment_text:
                    is_filler = True
                    break
        
        if is_filler:
            classified.append({
                **seg,
                "type": "filler"
            })
            continue
        
        # Check if it's a retake (similar content before/after)
        # This is a simplified check - in practice, you'd compare semantic similarity
        is_retake = False
        if duration > 1.0 and duration < 10.0:  # Reasonable retake duration
            # Check for similar words nearby
            before_words = [w for w in words if w["end"] <= start and start - w["end"] < 5.0]
            after_words = [w for w in words if w["start"] >= end and w["start"] - end < 5.0]
            
            if before_words and after_words:
                before_text = " ".join([w["text"] for w in before_words[-5:]]).lower()
                after_text = " ".join([w["text"] for w in after_words[:5]]).lower()
                
                # Simple similarity check (word overlap)
                before_set = set(before_text.split())
                after_set = set(after_text.split())
                if len(before_set & after_set) > 2:
                    is_retake = True
        
        if is_retake:
            classified.append({
                **seg,
                "type": "retake"
            })
            continue
        
        # Default to noise
        classified.append({
            **seg,
            "type": "noise"
        })
    
    return classified

