#!/usr/bin/env python3
"""
Build script for Content Spoofer Desktop (Reels Washer) - macOS Version
Packages the application into a standalone .app bundle using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean pycache in subdirectories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                print(f"🧹 Cleaning {pycache_path}...")
                shutil.rmtree(pycache_path)

def check_mac_dependencies():
    """Check if all required files and dependencies exist for Mac."""
    required_files = [
        'main.py',
        'content-spoofer-mac.spec',
        'requirements.txt',
        'src/core/process.py',
        'src/ui/gui.py',
    ]
    
    # Check for FFmpeg (Mac versions without .exe)
    ffmpeg_commands = ['ffmpeg', 'ffprobe', 'ffplay']
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    # Check FFmpeg availability
    missing_ffmpeg = []
    for cmd in ffmpeg_commands:
        try:
            result = subprocess.run([cmd, '-version'], capture_output=True, text=True)
            if result.returncode != 0:
                missing_ffmpeg.append(cmd)
        except FileNotFoundError:
            missing_ffmpeg.append(cmd)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
    
    if missing_ffmpeg:
        print("❌ Missing FFmpeg commands (install with 'brew install ffmpeg'):")
        for cmd in missing_ffmpeg:
            print(f"   - {cmd}")
        print("\nTo install FFmpeg on Mac:")
        print("   brew install ffmpeg")
    
    if missing_files or missing_ffmpeg:
        return False
    
    print("✅ All required files and dependencies found")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_ffmpeg_symlinks():
    """Create symbolic links to system FFmpeg binaries."""
    ffmpeg_commands = ['ffmpeg', 'ffprobe', 'ffplay']
    
    for cmd in ffmpeg_commands:
        try:
            # Find the system FFmpeg path
            result = subprocess.run(['which', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                ffmpeg_path = result.stdout.strip()
                
                # Create symlink in current directory
                local_path = os.path.join('.', cmd)
                if os.path.exists(local_path):
                    os.remove(local_path)
                
                os.symlink(ffmpeg_path, local_path)
                print(f"✅ Created symlink for {cmd}")
            else:
                print(f"❌ Could not find {cmd} in system PATH")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create symlink for {cmd}: {e}")
            return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building macOS application...")
    try:
        # Run PyInstaller with the Mac spec file
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',  # Clean cache and remove temporary files
            'content-spoofer-mac.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print("Error output:")
        print(e.stderr)
        return False

def post_build_tasks():
    """Perform post-build tasks for macOS."""
    dist_dir = Path('dist/ReelsWasher')
    
    if not dist_dir.exists():
        print("❌ Build directory not found!")
        return False
    
    # Create output directory in the built app
    output_dir = dist_dir / 'output'
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Created output directory: {output_dir}")
    
    # Copy additional files if needed
    additional_files = ['README.md']
    for file_name in additional_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_dir)
            print(f"📄 Copied {file_name} to build directory")
    
    print(f"📁 Application built in: {dist_dir.absolute()}")
    print(f"🚀 Main executable: {dist_dir / 'ReelsWasher'}")
    
    return True

def main():
    """Main build process for macOS."""
    print("🍎 Content Spoofer Desktop - macOS Build Script")
    print("=" * 50)
    
    start_time = time.time()
    
    # Check if we're actually on macOS
    if sys.platform != "darwin":
        print("❌ This script is designed for macOS only")
        print(f"   Current platform: {sys.platform}")
        return 1
    
    # Step 1: Check dependencies
    if not check_mac_dependencies():
        print("❌ Build aborted due to missing dependencies")
        return 1
    
    # Step 2: Clean previous builds
    clean_build_dirs()
    
    # Step 3: Create FFmpeg symlinks
    if not create_ffmpeg_symlinks():
        print("❌ Build aborted due to FFmpeg issues")
        return 1
    
    # Step 4: Install dependencies
    if not install_dependencies():
        print("❌ Build aborted due to dependency issues")
        return 1
    
    # Step 5: Build executable
    if not build_executable():
        print("❌ Build failed")
        return 1
    
    # Step 6: Post-build tasks
    if not post_build_tasks():
        print("❌ Post-build tasks failed")
        return 1
    
    # Build summary
    build_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"🎉 macOS build completed successfully in {build_time:.1f} seconds!")
    print(f"📁 Find your application in: dist/ReelsWasher/")
    print(f"🚀 Run: dist/ReelsWasher/ReelsWasher")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
