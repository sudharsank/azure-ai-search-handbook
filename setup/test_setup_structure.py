#!/usr/bin/env python3
"""
Test Setup Structure
Verify that all setup files and directories are created correctly
"""

import os
import sys
from pathlib import Path

def test_setup_structure():
    """Test that all required setup files and directories exist"""
    print("🔍 Testing Azure AI Search Handbook Setup Structure")
    print("=" * 60)
    
    # Required files
    required_files = [
        "setup/__init__.py",
        "setup/connection_utils.py",
        "setup/common_utils.py",
        "setup/config_templates.py",
        "setup/environment_setup.py",
        "setup/validate_setup.py",
        "setup/setup_cli.py",
        "setup/test_setup_structure.py",
        "setup.py",
        "requirements.txt",
        ".env.template"
    ]
    
    # Required directories
    required_dirs = [
        "config",
        "data",
        "logs",
        "notebooks",
        "scripts",
        "tests",
        "setup"
    ]
    
    # Check files
    print("📁 Checking required files:")
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    # Check directories
    print("\n📂 Checking required directories:")
    missing_dirs = []
    for dir_path in required_dirs:
        if Path(dir_path).exists() and Path(dir_path).is_dir():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/")
            missing_dirs.append(dir_path)
    
    # Check file contents (basic validation)
    print("\n📄 Checking file contents:")
    
    # Check if __init__.py has the right imports
    init_file = Path("setup/__init__.py")
    if init_file.exists():
        content = init_file.read_text()
        if "AzureSearchConnectionManager" in content and "DataGenerator" in content:
            print("  ✅ setup/__init__.py has correct imports")
        else:
            print("  ❌ setup/__init__.py missing expected imports")
    
    # Check if requirements.txt has Azure packages
    req_file = Path("requirements.txt")
    if req_file.exists():
        content = req_file.read_text()
        if "azure-search-documents" in content:
            print("  ✅ requirements.txt includes Azure packages")
        else:
            print("  ❌ requirements.txt missing Azure packages")
    
    # Check if .env.template has required variables
    env_template = Path(".env.template")
    if env_template.exists():
        content = env_template.read_text()
        if "AZURE_SEARCH_SERVICE_ENDPOINT" in content and "AZURE_SEARCH_API_KEY" in content:
            print("  ✅ .env.template has required variables")
        else:
            print("  ❌ .env.template missing required variables")
    
    # Summary
    print("\n" + "=" * 60)
    
    total_issues = len(missing_files) + len(missing_dirs)
    
    if total_issues == 0:
        print("🎉 All setup structure tests passed!")
        print("✅ Azure AI Search Handbook setup is correctly structured")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure environment: cp .env.template .env")
        print("3. Run full setup: python3 setup.py setup")
        return True
    else:
        print(f"❌ Found {total_issues} issues with setup structure")
        if missing_files:
            print(f"   Missing files: {', '.join(missing_files)}")
        if missing_dirs:
            print(f"   Missing directories: {', '.join(missing_dirs)}")
        return False

def main():
    """Main test function"""
    success = test_setup_structure()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())