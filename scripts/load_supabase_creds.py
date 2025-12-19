#!/usr/bin/env python3
"""
Load Supabase credentials from Inquiry.Institute .env.local file.
"""

import os
from pathlib import Path
import re


def load_env_file(env_path: Path) -> dict:
    """Load environment variables from .env file."""
    env_vars = {}
    if not env_path.exists():
        return env_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            match = re.match(r'^([^#=]+)=(.*)$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip().strip('"\'')
                env_vars[key] = value
    
    return env_vars


def get_supabase_credentials():
    """
    Get Supabase credentials from Inquiry.Institute .env.local file.
    
    Returns:
        Tuple of (supabase_url, supabase_key) or (None, None)
    """
    # Try to find .env.local in parent directory
    inquiry_institute_path = Path(__file__).parent.parent.parent / "Inquiry.Institute"
    env_path = inquiry_institute_path / ".env.local"
    
    if not env_path.exists():
        # Try .env as fallback
        env_path = inquiry_institute_path / ".env"
    
    if not env_path.exists():
        return None, None
    
    env_vars = load_env_file(env_path)
    
    # Get Supabase URL and key
    # For service role operations, we need the service role key
    supabase_url = env_vars.get('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = env_vars.get('SUPABASE_SERVICE_ROLE_KEY') or env_vars.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    return supabase_url, supabase_key


if __name__ == "__main__":
    url, key = get_supabase_credentials()
    if url and key:
        print(f"SUPABASE_URL={url}")
        print(f"SUPABASE_KEY={key[:20]}...")
    else:
        print("Could not find Supabase credentials")
        print(f"Looking in: {Path(__file__).parent.parent.parent / 'Inquiry.Institute' / '.env.local'}")
