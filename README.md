# Dockerized AI-Assisted Auto Video Editor (Telugu+English)

An automatic video editing system that learns editing style once (offline) and applies it deterministically to new videos.

## Features

- **Style Learning Mode**: Learns editing patterns from raw + edited video pairs
- **Auto Editing Mode**: Applies frozen style profile to new videos
- **Deterministic Output**: Same input + same style = same output
- **No Runtime Learning**: All learning happens offline
- **Rule-Driven**: All editing decisions based on JSON rules

## System Architecture

### Two Modes

1. **MODE 1 — STYLE LEARNING** (Offline, Rare)
   - Uses raw + edited video pairs
   - Extracts editor behavior
   - Outputs a style JSON
   - Never runs during daily editing

2. **MODE 2 — AUTO EDITING** (Daily)
   - Uses only raw video + frozen style JSON
   - No learning
   - Fast execution

## Project Structure

```
auto-editor/
├── Dockerfile
├── docker-compose.yml
├── run.py                      # Auto Editing Mode entry
├── learn_style.py              # Style Learning Mode entry
│
├── styles/
│   └── telugu_news_v1.json     # Frozen style profile
│
├── input/
│   └── raw_video.mp4
├── output/
│   └── final_video.mp4
│
├── editor/
│   ├── extract_audio.py
│   ├── silence_detector.py
│   ├── speech_to_text.py
│   ├── filler_remover.py
│   ├── retake_detector.py
│   ├── timeline_builder.py
│   └── video_cutter.py
│
├── learn_style/
│   ├── align_audio.py
│   ├── classify_removals.py
│   └── extract_rules.py
│
└── README.md
```

## Prerequisites

- Docker
- Docker Compose

## Quick Start

### 1. Setup Directory Structure

```bash
mkdir -p input/raw input/edited output styles
```

### 2. Learn Style (First Time Only)

Place your raw and edited video pairs:
- Raw videos: `input/raw/`
- Edited videos: `input/edited/`

Run style learning:

```bash
docker compose run editor python learn_style.py
```

This will generate a style JSON file in `styles/telugu_news_v1.json`.

### 3. Auto Edit Videos (Daily Use)

Place raw video in `input/` (supports `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.flv`, `.wmv`, `.webm`):

```bash
# Copy your video (any supported format)
cp your_video.mov input/
# or
cp your_video.mp4 input/
```

Run auto editing:

```bash
docker compose up
```

The edited video will be saved to `output/edited_your_video.mp4` (always `.mp4` format).

## Style JSON Format

The style JSON contains frozen editing rules:

```json
{
  "silence": {
    "min_ms": 460,
    "threshold_db": -35.0
  },
  "fillers": {
    "words": ["అంటే", "అదే", "so"],
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
```

## Constraints

- ❌ DO NOT fine-tune or train any LLM
- ❌ DO NOT allow learning during editing
- ❌ DO NOT use black-box AI decisions
- ✅ Use Whisper only as pre-trained STT
- ✅ All "learning" must produce JSON rules
- ✅ Editing must be rule-driven + deterministic
- ✅ Entire system must run via Docker Compose

## Editing Features

The system automatically:

1. **Removes long silences** based on configurable thresholds
2. **Removes filler words** (Telugu + English) when followed by pauses
3. **Detects retakes** using semantic similarity and keeps the final take
4. **Applies padding** around cuts for smooth transitions
5. **Builds timeline** by merging all cuts and resolving overlaps

## Development

### Building the Docker Image

```bash
docker compose build
```

### Running Tests

```bash
# Test style learning
docker compose run editor python learn_style.py

# Test auto editing
docker compose up
```

## Troubleshooting

### No style file found

Make sure you've run style learning first:
```bash
docker compose run editor python learn_style.py
```

### Video not found

Ensure your video is in the correct directory:
- For auto editing: `input/`
- For style learning: `input/raw/` and `input/edited/`

### FFmpeg errors

Check that your video file is a valid MP4 file and not corrupted.

## License

MIT

