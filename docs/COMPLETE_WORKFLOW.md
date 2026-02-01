# Complete Workflow: Khan Academy → Kolibri → S3 → Matrix Chat

## Overview

This document describes the complete workflow for getting Khan Academy content into the Matrix Chat for dialogic delivery by a.Faculty.

## Workflow Steps

### 1. Setup Kolibri

```bash
# Install Kolibri (if not already installed)
pip install kolibri

# Start Kolibri server
kolibri start

# Import Khan Academy channel in Kolibri web interface
# Navigate to http://localhost:8080 and import Khan Academy content
```

### 2. Find Kolibri URL

```bash
# Auto-detect
bash scripts/find-kolibri-url.sh

# Or test manually
python scripts/kolibri-quick-test.py --kolibri-url http://localhost:8080
```

### 3. Discover Content

```bash
# Discover all available Khan Academy content
python scripts/kolibri-discover-content.py --kolibri-url http://your-url:port

# This creates: data/metadata/kolibri_khan_academy_catalog.json
```

### 4. Download Transcripts

```bash
# Download and process transcripts (all-in-one)
python scripts/kolibri-workflow.py --kolibri-url http://your-url:port --max-videos 10

# Or step by step:
# List available videos
python scripts/kolibri-list-videos.py --kolibri-url http://your-url:port

# Download transcripts
python scripts/kolibri-download-transcripts.py --kolibri-url http://your-url:port --max 10
```

### 5. Upload to S3 (Optional)

```bash
# Upload all courses to S3
python scripts/upload-to-s3.py --bucket singh-courses

# Upload single course
python scripts/upload-to-s3.py --course data/metadata/sample_ka_class.json

# Update manifest
python scripts/upload-to-s3.py --update-manifest
```

### 6. Use in Matrix Chat

1. Open `http://localhost:4321/matrix-chat` (or deployed site)
2. Select course from dropdown
3. Select a.Faculty persona
4. Click "Start Delivery"
5. Content is delivered dialogically with interruptible Q&A

## Current Status

### ✅ Ready to Use

- **Kolibri Integration**: Complete API client and scripts
- **Transcript Processing**: VTT → Dialogic format converter
- **Matrix Chat**: Full dialogic delivery interface
- **S3 Storage**: Design and upload scripts ready
- **Real Transcript**: One Khan Academy transcript downloaded and processed

### 📋 Next Steps

1. **Connect to Kolibri**: Find your Kolibri URL and test connection
2. **Discover Content**: Run discovery to see available courses
3. **Download Transcripts**: Download transcripts for courses you want
4. **Upload to S3**: Upload to S3 for scalable storage (optional)
5. **Test Delivery**: Use Matrix Chat to test dialogic delivery

## File Locations

### Local Files
- **Transcripts**: `data/transcripts/processed/*_dialogic_transcript.json`
- **Metadata**: `data/metadata/*.json`
- **Raw VTT**: `data/transcripts/raw/*.vtt`

### S3 Structure (when uploaded)
```
s3://singh-courses/
├── manifest.json
├── sources/
│   └── khan-academy/
│       ├── manifest.json
│       └── courses/
│           └── {course_id}/
│               ├── metadata.json
│               └── videos/
│                   └── {video_id}/
│                       └── transcript_dialogic.json
```

## Quick Commands

```bash
# Find Kolibri
bash scripts/find-kolibri-url.sh

# Test connection
python scripts/kolibri-quick-test.py --kolibri-url http://localhost:8080

# Complete workflow (discover + download + process)
python scripts/kolibri-workflow.py --kolibri-url http://localhost:8080 --max-videos 10

# Upload to S3
python scripts/upload-to-s3.py
```

## Troubleshooting

### Kolibri Not Found
- Check if running: `kolibri status`
- Check port: `cat ~/.kolibri/server/port`
- See: `docs/FIND_KOLIBRI_URL.md`

### No Transcripts
- Some videos may not have transcripts
- Check Kolibri for transcript availability
- Script will skip videos without transcripts

### S3 Upload Fails
- Check AWS credentials: `aws configure`
- Verify bucket exists: `aws s3 ls s3://singh-courses`
- Check permissions

## Integration Points

1. **Kolibri** → Downloads Khan Academy content
2. **Transcript Processor** → Converts to dialogic format
3. **S3** → Stores for scalable access
4. **Matrix Chat** → Delivers via a.Faculty personas
5. **Dialogic Library** → Handles interruptible delivery
