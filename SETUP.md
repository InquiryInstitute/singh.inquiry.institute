# Setup Guide

## Initial Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install ffmpeg (optional, for video processing):**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

## Quick Start: Collect All Khan Academy Content

### Step 0: Setup Google Cloud Storage (Recommended)

For large-scale downloads, storing videos in GCS is recommended:

1. Create a GCS bucket (see [GCS Setup Guide](./docs/GCS_SETUP.md))
2. Set credentials: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"`

### Step 1: Discover All Videos

This creates a comprehensive catalog of all Khan Academy videos:

```bash
python scripts/discover_all_content.py
```

This will:
- Connect to Khan Academy's API
- Discover all topics and courses
- Catalog all videos with metadata
- Save to `data/metadata/khan_academy_catalog.json`

**Time estimate:** 30-60 minutes (depending on rate limiting)

### Step 2: Download Videos and Transcripts

Once you have the catalog, download all videos and transcripts:

```bash
# Download to Google Cloud Storage (recommended)
python scripts/download_all.py --gcs-bucket your-bucket-name --max 10

# Or download to local storage
python scripts/download_all.py --max 10

# Download everything (this will take a LONG time)
python scripts/download_all.py --gcs-bucket your-bucket-name
```

**Note:** Full download will:
- Take many hours/days
- Require hundreds of GB of storage (GCS recommended)
- Download thousands of videos
- Automatically upload to GCS and delete local files (unless `--keep-local` is used)

### Step 3: Process Transcripts

Transcripts are automatically processed during download, but you can reprocess them:

```bash
python -m src.process.process_transcripts --input data/videos --output data/transcripts
```

## Data Storage

- **Videos:** Stored in `data/videos/` (large files, gitignored)
- **Transcripts:** Processed transcripts in `data/transcripts/` (JSON and TXT formats)
- **Metadata:** Catalogs and indexes in `data/metadata/`

## Next Steps

After collecting all videos and transcripts:

1. **Map to aFaculty personas** - Assign courses to specific teaching assistants
2. **Prepare for LoRA training** - Structure data for fine-tuning workflows
3. **Integrate with Inquiry Institute** - Connect to existing tooling

See [TODO.md](./TODO.md) for detailed project objectives.
