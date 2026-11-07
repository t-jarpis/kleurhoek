"""Lijntekening (PNG, zwart op wit) omzetten naar een plaat met gesloten vlakken (ADR 0091).

    python3 trace.py <tekening.png> <uit.svg> [--kier 7] [--nummers <uit.png>]

- Inkt: alles donkerder dan de drempel. Die wordt de inktlaag (`<g class="ink">`, zwarte vorm): precies de lijnen
  van de tekening.
- Vlakken: de witte gebieden tussen de lijnen. Om ze te vinden worden kleine kiertjes in de lijnen eerst gedicht
  (`--kier`, in pixels), zodat een blaadje dat net niet sluit toch een eigen vlak wordt. Elk vlak groeit daarna een
  paar pixels onder de lijn, zodat er na het inkleuren geen witte rand overblijft.
- Te kleine vlakjes (stipjes, glimlichtjes) blijven wit en krijgen geen nummer.
- Vlakken staan van groot naar klein. `--nummers` maakt een plaatje met het volgnummer per vlak, om de kleurcodes
  voor kleur-op-nummer te kiezen.
Nodig: pip install opencv-python-headless numpy (alleen voor de generators).
"""
import argparse

import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("png")
ap.add_argument("svg")
ap.add_argument("--kier", type=int, default=7)
ap.add_argument("--drempel", type=int, default=140)
ap.add_argument("--min", type=float, default=0.00012, help="kleinste vlak, als deel van het hele vel")
ap.add_argument("--nummers")
a = ap.parse_args()

img = cv2.imread(a.png, cv2.IMREAD_GRAYSCALE)
h, w = img.shape
side = max(h, w)
canvas = np.full((side, side), 255, np.uint8)
canvas[(side - h) // 2:(side - h) // 2 + h, (side - w) // 2:(side - w) // 2 + w] = img
img = canvas
s = 200 / side
ink = (img < a.drempel).astype(np.uint8)
ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
closed = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (a.kier, a.kier)))
white = (1 - closed).astype(np.uint8)
n, lab, stats, cent = cv2.connectedComponentsWithStats(white, connectivity=4)


def path(cnts, eps):
    out = []
    for c in cnts:
        c = cv2.approxPolyDP(c, eps, True)
        if len(c) < 3:
            continue
        out.append("M" + " L".join(f"{x * s:.1f} {y * s:.1f}" for x, y in c[:, 0, :]) + "Z")
    return " ".join(out)


# Wat het dichten van kiertjes aan wit heeft afgesnoept, gaat terug naar het vlak ernaast, en alle vlakken lopen
# daarna onder de lijnen door tot ze elkaar raken: geen witte randjes na het inkleuren.
keep = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= side * side * a.min]
lab2 = np.zeros_like(lab, np.int32)
for i in keep:
    lab2[lab == i] = i
paper = ink == 0
for _ in range(a.kier + 6):
    grown = cv2.dilate(lab2.astype(np.float32), np.ones((3, 3), np.uint8)).astype(np.int32)
    fill = (lab2 == 0) & (grown > 0) & (paper | (cv2.dilate(lab2.astype(np.float32), np.ones((3, 3), np.uint8)) > 0))
    lab2[fill & (paper | (_ >= a.kier))] = grown[fill & (paper | (_ >= a.kier))]
regions = []
for i in keep:
    m = (lab2 == i).astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    regions.append((int(stats[i, cv2.CC_STAT_AREA]), path(cnts, 1.5), cent[i]))
regions.sort(key=lambda r: -r[0])
cnts, _ = cv2.findContours(ink, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">'
       + "".join(f'<path class="r" fill-rule="evenodd" d="{d}"/>' for _, d, _ in regions)
       + f'<g class="ink"><path class="dot" fill-rule="evenodd" d="{path(cnts, 1.0)}"/></g></svg>')
open(a.svg, "w").write(svg + "\n")
print(f"{len(regions)} vlakken, {len(svg) // 1024} kB")
if a.nummers:
    out = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for k, (_, _, (cx, cy)) in enumerate(regions):
        cv2.putText(out, str(k), (int(cx) - 8, int(cy) + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.imwrite(a.nummers, out)
