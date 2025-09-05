import customtkinter as ctk
import random
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))

from src.core.washer_controller import WasherController

class ReelsWasherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Reels Washer GUI")
        self.geometry("1000x800")
        self.resizable(True, True)
        
        # Initialize controller
        self.controller = WasherController(self)
        
        self.tabview = ctk.CTkTabview(self, width=980, height=780)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        self.tab_main = self.tabview.add("Main")
        self.tab_effects = self.tabview.add("Effects")
        self.setup_main_tab()
        self.setup_effects_tab()
        
        # Initialize UI state based on defaults
        self.update_output_mode()
        self.update_copy_type_info()

    def setup_main_tab(self):
        # Main scrollable container
        main_container = ctk.CTkScrollableFrame(self.tab_main, width=960, height=750)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Hero Section - File Selection (most prominent)
        self.create_hero_section(main_container)
        
        # Output selection
        output_frame = ctk.CTkFrame(main_container)
        output_frame.pack(fill="x", pady=5)

        # Progress bar container (initially hidden)
        self.progress_container = ctk.CTkFrame(main_container, corner_radius=10)
        self.progress_label = ctk.CTkLabel(self.progress_container, text="Processing...", font=ctk.CTkFont(size=12, weight="bold"))
        self.progress_label.pack(pady=(10, 5))
        self.progress_bar = ctk.CTkProgressBar(self.progress_container, width=300, height=20)
        self.progress_bar.pack(padx=20, pady=(0, 10))
        self.progress_bar.set(0)

    def create_hero_section(self, parent):
        """Create the prominent file selection hero section"""
        # Large, prominent file selection card
        hero_card = ctk.CTkFrame(parent, height=250, corner_radius=15)
        hero_card.pack(fill="x", padx=20, pady=20)
        
        # App title
        title = ctk.CTkLabel(hero_card, text="🎬 Reels Washer", 
                            font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=(25, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(hero_card, text="Transform your videos with professional wash effects", 
                               font=ctk.CTkFont(size=14), text_color="gray60")
        subtitle.pack(pady=(0, 20))
        
        # File selection area
        file_area = ctk.CTkFrame(hero_card, height=140, corner_radius=12)
        file_area.pack(fill="x", padx=30, pady=(0, 20))
        
        # Big select button
        self.select_btn = ctk.CTkButton(file_area, text="📁 Select Video or GIF", 
                                       command=self.controller.select_video_and_show_info,
                                       height=55, font=ctk.CTkFont(size=16, weight="bold"),
                                       corner_radius=10)
        self.select_btn.pack(pady=(25, 10))
        
        # File info display
        self.file_label = ctk.CTkLabel(file_area, text="No file selected", 
                                      font=ctk.CTkFont(size=12), text_color="gray60")
        self.file_label.pack(pady=(0, 10))
        
        # Video preview display
        preview_frame = ctk.CTkFrame(file_area, corner_radius=8)
        preview_frame.pack(pady=(5, 10), padx=10)
        
        self.preview_label = ctk.CTkLabel(preview_frame, text="No video selected", 
                                         font=ctk.CTkFont(size=10), 
                                         width=400, height=200,
                                         text_color="gray50")
        self.preview_label.pack(padx=10, pady=10)
        
        # Video info display (more compact)
        self.video_info_frame = ctk.CTkFrame(file_area, corner_radius=8)
        self.video_info_label = ctk.CTkLabel(self.video_info_frame, text="", font=ctk.CTkFont(size=10))
        self.video_info_label.pack(padx=10, pady=5)

        # Output selection
        output_frame = ctk.CTkFrame(parent)
        output_frame.pack(fill="x", pady=5)

        # Output mode selection
        mode_frame = ctk.CTkFrame(output_frame)
        mode_frame.pack(fill="x", pady=5)
        mode_label = ctk.CTkLabel(mode_frame, text="Output Mode:")
        mode_label.pack(side="left", padx=5)
        self.output_mode_var = ctk.StringVar(value="video")
        gif_radio = ctk.CTkRadioButton(mode_frame, text="GIF", variable=self.output_mode_var, value="gif", command=self.update_output_mode)
        gif_radio.pack(side="left", padx=5)
        video_radio = ctk.CTkRadioButton(mode_frame, text="Video", variable=self.output_mode_var, value="video", command=self.update_output_mode)
        video_radio.pack(side="left", padx=5)

        # Output folder selection
        folder_frame = ctk.CTkFrame(output_frame)
        folder_frame.pack(fill="x", pady=5)
        folder_label = ctk.CTkLabel(folder_frame, text="Output Folder:")
        folder_label.pack(side="left", padx=5)
        self.output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        self.output_label = ctk.CTkLabel(folder_frame, text=self.output_folder)
        self.output_label.pack(side="left", fill="x", expand=True, padx=5)
        folder_btn = ctk.CTkButton(folder_frame, text="Browse", command=self.controller.browse_output_folder)
        folder_btn.pack(side="left", padx=5)
        open_folder_btn = ctk.CTkButton(folder_frame, text="Open Folder", command=self.controller.open_output_folder)
        open_folder_btn.pack(side="left", padx=5)

        # File name prefix
        name_frame = ctk.CTkFrame(output_frame)
        name_frame.pack(fill="x", pady=5)
        name_label = ctk.CTkLabel(name_frame, text="File Name Prefix:")
        name_label.pack(side="left", padx=5)
        self.prefix_var = ctk.StringVar(value="video")
        prefix_entry = ctk.CTkEntry(name_frame, textvariable=self.prefix_var)
        prefix_entry.pack(side="left", fill="x", expand=True, padx=5)

        # GIF-specific options
        self.gif_options_frame = ctk.CTkFrame(output_frame)
        self.gif_options_frame.pack(fill="x", pady=5)
        fps_frame = ctk.CTkFrame(self.gif_options_frame)
        fps_frame.pack(fill="x", pady=2)
        fps_label = ctk.CTkLabel(fps_frame, text="FPS:")
        fps_label.pack(side="left", padx=5)
        self.fps_var = ctk.IntVar(value=10)
        fps_entry = ctk.CTkEntry(fps_frame, textvariable=self.fps_var, width=80)
        fps_entry.pack(side="left", padx=5)
        quality_frame = ctk.CTkFrame(self.gif_options_frame)
        quality_frame.pack(fill="x", pady=2)
        quality_label = ctk.CTkLabel(quality_frame, text="Quality:")
        quality_label.pack(side="left", padx=5)
        self.quality_var = ctk.IntVar(value=75)
        quality_scale = ctk.CTkSlider(quality_frame, from_=1, to=100, number_of_steps=99, command=lambda v: self.quality_var.set(int(float(v))))
        quality_scale.set(self.quality_var.get())
        quality_scale.pack(side="left", fill="x", expand=True, padx=5)
        quality_value = ctk.CTkLabel(quality_frame, textvariable=self.quality_var)
        quality_value.pack(side="left", padx=5)

        # Video-specific options
        self.video_options_frame = ctk.CTkFrame(output_frame)
        # Not packed by default
        codec_frame = ctk.CTkFrame(self.video_options_frame)
        codec_frame.pack(fill="x", pady=2)
        codec_label = ctk.CTkLabel(codec_frame, text="Codec:")
        codec_label.pack(side="left", padx=5)
        self.codec_var = ctk.StringVar(value="libx264")
        codec_combo = ctk.CTkComboBox(codec_frame, variable=self.codec_var, values=["libx264", "h264_nvenc", "hevc", "hevc_nvenc", "libvpx", "libvpx-vp9"])
        codec_combo.pack(side="left", fill="x", expand=True, padx=5)
        bitrate_frame = ctk.CTkFrame(self.video_options_frame)
        bitrate_frame.pack(fill="x", pady=2)
        bitrate_label = ctk.CTkLabel(bitrate_frame, text="Bitrate (kb/s):")
        bitrate_label.pack(side="left", padx=5)
        self.bitrate_var = ctk.IntVar(value=2000)
        bitrate_entry = ctk.CTkEntry(bitrate_frame, textvariable=self.bitrate_var, width=100)
        bitrate_entry.pack(side="left", padx=5)
        fps_info_frame = ctk.CTkFrame(self.video_options_frame)
        fps_info_frame.pack(fill="x", pady=2)
        fps_info_label = ctk.CTkLabel(fps_info_frame, text="Output Frame Rate:")
        fps_info_label.pack(side="left", padx=5)
        self.output_fps_var = ctk.StringVar(value="Original FPS")
        fps_value_label = ctk.CTkLabel(fps_info_frame, textvariable=self.output_fps_var, text_color="green")
        fps_value_label.pack(side="left", padx=5)



        # Generation controls
        gen_frame = ctk.CTkFrame(parent)
        gen_frame.pack(fill="x", pady=5)
        copy_type_frame = ctk.CTkFrame(gen_frame)
        copy_type_frame.pack(fill="x", pady=5)
        copy_label = ctk.CTkLabel(copy_type_frame, text="Copy Type:")
        copy_label.pack(side="left", padx=5)
        self.copy_type_var = ctk.StringVar(value="variations")
        exact_radio = ctk.CTkRadioButton(copy_type_frame, text="Exact Copy", variable=self.copy_type_var, value="exact")
        exact_radio.pack(side="left", padx=5)
        variations_radio = ctk.CTkRadioButton(copy_type_frame, text="🎲 Variations", variable=self.copy_type_var, value="variations", command=self.update_copy_type_info)
        variations_radio.pack(side="left", padx=5)
        
        # Add command to exact radio button
        exact_radio.configure(command=self.update_copy_type_info)
        
        # Variations info label (initially hidden)
        self.variations_info_frame = ctk.CTkFrame(gen_frame)
        self.variations_info_label = ctk.CTkLabel(self.variations_info_frame, 
                                                 text="💡 Variations mode: Each copy will have randomized effect parameters within your set ranges",
                                                 font=ctk.CTkFont(size=10), text_color="gray60")
        self.variations_info_label.pack(padx=10, pady=2)
        copies_frame = ctk.CTkFrame(gen_frame)
        copies_frame.pack(fill="x", pady=5)
        copies_label = ctk.CTkLabel(copies_frame, text="Number of Copies:")
        copies_label.pack(side="left", padx=5)
        self.copies_var = ctk.IntVar(value=1)
        self.copies_entry = ctk.CTkEntry(copies_frame, textvariable=self.copies_var, width=80)
        self.copies_entry.pack(side="left", padx=5)
        speed_frame = ctk.CTkFrame(gen_frame)
        speed_frame.pack(fill="x", pady=5)
        speed_label = ctk.CTkLabel(speed_frame, text="Playback Speed:")
        speed_label.pack(side="left", padx=5)
        self.speed_var = ctk.StringVar(value="1.0x")
        self.speed_entry = ctk.CTkEntry(speed_frame, textvariable=self.speed_var, width=80)
        self.speed_entry.pack(side="left", padx=5)
        button_frame = ctk.CTkFrame(gen_frame)
        button_frame.pack(fill="x", pady=10)
        self.generate_button = ctk.CTkButton(button_frame, text="🎬 Generate", command=lambda: self.controller.generate_media(),
                                            corner_radius=8, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.generate_button.pack(side="left", padx=5)
        self.stop_button = ctk.CTkButton(button_frame, text="⏹️ Stop", command=self.controller.stop_processing, 
                                        state="disabled", corner_radius=8, height=40)
        self.stop_button.pack(side="left", padx=5)

        # Effects status
        effects_status_frame = ctk.CTkFrame(parent)
        effects_status_frame.pack(fill="x", pady=5)
        effects_status_label = ctk.CTkLabel(effects_status_frame, text="Effects Status:")
        effects_status_label.pack(side="left", padx=5, pady=5)
        self.effects_status_var = ctk.StringVar(value="No effects applied")
        self.effects_status_display = ctk.CTkLabel(effects_status_frame, textvariable=self.effects_status_var, font=("Arial", 10, "bold"))
        self.effects_status_display.pack(side="left", fill="x", expand=True, padx=5, pady=5)

    def update_output_mode(self):
        """Update UI based on output mode selection."""
        if self.output_mode_var.get() == "gif":
            self.gif_options_frame.pack(fill="x", pady=5)
            self.video_options_frame.pack_forget()
        else:
            self.gif_options_frame.pack_forget()
            self.video_options_frame.pack(fill="x", pady=5)
    
    def update_copy_type_info(self):
        """Update UI based on copy type selection."""
        if self.copy_type_var.get() == "variations":
            self.variations_info_frame.pack(fill="x", pady=2)
        else:
            self.variations_info_frame.pack_forget()

    def setup_effects_tab(self):
        # Scrollable frame for effects
        effects_canvas = ctk.CTkScrollableFrame(self.tab_effects, width=900, height=700)
        effects_canvas.pack(fill="both", expand=True, padx=10, pady=10)



        # Initialize removed variables with defaults to prevent errors
        self.consistent_effects = ctk.BooleanVar(value=False)
        self.effect_seed = ctk.StringVar(value="1")
        
        # Quick Wash Buttons Frame
        wash_buttons_frame = ctk.CTkFrame(effects_canvas)
        wash_buttons_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(wash_buttons_frame, text="🎨 Quick Wash Presets", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=5, pady=(0, 5))
        ctk.CTkButton(wash_buttons_frame, text="✨ Normal Wash", command=lambda: self.controller.apply_quick_wash('normal')).pack(side="left", padx=10, pady=5, fill="x", expand=True)
        ctk.CTkButton(wash_buttons_frame, text="🔥 Deep Wash", command=lambda: self.controller.apply_quick_wash('deep')).pack(side="left", padx=10, pady=5, fill="x", expand=True)
        ctk.CTkButton(wash_buttons_frame, text="💥 Extreme Wash", command=lambda: self.controller.apply_quick_wash('extreme')).pack(side="left", padx=10, pady=5, fill="x", expand=True)

        # Brightness
        bright_frame = ctk.CTkFrame(effects_canvas)
        bright_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(bright_frame, text="Brightness", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.brightness_enabled = ctk.BooleanVar(value=False)
        bright_cb = ctk.CTkCheckBox(bright_frame, text="Enable Brightness Adjustment (Random 0.9-1.1)", variable=self.brightness_enabled)
        bright_cb.pack(anchor="w", padx=5, pady=2)
        # Info label
        bright_info_label = ctk.CTkLabel(bright_frame, text="💡 Applies random brightness variation using FFmpeg", 
                                       font=ctk.CTkFont(size=10), text_color="gray60")
        bright_info_label.pack(anchor="w", padx=5, pady=2)

        # Contrast
        contrast_frame = ctk.CTkFrame(effects_canvas)
        contrast_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(contrast_frame, text="Contrast", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.contrast_enabled = ctk.BooleanVar(value=False)
        contrast_cb = ctk.CTkCheckBox(contrast_frame, text="Enable Contrast Adjustment (Random 0.95-1.1)", variable=self.contrast_enabled)
        contrast_cb.pack(anchor="w", padx=5, pady=2)
        # Info label
        contrast_info_label = ctk.CTkLabel(contrast_frame, text="💡 Applies random contrast variation using FFmpeg", 
                                         font=ctk.CTkFont(size=10), text_color="gray60")
        contrast_info_label.pack(anchor="w", padx=5, pady=2)

        # Saturation
        saturation_frame = ctk.CTkFrame(effects_canvas)
        saturation_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(saturation_frame, text="Saturation", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.saturation_enabled = ctk.BooleanVar(value=False)
        saturation_cb = ctk.CTkCheckBox(saturation_frame, text="Enable Saturation Adjustment (Random 0.9-1.1)", variable=self.saturation_enabled)
        saturation_cb.pack(anchor="w", padx=5, pady=2)
        # Info label
        saturation_info_label = ctk.CTkLabel(saturation_frame, text="💡 Applies random saturation variation using FFmpeg", 
                                           font=ctk.CTkFont(size=10), text_color="gray60")
        saturation_info_label.pack(anchor="w", padx=5, pady=2)

        # Hue
        hue_frame = ctk.CTkFrame(effects_canvas)
        hue_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(hue_frame, text="Hue Shift", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.hue_enabled = ctk.BooleanVar(value=False)
        hue_cb = ctk.CTkCheckBox(hue_frame, text="Enable Hue Shift (Random -15° to +15°)", variable=self.hue_enabled)
        hue_cb.pack(anchor="w", padx=5, pady=2)
        # Info label
        hue_info_label = ctk.CTkLabel(hue_frame, text="💡 Applies random hue shift using FFmpeg", 
                                    font=ctk.CTkFont(size=10), text_color="gray60")
        hue_info_label.pack(anchor="w", padx=5, pady=2)

        # Blur
        blur_frame = ctk.CTkFrame(effects_canvas)
        blur_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(blur_frame, text="Blur", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.blur_enabled = ctk.BooleanVar(value=False)
        blur_cb = ctk.CTkCheckBox(blur_frame, text="Enable Blur (Random 0.5-3.0 radius)", variable=self.blur_enabled)
        blur_cb.pack(anchor="w", padx=5, pady=2)
        # Info label
        blur_info_label = ctk.CTkLabel(blur_frame, text="💡 Applies random blur using FFmpeg gblur filter", 
                                     font=ctk.CTkFont(size=10), text_color="gray60")
        blur_info_label.pack(anchor="w", padx=5, pady=2)



        # Resize
        resize_frame = ctk.CTkFrame(effects_canvas)
        resize_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(resize_frame, text="Resize", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.resize_enabled = ctk.BooleanVar(value=False)
        resize_cb = ctk.CTkCheckBox(resize_frame, text="Enable Random Resize (98-102% of original)", variable=self.resize_enabled)
        resize_cb.pack(anchor="w", padx=5, pady=2)
        # Info label
        resize_info_label = ctk.CTkLabel(resize_frame, text="💡 Applies random resize using FFmpeg scale filter", 
                                       font=ctk.CTkFont(size=10), text_color="gray60")
        resize_info_label.pack(anchor="w", padx=5, pady=2)

        # Noise
        noise_frame = ctk.CTkFrame(effects_canvas)
        noise_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(noise_frame, text="Noise", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.noise_enabled = ctk.BooleanVar(value=False)
        noise_cb = ctk.CTkCheckBox(noise_frame, text="Enable Noise (Random 0.01-0.05 strength)", variable=self.noise_enabled)
        noise_cb.pack(anchor="w", padx=5, pady=2)
        # Info label
        noise_info_label = ctk.CTkLabel(noise_frame, text="💡 Applies random noise using FFmpeg noise filter", 
                                      font=ctk.CTkFont(size=10), text_color="gray60")
        noise_info_label.pack(anchor="w", padx=5, pady=2)

        # FPS Change
        fps_change_frame = ctk.CTkFrame(effects_canvas)
        fps_change_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(fps_change_frame, text="FPS Micro Change", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.fps_change_enabled = ctk.BooleanVar(value=False)
        fps_change_cb = ctk.CTkCheckBox(fps_change_frame, text="Enable FPS Micro Change (Random ±1.5 FPS)", variable=self.fps_change_enabled)
        fps_change_cb.pack(anchor="w", padx=5, pady=2)
        # Info label
        fps_change_info_label = ctk.CTkLabel(fps_change_frame, text="💡 Applies subtle FPS changes using FFmpeg fps filter", 
                                           font=ctk.CTkFont(size=10), text_color="gray60")
        fps_change_info_label.pack(anchor="w", padx=5, pady=2)

        # Audio Fingerprint Evasion
        audio_frame = ctk.CTkFrame(effects_canvas)
        audio_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(audio_frame, text="Audio Fingerprint Evasion", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.audio_fingerprint_enabled = ctk.BooleanVar(value=False)
        audio_cb = ctk.CTkCheckBox(audio_frame, text="Enable Audio Fingerprint Evasion", variable=self.audio_fingerprint_enabled)
        audio_cb.pack(anchor="w", padx=5, pady=2)
        # Info label
        audio_info_label = ctk.CTkLabel(audio_frame, text="💡 Combines pitch shift (±2%), speed change with tempo correction, and subtle EQ", 
                                      font=ctk.CTkFont(size=10), text_color="gray60")
        audio_info_label.pack(anchor="w", padx=5, pady=2)
        audio_info_label2 = ctk.CTkLabel(audio_frame, text="🎯 Designed to evade Instagram and other platform fingerprinting while maintaining audio quality", 
                                       font=ctk.CTkFont(size=10), text_color="orange")
        audio_info_label2.pack(anchor="w", padx=5, pady=2)

        # Region
        region_frame = ctk.CTkFrame(effects_canvas)
        region_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(region_frame, text="Region", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.region_enabled = ctk.BooleanVar(value=False)
        region_cb = ctk.CTkCheckBox(region_frame, text="Enable Region Effects", variable=self.region_enabled)
        region_cb.pack(anchor="w", padx=5, pady=2)
        region_options_frame = ctk.CTkFrame(region_frame)
        region_options_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(region_options_frame, text="X:").pack(side="left", padx=5)
        self.region_x_var = ctk.IntVar(value=0)
        region_x_entry = ctk.CTkEntry(region_options_frame, textvariable=self.region_x_var, width=80)
        region_x_entry.pack(side="left", padx=5)
        ctk.CTkLabel(region_options_frame, text="Y:").pack(side="left", padx=(20, 5))
        self.region_y_var = ctk.IntVar(value=0)
        region_y_entry = ctk.CTkEntry(region_options_frame, textvariable=self.region_y_var, width=80)
        region_y_entry.pack(side="left", padx=5)
        ctk.CTkLabel(region_options_frame, text="Width:").pack(side="left", padx=(20, 5))
        self.region_width_var = ctk.IntVar(value=100)
        region_width_entry = ctk.CTkEntry(region_options_frame, textvariable=self.region_width_var, width=80)
        region_width_entry.pack(side="left", padx=5)
        ctk.CTkLabel(region_options_frame, text="Height:").pack(side="left", padx=(20, 5))
        self.region_height_var = ctk.IntVar(value=100)
        region_height_entry = ctk.CTkEntry(region_options_frame, textvariable=self.region_height_var, width=80)
        region_height_entry.pack(side="left", padx=5)

        # Bitplane
        bitplane_frame = ctk.CTkFrame(effects_canvas)
        bitplane_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(bitplane_frame, text="Bit Plane Manipulation", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.bitplane_enabled = ctk.BooleanVar(value=False)
        bitplane_cb = ctk.CTkCheckBox(bitplane_frame, text="Enable Bit Plane Manipulation", variable=self.bitplane_enabled)
        bitplane_cb.pack(anchor="w", padx=5, pady=2)
        intensity_frame = ctk.CTkFrame(bitplane_frame)
        intensity_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(intensity_frame, text="Intensity:").pack(side="left", padx=5)
        self.bitplane_intensity_var = ctk.DoubleVar(value=0.5)
        intensity_scale = ctk.CTkSlider(intensity_frame, from_=0.1, to=1.0, number_of_steps=90, variable=self.bitplane_intensity_var)
        intensity_scale.pack(side="left", padx=5)
        ctk.CTkLabel(intensity_frame, textvariable=self.bitplane_intensity_var, width=5).pack(side="left", padx=5)
        planes_frame = ctk.CTkFrame(bitplane_frame)
        planes_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(planes_frame, text="Bit Planes:").pack(side="left", padx=5)
        self.bitplane_planes_var = ctk.IntVar(value=1)
        planes_scale = ctk.CTkSlider(planes_frame, from_=1, to=3, number_of_steps=2, variable=self.bitplane_planes_var)
        planes_scale.pack(side="left", padx=5)
        ctk.CTkLabel(planes_frame, textvariable=self.bitplane_planes_var, width=5).pack(side="left", padx=5)

        # Overlay
        overlay_frame = ctk.CTkFrame(effects_canvas)
        overlay_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(overlay_frame, text="Transparent Frame Overlay", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.overlay_enabled = ctk.BooleanVar(value=False)
        overlay_cb = ctk.CTkCheckBox(overlay_frame, text="Enable Transparent Frame Overlay", variable=self.overlay_enabled)
        overlay_cb.pack(anchor="w", padx=5, pady=2)
        overlay_interval_frame = ctk.CTkFrame(overlay_frame)
        overlay_interval_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(overlay_interval_frame, text="Apply every N frames:").pack(side="left", padx=5)
        self.frame_overlay_interval = ctk.IntVar(value=1)
        interval_scale = ctk.CTkSlider(overlay_interval_frame, from_=1, to=100, number_of_steps=99, variable=self.frame_overlay_interval)
        interval_scale.pack(side="left", padx=5)
        ctk.CTkLabel(overlay_interval_frame, textvariable=self.frame_overlay_interval, width=5).pack(side="left", padx=5)

        # Shadow lines effect
        shadow_lines_frame = ctk.CTkFrame(effects_canvas)
        shadow_lines_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(shadow_lines_frame, text="Shadow Lines Effect", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.shadow_enabled = ctk.BooleanVar(value=False)
        shadow_lines_cb = ctk.CTkCheckBox(shadow_lines_frame, text="Enable Shadow Lines Effect", variable=self.shadow_enabled)
        shadow_lines_cb.pack(anchor="w", padx=5, pady=2)
        # Horizontal lines
        h_lines_frame = ctk.CTkFrame(shadow_lines_frame)
        h_lines_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(h_lines_frame, text="Horizontal Lines:").pack(side="left", padx=5)
        self.shadow_h_lines_var = ctk.IntVar(value=0)
        h_lines_scale = ctk.CTkSlider(h_lines_frame, from_=0, to=10, number_of_steps=10, variable=self.shadow_h_lines_var)
        h_lines_scale.pack(side="left", padx=5)
        ctk.CTkLabel(h_lines_frame, textvariable=self.shadow_h_lines_var, width=5).pack(side="left", padx=5)
        # Vertical lines
        v_lines_frame = ctk.CTkFrame(shadow_lines_frame)
        v_lines_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(v_lines_frame, text="Vertical Lines:").pack(side="left", padx=5)
        self.shadow_v_lines_var = ctk.IntVar(value=0)
        v_lines_scale = ctk.CTkSlider(v_lines_frame, from_=0, to=10, number_of_steps=10, variable=self.shadow_v_lines_var)
        v_lines_scale.pack(side="left", padx=5)
        ctk.CTkLabel(v_lines_frame, textvariable=self.shadow_v_lines_var, width=5).pack(side="left", padx=5)
        # Intensity
        intensity_frame_shadow = ctk.CTkFrame(shadow_lines_frame)
        intensity_frame_shadow.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(intensity_frame_shadow, text="Intensity:").pack(side="left", padx=5)
        self.shadow_intensity_var = ctk.DoubleVar(value=0.1)
        intensity_scale_shadow = ctk.CTkSlider(intensity_frame_shadow, from_=0.1, to=0.5, number_of_steps=40, variable=self.shadow_intensity_var)
        intensity_scale_shadow.pack(side="left", padx=5)
        ctk.CTkLabel(intensity_frame_shadow, textvariable=self.shadow_intensity_var, width=5).pack(side="left", padx=5)
        # Line Width
        width_frame = ctk.CTkFrame(shadow_lines_frame)
        width_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(width_frame, text="Line Width:").pack(side="left", padx=5)
        self.shadow_line_width_var = ctk.IntVar(value=1)
        width_scale = ctk.CTkSlider(width_frame, from_=1, to=5, number_of_steps=4, variable=self.shadow_line_width_var)
        width_scale.pack(side="left", padx=5)
        ctk.CTkLabel(width_frame, textvariable=self.shadow_line_width_var, width=5).pack(side="left", padx=5)
        # Movement Speed
        speed_frame = ctk.CTkFrame(shadow_lines_frame)
        speed_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(speed_frame, text="Speed:").pack(side="left", padx=5)
        self.shadow_speed_var = ctk.DoubleVar(value=0.5)
        speed_scale = ctk.CTkSlider(speed_frame, from_=0.5, to=2.0, number_of_steps=30, variable=self.shadow_speed_var)
        speed_scale.pack(side="left", padx=5)
        ctk.CTkLabel(speed_frame, textvariable=self.shadow_speed_var, width=5).pack(side="left", padx=5)

        # Video Clipping Effect
        clipping_frame = ctk.CTkFrame(effects_canvas)
        clipping_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(clipping_frame, text="Video Clipping", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.clipping_enabled = ctk.BooleanVar(value=False)
        clipping_cb = ctk.CTkCheckBox(clipping_frame, text="Enable End Clipping (Random % from last 2 seconds)", variable=self.clipping_enabled)
        clipping_cb.pack(anchor="w", padx=5, pady=2)
        # Clipping info
        clipping_info_label = ctk.CTkLabel(clipping_frame, text="💡 Randomly clips 5-10% from the end of the video", 
                                         font=ctk.CTkFont(size=10), text_color="gray60")
        clipping_info_label.pack(anchor="w", padx=5, pady=2)
        # Clipping range
        clipping_range_frame = ctk.CTkFrame(clipping_frame)
        clipping_range_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(clipping_range_frame, text="Min %:").pack(side="left", padx=5)
        self.clipping_min_var = ctk.DoubleVar(value=5.0)
        min_clip_scale = ctk.CTkSlider(clipping_range_frame, from_=1.0, to=15.0, number_of_steps=140, variable=self.clipping_min_var)
        min_clip_scale.pack(side="left", padx=5)
        ctk.CTkLabel(clipping_range_frame, textvariable=self.clipping_min_var, width=5).pack(side="left", padx=5)
        ctk.CTkLabel(clipping_range_frame, text="Max %:").pack(side="left", padx=(20, 5))
        self.clipping_max_var = ctk.DoubleVar(value=10.0)
        max_clip_scale = ctk.CTkSlider(clipping_range_frame, from_=1.0, to=15.0, number_of_steps=140, variable=self.clipping_max_var)
        max_clip_scale.pack(side="left", padx=5)
        ctk.CTkLabel(clipping_range_frame, textvariable=self.clipping_max_var, width=5).pack(side="left", padx=5)

        # Horizontal Flip Effect
        flip_frame = ctk.CTkFrame(effects_canvas)
        flip_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(flip_frame, text="Horizontal Flip", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.flip_enabled = ctk.BooleanVar(value=False)
        flip_cb = ctk.CTkCheckBox(flip_frame, text="Enable Horizontal Flip (Mirror Left/Right)", variable=self.flip_enabled)
        flip_cb.pack(anchor="w", padx=5, pady=2)
        # Flip info
        flip_info_label = ctk.CTkLabel(flip_frame, text="💡 Mirrors the video horizontally (left becomes right)", 
                                     font=ctk.CTkFont(size=10), text_color="gray60")
        flip_info_label.pack(anchor="w", padx=5, pady=2)

        # Reset button only
        button_frame = ctk.CTkFrame(effects_canvas)
        button_frame.pack(fill="x", pady=10)
        self.reset_effects_button = ctk.CTkButton(button_frame, text="🔄 Reset All Effects", command=self.controller.reset_effects,
                                                 corner_radius=8, height=35, font=ctk.CTkFont(size=12, weight="bold"))
        self.reset_effects_button.pack(side="left", padx=5)

        # Effects status label
        self.effects_status_label = ctk.CTkLabel(effects_canvas, text="No effects applied", font=("Arial", 10, "bold"))
        self.effects_status_label.pack(fill="x", pady=5)

        # Bindings for dynamic updates
        self.brightness_enabled.trace_add("write", self.update_effects_status)
        self.contrast_enabled.trace_add("write", self.update_effects_status)
        self.saturation_enabled.trace_add("write", self.update_effects_status)
        self.hue_enabled.trace_add("write", self.update_effects_status)
        self.blur_enabled.trace_add("write", self.update_effects_status)
        self.resize_enabled.trace_add("write", self.update_effects_status)
        self.noise_enabled.trace_add("write", self.update_effects_status)
        self.fps_change_enabled.trace_add("write", self.update_effects_status)
        self.audio_fingerprint_enabled.trace_add("write", self.update_effects_status)
        self.region_enabled.trace_add("write", self.update_effects_status)
        self.bitplane_enabled.trace_add("write", self.update_effects_status)
        self.overlay_enabled.trace_add("write", self.update_effects_status)
        self.shadow_enabled.trace_add("write", self.update_effects_status)
        self.clipping_enabled.trace_add("write", self.update_effects_status)
        self.flip_enabled.trace_add("write", self.update_effects_status)

    def update_effects_status(self, *args):
        # Update the effects status label based on the current settings
        status = []
        if self.brightness_enabled.get():
            status.append("Brightness")
        if self.contrast_enabled.get():
            status.append("Contrast")
        if self.saturation_enabled.get():
            status.append("Saturation")
        if self.hue_enabled.get():
            status.append("Hue")
        if self.blur_enabled.get():
            status.append("Blur")
        if self.resize_enabled.get():
            status.append("Resize")
        if self.noise_enabled.get():
            status.append("Noise")
        if self.fps_change_enabled.get():
            status.append("FPS Change")
        if self.audio_fingerprint_enabled.get():
            status.append("Audio Fingerprint")
        if self.region_enabled.get():
            status.append("Region")
        if self.bitplane_enabled.get():
            status.append("Bitplane")
        if self.overlay_enabled.get():
            status.append("Overlay")
        if self.shadow_enabled.get():
            status.append("Shadow Lines")
        if self.clipping_enabled.get():
            status.append("Clipping")
        if self.flip_enabled.get():
            status.append("Horizontal Flip")
        if not status:
            status.append("No effects applied")
        self.effects_status_label.configure(text=", ".join(status))

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = ReelsWasherApp()
    app.mainloop()
