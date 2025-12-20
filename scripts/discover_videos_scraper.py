#!/usr/bin/env python3
"""
Discover Khan Academy videos using web scraping.

Since the API has been removed, this script scrapes the website to find videos.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api.khan_scraper import KhanAcademyScraper
import logging
import argparse
import json
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Discover Khan Academy videos via web scraping")
    parser.add_argument("--topic-url", type=str,
                       help="Khan Academy topic/course URL to scrape")
    parser.add_argument("--output", type=Path,
                       default=Path("data/metadata/khan_academy_catalog.json"),
                       help="Output path for catalog")
    parser.add_argument("--max-videos", type=int, default=None,
                       help="Maximum number of videos to discover")
    parser.add_argument("--rate-limit", type=float, default=1.0,
                       help="Delay between requests in seconds")
    
    args = parser.parse_args()
    
    scraper = KhanAcademyScraper(rate_limit_delay=args.rate_limit)
    
    if args.topic_url:
        # Scrape specific topic
        logger.info(f"Discovering videos from: {args.topic_url}")
        videos = scraper.discover_videos_from_topic(args.topic_url, max_videos=args.max_videos)
        
        logger.info(f"Found {len(videos)} videos")
        
        # Save catalog
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved catalog to: {args.output}")
    else:
        # Try sitemap
        logger.info("Attempting to discover videos from sitemap...")
        video_urls = scraper.discover_from_sitemap()
        
        if video_urls:
            logger.info(f"Found {len(video_urls)} video URLs in sitemap")
            logger.info("Scraping video pages...")
            
            videos = []
            for url in tqdm(video_urls[:args.max_videos] if args.max_videos else video_urls):
                video_data = scraper.scrape_video_page(url)
                if video_data:
                    videos.append(video_data)
            
            logger.info(f"Successfully scraped {len(videos)} videos")
            
            # Save catalog
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved catalog to: {args.output}")
        else:
            logger.warning("No videos found. Try providing --topic-url")
            logger.info("Example: --topic-url https://www.khanacademy.org/math/algebra")


if __name__ == "__main__":
    main()
