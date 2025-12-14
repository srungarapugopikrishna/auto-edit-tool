"""
Timeline builder module.
Merges all cuts and builds final editing timeline.
"""

from typing import List, Dict


def build_timeline(
    silence_cuts: List[Dict],
    filler_cuts: List[Dict],
    retake_cuts: List[Dict],
    style: Dict,
    total_duration: float
) -> List[Dict[str, any]]:
    """
    Build final editing timeline by merging all cuts.
    
    Args:
        silence_cuts: List of silence segments to cut
        filler_cuts: List of filler segments to cut
        retake_cuts: List of retake segments to cut
        style: Style JSON dictionary
        total_duration: Total video duration in seconds
        
    Returns:
        List of segments to keep:
        [
            {"start": 0.0, "end": 1.8},
            {"start": 2.9, "end": 5.2},
            ...
        ]
    """
    cuts_config = style.get("cuts", {})
    padding_ms = cuts_config.get("padding_ms", 90)
    padding_s = padding_ms / 1000.0
    
    # Combine all cuts
    all_cuts = []
    
    for cut in silence_cuts + filler_cuts + retake_cuts:
        all_cuts.append({
            "start": cut["start"],
            "end": cut["end"]
        })
    
    # Sort by start time
    all_cuts.sort(key=lambda x: x["start"])
    
    # Merge overlapping cuts
    merged_cuts = []
    for cut in all_cuts:
        if not merged_cuts:
            merged_cuts.append(cut)
        else:
            last_cut = merged_cuts[-1]
            # Check overlap
            if cut["start"] <= last_cut["end"]:
                # Merge
                last_cut["end"] = max(last_cut["end"], cut["end"])
            else:
                merged_cuts.append(cut)
    
    # Build keep segments (inverse of cuts)
    keep_segments = []
    current_start = 0.0
    
    for cut in merged_cuts:
        # Add padding
        segment_start = max(0.0, current_start)
        segment_end = max(0.0, cut["start"] - padding_s)
        
        if segment_end > segment_start:
            keep_segments.append({
                "start": segment_start,
                "end": segment_end
            })
        
        current_start = cut["end"] + padding_s
    
    # Add final segment
    if current_start < total_duration:
        keep_segments.append({
            "start": current_start,
            "end": total_duration
        })
    
    # Filter out very short segments
    min_segment_ms = cuts_config.get("min_segment_ms", 100)
    min_segment_s = min_segment_ms / 1000.0
    
    keep_segments = [
        seg for seg in keep_segments
        if seg["end"] - seg["start"] >= min_segment_s
    ]
    
    return keep_segments

