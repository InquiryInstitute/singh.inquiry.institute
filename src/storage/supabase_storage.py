"""
Supabase storage utilities for Khan Academy transcripts.

Handles uploading transcripts, videos, and chunks to Supabase with vector embeddings.
"""

import os
import logging
from typing import Optional, Dict, List, Any
from pathlib import Path
from supabase import create_client, Client
import json

logger = logging.getLogger(__name__)


class SupabaseStorage:
    """
    Handles storage and retrieval of Khan Academy transcripts in Supabase.
    """
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize Supabase client.
        
        Args:
            supabase_url: Supabase project URL (or use SUPABASE_URL env var)
            supabase_key: Supabase service role key (or use SUPABASE_KEY env var)
        """
        # Try to load from Inquiry.Institute .env.local if not provided
        if not supabase_url or not supabase_key:
            try:
                from pathlib import Path
                import re
                
                inquiry_institute_path = Path(__file__).parent.parent.parent.parent / "Inquiry.Institute"
                env_path = inquiry_institute_path / ".env.local"
                
                if not env_path.exists():
                    env_path = inquiry_institute_path / ".env"
                
                if env_path.exists():
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue
                            match = re.match(r'^([^#=]+)=(.*)$', line)
                            if match:
                                key = match.group(1).strip()
                                value = match.group(2).strip().strip('"\'')
                                if key == 'NEXT_PUBLIC_SUPABASE_URL' and not supabase_url:
                                    supabase_url = value
                                elif key == 'SUPABASE_SERVICE_ROLE_KEY' and not supabase_key:
                                    supabase_key = value
                                elif key == 'NEXT_PUBLIC_SUPABASE_ANON_KEY' and not supabase_key:
                                    # Fallback to anon key if service role not available
                                    supabase_key = value
            except Exception as e:
                logger.debug(f"Could not load credentials from Inquiry.Institute: {e}")
        
        self.supabase_url = supabase_url or os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
        self.supabase_key = supabase_key or os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase URL and key required. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables, "
                "or pass them as arguments. "
                "Will also try to load from ../Inquiry.Institute/.env.local"
            )
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase client initialized")
    
    def upsert_video(self, video_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert or update a video record.
        
        Args:
            video_data: Dictionary with video metadata including:
                - youtube_id (required)
                - title, description, duration_seconds
                - khan_topic, khan_subject, khan_course
                - url, thumbnail_url
                - metadata (jsonb)
        
        Returns:
            Video UUID if successful, None otherwise
        """
        try:
            # Check if video exists
            result = self.client.table('khan_videos').select('id').eq('youtube_id', video_data['youtube_id']).execute()
            
            if result.data:
                # Update existing
                video_id = result.data[0]['id']
                self.client.table('khan_videos').update(video_data).eq('id', video_id).execute()
                logger.info(f"Updated video: {video_data['youtube_id']}")
            else:
                # Insert new
                result = self.client.table('khan_videos').insert(video_data).execute()
                video_id = result.data[0]['id'] if result.data else None
                logger.info(f"Inserted video: {video_data['youtube_id']}")
            
            return video_id
        except Exception as e:
            logger.error(f"Failed to upsert video {video_data.get('youtube_id')}: {e}")
            return None
    
    def upsert_transcript(self, transcript_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert or update a transcript record.
        
        Args:
            transcript_data: Dictionary with transcript data including:
                - video_id (uuid) or youtube_id (text)
                - full_text (required)
                - raw_vtt (optional)
                - word_count (optional)
                - metadata (jsonb)
        
        Returns:
            Transcript UUID if successful, None otherwise
        """
        try:
            # If youtube_id provided, get video_id
            if 'youtube_id' in transcript_data and 'video_id' not in transcript_data:
                video_result = self.client.table('khan_videos').select('id').eq('youtube_id', transcript_data['youtube_id']).execute()
                if not video_result.data:
                    logger.error(f"Video not found for youtube_id: {transcript_data['youtube_id']}")
                    return None
                transcript_data['video_id'] = video_result.data[0]['id']
            
            # Check if transcript exists
            result = self.client.table('khan_transcripts').select('id').eq('video_id', transcript_data['video_id']).execute()
            
            if result.data:
                # Update existing
                transcript_id = result.data[0]['id']
                # Remove video_id from update (already set)
                update_data = {k: v for k, v in transcript_data.items() if k != 'video_id'}
                self.client.table('khan_transcripts').update(update_data).eq('id', transcript_id).execute()
                logger.info(f"Updated transcript for video_id: {transcript_data['video_id']}")
            else:
                # Insert new
                result = self.client.table('khan_transcripts').insert(transcript_data).execute()
                transcript_id = result.data[0]['id'] if result.data else None
                logger.info(f"Inserted transcript for video_id: {transcript_data['video_id']}")
            
            return transcript_id
        except Exception as e:
            logger.error(f"Failed to upsert transcript: {e}")
            return None
    
    def upsert_chunks(self, chunks: List[Dict[str, Any]], transcript_id: str, video_id: str) -> int:
        """
        Insert or update transcript chunks with embeddings.
        
        Args:
            chunks: List of chunk dictionaries with:
                - chunk_text (required)
                - chunk_index (required)
                - start_time_seconds, end_time_seconds (optional)
                - embedding (vector, optional)
                - metadata (jsonb, optional)
            transcript_id: UUID of the transcript
            video_id: UUID of the video
        
        Returns:
            Number of chunks successfully inserted/updated
        """
        if not chunks:
            return 0
        
        try:
            # Delete existing chunks for this transcript
            self.client.table('khan_transcript_chunks').delete().eq('transcript_id', transcript_id).execute()
            
            # Prepare chunks with required fields
            chunks_to_insert = []
            for chunk in chunks:
                chunk_data = {
                    'transcript_id': transcript_id,
                    'video_id': video_id,
                    'chunk_text': chunk['chunk_text'],
                    'chunk_index': chunk['chunk_index'],
                    'start_time_seconds': chunk.get('start_time_seconds'),
                    'end_time_seconds': chunk.get('end_time_seconds'),
                    'embedding': chunk.get('embedding'),
                    'metadata': chunk.get('metadata', {})
                }
                chunks_to_insert.append(chunk_data)
            
            # Insert all chunks
            result = self.client.table('khan_transcript_chunks').insert(chunks_to_insert).execute()
            count = len(result.data) if result.data else 0
            logger.info(f"Inserted {count} chunks for transcript {transcript_id}")
            return count
        except Exception as e:
            logger.error(f"Failed to upsert chunks: {e}")
            return 0
    
    def search_chunks(self, query_embedding: List[float], match_threshold: float = 0.7, 
                     match_count: int = 10, topic_filter: Optional[str] = None,
                     subject_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search transcript chunks by vector similarity.
        
        Args:
            query_embedding: Query vector (1536 dimensions)
            match_threshold: Minimum similarity threshold (0-1)
            match_count: Maximum number of results
            topic_filter: Optional topic filter
            subject_filter: Optional subject filter
        
        Returns:
            List of matching chunks with metadata
        """
        try:
            # Call the search function
            result = self.client.rpc(
                'search_transcript_chunks',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': match_threshold,
                    'match_count': match_count,
                    'topic_filter': topic_filter,
                    'subject_filter': subject_filter
                }
            ).execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to search chunks: {e}")
            return []
    
    def get_video_by_youtube_id(self, youtube_id: str) -> Optional[Dict[str, Any]]:
        """Get video by YouTube ID."""
        try:
            result = self.client.table('khan_videos').select('*').eq('youtube_id', youtube_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get video {youtube_id}: {e}")
            return None
    
    def get_transcript_by_video_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get transcript by video UUID."""
        try:
            result = self.client.table('khan_transcripts').select('*').eq('video_id', video_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get transcript for video {video_id}: {e}")
            return None
