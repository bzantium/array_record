#!/usr/bin/env python3
"""
Script to help publish ArrayRecord Python to PyPI.

This script automates the process of building and uploading the package to PyPI.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, check=True, 
            capture_output=True, text=True
        )
        print("✓ Success")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def check_requirements():
    """Check if required tools are installed."""
    print("Checking requirements...")
    
    required_packages = ['build', 'twine']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {missing_packages}")
        print("Installing missing packages...")
        cmd = f"pip install {' '.join(missing_packages)}"
        if not run_command(cmd):
            return False
    
    print("✓ All requirements satisfied")
    return True


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    # Remove build directories
    dirs_to_remove = ['build', 'dist', 'array_record.egg-info', 'array_record_python.egg-info']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            if not run_command(f"rm -rf {dir_name}"):
                return False
    
    print("✓ Build artifacts cleaned")
    return True


def build_package():
    """Build the package."""
    print("Building package...")
    
    # Build source distribution and wheel
    if not run_command("python -m build"):
        return False
    
    print("✓ Package built successfully")
    return True


def check_package():
    """Check the built package."""
    print("Checking package...")
    
    # Check with twine
    if not run_command("twine check dist/*"):
        return False
    
    print("✓ Package check passed")
    return True


def upload_to_test_pypi():
    """Upload to Test PyPI."""
    print("Uploading to Test PyPI...")
    
    cmd = "twine upload --repository testpypi dist/*"
    if not run_command(cmd):
        print("Failed to upload to Test PyPI")
        print("Make sure you have configured your Test PyPI credentials:")
        print("  pip install keyring")
        print("  twine configure")
        return False
    
    print("✓ Package uploaded to Test PyPI")
    print("You can test install with:")
    print("  pip install --index-url https://test.pypi.org/simple/ array-record-python")
    return True


def upload_to_pypi():
    """Upload to PyPI."""
    print("Uploading to PyPI...")
    
    # Confirm before uploading to production PyPI
    response = input("Are you sure you want to upload to production PyPI? (yes/no): ")
    if response.lower() != 'yes':
        print("Upload cancelled")
        return False
    
    cmd = "twine upload dist/*"
    if not run_command(cmd):
        print("Failed to upload to PyPI")
        print("Make sure you have configured your PyPI credentials:")
        print("  pip install keyring")
        print("  twine configure")
        return False
    
    print("✓ Package uploaded to PyPI")
    print("You can now install with:")
    print("  pip install array-record-python")
    return True


def validate_version():
    """Validate that version information is correct."""
    print("Validating version information...")
    
    # Check that version is set correctly
    try:
        from array_record import __version__
        print(f"Package version: {__version__}")
    except ImportError:
        print("Warning: Could not import version from package")
    
    # Check setup.py version
    with open('setup.py', 'r') as f:
        content = f.read()
        if "version='0.8.1'" in content:
            print("✓ Version found in setup.py")
        else:
            print("Warning: Version not found in setup.py")
    
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Publish ArrayRecord Python to PyPI")
    
    parser.add_argument(
        '--test', 
        action='store_true', 
        help='Upload to Test PyPI instead of production PyPI'
    )
    parser.add_argument(
        '--skip-build', 
        action='store_true', 
        help='Skip the build step (use existing dist/ files)'
    )
    parser.add_argument(
        '--clean-only', 
        action='store_true', 
        help='Only clean build artifacts and exit'
    )
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("ArrayRecord Python PyPI Publisher")
    print("=" * 40)
    
    # Clean build artifacts
    if not clean_build():
        sys.exit(1)
    
    if args.clean_only:
        print("Clean completed. Exiting.")
        return
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Validate version
    if not validate_version():
        sys.exit(1)
    
    # Build package
    if not args.skip_build:
        if not build_package():
            sys.exit(1)
    else:
        print("Skipping build step...")
    
    # Check package
    if not check_package():
        sys.exit(1)
    
    # Upload to appropriate PyPI
    if args.test:
        if not upload_to_test_pypi():
            sys.exit(1)
    else:
        if not upload_to_pypi():
            sys.exit(1)
    
    print("\n🎉 Publication completed successfully!")
    
    if args.test:
        print("\nNext steps:")
        print("1. Test install from Test PyPI:")
        print("   pip install --index-url https://test.pypi.org/simple/ array-record-python")
        print("2. If everything works, publish to production PyPI:")
        print("   python publish_to_pypi.py")
    else:
        print("\nYour package is now available on PyPI!")
        print("Users can install it with: pip install array-record-python")


if __name__ == "__main__":
    main()
