# Quick Start: Download Transcripts Only

Get started quickly by downloading only transcripts (no videos needed).

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up Google Cloud (Optional but Recommended)

```bash
# Create GCS bucket
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://khan-academy-videos

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

## 3. Download Transcripts

```bash
# Discover all videos and download their transcripts
python scripts/download_transcripts_only.py \
  --gcs-bucket khan-academy-videos \
  --discover-first \
  --max 10  # Start with 10 to test
```

## 4. Check Results

```bash
# List downloaded transcripts in GCS
gsutil ls gs://khan-academy-videos/transcripts/

# Download a processed transcript to view
gsutil cp gs://khan-academy-videos/transcripts/processed/VIDEO_ID_transcript.txt ./
```

## What You Get

- **Raw transcripts** (.vtt files) in `transcripts/`
- **Processed JSON** with timestamps in `transcripts/processed/`
- **Plain text** transcripts in `transcripts/processed/`
- **Catalog** of all videos in `metadata/`

## Next Steps

1. Analyze transcripts to understand content
2. Map courses to aFaculty personas
3. Download videos selectively for key courses

See [TRANSCRIPTS_ONLY.md](./docs/TRANSCRIPTS_ONLY.md) for detailed documentation.
