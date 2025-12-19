#!/usr/bin/env python3
"""
Index Khan Academy transcripts in Supabase.

This script:
1. Reads transcripts from local files or processes them
2. Chunks transcripts for vector embeddings
3. Uploads to Supabase with metadata
4. Optionally generates embeddings (requires OpenAI API or similar)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from storage.supabase_storage import SupabaseStorage
from process.process_transcripts import TranscriptProcessor
import logging
import argparse
import json
import os
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Split text into chunks for embedding.
    
    Args:
        text: Full text to chunk
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks in characters
    
    Returns:
        List of chunk dictionaries
    """
    chunks = []
    words = text.split()
    current_chunk = []
    current_length = 0
    chunk_index = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        if current_length + word_length > chunk_size and current_chunk:
            # Save current chunk
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'chunk_text': chunk_text,
                'chunk_index': chunk_index,
                'start_time_seconds': None,  # Could parse from VTT if available
                'end_time_seconds': None,
                'metadata': {}
            })
            chunk_index += 1
            
            # Start new chunk with overlap
            overlap_words = int(overlap / 10)  # Rough word count for overlap
            current_chunk = current_chunk[-overlap_words:] if len(current_chunk) > overlap_words else current_chunk
            current_length = sum(len(w) + 1 for w in current_chunk)
        
        current_chunk.append(word)
        current_length += word_length
    
    # Add final chunk
    if current_chunk:
        chunks.append({
            'chunk_text': ' '.join(current_chunk),
            'chunk_index': chunk_index,
            'start_time_seconds': None,
            'end_time_seconds': None,
            'metadata': {}
        })
    
    return chunks


def generate_embedding(text: str, api_key: Optional[str] = None) -> Optional[List[float]]:
    """
    Generate embedding for text using OpenAI API.
    
    Args:
        text: Text to embed
        api_key: OpenAI API key (or use OPENAI_API_KEY env var)
    
    Returns:
        Embedding vector (1536 dimensions) or None
    """
    try:
        import openai
        
        api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API key not found. Skipping embedding generation.")
            return None
        
        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except ImportError:
        logger.warning("openai package not installed. Install with: pip install openai")
        return None
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None


def index_transcript_file(transcript_path: Path, supabase: SupabaseStorage, 
                         video_metadata: Dict[str, Any], generate_embeddings: bool = False) -> bool:
    """
    Index a single transcript file in Supabase.
    
    Args:
        transcript_path: Path to transcript file (.txt or .json)
        supabase: Supabase storage instance
        video_metadata: Video metadata dictionary
        generate_embeddings: Whether to generate embeddings for chunks
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read transcript
        if transcript_path.suffix == '.json':
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)
                full_text = transcript_data.get('text', '')
                raw_vtt = transcript_data.get('raw_vtt', '')
        else:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
                raw_vtt = None
        
        if not full_text:
            logger.warning(f"Empty transcript: {transcript_path}")
            return False
        
        # Upsert video
        video_id = supabase.upsert_video(video_metadata)
        if not video_id:
            logger.error(f"Failed to upsert video: {video_metadata.get('youtube_id')}")
            return False
        
        # Upsert transcript
        transcript_data = {
            'video_id': video_id,
            'youtube_id': video_metadata['youtube_id'],
            'full_text': full_text,
            'raw_vtt': raw_vtt,
            'word_count': len(full_text.split()),
            'metadata': {}
        }
        transcript_id = supabase.upsert_transcript(transcript_data)
        if not transcript_id:
            logger.error(f"Failed to upsert transcript for video: {video_metadata.get('youtube_id')}")
            return False
        
        # Chunk transcript
        chunks = chunk_text(full_text)
        logger.info(f"Created {len(chunks)} chunks for transcript {transcript_id}")
        
        # Generate embeddings if requested
        if generate_embeddings:
            logger.info("Generating embeddings...")
            for chunk in chunks:
                embedding = generate_embedding(chunk['chunk_text'])
                if embedding:
                    chunk['embedding'] = embedding
        
        # Upsert chunks
        chunk_count = supabase.upsert_chunks(chunks, transcript_id, video_id)
        logger.info(f"Indexed {chunk_count} chunks for video {video_metadata.get('youtube_id')}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to index transcript {transcript_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Index Khan Academy transcripts in Supabase")
    parser.add_argument("--transcripts-dir", type=Path, required=True,
                       help="Directory containing transcript files")
    parser.add_argument("--catalog", type=Path,
                       help="Video catalog JSON file (for metadata)")
    parser.add_argument("--supabase-url", type=str,
                       help="Supabase project URL (or use SUPABASE_URL env var, or loads from ../Inquiry.Institute/.env.local)")
    parser.add_argument("--supabase-key", type=str,
                       help="Supabase service role key (or use SUPABASE_KEY env var, or loads from ../Inquiry.Institute/.env.local)")
    parser.add_argument("--generate-embeddings", action="store_true",
                       help="Generate embeddings for chunks (requires OpenAI API key)")
    parser.add_argument("--max", type=int, default=None,
                       help="Maximum number of transcripts to index")
    
    args = parser.parse_args()
    
    # Initialize Supabase (will auto-load from Inquiry.Institute if not provided)
    try:
        supabase = SupabaseStorage(args.supabase_url, args.supabase_key)
        logger.info(f"Connected to Supabase: {supabase.supabase_url[:30]}...")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
        logger.info("Trying to load credentials from ../Inquiry.Institute/.env.local...")
        return
    
    # Load catalog if provided
    catalog = {}
    if args.catalog and args.catalog.exists():
        with open(args.catalog, 'r', encoding='utf-8') as f:
            catalog_list = json.load(f)
            # Index by youtube_id
            for video in catalog_list:
                youtube_id = video.get('youtube_id') or video.get('id')
                if youtube_id:
                    catalog[youtube_id] = video
    
    # Find transcript files
    transcript_files = []
    for ext in ['.txt', '.json']:
        transcript_files.extend(args.transcripts_dir.glob(f'*{ext}'))
        transcript_files.extend(args.transcripts_dir.glob(f'**/*{ext}'))
    
    if args.max:
        transcript_files = transcript_files[:args.max]
    
    logger.info(f"Found {len(transcript_files)} transcript files")
    
    # Index each transcript
    successful = 0
    failed = 0
    
    for transcript_file in transcript_files:
        # Try to extract YouTube ID from filename
        youtube_id = transcript_file.stem.replace('_transcript', '').replace('_text', '')
        
        # Get metadata from catalog
        video_metadata = catalog.get(youtube_id, {
            'youtube_id': youtube_id,
            'title': None,
            'description': None,
        })
        
        # Ensure youtube_id is set
        video_metadata['youtube_id'] = youtube_id
        
        if index_transcript_file(transcript_file, supabase, video_metadata, args.generate_embeddings):
            successful += 1
        else:
            failed += 1
    
    logger.info(f"Indexing complete: {successful} successful, {failed} failed")


if __name__ == "__main__":
    main()
