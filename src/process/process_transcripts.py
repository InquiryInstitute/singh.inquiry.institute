"""
Transcript Processing

Processes downloaded transcripts (WebVTT format) and converts them to
structured formats for use with aFaculty personas.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging
from webvtt import WebVTT
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.gcs_storage import GCSStorage

logger = logging.getLogger(__name__)


class TranscriptProcessor:
    """
    Processes WebVTT transcript files into structured formats.
    """
    
    def __init__(self, transcripts_dir: Path, output_dir: Path, 
                 gcs_storage: Optional[GCSStorage] = None, upload_to_gcs: bool = False):
        """
        Initialize the transcript processor.
        
        Args:
            transcripts_dir: Directory containing .vtt transcript files (or GCS bucket path)
            output_dir: Directory to save processed transcripts (temporary if uploading to GCS)
            gcs_storage: Optional GCS storage instance
            upload_to_gcs: Whether to upload processed transcripts to GCS
        """
        self.transcripts_dir = Path(transcripts_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.gcs_storage = gcs_storage
        self.upload_to_gcs = upload_to_gcs
    
    def parse_vtt(self, vtt_path: Path) -> List[Dict]:
        """
        Parse a WebVTT file into structured format.
        
        Args:
            vtt_path: Path to .vtt file
            
        Returns:
            List of transcript segments with timestamps
        """
        try:
            vtt = WebVTT().read(vtt_path)
            segments = []
            
            for caption in vtt:
                segments.append({
                    'start': caption.start,
                    'end': caption.end,
                    'text': caption.text.strip(),
                    'duration': self._calculate_duration(caption.start, caption.end)
                })
            
            return segments
        except Exception as e:
            logger.error(f"Failed to parse VTT file {vtt_path}: {e}")
            return []
    
    def _calculate_duration(self, start: str, end: str) -> float:
        """
        Calculate duration in seconds from time strings.
        
        Args:
            start: Start time string (HH:MM:SS.mmm)
            end: End time string (HH:MM:SS.mmm)
            
        Returns:
            Duration in seconds
        """
        def time_to_seconds(time_str: str) -> float:
            parts = time_str.split(':')
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        
        return time_to_seconds(end) - time_to_seconds(start)
    
    def extract_full_text(self, segments: List[Dict]) -> str:
        """
        Extract full text from transcript segments.
        
        Args:
            segments: List of transcript segments
            
        Returns:
            Full transcript text
        """
        return ' '.join(segment['text'] for segment in segments)
    
    def process_transcript(self, vtt_path: Path, video_metadata: Optional[Dict] = None) -> Dict:
        """
        Process a single transcript file.
        
        Args:
            vtt_path: Path to .vtt file
            video_metadata: Optional metadata about the video
            
        Returns:
            Processed transcript dictionary
        """
        video_id = vtt_path.stem.replace('.en', '').replace('.vtt', '')
        logger.info(f"Processing transcript: {video_id}")
        
        segments = self.parse_vtt(vtt_path)
        full_text = self.extract_full_text(segments)
        
        result = {
            'video_id': video_id,
            'segments': segments,
            'full_text': full_text,
            'word_count': len(full_text.split()),
            'segment_count': len(segments),
            'total_duration': sum(s['duration'] for s in segments),
            'metadata': video_metadata or {}
        }
        
        # Save processed transcript locally
        output_path = self.output_dir / f"{video_id}_transcript.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Also save plain text version
        text_path = self.output_dir / f"{video_id}_transcript.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Upload to GCS if configured
        if self.upload_to_gcs and self.gcs_storage:
            gcs_json_path = f"transcripts/processed/{video_id}_transcript.json"
            gcs_txt_path = f"transcripts/processed/{video_id}_transcript.txt"
            
            self.gcs_storage.upload_file(output_path, gcs_json_path, content_type='application/json')
            self.gcs_storage.upload_file(text_path, gcs_txt_path, content_type='text/plain')
            
            logger.info(f"Uploaded processed transcript to GCS: {gcs_json_path}")
        
        logger.info(f"Processed transcript: {len(segments)} segments, {result['word_count']} words")
        return result
    
    def process_all_transcripts(self, transcripts_dir: Optional[Path] = None) -> List[Dict]:
        """
        Process all transcript files in a directory.
        
        Args:
            transcripts_dir: Directory containing transcripts (defaults to self.transcripts_dir)
            
        Returns:
            List of processed transcript dictionaries
        """
        if transcripts_dir is None:
            transcripts_dir = self.transcripts_dir
        
        vtt_files = list(Path(transcripts_dir).glob("*.vtt"))
        logger.info(f"Found {len(vtt_files)} transcript files")
        
        results = []
        for vtt_path in vtt_files:
            try:
                result = self.process_transcript(vtt_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {vtt_path}: {e}")
        
        # Save summary
        summary_path = self.output_dir / "transcripts_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                'total_transcripts': len(results),
                'total_words': sum(r['word_count'] for r in results),
                'total_segments': sum(r['segment_count'] for r in results),
                'transcripts': [{
                    'video_id': r['video_id'],
                    'word_count': r['word_count'],
                    'segment_count': r['segment_count']
                } for r in results]
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processed {len(results)} transcripts")
        return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process Khan Academy transcripts")
    parser.add_argument("--input", type=Path, default=Path("data/videos"), help="Directory containing .vtt files")
    parser.add_argument("--output", type=Path, default=Path("data/transcripts"), help="Output directory")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    processor = TranscriptProcessor(
        transcripts_dir=args.input,
        output_dir=args.output
    )
    
    processor.process_all_transcripts()
