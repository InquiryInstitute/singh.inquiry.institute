# Kolibri Integration for Khan Academy Content

## Overview

Kolibri is an offline learning platform that can download and mirror Khan Academy content. This is the recommended approach since the Khan Academy API has been removed.

## What is Kolibri?

Kolibri is an open-source learning platform that:
- Downloads educational content from Khan Academy and other sources
- Works offline
- Provides a local content server
- Has APIs for accessing content and metadata
- Can export content in various formats

## Setup Kolibri

### Installation

```bash
# Install Kolibri
pip install kolibri

# Or use Docker
docker run -d -p 8080:8080 learningequality/kolibri
```

### Initial Setup

1. **Start Kolibri server:**
   ```bash
   kolibri start
   ```

2. **Access Kolibri interface:**
   - Open browser to `http://localhost:8080`
   - Complete initial setup
   - Import Khan Academy channel

3. **Download Khan Academy content:**
   - Navigate to Channels
   - Select Khan Academy channel
   - Choose topics/courses to download
   - Start download

## Kolibri API Access

Kolibri provides a REST API for accessing content:

### Base URL
```
http://localhost:8080/api
```

### Key Endpoints

1. **List Channels:**
   ```
   GET /api/content/channel
   ```

2. **Get Channel Content:**
   ```
   GET /api/content/contentnode?channel_id={channel_id}
   ```

3. **Get Content Details:**
   ```
   GET /api/content/contentnode/{content_id}
   ```

4. **Get File URLs:**
   ```
   GET /api/content/file?contentnode_id={content_id}
   ```

5. **Get Transcripts:**
   ```
   GET /api/content/contentnode/{content_id}/transcript
   ```

## Integration with Singh

### Option 1: Use Kolibri as Content Source

1. **Query Kolibri API for available content**
2. **Download transcripts via Kolibri API**
3. **Process transcripts to dialogic format**
4. **Store in S3 or local filesystem**

### Option 2: Export from Kolibri

1. **Use Kolibri export features**
2. **Extract transcripts and metadata**
3. **Process and store in our format**

### Option 3: Direct Kolibri Integration

1. **Point Matrix Chat to Kolibri API**
2. **Load content on-demand from Kolibri**
3. **Process transcripts in real-time**

## Implementation Plan

### Phase 1: Kolibri Setup
- [ ] Install and configure Kolibri
- [ ] Download Khan Academy channel
- [ ] Test API access
- [ ] Document available content

### Phase 2: Content Discovery
- [ ] Create Kolibri API client
- [ ] List available Khan Academy courses
- [ ] Map to our course structure
- [ ] Generate course metadata

### Phase 3: Transcript Extraction
- [ ] Extract transcripts from Kolibri
- [ ] Convert to dialogic format
- [ ] Store in S3 or local filesystem
- [ ] Update course metadata

### Phase 4: Integration
- [ ] Update Matrix Chat to use Kolibri content
- [ ] Add Kolibri as content source option
- [ ] Implement on-demand loading
- [ ] Add caching layer

## Kolibri API Client

```python
import requests

class KolibriClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
    
    def get_channels(self):
        """Get list of available channels."""
        response = requests.get(f"{self.api_url}/content/channel")
        return response.json()
    
    def get_content_nodes(self, channel_id, kind="video"):
        """Get content nodes for a channel."""
        params = {
            "channel_id": channel_id,
            "kind": kind
        }
        response = requests.get(f"{self.api_url}/content/contentnode", params=params)
        return response.json()
    
    def get_transcript(self, content_id):
        """Get transcript for a content node."""
        response = requests.get(f"{self.api_url}/content/contentnode/{content_id}/transcript")
        return response.json()
```

## Advantages of Kolibri

1. **Reliable Content Source**: Kolibri maintains Khan Academy content
2. **Offline Access**: Content is stored locally
3. **Structured Data**: Well-organized content hierarchy
4. **API Access**: RESTful API for programmatic access
5. **Transcripts Available**: Many videos have transcripts
6. **Metadata Rich**: Includes titles, descriptions, topics, etc.

## Next Steps

1. Install Kolibri
2. Download Khan Academy channel
3. Explore available content via API
4. Create integration scripts
5. Test transcript extraction
6. Integrate with Matrix Chat
