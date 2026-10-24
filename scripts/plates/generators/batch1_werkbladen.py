import os
import math, random
from kit import *

OUT = os.environ.get("OUT", "concepten/batch1")
POTLOOD = [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}]

# ---------- Doolhoven ----------
def maze(cols, rows, seed):
    rnd = random.Random(seed)
    walls = {(c, r): {"N", "S", "E", "W"} for c in range(cols) for r in range(rows)}
    seen = {(0, 0)}; stack = [(0, 0)]
    D = {"N": (0, -1, "S"), "S": (0, 1, "N"), "E": (1, 0, "W"), "W": (-1, 0, "E")}
    while stack:
        c, r = stack[-1]
        opts = [(d, c + dx, r + dy, o) for d, (dx, dy, o) in D.items() if 0 <= c + dx < cols and 0 <= r + dy < rows and (c + dx, r + dy) not in seen]
        if not opts: stack.pop(); continue
        d, nc, nr, o = rnd.choice(opts)
        walls[(c, r)].discard(d); walls[(nc, nr)].discard(o)
        seen.add((nc, nr)); stack.append((nc, nr))
    # pad van start (0,0) naar eind (cols-1, rows-1) via BFS
    prev = {(0, 0): None}; q = [(0, 0)]
    for cell in q:
        c, r = cell
        for d, (dx, dy, _) in D.items():
            if d not in walls[cell] and (c + dx, r + dy) not in prev:
                prev[(c + dx, r + dy)] = cell; q.append((c + dx, r + dy))
    path, cur = [], (cols - 1, rows - 1)
    while cur: path.append(cur); cur = prev[cur]
    return walls, path[::-1]

def draw_maze(sh, walls, cols, rows, x0, y0, s, path=None):
    d = []
    for (c, r), w in walls.items():
        x, y = x0 + c * s, y0 + r * s
        if "N" in w and not (c == 0 and r == 0): d.append(f"M{f(x)} {f(y)}H{f(x + s)}")
        if "W" in w: d.append(f"M{f(x)} {f(y)}V{f(y + s)}")
        if "S" in w and not (c == cols - 1 and r == rows - 1): d.append(f"M{f(x)} {f(y + s)}H{f(x + s)}")
        if "E" in w: d.append(f"M{f(x + s)} {f(y)}V{f(y + s)}")
    sh.line("".join(d))
    if path:
        pd = f"M{f(x0 + s / 2)} {f(y0 - s / 2)}" + "".join(f"L{f(x0 + c * s + s / 2)} {f(y0 + r * s + s / 2)}" for c, r in path) + f"L{f(x0 + (cols - .5) * s)} {f(y0 + rows * s + s / 2)}"
        sh.line(pd, "l", "stroke-width:2.2;stroke-dasharray:.1 3.2;stroke-linecap:round")

def egel(sh, x, y, k=1):
    # stekelig lijf (halve ellips met punten), kopje rechtsvoor
    pts_ = []
    for i in range(15):
        a = math.pi + i * math.pi / 14
        r = 1 if i % 2 == 0 else 1.32
        pts_.append((x + 9 * k * r * math.cos(a), y + 2 * k + 9.5 * k * r * math.sin(a)))
    sh.poly_r(pts_, "w")
    sh.region(f"M{f(x + 4*k)} {f(y + 2*k)}Q{f(x + 9*k)} {f(y - 4*k)} {f(x + 14*k)} {f(y + 1*k)}Q{f(x + 10*k)} {f(y + 3.5*k)} {f(x + 4*k)} {f(y + 2*k)}Z", "o")
    sh.dot(x + 14 * k, y + 1 * k, .9 * k); sh.dot(x + 9 * k, y - .5 * k, .6 * k)

def appel(sh, x, y, k=1):
    sh.region(f"M{f(x)} {f(y - 5*k)}C{f(x - 9*k)} {f(y - 10*k)} {f(x - 10*k)} {f(y + 4*k)} {f(x - 3*k)} {f(y + 8*k)}Q{f(x)} {f(y + 9*k)} {f(x + 3*k)} {f(y + 8*k)}C{f(x + 10*k)} {f(y + 4*k)} {f(x + 9*k)} {f(y - 10*k)} {f(x)} {f(y - 5*k)}Z", "r")
    sh.region(f"M{f(x)} {f(y - 5*k)}Q{f(x + 3*k)} {f(y - 11*k)} {f(x + 8*k)} {f(y - 10*k)}Q{f(x + 5*k)} {f(y - 5*k)} {f(x)} {f(y - 5*k)}Z", "g")

def doolhof(slug, name, cols, rows, age, diff, seed):
    walls, path = maze(cols, rows, seed)
    s = min(160 / cols, 196 / rows); x0 = (W - cols * s) / 2; y0 = 52
    def page(answer):
        sh = Sheet()
        title(sh, "Antwoorden: zo kom je er" if answer else "Help de egel naar de appel", 18)
        egel(sh, x0 + 6, y0 - 12, 1.6)
        appel(sh, x0 + cols * s - 8, y0 + rows * s + 16, 1.5)
        draw_maze(sh, walls, cols, rows, x0, y0, s, path if answer else None)
        return sh
    main, ans = page(False), page(True)
    write(OUT, slug, main, {
        "category": "dieren", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 5 + diff * 5,
        "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            "Zet je potlood bij de egel bovenaan.",
            "Zoek de weg door het doolhof naar de appel onderaan, zonder door een muur te gaan.",
            "Klaar? Kleur de egel en de appel. Het antwoord staat op het antwoordblad."]}},
    }, [("antwoorden", "Antwoorden", ans)])

doolhof("doolhof-egel-makkelijk", "Doolhof: egel zoekt appel (makkelijk)", 6, 7, "4-6", 1, 11)
doolhof("doolhof-egel-gemiddeld", "Doolhof: egel zoekt appel (gemiddeld)", 10, 12, "6-9", 2, 22)
doolhof("doolhof-egel-moeilijk", "Doolhof: egel zoekt appel (uitdagend)", 16, 19, "9+", 3, 33)

# ---------- Verbind de punten ----------
def star_pts(cx, cy, r1, r2, n=5):
    return [(cx + (r1 if i % 2 == 0 else r2) * math.sin(math.pi * i / n), cy - (r1 if i % 2 == 0 else r2) * math.cos(math.pi * i / n)) for i in range(2 * n)]

def dots_sheet(slug, name, points, age, diff, extra, word, cat):
    cx = sum(x for x, _ in points) / len(points); cy = sum(y for _, y in points) / len(points)
    def page(answer):
        sh = Sheet()
        title(sh, "Antwoord" if answer else f"Verbind de punten van 1 tot {len(points)}", 18)
        extra(sh)
        if answer:
            sh.line("M" + " L".join(f"{f(x)} {f(y)}" for x, y in points) + "Z")
        for i, (x, y) in enumerate(points):
            sh.dot(x, y, 1.5)
            dx, dy = x - cx, y - cy; d = math.hypot(dx, dy) or 1
            sh.text(x + dx / d * 7, y + dy / d * 7 + 2.2, str(i + 1), 6.5)
        sh.text(100, 268, "Wat is het? " + ("Een " + word + "!" if answer else "........................"), 8)
        return sh
    write(OUT, slug, page(False), {
        "category": cat, "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 10,
        "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            "Begin bij punt 1 en trek een lijn naar 2, dan naar 3, en zo verder.",
            "Ga van het laatste punt terug naar 1.",
            "Kleur de tekening en schrijf op wat het is. Het antwoord staat op het antwoordblad."]}},
    }, [("antwoorden", "Antwoord", page(True))])

def ster_extra(sh):
    for x, y in [(28, 40), (172, 40), (24, 250), (176, 250)]:
        sh.poly_r(star_pts(x, y, 6, 2.6), "y")
dots_sheet("verbind-de-punten-ster", "Verbind de punten: ster (1 tot 10)", star_pts(100, 145, 80, 34), "4-6", 1, ster_extra, "ster", "ruimte")

def vis_points():
    pts_ = []
    # lijf (ellips) van de neus links-boven naar de staart, staart, terug onderlangs
    for i in range(0, 9):
        a = math.pi + i * (math.pi / 8)  # bovenkant van links naar rechts
        pts_.append((90 + 55 * math.cos(a), 140 + 36 * math.sin(a)))
    pts_ += [(178, 100), (172, 140), (178, 180)]
    for i in range(1, 8):
        a = 0 + i * (math.pi / 8)
        pts_.append((90 + 55 * math.cos(a), 140 + 36 * math.sin(a)))
    return pts_[:-1] if False else pts_
def vis_extra(sh):
    sh.circle_r(58, 132, 5, "-"); sh.dot(58, 132, 2)
    for i, (x, y, r) in enumerate([(30, 60, 5), (42, 44, 3.5), (52, 32, 2.5)]): sh.circle_r(x, y, r, "b")
    for x in (40, 150):
        sh.region(f"M{x} 250C{x - 8} 235 {x + 8} 225 {x} 205C{x + 12} 222 {x + 6} 238 {x + 6} 250Z", "g")
dots_sheet("verbind-de-punten-vis", "Verbind de punten: vis (1 tot 19)", vis_points(), "6-9", 2, vis_extra, "vis", "zee")

def raket_points():
    p = []
    # neus, rechterkant omlaag, vin, onderkant, linkervin, links omhoog
    p += [(100, 40), (112, 58), (122, 82), (126, 110), (127, 140), (127, 170), (146, 192), (148, 212), (128, 205), (118, 214), (100, 214), (82, 214), (72, 205), (52, 212), (54, 192), (73, 170), (73, 140), (74, 110), (78, 82), (88, 58)]
    # extra punten zodat het 30 wordt: verdeel lange zijden
    out = []
    for i, a in enumerate(p):
        b = p[(i + 1) % len(p)]
        out.append(a)
        if math.dist(a, b) > 36: out.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
    return out
def raket_extra(sh):
    sh.circle_r(100, 112, 11, "b"); sh.circle_line(100, 112, 7)
    for x, y in [(30, 50), (170, 40), (35, 150), (168, 130), (40, 240), (160, 250)]:
        sh.poly_r(star_pts(x, y, 6, 2.6), "y")
rp = raket_points()
dots_sheet(f"verbind-de-punten-raket", f"Verbind de punten: raket (1 tot {len(rp)})", rp, "6-9", 2, raket_extra, "raket", "ruimte")

# ---------- Rekenen ----------
def sums_sheet(slug, name, items, age, diff, intro, steps):
    def page(answer):
        sh = Sheet()
        t = name.split(": ", 1)[-1]; t = t[0].upper() + t[1:]
        title(sh, ("Antwoorden: " + t.lower()) if answer else t, 18)
        sh.text(100, 30, intro, 6.5)
        for i, (q, a) in enumerate(items):
            col, row = i % 2, i // 2
            x, y = 22 + col * 92, 52 + row * 30
            sh.text(x, y + 9, q + " =", 10, "start")
            sh.raw(f'<rect class="ans" x="{x + 52}" y="{y - 1}" width="24" height="14" rx="2"/>')
            if answer: sh.text(x + 64, y + 9.5, str(a), 10)
        # beloning om in te kleuren
        sh.poly_r(star_pts(100, 250, 14, 6), "y")
        sh.text(100, 274, "Alles af? Kleur de ster!", 6.5)
        return sh
    write(OUT, slug, page(False), {
        "category": "leren", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 10,
        "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": name, "steps": steps + ["Kijk samen na met het antwoordblad."]}},
    }, [("antwoorden", "Antwoorden", page(True))])

rnd = random.Random(7)
plus = []
while len(plus) < 12:
    a, b = rnd.randint(1, 9), rnd.randint(1, 9)
    if a + b <= 10 and (f"{a} + {b}", a + b) not in plus: plus.append((f"{a} + {b}", a + b))
sums_sheet("rekenen-optellen-tot-10", "Rekenen: optellen tot 10", plus, "6-9", 1, "Reken uit en schrijf het antwoord in het hokje.", ["Lees de som, bijvoorbeeld 3 + 4.", "Tel uit (op je vingers mag ook) en schrijf het antwoord in het hokje."])
minus = []
while len(minus) < 12:
    a = rnd.randint(8, 20); b = rnd.randint(1, a - 1)
    if (f"{a} − {b}", a - b) not in minus: minus.append((f"{a} − {b}", a - b))
sums_sheet("rekenen-aftrekken-tot-20", "Rekenen: aftrekken tot 20", minus, "6-9", 2, "Haal eraf en schrijf het antwoord in het hokje.", ["Lees de som, bijvoorbeeld 15 − 7.", "Reken uit hoeveel er overblijft en schrijf het antwoord in het hokje."])
tafel = [(f"{n} × 3", n * 3) for n in [3, 7, 1, 10, 5, 8, 2, 6, 9, 4, 0, 11]]
sums_sheet("rekenen-tafel-van-3", "Rekenen: de tafel van 3", tafel, "6-9", 2, "Weet je de tafel van 3? Schrijf het antwoord in het hokje.", ["Zeg de tafel van 3 hardop: 1 × 3 = 3, 2 × 3 = 6 …", "Vul de antwoorden in. Ze staan door elkaar!"])

# ---------- Klokkijken ----------
def clock(sh, cx, cy, r, h, m):
    sh.circle_r(cx, cy, r, "-")
    for i in range(12):
        a = math.radians(i * 30)
        sh.seg(cx + (r - 3) * math.sin(a), cy - (r - 3) * math.cos(a), cx + r * math.sin(a), cy - r * math.cos(a), "l", "stroke-width:1")
        n = 12 if i == 0 else i
        sh.text(cx + (r - 8) * math.sin(a), cy - (r - 8) * math.cos(a) + 2.2, str(n), 6)
    ha = math.radians((h % 12) * 30 + m * .5); ma = math.radians(m * 6)
    sh.seg(cx, cy, cx + r * .5 * math.sin(ha), cy - r * .5 * math.cos(ha), "l", "stroke-width:2.6")
    sh.seg(cx, cy, cx + r * .78 * math.sin(ma), cy - r * .78 * math.cos(ma), "l", "stroke-width:1.6")
    sh.dot(cx, cy, 1.8)

def tijd(h, m):
    return f"{h} uur" if m == 0 else f"half {h % 12 + 1}"

times = [(3, 0), (7, 30), (12, 0), (9, 30), (5, 0), (1, 30)]
def klok_page(answer):
    sh = Sheet()
    title(sh, "Antwoorden" if answer else "Hoe laat is het?", 18)
    sh.text(100, 30, "Hele en halve uren. Schrijf de tijd onder de klok.", 6.5)
    for i, (h, m) in enumerate(times):
        col, row = i % 2, i // 2
        cx, cy = 58 + col * 84, 72 + row * 72
        clock(sh, cx, cy, 26, h, m)
        sh.seg(cx - 26, cy + 42, cx + 26, cy + 42, "guide")
        if answer: sh.text(cx, cy + 40, tijd(h, m), 8)
    return sh
write(OUT, "klokkijken-hele-en-halve-uren", klok_page(False), {
    "category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 2, "minutes": 10,
    "materials": [{"slug": "potlood"}],
    "i18n": {"nl": {"name": "Klokkijken: hele en halve uren", "steps": [
        "De korte wijzer wijst het uur aan, de lange wijzer de minuten.",
        "Staat de lange wijzer op de 12? Dan is het een heel uur, bijvoorbeeld 3 uur.",
        "Staat de lange wijzer op de 6? Dan is het half: half 8 is een half uur vóór 8 uur.",
        "Schrijf de tijd op de lijn onder elke klok en kijk na met het antwoordblad."]}},
}, [("antwoorden", "Antwoorden", klok_page(True))])

# ---------- Tellen ----------
def shape(sh, kind, x, y, s):
    if kind == "ster": sh.poly_r(star_pts(x, y, s, s * .45), "y")
    elif kind == "bal": sh.circle_r(x, y, s * .8, "r")
    elif kind == "hart":
        k = s / 8
        sh.region(f"M{f(x)} {f(y + 7*k)}C{f(x - 10*k)} {f(y)} {f(x - 7*k)} {f(y - 8*k)} {f(x)} {f(y - 3*k)}C{f(x + 7*k)} {f(y - 8*k)} {f(x + 10*k)} {f(y)} {f(x)} {f(y + 7*k)}Z", "m")
    elif kind == "blad":
        sh.region(f"M{f(x - s)} {f(y + s*.6)}Q{f(x - s*.6)} {f(y - s)} {f(x + s)} {f(y - s*.6)}Q{f(x + s*.6)} {f(y + s)} {f(x - s)} {f(y + s*.6)}Z", "g")
counts = [("ster", 3), ("bal", 5), ("hart", 2), ("blad", 6), ("ster", 4), ("bal", 7)]
def tel_page(answer):
    sh = Sheet()
    title(sh, "Antwoorden" if answer else "Tel en schrijf het getal", 18)
    for i, (kind, n) in enumerate(counts):
        col, row = i % 2, i // 2
        bx, by = 18 + col * 86, 32 + row * 78
        sh.rect_line(bx, by, 78, 70, "l", 4, "stroke-width:1.2")
        rnd2 = random.Random(i * 13)
        spots = [(bx + 12 + (j % 3) * 20 + rnd2.uniform(-2, 2), by + 13 + (j // 3) * 19 + rnd2.uniform(-2, 2)) for j in range(n)]
        for x, y in spots: shape(sh, kind, x, y, 6)
        sh.raw(f'<rect class="ans" x="{bx + 52}" y="{by + 50}" width="20" height="14" rx="2"/>')
        if answer: sh.text(bx + 62, by + 60.5, str(n), 10)
    return sh
write(OUT, "tellen-tot-7", tel_page(False), {
    "category": "leren", "age": "4-6", "kind": "werkblad", "difficulty": 1, "minutes": 10,
    "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden"}],
    "i18n": {"nl": {"name": "Tellen tot 7", "steps": [
        "Tel in elk vak hoeveel er zijn. Wijs ze één voor één aan.",
        "Schrijf het getal in het hokje rechtsonder.",
        "Kleur daarna alles in en kijk samen na met het antwoordblad."]}},
}, [("antwoorden", "Antwoorden", tel_page(True))])

# ---------- Letters schrijven ----------
def letters(slug, name, chars):
    sh = Sheet()
    t = name.split(": ", 1)[-1]; title(sh, t[0].upper() + t[1:], 18)
    sh.text(100, 29, "Trek de stippellijntjes over en schrijf de letter daarna zelf.", 6.5)
    y = 44
    for ch in chars:
        sh.line(f"M14 {y + 22}H186", "guide"); sh.line(f"M14 {y + 6}H186", "guide", "stroke-dasharray:3 3"); sh.line(f"M14 {y + 14}H186", "guide", "stroke-dasharray:3 3")
        sh.text(26, y + 22, ch, 22, "middle", "tx")
        for i in range(5):
            sh.text(58 + i * 28, y + 22, ch, 22, "middle", "trace")
        y += 44
    write(OUT, slug, sh, {
        "category": "leren", "age": "4-6", "kind": "werkblad", "difficulty": 1, "minutes": 10,
        "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": name, "steps": [
            "Kijk naar de letter vooraan in de rij.",
            "Trek de stippellijntjes over met je potlood, zonder op te tillen als het kan.",
            "Probeer de letter daarna zelf op de lijn te schrijven."]}},
    })
letters("schrijven-letters-a-tot-e", "Schrijven: de letters a tot en met e", list("abcde"))
letters("schrijven-letters-f-tot-j", "Schrijven: de letters f tot en met j", list("fghij"))
print("werkbladen klaar")
