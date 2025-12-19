"""
Khan Academy Video Downloader

Downloads all Khan Academy videos using yt-dlp (YouTube-DL successor).
Khan Academy hosts videos on YouTube, so we can download them directly.
"""

import yt_dlp
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm
import time
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.gcs_storage import GCSStorage

logger = logging.getLogger(__name__)


class VideoDownloader:
    """
    Downloads Khan Academy videos and extracts transcripts.
    """
    
    def __init__(self, output_dir: Path, download_video: bool = True, 
                 download_transcript: bool = True, gcs_storage: Optional[GCSStorage] = None,
                 upload_to_gcs: bool = False, delete_after_upload: bool = True):
        """
        Initialize the video downloader.
        
        Args:
            output_dir: Directory to save videos (temporary if uploading to GCS)
            download_video: Whether to download video files
            download_transcript: Whether to download transcripts
            gcs_storage: Optional GCS storage instance for uploading
            upload_to_gcs: Whether to upload files to GCS after download
            delete_after_upload: Whether to delete local files after successful GCS upload
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.download_video = download_video
        self.download_transcript = download_transcript
        self.gcs_storage = gcs_storage
        self.upload_to_gcs = upload_to_gcs
        self.delete_after_upload = delete_after_upload
        
        if upload_to_gcs and not gcs_storage:
            raise ValueError("gcs_storage must be provided if upload_to_gcs is True")
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(self.output_dir / '%(id)s.%(ext)s'),
            'writesubtitles': download_transcript,
            'writeautomaticsub': True,  # Get auto-generated subtitles if manual don't exist
            'subtitleslangs': ['en'],
            'subtitlesformat': 'vtt',  # WebVTT format
            'quiet': False,
            'no_warnings': False,
        }
    
    def download_single_video(self, video_url: str, video_metadata: Dict) -> Optional[Dict]:
        """
        Download a single video.
        
        Args:
            video_url: YouTube URL or Khan Academy video URL
            video_metadata: Metadata about the video
            
        Returns:
            Download result dictionary or None if failed
        """
        video_id = video_metadata.get('youtube_id') or video_metadata.get('id')
        logger.info(f"Downloading video: {video_metadata.get('title', video_id)}")
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=self.download_video)
                
                result = {
                    'video_id': video_id,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'description': info.get('description'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'file_path': None,
                    'transcript_path': None,
                    'gcs_video_path': None,
                    'gcs_transcript_path': None,
                }
                
                if self.download_video:
                    # Find the downloaded file
                    filename = ydl.prepare_filename(info)
                    local_file = Path(filename)
                    
                    if local_file.exists():
                        result['file_path'] = str(local_file)
                        
                        # Upload to GCS if configured
                        if self.upload_to_gcs and self.gcs_storage:
                            gcs_path = f"videos/{video_id}.{local_file.suffix[1:]}"
                            if self.gcs_storage.upload_file(local_file, gcs_path, 
                                                           content_type='video/mp4',
                                                           metadata={'title': result['title']}):
                                result['gcs_video_path'] = gcs_path
                                
                                # Delete local file if configured
                                if self.delete_after_upload:
                                    local_file.unlink()
                                    logger.info(f"Deleted local file after GCS upload: {local_file}")
                
                if self.download_transcript:
                    # Transcript should be in same directory with .vtt extension
                    transcript_path = Path(filename).with_suffix('.en.vtt')
                    if transcript_path.exists():
                        result['transcript_path'] = str(transcript_path)
                        
                        # Upload transcript to GCS if configured
                        if self.upload_to_gcs and self.gcs_storage:
                            gcs_transcript_path = f"transcripts/{video_id}.vtt"
                            if self.gcs_storage.upload_file(transcript_path, gcs_transcript_path,
                                                           content_type='text/vtt'):
                                result['gcs_transcript_path'] = gcs_transcript_path
                                
                                # Delete local transcript if configured
                                if self.delete_after_upload:
                                    transcript_path.unlink()
                                    logger.info(f"Deleted local transcript after GCS upload: {transcript_path}")
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to download video {video_id}: {e}")
            return None
    
    def download_from_catalog(self, catalog_path: Path, max_videos: Optional[int] = None):
        """
        Download all videos from a catalog file.
        
        Args:
            catalog_path: Path to JSON catalog file
            max_videos: Maximum number of videos to download (None for all)
        """
        logger.info(f"Loading catalog from {catalog_path}")
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        
        if not isinstance(catalog, list):
            catalog = [catalog]
        
        if max_videos:
            catalog = catalog[:max_videos]
        
        results = []
        failed = []
        
        logger.info(f"Starting download of {len(catalog)} videos...")
        
        for video_meta in tqdm(catalog, desc="Downloading videos"):
            # Extract YouTube URL from video metadata
            youtube_id = video_meta.get('youtube_id') or video_meta.get('id')
            if not youtube_id:
                logger.warning(f"No YouTube ID found for video: {video_meta}")
                failed.append(video_meta)
                continue
            
            video_url = f"https://www.youtube.com/watch?v={youtube_id}"
            result = self.download_single_video(video_url, video_meta)
            
            if result:
                results.append(result)
            else:
                failed.append(video_meta)
            
            # Rate limiting
            time.sleep(1)
        
        # Save download results
        results_path = self.output_dir / "download_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump({
                'successful': results,
                'failed': failed,
                'total': len(catalog),
                'success_count': len(results),
                'failed_count': len(failed)
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Download complete: {len(results)} successful, {len(failed)} failed")
        return results, failed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Khan Academy videos")
    parser.add_argument("--catalog", type=Path, required=True, help="Path to video catalog JSON")
    parser.add_argument("--output", type=Path, default=Path("data/videos"), help="Output directory")
    parser.add_argument("--max", type=int, default=None, help="Maximum number of videos to download")
    parser.add_argument("--no-video", action="store_true", help="Don't download video files, only transcripts")
    parser.add_argument("--no-transcript", action="store_true", help="Don't download transcripts")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    downloader = VideoDownloader(
        output_dir=args.output,
        download_video=not args.no_video,
        download_transcript=not args.no_transcript
    )
    
    downloader.download_from_catalog(args.catalog, max_videos=args.max)
