"""Batch 25: ronde doolhoven (met antwoordblad)."""
import math, random
from lib_gen import *

def ronde_doolhof(slug, name, rings, base, age, diff, seed):
    rng = random.Random(seed)
    # cellen: (ring, sector); ring 0 = binnenste; het aantal sectoren verdubbelt als de cellen te breed worden
    secs = []
    n = base
    for r in range(rings):
        if r > 0 and (r + 1) * 2 * math.pi / n > 2.0 * 1.0 and n < 128: n *= 2
        secs.append(n)
    cells = [(r, s) for r in range(rings) for s in range(secs[r])]
    def nbrs(c):
        r, s = c; out = [(r, (s + 1) % secs[r]), (r, (s - 1) % secs[r])]
        if r + 1 < rings:
            k = secs[r + 1] // secs[r]; out += [(r + 1, s * k + i) for i in range(k)]
        if r > 0:
            k = secs[r] // secs[r - 1]; out.append((r - 1, s // k))
        return out
    start = (rings - 1, 0); seen = {start}; stack = [start]; passages = set()
    while stack:
        c = stack[-1]; opts = [d for d in nbrs(c) if d not in seen]
        if not opts: stack.pop(); continue
        d = rng.choice(opts); seen.add(d); passages.add(frozenset((c, d))); stack.append(d)
    # pad van buiten (start) naar het midden (ring 0, sector 0)
    goal = (0, 0); prev = {start: None}; q = [start]
    while q:
        c = q.pop(0)
        for d in nbrs(c):
            if frozenset((c, d)) in passages and d not in prev: prev[d] = c; q.append(d)
    path = []; c = goal
    while c: path.append(c); c = prev[c]
    cx, cy, R0 = 100, 150, 14; dr = (88 - R0) / rings
    P = lambda rad, ang: (cx + rad * math.cos(ang), cy + rad * math.sin(ang))
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else cap(name.split(": ", 1)[-1]), 16)
        if not ans: sh.text(100, 30, "Zoek de weg van de opening buiten naar de ster.", 6)
        d = []
        for r in range(rings):
            rin, rout = R0 + r * dr, R0 + (r + 1) * dr; n = secs[r]
            for s in range(n):
                a1, a2 = 2 * math.pi * s / n - math.pi / 2, 2 * math.pi * (s + 1) / n - math.pi / 2
                # radiale muur tussen s en s+1
                if frozenset(((r, s), (r, (s + 1) % n))) not in passages:
                    p, q = P(rin, a2), P(rout, a2); d.append(f"M{f(p[0])} {f(p[1])}L{f(q[0])} {f(q[1])}")
                # buitenmuur (naar ring r+1 of de rand)
                if r + 1 < rings:
                    k = secs[r + 1] // n
                    for i in range(k):
                        if frozenset(((r, s), (r + 1, s * k + i))) not in passages:
                            b1 = a1 + (a2 - a1) * i / k; b2 = a1 + (a2 - a1) * (i + 1) / k
                            p, q = P(rout, b1), P(rout, b2); d.append(f"M{f(p[0])} {f(p[1])}A{f(rout)} {f(rout)} 0 0 1 {f(q[0])} {f(q[1])}")
                elif s != 0:
                    p, q = P(rout, a1), P(rout, a2); d.append(f"M{f(p[0])} {f(p[1])}A{f(rout)} {f(rout)} 0 0 1 {f(q[0])} {f(q[1])}")
            if r == 0:
                # binnenste ring: muur naar het midden behalve bij sector 0
                for s in range(n):
                    if s == 0: continue
                    a1, a2 = 2 * math.pi * s / n - math.pi / 2, 2 * math.pi * (s + 1) / n - math.pi / 2
                    p, q = P(rin, a1), P(rin, a2); d.append(f"M{f(p[0])} {f(p[1])}A{f(rin)} {f(rin)} 0 0 1 {f(q[0])} {f(q[1])}")
        sh.line("".join(d), "l", "stroke-width:1.3")
        sh.region(star_pts(cx, cy, 8, 3.4) and "M" + " L".join(f"{f(x)} {f(y)}" for x, y in star_pts(cx, cy, 8, 3.4)) + "Z", "y")
        if ans:
            pts = []
            for r, s in reversed(path):
                n = secs[r]; a = 2 * math.pi * (s + .5) / n - math.pi / 2; pts.append(P(R0 + (r + .5) * dr, a))
            pts = [P(R0 + (rings + .6) * dr, 2 * math.pi * .5 / secs[-1] - math.pi / 2)] + pts + [(cx, cy)]
            sh.line("M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts), "l", "stroke-width:2;stroke-dasharray:.1 3;stroke-linecap:round")
        return sh
    write(OUT, slug, page(False), {"category": "vormen", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 10 + diff * 5, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            "Zoek de opening in de buitenste ring, bovenaan.",
            "Volg de gangen naar binnen zonder door een muur te gaan, tot je bij de ster in het midden bent.",
            "Vast? Ga terug naar de laatste splitsing en probeer een andere gang. Het antwoord staat op het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
ronde_doolhof("ronde-doolhof-makkelijk", "Doolhof: rond, naar het midden", 6, 8, "6-9", 2, 2501)
ronde_doolhof("ronde-doolhof-moeilijk", "Doolhof: rond en pittig", 11, 8, "12+", 3, 2502)
