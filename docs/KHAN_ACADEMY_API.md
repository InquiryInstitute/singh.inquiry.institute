# Khan Academy API Documentation

## Overview

Khan Academy doesn't provide a public API, but we can access their content through:

1. **Internal API endpoints** - Reverse-engineered from their website
2. **YouTube** - Khan Academy hosts all videos on YouTube
3. **Web scraping** - For content discovery and metadata

## API Endpoints

### Base URLs
- Website: `https://www.khanacademy.org`
- API Base: `https://www.khanacademy.org/api/v1`

### Key Endpoints

#### Get Topic Tree
```
GET /api/v1/topictree?kind=Topic
```
Returns the complete topic tree structure with all subjects and courses.

#### Get Topic Content
```
GET /api/v1/topic/{topic_slug}
```
Returns all content (videos, exercises, articles) for a specific topic.

#### Get Video Information
```
GET /api/v1/video/{video_slug}
```
Returns detailed information about a specific video, including:
- YouTube ID
- Title and description
- Duration
- Transcript URL
- Related content

## Video Access

All Khan Academy videos are hosted on YouTube. The video metadata includes a `youtube_id` field that can be used to construct YouTube URLs:

```
https://www.youtube.com/watch?v={youtube_id}
```

## Transcripts

Transcripts are available in multiple formats:
1. **WebVTT** - Subtitle files (.vtt) available via YouTube
2. **API** - Some videos have transcript data in the API response
3. **Auto-generated** - YouTube provides auto-generated transcripts for all videos

## Rate Limiting

Khan Academy's servers may rate limit requests. Best practices:
- Add delays between requests (0.5-1 second recommended)
- Use session cookies for authenticated requests if needed
- Cache responses to avoid redundant requests

## Data Structure

### Video Object
```json
{
  "id": "video_slug",
  "youtube_id": "youtube_video_id",
  "title": "Video Title",
  "description": "Video description",
  "duration": 600,
  "transcript_url": "https://...",
  "topic": {
    "id": "topic_id",
    "title": "Topic Title",
    "slug": "topic-slug"
  }
}
```

### Topic Object
```json
{
  "id": "topic_id",
  "title": "Topic Title",
  "slug": "topic-slug",
  "kind": "Topic",
  "children": [
    {
      "kind": "Video",
      "id": "video_id",
      ...
    }
  ]
}
```

## Implementation Notes

1. **Content Discovery**: Start with the topictree endpoint and recursively traverse all children to discover all videos.

2. **Video Download**: Use `yt-dlp` (or `youtube-dl`) to download videos and transcripts from YouTube using the `youtube_id`.

3. **Transcript Processing**: WebVTT files need to be parsed and converted to structured formats (JSON, plain text) for use with aFaculty personas.

4. **Caching**: Cache API responses and downloaded content to avoid redundant requests and downloads.

## Tools and Libraries

- **yt-dlp**: Modern YouTube downloader (successor to youtube-dl)
- **requests**: HTTP client for API calls
- **webvtt-py**: WebVTT subtitle parser
- **beautifulsoup4**: HTML parsing if web scraping is needed

## Example Usage

See the implementation in:
- `src/api/khan_academy_api.py` - API client
- `src/download/download_videos.py` - Video downloader
- `src/process/process_transcripts.py` - Transcript processor
- `scripts/discover_all_content.py` - Discovery script
- `scripts/download_all.py` - Download script
