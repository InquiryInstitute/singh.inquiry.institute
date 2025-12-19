-- Khan Academy Transcripts Schema for Supabase
-- Supports vector embeddings for RAG/search functionality

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

-- Enable pgvector for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- TABLES
-- ============================================================================

-- Videos table: stores metadata about Khan Academy videos
CREATE TABLE IF NOT EXISTS public.khan_videos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  youtube_id text UNIQUE NOT NULL,
  title text,
  description text,
  duration_seconds int,
  khan_topic text,
  khan_subject text,
  khan_course text,
  url text,
  thumbnail_url text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Transcripts table: stores processed transcripts
CREATE TABLE IF NOT EXISTS public.khan_transcripts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id uuid NOT NULL REFERENCES public.khan_videos(id) ON DELETE CASCADE,
  youtube_id text NOT NULL, -- Denormalized for easier queries
  raw_vtt text, -- Original WebVTT content
  full_text text NOT NULL, -- Full transcript text
  word_count int,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Transcript chunks: for vector embeddings and RAG
CREATE TABLE IF NOT EXISTS public.khan_transcript_chunks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  transcript_id uuid NOT NULL REFERENCES public.khan_transcripts(id) ON DELETE CASCADE,
  video_id uuid NOT NULL REFERENCES public.khan_videos(id) ON DELETE CASCADE,
  chunk_text text NOT NULL,
  chunk_index int NOT NULL, -- Order within transcript
  start_time_seconds float,
  end_time_seconds float,
  embedding vector(1536), -- OpenAI ada-002 or similar
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Video indexes
CREATE INDEX IF NOT EXISTS idx_khan_videos_youtube_id ON public.khan_videos(youtube_id);
CREATE INDEX IF NOT EXISTS idx_khan_videos_topic ON public.khan_videos(khan_topic);
CREATE INDEX IF NOT EXISTS idx_khan_videos_subject ON public.khan_videos(khan_subject);
CREATE INDEX IF NOT EXISTS idx_khan_videos_course ON public.khan_videos(khan_course);

-- Transcript indexes
CREATE INDEX IF NOT EXISTS idx_khan_transcripts_video_id ON public.khan_transcripts(video_id);
CREATE INDEX IF NOT EXISTS idx_khan_transcripts_youtube_id ON public.khan_transcripts(youtube_id);
CREATE INDEX IF NOT EXISTS idx_khan_transcripts_full_text ON public.khan_transcripts USING gin(to_tsvector('english', full_text));

-- Chunk indexes
CREATE INDEX IF NOT EXISTS idx_khan_chunks_transcript_id ON public.khan_transcript_chunks(transcript_id);
CREATE INDEX IF NOT EXISTS idx_khan_chunks_video_id ON public.khan_transcript_chunks(video_id);
CREATE INDEX IF NOT EXISTS idx_khan_chunks_embedding ON public.khan_transcript_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Search transcripts by similarity
CREATE OR REPLACE FUNCTION search_transcript_chunks(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 10,
  topic_filter text DEFAULT NULL,
  subject_filter text DEFAULT NULL
)
RETURNS TABLE (
  chunk_id uuid,
  video_id uuid,
  youtube_id text,
  title text,
  chunk_text text,
  similarity float,
  start_time_seconds float,
  end_time_seconds float,
  metadata jsonb
) AS $$
BEGIN
  RETURN QUERY
    SELECT 
      c.id as chunk_id,
      c.video_id,
      v.youtube_id,
      v.title,
      c.chunk_text,
      1 - (c.embedding <=> query_embedding) as similarity,
      c.start_time_seconds,
      c.end_time_seconds,
      c.metadata
    FROM public.khan_transcript_chunks c
    JOIN public.khan_videos v ON c.video_id = v.id
    WHERE 
      c.embedding IS NOT NULL
      AND (topic_filter IS NULL OR v.khan_topic = topic_filter)
      AND (subject_filter IS NULL OR v.khan_subject = subject_filter)
      AND (1 - (c.embedding <=> query_embedding)) >= match_threshold
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER update_khan_videos_updated_at
  BEFORE UPDATE ON public.khan_videos
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_khan_transcripts_updated_at
  BEFORE UPDATE ON public.khan_transcripts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_khan_chunks_updated_at
  BEFORE UPDATE ON public.khan_transcript_chunks
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- RLS (Row Level Security)
-- ============================================================================

ALTER TABLE public.khan_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.khan_transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.khan_transcript_chunks ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Public read access on videos"
  ON public.khan_videos FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Public read access on transcripts"
  ON public.khan_transcripts FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Public read access on chunks"
  ON public.khan_transcript_chunks FOR SELECT
  TO public
  USING (true);

-- Service role full access
CREATE POLICY "Service role full access on videos"
  ON public.khan_videos FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role full access on transcripts"
  ON public.khan_transcripts FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role full access on chunks"
  ON public.khan_transcript_chunks FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE public.khan_videos IS 'Khan Academy video metadata';
COMMENT ON TABLE public.khan_transcripts IS 'Processed transcripts from Khan Academy videos';
COMMENT ON TABLE public.khan_transcript_chunks IS 'Chunked transcripts with vector embeddings for RAG/search';
COMMENT ON FUNCTION search_transcript_chunks IS 'Search transcript chunks by vector similarity with optional topic/subject filters';
