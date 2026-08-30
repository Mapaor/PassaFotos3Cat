import shutil
import subprocess
import sys
from pathlib import Path


def get_runtime_root() -> Path:
    """Return the application root in development and in a PyInstaller build."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _resolve_first_existing(*candidates: Path) -> Path | None:
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate.resolve()
    return None


def get_ffmpeg_path() -> Path:
    runtime_root = get_runtime_root()
    bundled = runtime_root / "ffmpeg" / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
    fallback = Path(shutil.which("ffmpeg") or "")
    resolved = _resolve_first_existing(bundled, fallback)
    if resolved is not None:
        return resolved
    return bundled


def get_ffprobe_path() -> Path:
    runtime_root = get_runtime_root()
    bundled = runtime_root / "ffmpeg" / ("ffprobe.exe" if sys.platform == "win32" else "ffprobe")
    fallback = Path(shutil.which("ffprobe") or "")
    resolved = _resolve_first_existing(bundled, fallback)
    if resolved is not None:
        return resolved
    return bundled


def check_ffmpeg() -> str:
    """Run FFmpeg and return its version line, or raise a clear error."""
    ffmpeg_path = get_ffmpeg_path()
    ffprobe_path = get_ffprobe_path()

    missing = [path.name for path in (ffmpeg_path, ffprobe_path) if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            f"Missing FFmpeg executable(s): {', '.join(missing)} "
            f"(looked in {ffmpeg_path.parent})"
        )

    result = subprocess.run(
        [str(ffmpeg_path), "-version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        details = result.stderr.strip() or "unknown error"
        raise RuntimeError(f"FFmpeg could not start: {details}")

    first_line = result.stdout.splitlines()[0] if result.stdout else "FFmpeg is available"
    return first_line