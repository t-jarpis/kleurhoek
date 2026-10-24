"""Batch 43d: knipplaten: aankleedpoppen, knipoefenbladen, knip-en-plak rekenen en taal, vingerpoppetjes, kettingen, fladderfiguren, plakscènes en bordspellen."""
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

# ---------- overgenomen uit batch 37b, 13b en 7b (gekopieerd, niet geïmporteerd) ----------
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
def chain_strip(sh, y, pw, h, n, polys, details, code_hint=None):
    x0 = (200 - pw * n) / 2
    sh.rect_line(x0, y, pw * n, h, "cut")
    for k in range(1, n): sh.seg(x0 + k * pw, y, x0 + k * pw, y + h, "fold")
    ps = [T(p, x0, y) for p in polys]
    for lp in outline(ps, 0, .25):
        for part in clip_x(lp, x0, x0 + pw): sh.line(PL(part), "cut")
    details(sh, x0, y)
    return x0

TOUW = {"slug": "touw"}
def M(pts, ax=50): return [(2 * ax - x, y) for x, y in pts][::-1]
def both(pc, pts, code, sil=True):
    pc.add(pts, code, sil); pc.add(M(pts), code, sil)

# =====================================================================
# Aankleedpoppen: één eigen figuur (kind) met kleren per seizoen
# =====================================================================
DK = 1.15  # schaal van pop en kleren
HEAD = (50, 36, 17)
def kid(hair):
    def fn(pc):
        hx, hy, hr = HEAD
        pc.add(rect(20, 198, 60, 17), "l")
        for x in range(26, 78, 6): pc.ln([(x, 215), (x + 2, 210)], style="stroke-width:.7")
        pc.ln([(20, 200), (80, 200)], "fold")
        if hair == "staartjes":
            for s in (-1, 1): pc.add(ellp(50 + s * 22, 34, 6, 9, s * 20), "w")
        if hair == "lang": pc.add(sample("M31 36C29 50 30 58 34 62H66C70 58 71 50 69 36Z"), "w")
        for s in (-1, 1):
            pc.add(bar(50 + s * 19, 62, 50 + s * 32, 112, 5), "-")
            pc.add(circ(50 + s * 32.5, 116, 5.5), "-")
            pc.add(bar(50 + s * 9, 126, 50 + s * 10, 192, 6.5), "-")
            pc.add(ellp(50 + s * 13, 195, 9, 5), "-")
        pc.add(rect(45, 50, 10, 9), "-")
        pc.add(sample("M30 66Q30 58 40 57H60Q70 58 70 66V122H30Z"), "-")
        pc.ln(sample("M40 57Q50 66 60 57", 6), style="stroke-width:.8")
        pc.add(sample("M30 116H70V130Q60 134 50 128Q40 134 30 130Z"), "b")
        pc.add(circ(hx, hy, hr), "-")
        if hair in ("kort", "staartjes", "lang"):
            pc.add(sample("M33 38C30 20 40 17 50 17C61 17 71 21 67 38C64 30 58 27 52 28Q46 26 40 29C37 31 35 34 33 38Z"), "w")
        if hair == "krullen":
            for a in range(150, 400, 25):
                t = math.radians(a); pc.add(circ(hx + 16 * math.cos(t), hy - 2 + 14 * math.sin(t), 5.2), "x")
        for s in (-1, 1): pc.dot(50 + s * 6, 38, 1.7); pc.add(circ(50 + s * 10, 44, 2.6), "k", sil=False)
        pc.ln(sample("M45 45Q50 49 55 45", 5), style="stroke-width:1.1")
        pc.ln(sample("M49 41Q48 43 50 43.5", 3), style="stroke-width:.8")
    return fn

def htab(pc, y1, y2):
    hx, hy, hr = HEAD
    for s in (-1, 1):
        p1 = (hx + s * math.sqrt(hr * hr - (y1 - hy) ** 2), y1); p2 = (hx + s * math.sqrt(hr * hr - (y2 - hy) ** 2), y2)
        pc.tab(p1, p2, 5, (hx, hy))
def shtab(pc):
    for s in (-1, 1): pc.tab((50 + s * 15, 56.4), (50 + s * 8, 55.6), 5, (50, 90))
def sidetab(pc, y1, y2, x=29):
    for s in (-1, 1): pc.tab((50 + s * (50 - x), y1), (50 + s * (50 - x), y2), 5, (50, (y1 + y2) / 2))

def torso_cloth(bottom, flare=0):
    return sample(f"M28 66Q28 56 40 55H44Q50 62 56 55H60Q72 56 72 66L{72 + flare} {bottom}H{28 - flare}Z")
def sleeve(pc, code, long=True, cuff=None):
    for s in (-1, 1):
        if long:
            pc.add(bar(50 + s * 19, 62, 50 + s * 31.6, 108, 7.2), code)
            if cuff: pc.add(bar(50 + s * 31, 106, 50 + s * 32, 111, 7.2), cuff)
        else:
            pc.add(bar(50 + s * 19, 62, 50 + s * 24, 82, 7.5), code)

def grip(pc, hx, code="-"):
    """Wit lusje over de hand, met een flapje om de hand heen te vouwen."""
    s = -1 if hx < 50 else 1
    pc.add(rrect(hx - 6.5, 110, 13, 12, 2.5), code)
    pc.tab((hx + s * 6.5, 112), (hx + s * 6.5, 120), 4.5, (hx, 116))
    pc.text(hx, 117.5, "hand", 3.2) if False else None
# ---- zomer ----
def tshirt_z(pc):
    shtab(pc); sleeve(pc, "y", False); pc.add(torso_cloth(120), "y")
    for x, y in [(40, 80), (58, 92), (44, 104), (62, 72), (50, 76)]: pc.add(circ(x, y, 2.6), "o", sil=False)
def korte_broek_z(pc):
    sidetab(pc, 118, 126)
    pc.add(sample("M29 116H71L73 146H53L50 132L47 146H27Z"), "t")
    pc.ln([(29, 121), (71, 121)], style="stroke-width:.8")
def badpak(pc):
    for s in (-1, 1): pc.tab((50 + s * 17, 60.3), (50 + s * 11, 60.3), 4.5, (50, 90))
    pc.add(sample("M33 60H39L41 70Q50 74 59 70L61 60H67L70 120L73 136H58Q50 128 42 136H27L30 120Z"), "m")
    for y in (90, 104): pc.ln(sample(f"M31 {y}Q40 {y - 5} 50 {y}Q60 {y + 5} 69 {y}", 8), style="stroke-width:.9")
def zonnehoed_z(pc):
    htab(pc, 30, 37)
    pc.add(sample("M35 32C35 18 42 13 50 13C58 13 65 18 65 32Z"), "y")
    pc.add(ellp(50, 32, 27, 5.5), "y"); pc.add(rect(35.3, 25, 29.4, 5), "r", sil=False)
    pc.add(ellp(64, 26, 3.4, 2.2, -20), "m", sil=False)
def zonnebril_z(pc):
    for s in (-1, 1):
        pc.add(bar(50 + s * 12, 37, 50 + s * 17.5, 37, 1.3), "x")
        pc.tab((50 + s * 17.5, 35.3), (50 + s * 17.5, 38.7), 4.5, (50, 37))
        pc.add(ellp(50 + s * 6.8, 38, 5.6, 4.4), "n")
    pc.add(bar(48, 37, 52, 37, 1), "x")
def slipper(x):
    def fn(pc):
        s = -1 if x < 50 else 1
        pc.tab((x + s * 9.6, 192.5), (x + s * 9.6, 197.5), 4, (x, 195))
        pc.add(ellp(x, 196, 10, 5), "g")
        pc.ln(sample(f"M{x - 6} 196Q{x} 189 {x + 6} 196", 5), style="stroke-width:1.8")
    return fn
def emmer_z(pc):
    grip(pc, 17.5)
    pc.add(sample("M8 126H28L26 148H10Z"), "r"); pc.add(rect(7, 123, 22, 4), "r")
    pc.ln(sample("M9 124Q12 118 14 117", 4), style="stroke-width:1.2"); pc.ln(sample("M27 124Q24 118 21 117", 4), style="stroke-width:1.2")
    pc.add(star_pts(18, 137, 5, 2.2), "y", sil=False)
def zwembroek(pc):
    sidetab(pc, 117, 124)
    pc.add(sample("M29 116H71L72 138H54L50 130L46 138H28Z"), "n")
    for x in (36, 44, 58, 66): pc.ln([(x, 120), (x - 2, 134)], style="stroke-width:.8")
def ijsje(pc):
    grip(pc, 82.5)
    pc.add([(77, 122), (88, 122), (82.5, 146)], "w")
    for k in range(3): pc.ln([(78.5 + k * 3, 123), (82 + k * 2, 133)], style="stroke-width:.6")
    pc.add(circ(82.5, 103, 7), "m"); pc.add(circ(82.5, 92, 6), "y"); pc.add(ellp(86, 87, 2, 2.6), "r")
    pc.sil(rect(77, 103, 11, 8))
def zwembandjes(pc):
    for s in (-1, 1):
        cx = 50 + s * 22.5
        pc.add(ellp(cx, 74, 8.5, 6, s * -15), "o")
        pc.ln(sample(f"M{cx - 6} 74Q{cx} 71 {cx + 6} 74", 4), style="stroke-width:.8")
        pc.tab((cx - 3, 68.5), (cx + 3, 68.5), 4, (cx, 74))
zomer_items = [tshirt_z, korte_broek_z, badpak, zonnehoed_z, zonnebril_z, zwembandjes, slipper(37), slipper(63)]

# ---- winter ----
def winterjas_w(pc):
    shtab(pc); sleeve(pc, "r", True, "-")
    pc.add(torso_cloth(150, 3), "r")
    pc.add(sample("M40 55Q50 66 60 55L62 60Q50 72 38 60Z"), "-")
    pc.ln([(50, 66), (50, 150)])
    for y in (82, 100, 118, 136): pc.add(rrect(51.5, y - 1.5, 6, 3, 1.5), "w", sil=False)
    for x in (32, 60): pc.ln([(x, 126), (x + 8, 126), (x + 8, 134)], style="stroke-width:.9")
    pc.add(rect(25, 144, 50, 6), "-", sil=False)
def winterbroek(pc):
    sidetab(pc, 118, 126)
    pc.add(sample("M29 116H71L70 186H53L50 136L47 186H30Z"), "n")
    for x in (34, 64): pc.ln([(x, 150), (x, 182)], style="stroke-width:.8")
def muts_w(pc):
    htab(pc, 27, 34)
    pc.add(sample("M33.5 28C33 15 41 9 50 9C59 9 67 15 66.5 28Z"), "b")
    pc.add(rrect(32, 25, 36, 8, 3), "n"); pc.add(circ(50, 7, 5.5), "-")
    for x in (42, 58): pc.ln(sample(f"M{x} 25Q{x + (1 if x < 50 else -1) * 2} 17 {x + (1 if x < 50 else -1) * 3} 12", 5), style="stroke-width:.8")
def sjaal_w(pc):
    pc.tab((38, 55), (38, 63), 5, (50, 59)); pc.tab((62, 55), (62, 63), 5, (50, 59))
    pc.add(rect(52, 60, 9, 30), "g"); pc.add(rrect(37, 53, 26, 10, 4), "g")
    for y in (70, 80): pc.ln([(52, y), (61, y)], style="stroke-width:.9")
    for x in (54, 56.5, 59): pc.ln([(x, 90), (x, 95)], style="stroke-width:.9")
    pc.sil(rect(52, 90, 9, 5))
def trui_w(pc):
    shtab(pc); sleeve(pc, "b", True, "n")
    pc.add(torso_cloth(124), "b"); pc.add(rect(28, 118, 44, 6), "n", sil=False)
    pc.add(sample("M40 55Q50 64 60 55L61 58Q50 68 39 58Z"), "n", sil=False)
    for k in range(5):
        cx = 34 + k * 8; pc.add(star_pts(cx, 92, 3.4, 1.4, 6), "-", sil=False)
def want(x):
    def fn(pc):
        s = -1 if x < 50 else 1
        pc.tab((x - 4.5, 109.5), (x + 4.5, 109.5), 4, (x, 116))
        pc.add(sample(f"M{x - 6.5} 110H{x + 6.5}V119Q{x + 6.5} 125 {x} 125Q{x - 6.5} 125 {x - 6.5} 119Z"), "y")
        pc.add(ellp(x - s * 7, 115, 2.6, 4, s * 20), "y")
        pc.add(rect(x - 6.5, 109.5, 13, 3.5), "-", sil=False)
    return fn
def laars_w(x, code="w", rain=False):
    def fn(pc):
        s = -1 if x < 50 else 1
        pc.tab((x + s * 7.5, 170), (x + s * 7.5, 177), 4.5, (x, 180))
        pc.add(rect(x - 7.5, 166, 15, 28), code)
        pc.add(ellp(x + s * 3, 195, 10.5, 6), code)
        if not rain: pc.add(rrect(x - 8.5, 164, 17, 6, 2.5), "-")
        else: pc.ln([(x - 7.5, 172), (x + 7.5, 172)], style="stroke-width:.8")
        pc.ln([(x - 7, 192), (x + 4 * s + 6, 192)], style="stroke-width:.7") if not rain else None
    return fn
def slee(pc):
    pc.tab((84.5, 110), (84.5, 117), 4, (82, 113))
    pc.ln([(83, 114), (90, 130)], style="stroke-width:1.2"); pc.sil(bar(83, 114, 90, 130, 1))
    pc.add(rect(80, 130, 30, 6), "w"); pc.add(sample("M78 140H112Q118 140 116 134"), "x") if False else None
    pc.add(sample("M78 138H110Q116 138 116 132H113Q113 135 110 135H78Z"), "z")
    for x in (84, 104): pc.add(rect(x, 135, 2.5, 3), "z", sil=False)
winter_items = [winterjas_w, winterbroek, muts_w, sjaal_w, want(17.5), want(82.5), laars_w(37), laars_w(63)]

# ---- herfst (regen) ----
def regenjas_h(pc):
    shtab(pc); sleeve(pc, "y")
    pc.add(torso_cloth(142, 5), "y")
    pc.add(sample("M40 55L50 68L60 55Q50 52 40 55Z"), "-")
    pc.ln([(50, 68), (50, 142)])
    for y in (84, 104, 124): pc.add(rrect(46, y - 1.5, 8, 3, 1.5), "w", sil=False)
    for x in (31, 60): pc.ln([(x, 116), (x + 9, 116), (x + 9, 126)], style="stroke-width:.9")
def zuidwester(pc):
    htab(pc, 30, 37)
    pc.add(sample("M34 33C34 18 41 13 50 13C59 13 66 18 66 33Z"), "y")
    pc.add(sample("M28 33Q50 26 72 33L75 39Q50 32 25 39Z"), "y")
    pc.ln(sample("M36 26Q50 21 64 26", 6), style="stroke-width:.8")
def paraplu(pc):
    pc.add(bar(83, 70, 83, 110, 1.1), "x")
    grip(pc, 82.5, "w")
    pc.add(sample("M58 72Q60 44 83 42Q106 44 108 72Q102 66 95.5 72Q89 66 83 72Q77 66 70.5 72Q64 66 58 72Z"), "p")
    for x in (70.5, 95.5): pc.ln(sample(f"M{x} 72Q{x + (83 - x) * .45} 52 83 42", 5), style="stroke-width:.8")
    pc.add(bar(83, 42, 83, 37, 1), "x")
def trui_h(pc):
    shtab(pc); sleeve(pc, "o", True, "o")
    pc.add(torso_cloth(124), "o")
    pc.add(rect(28, 118, 44, 6), "o", sil=False)
    for y in (78, 94):
        for k in range(5): pc.add([(32 + k * 8, y), (36 + k * 8, y - 5), (40 + k * 8, y)], "w", sil=False)
def lange_broek_h(pc):
    sidetab(pc, 118, 126)
    pc.add(sample("M29 116H71L70 188H53L50 136L47 188H30Z"), "n")
    pc.ln([(29, 121), (71, 121)], style="stroke-width:.8")
    for x in (36, 58): pc.add(rect(x, 140, 7, 8), "b", sil=False)
def sjaal_h(pc):
    pc.tab((38, 55), (38, 63), 5, (50, 59)); pc.tab((62, 55), (62, 63), 5, (50, 59))
    pc.add(rect(40, 60, 9, 32), "o"); pc.add(rrect(37, 53, 26, 10, 4), "o")
    for y in (68, 76, 84): pc.add(rect(40, y, 9, 3), "r", sil=False)
    for x in (42, 44.5, 47): pc.ln([(x, 92), (x, 97)], style="stroke-width:.9")
    pc.sil(rect(40, 92, 9, 5))
def kastanje(pc):
    grip(pc, 17.5)
    pc.add(sample("M7 130C7 122 14 121 18 124C22 121 29 122 29 130C29 140 22 144 18 144C14 144 7 140 7 130Z"), "w")
    pc.add(sample("M12 125Q18 121 24 125Q18 128 12 125Z"), "-", sil=False)
    pc.ln(sample("M17.5 122V124", 2), style="stroke-width:1")

# ---- lente ----
def tuinbroek(pc):
    for s in (-1, 1): pc.tab((50 + s * 16, 57.6), (50 + s * 10.4, 57.6), 4.5, (50, 90))
    pc.add(sample("M33 58H40L42 80H58L60 58H67L65 82L71 116L72 150H53L50 134L47 150H28L29 116L35 82Z"), "b")
    pc.add(rrect(42, 86, 16, 14, 2), "b", sil=False)
    for x in (38, 62): pc.add(circ(x, 80, 2), "y", sil=False)
    pc.ln(sample("M44 92Q50 96 56 92", 4), style="stroke-width:.8")
def bloesje(pc):
    shtab(pc); sleeve(pc, "k", False); pc.add(torso_cloth(120), "k")
    pc.add(sample("M40 55L45 63L50 57L55 63L60 55Q50 52 40 55Z"), "-")
    for y in (72, 86, 100, 112): pc.add(circ(50, y, 1.4), "-", sil=False)
def petje(pc):
    htab(pc, 28, 34)
    pc.add(sample("M34 30C34 17 41 12 50 12C59 12 66 17 66 30Z"), "g")
    pc.add(sample("M50 30H78Q80 34 74 34H50Z"), "g"); pc.add(circ(50, 12, 2.2), "g")
def gieter(pc):
    grip(pc, 82.5)
    pc.add(sample("M76 122H100V144Q100 148 96 148H80Q76 148 76 144Z"), "t")
    pc.add(bar(98, 128, 112, 114, 2), "t"); pc.add(ellp(113, 112.5, 4, 2.2, -45), "t")
    pc.ln(sample("M88 122Q94 112 98 122", 6), style="stroke-width:2"); pc.sil(bar(88, 122, 93, 114, 1.5)); pc.sil(bar(98, 122, 93, 114, 1.5))
    for k, (x, y) in enumerate([(118, 116), (121, 121), (119, 126)]): pc.add(ellp(x, y, 1.2, 1.8), "b", sil=False)
def rokje(pc):
    sidetab(pc, 117, 124, 30)
    pc.add(sample("M30 115H70L78 150H22Z"), "r")
    for x, y in [(36, 128), (50, 138), (62, 126), (44, 122), (68, 142), (30, 144), (56, 146)]: pc.add(circ(x, y, 2), "-", sil=False)
def vestje(pc):
    shtab(pc); sleeve(pc, "l", True, "g")
    pc.add(sample("M28 66Q28 56 40 55L49 92V124H28Z"), "l"); pc.add(sample("M72 66Q72 56 60 55L51 92V124H72Z"), "l")
    pc.sil(rect(48, 95, 4, 28))
    for y in (98, 108, 118): pc.add(circ(46, y, 1.6), "y", sil=False)
def gymp(x):
    def fn(pc):
        s = -1 if x < 50 else 1
        pc.tab((x - 5, 188), (x + 5, 188), 4, (x, 195))
        pc.add(sample(f"M{x - 6} 188H{x + 6}V190Q{x + 6 + s * 2} 191 {x + 6 * s + s * 6} 196Q{x + 3 * s} 201 {x - 3 * s} 201Q{x - 9 * s} 200 {x - 7 * s} 192Z") if False else union([rect(x - 6, 188, 12, 8), ellp(x + s * 3, 196, 10.5, 5)]), "r")
        pc.add(rect(x - 7 + s * 3, 199, 21, 2.2) if False else ellp(x + s * 3, 199.5, 10, 1.6), "-", sil=False)
        for y in (190.5, 193): pc.ln([(x - 3, y), (x + 3, y)], style="stroke-width:.8")
    return fn
def bloemkrans(pc):
    htab(pc, 22, 27)
    for k in range(7):
        a = math.radians(200 + k * 23.3); cx, cy = 50 + 18.5 * math.cos(a), 36 + 18.5 * math.sin(a)
        pc.add(circ(cx, cy, 4.2), "ymykmym"[k]); pc.add(circ(cx, cy, 1.5), "o", sil=False)
lente_items = [tuinbroek, bloesje, petje, bloemkrans, gieter, gymp(37), gymp(63)]

def aankleedpop(slug, name, hair, items_p1, items_p2, season, age, color_tip, extra_steps, cat="thuis"):
    sh = Sheet(); head(sh, name.split(": ")[0])
    place(sh, S(kid(hair), DK), 0, 24)
    flow(sh, [S(fn, DK) for fn in items_p1], 116, 26, 199, gap=2)
    sh.legend(["cut", "fold"], 277)
    p2 = Sheet(); head(p2, "Nog meer " + season + "kleren")
    pack(p2, items_p2, y0=26, ymax=268, gap=3, k=DK)
    p2.legend(["cut", "fold"], 277)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": 2, "minutes": 40, "adultHelp": age == "2-4", "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, STEVIG],
        "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier (160 gram), dan blijft de pop beter staan en gaan de flapjes minder snel stuk.", "steps": [
            "Kleur de pop en alle kleren in. " + color_tip,
            "Knip alles uit langs de streepjeslijn. Knip de witte flapjes niet af: die heb je nodig.",
            "Vouw het grasstrookje onder de voeten naar achteren, dan blijft de pop staan.",
            "Leg een kledingstuk op de pop en vouw de witte flapjes om de rand naar achteren. Zo blijft het zitten.",
        ] + extra_steps}}}, [("extra", "Nog meer " + season + "kleren", p2)])

aankleedpop("aankleedpop-zomer-aan-zee", "Aankleedpop: zomer aan zee", "staartjes",
    [tshirt_z, korte_broek_z, zonnehoed_z],
    [[badpak, zwembroek], [zwembandjes, zonnebril_z, slipper(37), slipper(63)], [emmer_z, ijsje]], "zomer", "4-6",
    "Wat voor haar heeft jouw pop? Kleur het zoals jij wilt.", ["Gaat de pop zwemmen of een ijsje eten? Trek het badpak met de zwembandjes aan, of het T-shirt met de korte broek."])
aankleedpop("aankleedpop-winter-in-de-sneeuw", "Aankleedpop: winter in de sneeuw", "krullen",
    [winterjas_w, muts_w],
    [[trui_w, winterbroek], [sjaal_w, want(17.5), want(82.5), laars_w(37), laars_w(63)]], "winter", "4-6",
    "De jas en de muts mogen echte winterkleuren krijgen.", ["Begin met de broek, dan de laarzen, dan de jas en tot slot de sjaal, de muts en de wanten. Zo doe je het ook als je echt naar buiten gaat!"])
aankleedpop("aankleedpop-herfst-in-de-regen", "Aankleedpop: herfst in de regen", "kort",
    [regenjas_h, zuidwester],
    [[trui_h, lange_broek_h], [paraplu, sjaal_h, kastanje, laars_w(37, "g", True), laars_w(63, "g", True)]], "herfst", "4-6",
    "Een gele regenjas zie je goed in het donker.", ["Regent het? Trek de regenjas, de regenhoed en de laarzen aan en geef de pop de paraplu in de hand. Haak het flapje om de hand."])
aankleedpop("aankleedpop-lente-in-de-tuin", "Aankleedpop: lente in de tuin", "lang",
    [tuinbroek, bloesje],
    [[vestje, rokje], [petje, bloemkrans, gieter, gymp(37), gymp(63)]], "lente", "4-6",
    "Geef het bloesje een vrolijk lentekleurtje.", ["Trek eerst het bloesje aan en dan de tuinbroek eroverheen. Geef de pop de gieter: dan kan hij de bloemen water geven."])
