import subprocess
import os
import shutil
import threading
import time
import sys
from src.utils.utils import select_file_dialog, ensure_output_folder_exists
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np
import random
import cv2
from moviepy.editor import VideoFileClip, ImageSequenceClip
import glob
import datetime


# Global variables for processing control
processing_thread = None
stop_processing = False

# Windows-specific subprocess settings to hide console windows
def get_subprocess_creation_flags():
    """Get the appropriate creation flags for subprocess to hide console windows on Windows."""
    if sys.platform == "win32":
        return subprocess.CREATE_NO_WINDOW
    return 0


def generate_variation(output_folder, prefix, codec, bitrate, variations, speed):
    # Placeholder for generation logic
    print("Generating variations...")
    print(f"Output Folder: {output_folder}")
    print(f"Prefix: {prefix}")
    print(f"Codec: {codec}")
    print(f"Bitrate: {bitrate}")
    print(f"Variations: {variations}")
    print(f"Speed: {speed}")


def get_video_info_ffprobe(video_path):
    """Get video info using ffprobe."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration:stream=width,height,codec_name,avg_frame_rate',
            '-of', 'default=noprint_wrappers=1',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        info = {}
        for line in result.stdout.splitlines():
            if '=' in line:
                k, v = line.split('=', 1)
                info[k.strip()] = v.strip()
        
        # Parse frame rate
        if 'avg_frame_rate' in info and info['avg_frame_rate'] != 'N/A':
            try:
                if '/' in info['avg_frame_rate']:
                    num, den = info['avg_frame_rate'].split('/')
                    info['fps'] = round(float(num) / float(den), 2)
                else:
                    info['fps'] = float(info['avg_frame_rate'])
            except:
                info['fps'] = 30.0
        else:
            info['fps'] = 30.0
        
        return info
    except Exception as e:
        print(f"Error getting video info: {e}")
        return {}


def apply_clipping_with_ffmpeg(video_path, output_path, clipping_min=5, clipping_max=10):
    """
    Clip video by removing a random percentage from the last 2 seconds.
    
    Args:
        video_path: Input video path
        output_path: Output video path
        clipping_min: Minimum clipping percentage
        clipping_max: Maximum clipping percentage
    
    Returns:
        Path to clipped video, or original path if processing fails
    """
    try:
        # Get video duration
        video_info = get_video_info_ffprobe(video_path)
        total_duration = float(video_info.get('duration', 0))
        
        if total_duration <= 0:
            print("Could not determine video duration for clipping")
            return video_path
        
        # Focus on last 2 seconds
        last_2_seconds_start = max(0, total_duration - 2.0)
        last_2_seconds_duration = total_duration - last_2_seconds_start
        
        # Use time-based seed for truly random clipping (independent of effect consistency)
        import time
        clip_random = random.Random(time.time() * 1000 + random.randint(0, 9999))
        
        # Calculate random clip percentage using independent random state
        clip_percentage = clip_random.uniform(clipping_min, clipping_max) / 100.0
        clip_duration = last_2_seconds_duration * clip_percentage
        new_duration = max(1.0, total_duration - clip_duration)  # Ensure minimum 1 second
        
        # FFmpeg command to clip video
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-ss', '0',                    # Start from beginning
            '-t', str(new_duration),       # Duration (clips the end)
            '-c', 'copy',                  # Copy without re-encoding (faster)
            output_path
        ]
        
        print(f"Clipping video from {total_duration:.2f}s to {new_duration:.2f}s ({clip_percentage*100:.1f}% clipped)")
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            print(f"Successfully clipped video: {output_path}")
            return output_path
        else:
            print(f"Video clipping failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error in apply_clipping_with_ffmpeg: {e}")
        return video_path


def apply_flipping_with_ffmpeg(video_path, output_path):
    """
    Apply horizontal flip to video using FFmpeg hflip filter.
    
    Args:
        video_path: Input video path
        output_path: Output video path
    
    Returns:
        Path to flipped video, or original path if processing fails
    """
    try:
        # FFmpeg command with horizontal flip filter
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', 'hflip',                # Horizontal flip filter
            '-c:a', 'copy',                # Copy audio without re-encoding
            output_path
        ]
        
        print(f"Applying horizontal flip to video")
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            print(f"Successfully flipped video: {output_path}")
            return output_path
        else:
            print(f"Video flipping failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error in apply_flipping_with_ffmpeg: {e}")
        return video_path


def apply_brightness_contrast_saturation_with_ffmpeg(video_path, output_path, brightness=1.0, contrast=1.0, saturation=1.0):
    """
    Apply brightness, contrast, and saturation adjustments using FFmpeg eq filter.
    
    Args:
        video_path: Input video path
        output_path: Output video path
        brightness: Brightness factor (0.1-3.0, 1.0=no change)
        contrast: Contrast factor (0.1-3.0, 1.0=no change)
        saturation: Saturation factor (0.1-3.0, 1.0=no change)
    
    Returns:
        Path to processed video, or original path if processing fails
    """
    try:
        # Convert brightness to FFmpeg eq format (brightness is relative, so -1 to 1)
        brightness_eq = brightness - 1.0
        
        # FFmpeg command with eq filter
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f'eq=brightness={brightness_eq:.3f}:contrast={contrast:.3f}:saturation={saturation:.3f}',
            '-c:a', 'copy',
            output_path
        ]
        
        print(f"Applying brightness={brightness:.2f}, contrast={contrast:.2f}, saturation={saturation:.2f}")
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            print(f"Successfully applied color adjustments: {output_path}")
            return output_path
        else:
            print(f"Color adjustment failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error in apply_brightness_contrast_saturation_with_ffmpeg: {e}")
        return video_path


def apply_hue_shift_with_ffmpeg(video_path, output_path, hue_shift=0):
    """
    Apply hue shift using FFmpeg hue filter.
    
    Args:
        video_path: Input video path
        output_path: Output video path
        hue_shift: Hue shift in degrees (-180 to 180)
    
    Returns:
        Path to processed video, or original path if processing fails
    """
    try:
        # FFmpeg command with hue filter
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f'hue=h={hue_shift:.1f}',
            '-c:a', 'copy',
            output_path
        ]
        
        print(f"Applying hue shift: {hue_shift:.1f} degrees")
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            print(f"Successfully applied hue shift: {output_path}")
            return output_path
        else:
            print(f"Hue shift failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error in apply_hue_shift_with_ffmpeg: {e}")
        return video_path


def apply_blur_with_ffmpeg(video_path, output_path, blur_radius=1.0):
    """
    Apply blur using FFmpeg gblur filter.
    
    Args:
        video_path: Input video path
        output_path: Output video path
        blur_radius: Blur radius (0.1-20.0)
    
    Returns:
        Path to processed video, or original path if processing fails
    """
    try:
        # FFmpeg command with gblur filter
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f'gblur=sigma={blur_radius:.2f}',
            '-c:a', 'copy',
            output_path
        ]
        
        print(f"Applying blur with radius: {blur_radius:.2f}")
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            print(f"Successfully applied blur: {output_path}")
            return output_path
        else:
            print(f"Blur failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error in apply_blur_with_ffmpeg: {e}")
        return video_path


def apply_resize_with_ffmpeg(video_path, output_path, width, height):
    """
    Apply resize using FFmpeg scale filter.
    
    Args:
        video_path: Input video path
        output_path: Output video path
        width: Target width
        height: Target height
    
    Returns:
        Path to processed video, or original path if processing fails
    """
    try:
        # FFmpeg command with scale filter
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f'scale={width}:{height}',
            '-c:a', 'copy',
            output_path
        ]
        
        print(f"Resizing video to {width}x{height}")
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            print(f"Successfully resized video: {output_path}")
            return output_path
        else:
            print(f"Resize failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error in apply_resize_with_ffmpeg: {e}")
        return video_path


def apply_noise_with_ffmpeg(video_path, output_path, noise_level=0.02):
    """
    Apply noise using FFmpeg noise filter.
    
    Args:
        video_path: Input video path
        output_path: Output video path
        noise_level: Noise strength (0.0-1.0)
    
    Returns:
        Path to processed video, or original path if processing fails
    """
    try:
        # Convert noise level to FFmpeg format (0-100)
        noise_strength = int(noise_level * 100)
        
        # FFmpeg command with noise filter
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f'noise=alls={noise_strength}:allf=t',
            '-c:a', 'copy',
            output_path
        ]
        
        print(f"Applying noise with strength: {noise_strength}")
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            print(f"Successfully applied noise: {output_path}")
            return output_path
        else:
            print(f"Noise application failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error in apply_noise_with_ffmpeg: {e}")
        return video_path


def apply_audio_fingerprint_evasion_with_ffmpeg(video_path, output_path):
    """
    Apply audio fingerprint evasion using pitch shift, speed change, and EQ.
    
    Args:
        video_path: Input video path
        output_path: Output video path
    
    Returns:
        Path to processed video, or original path if processing fails
    """
    try:
        # Random audio modifications for fingerprint evasion
        import random
        
        # 1. Pitch shift: ±1-2% (about 0.2-0.3 semitones)
        # FFmpeg asetrate changes sample rate to shift pitch
        pitch_shift_percent = random.uniform(-2.0, 2.0)
        original_rate = 48000  # Assume 48kHz, will be auto-detected by FFmpeg
        new_rate = int(original_rate * (1 + pitch_shift_percent / 100))
        
        # 2. Speed change: ±1-2% with tempo correction to preserve pitch
        speed_change_percent = random.uniform(-2.0, 2.0)
        tempo_factor = 1 + (speed_change_percent / 100)
        
        # 3. EQ adjustments: subtle frequency boosts/cuts
        eq_8khz = random.uniform(-1.5, 1.5)  # High frequency adjustment
        eq_200hz = random.uniform(-1.5, 1.5)  # Low frequency adjustment
        eq_1khz = random.uniform(-1.0, 1.0)   # Mid frequency adjustment
        
        # Build complex audio filter chain
        audio_filters = []
        
        # Pitch shift via sample rate change + rate correction
        audio_filters.append(f"asetrate={new_rate}")
        audio_filters.append(f"aresample=48000")  # Resample back to standard rate
        
        # Tempo change with pitch preservation (rubberband-style)
        audio_filters.append(f"atempo={tempo_factor:.6f}")
        
        # EQ adjustments using equalizer filter
        audio_filters.append(f"equalizer=f=200:width_type=h:width=100:g={eq_200hz:.2f}")
        audio_filters.append(f"equalizer=f=1000:width_type=h:width=200:g={eq_1khz:.2f}")
        audio_filters.append(f"equalizer=f=8000:width_type=h:width=1000:g={eq_8khz:.2f}")
        
        # Combine all audio filters
        audio_filter_chain = ",".join(audio_filters)
        
        # FFmpeg command with audio fingerprint evasion
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-af', audio_filter_chain,
            '-c:v', 'copy',  # Copy video without re-encoding
            output_path
        ]
        
        print(f"Applying audio fingerprint evasion:")
        print(f"  Pitch shift: {pitch_shift_percent:+.2f}%")
        print(f"  Speed change: {speed_change_percent:+.2f}% (tempo corrected)")
        print(f"  EQ: 200Hz{eq_200hz:+.1f}dB, 1kHz{eq_1khz:+.1f}dB, 8kHz{eq_8khz:+.1f}dB")
        
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            print(f"Successfully applied audio fingerprint evasion: {output_path}")
            return output_path
        else:
            print(f"Audio fingerprint evasion failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error in apply_audio_fingerprint_evasion_with_ffmpeg: {e}")
        return video_path


def apply_fps_change_with_ffmpeg(video_path, output_path, fps_adjustment=0.5):
    """
    Apply FPS micro change using FFmpeg to avoid detection.
    
    Args:
        video_path: Input video path
        output_path: Output video path
        fps_adjustment: FPS adjustment in range (-2.0 to +2.0)
    
    Returns:
        Path to processed video, or original path if processing fails
    """
    try:
        # Get original video FPS
        video_info = get_video_info_ffprobe(video_path)
        original_fps = video_info.get('fps', 30.0)
        
        # Calculate new FPS with adjustment
        new_fps = max(15.0, min(60.0, original_fps + fps_adjustment))  # Keep within reasonable bounds
        
        # FFmpeg command with FPS change
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-filter:v', f'fps={new_fps:.3f}',
            '-c:a', 'copy',
            output_path
        ]
        
        print(f"Changing FPS from {original_fps:.2f} to {new_fps:.2f} (adjustment: {fps_adjustment:+.2f})")
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            print(f"Successfully changed FPS: {output_path}")
            return output_path
        else:
            print(f"FPS change failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error in apply_fps_change_with_ffmpeg: {e}")
        return video_path


def safe_get(var, default_value):
    """Helper function to safely get values from variables."""
    try:
        if hasattr(var, 'get'):
            value = var.get()
            # Handle empty string values for numeric types
            if isinstance(default_value, (int, float)) and value == "":
                return default_value
            return value
        else:
            return var if var is not None else default_value
    except:
        return default_value


def upload_and_get_video_info():
    """Upload a video and get its info using ffprobe."""
    video_path = select_file_dialog(filetypes=[('Video files', '*.mp4;*.mov;*.avi;*.mkv;*.webm;*.gif'), ('All files', '*.*')])
    if not video_path:
        return None, None
    info = get_video_info_ffprobe(video_path)
    return video_path, info


def extract_frames_from_video(video_path, start_time=0, end_time=None, output_dir="temp_frames"):
    """Extract frames from video using OpenCV."""
    try:
        ensure_output_folder_exists(output_dir)
        
        # Clear existing frames
        for f in glob.glob(os.path.join(output_dir, "*.jpg")):
            os.remove(f)
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps) if end_time else total_frames
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        frame_count = 0
        extracted_frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret or cap.get(cv2.CAP_PROP_POS_FRAMES) > end_frame:
                break
            
            frame_filename = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
            cv2.imwrite(frame_filename, frame)
            extracted_frames.append(frame_filename)
            frame_count += 1
        
        cap.release()
        return extracted_frames, fps
    
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return [], 30.0


def apply_shadow_lines_effect(frame, h_lines, v_lines, intensity, line_width, speed, frame_index):
    """Apply shadow lines effect to a frame."""
    if h_lines == 0 and v_lines == 0:
        return frame
    
    result = frame.copy()
    draw = ImageDraw.Draw(result)
    width, height = result.size
    
    # Calculate line positions based on frame index for movement
    offset = int(frame_index * speed) % max(height // max(h_lines, 1), width // max(v_lines, 1))
    
    # Draw horizontal lines
    if h_lines > 0:
        line_spacing = height // h_lines
        for i in range(h_lines):
            y = (i * line_spacing + offset) % height
            # Create shadow effect
            shadow_color = (0, 0, 0, int(255 * intensity))
            for w in range(line_width):
                if y + w < height:
                    draw.line([(0, y + w), (width, y + w)], fill=shadow_color, width=1)
    
    # Draw vertical lines
    if v_lines > 0:
        line_spacing = width // v_lines
        for i in range(v_lines):
            x = (i * line_spacing + offset) % width
            # Create shadow effect
            shadow_color = (0, 0, 0, int(255 * intensity))
            for w in range(line_width):
                if x + w < width:
                    draw.line([(x + w, 0), (x + w, height)], fill=shadow_color, width=1)
    
    return result


def apply_effects_to_frame(frame, vars, frame_index=0):
    """
    Apply configured effects to a single frame using the provided variables dict.
    Args:
        frame (PIL.Image.Image): The frame to apply effects to
        vars (dict): Dictionary of effect variables (should be ctk variables or values)
        frame_index (int): Current frame index for effects that depend on frame number
    Returns:
        PIL.Image.Image: The frame with effects applied
    """
    result = frame.copy()
    
    # Set random seed for consistency if enabled
    consistent_effects = vars.get('consistent_effects')
    if consistent_effects and safe_get(consistent_effects, False):
        effect_seed = vars.get('effect_seed')
        seed_val = safe_get(effect_seed, '1')
        try:
            random.seed(int(seed_val))
            np.random.seed(int(seed_val))
        except:
            random.seed(1)
            np.random.seed(1)
    
    # Store frame index for overlay effect
    vars['current_processing_frame_index'] = frame_index
    
    # Note: Brightness, Contrast, Saturation, Hue, Blur, Resize, and Noise are now handled by FFmpeg
    # Only keep the effects that require frame-level processing
    
    # Numpy-based effects (bitplane only, noise moved to FFmpeg)
    bitplane_enabled = vars.get('bitplane_enabled')
    
    if bitplane_enabled and safe_get(bitplane_enabled, False):
        img_array = np.array(result).astype('float32')
        
        # Bitplane manipulation
        intensity = safe_get(vars.get('bitplane_intensity_var'), 0.5)
        num_planes = safe_get(vars.get('bitplane_planes_var'), 1)
        try:
            num_planes = int(num_planes)
        except (ValueError, TypeError):
            num_planes = 1
        try:
            original_array = img_array.copy()
            planes_to_modify = random.sample(range(0, 4), min(num_planes, 4))
            temp_array = np.clip(img_array, 0, 255).astype(np.uint8)
            for i in range(3):
                channel = temp_array[:,:,i].copy()
                for plane in planes_to_modify:
                    bit_plane = (channel & (1 << plane)) >> plane
                    mask = np.random.random(channel.shape) < 0.5
                    bit_plane = np.logical_xor(bit_plane, mask).astype(np.uint8)
                    channel_int32 = channel.astype(np.int32)
                    channel_int32 = channel_int32 & ~(1 << plane)
                    channel_int32 = channel_int32 | (bit_plane.astype(np.int32) << plane)
                    channel = np.clip(channel_int32, 0, 255).astype(np.uint8)
                temp_array[:,:,i] = channel
            img_array = (original_array * (1 - intensity) + temp_array.astype(np.float32) * intensity)
        except Exception as e:
            print(f"Error in bitplane effect: {str(e)}")
        
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        result = Image.fromarray(img_array)
    
    # Region effects
    region_enabled = vars.get('region_effects_enabled') or vars.get('region_enabled')
    if region_enabled and safe_get(region_enabled, False):
        width, height = result.size
        region_width = safe_get(vars.get('region_width_var'), 100)
        region_height = safe_get(vars.get('region_height_var'), 100)
        
        try:
            region_width = int(region_width)
            region_height = int(region_height)
        except (ValueError, TypeError):
            region_width = 100
            region_height = 100
        
        if region_width > width:
            region_width = width
        if region_height > height:
            region_height = height
        
        x1 = random.randint(0, width - region_width)
        y1 = random.randint(0, height - region_height)
        x2 = x1 + region_width
        y2 = y1 + region_height
        
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rectangle([x1, y1, x2, y2], fill=255)
        
        region_effect = safe_get(vars.get('region_effect_type'), 'random')
        
        if region_effect == 'random':
            region_effect = random.choice(['brighten', 'darken'])
        
        region = result.crop((x1, y1, x2, y2))
        if region_effect == 'brighten':
            enhancer = ImageEnhance.Brightness(region)
            region = enhancer.enhance(1.5)
        else:
            enhancer = ImageEnhance.Brightness(region)
            region = enhancer.enhance(0.7)
        
        result_copy = result.copy()
        result_copy.paste(region, (x1, y1, x2, y2))
        result = Image.composite(result_copy, result, mask)
    
    # Frame overlay
    overlay_enabled = vars.get('frame_overlay_enabled') or vars.get('overlay_enabled')
    if overlay_enabled and safe_get(overlay_enabled, False):
        interval = safe_get(vars.get('frame_overlay_interval'), 1)
        try:
            interval = int(interval)
        except (ValueError, TypeError):
            interval = 1
        if (frame_index + 1) % interval == 0:
            width, height = result.size
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 10))
            if result.mode != 'RGBA':
                result = result.convert('RGBA')
            result = Image.alpha_composite(result, overlay)
            if result.mode != frame.mode and frame.mode == 'RGB':
                result = result.convert('RGB')
    
    # Shadow lines effect
    shadow_enabled = vars.get('shadow_lines_enabled') or vars.get('shadow_enabled')
    if shadow_enabled and safe_get(shadow_enabled, False):
        h_lines = safe_get(vars.get('shadow_h_lines_var'), 0)
        v_lines = safe_get(vars.get('shadow_v_lines_var'), 0)
        intensity = safe_get(vars.get('shadow_intensity_var'), 0.1)
        line_width = safe_get(vars.get('shadow_line_width_var'), 1)
        speed = safe_get(vars.get('shadow_speed_var'), 0.5)
        
        try:
            h_lines = int(h_lines)
            v_lines = int(v_lines)
            line_width = int(line_width)
            intensity = float(intensity)
            speed = float(speed)
        except (ValueError, TypeError):
            h_lines = 0
            v_lines = 0
            line_width = 1
            intensity = 0.1
            speed = 0.5
        
        result = apply_shadow_lines_effect(result, h_lines, v_lines, intensity, line_width, speed, frame_index)
    
    return result


def process_frames_with_effects(frame_files, effect_vars, progress_callback=None):
    """Process a list of frame files with effects."""
    processed_frames = []
    total_frames = len(frame_files)
    
    for i, frame_file in enumerate(frame_files):
        if stop_processing:
            break
            
        try:
            frame = Image.open(frame_file)
            processed_frame = apply_effects_to_frame(frame, effect_vars, i)
            
            # Save processed frame
            processed_filename = frame_file.replace('.jpg', '_processed.jpg')
            processed_frame.save(processed_filename, quality=95)
            processed_frames.append(processed_filename)
            
            if progress_callback:
                progress_callback(i + 1, total_frames)
                
        except Exception as e:
            print(f"Error processing frame {frame_file}: {e}")
    
    return processed_frames


def create_gif_from_frames(frame_files, output_path, fps=10, quality=75):
    """Create GIF from frames with spoofed metadata."""
    try:
        if not frame_files:
            print("No frames to create GIF from")
            return False
        
        # Generate spoofed metadata for GIF
        metadata = generate_spoofed_metadata()
        
        # Load frames
        frames = []
        for frame_file in frame_files:
            try:
                frame = Image.open(frame_file)
                frames.append(frame)
            except Exception as e:
                print(f"Error loading frame {frame_file}: {e}")
                continue
        
        if not frames:
            print("No valid frames found")
            return False
        
        # Calculate duration per frame
        duration = int(1000 / fps)  # milliseconds
        
        # Create GIF with metadata
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            optimize=True,
            quality=quality,
            # Add metadata to GIF
            comment=f"Created with {metadata['device']} using {metadata['encoder']} on {metadata['creation_time'][:10]}"
        )
        
        print(f"GIF created successfully with spoofed metadata: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error creating GIF: {e}")
        return False


def create_video_from_frames(frame_files, output_path, fps=30, codec='libx264', bitrate=2000):
    """Create video from frames with spoofed metadata."""
    try:
        if not frame_files:
            print("No frames to create video from")
            return False
        
        # Generate spoofed metadata
        metadata = generate_spoofed_metadata()
        
        # Create temporary file list for ffmpeg
        temp_dir = os.path.dirname(frame_files[0])
        file_list_path = os.path.join(temp_dir, "file_list.txt")
        
        with open(file_list_path, 'w') as f:
            for frame_file in frame_files:
                f.write(f"file '{os.path.abspath(frame_file)}'\n")
                f.write(f"duration {1/fps}\n")
        
        # Build FFmpeg command with metadata
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', file_list_path,
            '-c:v', codec,
            '-b:v', f'{bitrate}k',
            '-pix_fmt', 'yuv420p',
            '-r', str(fps),
            # Add spoofed metadata
            '-metadata', f'creation_time={metadata["creation_time"]}',
            '-metadata', f'encoder={metadata["encoder"]}',
            '-metadata', f'title=Video_{metadata["unique_id"]}',
            '-metadata', f'comment=Created with {metadata["device"]}',
            '-metadata', f'software={metadata["encoder"]} v{metadata["software_version"]}',
            '-metadata', f'timecode={metadata["timecode"]}',
            '-metadata', f'device_manufacturer={metadata["device"].split()[0] if " " in metadata["device"] else "Unknown"}',
            '-metadata', f'device_model={metadata["device"]}',
            '-movflags', '+faststart',  # Optimize for web playback
            output_path
        ]
        
        print(f"Creating video with spoofed metadata: {metadata['device']} - {metadata['encoder']}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        # Clean up temporary file
        try:
            os.remove(file_list_path)
        except:
            pass
        
        if result.returncode == 0:
            print(f"Video created successfully: {output_path}")
            return True
        else:
            print(f"Error creating video: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error in create_video_from_frames: {e}")
        return False


def generate_spoofed_metadata():
    """Generate randomized metadata to avoid detection"""
    import datetime
    import random
    
    # Random creation time within last year
    base_date = datetime.datetime.now()
    days_back = random.randint(1, 365)
    creation_time = base_date - datetime.timedelta(days=days_back)
    
    # Random software/encoder
    encoders = [
        "Adobe Premiere Pro 2023", "Final Cut Pro 10.6", "DaVinci Resolve 18",
        "Handbrake 1.6.1", "FFmpeg 5.1.2", "VLC media player", "Shotcut 22.12",
        "OpenShot 3.0", "Blender VSE", "Avidemux 2.8"
    ]
    
    # Random device signature
    devices = [
        "iPhone 14 Pro", "Samsung Galaxy S23", "Google Pixel 7", "Canon EOS R5",
        "Sony A7IV", "GoPro Hero 11", "DJI Pocket 2", "MacBook Pro M2", "Windows PC"
    ]
    
    metadata = {
        'creation_time': creation_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'encoder': random.choice(encoders),
        'device': random.choice(devices),
        'software_version': f"{random.randint(1,10)}.{random.randint(0,99)}.{random.randint(0,999)}",
        'unique_id': f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}",
        'timecode': f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}:{random.randint(0,29):02d}"
    }
    
    return metadata


def apply_additional_metadata_spoofing(file_path, metadata):
    """Apply additional metadata spoofing using FFmpeg after file creation."""
    try:
        # Get file extension and create proper temp file name
        file_ext = os.path.splitext(file_path)[1]
        temp_path = file_path.replace(file_ext, f"_temp{file_ext}")
        
        # Additional metadata fields for more comprehensive spoofing
        cmd = [
            'ffmpeg', '-y',
            '-i', file_path,
            '-c', 'copy',  # Copy streams without re-encoding
            '-metadata', f'artist={metadata["device"]}',
            '-metadata', f'album=Video Collection {random.randint(1, 100)}',
            '-metadata', f'date={metadata["creation_time"][:4]}',
            '-metadata', f'genre=Video',
            '-metadata', f'track={random.randint(1, 50)}',
            '-metadata', f'copyright=© {metadata["creation_time"][:4]} User',
            temp_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=get_subprocess_creation_flags())
        
        if result.returncode == 0:
            # Replace original file with metadata-enhanced version
            os.replace(temp_path, file_path)
            print(f"Additional metadata applied to: {file_path}")
            return True
        else:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"Warning: Could not apply additional metadata: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error applying additional metadata: {e}")
        return False


def generate_washed_media(video_path, output_folder, prefix, output_mode, effect_vars, 
                         start_time=0, end_time=None, fps=10, quality=75, 
                         codec='libx264', bitrate=2000, copies=1, speed=1.0, 
                         copy_type='exact', progress_callback=None, status_callback=None):
    """Generate washed media with spoofed metadata."""
    global stop_processing
    stop_processing = False
    
    try:
        ensure_output_folder_exists(output_folder)
        
        success_count = 0
        
        for copy_num in range(copies):
            if stop_processing:
                break
                
            if status_callback:
                status_callback(f"Processing copy {copy_num + 1}/{copies}...")
            
            # Generate unique metadata for each copy
            copy_metadata = generate_spoofed_metadata()
            
            # Determine effect variables for this copy
            if copy_type == 'variations':
                current_effect_vars = create_variation_effects(effect_vars, copy_num)
            else:
                current_effect_vars = effect_vars
            
            # Change random seed for each variation to ensure different random values
            import time
            import os
            variation_seed = int(time.time() * 1000000) + os.getpid() + copy_num * 1000 + hash(str(time.time())) % 1000000
            random.seed(variation_seed)
            np.random.seed(variation_seed % 2**32)
            
            # Check which effects are enabled
            clipping_enabled = safe_get(current_effect_vars.get('clipping_enabled'), False)
            flip_enabled = safe_get(current_effect_vars.get('flip_enabled'), False)
            brightness_enabled = safe_get(current_effect_vars.get('brightness_enabled'), False)
            contrast_enabled = safe_get(current_effect_vars.get('contrast_enabled'), False)
            saturation_enabled = safe_get(current_effect_vars.get('saturation_enabled'), False)
            hue_enabled = safe_get(current_effect_vars.get('hue_enabled'), False)
            blur_enabled = safe_get(current_effect_vars.get('blur_enabled'), False)
            resize_enabled = safe_get(current_effect_vars.get('resize_enabled'), False)
            noise_enabled = safe_get(current_effect_vars.get('noise_enabled'), False)
            fps_change_enabled = safe_get(current_effect_vars.get('fps_change_enabled'), False)
            audio_fingerprint_enabled = safe_get(current_effect_vars.get('audio_fingerprint_enabled'), False)
            
            # Start with original video path
            current_video_path = video_path
            temp_files_to_cleanup = []
            
            # Apply clipping if enabled
            if clipping_enabled:
                if status_callback:
                    status_callback(f"Applying clipping to copy {copy_num + 1}/{copies}...")
                
                clipping_min = safe_get(current_effect_vars.get('clipping_min_var'), 5)
                clipping_max = safe_get(current_effect_vars.get('clipping_max_var'), 10)
                
                clipped_video_path = os.path.join(output_folder, f"temp_clipped_{copy_num}.mp4")
                current_video_path = apply_clipping_with_ffmpeg(
                    current_video_path, clipped_video_path, clipping_min, clipping_max
                )
                
                if current_video_path == clipped_video_path:
                    temp_files_to_cleanup.append(clipped_video_path)
            
            # Apply flipping if enabled
            if flip_enabled:
                if status_callback:
                    status_callback(f"Applying flip to copy {copy_num + 1}/{copies}...")
                
                flipped_video_path = os.path.join(output_folder, f"temp_flipped_{copy_num}.mp4")
                current_video_path = apply_flipping_with_ffmpeg(
                    current_video_path, flipped_video_path
                )
                
                if current_video_path == flipped_video_path:
                    temp_files_to_cleanup.append(flipped_video_path)
            
            # Apply brightness/contrast/saturation if any are enabled
            if brightness_enabled or contrast_enabled or saturation_enabled:
                if status_callback:
                    status_callback(f"Applying color adjustments to copy {copy_num + 1}/{copies}...")
                
                # Use predefined random ranges for each effect
                brightness = 1.0
                contrast = 1.0
                saturation = 1.0
                
                if brightness_enabled:
                    brightness = random.uniform(0.9, 1.1)  # Random brightness variation
                
                if contrast_enabled:
                    contrast = random.uniform(0.95, 1.1)  # Random contrast variation
                
                if saturation_enabled:
                    saturation = random.uniform(0.9, 1.1)  # Random saturation variation
                
                color_adjusted_path = os.path.join(output_folder, f"temp_color_{copy_num}.mp4")
                current_video_path = apply_brightness_contrast_saturation_with_ffmpeg(
                    current_video_path, color_adjusted_path, brightness, contrast, saturation
                )
                
                if current_video_path == color_adjusted_path:
                    temp_files_to_cleanup.append(color_adjusted_path)
            
            # Apply hue shift if enabled
            if hue_enabled:
                if status_callback:
                    status_callback(f"Applying hue shift to copy {copy_num + 1}/{copies}...")
                
                hue_shift = random.uniform(-15.0, 15.0)  # Random hue shift ±15 degrees
                
                hue_shifted_path = os.path.join(output_folder, f"temp_hue_{copy_num}.mp4")
                current_video_path = apply_hue_shift_with_ffmpeg(
                    current_video_path, hue_shifted_path, hue_shift
                )
                
                if current_video_path == hue_shifted_path:
                    temp_files_to_cleanup.append(hue_shifted_path)
            
            # Apply blur if enabled
            if blur_enabled:
                if status_callback:
                    status_callback(f"Applying blur to copy {copy_num + 1}/{copies}...")
                
                blur_radius = random.uniform(0.5, 3.0)  # Random blur radius
                
                blurred_path = os.path.join(output_folder, f"temp_blur_{copy_num}.mp4")
                current_video_path = apply_blur_with_ffmpeg(
                    current_video_path, blurred_path, blur_radius
                )
                
                if current_video_path == blurred_path:
                    temp_files_to_cleanup.append(blurred_path)
            
            # Apply resize if enabled
            if resize_enabled:
                if status_callback:
                    status_callback(f"Applying resize to copy {copy_num + 1}/{copies}...")
                
                # Get original video dimensions
                video_info = get_video_info_ffprobe(current_video_path)
                original_width = int(video_info.get('width', 1920))
                original_height = int(video_info.get('height', 1080))
                
                # Apply random resize factor (98-102% of original)
                resize_factor = random.uniform(0.98, 1.02)
                resize_width = int(original_width * resize_factor)
                resize_height = int(original_height * resize_factor)
                
                # Ensure dimensions are even (required for H.264 encoding)
                resize_width = resize_width & ~1  # Clear least significant bit to make even
                resize_height = resize_height & ~1  # Clear least significant bit to make even
                
                resized_path = os.path.join(output_folder, f"temp_resize_{copy_num}.mp4")
                current_video_path = apply_resize_with_ffmpeg(
                    current_video_path, resized_path, resize_width, resize_height
                )
                
                if current_video_path == resized_path:
                    temp_files_to_cleanup.append(resized_path)
            
            # Apply noise if enabled
            if noise_enabled:
                if status_callback:
                    status_callback(f"Applying noise to copy {copy_num + 1}/{copies}...")
                
                noise_level = random.uniform(0.01, 0.05)  # Random noise level
                
                noisy_path = os.path.join(output_folder, f"temp_noise_{copy_num}.mp4")
                current_video_path = apply_noise_with_ffmpeg(
                    current_video_path, noisy_path, noise_level
                )
                
                if current_video_path == noisy_path:
                    temp_files_to_cleanup.append(noisy_path)
            
            # Apply FPS change if enabled
            if fps_change_enabled:
                if status_callback:
                    status_callback(f"Applying FPS change to copy {copy_num + 1}/{copies}...")
                
                fps_adjustment = random.uniform(-1.5, 1.5)  # Random FPS adjustment ±1.5
                
                fps_changed_path = os.path.join(output_folder, f"temp_fps_{copy_num}.mp4")
                current_video_path = apply_fps_change_with_ffmpeg(
                    current_video_path, fps_changed_path, fps_adjustment
                )
                
                if current_video_path == fps_changed_path:
                    temp_files_to_cleanup.append(fps_changed_path)
            
            # Apply audio fingerprint evasion if enabled
            if audio_fingerprint_enabled:
                if status_callback:
                    status_callback(f"Applying audio fingerprint evasion to copy {copy_num + 1}/{copies}...")
                
                audio_processed_path = os.path.join(output_folder, f"temp_audio_{copy_num}.mp4")
                current_video_path = apply_audio_fingerprint_evasion_with_ffmpeg(
                    current_video_path, audio_processed_path
                )
                
                if current_video_path == audio_processed_path:
                    temp_files_to_cleanup.append(audio_processed_path)
            
            # Check if any PIL effects are enabled
            bitplane_enabled = safe_get(current_effect_vars.get('bitplane_enabled'), False)
            region_enabled = safe_get(current_effect_vars.get('region_enabled'), False) or safe_get(current_effect_vars.get('region_effects_enabled'), False)
            overlay_enabled = safe_get(current_effect_vars.get('overlay_enabled'), False) or safe_get(current_effect_vars.get('frame_overlay_enabled'), False)
            shadow_enabled = safe_get(current_effect_vars.get('shadow_enabled'), False) or safe_get(current_effect_vars.get('shadow_lines_enabled'), False)
            
            pil_effects_enabled = bitplane_enabled or region_enabled or overlay_enabled or shadow_enabled
            
            if not pil_effects_enabled:
                # No PIL effects enabled - use FFmpeg output directly (MUCH faster!)
                if status_callback:
                    status_callback(f"Creating final output for copy {copy_num + 1}/{copies} (FFmpeg only)...")
                
                # Generate output filename with metadata info
                if copies > 1:
                    output_filename = f"{prefix}_copy_{copy_num + 1:03d}_{copy_metadata['unique_id']}"
                else:
                    output_filename = f"{prefix}_{copy_metadata['unique_id']}"
                
                if output_mode == 'gif':
                    # For GIF, we still need to extract frames (GIF creation requires frame sequence)
                    if status_callback:
                        status_callback(f"Extracting frames for GIF creation (copy {copy_num + 1}/{copies})...")
                    
                    temp_frames_dir = os.path.join(output_folder, f"temp_frames_{copy_num}")
                    frame_files, original_fps = extract_frames_from_video(current_video_path, start_time, end_time, temp_frames_dir)
                    
                    if frame_files:
                        output_path = os.path.join(output_folder, f"{output_filename}.gif")
                        success = create_gif_from_frames(frame_files, output_path, fps, quality)
                        
                        # Clean up frames
                        for frame_file in frame_files:
                            try:
                                if os.path.exists(frame_file):
                                    os.remove(frame_file)
                            except:
                                pass
                        
                        # Remove temp directory
                        try:
                            if os.path.exists(temp_frames_dir):
                                os.rmdir(temp_frames_dir)
                        except:
                            pass
                    else:
                        success = False
                else:
                    # For MP4, just copy the FFmpeg output with spoofed metadata
                    output_path = os.path.join(output_folder, f"{output_filename}.mp4")
                    
                    try:
                        # Copy the final FFmpeg video to output location
                        import shutil
                        shutil.copy2(current_video_path, output_path)
                        
                        # Apply spoofed metadata
                        apply_additional_metadata_spoofing(output_path, copy_metadata)
                        success = True
                        
                    except Exception as e:
                        print(f"Error copying final video: {e}")
                        success = False
                
                if success:
                    success_count += 1
                    print(f"Successfully created copy {copy_num + 1} with spoofed metadata from {copy_metadata['device']} (FFmpeg-only processing)")
                
                # Clean up temporary video files
                for temp_file in temp_files_to_cleanup:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                            print(f"Cleaned up temp file: {temp_file}")
                    except:
                        pass
                
                continue  # Skip to next copy
            
            # PIL effects are enabled - extract frames for frame-level processing
            if status_callback:
                status_callback(f"Extracting frames for PIL effects (copy {copy_num + 1}/{copies})...")
            
            temp_frames_dir = os.path.join(output_folder, f"temp_frames_{copy_num}")
            frame_files, original_fps = extract_frames_from_video(current_video_path, start_time, end_time, temp_frames_dir)
            
            if not frame_files:
                print(f"No frames extracted for copy {copy_num + 1}")
                # Clean up temp files
                for temp_file in temp_files_to_cleanup:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
                continue
            
            if stop_processing:
                # Clean up temp files
                for temp_file in temp_files_to_cleanup:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
                break
            
            # Process frames with effects
            processed_frames = process_frames_with_effects(frame_files, current_effect_vars, progress_callback)
            
            if stop_processing:
                break
            
            if not processed_frames:
                print(f"No processed frames for copy {copy_num + 1}")
                continue
            
            # Apply speed adjustment if needed
            if speed != 1.0:
                # Adjust frame selection based on speed
                if speed > 1.0:
                    # Speed up: skip frames
                    step = int(speed)
                    processed_frames = processed_frames[::step]
                else:
                    # Slow down: duplicate frames
                    factor = int(1.0 / speed)
                    new_frames = []
                    for frame in processed_frames:
                        for _ in range(factor):
                            new_frames.append(frame)
                    processed_frames = new_frames
            
            # Generate output filename with metadata info
            if copies > 1:
                output_filename = f"{prefix}_copy_{copy_num + 1:03d}_{copy_metadata['unique_id']}"
            else:
                output_filename = f"{prefix}_{copy_metadata['unique_id']}"
            
            if output_mode == 'gif':
                output_path = os.path.join(output_folder, f"{output_filename}.gif")
                success = create_gif_from_frames(processed_frames, output_path, fps, quality)
            else:
                output_path = os.path.join(output_folder, f"{output_filename}.mp4")
                success = create_video_from_frames(processed_frames, output_path, original_fps if fps is None else fps, codec, bitrate)
                
                # Apply additional metadata spoofing for videos
                if success and output_mode == 'video':
                    apply_additional_metadata_spoofing(output_path, copy_metadata)
            
            if success:
                success_count += 1
                print(f"Successfully created copy {copy_num + 1} with spoofed metadata from {copy_metadata['device']}")
            
            # Clean up processed frames for this copy
            for frame_file in processed_frames:
                try:
                    if os.path.exists(frame_file):
                        os.remove(frame_file)
                except:
                    pass
            
            # Clean up original frames
            for frame_file in frame_files:
                try:
                    if os.path.exists(frame_file):
                        os.remove(frame_file)
                except:
                    pass
            
            # Remove temp directory if empty
            try:
                if os.path.exists(temp_frames_dir):
                    os.rmdir(temp_frames_dir)
            except:
                pass
            
            # Clean up temporary video files (clipped/flipped)
            for temp_file in temp_files_to_cleanup:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        print(f"Cleaned up temp file: {temp_file}")
                except:
                    pass
        
        if status_callback:
            status_callback(f"Completed! Generated {success_count}/{copies} files with spoofed metadata")
        
        return success_count > 0
        
    except Exception as e:
        print(f"Error in generate_washed_media: {e}")
        if status_callback:
            status_callback(f"Error: {str(e)}")
        return False


def create_variation_effects(original_effect_vars, variation_seed=0):
    """Create a variation of effect parameters with randomized values within specified ranges."""
    import random
    import copy
    import time
    import os
    
    # Set seed for truly random variations (different each time)
    # Use time in microseconds + process ID + variation_seed for uniqueness
    dynamic_seed = int(time.time() * 1000000) + os.getpid() + variation_seed * 1000 + hash(str(time.time())) % 1000000
    random.seed(dynamic_seed)
    
    # Create a deep copy of the original effect variables
    varied_effects = {}
    
    # Copy all the original variables
    for key, var in original_effect_vars.items():
        varied_effects[key] = var
    
    # Create mock variables for randomized values
    class MockVar:
        def __init__(self, value):
            self.value = value
        def get(self):
            return self.value
        def set(self, value):
            self.value = value
    
    # Note: FFmpeg-handled effects (brightness, contrast, saturation, hue, blur, resize, noise) 
    # get their random values directly in the main processing loop, no need for variations here
    try:
        
        # Note: Brightness, Contrast, Saturation, Hue, Blur, Resize, Noise variations are now handled by FFmpeg
        # No need for variations here as they get random values in the main processing loop
        
        # Bitplane variation
        if original_effect_vars.get('bitplane_enabled', MockVar(False)).get():
            intensity = original_effect_vars.get('bitplane_intensity_var', MockVar(0.5)).get()
            planes = original_effect_vars.get('bitplane_planes_var', MockVar(1)).get()
            # Add some randomness
            random_intensity = max(0.1, min(1.0, intensity * random.uniform(0.8, 1.2)))
            random_planes = max(1, min(3, planes + random.randint(-1, 1)))
            varied_effects['bitplane_intensity_var'] = MockVar(random_intensity)
            varied_effects['bitplane_planes_var'] = MockVar(random_planes)
        
        # Shadow lines variation
        if original_effect_vars.get('shadow_enabled', MockVar(False)).get():
            h_lines = original_effect_vars.get('shadow_h_lines_var', MockVar(0)).get()
            v_lines = original_effect_vars.get('shadow_v_lines_var', MockVar(0)).get()
            intensity = original_effect_vars.get('shadow_intensity_var', MockVar(0.1)).get()
            line_width = original_effect_vars.get('shadow_line_width_var', MockVar(1)).get()
            speed = original_effect_vars.get('shadow_speed_var', MockVar(0.5)).get()
            
            # Add randomness to shadow parameters
            varied_effects['shadow_h_lines_var'] = MockVar(max(0, h_lines + random.randint(-2, 2)))
            varied_effects['shadow_v_lines_var'] = MockVar(max(0, v_lines + random.randint(-2, 2)))
            varied_effects['shadow_intensity_var'] = MockVar(max(0.1, min(0.5, intensity * random.uniform(0.8, 1.2))))
            varied_effects['shadow_line_width_var'] = MockVar(max(1, min(5, line_width + random.randint(-1, 1))))
            varied_effects['shadow_speed_var'] = MockVar(max(0.5, min(2.0, speed * random.uniform(0.9, 1.1))))
        
        # Clipping variation - use independent random state for truly random clipping
        if original_effect_vars.get('clipping_enabled', MockVar(False)).get():
            min_val = original_effect_vars.get('clipping_min_var', MockVar(5.0)).get()
            max_val = original_effect_vars.get('clipping_max_var', MockVar(10.0)).get()
            # Use independent random state for clipping variations
            import time
            clip_random = random.Random(time.time() * 1000 + random.randint(0, 9999))
            # Add some randomness to the range
            new_min = max(1.0, min_val + clip_random.uniform(-2, 2))
            new_max = max(new_min + 1.0, max_val + clip_random.uniform(-2, 2))
            varied_effects['clipping_min_var'] = MockVar(new_min)
            varied_effects['clipping_max_var'] = MockVar(new_max)
        
        # Flip variation - randomly enable/disable for variation
        if original_effect_vars.get('flip_enabled', MockVar(False)).get():
            # Use independent random state for flip variations
            flip_random = random.Random(time.time() * 1000 + random.randint(0, 9999))
            # 70% chance to keep flip enabled for variations
            flip_chance = flip_random.random() < 0.7
            varied_effects['flip_enabled'] = MockVar(flip_chance)
        
    except Exception as e:
        print(f"Error creating variation effects: {e}")
        # Return original effects if there's an error
        return original_effect_vars
    
    return varied_effects


def stop_generation():
    """Stop the current generation process."""
    global stop_processing
    stop_processing = True


def apply_quick_wash_preset(effect_vars, wash_type):
    """Apply quick wash presets to effect variables."""
    # Reset all effects first
    for key in effect_vars:
        if 'enabled' in key:
            try:
                effect_vars[key].set(False)
            except:
                pass
    
    if wash_type == 'normal':
        # Normal wash: light effects (FFmpeg effects use predefined ranges)
        effect_vars.get('brightness_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('contrast_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('saturation_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('noise_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('fps_change_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('resize_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('flip_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('audio_fingerprint_enabled', type('', (), {'set': lambda x: None})()).set(True)
        
        # Video effects (still have controls)
        effect_vars.get('clipping_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('clipping_min_var', type('', (), {'set': lambda x: None})()).set(3)
        effect_vars.get('clipping_max_var', type('', (), {'set': lambda x: None})()).set(7)
        
    elif wash_type == 'deep':
        # Deep wash: moderate effects (FFmpeg effects use predefined ranges)
        effect_vars.get('brightness_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('contrast_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('saturation_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('noise_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('fps_change_enabled', type('', (), {'set': lambda x: None})()).set(True)
        
    elif wash_type == 'extreme':
        # Extreme wash: heavy effects (FFmpeg effects use predefined ranges)
        effect_vars.get('brightness_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('contrast_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('saturation_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('hue_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('noise_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('fps_change_enabled', type('', (), {'set': lambda x: None})()).set(True)
        
        # PIL effects (still have controls)
        effect_vars.get('bitplane_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('bitplane_intensity_var', type('', (), {'set': lambda x: None})()).set(0.3)
        effect_vars.get('bitplane_planes_var', type('', (), {'set': lambda x: None})()).set(2)
        
        # Video effects (still have controls)
        effect_vars.get('clipping_enabled', type('', (), {'set': lambda x: None})()).set(True)
        effect_vars.get('clipping_min_var', type('', (), {'set': lambda x: None})()).set(8)
        effect_vars.get('clipping_max_var', type('', (), {'set': lambda x: None})()).set(12)
        
        effect_vars.get('flip_enabled', type('', (), {'set': lambda x: None})()).set(True)
