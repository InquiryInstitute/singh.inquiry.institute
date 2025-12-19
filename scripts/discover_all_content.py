#!/usr/bin/env python3
"""
Main script to discover all Khan Academy content.

This script:
1. Discovers all topics and videos from Khan Academy
2. Saves a comprehensive catalog
3. Can optionally start downloading videos and transcripts
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api.khan_academy_api import KhanAcademyAPI
import logging
import argparse
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Discover all Khan Academy content")
    parser.add_argument("--output", type=Path, default=Path("data/metadata/khan_academy_catalog.json"),
                       help="Output path for catalog")
    parser.add_argument("--rate-limit", type=float, default=0.5,
                       help="Delay between API requests in seconds")
    
    args = parser.parse_args()
    
    logger.info("Starting Khan Academy content discovery...")
    
    # Initialize API client
    api = KhanAcademyAPI(rate_limit_delay=args.rate_limit)
    
    # Discover all videos
    logger.info("Discovering all videos...")
    all_videos = api.discover_all_videos()
    
    # Save catalog
    logger.info(f"Saving catalog with {len(all_videos)} videos...")
    api.save_catalog(all_videos, args.output)
    
    # Print summary
    print("\n" + "="*60)
    print(f"Discovery Complete!")
    print(f"Total videos found: {len(all_videos)}")
    print(f"Catalog saved to: {args.output}")
    print("="*60)
    
    # Group by topic/subject
    topics = {}
    for video in all_videos:
        topic = video.get('topic', {}).get('title', 'Unknown')
        if topic not in topics:
            topics[topic] = 0
        topics[topic] += 1
    
    print("\nVideos by topic:")
    for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
        print(f"  {topic}: {count} videos")


if __name__ == "__main__":
    main()
