"""Batch 37b: knip-, plak- en knutselbladen (knipplaat): volgorde, sorteren, collages, puzzels, maskers, hoofdbanden, splitpenpoppen en meer."""
import math, re, random
from lib_gen import *
from shapes import heart_path, moon_path, star_path, cloud_path, leaf_path, fish_path

# Na review weggelaten (niet herkenbaar genoeg).
SKIP = {"happende-krokodil-splitpen", "klappervogel-met-touwtje", "splitpenpop-ridder"}
_write = write
def write(out, slug, *a, **k):
    if slug not in SKIP:
        return _write(out, slug, *a, **k)

LIJM = {"slug": "lijmstift"}
KLEUR = {"slug": "kleurpotloden"}
SPLIT = {"slug": "splitpennen"}
STEVIG = {"slug": "stevig-papier"}

# =====================================================================
# geometrie: alles als lijsten punten, zodat we automatisch een
# kniplijn rondom een samengesteld figuur kunnen berekenen
# =====================================================================
def ellp(cx, cy, rx, ry, rot=0, n=48, a0=0, a1=360):
    full = (a1 - a0) >= 360
    m = n if full else max(4, int(n * (a1 - a0) / 360) + 2)
    r = math.radians(rot); out = []
    for i in range(m):
        t = math.radians(a0 + (a1 - a0) * i / (m if full else m - 1))
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return out
def circ(cx, cy, r, n=40): return ellp(cx, cy, r, r, n=n)
def rect(x, y, w, h): return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
def rrect(x, y, w, h, r, n=5):
    out = []
    for cx, cy, a in [(x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)]:
        for i in range(n + 1):
            t = math.radians(a + 90 * i / n); out.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return out
def bar(x1, y1, x2, y2, w):
    """Rechthoek van p1 naar p2 met halve breedte w."""
    dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy); nx, ny = -dy / L * w, dx / L * w
    return [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]
def bone(x1, y1, x2, y2, w, r):
    return [bar(x1, y1, x2, y2, w), circ(x1, y1, r, 28), circ(x2, y2, r, 28)]

_TOK = re.compile(r"[MLHVCQZ]|-?\d*\.?\d+(?:e-?\d+)?")
def sample(d, n=12):
    """Absoluut SVG-pad (M L H V C Q Z) naar punten (eerste subpad)."""
    toks = _TOK.findall(d); i = 0; pts = []; cur = (0, 0); cmd = None
    def num():
        nonlocal i; v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if toks[i].isalpha(): cmd = toks[i]; i += 1
        if cmd == "Z": continue
        if cmd == "M": cur = (num(), num()); pts.append(cur); cmd = "L"
        elif cmd == "L": cur = (num(), num()); pts.append(cur)
        elif cmd == "H": cur = (num(), cur[1]); pts.append(cur)
        elif cmd == "V": cur = (cur[0], num()); pts.append(cur)
        elif cmd == "C":
            p0 = cur; p1 = (num(), num()); p2 = (num(), num()); p3 = (num(), num())
            for k in range(1, n + 1):
                t = k / n; u = 1 - t
                pts.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0], u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
            cur = p3
        elif cmd == "Q":
            p0 = cur; p1 = (num(), num()); p2 = (num(), num())
            for k in range(1, n + 1):
                t = k / n; u = 1 - t
                pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
            cur = p2
    if len(pts) > 1 and math.dist(pts[0], pts[-1]) < 1e-6: pts.pop()
    return pts

def P(pts): return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in pts) + "Z"
def PL(pts): return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in pts)
def T(pts, dx=0, dy=0, s=1): return [(x * s + dx, y * s + dy) for x, y in pts]
def MX(pts, ax): return [(2 * ax - x, y) for x, y in pts][::-1]
def area(pts): return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2

def offset_poly(pts, d):
    if area(pts) < 0: pts = pts[::-1]
    n = len(pts); out = []
    for i in range(n):
        a, p, b = pts[i - 1], pts[i], pts[(i + 1) % n]
        e1 = (p[0] - a[0], p[1] - a[1]); e2 = (b[0] - p[0], b[1] - p[1])
        l1 = math.hypot(*e1) or 1; l2 = math.hypot(*e2) or 1
        n1 = (e1[1] / l1, -e1[0] / l1); n2 = (e2[1] / l2, -e2[0] / l2)
        c = 1 + n1[0] * n2[0] + n1[1] * n2[1]
        if c < .35:
            out += [(p[0] + n1[0] * d, p[1] + n1[1] * d), (p[0] + n2[0] * d, p[1] + n2[1] * d)]
        else:
            out.append((p[0] + (n1[0] + n2[0]) * d / c, p[1] + (n1[1] + n2[1]) * d / c))
    return out

def _dp(pts, eps):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]; dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1e-9
    best, bi = 0, 0
    for i in range(1, len(pts) - 1):
        dd = abs((pts[i][0] - a[0]) * dy - (pts[i][1] - a[1]) * dx) / L
        if dd > best: best, bi = dd, i
    if best <= eps: return [a, b]
    return _dp(pts[:bi + 1], eps)[:-1] + _dp(pts[bi:], eps)

def outline(polys, d=3, res=.3):
    """Buitenrand (lussen) van de vereniging van alle veelhoeken, d naar buiten verschoven."""
    ps = [offset_poly(p, d) if d else p for p in polys]
    xs = [x for p in ps for x, _ in p]; ys = [y for p in ps for _, y in p]
    X0, Y0 = min(xs) - 2 * res, min(ys) - 2 * res
    nx, ny = int((max(xs) - X0) / res) + 4, int((max(ys) - Y0) / res) + 4
    g = [bytearray(nx) for _ in range(ny)]
    for p in ps:
        ed = list(zip(p, p[1:] + p[:1])); pys = [y for _, y in p]
        for j in range(max(0, int((min(pys) - Y0) / res) - 1), min(ny - 1, int((max(pys) - Y0) / res) + 1) + 1):
            y = Y0 + (j + .5) * res
            xc = sorted(ax + (y - ay) * (bx - ax) / (by - ay) for (ax, ay), (bx, by) in ed if (ay <= y) != (by <= y))
            row = g[j]
            for k in range(0, len(xc) - 1, 2):
                for i in range(max(0, math.ceil((xc[k] - X0) / res - .5)), min(nx - 1, math.floor((xc[k + 1] - X0) / res - .5)) + 1): row[i] = 1
    nxt = {}
    def inside(i, j): return 0 <= i < nx and 0 <= j < ny and g[j][i]
    for j in range(ny):
        for i in range(nx):
            if not g[j][i]: continue
            if not inside(i, j - 1): nxt.setdefault((i, j), []).append((i + 1, j))
            if not inside(i + 1, j): nxt.setdefault((i + 1, j), []).append((i + 1, j + 1))
            if not inside(i, j + 1): nxt.setdefault((i + 1, j + 1), []).append((i, j + 1))
            if not inside(i - 1, j): nxt.setdefault((i, j + 1), []).append((i, j))
    loops = []
    while nxt:
        start = next(iter(nxt)); cur = start; loop = []
        while True:
            loop.append(cur)
            lst = nxt.get(cur)
            if not lst: break
            nb = lst.pop()
            if not lst: del nxt[cur]
            cur = nb
            if cur == start: break
        if len(loop) > 8: loops.append([(X0 + i * res, Y0 + j * res) for i, j in loop])
    res_loops = []
    for lp in loops:
        if area(lp) <= 0: continue  # gaten overslaan
        m = [((lp[k][0] + lp[k - 1][0]) / 2, (lp[k][1] + lp[k - 1][1]) / 2) for k in range(len(lp))]
        for _ in range(2):
            q = []
            for k in range(len(m)):
                a, b = m[k], m[(k + 1) % len(m)]
                q += [(a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25), (a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75)]
            m = q
        h = len(m) // 2
        s = _dp(m[:h + 1], .1)[:-1] + _dp(m[h:] + [m[0]], .1)[:-1]
        res_loops.append(s)
    return res_loops

def clip_x(loop, x0, x1):
    """Delen van een gesloten lus die tussen x0 en x1 liggen, als open lijnen."""
    n = len(loop); ins = [x0 <= x <= x1 for x, _ in loop]
    if all(ins): return [loop + [loop[0]]]
    k0 = next(i for i in range(n) if not ins[i])
    parts, cur = [], None
    for s in range(n):
        i = (k0 + s) % n; j = (i + 1) % n
        a, b = loop[i], loop[j]
        if ins[i] and cur is not None: cur.append(a)
        if ins[i] != ins[j]:
            xb = x0 if (a[0] < x0) != (b[0] < x0) else x1
            t = (xb - a[0]) / (b[0] - a[0]); pt = (xb, a[1] + (b[1] - a[1]) * t)
            if ins[i]: cur.append(pt); parts.append(cur); cur = None
            else: cur = [pt]
    return [p for p in parts if len(p) > 1]

class Pc:
    """Knipstuk: kleurvlakken + automatische kniplijn rondom."""
    def __init__(s, sh, dx=0, dy=0, sc=1):
        s.sh, s.dx, s.dy, s.sc, s.polys = sh, dx, dy, sc, []
    def T(s, pts): return [(x * s.sc + s.dx, y * s.sc + s.dy) for x, y in pts]
    def add(s, pts, code="-", sil=True):
        s.sh.poly_r(s.T(pts), code)
        if sil: s.polys.append(s.T(pts))
        return s
    def sil(s, pts): s.polys.append(s.T(pts)); return s
    def ln(s, pts, closed=False, cls="l", style=None):
        q = s.T(pts); s.sh.line(P(q) if closed else PL(q), cls, style)
    def dot(s, x, y, r=1.4):
        (x, y), = s.T([(x, y)]); s.sh.dot(x, y, r * s.sc)
    def text(s, x, y, t, size=6, **kw):
        (x, y), = s.T([(x, y)]); s.sh.text(x, y, t, size, **kw)
    def hole(s, x, y):
        (x, y), = s.T([(x, y)]); s.sh.circle_line(x, y, 1.6, "cut"); s.sh.seg(x - 1, y, x + 1, y, "l", "stroke-width:.5"); s.sh.seg(x, y - 1, x, y + 1, "l", "stroke-width:.5")
    def tab(s, p1, p2, depth=6, inside=None, glue=False):
        """Flapje op de rand p1-p2, naar de kant weg van punt `inside`."""
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        if inside and (inside[0] - mx) * nx + (inside[1] - my) * ny > 0: nx, ny = -nx, -ny
        k = .22
        q = [p1, p2, (p2[0] + nx * depth - dx * k, p2[1] + ny * depth - dy * k), (p1[0] + nx * depth + dx * k, p1[1] + ny * depth + dy * k)]
        tq = s.T(q)
        if glue: s.sh.raw(f'<path class="glue" d="{P(tq)}"/>')
        else: s.sh.poly_r(tq, "-")
        s.polys.append(tq); s.sh.line(PL(s.T([p1, p2])), "fold")
    def cut(s, d=3):
        if not s.polys: return s
        for lp in outline(s.polys, d): s.sh.line(P(lp), "cut")
        return s

def bbox(fn):
    pc = Pc(Sheet()); fn(pc)
    xs = [x for p in pc.polys for x, _ in p]; ys = [y for p in pc.polys for _, y in p]
    return min(xs), min(ys), max(xs), max(ys)
def place(sh, fn, x, y, anchor="tl", d=3):
    """Teken knipstuk fn met de linkerbovenhoek (incl. kniprand) op x, y; anchor 'tc' = midden boven."""
    x0, y0, x1, y1 = bbox(fn)
    if anchor == "tc": x -= (x1 - x0 + 2 * d) / 2
    pc = Pc(sh, x - x0 + d, y - y0 + d); fn(pc); pc.cut(d)
    return x1 - x0 + 2 * d, y1 - y0 + 2 * d

def S(fn, k):
    def g(pc):
        pc.sc *= k; fn(pc)
    return g
def flow(sh, fns, x0, y0, x1, gap=1, center=True):
    """Zet knipstukken in rijen van links naar rechts; geeft de y onder de laatste rij terug."""
    rows, row, w = [], [], 0
    for fn in fns:
        bw, bh = (lambda b: (b[2] - b[0] + 6, b[3] - b[1] + 6))(bbox(fn))
        if row and w + bw > x1 - x0: rows.append((row, w)); row, w = [], 0
        row.append((fn, bw, bh)); w += bw + gap
    if row: rows.append((row, w))
    y = y0
    for row, w in rows:
        x = x0 + ((x1 - x0) - (w - gap)) / 2 if center else x0
        hmax = max(h for _, _, h in row)
        for fn, bw, bh in row:
            place(sh, fn, x, y + (hmax - bh) / 2); x += bw + gap
        y += hmax + gap
    if y > 270 and not getattr(sh, "dry", False): print("LET OP: flow loopt over de rand", y)
    return y

def ept(cx, cy, rx, ry, a):
    t = math.radians(a); return (cx + rx * math.cos(t), cy + ry * math.sin(t))

def head(sh, t, size=11):
    title(sh, t, 15, size)

def L(fn, *a): return lambda pc: fn(pc, *a)
def pack(sh, rows, y0=28, ymax=270, gap=2, k=2.0):
    """Zet rijen knipstukken onder elkaar; verkleint alles tot het op het vel past (en elke rij in de breedte)."""
    def run(target, kk):
        y = y0
        for row in rows:
            fns = [S(fn, kk) for fn in row]
            ws = sum(bbox(fn)[2] - bbox(fn)[0] + 6 + gap for fn in fns) - gap
            if ws > 197: return None
            y = flow(target, fns, 1.5, y, 198.5, gap) + gap
        return y
    while k > .3:
        d = Sheet(); d.dry = True; yy = run(d, k)
        if yy is not None and yy - gap <= ymax: run(sh, k); return k
        k -= .02
    raise ValueError("past niet")
def union(polys, res=.3):
    """Eén buitenrand om overlappende vormen (zonder binnenlijnen)."""
    return max(outline(polys, 0, res), key=lambda l: abs(area(l)))
def two(fn): return [fn, fn]
def icon_at(sh, fn, x, y, k):
    sh.raw(f'<g transform="translate({f(float(x))} {f(float(y))}) scale({k})">'); fn(Pc(sh)); sh.raw("</g>")
def glue_rect(sh, x, y, w, h):
    sh.raw(f'<rect class="glue" x="{f(float(x))}" y="{f(float(y))}" width="{f(float(w))}" height="{f(float(h))}"/>')
def wrap(fn, k, dx, dy):
    def g(p):
        p.sc, p.dx, p.dy = p.sc * k, p.dx + dx * p.sc, p.dy + dy * p.sc; fn(p)
    return g
def put(sh, fn, x, y, k=1): fn(Pc(sh, x, y, k))
def waves(p, y, x0=2, x1=60, h=2.2, step=8, style="stroke-width:1"):
    d = f"M{x0} {y}" + "".join(f"Q{x0 + i * step + step / 4} {y - h} {x0 + i * step + step / 2} {y}Q{x0 + i * step + 3 * step / 4} {y + h} {x0 + (i + 1) * step} {y}" for i in range(int((x1 - x0) // step)))
    p.ln(sample(d, 4), style=style)
SILFILL = "fill:#d6d1c8;stroke:#9a948a;stroke-width:.8"
def silhouette(sh, fn, x, y, k=1, d=3):
    """Grijze schaduw (zelfde omtrek als het knipstuk, zonder kniprand)."""
    pc = Pc(Sheet(), x, y, k); fn(pc)
    for lp in outline(pc.polys, d, .25): sh.line(P(lp), "l", SILFILL)

# =====================================================================
# Op volgorde: vier plaatjes knippen en in de goede volgorde plakken
# =====================================================================
CW, CH = 62, 50
def frame_at(sh, fn, x, y):
    sh.raw(f'<g transform="translate({f(float(x))} {f(float(y))})">'); fn(Pc(sh)); sh.raw("</g>")
def volgorde(slug, name, heading, scenes, shuffled, cat, age, steps, diff=1):
    assert sorted(shuffled) == [0, 1, 2, 3] and shuffled != [0, 1, 2, 3]
    BW, BH = 66, 54
    def boxes(sh, answer):
        for i in range(4):
            col, row = i % 2, i // 2
            bx, by = 100 - BW - 4 + col * (BW + 8), 34 + row * (BH + 8)
            sh.rect_line(bx, by, BW, BH, "l", 3, "stroke-width:1.2")
            if answer: frame_at(sh, scenes[i], bx + 2, by + 2)
            sh.circle_r(bx + 2, by + 2, 5.5, "-"); sh.text(bx + 2, by + 4.6, str(i + 1), 7.5)
        sh.line(f"M{100 - 3} 61h6m-3 -3l3 3l-3 3", "l", "stroke-width:1.2")
        sh.line(f"M{100 - 3} 123h6m-3 -3l3 3l-3 3", "l", "stroke-width:1.2")
    sh = Sheet(); head(sh, heading)
    sh.text(100, 27, "Wat komt eerst? Plak de plaatjes in de goede volgorde: 1, 2, 3, 4.", 6)
    boxes(sh, False)
    sh.text(100, 160, "Kleur de plaatjes en knip ze los:", 6)
    gx, gy = 100 - CW, 166
    for k, j in enumerate(shuffled):
        col, row = k % 2, k // 2; frame_at(sh, scenes[j], gx + col * CW, gy + row * CH)
    for r in range(3): sh.seg(gx, gy + r * CH, gx + 2 * CW, gy + r * CH, "cut")
    for c in range(3): sh.seg(gx + c * CW, gy, gx + c * CW, gy + 2 * CH, "cut")
    sh.legend(["cut"], 277)
    an = Sheet(); head(an, "Antwoorden"); boxes(an, True)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": 15,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": name, "steps": [
            "Kleur de vier plaatjes in en knip ze los langs de streepjeslijnen.",
            "Leg ze naast elkaar en bekijk ze goed. " + steps[0],
            "Leg de plaatjes in de vakken 1, 2, 3 en 4. " + steps[1],
            "Kijk na met het antwoordblad en plak de plaatjes vast. Vertel het verhaal nog een keer na."]}}},
        [("antwoorden", "Antwoorden", an)])

# ---------- boon in een glazen pot ----------
def jar(p):
    p.add(sample("M19 22H43V43Q43 47 39 47H23Q19 47 19 43Z"), "-")
    p.add(rrect(17, 18, 28, 5, 1.5), "-")
    p.add(sample("M20 36Q23 33 27 35.5Q31 33 35 35.5Q39 33 42 35.5V43Q42 46 39 46H23Q20 46 20 43Z"), "-")
    p.ln([(22, 25), (22, 32)], style="stroke-width:.8")
def bean(p, x, y): p.add(ellp(x, y, 5, 3.4, -15), "w"); p.ln(sample(f"M{x - 1.5} {y + .6}Q{x} {y - .6} {x + 1.5} {y - 1}", 3), style="stroke-width:.8")
def roots(p, x, y):
    p.ln(sample(f"M{x} {y}Q{x - 1} {y + 5} {x + 1} {y + 9}Q{x + 2} {y + 12} {x} {y + 14}", 6), style="stroke-width:1.2")
    p.ln(sample(f"M{x + .5} {y + 6}Q{x + 4} {y + 8} {x + 6} {y + 12}", 4), style="stroke-width:.8"); p.ln(sample(f"M{x} {y + 9}Q{x - 4} {y + 11} {x - 5} {y + 14}", 4), style="stroke-width:.8")
def bo1(p): jar(p); bean(p, 31, 32)
def bo2(p): jar(p); roots(p, 31, 34); bean(p, 31, 31)
def bo3(p):
    jar(p); roots(p, 31, 33)
    p.ln(sample("M31 29Q30 20 31 9", 6), style="stroke-width:1.4")
    p.add(ellp(26, 10, 5.5, 2.6, 20), "g"); p.add(ellp(36, 10, 5.5, 2.6, -20), "g"); bean(p, 31, 30)
def bo4(p):
    jar(p); roots(p, 31, 33)
    p.ln(sample("M31 31Q29 18 31 2", 8), style="stroke-width:1.6")
    p.add(ellp(24.5, 6, 6.5, 2.6, 20), "g"); p.add(ellp(37.5, 4, 6.5, 2.6, -20), "g")
    p.add(ellp(23.5, 14, 7.5, 3, 15), "g"); p.add(ellp(38.5, 11, 7.5, 3, -15), "g")
    p.add(circ(53, 9, 4.5), "y")
volgorde("volgorde-boon-groeit-in-een-pot", "Op volgorde: een boon groeit in een pot", "Een boon groeit", [bo1, bo2, bo3, bo4], [2, 0, 3, 1], "natuur", "4-6", [
    "Waar zie je alleen de boon? Waar komen er worteltjes uit? En waar groeit de plant al boven de pot uit?",
    "Eerst leg je de boon op nat watten en geef je water. Dan groeien er worteltjes naar beneden, dan een stengel met twee blaadjes naar boven, en tot slot wordt het een lange plant met veel bladeren."])

# ---------- kikkerdril ----------
def water(p): p.add(rect(0, 0, CW, CH), "b")
def reed(p, x):
    p.ln(sample(f"M{x} 50Q{x - 1} 30 {x + 2} 10", 6), style="stroke-width:1.2")
    p.add(sample(f"M{x + 2} 10Q{x + 5} 18 {x + 3} 26Q{x} 18 {x + 2} 10Z"), "g")
def tadpole(p, x, y, s=1, legs=0, rot=0):
    q = Pc(p.sh, p.dx + x * p.sc, p.dy + y * p.sc, p.sc * s); q.polys = p.polys
    q.add(sample("M-2 0Q8 -6 16 0Q8 4 -2 0Z"), "x" if legs < 2 else "w")
    if legs:
        for sy in (-1, 1): q.ln([(1, sy * 2.5), (-1, sy * 6), (-4, sy * 5.5)], style="stroke-width:1.1")
    if legs == 2:
        for sy in (-1, 1): q.ln([(-7, sy * 3), (-9, sy * 6)], style="stroke-width:1")
    q.add(ellp(-6, 0, 5, 4), "w"); q.dot(-8, -1.6, .9); q.dot(-8, 1.6, .9)
def kd1(p):
    water(p); reed(p, 52)
    for k, (x, y) in enumerate([(14, 24), (20, 20), (26, 24), (18, 28), (24, 30), (30, 27), (12, 31), (30, 19), (22, 35), (16, 37)]):
        p.add(circ(x, y, 4), "-"); p.dot(x, y, 1.1)
    waves(p, 6, 2, 46)
def kd2(p):
    water(p); reed(p, 52)
    for x, y in [(16, 18), (30, 30), (18, 38)]: tadpole(p, x, y)
    waves(p, 6, 2, 46)
def kd3(p):
    water(p); reed(p, 52)
    tadpole(p, 24, 22, 1.6, 2)
    waves(p, 6, 2, 46)
def kd4(p):
    water(p); p.add(ellp(28, 38, 24, 8), "g"); p.add(sample("M28 38L48 33L50 38Z"), "b", sil=False)
    for s in (-1, 1): p.add(ellp(28 + s * 10, 34, 5, 3), "l")
    p.add(ellp(28, 28, 11, 8), "l")
    for s in (-1, 1): p.add(circ(28 + s * 6, 20, 4.2), "l"); p.add(circ(28 + s * 6, 20, 2.6), "-", sil=False); p.dot(28 + s * 6.4, 20.4, 1.1)
    p.ln(sample("M22 29Q28 33 34 29", 4), style="stroke-width:1")
    p.add(circ(52, 10, 2), "x")
    for a in (0, 1): p.add(ellp(52 + (a * 2 - 1) * 3, 8, 2.6, 1.4, (a * 2 - 1) * 30), "-")
volgorde("volgorde-kikkerdril-wordt-kikker", "Op volgorde: van kikkerdril tot kikker", "Van kikkerdril tot kikker", [kd1, kd2, kd3, kd4], [3, 0, 2, 1], "dieren", "4-6", [
    "Zoek de eitjes (het kikkerdril), de kikkervisjes, het grote kikkervisje met pootjes en de kikker.",
    "Eerst legt de kikker een klont eitjes in het water. Daar komen kleine kikkervisjes uit. Ze krijgen pootjes en hun staart wordt korter, en tot slot springt er een kikker uit het water."])

# ---------- sneeuwpop smelt ----------
def snow_ground(p): p.add(sample("M0 50V42Q20 38 40 42Q52 44 62 40V50Z"), "-")
def sun(p, x, y, r=5):
    p.add(circ(x, y, r), "y")
    for a in range(0, 360, 45):
        t = math.radians(a); p.ln([(x + (r + 1.5) * math.cos(t), y + (r + 1.5) * math.sin(t)), (x + (r + 4) * math.cos(t), y + (r + 4) * math.sin(t))], style="stroke-width:1")
def hat(p, x, y, rot=0):
    q = Pc(p.sh, p.dx + x * p.sc, p.dy + y * p.sc, p.sc); q.polys = p.polys
    pts = lambda L: [(px * math.cos(math.radians(rot)) - py * math.sin(math.radians(rot)), px * math.sin(math.radians(rot)) + py * math.cos(math.radians(rot))) for px, py in L]
    q.add(pts(rect(-5, -8, 10, 8)), "x"); q.add(pts(rect(-8, -1, 16, 2.4)), "x")
def carrot(p, x, y, dx=7): p.add([(x, y - 1.6), (x + dx, y), (x, y + 1.6)], "o")
def sm1(p):
    snow_ground(p); p.add(sample("M10 14C10 8 18 8 18 14C24 14 24 20 18 20H10C5 20 5 14 10 14Z"), "-")
    p.add(circ(31, 34, 10), "-"); p.add(circ(31, 19, 7), "-")
    hat(p, 31, 13); carrot(p, 31, 20); p.dot(29, 17.5, .9); p.dot(33, 17.5, .9)
    p.add(rect(25, 25, 12, 3), "r"); p.add(rect(33, 25, 3, 8), "r")
    for y in (31, 36): p.dot(31, y, 1)
    for x, y in [(8, 30), (50, 12), (54, 30), (44, 22), (6, 6)]: p.add(circ(x, y, 1.2), "-")
def sm2(p):
    snow_ground(p); sun(p, 52, 10)
    p.add(sample("M22 43C20 34 22 28 31 28C40 28 42 34 40 43Z"), "-"); p.add(circ(31, 22, 6.5), "-")
    hat(p, 32, 16.5, 10); carrot(p, 31, 23); p.dot(29, 20.5, .9); p.dot(33, 20.5, .9)
    p.add(sample("M25 28H37V31H25Z"), "r"); p.add(rect(33, 30, 3, 7), "r")
    p.ln(sample("M23 40Q22 44 24 46", 3), style="stroke-width:1"); p.ln(sample("M39 40Q41 44 39 46", 3), style="stroke-width:1")
def sm3(p):
    snow_ground(p); sun(p, 50, 10, 6)
    p.add(ellp(31, 44, 22, 4), "b")
    p.add(sample("M15 44C15 34 22 27 31 27C40 27 47 34 47 44Z"), "-")
    hat(p, 33, 28, -15); carrot(p, 31, 35); p.dot(28, 32.5, .9); p.dot(34, 32.5, .9)
    p.add(rect(19, 39, 24, 3), "r")
def sm4(p):
    snow_ground(p); sun(p, 50, 10, 7)
    p.add(ellp(31, 43, 25, 5), "b")
    hat(p, 22, 44); carrot(p, 33, 42, 8)
    p.add(sample("M42 41H52V44H42Z"), "r")
    p.dot(17, 44.5, .9); p.dot(28, 45, .9)
volgorde("volgorde-sneeuwpop-smelt", "Op volgorde: de sneeuwpop smelt", "De sneeuwpop smelt", [sm1, sm2, sm3, sm4], [2, 3, 0, 1], "natuur", "2-4", [
    "Waar is de sneeuwpop nog groot? Waar schijnt de zon? Waar ligt alleen nog een plas?",
    "Eerst sneeuwt het en staat de sneeuwpop er mooi bij. Dan komt de zon en wordt hij kleiner, dan zakt hij in elkaar, en tot slot liggen alleen de hoed, de wortel en de sjaal in een plas water."])

# ---------- appel opeten ----------
def table(p): p.add(rect(0, 42, CW, 8), "w"); p.ln([(0, 46), (62, 46)], style="stroke-width:.6")
def apple_top(p, x=31):
    p.ln([(x, 9), (x + 1, 4)], style="stroke-width:1.4"); p.add(ellp(x + 5.5, 5, 4.5, 2, -20), "g")
def ap1(p):
    table(p); p.add(sample("M31 10C24 5 15 9 15 21C15 33 22 42 31 40C40 42 47 33 47 21C47 9 38 5 31 10Z"), "r"); apple_top(p)
    p.ln(sample("M21 16Q19 20 20 24", 3), style="stroke-width:1")
def ap2(p):
    table(p); p.add(sample("M31 10C24 5 15 9 15 21C15 33 22 42 31 40C40 42 47 33 47 26C43 27 41 22 43 19C41 17 42 13 44 12C41 8 36 7 31 10Z"), "r"); apple_top(p)
    p.add(sample("M47 26C43 27 41 22 43 19C41 17 42 13 44 12C45 15 46 20 47 26Z"), "y", sil=False)
def ap3(p):
    table(p); p.add(sample("M31 10C24 5 15 9 15 21C15 33 22 42 31 40C34 40 34 36 33 34C36 32 36 28 34 26C37 24 36 19 34 17C36 14 35 11 31 10Z"), "r"); apple_top(p)
    p.add(sample("M31 40C34 40 34 36 33 34C36 32 36 28 34 26C37 24 36 19 34 17C36 14 35 11 31 10C30 20 30 30 31 40Z"), "y", sil=False)
    p.dot(31.5, 22, .8); p.dot(31.5, 27, .8)
def ap4(p):
    table(p)
    p.add(sample("M31 10C27 10 25 12 27 16C29 20 29 22 28 25C27 28 27 31 29 34C27 37 26 39 31 40C36 39 35 37 33 34C35 31 35 28 34 25C33 22 33 20 35 16C37 12 35 10 31 10Z"), "y")
    p.add(sample("M26 10C24 9 24 11 27 12L28 11Z"), "r") if False else None
    p.add(sample("M27 10Q31 8 35 10L35 12Q31 11 27 12Z"), "r"); p.add(sample("M27 38Q31 41 35 38L35 40.5Q31 42 27 40.5Z"), "r")
    p.ln([(31, 9), (32, 4)], style="stroke-width:1.4")
    p.dot(30.3, 24, .8); p.dot(31.8, 27, .8)
volgorde("volgorde-appel-opeten", "Op volgorde: een appel opeten", "Hap, hap, hap!", [ap1, ap2, ap3, ap4], [3, 1, 0, 2], "eten", "2-4", [
    "Waar is de appel nog heel? Waar is er één hap uit? Waar is alleen het klokhuis over?",
    "Eerst is de appel heel. Dan neem je één hap, dan nog veel meer happen, en tot slot is alleen het klokhuis over."])

# ---------- boterham smeren ----------
def board(p): p.add(rrect(4, 34, 54, 12, 3), "w"); p.add(circ(52, 40, 1.8), "-", sil=False)
def slice_(p, x=22, y=12, code="y"):
    p.add(sample(f"M{x - 2} {y + 22}V{y + 8}C{x - 8} {y + 8} {x - 8} {y - 4} {x + 2} {y - 3}C{x + 8} {y - 8} {x + 18} {y - 4} {x + 18} {y + 2}C{x + 22} {y + 4} {x + 22} {y + 10} {x + 18} {y + 10}V{y + 22}Z"), "w")
    p.add(sample(f"M{x} {y + 20}V{y + 7}C{x - 5} {y + 7} {x - 5} {y - 2} {x + 2} {y - 1}C{x + 8} {y - 6} {x + 16} {y - 2} {x + 16} {y + 3}C{x + 19} {y + 5} {x + 19} {y + 9} {x + 16} {y + 9}V{y + 20}Z"), code, sil=False)
def knife(p, x, y, ang=-20):
    t = math.radians(ang); c, s = math.cos(t), math.sin(t)
    R = lambda L: [(x + px * c - py * s, y + px * s + py * c) for px, py in L]
    p.add(R([(0, -1.6), (12, -1.6), (12, 1.6), (0, 1.6)]), "z"); p.add(R(sample("M12 -1.6H24Q27 -1.6 26 0Q25 1.6 22 1.6H12Z")), "-")
def bt1(p):
    board(p); slice_(p, 14, 12, "-")
    p.add(rect(42, 18, 14, 9), "y"); p.add(rect(42, 18, 14, 3), "b", sil=False); knife(p, 36, 32, -10)
def bt2(p):
    board(p); slice_(p, 14, 12, "y")
    for x, y in [(16, 16), (22, 23), (15, 27)]: p.ln(sample(f"M{x} {y}Q{x + 3} {y - 2} {x + 6} {y}Q{x + 9} {y + 2} {x + 12} {y}", 4), style="stroke-width:.9")
    knife(p, 24, 20, -25)
    p.add(rect(42, 18, 14, 9), "y"); p.add(rect(42, 18, 14, 3), "b", sil=False)
def bt3(p):
    board(p); slice_(p, 14, 12, "y")
    p.add(sample("M11 16H35V31H11Z"), "o")
    for x, y, r in [(16, 21, 1.6), (25, 26, 2), (30, 19, 1.4)]: p.add(circ(x, y, r), "-", sil=False)
    p.add(sample("M42 30L56 30L56 18Z"), "o"); p.add(circ(51, 26, 1.3), "-", sil=False)
def bt4(p):
    board(p); slice_(p, 14, 12, "y")
    p.add(sample("M11 16H35V31H11Z"), "o")
    slice_(p, 18, 9, "y")
    p.add(sample("M32 31H36V34H32Z"), "o", sil=False)
volgorde("volgorde-boterham-smeren", "Op volgorde: een boterham smeren", "Een boterham smeren", [bt1, bt2, bt3, bt4], [1, 3, 0, 2], "eten", "4-6", [
    "Waar ligt de boterham nog leeg op de plank? Waar zit de boter erop? Waar de kaas? En waar ligt er al een tweede snee bovenop?",
    "Eerst leg je een snee brood op de plank. Dan smeer je er boter op, dan leg je er een plak kaas op, en tot slot leg je er een tweede snee brood op. Smakelijk!"])

# ---------- iconen overgenomen uit batch 13b (gekopieerd, niet geïmporteerd) ----------
def taper(pts, w0, w1):
    """Veelhoek rond een middenlijn die van halve breedte w0 naar w1 versmalt."""
    n = len(pts); left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        w = w0 + (w1 - w0) * i / (n - 1)
        left.append((x - dy / l * w, y + dx / l * w)); right.append((x + dy / l * w, y - dx / l * w))
    return left + right[::-1]
def ic_hond(p):
    p.ln(sample("M8 22Q3 18 5 12", 4), style="stroke-width:2")
    for x in (11, 15, 23, 27): p.add(rect(x - 1.8, 24, 3.6, 10), "w")
    p.add(ellp(19, 23, 12, 6.5), "w"); p.add(circ(29, 14, 7), "w"); p.add(ellp(35, 16, 4, 3), "w")
    p.add(ellp(26, 15, 3, 6, 15), "x"); p.dot(30, 12, 1.3); p.add(circ(38.5, 15.5, 1.5), "x")
def ic_olifant(p):
    for x in (9, 15, 22, 27): p.add(rect(x - 2.5, 26, 5, 9), "z")
    p.add(ellp(17, 22, 13, 10), "z"); p.add(taper(sample("M33 18Q37 26 36 34", 6), 3, 2), "z")
    p.add(circ(30, 15, 8), "z"); p.add(ellp(26, 17, 5, 7.5), "z"); p.dot(32, 13, 1.3)
def ic_muis(p):
    p.ln(sample("M8 26Q1 26 3 18Q5 14 2 10", 6), style="stroke-width:1.4")
    p.add(sample("M8 28C6 18 16 14 26 18L36 24C34 27 30 28 26 28Z"), "z"); p.add(circ(24, 15, 5), "k"); p.dot(29, 21, 1.3); p.add(circ(36, 24, 1.6), "x")
def ic_giraf(p):
    for x in (10, 14, 20, 24): p.ln([(x, 27), (x, 38)], style="stroke-width:2")
    p.add(ellp(17, 25, 9, 5.5), "y"); p.add(bar(21, 22, 28, 6, 2.6), "y"); p.add(ellp(31, 6, 5.5, 3.2, 20), "y")
    p.ln([(27, 3), (27, 0)], style="stroke-width:1.2"); p.ln([(29.5, 2.5), (30, -0.5)], style="stroke-width:1.2"); p.dot(30, 5, 1)
    for x, y in [(13, 24), (19, 27), (21, 23), (24, 15), (26, 10)]: p.add(circ(x, y, 1.4), "w", sil=False)
def ic_slak(p):
    p.add(sample("M3 32C3 28 6 27 9 28L32 28C36 28 37 32 35 33L5 34Z"), "y")
    p.add(bar(7, 28, 5, 20, .9), "y"); p.add(circ(5, 19, 1.8), "y"); p.add(bar(9, 28, 10, 20, .9), "y"); p.add(circ(10, 19, 1.8), "y")
    p.add(circ(23, 19, 10), "w"); p.ln(sample("M23 19C26 19 26 15 22 15C18 15 17 21 22 23C28 25 32 18 29 13", 10), style="stroke-width:1.4")
def ic_vogel(p):
    p.add([(9, 20), (2, 14), (3, 26)], "b"); p.add(ellp(18, 22, 11, 8), "b"); p.add(circ(28, 15, 6.5), "b")
    p.add([(33.5, 13), (39, 16), (33.5, 18)], "o"); p.add(sample("M11 20Q18 10 25 21Q18 26 11 20Z"), "n"); p.dot(29.5, 14, 1.3)
    p.ln([(16, 30), (15, 36)], style="stroke-width:1.4"); p.ln([(21, 30), (22, 36)], style="stroke-width:1.4")
def bd_kip(pc):
    pc.add(sample("M-14 -6L-22 -18L-14 -14L-18 -24L-8 -12Z"), "w")
    for x in (-3, 4): pc.add(bar(x, 8, x, 16, 1.2), "o"); pc.add(bar(x, 16, x + 4, 17, 1), "o")
    pc.add(sample("M-14 0C-14 -10 2 -12 6 -6C6 -18 22 -18 22 -8C22 6 10 10 2 10C-8 10 -14 6 -14 0Z"), "-")
    pc.add([(22, -10), (29, -7), (22, -5)], "o")
    pc.add(sample("M10 -18Q12 -24 14 -19Q16 -24 18 -18Z"), "r"); pc.add(ellp(20, -2, 2, 3), "r", sil=False)
    pc.dot(16, -10, 1.4); pc.ln(sample("M-6 -2Q2 4 10 -2", 6), style="stroke-width:1.2")
def bd_kuiken(pc):
    for x in (-3, 3): pc.add(bar(x, 8, x, 13, .9), "o")
    pc.add(circ(0, 2, 8), "y"); pc.add(circ(5, -8, 6), "y"); pc.add([(10, -9), (15, -7), (10, -5)], "o")
    pc.dot(7, -9, 1.2); pc.ln(sample("M-5 1Q0 5 4 1", 4), style="stroke-width:1.1")
def bd_eend(pc):
    pc.add(sample("M-20 0C-24 -6 -22 -8 -16 -4C-10 -8 0 -8 4 -6C2 -18 18 -20 20 -8L30 -6L20 -2C22 8 8 12 -4 12C-14 12 -20 8 -20 0Z"), "-")
    pc.add(sample("M20 -8L30 -6L20 -2Z"), "o", sil=False)
    pc.ln(sample("M-10 0Q0 8 8 0", 6)); pc.dot(13, -11, 1.5)

# =====================================================================
# Sorteerbladen met plaatjes van 40x40
# =====================================================================
def sorteer(slug, name, heading, cats, cat, age, steps, seed, diff=1, intro="Knip de kaartjes los en leg ze in het goede vak."):
    n = len(cats); bw = (188 - (n - 1) * 4) / n
    def boxes(sh):
        for i, (label, _, icon) in enumerate(cats):
            bx = 6 + i * (bw + 4)
            sh.rect_line(bx, 32, bw, 118, "l", 4, "stroke-width:1.4")
            if icon:
                sh.text(bx + bw / 2 + 7, 46, label, 8); icon_at(sh, icon, bx + bw / 2 - len(label) * 2.4 - 15, 36, .32)
            else:
                sh.text(bx + bw / 2, 46, label, 8)
    sh = Sheet(); head(sh, heading)
    sh.text(100, 26, intro, 6.5)
    boxes(sh)
    items = [fn for _, fns, _ in cats for fn in fns]
    random.Random(seed).shuffle(items)
    C = 36; cols = 4 if len(items) <= 12 else 5; gx = 100 - cols * C / 2; gy = 160
    for k, fn in enumerate(items):
        r, c = divmod(k, cols); icon_at(sh, fn, gx + c * C + 3, gy + r * C + 3, .75)
    rows = (len(items) + cols - 1) // cols
    for r in range(rows + 1): sh.seg(gx, gy + r * C, gx + cols * C, gy + r * C, "cut")
    for c in range(cols + 1): sh.seg(gx + c * C, gy, gx + c * C, gy + rows * C, "cut")
    sh.legend(["cut"], 277)
    an = Sheet(); head(an, "Antwoorden"); boxes(an)
    C2 = 28; per = {2: 3, 3: 2, 4: 1}[n]
    for i, (_, fns, _) in enumerate(cats):
        bx = 6 + i * (bw + 4)
        for k, fn in enumerate(fns):
            r, c = divmod(k, per)
            x = bx + bw / 2 - per * C2 / 2 + c * C2 + 1; y = 56 + r * C2
            an.rect_line(x, y, C2 - 2, C2 - 2, "l", 2, "stroke-width:.6"); icon_at(an, fn, x + 1, y + 1, .6)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": 20,
        "materials": [KLEUR, SCHAAR, {"slug": "lijmstift", "optional": True}],
        "i18n": {"nl": {"name": name, "steps": steps + ["Kijk samen na met het antwoordblad. Klopt alles? Plak de kaartjes dan vast."]}}},
        [("antwoorden", "Antwoorden", an)])

# ---------- drijft of zinkt ----------
def ic_badeend(p):
    p.add(sample("M5 24C5 18 12 17 18 20C18 12 22 8 27 8C32 8 35 12 34 17C33 20 31 21 30 22C36 22 37 26 35 29C32 34 24 35 16 35C8 35 5 30 5 24Z"), "y")
    p.add(sample("M33 15L40 16L34 19Z"), "o"); p.dot(29, 13, 1.4)
    p.ln(sample("M12 26Q18 31 25 26", 6), style="stroke-width:1.2")
def ic_kurk(p):
    p.add([(8, 13), (30, 15), (30, 27), (8, 29)], "w"); p.add(ellp(8, 21, 4, 8), "w"); p.add(ellp(30, 21, 3.2, 6), "w")
    for x, y in [(14, 18), (20, 23), (25, 19), (16, 25), (29, 20), (31, 23)]: p.dot(x, y, .9)
def ic_blad(p):
    p.add(sample("M6 34C4 18 16 6 34 6C34 22 22 34 6 34Z"), "g"); p.ln([(6, 34), (30, 10)], style="stroke-width:1.2")
    for t in (.35, .6): x, y = 6 + 24 * t, 34 - 24 * t; p.ln([(x, y), (x - 5, y - 7)], style="stroke-width:1"); p.ln([(x, y), (x + 7, y + 5)], style="stroke-width:1")
def ic_strandbal(p):
    p.add(circ(20, 20, 15), "-")
    p.add(sample("M20 5C12 12 12 28 20 35C16 28 16 12 20 5Z"), "r", sil=False)
    p.add(sample("M20 5C28 12 28 28 20 35C24 28 24 12 20 5Z"), "b", sil=False)
    p.add(sample("M20 5C8 8 5 18 6 24C10 14 15 8 20 5Z"), "y", sil=False)
    p.add(circ(20, 20, 3), "-", sil=False)
def ic_appel(p): p.add(sample("M20 12C12 6 4 12 6 22C8 32 14 36 20 33C26 36 32 32 34 22C36 12 28 6 20 12Z"), "r"); p.ln([(20, 12), (21, 5)]); p.add(ellp(26, 7, 5, 2.5, -20), "g")
def ic_stammetje(p):
    p.add(sample("M8 14H30V30H8Z"), "w"); p.add(ellp(8, 22, 4, 8), "w"); p.add(ellp(30, 22, 4, 8), "y")
    p.add(ellp(30, 22, 2, 4.5), "y", sil=False); p.ln(sample("M12 18Q18 16 24 18", 4), style="stroke-width:1"); p.ln(sample("M14 26Q20 28 26 26", 4), style="stroke-width:1")
    p.add(sample("M18 14L20 8Q22 10 21 14Z"), "g")
def ic_steen(p): p.add(sample("M6 28C4 20 10 12 18 12C24 10 32 14 34 22C36 30 30 34 20 34C12 34 7 32 6 28Z"), "z"); p.ln(sample("M12 20Q16 17 20 18", 4), style="stroke-width:1")
def ic_sleutel(p):
    p.add(circ(11, 20, 7), "y"); p.add(circ(11, 20, 3), "-", sil=False)
    p.add(rect(17, 18, 18, 4), "y"); p.add(rect(26, 22, 3, 5), "y"); p.add(rect(31, 22, 3, 7), "y")
def ic_munt(p):
    p.add(circ(20, 20, 14), "y"); p.circle = None
    p.sh.circle_line(p.dx + 20 * p.sc, p.dy + 20 * p.sc, 10.5 * p.sc, "l", f"stroke-width:{1 * p.sc}")
    p.text(20, 25.5, "1", 14)
def ic_knikker(p):
    p.add(circ(20, 20, 13), "b"); p.add(sample("M12 16C16 10 24 12 22 18C20 24 28 26 30 20C30 30 18 32 13 26C10 22 10 19 12 16Z"), "n", sil=False)
    p.add(circ(15, 13, 2.2), "-", sil=False)
def ic_lepel(p):
    p.add(ellp(12, 12, 7, 9, -45), "z"); p.add(bar(16, 16, 34, 34, 2), "z")
def ic_spijker(p):
    p.add(rrect(10, 4, 20, 5, 1.5), "z"); p.add(rect(18, 9, 4, 22), "z"); p.add([(18, 31), (22, 31), (20, 37)], "z")
sorteer("sorteren-drijft-of-zinkt", "Sorteren: drijft het of zinkt het?", "Drijft het of zinkt het?", [
    ("Drijft", [ic_badeend, ic_kurk, ic_blad, ic_strandbal, ic_appel, ic_stammetje], None),
    ("Zinkt", [ic_steen, ic_sleutel, ic_munt, ic_knikker, ic_lepel, ic_spijker], None)], "leren", "4-6", [
    "Kleur de plaatjes in en knip de kaartjes los langs de streepjeslijnen.",
    "Wat gebeurt er als je het in een bak water legt? Blijft het bovenop drijven, of zakt het naar de bodem? Leg elk kaartje in het goede vak.",
    "Twijfel je? Probeer het samen uit met een bak water en echte spullen (geen munt of spijker in je mond stoppen!)."], 21, diff=2)

# ---------- keuken of badkamer ----------
def ic_kookpan(p):
    p.add(rrect(8, 16, 24, 18, 3), "z"); p.add(rect(2, 18, 6, 3), "x"); p.add(rect(32, 18, 6, 3), "x")
    p.add(rrect(6, 12, 28, 4, 1.5), "z"); p.add(rrect(17, 8, 6, 4, 1.5), "x")
def ic_garde(p):
    p.add(rect(18, 26, 4, 12), "w")
    for w in (3, 7, 11): p.ln(sample(f"M18.5 26C{20 - w} 18 {20 - w} 4 20 3C{20 + w} 4 {20 + w} 18 21.5 26", 10), style="stroke-width:1.2")
def ic_deegroller(p):
    p.add(rrect(10, 15, 20, 10, 3), "w"); p.add(rrect(2, 18, 8, 4, 2), "w"); p.add(rrect(30, 18, 8, 4, 2), "w")
def ic_theepot(p):
    p.add(sample("M30 18C36 16 36 24 31 28L30 26C33 23 33 20 30 20Z"), "m")
    p.add(sample("M10 22L3 14L5 13L12 18Z"), "m")
    p.add(sample("M8 20C8 12 32 12 32 20C32 30 26 34 20 34C14 34 8 30 8 20Z"), "m"); p.add(ellp(20, 13, 8, 2.5), "m"); p.add(circ(20, 9.5, 2), "m")
    p.add(circ(20, 24, 3), "-", sil=False)
def ic_broodrooster(p):
    p.add(sample("M12 14V8C12 4 16 4 16 8V14Z"), "y"); p.add(sample("M23 14V8C23 4 27 4 27 8V14Z"), "y")
    p.add(rrect(6, 14, 28, 20, 4), "z"); p.add(rect(34, 18, 3, 2), "x"); p.ln([(12, 18), (16, 18)]); p.ln([(23, 18), (27, 18)])
def ic_koekenpan(p):
    p.add(ellp(16, 22, 13, 8), "x"); p.add(ellp(16, 21, 10, 5.5), "z", sil=False); p.add(bar(28, 20, 39, 14, 1.8), "w")
    p.add(ellp(15, 21, 5, 3), "-", sil=False); p.add(circ(15, 21, 1.8), "y", sil=False)
def ic_tandenborstel(p):
    p.add(sample("M10 16H30L28 36H12Z"), "b")
    p.add(bar(16, 18, 22, 2, 1.4), "g"); p.add(rect(20, 1, 5, 5), "-")
    p.add(bar(24, 18, 28, 5, 1.4), "r")
def ic_zeep(p):
    p.add(rrect(8, 16, 24, 14, 6), "k")
    for x, y, r in [(12, 11, 3), (18, 8, 2), (29, 12, 2.5)]: p.circle_line = None; p.add(circ(x, y, r), "-")
def ic_handdoek(p):
    p.add(rect(4, 6, 32, 3), "w"); p.add(rect(9, 9, 22, 26), "t"); p.add(rect(9, 27, 22, 4), "-", sil=False)
def ic_douchekop(p):
    p.ln(sample("M6 4V12Q6 16 12 16H20", 6), style="stroke-width:2.2")
    p.add(sample("M18 12H32L30 18H20Z"), "z")
    for x in (21, 25, 29): p.ln([(x, 21), (x - 1, 30)], style="stroke-width:1.2")
def ic_wcrol(p):
    p.add(rect(8, 10, 18, 24), "-"); p.add(ellp(26, 22, 5, 12), "-"); p.add(ellp(26, 22, 2, 4.5), "z", sil=False)
    p.add(ellp(8, 22, 5, 12), "-") if False else None
    p.add(sample("M8 34H32V38H8Z"), "-") if False else None
sorteer("sorteren-keuken-of-badkamer", "Sorteren: hoort het in de keuken of in de badkamer?", "Keuken of badkamer?", [
    ("Keuken", [ic_kookpan, ic_garde, ic_deegroller, ic_theepot, ic_broodrooster, ic_koekenpan], None),
    ("Badkamer", [ic_tandenborstel, ic_zeep, ic_handdoek, ic_douchekop, ic_wcrol, ic_badeend], None)], "thuis", "2-4", [
    "Kleur de plaatjes in. Een volwassene helpt met het losknippen van de kaartjes.",
    "Wat is het en waar gebruik je het? Bij het koken in de keuken, of bij het wassen in de badkamer? Leg elk kaartje in het goede vak."], 31)

# ---------- afval scheiden ----------
def ic_krant(p):
    p.add(rect(6, 6, 28, 30), "-"); p.add(rect(10, 10, 20, 5), "z", sil=False)
    for y in (19, 23, 27, 31): p.ln([(10, y), (19, y)], style="stroke-width:.9"); p.ln([(22, y), (30, y)], style="stroke-width:.9")
def ic_doos(p):
    p.add([(6, 16), (26, 16), (26, 36), (6, 36)], "w"); p.add([(26, 16), (34, 10), (34, 30), (26, 36)], "w")
    p.add([(6, 16), (14, 10), (34, 10), (26, 16)], "w"); p.add([(6, 16), (2, 9), (10, 5), (14, 10)], "w")
    p.ln([(6, 26), (26, 26)], style="stroke-width:1")
def ic_envelop(p): p.add(rect(4, 10, 32, 22), "-"); p.ln([(4, 10), (20, 23), (36, 10)], style="stroke-width:1.4"); p.add(rect(28, 13, 5, 6), "r", sil=False)
def ic_eierdoos(p):
    p.add(sample("M3 24H37L35 34Q32 30 29 34Q26 30 23 34Q20 30 17 34Q14 30 11 34Q8 30 5 34Z"), "z")
    p.add(sample("M3 24L7 14H33L37 24Z"), "z"); p.ln([(5, 24), (35, 24)], style="stroke-width:1")
def ic_fles(p):
    p.add(rrect(13, 14, 14, 23, 4), "b"); p.add(sample("M16 14Q16 9 18 8H22Q24 9 24 14Z"), "b"); p.add(rect(17, 3, 6, 5), "n")
    p.add(rect(13, 21, 14, 8), "-", sil=False)
def ic_shampoo(p):
    p.add(sample("M10 36V16Q10 12 14 12H26Q30 12 30 16V36Z"), "t"); p.add(rect(16, 6, 8, 6), "p"); p.add(rect(22, 4, 7, 3), "p")
    p.add(ellp(20, 25, 6, 4), "-", sil=False)
def ic_beker(p):
    p.add([(9, 12), (31, 12), (28, 36), (12, 36)], "-"); p.add(rrect(7, 8, 26, 4, 1.5), "r")
    p.ln(sample("M13 22Q20 26 27 22", 4), style="stroke-width:1")
def ic_tasje(p):
    p.add(sample("M7 14H33L31 36H9Z"), "-"); p.add(sample("M12 14V8Q12 4 15 4H25Q28 4 28 8V14H25V9Q25 7 23 7H17Q15 7 15 9V14Z"), "-")
    p.ln([(14, 22), (26, 22)], style="stroke-width:1")
def ic_bananenschil(p):
    p.add(sample("M20 14Q12 22 8 34Q14 30 18 22Q20 30 20 36Q24 28 22 20Q28 26 34 32Q30 20 22 14Z"), "y")
    p.add(rect(18, 7, 5, 8), "w")
def ic_klokhuis(p):
    p.add(sample("M15 8C11 8 11 12 14 16C16 19 16 22 15 25C14 28 13 31 16 34C18 35 22 35 24 34C27 31 26 28 25 25C24 22 24 19 26 16C29 12 29 8 25 8Z"), "y")
    p.add(rrect(14, 6, 12, 3, 1.5), "r"); p.ln([(20, 6), (21, 1)], style="stroke-width:1.4"); p.dot(19.5, 19, 1); p.dot(20.5, 23, 1)
def ic_eierschaal(p):
    p.add(sample("M4 30C4 22 8 18 13 18L15 22L18 19L21 23L22 30Q14 34 4 30Z"), "-")
    p.add(sample("M20 34C20 26 24 20 30 20C35 20 37 26 36 30L33 28L31 31L28 28L25 32Z"), "-")
def ic_herfstblad(p):
    p.add(sample("M20 36V30L10 32L12 26L4 22L10 18L6 10L14 12L16 4L20 10L24 4L26 12L34 10L30 18L36 22L28 26L30 32L20 30Z"), "o")
    p.ln([(20, 36), (20, 12)], style="stroke-width:1.1")
sorteer("sorteren-afval-scheiden", "Sorteren: afval scheiden in papier, plastic en gft", "Afval scheiden", [
    ("Papier", [ic_krant, ic_doos, ic_envelop, ic_eierdoos], None),
    ("Plastic", [ic_fles, ic_shampoo, ic_beker, ic_tasje], None),
    ("Gft", [ic_bananenschil, ic_klokhuis, ic_eierschaal, ic_herfstblad], None)], "thuis", "6-9", [
    "Kleur de plaatjes in en knip de kaartjes los langs de streepjeslijnen.",
    "Waar hoort elk stuk afval? Oud papier en karton gaan bij papier. Flessen, bekers en zakjes van plastic gaan bij plastic. Etensresten, schillen en bladeren gaan bij gft (groente, fruit en tuin).",
    "Leg elk kaartje in de goede bak. Kijk daarna samen hoe jullie thuis afval scheiden: dat is niet in elke gemeente precies hetzelfde."], 41, diff=2)

# ---------- uit een ei of geboren ----------
def ic_kip(p): wrap(bd_kip, .9, 18, 24)(p)
def ic_schildpad(p):
    for x in (10, 26): p.add(ellp(x, 30, 3.5, 4), "l")
    p.add(ellp(34, 22, 6, 4.5), "l"); p.add([(4, 26), (0, 28), (5, 29)], "l")
    p.add(sample("M4 28C4 14 32 14 32 28Z"), "g")
    p.ln([(10, 28), (13, 20), (23, 20), (26, 28)], style="stroke-width:1"); p.ln([(18, 20), (18, 28)], style="stroke-width:1"); p.dot(36, 21, 1)
def ic_krokodil(p):
    p.add(sample("M1 22Q8 16 16 18H30L39 20L39 24L30 25Q30 28 26 28H12Q6 28 1 22Z"), "g")
    for x in (12, 24): p.add(rect(x - 2, 26, 4, 6), "g")
    for x in (10, 15, 20, 25): p.add([(x - 2, 18), (x, 15), (x + 2, 18)], "g")
    p.add(circ(28, 17, 2.5), "g"); p.dot(28, 16.5, 1); p.ln([(30, 22), (39, 22)], style="stroke-width:1")
def ic_kikker(p):
    for s in (-1, 1): p.add(ellp(20 + s * 12, 32, 6, 3), "g")
    p.add(ellp(20, 25, 12, 9), "g")
    for s in (-1, 1): p.add(circ(20 + s * 7, 14, 5), "g"); p.add(circ(20 + s * 7, 14, 2.8), "-", sil=False); p.dot(20 + s * 7, 14, 1.3)
    p.ln(sample("M13 25Q20 30 27 25", 4), style="stroke-width:1.2")
def ic_kat(p):
    p.ln(sample("M30 30Q38 28 36 18", 6), style="stroke-width:2.4")
    p.add(sample("M10 36C8 26 12 20 20 20C28 20 32 26 30 36Z"), "o")
    p.add([(10, 12), (11, 3), (17, 8)], "o"); p.add([(30, 12), (29, 3), (23, 8)], "o")
    p.add(circ(20, 14, 10), "o"); p.dot(16, 13, 1.4); p.dot(24, 13, 1.4); p.add([(18.5, 17), (21.5, 17), (20, 19)], "m")
    for s in (-1, 1): p.ln([(20 + s * 4, 18.5), (20 + s * 12, 17)], style="stroke-width:.8")
def ic_koe(p):
    for x in (9, 14, 25, 30): p.add(rect(x - 1.8, 24, 3.6, 11), "-")
    p.add(rrect(5, 12, 30, 15, 6), "-"); p.add(sample("M10 13C12 18 18 18 18 13Z"), "x", sil=False); p.add(ellp(26, 20, 4, 3), "x", sil=False)
    p.add(ellp(36, 13, 5, 7), "-"); p.add(ellp(36, 18, 4.5, 3), "k"); p.dot(34.5, 11, 1.1)
    p.add([(33, 7), (32, 3), (35, 6)], "y"); p.add([(39, 7), (40, 3), (37, 6)], "y")
    p.ln(sample("M5 15Q1 18 2 24", 4), style="stroke-width:1.2")
sorteer("sorteren-uit-een-ei-of-geboren", "Sorteren: komt het dier uit een ei of wordt het geboren?", "Uit een ei of geboren?", [
    ("Uit een ei", [ic_kip, ic_vogel, ic_schildpad, ic_krokodil, ic_kikker, ic_slak], None),
    ("Geboren", [ic_hond, ic_kat, ic_koe, ic_olifant, ic_muis, ic_giraf], None)], "dieren", "4-6", [
    "Kleur de dieren in en knip de kaartjes los langs de streepjeslijnen.",
    "Sommige babydieren kruipen uit een ei. Andere groeien in de buik van hun moeder en worden geboren, net als jij. Leg elk dier in het goede vak."], 52, diff=2)

# =====================================================================
# Knip-en-plak-collages: een knipvel met losse stukjes en een plakvel
# =====================================================================
def collage(slug, name, heading, pieces_page, glue_page, cat, age, steps, minutes=30, holiday=None, diff=2, adult=False):
    sh = Sheet(); head(sh, heading)
    pieces_page(sh); sh.legend(["cut"], 277)
    pv = Sheet(); glue_page(pv)
    meta = {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": minutes,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": name, "printNote": "Print beide pagina's: de eerste is het knipvel, de tweede het plakvel.", "steps": steps}}}
    if adult: meta["adultHelp"] = True
    if holiday: meta["holiday"] = holiday
    write(OUT, slug, sh, meta, [("extra", "Plakvel", pv)])
def crenel(x0, x1, y, h=4, n=None):
    """Kantelen: punten van links naar rechts langs de bovenkant."""
    n = n or max(2, round((x1 - x0) / 6)); w = (x1 - x0) / (2 * n - 1); out = []
    for i in range(2 * n - 1):
        xa, xb = x0 + i * w, x0 + (i + 1) * w
        yy = y - h if i % 2 == 0 else y
        out += [(xa, yy), (xb, yy)]
    return out

# ---------- bouw een kasteel ----------
def ks_toren(pc):
    pc.add([(0, 70)] + crenel(0, 22, 4, 5, 3) + [(22, 70)], "z")
    for y in (20, 34, 48, 62): pc.ln([(0, y), (22, y)], style="stroke-width:.8")
    for y, xs in [(13, (6, 15)), (27, (2, 11, 18)), (41, (6, 15)), (55, (2, 11, 18))]:
        for x in xs: pc.ln([(x, y), (x, y + 7)], style="stroke-width:.8")
def ks_muur(pc):
    pc.add([(0, 40)] + crenel(0, 56, 4, 5, 6) + [(56, 40)], "z")
    for y in (14, 24, 34): pc.ln([(0, y), (56, y)], style="stroke-width:.8")
    for k in range(6): pc.ln([(4 + k * 10 + (5 if k % 2 else 0), 14), (4 + k * 10 + (5 if k % 2 else 0), 24)], style="stroke-width:.8")
def ks_poort(pc):
    pc.add(sample("M0 30V10C0 0 22 0 22 10V30Z"), "w")
    for x in (5.5, 11, 16.5): pc.ln([(x, 2), (x, 30)], style="stroke-width:1")
    for y in (9, 16, 23): pc.ln([(0, y), (22, y)], style="stroke-width:1")
def ks_dak(pc): pc.add([(0, 26), (13, 0), (26, 26)], "r"); pc.add(rect(0, 26, 26, 3), "r")
def ks_vlag(code):
    def fn(pc):
        pc.add(rect(0, 0, 2, 22), "w"); pc.add([(2, 1), (16, 5), (2, 10)], code); pc.add(circ(1, -.5, 1.8), "y")
    return fn
def ks_raam(pc): pc.add(sample("M0 14V5C0 -1 10 -1 10 5V14Z"), "x"); pc.ln([(5, 0), (5, 14)], style="stroke-width:1")
def ks_brug(pc):
    pc.add(rect(0, 0, 22, 30), "w")
    for y in (6, 12, 18, 24): pc.ln([(0, y), (22, y)], style="stroke-width:1")
    for x in (2, 20): pc.add(circ(x, 2, 1.4), "z", sil=False)
def ks_ridder(pc):
    pc.add(rect(4, 26, 4, 12), "z"); pc.add(rect(12, 26, 4, 12), "z")
    pc.add(rrect(2, 12, 16, 16, 3), "z"); pc.add(sample("M10 0C3 0 3 6 3 12H17C17 6 17 0 10 0Z"), "z")
    pc.add(rect(3, 5, 14, 2.5), "x", sil=False)
    pc.add(sample("M10 0Q12 -6 18 -6Q14 -3 12 1Z"), "r")
    pc.add(sample("M-6 14H4V22Q4 28 -1 30Q-6 28 -6 22Z"), "b"); pc.add(rect(17, 6, 2, 22), "z"); pc.add(rect(14, 22, 8, 2), "w")
def ks_draak(pc):
    pc.add(sample("M18 10L30 0L28 12L36 6L32 18Z"), "l")
    pc.add(sample("M4 26C2 16 10 10 20 12C26 13 30 18 30 24C34 22 38 24 40 20C42 26 36 30 30 30H8Z"), "g")
    pc.add(sample("M4 16C0 14 -2 8 2 4C6 2 10 6 10 10L12 14C8 16 6 16 4 16Z"), "g"); pc.dot(4, 8, 1.2)
    for x in (10, 22): pc.add(rect(x, 28, 4, 6), "g")
    pc.add(sample("M-2 8Q-8 6 -10 9Q-7 10 -2 10Z"), "o")
def kasteel_knip(sh):
    sh.text(100, 25, "Kleur de stukjes, knip ze uit en bouw je eigen kasteel.", 6)
    pack(sh, [[ks_toren, ks_toren, ks_muur],
              [ks_poort, ks_dak, ks_dak, ks_brug],
              [ks_vlag("r"), ks_vlag("b"), ks_vlag("y"), ks_raam, ks_raam, ks_raam, ks_raam],
              [ks_ridder, ks_draak]], gap=3)
def kasteel_plak(sh):
    head(sh, "Mijn kasteel")
    sh.region(cloud_path(40, 50, 12), "-"); sh.region(cloud_path(150, 64, 10), "-")
    sh.circle_r(176, 38, 11, "y")
    sh.region("M0 262V176Q50 160 100 170T200 172V262Z", "l") if False else sh.region("M0 262V176Q50 160 100 170Q150 180 200 168V262Z", "l")
    sh.region("M0 230Q100 214 200 228V246Q100 234 0 248Z", "b")
    for x in (40, 110, 160): sh.line(f"M{x - 6} 236q3 -2 6 0t6 0", "l", "stroke-width:1.1")
    sh.line("M24 202H176", "guide", "stroke-dasharray:3 3"); sh.text(100, 198, "zet je kasteel op deze lijn", 5, cls="tip")
    sh.text(100, 271, "Hoe heet jouw kasteel? ...............................", 6.5)
collage("bouw-een-kasteel-plakken", "Bouw een kasteel: knippen en plakken", "Kasteel: knipvel", kasteel_knip, kasteel_plak, "sprookjes", "4-6", [
    "Kleur de torens, de muur, de poort, de daken en de vlaggen in. Vergeet de ridder en het draakje niet.",
    "Kleur op het plakvel de lucht, de heuvel en de slotgracht.",
    "Knip alle stukjes uit langs de streepjeslijn.",
    "Zet de muur met de poort op de stippellijn, met een toren aan elke kant. Plak de daken bovenop de torens en de vlaggen op de daken.",
    "Plak de ramen in de torens en de brug onder de poort, over de slotgracht. Waar staan de ridder en het draakje?"], minutes=35)

# ---------- pizza beleggen ----------
def pz_salami(pc):
    pc.add(circ(0, 0, 8), "r")
    for x, y in [(-3, -3), (3.5, -1), (-1, 4)]: pc.add(circ(x, y, 1.5), "-", sil=False)
def pz_champignon(pc):
    pc.add(sample("M-9 0C-9 -8 9 -8 9 0Q5 1 3 0V8H-3V0Q-5 1 -9 0Z"), "-")
    pc.ln(sample("M-6 -1Q0 -3 6 -1", 4), style="stroke-width:.8")
def pz_paprika(code):
    def fn(pc): pc.add(sample("M-10 0Q0 -9 10 0L8 2Q0 -5 -8 2Z"), code)
    return fn
def pz_olijf(pc): pc.add(circ(0, 0, 4.5), "x"); pc.add(circ(0, 0, 1.8), "-", sil=False)
def pz_tomaat(pc):
    pc.add(circ(0, 0, 8.5), "r"); pc.add(circ(0, 0, 6), "r", sil=False)
    for a in range(0, 360, 72):
        t = math.radians(a); pc.add(ellp(3.4 * math.cos(t), 3.4 * math.sin(t), 1, 1.8, a + 90), "y", sil=False)
def pz_blad(pc): pc.add(sample(leaf_path(0, 0, 5, 9)), "g"); pc.ln([(0, -7), (0, 7)], style="stroke-width:.8")
def pz_ananas(pc): pc.add([(-6, 4), (0, -6), (6, 4)], "y"); pc.ln([(-2, 0), (2, 0)], style="stroke-width:.8")
def pz_ham(pc): pc.add(sample("M-9 -5Q-2 -9 8 -6Q11 0 7 6Q0 9 -8 5Q-11 0 -9 -5Z"), "k")
def pizza_knip(sh):
    sh.text(100, 25, "Kleur het beleg in, knip het uit en maak je eigen pizza.", 6)
    pack(sh, [[pz_salami] * 6, [pz_tomaat] * 4 + [pz_ham] * 2, [pz_champignon] * 6,
              [pz_paprika("g")] * 3 + [pz_paprika("r")] * 3, [pz_olijf] * 8, [pz_blad] * 5 + [pz_ananas] * 4], gap=3, k=2.2)
def pizza_plak(sh):
    head(sh, "Mijn pizza")
    sh.rect_r(10, 40, 180, 200, "w", 6)
    sh.circle_r(100, 140, 86, "o"); sh.circle_r(100, 140, 74, "r")
    for a in range(0, 360, 30):
        t = math.radians(a); x, y = 100 + 80 * math.cos(t), 140 + 80 * math.sin(t)
        sh.line(f"M{f(x)} {f(y)}l{f(2 * math.cos(t + 1.6))} {f(2 * math.sin(t + 1.6))}", "l", "stroke-width:1")
    for x, y in [(70, 110), (130, 120), (95, 175), (120, 160), (80, 150), (110, 95)]:
        sh.line(f"M{x} {y}q3 -2 6 0", "l", "stroke-width:1")
    sh.text(100, 256, "Pizza ................................", 8)
    sh.text(100, 270, "Bedenk een naam voor jouw pizza!", 6)
collage("pizza-beleggen-plakken", "Pizza beleggen: knippen en plakken", "Pizza: knipvel", pizza_knip, pizza_plak, "eten", "4-6", [
    "Kleur het beleg in: salami, tomaat, ham, champignons, paprika, olijven, basilicum en ananas.",
    "Kleur op het plakvel de korst lichtbruin en de tomatensaus rood.",
    "Knip alles uit langs de streepjeslijn. De kleine stukjes zijn een mooie knipoefening.",
    "Kies wat jij lekker vindt en plak het op de pizza. Je hoeft niet alles te gebruiken.",
    "Geef je pizza een naam en schrijf die eronder. Speel samen pizzeria!"])

# ---------- ijsjes ----------
def ij_bol(code):
    def fn(pc):
        pc.add(sample("M-16 6C-20 -4 -12 -16 0 -16C12 -16 20 -4 16 6Q12 10 8 6Q4 11 0 6Q-4 11 -8 6Q-12 10 -16 6Z"), code)
        pc.ln(sample("M-8 -8Q-6 -11 -2 -12", 4), style="stroke-width:1")
    return fn
def ij_kers(pc): pc.add(circ(0, 4, 6), "r"); pc.ln(sample("M0 -2Q2 -8 6 -10", 4), style="stroke-width:1.4"); pc.sil(bar(0, -2, 6, -10, 1))
def ij_wafel(pc):
    pc.add([(-4, 12), (-6, -10), (6, -12), (4, 12)], "w")
    for y in (-4, 4): pc.ln([(-5, y), (5, y - 1)], style="stroke-width:.8")
def ij_spikkels(pc):
    pc.add(rrect(-14, -6, 28, 12, 5), "-")
    for k, (x, y, a) in enumerate([(-9, -2, 30), (-4, 2, -20), (1, -3, 60), (6, 2, 10), (10, -2, -40), (-10, 3, 80), (3, 3, -70)]):
        t = math.radians(a); pc.ln([(x - 1.6 * math.cos(t), y - 1.6 * math.sin(t)), (x + 1.6 * math.cos(t), y + 1.6 * math.sin(t))], style="stroke-width:1.4")
def ijs_knip(sh):
    sh.text(100, 25, "Kleur de bolletjes ijs in je lievelingssmaken en knip ze uit.", 6)
    pack(sh, [[ij_bol("m"), ij_bol("w"), ij_bol("y")], [ij_bol("l"), ij_bol("k"), ij_bol("o")], [ij_bol("r"), ij_bol("b"), ij_bol("-")],
              [ij_kers, ij_kers, ij_wafel, ij_wafel, ij_spikkels]], gap=4, k=2.4)
def ijs_plak(sh):
    head(sh, "Mijn ijsjes")
    sh.text(100, 27, "Plak bolletjes op de hoorntjes. Hoeveel bolletjes heeft elk ijsje?", 6)
    for cx in (55, 145):
        sh.poly_r([(cx - 26, 170), (cx + 26, 170), (cx, 252)], "w")
        A, B, C = (cx - 26, 170), (cx + 26, 170), (cx, 252)
        for t in (.2, .4, .6, .8):
            P_ = (A[0] + t * (B[0] - A[0]), 170)
            Q1 = (B[0] + (1 - t) * (C[0] - B[0]), B[1] + (1 - t) * (C[1] - B[1])); Q2 = (A[0] + t * (C[0] - A[0]), A[1] + t * (C[1] - A[1]))
            sh.seg(P_[0], P_[1], Q1[0], Q1[1], "l", "stroke-width:1"); sh.seg(P_[0], P_[1], Q2[0], Q2[1], "l", "stroke-width:1")
        sh.rect_line(cx - 22, 254, 44, 12, "l", 3, "stroke-width:1"); sh.text(cx - 14, 262.5, "bolletjes:", 4.6, "start", "tip")
collage("ijsjes-stapelen-plakken", "IJsjes stapelen: knippen en plakken", "IJsjes: knipvel", ijs_knip, ijs_plak, "eten", "2-4", [
    "Kleur de bolletjes ijs in. Welke smaak is roze? En bruin? Een volwassene helpt met knippen.",
    "Knip de bolletjes, de kersen, de wafeltjes en de spikkels uit.",
    "Plak de bolletjes op elkaar op de hoorntjes, met de golfjesrand naar beneden. Bovenop mag een kers of een wafeltje.",
    "Tel de bolletjes van elk ijsje en schrijf het getal in het vakje eronder."], minutes=20, diff=1, adult=True)

# ---------- bloementuin ----------
def stem(pc, h, leaf=True):
    pc.add(rect(-1.2, 0, 2.4, h), "g")
    if leaf: pc.add(ellp(5, h * .55, 5, 2.2, -30), "g"); pc.add(ellp(-5, h * .75, 5, 2.2, 30), "g")
def bt_tulp(code):
    def fn(pc):
        stem(pc, 34); pc.add(sample("M-8 2V-10L-4 -5L0 -12L4 -5L8 -10V2Q0 8 -8 2Z"), code)
    return fn
def bt_madelief(pc):
    stem(pc, 34)
    for a in range(0, 360, 30):
        t = math.radians(a); pc.add(ellp(7 * math.cos(t), 7 * math.sin(t), 4.5, 1.8, a), "-")
    pc.add(circ(0, 0, 3.6), "y")
def bt_zonnebloem(pc):
    stem(pc, 44)
    for a in range(0, 360, 24):
        t = math.radians(a); pc.add(ellp(10 * math.cos(t), 10 * math.sin(t), 5, 2.4, a), "y")
    pc.add(circ(0, 0, 6.5), "w")
    for x, y in [(-2, -2), (2, -2), (0, 2), (-3, 2), (3, 2), (0, -4)]: pc.dot(x, y, .7)
def bt_bolbloem(code):
    def fn(pc):
        stem(pc, 30)
        for a in range(0, 360, 72):
            t = math.radians(a - 90); pc.add(circ(5 * math.cos(t), 5 * math.sin(t), 4.5), code)
        pc.add(circ(0, 0, 3), "y")
    return fn
def bt_klokje(pc):
    pc.add(sample("M0 34V8Q0 -2 8 -4"), "g") if False else None
    pc.ln(sample("M0 34Q-1 10 6 -4", 8), style="stroke-width:1.6"); pc.sil(bar(0, 34, 6, -4, 1.2))
    for (x, y) in [(5, 0), (2, 10), (0, 20)]:
        pc.add(sample(f"M{x - 3} {y}H{x + 3}L{x + 4.5} {y + 6}L{x + 3} {y + 5}L{x + 1.5} {y + 6.5}L{x} {y + 5}L{x - 1.5} {y + 6.5}L{x - 3} {y + 5}L{x - 4.5} {y + 6}Z"), "p")
    pc.add(ellp(4, 30, 5, 2, -30), "g")
def bt_bij(pc):
    pc.add(ellp(-3, -7, 4, 5.5, -20), "-"); pc.add(ellp(4, -7, 4, 5.5, 20), "-")
    pc.add(ellp(0, 0, 9, 6), "y")
    for x in (-2, 3): pc.ln(sample(f"M{x} -5.5Q{x + 1.5} 0 {x} 5.5", 4), style="stroke-width:2")
    pc.add(circ(-10, 0, 4), "x"); pc.add([(9, -1), (12, 0), (9, 1)], "x")
def bt_vlinder(c1, c2):
    def fn(pc):
        for s in (-1, 1): pc.add(ellp(s * 7, -5, 7, 6, s * 20), c1); pc.add(ellp(s * 6, 6, 5, 4.5, -s * 20), c2)
        pc.add(ellp(0, 0, 2, 10), "x"); pc.ln(sample("M-1 -9Q-3 -14 -6 -15", 4), style="stroke-width:1.1"); pc.ln(sample("M1 -9Q3 -14 6 -15", 4), style="stroke-width:1.1")
        pc.sil(bar(-1, -9, -6, -15, 1)); pc.sil(bar(1, -9, 6, -15, 1))
    return fn
def bt_gieter(pc):
    pc.add(sample("M-14 -8L-26 -18L-24 -20L-12 -12Z"), "t"); pc.add(rrect(-26, -22, 5, 5, 1), "t")
    pc.add(rrect(-14, -12, 26, 22, 3), "t"); pc.add(sample("M12 -6C20 -6 20 6 12 6V3C16 3 16 -3 12 -3Z"), "t")
    pc.add(sample("M-8 -12Q0 -22 8 -12H5Q0 -18 -5 -12Z"), "t")
def bt_slak(pc): wrap(ic_slak, .9, -18, -22)(pc)
def bt_hek(pc):
    for k in range(5): pc.add(sample(f"M{k * 9} 24V2L{k * 9 + 3} -2L{k * 9 + 6} 2V24Z"), "w")
    pc.add(rect(-1, 6, 44, 3), "w"); pc.add(rect(-1, 16, 44, 3), "w")
def tuin_knip(sh):
    sh.text(100, 25, "Kleur de bloemen en de diertjes, knip ze uit en maak een tuin.", 6)
    pack(sh, [[bt_tulp("r"), bt_tulp("y"), bt_tulp("m"), bt_zonnebloem, bt_madelief, bt_madelief],
              [bt_bolbloem("b"), bt_bolbloem("o"), bt_klokje, bt_klokje, bt_gieter],
              [bt_bij, bt_bij, bt_vlinder("o", "y"), bt_vlinder("b", "p"), bt_slak],
              [bt_hek, bt_hek]], gap=3)
def tuin_plak(sh):
    head(sh, "Mijn bloementuin")
    sh.circle_r(30, 48, 12, "y")
    for a in range(0, 360, 45):
        t = math.radians(a); sh.seg(30 + 15 * math.cos(t), 48 + 15 * math.sin(t), 30 + 20 * math.cos(t), 48 + 20 * math.sin(t), "l", "stroke-width:1.4")
    sh.region(cloud_path(130, 50, 12), "-")
    sh.region("M0 262V150Q100 138 200 150V262Z", "l")
    for y0 in (190, 236):
        sh.region(f"M14 {y0}Q100 {y0 - 8} 186 {y0}L186 {y0 + 16}Q100 {y0 + 10} 14 {y0 + 16}Z", "w")
        for x in range(26, 180, 22): sh.dot(x, y0 + 7 + (x % 3), .9)
    sh.region("M150 150C150 136 158 128 168 128C178 128 186 136 186 150Z", "g")
    sh.text(100, 274, "Wie woont er in jouw tuin?", 6.5)
collage("bloementuin-plakken", "Bloementuin: knippen en plakken", "Bloementuin: knipvel", tuin_knip, tuin_plak, "natuur", "4-6", [
    "Kleur de bloemen, de bijen, de vlinders, de slak, de gieter en de hekjes in.",
    "Kleur op het plakvel het gras groen en de bloembedden bruin.",
    "Knip alles uit langs de streepjeslijn. Knip voorzichtig rond de dunne steeltjes.",
    "Plak de bloemen met hun steel in de bruine bloembedden. Zet het hekje achteraan en laat de bijen en vlinders boven de bloemen vliegen."])

def paardfig(pc, code="w", zebra=False, k=.9):
    def T_(pts): return [((x - 50) * k, (y - 50) * k) for x, y in pts]
    def addp(d, c): pc.add(T_(sample(d, 8)), c)
    addp("M27 46C18 48 15 58 19 67C22 60 24 54 29 50Z", "x")
    for x, y0 in [(31, 56), (36, 57), (55, 56), (60, 56)]:
        addp(f"M{x - 1.8} {y0}V70H{x + 1.8}V{y0}Z", code); addp(f"M{x - 2.2} 70H{x + 2.2}V72.5H{x - 2.2}Z", "x")
    addp("M26 48C26 40 36 40 46 41C54 42 58 40 62 34L68 22C70 20 72 20 74 22L82 31C84 34 82 36 79 36L72 34C68 34 66 38 64 44C64 52 62 58 56 60L32 60C26 60 26 54 26 48Z", code)
    if zebra:
        for x in (33, 39, 45, 51):
            pc.ln(T_([(x, 43), (x + 1, 51), (x - 1, 58)]), style="stroke-width:2.2")
        for (x1, y1), (x2, y2) in [((60, 37), (65, 41)), ((64, 30), (68, 34)), ((70, 26), (74, 29))]:
            pc.ln(T_([(x1, y1), (x2, y2)]), style="stroke-width:2")
    addp("M68 21L65 23L66 25L62 27L63 29L59 31L60 33L56 36L58 39L62 34L68 22Z", "x")
    addp("M69 22L70 15L73 21Z", code)
    (ex, ey), = T_([(73.5, 25.5)]); pc.dot(ex, ey, 1.2)
def bd_paard(pc): paardfig(pc, "w")
# ---------- dierentuin ----------
def dt_giraf(pc):
    def g(p):
        for x in (10, 14, 20, 24): p.sil(bar(x, 27, x, 38, 1.2))
        ic_giraf(p)
    wrap(g, 1.5, -18, -20)(pc)
def dt_olifant(pc): wrap(ic_olifant, 1.6, -20, -20)(pc)
def dt_leeuw(pc):
    pc.ln(sample("M12 4Q24 0 24 -10", 6), style="stroke-width:1.6"); pc.sil(bar(12, 4, 24, -10, 1)); pc.add(circ(24, -11, 2.4), "w")
    for x in (-10, -5, 6, 11): pc.add(rect(x - 2, 6, 4, 12), "y")
    pc.add(ellp(2, 4, 15, 8), "y")
    pc.add(union([circ(-14 + 9 * math.cos(math.radians(a)), -6 + 9 * math.sin(math.radians(a)), 4) for a in range(0, 360, 30)]), "o")
    pc.add(circ(-14, -6, 7), "y"); pc.dot(-17, -8, 1); pc.dot(-11, -8, 1); pc.add([(-15.5, -4), (-12.5, -4), (-14, -2)], "x")
    pc.ln(sample("M-17 -1Q-14 1 -11 -1", 4), style="stroke-width:1")
def dt_zebra(pc): paardfig(pc, '-', True, .75)
def dt_zebra_oud(pc):
    for x in (-10, -5, 6, 11): pc.add(rect(x - 2, 6, 4, 13), "-")
    pc.add(ellp(1, 3, 15, 8), "-")
    pc.add(sample("M-12 0L-16 -14L-20 -16Q-26 -14 -26 -9L-22 -6L-16 -5L-10 4Z"), "-")
    pc.add(sample("M-14 -12L-11 -18L-8 -15L-10 -4Z"), "x")
    for x in (-6, -1, 4, 9): pc.add(sample(f"M{x} -5Q{x + 2} 2 {x} 10L{x + 2} 10Q{x + 4} 2 {x + 2} -5Z"), "x", sil=False)
    pc.ln(sample("M16 2Q20 6 19 12", 4), style="stroke-width:1.4"); pc.sil(bar(16, 2, 19, 12, 1))
    pc.dot(-20, -12, 1)
def dt_pinguin(pc):
    pc.add(ellp(0, 2, 9, 14), "x"); pc.add(ellp(0, 5, 6, 10), "-")
    pc.add(circ(0, -11, 6.5), "x"); pc.add(ellp(-2, -11, 2, 2), "-", sil=False); pc.add(ellp(2, -11, 2, 2), "-", sil=False)
    pc.dot(-2, -11, .8); pc.dot(2, -11, .8); pc.add([(-2, -8), (2, -8), (0, -5)], "o")
    for s in (-1, 1): pc.add(ellp(s * 4, 16, 4, 2), "o")
def dt_aap(pc):
    pc.ln(sample("M8 10Q18 12 16 0Q14 -6 18 -8", 6), style="stroke-width:1.8"); pc.sil(taper(sample("M8 10Q18 12 16 0Q14 -6 18 -8", 6), 1.2, 1.2))
    pc.add(ellp(0, 6, 8, 10), "w"); pc.add(ellp(0, 8, 5, 6), "y")
    for s in (-1, 1): pc.add(bar(s * 6, 0, s * 12, -12, 2), "w"); pc.add(bar(s * 4, 14, s * 7, 22, 2.2), "w")
    for s in (-1, 1): pc.add(circ(s * 9, -12, 3.4), "w"); pc.add(circ(s * 9, -12, 1.8), "y", sil=False)
    pc.add(circ(0, -11, 8), "w"); pc.add(ellp(0, -9, 5.5, 5), "y"); pc.dot(-2.5, -12, 1); pc.dot(2.5, -12, 1); pc.ln(sample("M-2 -7Q0 -5.5 2 -7", 3), style="stroke-width:1")
def dt_palm(pc):
    pc.add(taper(sample("M0 40Q2 20 0 0", 6), 3, 2), "w")
    for a in (-160, -120, -60, -20, -90):
        t = math.radians(a); x, y = 16 * math.cos(t), 4 + 12 * math.sin(t) + (6 if abs(a + 90) > 50 else 0)
        pc.add(sample(f"M0 0Q{x * .5} {y - 8} {x} {y}Q{x * .5} {y - 2} 0 2Z"), "g")
    pc.add(circ(-2, 3, 2.4), "w"); pc.add(circ(2, 4, 2.4), "w")
def dt_rots(pc): pc.add(sample("M-20 10C-20 0 -12 -10 -2 -10C6 -14 18 -6 20 4C22 10 18 12 10 12H-16Q-20 12 -20 10Z"), "z"); pc.ln(sample("M-8 -2Q-4 -6 2 -4", 4), style="stroke-width:1")
def dt_bord(pc):
    pc.add(rect(-1.5, 0, 3, 18), "w"); pc.add(rrect(-16, -10, 32, 12, 2), "y"); pc.text(0, -1.8, "ZOO", 7)
def zoo_knip(sh):
    sh.text(100, 25, "Kleur de dieren, knip ze uit en zet ze in de dierentuin.", 6)
    pack(sh, [[dt_giraf, dt_olifant, dt_leeuw], [dt_zebra, dt_aap, dt_pinguin, dt_pinguin], [dt_palm, dt_palm, dt_rots, dt_bord]], gap=3)
def zoo_plak(sh):
    head(sh, "Mijn dierentuin")
    sh.region(cloud_path(40, 46, 11), "-"); sh.circle_r(172, 44, 11, "y")
    sh.region("M0 262V112Q100 100 200 112V262Z", "l")
    sh.region("M10 252V200Q60 190 110 200V252Z", "y")
    sh.region("M124 250C120 228 136 214 160 214C182 214 196 226 192 250Z", "b")
    for x in (138, 158, 176): sh.line(f"M{x - 5} 232q2.5 -2 5 0t5 0", "l", "stroke-width:1.1")
    def hek(x0, x1, y):
        sh.seg(x0, y - 10, x1, y - 10, "l", "stroke-width:1.2"); sh.seg(x0, y - 4, x1, y - 4, "l", "stroke-width:1.2")
        for x in range(int(x0), int(x1) + 1, 8): sh.seg(x, y - 14, x, y, "l", "stroke-width:1.2")
    hek(8, 192, 150); sh.seg(100, 150, 100, 192, "l", "stroke-width:1.2")
    sh.text(54, 247, "zand", 5, cls="tip"); sh.text(158, 247, "water", 5, cls="tip")
    sh.text(100, 274, "Welk dier woont waar?", 6.5)
collage("dierentuin-collage-plakken", "Dierentuin-collage: knippen en plakken", "Dierentuin: knipvel", zoo_knip, zoo_plak, "dieren", "4-6", [
    "Kleur de giraf, de olifant, de leeuw, de zebra, de aap en de pinguïns in. Vergeet de palmbomen, de rots en het bordje niet.",
    "Kleur op het plakvel het gras, het zand en het water.",
    "Knip alles uit langs de streepjeslijn.",
    "Zet de dieren in de dierentuin. De pinguïns wonen bij het water, de leeuw ligt graag op de rots in het zand. Plak alles vast."])

# ---------- vliegveld ----------
def vv_vliegtuig(code):
    def fn(pc):
        pc.add(sample("M-34 -2Q-34 -8 -26 -8H24Q34 -8 38 0Q34 6 24 6H-26Q-34 6 -34 -2Z"), "-")
        pc.add(sample("M-30 -6L-36 -22H-28L-18 -8Z"), code)
        pc.add(sample("M-4 2L-14 16H-6L10 2Z"), code)
        for x in range(-18, 22, 6): pc.add(rrect(x, -5, 3.6, 4, 1), "b", sil=False)
        pc.add(sample("M28 -6Q34 -6 36 -2H28Z"), "b", sil=False)
        pc.add(rect(-26, 0.5, 50, 2), code, sil=False)
    return fn
def vv_toren(pc):
    pc.add(rect(-4, -10, 8, 52), "-"); pc.add(sample("M-14 -24H14L10 -10H-10Z"), "b")
    pc.add(rect(-15, -27, 30, 3), "z"); pc.add(rect(-1, -36, 2, 9), "z"); pc.add(circ(0, -37, 2), "r")
    for y in (4, 18, 32): pc.add(rect(-2, y, 4, 5), "b", sil=False)
def vv_heli(pc): wrap(lambda p: (p.add(ellp(16, 24, 11, 8), "r"), p.add(bar(26, 22, 37, 20, 2), "r"), p.add(sample("M10 22Q10 18 16 18V24H10Z"), "b", sil=False), p.add(rect(4, 11, 24, 2), "z"), p.add(rect(15, 12, 2, 5), "z"), p.add(rect(8, 33, 16, 2), "z"), p.add(rect(11, 31, 2, 3), "z"), p.add(rect(19, 31, 2, 3), "z")), 1.3, -20, -22)(pc)
def vv_bagage(pc):
    pc.add(rect(-22, 4, 44, 4), "z")
    for x in (-16, 16): pc.add(circ(x, 11, 3.5), "x")
    pc.add(rrect(-20, -14, 14, 18, 2), "r"); pc.add(rrect(-4, -8, 12, 12, 2), "b"); pc.add(rrect(9, -18, 11, 22, 2), "y")
    for x in (-13, 2, 14.5): pc.ln([(x - 2, -14 if x < 0 else (-8 if x < 10 else -18)), (x - 2, -17 if x < 0 else (-11 if x < 10 else -21)), (x + 2, -17 if x < 0 else (-11 if x < 10 else -21)), (x + 2, -14 if x < 0 else (-8 if x < 10 else -18))], style="stroke-width:1.1")
    pc.ln([(-22, 6), (-30, 2)], style="stroke-width:1.4"); pc.sil(bar(-22, 6, -30, 2, 1))
def vv_tankwagen(pc):
    pc.add(rrect(-28, -10, 36, 16, 6), "y"); pc.add(sample("M10 6V-8H20L26 -2V6Z"), "r"); pc.add(sample("M13 -6H19L23 -2H13Z"), "b", sil=False)
    pc.add(rect(-30, 4, 58, 4), "z"); pc.text(-10, 0.5, "KEROSINE", 4.6)
    for x in (-20, -6, 18): pc.add(circ(x, 9, 4), "x")
def vv_trap(pc):
    pc.add(rect(-20, 4, 34, 6), "w"); pc.add([(-16, 4), (8, -20), (14, -20), (-8, 4)], "-")
    for k in range(1, 6): x = -14 + k * 4.2; y = 4 - k * 4.4; pc.ln([(x - 2, y), (x + 4, y)], style="stroke-width:1")
    pc.add(rect(14, -22, 4, 26), "z")
    for x in (-14, 8): pc.add(circ(x, 12, 3.4), "x")
def vv_windzak(pc):
    pc.add(rect(-1.5, -14, 3, 34), "z")
    pc.add(sample("M1 -14L26 -11L26 -5L1 -2Z"), "o")
    for x in (7, 13, 19): pc.ln([(x, -13.3 + (x - 1) * .12), (x, -2.7 - (x - 1) * .12)], style="stroke-width:1")
def vv_wolk(pc): pc.add(union([circ(-8, 2, 6), circ(0, -3, 8), circ(9, 2, 6), rect(-8, 2, 17, 6)]), "-")
def vliegveld_knip(sh):
    sh.text(100, 25, "Kleur alles in, knip het uit en maak een vliegveld.", 6)
    pack(sh, [[vv_vliegtuig("r"), vv_vliegtuig("n")], [vv_toren, vv_heli, vv_tankwagen], [vv_bagage, vv_trap, vv_windzak, vv_wolk, vv_wolk]], gap=3)
def vliegveld_plak(sh):
    head(sh, "Op het vliegveld")
    sh.circle_r(176, 42, 10, "y")
    sh.region("M0 262V128H200V262Z", "l")
    sh.rect_r(0, 196, 200, 46, "z")
    for x in range(8, 200, 24): sh.rect_r(x, 217, 12, 3, "-")
    sh.text(186, 210, "27", 9, rotate=-90)
    sh.rect_r(10, 132, 92, 40, "-"); sh.rect_r(10, 126, 92, 6, "b")
    for x in range(16, 100, 14): sh.rect_r(x, 140, 10, 12, "b")
    sh.rect_r(46, 156, 18, 16, "b"); sh.text(56, 131.6, "VLIEGVELD", 5)
    sh.rect_r(102, 180, 98, 16, "z")
    sh.text(100, 254, "Welk vliegtuig mag als eerste opstijgen?", 6.5)
collage("vliegveld-plakken", "Vliegveld: knippen en plakken", "Vliegveld: knipvel", vliegveld_knip, vliegveld_plak, "voertuigen", "6-9", [
    "Kleur de vliegtuigen, de verkeerstoren, de helikopter en de auto's in.",
    "Kleur op het plakvel het gras groen en de landingsbaan grijs. De strepen blijven wit.",
    "Knip alles uit langs de streepjeslijn.",
    "Zet de verkeerstoren naast het gebouw. Plak één vliegtuig op de landingsbaan en één bij het gebouw, met de trap en de bagagekar ernaast.",
    "Plak de helikopter, de wolken en de windzak waar jij wilt. Welke kant waait de wind op?"])

# ---------- boerderijdieren uit batch 13b (gekopieerd) ----------
def bd_koe(pc):
    pc.ln(sample("M-22 -4C-26 0 -27 6 -28 12", 6), style="stroke-width:1.6"); pc.sil(rect(-29, -4, 6, 16))
    pc.add(ellp(-28, 14, 2.6, 4), "x")
    for x in (-18, -9, 9, 17): pc.add(rect(x - 3, 6, 6, 18), "-"); pc.add(rect(x - 3, 21, 6, 4), "x", sil=False)
    pc.add(ellp(0, 0, 24, 14), "-")
    pc.add(ellp(3, 13, 5, 3), "k", sil=False)
    pc.add(sample("M-14 -12C-6 -14 -4 -6 -10 -2C-14 2 -20 -2 -20 -6C-20 -10 -18 -12 -14 -12Z"), "x", sil=False)
    pc.add(sample("M4 2C10 -2 16 2 14 8C12 12 4 10 4 2Z"), "x", sil=False)
    pc.add([(21, -22), (19, -30), (25, -24)], "y"); pc.add([(33, -22), (35, -30), (29, -24)], "y")
    pc.add(ellp(18, -18, 6, 3, -25), "-"); pc.add(ellp(36, -18, 6, 3, 25), "-")
    pc.add(rrect(19, -24, 16, 22, 7), "-")
    pc.add(ellp(27, -2, 9, 6), "k"); pc.dot(24, -2, 1.1); pc.dot(30, -2, 1.1)
    pc.dot(23, -14, 1.6); pc.dot(31, -14, 1.6)
def bd_varken(pc):
    pc.ln(sample("M-22 -4C-28 -6 -30 -12 -26 -14C-22 -15 -22 -10 -26 -9", 6), style="stroke-width:1.6")
    pc.sil(rect(-30, -15, 8, 12))
    for x in (-15, -6, 6, 13): pc.add(rect(x - 3, 6, 6, 13), "k")
    pc.add(ellp(0, 0, 22, 13), "k")
    pc.add([(16, -14), (17, -24), (24, -16)], "k"); pc.add([(26, -15), (31, -23), (32, -12)], "k")
    pc.add(circ(23, -6, 11), "k")
    pc.add(ellp(32, -3, 4.5, 6), "m"); pc.dot(31, -5, 1); pc.dot(31, -1, 1)
    pc.dot(24, -9, 1.6); pc.ln(sample("M20 -1Q23 2 26 0", 4), style="stroke-width:1.2")
def bd_schaap(pc):
    for x in (-14, -5, 6, 14): pc.add(rect(x - 2.2, 4, 4.4, 18), "x")
    pc.add(union([ellp(0, -2, 20, 11)] + [circ(*ept(0, -2, 20, 11, a), 7) for a in range(0, 360, 30)]), "-")
    for x, y in [(-10, -4), (2, -6), (-2, 4), (10, 2)]: pc.ln(sample(f"M{x - 3} {y}Q{x} {y - 4} {x + 3} {y}", 4), style="stroke-width:1")
    pc.add(ellp(26, -8, 7, 9, -25), "z"); pc.add(ellp(19, -12, 5, 2.5, 20), "z")
    pc.dot(27, -10, 1.5)
    for x, y in [(22, -17), (27, -18)]: pc.add(circ(x, y, 3.5), "-")

# =====================================================================
# Legpuzzels met legbord
# =====================================================================
def jig_edge(a, b, sgn):
    (ax, ay), (bx, by) = a, b; ux, uy = bx - ax, by - ay; nx, ny = -uy * sgn, ux * sgn
    def p(t, h): return f"{f(ax + ux * t + nx * h)} {f(ay + uy * t + ny * h)}"
    return f"L{p(.36, 0)}C{p(.40, 0)} {p(.42, -.05)} {p(.39, -.11)}C{p(.33, -.25)} {p(.67, -.25)} {p(.61, -.11)}C{p(.58, -.05)} {p(.60, 0)} {p(.64, 0)}L{p(1, 0)}"
def jigsaw_lines(cols, rows, x0, y0, c, seed):
    rnd = random.Random(seed); d = []
    for k in range(1, cols):
        x = x0 + k * c; d.append(f"M{f(x)} {f(y0)}" + "".join(jig_edge((x, y0 + r * c), (x, y0 + (r + 1) * c), rnd.choice((-1, 1))) for r in range(rows)))
    for k in range(1, rows):
        y = y0 + k * c; d.append(f"M{f(x0)} {f(y)}" + "".join(jig_edge((x0 + r * c, y), (x0 + (r + 1) * c, y), rnd.choice((-1, 1))) for r in range(cols)))
    return "".join(d)
def straight_lines(cols, rows, x0, y0, c):
    return "".join(f"M{f(x0 + k * c)} {f(y0)}V{f(y0 + rows * c)}" for k in range(1, cols)) + "".join(f"M{f(x0)} {f(y0 + k * c)}H{f(x0 + cols * c)}" for k in range(1, rows))
def puzzle(slug, name, cols, rows, c, draw, cat, age, diff, seed, straight=False, minutes=25):
    W, H = cols * c, rows * c; x0, y0 = (200 - W) / 2, 40
    lines = straight_lines(cols, rows, x0, y0, c) if straight else jigsaw_lines(cols, rows, x0, y0, c, seed)
    sh = Sheet(); head(sh, name.split(": ")[-1][0].upper() + name.split(": ")[-1][1:])
    sh.text(100, 28, "Kleur de tekening, knip de stukjes los en leg de puzzel.", 6)
    draw(sh, x0, y0, W, H)
    sh.line(lines, "cut"); sh.rect_line(x0, y0, W, H, "cut")
    for i in range(cols * rows):
        r, k = divmod(i, cols); bx, by = x0 + k * c + 6.5, y0 + r * c + 6.5
        sh.circle_r(bx, by, 4.6, "-"); sh.text(bx, by + 2, str(i + 1), 5.5)
    sh.legend(["cut"], 277)
    lb = Sheet(); head(lb, "Legbord")
    lb.text(100, 28, "Leg elk stukje op het vak met hetzelfde nummer.", 6.5)
    lb.line(lines, "l", "stroke-width:1"); lb.rect_line(x0, y0, W, H, "l", 0, "stroke-width:1.6")
    for i in range(cols * rows):
        r, k = divmod(i, cols); lb.text(x0 + k * c + c / 2, y0 + r * c + c / 2 + 5, str(i + 1), 14)
    cutstep = "Knip de stukjes los langs de rechte streepjeslijnen. Een volwassene kan helpen." if straight else "Knip eerst langs de rechte buitenrand en daarna de stukjes los langs de streepjeslijnen."
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": minutes, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, {"slug": "stevig-papier", "optional": True}, {"slug": "lijmstift", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Op stevig papier gaat de puzzel langer mee. Print het legbord op gewoon papier.", "steps": [
            "Kleur de tekening helemaal in.", cutstep, "Hussel de stukjes door elkaar.",
            "Leg de puzzel op het legbord: elk stukje hoort op het vak met hetzelfde nummer. Lukt het ook zonder nummers te kijken? Wil je hem bewaren? Plak de stukjes vast."]}}},
        [("extra", "Legbord", lb)])

def horse(sh, X, Y, code="w"):
    def Pp(d):  # pad in 0..100-coördinaten naar vel
        toks = re.findall(r"[A-Z]|-?\d*\.?\d+", d); out = []; xy = 0
        for t in toks:
            if t.isalpha(): out.append(t); xy = 0
            else: out.append(f(X(float(t))) if xy % 2 == 0 else f(Y(float(t)))); xy += 1
        return " ".join(out)
    sh.region(Pp("M27 46C18 48 15 58 19 67C22 60 24 54 29 50Z"), "x")
    for x, y0 in [(31, 56), (36, 57), (55, 56), (60, 56)]:
        sh.region(Pp(f"M{x - 1.8} {y0}V70H{x + 1.8}V{y0}Z"), code); sh.region(Pp(f"M{x - 2.2} 70H{x + 2.2}V72.5H{x - 2.2}Z"), "x")
    sh.region(Pp("M26 48C26 40 36 40 46 41C54 42 58 40 62 34L68 22C70 20 72 20 74 22L82 31C84 34 82 36 79 36L72 34C68 34 66 38 64 44C64 52 62 58 56 60L32 60C26 60 26 54 26 48Z"), code)
    sh.region(Pp("M68 21L65 23L66 25L62 27L63 29L59 31L60 33L56 36L58 39L62 34L68 22Z"), "x")
    sh.region(Pp("M69 22L70 15L73 21Z"), code)
    sh.dot(X(73.5), Y(25.5), 1.3); sh.dot(X(80.5), Y(33.2), .9)
def paard_scene(sh, x0, y0, W, H):
    X = lambda v: x0 + v * W / 100; Y = lambda v: y0 + v * H / 75
    sh.rect_r(x0, y0, W, H, "b")
    sh.circle_r(X(88), Y(11), W * .06, "y")
    sh.region(f"M{X(10)} {Y(16)}C{X(10)} {Y(10)} {X(18)} {Y(8)} {X(22)} {Y(12)}C{X(26)} {Y(6)} {X(38)} {Y(8)} {X(38)} {Y(14)}C{X(42)} {Y(14)} {X(42)} {Y(20)} {X(37)} {Y(20)}H{X(12)}C{X(6)} {Y(20)} {X(6)} {Y(16)} {X(10)} {Y(16)}Z", "-")
    sh.region(f"M{x0} {Y(44)}Q{X(40)} {Y(36)} {X(100)} {Y(42)}V{Y(75)}H{x0}Z", "l")
    # boom rechts
    sh.rect_r(X(86), Y(26), W * .04, H * .22, "w"); sh.circle_r(X(88), Y(24), W * .085, "g")
    # hek
    for k in range(5): sh.rect_r(X(2 + k * 9), Y(38), W * .022, H * .13, "w")
    sh.rect_r(X(1), Y(41), W * .4, H * .025, "w"); sh.rect_r(X(1), Y(46), W * .4, H * .025, "w")
    horse(sh, X, Y)
    for x, c in [(10, "r"), (16, "y"), (88, "m"), (94, "r")]:
        sh.line(f"M{X(x)} {Y(73)}V{Y(67)}", "l", "stroke-width:1.2"); sh.circle_r(X(x), Y(66), 2.4, c)
puzzle("puzzel-paard-in-de-wei-12-stukjes", "Puzzel knippen: paard in de wei (12 stukjes)", 4, 3, 42, paard_scene, "boerderij", "6-9", 2, 37)

def brandweer_scene(sh, x0, y0, W, H):
    X = lambda v: x0 + v * W / 100; Y = lambda v: y0 + v * H / 66.7
    sh.rect_r(x0, y0, W, H, "b")
    sh.region(f"M{X(10)} {Y(10)}C{X(10)} {Y(4)} {X(18)} {Y(2)} {X(22)} {Y(6)}C{X(26)} {Y(1)} {X(36)} {Y(3)} {X(35)} {Y(9)}C{X(39)} {Y(10)} {X(38)} {Y(15)} {X(34)} {Y(15)}H{X(12)}C{X(7)} {Y(15)} {X(7)} {Y(10)} {X(10)} {Y(10)}Z", "-")
    sh.circle_r(X(88), Y(9), W * .05, "y")
    sh.rect_r(x0, Y(56), W, H - (Y(56) - y0), "z")
    for k in range(6): sh.rect_r(X(4 + k * 17), Y(61), W * .08, 2, "-")
    # ladder
    sh.rect_r(X(6), Y(22), W * .56, H * .06, "z")
    for k in range(1, 10): sh.seg(X(6 + 5.6 * k), Y(22), X(6 + 5.6 * k), Y(26), "l", "stroke-width:1.2")
    sh.rect_r(X(50), Y(26), W * .04, H * .03, "z")
    sh.rect_r(X(4), Y(28), W * .6, H * .24, "r")
    sh.region(f"M{X(64)} {Y(52)}V{Y(22)}H{X(84)}Q{X(90)} {Y(22)} {X(93)} {Y(34)}L{X(95)} {Y(40)}V{Y(52)}Z", "r")
    sh.region(f"M{X(70)} {Y(26)}H{X(84)}Q{X(87)} {Y(26)} {X(89)} {Y(35)}H{X(70)}Z", "b")
    sh.rect_r(X(70), Y(18), W * .08, H * .04, "n"); sh.rect_r(X(80), Y(18), W * .05, H * .04, "o")
    for k in range(3): sh.rect_r(X(8 + k * 18), Y(32), W * .13, H * .1, "z")
    sh.rect_r(X(4), Y(44), W * .91, H * .03, "y")
    for x in (18, 46, 80): sh.circle_r(X(x), Y(54), W * .07, "x"); sh.circle_r(X(x), Y(54), W * .03, "z")
    sh.rect_r(X(93), Y(42), W * .03, H * .05, "y")
puzzle("puzzel-brandweerauto-6-stukjes", "Puzzel knippen: brandweerauto (6 stukjes)", 3, 2, 56, brandweer_scene, "voertuigen", "2-4", 1, 3, straight=True, minutes=15)

# =====================================================================
# Schaduwen: knip het dier uit en plak het op zijn schaduw
# =====================================================================
SCHADUW = [(bd_koe, 1.1), (bd_varken, 1.1), (bd_schaap, 1.1), (bd_kip, 1.1), (bd_eend, 1.1), (bd_paard, 1.25)]
def schaduwen():
    sh = Sheet(); head(sh, "Wie hoort bij welke schaduw?")
    sh.text(100, 26, "Kleur de dieren, knip ze uit en plak ze op hun schaduw op blad 2.", 6)
    K = pack(sh, [[S(fn, k) for fn, k in SCHADUW[0:2]], [S(fn, k) for fn, k in SCHADUW[2:4]], [S(fn, k) for fn, k in SCHADUW[4:6]]], gap=6, k=1.6)
    sh.legend(["cut"], 277)
    pl = Sheet(); head(pl, "Plak elk dier op zijn schaduw")
    order = [3, 5, 1, 4, 0, 2]
    for i, j in enumerate(order):
        fn, kf = SCHADUW[j]; g = S(S(fn, kf), K)
        x0_, y0_, x1_, y1_ = bbox(g)
        col, row = i % 2, i // 2
        cx, cy = 52 + col * 96, 66 + row * 76
        silhouette(pl, g, cx - (x0_ + x1_) / 2, cy - (y0_ + y1_) / 2)
    pl.text(100, 272, "Past het precies? Dan heb je de goede schaduw gevonden!", 6)
    assert K
    write(OUT, "schaduwen-boerderijdieren-plakken", sh, {"category": "boerderij", "age": "2-4", "kind": "knipplaat", "difficulty": 1, "minutes": 20, "adultHelp": True,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": "Schaduwen: boerderijdieren knippen en plakken", "printNote": "Print beide pagina's op ware grootte (100%), dan passen de dieren precies op hun schaduw.", "steps": [
            "Kleur de koe, het varken, het schaap, de kip, de eend en het paard in.",
            "Knip de dieren uit langs de streepjeslijn. Een volwassene helpt bij de kleine stukjes, zoals de pootjes.",
            "Leg een dier op blad 2 en zoek de schaduw met precies dezelfde vorm. Kijk goed naar de oren, de staart en de pootjes.",
            "Past het? Plak het dier op zijn schaduw. Weet je welk geluid elk dier maakt?"]}}},
        [("extra", "Plakvel", pl)])
schaduwen()

# =====================================================================
# Maskers
# =====================================================================
def masker(slug, name, title_, build, colors_step, age="4-6"):
    sh = Sheet(); head(sh, title_)
    pc = Pc(sh, 100, 110); build(pc); pc.cut(2.5)
    for s in (-1, 1):
        sh.raw(f'<ellipse class="cut" cx="{100 + s * 28}" cy="104" rx="13" ry="9" fill="none"/>')
        sh.circle_line(100 + s * 66, 106, 2.4, "cut")
    sh.text(100, 206, "Ooggaten en gaatjes voor het elastiek: laat een volwassene helpen.", 6)
    sh.legend(["cut"], 277)
    write(OUT, slug, sh, {"category": "dieren", "age": age, "kind": "knipplaat", "difficulty": 2, "minutes": 25, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, {"slug": "elastiek"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier (160 gram), dan blijft het masker beter in vorm.", "steps": [
            colors_step,
            "Knip het masker uit langs de buitenste streepjeslijn.",
            "Een volwassene knipt de ooggaten uit (prik eerst een gaatje in het midden) en prikt de twee kleine gaatjes aan de zijkant.",
            "Knoop aan elke kant een stuk elastiek vast, zo lang dat het masker goed om je hoofd past. Probeer of je goed kunt kijken."]}}})
def kikker_m(p):
    for s in (-1, 1): p.add(circ(s * 30, -14, 27), "g")
    p.add(ellp(0, 14, 84, 50), "g")
    for s in (-1, 1): p.add(circ(s * 30, -14, 27), "g", sil=False); p.add(ellp(s * 28, -6, 19, 15), "y", sil=False)
    p.ln(sample("M-56 26Q0 62 56 26", 12), style="stroke-width:2.6")
    for s in (-1, 1): p.ln(sample(f"M{s * 56} 26Q{s * 62} 24 {s * 62} 18", 4), style="stroke-width:2.2")
    for s in (-1, 1): p.dot(s * 7, 16, 2); p.add(circ(s * 56, 40, 8), "k", sil=False)
    for x, y, r in [(-14, 44, 4), (16, 50, 3), (38, 54, 4), (-36, 56, 4), (0, -30, 4)]: p.add(circ(x, y, r), "l", sil=False)
masker("masker-kikker", "Masker: kikker", "Kikkermasker", kikker_m, "Kleur de kikker groen met lichtgroene vlekjes. Maak de randen rond de ogen geel en de wangen roze.")
def egel_m(p):
    spikes = []
    n = 17
    for i in range(n + 1):
        a = math.radians(170 + i * 200 / n)
        r = 86 if i % 2 == 0 else 66
        spikes.append((r * math.cos(a) * 1.05, -2 + r * math.sin(a) * .95))
    p.add(spikes + [(60, 30), (0, 30), (-60, 30)], "w")
    for s in (-1, 1): p.add(circ(s * 50, -36, 11), "k")
    p.add(sample("M-62 0C-62 -40 -30 -52 0 -52C30 -52 62 -40 62 0C62 28 30 40 14 60Q0 70 -14 60C-30 40 -62 28 -62 0Z"), "k")
    for s in (-1, 1): p.add(circ(s * 50, -36, 6), "w", sil=False); p.add(ellp(s * 28, -6, 18, 14), "-", sil=False)
    p.add(ellp(0, 42, 10, 7.5), "x", sil=False); p.add(circ(-3, 40, 2.2), "-", sil=False)
    p.ln([(0, 49.5), (0, 54)], style="stroke-width:2"); p.ln(sample("M-9 53Q0 60 9 53", 6), style="stroke-width:2")
    for s in (-1, 1): p.add(circ(s * 40, 22, 7), "m", sil=False)
    for k in range(9):
        a = math.radians(196 + k * 18.5); p.ln([(72 * math.cos(a) * 1.02, -2 + 72 * math.sin(a) * .93), (58 * math.cos(a), -2 + 58 * math.sin(a) * .9)], style="stroke-width:1.4")
masker("masker-egel", "Masker: egel", "Egelmasker", egel_m, "Kleur de stekels bruin en het gezicht lichtroze. De neus is zwart en de wangen roze.")

# =====================================================================
# Hoofdbanden: drie lange stroken (samen ruim genoeg voor elk hoofd)
# =====================================================================
SL = 244
def band_strip(sh, x, y, w, label, deco, glue=True):
    pc = Pc(sh, x, y)
    pc.add(rect(0, 0, w, SL), "-")
    if glue: glue_rect(sh, x + 1, y + 1, w - 2, 12)
    deco(pc, w)
    sh.text(x + w / 2, y + (24 if glue else 10), label, 8)
    for lp in outline(pc.polys, 2.5, .25): sh.line(P(lp), "cut")
def lijmflap(pc, w, y0, h=9):
    pc.add(rect(-w / 2, y0, w, h), "-"); pc.text(0, y0 + h / 2 + 2, "lijm", 4.6, cls="tip")
def bloemenkroon():
    sh = Sheet(); head(sh, "Bloemenkroon")
    def deco(pc, w):
        pc.ln(sample(f"M{w / 2} 30" + "".join(f"Q{w / 2 + (7 if k % 2 else -7)} {40 + k * 20} {w / 2} {50 + k * 20}" for k in range(9)), 6), style="stroke-width:1.2")
        for k in range(9): pc.add(ellp(w / 2 + (6 if k % 2 else -6), 42 + k * 20, 4.5, 2.2, 35 if k % 2 else -35), "g", sil=False)
    band_strip(sh, 8, 24, 22, "A", deco, glue=False)
    band_strip(sh, 38, 24, 22, "B", deco)
    band_strip(sh, 68, 24, 22, "C", deco)
    def bloem5(code, r=9):
        def fn(pc):
            lijmflap(pc, 10, r * .9, 11)
            pc.add(union([circ(r * .8 * math.cos(math.radians(a - 90)), r * .8 * math.sin(math.radians(a - 90)), r * .62) for a in range(0, 360, 72)]), code)
            pc.add(circ(0, 0, r * .4), "y")
        return fn
    def madelief(pc):
        lijmflap(pc, 10, 9, 11)
        for a in range(0, 360, 30): t = math.radians(a); pc.add(ellp(8 * math.cos(t), 8 * math.sin(t), 5, 2, a), "-")
        pc.add(circ(0, 0, 4), "y")
    def tulpje(code):
        def fn(pc):
            lijmflap(pc, 10, 7, 11)
            pc.add(sample("M-8 6V-8L-4 -3L0 -10L4 -3L8 -8V6Q0 11 -8 6Z"), code)
        return fn
    def blad(pc): pc.add(sample(leaf_path(0, 0, 5, 11)), "g"); pc.ln([(0, -9), (0, 9)], style="stroke-width:1")
    K = 1.2
    flow(sh, [S(bloem5("m"), K), S(bloem5("r"), K), S(madelief, K), S(tulpje("o"), K), S(bloem5("p"), K), S(madelief, K),
              S(tulpje("y"), K), S(bloem5("b"), K), S(madelief, K)] + [S(blad, 1.0)] * 6, 96, 26, 199, 2)
    sh.legend(["cut", "glue"], 277)
    write(OUT, "bloemenkroon-hoofdband", sh, {"category": "natuur", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 30, "adultHelp": True,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "plakband", "optional": True}],
        "i18n": {"nl": {"name": "Bloemenkroon om op te zetten", "printNote": "Print op ware grootte (100%), dan zijn de stroken samen lang genoeg.", "steps": [
            "Kleur de stroken, de bloemen en de blaadjes in. Gebruik veel verschillende kleuren!",
            "Knip alles uit langs de streepjeslijn. Laat het witte lijmstrookje onder elke bloem zitten.",
            "Plak strook B aan strook A: lijm op het grijze vakje van B en leg het einde van A erop. Plak strook C op dezelfde manier aan B.",
            "Leg de band om het hoofd en plak hem op de goede maat vast. Knip het stuk dat te lang is eraf.",
            "Smeer lijm op de achterkant van het witte strookje onder een bloem en plak het achter de bovenrand van de band, zodat de bloem erboven uitsteekt. Zet zo alle bloemen rondom en plak de blaadjes ertussen."]}}})
bloemenkroon()

def ridderhelm():
    sh = Sheet(); head(sh, "Ridderhelm-hoofdband")
    def deco(pc, w):
        for y in range(40, SL - 6, 22): pc.add(circ(w / 2, y, 2.4), "z", sil=False)
        pc.ln([(3, 4), (3, SL - 4)], style="stroke-width:1"); pc.ln([(w - 3, 4), (w - 3, SL - 4)], style="stroke-width:1")
    def deco_a(pc, w):
        deco(pc, w); pc.add(rect(w / 2 - 9, SL / 2 - 22, 18, 44), "-", sil=False); pc.text(w / 2, SL / 2 + 2, "helm", 5, cls="tip")
    band_strip(sh, 8, 24, 22, "A", deco_a, glue=False)
    band_strip(sh, 38, 24, 22, "B", deco)
    band_strip(sh, 68, 24, 22, "C", deco)
    def helm(pc):
        pc.add(sample("M-34 40V0C-34 -26 -18 -40 0 -40C18 -40 34 -26 34 0V40Z"), "z")
        pc.add(rect(-34, 40, 68, 14), "-"); pc.text(0, 49.5, "lijm achter", 4.6, cls="tip")
        pc.add(rect(-3, -38, 6, 78), "z", sil=False)
        for y in (6, 16): pc.add(rrect(-28, y, 22, 4, 2), "x", sil=False); pc.add(rrect(6, y, 22, 4, 2), "x", sil=False)
        for x, y in [(-26, -10), (26, -10), (-30, 32), (30, 32), (-18, -26), (18, -26)]: pc.add(circ(x, y, 2), "-", sil=False)
    def pluim(pc):
        pc.add(sample("M-4 40C-14 30 -20 10 -14 -10C-10 -24 0 -32 10 -34C2 -24 6 -14 10 -6C14 4 10 22 4 40Z"), "r")
        for d in ("M-2 34Q-12 16 -6 -8", "M2 34Q0 10 6 -20"): pc.ln(sample(d, 6), style="stroke-width:1.1")
        pc.add(rect(-5, 40, 10, 12), "-"); pc.text(0, 48, "lijm", 4.6, cls="tip")
    def schild(pc):
        pc.add(sample("M-16 -18H16V2C16 14 6 20 0 24C-6 20 -16 14 -16 2Z"), "b")
        pc.add(rect(-3, -18, 6, 40), "y", sil=False); pc.add(rect(-16, -6, 32, 6), "y", sil=False)
    def veer(code):
        def fn(pc):
            pc.add(sample("M0 26C-8 14 -8 -6 0 -24C8 -6 8 14 0 26Z"), code); pc.ln([(0, -18), (0, 26)], style="stroke-width:1")
        return fn
    place(sh, S(helm, 1.3), 104, 28)
    place(sh, S(pluim, 1.0), 158, 162); place(sh, S(schild, 1.1), 110, 162)
    flow(sh, [S(veer("y"), .82), S(veer("b"), .82)], 100, 214, 156, 4)
    sh.legend(["cut", "glue"], 277)
    write(OUT, "ridderhelm-hoofdband", sh, {"category": "sprookjes", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 30, "adultHelp": True,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "plakband", "optional": True}],
        "i18n": {"nl": {"name": "Ridderhelm om op te zetten", "printNote": "Print op ware grootte (100%), dan zijn de stroken samen lang genoeg.", "steps": [
            "Kleur de stroken en de helm grijs, de pluim rood en het schild en de veren in jouw ridderkleuren.",
            "Knip alles uit langs de streepjeslijn. Laat de witte lijmstrookjes zitten.",
            "Plak strook B aan strook A: lijm op het grijze vakje van B en leg het einde van A erop. Plak strook C op dezelfde manier aan B.",
            "Leg de band om het hoofd, met het vak 'helm' van strook A midden op je voorhoofd. Plak hem op de goede maat vast en knip het stuk dat te lang is eraf.",
            "Smeer lijm op het witte strookje onder de helm en plak het achter de band, op het vak 'helm'. De helm steekt boven je hoofd uit.",
            "Plak de pluim achter de bovenkant van de helm. Het schild en de twee veren plak je op de zijkanten van de band. Klaar voor het toernooi!"]}}})
ridderhelm()

# =====================================================================
# Splitpenpoppen: armen en benen die bewegen
# =====================================================================
def limb(L, w, end_fn=None, code="z", top_r=None, hole=True):
    """Arm of been: ronde bovenkant met gaatje op (0,0), naar beneden lang L."""
    def fn(pc):
        r = top_r or w
        pc.add(circ(0, 0, r), code); pc.add(rect(-w, 0, 2 * w, L), code)
        if end_fn: end_fn(pc, L)
        if hole: pc.hole(0, 0)
    return fn
def splitpop(slug, name, heading, cat, torso, limbs, steps_color, extra_steps, holes_text, lk=1.7):
    sh = Sheet(); head(sh, heading)
    sh.text(100, 26, "Knip alles uit. Zet armen en benen vast met splitpennen.", 6)
    place(sh, S(torso, 1.75), 4, 34)
    y = flow(sh, [S(fn, lk) for fn in limbs[:2]], 100, 32, 199, 4)
    flow(sh, [S(fn, lk) for fn in limbs[2:]], 100, max(y + 2, 146), 199, 4)
    sh.text(100, 268, holes_text, 6)
    sh.legend(["cut"], 277)
    write(OUT, slug, sh, {"category": cat, "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 35, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, SPLIT, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier (160 gram), dan scheuren de gaatjes niet zo snel.", "steps": [
            steps_color,
            "Knip het lijf en de armen en benen uit langs de streepjeslijn.",
            "Een volwassene prikt een gaatje in elk rondje met een kruisje, bijvoorbeeld met de punt van een potlood op een gum.",
            "Leg een arm achter het lijf, zo dat de gaatjes precies over elkaar liggen. Steek er van voren een splitpen door en buig de pootjes aan de achterkant opzij. Doe hetzelfde met de andere arm en met de benen.",
        ] + extra_steps}}})

# ---------- ridder ----------
def ridder_torso(pc):
    pc.add(rect(-7, 14, 14, 10), "z")
    pc.add(sample("M-14 22H14L18 70H-18Z"), "z")
    pc.add(sample("M-11 22H11L14 72H-14Z"), "b")
    pc.add(rect(-2.5, 26, 5, 40), "y", sil=False); pc.add(rect(-11, 38, 22, 5), "y", sil=False)
    pc.add(rect(-15, 58, 30, 5), "w", sil=False); pc.add(rect(-3, 57, 6, 7), "y", sil=False)
    pc.add(sample("M-1 -12Q4 -24 14 -22Q8 -18 6 -12Z"), "r")
    pc.add(sample("M-12 18V-2C-12 -12 -6 -16 0 -16C6 -16 12 -12 12 -2V18Z"), "z")
    pc.add(rect(-12, 2, 24, 4), "x", sil=False); pc.ln([(0, 6), (0, 18)], style="stroke-width:1.2")
    for x in (-6, 6):
        for y in (10, 14): pc.dot(x, y, .8)
    for x, y in [(-10, 28), (10, 28), (-8, 64), (8, 64)]: pc.hole(x, y)
def zwaard(pc, L):
    pc.add(circ(0, L + 2, 5), "z"); pc.add(rect(-10, L + 6, 20, 3), "y"); pc.add(rect(-2, L - 2, 4, 9), "w", sil=False)
    pc.add(sample(f"M-2.5 {L + 9}H2.5V{L + 40}L0 {L + 45}L-2.5 {L + 40}Z"), "z")
def schild_arm(pc, L):
    pc.add(circ(0, L + 2, 5), "z")
    pc.add(sample(f"M-14 {L - 4}H14V{L + 12}C14 {L + 22} 6 {L + 28} 0 {L + 30}C-6 {L + 28} -14 {L + 22} -14 {L + 12}Z"), "b")
    pc.add(rect(-2.5, L - 4, 5, 34), "y", sil=False); pc.add(rect(-14, L + 6, 28, 5), "y", sil=False)
def laars(pc, L): pc.add(sample(f"M-5 {L - 4}H5V{L + 4}H11Q13 {L + 4} 13 {L + 8}H-5Z"), "w")
splitpop("splitpenpop-ridder", "Splitpenpop: ridder met zwaard en schild", "Beweegbare ridder", "sprookjes", ridder_torso,
    [limb(30, 4.5, zwaard), limb(30, 4.5, schild_arm), limb(34, 5, laars), limb(34, 5, laars)],
    "Kleur de ridder in: een grijs harnas, een kleurig hemd met een kruis en een rode pluim op de helm. Het schild krijgt dezelfde kleuren.",
    ["Klaar! Laat de ridder zijn zwaard opsteken en zijn schild omhoog houden."], "4 splitpennen: twee schouders en twee heupen.", lk=1.4)

# ---------- astronaut ----------
def astro_torso(pc):
    pc.add(rrect(-24, 18, 48, 40, 6), "-")
    pc.add(rrect(-16, 20, 32, 50, 7), "-")
    pc.add(rrect(-9, 30, 18, 12, 2), "z", sil=False)
    for k, c in enumerate("rgy"): pc.add(circ(-5 + k * 5, 34, 1.6), c, sil=False)
    pc.add(rect(-6, 37.5, 12, 2.4), "b", sil=False)
    pc.add(rect(-16, 52, 32, 4), "z", sil=False)
    pc.add(circ(0, 2, 17), "-"); pc.add(sample("M-12 0C-12 -10 12 -10 12 0C12 8 6 10 0 10C-6 10 -12 8 -12 0Z"), "n", sil=False)
    pc.add(sample("M-7 -4Q-4 -7 0 -7"), "-", sil=False) if False else pc.ln(sample("M-8 -2Q-6 -6 -1 -6", 4), style="stroke-width:1.2")
    pc.add(rect(-8, 16, 16, 4), "z", sil=False)
    for x, y in [(-17, 26), (17, 26), (-9, 66), (9, 66)]: pc.hole(x, y)
def handschoen(pc, L): pc.add(rect(-6, L - 2, 12, 4), "r"); pc.add(sample(f"M-5 {L + 2}H5V{L + 10}Q5 {L + 13} 0 {L + 13}Q-5 {L + 13} -5 {L + 10}Z"), "z")
def maanlaars(pc, L): pc.add(rect(-6.5, L - 2, 13, 4), "r"); pc.add(sample(f"M-6 {L + 2}H6V{L + 6}H12Q14 {L + 6} 14 {L + 10}V{L + 12}H-6Z"), "z")
def vlag_arm(pc, L):
    handschoen(pc, L); pc.add(rect(4, L - 20, 2, 36), "w"); pc.add(rect(6, L - 20, 20, 13), "-")
    pc.text(16, L - 11.5, "NL?", 4.6) if False else pc.add(star_pts(16, L - 13.5, 4.5, 2), "y", sil=False)
splitpop("splitpenpop-astronaut", "Splitpenpop: astronaut die zwaait", "Beweegbare astronaut", "ruimte", astro_torso,
    [limb(28, 5.5, handschoen, "-"), limb(28, 5.5, vlag_arm, "-"), limb(30, 6, maanlaars, "-"), limb(30, 6, maanlaars, "-")],
    "Kleur het ruimtepak, het vizier van de helm, de knopjes op het borstpaneel en de vlag in. Een ruimtepak is vaak wit: kleur dan alleen de randjes en de knoppen.",
    ["Klaar! Laat de astronaut zwaaien met zijn vlag en een maanwandeling maken. Plak hem op een zwart vel met sterren voor een ruimteplaat."], "4 splitpennen: twee schouders en twee heupen.")

# ---------- happende krokodil ----------
def kroko_lijf(pc):
    pc.add(sample("M-70 4C-58 -6 -40 -8 -20 -8H30L76 -4Q80 0 76 4L30 10H-20C-30 14 -50 14 -70 4Z"), "g") if False else None
    pc.add(sample("M-92 0Q-80 -6 -60 -8C-40 -14 -10 -16 14 -12L30 -8V14L-10 16C-40 16 -70 10 -92 0Z"), "g")
    for x in (-40, -6): pc.add(sample(f"M{x - 6} 12L{x - 8} 26H{x + 4}L{x + 6} 12Z"), "g"); pc.ln([(x - 8, 26), (x - 9, 29)], style="stroke-width:1.2"); pc.ln([(x - 3, 26), (x - 3, 29)], style="stroke-width:1.2"); pc.ln([(x + 2, 26), (x + 3, 29)], style="stroke-width:1.2")
    for x in (-60, -44, -28, -12): pc.ln(sample(f"M{x} -8Q{x + 4} 2 {x} 12", 4), style="stroke-width:1")
    # onderkaak
    pc.add(sample("M24 -2H84Q90 0 88 6Q84 12 70 12H24Z"), "g")
    for k in range(6): x = 36 + k * 8; pc.add([(x, -2), (x + 3, -8), (x + 6, -2)], "-")
    pc.add(sample("M30 2H82Q84 6 78 8H30Z"), "m", sil=False)
    pc.hole(30, 0)
def kroko_kop(pc):
    pc.add(sample("M-8 -8C-8 -20 4 -26 14 -22C20 -20 22 -14 24 -12H50Q60 -12 62 -4Q62 4 56 4H-2Q-8 4 -8 -2Z"), "g")
    for k in range(6): x = 20 + k * 6.5; pc.add([(x, 4), (x + 3, 10), (x + 6, 4)], "-")
    pc.add(circ(10, -18, 7), "-", sil=False); pc.add(circ(11, -18, 3.4), "y", sil=False); pc.dot(11.5, -18, 1.6)
    for x in (55, 58.5): pc.dot(x, -8, 1.1)
    for x in (30, 42): pc.dot(x, -6, 1)
    pc.hole(0, 0)
def visje(pc):
    pc.add(sample(fish_path(0, 0, 12)), "o"); pc.dot(-6, -2, 1.3)
def krokodil():
    sh = Sheet(); head(sh, "Happende krokodil")
    sh.text(100, 26, "Zet de kop met een splitpen vast op het lijf. Hap, hap!", 6)
    place(sh, S(kroko_lijf, 1.0), 6, 40)
    place(sh, S(kroko_kop, 1.0), 60, 100)
    flow(sh, [S(visje, 1.2)] * 3, 20, 150, 180, 8)
    # voorbeeld
    sh.text(100, 200, "Zo werkt het:", 7)
    ex = Sheet()
    sh.raw('<g transform="translate(60 228) scale(.42)">')
    pc = Pc(sh, 0, 0); kroko_lijf(pc)
    sh.raw('</g>')
    sh.raw('<g transform="translate(60 228) scale(.42) translate(30 0) rotate(-22)">')
    pc = Pc(sh, 0, 0); kroko_kop(pc)
    sh.raw('</g>')
    sh.line("M140 236Q150 222 146 210", "l", "stroke-width:1"); sh.line("M146 210l-3 4m3 -4l2 4", "l", "stroke-width:1")
    sh.text(164, 238, "duw de neus", 5, cls="tip"); sh.text(164, 245, "omhoog", 5, cls="tip")
    sh.legend(["cut"], 277)
    write(OUT, "happende-krokodil-splitpen", sh, {"category": "dieren", "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 25, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, SPLIT, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": "Happende krokodil met splitpen", "printNote": "Print op stevig papier (160 gram), dan gaat de bek langer mee.", "steps": [
            "Kleur de krokodil groen, de binnenkant van de bek roze en de visjes in vrolijke kleuren.",
            "Knip het lijf, de kop en de visjes uit langs de streepjeslijn.",
            "Een volwassene prikt een gaatje in de twee rondjes met een kruisje: één op het lijf bij de onderkaak en één achter in de kop.",
            "Leg de kop op het lijf, zo dat de gaatjes over elkaar liggen en de tanden van boven en onder in elkaar passen. Steek er een splitpen door en buig de pootjes aan de achterkant opzij.",
            "Duw de neus omhoog en laat hem weer zakken: hap! Kan de krokodil de visjes vangen?"]}}})
krokodil()

# =====================================================================
# Kijkdoos: jungle in een schoenendoos
# =====================================================================
def stand(fn, tab_w=None):
    """Figuurtje met een standaardje eronder: vouwen langs de stippellijn en vastplakken op de bodem."""
    def g(pc):
        x0, y0, x1, y1 = bbox(fn)
        st = (pc.sc, pc.dx, pc.dy); fn(pc); pc.sc, pc.dx, pc.dy = st
        w = tab_w or min(24, max(14, (x1 - x0) * .4)); cx = (x0 + x1) / 2
        q = [(cx - w / 2, y1 - .5), (cx + w / 2, y1 - .5), (cx + w / 2, y1 + 12), (cx - w / 2, y1 + 12)]
        pc.add(q, "-")
        pc.ln([(cx - w / 2, y1 - .5), (cx + w / 2, y1 - .5)], cls="fold")
        tq = pc.T([(cx - w / 2 + 1.5, y1 + 4), (cx + w / 2 - 1.5, y1 + 4), (cx + w / 2 - 1.5, y1 + 10.5), (cx - w / 2 + 1.5, y1 + 10.5)])
        pc.sh.raw(f'<path class="glue" d="{P(tq)}"/>')
    return g
def jg_papegaai(pc):
    pc.add(sample("M-2 20L-7 30L0 29L4 22Z"), "b")
    pc.add(rect(-16, 26, 32, 4), "w")
    pc.add(ellp(0, 8, 9, 14, 10), "r"); pc.add(ellp(4, 10, 5, 10, 20), "y", sil=False)
    pc.add(circ(-2, -8, 7), "r"); pc.add(circ(-4, -9, 2.6), "-", sil=False); pc.dot(-4.4, -9, 1)
    pc.add(sample("M-9 -10Q-16 -8 -12 -1Q-11 -5 -8 -5Z"), "y")
    for x in (-3, 3): pc.ln([(x, 20), (x, 23)], style="stroke-width:1.2")
def jg_slang(pc):
    pc.add(taper(sample("M-30 14Q-20 2 -10 12Q0 22 10 12Q18 4 26 8", 10), 2, 4.5), "l")
    pc.add(ellp(30, 6, 7, 5, -15), "l"); pc.dot(31, 4, 1.1)
    pc.ln([(36, 7), (41, 8), (43, 6)], style="stroke-width:.9"); pc.ln([(41, 8), (43, 10)], style="stroke-width:.9")
    for x in (-22, -6, 10): pc.add(circ(x, 10 + (x % 3), 1.6), "y", sil=False)
    pc.add(rect(-32, 13, 64, 3), "l")
def jg_kikker(pc): wrap(ic_kikker, .9, -18, -22)(pc)
def jg_olifant(pc): wrap(ic_olifant, 1.6, -20, -20)(pc)
def jg_aap(pc): dt_aap(pc)
def jg_varen(pc):
    for a in (-60, -35, -10, 15, 40):
        t = math.radians(a - 90); x, y = 22 * math.cos(t), 22 * math.sin(t) + 20
        pc.add(sample(f"M0 22Q{x * .3 - 4} {y - 2} {x} {y}Q{x * .5 + 4} {y + 6} 0 22Z"), "g")
    pc.add(rect(-12, 20, 24, 3), "g")
def jg_tijger(pc):
    pc.ln(sample("M16 2Q26 0 26 -12", 6), style="stroke-width:1.6"); pc.sil(bar(16, 2, 26, -12, 1))
    for x in (-12, -6, 6, 12): pc.add(rect(x - 2, 4, 4, 13), "o")
    pc.add(ellp(2, 2, 17, 8), "o")
    for x in (-6, 0, 6, 12): pc.add(sample(f"M{x} -6L{x + 2} 0L{x} 4Z"), "x", sil=False)
    pc.add(circ(-16, -6, 8), "o"); pc.add(circ(-21, -13, 3), "o"); pc.add(circ(-11, -13, 3), "o")
    pc.add(ellp(-16, -3, 4, 3), "-", sil=False); pc.dot(-19, -8, 1); pc.dot(-13, -8, 1); pc.add([(-17.5, -4.5), (-14.5, -4.5), (-16, -3)], "x", sil=False)
def kijkdoos():
    sh = Sheet(); head(sh, "Kijkdoos: de jungle")
    sh.text(100, 25, "De achterwand: plak hem achter in een schoenendoos.", 6)
    x0, y0, W, H = 8, 30, 184, 128
    sh.rect_r(x0, y0, W, H, "b")
    sh.circle_r(162, 52, 11, "y")
    sh.region(f"M{x0} 100Q40 70 76 92Q110 66 150 88Q172 76 {x0 + W} 84V{y0 + H}H{x0}Z", "l")
    sh.region("M96 80Q100 74 106 80V136H96Z", "t"); sh.ellipse_r(101, 138, 14, 4, "t")
    for y in (92, 104, 116, 128): sh.line(f"M98 {y}q3 3 6 0", "l", "stroke-width:1")
    sh.region(f"M{x0} 136Q60 124 100 138Q140 150 {x0 + W} 132V{y0 + H}H{x0}Z", "g")
    def boom(cx, h, r):
        sh.rect_r(cx - 4, y0 + H - h, 8, h, "w")
        for dx, dy, rr in [(-r * .6, 0, r * .7), (r * .6, 0, r * .7), (0, -r * .5, r * .8)]: sh.circle_r(cx + dx, y0 + H - h + dy, rr, "g")
    boom(34, 84, 18); boom(170, 70, 16)
    for x in (52, 64, 140):
        sh.line(f"M{x} {y0}Q{x - 4} {y0 + 20} {x + 2} {y0 + 38}", "l", "stroke-width:1.4")
        for k in range(3): sh.region(leaf_path(x - 1 + (3 if k % 2 else -3), y0 + 10 + k * 10, 2.6, 4.5, 40 if k % 2 else -40), "g")
    sh.rect_line(x0, y0, W, H, "cut")
    # voorgrond-strook met zijflappen
    sh.text(100, 168, "De voorgrond: plak de flappen vooraan tegen de zijkanten.", 6)
    fx0, fy0 = 22, 174
    pc = Pc(sh)
    d = f"M{fx0} {fy0 + 30}"
    pts = [(fx0, fy0 + 30)]
    for k in range(13):
        xx = fx0 + k * 12.5
        pts += [(xx + 3, fy0 + 10 + (k % 3) * 4), (xx + 6, fy0 + 18), (xx + 9, fy0 + 6 + (k % 2) * 6), (xx + 12.5, fy0 + 20)]
    pts += [(fx0 + 156, fy0 + 30)]
    pc.add(pts, "g")
    for s, xx in ((-1, fx0), (1, fx0 + 156)): pc.tab((xx, fy0 + 20), (xx, fy0 + 30), 12, (fx0 + 78, fy0 + 25), glue=True)
    pc.cut(2.5)
    sh.text(100, 222, "Dieren met een standaardje staan op blad 2.", 6)
    sh.legend(["cut", "fold", "glue"], 277)
    p2 = Sheet(); head(p2, "Dieren voor de kijkdoos")
    p2.text(100, 25, "Vouw elk standaardje naar achteren en plak het op de bodem.", 6)
    pack(p2, [[stand(jg_olifant), stand(jg_tijger), stand(jg_aap)], [stand(jg_papegaai), stand(jg_slang), stand(jg_kikker)], [stand(jg_varen), stand(jg_varen), stand(jg_varen)]], y0=30, ymax=268, gap=4, k=1.6)
    p2.legend(["cut", "fold", "glue"], 277)
    write(OUT, "kijkdoos-jungle", sh, {"category": "dieren", "age": "6-9", "kind": "knipplaat", "difficulty": 3, "minutes": 50, "adultHelp": True,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "plakband", "optional": True}],
        "i18n": {"nl": {"name": "Kijkdoos: de jungle in een schoenendoos", "printNote": "Je hebt ook een lege schoenendoos nodig. Print beide pagina's.", "steps": [
            "Zet een schoenendoos op zijn kant, met de open kant naar je toe.",
            "Kleur de achterwand, de voorgrond en de dieren op blad 2 in.",
            "Knip de achterwand uit en plak hem tegen de achterkant van de doos. Is hij te groot? Knip er een randje af.",
            "Knip de dieren uit. Vouw het standaardje onder elk dier naar achteren en plak het grijze vakje op de bodem van de doos. Zet de grote dieren achteraan en de kleine vooraan.",
            "Knip de voorgrond uit, vouw de flappen naar achteren en plak ze aan de binnenkant van de zijwanden, vooraan in de doos.",
            "Kijk erin: welke dieren zie jij in jouw jungle? Een papegaai kun je ook aan een draadje laten hangen."]}}},
        [("extra", "Dieren voor de kijkdoos", p2)])
kijkdoos()

# =====================================================================
# Stokpoppen: de grote raap (volksverhaal)
# =====================================================================
def stokvak(pc, y, w=10, h=22):
    pc.add(rect(-w / 2, y, w, h), "-")
    tq = pc.T(rect(-w / 2 + 1.2, y + 2, w - 2.4, h - 3.5)); pc.sh.raw(f'<path class="glue" d="{P(tq)}"/>')
def persoon(hair, dress, shirt, extra=None, h=1.0, beard=False):
    def fn(pc):
        stokvak(pc, 60 * h - 4)
        for x in (-6, 4): pc.add(rect(x, 44 * h, 4, 16 * h), "w" if dress else "n"); pc.add(rrect(x - 1, 60 * h - 4, 7, 4, 1.5), "x")
        if dress: pc.add(sample(f"M-8 {22 * h}H8L14 {48 * h}H-14Z"), dress)
        else: pc.add(rrect(-9, 22 * h, 18, 24 * h, 3), shirt)
        for s in (-1, 1): pc.add(bar(s * 8, 24 * h, s * 13, 40 * h, 2.6), shirt if not dress else dress); pc.add(circ(s * 13, 41 * h, 3), "k")
        hair(pc, h)
        pc.add(circ(0, 12, 10), "k"); pc.dot(-3.5, 10.5, 1.2); pc.dot(3.5, 10.5, 1.2); pc.ln(sample("M-3 15Q0 17.5 3 15", 4), style="stroke-width:1.1")
        if beard: pc.add(sample("M-9 13Q-8 26 0 28Q8 26 9 13Q6 18 0 18Q-6 18 -9 13Z"), "-")
        if extra: extra(pc, h)
    return fn
def haar_opa(pc, h):
    pc.add(sample("M-11 10C-12 2 -8 0 -6 2C-4 -2 4 -2 6 2C8 0 12 2 11 10Z"), "-")
def pet(pc, h): pc.add(sample("M-10 5C-10 -3 10 -3 10 5Z"), "g"); pc.add(sample("M4 3H16V6H4Z"), "g")
def haar_oma(pc, h):
    pc.add(circ(0, -2, 6), "z"); pc.add(sample("M-11 12C-12 0 12 0 11 12C9 6 -9 6 -11 12Z"), "z")
def bril(pc, h):
    for x in (-3.5, 3.5): pc.sh.circle_line(*pc.T([(x, 10.5)])[0], 2.8 * pc.sc, "l", f"stroke-width:{.9 * pc.sc}")
def haar_meisje(pc, h):
    for s in (-1, 1): pc.add(sample(f"M{s * 9} 6C{s * 18} 8 {s * 18} 22 {s * 14} 26C{s * 12} 20 {s * 10} 14 {s * 8} 12Z"), "y"); pc.add(circ(s * 10, 5, 2.4), "r")
    pc.add(sample("M-11 11C-12 0 12 0 11 11C8 5 -8 5 -11 11Z"), "y")
def dier_stok(body, y_stick):
    def fn(pc): stokvak(pc, y_stick); body(pc)
    return fn
def hond_b(pc): wrap(ic_hond, 1.4, -24, -30)(pc)
def kat_b(pc): wrap(ic_kat, 1.2, -24, -26)(pc)
def muis_b(pc): wrap(ic_muis, 1.0, -20, -26)(pc)
def raap(pc):
    for a in (-30, 0, 30): pc.add(sample(f"M0 -20Q{a * .2 - 8} -40 {a * .5} -54Q{a * .2 + 8} -40 0 -20Z"), "g")
    pc.add(sample("M0 -24C-26 -24 -34 -6 -30 8C-26 22 -10 30 0 44C10 30 26 22 30 8C34 -6 26 -24 0 -24Z"), "-")
    pc.add(sample("M-28 -2C-28 -18 -12 -24 0 -24C12 -24 28 -18 28 -2Q0 -10 -28 -2Z"), "p", sil=False)
    pc.ln(sample("M-14 12Q-10 14 -6 12", 4), style="stroke-width:1"); pc.ln(sample("M8 20Q12 22 16 20", 4), style="stroke-width:1")
    pc.ln([(0, 44), (1, 50)], style="stroke-width:1.2"); pc.sil(bar(0, 44, 1, 50, 1))
    stokvak(pc, 50, 10, 20)
def raap_verhaal(sh):
    paras = [
        ["Opa zaait een raapje in de moestuin.", "Het raapje groeit en groeit en groeit."],
        ["Het wordt een reuzenraap! Opa trekt aan de raap.", "Hij trekt en trekt... maar de raap zit vast."],
        ["Opa roept oma. Oma trekt aan opa,", "opa trekt aan de raap. Ze trekken en trekken...", "maar de raap zit vast."],
        ["Oma roept het meisje. Het meisje trekt aan oma,", "oma trekt aan opa, opa trekt aan de raap...", "maar de raap zit nog steeds vast."],
        ["Het meisje roept de hond. De hond roept de kat.", "Ze trekken allemaal... maar de raap zit vast."],
        ["Dan roept de kat het muisje.", "Het muisje trekt aan de kat, de kat aan de hond..."],
        ["FLOEP! De raap schiet uit de grond.", "Iedereen valt op een hoop! 's avonds eten ze", "samen raapsoep. Zelfs het muisje krijgt een kommetje."],
    ]
    sh.text(100, 34, "De grote raap (een oud volksverhaal)", 8)
    y = 48
    for i, para in enumerate(paras):
        sh.text(20, y, f"{i + 1}.", 6.5, "start")
        for ln_ in para: sh.text(28, y, ln_, 6.2, "start"); y += 8
        y += 5
    sh.text(100, y + 6, "Wie trekt aan wie? Zet de stokpoppen in een rij:", 6.5)
    names = ["raap", "opa", "oma", "meisje", "hond", "kat", "muis"]
    for k, n in enumerate(names):
        x = 20 + k * 26.7
        sh.rect_line(x - 11, y + 14, 22, 14, "l", 3, "stroke-width:.8"); sh.text(x, y + 23.5, n, 5.5)
        if k < 6: sh.line(f"M{x + 12} {y + 21}h3", "l", "stroke-width:1")
def stokpoppen():
    sh = Sheet(); head(sh, "Stokpoppen: de grote raap")
    sh.text(100, 25, "Kleur de poppen in, knip ze uit en plak een stokje op het grijze vak.", 6)
    pack(sh, [[raap, persoon(lambda p, h: (haar_opa(p, h), pet(p, h)), None, "b", beard=True), persoon(haar_oma, "p", "p", lambda p, h: bril(p, h)), persoon(haar_meisje, "r", "r", h=.85)],
              [dier_stok(hond_b, 10), dier_stok(kat_b, 12), dier_stok(muis_b, 1)]], y0=33, ymax=268, gap=4, k=2.0)
    sh.legend(["cut", "glue"], 277)
    vh = Sheet(); head(vh, "Het verhaal")
    raap_verhaal(vh)
    write(OUT, "stokpoppen-de-grote-raap", sh, {"category": "sprookjes", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 35, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "plakband", "optional": True}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Stokpoppen: de grote raap (met verhaal)", "printNote": "Je hebt ook 7 ijsstokjes, rietjes of satéprikkers zonder punt nodig. Op stevig papier blijven de poppen beter staan.", "steps": [
            "Kleur de raap, opa, oma, het meisje, de hond, de kat en het muisje in.",
            "Knip de poppen uit langs de streepjeslijn. Het witte vakje onderaan blijft eraan vast.",
            "Plak een ijsstokje of rietje op het grijze vak aan de achterkant. Met een stukje plakband eroverheen zit het extra stevig.",
            "Lees het verhaal op blad 2 voor. Wie in het verhaal komt, steekt zijn stokpop omhoog en trekt mee.",
            "Speel het verhaal na: zet de poppen achter elkaar in een rij en roep samen: FLOEP!"]}}},
        [("extra", "Het verhaal", vh)])
stokpoppen()

# =====================================================================
# Klappervogel: vleugels gaan omhoog als je aan het touwtje trekt
# =====================================================================
def kv_lijf(pc):
    pc.add(sample("M-6 50L-16 66L-6 64L0 70L6 64L16 66L6 50Z"), "b")
    pc.add(ellp(0, 26, 14, 28), "b")
    pc.add(ellp(0, 30, 8, 18), "y", sil=False)
    pc.add(circ(0, -8, 12), "b")
    pc.add(sample("M-4 -4L0 4L4 -4Z"), "o")
    for s in (-1, 1): pc.add(circ(s * 5, -10, 3.2), "-", sil=False); pc.dot(s * 5, -10, 1.4)
    pc.add(sample("M-3 -19Q0 -26 3 -19Z"), "b")
    for s in (-1, 1): pc.hole(s * 10, 16)
    pc.hole(0, -15)
def kv_vleugel(s):
    def fn(pc):
        # draaipunt (0,0), stompje naar binnen tot x = -s*7 met gaatje, vleugel naar buiten
        pc.add(rrect(-11 if s > 0 else -1, -4.5, 12, 9, 4), "b")
        pc.add(sample(f"M{-s * 3} -5C{s * 20} -14 {s * 50} -16 {s * 70} -8C{s * 62} -2 {s * 58} 0 {s * 60} 4C{s * 50} 4 {s * 46} 6 {s * 48} 10C{s * 36} 10 {s * 30} 12 {s * 30} 16C{s * 16} 12 {s * 6} 8 {-s * 3} 6Z"), "n")
        for k, (a, b) in enumerate([(20, -8), (36, -9), (50, -8)]): pc.ln(sample(f"M{s * a} {b}Q{s * (a + 6)} {b + 6} {s * (a + 4)} {b + 14}", 4), style="stroke-width:1")
        pc.hole(0, 0); pc.hole(-s * 6.5, 0)
    return fn
def klappervogel():
    sh = Sheet(); head(sh, "Klappervogel")
    sh.text(100, 25, "Trek aan het touwtje en de vogel klappert met zijn vleugels.", 6)
    place(sh, S(kv_lijf, 1.25), 74, 32)
    place(sh, S(kv_vleugel(-1), 1.3), 100, 158, "tc")
    place(sh, S(kv_vleugel(1), 1.3), 100, 210, "tc")
    # uitleg-tekeningetje achterkant
    sh.text(158, 46, "Achterkant:", 6.5)
    gx, gy = 158, 78
    sh.ellipse_r(gx, gy, 12, 22, "-")
    for s in (-1, 1):
        sh.line(f"M{gx + s * 6} {gy - 6}L{gx + s * 32} {gy - 20}", "l", "stroke-width:4")
        sh.dot(gx + s * 6, gy - 6, 1.6)
    sh.line(f"M{gx - 2} {gy - 4}Q{gx} {gy + 4} {gx + 2} {gy - 4}", "l", "stroke-width:1")
    sh.line(f"M{gx} {gy + 1}V{gy + 36}", "l", "stroke-width:1"); sh.line(f"M{gx - 3} {gy + 32}l3 4l3 -4", "l", "stroke-width:1")
    sh.text(gx, gy + 44, "touwtje tussen de", 5, cls="tip"); sh.text(gx, gy + 50, "stompjes, trek hier", 5, cls="tip")
    sh.text(30, 60, "Nodig:", 6.5); sh.text(30, 68, "2 splitpennen", 5.5); sh.text(30, 75, "2 stukken touw", 5.5)
    sh.legend(["cut"], 277)
    write(OUT, "klappervogel-met-touwtje", sh, {"category": "dieren", "age": "9+", "kind": "knipplaat", "difficulty": 3, "minutes": 40, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, SPLIT, {"slug": "touw"}, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": "Klappervogel met touwtje", "printNote": "Print op stevig papier (160 gram), anders zijn de vleugels te slap.", "steps": [
            "Kleur het lijf en de twee vleugels van de vogel in.",
            "Knip alles uit langs de streepjeslijn. Laat het ronde stompje aan de binnenkant van elke vleugel zitten.",
            "Prik een gaatje in elk rondje met een kruisje (laat een volwassene helpen): twee op het lijf, twee op elke vleugel en één in het kopje.",
            "Elke vleugel heeft twee gaatjes: één waar de vleugel begint en één aan het eind van het ronde stompje. Leg een vleugel achter het lijf, zo dat het gaatje waar de vleugel begint precies achter een gaatje in de buik ligt. Zet hem vast met een splitpen. Niet te strak: de vleugel moet makkelijk kunnen draaien. Doe hetzelfde aan de andere kant.",
            "Draai de vogel om. Knoop een touwtje van het gaatje aan het eind van het ene stompje naar het gaatje aan het eind van het andere stompje. Laat het touwtje een beetje slap hangen.",
            "Knoop een tweede lang touwtje in het midden van het eerste touwtje vast; dat hangt onder de vogel. Hang de vogel op aan een draadje door het kopje.",
            "Trek aan het onderste touwtje: de vleugels gaan omhoog. Laat los: ze zakken weer. Flap, flap!"]}}})
klappervogel()

# =====================================================================
# Lieveheersbeestjes: plak het goede aantal stippen
# =====================================================================
def lieveheersbeestjes():
    sh = Sheet(); head(sh, "Stippen tellen en plakken")
    sh.text(100, 25, "Lees het getal en plak zoveel stippen op het lieveheersbeestje.", 6)
    nums = [3, 1, 5, 2, 6, 4]
    for i, n in enumerate(nums):
        col, row = i % 3, i // 3
        cx, cy = 36 + col * 64, 72 + row * 80
        sh.circle_r(cx, cy - 23, 9, "x")
        for s in (-1, 1): sh.line(f"M{cx + s * 4} {cy - 30}Q{cx + s * 8} {cy - 37} {cx + s * 12} {cy - 37}", "l", "stroke-width:1.4")
        sh.circle_r(cx, cy, 24, "r")
        sh.seg(cx, cy - 24, cx, cy + 24, "l", "stroke-width:1.6")
        sh.circle_r(cx, cy + 31, 6.5, "-"); sh.text(cx, cy + 35, str(n), 10)
        for s in (-1, 1): sh.dot(cx + s * 3.5, cy - 27, 1.6) if False else None
    sh.text(100, 203, "Kleur de stippen zwart en knip ze los:", 6)
    C = 17; cols = 8; rows = 3; gx = 100 - cols * C / 2; gy = 208
    for r in range(rows):
        for c in range(cols): sh.circle_r(gx + c * C + C / 2, gy + r * C + C / 2, 6, "x")
    for r in range(rows + 1): sh.seg(gx, gy + r * C, gx + cols * C, gy + r * C, "cut")
    for c in range(cols + 1): sh.seg(gx + c * C, gy, gx + c * C, gy + rows * C, "cut")
    sh.text(100, 266, "Samen zijn het 21 stippen. Je hebt er 3 over voor een eigen beestje!", 5.5)
    sh.legend(["cut"], 277)
    an = Sheet(); head(an, "Antwoorden")
    for i, n in enumerate(nums):
        col, row = i % 3, i // 3
        cx, cy = 36 + col * 64, 72 + row * 80
        an.circle_r(cx, cy - 23, 9, "x"); an.circle_r(cx, cy, 24, "r"); an.seg(cx, cy - 24, cx, cy + 24, "l", "stroke-width:1.6")
        spots = {1: [(0, 0)], 2: [(-12, 0), (12, 0)], 3: [(-12, -8), (12, -8), (0, 12)], 4: [(-12, -9), (12, -9), (-12, 9), (12, 9)],
                 5: [(-12, -10), (12, -10), (-14, 6), (14, 6), (0, 16)], 6: [(-12, -12), (12, -12), (-15, 2), (15, 2), (-8, 15), (8, 15)]}[n]
        for x, y in spots: an.circle_r(cx + x * 1.05, cy + y * 1.05, 5.4, "x")
        an.circle_r(cx, cy + 31, 6.5, "-"); an.text(cx, cy + 35, str(n), 10)
    an.text(100, 214, "De stippen mogen overal zitten, als het aantal maar klopt.", 6)
    write(OUT, "lieveheersbeestjes-stippen-plakken", sh, {"category": "leren", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 20,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": "Lieveheersbeestjes: stippen tellen en plakken", "steps": [
            "Kleur de lieveheersbeestjes rood en hun kopjes zwart. Kleur ook de stippen onderaan zwart.",
            "Knip de rij stippen los langs de lange streepjeslijnen en knip daarna elk vakje los. Wil je, dan knip je de stip ook nog rond.",
            "Lees het getal onder elk lieveheersbeestje. Tel zoveel stippen af en plak ze op zijn rug.",
            "Tel nog eens na en kijk op het antwoordblad. Met de 3 stippen die over zijn maak je een eigen beestje: teken het zelf!"]}}},
        [("antwoorden", "Antwoorden", an)])
lieveheersbeestjes()

# =====================================================================
# Dieren van vormen: plak de vormen op de stippellijnen
# =====================================================================
def tri(cx, cy, w, h, up=True): return [(cx - w / 2, cy + h / 2), (cx, cy - h / 2), (cx + w / 2, cy + h / 2)] if up else [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx, cy + h / 2)]
def halfc(cx, cy, r): return ellp(cx, cy, r, r, a0=180, a1=360, n=60)
VORMDIEREN0 = [
    ("vis", [("cirkel", circ(54, 64, 24), "o"), ("driehoek", [(76, 64), (100, 44), (100, 84)], "y"), ("cirkel", circ(42, 58, 5), "-"), ("driehoek", tri(56, 38, 14, 10), "r")]),
    ("kat", [("halve cirkel", halfc(140, 84, 26), "z"), ("cirkel", circ(140, 44, 16), "z"), ("driehoek", tri(128, 26, 10, 12), "z"), ("driehoek", tri(152, 26, 10, 12), "z"),
             ("rechthoek", rect(166, 70, 22, 6), "z")]),
    ("uil", [("vierkant", rect(30, 140, 50, 50), "w"), ("cirkel", circ(44, 154, 9), "y"), ("cirkel", circ(66, 154, 9), "y"), ("driehoek", tri(55, 168, 10, 10, False), "o"),
             ("driehoek", tri(36, 134, 12, 12), "w"), ("driehoek", tri(74, 134, 12, 12), "w")]),
    ("huisje voor de muis", [("vierkant", rect(124, 150, 44, 44), "r"), ("driehoek", tri(146, 133, 56, 34), "b"), ("rechthoek", rect(140, 172, 12, 22), "y")]),
]
def _shift(pts, dy): return [(x, y + dy) for x, y in pts]
VORMDIEREN = [(n, [(t, _shift(pts, 12), c) for t, pts, c in parts]) for n, parts in VORMDIEREN0]
def vormendieren():
    sh = Sheet(); head(sh, "Vormen knippen")
    sh.text(100, 25, "Kleur de vormen, knip ze uit en plak ze op blad 2.", 6)
    pieces = []
    for _, parts in VORMDIEREN:
        for _, pts, code in parts:
            xs = [x for x, _ in pts]; ys = [y for _, y in pts]
            mx, my = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            pieces.append(lambda pc, pts=pts, code=code, mx=mx, my=my: pc.add([(x - mx, y - my) for x, y in pts], code))
    pieces.sort(key=lambda fn: -(bbox(fn)[3] - bbox(fn)[1]) * (bbox(fn)[2] - bbox(fn)[0]))
    y = flow(sh, pieces, 4, 34, 196, 6)
    assert y < 268
    sh.legend(["cut"], 277)
    pl = Sheet(); head(pl, "Plak de vormen op hun plek")
    pl.text(100, 25, "Zoek de vorm die precies op de stippellijn past.", 6)
    for name, parts in VORMDIEREN:
        for _, pts, _ in parts: pl.line(P(pts), "l", "stroke-width:1;stroke-dasharray:2.5 2")
    pl.text(64, 124, "een vis", 7); pl.text(150, 124, "een kat", 7); pl.text(55, 224, "een uil", 7); pl.text(146, 224, "een huisje", 7)
    pl.text(100, 250, "Teken zelf ogen, snorharen en een muisje bij het huis!", 6)
    write(OUT, "vormendieren-plakken", sh, {"category": "vormen", "age": "2-4", "kind": "knipplaat", "difficulty": 1, "minutes": 20, "adultHelp": True,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "potlood"}],
        "i18n": {"nl": {"name": "Dieren van vormen: knippen en plakken", "printNote": "Print beide pagina's op ware grootte (100%), dan passen de vormen precies.", "steps": [
            "Kleur de vormen in. Een volwassene helpt met knippen; rechte kanten knip je in één keer.",
            "Benoem samen de vormen: cirkel, halve cirkel, driehoek, vierkant en rechthoek.",
            "Zoek op blad 2 de stippellijn waar een vorm precies op past en plak hem daar. Begin met de grote vormen.",
            "Klaar? Teken er ogen, een mond en snorharen bij. Welke dieren heb je gemaakt?"]}}},
        [("extra", "Plakvel", pl)])
vormendieren()
