# Supabase TTS Edge Function Setup

## Overview

The text-to-speech functionality now uses a Supabase Edge Function that securely handles ElevenLabs API calls. The API key is stored in Supabase secrets, not exposed to the client.

## Setup Steps

### 1. Set ElevenLabs API Key in Supabase

**Using Supabase Dashboard (Recommended)**
1. Go to: https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj
2. Navigate to: **Project Settings** → **Edge Functions** → **Secrets**
3. Click **Add Secret**
4. Name: `ELEVENLABS_API_KEY`
5. Value: `sk_ca784069ef0a2893180b5e730db281ad04313dff403a0a8d`
6. Click **Save**

**Alternative: Using Supabase CLI**
```bash
cd /Users/danielmcshan/GitHub/singh
supabase secrets set ELEVENLABS_API_KEY=sk_ca784069ef0a2893180b5e730db281ad04313dff403a0a8d
```

### 2. Deploy Edge Function

```bash
cd /Users/danielmcshan/GitHub/singh
supabase functions deploy text-to-speech
```

### 3. Update Frontend (Already Done)

The frontend now calls the Supabase Edge Function instead of ElevenLabs directly:
- Function URL: `https://xougqdomkoisrxdnagcj.supabase.co/functions/v1/text-to-speech`
- Requires Supabase Anon Key (stored in localStorage)

### 4. Set Supabase Anon Key in Browser

The frontend will prompt for the Supabase Anon Key on first load, or you can set it manually:

```javascript
localStorage.setItem('SUPABASE_ANON_KEY', 'your-anon-key-here');
```

To get your Supabase Anon Key:
1. Go to: https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/settings/api
2. Copy the **anon/public** key

## How It Works

1. **Frontend** sends request to Supabase Edge Function with:
   - `faculty_name`: Name or ID of faculty member
   - `text`: Text to convert to speech

2. **Edge Function**:
   - Looks up faculty in Supabase database
   - Retrieves `elevenlabs_voice_id` or `elevenlabs_voice_prompt`
   - Calls ElevenLabs API using secret stored in Supabase
   - Returns base64-encoded audio

3. **Frontend**:
   - Converts base64 to audio blob
   - Plays audio in browser

## Security Benefits

- ✅ ElevenLabs API key never exposed to client
- ✅ Rate limiting can be added at function level
- ✅ Usage tracking possible
- ✅ Centralized error handling

## Testing

Test the function directly:

```bash
curl -X POST 'https://xougqdomkoisrxdnagcj.supabase.co/functions/v1/text-to-speech' \
  -H 'Authorization: Bearer YOUR_ANON_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "faculty_name": "Mary Shelley",
    "text": "Hello, this is a test of the text to speech function."
  }'
```

## GitHub Secrets

The ElevenLabs key is also stored in GitHub Secrets for CI/CD:
- Secret name: `ELEVENLABS_API_KEY`
- Set via: `gh secret set ELEVENLABS_API_KEY`

This allows GitHub Actions to use the key if needed for automated processes.
