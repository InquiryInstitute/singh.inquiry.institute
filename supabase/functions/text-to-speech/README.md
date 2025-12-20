# Text-to-Speech Edge Function

Supabase Edge Function that generates audio using ElevenLabs API based on faculty voice prompts.

## Setup

### 1. Set ElevenLabs API Key in Supabase

```bash
# Using Supabase CLI
supabase secrets set ELEVENLABS_API_KEY=sk_ca784069ef0a2893180b5e730db281ad04313dff403a0a8d

# Or via Supabase Dashboard:
# Project Settings → Edge Functions → Secrets → Add Secret
# Name: ELEVENLABS_API_KEY
# Value: sk_ca784069ef0a2893180b5e730db281ad04313dff403a0a8d
```

### 2. Deploy Function

```bash
supabase functions deploy text-to-speech
```

## Usage

### Request

```javascript
const response = await fetch('https://YOUR_PROJECT.supabase.co/functions/v1/text-to-speech', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    faculty_name: 'Mary Shelley',  // or 'shelley', 'a.shelley', etc.
    text: 'Welcome to this lecture on algebra...'
  })
})

const data = await response.json()
// data.audio_base64 contains base64-encoded MP3
```

### Response

```json
{
  "success": true,
  "faculty_id": "a.shelley",
  "faculty_name": "Mary Shelley",
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "audio_base64": "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwM...",
  "audio_format": "audio/mpeg"
}
```

## How It Works

1. Receives `faculty_name` and `text` in request body
2. Queries Supabase `faculty` table to find matching faculty
3. Retrieves `elevenlabs_voice_id` or `elevenlabs_voice_prompt`
4. Calls ElevenLabs API with appropriate voice
5. Returns base64-encoded audio

## Error Handling

- 400: Missing required fields
- 404: Faculty not found
- 500: ElevenLabs API error or function error
