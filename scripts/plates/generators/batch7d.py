"""Batch 7d: leerwerkjes en spelletjes."""
import math, random
from lib_gen import *
from shapes import heart_path, star_path, moon_path, drop_path, cloud_path, leaf_path, fish_path

rnd = random.Random(707)
# ---------- tafels en delen ----------
for t, order in [(4, [3, 7, 1, 10, 5, 8, 2, 6, 9, 4, 0, 12]), (6, [4, 9, 2, 6, 10, 1, 7, 3, 8, 5, 11, 0]), (7, [3, 8, 1, 6, 10, 4, 9, 2, 7, 5, 0, 12]),
                 (8, [6, 2, 9, 4, 10, 1, 7, 3, 8, 5, 12, 0]), (9, [5, 9, 2, 7, 3, 10, 1, 8, 4, 6, 11, 0])]:
    sums_sheet(f"rekenen-tafel-van-{t}", f"Rekenen: de tafel van {t}", [(f"{n} × {t}", n * t) for n in order], "6-9" if t < 7 else "9+", 2 if t < 7 else 3,
               f"Weet je de tafel van {t}? Schrijf het antwoord in het hokje.", [f"Zeg de tafel van {t} hardop: 1 × {t} = {t}, 2 × {t} = {2 * t} …", "Vul de antwoorden in. Ze staan door elkaar!"])
def uniq(fn, n):
    out, seen = [], set()
    while len(out) < n:
        q = fn()
        if q[0] not in seen: seen.add(q[0]); out.append(q)
    return out
def mix610():
    a, b = rnd.randint(2, 10), rnd.randint(6, 10)
    return (f"{a} × {b}", a * b)
sums_sheet("rekenen-tafels-6-tot-10-door-elkaar", "Rekenen: tafels van 6 tot 10 door elkaar", uniq(mix610, 12), "9+", 3,
           "De moeilijke tafels door elkaar. Lukt het zonder te tellen?", ["Lees de som en zeg de tafel in je hoofd.", "Weet je het niet meteen? Begin bij een som die je wel weet: 7 × 8 is 5 × 8 plus 2 × 8."])
def div(lo, hi):
    def g():
        b = rnd.randint(lo, hi); a = rnd.randint(1, 10)
        return (f"{a * b} : {b}", a)
    return g
sums_sheet("rekenen-delen-door-2-tot-5", "Rekenen: delen door 2, 3, 4 en 5", uniq(div(2, 5), 12), "6-9", 2,
           "Hoe vaak past het tweede getal in het eerste?", ["Delen is de tafel andersom: 15 : 5 is de vraag hoeveel keer 5 er in 15 past.", "Zeg de tafel op tot je het getal tegenkomt: 5, 10, 15. Dat is 3 keer, dus 15 : 5 = 3."])
sums_sheet("rekenen-delen-door-6-tot-10", "Rekenen: delen door 6 tot en met 10", uniq(div(6, 10), 12), "9+", 3,
           "Hoe vaak past het tweede getal in het eerste?", ["Delen is de tafel andersom: 56 : 8 is de vraag hoeveel keer 8 er in 56 past.", "Weet je het niet? Zoek de som in de tafel: 7 × 8 = 56, dus 56 : 8 = 7."])

# ---------- woordzoekers ----------
def woordzoeker(slug, name, words, n, dirs, age, diff, seed, cat):
    r = random.Random(seed)
    for attempt in range(500):
        g = [[None] * n for _ in range(n)]; placed = []
        ok = True
        for w in sorted(words, key=len, reverse=True):
            for _ in range(400):
                dx, dy = r.choice(dirs); x0 = r.randrange(n); y0 = r.randrange(n)
                x1, y1 = x0 + dx * (len(w) - 1), y0 + dy * (len(w) - 1)
                if not (0 <= x1 < n and 0 <= y1 < n): continue
                if all(g[y0 + dy * i][x0 + dx * i] in (None, w[i]) for i in range(len(w))):
                    for i in range(len(w)): g[y0 + dy * i][x0 + dx * i] = w[i]
                    placed.append((w, x0, y0, x1, y1)); break
            else: ok = False; break
        if ok: break
    else: raise SystemExit("woordzoeker lukt niet: " + slug)
    for y in range(n):
        for x in range(n):
            if g[y][x] is None: g[y][x] = r.choice("ABDEGHIKLMNOPRSTUVW")
    # elk woord precies één keer te vinden
    full = "".join("".join(row) for row in g)
    def count(w):
        c = 0
        for y in range(n):
            for x in range(n):
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if (dx, dy) == (0, 0): continue
                        if all(0 <= x + dx * i < n and 0 <= y + dy * i < n and g[y + dy * i][x + dx * i] == w[i] for i in range(len(w))): c += 1
        return c
    for w in words: assert count(w) == 1, (slug, w, count(w))
    cell = 150 / n; x0, y0 = 25, 34
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else cap(name.split(": ", 1)[-1]), 16)
        if not ans: sh.text(100, 27, "Zoek de woorden en zet er een rondje omheen.", 6)
        sh.rect_line(x0 - 3, y0 - 3, n * cell + 6, n * cell + 6, "l", 4)
        if ans:
            for w, a, b, c, d in placed:
                ax, ay = x0 + a * cell + cell / 2, y0 + b * cell + cell / 2; cx, cy = x0 + c * cell + cell / 2, y0 + d * cell + cell / 2
                ang = math.degrees(math.atan2(cy - ay, cx - ax)); ln = math.hypot(cx - ax, cy - ay)
                sh.raw(f'<rect class="l" style="stroke-width:1" x="{f(ax - cell * .45)}" y="{f(ay - cell * .4)}" width="{f(ln + cell * .9)}" height="{f(cell * .8)}" rx="{f(cell * .4)}" transform="rotate({f(ang)} {f(ax)} {f(ay)})" fill="none"/>')
        for y in range(n):
            for x in range(n): sh.text(x0 + x * cell + cell / 2, y0 + y * cell + cell * .7, g[y][x], cell * .55)
        for i, w in enumerate(sorted(words)):
            col, row = i % 3, i // 3
            sh.text(30 + col * 52, 204 + row * 11, w.lower(), 7, "start")
            if not ans: sh.raw(f'<rect class="ans" x="{22 + col * 52}" y="{198 + row * 11}" width="6" height="6" rx="1"/>')
        return sh
    write(OUT, slug, page(False), {"category": cat, "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 20, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            "Kies een woord uit het lijstje onderaan.",
            "Zoek de eerste letter in het rooster en kijk of de rest erachter staat: " + ("van links naar rechts of van boven naar beneden." if len(dirs) == 2 else "naar rechts, naar beneden of schuin."),
            "Gevonden? Zet een rondje om het woord en vink het af in het lijstje. Op het antwoordblad zie je waar alles staat."]}}},
        [("antwoorden", "Antwoorden", page(True))])
H, V, D = (1, 0), (0, 1), (1, 1)
woordzoeker("woordzoeker-dieren", "Woordzoeker: dieren", ["KAT", "HOND", "KOE", "PAARD", "VIS", "UIL", "BEER", "SCHAAP", "KONIJN", "EEND", "MUIS", "GEIT"], 10, [H, V], "6-9", 1, 11, "dieren")
woordzoeker("woordzoeker-eten", "Woordzoeker: lekker eten", ["APPEL", "BROOD", "KAAS", "PEER", "SOEP", "TAART", "PASTA", "MELK", "BANAAN", "WORTEL", "PIZZA", "RIJST"], 11, [H, V], "6-9", 2, 12, "eten")
woordzoeker("woordzoeker-vervoer", "Woordzoeker: vervoer", ["AUTO", "BUS", "TREIN", "FIETS", "BOOT", "TRAM", "STEP", "RAKET", "METRO", "TAXI", "KANO", "TRACTOR"], 11, [H, V], "6-9", 2, 13, "voertuigen")
woordzoeker("woordzoeker-sport", "Woordzoeker: sport", ["VOETBAL", "HOCKEY", "TENNIS", "JUDO", "ZWEMMEN", "TURNEN", "DANSEN", "SCHAATSEN", "KORFBAL", "ROEIEN", "GOLF", "RUGBY"], 12, [H, V, D], "9+", 3, 14, "sport")

# ---------- breuken kleuren ----------
def breuken():
    sh = Sheet(); title(sh, "Breuken kleuren", 16)
    sh.text(100, 27, "Kleur het stuk dat erbij staat. Er zijn soms meer goede manieren!", 6)
    tasks = [("1/2", "circ", 2), ("1/4", "circ", 4), ("3/4", "circ", 4), ("1/3", "rect", 3), ("2/3", "rect", 3), ("2/4", "rect", 4), ("1/8", "circ", 8), ("5/8", "circ", 8), ("3/6", "rect", 6)]
    for i, (lab, kind, n) in enumerate(tasks):
        col, row = i % 3, i // 3
        cx, cy = 38 + col * 62, 72 + row * 70
        num, den = lab.split("/")
        sh.text(cx - 26, cy - 30, num, 9, "start"); sh.seg(cx - 28, cy - 27, cx - 18, cy - 27); sh.text(cx - 26, cy - 18, den, 9, "start")
        if kind == "circ":
            for k in range(n): sh.region(arc_path(cx + 4, cy, 0.01, 22, k * 360 / n - 90, (k + 1) * 360 / n - 90), "y")
        else:
            w = 50 / n
            for k in range(n): sh.rect_r(cx - 21 + k * w, cy - 14, w, 28, "y")
    sh.text(100, 268, "Tip: 2/4 is net zoveel als 1/2. Zie je dat?", 6)
    write(OUT, "breuken-kleuren", sh, {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 2, "minutes": 15,
        "materials": [{"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": "Breuken kleuren", "steps": [
            "Kijk naar het onderste getal: in zoveel gelijke stukken is de vorm verdeeld.",
            "Het bovenste getal zegt hoeveel stukken je kleurt. Bij 3/4 kleur je 3 van de 4 stukken.",
            "Controleer: tel de gekleurde stukken en de stukken in totaal."]}}})
breuken()

# ---------- geld tellen ----------
def geld():
    coins = {"5c": (5, 9), "10c": (10, 9.5), "20c": (20, 10), "50c": (50, 11), "€1": (100, 11.5), "€2": (200, 12.5)}
    r = random.Random(77)
    rows = []
    for i in range(6):
        k = r.randint(2, 4)
        pick = [r.choice(list(coins)) for _ in range(k)]
        rows.append(sorted(pick, key=lambda c: -coins[c][0]))
    def fmt(c):
        return f"€ {c // 100},{c % 100:02d}"
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Geld tellen", 16)
        if not ans: sh.text(100, 27, "Tel de munten bij elkaar op. Hoeveel geld is het?", 6.5)
        for i, row in enumerate(rows):
            y = 52 + i * 34; x = 22
            for c in row:
                rr = coins[c][1]; sh.circle_r(x + rr, y, rr, "y" if c in ("5c", "10c", "20c", "50c") else "z")
                sh.circle_line(x + rr, y, rr - 1.8); sh.text(x + rr, y + 2.2, c, 6 if len(c) < 3 else 5.5)
                x += 2 * rr + 6
            sh.text(150, y + 3, "=", 10)
            sh.raw(f'<rect class="ans" x="158" y="{y - 9}" width="36" height="16" rx="2"/>')
            if ans: sh.text(176, y + 3, fmt(sum(coins[c][0] for c in row)), 8)
        return sh
    write(OUT, "geld-tellen-munten", page(False), {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 2, "minutes": 15, "materials": POTLOOD,
        "i18n": {"nl": {"name": "Geld tellen met munten", "steps": [
            "Begin bij de grootste munt en tel de andere erbij op.",
            "100 cent is 1 euro. Heb je meer dan 100 cent? Schrijf het als euro's en centen, zoals € 1,25.",
            "Kijk na met het antwoordblad. Leuk om daarna met echte munten na te spelen!"]}}},
        [("antwoorden", "Antwoorden", page(True))])
geld()

# ---------- schaduw zoeken ----------
def schaduw():
    shapes_ = [("hart", lambda x, y: heart_path(x, y, 16)), ("ster", lambda x, y: star_path(x, y, 18, 8)), ("maan", lambda x, y: moon_path(x, y, 16)),
               ("vis", lambda x, y: fish_path(x - 2, y, 14)), ("wolk", lambda x, y: cloud_path(x, y + 4, 12)), ("blad", lambda x, y: leaf_path(x, y, 12, 18))]
    order = [3, 0, 5, 1, 4, 2]
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Welke schaduw hoort erbij?", 15)
        if not ans: sh.text(100, 27, "Trek een lijn van elk plaatje naar zijn schaduw.", 6.5)
        for i, (_, d) in enumerate(shapes_):
            y = 52 + i * 36
            sh.region(d(46, y), "y" if i % 2 else "o"); sh.dot(74, y, 2.4)
            j = order.index(i); y2 = 52 + j * 36
            if ans: sh.seg(74, y, 126, y2, "l", "stroke-width:1.4")
        for j, i in enumerate(order):
            y = 52 + j * 36
            sh.raw(f'<path class="r" d="{shapes_[i][1](154, y)}" style="fill:#222"/>', "x"); sh.dot(126, y, 2.4)
        return sh
    write(OUT, "schaduw-zoeken-vormen", page(False), {"category": "vormen", "age": "2-4", "kind": "werkblad", "difficulty": 1, "minutes": 5,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": "Schaduw zoeken: vormen", "steps": [
            "Kijk naar het plaatje links. Welke zwarte vorm rechts heeft precies dezelfde vorm?",
            "Trek een lijn van het stipje bij het plaatje naar het stipje bij de schaduw.",
            "Klaar? Kleur de plaatjes links in."]}}}, [("antwoorden", "Antwoorden", page(True))])
schaduw()

# ---------- patronen afmaken ----------
def patronen():
    def shp(sh, kind, x, y, s=8):
        if kind == "C": sh.circle_r(x, y, s, "r")
        elif kind == "S": sh.rect_r(x - s, y - s, 2 * s, 2 * s, "b")
        elif kind == "T": sh.poly_r([(x, y - s), (x + s, y + s * .8), (x - s, y + s * .8)], "y")
        elif kind == "H": sh.region(heart_path(x, y, s * .9), "m")
        elif kind == "c": sh.circle_r(x, y, s * .55, "r")
        elif kind == "R": sh.poly_r(star_pts(x, y, s * 1.1, s * .5), "g")
    rows = ["CSCSCSCS", "CCSCCSCC", "CSTCSTCS", "HHTTHHTT", "CcCcCcCc", "RCSRCSRC", "TSSTSSTS"]
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Maak het patroon af", 16)
        if not ans: sh.text(100, 27, "Kijk goed hoe het rijtje gaat. Teken de laatste twee vormen zelf.", 6.5)
        for i, row in enumerate(rows):
            y = 50 + i * 30
            for k, kind in enumerate(row):
                x = 22 + k * 22
                if k >= 6:
                    sh.raw(f'<rect class="ans" x="{x - 10}" y="{y - 10}" width="20" height="20" rx="3"/>')
                    if not ans: continue
                shp(sh, kind, x, y)
        return sh
    write(OUT, "patronen-afmaken", page(False), {"category": "vormen", "age": "4-6", "kind": "werkblad", "difficulty": 1, "minutes": 10,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": "Patronen afmaken", "steps": [
            "Zeg het rijtje hardop: rondje, vierkant, rondje, vierkant …",
            "Welke vorm komt er daarna? Teken hem in het lege hokje, en daarna nog één.",
            "Kleur je vormen in dezelfde kleur als de rest van het rijtje."]}}}, [("antwoorden", "Antwoorden", page(True))])
patronen()

# ---------- dobbelspel: teken een monster ----------
def monster():
    sh = Sheet(); title(sh, "Dobbel een monster", 16)
    sh.text(100, 27, "Gooi voor elk onderdeel en teken wat erbij hoort.", 6.5)
    parts = ["lijf", "ogen", "mond", "armen", "benen", "extra"]
    xs = [44 + k * 26 for k in range(6)]
    for k in range(6):
        sh.rect_line(xs[k] - 12, 34, 24, 12, "l", 2, "stroke-width:.6")
        for p in range(k + 1):
            pass
        sh.text(xs[k], 42.5, str(k + 1), 7)
    def pip(x, y, n):
        sh.rect_line(x - 6, y - 6, 12, 12, "l", 2, "stroke-width:.8")
        pos = {1: [(0, 0)], 2: [(-3, -3), (3, 3)], 3: [(-3, -3), (0, 0), (3, 3)], 4: [(-3, -3), (3, -3), (-3, 3), (3, 3)], 5: [(-3, -3), (3, -3), (0, 0), (-3, 3), (3, 3)], 6: [(-3, -3), (3, -3), (-3, 0), (3, 0), (-3, 3), (3, 3)]}
        for dx, dy in pos[n]: sh.dot(x + dx, y + dy, 1.1)
    for k in range(6): sh.raw(""); 
    # rijen per onderdeel
    for r_, part in enumerate(parts):
        y = 60 + r_ * 22
        sh.text(14, y + 2, part, 6.5, "start")
        for k in range(6):
            x = xs[k]
            if part == "lijf":
                [lambda: sh.circle_line(x, y, 8), lambda: sh.rect_line(x - 8, y - 8, 16, 16, "l", 2), lambda: sh.line(f"M{x} {y - 9}L{x + 9} {y + 8}H{x - 9}Z"),
                 lambda: sh.line(f"M{x - 9} {y}Q{x} {y - 14} {x + 9} {y}Q{x} {y + 14} {x - 9} {y}Z"), lambda: sh.line(star_path(x, y, 9, 4)), lambda: sh.line(cloud_path(x, y + 2, 6))][k]()
            elif part == "ogen":
                for e in range(k + 1):
                    ex = x - 8 + (16 / (k + 1)) * (e + .5); sh.circle_line(ex, y, 2.2); sh.dot(ex, y, .8)
            elif part == "mond":
                [lambda: sh.line(f"M{x - 6} {y - 2}Q{x} {y + 5} {x + 6} {y - 2}"), lambda: sh.line(f"M{x - 6} {y}H{x + 6}"), lambda: sh.circle_line(x, y, 3),
                 lambda: sh.line(f"M{x - 7} {y - 2}L{x - 4} {y + 2}L{x - 1} {y - 2}L{x + 2} {y + 2}L{x + 5} {y - 2}"), lambda: sh.line(f"M{x - 6} {y + 3}Q{x} {y - 4} {x + 6} {y + 3}"),
                 lambda: sh.line(f"M{x - 6} {y - 2}H{x + 6}M{x - 3} {y - 2}V{y + 3}M{x + 3} {y - 2}V{y + 3}")][k]()
            elif part == "armen":
                [lambda: sh.line(f"M{x - 9} {y}H{x + 9}"), lambda: sh.line(f"M{x - 9} {y - 6}L{x} {y}L{x + 9} {y - 6}"), lambda: sh.line(f"M{x - 9} {y + 4}Q{x - 4} {y - 8} {x} {y}Q{x + 4} {y - 8} {x + 9} {y + 4}"),
                 lambda: sh.line(f"M{x - 9} {y}H{x + 9}M{x - 9} {y + 5}H{x + 9}"), lambda: sh.line(f"M{x - 9} {y - 7}V{y + 7}M{x + 9} {y - 7}V{y + 7}"), lambda: sh.circle_line(x, y, 2)][k]()
            elif part == "benen":
                for e in range(k if k < 5 else 8):
                    n_ = k if k < 5 else 8
                    if n_ == 0: break
                    lx = x - 8 + (16 / n_) * (e + .5); sh.seg(lx, y - 6, lx, y + 6)
                if k == 0: sh.line(f"M{x - 8} {y + 4}Q{x} {y - 6} {x + 8} {y + 4}")
            else:
                [lambda: sh.line(f"M{x - 4} {y - 2}L{x - 7} {y - 9}M{x + 4} {y - 2}L{x + 7} {y - 9}"), lambda: sh.line(f"M{x - 6} {y + 6}Q{x - 8} {y - 6} {x} {y - 8}Q{x + 8} {y - 6} {x + 6} {y + 6}"),
                 lambda: sh.line(f"M{x - 8} {y + 6}L{x - 4} {y - 6}L{x} {y + 6}L{x + 4} {y - 6}L{x + 8} {y + 6}"), lambda: sh.line(f"M{x - 8} {y}Q{x - 4} {y - 6} {x} {y}T{x + 8} {y}"),
                 lambda: sh.line(f"M{x - 6} {y + 6}V{y - 4}H{x + 6}V{y + 6}M{x - 8} {y - 4}H{x + 8}"), lambda: sh.line(f"M{x - 8} {y + 6}Q{x} {y - 12} {x + 8} {y + 6}")][k]()
    sh.text(100, 196, "Mijn monster heet: ...............................", 7)
    sh.rect_line(20, 202, 160, 70, "l", 4, "stroke-width:.8")
    write(OUT, "dobbelspel-teken-een-monster", sh, {"category": "sprookjes", "age": "4-6", "kind": "spel", "difficulty": 1, "minutes": 15,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": "Dobbelspel: teken een monster", "printNote": "Je hebt ook een dobbelsteen nodig.", "steps": [
            "Gooi de dobbelsteen. Het getal zegt welk lijf je monster krijgt (kijk in de rij lijf).",
            "Teken het lijf groot in het vak onderaan.",
            "Gooi opnieuw voor de ogen, de mond, de armen, de benen en iets extra's, en teken ze erbij.",
            "Geef je monster een naam en kleur het in. Speel je met z'n tweeën? Vergelijk jullie monsters!"]}}})
monster()
