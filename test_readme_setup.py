#!/usr/bin/env python3
"""
Test script to verify README setup instructions work correctly
This script simulates following the README setup process
"""

import os
import sys
import subprocess
from pathlib import Path


def test_readme_setup():
    """Test the README setup instructions"""
    print("🧪 Testing README Setup Instructions")
    print("=" * 50)
    
    # Test 1: Check if required files exist
    print("\n📋 Test 1: Checking required files...")
    required_files = [
        "README.md",
        "requirements.txt",
        "setup/environment_setup.py",
        "setup/setup_cli.py",
        "cleanup_global_install.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    # Test 2: Check Python version
    print(f"\n📋 Test 2: Python version check...")
    if sys.version_info >= (3, 8):
        print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor} (meets requirement)")
    else:
        print(f"  ❌ Python {sys.version_info.major}.{sys.version_info.minor} (requires 3.8+)")
        return False
    
    # Test 3: Check if CLI commands are accessible
    print(f"\n📋 Test 3: CLI accessibility...")
    try:
        result = subprocess.run([sys.executable, "setup/setup_cli.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✅ CLI is accessible")
        else:
            print("  ❌ CLI not accessible")
            return False
    except Exception as e:
        print(f"  ❌ CLI test failed: {e}")
        return False
    
    # Test 4: Check virtual environment detection
    print(f"\n📋 Test 4: Virtual environment detection...")
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print(f"  ✅ Running in virtual environment: {sys.prefix}")
    else:
        print("  ⚠️  Not in virtual environment (this is expected for testing)")
    
    # Test 5: Check if requirements.txt is readable
    print(f"\n📋 Test 5: Requirements file validation...")
    try:
        with open("requirements.txt", 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"  ✅ Found {len(lines)} packages in requirements.txt")
    except Exception as e:
        print(f"  ❌ Requirements file error: {e}")
        return False
    
    # Test 6: Test status command
    print(f"\n📋 Test 6: Status command test...")
    try:
        result = subprocess.run([sys.executable, "setup/setup_cli.py", "status"], 
                              capture_output=True, text=True, timeout=15)
        if "Environment Status" in result.stdout:
            print("  ✅ Status command works")
        else:
            print("  ❌ Status command output unexpected")
            print(f"  Output: {result.stdout[:200]}...")
            return False
    except Exception as e:
        print(f"  ❌ Status command failed: {e}")
        return False
    
    print(f"\n✅ All README setup tests passed!")
    print(f"\n📋 You can now follow the README instructions:")
    print(f"1. Run: python setup/environment_setup.py")
    print(f"2. Or: python setup/setup_cli.py setup")
    print(f"3. Configure .env file")
    print(f"4. Test: python scripts/test_connection.py")
    
    return True


def show_readme_commands():
    """Show the key commands from README"""
    print(f"\n📖 Key Commands from README:")
    print(f"=" * 40)
    
    commands = [
        ("Clean global packages", "python cleanup_global_install.py"),
        ("Create virtual env", "python3 -m venv venv"),
        ("Activate virtual env (macOS/Linux)", "source venv/bin/activate"),
        ("Activate virtual env (Windows)", "venv\\Scripts\\activate"),
        ("Run setup", "python setup/environment_setup.py"),
        ("CLI setup", "python setup/setup_cli.py setup"),
        ("Check status", "python setup/setup_cli.py status"),
        ("Test connection", "python scripts/test_connection.py"),
        ("Generate notebooks", "python setup/setup_cli.py notebooks"),
        ("Generate sample data", "python scripts/generate_sample_data.py")
    ]
    
    for description, command in commands:
        print(f"  {description}:")
        print(f"    {command}")
        print()


if __name__ == "__main__":
    print("🧪 README Setup Verification")
    print("This script tests if the README setup instructions will work")
    print()
    
    try:
        if test_readme_setup():
            show_readme_commands()
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check the issues above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)