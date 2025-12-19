#!/usr/bin/env python3
"""
Main script to download all Khan Academy videos and transcripts.

This script:
1. Loads the video catalog
2. Downloads all videos and transcripts
3. Processes and saves everything
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from download.download_videos import VideoDownloader
from process.process_transcripts import TranscriptProcessor
from storage.gcs_storage import GCSStorage
import logging
import argparse
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Download all Khan Academy videos and transcripts")
    parser.add_argument("--catalog", type=Path, default=Path("data/metadata/khan_academy_catalog.json"),
                       help="Path to video catalog JSON")
    parser.add_argument("--video-dir", type=Path, default=Path("data/videos"),
                       help="Directory to save videos")
    parser.add_argument("--transcript-dir", type=Path, default=Path("data/transcripts"),
                       help="Directory to save processed transcripts")
    parser.add_argument("--max", type=int, default=None,
                       help="Maximum number of videos to download (for testing)")
    parser.add_argument("--skip-video", action="store_true",
                       help="Skip video download, only get transcripts")
    parser.add_argument("--skip-transcript", action="store_true",
                       help="Skip transcript processing")
    parser.add_argument("--gcs-bucket", type=str, default=None,
                       help="Google Cloud Storage bucket name (enables GCS upload)")
    parser.add_argument("--gcs-credentials", type=Path, default=None,
                       help="Path to GCS credentials JSON file (or set GOOGLE_APPLICATION_CREDENTIALS env var)")
    parser.add_argument("--keep-local", action="store_true",
                       help="Keep local files after uploading to GCS (default: delete after upload)")
    
    args = parser.parse_args()
    
    if not args.catalog.exists():
        logger.error(f"Catalog file not found: {args.catalog}")
        logger.info("Run 'python scripts/discover_all_content.py' first to create the catalog")
        return
    
    logger.info("Starting video and transcript download...")
    
    # Setup GCS storage if configured
    gcs_storage = None
    upload_to_gcs = False
    if args.gcs_bucket:
        logger.info(f"Initializing GCS storage for bucket: {args.gcs_bucket}")
        credentials_path = args.gcs_credentials
        if not credentials_path:
            # Check environment variable
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path:
                credentials_path = Path(credentials_path)
        
        try:
            gcs_storage = GCSStorage(args.gcs_bucket, str(credentials_path) if credentials_path else None)
            upload_to_gcs = True
            logger.info("GCS upload enabled - files will be uploaded to bucket after download")
        except Exception as e:
            logger.error(f"Failed to initialize GCS storage: {e}")
            logger.error("Continuing with local storage only")
            upload_to_gcs = False
    
    # Download videos
    if not args.skip_video:
        logger.info("Downloading videos...")
        downloader = VideoDownloader(
            output_dir=args.video_dir,
            download_video=True,
            download_transcript=True,
            gcs_storage=gcs_storage,
            upload_to_gcs=upload_to_gcs,
            delete_after_upload=upload_to_gcs and not args.keep_local
        )
        results, failed = downloader.download_from_catalog(args.catalog, max_videos=args.max)
        logger.info(f"Downloaded {len(results)} videos, {len(failed)} failed")
        
        # Upload download results to GCS if configured
        if upload_to_gcs and gcs_storage:
            import json
            results_summary = {
                'successful': len(results),
                'failed': len(failed),
                'total': len(results) + len(failed),
                'results': results[:100]  # First 100 for reference
            }
            gcs_storage.upload_json(results_summary, "metadata/download_results.json")
            logger.info("Uploaded download results to GCS")
    else:
        logger.info("Skipping video download")
    
    # Process transcripts
    if not args.skip_transcript:
        logger.info("Processing transcripts...")
        processor = TranscriptProcessor(
            transcripts_dir=args.video_dir,
            output_dir=args.transcript_dir,
            gcs_storage=gcs_storage,
            upload_to_gcs=upload_to_gcs
        )
        processed = processor.process_all_transcripts()
        logger.info(f"Processed {len(processed)} transcripts")
        
        # Upload transcript summary to GCS if configured
        if upload_to_gcs and gcs_storage and processed:
            import json
            summary = {
                'total_transcripts': len(processed),
                'total_words': sum(p.get('word_count', 0) for p in processed),
                'total_segments': sum(p.get('segment_count', 0) for p in processed)
            }
            gcs_storage.upload_json(summary, "metadata/transcripts_summary.json")
            logger.info("Uploaded transcript summary to GCS")
    else:
        logger.info("Skipping transcript processing")
    
    logger.info("Download and processing complete!")


if __name__ == "__main__":
    main()
