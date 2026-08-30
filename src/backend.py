import os
import subprocess
import threading
import json
import tempfile
from urllib.parse import unquote
# pyrefly: ignore [missing-import]
from PySide6.QtCore import QObject, Slot, Signal

from ffmpeg_runtime import get_ffmpeg_path
from utils import get_output_path
from command_builder import build_ffmpeg_slideshow_command

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
    progressUpdated = Signal(float)

    @Slot(str, str, str, float, float, float)
    def convert_slideshow(
        self,
        images_json: str,
        output_dir: str,
        output_name: str,
        photo_duration: float,
        transition_duration: float,
        zoom_end: float
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
                photo_duration, transition_duration, zoom_end
            ),
            daemon=True
        ).start()

    def _convert_thread(
        self,
        images_data, output_dir, output_name,
        photo_duration, transition_duration, zoom_end
    ):
        try:
            # The first image gives the base output path if needed, but we can just use the first image's path as base
            base_path = images_data[0]["path"]
            output_path = get_output_path(base_path, output_dir, output_name)
            
            # Calculate total duration for progress bar
            num_images = len(images_data)
            if num_images == 1:
                total_duration = photo_duration
            else:
                total_duration = (num_images * photo_duration) + ((num_images - 1) * transition_duration)

            cmd = build_ffmpeg_slideshow_command(
                get_ffmpeg_path(),
                images_data,
                output_path,
                photo_duration,
                transition_duration,
                zoom_end
            )

            # Inject progress flags before the output path (last element)
            output = cmd.pop()
            cmd.extend(["-progress", "pipe:1", "-nostats"])
            cmd.append(output)

            # We use creationflags=subprocess.CREATE_NO_WINDOW on windows so terminal doesn't pop up
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stderr_lines = []
            def read_stderr(pipe):
                for l in pipe:
                    line = l.strip()
                    stderr_lines.append(line)
                    print(f"[FFMPEG] {line}")
                    
            stderr_thread = threading.Thread(target=read_stderr, args=(process.stderr,), daemon=True)
            stderr_thread.start()

            for line in process.stdout:
                line = line.strip()
                if line.startswith("out_time_us="):
                    try:
                        out_time_us = int(line.split("=", 1)[1])
                        if total_duration > 0:
                            percent = min(out_time_us / (total_duration * 1_000_000), 1.0)
                            self.progressUpdated.emit(percent)
                    except ValueError:
                        pass
                elif line == "progress=end":
                    self.progressUpdated.emit(1.0)

            process.wait()
            stderr_thread.join()

            if process.returncode != 0:
                error_msg = "\\n".join(stderr_lines[-5:]) if stderr_lines else "Error desconegut."
                raise RuntimeError(f"FFmpeg ha retornat un error:\\n{error_msg}")

            self.conversionFinished.emit(True, f"Vídeo desat a: {output_path}")

        except Exception as e:
            self.conversionFinished.emit(False, str(e))

    @Slot(str, float, float, float)
    def preview_slideshow(
        self,
        images_json: str,
        photo_duration: float,
        transition_duration: float,
        zoom_end: float
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
                images_data, photo_duration, transition_duration, zoom_end
            ),
            daemon=True
        ).start()

    def _preview_thread(
        self,
        images_data, photo_duration, transition_duration, zoom_end
    ):
        try:
            output_path = os.path.join(tempfile.gettempdir(), "passafotos_preview.mp4")
            
            # Calculate total duration for progress bar
            num_images = len(images_data)
            if num_images == 1:
                total_duration = photo_duration
            else:
                total_duration = (num_images * photo_duration) + ((num_images - 1) * transition_duration)

            cmd = build_ffmpeg_slideshow_command(
                get_ffmpeg_path(),
                images_data,
                output_path,
                photo_duration,
                transition_duration,
                zoom_end,
                preview=True
            )

            output = cmd.pop()
            cmd.extend(["-progress", "pipe:1", "-nostats"])
            cmd.append(output)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stderr_lines = []
            def read_stderr(pipe):
                for l in pipe:
                    line = l.strip()
                    stderr_lines.append(line)
                    print(f"[FFMPEG PREVIEW] {line}")
                    
            stderr_thread = threading.Thread(target=read_stderr, args=(process.stderr,), daemon=True)
            stderr_thread.start()

            for line in process.stdout:
                line = line.strip()
                if line.startswith("out_time_us="):
                    try:
                        out_time_us = int(line.split("=", 1)[1])
                        if total_duration > 0:
                            percent = min(out_time_us / (total_duration * 1_000_000), 1.0)
                            self.progressUpdated.emit(percent)
                    except ValueError:
                        pass
                elif line == "progress=end":
                    self.progressUpdated.emit(1.0)

            process.wait()
            stderr_thread.join()

            if process.returncode != 0:
                error_msg = "\\n".join(stderr_lines[-5:]) if stderr_lines else "Error desconegut."
                raise RuntimeError(f"FFmpeg preview ha retornat un error:\\n{error_msg}")

            self.previewFinished.emit(True, f"file:///{output_path.replace(chr(92), '/')}")

        except Exception as e:
            self.previewFinished.emit(False, str(e))


