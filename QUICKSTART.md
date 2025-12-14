# Quick Start Guide

## Initial Setup

1. **Create directory structure:**
```bash
mkdir -p input/raw input/edited output styles
```

## Learning Style (First Time Only)

1. **Place your video pairs:**
   - Raw video: `input/raw/your_video.mov` (or `.mp4`, `.avi`, `.mkv`, etc.)
   - Edited video: `input/edited/your_video.mov` (or matching name, any supported format)

2. **Run style learning:**
```bash
docker compose run editor python learn_style.py
```

3. **Check output:**
   - Style JSON will be saved to `styles/telugu_news_v1.json` (or v2, v3, etc.)

## Auto Editing (Daily Use)

1. **Place raw video (supports `.mov`, `.mp4`, `.avi`, `.mkv`, `.m4v`, `.flv`, `.wmv`, `.webm`):**
```bash
cp your_new_video.mov input/
# or any other supported format
```

2. **Run auto editing:**
```bash
docker compose up
```

3. **Get edited video:**
   - Output will be in `output/edited_your_new_video.mp4` (always `.mp4` format)

## Troubleshooting

### "No style file found"
Run style learning first (see above).

### "No video files found"
- For auto editing: Place video in `input/`
- For style learning: Place videos in `input/raw/` and `input/edited/`

### Docker build fails
Make sure you have Docker and Docker Compose installed and running.

