"""
Retake detection module.
Detects and removes retakes, keeping the final/best take.
"""

from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np


class RetakeDetector:
    """Detects retakes using semantic similarity."""
    
    def __init__(self):
        """Initialize sentence transformer model."""
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    def detect_retakes(
        self,
        words: List[Dict],
        style: Dict
    ) -> List[Dict[str, any]]:
        """
        Detect retake segments to remove.
        
        Args:
            words: List of word dicts with "text", "start", "end"
            style: Style JSON dictionary
            
        Returns:
            List of segments to cut:
            [
                {"start": 5.2, "end": 8.1, "type": "retake"},
                ...
            ]
        """
        retake_config = style.get("retakes", {})
        strategy = retake_config.get("strategy", "keep_last")
        similarity_threshold = retake_config.get("similarity_threshold", 0.85)
        max_gap_seconds = retake_config.get("max_gap_seconds", 10.0)
        
        # Group words into sentences
        sentences = self._group_into_sentences(words)
        
        if len(sentences) < 2:
            return []
        
        # Compute embeddings
        sentence_texts = [s["text"] for s in sentences]
        embeddings = self.model.encode(sentence_texts)
        
        # Find similar sentences (potential retakes)
        cuts = []
        removed_indices = set()
        
        for i in range(len(sentences) - 1):
            if i in removed_indices:
                continue
            
            for j in range(i + 1, len(sentences)):
                if j in removed_indices:
                    continue
                
                # Check gap
                gap = sentences[j]["start"] - sentences[i]["end"]
                if gap > max_gap_seconds:
                    break  # Too far apart
                
                # Compute similarity
                similarity = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                )
                
                if similarity >= similarity_threshold:
                    # Similar content found - remove earlier one (keep last)
                    if strategy == "keep_last":
                        cuts.append({
                            "start": sentences[i]["start"],
                            "end": sentences[i]["end"],
                            "type": "retake"
                        })
                        removed_indices.add(i)
                        break
        
        return cuts
    
    def _group_into_sentences(self, words: List[Dict]) -> List[Dict]:
        """Group words into sentences based on pauses."""
        if not words:
            return []
        
        sentences = []
        current_sentence = {
            "text": "",
            "words": [],
            "start": words[0]["start"],
            "end": words[0]["end"]
        }
        
        for i, word in enumerate(words):
            # Add word to current sentence
            if current_sentence["text"]:
                current_sentence["text"] += " "
            current_sentence["text"] += word["text"]
            current_sentence["words"].append(word)
            current_sentence["end"] = word["end"]
            
            # Check for sentence boundary (pause > 0.5s or end of words)
            if i < len(words) - 1:
                next_word = words[i + 1]
                pause = next_word["start"] - word["end"]
                
                if pause > 0.5:  # Sentence boundary
                    sentences.append(current_sentence)
                    current_sentence = {
                        "text": "",
                        "words": [],
                        "start": next_word["start"],
                        "end": next_word["end"]
                    }
        
        # Add last sentence
        if current_sentence["text"]:
            sentences.append(current_sentence)
        
        return sentences

