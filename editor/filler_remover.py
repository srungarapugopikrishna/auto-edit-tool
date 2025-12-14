"""
Filler word removal module.
Removes filler words based on style rules.
"""

from typing import List, Dict
from editor.speech_to_text import SpeechToText


def remove_fillers(
    words: List[Dict],
    style: Dict
) -> List[Dict[str, any]]:
    """
    Identify filler words to remove based on style rules.
    
    Args:
        words: List of word dicts with "text", "start", "end"
        style: Style JSON dictionary
        
    Returns:
        List of segments to cut:
        [
            {"start": 1.2, "end": 1.5, "type": "filler"},
            ...
        ]
    """
    filler_config = style.get("fillers", {})
    filler_words = filler_config.get("words", [])
    min_pause_ms = filler_config.get("min_pause_ms", 280)
    max_duration_ms = filler_config.get("max_duration_ms", 2000)
    
    cuts = []
    
    for i, word in enumerate(words):
        word_text = word["text"].lower().strip()
        
        # Check if word is a filler
        is_filler = False
        for filler in filler_words:
            if filler.lower() in word_text or word_text in filler.lower():
                is_filler = True
                break
        
        if not is_filler:
            continue
        
        # Check duration
        duration_ms = (word["end"] - word["start"]) * 1000
        if duration_ms > max_duration_ms:
            continue
        
        # Check if followed by pause
        has_pause_after = False
        if i < len(words) - 1:
            next_word = words[i + 1]
            pause_duration = (next_word["start"] - word["end"]) * 1000
            if pause_duration >= min_pause_ms:
                has_pause_after = True
        
        # Check if preceded by pause (standalone usage)
        has_pause_before = False
        if i > 0:
            prev_word = words[i - 1]
            pause_duration = (word["start"] - prev_word["end"]) * 1000
            if pause_duration >= min_pause_ms:
                has_pause_before = True
        
        # Remove if standalone or followed by pause
        if has_pause_after or has_pause_before:
            cuts.append({
                "start": word["start"],
                "end": word["end"],
                "type": "filler"
            })
    
    return cuts

