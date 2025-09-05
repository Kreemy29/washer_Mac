#!/usr/bin/env python3
"""
Reels Washer - Video/GIF Processing Application
A tool for applying various effects to videos and creating "washed" versions.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
from src.ui.gui import ReelsWasherApp

def main():
    """Main entry point for the application."""
    # Set up CustomTkinter appearance
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    try:
        # Create and run the application
        app = ReelsWasherApp()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 