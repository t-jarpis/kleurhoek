"""Herbruikbare generators voor werkjes (vanaf batch 2). Elke functie schrijft één concept naar OUT."""
import math, os, random
from kit import *

OUT = os.environ.get("OUT", "concepten")
POTLOOD = [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}]
SCHAAR = {"slug": "kinderschaar"}

def cap(s): return s[0].upper() + s[1:]
def star_pts(cx, cy, r1, r2, n=5):
    return [(cx + (r1 if i % 2 == 0 else r2) * math.sin(math.pi * i / n), cy - (r1 if i % 2 == 0 else r2) * math.cos(math.pi * i / n)) for i in range(2 * n)]

# ---------- doolhof ----------
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
        walls[(c, r)].discard(d); walls[(nc, nr)].discard(o); seen.add((nc, nr)); stack.append((nc, nr))
    prev = {(0, 0): None}; q = [(0, 0)]
    for cell in q:
        c, r = cell
        for d, (dx, dy, _) in D.items():
            if d not in walls[cell] and (c + dx, r + dy) not in prev:
                prev[(c + dx, r + dy)] = cell; q.append((c + dx, r + dy))
    path, cur = [], (cols - 1, rows - 1)
    while cur: path.append(cur); cur = prev[cur]
    return walls, path[::-1]

def doolhof(slug, name, heading, cols, rows, age, diff, seed, start, finish, cat, start_word, finish_word):
    """start/finish: functies (sheet, x, y) die een figuurtje tekenen."""
    walls, path = maze(cols, rows, seed)
    s = min(160 / cols, 190 / rows); x0 = (W - cols * s) / 2; y0 = 56
    def page(answer):
        sh = Sheet()
        title(sh, "Antwoorden: zo kom je er" if answer else heading, 18)
        start(sh, x0 + 8, y0 - 14)
        finish(sh, x0 + cols * s - 8, y0 + rows * s + 16)
        d = []
        for (c, r), w in walls.items():
            x, y = x0 + c * s, y0 + r * s
            if "N" in w and not (c == 0 and r == 0): d.append(f"M{f(x)} {f(y)}H{f(x + s)}")
            if "W" in w: d.append(f"M{f(x)} {f(y)}V{f(y + s)}")
            if "S" in w and not (c == cols - 1 and r == rows - 1): d.append(f"M{f(x)} {f(y + s)}H{f(x + s)}")
            if "E" in w: d.append(f"M{f(x + s)} {f(y)}V{f(y + s)}")
        sh.line("".join(d))
        if answer:
            pd = f"M{f(x0 + s / 2)} {f(y0 - s / 2)}" + "".join(f"L{f(x0 + c * s + s / 2)} {f(y0 + r * s + s / 2)}" for c, r in path) + f"L{f(x0 + (cols - .5) * s)} {f(y0 + rows * s + s / 2)}"
            sh.line(pd, "l", "stroke-width:2.2;stroke-dasharray:.1 3.2;stroke-linecap:round")
        return sh
    write(OUT, slug, page(False), {
        "category": cat, "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 5 + diff * 5, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            f"Zet je potlood bij {start_word} bovenaan.",
            f"Zoek de weg door het doolhof naar {finish_word} onderaan, zonder door een muur te gaan.",
            "Klaar? Kleur de tekeningetjes in. Het antwoord staat op het antwoordblad."]}},
    }, [("antwoorden", "Antwoorden", page(True))])

# ---------- verbind de punten ----------
def dots_sheet(slug, name, points, age, diff, extra, word, cat, minutes=10):
    cx = sum(x for x, _ in points) / len(points); cy = sum(y for _, y in points) / len(points)
    def page(answer):
        sh = Sheet()
        title(sh, "Antwoord" if answer else f"Verbind de punten van 1 tot {len(points)}", 18)
        extra(sh)
        if answer: sh.line("M" + " L".join(f"{f(x)} {f(y)}" for x, y in points) + "Z")
        for i, (x, y) in enumerate(points):
            sh.dot(x, y, 1.5)
            dx, dy = x - cx, y - cy; d = math.hypot(dx, dy) or 1
            sh.text(x + dx / d * 7, y + dy / d * 7 + 2.2, str(i + 1), 6.5)
        sh.text(100, 268, "Wat is het? " + ((("Een " + word) if not word[0].isupper() else word) + "!" if answer else "........................"), 8)
        return sh
    write(OUT, slug, page(False), {
        "category": cat, "age": age, "kind": "werkblad", "difficulty": diff, "minutes": minutes, "materials": POTLOOD,
        "i18n": {"nl": {"name": f"{name} (1 tot {len(points)})", "steps": [
            "Begin bij punt 1 en trek een lijn naar 2, dan naar 3, en zo verder.",
            "Ga van het laatste punt terug naar 1.",
            "Kleur de tekening en schrijf op wat het is. Het antwoord staat op het antwoordblad."]}},
    }, [("antwoorden", "Antwoord", page(True))])

def outline_points(segments, spacing):
    """Punten op gelijke afstand langs een open of gesloten veelhoek (lijst punten)."""
    pts, total = [], 0
    poly = segments + [segments[0]]
    lens = [math.dist(poly[i], poly[i + 1]) for i in range(len(poly) - 1)]
    L = sum(lens); n = max(6, round(L / spacing)); step = L / n
    for k in range(n):
        t = k * step; i = 0
        while t > lens[i]: t -= lens[i]; i += 1
        a, b = poly[i], poly[i + 1]; u = t / lens[i] if lens[i] else 0
        pts.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return pts

# ---------- rekenen ----------
def sums_sheet(slug, name, items, age, diff, intro, steps, cat="leren", box_w=24, eq=" =", after=None):
    def page(answer):
        sh = Sheet()
        t = cap(name.split(": ", 1)[-1])
        at = "Antwoorden: " + t[0].lower() + t[1:]
        title(sh, (at if len(at) <= 32 else "Antwoorden") if answer else t, 18)
        sh.text(100, 30, intro, 6.5)
        for i, (q, a) in enumerate(items):
            col, row = i % 2, i // 2
            x, y = 18 + col * 92, 52 + row * 30
            bx = x + (30 if after else 54)
            sh.text(x, y + 9, q + eq, 10, "start")
            sh.raw(f'<rect class="ans" x="{bx}" y="{y - 1}" width="{box_w}" height="14" rx="2"/>')
            if after: sh.text(bx + box_w + 4, y + 9, after, 10, "start")
            if answer: sh.text(bx + box_w / 2, y + 9.5, str(a), 10)
        sh.poly_r(star_pts(100, 250, 14, 6), "y")
        sh.text(100, 274, "Alles af? Kleur de ster!", 6.5)
        return sh
    write(OUT, slug, page(False), {
        "category": cat, "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 10, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": name, "steps": steps + ["Kijk samen na met het antwoordblad."]}},
    }, [("antwoorden", "Antwoorden", page(True))])

# ---------- schrijven ----------
def letters(slug, name, chars, age="4-6", intro="Trek de stippellijntjes over en schrijf daarna zelf."):
    sh = Sheet()
    title(sh, cap(name.split(": ", 1)[-1]), 18)
    sh.text(100, 29, intro, 6.5)
    y = 44; step = min(44, 222 / len(chars))
    for ch in chars:
        sh.line(f"M14 {y + 22}H186", "guide"); sh.line(f"M14 {y + 6}H186", "guide", "stroke-dasharray:3 3"); sh.line(f"M14 {y + 14}H186", "guide", "stroke-dasharray:3 3")
        sh.text(26, y + 22, ch, 22, "middle", "tx")
        for i in range(5): sh.text(58 + i * 28, y + 22, ch, 22, "middle", "trace")
        y += step
    write(OUT, slug, sh, {
        "category": "leren", "age": age, "kind": "werkblad", "difficulty": 1, "minutes": 10, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": name, "steps": [
            "Kijk naar het voorbeeld vooraan in de rij.",
            "Trek de stippellijntjes over met je potlood.",
            "Probeer het daarna zelf op de lijn te schrijven."]}},
    })

# ---------- mandala ----------
def mandala(slug, name, rings, age="12+", diff=3, cat="patronen", holiday=None):
    sh = Sheet(200)
    cx, cy = 100, 100
    for kind, r1, r2, n, colors, *rest in rings:
        rot = rest[0] if rest else 0
        for i in range(n):
            a1, a2 = i * 360 / n - 90 + rot, (i + 1) * 360 / n - 90 + rot
            code = colors[i % len(colors)]
            if kind == "seg" and n == 1 and r1 == 0: sh.circle_r(cx, cy, r2, code)
            elif kind == "seg": sh.region(arc_path(cx, cy, r1, r2, a1, a2), code)
            elif kind == "petal":
                am = math.radians((a1 + a2) / 2); w = math.radians((a2 - a1) / 2)
                p0 = (cx + r1 * math.cos(am), cy + r1 * math.sin(am)); p2 = (cx + r2 * math.cos(am), cy + r2 * math.sin(am))
                R = (r1 + r2) / 2 / math.cos(w * .9)
                c1 = (cx + R * math.cos(am - w * .9), cy + R * math.sin(am - w * .9)); c2 = (cx + R * math.cos(am + w * .9), cy + R * math.sin(am + w * .9))
                sh.region(f"M{f(p0[0])} {f(p0[1])}Q{f(c1[0])} {f(c1[1])} {f(p2[0])} {f(p2[1])}Q{f(c2[0])} {f(c2[1])} {f(p0[0])} {f(p0[1])}Z", code)
            elif kind == "dot":
                am = math.radians((a1 + a2) / 2); rr = (r1 + r2) / 2
                sh.circle_r(cx + rr * math.cos(am), cy + rr * math.sin(am), (r2 - r1) / 2, code)
            elif kind == "tri":
                am1, am2, amm = math.radians(a1), math.radians(a2), math.radians((a1 + a2) / 2)
                sh.poly_r([(cx + r1 * math.cos(am1), cy + r1 * math.sin(am1)), (cx + r2 * math.cos(amm), cy + r2 * math.sin(amm)), (cx + r1 * math.cos(am2), cy + r1 * math.sin(am2))], code)
            elif kind == "heart":
                am = math.radians((a1 + a2) / 2); rr = (r1 + r2) / 2; k = (r2 - r1) / 18
                hx, hy = cx + rr * math.cos(am), cy + rr * math.sin(am); deg = math.degrees(am) - 90
                sh.raw(f'<path class="r" transform="rotate({f(deg)} {f(hx)} {f(hy)})" d="M{f(hx)} {f(hy + 9*k)}C{f(hx - 13*k)} {f(hy)} {f(hx - 9*k)} {f(hy - 10*k)} {f(hx)} {f(hy - 4*k)}C{f(hx + 9*k)} {f(hy - 10*k)} {f(hx + 13*k)} {f(hy)} {f(hx)} {f(hy + 9*k)}Z"/>', code)
    meta = {"category": cat, "age": age, "kind": "kleurplaat", "difficulty": diff,
            "materials": [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}], "i18n": {"nl": {"name": name}}}
    if holiday: meta["holiday"] = holiday
    write(OUT, slug, sh, meta)

# ---------- patroon (tegels) ----------
def tiling(slug, name, kind, age, diff, colors, cat="patronen"):
    sh = Sheet(200)
    if kind == "zeshoek":
        r = 12; h = r * math.sqrt(3)
        for row in range(-1, 11):
            for col in range(-1, 10):
                cx = col * r * 1.5 + 8; cy = row * h + (h / 2 if col % 2 else 0) + 6
                p = [(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k))) for k in range(6)]
                if all(-1 <= x <= 201 and -1 <= y <= 201 for x, y in p):
                    sh.poly_r(p, colors[(row + col) % len(colors)])
    elif kind == "driehoek":
        s = 25; h = s * math.sqrt(3) / 2
        for row in range(int(200 / h)):
            for k in range(-1, 18):
                x = k * s / 2; y = row * h
                up = (k + row) % 2 == 0
                p = [(x, y + h), (x + s / 2, y), (x + s, y + h)] if up else [(x, y), (x + s, y), (x + s / 2, y + h)]
                if all(-0.5 <= px <= 200.5 for px, _ in p):
                    sh.poly_r(p, colors[(k + 2 * row) % len(colors)])
    elif kind == "sterren":
        for row in range(7):
            for col in range(6):
                cx = 18 + col * 33 + (16 if row % 2 else 0); cy = 16 + row * 28
                if cx + 13 > 200: continue
                sh.poly_r(star_pts(cx, cy, 13, 5.5), colors[(row + col) % len(colors)])
                if col < 5 and cx + 33 + 13 <= 200: sh.circle_r(cx + 16.5, cy + 2, 3.2, colors[(row + col + 1) % len(colors)])
    elif kind == "ruit":
        s = 22
        for row in range(-1, 20):
            for col in range(-1, 10):
                cx = col * s + (s / 2 if row % 2 else 0) + 6; cy = row * s / 2 + 6
                p = [(cx, cy - s / 2), (cx + s / 2, cy), (cx, cy + s / 2), (cx - s / 2, cy)]
                if all(-0.5 <= x <= 200.5 and -0.5 <= y <= 200.5 for x, y in p):
                    sh.poly_r(p, colors[(row + col) % len(colors)])
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "kleurplaat", "difficulty": diff,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}], "i18n": {"nl": {"name": name}}})

# ---------- kaart ----------
def card(slug, name, front, back_text, cat, age, steps_extra, holiday=None, minutes=20):
    sh = Sheet()
    x0, y0, w, h = 14, 12, 172, 250
    sh.rect_line(x0, y0, w, h, "cut", 3)
    mid = y0 + h / 2
    sh.seg(x0, mid, x0 + w, mid, "fold")
    sh.raw(f'<g transform="rotate(180 100 {f(y0 + h / 4)})">')
    sh.text(100, y0 + h / 4 - 8, back_text, 7)
    sh.text(100, y0 + h / 4 + 8, "Gemaakt door: ...........................", 7)
    sh.raw('</g>')
    front(sh, x0, mid, w, h / 2)
    sh.legend(["cut", "fold"], 276)
    meta = {"category": cat, "age": age, "kind": "kaart", "difficulty": 1, "minutes": minutes, "paperGsm": 160,
            "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "stiften", "optional": True}, {"slug": "stevig-papier", "optional": True}],
            "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier (160 gram) als je het hebt; gewoon papier kan ook.", "steps": [
                "Kleur de voorkant (de onderste helft) mooi in.",
                "Knip de kaart uit langs de streepjeslijn.",
                "Vouw hem dubbel op de stippellijn, met de tekening aan de buitenkant. De kaart staat dan rechtop met de vouw bovenaan.",
            ] + steps_extra}}}
    if holiday: meta["holiday"] = holiday
    write(OUT, slug, sh, meta)

def outline_text(sh, x, y, s, size):
    sh.raw(f'<text class="l" style="stroke-width:1.1" x="{f(float(x))}" y="{f(float(y))}" font-size="{size}" text-anchor="middle" font-weight="800">{s}</text>')
