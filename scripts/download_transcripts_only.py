#!/usr/bin/env python3
"""
Download only transcripts from Khan Academy videos.

This script is optimized for transcript-only downloads:
- Much faster (no video files)
- Much smaller storage requirements
- Can download transcripts directly from YouTube without downloading videos
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api.khan_academy_api import KhanAcademyAPI
from storage.gcs_storage import GCSStorage
import logging
import argparse
import json
import yt_dlp
import os
from tqdm import tqdm
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class TranscriptDownloader:
    """
    Downloads only transcripts from Khan Academy videos.
    Uses yt-dlp to extract transcripts directly without downloading video files.
    """
    
    def __init__(self, gcs_storage=None, upload_to_gcs=False, output_dir=None):
        """
        Initialize transcript downloader.
        
        Args:
            gcs_storage: Optional GCS storage instance
            upload_to_gcs: Whether to upload to GCS
            output_dir: Local output directory (temporary if uploading to GCS)
        """
        self.gcs_storage = gcs_storage
        self.upload_to_gcs = upload_to_gcs
        self.output_dir = Path(output_dir) if output_dir else Path("/tmp/transcripts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure yt-dlp for transcript-only download
        self.ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,  # Get auto-generated if manual don't exist
            'subtitleslangs': ['en'],
            'subtitlesformat': 'vtt',
            'skip_download': True,  # Don't download video, only subtitles
            'quiet': False,
            'no_warnings': False,
        }
    
    def download_transcript(self, video_url: str, video_metadata: dict) -> dict:
        """
        Download transcript for a single video.
        
        Args:
            video_url: YouTube URL
            video_metadata: Video metadata dictionary
            
        Returns:
            Result dictionary with transcript info
        """
        video_id = video_metadata.get('youtube_id') or video_metadata.get('id')
        logger.info(f"Downloading transcript for: {video_metadata.get('title', video_id)}")
        
        try:
            # Set output template for this specific video
            ydl_opts = self.ydl_opts.copy()
            ydl_opts['outtmpl'] = str(self.output_dir / f'{video_id}.%(ext)s')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                # Find the downloaded transcript file
                transcript_path = self.output_dir / f"{video_id}.en.vtt"
                if not transcript_path.exists():
                    # Try without .en suffix
                    transcript_path = self.output_dir / f"{video_id}.vtt"
                
                result = {
                    'video_id': video_id,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'transcript_path': str(transcript_path) if transcript_path.exists() else None,
                    'gcs_transcript_path': None,
                    'success': transcript_path.exists()
                }
                
                if transcript_path.exists():
                    # Upload to GCS if configured
                    if self.upload_to_gcs and self.gcs_storage:
                        gcs_path = f"transcripts/{video_id}.vtt"
                        if self.gcs_storage.upload_file(transcript_path, gcs_path, 
                                                       content_type='text/vtt',
                                                       metadata={'title': result['title']}):
                            result['gcs_transcript_path'] = gcs_path
                            # Delete local file after upload
                            transcript_path.unlink()
                            logger.info(f"Uploaded and deleted local transcript: {video_id}")
                    
                    return result
                else:
                    logger.warning(f"Transcript file not found for {video_id}")
                    return result
                    
        except Exception as e:
            logger.error(f"Failed to download transcript for {video_id}: {e}")
            return {
                'video_id': video_id,
                'success': False,
                'error': str(e)
            }
    
    def download_from_catalog(self, catalog_path: Path, max_videos=None):
        """
        Download transcripts from catalog.
        
        Args:
            catalog_path: Path to video catalog JSON
            max_videos: Maximum number of videos to process
        """
        logger.info(f"Loading catalog from {catalog_path}")
        
        # Load catalog (could be local file or GCS path)
        if str(catalog_path).startswith('gs://') or (self.gcs_storage and not catalog_path.exists()):
            # Download from GCS
            local_catalog = self.output_dir / "catalog.json"
            if self.gcs_storage:
                gcs_path = str(catalog_path).replace('gs://', '').split('/', 1)[1] if 'gs://' in str(catalog_path) else str(catalog_path)
                self.gcs_storage.download_file(gcs_path, local_catalog)
                catalog_path = local_catalog
        
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        
        if not isinstance(catalog, list):
            catalog = [catalog]
        
        if max_videos:
            catalog = catalog[:max_videos]
        
        results = []
        failed = []
        
        logger.info(f"Starting transcript download for {len(catalog)} videos...")
        
        for video_meta in tqdm(catalog, desc="Downloading transcripts"):
            youtube_id = video_meta.get('youtube_id') or video_meta.get('id')
            if not youtube_id:
                logger.warning(f"No YouTube ID found for video: {video_meta}")
                failed.append(video_meta)
                continue
            
            video_url = f"https://www.youtube.com/watch?v={youtube_id}"
            result = self.download_transcript(video_url, video_meta)
            
            if result.get('success'):
                results.append(result)
            else:
                failed.append(video_meta)
            
            # Rate limiting
            time.sleep(0.5)  # Faster for transcripts only
        
        # Save results
        results_data = {
            'successful': len(results),
            'failed': len(failed),
            'total': len(catalog),
            'results': results[:100]  # First 100 for reference
        }
        
        # Save locally
        results_path = self.output_dir / "transcript_download_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        # Upload to GCS if configured
        if self.upload_to_gcs and self.gcs_storage:
            self.gcs_storage.upload_json(results_data, "metadata/transcript_download_results.json")
        
        logger.info(f"Transcript download complete: {len(results)} successful, {len(failed)} failed")
        return results, failed


def main():
    parser = argparse.ArgumentParser(description="Download Khan Academy transcripts only")
    parser.add_argument("--catalog", type=Path, 
                       default=Path("data/metadata/khan_academy_catalog.json"),
                       help="Path to video catalog JSON (local or gs:// path)")
    parser.add_argument("--gcs-bucket", type=str, default=None,
                       help="Google Cloud Storage bucket name")
    parser.add_argument("--gcs-credentials", type=Path, default=None,
                       help="Path to GCS credentials JSON file")
    parser.add_argument("--output-dir", type=Path, default=None,
                       help="Local output directory (temporary if using GCS)")
    parser.add_argument("--max", type=int, default=None,
                       help="Maximum number of transcripts to download")
    parser.add_argument("--discover-first", action="store_true",
                       help="Discover all videos first, then download transcripts")
    
    args = parser.parse_args()
    
    # Setup GCS if configured
    gcs_storage = None
    upload_to_gcs = False
    
    if args.gcs_bucket:
        logger.info(f"Initializing GCS storage for bucket: {args.gcs_bucket}")
        from storage.gcs_storage import GCSStorage
        
        credentials_path = args.gcs_credentials
        if not credentials_path:
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path:
                credentials_path = Path(credentials_path)
        
        try:
            gcs_storage = GCSStorage(args.gcs_bucket, str(credentials_path) if credentials_path else None)
            upload_to_gcs = True
            logger.info("GCS upload enabled")
        except Exception as e:
            logger.error(f"Failed to initialize GCS: {e}")
            logger.info("Continuing with local storage only")
    
    # Discover videos if requested
    if args.discover_first:
        logger.info("Discovering all Khan Academy videos...")
        api = KhanAcademyAPI()
        all_videos = api.discover_all_videos()
        
        # Save catalog
        catalog_path = args.catalog if args.catalog.exists() else Path("/tmp/catalog.json")
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        api.save_catalog(all_videos, catalog_path)
        
        # Upload to GCS if configured
        if upload_to_gcs and gcs_storage:
            gcs_storage.upload_file(catalog_path, "metadata/khan_academy_catalog.json")
            logger.info("Uploaded catalog to GCS")
        
        args.catalog = catalog_path
    
    # Check catalog exists
    if not args.catalog.exists() and not upload_to_gcs:
        logger.error(f"Catalog file not found: {args.catalog}")
        logger.info("Run with --discover-first to create catalog, or provide valid catalog path")
        return
    
    # Download transcripts
    logger.info("Starting transcript download...")
    downloader = TranscriptDownloader(
        gcs_storage=gcs_storage,
        upload_to_gcs=upload_to_gcs,
        output_dir=args.output_dir
    )
    
    results, failed = downloader.download_from_catalog(args.catalog, max_videos=args.max)
    
    logger.info(f"Complete! Downloaded {len(results)} transcripts, {len(failed)} failed")
    
    # Process transcripts if we have them locally
    if not upload_to_gcs or args.output_dir:
        logger.info("Processing transcripts...")
        from process.process_transcripts import TranscriptProcessor
        
        processor = TranscriptProcessor(
            transcripts_dir=downloader.output_dir,
            output_dir=Path(args.output_dir or "/tmp/transcripts") / "processed",
            gcs_storage=gcs_storage,
            upload_to_gcs=upload_to_gcs
        )
        processed = processor.process_all_transcripts()
        logger.info(f"Processed {len(processed)} transcripts")


if __name__ == "__main__":
    main()
