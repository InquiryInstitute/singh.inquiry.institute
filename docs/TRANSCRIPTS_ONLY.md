# Transcript-Only Download Guide

This guide focuses on downloading **only transcripts** from Khan Academy videos, which is:
- **Much faster** - No large video files to download
- **Much smaller** - Transcripts are typically 10-50KB vs 50-500MB for videos
- **More efficient** - Can process thousands of transcripts quickly
- **Perfect for aFaculty** - Transcripts are what you need for teaching personas

## Quick Start

### Local Download

```bash
# Discover all videos and download their transcripts
python scripts/download_transcripts_only.py --discover-first --max 10

# Or use existing catalog
python scripts/download_transcripts_only.py --catalog data/metadata/khan_academy_catalog.json --max 100
```

### Download to Google Cloud Storage

```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# Download transcripts directly to GCS
python scripts/download_transcripts_only.py \
  --gcs-bucket khan-academy-videos \
  --discover-first \
  --max 100
```

## How It Works

The transcript-only downloader:

1. **Uses yt-dlp with `skip_download=True`** - Downloads only subtitles, not video files
2. **Extracts WebVTT files** - Gets transcripts in WebVTT format from YouTube
3. **Processes transcripts** - Converts to structured JSON and plain text
4. **Uploads to GCS** - Stores transcripts in cloud storage
5. **Cleans up locally** - Deletes local files after successful upload

## Storage Requirements

### Transcript Sizes
- **Raw VTT file**: ~10-50KB per video
- **Processed JSON**: ~20-100KB per video
- **Plain text**: ~5-30KB per video

### Example Storage
- **1,000 videos**: ~50-100MB (vs 50-500GB for videos!)
- **10,000 videos**: ~500MB-1GB (vs 500GB-5TB for videos!)
- **All Khan Academy**: ~5-10GB estimated (vs 5-50TB for videos!)

## Cloud Deployment (Transcript-Only)

### Deploy to Cloud Run

```bash
# Build lighter image (no ffmpeg needed)
gcloud builds submit -f Dockerfile.transcripts \
  --tag gcr.io/$PROJECT_ID/khan-academy-transcripts:latest .

# Deploy with lower resource requirements
gcloud run deploy khan-academy-transcripts \
  --image gcr.io/$PROJECT_ID/khan-academy-transcripts:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 20 \
  --set-env-vars GCS_BUCKET=khan-academy-videos
```

### Trigger Transcript Download

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe khan-academy-transcripts \
  --region=us-central1 --format='value(status.url)')

# Trigger transcript download
curl -X POST "$SERVICE_URL/run" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "transcripts_only",
    "max_videos": 1000,
    "gcs_bucket": "khan-academy-videos"
  }'
```

### Schedule Daily Transcript Updates

```bash
# Create scheduled job for transcripts
gcloud scheduler jobs create http khan-transcripts-daily \
  --location=us-central1 \
  --schedule="0 2 * * *" \
  --time-zone="America/Los_Angeles" \
  --uri="$SERVICE_URL/run" \
  --http-method=POST \
  --message-body='{"command":"transcripts_only","max_videos":1000}' \
  --oidc-service-account-email=SERVICE_ACCOUNT_EMAIL
```

## GCS Bucket Structure (Transcripts)

```
gs://khan-academy-videos/
├── transcripts/
│   ├── {video_id_1}.vtt          # Raw WebVTT files
│   ├── {video_id_2}.vtt
│   └── processed/
│       ├── {video_id_1}_transcript.json
│       ├── {video_id_1}_transcript.txt
│       └── ...
└── metadata/
    ├── khan_academy_catalog.json
    └── transcript_download_results.json
```

## Processing Transcripts

After downloading, transcripts are automatically processed into:

1. **Structured JSON** - With timestamps, segments, word counts
2. **Plain text** - Full transcript text for easy reading/searching

You can also process existing transcripts:

```bash
# Process transcripts from GCS
python -m src.process.process_transcripts \
  --input gs://bucket/transcripts \
  --output gs://bucket/transcripts/processed \
  --gcs-bucket bucket-name
```

## Cost Comparison

### Transcript-Only Download
- **Storage**: ~$0.10-1.00/month for 10,000 transcripts (vs $100-1000 for videos)
- **Network**: Minimal (small files)
- **Compute**: Lower (no video processing)
- **Time**: Minutes to hours (vs days/weeks for videos)

### Example Costs (10,000 videos)
- **Transcripts**: ~$0.50/month storage
- **Videos**: ~$500-5000/month storage

## Workflow Recommendations

### Phase 1: Transcripts First (Recommended)
1. Download all transcripts first
2. Process and analyze content
3. Map to aFaculty personas
4. Download videos only for selected courses later

### Phase 2: Selective Video Download
1. Use transcript analysis to identify key videos
2. Download videos only for courses assigned to aFaculty
3. Much more efficient than downloading everything

## Script Options

```bash
python scripts/download_transcripts_only.py [OPTIONS]

Options:
  --catalog PATH          Catalog JSON file (local or gs:// path)
  --gcs-bucket NAME      GCS bucket name (enables cloud upload)
  --gcs-credentials PATH Path to GCS credentials JSON
  --output-dir PATH      Local output directory
  --max N                Maximum number of transcripts
  --discover-first       Discover all videos first, then download transcripts
```

## Troubleshooting

### No Transcripts Found
Some videos may not have transcripts. The script will:
- Try auto-generated subtitles if manual don't exist
- Log warnings for videos without transcripts
- Continue with next video

### Rate Limiting
YouTube may rate limit requests. The script includes:
- 0.5 second delay between requests
- Error handling and retries
- Progress tracking

### GCS Upload Failures
- Check bucket permissions
- Verify service account has Storage Admin role
- Check network connectivity

## Next Steps

After downloading transcripts:

1. **Analyze content** - Use transcripts to understand course structure
2. **Map to aFaculty** - Assign courses to teaching personas
3. **Prepare for LoRA** - Structure transcripts for fine-tuning
4. **Selective video download** - Download videos only for key courses

## Benefits of Transcript-First Approach

✅ **Fast iteration** - Test ideas quickly with transcripts
✅ **Lower costs** - Minimal storage and compute
✅ **Better planning** - Understand content before downloading videos
✅ **Easier analysis** - Text is easier to search and analyze
✅ **aFaculty ready** - Transcripts are what you need for teaching
