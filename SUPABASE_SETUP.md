# Supabase Setup for Khan Academy Transcripts

## Overview

This project uses Supabase to store and index Khan Academy transcripts with vector embeddings for RAG/search functionality.

## Credentials

The Supabase credentials are automatically loaded from `../Inquiry.Institute/.env.local` if available. The following environment variables are used:

- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Service role key (preferred for server-side operations)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Anonymous key (fallback if service role not available)

## Manual Setup

If you need to set credentials manually:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-service-role-key"
```

Or create a `.env` file in the project root:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

## Database Schema

Run the migration to create the necessary tables:

```bash
# Using Supabase CLI (if installed)
supabase db push supabase/migrations/001_create_transcripts_schema.sql

# Or manually via Supabase Dashboard > SQL Editor
# Copy and paste the contents of supabase/migrations/001_create_transcripts_schema.sql
```

## Tables Created

1. **khan_videos** - Video metadata (YouTube ID, title, topic, etc.)
2. **khan_transcripts** - Full transcripts with text
3. **khan_transcript_chunks** - Chunked transcripts with vector embeddings

## Usage

### Index Transcripts

```bash
# Index transcripts from local directory
python scripts/index_transcripts_supabase.py \
  --transcripts-dir data/transcripts/processed \
  --catalog data/metadata/khan_academy_catalog.json \
  --generate-embeddings  # Optional: requires OPENAI_API_KEY
```

### Search Transcripts

The schema includes a `search_transcript_chunks` function for vector similarity search:

```sql
SELECT * FROM search_transcript_chunks(
  query_embedding := '[0.1, 0.2, ...]'::vector(1536),
  match_threshold := 0.7,
  match_count := 10,
  topic_filter := 'algebra'  -- Optional
);
```

## Vector Embeddings

To generate embeddings, you need:

1. OpenAI API key: `export OPENAI_API_KEY="sk-..."`
2. Run with `--generate-embeddings` flag

The script uses `text-embedding-ada-002` model (1536 dimensions).

## Next Steps

1. Run the migration to create tables
2. Download transcripts (see `TRANSCRIPT_STATUS.md`)
3. Index transcripts in Supabase
4. Generate embeddings for search functionality
