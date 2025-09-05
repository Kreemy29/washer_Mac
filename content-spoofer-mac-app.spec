# -*- mode: python ; coding: utf-8 -*-
"""
Mac App Bundle Builder for Reels Washer
Creates a proper .app bundle that Mac users can double-click
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata
import customtkinter

# Get paths
current_dir = os.path.abspath('.')
main_script = 'main.py'

# Comprehensive CustomTkinter collection
def collect_customtkinter():
    """Collect all CustomTkinter files and dependencies."""
    datas = []
    hiddenimports = []
    
    # Get CustomTkinter path
    ctk_path = os.path.dirname(customtkinter.__file__)
    
    # Add all data files
    try:
        ctk_data = collect_data_files('customtkinter')
        datas.extend(ctk_data)
    except Exception as e:
        print(f"Warning collecting CustomTkinter data: {e}")
    
    # Add assets and themes
    for subdir in ['assets', 'assets/themes']:
        assets_path = os.path.join(ctk_path, subdir)
        if os.path.exists(assets_path):
            datas.append((assets_path, f'customtkinter/{subdir}'))
    
    # Collect submodules
    try:
        ctk_modules = collect_submodules('customtkinter')
        hiddenimports.extend(ctk_modules)
    except Exception as e:
        print(f"Warning collecting CustomTkinter modules: {e}")
    
    # Add metadata
    try:
        metadata = copy_metadata('customtkinter')
        datas.extend(metadata)
    except Exception as e:
        print(f"Warning collecting CustomTkinter metadata: {e}")
    
    return datas, hiddenimports

# Get CustomTkinter files
ctk_datas, ctk_hiddenimports = collect_customtkinter()

# Data files
datas = [
    ('src', 'src'),
    ('README.md', '.'),
]

# Add FFmpeg binaries for Mac
ffmpeg_binaries = []
for cmd in ['ffmpeg', 'ffprobe', 'ffplay']:
    # Try to find system FFmpeg
    import subprocess
    try:
        result = subprocess.run(['which', cmd], capture_output=True, text=True)
        if result.returncode == 0:
            ffmpeg_path = result.stdout.strip()
            ffmpeg_binaries.append((ffmpeg_path, '.'))
            datas.append((ffmpeg_path, '.'))
    except:
        pass

# Add CustomTkinter data
datas.extend(ctk_datas)

# Hidden imports - comprehensive list
hiddenimports = [
    'customtkinter',
    'customtkinter.windows',
    'customtkinter.windows.widgets',
    'customtkinter.windows.ctk_tk',
    'customtkinter.windows.ctk_toplevel',
    'customtkinter.widgets',
    'customtkinter.widgets.ctk_button',
    'customtkinter.widgets.ctk_canvas',
    'customtkinter.widgets.ctk_checkbox',
    'customtkinter.widgets.ctk_combobox',
    'customtkinter.widgets.ctk_entry',
    'customtkinter.widgets.ctk_frame',
    'customtkinter.widgets.ctk_label',
    'customtkinter.widgets.ctk_optionmenu',
    'customtkinter.widgets.ctk_progressbar',
    'customtkinter.widgets.ctk_radiobutton',
    'customtkinter.widgets.ctk_scrollable_frame',
    'customtkinter.widgets.ctk_scrollbar',
    'customtkinter.widgets.ctk_slider',
    'customtkinter.widgets.ctk_switch',
    'customtkinter.widgets.ctk_tabview',
    'customtkinter.widgets.ctk_textbox',
    'customtkinter.widgets.font',
    'customtkinter.appearance_mode_tracker',
    'customtkinter.theme_manager',
    'customtkinter.settings',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageEnhance',
    'PIL.ImageFilter',
    'PIL.ImageDraw',
    'PIL._imaging',
    'PIL._imagingft',
    'cv2',
    'numpy',
    'moviepy',
    'moviepy.editor',
    'ffmpeg',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.font',
    'tkinter.ttk',
    '_tkinter',
    'src.core.process',
    'src.core.washer_controller',
    'src.ui.gui',
    'src.utils.utils',
]

# Add collected CustomTkinter modules
hiddenimports.extend(ctk_hiddenimports)

# Analysis
a = Analysis(
    [main_script],
    pathex=[current_dir],
    binaries=ffmpeg_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy', 
        'pandas',
        'jupyter',
        'notebook',
        'tkinter.test',
        'test',
        'unittest',
    ],
    noarchive=False,
)

# Remove duplicates
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
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
    console=False,  # GUI app, no console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Create app bundle
app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Reels Washer.app',
    icon=None,  # Add icon path here if you have one
    bundle_identifier='com.reelswasher.app',
    version='1.0.0',
    info_plist={
        'CFBundleDisplayName': 'Reels Washer',
        'CFBundleName': 'Reels Washer',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSRequiresAquaSystemAppearance': False,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
    },
)
