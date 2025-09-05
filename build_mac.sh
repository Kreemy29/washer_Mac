#!/bin/bash
# Content Spoofer Desktop - Mac Build Script
# Simple shell script for Mac users

echo "🍎 Content Spoofer Desktop - Mac Builder"
echo "========================================"
echo ""

# Check if on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is for macOS only"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Install with: brew install python3"
    exit 1
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is required. Install with: brew install ffmpeg"
    echo ""
    echo "Run this command and then try again:"
    echo "brew install ffmpeg"
    exit 1
fi

echo "✅ All prerequisites found!"
echo ""
echo "🔨 Building application..."

# Run the Python build script
python3 build_mac.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Build completed successfully!"
    echo "📁 Your app is in: dist/ReelsWasher/"
    echo "🚀 Run it with: ./dist/ReelsWasher/ReelsWasher"
    echo ""
    echo "Opening the build folder..."
    open dist/ReelsWasher/
else
    echo ""
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi
