#!/usr/bin/env python3
"""
Documentation Server Script
Serves the MkDocs documentation with optimal settings
"""

import subprocess
import sys
import os
from pathlib import Path


def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    return start_port  # Fallback to original port


def serve_docs():
    """Serve the documentation with optimal settings"""
    print("🚀 Starting Azure AI Search Handbook Documentation Server")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("mkdocs.yml").exists():
        print("❌ mkdocs.yml not found!")
        print("💡 Make sure you're in the project root directory")
        return False
    
    # Find available port
    port = find_available_port()
    
    # Build the command
    cmd = [
        "mkdocs", "serve",
        "--dev-addr", f"localhost:{port}",
        "--no-livereload"  # Disable live reload for stability
    ]
    
    print(f"📡 Starting server on http://localhost:{port}")
    print("📋 Server options:")
    print(f"   • Port: {port}")
    print(f"   • Live reload: Disabled (for stability)")
    print(f"   • Address: localhost")
    print()
    print("🌐 Open http://localhost:{} in your browser".format(port))
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    try:
        # Run MkDocs serve
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start documentation server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Documentation server stopped")
        return True


def main():
    """Main function"""
    try:
        success = serve_docs()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()