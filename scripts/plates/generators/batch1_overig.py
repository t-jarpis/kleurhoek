import os
import math, random
from kit import *
OUT = os.environ.get("OUT", "concepten/batch1")
SCHAAR = {"slug": "kinderschaar"}

def star(cx, cy, r1, r2, n=5):
    return [(cx + (r1 if i % 2 == 0 else r2) * math.sin(math.pi * i / n), cy - (r1 if i % 2 == 0 else r2) * math.cos(math.pi * i / n)) for i in range(2 * n)]

# ---------- Waaier ----------
def waaier():
    sh = Sheet()
    title(sh, "Waaier", 16)
    x0, y0, w, h = 10, 30, 180, 120
    # schubbenpatroon in rijen (vlakken), daarna de vouwlijnen erover
    r = 15; colors = "bntp"
    for row in range(4):
        cy = y0 + h - row * 24
        for k in range(-1, 7):
            cx = x0 + k * 30 + (15 if row % 2 else 0)
            if cx - r < x0 - 1 or cx + r > x0 + w + 1: continue
            sh.region(arc_path(cx, cy, 0, r * 1.15, 180, 360), colors[(row + k) % 4])
    sh.rect_line(x0, y0, w, h, "cut")
    for i in range(1, 18):
        sh.seg(x0 + i * 10, y0, x0 + i * 10, y0 + h, "fold")
    # stappenvoorbeeld
    sh.text(100, 172, "Zo vouw je hem:", 8)
    sh.line("M40 214" + "".join(f"L{40 + (i + 1) * 13} {184 if i % 2 == 0 else 214}" for i in range(9)), "l", "stroke-width:1.2")
    sh.text(100, 232, "heen en weer, als een zigzag", 6.5)
    sh.legend(["cut", "fold"], 274)
    write(OUT, "waaier-vouwen", sh, {"category": "zee", "age": "6-9", "kind": "vouwblad", "difficulty": 1, "minutes": 20,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "plakband"}],
        "i18n": {"nl": {"name": "Waaier vouwen", "steps": [
            "Kleur de schubben aan de voorkant in, in mooie kleuren.",
            "Knip de rechthoek uit langs de streepjeslijn.",
            "Vouw op de eerste stippellijn naar achteren, op de volgende naar voren, en zo verder: heen en weer als een zigzag.",
            "Knijp de onderkant stevig samen en wikkel er een stukje plakband omheen. Klap de bovenkant open: klaar is je waaier."]}}})
waaier()

# ---------- Papieren vliegtuig ----------
def vliegtuig():
    sh = Sheet()
    sh.seg(100, 0, 100, 280, "fold")
    sh.line("M100 0L0 100M100 0L200 100", "fold")
    sh.line("M100 0L0 241M100 0L200 241", "fold")
    sh.text(100, 120, "1", 9); sh.text(56, 52, "2", 9); sh.text(144, 52, "2", 9); sh.text(30, 170, "3", 9); sh.text(170, 170, "3", 9)
    # versiering op de vleugels om in te kleuren
    for cx, cy, c in [(40, 215, "r"), (160, 215, "b")]:
        sh.circle_r(cx, cy, 11, c); sh.circle_r(cx, cy, 5, "-")
    sh.poly_r([(100 - 6, 150), (100, 140), (106, 150), (100, 160)], "y")
    sh.text(100, 268, "Mijn vliegtuig", 7)
    # stappenpagina met tekeningen
    st = Sheet()
    title(st, "Zo vouw je het vliegtuig", 16)
    k = .25
    shapes = [
        ("1. Dubbel en weer open", [(0, 0), (200, 0), (200, 280), (0, 280)], ["M100 0V280"]),
        ("2. Hoeken naar het midden", [(100, 0), (200, 100), (200, 280), (0, 280), (0, 100)], ["M100 0V100", "M100 0L0 100M100 0L200 100"]),
        ("3. Randen weer naar het midden", [(100, 0), (200, 241), (200, 280), (0, 280), (0, 241)], ["M100 0V241"]),
        ("4. Dubbel vouwen", [(100, 0), (100, 280), (0, 280), (0, 241)], []),
        ("5. Vleugels omlaag", [(100, 0), (100, 280), (75, 280), (75, 60)], ["M75 60L0 241L0 280L75 280"]),
    ]
    for i, (label, poly, lines) in enumerate(shapes):
        col, row = i % 2, i // 2
        ox, oy = 26 + col * 92, 30 + row * 84
        st.raw(f'<path class="l" style="stroke-width:1.2" fill="none" transform="translate({ox} {oy}) scale({k})" d="M' + " L".join(f"{x} {y}" for x, y in poly) + 'Z"/>')
        for d in lines: st.raw(f'<path class="fold" transform="translate({ox} {oy}) scale({k})" d="{d}" style="stroke-width:3.2"/>')
        st.text(ox + 25, oy + 78, label, 6)
    st.text(146, 210, "6. Laat hem vliegen!", 7)
    write(OUT, "papieren-vliegtuig", sh, {"category": "voertuigen", "age": "6-9", "kind": "vouwblad", "difficulty": 2, "minutes": 10,
        "materials": [{"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": "Papieren vliegtuig vouwen", "printNote": "Gewoon printpapier vliegt het best.", "steps": [
            "Kleur de rondjes op de vleugels in (dat wordt de buitenkant).",
            "Leg het vel met de tekening naar beneden. Vouw het dubbel in de lengte op lijn 1 en vouw het weer open.",
            "Vouw de twee bovenhoeken naar de middenlijn, zodat de schuine randen op lijn 2 komen.",
            "Vouw de nieuwe schuine randen nog een keer naar het midden (lijn 3).",
            "Vouw het vliegtuig dubbel langs het midden, met de vouwtjes aan de binnenkant.",
            "Vouw elke vleugel omlaag zodat de bovenrand gelijk ligt met de onderkant van de romp. Klaar: gooi hem zachtjes recht vooruit."],
}}}, [("extra", "Zo vouw je het (tekeningen)", st)])
vliegtuig()

# ---------- Slangen en ladders + pionnen en dobbelsteen ----------
def cell_xy(n, x0, y0, s, size=6):
    r = (n - 1) // size; c = (n - 1) % size
    if r % 2: c = size - 1 - c
    return x0 + c * s + s / 2, y0 + (size - 1 - r) * s + s / 2

def snake(sh, a, b, code):
    (x1, y1), (x2, y2) = a, b
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -uy, ux
    left, right = [], []
    N = 24
    for i in range(N + 1):
        t = i / N
        off = math.sin(t * math.pi * 3) * 6
        cx, cy = x1 + (x2 - x1) * t + nx * off, y1 + (y2 - y1) * t + ny * off
        wdt = 3.4 * (1 - t * .7)
        left.append((cx + nx * wdt, cy + ny * wdt)); right.append((cx - nx * wdt, cy - ny * wdt))
    sh.poly_r(left + right[::-1], code)
    sh.circle_r(x1, y1, 5, code); sh.dot(x1 - 1.6, y1 - 1.2, .8); sh.dot(x1 + 1.6, y1 - 1.2, .8)

def ladder(sh, a, b):
    (x1, y1), (x2, y2) = a, b
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -uy * 4, ux * 4
    sh.line(f"M{f(x1 + nx)} {f(y1 + ny)}L{f(x2 + nx)} {f(y2 + ny)}M{f(x1 - nx)} {f(y1 - ny)}L{f(x2 - nx)} {f(y2 - ny)}", "l", "stroke-width:1.6")
    steps = int(L / 7)
    for i in range(1, steps):
        t = i / steps; px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        sh.seg(px + nx, py + ny, px - nx, py - ny, "l", "stroke-width:1.2")

def slangen():
    sh = Sheet()
    title(sh, "Slangen en ladders", 16)
    x0, y0, s = 13, 28, 29
    colors = "yklbtk"
    for n in range(1, 37):
        cx, cy = cell_xy(n, x0, y0, s)
        sh.rect_r(cx - s / 2, cy - s / 2, s, s, "-")
        sh.text(cx - s / 2 + 3, cy - s / 2 + 8, str(n), 6.5, "start")
    c1 = cell_xy(1, x0, y0, s); sh.text(c1[0] + 3, c1[1] + 9, "start", 5.5)
    c36 = cell_xy(36, x0, y0, s); sh.text(c36[0] + 2, c36[1] + 9, "finish", 5.5)
    for a, b in [(3, 16), (8, 22), (20, 29)]: ladder(sh, cell_xy(a, x0, y0, s), cell_xy(b, x0, y0, s))
    for head, tail, c in [(17, 5, "g"), (27, 15, "o"), (33, 24, "p")]: snake(sh, cell_xy(head, x0, y0, s), cell_xy(tail, x0, y0, s), c)
    sh.text(100, 210, "Ladder op: klim omhoog. Op een slangenkop: glij naar de staart.", 5.6)
    sh.text(100, 219, "Wie het eerst op 36 staat, wint.", 5.6)
    # pionnen en dobbelsteen op pagina 2
    p2 = Sheet()
    title(p2, "Pionnen en dobbelsteen", 16)
    for i in range(4):
        x, y, w = 14 + i * 26, 30, 22
        p2.rect_line(x, y, w, 96, "cut")
        for yy in (y + 8, y + 48, y + 88): p2.seg(x, yy, x + w, yy, "fold")
        # figuurtje twee keer: rechtop (onder) en op zijn kop (boven)
        for flip, base in ((False, y + 88), (True, y + 8)):
            cx = x + w / 2
            if not flip:
                p2.circle_r(cx, base - 30, 5, "-"); p2.region(f"M{f(cx - 7)} {f(base - 4)}Q{f(cx - 7)} {f(base - 24)} {f(cx)} {f(base - 24)}Q{f(cx + 7)} {f(base - 24)} {f(cx + 7)} {f(base - 4)}Z", "rbgy"[i])
            else:
                p2.circle_r(cx, base + 30, 5, "-"); p2.region(f"M{f(cx - 7)} {f(base + 4)}Q{f(cx - 7)} {f(base + 24)} {f(cx)} {f(base + 24)}Q{f(cx + 7)} {f(base + 24)} {f(cx + 7)} {f(base + 4)}Z", "rbgy"[i])
    # dobbelsteen: kruisvorm; tegenover elkaar samen 7
    q = 22; dx0, dy0 = 132, 46
    faces = {(1, 0): 2, (0, 1): 3, (1, 1): 1, (2, 1): 4, (1, 2): 5, (1, 3): 6}
    pips = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)], 5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}
    def tab(x1, y1, x2, y2):
        # trapezium naar buiten (links van de richting x1->x2)
        ux, uy = x2 - x1, y2 - y1; L = math.hypot(ux, uy); nx, ny = uy / L * 6, -ux / L * 6
        a = (x1 + ux * .15 + nx, y1 + uy * .15 + ny); b = (x1 + ux * .85 + nx, y1 + uy * .85 + ny)
        p2.raw(f'<path class="glue" d="M{f(x1)} {f(y1)}L{f(a[0])} {f(a[1])}L{f(b[0])} {f(b[1])}L{f(x2)} {f(y2)}Z"/>')
        p2.line(f"M{f(x1)} {f(y1)}L{f(a[0])} {f(a[1])}L{f(b[0])} {f(b[1])}L{f(x2)} {f(y2)}", "cut")
    for (c, r), v in faces.items():
        x, y = dx0 + c * q, dy0 + r * q
        p2.rect_r(x, y, q, q, "-")
        for px, py in pips[v]: p2.dot(x + q / 2 + px * 6, y + q / 2 + py * 6, 1.9)
    X = lambda c: dx0 + c * q; Y = lambda r: dy0 + r * q
    # buitenrand knippen, randen tussen vlakken vouwen, lijmflappen op 7 randen
    tab(X(1), Y(1), X(1), Y(0))        # A links
    tab(X(2), Y(0), X(2), Y(1))        # A rechts
    tab(X(1), Y(0), X(2), Y(0))        # A boven
    tab(X(1), Y(3), X(1), Y(2))        # E links
    tab(X(2), Y(2), X(2), Y(3))        # E rechts
    tab(X(1), Y(4), X(1), Y(3))        # F links
    tab(X(2), Y(3), X(2), Y(4))        # F rechts
    # overige buitenranden knippen
    p2.line(f"M{X(1)} {Y(1)}H{X(0)}V{Y(2)}H{X(1)}M{X(2)} {Y(1)}H{X(3)}V{Y(2)}H{X(2)}M{X(1)} {Y(4)}H{X(2)}", "cut")
    for x1, y1, x2, y2 in [(X(1), Y(1), X(2), Y(1)), (X(1), Y(2), X(2), Y(2)), (X(1), Y(3), X(2), Y(3)), (X(1), Y(1), X(1), Y(2)), (X(2), Y(1), X(2), Y(2))]:
        p2.seg(x1, y1, x2, y2, "fold")
    p2.text(156, 150, "dobbelsteen", 6.5)
    p2.legend(["cut", "fold", "glue"], 274)
    write(OUT, "slangen-en-ladders", sh, {"category": "sport", "age": "4-6", "kind": "spel", "difficulty": 1, "minutes": 30, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Slangen en ladders (met pionnen en dobbelsteen)", "printNote": "Print het bord op gewoon papier en pagina 2 liefst op stevig papier.", "steps": [
            "Kleur het speelbord, de slangen en de pionnen in.",
            "Pionnen: knip ze uit, vouw ze op de stippellijnen tot een dakje en vouw de voetjes naar buiten.",
            "Dobbelsteen: knip hem uit, vouw alle stippellijnen, smeer lijm op de grijze flapjes en plak hem dicht tot een kubus.",
            "Spelen: iedereen begint op 1. Gooi om de beurt en loop zoveel vakjes. Onderaan een ladder klim je omhoog; land je op een slangenkop, dan glij je naar de staart. Wie het eerst op 36 staat, wint."]}}},
        [("extra", "Pionnen en dobbelsteen", p2)])
slangen()

def bke():
    sh = Sheet()
    title(sh, "Boter, kaas en eieren", 16)
    for i in range(6):
        col, row = i % 2, i // 2
        x, y = 22 + col * 88, 34 + row * 80
        sh.line(f"M{x + 23} {y}V{y + 66}M{x + 45} {y}V{y + 66}M{x} {y + 22}H{x + 68}M{x} {y + 44}H{x + 68}")
    sh.text(100, 268, "Om de beurt een kruisje of een rondje. Drie op een rij wint!", 6)
    write(OUT, "boter-kaas-en-eieren", sh, {"category": "sport", "age": "4-6", "kind": "spel", "difficulty": 1, "minutes": 15,
        "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": "Boter, kaas en eieren (6 spelletjes)", "steps": [
            "Speel met z'n tweeën. De een zet kruisjes, de ander rondjes.",
            "Zet om de beurt jouw teken in een leeg vakje.",
            "Wie als eerste drie op een rij heeft (recht of schuin), wint. Vol zonder winnaar? Gelijkspel: op naar het volgende veld."]}}})
bke()

# ---------- Maskers ----------
def mask(slug, name, build, cat):
    sh = Sheet()
    title(sh, name, 14)
    build(sh)
    sh.legend(["cut"], 274)
    write(OUT, slug, sh, {"category": cat, "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25, "adultHelp": True, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "elastiek"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier, dan blijft het masker beter in vorm.", "steps": [
            "Kleur het masker in.",
            "Knip het masker uit langs de buitenste streepjeslijn.",
            "Een volwassene knipt of snijdt de ooggaten uit en prikt de twee gaatjes aan de zijkant.",
            "Knoop aan elke kant een stuk elastiek vast, zo lang dat het masker goed om je hoofd past."]}}})

def vos(sh):
    cy = 110
    outline = [(18, cy - 14), (30, cy - 72), (64, cy - 34), (100, cy - 42), (136, cy - 34), (170, cy - 72), (182, cy - 14), (168, cy + 26), (124, cy + 56), (100, cy + 82), (76, cy + 56), (32, cy + 26)]
    sh.line("M" + " L".join(f"{x} {y}" for x, y in outline) + "Z", "cut")
    sh.poly_r(outline, "o")
    sh.poly_r([(34, cy - 58), (58, cy - 34), (40, cy - 24)], "k"); sh.poly_r([(166, cy - 58), (142, cy - 34), (160, cy - 24)], "k")
    sh.region(f"M32 {cy + 26}Q60 {cy + 10} 76 {cy + 56}L100 {cy + 82}L124 {cy + 56}Q140 {cy + 10} 168 {cy + 26}L124 {cy + 56}L100 {cy + 82}L76 {cy + 56}Z", "-")
    sh.ellipse_r(100, cy + 70, 9, 7, "x")
    for ex in (68, 132):
        sh.raw(f'<ellipse class="cut" cx="{ex}" cy="{cy - 4}" rx="15" ry="10"/>')
    for hx in (26, 174): sh.circle_line(hx, cy + 4, 2.6, "cut")
mask("masker-vos", "Masker: vos", vos, "dieren")

def uil_mask(sh):
    cy = 112
    sh.region(f"M100 {cy - 60}C150 {cy - 60} 186 {cy - 40} 184 {cy}C182 {cy + 50} 140 {cy + 70} 100 {cy + 70}C60 {cy + 70} 18 {cy + 50} 16 {cy}C14 {cy - 40} 50 {cy - 60} 100 {cy - 60}Z", "w")
    sh.line(f"M100 {cy - 60}C150 {cy - 60} 186 {cy - 40} 184 {cy}C182 {cy + 50} 140 {cy + 70} 100 {cy + 70}C60 {cy + 70} 18 {cy + 50} 16 {cy}C14 {cy - 40} 50 {cy - 60} 100 {cy - 60}Z", "cut")
    sh.poly_r([(30, cy - 40), (24, cy - 78), (60, cy - 54)], "w"); sh.poly_r([(170, cy - 40), (176, cy - 78), (140, cy - 54)], "w")
    sh.line(f"M30 {cy - 40}L24 {cy - 78}L60 {cy - 54}M170 {cy - 40}L176 {cy - 78}L140 {cy - 54}", "cut")
    for ex in (66, 134):
        sh.circle_r(ex, cy - 4, 28, "y")
        sh.circle_r(ex, cy - 4, 20, "o")
        sh.raw(f'<circle class="cut" cx="{ex}" cy="{cy - 4}" r="11"/>')
    sh.poly_r([(92, cy + 22), (108, cy + 22), (100, cy + 40)], "o")
    for i in range(5):
        x = 64 + i * 18
        sh.line(f"M{x - 7} {cy + 50}Q{x} {cy + 58} {x + 7} {cy + 50}")
    for hx in (22, 178): sh.circle_line(hx, cy + 6, 2.6, "cut")
mask("masker-uil", "Masker: uil", uil_mask, "dieren")

# ---------- Kroon ----------
def kroon():
    sh = Sheet()
    title(sh, "Kroon", 14)
    def band(y, points=True, glue=True):
        x0, x1, h = 10, 190, 52
        top = [(x0, y)]
        if points:
            n = 6; seg = (x1 - x0) / n
            top = []
            for i in range(n):
                top += [(x0 + i * seg, y + 18), (x0 + i * seg + seg / 2, y)]
            top += [(x1, y + 18)]
            outline = top + [(x1, y + h), (x0, y + h)]
        else:
            outline = [(x0, y + 18), (x1, y + 18), (x1, y + h), (x0, y + h)]
        sh.poly_r(outline, "y")
        sh.line("M" + " L".join(f"{f(x)} {f(yy)}" for x, yy in outline) + "Z", "cut")
        if points:
            for i in range(6):
                cx = x0 + i * 30 + 15
                sh.circle_r(cx, y + 34, 5, "rbg"[i % 3])
            for i in range(6):
                sh.poly_r(star(x0 + i * 30 + 15, y + 8, 3.4, 1.5), "-")
        if glue:
            sh.raw(f'<rect class="glue" x="{x1 - 14}" y="{y + 20}" width="12" height="{h - 22}"/>')
    band(30); band(98); band(166, points=False)
    sh.text(100, 236, "Strook zonder punten: om de kroon langer te maken.", 6)
    sh.legend(["cut", "glue"], 274)
    write(OUT, "kroon-knippen", sh, {"category": "sprookjes", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 20,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "plakband", "optional": True}],
        "i18n": {"nl": {"name": "Kroon om op te zetten", "steps": [
            "Kleur de stroken met punten in: de edelstenen in mooie kleuren.",
            "Knip de stroken uit langs de streepjeslijn.",
            "Plak twee stroken met punten aan elkaar (grijze flap onder het andere uiteinde). Te klein? Plak de strook zonder punten ertussen.",
            "Meet om je hoofd en plak de kroon dicht. Klaar, majesteit!"]}}})
kroon()

# ---------- Mandala's (12+) ----------
def mandala(slug, name, rings, seed):
    sh = Sheet(200)
    cx, cy = 100, 100
    rnd = random.Random(seed)
    for kind, r1, r2, n, colors in rings:
        for i in range(n):
            a1, a2 = i * 360 / n - 90, (i + 1) * 360 / n - 90
            code = colors[i % len(colors)]
            if kind == "seg" and n == 1 and r1 == 0:
                sh.circle_r(cx, cy, r2, code)
            elif kind == "seg":
                sh.region(arc_path(cx, cy, r1, r2, a1, a2), code)
            elif kind == "petal":
                am = math.radians((a1 + a2) / 2); w = math.radians((a2 - a1) / 2)
                p0 = (cx + r1 * math.cos(am), cy + r1 * math.sin(am)); p2 = (cx + r2 * math.cos(am), cy + r2 * math.sin(am))
                c1 = (cx + (r1 + r2) / 2 / math.cos(w * .9) * math.cos(am - w * .9), cy + (r1 + r2) / 2 / math.cos(w * .9) * math.sin(am - w * .9))
                c2 = (cx + (r1 + r2) / 2 / math.cos(w * .9) * math.cos(am + w * .9), cy + (r1 + r2) / 2 / math.cos(w * .9) * math.sin(am + w * .9))
                sh.region(f"M{f(p0[0])} {f(p0[1])}Q{f(c1[0])} {f(c1[1])} {f(p2[0])} {f(p2[1])}Q{f(c2[0])} {f(c2[1])} {f(p0[0])} {f(p0[1])}Z", code)
            elif kind == "dot":
                am = math.radians((a1 + a2) / 2); rr = (r1 + r2) / 2
                sh.circle_r(cx + rr * math.cos(am), cy + rr * math.sin(am), (r2 - r1) / 2, code)
            elif kind == "tri":
                am1, am2, amm = math.radians(a1), math.radians(a2), math.radians((a1 + a2) / 2)
                sh.poly_r([(cx + r1 * math.cos(am1), cy + r1 * math.sin(am1)), (cx + r2 * math.cos(amm), cy + r2 * math.sin(amm)), (cx + r1 * math.cos(am2), cy + r1 * math.sin(am2))], code)
    write(OUT, slug, sh, {"category": "patronen", "age": "12+", "kind": "kleurplaat", "difficulty": 3,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}],
        "i18n": {"nl": {"name": name}}})

mandala("mandala-bloem", "Mandala: bloem", [
    ("seg", 0, 8, 1, "y"), ("petal", 8, 30, 8, "om"), ("seg", 30, 36, 16, "ky"), ("petal", 36, 62, 16, "bntp"),
    ("dot", 62, 70, 32, "y"), ("tri", 70, 86, 32, "glg"), ("seg", 86, 94, 48, "mk")], 1)
mandala("mandala-ster", "Mandala: ster", [
    ("seg", 0, 10, 6, "ry"), ("tri", 10, 34, 6, "o"), ("seg", 34, 42, 12, "pn"), ("petal", 42, 66, 12, "tb"),
    ("tri", 66, 84, 24, "yo"), ("dot", 84, 92, 36, "mpk")], 2)
mandala("mandala-golven", "Mandala: golven", [
    ("seg", 0, 6, 1, "b"), ("seg", 6, 16, 10, "nb"), ("petal", 16, 40, 10, "tg"), ("seg", 40, 46, 20, "yl"),
    ("petal", 46, 70, 20, "nbtp"), ("seg", 70, 78, 40, "ok"), ("tri", 78, 94, 40, "rm")], 3)
print("overig klaar")
