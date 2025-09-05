# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import copy_metadata

# Get the current directory
current_dir = os.path.abspath('.')

# Define paths
main_script = 'main.py'
src_dir = os.path.join(current_dir, 'src')

# Data files to include for Mac
datas = [
    # FFmpeg executables (no .exe extension on Mac)
    ('ffmpeg', '.'),
    ('ffplay', '.'), 
    ('ffprobe', '.'),
    # Source files
    ('src', 'src'),
    # README for reference
    ('README.md', '.'),
]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'customtkinter',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageEnhance',
    'PIL.ImageFilter',
    'PIL.ImageDraw',
    'cv2',
    'numpy',
    'moviepy',
    'moviepy.editor',
    'moviepy.video.io.VideoFileClip',
    'moviepy.video.VideoClip',
    'ffmpeg',
    'subprocess',
    'threading',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'src.core.process',
    'src.core.washer_controller',
    'src.ui.gui',
    'src.utils.utils',
]

# Binaries (external executables) for Mac
binaries = [
    ('ffmpeg', '.'),
    ('ffplay', '.'),
    ('ffprobe', '.'),
]

# Collect CustomTkinter assets
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    datas.append((os.path.join(ctk_path, 'assets'), 'customtkinter/assets'))
except ImportError:
    pass

# Collect metadata for packages that need it
try:
    datas += copy_metadata('customtkinter')
except Exception:
    pass

a = Analysis(
    [main_script],
    pathex=[current_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude heavy unused packages
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'tkinter.test',
    ],
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ReelsWasher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False for GUI-only app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add .icns icon here for Mac
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ReelsWasher',
)
