"""Batch 19: zoek de verschillen (twee tekeningen, vijf verschillen, met antwoordblad)."""
import math
from lib_gen import *
from shapes import heart_path, star_path, cloud_path, fish_path, leaf_path

def verschillen(slug, name, draw, diffs, age, diff, cat):
    """draw(sh, ox, oy, changed:set) tekent de scène (200x105) met offset; diffs: [(id, x, y, r)] voor het antwoordblad."""
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else cap(name.split(": ", 1)[-1]), 16)
        sh.text(100, 27, f"Zoek de {len(diffs)} verschillen en zet er een rondje om.", 6.5)
        sh.rect_line(4, 34, 192, 108, "l", 4, "stroke-width:.8"); sh.rect_line(4, 150, 192, 108, "l", 4, "stroke-width:.8")
        draw(sh, 4, 34, set()); draw(sh, 4, 150, {d[0] for d in diffs})
        if ans:
            for _, x, y, r in diffs: sh.circle_line(4 + x, 150 + y, r, "l", "stroke-width:1.6;stroke-dasharray:3 2")
        sh.text(100, 270, "Gevonden: " + "  ".join("○" for _ in diffs), 8)
        return sh
    write(OUT, slug, page(False), {"category": cat, "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 10 + diff * 5,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": name, "steps": [
            "Vergelijk de twee tekeningen stukje voor stukje, bijvoorbeeld van links naar rechts.",
            "Zie je iets wat anders is? Zet een rondje om het verschil in de onderste tekening en kleur een rondje onderaan.",
            f"Vind je ze alle {len(diffs)}? Kijk na met het antwoordblad en kleur daarna de tekeningen in."]}}},
        [("antwoorden", "Antwoorden", page(True))])

def tuin(sh, ox, oy, ch):
    T = lambda x, y: (ox + x, oy + y)
    sh.region(f"M{ox} {oy + 105}V{oy + 84}Q{ox + 100} {oy + 76} {ox + 192} {oy + 84}V{oy + 105}Z", "l")
    # huis
    x, y = T(20, 40); sh.rect_r(x, y, 56, 46, "y"); sh.poly_r([(x - 6, y), (x + 28, y - 26), (x + 62, y)], "r")
    sh.rect_r(x + 22, y + 22, 14, 24, "w")
    sh.rect_r(x + 6, y + 8, 12, 10, "b")
    if "raam" not in ch: sh.rect_r(x + 40, y + 8, 12, 10, "b")
    if "schoorsteen" not in ch: sh.rect_r(x + 42, y - 22, 7, 12, "r")
    # boom
    x, y = T(130, 30); sh.rect_r(x - 4, y + 22, 8, 34, "w"); sh.circle_r(x, y + 10, 20, "g")
    if "appel" in ch: sh.circle_r(x + 8, y + 14, 3.5, "r")
    sh.circle_r(x - 9, y + 6, 3.5, "r")
    # zon en wolk
    x, y = T(176, 14); sh.circle_r(x, y, 9, "y")
    rays = 8 if "stralen" not in ch else 6
    for k in range(rays): a = math.radians(k * 360 / rays); sh.seg(x + 11 * math.cos(a), y + 11 * math.sin(a), x + 15 * math.cos(a), y + 15 * math.sin(a))
    sh.region(cloud_path(ox + 96, oy + 18, 9), "-")
    # bloemen
    for i, bx in enumerate((92, 104, 116, 160, 174)):
        if "bloem" in ch and i == 1: continue
        x, y = T(bx, 92); sh.line(f"M{x} {y}V{y - 10}")
        for k in range(5): a = math.radians(k * 72); sh.circle_r(x + 3 * math.cos(a), y - 12 + 3 * math.sin(a), 2.4, "m")
verschillen("zoek-de-verschillen-tuin", "Zoek de verschillen: huis en tuin", tuin,
            [("raam", 66, 54, 10), ("schoorsteen", 66, 20, 10), ("appel", 138, 44, 8), ("stralen", 176, 14, 18), ("bloem", 104, 82, 9)], "4-6", 1, "thuis")

def zee(sh, ox, oy, ch):
    sh.rect_r(ox, oy, 192, 108, "b")
    sh.region(f"M{ox} {oy + 108}V{oy + 92}Q{ox + 50} {oy + 86} {ox + 100} {oy + 92}T{ox + 192} {oy + 90}V{oy + 108}Z", "y")
    for i, (x, y, c) in enumerate(((40, 30, "o"), (120, 22, "y"), (90, 60, "r"), (150, 56, "g"))):
        if "vis" in ch and i == 3: continue
        flip = "vin" in ch and i == 0
        sh.region(fish_path(ox + x, oy + y, 9) if not flip else fish_path(ox + x, oy + y, 9), c)
        sh.dot(ox + x - 5, oy + y - 1, 1)
    for i, x in enumerate((20, 34, 170)):
        h = 30 if not ("plant" in ch and i == 1) else 18
        sh.region(f"M{ox + x} {oy + 94}C{ox + x - 8} {oy + 94 - h * .6} {ox + x + 8} {oy + 94 - h * .8} {ox + x} {oy + 94 - h}C{ox + x + 10} {oy + 94 - h * .7} {ox + x + 4} {oy + 94 - h * .3} {ox + x + 6} {oy + 94}Z", "g")
    sh.region(star_path(ox + 110, oy + 96, 9, 4), "o")
    if "schelp" not in ch: sh.region(f"M{ox + 140} {oy + 100}L{ox + 132} {oy + 92}A10 10 0 0 1 {ox + 148} {oy + 92}Z", "k")
    for i, (x, y, r) in enumerate(((60, 14, 3), (64, 6, 2), (100, 40, 2.5))):
        if "bel" in ch and i == 2: continue
        sh.circle_r(ox + x, oy + y, r, "-")
    if "krab" in ch:
        sh.ellipse_r(ox + 70, oy + 98, 7, 5, "r"); sh.dot(ox + 67, oy + 95, .9); sh.dot(ox + 73, oy + 95, .9)
verschillen("zoek-de-verschillen-onder-water", "Zoek de verschillen: onder water", zee,
            [("vis", 150, 56, 12), ("plant", 34, 74, 14), ("schelp", 140, 94, 10), ("bel", 100, 40, 7), ("krab", 70, 98, 9)], "6-9", 2, "zee")

def ruimte(sh, ox, oy, ch):
    sh.rect_r(ox, oy, 192, 108, "n")
    stars = [(20, 20), (60, 12), (150, 16), (180, 50), (30, 80), (110, 90), (170, 96), (84, 40)]
    for i, (x, y) in enumerate(stars):
        if "ster" in ch and i == 4: continue
        sh.region(star_path(ox + x, oy + y, 5, 2.2), "y")
    sh.circle_r(ox + 150, oy + 70, 18, "p" if True else "o")
    if "ring" not in ch: sh.region(f"M{ox + 126} {oy + 74}Q{ox + 150} {oy + 60} {ox + 174} {oy + 66}Q{ox + 152} {oy + 82} {ox + 126} {oy + 74}Z", "o")
    cx, cy = ox + 70, oy + 64
    sh.region(f"M{cx - 9} {cy + 26}V{cy - 6}Q{cx} {cy - 30} {cx + 9} {cy - 6}V{cy + 26}Z", "r")
    if "raam" not in ch: sh.circle_r(cx, cy, 5, "b")
    fin = 14 if "vin" not in ch else 8
    sh.poly_r([(cx - 9, cy + 12), (cx - 9 - fin * .7, cy + 28), (cx - 9, cy + 26)], "o"); sh.poly_r([(cx + 9, cy + 12), (cx + 9 + fin * .7, cy + 28), (cx + 9, cy + 26)], "o")
    sh.region(f"M{cx - 6} {cy + 26}Q{cx} {cy + 40} {cx + 6} {cy + 26}Z", "y")
    sh.circle_r(ox + 30, oy + 44, 10, "z")
    if "krater" not in ch: sh.circle_r(ox + 27, oy + 41, 2.5, "-")
    if "ufo" in ch: sh.ellipse_r(ox + 120, oy + 30, 10, 4, "l"); sh.region(f"M{ox + 114} {oy + 28}A6 6 0 0 1 {ox + 126} {oy + 28}Z", "b")
verschillen("zoek-de-verschillen-ruimte", "Zoek de verschillen: in de ruimte", ruimte,
            [("ster", 30, 80, 8), ("ring", 150, 70, 22), ("raam", 70, 64, 8), ("krater", 27, 41, 7), ("ufo", 120, 30, 13)], "6-9", 2, "ruimte")
