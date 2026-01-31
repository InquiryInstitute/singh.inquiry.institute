#!/usr/bin/env python3
"""
Find running Kolibri server.
"""

import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from api.kolibri_client import KolibriClient

def find_kolibri_server():
    """Try to find Kolibri server on common ports."""
    common_urls = [
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8000",
        "http://0.0.0.0:8080",
    ]
    
    print("Searching for Kolibri server...")
    
    for url in common_urls:
        try:
            client = KolibriClient(url)
            if client.test_connection():
                print(f"✅ Found Kolibri at: {url}")
                channels = client.get_channels()
                print(f"   Channels: {len(channels)}")
                for channel in channels[:3]:
                    print(f"     - {channel.get('name')} (ID: {channel.get('id')})")
                return url
        except Exception as e:
            continue
    
    print("❌ Kolibri server not found on common ports")
    print("\nTo start Kolibri:")
    print("  kolibri start")
    print("\nOr specify URL manually:")
    print("  python scripts/kolibri-discover-content.py --kolibri-url http://your-kolibri-url:port")
    return None

if __name__ == "__main__":
    find_kolibri_server()
