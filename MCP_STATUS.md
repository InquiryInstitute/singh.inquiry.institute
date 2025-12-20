# Supabase MCP Status

## Current Situation

The Supabase MCP server is configured in `~/.cursor/mcp.json`, but the tools are not available:
- Error: "Method not found" when trying to list MCP resources
- The server at `https://mcp.supabase.com/mcp` may not be a standard MCP server
- Or it may require a Supabase access token (starts with `sbp_`) instead of the anon key

## Options

### Option 1: Deploy via Dashboard (Recommended)
1. Go to: https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/functions
2. Click "Create a new function"
3. Name: `text-to-speech`
4. Copy code from `supabase/functions/text-to-speech/index.ts` (148 lines)
5. Click Deploy

### Option 2: Get Supabase Access Token
If the MCP server needs an access token:
1. Go to: https://supabase.com/dashboard/account/tokens
2. Create a new access token
3. Update `~/.cursor/mcp.json` with the token in the Authorization header

### Option 3: Use Supabase CLI (when Docker is working)
```bash
supabase functions deploy text-to-speech --project-ref xougqdomkoisrxdnagcj
```

## Current Configuration

The MCP is configured with:
- URL: `https://mcp.supabase.com/mcp`
- Headers: Authorization, apikey, x-project-ref
- But tools are not accessible

The `ELEVENLABS_API_KEY` secret is already set in Supabase, so once the function is deployed (via any method), it will work.
