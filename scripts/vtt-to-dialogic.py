#!/usr/bin/env python3
"""
Convert WebVTT transcript directly to dialogic format.
"""

import re
import json
import sys
from pathlib import Path
from datetime import timedelta

def parse_time(time_str):
    """Parse WebVTT time format (HH:MM:SS.mmm) to seconds."""
    parts = time_str.split(':')
    hours = float(parts[0])
    minutes = float(parts[1])
    seconds_parts = parts[2].split('.')
    seconds = float(seconds_parts[0])
    milliseconds = float(seconds_parts[1]) if len(seconds_parts) > 1 else 0
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000

def vtt_to_dialogic(vtt_path, output_path=None, video_id=None, title=None):
    """Convert VTT file to dialogic format."""
    if video_id is None:
        video_id = Path(vtt_path).stem.replace('.en', '').replace('.vtt', '')
    
    if output_path is None:
        output_path = Path(vtt_path).parent.parent / 'processed' / f'{video_id}_dialogic_transcript.json'
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    segments = []
    segment_id = 1
    
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse WebVTT format
    # Pattern: timestamp line followed by text lines
    pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})\s*\n(.*?)(?=\n\d{2}:\d{2}:\d{2}\.\d{3}|\n\n|$)'
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        start_time_str = match.group(1)
        end_time_str = match.group(2)
        text = match.group(3).strip()
        
        # Remove WebVTT tags and clean text
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'\n+', ' ', text)  # Replace newlines with spaces
        text = ' '.join(text.split())  # Normalize whitespace
        
        if not text:
            continue
        
        start_time = parse_time(start_time_str)
        end_time = parse_time(end_time_str)
        duration = end_time - start_time
        
        # Determine pause duration (longer for longer segments)
        pause_duration = min(3000, max(1500, int(duration * 200)))
        
        # Detect topic markers
        topic_marker = None
        text_lower = text.lower()
        if any(word in text_lower for word in ['welcome', 'introduction', 'today']):
            topic_marker = 'introduction'
        elif any(word in text_lower for word in ['example', 'for instance', 'let\'s say']):
            topic_marker = 'example'
        elif any(word in text_lower for word in ['conclusion', 'summary', 'recap', 'that\'s']):
            topic_marker = 'summary'
        elif any(word in text_lower for word in ['variable', 'symbol', 'letter']):
            topic_marker = 'definition'
        
        segments.append({
            'segment_id': segment_id,
            'text': text,
            'start_time': int(start_time),
            'end_time': int(end_time),
            'duration': int(duration),
            'allows_questions': True,
            'pause_duration': pause_duration,
            'topic_marker': topic_marker
        })
        segment_id += 1
    
    # Create dialogic transcript
    dialogic_transcript = {
        'class_id': 'algebra-basics-intro',
        'video_id': video_id,
        'title': title or 'Introduction to variables',
        'segments': segments,
        'total_segments': len(segments),
        'total_duration': sum(s['duration'] for s in segments),
        'metadata': {
            'source': 'khan-academy',
            'created': '2025-01-20',
            'format_version': '1.0'
        }
    }
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dialogic_transcript, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created dialogic transcript: {output_path}")
    print(f"   Segments: {len(segments)}")
    print(f"   Total duration: {dialogic_transcript['total_duration']} seconds")
    print(f"   Video: {title or video_id}")
    
    return dialogic_transcript

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vtt-to-dialogic.py <transcript.vtt> [output.json] [video_id] [title]")
        sys.exit(1)
    
    vtt_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    video_id = sys.argv[3] if len(sys.argv) > 3 else None
    title = sys.argv[4] if len(sys.argv) > 4 else None
    
    vtt_to_dialogic(vtt_path, output_path, video_id, title)
