# Deploy Function via Dashboard (Recommended)

Since Docker is having issues and the Management API requires an access token, the easiest way is via the Supabase Dashboard:

## Steps:

1. **Go to Edge Functions:**
   https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/functions

2. **Create New Function:**
   - Click **"Create a new function"**
   - Name: `text-to-speech`
   - Copy the entire code from `supabase/functions/text-to-speech/index.ts` (148 lines)
   - Click **Deploy**

3. **Verify Secret is Set:**
   - The `ELEVENLABS_API_KEY` secret is already set via CLI
   - Verify at: https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/settings/functions

4. **Test the Function:**
   ```bash
   curl -X POST 'https://xougqdomkoisrxdnagcj.supabase.co/functions/v1/text-to-speech' \
     -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvdWdxZG9ta29pc3J4ZG5hZ2NqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5NjIwMTIsImV4cCI6MjA4MTUzODAxMn0.eA1vXG6UVI1AjUOXN7q3gTlSyPoDByuVehOcKPjHmvs' \
     -H 'Content-Type: application/json' \
     -d '{"faculty_name":"Mary Shelley","text":"Hello, this is a test."}'
   ```

The function code is ready at: `supabase/functions/text-to-speech/index.ts`
