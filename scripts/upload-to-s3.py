#!/usr/bin/env python3
"""
Upload processed transcripts and course metadata to S3.

Organizes content according to the S3 course storage design.
"""

import sys
import json
import boto3
from pathlib import Path
import argparse
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3CourseUploader:
    """Upload courses to S3 following the course storage design."""
    
    def __init__(self, bucket: str = 'singh-courses', region: str = 'us-east-1'):
        """
        Initialize S3 uploader.
        
        Args:
            bucket: S3 bucket name
            region: AWS region
        """
        self.bucket = bucket
        self.region = region
        self.s3_client = None
        
        try:
            self.s3_client = boto3.client('s3', region_name=region)
            # Test connection
            self.s3_client.head_bucket(Bucket=bucket)
            logger.info(f"✅ Connected to S3 bucket: {bucket}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to S3: {e}")
            logger.info("Make sure AWS credentials are configured:")
            logger.info("  aws configure")
            logger.info("  # or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
            raise
    
    def upload_file(self, local_path: Path, s3_key: str, content_type: str = None) -> bool:
        """Upload a file to S3."""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.upload_file(
                str(local_path),
                self.bucket,
                s3_key,
                ExtraArgs=extra_args
            )
            logger.info(f"  ✅ Uploaded: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"  ❌ Failed to upload {s3_key}: {e}")
            return False
    
    def upload_course(self, course_metadata_path: Path, transcripts_dir: Path) -> bool:
        """
        Upload a complete course to S3.
        
        Args:
            course_metadata_path: Path to course metadata JSON
            transcripts_dir: Directory containing processed transcripts
        """
        try:
            with open(course_metadata_path, 'r') as f:
                course_metadata = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load course metadata: {e}")
            return False
        
        course_id = course_metadata.get('class_id') or course_metadata.get('course_id')
        if not course_id:
            logger.error("Course metadata missing class_id or course_id")
            return False
        
        source = course_metadata.get('source', 'khan-academy')
        logger.info(f"📦 Uploading course: {course_id} (source: {source})")
        
        # Upload course metadata
        metadata_key = f"sources/{source}/courses/{course_id}/metadata.json"
        self.upload_file(course_metadata_path, metadata_key, 'application/json')
        
        # Upload transcripts
        transcript_files = list(transcripts_dir.glob("*_dialogic_transcript.json"))
        logger.info(f"   Found {len(transcript_files)} transcript files")
        
        for transcript_file in transcript_files:
            # Extract video ID from filename
            video_id = transcript_file.stem.replace('_dialogic_transcript', '')
            
            # Upload transcript
            transcript_key = f"sources/{source}/courses/{course_id}/videos/{video_id}/transcript_dialogic.json"
            self.upload_file(transcript_file, transcript_key, 'application/json')
        
        logger.info(f"✅ Course uploaded: {course_id}")
        return True
    
    def update_manifest(self, source: str = 'khan-academy'):
        """
        Update source manifest with available courses.
        
        Args:
            source: Source identifier (khan-academy, mit-ocw, etc.)
        """
        try:
            # List all courses in S3
            prefix = f"sources/{source}/courses/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                Delimiter='/'
            )
            
            courses = []
            for prefix_info in response.get('CommonPrefixes', []):
                course_path = prefix_info['Prefix']
                course_id = course_path.split('/')[-2]  # Get course ID from path
                
                # Try to get metadata
                metadata_key = f"{course_path}metadata.json"
                try:
                    obj = self.s3_client.get_object(Bucket=self.bucket, Key=metadata_key)
                    metadata = json.loads(obj['Body'].read())
                    courses.append({
                        'course_id': course_id,
                        'title': metadata.get('title', course_id),
                        'subject': metadata.get('subject', ''),
                        'path': course_path,
                        'metadata_path': metadata_key,
                        'video_count': len(metadata.get('videos', [])),
                    })
                except:
                    # Metadata not found, use defaults
                    courses.append({
                        'course_id': course_id,
                        'title': course_id,
                        'path': course_path,
                    })
            
            # Create/update source manifest
            manifest = {
                'source_id': source,
                'version': '1.0',
                'last_updated': Path(__file__).stat().st_mtime,  # Use file timestamp
                'courses': courses,
                'total_courses': len(courses)
            }
            
            manifest_key = f"sources/{source}/manifest.json"
            manifest_json = json.dumps(manifest, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=manifest_key,
                Body=manifest_json.encode('utf-8'),
                ContentType='application/json'
            )
            
            logger.info(f"✅ Updated manifest: {manifest_key} ({len(courses)} courses)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update manifest: {e}")
            return False


def upload_all_courses(local_data_dir: Path, bucket: str = 'singh-courses'):
    """Upload all courses from local data directory to S3."""
    uploader = S3CourseUploader(bucket)
    
    metadata_dir = local_data_dir / 'metadata'
    transcripts_dir = local_data_dir / 'transcripts' / 'processed'
    
    if not metadata_dir.exists():
        logger.error(f"Metadata directory not found: {metadata_dir}")
        return
    
    # Find all course metadata files
    course_files = list(metadata_dir.glob("*.json"))
    logger.info(f"Found {len(course_files)} course metadata files")
    
    for course_file in course_files:
        uploader.upload_course(course_file, transcripts_dir)
    
    # Update manifest
    uploader.update_manifest('khan-academy')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload courses to S3')
    parser.add_argument('--bucket', default='singh-courses',
                       help='S3 bucket name (default: singh-courses)')
    parser.add_argument('--data-dir', type=Path, default=Path('data'),
                       help='Local data directory (default: data)')
    parser.add_argument('--course', type=Path, default=None,
                       help='Upload single course metadata file')
    parser.add_argument('--update-manifest', action='store_true',
                       help='Update source manifest')
    
    args = parser.parse_args()
    
    if args.course:
        # Upload single course
        uploader = S3CourseUploader(args.bucket)
        transcripts_dir = args.data_dir / 'transcripts' / 'processed'
        uploader.upload_course(args.course, transcripts_dir)
    elif args.update_manifest:
        # Just update manifest
        uploader = S3CourseUploader(args.bucket)
        uploader.update_manifest('khan-academy')
    else:
        # Upload all courses
        upload_all_courses(args.data_dir, args.bucket)
