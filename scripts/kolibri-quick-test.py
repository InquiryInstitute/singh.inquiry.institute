#!/usr/bin/env python3
"""
Quick test script to verify Kolibri connection and show available content.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from api.kolibri_client import KolibriClient
import argparse

def main():
    parser = argparse.ArgumentParser(description='Quick test of Kolibri connection')
    parser.add_argument('--kolibri-url', default='http://localhost:8080',
                       help='Kolibri server URL')
    args = parser.parse_args()
    
    print(f"Testing connection to {args.kolibri_url}...")
    client = KolibriClient(args.kolibri_url)
    
    if not client.test_connection():
        print(f"❌ Cannot connect to Kolibri at {args.kolibri_url}")
        print("\nTroubleshooting:")
        print("1. Make sure Kolibri is running: kolibri start")
        print("2. Check the port: kolibri manage showconfig")
        print("3. Try a different URL: python scripts/kolibri-quick-test.py --kolibri-url http://your-url:port")
        return 1
    
    print("✅ Connected to Kolibri!\n")
    
    # Get channels
    channels = client.get_channels()
    print(f"📚 Found {len(channels)} channels:")
    for ch in channels:
        print(f"   - {ch.get('name')} (ID: {ch.get('id')})")
    
    # Get Khan Academy channel
    ka_channel = client.get_khan_academy_channel()
    if ka_channel:
        print(f"\n🎓 Khan Academy channel: {ka_channel.get('name')}")
        
        # Get video count
        videos = client.get_content_nodes(ka_channel['id'], kind='video')
        print(f"   Videos: {len(videos)}")
        
        # Show sample videos
        if videos:
            print(f"\n📹 Sample videos (first 5):")
            for i, video in enumerate(videos[:5], 1):
                details = client.get_content_node_details(video['id'])
                title = details.get('title', 'Unknown') if details else 'Unknown'
                files = client.get_content_files(video['id'])
                has_transcript = any('subtitle' in f.get('preset', '').lower() 
                                   for f in files)
                print(f"   {i}. {title}")
                print(f"      Transcript: {'✅' if has_transcript else '❌'}")
    else:
        print("\n⚠️  Khan Academy channel not found")
        print("   Make sure you've imported the Khan Academy channel in Kolibri")
    
    print("\n✅ Kolibri is ready to use!")
    print("\nNext steps:")
    print("  python scripts/kolibri-discover-content.py --kolibri-url", args.kolibri_url)
    print("  python scripts/kolibri-list-videos.py --kolibri-url", args.kolibri_url)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
