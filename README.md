# PassaFotos

Una app feta amb PySide6 (Python i Qt6) que desplega una UI moderna per utilitzar ffmpeg internament amb l'objectiu d'agafar imatges com a input i generar un passa-fotos o Kern Burns effect, és a dir un vídeo on es va fent un subtil zoom a cada imatge i es canvia d'imatge a imatge per fosa.

<img width="959" height="539" alt="pf-0" src="https://github.com/user-attachments/assets/f88687d0-998f-406d-8c28-07cd54724202" />

<details><summary>Més captures</summary>

<img width="494" height="241" alt="pf-2" src="https://github.com/user-attachments/assets/e2d78493-2dc2-411f-8c4b-a6316ce96ec0" />

<img width="959" height="503" alt="pf-3" src="https://github.com/user-attachments/assets/61029b52-df1d-40c6-947e-17f9241e7f87" />


</details>

## Estructura

- `src/main.py` — Des d'on s'executa la app
- `src/qml/` — Mòduls i components QML
- `pyinstaller/` — Fitxers de configuració relacionats amb PyInstaller i runtime helpers per aconseguir generar l'executable
- `requirements.txt` — Dependències Python que cal instal·lar
- `fonts/` hi ha la tipografia utilitzada (en aquest cas la de 3Cat)
- `ffmpeg/` hi ha els binaris ffmpeg.exe i ffprobe.exe

Important mantenir en el gitignore les carpetes `build/` i `dist/` i l'entorn virtual de python `.venv/`.

## Requisits
Un IDE (per exemple VSCode), python 3.10 o superior i pip. 

Tenir PowerShell a la terminal serà útil per assegurar que funcionen els següents comandaments.

També recomanaria les extensions del VsCode "QT Core", "QT QML" i "QT Python".

## Preparació

A una terminal fer:
```powershell
python -m venv .venv
```
```powershell
.\.venv\Scripts\Activate.ps1
```
```powershell
python -m pip install --upgrade pip
```
```powershell
pip install -r requirements.txt
```

I també seleccionar l'entorn virtual com a Python Interpeter en el IDE que sigui que utilitzes. En el VSCode: Ctrl+Shift+P > Python: Select Interpreter: venv.

A dins de `.vscode/settings.json` i `.vscode/launch.json` hi ha una configuració per permetre executar la app clicant el botó "Run" que apareix a dalt a la dreta d'el fitxer python `main.py`.

## Desenvolupament
Desenvolupa l'aplicació al teu gust, simplement anar fent  canvis i executant `main.py` per veure'ls.

Nota: L'activació de l'entorn virtual l'hauràs de fer cada vegada que obris l'IDE (`.\.venv\Scripts\Activate.ps1`).

## Generar l'executable

El primer cop fer-ho tot afegint pyinstaller:
```powershell
python -m PyInstaller .\pyinstaller\MyApp.spec --noconfirm
```

Després quan vulguem tornar a generar l'executable podem fer simplement...
```powershell
pyinstaller .\pyinstaller\MyApp.spec --noconfirm
```

El `.exe` es generarà dins de la carpeta `dist/`, es dirà `MyApp.exe` però li pots canviar el nom sense problemes.

## Llicència

[MIT](/LICENSE)

El codi de la aplicació PySide6 té llicència MIT (permissiva), els binaris de ffmpeg tenen una llicència també permisiva (LGPL 2.1), la font BW3Cat té la seva respectiva llicència propietària.
