# Deploy Function via Supabase API

Since Docker is having issues, here's an alternative using the Supabase Management API:

## Option 1: Use Supabase Dashboard (Easiest)

1. Go to: https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/functions
2. Click **"Create a new function"**
3. Name: `text-to-speech`
4. Copy the code from `supabase/functions/text-to-speech/index.ts`
5. Click **Deploy**

## Option 2: Fix Docker and Retry CLI

```bash
# Restart Docker Desktop
# Then retry:
cd /Users/danielmcshan/GitHub/singh
supabase functions deploy text-to-speech --project-ref xougqdomkoisrxdnagcj
```

## Option 3: Use Supabase Management API

You can deploy via the Management API using curl:

```bash
# Get your access token from: https://supabase.com/dashboard/account/tokens
ACCESS_TOKEN="your-access-token"
PROJECT_REF="xougqdomkoisrxdnagcj"

# Read the function code
FUNCTION_CODE=$(cat supabase/functions/text-to-speech/index.ts)

# Deploy via API (this requires the function to be bundled first, which needs Docker)
```

The Management API still requires Docker for bundling, so the dashboard is the best option when Docker isn't working.
