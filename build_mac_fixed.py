#!/usr/bin/env python3
"""
FIXED Build script for Content Spoofer Desktop (Reels Washer) - macOS Version
This version addresses common CustomTkinter GUI issues on macOS.
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
        for dir_name in dirs[:]:  # Use slice to avoid modifying list while iterating
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                print(f"🧹 Cleaning {pycache_path}...")
                shutil.rmtree(pycache_path)
                dirs.remove(dir_name)

def check_mac_dependencies():
    """Check if all required files and dependencies exist for Mac."""
    required_files = [
        'main.py',
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
    """Install required Python packages with macOS-specific fixes."""
    print("📦 Installing dependencies with macOS optimizations...")
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True)
        
        # Install specific CustomTkinter version known to work well on macOS
        print("🔧 Installing CustomTkinter (macOS optimized)...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'customtkinter==5.2.0'], 
                      check=True)
        
        # Install other requirements
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        
        # Install PyInstaller with latest version for macOS compatibility
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pyinstaller'], 
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
                if os.path.exists(local_path) or os.path.islink(local_path):
                    os.remove(local_path)
                
                os.symlink(ffmpeg_path, local_path)
                print(f"✅ Created symlink for {cmd} -> {ffmpeg_path}")
            else:
                print(f"❌ Could not find {cmd} in system PATH")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create symlink for {cmd}: {e}")
            return False
    
    return True

def test_customtkinter():
    """Test CustomTkinter installation and functionality."""
    print("🧪 Testing CustomTkinter installation...")
    try:
        import customtkinter as ctk
        print(f"✅ CustomTkinter version: {ctk.__version__}")
        
        # Test basic functionality
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Create a test window (don't show it)
        root = ctk.CTk()
        root.withdraw()  # Hide the window
        test_frame = ctk.CTkFrame(root)
        test_button = ctk.CTkButton(test_frame, text="Test")
        root.destroy()
        
        print("✅ CustomTkinter basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ CustomTkinter test failed: {e}")
        print("This might cause GUI issues in the built application.")
        return False

def create_fixed_spec_file():
    """Create or verify the fixed spec file exists."""
    spec_file = 'content-spoofer-mac-fixed.spec'
    if not os.path.exists(spec_file):
        print(f"❌ Fixed spec file '{spec_file}' not found!")
        print("Make sure you have the content-spoofer-mac-fixed.spec file")
        return False
    
    print(f"✅ Using fixed spec file: {spec_file}")
    return True

def build_executable():
    """Build the executable using PyInstaller with the fixed spec."""
    print("🔨 Building macOS application with GUI fixes...")
    try:
        # Use the fixed spec file
        spec_file = 'content-spoofer-mac-fixed.spec'
        
        if not os.path.exists(spec_file):
            print(f"❌ Spec file {spec_file} not found!")
            return False
        
        # Run PyInstaller with the fixed Mac spec file
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',  # Clean cache and remove temporary files
            '--noconfirm',  # Don't ask for confirmation
            spec_file
        ]
        
        print(f"🔧 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        print(f"Build output preview:\n{result.stdout[-500:]}")  # Last 500 chars
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print("Error output:")
        print(e.stderr)
        print("\n💡 Common solutions:")
        print("   1. Run with debug: Set debug=True and console=True in spec file")
        print("   2. Check CustomTkinter version: pip install customtkinter==5.2.0")
        print("   3. Clear Python cache: rm -rf ~/.cache/pip")
        return False

def post_build_tasks():
    """Perform post-build tasks for macOS with GUI fixes."""
    dist_dir = Path('dist/ReelsWasher')
    
    if not dist_dir.exists():
        print("❌ Build directory not found!")
        return False
    
    print(f"📁 Build directory found: {dist_dir.absolute()}")
    
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
    
    # Make the executable actually executable
    executable_path = dist_dir / 'ReelsWasher'
    if executable_path.exists():
        os.chmod(executable_path, 0o755)
        print(f"✅ Made executable: {executable_path}")
    
    # Create a simple launcher script for troubleshooting
    launcher_script = dist_dir / 'run_debug.sh'
    launcher_content = '''#!/bin/bash
echo "🍎 Reels Washer Debug Launcher"
echo "Current directory: $(pwd)"
echo "Executable path: $(readlink -f ReelsWasher)"
echo ""
echo "Starting application..."
./ReelsWasher
'''
    with open(launcher_script, 'w') as f:
        f.write(launcher_content)
    os.chmod(launcher_script, 0o755)
    print(f"🔧 Created debug launcher: {launcher_script}")
    
    print(f"📁 Application built in: {dist_dir.absolute()}")
    print(f"🚀 Main executable: {executable_path}")
    print(f"🔧 Debug launcher: {launcher_script}")
    
    return True

def main():
    """Main build process for macOS with GUI fixes."""
    print("🍎 Content Spoofer Desktop - FIXED macOS Build Script")
    print("=" * 60)
    print("This version includes fixes for common CustomTkinter GUI issues")
    print("=" * 60)
    
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
    
    # Step 4: Install dependencies with macOS fixes
    if not install_dependencies():
        print("❌ Build aborted due to dependency issues")
        return 1
    
    # Step 5: Test CustomTkinter
    if not test_customtkinter():
        print("⚠️  CustomTkinter test failed - proceeding anyway")
        print("   (The build might still work)")
    
    # Step 6: Check for fixed spec file
    if not create_fixed_spec_file():
        print("❌ Build aborted - fixed spec file missing")
        return 1
    
    # Step 7: Build executable
    if not build_executable():
        print("❌ Build failed")
        return 1
    
    # Step 8: Post-build tasks
    if not post_build_tasks():
        print("❌ Post-build tasks failed")
        return 1
    
    # Build summary
    build_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"🎉 FIXED macOS build completed in {build_time:.1f} seconds!")
    print(f"📁 Find your application in: dist/ReelsWasher/")
    print(f"🚀 Run: ./dist/ReelsWasher/ReelsWasher")
    print(f"🔧 Debug: ./dist/ReelsWasher/run_debug.sh")
    print("\n💡 If GUI is still blank, try:")
    print("   1. Run the debug launcher to see error messages")
    print("   2. Check Console.app for application errors")
    print("   3. Try running from Terminal to see Python errors")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


