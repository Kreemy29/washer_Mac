# 🍎 CONTENT SPOOFER DESKTOP - MAC BUILD INSTRUCTIONS

## Quick Start for Mac Users

This package contains everything needed to build Content Spoofer Desktop on macOS.

### 1️⃣ Install Prerequisites

Open Terminal and run these commands:

```bash
# Install Homebrew (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg

# Verify installations
python3 --version  # Should be 3.8+
ffmpeg -version    # Should show FFmpeg info
```

### 2️⃣ Build the Application

```bash
# Navigate to the project folder
cd /path/to/content-spoofer-desktop

# Run the Mac build script
python3 build_mac.py
```

That's it! 🎉

### 3️⃣ Run Your Application

```bash
# After building, run:
./dist/ReelsWasher/ReelsWasher
```

## 📁 What You'll Get

```
dist/ReelsWasher/
├── ReelsWasher              # ← Your main app!
├── _internal/               # Python runtime
├── ffmpeg, ffprobe, ffplay  # Video processing tools
├── src/                     # Source code
└── output/                  # Where processed videos go
```

## 🚀 Features That Work on Mac

- ✅ **Modern GUI** - Native macOS look and feel
- ✅ **Video Processing** - All effects work perfectly  
- ✅ **File Operations** - Mac-native file dialogs
- ✅ **Drag & Drop** - (coming soon)
- ✅ **Retina Support** - Crisp on high-DPI displays

## 🔧 If Something Goes Wrong

### FFmpeg Not Found?
```bash
brew install ffmpeg
```

### Python Issues?
```bash
# Use Python 3.8+
python3 --version

# Install dependencies manually
pip3 install -r requirements.txt
```

### Permission Issues?
```bash
# Make executable
chmod +x dist/ReelsWasher/ReelsWasher
```

### Build Fails?
```bash
# Clean and retry
rm -rf build dist __pycache__
python3 build_mac.py
```

## 📧 Need Help?

The build process is automated and should "just work" on Mac. If you run into issues:

1. Check the error messages carefully
2. Make sure you have FFmpeg installed (`brew install ffmpeg`)
3. Try the manual build: `pyinstaller content-spoofer-mac.spec`

## 🎯 File Structure

```
Project Files:
├── build_mac.py              # ← Run this to build!
├── content-spoofer-mac.spec  # Mac build configuration  
├── main.py                   # App entry point
├── requirements.txt          # Dependencies
├── src/                      # Source code
└── README_MAC.md            # Detailed Mac guide
```

---

**Happy building! Your Mac users will love this app! 🚀**
