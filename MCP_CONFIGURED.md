# Supabase MCP Configuration

The Supabase MCP server has been configured in `~/.cursor/mcp.json` with:

- **URL**: `https://mcp.supabase.com/mcp`
- **Headers**: 
  - `Authorization`: Bearer token with Supabase anon key
  - `apikey`: Supabase anon key
  - `x-project-ref`: Project reference `xougqdomkoisrxdnagcj`

## Next Steps

1. **Restart Cursor** for the MCP configuration to take effect
2. After restart, Supabase MCP tools should be available
3. You can then deploy the Edge Function using MCP tools

## Note

If the MCP server still doesn't work after restart, it may require a Supabase access token (starts with `sbp_`) instead of the anon key. You can get this from:
- https://supabase.com/dashboard/account/tokens

## Current Status

- ✅ MCP configuration updated
- ✅ Project reference added
- ⏳ Waiting for Cursor restart to activate MCP tools
