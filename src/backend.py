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
from settings import OUTPUT_WIDTH, OUTPUT_HEIGHT, FPS
from renderer import render_full_slideshow

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
            ffmpeg_bin = get_ffmpeg_path()
            
            def progress_cb(f, total_frames):
                percent = f / max(1, total_frames)
                self.progressUpdated.emit(percent, "Generant vídeo...")
                
            render_full_slideshow(
                images_data=images_data,
                out_path=output_path,
                ffmpeg_path=ffmpeg_bin,
                width=OUTPUT_WIDTH,
                height=OUTPUT_HEIGHT,
                fps=FPS,
                photo_duration=photo_duration,
                transition_duration=transition_duration,
                zoom_end=zoom_end,
                tail_duration=tail_duration,
                crf=18,
                preset="medium",
                abort_event=self.abort_event,
                progress_callback=progress_cb
            )
            
            self.progressUpdated.emit(1.0, "Generant vídeo...")
            self.conversionFinished.emit(True, f"Vídeo desat a: {output_path}")

        except InterruptedError:
            self.conversionFinished.emit(False, "Operació cancel·lada.")
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
            ffmpeg_bin = get_ffmpeg_path()
            
            preview_fps = 15
            preview_width = 1280
            preview_height = 720
            
            def progress_cb(f, total_frames):
                percent = f / max(1, total_frames)
                self.progressUpdated.emit(percent, "Generant vídeo...")
                
            render_full_slideshow(
                images_data=images_data,
                out_path=output_path,
                ffmpeg_path=ffmpeg_bin,
                width=preview_width,
                height=preview_height,
                fps=preview_fps,
                photo_duration=photo_duration,
                transition_duration=transition_duration,
                zoom_end=zoom_end,
                tail_duration=tail_duration,
                crf=23,
                preset="ultrafast",
                abort_event=self.abort_event,
                progress_callback=progress_cb
            )
            
            self.progressUpdated.emit(1.0, "Generant vídeo...")
            self.previewFinished.emit(True, f"file:///{output_path.replace(chr(92), '/')}")

        except InterruptedError:
            self.previewFinished.emit(False, "Operació cancel·lada.")
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
