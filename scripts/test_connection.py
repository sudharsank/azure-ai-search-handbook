#!/usr/bin/env python3
"""
Quick test script to verify Azure AI Search connection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import directly from connection_utils to avoid setup package issues
try:
    from setup.connection_utils import test_default_connection
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure Azure packages are installed: pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    print("🔍 Testing Azure AI Search connection...")
    try:
        if test_default_connection():
            print("✅ Connection test passed!")
            sys.exit(0)
        else:
            print("❌ Connection test failed!")
            print("💡 Check your .env file configuration")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        print("💡 Make sure your .env file is configured correctly")
        sys.exit(1)
