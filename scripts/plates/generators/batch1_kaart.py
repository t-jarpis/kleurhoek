import os
import math, random
from kit import *
OUT = os.environ.get("OUT", "concepten/batch1")
SCHAAR = {"slug": "kinderschaar"}

def balloon(sh, x, y, s, code):
    sh.region(f"M{f(x)} {f(y + s*1.2)}C{f(x - s*1.2)} {f(y + s*.4)} {f(x - s)} {f(y - s*1.2)} {f(x)} {f(y - s*1.2)}C{f(x + s)} {f(y - s*1.2)} {f(x + s*1.2)} {f(y + s*.4)} {f(x)} {f(y + s*1.2)}Z", code)
    sh.poly_r([(x, y + s * 1.2), (x - s * .2, y + s * 1.45), (x + s * .2, y + s * 1.45)], code)
    sh.line(f"M{f(x)} {f(y + s*1.45)}Q{f(x + s*.4)} {f(y + s*2.2)} {f(x - s*.1)} {f(y + s*3)}")

def card(slug, name, front, inside_text, cat, age, steps_extra, holiday=None):
    """Kaart: knip het kader uit, vouw op de lijn (bedrukte kant buiten). Onder = voorkant, boven = achterkant (op zijn kop)."""
    sh = Sheet()
    x0, y0, w, h = 14, 12, 172, 250
    sh.rect_line(x0, y0, w, h, "cut", 3)
    mid = y0 + h / 2
    sh.seg(x0, mid, x0 + w, mid, "fold")
    # achterkant (op zijn kop, zodat hij goed leest na het vouwen)
    sh.raw(f'<g transform="rotate(180 100 {f(y0 + h / 4)})">')
    sh.text(100, y0 + h / 4 - 8, inside_text, 7)
    sh.text(100, y0 + h / 4 + 8, "Gemaakt door: ...........................", 7)
    sh.raw('</g>')
    front(sh, x0, mid, w, h / 2)
    sh.legend(["cut", "fold"], 276)
    meta = {"category": cat, "age": age, "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
            "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "stiften", "optional": True}, {"slug": "stevig-papier", "optional": True}],
            "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier (160 gram) als je het hebt; gewoon papier kan ook.", "steps": [
                "Kleur de voorkant (de onderste helft) mooi in.",
                "Knip de kaart uit langs de streepjeslijn.",
                "Vouw hem dubbel op de stippellijn, met de tekening aan de buitenkant. De kaart staat dan rechtop met de vouw bovenaan.",
            ] + steps_extra}}}
    if holiday: meta["holiday"] = holiday
    write(OUT, slug, sh, meta)

def front_balloons(sh, x0, y0, w, h):
    sh.raw(f'<text class="l" style="stroke-width:1.1" x="100" y="{f(y0 + 30)}" font-size="24" text-anchor="middle" font-weight="800">Hoera!</text>')
    for i, (dx, dy, c) in enumerate([(-50, 62, "r"), (-18, 52, "b"), (14, 60, "y"), (46, 50, "g")]):
        balloon(sh, 100 + dx, y0 + dy, 14, c)
    for i, (sx, sy) in enumerate([(30, 50), (170, 44), (26, 96), (174, 100)]):
        sh.poly_r([(sx + (6 if k % 2 == 0 else 2.6) * math.sin(math.pi * k / 5), y0 + sy - (6 if k % 2 == 0 else 2.6) * math.cos(math.pi * k / 5)) for k in range(10)], "y")
card("verjaardagskaart-ballonnen", "Verjaardagskaart met ballonnen", front_balloons, "Fijne verjaardag!", "feest", "4-6",
     ["Schrijf binnenin een lief berichtje."], holiday="verjaardag")

def front_flowers(sh, x0, y0, w, h):
    sh.raw(f'<text class="l" style="stroke-width:1.1" x="100" y="{f(y0 + 28)}" font-size="20" text-anchor="middle" font-weight="800">Dank je wel!</text>')
    for i, (cx, c) in enumerate([(55, "m"), (100, "y"), (145, "p")]):
        stem_top = y0 + 62 + (i % 2) * 10
        sh.line(f"M{cx} {stem_top + 10}V{y0 + h - 8}")
        sh.region(f"M{cx} {y0 + h - 30}Q{cx + 14} {y0 + h - 42} {cx + 18} {y0 + h - 28}Q{cx + 8} {y0 + h - 24} {cx} {y0 + h - 30}Z", "g")
        for k in range(6):
            a = math.radians(k * 60)
            sh.ellipse_r(cx + 9 * math.cos(a), stem_top + 9 * math.sin(a), 6, 6, c)
        sh.circle_r(cx, stem_top, 5, "o")
card("bedankkaart-bloemen", "Bedankkaart met bloemen", front_flowers, "Bedankt voor alles!", "natuur", "4-6",
     ["Schrijf binnenin voor wie de kaart is."])

# ---------- Boekenleggers ----------
def bookmarks(slug, name, patterns, cat, age):
    sh = Sheet()
    title(sh, name, 14)
    for i, pat in enumerate(patterns):
        x, y, w, h = 14 + i * 44, 24, 40, 230
        sh.rect_line(x, y, w, h, "cut", 3)
        sh.circle_line(x + w / 2, y + 10, 3, "cut")
        pat(sh, x, y + 20, w, h - 26)
    sh.legend(["cut"], 274)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw", "optional": True}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Op stevig papier blijven de boekenleggers langer mooi.", "steps": [
            "Kleur de vier boekenleggers in, elk op een eigen manier.",
            "Knip ze uit langs de streepjeslijn.",
            "Prik (met hulp) een gaatje in het rondje bovenaan en knoop er een stukje touw of lint door."]}}})

def pat_stripes(sh, x, y, w, h):
    n = 10; step = h / n
    for k in range(n):
        sh.poly_r([(x, y + k * step), (x + w, y + k * step - 8), (x + w, y + (k + 1) * step - 8), (x, y + (k + 1) * step)] if k else [(x, y), (x + w, y), (x + w, y + step - 8), (x, y + step)], "rbyg"[k % 4])
def pat_dots(sh, x, y, w, h):
    for r in range(9):
        for c in range(2):
            sh.circle_r(x + 10 + c * 20 + (r % 2) * 0, y + 10 + r * 23, 7, "mtpo"[(r + c) % 4])
def pat_hearts(sh, x, y, w, h):
    for r in range(7):
        cx, cy = x + w / 2, y + 14 + r * 30; k = 1.3
        sh.region(f"M{f(cx)} {f(cy + 9*k)}C{f(cx - 13*k)} {f(cy)} {f(cx - 9*k)} {f(cy - 10*k)} {f(cx)} {f(cy - 4*k)}C{f(cx + 9*k)} {f(cy - 10*k)} {f(cx + 13*k)} {f(cy)} {f(cx)} {f(cy + 9*k)}Z", "mk"[r % 2])
def pat_waves(sh, x, y, w, h):
    for k in range(8):
        yy = y + k * 25
        sh.region(f"M{f(x)} {f(yy + 10)}Q{f(x + w/4)} {f(yy)} {f(x + w/2)} {f(yy + 10)}T{f(x + w)} {f(yy + 10)}V{f(yy + 22)}Q{f(x + w*3/4)} {f(yy + 32)} {f(x + w/2)} {f(yy + 22)}T{f(x)} {f(yy + 22)}Z", "btn"[k % 3])
bookmarks("boekenleggers-patronen", "Boekenleggers met patronen", [pat_stripes, pat_dots, pat_hearts, pat_waves], "patronen", "6-9")

# ---------- Cadeaulabels ----------
def tags():
    sh = Sheet()
    title(sh, "Cadeaulabels", 14)
    deco = ["ster", "hart", "bal", "boom", "ster", "hart"]
    for i in range(6):
        col, row = i % 2, i // 2
        x, y = 16 + col * 88, 26 + row * 80
        w, h = 80, 72
        sh.line(f"M{x + 14} {y}H{x + w}V{y + h}H{x}V{y + 14}Z", "cut")
        sh.circle_line(x + 10, y + 10, 2.6, "cut")
        sh.text(x + 22, y + 46, "Voor: ............", 7, "start")
        sh.text(x + 22, y + 60, "Van: ..............", 7, "start")
        cx, cy = x + 52, y + 22
        if deco[i] == "ster": sh.poly_r([(cx + (10 if k % 2 == 0 else 4.4) * math.sin(math.pi * k / 5), cy - (10 if k % 2 == 0 else 4.4) * math.cos(math.pi * k / 5)) for k in range(10)], "y")
        elif deco[i] == "hart": sh.region(f"M{cx} {cy + 9}C{cx - 12} {cy} {cx - 9} {cy - 9} {cx} {cy - 4}C{cx + 9} {cy - 9} {cx + 12} {cy} {cx} {cy + 9}Z", "r")
        elif deco[i] == "bal": sh.circle_r(cx, cy, 9, "b"); sh.line(f"M{cx - 9} {cy}Q{cx} {cy - 6} {cx + 9} {cy}M{cx - 9} {cy}Q{cx} {cy + 6} {cx + 9} {cy}")
        else: sh.poly_r([(cx, cy - 12), (cx + 10, cy + 6), (cx - 10, cy + 6)], "g"); sh.rect_r(cx - 2, cy + 6, 4, 5, "w")
    sh.legend(["cut"], 274)
    write(OUT, "cadeaulabels", sh, {"category": "feest", "age": "6-9", "kind": "kaart", "difficulty": 1, "minutes": 15, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}],
        "i18n": {"nl": {"name": "Cadeaulabels om in te vullen", "steps": [
            "Kleur de plaatjes en schrijf op voor wie het cadeau is en van wie.",
            "Knip de labels uit langs de streepjeslijn.",
            "Prik een gaatje in het rondje en bind het label met touw of lint aan het cadeau."]}}})
tags()

# ---------- Vlaggenslinger ----------
def bunting():
    sh = Sheet()
    title(sh, "Vlaggenslinger", 14)
    pats = ["streep", "stip", "zigzag", "ster"]
    for i in range(4):
        col, row = i % 2, i // 2
        x, y, w = 14 + col * 88, 26 + row * 124, 84
        flap = 14
        sh.line(f"M{x} {y}H{x + w}V{y + flap}L{x + w/2} {y + flap + 100}L{x} {y + flap}Z", "cut")
        sh.seg(x, y + flap, x + w, y + flap, "fold")
        sh.raw(f'<rect class="glue" x="{x + 2}" y="{y + 2}" width="{w - 4}" height="{flap - 4}"/>')
        tri = [(x, y + flap), (x + w, y + flap), (x + w / 2, y + flap + 100)]
        sh.poly_r(tri, "rybg"[i])
        cx, cy = x + w / 2, y + flap + 34
        if pats[i] == "streep":
            for k in range(3): sh.seg(x + 14 + k * 4, y + flap + 14 + k * 18, x + w - 14 - k * 4, y + flap + 14 + k * 18 + 0)
        elif pats[i] == "stip":
            for dx, dy in [(-16, -8), (16, -8), (0, 10), (-6, 30), (8, 30)]: sh.circle_r(cx + dx, cy + dy, 5, "-")
        elif pats[i] == "zigzag":
            sh.line(f"M{x + 12} {y + flap + 20}" + "".join(f"L{x + 12 + (k + 1) * 10} {y + flap + (12 if k % 2 == 0 else 20)}" for k in range(6)))
        else:
            sh.poly_r([(cx + (13 if k % 2 == 0 else 5.5) * math.sin(math.pi * k / 5), cy - (13 if k % 2 == 0 else 5.5) * math.cos(math.pi * k / 5)) for k in range(10)], "-")
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "vlaggenslinger", sh, {"category": "feest", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 25,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "touw"}],
        "i18n": {"nl": {"name": "Vlaggenslinger voor een feestje", "printNote": "Print het vel een paar keer voor een lange slinger.", "steps": [
            "Kleur de vlaggetjes in.", "Knip ze uit langs de streepjeslijn.",
            "Leg een touw langs de stippellijn, smeer lijm op het grijze randje en vouw het over het touw.",
            "Schuif de vlaggetjes een stukje uit elkaar en hang de slinger op."]}}})
bunting()
print("kaarten klaar")
