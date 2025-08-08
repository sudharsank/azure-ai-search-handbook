#!/usr/bin/env python3
"""
Cleanup script to remove globally installed packages from requirements.txt
This script helps clean up packages that were installed globally before
switching to a virtual environment approach.
"""

import subprocess
import sys
from pathlib import Path

def get_packages_from_requirements():
    """Extract package names from requirements.txt"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return []
    
    packages = []
    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name (before version specifiers)
                package_name = line.split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
                packages.append(package_name)
    
    return packages

def check_if_package_installed(package):
    """Check if a package is installed"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", package], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def cleanup_packages():
    """Remove globally installed packages"""
    print("🧹 Azure AI Search Handbook - Global Package Cleanup")
    print("=" * 60)
    
    # Get packages from requirements.txt
    packages_to_remove = get_packages_from_requirements()
    
    if not packages_to_remove:
        print("❌ No packages found in requirements.txt")
        return False
    
    print(f"📦 Found {len(packages_to_remove)} packages in requirements.txt")
    
    # Check which packages are actually installed
    installed_packages = []
    for package in packages_to_remove:
        if check_if_package_installed(package):
            installed_packages.append(package)
    
    if not installed_packages:
        print("✅ No packages from requirements.txt are currently installed globally")
        return True
    
    print(f"\n🔍 Found {len(installed_packages)} packages installed globally:")
    for package in installed_packages:
        print(f"  • {package}")
    
    # Confirm removal
    print(f"\n⚠️  This will remove {len(installed_packages)} packages from your global Python environment")
    response = input("Do you want to continue? (y/N): ").lower().strip()
    
    if response != 'y':
        print("❌ Cleanup cancelled")
        return False
    
    # Remove packages
    print(f"\n🗑️  Removing {len(installed_packages)} packages...")
    removed_count = 0
    failed_packages = []
    
    for package in installed_packages:
        try:
            print(f"  Removing {package}...", end=" ")
            result = subprocess.run([sys.executable, "-m", "pip", "uninstall", package, "-y"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅")
                removed_count += 1
            else:
                print("❌")
                failed_packages.append(package)
        except Exception as e:
            print(f"❌ (Error: {e})")
            failed_packages.append(package)
    
    # Summary
    print(f"\n📊 Cleanup Summary:")
    print(f"  ✅ Successfully removed: {removed_count} packages")
    if failed_packages:
        print(f"  ❌ Failed to remove: {len(failed_packages)} packages")
        print(f"     Failed packages: {', '.join(failed_packages)}")
    
    print(f"\n✅ Global cleanup completed!")
    return True

def show_next_steps():
    """Show recommended next steps"""
    print("\n📋 Recommended next steps:")
    print("1. Create virtual environment:")
    print("   python3 -m venv venv")
    print("\n2. Activate virtual environment:")
    print("   # On macOS/Linux:")
    print("   source venv/bin/activate")
    print("   # On Windows:")
    print("   venv\\Scripts\\activate")
    print("\n3. Install packages in virtual environment:")
    print("   pip install -r requirements.txt")
    print("\n4. Run the setup script:")
    print("   python setup/environment_setup.py")
    print("\n5. Or use the CLI:")
    print("   python setup/setup_cli.py setup")

def main():
    """Main function"""
    try:
        if cleanup_packages():
            show_next_steps()
            return 0
        else:
            return 1
    except KeyboardInterrupt:
        print("\n⚠️  Cleanup cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())