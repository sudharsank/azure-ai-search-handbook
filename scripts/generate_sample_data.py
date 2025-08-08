#!/usr/bin/env python3
"""
Generate sample data for exercises and testing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from setup.common_utils import setup_sample_environment

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"🎲 Generating {count} sample documents...")
    
    documents = setup_sample_environment(document_count=count)
    print(f"✅ Generated {len(documents)} sample documents")
