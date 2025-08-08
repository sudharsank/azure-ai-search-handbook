#!/usr/bin/env python3
"""
Azure AI Search Handbook Setup Wrapper
Simple wrapper script for the setup CLI
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the setup CLI with all arguments passed through"""
    setup_cli_path = Path(__file__).parent / "setup" / "setup_cli.py"
    
    # Pass all arguments to the setup CLI
    cmd = [sys.executable, str(setup_cli_path)] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error running setup: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())