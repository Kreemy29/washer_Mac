# Content Spoofer Desktop - macOS Build Guide

## 🍎 Building for macOS

This guide explains how to build the Content Spoofer Desktop application for macOS.

## Prerequisites

### 1. Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install FFmpeg
```bash
brew install ffmpeg
```

### 3. Install Python 3.8+
```bash
brew install python3
```

### 4. Verify installations
```bash
python3 --version
ffmpeg -version
ffprobe -version
ffplay -version
```

## Build Process

### Option 1: Automated Build (Recommended)
```bash
python3 build_mac.py
```

### Option 2: Manual Build
```bash
# Install dependencies
pip3 install -r requirements.txt
pip3 install pyinstaller

# Build the app
pyinstaller --clean content-spoofer-mac.spec
```

## Output

After building, you'll find your application in:
```
dist/ReelsWasher/
├── ReelsWasher              # Main executable
├── _internal/               # Python runtime and dependencies
├── ffmpeg -> /usr/local/bin/ffmpeg    # Symlink to system FFmpeg
├── ffprobe -> /usr/local/bin/ffprobe  # Symlink to system FFprobe
├── ffplay -> /usr/local/bin/ffplay    # Symlink to system FFplay
├── src/                     # Source code
├── output/                  # Generated files folder
└── README.md                # Documentation
```

## Running the Application

### From Terminal
```bash
./dist/ReelsWasher/ReelsWasher
```

### Create .app Bundle (Optional)
To create a proper macOS .app bundle:

1. Create the bundle structure:
```bash
mkdir -p "ReelsWasher.app/Contents/MacOS"
mkdir -p "ReelsWasher.app/Contents/Resources"
```

2. Copy the executable:
```bash
cp -r dist/ReelsWasher/* "ReelsWasher.app/Contents/MacOS/"
```

3. Create Info.plist:
```bash
cat > "ReelsWasher.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>ReelsWasher</string>
    <key>CFBundleIdentifier</key>
    <string>com.contentspoofer.reelswasher</string>
    <key>CFBundleName</key>
    <string>Reels Washer</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF
```

## Troubleshooting

### FFmpeg Not Found
```bash
# Install FFmpeg
brew install ffmpeg

# Verify installation
which ffmpeg
```

### Permission Issues
```bash
# Make executable
chmod +x dist/ReelsWasher/ReelsWasher

# If blocked by Gatekeeper
xattr -d com.apple.quarantine ReelsWasher.app
```

### CustomTkinter Issues
```bash
# Reinstall CustomTkinter
pip3 uninstall customtkinter
pip3 install customtkinter
```

### Memory Issues
- Ensure you have at least 4GB free RAM
- Close other applications during build

## Distribution

To distribute your macOS app:

1. **Zip the .app bundle** (maintains file permissions)
2. **Code sign** (for distribution outside App Store)
3. **Notarize** (for macOS 10.15+)

### Code Signing (Optional)
```bash
# Sign the app (requires Apple Developer account)
codesign --deep --sign "Developer ID Application: Your Name" ReelsWasher.app
```

## Performance Notes

- **Startup time**: 2-4 seconds (depending on Mac model)
- **Memory usage**: 60-120 MB base + video processing overhead
- **Compatible with**: macOS 10.14+ (Intel and Apple Silicon)

## Differences from Windows Version

- Uses system FFmpeg instead of bundled executables
- Cross-platform file explorer opening
- Native macOS file dialogs
- Optimized for Retina displays

---

**Happy building! 🎉**

Your Content Spoofer Desktop is now ready for macOS users.
