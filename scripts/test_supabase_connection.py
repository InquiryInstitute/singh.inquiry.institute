#!/usr/bin/env python3
"""
Test Supabase connection and verify schema.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from storage.supabase_storage import SupabaseStorage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection():
    """Test Supabase connection and verify tables exist."""
    try:
        logger.info("Initializing Supabase client...")
        supabase = SupabaseStorage()
        logger.info(f"✓ Connected to Supabase: {supabase.supabase_url}")
        
        # Test querying tables
        logger.info("\nTesting table access...")
        
        # Check khan_videos table
        try:
            result = supabase.client.table('khan_videos').select('count', count='exact').limit(1).execute()
            logger.info(f"✓ khan_videos table accessible (count: {result.count if hasattr(result, 'count') else 'N/A'})")
        except Exception as e:
            logger.warning(f"✗ khan_videos table: {e}")
            logger.info("  → Run migration: supabase/migrations/001_create_transcripts_schema.sql")
        
        # Check khan_transcripts table
        try:
            result = supabase.client.table('khan_transcripts').select('count', count='exact').limit(1).execute()
            logger.info(f"✓ khan_transcripts table accessible (count: {result.count if hasattr(result, 'count') else 'N/A'})")
        except Exception as e:
            logger.warning(f"✗ khan_transcripts table: {e}")
        
        # Check khan_transcript_chunks table
        try:
            result = supabase.client.table('khan_transcript_chunks').select('count', count='exact').limit(1).execute()
            logger.info(f"✓ khan_transcript_chunks table accessible (count: {result.count if hasattr(result, 'count') else 'N/A'})")
        except Exception as e:
            logger.warning(f"✗ khan_transcript_chunks table: {e}")
        
        # Test search function
        logger.info("\nTesting search function...")
        try:
            # Create a dummy embedding vector (1536 dimensions)
            dummy_embedding = [0.0] * 1536
            result = supabase.client.rpc(
                'search_transcript_chunks',
                {
                    'query_embedding': dummy_embedding,
                    'match_threshold': 0.7,
                    'match_count': 1
                }
            ).execute()
            logger.info("✓ search_transcript_chunks function accessible")
        except Exception as e:
            logger.warning(f"✗ search_transcript_chunks function: {e}")
        
        logger.info("\n✓ Supabase connection test complete!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Connection failed: {e}")
        logger.info("\nTroubleshooting:")
        logger.info("1. Check that ../Inquiry.Institute/.env.local exists")
        logger.info("2. Verify SUPABASE_URL and SUPABASE_KEY are set")
        logger.info("3. Run migration: supabase/migrations/001_create_transcripts_schema.sql")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
