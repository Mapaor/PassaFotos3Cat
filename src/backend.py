import os
import subprocess
import threading
import json
import tempfile
import time
import glob
from urllib.parse import unquote
# pyrefly: ignore [missing-import]
from PySide6.QtCore import QObject, Slot, Signal

from ffmpeg_runtime import get_ffmpeg_path
from utils import get_output_path
from command_builder import build_ffmpeg_concat_command
from settings import OUTPUT_WIDTH, OUTPUT_HEIGHT, FPS
from renderer import render_video_clip

def _clean_path(path: str) -> str:
    if not path:
        return ""
    if path.startswith("file:///"):
        path = path[8:]
    return unquote(path)

class VideoConverter(QObject):
    conversionStarted = Signal()
    conversionFinished = Signal(bool, str)
    previewFinished = Signal(bool, str)
    progressUpdated = Signal(float, str)

    def __init__(self):
        super().__init__()
        self.abort_event = threading.Event()
        
        # Setup specific temp directory and clean it up on startup
        self.temp_dir = os.path.join(tempfile.gettempdir(), "passafotos3cat")
        os.makedirs(self.temp_dir, exist_ok=True)
        for old_file in glob.glob(os.path.join(self.temp_dir, "*.mp4")):
            try:
                os.remove(old_file)
            except OSError:
                pass

    @Slot(str, str, str, float, float, float, float)
    def convert_slideshow(
        self,
        images_json: str,
        output_dir: str,
        output_name: str,
        photo_duration: float,
        transition_duration: float,
        zoom_end: float,
        tail_duration: float
    ):
        output_dir = _clean_path(output_dir)
        
        try:
            images_data = json.loads(images_json)
        except json.JSONDecodeError:
            self.conversionFinished.emit(False, "Error llegint les dades de les imatges.")
            return
            
        if not images_data:
            self.conversionFinished.emit(False, "No hi ha imatges per processar.")
            return

        for img in images_data:
            img["path"] = _clean_path(img.get("path", ""))

        self.conversionStarted.emit()
        threading.Thread(
            target=self._convert_thread,
            args=(
                images_data, output_dir, output_name,
                photo_duration, transition_duration, zoom_end, tail_duration
            ),
            daemon=True
        ).start()

    def _convert_thread(
        self,
        images_data, output_dir, output_name,
        photo_duration, transition_duration, zoom_end, tail_duration
    ):
        try:
            self.abort_event.clear()
            base_path = images_data[0]["path"]
            output_path = get_output_path(base_path, output_dir, output_name)
            
            num_images = len(images_data)
            ffmpeg_bin = get_ffmpeg_path()
            temp_dir = self.temp_dir
            temp_videos = []
            
            if num_images == 1:
                total_duration = photo_duration + tail_duration
            else:
                total_duration = (num_images * photo_duration) + ((num_images - 1) * transition_duration) + tail_duration
            
            # Phase 1: Python rendering
            for i, img in enumerate(images_data):
                if self.abort_event.is_set():
                    break
                    
                temp_vid = os.path.join(temp_dir, f"passafotos_temp_{int(time.time()*1000)}_{i}.mp4")
                temp_videos.append(temp_vid)
                
                dur = photo_duration if num_images == 1 else (photo_duration + transition_duration if i == 0 or i == num_images - 1 else photo_duration + 2 * transition_duration)
                if i == num_images - 1:
                    dur += tail_duration
                total_frames = int(dur * FPS)
                
                def progress_cb(frame_idx, idx=i):
                    base_progress = (idx / num_images)
                    current_progress = (frame_idx / max(1, total_frames)) * (1.0 / num_images)
                    self.progressUpdated.emit(base_progress + current_progress, "Generant frames amb QPainter (1/2)")
                
                render_video_clip(
                    image_path=img["path"], out_path=temp_vid, ffmpeg_path=ffmpeg_bin,
                    width=OUTPUT_WIDTH, height=OUTPUT_HEIGHT, fps=FPS, duration=dur,
                    zoom_end=zoom_end, crop_x=img.get("crop_x", 0.0), crop_y=img.get("crop_y", 0.0),
                    crop_w=img.get("crop_w", 1.0), crop_h=img.get("crop_h", 1.0),
                    anchor_x=img.get("anchor_x", 0.5), anchor_y=img.get("anchor_y", 0.5),
                    abort_event=self.abort_event, progress_callback=progress_cb
                )
                
            if self.abort_event.is_set():
                for v in temp_videos:
                    if os.path.exists(v): os.remove(v)
                return
                
            # Phase 2: FFmpeg xfade
            cmd = build_ffmpeg_concat_command(ffmpeg_bin, temp_videos, output_path, photo_duration, transition_duration, preview=False)
            output = cmd.pop()
            cmd.extend(["-progress", "pipe:1", "-nostats", output])
            
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stderr_lines = []
            def read_stderr(pipe):
                for l in pipe:
                    stderr_lines.append(l.strip())
            threading.Thread(target=read_stderr, args=(process.stderr,), daemon=True).start()
            
            for line in process.stdout:
                if line.strip().startswith("out_time_us="):
                    try:
                        out_time_us = int(line.strip().split("=", 1)[1])
                        if total_duration > 0:
                            percent = min(out_time_us / (total_duration * 1_000_000), 1.0)
                            self.progressUpdated.emit(percent, "Generant vídeo amb FFmpeg (2/2)")
                    except ValueError:
                        pass
                elif line.strip() == "progress=end":
                    self.progressUpdated.emit(1.0, "Generant vídeo amb FFmpeg (2/2)")
            
            process.wait()
            
            for v in temp_videos:
                if os.path.exists(v): os.remove(v)
                
            if process.returncode != 0:
                error_msg = "\\n".join(stderr_lines[-5:]) if stderr_lines else "Error desconegut."
                raise RuntimeError(f"FFmpeg ha retornat un error:\\n{error_msg}")
                
            self.conversionFinished.emit(True, f"Vídeo desat a: {output_path}")

        except Exception as e:
            self.conversionFinished.emit(False, str(e))

    @Slot(str, float, float, float, float)
    def preview_slideshow(
        self,
        images_json: str,
        photo_duration: float,
        transition_duration: float,
        zoom_end: float,
        tail_duration: float
    ):
        try:
            images_data = json.loads(images_json)
        except json.JSONDecodeError:
            self.previewFinished.emit(False, "Error llegint les dades de les imatges.")
            return
            
        if not images_data:
            self.previewFinished.emit(False, "No hi ha imatges per processar.")
            return

        for img in images_data:
            img["path"] = _clean_path(img.get("path", ""))

        self.conversionStarted.emit()
        threading.Thread(
            target=self._preview_thread,
            args=(
                images_data, photo_duration, transition_duration, zoom_end, tail_duration
            ),
            daemon=True
        ).start()

    def _preview_thread(
        self,
        images_data, photo_duration, transition_duration, zoom_end, tail_duration
    ):
        try:
            self.abort_event.clear()
            temp_dir = self.temp_dir
            for old_file in glob.glob(os.path.join(temp_dir, "passafotos_preview_*.mp4")):
                try: os.remove(old_file)
                except OSError: pass

            output_path = os.path.join(temp_dir, f"passafotos_preview_{int(time.time()*1000)}.mp4")
            num_images = len(images_data)
            ffmpeg_bin = get_ffmpeg_path()
            temp_videos = []
            
            preview_fps = 15
            preview_width = 1280
            preview_height = 720
            
            if num_images == 1:
                total_duration = photo_duration + tail_duration
            else:
                total_duration = (num_images * photo_duration) + ((num_images - 1) * transition_duration) + tail_duration

            # Phase 1: Python rendering
            for i, img in enumerate(images_data):
                if self.abort_event.is_set():
                    break
                    
                temp_vid = os.path.join(temp_dir, f"passafotos_temp_prev_{int(time.time()*1000)}_{i}.mp4")
                temp_videos.append(temp_vid)
                
                dur = photo_duration if num_images == 1 else (photo_duration + transition_duration if i == 0 or i == num_images - 1 else photo_duration + 2 * transition_duration)
                if i == num_images - 1:
                    dur += tail_duration
                total_frames = int(dur * preview_fps)
                
                def progress_cb(frame_idx, idx=i):
                    base_progress = (idx / num_images)
                    current_progress = (frame_idx / max(1, total_frames)) * (1.0 / num_images)
                    self.progressUpdated.emit(base_progress + current_progress, "Generant frames amb QPainter (1/2)")
                
                render_video_clip(
                    image_path=img["path"], out_path=temp_vid, ffmpeg_path=ffmpeg_bin,
                    width=preview_width, height=preview_height, fps=preview_fps, duration=dur,
                    zoom_end=zoom_end, crop_x=img.get("crop_x", 0.0), crop_y=img.get("crop_y", 0.0),
                    crop_w=img.get("crop_w", 1.0), crop_h=img.get("crop_h", 1.0),
                    anchor_x=img.get("anchor_x", 0.5), anchor_y=img.get("anchor_y", 0.5),
                    abort_event=self.abort_event, progress_callback=progress_cb
                )
                
            if self.abort_event.is_set():
                for v in temp_videos:
                    if os.path.exists(v): os.remove(v)
                return
                
            # Phase 2: FFmpeg xfade
            cmd = build_ffmpeg_concat_command(ffmpeg_bin, temp_videos, output_path, photo_duration, transition_duration, preview=True)
            output = cmd.pop()
            cmd.extend(["-progress", "pipe:1", "-nostats", output])
            
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stderr_lines = []
            def read_stderr(pipe):
                for l in pipe:
                    stderr_lines.append(l.strip())
            threading.Thread(target=read_stderr, args=(process.stderr,), daemon=True).start()
            
            for line in process.stdout:
                if line.strip().startswith("out_time_us="):
                    try:
                        out_time_us = int(line.strip().split("=", 1)[1])
                        if total_duration > 0:
                            percent = min(out_time_us / (total_duration * 1_000_000), 1.0)
                            self.progressUpdated.emit(percent, "Generant vídeo amb FFmpeg (2/2)")
                    except ValueError:
                        pass
                elif line.strip() == "progress=end":
                    self.progressUpdated.emit(1.0, "Generant vídeo amb FFmpeg (2/2)")
            
            process.wait()
            
            for v in temp_videos:
                if os.path.exists(v): os.remove(v)
                
            if process.returncode != 0:
                error_msg = "\\n".join(stderr_lines[-5:]) if stderr_lines else "Error desconegut."
                raise RuntimeError(f"FFmpeg preview ha retornat un error:\\n{error_msg}")

            self.previewFinished.emit(True, f"file:///{output_path.replace(chr(92), '/')}")

        except Exception as e:
            self.previewFinished.emit(False, str(e))

    @Slot(str)
    def open_and_select_file(self, file_path: str):
        import sys
        file_path = _clean_path(file_path)
        if not file_path or not os.path.exists(file_path):
            return
            
        if sys.platform == 'win32':
            subprocess.Popen(['explorer', f'/select,{os.path.normpath(file_path)}'])
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', '-R', file_path])
        else:
            subprocess.Popen(['xdg-open', os.path.dirname(file_path)])


