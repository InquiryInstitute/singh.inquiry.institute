#!/usr/bin/env python3
"""
Download transcripts from Kolibri for Khan Academy videos.

Downloads transcripts and converts them to dialogic format.
"""

import sys
import json
from pathlib import Path
import argparse
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api.kolibri_client import KolibriClient
from process.process_transcripts import TranscriptProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_transcripts_from_kolibri(
    kolibri_url: str = "http://localhost:8080",
    output_dir: Path = None,
    max_videos: int = None,
    subject: str = None
):
    """
    Download transcripts from Kolibri for Khan Academy videos.
    
    Args:
        kolibri_url: Kolibri server URL
        output_dir: Directory to save transcripts
        max_videos: Maximum number of videos to process
        subject: Optional subject filter
    """
    client = KolibriClient(kolibri_url)
    
    if not client.test_connection():
        logger.error(f"Cannot connect to Kolibri at {kolibri_url}")
        return
    
    # Get Khan Academy channel
    ka_channel = client.get_khan_academy_channel()
    if not ka_channel:
        logger.error("Khan Academy channel not found")
        return
    
    # Get videos
    videos = client.get_content_nodes(ka_channel['id'], kind='video')
    
    if subject:
        videos = [v for v in videos if subject.lower() in v.get('title', '').lower()]
    
    if max_videos:
        videos = videos[:max_videos]
    
    logger.info(f"Processing {len(videos)} videos...")
    
    # Setup output directories
    if output_dir is None:
        output_dir = Path('data/transcripts')
    output_dir = Path(output_dir)
    raw_dir = output_dir / 'raw'
    processed_dir = output_dir / 'processed'
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each video
    successful = 0
    failed = 0
    
    for i, video in enumerate(videos, 1):
        video_id = video['id']
        title = video.get('title', 'Unknown')
        
        logger.info(f"[{i}/{len(videos)}] Processing: {title}")
        
        try:
            # Get transcript
            transcript_text = client.get_transcript(video_id)
            
            if not transcript_text:
                logger.warning(f"  No transcript available for {title}")
                failed += 1
                continue
            
            # Save raw transcript (VTT format if available, or plain text)
            transcript_path = raw_dir / f"{video_id}.vtt"
            if not transcript_text.strip().startswith('WEBVTT'):
                # If not VTT, try to get VTT file from files
                files = client.get_content_files(video_id)
                for file_info in files:
                    preset = file_info.get('preset', '').lower()
                    if 'subtitle' in preset or 'vtt' in preset:
                        file_url = file_info.get('storage_url') or file_info.get('url')
                        if file_url and client.download_file(file_url, transcript_path):
                            break
                else:
                    # Save as plain text if no VTT found
                    transcript_path = raw_dir / f"{video_id}.txt"
                    transcript_path.write_text(transcript_text)
            else:
                transcript_path.write_text(transcript_text)
            
            # Process to dialogic format
            processor = TranscriptProcessor(raw_dir, processed_dir)
            result = processor.process_transcript(transcript_path, {
                'title': title,
                'id': video_id,
                'source': 'kolibri'
            })
            
            # Convert to dialogic format
            from scripts.vtt_to_dialogic import vtt_to_dialogic
            dialogic_path = processed_dir / f"{video_id}_dialogic_transcript.json"
            vtt_to_dialogic(transcript_path, dialogic_path, video_id, title)
            
            logger.info(f"  ✅ Processed: {dialogic_path}")
            successful += 1
            
        except Exception as e:
            logger.error(f"  ❌ Failed to process {title}: {e}")
            failed += 1
    
    logger.info(f"\n✅ Completed: {successful} successful, {failed} failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download transcripts from Kolibri')
    parser.add_argument('--kolibri-url', default='http://localhost:8080',
                       help='Kolibri server URL')
    parser.add_argument('--output-dir', type=Path, default=Path('data/transcripts'),
                       help='Output directory')
    parser.add_argument('--max', type=int, default=None,
                       help='Maximum number of videos to process')
    parser.add_argument('--subject', type=str, default=None,
                       help='Filter by subject (e.g., "algebra", "geometry")')
    
    args = parser.parse_args()
    
    download_transcripts_from_kolibri(
        args.kolibri_url,
        args.output_dir,
        args.max,
        args.subject
    )
