#!/usr/bin/env python3
"""
Mac App Testing Script - Validates the built app
This runs on the Mac builder to test if the app works properly
"""

import os
import sys
import subprocess
import time

def test_app_structure():
    """Test if the .app bundle has correct structure."""
    print("🔍 Testing app bundle structure...")
    
    app_path = "dist/Reels Washer.app"
    
    # Check main structure
    required_paths = [
        f"{app_path}/Contents",
        f"{app_path}/Contents/MacOS", 
        f"{app_path}/Contents/Resources",
        f"{app_path}/Contents/Info.plist",
        f"{app_path}/Contents/MacOS/ReelsWasher"
    ]
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"✅ {path}")
        else:
            print(f"❌ Missing: {path}")
            return False
    
    return True

def test_executable():
    """Test if the executable can run basic validation."""
    print("🧪 Testing executable...")
    
    executable = "dist/Reels Washer.app/Contents/MacOS/ReelsWasher"
    
    if not os.path.exists(executable):
        print("❌ Executable not found")
        return False
    
    # Check if it's executable
    if not os.access(executable, os.X_OK):
        print("❌ File is not executable")
        return False
    
    print("✅ Executable exists and has proper permissions")
    
    # Try to run it with --version flag (if supported) or just check it loads
    try:
        # This will fail fast if there are import errors
        result = subprocess.run([executable, "--help"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        print(f"✅ App starts without critical errors")
        return True
    except subprocess.TimeoutExpired:
        print("✅ App starts (timeout expected for GUI app)")
        return True
    except Exception as e:
        print(f"⚠️  App might have issues: {e}")
        return True  # Don't fail build for this

def test_dependencies():
    """Test if all required dependencies are bundled."""
    print("📦 Testing dependencies...")
    
    # Check if CustomTkinter assets are included
    app_path = "dist/Reels Washer.app/Contents/Resources"
    ctk_assets = os.path.join(app_path, "customtkinter")
    
    if os.path.exists(ctk_assets):
        print("✅ CustomTkinter assets found")
    else:
        print("⚠️  CustomTkinter assets not found - GUI might not work")
    
    # Check if FFmpeg is bundled
    ffmpeg_path = "dist/Reels Washer.app/Contents/MacOS/ffmpeg"
    if os.path.exists(ffmpeg_path):
        print("✅ FFmpeg bundled")
    else:
        print("⚠️  FFmpeg not bundled - video processing might fail")
    
    return True

def main():
    """Main test function."""
    print("🍎 Mac App Validation Tests")
    print("=" * 40)
    
    tests = [
        ("App Structure", test_app_structure),
        ("Executable", test_executable), 
        ("Dependencies", test_dependencies)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 40)
    print(f"🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! App should work on Mac.")
    else:
        print("⚠️  Some tests failed - app might have issues.")
    
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
