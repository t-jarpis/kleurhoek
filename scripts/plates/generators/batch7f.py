"""Batch 7f: bouwplaten van regelmatige veelvlakken (geometrisch gecontroleerd)."""
import math
from lib_gen import *

def tab(sh, p, q, inside, depth=6, shrink=.22):
    """Lijmflap op rand p-q, aan de kant weg van punt 'inside'."""
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    if (inside[0] - mx) * nx + (inside[1] - my) * ny > 0: nx, ny = -nx, -ny
    a = (p[0] + dx * shrink + nx * depth, p[1] + dy * shrink + ny * depth); b = (q[0] - dx * shrink + nx * depth, q[1] - dy * shrink + ny * depth)
    d = f"M{f(p[0])} {f(p[1])}L{f(a[0])} {f(a[1])}L{f(b[0])} {f(b[1])}L{f(q[0])} {f(q[1])}"
    sh.raw(f'<path class="glue" d="{d}Z"/>'); sh.line(d, "cut")
def build(sh, tris, codes, tabs):
    """tris: lijst driehoeken; randen die twee keer voorkomen = vouwen, de rest kniplijn (of flap)."""
    key = lambda p: (round(p[0], 2), round(p[1], 2))
    count = {}
    for t in tris:
        for i in range(3):
            e = tuple(sorted((key(t[i]), key(t[(i + 1) % 3])))); count[e] = count.get(e, 0) + 1
    for t, c in zip(tris, codes): sh.raw(f'<path class="r" style="stroke:none" d="M{pts(t)}Z"/>', c)
    tabbed = {tuple(sorted((key(p), key(q)))) for p, q, _ in tabs}
    for e, n in count.items():
        if n == 2: sh.seg(*e[0], *e[1], "fold")
        elif e not in tabbed: sh.seg(*e[0], *e[1], "cut")
    for p, q, inside in tabs: tab(sh, p, q, inside)
    # controle: elk rand-paar moet precies één flap hebben
    return count

def icosaeder():
    sh = Sheet(); title(sh, "Twintigvlak", 16)
    sh.text(100, 27, "Twintig driehoeken worden samen bijna een bal.", 6.5)
    a = 33; h = a * math.sqrt(3) / 2; x0 = 7; y1 = 110; y2 = y1 + h
    T = [(x0 + k * a, y1) for k in range(6)]; B = [(x0 + a / 2 + k * a, y2) for k in range(6)]
    top = [(T[k], T[k + 1], (x0 + k * a + a / 2, y1 - h)) for k in range(5)]
    band = []
    for k in range(5): band += [(T[k], T[k + 1], B[k]), (B[k], B[k + 1], T[k + 1])]
    bot = [(B[k], B[k + 1], (x0 + a + k * a, y2 + h)) for k in range(5)]
    tris = top + band + bot
    cent = lambda t: (sum(p[0] for p in t) / 3, sum(p[1] for p in t) / 3)
    tabs = [(t[1], t[2], cent(t)) for t in top] + [(t[1], t[2], cent(t)) for t in bot] + [(B[5], T[5], cent(band[-1]))]
    codes = ["rybgp"[k] for k in range(5)] + ["obtlkmrnyg"[k] for k in range(10)] + ["gpryb"[k] for k in range(5)]
    cnt = build(sh, tris, codes, tabs)
    assert sum(1 for n in cnt.values() if n == 2) == 19 and sum(1 for n in cnt.values() if n == 1) == 22
    sh.text(100, 210, "Tip: kras de vouwlijnen eerst met een lege balpen en een liniaal.", 6)
    sh.legend(["cut", "fold", "glue"], 274)
    write(OUT, "twintigvlak", sh, {"category": "vormen", "age": "12+", "kind": "bouwplaat", "difficulty": 3, "minutes": 45, "adultHelp": False, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Bouwplaat: twintigvlak", "printNote": "Op stevig papier (160 gram) wordt hij het mooist.", "steps": [
            "Kleur de driehoeken in. Knip de bouwplaat uit langs de doorgetrokken lijnen; knip de grijze flapjes niet los.",
            "Vouw alle stippellijnen en alle flapjes naar binnen (de tekening blijft buiten).",
            "Plak de lange middenbaan dicht tot een ring: het flapje aan de rechterkant komt onder de linkerrand.",
            "Plak de vijf bovenste driehoeken één voor één aan elkaar tot een puntdak. Doe daarna hetzelfde aan de onderkant; het laatste flapje druk je van buitenaf aan."]}}})
icosaeder()

def viervlak():
    sh = Sheet(); title(sh, "Viervlak", 16)
    sh.text(100, 27, "Vier driehoeken worden samen een piramide.", 6.5)
    a = 80; h = a * math.sqrt(3) / 2; cx = 100; top = 50
    A = (cx, top); Bp = (cx - a, top + 2 * h); C = (cx + a, top + 2 * h)
    mAB = ((A[0] + Bp[0]) / 2, (A[1] + Bp[1]) / 2); mAC = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2); mBC = ((Bp[0] + C[0]) / 2, (Bp[1] + C[1]) / 2)
    tris = [(A, mAB, mAC), (mAB, Bp, mBC), (mAC, mBC, C), (mAB, mBC, mAC)]
    cent = lambda t: (sum(p[0] for p in t) / 3, sum(p[1] for p in t) / 3)
    tabs = [(A, mAB, cent(tris[0])), (Bp, mBC, cent(tris[1])), (C, mAC, cent(tris[2]))]
    cnt = build(sh, tris, ["r", "b", "y", "g"], tabs)
    assert sum(1 for n in cnt.values() if n == 2) == 3
    sh.legend(["cut", "fold", "glue"], 274)
    write(OUT, "viervlak", sh, {"category": "vormen", "age": "6-9", "kind": "bouwplaat", "difficulty": 1, "minutes": 15, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Bouwplaat: viervlak", "steps": [
            "Kleur de vier driehoeken elk in een andere kleur.",
            "Knip langs de doorgetrokken lijnen, de grijze flapjes blijven eraan.",
            "Vouw de stippellijnen en de flapjes naar binnen.",
            "Breng de drie punten van de grote driehoek boven elkaar bij elkaar en plak de flapjes vast. Klaar is je viervlak!"]}}})
viervlak()
