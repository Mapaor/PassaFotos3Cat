# Pasafotos — Renderitzat FFmpeg

## 1. Objectiu

Generar un vídeo:

* `1920x1080`
* `25 fps`
* H.264 (`libx264`)
* MP4
* Fotografies amb zoom progressiu
* Cada fotografia té un **anchor point** definit per l'usuari
* Transicions `xfade` entre fotografies

L'usuari **no defineix cap moviment X/Y**. Només defineix l'anchor sobre la fotografia ja re-enquadrada.

---

## 2. Flux

```text
Imatge original
      ↓
Re-enquadrament 16:9
      ↓
Zoom + pan automàtic al voltant de l'anchor
      ↓
1920×1080
      ↓
xfade
      ↓
H.264 / MP4
```

La imatge no s'ha de renderitzar prèviament amb Pillow. Python passa els paràmetres a FFmpeg.

---

## 3. Configuració per fotografia

```python
{
    "path": "image.jpg",
    "duration": 5.0,
    "anchor_x": 0.70,
    "anchor_y": 0.35,
    "zoom_start": 1.00,
    "zoom_end": 1.12
}
```

`anchor_x` i `anchor_y` són coordenades normalitzades `0..1` sobre la imatge 16:9.

---

## 4. Normalització 16:9

Fer que la fotografia cobreixi un frame 16:9 mantenint la proporció:

```bash
scale=...:force_original_aspect_ratio=increase,
crop=...
```

La resolució de treball ha de ser suficient per al zoom màxim, però **no cal treballar a 3840×2160 si la sortida és 1920×1080**.

---

## 5. Zoom basat en `progress`

No utilitzar:

```text
pzoom + 0.001
```

Definir:

```text
p = on / (total_frames - 1)
```

amb:

```text
p = 0 → inici
p = 1 → final
```

I:

```text
zoom = zoom_start + (zoom_end - zoom_start) * p
```

Això garanteix que el zoom arriba exactament al valor final al mateix temps que acaba l'animació.

---

## 6. Anchor point

Si:

```text
anchor_x = 0.70
anchor_y = 0.35
```

el zoom es fa al voltant d'aquest punt.

Les coordenades del crop:

```text
x = anchor_x * (iw - iw/zoom)
y = anchor_y * (ih - ih/zoom)
```

Amb:

```text
anchor = (0.5, 0.5)
```

equival a un zoom central:

```text
x = (iw-iw/zoom)/2
y = (ih-ih/zoom)/2
```

---

## 7. Preparació de cada stream

```bash
[0:v]
scale=...,
crop=...,
zoompan=...,
setpts=PTS-STARTPTS
[v0]
```

I igual per `v1`, `v2`, etc.

---

## 8. Transicions

Amb fotografies de `5 s` i transicions de `1 s`:

```bash
[v0][v1]xfade=transition=fade:duration=1:offset=4[x1];
[x1][v2]xfade=transition=fade:duration=1:offset=8[v]
```

Els offsets els ha de calcular Python.

---

## 9. Encoding final

```bash
-map "[v]"
-c:v libx264
-crf 18
-preset medium
-pix_fmt yuv420p
-movflags +faststart
output.mp4
```

---

# 10. Comandament FFmpeg complet d'exemple

Aquest exemple té:

* 3 fotografies
* 5 segons cadascuna
* 25 fps
* zoom `1.00 → 1.12`
* `image1`: anchor `(0.50, 0.50)`
* `image2`: anchor `(0.70, 0.35)`
* `image3`: anchor `(0.25, 0.65)`
* fade d'1 segon
* sortida `1920×1080`

```bash
ffmpeg -y ^
  -loop 1 -t 5 -i image1.png ^
  -loop 1 -t 5 -i image2.png ^
  -loop 1 -t 5 -i image3.png ^
  -filter_complex "
    [0:v]
    scale=1920:1080:force_original_aspect_ratio=increase,
    crop=1920:1080,
    zoompan=
      z='1+(1.12-1)*on/124':
      x='0.50*(iw-iw/zoom)':
      y='0.50*(ih-ih/zoom)':
      d=1:
      s=1920x1080:
      fps=25,
    setpts=PTS-STARTPTS
    [v0];

    [1:v]
    scale=1920:1080:force_original_aspect_ratio=increase,
    crop=1920:1080,
    zoompan=
      z='1+(1.12-1)*on/124':
      x='0.70*(iw-iw/zoom)':
      y='0.35*(ih-ih/zoom)':
      d=1:
      s=1920x1080:
      fps=25,
    setpts=PTS-STARTPTS
    [v1];

    [2:v]
    scale=1920:1080:force_original_aspect_ratio=increase,
    crop=1920:1080,
    zoompan=
      z='1+(1.12-1)*on/124':
      x='0.25*(iw-iw/zoom)':
      y='0.65*(ih-ih/zoom)':
      d=1:
      s=1920x1080:
      fps=25,
    setpts=PTS-STARTPTS
    [v2];

    [v0][v1]
    xfade=transition=fade:duration=1:offset=4
    [x1];

    [x1][v2]
    xfade=transition=fade:duration=1:offset=8,
    format=yuv420p
    [v]
  " ^
  -map "[v]" ^
  -c:v libx264 ^
  -crf 18 ^
  -preset medium ^
  -pix_fmt yuv420p ^
  -movflags +faststart ^
  output.mp4
```

> **Nota:** aquest exemple assumeix Windows/CMD (`^` per continuar línies). En PowerShell caldria adaptar la continuació de línia.

---

## 11. Responsabilitats

### Qt / Python

* Mostrar el preview 16:9.
* Permetre seleccionar l'anchor.
* Guardar `anchor_x`, `anchor_y`.
* Guardar zoom, duració i transició.
* Calcular `total_frames`, `progress` i `xfade offsets`.
* Generar el comandament/filter de FFmpeg.

### FFmpeg

* Llegir les imatges originals.
* Fer `scale`/`crop`.
* Aplicar zoom.
* Calcular el pan necessari per mantenir el zoom centrat en l'anchor.
* Fer les transicions.
* Codificar el vídeo final.

**Principi clau:** Python defineix *què* vol l'usuari; FFmpeg calcula/renderitza *com* obtenir cada frame.
