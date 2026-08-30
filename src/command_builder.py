from settings import OUTPUT_WIDTH, OUTPUT_HEIGHT, DEFAULT_CRF, FPS

def build_ffmpeg_slideshow_command(
    ffmpeg_path,
    images_data,
    output_path,
    photo_duration,
    transition_duration,
    zoom_end,
    preview=False
):
    cmd = [str(ffmpeg_path), "-y"]
    
    # Configure presets based on preview mode
    crf_value = 35 if preview else DEFAULT_CRF
    preset_value = "ultrafast" if preview else "medium"
    scale_factor = 1 if preview else 4
    current_fps = 15 if preview else FPS
    
    # Inputs
    input_durations = []
    num_images = len(images_data)
    
    for i, img in enumerate(images_data):
        if num_images == 1:
            dur = photo_duration
        elif i == 0 or i == num_images - 1:
            dur = photo_duration + transition_duration
        else:
            dur = photo_duration + 2 * transition_duration
            
        input_durations.append(dur)
        
        cmd.extend([
            "-loop", "1",
            "-t", str(dur),
            "-i", img["path"]
        ])
    
    filters = []
    # Process each image
    for i, img in enumerate(images_data):
        dur = input_durations[i]
        total_frames_per_image = int(dur * current_fps)
        
        cw = img.get("crop_w", 1.0)
        ch = img.get("crop_h", 1.0)
        cx = img.get("crop_x", 0.0)
        cy = img.get("crop_y", 0.0)
        
        ax = img.get("anchor_x", 0.5)
        ay = img.get("anchor_y", 0.5)
        
        # 1. Crop original image based on user framing
        # 2. Scale to output resolution
        # 3. Zoompan
        
        filter_str = (
            f"[{i}:v]"
            f"crop=w={cw}*iw:h={ch}*ih:x={cx}*iw:y={cy}*ih,"
            f"scale={OUTPUT_WIDTH*scale_factor}:{OUTPUT_HEIGHT*scale_factor}:force_original_aspect_ratio=increase,"
            f"crop={OUTPUT_WIDTH*scale_factor}:{OUTPUT_HEIGHT*scale_factor},"
            f"zoompan=z='1+({zoom_end}-1)*on/{total_frames_per_image - 1}':"
            f"x='{ax}*(iw-iw/zoom)':"
            f"y='{ay}*(ih-ih/zoom)':"
            f"d=1:"
            f"s={OUTPUT_WIDTH}x{OUTPUT_HEIGHT}:"
            f"fps={current_fps},"
            f"setpts=PTS-STARTPTS,"
            f"settb=1/{current_fps},"
            f"fps={current_fps}"
            f"[v{i}]"
        )
        filters.append(filter_str)
        
    # Xfade transitions
    if num_images > 1:
        current_in = "[v0]"
        current_offset = photo_duration
        
        for i in range(1, num_images):
            next_in = f"[v{i}]"
            out_name = f"[x{i}]" if i < num_images - 1 else "[v]"
            
            fade_filter = f"{current_in}{next_in}xfade=transition=fade:duration={transition_duration}:offset={current_offset}{out_name}"
            
            # For the last transition, add format
            if i == num_images - 1:
                fade_filter = f"{current_in}{next_in}xfade=transition=fade:duration={transition_duration}:offset={current_offset},format=yuv420p{out_name}"
            
            filters.append(fade_filter)
            
            current_in = out_name
            current_offset += (photo_duration + transition_duration)
    else:
        filters.append("[v0]format=yuv420p[v]")

    filter_complex_str = ";".join(filters)
    
    cmd.extend([
        "-filter_complex", filter_complex_str,
        "-map", "[v]",
        "-c:v", "libx264",
        "-crf", str(crf_value),
        "-preset", preset_value,
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ])
    
    return cmd
