"""Batch 10: spelletjes om te printen (domino, bingo, kamertje verhuren, racebord, tangram)."""
import math, random
from shapely.geometry import Polygon
from shapely.ops import unary_union
from lib_gen import *
from shapes import heart_path, star_path

# ---------- domino ----------
PIPS = {0: [], 1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
        5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}
def domino():
    sh = Sheet(); title(sh, "Domino", 16)
    sh.text(100, 27, "28 stenen: elke combinatie van 0 tot en met 6 precies één keer.", 6.5)
    tiles = [(a, b) for a in range(7) for b in range(a, 7)]
    assert len(tiles) == 28
    w, h = 44, 22
    for i, (a, b) in enumerate(tiles):
        col, row = i % 4, i // 4
        x, y = 12 + col * 45, 36 + row * 32
        sh.rect_r(x, y, w, h, "-", 4); sh.seg(x + w / 2, y + 3, x + w / 2, y + h - 3)
        for half, n in ((0, a), (1, b)):
            cx = x + w / 4 + half * w / 2; cy = y + h / 2
            for dx, dy in PIPS[n]: sh.dot(cx + dx * 6, cy + dy * 6, 1.8)
        sh.rect_line(x - .5, y - .5, w + 1, h + 1, "cut", 4)
    sh.legend(["cut"], 276)
    write(OUT, "domino-stenen", sh, {"category": "leren", "age": "4-6", "kind": "spel", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kinderschaar"}, {"slug": "stevig-papier", "optional": True}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": "Domino om zelf te knippen", "printNote": "Op stevig papier (of op karton geplakt) gaan de stenen langer mee.", "steps": [
            "Knip de 28 dominostenen uit.",
            "Leg ze omgekeerd op tafel en husselen maar. Iedereen pakt er 7 (met z'n tweeën) of 5 (met meer spelers).",
            "Wie de dubbele zes heeft, begint. Om de beurt leg je een steen aan: het aantal stippen moet hetzelfde zijn als waar je tegenaan legt.",
            "Kun je niet? Pak een steen van de stapel of sla een beurt over. Wie het eerst al zijn stenen kwijt is, wint."]}}})
domino()

# ---------- bingo: kleuren en vormen ----------
def bingo():
    shapes_ = ["rond", "vierkant", "driehoek", "ster", "hart", "ruit"]
    cols = [("r", "rood"), ("b", "blauw"), ("y", "geel"), ("g", "groen")]
    combos = [(s, c) for s in shapes_ for c in cols]  # 24
    def draw(sh, s, code, x, y, r=9):
        if s == "rond": sh.circle_r(x, y, r, code)
        elif s == "vierkant": sh.rect_r(x - r * .85, y - r * .85, r * 1.7, r * 1.7, code)
        elif s == "driehoek": sh.poly_r([(x, y - r), (x + r, y + r * .8), (x - r, y + r * .8)], code)
        elif s == "ster": sh.region(star_path(x, y, r * 1.15, r * .5), code)
        elif s == "hart": sh.region(heart_path(x, y, r * .95), code)
        else: sh.poly_r([(x, y - r), (x + r * .8, y), (x, y + r), (x - r * .8, y)], code)
    rr = random.Random(4)
    sh = Sheet(); title(sh, "Bingo: kleuren en vormen", 15)
    cards = []
    for k in range(4):
        pick = rr.sample(combos, 9); cards.append(pick)
        ox, oy = 14 + (k % 2) * 90, 30 + (k // 2) * 94
        sh.rect_line(ox, oy, 82, 82, "cut", 4)
        for i, (s, (code, _)) in enumerate(pick):
            x, y = ox + 14 + (i % 3) * 27, oy + 14 + (i // 3) * 27
            draw(sh, s, code, x, y - 2, 8)
            sh.text(x, y + 11, dict(cols)[code], 4.6)
    assert len({tuple(c) for c in cards}) == 4
    sh.text(100, 226, "Speelkaartjes voor de spelleider staan op de tweede bladzijde.", 6)
    sh.legend(["cut"], 276)
    caller = Sheet(); title(caller, "Trekkaartjes", 16)
    for i, (s, (code, word)) in enumerate(combos):
        x, y = 12 + (i % 6) * 30, 30 + (i // 6) * 40
        caller.rect_line(x, y, 28, 36, "cut", 3)
        draw(caller, s, code, x + 14, y + 14, 8)
        caller.text(x + 14, y + 31, word, 5)
    caller.legend(["cut"], 276)
    write(OUT, "bingo-kleuren-en-vormen", sh, {"category": "vormen", "age": "2-4", "kind": "spel", "difficulty": 1, "minutes": 15,
        "materials": [{"slug": "kinderschaar"}, {"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": "Bingo met kleuren en vormen", "steps": [
            "Kleur de vormen in de kleur die de spelleider kiest, of print in kleur. Op de trekkaartjes staat bij elke vorm de kleur.",
            "Knip de vier bingokaarten en de trekkaartjes uit.",
            "De spelleider trekt een kaartje en zegt bijvoorbeeld: een rode ster. Wie hem heeft, legt er een knoopje of muntje op.",
            "Drie op een rij? Roep bingo! Een volle kaart is de grote bingo."]}}}, [("extra", "Trekkaartjes", caller)])
bingo()

# ---------- kamertje verhuren ----------
def kamertje():
    sh = Sheet(); title(sh, "Kamertje verhuren", 16)
    sh.text(100, 27, "Om de beurt een streepje. Hokje dicht? Zet je letter erin.", 5.6)
    n = 10; s = 16; x0 = 100 - n / 2 * s; y0 = 40
    for i in range(n + 1):
        for j in range(n + 1): sh.dot(x0 + i * s, y0 + j * s, 1.6)
    sh.text(40, 222, "Speler 1: ......", 8, "start"); sh.text(110, 222, "Speler 2: ......", 8, "start")
    sh.text(40, 238, "Hokjes: ......", 8, "start"); sh.text(110, 238, "Hokjes: ......", 8, "start")
    write(OUT, "kamertje-verhuren", sh, {"category": "vormen", "age": "6-9", "kind": "spel", "difficulty": 2, "minutes": 20,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": "Kamertje verhuren (stippenspel)", "steps": [
            "Speel met z'n tweeën, elk met een eigen kleur potlood.",
            "Om de beurt trek je één streepje tussen twee stippen die naast of onder elkaar liggen (niet schuin).",
            "Maak je met jouw streepje een hokje dicht? Dan schrijf je je letter erin en mag je nog een keer.",
            "Zijn alle stippen verbonden? Tel de hokjes: wie de meeste heeft, wint."]}}})
kamertje()

# ---------- racebord ----------
def racebord():
    sh = Sheet(); title(sh, "Dobbelrace naar de finish", 15)
    path = []
    cols, rows = 7, 6; s = 24; x0 = 16; y0 = 40
    for r_ in range(rows):
        cs = range(cols) if r_ % 2 == 0 else range(cols - 1, -1, -1)
        for c in cs: path.append((x0 + c * s, y0 + r_ * s * 1.2))
    special = {5: ("2 vooruit", "l"), 11: ("1 terug", "k"), 16: ("nog eens", "y"), 22: ("naar 18", "k"), 27: ("3 vooruit", "l"), 33: ("beurt over", "b"), 38: ("2 terug", "k")}
    for i, (x, y) in enumerate(path):
        txt, code = special.get(i, (None, "-"))
        if i == 0: code = "g"
        if i == len(path) - 1: code = "r"
        sh.rect_r(x, y, s - 2, s - 2, code, 3)
        sh.text(x + 4, y + 7, str(i + 1), 6, "start")
        if txt:
            words = txt.split(" ")
            for k, wd in enumerate(words): sh.text(x + (s - 2) / 2, y + 13 + k * 5, wd, 4.6)
    sh.text(path[0][0] + 11, path[0][1] + 17, "start", 4.8)
    sh.text(path[-1][0] + 11, path[-1][1] + 17, "finish", 4.8)
    sh.text(100, 236, "Je hebt een dobbelsteen nodig en voor elke speler een pion", 6)
    sh.text(100, 244, "(een knoopje, muntje of gummetje).", 6)
    for k, c in enumerate("rbyg"):
        cx = 60 + k * 26; sh.circle_r(cx, 260, 7, c); sh.circle_r(cx, 252, 4, c)
    write(OUT, "dobbelrace", sh, {"category": "vormen", "age": "4-6", "kind": "spel", "difficulty": 1, "minutes": 20,
        "materials": [{"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": "Dobbelrace: bordspel om te printen", "printNote": "Je hebt ook een dobbelsteen nodig.", "steps": [
            "Kleur het bord in. Iedereen zet zijn pion op start (vakje 1).",
            "Gooi om de beurt en loop zoveel vakjes verder als je gooit.",
            "Kom je op een vakje met tekst? Doe wat er staat.",
            "Wie als eerste op de finish komt, wint. Je hoeft niet precies te gooien."]}}})
racebord()

# ---------- tangram ----------
def pieces():
    return {"groot1": [(0, 0), (8, 0), (4, 4)], "groot2": [(0, 0), (4, 4), (0, 8)], "middel": [(8, 4), (8, 8), (4, 8)],
            "vierkant": [(4, 4), (6, 6), (4, 8), (2, 6)], "klein1": [(0, 8), (2, 6), (4, 8)], "klein2": [(4, 4), (6, 2), (6, 6)],
            "ruit": [(8, 0), (8, 4), (6, 6), (6, 2)]}
CODES = {"groot1": "r", "groot2": "b", "middel": "y", "vierkant": "g", "klein1": "o", "klein2": "p", "ruit": "t"}
def check(fig):
    polys = [Polygon(p) for p in fig.values()]
    assert all(p.is_valid for p in polys)
    tot = sum(p.area for p in polys); un = unary_union(polys).area
    assert abs(tot - 64) < 1e-6 and abs(un - 64) < 1e-3, (tot, un)
r2 = math.sqrt(2)
def figures():
    vis = {"groot1": [(0, 4), (8, 4), (4, 0)], "groot2": [(0, 4), (8, 4), (4, 8)],
           "middel": [(0, 4), (-2 * r2, 4 - 2 * r2), (-2 * r2, 4 + 2 * r2)],
           "klein1": [(2, 2), (4, 0), (2, -2)], "klein2": [(2, 6), (4, 8), (2, 10)],
           "vierkant": [(8, 4), (10, 2), (12, 4), (10, 6)],
           "ruit": [(-2 * r2, 4 - 2 * r2), (-2 * r2 - 2, 4 - 2 * r2 - 2), (-2 * r2 - 2, 4 - 2 * r2 + 2), (-2 * r2, 4 - 2 * r2 + 4)]}
    a = 4 * r2
    boot = {"groot1": [(4, 8), (4, 8 - a), (4 + a, 8)], "groot2": [(4, 8), (4, 8 - a), (4 - a, 8)],
            "klein1": [(4 - a, 8), (4 - a + 2 * r2, 8), (4 - a + 2 * r2, 8 + 2 * r2)],
            "vierkant": [(4 - a + 2 * r2, 8), (4, 8), (4, 8 + 2 * r2), (4 - a + 2 * r2, 8 + 2 * r2)],
            "middel": [(4, 8), (4 + a, 8), (4 + 2 * r2, 8 + 2 * r2)],
            "klein2": [(4, 8), (4 + 2 * r2, 8 + 2 * r2), (4, 8 + 2 * r2)],
            "ruit": [(4, 8 - a), (4, 8 - a - 4), (6, 8 - a - 6), (6, 8 - a - 2)]}
    return [("Vierkant", pieces()), ("Vis", vis), ("Zeilboot", boot)]
def tangram():
    figs = figures()
    for _, fg in figs: check(fg)
    sh = Sheet(); title(sh, "Tangram", 16)
    sh.text(100, 27, "Zeven stukjes, eindeloos veel figuren. Knip ze uit en leg ze na.", 6.5)
    k = 19; ox, oy = 24, 40
    for name, p in pieces().items():
        sh.poly_r([(ox + x * k, oy + y * k) for x, y in p], CODES[name])
    sh.rect_line(ox, oy, 8 * k, 8 * k, "cut")
    for name, p in pieces().items():
        sh.line("M" + " L".join(f"{f(ox + x * k)} {f(oy + y * k)}" for x, y in p) + "Z", "cut")
    sh.text(100, 210, "Leg de figuren op de volgende bladzijde na.", 6)
    sh.text(100, 218, "Alle zeven stukjes doen mee, zonder overlap.", 6)
    sh.legend(["cut"], 276)
    ch = Sheet(); title(ch, "Leg deze figuren na", 16)
    ans = Sheet(); title(ans, "Zo kan het", 16)
    for i, (name, fg) in enumerate(figs):
        allpts = [pt for p in fg.values() for pt in p]
        mnx, mxx = min(x for x, _ in allpts), max(x for x, _ in allpts); mny, mxy = min(y for _, y in allpts), max(y for _, y in allpts)
        sc = min(70 / (mxx - mnx), 70 / (mxy - mny))
        bx, by = 100 - (mxx - mnx) * sc / 2, 40 + i * 80
        poly = unary_union([Polygon(p) for p in fg.values()])
        geoms = getattr(poly, "geoms", [poly])
        for g in geoms:
            d = "M" + " L".join(f"{f(bx + (x - mnx) * sc)} {f(by + (y - mny) * sc)}" for x, y in list(g.exterior.coords)[:-1]) + "Z"
            ch.raw(f'<path class="r" d="{d}" style="fill:#222"/>', "x")
        ch.text(20, by + 8, name, 7, "start"); ans.text(20, by + 8, name, 7, "start")
        for pn, p in fg.items():
            ans.poly_r([(bx + (x - mnx) * sc, by + (y - mny) * sc) for x, y in p], CODES[pn])
    write(OUT, "tangram", sh, {"category": "vormen", "age": "6-9", "kind": "spel", "difficulty": 2, "minutes": 25, "paperGsm": 160,
        "materials": [{"slug": "kinderschaar"}, {"slug": "kleurpotloden"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Tangram: knip en leg figuren", "steps": [
            "Kleur de zeven stukjes elk in een eigen kleur en knip ze uit langs de lijnen.",
            "Leg eerst het vierkant weer in elkaar, net als op het vel.",
            "Probeer daarna de vis en de zeilboot van de tweede bladzijde. Gebruik altijd alle zeven stukjes, zonder ze over elkaar te leggen.",
            "Lukt het niet? Op de laatste bladzijde zie je een oplossing. Verzin daarna zelf een figuur!"]}}},
        [("extra", "Leg deze figuren na", ch), ("antwoorden", "Zo kan het", ans)])
tangram()
