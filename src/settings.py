from pathlib import Path

# =====================================
# Projecte
# =====================================

APP_NAME = "Horitzontalitzador3Cat"
APP_VERSION = "1.0.0"

# =====================================
# Directoris
# =====================================

ROOT_DIR = Path(__file__).resolve().parent.parent

SRC_DIR = ROOT_DIR / "src"

ASSETS_DIR = ROOT_DIR / "assets"

ICON_PATH = ASSETS_DIR / "icon.ico"

FFMPEG_DIR = ROOT_DIR / "ffmpeg"

# =====================================
# FFmpeg
# =====================================

OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080

DEFAULT_CRF = 18
FPS = 25

DEFAULT_PHOTO_DURATION = 5.0
DEFAULT_TRANSITION_DURATION = 1.0
DEFAULT_ZOOM_END = 1.15

VIDEO_EXTENSIONS = (
    "*.mp4",
    "*.mov",
    "*.mkv",
    "*.avi",
    "*.webm",
)
IMAGE_EXTENSIONS = (
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.webp",
)

# =====================================
# GUI
# =====================================

WINDOW_WIDTH = 520
WINDOW_HEIGHT = 500

THEME = str(ASSETS_DIR / "themes" / "magenta.json")

APPEARANCE = "System"

FONT_FAMILY = "Bw3Cat"

# =====================================
# Preview
# =====================================

PREVIEW_WIDTH = 480
PREVIEW_HEIGHT = 270

PREVIEW_TEMP_FILE = ROOT_DIR / "preview.jpg"

# =====================================
# Image Editor
# =====================================

EDITOR_WIDTH = 720
EDITOR_HEIGHT = 405  # 16:9 ratio
