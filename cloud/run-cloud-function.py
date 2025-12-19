#!/usr/bin/env python3
"""
Cloud Function entry point for Khan Academy downloader.

This can be deployed as a Cloud Function or used as an HTTP endpoint
for Cloud Run/Cloud Scheduler.
"""

import os
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from download.download_videos import VideoDownloader
from storage.gcs_storage import GCSStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def discover_and_download(request):
    """
    Cloud Function entry point.
    
    Expected request format:
    {
        "command": "discover_and_download" | "download_only" | "transcripts_only",
        "catalog_path": "metadata/khan_academy_catalog.json",  # Optional
        "max_videos": 100,  # Optional
        "gcs_bucket": "khan-academy-videos"  # Optional, uses env var if not provided
    }
    """
    try:
        # Parse request
        if isinstance(request, str):
            request_data = json.loads(request)
        else:
            request_data = request.get_json() or {}
        
        command = request_data.get('command', 'discover_and_download')
        max_videos = request_data.get('max_videos')
        catalog_path = request_data.get('catalog_path', 'metadata/khan_academy_catalog.json')
        bucket_name = request_data.get('gcs_bucket') or os.environ.get('GCS_BUCKET', 'khan-academy-videos')
        
        logger.info(f"Received command: {command}")
        logger.info(f"Bucket: {bucket_name}, Max videos: {max_videos}")
        
        # Initialize GCS storage
        gcs = GCSStorage(bucket_name)
        
        # Create temporary local directory
        temp_dir = Path('/tmp/khan-downloader')
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Handle transcript-only mode
        if command == 'transcripts_only':
            logger.info("Starting transcript-only download...")
            
            # Use yt-dlp directly for transcript-only download
            import yt_dlp
            
            # Download catalog from GCS if needed
            local_catalog = temp_dir / "catalog.json"
            if not local_catalog.exists():
                gcs.download_file(catalog_path, local_catalog)
            
            with open(local_catalog, 'r') as f:
                catalog = json.load(f)
            
            if not isinstance(catalog, list):
                catalog = [catalog]
            
            if max_videos:
                catalog = catalog[:max_videos]
            
            results = []
            failed = []
            transcripts_dir = temp_dir / "transcripts"
            transcripts_dir.mkdir(parents=True, exist_ok=True)
            
            for video_meta in catalog:
                youtube_id = video_meta.get('youtube_id') or video_meta.get('id')
                if not youtube_id:
                    failed.append(video_meta)
                    continue
                
                video_url = f"https://www.youtube.com/watch?v={youtube_id}"
                ydl_opts = {
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['en'],
                    'subtitlesformat': 'vtt',
                    'skip_download': True,
                    'outtmpl': str(transcripts_dir / f'{youtube_id}.%(ext)s'),
                    'quiet': True,
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    
                    transcript_path = transcripts_dir / f"{youtube_id}.en.vtt"
                    if not transcript_path.exists():
                        transcript_path = transcripts_dir / f"{youtube_id}.vtt"
                    
                    if transcript_path.exists():
                        # Upload to GCS
                        gcs_path = f"transcripts/{youtube_id}.vtt"
                        gcs.upload_file(transcript_path, gcs_path, content_type='text/vtt')
                        transcript_path.unlink()  # Delete local
                        results.append({'video_id': youtube_id, 'success': True})
                    else:
                        failed.append(video_meta)
                except Exception as e:
                    logger.error(f"Failed {youtube_id}: {e}")
                    failed.append(video_meta)
            
            # Process transcripts
            from process.process_transcripts import TranscriptProcessor
            processor = TranscriptProcessor(
                transcripts_dir=transcripts_dir,
                output_dir=temp_dir / "processed",
                gcs_storage=gcs,
                upload_to_gcs=True
            )
            # Note: Transcripts are already in GCS, so processing would need to download them back
            # For now, just return results
            
            summary = {
                'successful': len(results),
                'failed': len(failed),
                'total': len(catalog)
            }
            gcs.upload_json(summary, 'metadata/transcript_download_results.json')
            
            return {
                'status': 'success',
                'message': f'Downloaded {len(results)} transcripts',
                'results': summary
            }, 200
        
        if command == 'discover_and_download':
            # Discover videos first
            logger.info("Discovering videos...")
            from api.khan_academy_api import KhanAcademyAPI
            
            api = KhanAcademyAPI()
            all_videos = api.discover_all_videos()
            
            # Save catalog locally
            local_catalog = temp_dir / "catalog.json"
            api.save_catalog(all_videos, local_catalog)
            
            # Upload catalog to GCS
            gcs.upload_file(local_catalog, catalog_path)
            logger.info(f"Uploaded catalog to gs://{bucket_name}/{catalog_path}")
        
        # Download videos
        logger.info("Starting video download...")
        
        # Download catalog from GCS if needed
        local_catalog = temp_dir / "catalog.json"
        if not local_catalog.exists():
            gcs.download_file(catalog_path, local_catalog)
        
        # Initialize downloader
        downloader = VideoDownloader(
            output_dir=temp_dir / "videos",
            download_video=True,
            download_transcript=True,
            gcs_storage=gcs,
            upload_to_gcs=True,
            delete_after_upload=True
        )
        
        # Download videos
        results, failed = downloader.download_from_catalog(local_catalog, max_videos=max_videos)
        
        # Upload results summary
        summary = {
            'successful': len(results),
            'failed': len(failed),
            'total': len(results) + len(failed),
            'timestamp': str(Path().cwd())
        }
        gcs.upload_json(summary, 'metadata/download_results.json')
        
        return {
            'status': 'success',
            'message': f'Downloaded {len(results)} videos, {len(failed)} failed',
            'results': summary
        }, 200
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e)
        }, 500


# For Cloud Run / HTTP
if __name__ == "__main__":
    from flask import Flask, request
    
    app = Flask(__name__)
    
    @app.route('/run', methods=['POST'])
    def run_endpoint():
        result, status_code = discover_and_download(request)
        return json.dumps(result), status_code, {'Content-Type': 'application/json'}
    
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'healthy'}, 200
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
