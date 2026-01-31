# Kolibri Integration Guide

## Quick Start

### 1. Find Your Kolibri Server

```bash
# Try to auto-detect
python scripts/kolibri-find-server.py

# Or specify URL manually
python scripts/kolibri-discover-content.py --kolibri-url http://your-kolibri-url:port
```

### 2. List Available Videos

```bash
# List first 20 videos
python scripts/kolibri-list-videos.py

# Search for specific content
python scripts/kolibri-list-videos.py --search "algebra" --limit 10

# Use custom Kolibri URL
python scripts/kolibri-list-videos.py --kolibri-url http://localhost:8080
```

### 3. Discover All Content

```bash
# Discover all Khan Academy content and save metadata
python scripts/kolibri-discover-content.py --output-dir data/metadata

# Use custom URL
python scripts/kolibri-discover-content.py --kolibri-url http://your-url:port
```

### 4. Download Transcripts

```bash
# Download transcripts for first 10 videos
python scripts/kolibri-download-transcripts.py --max 10

# Download transcripts for algebra videos
python scripts/kolibri-download-transcripts.py --subject "algebra" --max 50

# Use custom URL
python scripts/kolibri-download-transcripts.py --kolibri-url http://your-url:port
```

## Kolibri API Client Usage

```python
from src.api.kolibri_client import KolibriClient

# Initialize client
client = KolibriClient("http://localhost:8080")

# Test connection
if client.test_connection():
    # Get channels
    channels = client.get_channels()
    
    # Get Khan Academy channel
    ka_channel = client.get_khan_academy_channel()
    
    # Get videos
    videos = client.get_content_nodes(ka_channel['id'], kind='video')
    
    # Get transcript for a video
    transcript = client.get_transcript(video_id)
```

## Workflow

1. **Discover Content:**
   ```bash
   python scripts/kolibri-discover-content.py
   ```
   This creates `data/metadata/kolibri_khan_academy_catalog.json`

2. **Review Available Content:**
   ```bash
   python scripts/kolibri-list-videos.py --limit 50
   ```

3. **Download Transcripts:**
   ```bash
   python scripts/kolibri-download-transcripts.py --max 100
   ```

4. **Process Transcripts:**
   Transcripts are automatically converted to dialogic format and saved to:
   - `data/transcripts/raw/` - Raw VTT files
   - `data/transcripts/processed/` - Dialogic format JSON

5. **Use in Matrix Chat:**
   The processed transcripts are automatically available in the Matrix Chat interface.

## Troubleshooting

### Kolibri Not Found

If `kolibri-find-server.py` can't find your server:

1. Check if Kolibri is running:
   ```bash
   kolibri status
   ```

2. Check what port it's on:
   ```bash
   kolibri manage showconfig
   ```

3. Use the correct URL:
   ```bash
   python scripts/kolibri-discover-content.py --kolibri-url http://your-actual-url:port
   ```

### No Khan Academy Channel

If Khan Academy channel isn't found:

1. Make sure you've imported the Khan Academy channel in Kolibri
2. Check available channels:
   ```python
   from src.api.kolibri_client import KolibriClient
   client = KolibriClient("http://your-url:port")
   channels = client.get_channels()
   for ch in channels:
       print(f"{ch.get('name')} - {ch.get('id')}")
   ```

3. You can manually specify a channel ID in the scripts if needed

### No Transcripts Available

Some videos may not have transcripts. The script will skip these and continue.

## Integration with S3

Once transcripts are downloaded, you can upload them to S3:

```bash
# Upload to S3 (future script)
python scripts/upload-to-s3.py --source data/transcripts/processed
```

## Next Steps

1. Run discovery to see what content is available
2. Download transcripts for courses you want to use
3. Process and convert to dialogic format
4. Upload to S3 for the course storage system
5. Use in Matrix Chat for dialogic delivery
