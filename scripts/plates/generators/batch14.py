"""Batch 14: klokkijken, spiegeltekenen en pixelkunst op nummer."""
import math, random
from lib_gen import *

def clock(sh, cx, cy, r, h=None, m=None, nums=True):
    sh.circle_r(cx, cy, r, "-")
    for i in range(60):
        a = math.radians(i * 6); L = 3 if i % 5 == 0 else 1.4
        sh.seg(cx + (r - L) * math.sin(a), cy - (r - L) * math.cos(a), cx + r * math.sin(a), cy - r * math.cos(a), "l", "stroke-width:%s" % (1 if i % 5 == 0 else .5))
    if nums:
        for i in range(12):
            a = math.radians(i * 30); sh.text(cx + (r - 8) * math.sin(a), cy - (r - 8) * math.cos(a) + 2.2, str(12 if i == 0 else i), 6)
    if h is not None:
        ha = math.radians((h % 12) * 30 + m * .5); ma = math.radians(m * 6)
        sh.seg(cx, cy, cx + r * .5 * math.sin(ha), cy - r * .5 * math.cos(ha), "l", "stroke-width:2.6")
        sh.seg(cx, cy, cx + r * .8 * math.sin(ma), cy - r * .8 * math.cos(ma), "l", "stroke-width:1.5")
    sh.dot(cx, cy, 1.8)
def tijd5(h, m):
    nxt = h % 12 + 1
    return {0: f"{h} uur", 5: f"5 over {h}", 10: f"10 over {h}", 15: f"kwart over {h}", 20: f"10 voor half {nxt}", 25: f"5 voor half {nxt}",
            30: f"half {nxt}", 35: f"5 over half {nxt}", 40: f"10 over half {nxt}", 45: f"kwart voor {nxt}", 50: f"10 voor {nxt}", 55: f"5 voor {nxt}"}[m]

def vijf_minuten():
    times = [(3, 5), (7, 20), (10, 35), (1, 50), (6, 25), (11, 40), (4, 10), (8, 55), (2, 45)]
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Klokkijken per 5 minuten", 16)
        sh.text(100, 27, "Hoe laat is het? Schrijf het onder de klok.", 6.5)
        for i, (h, m) in enumerate(times):
            cx, cy = 38 + (i % 3) * 62, 62 + (i // 3) * 74
            clock(sh, cx, cy, 24, h, m)
            sh.seg(cx - 26, cy + 38, cx + 26, cy + 38, "guide")
            if ans: sh.text(cx, cy + 36, tijd5(h, m), 6)
        return sh
    write(OUT, "klokkijken-per-5-minuten", page(False), {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 3, "minutes": 15, "materials": POTLOOD,
        "i18n": {"nl": {"name": "Klokkijken: per 5 minuten", "steps": [
            "De kleine wijzer wijst het uur aan, de grote wijzer de minuten. Elk streepje met een cijfer is 5 minuten.",
            "Staat de grote wijzer rechts van de 12? Dan zeg je 'over' of 'voor half'. Links? Dan 'over half' of 'voor'.",
            "Bijvoorbeeld: grote wijzer op de 4 is 20 minuten over, dat zeg je als 10 voor half.",
            "Schrijf de tijd op het lijntje en kijk na met het antwoordblad."]}}}, [("antwoorden", "Antwoorden", page(True))])
vijf_minuten()

def digitaal():
    times = [(2, 30), (9, 15), (5, 0), (11, 45), (7, 30), (4, 15)]
    r = random.Random(3); order = list(range(6)); r.shuffle(order)
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Klok en digitale klok", 16)
        sh.text(100, 27, "Trek een lijn van elke klok naar de digitale tijd die erbij hoort.", 6.5)
        for i, (h, m) in enumerate(times):
            cy = 50 + i * 36
            clock(sh, 44, cy, 15, h, m, nums=False); sh.dot(66, cy, 2.2)
            j = order.index(i); y2 = 50 + j * 36
            if ans: sh.seg(66, cy, 128, y2, "l", "stroke-width:1.2")
        for j, i in enumerate(order):
            h, m = times[i]; y = 50 + j * 36
            sh.dot(128, y, 2.2); sh.rect_line(136, y - 9, 46, 18, "l", 3)
            sh.text(159, y + 4, f"{h}:{m:02d}", 11)
        return sh
    write(OUT, "klokkijken-digitaal-koppelen", page(False), {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 2, "minutes": 10, "materials": POTLOOD,
        "i18n": {"nl": {"name": "Klokkijken: wijzerklok en digitale klok koppelen", "steps": [
            "Kijk naar de kleine wijzer: welk uur is het?",
            "Kijk naar de grote wijzer: op de 12 is :00, op de 3 is :15, op de 6 is :30 en op de 9 is :45.",
            "Zoek de digitale tijd die erbij past en trek een lijn. Kijk na met het antwoordblad."]}}}, [("antwoorden", "Antwoorden", page(True))])
digitaal()

def vierentwintig():
    items = [("13:00", "1 uur 's middags"), ("15:30", "half 4 's middags"), ("18:00", "6 uur 's avonds"), ("20:15", "kwart over 8 's avonds"), ("07:45", "kwart voor 8 's ochtends"), ("22:30", "half 11 's avonds"),
             ("12:00", "12 uur 's middags"), ("16:45", "kwart voor 5 's middags"), ("09:15", "kwart over 9 's ochtends"), ("23:00", "11 uur 's avonds")]
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Tijd in 24 uur", 16)
        sh.text(100, 27, "Schrijf op hoe je de tijd zegt, met ochtend, middag of avond.", 6)
        for i, (d, s) in enumerate(items):
            y = 50 + i * 21
            sh.rect_line(16, y - 9, 34, 15, "l", 3); sh.text(33, y + 2, d, 9)
            sh.text(56, y + 2, "=", 9)
            sh.seg(64, y + 3, 186, y + 3, "guide")
            if ans: sh.text(66, y + 1, s, 7.5, "start")
        sh.text(100, 268, "Tip: na 12 uur 's middags haal je er 12 vanaf. 15:00 is 3 uur.", 6)
        return sh
    write(OUT, "klokkijken-24-uursklok", page(False), {"category": "leren", "age": "9+", "kind": "werkblad", "difficulty": 2, "minutes": 10, "materials": POTLOOD,
        "i18n": {"nl": {"name": "Klokkijken: de 24-uursklok", "steps": [
            "Op een digitale klok gaan de uren door tot 23. Na 12 uur 's middags tel je verder: 13, 14, 15 …",
            "Haal er 12 vanaf om te weten hoe je het zegt: 15:30 is half 4 's middags.",
            "Schrijf bij elke tijd hoe je hem zegt en kijk na met het antwoordblad."]}}}, [("antwoorden", "Antwoorden", page(True))])
vierentwintig()

# ---------- spiegeltekenen ----------
def spiegel(slug, name, half, cat, age, diff):
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16)
    sh.text(100, 27, "Teken de andere helft precies gespiegeld. Tel de hokjes!", 6.5)
    n = 12; s = 13; x0 = 100 - n / 2 * s; y0 = 38
    def grid(p):
        for i in range(n + 1):
            p.seg(x0 + i * s, y0, x0 + i * s, y0 + n * s, "guide"); p.seg(x0, y0 + i * s, x0 + n * s, y0 + i * s, "guide")
    grid(sh); sh.seg(100, y0 - 4, 100, y0 + n * s + 4, "l", "stroke-width:1.4;stroke-dasharray:4 3")
    P = lambda poly, mir=False: "M" + " L".join(f"{f(x0 + ((n - gx) if mir else gx) * s)} {f(y0 + gy * s)}" for gx, gy in poly)
    for poly in half: sh.line(P(poly), "l", "stroke-width:2")
    ans = Sheet(); title(ans, "Zo ziet hij er heel uit", 16); grid(ans)
    for poly in half: ans.line(P(poly), "l", "stroke-width:2"); ans.line(P(poly, True), "l", "stroke-width:2")
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "tekenles", "difficulty": diff, "minutes": 15, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            "De stippellijn in het midden is een spiegel.",
            "Kijk naar een hoekpunt links en tel hoeveel hokjes het van de spiegel af ligt. Zet rechts een stipje even ver van de spiegel.",
            "Verbind de stipjes. Klaar? Kleur de tekening in en kijk op het antwoordblad."]}}}, [("antwoorden", "Zo ziet hij er heel uit", ans)])
spiegel("spiegeltekenen-uil", "Spiegeltekenen: uil", [[(6, 2), (4, 2), (2, 1), (2, 4), (1, 6), (2, 9), (4, 11), (6, 11)], [(6, 4), (5, 3), (3, 3), (3, 5), (5, 5), (6, 4)], [(6, 6), (5, 6), (6, 7)], [(3, 7), (4, 9), (5, 8)]], "dieren", "6-9", 2)
# spiegel("spiegeltekenen-bloem", "Spiegeltekenen: bloem", [[(6, 1), (4, 1), (3, 3), (4, 5), (6, 5)], [(4, 3), (2, 2), (1, 4), (2, 5), (4, 4)], [(6, 5), (6, 11)], [(6, 8), (4, 7), (2, 7), (3, 9), (6, 9)], [(1, 11), (6, 11)]], "natuur", "6-9", 2)
spiegel("spiegeltekenen-kerstboom", "Spiegeltekenen: kerstboom", [[(6, 1), (4, 4), (5, 4), (3, 7), (4, 7), (1, 10), (5, 10), (5, 12), (6, 12)], [(6, 0), (5, 1), (6, 2)], [(4, 6), (4, 6.01)], [(3, 9), (3, 9.01)]], "feest", "6-9", 1)

# ---------- pixelkunst op nummer ----------
import json, os
HEX = {c["code"]: c["hex"] for c in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../packages/catalog-data/colors.json")))}
NAMES = {"r": "rood", "o": "oranje", "y": "geel", "l": "lichtgroen", "g": "groen", "b": "lichtblauw", "n": "blauw", "p": "paars", "m": "roze", "k": "lichtroze", "w": "bruin", "z": "grijs", "x": "zwart"}
def pixel(slug, name, rows, age, diff, cat):
    n_r, n_c = len(rows), len(rows[0])
    assert all(len(r) == n_c for r in rows), (slug, [len(r) for r in rows])
    codes = sorted({c for row in rows for c in row if c != "."}, key=lambda c: "rolygbnpmkwzx".index(c))
    num = {c: i + 1 for i, c in enumerate(codes)}
    s = min(160 / n_c, 170 / n_r); x0 = (200 - n_c * s) / 2; y0 = 42
    def page(ans):
        sh = Sheet(); title(sh, "Zo wordt het" if ans else cap(name.split(": ", 1)[-1]), 16)
        if not ans: sh.text(100, 30, "Kleur elk vakje in de kleur van het cijfer. Lege vakjes blijven wit.", 6)
        for r_, row in enumerate(rows):
            for c_, ch in enumerate(row):
                x, y = x0 + c_ * s, y0 + r_ * s
                if ans and ch != ".": sh.raw(f'<rect x="{f(x)}" y="{f(y)}" width="{f(s)}" height="{f(s)}" style="fill:{HEX[ch]};stroke:#222;stroke-width:.4"/>')
                else: sh.rect_line(x, y, s, s, "l", 0, "stroke-width:.4")
                if ch != "." and not ans: sh.text(x + s / 2, y + s * .7, str(num[ch]), max(4.6, s * .55))
        ly = y0 + n_r * s + 12
        for i, c in enumerate(codes):
            x = 20 + (i % 3) * 60; y = ly + (i // 3) * 12
            sh.text(x, y, f"{num[c]} = {NAMES[c]}", 7, "start")
        return sh
    p1 = page(False)
    write(OUT, slug, p1, {"category": cat, "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 15 + diff * 5,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}],
        "i18n": {"nl": {"name": name, "steps": [
            "Kijk onder het rooster welke kleur bij welk cijfer hoort.",
            "Kleur elk vakje met een cijfer in die kleur. Werk rij voor rij, dan sla je niets over.",
            "Wat verschijnt er? Op de tweede bladzijde zie je hoe het wordt."]}}}, [("antwoorden", "Zo wordt het", page(True))])
pixel("pixelkunst-hart", "Pixelkunst: hart", [
    "..........", ".rr....rr.", "rmrr..rrrr", "rmrrrrrrrr", "rrrrrrrrrr", ".rrrrrrrr.", "..rrrrrr..", "...rrrr...", "....rr....", ".........."], "4-6", 1, "vormen")
pixel("pixelkunst-vis", "Pixelkunst: vis", [
    "............", "...oooo.....", "..oooooo..o.", ".oxoooooo.oo", "ooooyooooooo", ".oooyoooo.oo", "..oooooo..o.", "...oooo.....", "............", ".b...b....b.", "bbbbbbbbbbbb", "............"], "4-6", 1, "zee")
pixel("pixelkunst-huis", "Pixelkunst: huisje", [
    "......r.........", ".....rrr..zz....", "....rrrrr.zz....", "...rrrrrrrzz....", "..rrrrrrrrrr....", ".rrrrrrrrrrrr...", "..yyyyyyyyyy....", "..ybbyyyybby....", "..ybbyyyybby....", "..yyyywwyyyy....",
    "..yyyywwyyyy....", "..yyyywwyyyy....", "llllllllllllllll", "gggggggggggggggg"], "6-9", 2, "thuis")
pixel("pixelkunst-ijsje", "Pixelkunst: ijsje", [
    "....mmmm....", "...mmmmmm...", "..mmkmmmmm..", "..mmmmmmmm..", "...bbbbbb...", "..bbbbbbbb..", "..bbbbkbbb..", "...oooooo...", "...owowow...", "....owow....", "....wowo....", ".....ow.....", ".....wo.....", "......o....."], "4-6", 1, "eten")
pixel("pixelkunst-schildpad", "Pixelkunst: schildpad", [
    "................", "................", ".....gggggg.....", "....glglglgl....", "...gllggllggl...", "..glgglgglgglgll", ".ggggggggggggglx", ".llllllllllllll.", "..ll..ll..ll....", "..ll..ll..ll....", "................",
    "bbbbbbbbbbbbbbbb"], "6-9", 2, "dieren")
pixel("pixelkunst-raket", "Pixelkunst: raket", [
    "nnnnnnnnnnnnnnnn", "nnnnnnnrnnnnnnyn", "nnnnnnrrrnnnnnnn", "nnynnnzzznnnnnnn", "nnnnnnzbznnnnnnn", "nnnnnnzzznnnnnnn", "nnnnnnzbznnnnynn", "nnnnnnzzznnnnnnn", "nnnnnrzzzrnnnnnn", "nnnnrrzzzrrnnnnn",
    "nnnnrnoyonrnnnnn", "nnnnnnyoynnnnnnn", "nnnnnnnonnnnnnnn", "nynnnnnnnnnnnynn"], "6-9", 3, "ruimte")
