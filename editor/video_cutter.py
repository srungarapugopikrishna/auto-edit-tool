"""
Video cutting module.
Cuts video based on timeline using FFmpeg.
"""

import subprocess
from pathlib import Path
from typing import List, Dict


def cut_video(
    input_video_path: str,
    timeline: List[Dict[str, float]],
    output_video_path: str,
    style: Dict
):
    """
    Cut video based on timeline segments.
    
    Args:
        input_video_path: Path to input video
        timeline: List of segments to keep: [{"start": 0.0, "end": 1.8}, ...]
        output_video_path: Path to output video
        style: Style JSON dictionary (for crossfade settings)
    """
    input_path = Path(input_video_path)
    output_path = Path(output_video_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input video not found: {input_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cuts_config = style.get("cuts", {})
    crossfade_ms = cuts_config.get("crossfade_ms", 80)
    
    # Create FFmpeg filter complex for cutting
    if len(timeline) == 0:
        raise ValueError("Timeline is empty - no segments to keep")
    
    # Use filter_complex method for precise cutting
    _cut_with_filters(input_video_path, timeline, output_video_path)


def _cut_with_filters(
    input_video_path: str,
    timeline: List[Dict[str, float]],
    output_video_path: str
):
    """Cut video using filter_complex."""
    if len(timeline) == 0:
        raise ValueError("Timeline is empty")
    
    # Build filter complex
    filter_parts = []
    
    for i, segment in enumerate(timeline):
        start = segment["start"]
        duration = segment["end"] - segment["start"]
        
        # Create trim filters for video and audio
        filter_parts.append(
            f"[0:v]trim=start={start}:duration={duration},setpts=PTS-STARTPTS[v{i}]"
        )
        filter_parts.append(
            f"[0:a]atrim=start={start}:duration={duration},asetpts=PTS-STARTPTS[a{i}]"
        )
    
    # Concatenate all segments
    concat_inputs = "".join([f"[v{i}][a{i}]" for i in range(len(timeline))])
    concat_filter = f"{concat_inputs}concat=n={len(timeline)}:v=1:a=1[outv][outa]"
    filter_parts.append(concat_filter)
    
    filter_complex = ";".join(filter_parts)
    
    cmd = [
        "ffmpeg",
        "-i", input_video_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-profile:v", "high",
        "-level", "4.0",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-y",
        str(output_video_path)
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Video cutting failed: {result.stderr}")
    
    if not Path(output_video_path).exists():
        raise RuntimeError(f"Output video was not created: {output_video_path}")
    
    print(f"✓ Video cut successfully: {output_video_path}")

