#!/usr/bin/env python3
"""
Convert processed transcript to dialogic format.
"""

import json
import sys
from pathlib import Path

def convert_to_dialogic(transcript_path, output_path=None):
    """Convert a processed transcript to dialogic format."""
    with open(transcript_path, 'r') as f:
        data = json.load(f)
    
    # Extract video metadata
    video_id = data.get('video_id', Path(transcript_path).stem.replace('_transcript', ''))
    
    # Convert segments to dialogic format
    dialogic_segments = []
    segment_id = 1
    
    for segment in data.get('segments', []):
        start_time = segment.get('start_time', 0)
        end_time = segment.get('end_time', start_time + segment.get('duration', 0))
        duration = end_time - start_time
        
        # Create dialogic segment
        dialogic_segment = {
            'segment_id': segment_id,
            'text': segment.get('text', ''),
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'allows_questions': True,  # All segments allow questions
            'pause_duration': 2000,  # Default 2 second pause
            'topic_marker': None  # Can be enhanced later
        }
        
        # Add topic markers based on sentence boundaries or content
        text = dialogic_segment['text'].lower()
        if any(word in text for word in ['introduction', 'welcome', 'today']):
            dialogic_segment['topic_marker'] = 'introduction'
        elif any(word in text for word in ['example', 'for instance']):
            dialogic_segment['topic_marker'] = 'example'
        elif any(word in text for word in ['conclusion', 'summary', 'recap']):
            dialogic_segment['topic_marker'] = 'summary'
        
        dialogic_segments.append(dialogic_segment)
        segment_id += 1
    
    # Create dialogic transcript
    dialogic_transcript = {
        'class_id': 'algebra-basics-intro',  # Default, can be updated
        'video_id': video_id,
        'title': data.get('metadata', {}).get('title', 'Unknown'),
        'segments': dialogic_segments,
        'total_segments': len(dialogic_segments),
        'total_duration': sum(s['duration'] for s in dialogic_segments),
        'metadata': {
            'source': 'khan-academy',
            'created': data.get('metadata', {}).get('created', '2025-01-20'),
            'format_version': '1.0'
        }
    }
    
    # Save dialogic transcript
    if output_path is None:
        output_path = Path(transcript_path).parent / f"{video_id}_dialogic_transcript.json"
    
    with open(output_path, 'w') as f:
        json.dump(dialogic_transcript, f, indent=2)
    
    print(f"✅ Created dialogic transcript: {output_path}")
    print(f"   Segments: {len(dialogic_segments)}")
    print(f"   Total duration: {dialogic_transcript['total_duration']} seconds")
    
    return dialogic_transcript

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process-to-dialogic.py <transcript.json> [output.json]")
        sys.exit(1)
    
    transcript_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_to_dialogic(transcript_path, output_path)
