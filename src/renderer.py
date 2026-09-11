import subprocess
import threading
from pathlib import Path
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import Qt, QRectF

def load_and_prepare_image(path):
    img = QImage(path)
    if img.isNull():
        raise RuntimeError(f"Could not load image {path}")
    if img.format() != QImage.Format_ARGB32_Premultiplied:
        img = img.convertToFormat(QImage.Format_ARGB32_Premultiplied)
    return img

def get_image_geometry(img_w, img_h, width, height, zoom_end, crop_x, crop_y, crop_w, crop_h, anchor_x, anchor_y):
    start_left = crop_x * img_w
    start_top = crop_y * img_h
    start_width = crop_w * img_w
    start_height = crop_h * img_h
    
    target_aspect = width / height
    current_aspect = start_width / start_height
    
    if current_aspect > target_aspect:
        new_width = start_height * target_aspect
        start_left += (start_width - new_width) / 2
        start_width = new_width
    elif current_aspect < target_aspect:
        new_height = start_width / target_aspect
        start_top += (start_height - new_height) / 2
        start_height = new_height
        
    start_rect = QRectF(start_left, start_top, start_width, start_height)
    
    end_width = start_width / zoom_end
    end_height = start_height / zoom_end
    
    anchor_px_x = start_left + (anchor_x * start_width)
    anchor_px_y = start_top + (anchor_y * start_height)
    
    end_left = anchor_px_x - (anchor_x * end_width)
    end_top = anchor_px_y - (anchor_y * end_height)
    end_rect = QRectF(end_left, end_top, end_width, end_height)
    
    return start_rect, end_rect

def render_full_slideshow(
    images_data: list,
    out_path: str,
    ffmpeg_path: str,
    width: int,
    height: int,
    fps: int,
    photo_duration: float,
    transition_duration: float,
    zoom_end: float,
    tail_duration: float,
    crf: int,
    preset: str,
    abort_event: threading.Event,
    progress_callback=None
):
    """
    Single-pass full slideshow rendering natively in QPainter.
    Handles zooming and crossfade transitions simultaneously.
    """
    num_images = len(images_data)
    if num_images == 0:
        return
        
    timeline = []
    total_duration = 0.0
    
    current_time = 0.0
    for i in range(num_images):
        start_t = current_time
        
        if i == 0:
            if num_images == 1:
                end_t = start_t + photo_duration + tail_duration
            else:
                end_t = start_t + photo_duration + transition_duration
            next_start_time = start_t + photo_duration
        elif i == num_images - 1:
            end_t = start_t + transition_duration + photo_duration + tail_duration
        else:
            end_t = start_t + transition_duration + photo_duration + transition_duration
            next_start_time = start_t + transition_duration + photo_duration
            
        timeline.append({
            "idx": i,
            "start_t": start_t,
            "end_t": end_t,
            "path": images_data[i]["path"],
            "dict": images_data[i]
        })
        
        if i < num_images - 1:
            current_time = next_start_time
            
    total_duration = timeline[-1]["end_t"]
        
    total_frames = int(total_duration * fps)
    
    cmd = [
        str(ffmpeg_path), "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    stderr_bytes = bytearray()
    def read_stderr():
        while True:
            chunk = proc.stderr.read(1024)
            if not chunk: break
            stderr_bytes.extend(chunk)
            
    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    stderr_thread.start()
    
    try:
        cache = {}
        geometry_cache = {}
        out_rect = QRectF(0, 0, width, height)
        
        for f in range(total_frames):
            if abort_event.is_set():
                break
                
            t = f / fps
            
            # Find active images
            active = []
            for item in timeline:
                if item["start_t"] <= t < item["end_t"]:
                    active.append(item)
                    
            # Memory cache management
            active_indices = [item["idx"] for item in active]
            for k in list(cache.keys()):
                if k not in active_indices:
                    del cache[k]
                    del geometry_cache[k]
                    
            for item in active:
                idx = item["idx"]
                if idx not in cache:
                    cache[idx] = load_and_prepare_image(item["path"])
                    geom = get_image_geometry(
                        cache[idx].width(), cache[idx].height(),
                        width, height, zoom_end,
                        item["dict"].get("crop_x", 0.0), item["dict"].get("crop_y", 0.0),
                        item["dict"].get("crop_w", 1.0), item["dict"].get("crop_h", 1.0),
                        item["dict"].get("anchor_x", 0.5), item["dict"].get("anchor_y", 0.5)
                    )
                    geometry_cache[idx] = geom
                    
            # Drawing
            out_img = QImage(width, height, QImage.Format_RGB888)
            out_img.fill(Qt.black)
            painter = QPainter(out_img)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.setRenderHint(QPainter.Antialiasing)
            
            for act_idx, item in enumerate(active):
                idx = item["idx"]
                img = cache[idx]
                start_rect, end_rect = geometry_cache[idx]
                
                item_duration = item["end_t"] - item["start_t"]
                z = (t - item["start_t"]) / max(0.001, item_duration)
                z = max(0.0, min(1.0, z))
                
                curr_left = start_rect.left() + (end_rect.left() - start_rect.left()) * z
                curr_top = start_rect.top() + (end_rect.top() - start_rect.top()) * z
                curr_width = start_rect.width() + (end_rect.width() - start_rect.width()) * z
                curr_height = start_rect.height() + (end_rect.height() - start_rect.height()) * z
                curr_rect = QRectF(curr_left, curr_top, curr_width, curr_height)
                
                opacity = 1.0
                if transition_duration > 0 and act_idx > 0:
                    fade = (t - item["start_t"]) / transition_duration
                    opacity = max(0.0, min(1.0, fade))
                    
                painter.setOpacity(opacity)
                painter.drawImage(out_rect, img, curr_rect)
                
            painter.end()
            
            ptr = out_img.constBits()
            try:
                raw_bytes = ptr.tobytes()
            except AttributeError:
                raw_bytes = bytes(ptr)
                
            proc.stdin.write(raw_bytes)
            
            if progress_callback:
                progress_callback(f, total_frames)
                
    finally:
        try: proc.stdin.close()
        except Exception: pass
        proc.wait()
        stderr_thread.join()
        
    if abort_event.is_set():
        if Path(out_path).exists():
            try: Path(out_path).unlink()
            except Exception: pass
        raise InterruptedError("Render was cancelled")
        
    if proc.returncode != 0:
        err = stderr_bytes.decode('utf-8', errors='ignore') if stderr_bytes else "Unknown error"
        raise RuntimeError(f"FFmpeg render error: {err}")
