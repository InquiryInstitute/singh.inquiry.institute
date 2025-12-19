# Transcript Collection Status

## Current Status: ❌ No Transcripts Downloaded Yet

**Last Updated**: 2025-12-16

## What We Have

✅ **Infrastructure Ready**:
- Transcript download script: `scripts/download_transcripts_only.py`
- Transcript processor: `src/process/process_transcripts.py`
- Khan Academy API client: `src/api/khan_academy_api.py`
- GCS storage integration: `src/storage/gcs_storage.py`
- Documentation: `QUICKSTART_TRANSCRIPTS.md`, `docs/TRANSCRIPTS_ONLY.md`

❌ **Missing**:
- No video catalog (`data/metadata/khan_academy_catalog.json`)
- No transcripts downloaded
- No processed transcripts

## Next Steps to Get Transcripts

### Option 1: Quick Test (10 videos)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Discover and download 10 transcripts (test)
python scripts/download_transcripts_only.py \
  --discover-first \
  --max 10
```

This will:
- Discover all Khan Academy videos (creates catalog)
- Download transcripts for first 10 videos
- Save to `data/transcripts/`

### Option 2: Download to Google Cloud Storage

```bash
# 1. Set up GCS credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# 2. Download transcripts to GCS
python scripts/download_transcripts_only.py \
  --gcs-bucket YOUR_BUCKET_NAME \
  --discover-first \
  --max 100  # Start with 100
```

### Option 3: Full Catalog First, Then Selective Download

```bash
# Step 1: Create catalog only (no downloads)
python scripts/discover_all_content.py

# Step 2: Review catalog
cat data/metadata/khan_academy_catalog.json | jq '. | length'
# Shows total number of videos

# Step 3: Download transcripts selectively
python scripts/download_transcripts_only.py \
  --catalog data/metadata/khan_academy_catalog.json \
  --max 1000
```

## Expected Results

After running the download script, you should have:

```
data/
├── metadata/
│   └── khan_academy_catalog.json  # Full catalog of all videos
├── transcripts/
│   ├── raw/                       # Raw .vtt files
│   │   └── VIDEO_ID.vtt
│   └── processed/                 # Processed transcripts
│       ├── VIDEO_ID_transcript.json
│       └── VIDEO_ID_transcript.txt
```

## Storage Estimates

### Transcript Sizes
- **Per video**: ~10-50KB (raw) + ~20-100KB (processed) = ~30-150KB total
- **1,000 videos**: ~30-150MB
- **10,000 videos**: ~300MB-1.5GB
- **All Khan Academy** (estimated 10,000-20,000 videos): ~500MB-3GB

### Comparison to Videos
- Videos: ~50-500MB each = 500GB-10TB for full collection
- Transcripts: ~100KB each = ~1-3GB for full collection
- **Transcripts are ~1000x smaller!**

## Verification Commands

```bash
# Check if catalog exists
ls -lh data/metadata/khan_academy_catalog.json

# Count videos in catalog
python3 -c "import json; print(len(json.load(open('data/metadata/khan_academy_catalog.json'))))"

# Count downloaded transcripts
find data/transcripts -name "*.vtt" | wc -l
find data/transcripts/processed -name "*.json" | wc -l

# Check GCS (if using cloud storage)
gsutil ls gs://YOUR_BUCKET/transcripts/ | wc -l
```

## Current Data Status

```
data/
├── metadata/
│   └── .gitkeep  ✅ (directory exists, but no catalog yet)
├── transcripts/  ❌ (doesn't exist yet)
├── videos/       ❌ (doesn't exist yet)
└── exercises/    ❌ (doesn't exist yet)
```

## Recommendations

1. **Start Small**: Download 10-100 transcripts first to test
2. **Use GCS**: For large-scale downloads, use Google Cloud Storage
3. **Create Catalog First**: Run `discover_all_content.py` to see total video count
4. **Process in Batches**: Download in batches of 1000 to avoid timeouts
5. **Monitor Progress**: Use `--max` flag to limit downloads during testing

## Related Documentation

- [Quick Start Guide](./QUICKSTART_TRANSCRIPTS.md)
- [Detailed Transcript Guide](./docs/TRANSCRIPTS_ONLY.md)
- [Khan Academy API Docs](./docs/KHAN_ACADEMY_API.md)
- [GCS Setup](./docs/GCS_SETUP.md)
