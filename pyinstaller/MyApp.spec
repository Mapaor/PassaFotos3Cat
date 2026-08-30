# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

try:
    ROOT = Path(__file__).resolve().parent.parent
except NameError:
    ROOT = Path.cwd().resolve()

ENTRY = ROOT / 'src' / 'main.py'
QML_SOURCE = ROOT / 'src' / 'qml'
FFMPEG_SOURCE = ROOT / 'ffmpeg'
FONTS_SOURCE = ROOT / 'fonts'
HOOK = ROOT / 'pyinstaller' / 'hook-qml.py'

if not ENTRY.exists():
    raise FileNotFoundError(f'Missing application entry point: {ENTRY}')
if not (FFMPEG_SOURCE / 'ffmpeg.exe').exists():
    raise FileNotFoundError(f'Missing FFmpeg executable: {FFMPEG_SOURCE / "ffmpeg.exe"}')

block_cipher = None

a = Analysis(
    [str(ENTRY)],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(QML_SOURCE), 'qml'),
        (str(FFMPEG_SOURCE), 'ffmpeg'),
        (str(FONTS_SOURCE), 'fonts'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(HOOK)],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / 'pyinstaller' / 'appIcon.ico'),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyApp',
)
