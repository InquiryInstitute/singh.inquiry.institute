# ElevenLabs Integration Setup

## Overview

The site now includes automatic faculty selection and ElevenLabs text-to-speech integration for delivering Khan Academy lectures. The TTS functionality uses a Supabase Edge Function for secure API key management.

## Features

1. **Automatic Faculty Selection**: Best faculty is automatically selected based on lecture subject and faculty expertise
2. **ElevenLabs Voice Generation**: Uses faculty voice prompts from Supabase to generate audio
3. **Playback Widget**: Each lecture card has a play button to generate and play audio

## Setup

### 1. Supabase Migration

Run the migration to add ElevenLabs voice fields to the faculty table:

```sql
-- Run in Supabase SQL Editor
ALTER TABLE public.faculty 
ADD COLUMN IF NOT EXISTS elevenlabs_voice_id text;

ALTER TABLE public.faculty 
ADD COLUMN IF NOT EXISTS elevenlabs_voice_prompt text;
```

Or use the migration file: `supabase/migrations/002_add_faculty_elevenlabs_voice.sql`

### 2. Add Voice Prompts to Faculty

Update faculty records with their ElevenLabs voice prompts:

```sql
UPDATE public.faculty 
SET elevenlabs_voice_prompt = 'A thoughtful, articulate female voice with a British accent, speaking with poetic elegance and scientific curiosity.'
WHERE id = 'a.shelley';

UPDATE public.faculty 
SET elevenlabs_voice_id = 'YOUR_VOICE_ID'  -- Optional: if you have a cloned voice
WHERE id = 'a.shelley';
```

### 3. Set Supabase Secrets

The ElevenLabs API key is stored securely in Supabase secrets (not exposed to client):

```bash
supabase secrets set ELEVENLABS_API_KEY=sk_ca784069ef0a2893180b5e730db281ad04313dff403a0a8d
```

See `SUPABASE_TTS_SETUP.md` for detailed setup instructions.

### 4. Set Supabase Anon Key in Browser

The frontend needs the Supabase Anon Key to call the Edge Function:

**Option A: Browser Prompt (First Load)**
- When you first visit the page, you'll be prompted to enter the Supabase Anon Key
- It's stored in localStorage

**Option B: Set Manually**
```javascript
localStorage.setItem('SUPABASE_ANON_KEY', 'your-anon-key-here');
```

Get your Supabase Anon Key from: https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/settings/api

## How It Works

1. **Faculty Selection**: When a lecture is displayed, the system automatically selects the best faculty based on:
   - Lecture subject (Math, Physics, Biology, etc.)
   - Faculty expertise fields
   - Matching score algorithm

2. **Audio Generation**: When you click play:
   - Calls Supabase Edge Function with faculty name and text
   - Edge Function fetches faculty voice prompt from database
   - Edge Function calls ElevenLabs API (key stored securely in Supabase)
   - Returns base64-encoded audio to frontend
   - Frontend converts to blob and caches in localStorage
   - Plays audio in playback widget

3. **Voice Selection**: 
   - If `elevenlabs_voice_id` exists, uses that specific voice
   - Otherwise uses default voice with voice prompt

## Faculty Expertise Mapping

The system maps lecture subjects to faculty expertise:

- **Math** → Mathematics, Physics, Engineering
- **Physics** → Physics, Mathematics, Engineering  
- **Biology** → Biology, Science, Natural History
- **Chemistry** → Chemistry, Physics, Science
- **History** → History, Philosophy
- **Earth Science** → Science, Natural History

## API Usage

The integration uses ElevenLabs Text-to-Speech API:

- **Endpoint**: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
- **Method**: POST
- **Headers**: 
  - `xi-api-key`: Your API key
  - `Accept`: `audio/mpeg`
- **Body**: JSON with text and voice settings

## Cost Considerations

ElevenLabs charges per character. For a typical 10-minute lecture transcript (~1500 words = ~7500 characters), expect:
- ~$0.30 per lecture (at $0.30 per 1000 characters)

## Next Steps

1. Run Supabase migration
2. Add voice prompts to faculty records
3. Get ElevenLabs API key
4. Test audio generation
5. Optionally clone voices for each faculty member
