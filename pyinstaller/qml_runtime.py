import sys
from pathlib import Path


def add_qml_import_path(engine):
    project_root = Path(__file__).resolve().parent.parent
    qml_root = project_root / "src" / "qml"

    if hasattr(sys, "_MEIPASS"):
        frozen_root = Path(sys._MEIPASS)
        if (frozen_root / "qml").is_dir():
            engine.addImportPath(str(frozen_root / "qml"))
            return

    if qml_root.is_dir():
        engine.addImportPath(str(qml_root))
