#!/bin/bash

echo "🍎 Reels Washer - One-Click Mac Installer"
echo "=========================================="

# Check if we're on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is for Mac only"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working in: $SCRIPT_DIR"

# Check if required files exist
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    echo "❌ Missing required files. Make sure you're in the ContentSpoofer-Mac directory"
    echo "   Should contain: main.py, requirements.txt, src/ folder"
    exit 1
fi

echo "✅ Required files found"

# Install Homebrew if not installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew already installed"
fi

# Install FFmpeg
echo "🎬 Installing FFmpeg..."
brew install ffmpeg

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "🐍 Installing Python..."
    brew install python
else
    echo "✅ Python3 found: $(python3 --version)"
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist __pycache__ venv
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Create virtual environment
echo "🏗️  Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python packages..."
pip install customtkinter==5.2.0
pip install -r requirements.txt
pip install --upgrade pyinstaller

# Test CustomTkinter
echo "🧪 Testing CustomTkinter..."
python3 -c "
import customtkinter as ctk
print('✅ CustomTkinter version:', ctk.__version__)
ctk.set_appearance_mode('System')
root = ctk.CTk()
root.withdraw()
root.destroy()
print('✅ CustomTkinter test passed')
"

# Build the app
echo "🔨 Building Reels Washer..."
python -m PyInstaller --clean --noconfirm content-spoofer-mac-fixed.spec

# Check if build succeeded
if [ -f "dist/ReelsWasher/ReelsWasher" ]; then
    # Make executable
    chmod +x dist/ReelsWasher/ReelsWasher
    
    # Create output directory
    mkdir -p dist/ReelsWasher/output
    
    echo ""
    echo "🎉 BUILD SUCCESSFUL!"
    echo "=============================="
    echo "📁 App location: $SCRIPT_DIR/dist/ReelsWasher/"
    echo "🚀 To run: cd dist/ReelsWasher && ./ReelsWasher"
    echo ""
    echo "🖱️  Or double-click: $SCRIPT_DIR/dist/ReelsWasher/ReelsWasher"
    echo ""
    
    # Create desktop launcher
    cat > "$HOME/Desktop/Reels Washer.command" << EOF
#!/bin/bash
cd "$SCRIPT_DIR/dist/ReelsWasher"
./ReelsWasher
EOF
    chmod +x "$HOME/Desktop/Reels Washer.command"
    echo "✅ Desktop shortcut created: ~/Desktop/Reels Washer.command"
    
else
    echo "❌ Build failed!"
    echo "Check the output above for errors."
    exit 1
fi

echo ""
echo "✨ Installation complete! The app is ready to use."

