"""
Khan Academy API Client

This module provides functionality to interact with Khan Academy's API
and discover all available courses, videos, and transcripts.
"""

import requests
import json
import time
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class KhanAcademyAPI:
    """
    Client for accessing Khan Academy content via their API and web scraping.
    
    Khan Academy doesn't have a public API, so we'll need to:
    1. Scrape their content tree from their website
    2. Use their internal API endpoints (reverse-engineered)
    3. Access YouTube for video content (KA hosts on YouTube)
    """
    
    BASE_URL = "https://www.khanacademy.org"
    API_BASE = "https://www.khanacademy.org/api/v1"
    
    def __init__(self, rate_limit_delay: float = 0.5):
        """
        Initialize the Khan Academy API client.
        
        Args:
            rate_limit_delay: Delay between requests in seconds
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.rate_limit_delay = rate_limit_delay
        self._cache = {}
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a rate-limited request to Khan Academy API.
        
        Args:
            endpoint: API endpoint (relative to API_BASE)
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.API_BASE}/{endpoint.lstrip('/')}"
        
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
    
    def get_topics(self) -> List[Dict]:
        """
        Get all top-level topics/subjects from Khan Academy.
        
        Returns:
            List of topic dictionaries
        """
        logger.info("Fetching all topics from Khan Academy...")
        try:
            # Khan Academy's topic tree endpoint
            data = self._request("topictree", params={"kind": "Topic"})
            return data.get("children", [])
        except Exception as e:
            logger.error(f"Failed to fetch topics: {e}")
            return []
    
    def get_topic_content(self, topic_slug: str) -> Dict:
        """
        Get all content for a specific topic.
        
        Args:
            topic_slug: The slug/identifier for the topic
            
        Returns:
            Topic content dictionary
        """
        logger.info(f"Fetching content for topic: {topic_slug}")
        try:
            data = self._request(f"topic/{topic_slug}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch topic content for {topic_slug}: {e}")
            return {}
    
    def get_video_info(self, video_slug: str) -> Dict:
        """
        Get detailed information about a specific video.
        
        Args:
            video_slug: The slug/identifier for the video
            
        Returns:
            Video information dictionary
        """
        logger.info(f"Fetching video info: {video_slug}")
        try:
            data = self._request(f"video/{video_slug}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch video info for {video_slug}: {e}")
            return {}
    
    def discover_all_videos(self) -> List[Dict]:
        """
        Discover all videos across all topics.
        
        This is a comprehensive crawl of Khan Academy's content tree.
        
        Returns:
            List of all video metadata dictionaries
        """
        logger.info("Starting comprehensive video discovery...")
        all_videos = []
        topics = self.get_topics()
        
        for topic in topics:
            topic_slug = topic.get("slug") or topic.get("id")
            if not topic_slug:
                continue
                
            logger.info(f"Processing topic: {topic.get('title', topic_slug)}")
            topic_content = self.get_topic_content(topic_slug)
            
            # Recursively extract videos from topic tree
            videos = self._extract_videos_from_topic(topic_content)
            all_videos.extend(videos)
            
            logger.info(f"Found {len(videos)} videos in {topic_slug}")
        
        logger.info(f"Total videos discovered: {len(all_videos)}")
        return all_videos
    
    def _extract_videos_from_topic(self, topic_data: Dict) -> List[Dict]:
        """
        Recursively extract all videos from a topic tree.
        
        Args:
            topic_data: Topic data dictionary
            
        Returns:
            List of video dictionaries
        """
        videos = []
        
        # Check if this node is a video
        if topic_data.get("kind") == "Video":
            videos.append(topic_data)
        
        # Recursively process children
        for child in topic_data.get("children", []):
            videos.extend(self._extract_videos_from_topic(child))
        
        return videos
    
    def get_video_transcript(self, video_slug: str) -> Optional[str]:
        """
        Get transcript for a video.
        
        Args:
            video_slug: The slug/identifier for the video
            
        Returns:
            Transcript text or None
        """
        logger.info(f"Fetching transcript for video: {video_slug}")
        try:
            video_info = self.get_video_info(video_slug)
            # Transcripts are typically in the video data or separate endpoint
            transcript_url = video_info.get("transcript_url")
            if transcript_url:
                response = self.session.get(transcript_url)
                return response.text
            return video_info.get("transcript")
        except Exception as e:
            logger.error(f"Failed to fetch transcript for {video_slug}: {e}")
            return None
    
    def save_catalog(self, videos: List[Dict], output_path: Path):
        """
        Save video catalog to JSON file.
        
        Args:
            videos: List of video dictionaries
            output_path: Path to save the catalog
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved catalog with {len(videos)} videos to {output_path}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    api = KhanAcademyAPI()
    
    # Discover all videos
    all_videos = api.discover_all_videos()
    
    # Save catalog
    catalog_path = Path("data/metadata/khan_academy_catalog.json")
    api.save_catalog(all_videos, catalog_path)
    
    print(f"Discovered {len(all_videos)} videos")
