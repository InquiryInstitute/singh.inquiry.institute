"""
Google Cloud Storage utilities for storing videos and transcripts.
"""

import os
import logging
from pathlib import Path
from typing import Optional, BinaryIO, Union
from google.cloud import storage
from google.cloud.exceptions import NotFound
import json

logger = logging.getLogger(__name__)


class GCSStorage:
    """
    Handles uploads and operations with Google Cloud Storage buckets.
    """
    
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        """
        Initialize GCS client.
        
        Args:
            bucket_name: Name of the GCS bucket
            credentials_path: Path to GCS credentials JSON file (optional, can use env var)
        """
        self.bucket_name = bucket_name
        
        # Initialize client with credentials if provided
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(bucket_name)
            logger.info(f"Initialized GCS client for bucket: {bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise
    
    def upload_file(self, local_path: Union[str, Path], remote_path: str, 
                   content_type: Optional[str] = None, metadata: Optional[dict] = None) -> bool:
        """
        Upload a file to GCS.
        
        Args:
            local_path: Path to local file
            remote_path: Path in GCS bucket (e.g., 'videos/video_id.mp4')
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        local_path = Path(local_path)
        if not local_path.exists():
            logger.error(f"Local file not found: {local_path}")
            return False
        
        try:
            blob = self.bucket.blob(remote_path)
            
            # Set content type
            if content_type:
                blob.content_type = content_type
            else:
                # Auto-detect from extension
                ext = local_path.suffix.lower()
                content_types = {
                    '.mp4': 'video/mp4',
                    '.m4a': 'audio/mp4',
                    '.vtt': 'text/vtt',
                    '.json': 'application/json',
                    '.txt': 'text/plain',
                }
                blob.content_type = content_types.get(ext, 'application/octet-stream')
            
            # Set metadata
            if metadata:
                blob.metadata = metadata
            
            # Upload file
            logger.info(f"Uploading {local_path.name} to gs://{self.bucket_name}/{remote_path}")
            blob.upload_from_filename(str(local_path))
            
            logger.info(f"Successfully uploaded: {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload {local_path} to {remote_path}: {e}")
            return False
    
    def upload_string(self, content: str, remote_path: str, 
                     content_type: Optional[str] = None) -> bool:
        """
        Upload string content directly to GCS.
        
        Args:
            content: String content to upload
            remote_path: Path in GCS bucket
            content_type: MIME type
            
        Returns:
            True if successful
        """
        try:
            blob = self.bucket.blob(remote_path)
            if content_type:
                blob.content_type = content_type
            
            blob.upload_from_string(content, content_type=content_type or 'text/plain')
            logger.info(f"Uploaded string content to: {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload string to {remote_path}: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: Union[str, Path]) -> bool:
        """
        Download a file from GCS.
        
        Args:
            remote_path: Path in GCS bucket
            local_path: Local path to save file
            
        Returns:
            True if successful
        """
        try:
            blob = self.bucket.blob(remote_path)
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            blob.download_to_filename(str(local_path))
            logger.info(f"Downloaded {remote_path} to {local_path}")
            return True
        except NotFound:
            logger.error(f"File not found in GCS: {remote_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to download {remote_path}: {e}")
            return False
    
    def file_exists(self, remote_path: str) -> bool:
        """
        Check if a file exists in GCS.
        
        Args:
            remote_path: Path in GCS bucket
            
        Returns:
            True if file exists
        """
        try:
            blob = self.bucket.blob(remote_path)
            return blob.exists()
        except Exception as e:
            logger.error(f"Error checking file existence: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """
        List files in bucket with optional prefix.
        
        Args:
            prefix: Prefix to filter files (e.g., 'videos/')
            
        Returns:
            List of blob names
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def upload_json(self, data: dict, remote_path: str) -> bool:
        """
        Upload JSON data to GCS.
        
        Args:
            data: Dictionary to upload as JSON
            remote_path: Path in GCS bucket
            
        Returns:
            True if successful
        """
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        return self.upload_string(json_str, remote_path, content_type='application/json')
    
    def get_public_url(self, remote_path: str) -> Optional[str]:
        """
        Get public URL for a file (if bucket is public).
        
        Args:
            remote_path: Path in GCS bucket
            
        Returns:
            Public URL or None
        """
        try:
            blob = self.bucket.blob(remote_path)
            return blob.public_url
        except Exception as e:
            logger.error(f"Error getting public URL: {e}")
            return None
    
    def make_public(self, remote_path: str) -> bool:
        """
        Make a file publicly accessible.
        
        Args:
            remote_path: Path in GCS bucket
            
        Returns:
            True if successful
        """
        try:
            blob = self.bucket.blob(remote_path)
            blob.make_public()
            logger.info(f"Made {remote_path} public")
            return True
        except Exception as e:
            logger.error(f"Failed to make {remote_path} public: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Test GCS storage")
    parser.add_argument("--bucket", required=True, help="GCS bucket name")
    parser.add_argument("--credentials", help="Path to GCS credentials JSON")
    parser.add_argument("--upload", help="Local file to upload")
    parser.add_argument("--remote", help="Remote path in bucket")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    gcs = GCSStorage(args.bucket, args.credentials)
    
    if args.upload and args.remote:
        gcs.upload_file(args.upload, args.remote)
