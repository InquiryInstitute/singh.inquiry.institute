# Khan Academy API Issue

## Problem

The Khan Academy API endpoint `/api/v1/topictree` has been removed and returns:
```
410 Client Error: Gone
API removed. Please see https://github.com/Khan/khan-api for details
```

## Impact

- Cannot automatically discover all Khan Academy videos via API
- Need alternative methods to find video IDs

## Solutions

### Option 1: Direct YouTube Download (If You Have Video IDs)

If you have a list of YouTube video IDs, you can download transcripts directly:

```bash
# Download transcript for a specific YouTube video
python scripts/download_transcripts_only.py \
  --youtube-ids "VIDEO_ID1,VIDEO_ID2,VIDEO_ID3" \
  --max 10
```

### Option 2: Use YouTube Data API

Search for Khan Academy videos using YouTube's API:

```python
# Search for Khan Academy videos
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey=API_KEY)
request = youtube.search().list(
    q='site:khanacademy.org',
    part='id',
    type='video',
    maxResults=50
)
```

### Option 3: Web Scraping

Scrape Khan Academy's website to find video pages and extract YouTube IDs.

### Option 4: Manual Catalog

Create a catalog manually or use an existing dataset of Khan Academy video IDs.

## Current Workaround

The transcript downloader can work with YouTube IDs directly. We need to:
1. Get a list of Khan Academy YouTube video IDs (from any source)
2. Use those IDs to download transcripts via yt-dlp

## Next Steps

1. Research alternative methods to discover Khan Academy videos
2. Consider using YouTube Data API with search queries
3. Look for existing datasets/catalogs of Khan Academy videos
4. Implement web scraping as fallback
