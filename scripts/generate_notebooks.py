#!/usr/bin/env python3
"""
Generate Jupyter notebooks from Python code samples and exercises
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from setup.notebook_generator import main as generate_notebooks

if __name__ == "__main__":
    print("📓 Generating Jupyter notebooks...")
    if generate_notebooks():
        print("✅ Notebook generation completed!")
        sys.exit(0)
    else:
        print("❌ Notebook generation failed!")
        sys.exit(1)
