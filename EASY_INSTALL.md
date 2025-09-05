# 🍎 Reels Washer - EASY Mac Installation

## ⚡ One-Click Method (RECOMMENDED)

1. **Extract the ContentSpoofer-Mac.zip** to your Desktop
2. **Open Terminal** (press `Cmd + Space`, type "Terminal", press Enter)
3. **Run this command:**
   ```bash
   cd ~/Desktop/ContentSpoofer-Mac && chmod +x auto_install.sh && ./auto_install.sh
   ```
4. **Wait 5-10 minutes** - it will install everything automatically
5. **Double-click the app** when it's done: `Desktop/ContentSpoofer-Mac/dist/ReelsWasher/ReelsWasher`

That's it! 🎉

---

## ❌ If Something Goes Wrong

### Option 1: Try the manual method
```bash
cd ~/Desktop/ContentSpoofer-Mac
python3 build_mac_fixed.py
```

### Option 2: Check what's missing
```bash
cd ~/Desktop/ContentSpoofer-Mac
ls -la
# Should see: main.py, requirements.txt, src/ folder
```

---

## 🆘 Still Not Working?

**Send your developer this error log:**
```bash
cd ~/Desktop/ContentSpoofer-Mac
./auto_install.sh > install_log.txt 2>&1
# Then send the install_log.txt file
```

