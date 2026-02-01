#!/usr/bin/env python3
"""
Complete workflow for downloading Khan Academy content from Kolibri.

This script:
1. Finds Kolibri server
2. Discovers available content
3. Downloads transcripts
4. Processes to dialogic format
5. Updates course metadata
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from api.kolibri_client import KolibriClient
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def find_kolibri_url():
    """Try to find Kolibri server."""
    common_urls = [
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8080",
    ]
    
    for url in common_urls:
        try:
            client = KolibriClient(url)
            if client.test_connection():
                return url
        except:
            continue
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Complete workflow for Kolibri Khan Academy content'
    )
    parser.add_argument('--kolibri-url', default=None,
                       help='Kolibri server URL (auto-detected if not provided)')
    parser.add_argument('--discover-only', action='store_true',
                       help='Only discover content, don\'t download')
    parser.add_argument('--max-videos', type=int, default=10,
                       help='Maximum number of videos to download (default: 10)')
    parser.add_argument('--subject', type=str, default=None,
                       help='Filter by subject (e.g., "algebra")')
    parser.add_argument('--output-dir', type=Path, default=Path('data'),
                       help='Output directory (default: data)')
    
    args = parser.parse_args()
    
    # Find Kolibri URL
    if not args.kolibri_url:
        logger.info("🔍 Auto-detecting Kolibri server...")
        args.kolibri_url = find_kolibri_url()
        
        if not args.kolibri_url:
            logger.error("❌ Could not find Kolibri server")
            logger.info("Please specify URL: --kolibri-url http://your-url:port")
            logger.info("Or start Kolibri: kolibri start")
            return 1
    
    logger.info(f"✅ Using Kolibri at: {args.kolibri_url}")
    
    # Test connection
    client = KolibriClient(args.kolibri_url)
    if not client.test_connection():
        logger.error(f"❌ Cannot connect to Kolibri at {args.kolibri_url}")
        return 1
    
    # Get Khan Academy channel
    ka_channel = client.get_khan_academy_channel()
    if not ka_channel:
        logger.error("❌ Khan Academy channel not found")
        channels = client.get_channels()
        logger.info(f"Available channels ({len(channels)}):")
        for ch in channels:
            logger.info(f"  - {ch.get('name')} (ID: {ch.get('id')})")
        return 1
    
    logger.info(f"✅ Found Khan Academy channel: {ka_channel.get('name')}")
    
    # Discover content
    logger.info("📚 Discovering content...")
    videos = client.get_content_nodes(ka_channel['id'], kind='video')
    logger.info(f"   Found {len(videos)} videos")
    
    if args.subject:
        videos = [v for v in videos if args.subject.lower() in v.get('title', '').lower()]
        logger.info(f"   Filtered to {len(videos)} videos matching '{args.subject}'")
    
    if args.discover_only:
        # Just list what's available
        logger.info("\n📹 Sample videos:")
        for i, video in enumerate(videos[:20], 1):
            details = client.get_content_node_details(video['id'])
            title = details.get('title', 'Unknown') if details else 'Unknown'
            files = client.get_content_files(video['id'])
            has_transcript = any('subtitle' in f.get('preset', '').lower() 
                               for f in files)
            logger.info(f"   {i}. {title} {'✅' if has_transcript else '❌'}")
        return 0
    
    # Download transcripts
    if not videos:
        logger.warning("No videos to download")
        return 0
    
    videos_to_download = videos[:args.max_videos]
    logger.info(f"\n📥 Downloading transcripts for {len(videos_to_download)} videos...")
    
    # Download transcripts
    output_dir = args.output_dir / 'transcripts'
    raw_dir = output_dir / 'raw'
    processed_dir = output_dir / 'processed'
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    successful = 0
    failed = 0
    
    for i, video in enumerate(videos_to_download, 1):
        video_id = video['id']
        title = video.get('title', 'Unknown')
        
        logger.info(f"[{i}/{len(videos_to_download)}] {title}")
        
        try:
            # Get transcript
            transcript_text = client.get_transcript(video_id)
            
            if not transcript_text:
                logger.warning(f"  No transcript available")
                failed += 1
                continue
            
            # Save transcript
            transcript_path = raw_dir / f"{video_id}.vtt"
            if not transcript_text.strip().startswith('WEBVTT'):
                # Try to get VTT file from files
                files = client.get_content_files(video_id)
                for file_info in files:
                    preset = file_info.get('preset', '').lower()
                    if 'subtitle' in preset or 'vtt' in preset:
                        file_url = file_info.get('storage_url') or file_info.get('url')
                        if file_url and client.download_file(file_url, transcript_path):
                            break
                else:
                    transcript_path = raw_dir / f"{video_id}.txt"
                    transcript_path.write_text(transcript_text)
            else:
                transcript_path.write_text(transcript_text)
            
            # Convert to dialogic format
            try:
                import subprocess
                dialogic_path = processed_dir / f"{video_id}_dialogic_transcript.json"
                result = subprocess.run(
                    ['python3', 'scripts/vtt-to-dialogic.py', 
                     str(transcript_path), str(dialogic_path), video_id, title],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    logger.info(f"  ✅ Processed")
                    successful += 1
                else:
                    logger.warning(f"  ⚠️  Conversion failed")
                    failed += 1
            except Exception as e:
                logger.warning(f"  ⚠️  Could not convert: {e}")
                failed += 1
                
        except Exception as e:
            logger.error(f"  ❌ Error: {e}")
            failed += 1
    
    logger.info(f"\n📊 Results: {successful} successful, {failed} failed")
    
    logger.info("\n✅ Workflow complete!")
    logger.info(f"   Transcripts saved to: {args.output_dir / 'transcripts'}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
