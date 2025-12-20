# Deploy Text-to-Speech Function

## Option 1: Deploy via Supabase Dashboard (Recommended)

1. **Go to Edge Functions in Dashboard:**
   - Navigate to: https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/functions

2. **Create New Function:**
   - Click **"Create a new function"**
   - Name: `text-to-speech`
   - Copy the contents of `supabase/functions/text-to-speech/index.ts` into the editor
   - Click **Deploy**

3. **Set Secret:**
   - Go to: https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/settings/functions
   - Under **Secrets**, click **Add Secret**
   - Name: `ELEVENLABS_API_KEY`
   - Value: `sk_ca784069ef0a2893180b5e730db281ad04313dff403a0a8d`
   - Click **Save**

## Option 2: Deploy via CLI (if Docker is working)

If you have Docker running and are authenticated:

```bash
cd /Users/danielmcshan/GitHub/singh

# Login to Supabase (will open browser)
supabase login

# Link project
supabase link --project-ref xougqdomkoisrxdnagcj

# Deploy function
supabase functions deploy text-to-speech --project-ref xougqdomkoisrxdnagcj
```

## Option 3: Manual Upload via Dashboard

1. Go to: https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/functions
2. Click **"Create a new function"**
3. Name it: `text-to-speech`
4. Copy the code from `supabase/functions/text-to-speech/index.ts`
5. Click **Deploy**

## Verify Deployment

After deployment, test the function:

```bash
curl -X POST 'https://xougqdomkoisrxdnagcj.supabase.co/functions/v1/text-to-speech' \
  -H 'Authorization: Bearer YOUR_ANON_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "faculty_name": "Mary Shelley",
    "text": "Hello, this is a test."
  }'
```

The function should return JSON with `audio_base64` field.
