"""Sudoku (gedeeld)."""
import random
from lib_gen import *

# ---------- sudoku's ----------
def solve(g, n, bh, bw, limit=2):
    sols = [0]
    def ok(r, c, v):
        if v in g[r] or any(g[i][c] == v for i in range(n)): return False
        r0, c0 = r - r % bh, c - c % bw
        return all(g[i][j] != v for i in range(r0, r0 + bh) for j in range(c0, c0 + bw))
    def rec():
        for r in range(n):
            for c in range(n):
                if g[r][c] == 0:
                    for v in range(1, n + 1):
                        if ok(r, c, v):
                            g[r][c] = v; rec(); g[r][c] = 0
                            if sols[0] >= limit: return
                    return
        sols[0] += 1
    rec(); return sols[0]
def make(n, bh, bw, givens, rng):
    base = [[(bw * (r % bh) + r // bh + c) % n + 1 for c in range(n)] for r in range(n)]
    perm = list(range(1, n + 1)); rng.shuffle(perm)
    sol = [[perm[v - 1] for v in row] for row in base]
    rows = [b * bh + i for b in rng.sample(range(n // bh), n // bh) for i in rng.sample(range(bh), bh)]
    cols = [b * bw + i for b in rng.sample(range(n // bw), n // bw) for i in rng.sample(range(bw), bw)]
    sol = [[sol[r][c] for c in cols] for r in rows]
    puz = [row[:] for row in sol]
    cells = [(r, c) for r in range(n) for c in range(n)]; rng.shuffle(cells)
    for r, c in cells:
        if sum(v != 0 for row in puz for v in row) <= givens: break
        keep = puz[r][c]; puz[r][c] = 0
        if solve([row[:] for row in puz], n, bh, bw) != 1: puz[r][c] = keep
    assert solve([row[:] for row in puz], n, bh, bw) == 1
    return puz, sol
def grid(sh, x, y, cell, n, bh, bw, vals, fill_ans=None):
    for i in range(n + 1):
        thick = "stroke-width:1.6" if i % bw == 0 else "stroke-width:.6"
        sh.seg(x + i * cell, y, x + i * cell, y + n * cell, "l", thick)
        thick = "stroke-width:1.6" if i % bh == 0 else "stroke-width:.6"
        sh.seg(x, y + i * cell, x + n * cell, y + i * cell, "l", thick)
    for r in range(n):
        for c in range(n):
            v = vals[r][c]
            if v: sh.text(x + c * cell + cell / 2, y + r * cell + cell * .68, str(v), cell * .55, weight=700 if fill_ans is None or fill_ans[r][c] else None)
def sudoku_sheet(slug, name, n, bh, bw, count, givens, age, diff, seed, intro):
    rng = random.Random(seed)
    ps = [make(n, bh, bw, givens, rng) for _ in range(count)]
    sh, ans = Sheet(), Sheet()
    title(sh, cap(name.split(": ", 1)[-1]), 16); title(ans, "Antwoorden", 16)
    sh.text(100, 27, intro, 6)
    per_row = 2; size = 80 if n == 4 else 84; cell = size / n
    for k, (p, s) in enumerate(ps):
        x = 14 + (k % per_row) * (size + 16); y = 42 + (k // per_row) * (size + 26)
        sh.text(x, y - 4, f"Puzzel {k + 1}", 6, "start"); ans.text(x, y - 4, f"Puzzel {k + 1}", 6, "start")
        grid(sh, x, y, cell, n, bh, bw, p)
        grid(ans, x, y, cell, n, bh, bw, s, p)
    write(OUT, slug, sh, {"category": "leren", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 10 + diff * 5, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            f"Elke rij, elke kolom en elk vak met een dikke rand krijgt de cijfers 1 tot en met {n}, elk cijfer precies één keer.",
            "Zoek een rij, kolom of vak waar nog maar één cijfer mist en vul dat in.",
            "Schrijf met potlood, dan kun je gummen. Vast? Kijk op de antwoordbladzijde."]}}}, [("antwoorden", "Antwoorden", ans)])
