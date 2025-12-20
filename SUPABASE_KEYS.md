# Supabase Keys Location

## Where to Get Supabase Anon Key

1. **Go to Supabase Dashboard:**
   https://supabase.com/dashboard/project/xougqdomkoisrxdnagcj/settings/api

2. **Find the "Project API keys" section**

3. **Copy the `anon` `public` key** (this is the anon key)

## Current Keys (from .env.local)

- **Supabase URL**: `https://xougqdomkoisrxdnagcj.supabase.co`
- **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvdWdxZG9ta29pc3J4ZG5hZ2NqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5NjIwMTIsImV4cCI6MjA4MTUzODAxMn0.eA1vXG6UVI1AjUOXN7q3gTlSyPoDByuVehOcKPjHmvs`
- **Service Role Key**: `sb_secret_sN0tF2L2uRk0d-kCV11FyA_Z3z5flmU` (secret, server-side only)

## For Supabase Access Token (for MCP)

If you need a Supabase access token (starts with `sbp_`):
1. Go to: https://supabase.com/dashboard/account/tokens
2. Click "Generate new token"
3. Copy the token (it starts with `sbp_`)

## Note

The anon key is already configured in the MCP settings. If the MCP server needs an access token instead, you'll need to get one from the tokens page.
