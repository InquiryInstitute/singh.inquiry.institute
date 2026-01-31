#!/usr/bin/env python3
"""
Discover Khan Academy content from Kolibri.

Lists available channels, content nodes, and generates course metadata.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api.kolibri_client import KolibriClient
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def discover_khan_academy_content(kolibri_url: str = "http://localhost:8080", 
                                  output_dir: Path = None) -> List[Dict]:
    """
    Discover all Khan Academy content from Kolibri.
    
    Args:
        kolibri_url: Kolibri server URL
        output_dir: Directory to save metadata
        
    Returns:
        List of course/video metadata dictionaries
    """
    client = KolibriClient(kolibri_url)
    
    # Test connection
    if not client.test_connection():
        logger.error(f"Cannot connect to Kolibri at {kolibri_url}")
        logger.info("Make sure Kolibri is running: kolibri start")
        return []
    
    logger.info(f"Connected to Kolibri at {kolibri_url}")
    
    # Get Khan Academy channel
    ka_channel = client.get_khan_academy_channel()
    if not ka_channel:
        logger.error("Khan Academy channel not found in Kolibri")
        logger.info("Available channels:")
        for channel in client.get_channels():
            logger.info(f"  - {channel.get('name')} (ID: {channel.get('id')})")
        return []
    
    logger.info(f"Found Khan Academy channel: {ka_channel.get('name')} (ID: {ka_channel.get('id')})")
    
    # Get all video content nodes
    logger.info("Discovering video content...")
    videos = client.get_content_nodes(ka_channel['id'], kind='video')
    logger.info(f"Found {len(videos)} videos")
    
    # Organize by topic/subject
    courses = {}
    
    for video in videos:
        # Get full details
        details = client.get_content_node_details(video['id'])
        if not details:
            continue
        
        # Extract topic/subject from path or tags
        topic = details.get('parent', {}).get('title', 'Uncategorized')
        subject = topic.split('/')[0] if '/' in topic else topic
        
        if subject not in courses:
            courses[subject] = {
                'subject': subject,
                'videos': []
            }
        
        # Get file URLs
        files = client.get_content_files(video['id'])
        video_url = None
        transcript_url = None
        
        for file_info in files:
            preset = file_info.get('preset', '').lower()
            if preset == 'high_res_video' or preset == 'video':
                video_url = file_info.get('storage_url') or file_info.get('url')
            elif 'subtitle' in preset or 'transcript' in preset:
                transcript_url = file_info.get('storage_url') or file_info.get('url')
        
        video_metadata = {
            'id': video['id'],
            'title': details.get('title', 'Untitled'),
            'description': details.get('description', ''),
            'duration': details.get('duration', 0),
            'kind': details.get('kind', 'video'),
            'video_url': video_url,
            'transcript_url': transcript_url,
            'topic': topic,
            'tags': details.get('tags', []),
            'thumbnail': details.get('thumbnail', ''),
        }
        
        courses[subject]['videos'].append(video_metadata)
    
    # Save metadata
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save full catalog
        catalog_path = output_dir / 'kolibri_khan_academy_catalog.json'
        with open(catalog_path, 'w') as f:
            json.dump(list(courses.values()), f, indent=2)
        logger.info(f"Saved catalog to {catalog_path}")
        
        # Save per-subject
        for subject, course_data in courses.items():
            subject_path = output_dir / f"{subject.replace(' ', '_').lower()}_catalog.json"
            with open(subject_path, 'w') as f:
                json.dump(course_data, f, indent=2)
    
    return list(courses.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discover Khan Academy content from Kolibri')
    parser.add_argument('--kolibri-url', default='http://localhost:8080',
                       help='Kolibri server URL (default: http://localhost:8080)')
    parser.add_argument('--output-dir', type=Path, default=Path('data/metadata'),
                       help='Output directory for metadata (default: data/metadata)')
    
    args = parser.parse_args()
    
    courses = discover_khan_academy_content(args.kolibri_url, args.output_dir)
    
    if courses:
        print(f"\n✅ Discovered {len(courses)} subjects/courses")
        total_videos = sum(len(c['videos']) for c in courses)
        print(f"   Total videos: {total_videos}")
        print(f"\nSubjects:")
        for course in courses:
            print(f"  - {course['subject']}: {len(course['videos'])} videos")
