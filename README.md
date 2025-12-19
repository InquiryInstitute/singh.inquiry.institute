# singh.inquiry.institute

Repository for Singh Inquiry Institute project - Khan Academy content collection and aFaculty integration.

## Overview

This repository contains tools and infrastructure for:
- **Collecting all Khan Academy videos and transcripts** - Comprehensive cataloging and download pipeline
- **Mapping content to aFaculty personas** - Connecting Khan Academy courses to teaching assistants
- **Preparing LoRA fine-tuning workflows** - Adapting aFaculty personas to teach Khan Academy content
- **Integrating with Inquiry Institute tooling** - Enabling aFaculty to guide learners through course content

## Project Structure

```
singh.inquiry.institute/
├── data/                    # Collected data (gitignored)
│   ├── videos/             # Downloaded video files
│   ├── transcripts/        # Processed transcripts
│   ├── metadata/           # Catalogs and metadata
│   └── exercises/          # Exercise data
├── src/                    # Source code
│   ├── api/               # Khan Academy API client
│   ├── download/          # Video download utilities
│   └── process/           # Data processing scripts
├── scripts/               # Main execution scripts
├── docs/                  # Documentation
└── .github/              # GitHub workflows (Pages deployment)
```

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Or use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1a. Setup Google Cloud Storage (Optional but Recommended)

For storing videos in GCS instead of locally:

1. Create a GCS bucket
2. Create a service account and download credentials JSON
3. Set environment variable: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"`

See [GCS Setup Guide](./docs/GCS_SETUP.md) for detailed instructions.

### 2. Discover All Khan Academy Content

```bash
# Discover all videos and create catalog
python scripts/discover_all_content.py

# This creates: data/metadata/khan_academy_catalog.json
```

### 3. Download Transcripts (Recommended First Step)

**Start with transcripts only** - Much faster and smaller:

```bash
# Discover and download transcripts to GCS
python scripts/download_transcripts_only.py \
  --gcs-bucket your-bucket-name \
  --discover-first \
  --max 100  # Test with 100 first

# Or use existing catalog
python scripts/download_transcripts_only.py \
  --gcs-bucket your-bucket-name \
  --catalog data/metadata/khan_academy_catalog.json
```

### 4. Download Videos (Optional, Later)

After analyzing transcripts, download videos selectively:

```bash
# Download to local storage
python scripts/download_all.py

# Download directly to Google Cloud Storage
python scripts/download_all.py --gcs-bucket your-bucket-name

# Or download a limited number for testing
python scripts/download_all.py --gcs-bucket your-bucket-name --max 10

# Download only transcripts (skip video files)
python scripts/download_all.py --skip-video

# Keep local files after GCS upload (default: delete after upload)
python scripts/download_all.py --gcs-bucket your-bucket-name --keep-local
```

### 4. Process Transcripts

```bash
# Process downloaded transcripts into structured formats
python scripts/download_all.py --skip-video  # Process existing transcripts
```

## Usage

### Discovery Script

```bash
python scripts/discover_all_content.py [OPTIONS]

Options:
  --output PATH     Output path for catalog (default: data/metadata/khan_academy_catalog.json)
  --rate-limit SEC Delay between API requests (default: 0.5)
```

### Download Script

```bash
python scripts/download_all.py [OPTIONS]

Options:
  --catalog PATH      Path to video catalog JSON
  --video-dir PATH    Directory to save videos
  --transcript-dir PATH  Directory to save processed transcripts
  --max N             Maximum number of videos to download
  --skip-video        Skip video download, only get transcripts
  --skip-transcript   Skip transcript processing
```

## Data Pipeline

1. **Discovery** → Catalog all Khan Academy videos
2. **Download** → Download videos and transcripts from YouTube
3. **Processing** → Convert transcripts to structured formats (JSON, plain text)
4. **Integration** → Map content to aFaculty personas and prepare for LoRA training

## Documentation

- [Khan Academy API Documentation](./docs/KHAN_ACADEMY_API.md) - API endpoints and data structures
- [Google Cloud Storage Setup](./docs/GCS_SETUP.md) - GCS bucket configuration and usage
- [AWS Route 53 Setup](./AWS_ROUTE53_SETUP.md) - DNS configuration for custom domain
- [Repository Setup](./REPOSITORY_SETUP.md) - GitHub repository configuration

## GitHub Pages

The site is configured to deploy automatically via GitHub Actions. See:
- `.github/workflows/pages.yml` - Deployment workflow
- Custom domain: `singh.inquiry.institute`

## Requirements

- Python 3.8+
- ffmpeg (for video processing, optional)
- Sufficient disk space for video storage (videos are large!)

## Next Steps

See [TODO.md](./TODO.md) for project objectives and near-term tasks.

---

Project scaffold initialized on 2025-11-09.
