from settings import DEFAULT_CRF, FPS

def build_ffmpeg_concat_command(
    ffmpeg_path,
    video_paths,
    output_path,
    photo_duration,
    transition_duration,
    preview=False
):
    cmd = [str(ffmpeg_path), "-y"]
    
    # Configure presets based on preview mode
    crf_value = 35 if preview else DEFAULT_CRF
    preset_value = "ultrafast" if preview else "medium"
    
    num_videos = len(video_paths)
    
    # Inputs
    for path in video_paths:
        cmd.extend(["-i", path])
        
    filters = []
    
    # Transitions
    if num_videos > 1:
        if transition_duration > 0:
            current_in = "[0:v]"
            current_offset = photo_duration
            
            for i in range(1, num_videos):
                next_in = f"[{i}:v]"
                out_name = f"[x{i}]" if i < num_videos - 1 else "[v]"
                
                fade_filter = f"{current_in}{next_in}xfade=transition=fade:duration={transition_duration}:offset={current_offset}{out_name}"
                
                # For the last transition, add format
                if i == num_videos - 1:
                    fade_filter = f"{current_in}{next_in}xfade=transition=fade:duration={transition_duration}:offset={current_offset},format=yuv420p{out_name}"
                
                filters.append(fade_filter)
                
                current_in = out_name
                current_offset += (photo_duration + transition_duration)
        else:
            concat_inputs = "".join(f"[{i}:v]" for i in range(num_videos))
            filters.append(f"{concat_inputs}concat=n={num_videos}:v=1:a=0,format=yuv420p[v]")
    else:
        filters.append("[0:v]format=yuv420p[v]")

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
