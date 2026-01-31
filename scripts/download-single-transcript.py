#!/usr/bin/env python3
"""
Quick script to download a single Khan Academy transcript from YouTube.
"""

import sys
from pathlib import Path
import yt_dlp
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def download_transcript(youtube_id, output_dir="data/transcripts/raw"):
    """Download transcript for a single YouTube video."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    video_url = f"https://www.youtube.com/watch?v={youtube_id}"
    
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,  # Get auto-generated if manual don't exist
        'subtitleslangs': ['en'],
        'subtitlesformat': 'vtt',
        'skip_download': True,  # Don't download video, only subtitles
        'outtmpl': str(output_path / f'{youtube_id}.%(ext)s'),
        'quiet': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading transcript for: {youtube_id}")
            info = ydl.extract_info(video_url, download=True)
            
            # Find the downloaded transcript file
            transcript_path = output_path / f"{youtube_id}.en.vtt"
            if not transcript_path.exists():
                transcript_path = output_path / f"{youtube_id}.vtt"
            
            if transcript_path.exists():
                print(f"✅ Successfully downloaded transcript: {transcript_path}")
                print(f"   Video title: {info.get('title', 'Unknown')}")
                print(f"   Duration: {info.get('duration', 0)} seconds")
                return transcript_path
            else:
                print(f"❌ Transcript file not found after download")
                return None
                
    except Exception as e:
        print(f"❌ Error downloading transcript: {e}")
        return None

if __name__ == "__main__":
    # Download the transcript for the video we have in metadata
    youtube_id = "NybHckSEQBI"  # "Introduction to variables"
    
    if len(sys.argv) > 1:
        youtube_id = sys.argv[1]
    
    result = download_transcript(youtube_id)
    
    if result:
        print(f"\n📝 Next step: Process the transcript with:")
        print(f"   python src/process/process_transcripts.py {result}")
