"""
Speech-to-text module using Whisper.
Provides word-level timestamps for Telugu and English.
"""

import whisper
import json
from pathlib import Path
from typing import List, Dict, Optional


class SpeechToText:
    """Whisper-based speech-to-text with word-level timestamps."""
    
    def __init__(self, model_size: str = "medium"):
        """
        Initialize Whisper model.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model = whisper.load_model(model_size)
        self.cache_dir = Path("/tmp/whisper_cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        Transcribe audio with word-level timestamps.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., "te" for Telugu, "en" for English)
                     If None, auto-detect
            use_cache: Whether to use cached transcription if available
            
        Returns:
            Dictionary with transcription data:
            {
                "text": "full transcription",
                "words": [
                    {"text": "word", "start": 1.2, "end": 1.5},
                    ...
                ]
            }
        """
        audio_path = Path(audio_path)
        
        # Check cache
        cache_file = self.cache_dir / f"{audio_path.stem}.json"
        if use_cache and cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # Transcribe with word-level timestamps
        result = self.model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=True,
            verbose=False
        )
        
        # Extract words with timestamps
        words = []
        if "segments" in result:
            for segment in result["segments"]:
                if "words" in segment:
                    for word_info in segment["words"]:
                        words.append({
                            "text": word_info["word"].strip(),
                            "start": word_info["start"],
                            "end": word_info["end"]
                        })
        
        output = {
            "text": result["text"],
            "words": words
        }
        
        # Cache result
        if use_cache:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
        
        return output

