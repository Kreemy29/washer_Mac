import threading
import os
import cv2
from PIL import Image, ImageTk
from src.core.process import generate_washed_media, stop_generation, apply_quick_wash_preset
from src.utils.utils import browse_output_folder, open_folder_in_explorer, ensure_output_folder_exists


class WasherController:
    """Controller class to connect GUI with backend processing."""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.current_video_path = None
        self.is_processing = False
        self.processing_thread = None
        
    def get_video_info_and_thumbnail(self, video_path):
        """Get video info and extract first frame as thumbnail."""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return None, None
            
            # Get basic properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            duration = frame_count / fps if fps > 0 else 0
            
            # Extract first frame for thumbnail
            ret, frame = cap.read()
            thumbnail = None
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize to fit preview area (maintain aspect ratio)
                preview_width = 400
                preview_height = 200
                
                # Calculate aspect ratio
                aspect_ratio = width / height
                if aspect_ratio > preview_width / preview_height:
                    # Width is limiting factor
                    new_width = preview_width
                    new_height = int(preview_width / aspect_ratio)
                else:
                    # Height is limiting factor
                    new_height = preview_height
                    new_width = int(preview_height * aspect_ratio)
                
                # Resize image
                thumbnail = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            cap.release()
            
            info = {
                'fps': round(fps, 2),
                'duration': round(duration, 2),
                'resolution': f"{width}x{height}",
                'frame_count': frame_count,
                'width': width,
                'height': height
            }
            
            return info, thumbnail
            
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None, None

    def select_video_and_show_info(self):
        """Handle video selection and display info with thumbnail."""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Video/GIF File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v"),
                ("GIF files", "*.gif"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            self.current_video_path = file_path
            
            # Update file label and prefix
            filename = os.path.basename(file_path)
            video_name = os.path.splitext(filename)[0]  # Remove extension
            self.gui.file_label.configure(text=filename)
            self.gui.prefix_var.set(video_name)
            
            # Get video info and thumbnail
            info, thumbnail = self.get_video_info_and_thumbnail(file_path)
            
            if info and thumbnail:
                # Convert PIL image to PhotoImage for tkinter
                photo = ImageTk.PhotoImage(thumbnail)
                
                # Update preview label to show image
                self.gui.preview_label.configure(image=photo, text="")
                self.gui.preview_label.image = photo  # Keep a reference
                
                # Show video info in the GUI
                info_text = f"📹 {info['resolution']} • {info['fps']} FPS • {info['duration']:.1f}s"
                self.gui.video_info_label.configure(text=info_text)
                self.gui.video_info_frame.pack(fill="x", padx=10, pady=(0, 10))
                
                # Update FPS info for output settings
                self.gui.output_fps_var.set(f"Original: {info['fps']} FPS")
                
                # Show detailed info popup
                info_text = f"File: {filename}\n"
                info_text += f"Duration: {info['duration']:.1f} seconds\n"
                info_text += f"Frame Rate: {info['fps']} FPS\n"
                info_text += f"Resolution: {info['resolution']}\n"
                info_text += f"Total Frames: {info['frame_count']}"
                
                self._show_info_popup("Video Information", info_text)
                
            elif info:
                # Fallback to text if thumbnail extraction failed
                preview_text = f"📹 {filename}\n"
                preview_text += f"Duration: {info['duration']:.1f}s\n"
                preview_text += f"FPS: {info['fps']}\n"
                preview_text += f"Resolution: {info['resolution']}\n"
                preview_text += f"Frames: {info['frame_count']}"
                
                self.gui.preview_label.configure(text=preview_text, image="")
                self.gui.preview_label.image = None
                
                # Show video info in the GUI
                info_text = f"📹 {info['resolution']} • {info['fps']} FPS • {info['duration']:.1f}s"
                self.gui.video_info_label.configure(text=info_text)
                self.gui.video_info_frame.pack(fill="x", padx=10, pady=(0, 10))
                
                # Update FPS info
                self.gui.output_fps_var.set(f"Original: {info['fps']} FPS")
                
            else:
                # Complete fallback for unsupported formats
                preview_text = f"📁 {filename}\n"
                preview_text += "File selected successfully\n"
                preview_text += "Ready for processing"
                
                self.gui.preview_label.configure(text=preview_text, image="")
                self.gui.preview_label.image = None
                self._show_info_popup("File Selected", f"Selected: {filename}\nReady for processing!")
                
        except Exception as e:
            self._show_error_popup("Error", f"Failed to load video: {str(e)}")
    
    def browse_output_folder(self):
        """Handle output folder selection."""
        folder = browse_output_folder()
        if folder:
            self.gui.output_folder = folder
            self.gui.output_label.configure(text=folder)
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        try:
            ensure_output_folder_exists(self.gui.output_folder)
            open_folder_in_explorer(self.gui.output_folder)
        except Exception as e:
            self._show_error_popup("Error", f"Could not open folder: {str(e)}")
    
    def generate_media(self, variation=False, bulk=False):
        """Generate washed media with current settings."""
        if not self.current_video_path:
            self._show_error_popup("Error", "Please select a video file first.")
            return
        
        if self.is_processing:
            self._show_error_popup("Error", "Processing already in progress.")
            return
        
        try:
            # Get settings from GUI
            output_mode = self.gui.output_mode_var.get()
            output_folder = self.gui.output_folder
            prefix = self.gui.prefix_var.get()
            
            # Use entire video (no time controls)
            start_time = 0.0
            end_time = None  # Process entire video
            
            # Output settings
            if output_mode == 'gif':
                fps = self.gui.fps_var.get()
                quality = self.gui.quality_var.get()
                codec = None
                bitrate = None
            else:
                fps = None
                quality = None
                codec = self.gui.codec_var.get()
                bitrate = self.gui.bitrate_var.get()
            
            # Generation settings
            if bulk:
                copies = 10  # Default bulk amount
            else:
                copies = self.gui.copies_var.get()
            
            speed_str = self.gui.speed_var.get().replace('x', '')
            try:
                speed = float(speed_str)
            except:
                speed = 1.0
            
            copy_type = self.gui.copy_type_var.get()
            
            # Get effect variables
            effect_vars = self._get_effect_variables()
            
            # Start processing in thread
            self.processing_thread = threading.Thread(
                target=self._process_media_thread,
                args=(output_mode, output_folder, prefix, effect_vars, start_time, end_time,
                      fps, quality, codec, bitrate, copies, speed, copy_type)
            )
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
        except Exception as e:
            self._show_error_popup("Error", f"Failed to start processing: {str(e)}")
    
    def stop_processing(self):
        """Stop the current processing operation."""
        if self.is_processing:
            stop_generation()
            self.is_processing = False
            self.gui.generate_button.configure(state="normal")
            self.gui.stop_button.configure(state="disabled")
    
    def apply_quick_wash(self, wash_type):
        """Apply quick wash presets."""
        try:
            effect_vars = self._get_effect_variables()
            apply_quick_wash_preset(effect_vars, wash_type)
            
            # Update effects status
            self.gui.update_effects_status()
            
            self._show_info_popup("Quick Wash Applied", f"{wash_type.title()} wash preset has been applied.")
            
        except Exception as e:
            self._show_error_popup("Error", f"Failed to apply quick wash: {str(e)}")
    
    def reset_effects(self):
        """Reset all effects to default values."""
        try:
            # Reset all effect checkboxes
            self.gui.brightness_enabled.set(False)
            self.gui.contrast_enabled.set(False)
            self.gui.saturation_enabled.set(False)
            self.gui.hue_enabled.set(False)
            self.gui.blur_enabled.set(False)
            self.gui.resize_enabled.set(False)
            self.gui.noise_enabled.set(False)
            self.gui.fps_change_enabled.set(False)
            self.gui.audio_fingerprint_enabled.set(False)
            self.gui.region_enabled.set(False)
            self.gui.bitplane_enabled.set(False)
            self.gui.overlay_enabled.set(False)
            self.gui.shadow_enabled.set(False)
            self.gui.clipping_enabled.set(False)
            self.gui.flip_enabled.set(False)
            
            # Reset values to defaults (only for effects that still have controls)
            # FFmpeg effects have no controls to reset - they use predefined ranges
            
            # PIL effects
            self.gui.bitplane_intensity_var.set(0.5)
            self.gui.bitplane_planes_var.set(1)
            self.gui.shadow_h_lines_var.set(0)
            self.gui.shadow_v_lines_var.set(0)
            self.gui.shadow_intensity_var.set(0.1)
            self.gui.shadow_line_width_var.set(1)
            self.gui.shadow_speed_var.set(0.5)
            
            # Video effects  
            self.gui.clipping_min_var.set(5.0)
            self.gui.clipping_max_var.set(10.0)
            
            self.gui.update_effects_status()
            
        except Exception as e:
            print(f"Error resetting effects: {e}")
    
    def _process_media_thread(self, output_mode, output_folder, prefix, effect_vars,
                             start_time, end_time, fps, quality, codec, bitrate,
                             copies, speed, copy_type):
        """Thread function for media processing."""
        self.is_processing = True
        
        # Update GUI
        self.gui.after(0, lambda: self.gui.generate_button.configure(state="disabled"))
        self.gui.after(0, lambda: self.gui.stop_button.configure(state="normal"))
        
        def progress_callback(current, total):
            progress = int((current / total) * 100)
            self.gui.after(0, lambda: self._update_status(f"Processing frames: {current}/{total} ({progress}%)"))
        
        def status_callback(status):
            self.gui.after(0, lambda: self._update_status(status))
        
        try:
            success = generate_washed_media(
                self.current_video_path, output_folder, prefix, output_mode,
                effect_vars, start_time, end_time, fps, quality, codec, bitrate,
                copies, speed, copy_type, progress_callback, status_callback
            )
            
            if success:
                self.gui.after(0, lambda: self._show_info_popup("Success", f"Successfully generated {copies} {output_mode} file(s)!"))
            else:
                self.gui.after(0, lambda: self._show_error_popup("Error", "Failed to generate media files."))
                
        except Exception as e:
            self.gui.after(0, lambda: self._show_error_popup("Error", f"Processing failed: {str(e)}"))
        
        finally:
            self.is_processing = False
            self.gui.after(0, lambda: self.gui.generate_button.configure(state="normal"))
            self.gui.after(0, lambda: self.gui.stop_button.configure(state="disabled"))
            self.gui.after(0, lambda: self._update_status("Ready"))
    
    def _get_effect_variables(self):
        """Get effect variables from GUI."""
        return {
            # FFmpeg effects (simple checkboxes only)
            'brightness_enabled': self.gui.brightness_enabled,
            'contrast_enabled': self.gui.contrast_enabled,
            'saturation_enabled': self.gui.saturation_enabled,
            'hue_enabled': self.gui.hue_enabled,
            'blur_enabled': self.gui.blur_enabled,
            'resize_enabled': self.gui.resize_enabled,
            'noise_enabled': self.gui.noise_enabled,
            'fps_change_enabled': self.gui.fps_change_enabled,
            'audio_fingerprint_enabled': self.gui.audio_fingerprint_enabled,
            
            # PIL effects (still have controls)
            'region_enabled': self.gui.region_enabled,
            'region_x_var': self.gui.region_x_var,
            'region_y_var': self.gui.region_y_var,
            'region_width_var': self.gui.region_width_var,
            'region_height_var': self.gui.region_height_var,
            'bitplane_enabled': self.gui.bitplane_enabled,
            'bitplane_intensity_var': self.gui.bitplane_intensity_var,
            'bitplane_planes_var': self.gui.bitplane_planes_var,
            'overlay_enabled': self.gui.overlay_enabled,
            'frame_overlay_interval': self.gui.frame_overlay_interval,
            'shadow_enabled': self.gui.shadow_enabled,
            'shadow_h_lines_var': self.gui.shadow_h_lines_var,
            'shadow_v_lines_var': self.gui.shadow_v_lines_var,
            'shadow_intensity_var': self.gui.shadow_intensity_var,
            'shadow_line_width_var': self.gui.shadow_line_width_var,
            'shadow_speed_var': self.gui.shadow_speed_var,
            
            # Video effects (still have controls)
            'clipping_enabled': self.gui.clipping_enabled,
            'clipping_min_var': self.gui.clipping_min_var,
            'clipping_max_var': self.gui.clipping_max_var,
            'flip_enabled': self.gui.flip_enabled,
        }
    
    def _update_status(self, status):
        """Update status in GUI."""
        try:
            self.gui.effects_status_var.set(status)
        except:
            pass
    
    def _show_info_popup(self, title, message):
        """Show information popup."""
        try:
            import customtkinter as ctk
            popup = ctk.CTkToplevel(self.gui)
            popup.title(title)
            popup.geometry("400x200")
            popup.transient(self.gui)
            popup.grab_set()
            
            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (400 // 2)
            y = (popup.winfo_screenheight() // 2) - (200 // 2)
            popup.geometry(f"400x200+{x}+{y}")
            
            # Message label
            label = ctk.CTkLabel(popup, text=message, wraplength=350, justify="left")
            label.pack(pady=20, padx=20, expand=True)
            
            # OK button
            ok_button = ctk.CTkButton(popup, text="OK", command=popup.destroy)
            ok_button.pack(pady=10)
            
        except Exception as e:
            print(f"Error showing info popup: {e}")
    
    def _show_error_popup(self, title, message):
        """Show error popup."""
        try:
            import customtkinter as ctk
            popup = ctk.CTkToplevel(self.gui)
            popup.title(title)
            popup.geometry("400x200")
            popup.transient(self.gui)
            popup.grab_set()
            
            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (400 // 2)
            y = (popup.winfo_screenheight() // 2) - (200 // 2)
            popup.geometry(f"400x200+{x}+{y}")
            
            # Error message label
            label = ctk.CTkLabel(popup, text=message, wraplength=350, justify="left", text_color="red")
            label.pack(pady=20, padx=20, expand=True)
            
            # OK button
            ok_button = ctk.CTkButton(popup, text="OK", command=popup.destroy)
            ok_button.pack(pady=10)
            
        except Exception as e:
            print(f"Error showing error popup: {e}") 