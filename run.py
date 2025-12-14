"""
Auto Editing Mode Entrypoint.
Applies frozen style profile to auto-edit new videos.
"""

import json
import sys
from pathlib import Path
from editor.extract_audio import extract_audio
from editor.silence_detector import detect_silences
from editor.speech_to_text import SpeechToText
from editor.filler_remover import remove_fillers
from editor.retake_detector import RetakeDetector
from editor.timeline_builder import build_timeline
from editor.video_cutter import cut_video
from pydub import AudioSegment


def load_style(style_path: str) -> dict:
    """Load style JSON file."""
    style_path = Path(style_path)
    if not style_path.exists():
        raise FileNotFoundError(f"Style file not found: {style_path}")
    
    with open(style_path, "r", encoding="utf-8") as f:
        return json.load(f)


def auto_edit(
    input_video_path: str,
    style_path: str,
    output_video_path: str
):
    """
    Auto-edit video using frozen style profile.
    
    Args:
        input_video_path: Path to raw input video
        style_path: Path to style JSON file
        output_video_path: Path to output edited video
    """
    print("=" * 60)
    print("AUTO EDITING MODE")
    print("=" * 60)
    print(f"Input: {input_video_path}")
    print(f"Style: {style_path}")
    print(f"Output: {output_video_path}")
    print()
    
    # Load style (frozen, no modifications)
    print("[1/7] Loading style profile...")
    style = load_style(style_path)
    print(f"  ✓ Style loaded: {style_path}")
    print(f"    Silence min: {style['silence']['min_ms']}ms")
    print(f"    Filler words: {len(style['fillers']['words'])}")
    
    # Extract audio
    print("\n[2/7] Extracting audio...")
    audio_path = extract_audio(input_video_path)
    print(f"  ✓ Audio extracted: {audio_path}")
    
    # Get video duration
    audio = AudioSegment.from_file(audio_path)
    total_duration = len(audio) / 1000.0
    print(f"  Duration: {total_duration:.2f}s")
    
    # Detect silences
    print("\n[3/7] Detecting silences...")
    silence_config = style.get("silence", {})
    silence_cuts = detect_silences(
        audio_path,
        threshold_db=silence_config.get("threshold_db", -35.0),
        min_silence_ms=silence_config.get("min_ms", 400)
    )
    print(f"  ✓ Found {len(silence_cuts)} silence segments")
    
    # Speech-to-text
    print("\n[4/7] Transcribing speech...")
    stt = SpeechToText(model_size="medium")
    transcription = stt.transcribe(audio_path, language="te")
    words = transcription.get("words", [])
    print(f"  ✓ Transcribed {len(words)} words")
    
    # Remove fillers
    print("\n[5/7] Removing filler words...")
    filler_cuts = remove_fillers(words, style)
    print(f"  ✓ Found {len(filler_cuts)} filler segments")
    
    # Detect retakes
    print("\n[6/7] Detecting retakes...")
    retake_detector = RetakeDetector()
    retake_cuts = retake_detector.detect_retakes(words, style)
    print(f"  ✓ Found {len(retake_cuts)} retake segments")
    
    # Build timeline
    print("\n[7/7] Building timeline and cutting video...")
    timeline = build_timeline(
        silence_cuts,
        filler_cuts,
        retake_cuts,
        style,
        total_duration
    )
    print(f"  ✓ Timeline: {len(timeline)} segments to keep")
    
    # Cut video
    cut_video(input_video_path, timeline, output_video_path, style)
    
    print("\n" + "=" * 60)
    print("✓ AUTO EDITING COMPLETE")
    print("=" * 60)
    print(f"Output: {output_video_path}")
    
    # Summary
    total_cut_time = sum(
        (seg["end"] - seg["start"])
        for seg in silence_cuts + filler_cuts + retake_cuts
    )
    final_duration = sum(seg["end"] - seg["start"] for seg in timeline)
    
    print(f"\nSummary:")
    print(f"  Original duration: {total_duration:.2f}s")
    print(f"  Cut duration: {total_cut_time:.2f}s")
    print(f"  Final duration: {final_duration:.2f}s")
    print(f"  Reduction: {((total_cut_time / total_duration) * 100):.1f}%")


def main():
    """Main entrypoint for auto editing."""
    # Supported video formats
    video_extensions = ["*.mp4", "*.mov", "*.avi", "*.mkv", "*.m4v", "*.flv", "*.wmv", "*.webm"]
    
    # Default paths
    input_dir = Path("/input")
    output_dir = Path("/output")
    styles_dir = Path("/styles")
    
    # Find input video (search for all supported formats)
    input_videos = []
    for ext in video_extensions:
        input_videos.extend(list(input_dir.glob(ext)))
        input_videos.extend(list(input_dir.glob(ext.upper())))  # Also check uppercase
    
    if not input_videos:
        print("ERROR: No video files found in /input/")
        print(f"Supported formats: {', '.join([ext.replace('*', '') for ext in video_extensions])}")
        print("Please place a video file in /input/")
        sys.exit(1)
    
    input_video = input_videos[0]
    print(f"Found input video: {input_video.name}")
    
    # Find style file
    style_files = list(styles_dir.glob("telugu_news_v*.json"))
    if not style_files:
        print("ERROR: No style files found in /styles/")
        print("Please run style learning first:")
        print("  docker compose run editor python learn_style.py")
        sys.exit(1)
    
    # Use latest version
    style_files.sort(key=lambda x: x.stem)
    style_file = style_files[-1]
    print(f"Using style: {style_file.name}")
    
    # Output path (always use .mp4 extension)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_video = output_dir / f"edited_{input_video.stem}.mp4"
    
    # Auto edit
    auto_edit(
        str(input_video),
        str(style_file),
        str(output_video)
    )


if __name__ == "__main__":
    main()

