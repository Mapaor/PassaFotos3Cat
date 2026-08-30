import os
import sys

if hasattr(sys, "_MEIPASS"):
    qml_root = os.path.join(sys._MEIPASS, "qml")
    if os.path.isdir(os.path.join(qml_root, "MyApp")):
        current = os.environ.get("QML2_IMPORT_PATH", "")
        paths = [p for p in (current.split(os.pathsep) if current else []) if p]
        if qml_root not in paths:
            paths.insert(0, qml_root)
        os.environ["QML2_IMPORT_PATH"] = os.pathsep.join(paths)
