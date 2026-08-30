import os
import subprocess
import json

from ffmpeg_runtime import get_ffprobe_path

def get_video_info(input_path: str) -> str:
    cmd = [
        str(get_ffprobe_path()),
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "format=format_name:stream=width,height,r_frame_rate,codec_name",
        "-of", "json",
        input_path
    ]
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=flags)
        if result.returncode != 0:
            return "Error a l'obtenir les propietats."
        data = json.loads(result.stdout)
        
        format_name = data.get("format", {}).get("format_name", "Desconegut").split(',')[0].upper()
        stream = data.get("streams", [{}])[0]
        width = stream.get("width", "?")
        height = stream.get("height", "?")
        fps_str = stream.get("r_frame_rate", "0/1")
        codec = stream.get("codec_name", "Desconegut").upper()
        
        # Calculate fps
        try:
            num, den = fps_str.split('/')
            if den != '0':
                fps = round(int(num) / int(den), 2)
                if fps.is_integer():
                    fps = int(fps)
            else:
                fps = "?"
        except ValueError:
            fps = fps_str
            
        return f"{width}x{height} • {fps} FPS • {format_name} • {codec}"
    except Exception:
        return "Propietats no disponibles"

def get_output_path(input_path, output_dir=None, output_name=None):
    if output_dir:
        directory = output_dir
    else:
        directory = os.path.dirname(input_path)
        
    filename = os.path.basename(input_path)
    original_name, extension = os.path.splitext(filename)
    
    if output_name:
        if output_name.lower().endswith(('.mp4', '.mov', '.mkv')):
            final_name = output_name
        else:
            final_name = f"{output_name}.mp4"
    else:
        final_name = f"passafotos_{original_name}.mp4"
        
    return os.path.normpath(os.path.join(
        directory,
        final_name,
    ))

def get_duration(input_path) -> float:
    """Return the total duration of the video in seconds."""
    cmd = [
        str(get_ffprobe_path()),
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_path
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError("No s'ha pogut obtenir la durada del vídeo.")

    try:
        return float(result.stdout.strip())
    except Exception:
        raise RuntimeError("Error a l'obtenir la durada del vídeo.")

def get_dimensions(input_path):
    cmd = [
        str(get_ffprobe_path()),
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        input_path
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError("No s'ha pogut analitzar el vídeo amb ffprobe.")

    try:
        width_str, height_str = result.stdout.strip().split("x")
        return int(width_str), int(height_str)
    except Exception:
        raise RuntimeError("Error a l'obtenir les dimensions del vídeo.")
