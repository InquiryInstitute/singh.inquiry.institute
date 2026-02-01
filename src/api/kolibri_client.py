"""
Kolibri API Client

Client for interacting with Kolibri server to discover and download
Khan Academy content, transcripts, and metadata.
"""

import requests
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class KolibriClient:
    """
    Client for Kolibri API.
    
    Kolibri provides a REST API for accessing downloaded educational content,
    including Khan Academy videos, transcripts, and metadata.
    """
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize Kolibri client.
        
        Args:
            base_url: Base URL of Kolibri server (default: http://localhost:8080)
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
        })
    
    def test_connection(self) -> bool:
        """Test if Kolibri server is accessible."""
        try:
            # Try with longer timeout and handle redirects
            response = self.session.get(f"{self.api_url}/content/channel", timeout=10, allow_redirects=True)
            # Accept 200 or 301/302 (redirects)
            return response.status_code in [200, 301, 302] or (response.status_code == 404 and 'api' in response.url)
        except requests.exceptions.Timeout:
            logger.error(f"Connection to Kolibri timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Kolibri: {e}")
            return False
    
    def get_channels(self) -> List[Dict]:
        """
        Get list of available channels (content sources).
        
        Returns:
            List of channel dictionaries with id, name, etc.
        """
        try:
            response = self.session.get(f"{self.api_url}/content/channel")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get channels: {e}")
            return []
    
    def get_khan_academy_channel(self) -> Optional[Dict]:
        """
        Get Khan Academy channel if available.
        
        Returns:
            Channel dictionary or None
        """
        channels = self.get_channels()
        for channel in channels:
            # Khan Academy channel typically has "khan" in name or id
            name = channel.get('name', '').lower()
            channel_id = channel.get('id', '').lower()
            if 'khan' in name or 'khan' in channel_id:
                return channel
        return None
    
    def get_content_nodes(self, channel_id: str, kind: str = "video", 
                         parent_id: Optional[str] = None) -> List[Dict]:
        """
        Get content nodes (videos, exercises, etc.) for a channel.
        
        Args:
            channel_id: Channel ID
            kind: Content kind filter (video, exercise, document, etc.)
            parent_id: Optional parent node ID to get children
            
        Returns:
            List of content node dictionaries
        """
        try:
            params = {
                'channel_id': channel_id,
                'kind': kind,
            }
            if parent_id:
                params['parent'] = parent_id
            
            response = self.session.get(f"{self.api_url}/content/contentnode", params=params)
            response.raise_for_status()
            results = response.json()
            
            # Handle pagination if needed
            if isinstance(results, dict) and 'results' in results:
                return results['results']
            return results if isinstance(results, list) else []
        except Exception as e:
            logger.error(f"Failed to get content nodes: {e}")
            return []
    
    def get_content_node_details(self, content_id: str) -> Optional[Dict]:
        """
        Get detailed information about a content node.
        
        Args:
            content_id: Content node ID
            
        Returns:
            Content node dictionary with full details
        """
        try:
            response = self.session.get(f"{self.api_url}/content/contentnode/{content_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get content node details: {e}")
            return None
    
    def get_content_files(self, content_id: str) -> List[Dict]:
        """
        Get file URLs for a content node (video, transcript, etc.).
        
        Args:
            content_id: Content node ID
            
        Returns:
            List of file dictionaries with URLs and metadata
        """
        try:
            params = {'contentnode_id': content_id}
            response = self.session.get(f"{self.api_url}/content/file", params=params)
            response.raise_for_status()
            results = response.json()
            
            if isinstance(results, dict) and 'results' in results:
                return results['results']
            return results if isinstance(results, list) else []
        except Exception as e:
            logger.error(f"Failed to get content files: {e}")
            return []
    
    def get_transcript(self, content_id: str) -> Optional[str]:
        """
        Get transcript for a video content node.
        
        Args:
            content_id: Content node ID
            
        Returns:
            Transcript text or None
        """
        try:
            # Try transcript endpoint
            response = self.session.get(
                f"{self.api_url}/content/contentnode/{content_id}/transcript",
                timeout=10
            )
            if response.status_code == 200:
                return response.text
            
            # Fallback: check files for subtitle/transcript files
            files = self.get_content_files(content_id)
            for file_info in files:
                file_name = file_info.get('preset', '').lower()
                if 'subtitle' in file_name or 'transcript' in file_name:
                    file_url = file_info.get('storage_url') or file_info.get('url')
                    if file_url:
                        file_response = self.session.get(file_url)
                        if file_response.status_code == 200:
                            return file_response.text
            
            return None
        except Exception as e:
            logger.error(f"Failed to get transcript: {e}")
            return None
    
    def download_file(self, file_url: str, output_path: Path) -> bool:
        """
        Download a file from Kolibri.
        
        Args:
            file_url: URL of file to download
            output_path: Local path to save file
            
        Returns:
            True if successful
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            response = self.session.get(file_url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded file to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return False
    
    def search_content(self, channel_id: str, search_term: str, 
                      kind: Optional[str] = None) -> List[Dict]:
        """
        Search for content in a channel.
        
        Args:
            channel_id: Channel ID
            search_term: Search query
            kind: Optional content kind filter
            
        Returns:
            List of matching content nodes
        """
        try:
            params = {
                'channel_id': channel_id,
                'search': search_term,
            }
            if kind:
                params['kind'] = kind
            
            response = self.session.get(f"{self.api_url}/content/contentnode", params=params)
            response.raise_for_status()
            results = response.json()
            
            if isinstance(results, dict) and 'results' in results:
                return results['results']
            return results if isinstance(results, list) else []
        except Exception as e:
            logger.error(f"Failed to search content: {e}")
            return []
