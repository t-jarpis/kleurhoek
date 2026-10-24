"""Woordzoeker (gedeeld)."""
import math, random
from lib_gen import *

# ---------- woordzoekers ----------
def woordzoeker(slug, name, words, n, dirs, age, diff, seed, cat, _try=0):
    assert not any(a != b and a in b for a in words for b in words), "woord zit in een ander woord"
    r = random.Random(seed * 1000 + _try)
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
    if any(count(w) != 1 for w in words):
        assert _try < 300, slug
        return woordzoeker(slug, name, words, n, dirs, age, diff, seed, cat, _try + 1)
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
