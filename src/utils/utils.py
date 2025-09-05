from tkinter import filedialog
import os

def browse_output_folder():
    """Open a dialog to select an output folder."""
    return filedialog.askdirectory()

def select_file_dialog(filetypes=(('All files', '*.*'),)):
    """Open a dialog to select a file (video/gif)."""
    return filedialog.askopenfilename(filetypes=filetypes)

def set_label_text(label, text):
    """Set the text of a label widget."""
    label.configure(text=text)

def ensure_output_folder_exists(folder_path):
    """Create the output folder if it does not exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def open_folder_in_explorer(folder_path):
    """Open the given folder in the system file explorer."""
    import sys
    import subprocess
    
    if os.path.exists(folder_path):
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", folder_path])
        else:  # Linux
            subprocess.run(["xdg-open", folder_path])

def set_slider_value(slider, value):
    """Set the value of a slider widget."""
    slider.set(value)
