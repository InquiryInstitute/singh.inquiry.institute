#!/usr/bin/env python3
"""
Quick script to list videos from Kolibri.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from api.kolibri_client import KolibriClient
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kolibri-url', default='http://localhost:8080',
                       help='Kolibri server URL')
    parser.add_argument('--limit', type=int, default=20,
                       help='Number of videos to list')
    parser.add_argument('--search', type=str, default=None,
                       help='Search term')
    args = parser.parse_args()
    
    client = KolibriClient(args.kolibri_url)
    
    if not client.test_connection():
        print(f"❌ Cannot connect to Kolibri at {args.kolibri_url}")
        print("Try: python scripts/kolibri-find-server.py")
        return
    
    # Get Khan Academy channel
    ka_channel = client.get_khan_academy_channel()
    if not ka_channel:
        print("❌ Khan Academy channel not found")
        channels = client.get_channels()
        print(f"Available channels ({len(channels)}):")
        for ch in channels:
            print(f"  - {ch.get('name')} (ID: {ch.get('id')})")
        return
    
    print(f"✅ Found Khan Academy channel: {ka_channel.get('name')}")
    
    # Get videos
    if args.search:
        videos = client.search_content(ka_channel['id'], args.search, kind='video')
    else:
        videos = client.get_content_nodes(ka_channel['id'], kind='video')
    
    if args.limit:
        videos = videos[:args.limit]
    
    print(f"\n📹 Found {len(videos)} videos:\n")
    
    for i, video in enumerate(videos, 1):
        details = client.get_content_node_details(video['id'])
        title = details.get('title', video.get('title', 'Unknown')) if details else video.get('title', 'Unknown')
        duration = details.get('duration', 0) if details else 0
        files = client.get_content_files(video['id'])
        has_transcript = any('subtitle' in f.get('preset', '').lower() or 'transcript' in f.get('preset', '').lower() 
                           for f in files)
        
        print(f"{i}. {title}")
        print(f"   ID: {video['id']}")
        if duration:
            print(f"   Duration: {duration // 60}m {duration % 60}s")
        print(f"   Transcript: {'✅' if has_transcript else '❌'}")
        print()

if __name__ == "__main__":
    main()
