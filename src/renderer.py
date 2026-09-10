import subprocess
import threading
from pathlib import Path
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import Qt, QRectF

def render_video_clip(
    image_path: str,
    out_path: str,
    ffmpeg_path: str,
    width: int,
    height: int,
    fps: int,
    duration: float,
    zoom_end: float,
    crop_x: float,
    crop_y: float,
    crop_w: float,
    crop_h: float,
    anchor_x: float,
    anchor_y: float,
    abort_event: threading.Event,
    progress_callback=None
):
    """
    Renders a zoompan video clip for a single image using QPainter and pipes raw frames to FFmpeg.
    """
    img = QImage(image_path)
    if img.isNull():
        raise RuntimeError(f"Could not load image {image_path}")

    # Ensure format is optimal for scaling and drawing
    if img.format() != QImage.Format_ARGB32_Premultiplied:
        img = img.convertToFormat(QImage.Format_ARGB32_Premultiplied)

    total_frames = int(duration * fps)
    
    orig_w = img.width()
    orig_h = img.height()
    
    # Calculate start rect based on crop
    start_left = crop_x * orig_w
    start_top = crop_y * orig_h
    start_width = crop_w * orig_w
    start_height = crop_h * orig_h
    
    # --- ASPECT RATIO CORRECTION ---
    # To prevent stretching, the start_rect MUST have exactly the same aspect ratio as the output video.
    # If it doesn't, we center-crop it (equivalent to FFmpeg's force_original_aspect_ratio=increase + crop).
    target_aspect = width / height
    current_aspect = start_width / start_height
    
    if current_aspect > target_aspect:
        # Crop is too wide -> clip left/right
        new_width = start_height * target_aspect
        start_left += (start_width - new_width) / 2
        start_width = new_width
    elif current_aspect < target_aspect:
        # Crop is too tall -> clip top/bottom
        new_height = start_width / target_aspect
        start_top += (start_height - new_height) / 2
        start_height = new_height
        
    start_rect = QRectF(start_left, start_top, start_width, start_height)
    
    # Calculate end rect based on zoom and anchor
    end_width = start_width / zoom_end
    end_height = start_height / zoom_end
    
    # The anchor is calculated relative to the CORRECTED start_rect to ensure we don't zoom out of bounds
    anchor_px_x = start_left + (anchor_x * start_width)
    anchor_px_y = start_top + (anchor_y * start_height)
    
    end_left = anchor_px_x - (anchor_x * end_width)
    end_top = anchor_px_y - (anchor_y * end_height)
    end_rect = QRectF(end_left, end_top, end_width, end_height)
    
    cmd = [
        str(ffmpeg_path),
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "0",
        "-pix_fmt", "yuv420p", # Ensures output is compatible with final xfade/concat
        str(out_path)
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    stderr_bytes = bytearray()
    def read_stderr():
        while True:
            chunk = proc.stderr.read(1024)
            if not chunk:
                break
            stderr_bytes.extend(chunk)
            
    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    stderr_thread.start()
    
    try:
        out_rect = QRectF(0, 0, width, height)
        for i in range(total_frames):
            if abort_event.is_set():
                break
                
            # Interpolation factor (0.0 to 1.0)
            t = i / max(1, total_frames - 1)
            
            # Interpolate current rect
            curr_left = start_rect.left() + (end_rect.left() - start_rect.left()) * t
            curr_top = start_rect.top() + (end_rect.top() - start_rect.top()) * t
            curr_width = start_rect.width() + (end_rect.width() - start_rect.width()) * t
            curr_height = start_rect.height() + (end_rect.height() - start_rect.height()) * t
            
            curr_rect = QRectF(curr_left, curr_top, curr_width, curr_height)
            
            # Draw frame
            out_img = QImage(width, height, QImage.Format_RGB888)
            out_img.fill(Qt.black)
            
            painter = QPainter(out_img)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.setRenderHint(QPainter.Antialiasing)
            
            painter.drawImage(out_rect, img, curr_rect)
            painter.end()
            
            # Write to FFmpeg
            ptr = out_img.constBits()
            # In PySide6, constBits() returns a memoryview or sip.voidptr that can be converted to bytes
            try:
                raw_bytes = ptr.tobytes()
            except AttributeError:
                raw_bytes = bytes(ptr)
                
            proc.stdin.write(raw_bytes)
            
            if progress_callback:
                progress_callback(i)
                
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        proc.wait()
        stderr_thread.join()
        
    if abort_event.is_set():
        if Path(out_path).exists():
            try:
                Path(out_path).unlink()
            except Exception:
                pass
        raise InterruptedError("Render was cancelled")
        
    if proc.returncode != 0:
        err = stderr_bytes.decode('utf-8', errors='ignore') if stderr_bytes else "Unknown error"
        raise RuntimeError(f"FFmpeg render error: {err}")
