# Supabase MCP Not Working

The Supabase MCP server at `https://mcp.supabase.com/mcp` is not responding correctly:
- Returns "JWT failed verification" 
- Returns "Method not found" for MCP methods
- Tools are not accessible

## Solution: Deploy via Dashboard

Since MCP isn't working, deploy the function via the Supabase Dashboard:

1. **Go to Edge Functions:**
   https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/functions

2. **Create New Function:**
   - Click "Create a new function"
   - Name: `text-to-speech`
   - Copy the code from `supabase/functions/text-to-speech/index.ts` (148 lines)
   - Click Deploy

3. **Verify:**
   - Secret `ELEVENLABS_API_KEY` is already set
   - Function will work immediately after deployment

The function code is ready and the secret is configured. Once deployed via dashboard, it will be fully functional.
