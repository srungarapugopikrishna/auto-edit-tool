"""
Style Learning Mode Entrypoint.
Learns editing style from raw + edited video pairs.
"""

import json
import sys
from pathlib import Path
from editor.extract_audio import extract_audio
from learn_style.align_audio import align_audio
from learn_style.classify_removals import classify_removals
from learn_style.extract_rules import extract_rules
from editor.speech_to_text import SpeechToText


def learn_style(
    raw_video_path: str,
    edited_video_path: str,
    output_style_path: str
):
    """
    Learn editing style from raw and edited video pair.
    
    Args:
        raw_video_path: Path to raw video
        edited_video_path: Path to edited video
        output_style_path: Path to save style JSON
    """
    print(f"Learning style from:")
    print(f"  Raw: {raw_video_path}")
    print(f"  Edited: {edited_video_path}")
    
    # Extract audio
    print("\n[1/5] Extracting audio...")
    raw_audio = extract_audio(raw_video_path)
    edited_audio = extract_audio(edited_video_path)
    print(f"  Raw audio: {raw_audio}")
    print(f"  Edited audio: {edited_audio}")
    
    # Align audio
    print("\n[2/5] Aligning audio...")
    aligned_segments = align_audio(raw_audio, edited_audio)
    print(f"  Found {len(aligned_segments)} segments")
    
    # Initialize STT
    print("\n[3/5] Initializing speech-to-text...")
    stt = SpeechToText(model_size="medium")
    
    # Classify removals
    print("\n[4/5] Classifying removals...")
    classified_segments = classify_removals(raw_audio, aligned_segments, stt)
    
    removal_counts = {}
    for seg in classified_segments:
        if seg.get("action") == "cut":
            removal_type = seg.get("type", "unknown")
            removal_counts[removal_type] = removal_counts.get(removal_type, 0) + 1
    
    print(f"  Removal breakdown:")
    for removal_type, count in removal_counts.items():
        print(f"    {removal_type}: {count}")
    
    # Extract rules
    print("\n[5/5] Extracting rules...")
    style = extract_rules(classified_segments, raw_audio)
    
    # Save style JSON
    output_path = Path(output_style_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(style, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Style saved to: {output_style_path}")
    print(f"  Silence min: {style['silence']['min_ms']}ms")
    print(f"  Filler words: {len(style['fillers']['words'])}")
    print(f"  Retake strategy: {style['retakes']['strategy']}")


def main():
    """Main entrypoint for style learning."""
    # Supported video formats
    video_extensions = ["*.mp4", "*.mov", "*.avi", "*.mkv", "*.m4v", "*.flv", "*.wmv", "*.webm"]
    
    # Default paths (can be overridden via command line)
    raw_dir = Path("/input/raw")
    edited_dir = Path("/input/edited")
    styles_dir = Path("/styles")
    
    # Find video pairs (search for all supported formats)
    raw_videos = []
    edited_videos = []
    
    if raw_dir.exists():
        for ext in video_extensions:
            raw_videos.extend(list(raw_dir.glob(ext)))
            raw_videos.extend(list(raw_dir.glob(ext.upper())))  # Also check uppercase
    
    if edited_dir.exists():
        for ext in video_extensions:
            edited_videos.extend(list(edited_dir.glob(ext)))
            edited_videos.extend(list(edited_dir.glob(ext.upper())))  # Also check uppercase
    
    if not raw_videos:
        print("ERROR: No raw videos found in /input/raw/")
        print(f"Supported formats: {', '.join([ext.replace('*', '') for ext in video_extensions])}")
        print("Please place raw video files in /input/raw/")
        sys.exit(1)
    
    if not edited_videos:
        print("ERROR: No edited videos found in /input/edited/")
        print(f"Supported formats: {', '.join([ext.replace('*', '') for ext in video_extensions])}")
        print("Please place edited video files in /input/edited/")
        sys.exit(1)
    
    # Use first pair (or match by name)
    raw_video = raw_videos[0]
    
    # Try to find matching edited video
    edited_video = None
    for ev in edited_videos:
        if ev.stem == raw_video.stem or ev.stem.startswith(raw_video.stem):
            edited_video = ev
            break
    
    if not edited_video:
        edited_video = edited_videos[0]
    
    # Determine style version
    styles_dir.mkdir(parents=True, exist_ok=True)
    existing_styles = list(styles_dir.glob("telugu_news_v*.json"))
    version = len(existing_styles) + 1
    style_path = styles_dir / f"telugu_news_v{version}.json"
    
    # Learn style
    learn_style(
        str(raw_video),
        str(edited_video),
        str(style_path)
    )


if __name__ == "__main__":
    main()

