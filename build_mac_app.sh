#!/bin/bash

echo "🍎 Building Professional Mac App for Reels Washer"
echo "================================================"

# Check if on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script must be run on macOS"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check required files
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    echo "❌ Missing required files"
    exit 1
fi

echo "✅ Required files found"

# Install system dependencies
echo "📦 Installing system dependencies..."
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

brew install create-dmg ffmpeg

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install customtkinter==5.2.0
pip install -r requirements.txt
pip install pyinstaller

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.app venv

# Create fresh virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install customtkinter==5.2.0
pip install -r requirements.txt
pip install pyinstaller

# Build the app
echo "🔨 Building Mac app..."
pyinstaller --clean --noconfirm content-spoofer-mac-app.spec

# Check if build successful
if [ ! -d "dist/Reels Washer.app" ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ App built successfully!"

# Create DMG installer
echo "📦 Creating professional installer..."
create-dmg \
    --volname "Reels Washer Installer" \
    --volicon "dist/Reels Washer.app/Contents/Resources/icon.icns" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "Reels Washer.app" 200 190 \
    --hide-extension "Reels Washer.app" \
    --app-drop-link 600 190 \
    --hdiutil-verbose \
    "Reels Washer Installer.dmg" \
    "dist/Reels Washer.app" 2>/dev/null || {
    
    echo "⚠️  DMG creation failed, creating ZIP instead..."
    cd dist
    zip -r "../Reels Washer.zip" "Reels Washer.app"
    cd ..
}

# Create simple ZIP as backup
cd dist
zip -r "../Reels Washer - Simple.zip" "Reels Washer.app"
cd ..

echo ""
echo "🎉 BUILD COMPLETE!"
echo "=================="

if [ -f "Reels Washer Installer.dmg" ]; then
    echo "📀 Professional installer: Reels Washer Installer.dmg"
fi

if [ -f "Reels Washer.zip" ]; then
    echo "📦 ZIP file: Reels Washer.zip"
fi

echo "📦 Simple ZIP: Reels Washer - Simple.zip"
echo ""
echo "📧 Send ANY of these files to your Mac user:"
echo "   • They double-click the DMG and drag to Applications"
echo "   • OR they unzip and double-click 'Reels Washer.app'"
echo "   • NO terminal commands needed!"
echo ""
echo "✨ Professional Mac app ready to distribute!"
