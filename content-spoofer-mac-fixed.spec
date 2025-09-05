# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata
import customtkinter

# Get the current directory
current_dir = os.path.abspath('.')

# Define paths
main_script = 'main.py'
src_dir = os.path.join(current_dir, 'src')

# Collect ALL CustomTkinter files and data (comprehensive approach)
def collect_customtkinter():
    """Collect all CustomTkinter files and dependencies for macOS."""
    datas = []
    hiddenimports = []
    
    # Get CustomTkinter path
    ctk_path = os.path.dirname(customtkinter.__file__)
    
    # Add all CustomTkinter data files recursively
    try:
        ctk_data = collect_data_files('customtkinter')
        datas.extend(ctk_data)
        print(f"✅ Collected {len(ctk_data)} CustomTkinter data files")
    except Exception as e:
        print(f"⚠️  Warning collecting CustomTkinter data: {e}")
    
    # Add CustomTkinter assets specifically
    assets_src = os.path.join(ctk_path, 'assets')
    if os.path.exists(assets_src):
        datas.append((assets_src, 'customtkinter/assets'))
        print(f"✅ Added CustomTkinter assets from: {assets_src}")
    
    # Add themes directory
    themes_src = os.path.join(ctk_path, 'assets', 'themes')
    if os.path.exists(themes_src):
        datas.append((themes_src, 'customtkinter/assets/themes'))
        print(f"✅ Added CustomTkinter themes")
    
    # Collect all CustomTkinter submodules
    try:
        ctk_modules = collect_submodules('customtkinter')
        hiddenimports.extend(ctk_modules)
        print(f"✅ Added {len(ctk_modules)} CustomTkinter modules")
    except Exception as e:
        print(f"⚠️  Warning collecting CustomTkinter modules: {e}")
    
    # Collect metadata
    try:
        metadata = copy_metadata('customtkinter')
        datas.extend(metadata)
        print(f"✅ Added CustomTkinter metadata")
    except Exception as e:
        print(f"⚠️  Warning collecting CustomTkinter metadata: {e}")
    
    return datas, hiddenimports

# Get CustomTkinter files
ctk_datas, ctk_hiddenimports = collect_customtkinter()

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

# Add CustomTkinter files
datas.extend(ctk_datas)

# Hidden imports (modules that PyInstaller might miss)
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
    'moviepy.video.io.VideoFileClip',
    'moviepy.video.VideoClip',
    'ffmpeg',
    'subprocess',
    'threading',
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

# Binaries (external executables) for Mac
binaries = [
    ('ffmpeg', '.'),
    ('ffplay', '.'),
    ('ffprobe', '.'),
]

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
        'test',
        'unittest',
        'pydoc_data',
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
    debug=False,  # Set to True for debugging
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging (shows console)
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


