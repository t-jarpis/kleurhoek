"""Gedeelde vormen (paden) en het sjabloonvel."""
import os, math
from kit import *
OUT = os.environ.get("OUT", "concepten")

def heart_path(cx, cy, s):
    k = s / 10
    return f"M{f(cx)} {f(cy + 9*k)}C{f(cx - 13*k)} {f(cy)} {f(cx - 9*k)} {f(cy - 10*k)} {f(cx)} {f(cy - 4*k)}C{f(cx + 9*k)} {f(cy - 10*k)} {f(cx + 13*k)} {f(cy)} {f(cx)} {f(cy + 9*k)}Z"
def star_path(cx, cy, r1, r2, n=5):
    p = [(cx + (r1 if i % 2 == 0 else r2) * math.sin(math.pi * i / n), cy - (r1 if i % 2 == 0 else r2) * math.cos(math.pi * i / n)) for i in range(2 * n)]
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in p) + "Z"
def moon_path(cx, cy, r):
    x = cx + r * .3; dy = r * math.sqrt(1 - .09)
    return f"M{f(x)} {f(cy - dy)}A{f(r)} {f(r)} 0 1 0 {f(x)} {f(cy + dy)}A{f(r*.8)} {f(r*.8)} 0 0 1 {f(x)} {f(cy - dy)}Z"
def drop_path(cx, cy, s):
    return f"M{f(cx)} {f(cy - s*1.3)}C{f(cx + s*.4)} {f(cy - s*.5)} {f(cx + s)} {f(cy)} {f(cx + s)} {f(cy + s*.4)}A{f(s)} {f(s)} 0 0 1 {f(cx - s)} {f(cy + s*.4)}C{f(cx - s)} {f(cy)} {f(cx - s*.4)} {f(cy - s*.5)} {f(cx)} {f(cy - s*1.3)}Z"
def cloud_path(cx, cy, s):
    return f"M{f(cx - s*1.4)} {f(cy + s*.5)}A{f(s*.5)} {f(s*.5)} 0 0 1 {f(cx - s)} {f(cy - s*.3)}A{f(s*.7)} {f(s*.7)} 0 0 1 {f(cx)} {f(cy - s*.7)}A{f(s*.6)} {f(s*.6)} 0 0 1 {f(cx + s)} {f(cy - s*.2)}A{f(s*.5)} {f(s*.5)} 0 0 1 {f(cx + s*1.4)} {f(cy + s*.5)}Z"
def leaf_path(cx, cy, w, h, rot=0):
    return f"M{f(cx)} {f(cy - h)}C{f(cx + w)} {f(cy - h*.4)} {f(cx + w*.8)} {f(cy + h*.6)} {f(cx)} {f(cy + h)}C{f(cx - w*.8)} {f(cy + h*.6)} {f(cx - w)} {f(cy - h*.4)} {f(cx)} {f(cy - h)}Z"
def fish_path(cx, cy, s):
    k = s / 10
    return f"M{f(cx - 10*k)} {f(cy)}C{f(cx - 4*k)} {f(cy - 8*k)} {f(cx + 6*k)} {f(cy - 8*k)} {f(cx + 9*k)} {f(cy - 1*k)}L{f(cx + 15*k)} {f(cy - 7*k)}V{f(cy + 7*k)}L{f(cx + 9*k)} {f(cy + 1*k)}C{f(cx + 6*k)} {f(cy + 8*k)} {f(cx - 4*k)} {f(cy + 8*k)} {f(cx - 10*k)} {f(cy)}Z"

def stencil(slug, name, shapes, cat, age):
    sh = Sheet()
    title(sh, name.split(": ", 1)[-1][0].upper() + name.split(": ", 1)[-1][1:], 16)
    sh.text(100, 26, "Knip elk kaartje uit en snijd de vorm uit het midden.", 6)
    for i, d in enumerate(shapes):
        col, row = i % 2, i // 2
        bx, by = 14 + col * 88, 34 + row * 76
        sh.rect_line(bx, by, 84, 70, "cut", 4)
        sh.line(d(bx + 42, by + 36), "cut")
        sh.raw(f'<path class="l" d="{d(bx + 42, by + 36)}" style="stroke-width:.6;opacity:.35" fill="none"/>')
    sh.legend(["cut"])
    write(OUT, slug, sh, {
        "category": cat, "age": age, "kind": "sjabloon", "difficulty": 2, "minutes": 20, "adultHelp": True, "paperGsm": 160,
        "materials": [{"slug": "stevig-papier"}, {"slug": "kinderschaar"}, {"slug": "potlood"}, {"slug": "verf", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier (160 gram) of plak het vel op karton: dan gaat het sjabloon langer mee.", "steps": [
            "Knip de kaartjes los langs de buitenste streepjeslijn.",
            "Vouw een kaartje voorzichtig dubbel door het midden van de vorm en knip de vorm eruit; een volwassene kan ook een hobbymesje gebruiken.",
            "Leg het sjabloon op een vel papier en trek met potlood langs de binnenrand, of dep er verf in met een sponsje.",
            "Til het sjabloon recht omhoog op, schuif het een stukje op en maak een patroon."]}},
    })
