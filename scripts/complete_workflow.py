#!/usr/bin/env python3
"""
Complete workflow: Discover videos → Download transcripts → Index in Supabase

This script ties together all the pieces:
1. Discover Khan Academy videos (web scraping)
2. Download transcripts (YouTube)
3. Process transcripts
4. Index in Supabase with embeddings
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import logging
import argparse
import subprocess
import json
from storage.supabase_storage import SupabaseStorage
from storage.gcs_storage import GCSStorage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_command(cmd, description):
    """Run a command and log the result."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Step: {description}")
    logger.info(f"Command: {' '.join(cmd)}")
    logger.info(f"{'='*60}\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Command failed: {result.stderr}")
        return False
    
    logger.info(result.stdout)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Complete workflow: Discover → Download → Index transcripts"
    )
    parser.add_argument("--topic-url", type=str,
                       help="Khan Academy topic URL to scrape (e.g., https://www.khanacademy.org/math/algebra)")
    parser.add_argument("--youtube-ids", type=str,
                       help="Comma-separated YouTube video IDs (skip discovery)")
    parser.add_argument("--catalog", type=Path,
                       default=Path("data/metadata/khan_academy_catalog.json"),
                       help="Path to existing catalog (skip discovery)")
    parser.add_argument("--max-videos", type=int, default=10,
                       help="Maximum number of videos to process")
    parser.add_argument("--generate-embeddings", action="store_true",
                       help="Generate embeddings for chunks (requires OPENAI_API_KEY)")
    parser.add_argument("--skip-discovery", action="store_true",
                       help="Skip video discovery step")
    parser.add_argument("--skip-download", action="store_true",
                       help="Skip transcript download step")
    parser.add_argument("--skip-indexing", action="store_true",
                       help="Skip Supabase indexing step")
    
    args = parser.parse_args()
    
    catalog_path = args.catalog
    transcripts_dir = Path("data/transcripts/processed")
    
    # Step 1: Discover videos
    if not args.skip_discovery and not args.catalog.exists() and not args.youtube_ids:
        logger.info("Step 1: Discovering videos...")
        
        if args.topic_url:
            cmd = [
                "python3", "scripts/discover_videos_scraper.py",
                "--topic-url", args.topic_url,
                "--output", str(catalog_path),
                "--max-videos", str(args.max_videos),
            ]
            if not run_command(cmd, "Discover videos from topic"):
                logger.error("Discovery failed")
                return
        elif args.youtube_ids:
            # Create minimal catalog from YouTube IDs
            logger.info("Creating catalog from YouTube IDs...")
            videos = []
            for yt_id in args.youtube_ids.split(','):
                videos.append({
                    'youtube_id': yt_id.strip(),
                    'title': None,
                    'description': None,
                })
            
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            with open(catalog_path, 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2)
            logger.info(f"Created catalog with {len(videos)} videos")
        else:
            logger.warning("No discovery method specified. Use --topic-url or --youtube-ids")
            return
    
    # Step 2: Download transcripts
    if not args.skip_download:
        logger.info("\nStep 2: Downloading transcripts...")
        
        if args.youtube_ids:
            cmd = [
                "python3", "scripts/download_transcripts_only.py",
                "--youtube-ids", args.youtube_ids,
                "--max", str(args.max_videos),
            ]
        else:
            cmd = [
                "python3", "scripts/download_transcripts_only.py",
                "--catalog", str(catalog_path),
                "--max", str(args.max_videos),
            ]
        
        if not run_command(cmd, "Download transcripts"):
            logger.error("Download failed")
            return
    
    # Step 3: Index in Supabase
    if not args.skip_indexing:
        logger.info("\nStep 3: Indexing transcripts in Supabase...")
        
        # Check if transcripts exist
        if not transcripts_dir.exists():
            logger.warning(f"Transcripts directory not found: {transcripts_dir}")
            logger.info("Skipping indexing step")
            return
        
        # Initialize Supabase
        try:
            supabase = SupabaseStorage()
            logger.info("✓ Connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            return
        
        cmd = [
            "python3", "scripts/index_transcripts_supabase.py",
            "--transcripts-dir", str(transcripts_dir),
            "--catalog", str(catalog_path),
        ]
        
        if args.generate_embeddings:
            cmd.append("--generate-embeddings")
        
        if not run_command(cmd, "Index transcripts in Supabase"):
            logger.error("Indexing failed")
            return
    
    logger.info("\n" + "="*60)
    logger.info("✓ Complete workflow finished!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
