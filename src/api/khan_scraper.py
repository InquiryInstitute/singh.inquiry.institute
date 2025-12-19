"""
Web scraper for Khan Academy videos.

Since the API has been removed, we scrape the website to discover videos.
"""

import requests
from bs4 import BeautifulSoup
import re
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class KhanAcademyScraper:
    """
    Scrapes Khan Academy website to discover videos and extract YouTube IDs.
    """
    
    BASE_URL = "https://www.khanacademy.org"
    
    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Initialize scraper.
        
        Args:
            rate_limit_delay: Delay between requests in seconds
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.rate_limit_delay = rate_limit_delay
    
    def extract_youtube_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats.
        
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def scrape_video_page(self, video_url: str) -> Optional[Dict]:
        """
        Scrape a Khan Academy video page to extract metadata.
        
        Args:
            video_url: URL to Khan Academy video page
        
        Returns:
            Dictionary with video metadata or None
        """
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(video_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract YouTube ID from page
            youtube_id = None
            
            # Try to find YouTube iframe or embed
            iframe = soup.find('iframe', {'src': re.compile(r'youtube\.com')})
            if iframe:
                youtube_id = self.extract_youtube_id_from_url(iframe.get('src', ''))
            
            # Try to find in script tags (Khan Academy embeds YouTube)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    match = re.search(r'youtube\.com[^"\' ]*v=([a-zA-Z0-9_-]{11})', script.string)
                    if match:
                        youtube_id = match.group(1)
                        break
            
            if not youtube_id:
                logger.warning(f"Could not extract YouTube ID from {video_url}")
                return None
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
                # Remove " | Khan Academy" suffix
                title = re.sub(r'\s*\|\s*Khan Academy\s*$', '', title)
            
            # Extract description
            description = None
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '').strip()
            
            # Extract topic/subject from URL or breadcrumbs
            parsed_url = urlparse(video_url)
            path_parts = [p for p in parsed_url.path.split('/') if p]
            
            topic = None
            subject = None
            course = None
            
            # Khan Academy URLs typically: /subject/course/topic/video-slug
            if len(path_parts) >= 2:
                subject = path_parts[0]
            if len(path_parts) >= 3:
                course = path_parts[1]
            if len(path_parts) >= 4:
                topic = path_parts[2]
            
            return {
                'youtube_id': youtube_id,
                'title': title,
                'description': description,
                'url': video_url,
                'khan_subject': subject,
                'khan_course': course,
                'khan_topic': topic,
            }
        except Exception as e:
            logger.error(f"Failed to scrape video page {video_url}: {e}")
            return None
    
    def discover_videos_from_topic(self, topic_url: str, max_videos: Optional[int] = None) -> List[Dict]:
        """
        Discover videos from a Khan Academy topic/course page.
        
        Args:
            topic_url: URL to topic or course page
            max_videos: Maximum number of videos to discover
        
        Returns:
            List of video metadata dictionaries
        """
        videos = []
        
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(topic_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all video links
            # Khan Academy video links typically have specific patterns
            video_links = []
            
            # Look for links to video pages
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                # Khan Academy video URLs typically contain specific patterns
                if '/v/' in href or '/video/' in href:
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in video_links:
                        video_links.append(full_url)
            
            logger.info(f"Found {len(video_links)} video links on {topic_url}")
            
            # Scrape each video page
            for video_url in video_links[:max_videos] if max_videos else video_links:
                video_data = self.scrape_video_page(video_url)
                if video_data:
                    videos.append(video_data)
                time.sleep(self.rate_limit_delay)
            
        except Exception as e:
            logger.error(f"Failed to discover videos from {topic_url}: {e}")
        
        return videos
    
    def discover_from_sitemap(self) -> List[str]:
        """
        Try to discover video URLs from sitemap (if available).
        
        Returns:
            List of video URLs
        """
        sitemap_urls = [
            f"{self.BASE_URL}/sitemap.xml",
            f"{self.BASE_URL}/sitemap_index.xml",
        ]
        
        video_urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                time.sleep(self.rate_limit_delay)
                response = self.session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'xml')
                    # Find all video URLs
                    for loc in soup.find_all('loc'):
                        url = loc.get_text()
                        if '/v/' in url or '/video/' in url:
                            video_urls.append(url)
                    break
            except Exception as e:
                logger.debug(f"Could not fetch sitemap {sitemap_url}: {e}")
        
        return video_urls
    
    def discover_from_search(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Discover videos using Khan Academy search (if available).
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of video metadata dictionaries
        """
        # This would require reverse-engineering Khan Academy's search API
        # For now, return empty list
        logger.warning("Search-based discovery not yet implemented")
        return []
