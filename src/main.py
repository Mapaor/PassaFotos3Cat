import sys
import os
from pathlib import Path

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# pyrefly: ignore [missing-import]
from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont, QIcon
# pyrefly: ignore [missing-import]
from PySide6.QtQml import QQmlApplicationEngine

from ffmpeg_runtime import check_ffmpeg
from backend import VideoConverter
from pyinstaller.qml_runtime import add_qml_import_path

QML_MODULE = "MyApp"
QML_ENTRY = "Main"


if __name__ == "__main__":
    try:
        ffmpeg_version = check_ffmpeg()
    except (FileNotFoundError, RuntimeError) as error:
        print(f"FFmpeg setup error: {error}", file=sys.stderr)
        raise SystemExit(1)

    app = QGuiApplication(sys.argv)
    
    if hasattr(sys, "_MEIPASS"):
        app_root = Path(sys._MEIPASS)
        icon_path = str(app_root / "qml" / "MyApp" / "assets" / "appIcon.svg")
    else:
        app_root = PROJECT_ROOT
        icon_path = str(app_root / "src" / "qml" / "MyApp" / "assets" / "appIcon.svg")
        
    app.setWindowIcon(QIcon(icon_path))
    font_path = str(app_root / "fonts" / "Bw3Cat" / "Bw3Cat-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family))
        
    engine = QQmlApplicationEngine()
    add_qml_import_path(engine)
    
    # Expose the VideoConverter to QML
    converter = VideoConverter()
    engine.rootContext().setContextProperty("videoConverter", converter)
    
    engine.rootContext().setContextProperty(
        "ffmpegStatus",
        f"App working, ffmpeg detected: {ffmpeg_version}",
    )
    engine.loadFromModule(QML_MODULE, QML_ENTRY)

    if not engine.rootObjects():
        raise SystemExit(-1)

    sys.exit(app.exec())