"""Batch 7b: knip-, plak- en knutselbladen (knipplaat) en vouwbladen (vouwblad), A4."""
import math, re, random
from lib_gen import *
from shapes import heart_path, moon_path, star_path, cloud_path, leaf_path, fish_path

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

# =====================================================================
# Knip-en-plak-collages: een knipvel met losse stukjes en een plakvel
# =====================================================================
def collage(slug, name, heading, pieces_page, glue_page, cat, age, steps, minutes=30, holiday=None, diff=2):
    sh = Sheet(); head(sh, heading)
    pieces_page(sh); sh.legend(["cut"], 277)
    pv = Sheet(); glue_page(pv)
    meta = {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": minutes,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": name, "printNote": "Print beide pagina's: de eerste is het knipvel, de tweede het plakvel.", "steps": steps}}}
    if holiday: meta["holiday"] = holiday
    write(OUT, slug, sh, meta, [("extra", "Plakvel", pv)])

# ---------- bouw een monster ----------
def m_body_blob(pc):
    pc.add(sample("M0 -40C24 -40 34 -20 34 4C34 30 24 42 0 42C-24 42 -34 30 -34 4C-34 -20 -24 -40 0 -40Z"), "p")
    pc.add(ellp(0, 14, 20, 22), "k", sil=False)
    for x, y, r in [(-22, -14, 4), (20, -22, 3), (26, 4, 3.5), (-26, 16, 3)]: pc.add(circ(x, y, r), "m", sil=False)
def m_body_fur(pc):
    pts = []
    for k in range(56):
        a = math.radians(k * 360 / 56); r = 38 if k % 2 == 0 else 33
        pts.append((r * math.cos(a), r * 1.08 * math.sin(a)))
    pc.add(pts, "b")
    pc.add(ellp(0, 8, 18, 20), "-", sil=False)
    for y in (-2, 8, 18): pc.ln(sample(f"M-12 {y}Q0 {y + 4} 12 {y}", 6), style="stroke-width:1")
def m_body_tall(pc):
    pc.add(rrect(-24, -42, 48, 84, 18), "g")
    for y in (-26, -10, 6, 22): pc.ln(sample(f"M-24 {y}Q0 {y + 8} 24 {y}", 8), style="stroke-width:1")
def m_eye_big(pc):
    pc.add(circ(0, 0, 15), "-"); pc.add(circ(0, 1, 7.5), "g", sil=False); pc.dot(0, 1, 3.4); pc.add(circ(2.5, -1.5, 1.4), "-", sil=False)
def m_eye_stalk(pc):
    pc.add(bar(0, 0, 0, -24, 2.6), "l"); pc.add(ellp(0, 2, 6, 3), "l")
    pc.add(circ(0, -28, 8), "-"); pc.dot(1.5, -28, 3)
def m_eye_small(pc):
    pc.add(circ(0, 0, 7), "-"); pc.dot(1, 1, 2.8)
def m_mouth_fangs(pc):
    pc.add(sample("M-22 0Q0 5 22 0Q16 20 0 20Q-16 20 -22 0Z"), "x")
    for s in (-1, 1): pc.add([(s * 14, 2.2), (s * 8, 3.2), (s * 11, 11)], "-", sil=False)
def m_mouth_grin(pc):
    pc.add(sample("M-24 -4Q0 4 24 -4Q20 18 0 18Q-20 18 -24 -4Z"), "r")
    pc.add(sample("M-10 15Q-10 6 0 6Q10 6 10 15Q0 19 -10 15Z"), "m", sil=False)
    pc.ln(sample("M-23 -2Q0 6 23 -2", 8))
def m_mouth_teeth(pc):
    pc.add(rrect(-22, -8, 44, 16, 6), "-")
    pc.ln([(-22, 0), (22, 0)])
    for x in range(-15, 20, 7): pc.ln([(x, -8), (x, 8)])
def m_horn(pc, s=1):
    pc.add(sample(f"M{-8 * s} 10C{-10 * s} -4 {-2 * s} -18 {14 * s} -24C{4 * s} -14 {6 * s} 0 {8 * s} 10Z"), "y")
    for y in (2, -6): pc.ln(sample(f"M{-8.5 * s} {y + 1}Q0 {y - 2} {7.5 * s} {y + 1}", 4), style="stroke-width:1")
def m_antenna(pc):
    pc.add(bar(0, 0, 4, -26, 1.6), "z"); pc.add(circ(5, -30, 6), "r"); pc.add(circ(3, -32, 1.8), "-", sil=False)
def taper(pts, w0, w1):
    """Veelhoek rond een middenlijn die van halve breedte w0 naar w1 versmalt."""
    n = len(pts); left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        w = w0 + (w1 - w0) * i / (n - 1)
        left.append((x - dy / l * w, y + dx / l * w)); right.append((x + dy / l * w, y - dx / l * w))
    return left + right[::-1]
def m_tentacle(pc, s=1):
    c = [(s * x, y) for x, y in sample("M0 0C14 -2 24 8 30 18C36 28 46 30 48 22C49 17 44 14 40 18", 14)]
    pc.add(taper(c, 7, 2.2), "p"); pc.add(circ(s * 41.5, 19.5, 2.4), "p")
    for x, y in [(10, 2), (18, 6), (25, 12), (31, 20)]: pc.add(circ(x * s, y + 2.5, 1.7), "k", sil=False)
def m_claw(pc, s=1):
    pc.add(bar(0, 0, 26 * s, -4, 5), "o")
    for a in (-38, 0, 38):
        t = math.radians(a); pc.add(ellp(34 * s + 11 * math.cos(t) * s, -5 + 11 * math.sin(t), 7, 3.6, a * s), "o")
        pc.add([(34 * s + 16 * math.cos(t) * s, -5 + 16 * math.sin(t) - 2), (34 * s + 23 * math.cos(t) * s, -5 + 23 * math.sin(t)), (34 * s + 16 * math.cos(t) * s, -5 + 16 * math.sin(t) + 2)], "-")
    pc.add(circ(34 * s, -5, 8.5), "o")
def m_foot(pc):
    pc.add(bar(0, -20, 0, 0, 7), "g")
    pc.add(sample("M-12 6C-14 -4 -4 -8 6 -6C14 -5 22 -2 24 6Z"), "g")
    for x in (2, 10, 18): pc.add([(x - 4, 5.5), (x + 4, 5.5), (x + 1, 12)], "-")
def m_tail(pc):
    c = sample("M0 0C14 4 26 4 36 -4C42 -9 48 -8 50 -2", 14)
    pc.add(taper(c, 7, 2), "l")
    for i in (2, 5, 8, 11):
        (x0, y0), (x1, y1) = c[i - 1], c[i + 1]; dx, dy = x1 - x0, y1 - y0; l = math.hypot(dx, dy)
        nx, ny = dy / l, -dx / l; w = 7 - 5 * i / 14; x, y = c[i]
        pc.add([(x - dx / l * 4 + nx * (w - 1), y - dy / l * 4 + ny * (w - 1)), (x + nx * (w + 8), y + ny * (w + 8)), (x + dx / l * 4 + nx * (w - 1), y + dy / l * 4 + ny * (w - 1))], "y")
def m_wing(pc, s=1):
    pc.add(sample(f"M0 0L{30 * s} -26Q{32 * s} -10 {44 * s} -6Q{36 * s} 0 {38 * s} 10Q{26 * s} 4 {20 * s} 14Q{14 * s} 4 0 6Z"), "x")
    for x, y in [(30, -26), (44, -6), (38, 10)]: pc.ln([(0, 3), (x * s * .8, y * .8)], style="stroke-width:.9")
def m_spot(pc, code="y"): pc.add(circ(0, 0, 6), code)
def monster_knip(sh):
    sh.text(100, 25, "Kleur alle stukjes, knip ze uit en bouw je eigen monster.", 6)
    y = flow(sh, [S(m_body_blob, .68), S(m_body_fur, .68), S(m_body_tall, .68)], 2, 28, 198, 6)
    y = flow(sh, [m_eye_big, m_eye_stalk, m_eye_stalk] + [m_eye_small] * 3 + [m_antenna, m_antenna], 2, y + 1, 198, 2)
    y = flow(sh, [S(m_mouth_fangs, .85), S(m_mouth_grin, .85), S(m_mouth_teeth, .85), S(L(m_horn, 1), .85), S(L(m_horn, -1), .85)], 2, y + 1, 198, 2)
    y = flow(sh, [S(L(m_tentacle, 1), .85), S(L(m_tentacle, -1), .85), m_tail], 2, y + 1, 198, 3)
    flow(sh, [m_foot, m_foot, S(L(m_wing, 1), .8), S(L(m_wing, -1), .8)], 2, y + 1, 198, 4)
def monster_plak(sh):
    head(sh, "Mijn monster")
    sh.region(moon_path(32, 52, 15), "y")
    for x, y in [(160, 40), (178, 62), (140, 66), (70, 36)]: sh.poly_r(star_pts(x, y, 5, 2.2), "y")
    sh.region("M0 280V214Q40 200 90 212T200 206V280Z", "l")
    for x, y, rx in [(30, 236, 12), (170, 232, 9), (120, 244, 7)]: sh.ellipse_r(x, y, rx, rx * .6, "z")
    for x in (60, 146, 186): sh.line(f"M{x} 226l3 -7l3 7M{x + 8} 226l2 -5l2 5", "l", "stroke-width:1.2")
    sh.text(100, 264, "Mijn monster heet: ..............................", 7.5)
collage("bouw-een-monster-plakken", "Bouw een monster: knippen en plakken", "Monster: knipvel", monster_knip, monster_plak, "sprookjes", "4-6", [
    "Kleur alle stukjes in. Monsters mogen elke kleur hebben!",
    "Knip de stukjes uit langs de streepjeslijn.",
    "Kies een lijf en leg het op het plakvel. Leg er ogen, een mond, hoorns, armen, voeten en misschien een staart of vleugels bij. Probeer verschillende monsters uit.",
    "Plak je monster vast met de lijmstift en verzin een naam. Wat eet jouw monster het liefst?"], minutes=30)

# ---------- bouw een ruimteschip ----------
def rs_romp(pc):
    pc.add(rrect(-18, -32, 36, 72, 5), "z")
    for y in (-18, 22): pc.ln([(-18, y), (18, y)])
    for x, y in [(-13, -26), (13, -26), (-13, 34), (13, 34)]: pc.dot(x, y, 1.3)
def rs_neus(pc):
    pc.add(sample("M-20 0C-18 -20 -8 -32 0 -38C8 -32 18 -20 20 0Z"), "r")
    pc.ln(sample("M-12 -18Q0 -14 12 -18", 6))
def rs_raam(pc):
    pc.add(circ(0, 0, 11), "-"); pc.add(circ(0, 0, 7), "b", sil=False); pc.ln(sample("M-3 -4Q-1 -6 2 -6", 4), style="stroke-width:1.2")
def rs_vleugel(pc, s=1):
    pc.add([(0, 0), (s * 10, 0), (s * 28, 26), (s * 28, 42), (0, 30)], "r")
    pc.ln([(s * 6, 8), (s * 22, 30)], style="stroke-width:1.2")
def rs_motor(pc):
    pc.add(rect(-10, 0, 20, 12), "z"); pc.add([(-8, 12), (8, 12), (12, 24), (-12, 24)], "x")
def rs_vlam(pc):
    pc.add(sample("M-12 0H12C14 14 8 24 4 32C3 24 1 26 0 36C-1 26 -3 24 -4 32C-8 24 -14 14 -12 0Z"), "o")
    pc.add(sample("M-6 2H6C7 10 4 16 0 22C-4 16 -7 10 -6 2Z"), "y", sil=False)
def rs_antenne(pc):
    pc.add(bar(0, 0, 0, -18, 1.6), "z"); pc.add(sample("M-12 -24Q0 -12 12 -24Q0 -18 -12 -24Z"), "z"); pc.add(circ(0, -27, 3), "r")
def rs_astronaut(pc):
    for s in (-1, 1):
        pc.add(rrect(s * 6 - 4, 18, 8, 16, 3), "-"); pc.add(rrect(s * 6 - 5, 32, 10, 6, 2), "z")
        pc.add(bar(s * 10, 6, s * 20, 18, 3.4), "-"); pc.add(circ(s * 20, 19, 4), "z")
    pc.add(rrect(-12, 2, 24, 20, 5), "-")
    pc.add(rect(-6, 8, 12, 7), "r", sil=False)
    pc.add(circ(0, -8, 12), "-"); pc.add(rrect(-8, -14, 16, 11, 5), "b", sil=False)
    pc.ln(sample("M-4 -12Q-1 -13 1 -11", 4), style="stroke-width:1")
def rs_alien(pc):
    pc.add(bar(-6, -12, -12, -24, 1.4), "l"); pc.add(bar(6, -12, 12, -24, 1.4), "l")
    pc.add(circ(-12, -25, 3.2), "y"); pc.add(circ(12, -25, 3.2), "y")
    pc.add(sample("M-14 20C-14 8 -10 4 -8 2C-14 -2 -16 -8 -14 -12C-10 -18 10 -18 14 -12C16 -8 14 -2 8 2C10 4 14 8 14 20Z"), "l")
    for x in (-6, 0, 6): pc.add(circ(x, -8, 3), "-", sil=False); pc.dot(x, -7.6, 1.3)
    pc.ln(sample("M-5 -1Q0 3 5 -1", 4)); pc.add(ellp(0, 12, 6, 5), "y", sil=False)
def rs_planeet(pc):
    pc.add(ellp(0, 0, 30, 8, -15), "y"); pc.add(circ(0, 0, 17), "p")
    pc.add(ellp(0, 0, 30, 8, -15, a0=0, a1=180) + ellp(0, 0, 20, 3.5, -15, a0=0, a1=180)[::-1], "y", sil=False)
    pc.ln(sample("M-14 -6Q0 -2 15 -8", 6), style="stroke-width:1.2"); pc.ln(sample("M-16 4Q0 8 16 2", 6), style="stroke-width:1.2")
def rs_ster(pc): pc.add(star_pts(0, 0, 10, 4.2), "y")
def rs_komeet(pc):
    pc.add(sample("M0 -7L32 -2L34 0L32 2L0 7Z"), "b"); pc.add(star_pts(0, 0, 10, 4.5), "y")
def ruimte_knip(sh):
    sh.text(100, 25, "Kleur de onderdelen, knip ze uit en bouw je eigen ruimteschip.", 6)
    y = flow(sh, [rs_romp, rs_neus, L(rs_vleugel, -1), L(rs_vleugel, 1), rs_alien], 1, 28, 199, 0)
    y = flow(sh, [rs_motor, rs_motor, S(rs_vlam, .85), S(rs_vlam, .85), rs_raam, rs_raam], 2, y + 2, 198, 3)
    y = flow(sh, [S(rs_astronaut, .9), rs_planeet, rs_antenne, S(rs_komeet, .9)], 1, y + 2, 199, 0)
    flow(sh, [rs_ster] * 6, 2, y + 2, 198, 4)
def ruimte_plak(sh):
    head(sh, "Mijn ruimteschip")
    sh.rect_r(10, 26, 180, 222, "n", 6)
    sh.region("M10 190C40 176 70 196 70 248H16Q10 248 10 242Z", "g")
    for x, y, r in [(26, 214, 6), (48, 230, 4), (22, 236, 3.5), (46, 206, 3)]: sh.circle_r(x, y, r, "l")
    sh.region(moon_path(166, 54, 14), "y")
    for x, y in [(40, 46), (110, 40), (150, 92), (40, 120), (176, 150), (96, 150), (130, 220), (176, 228)]:
        sh.region(star_path(x, y, 4.5, 1.8), "-")
    sh.text(100, 264, "Waar vliegt jouw ruimteschip naartoe? ......................", 6.5)
collage("bouw-een-ruimteschip-plakken", "Bouw een ruimteschip: knippen en plakken", "Ruimteschip: knipvel", ruimte_knip, ruimte_plak, "ruimte", "4-6", [
    "Kleur alle onderdelen in. Het grote vak op het plakvel is de ruimte: kleur die donkerblauw, maar laat de sterretjes wit.",
    "Knip de onderdelen uit langs de streepjeslijn.",
    "Leg eerst de romp op het plakvel, met de neus erop en de vleugels aan de zijkanten. Zet de motoren onderaan en de vlammen daaronder.",
    "Plak de raampjes en de antenne erop en plak alles vast.",
    "Laat de astronaut en het marsmannetje rondzweven en plak de planeet, de komeet en de sterren erbij."], minutes=30)

# ---------- bouw een stad ----------
def st_huis(pc, wall="r", roof="w"):
    pc.add(rect(-20, -22, 40, 44), wall)
    pc.add([(-25, -22), (0, -46), (25, -22)], roof)
    pc.add(rect(8, -42, 7, 12), "z")
    pc.add(rect(-6, 2, 12, 20), "w", sil=False); pc.dot(3.5, 12, 1)
    for x in (-16, 6): pc.add(rect(x, -16, 10, 10), "b", sil=False); pc.ln([(x + 5, -16), (x + 5, -6)], style="stroke-width:1")
    pc.add(circ(0, -30, 4), "y", sil=False)
def st_flat(pc):
    pc.add(rect(-22, -60, 44, 82), "z")
    pc.add(rect(-24, -64, 48, 5), "x")
    for r in range(5):
        for c in range(3):
            pc.add(rect(-17 + c * 13, -52 + r * 13, 8, 8), "b", sil=False)
    pc.add(rect(-6, 8, 12, 14), "w", sil=False)
def st_winkel(pc, label="BAKKER", code="y"):
    pc.add(rect(-26, -20, 52, 38), code)
    pc.add(rect(-26, -36, 52, 12), "-")
    pc.text(0, -27.5, label, 6.5)
    pc.add([(-28, -24), (28, -24), (28, -16)] + [(28 - k * 7 - 3.5 + (3.5 if False else 0), -12 if k % 1 == 0 else -16) for k in range(0)] + [(-28, -16)], "r")
    for k in range(8): pc.add(sample(f"M{-28 + k * 7} -16Q{-24.5 + k * 7} -10 {-21 + k * 7} -16Z"), "r" if k % 2 == 0 else "-", sil=k % 2 == 0)
    pc.add(rect(-22, -8, 22, 18), "b", sil=False)
    pc.add(rect(6, -8, 14, 26), "w", sil=False); pc.dot(9, 6, 1)
    pc.add(ellp(-11, 4, 7, 3.5), "w", sil=False)
def st_auto(pc, code="r"):
    pc.add(sample("M-26 6V-4Q-26 -8 -20 -9L-12 -10L-6 -20H10L18 -10L24 -8Q27 -7 27 -2V6Z"), code)
    pc.add(sample("M-4 -17H1V-10H-10Z"), "b", sil=False); pc.add(sample("M4 -17H9L15 -10H4Z"), "b", sil=False)
    pc.add(circ(-14, 6, 6.5), "x"); pc.add(circ(15, 6, 6.5), "x")
    pc.add(circ(-14, 6, 2.6), "-", sil=False); pc.add(circ(15, 6, 2.6), "-", sil=False)
    pc.add(rect(23, -6, 4, 3), "y", sil=False)
def st_bus(pc):
    pc.add(rrect(-36, -24, 72, 30, 4), "y")
    for k in range(5): pc.add(rect(-31 + k * 12, -19, 9, 10), "b", sil=False)
    pc.add(rect(28, -19, 6, 18), "b", sil=False)
    pc.ln([(-36, -4), (36, -4)], style="stroke-width:1")
    for x in (-22, 22): pc.add(circ(x, 6, 6.5), "x"); pc.add(circ(x, 6, 2.6), "-", sil=False)
def st_boom(pc, code="g"):
    pc.add(rect(-4, -6, 8, 30), "w")
    pc.add(union([circ(x, y, r) for x, y, r in [(0, -26, 14), (-11, -14, 11), (11, -14, 11), (0, -12, 11)]]), code)
def st_stoplicht(pc):
    pc.add(rect(-2, 0, 4, 44), "z")
    pc.add(rrect(-8, -34, 16, 36, 3), "x")
    for k, c in enumerate("ryg"): pc.add(circ(0, -26 + k * 11, 4.2), c, sil=False)
def st_lantaarn(pc):
    pc.add(rect(-2, -26, 4, 70), "z"); pc.add(rect(-6, 40, 12, 4), "z")
    pc.add(sample("M-9 -26L-6 -40H6L9 -26Z"), "y"); pc.add(rect(-10, -28, 20, 3), "x"); pc.add(sample("M-6 -40Q0 -48 6 -40Z"), "x")
def st_fiets(pc):
    for x in (-14, 14): pc.add(circ(x, 0, 9), "-"); pc.ln(circ(x, 0, 6), closed=True, style="stroke-width:1")
    pc.ln([(-14, 0), (-5, -14), (9, -14), (14, 0)]); pc.ln([(-5, -14), (0, 0), (9, -14)]); pc.ln([(0, 0), (-14, 0)])
    pc.ln([(-7, -18), (-2, -18)]); pc.ln([(9, -14), (8, -20), (12, -21)])
    pc.sil(rect(-10, -22, 26, 22))
def stad_knip(sh):
    sh.text(100, 25, "Kleur de huizen, auto's en bomen, knip ze uit en bouw een straat.", 6)
    pack(sh, [[st_flat, L(st_huis, "r", "w"), L(st_huis, "o", "x"), st_winkel],
              [L(st_boom, "g"), L(st_boom, "l"), st_lantaarn, st_stoplicht, st_fiets],
              [st_bus, L(st_auto, "r"), L(st_auto, "b")],
              [L(st_winkel, "IJSJES", "m"), L(st_huis, "y", "r"), L(st_boom, "g"), L(st_auto, "g")]])
def stad_plak(sh):
    head(sh, "Mijn straat")
    sh.region(cloud_path(40, 50, 14), "-"); sh.region(cloud_path(150, 40, 11), "-")
    sh.circle_r(100, 48, 10, "y")
    sh.rect_r(0, 176, 200, 14, "z")
    for x in range(0, 200, 20): sh.seg(x, 176, x, 190, "l", "stroke-width:.8")
    sh.rect_r(0, 190, 200, 50, "x")
    for x in range(8, 186, 26):
        if not (128 <= x <= 176): sh.rect_r(x, 213, 14, 3, "-")
    for y in range(193, 240, 8): sh.rect_r(132, y, 40, 5, "-")
    sh.rect_r(0, 240, 200, 14, "z")
    for x in range(0, 200, 20): sh.seg(x, 240, x, 254, "l", "stroke-width:.8")
    sh.text(100, 268, "Mijn straat heet: ..........................................", 7)
collage("bouw-een-stad-plakken", "Bouw een stad: knippen en plakken", "Stad: knipvel", stad_knip, stad_plak, "thuis", "4-6", [
    "Kleur de huizen, de winkel, de bomen, de lantaarnpaal en de voertuigen in.",
    "Kleur op het plakvel de weg donker en laat de strepen en het zebrapad wit.",
    "Knip alles uit langs de streepjeslijn.",
    "Plak de huizen, de winkel en de bomen naast elkaar op de bovenste stoep. Zet het stoplicht bij het zebrapad.",
    "Plak de bus en de auto's op de weg en de fiets op de onderste stoep. Hoe heet jouw straat?"], minutes=30)

# ---------- boerderij ----------
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
def bd_kip(pc):
    pc.add(sample("M-14 -6L-22 -18L-14 -14L-18 -24L-8 -12Z"), "w")
    for x in (-3, 4): pc.add(bar(x, 8, x, 16, 1.2), "o"); pc.add(bar(x, 16, x + 4, 17, 1), "o")
    pc.add(sample("M-14 0C-14 -10 2 -12 6 -6C6 -18 22 -18 22 -8C22 6 10 10 2 10C-8 10 -14 6 -14 0Z"), "-")
    pc.add([(22, -10), (29, -7), (22, -5)], "o")
    pc.add(sample("M10 -18Q12 -24 14 -19Q16 -24 18 -18Z"), "r"); pc.add(ellp(20, -2, 2, 3), "r", sil=False)
    pc.dot(16, -10, 1.4); pc.ln(sample("M-6 -2Q2 4 10 -2", 6), style="stroke-width:1.2")
def bd_eend(pc):
    pc.add(sample("M-20 0C-24 -6 -22 -8 -16 -4C-10 -8 0 -8 4 -6C2 -18 18 -20 20 -8L30 -6L20 -2C22 8 8 12 -4 12C-14 12 -20 8 -20 0Z"), "-")
    pc.add(sample("M20 -8L30 -6L20 -2Z"), "o", sil=False)
    pc.ln(sample("M-10 0Q0 8 8 0", 6)); pc.dot(13, -11, 1.5)
def bd_kuiken(pc):
    for x in (-3, 3): pc.add(bar(x, 8, x, 13, .9), "o")
    pc.add(circ(0, 2, 8), "y"); pc.add(circ(5, -8, 6), "y"); pc.add([(10, -9), (15, -7), (10, -5)], "o")
    pc.dot(7, -9, 1.2); pc.ln(sample("M-5 1Q0 5 4 1", 4), style="stroke-width:1.1")
def bd_hooi(pc):
    pc.add(rrect(-18, -12, 36, 24, 4), "y")
    for x in (-8, 8): pc.add(rect(x - 1.5, -12, 3, 24), "w", sil=False)
    for y in (-5, 2): pc.ln([(-14, y), (-11, y + 2)], style="stroke-width:1"); pc.ln([(12, y), (15, y + 2)], style="stroke-width:1")
def bd_trekker(pc):
    pc.add(rect(14, -26, 3, 12), "x")
    pc.add(rect(-6, -32, 18, 22), "r"); pc.add(rect(-2, -28, 11, 10), "b", sil=False)
    pc.add(rect(-18, -12, 46, 12), "r"); pc.add(rect(12, -16, 18, 6), "r")
    pc.add(circ(-10, 2, 13), "x"); pc.add(circ(-10, 2, 5), "y", sil=False)
    pc.add(circ(22, 6, 8), "x"); pc.add(circ(22, 6, 3), "y", sil=False)
def bd_hek(pc):
    for x in range(0, 50, 12): pc.add(sample(f"M{x - 3} 14V-10L{x} -14L{x + 3} -10V14Z"), "w")
    for y in (-6, 4): pc.add(rect(-3, y, 51, 4), "w")
def bd_appelboom(pc):
    st_boom(pc, "g")
    for x, y in [(-6, -26), (6, -20), (-12, -12), (10, -8), (0, -12)]: pc.add(circ(x, y, 2.8), "r", sil=False)
def boerderij_knip(sh):
    sh.text(100, 25, "Kleur de dieren en de rest, knip ze uit en plak ze op de boerderij.", 6)
    pack(sh, [[bd_koe, bd_varken],
              [bd_schaap, bd_kip, bd_eend],
              [bd_trekker, bd_appelboom, S(bd_kuiken, .9), S(bd_kuiken, .9), S(bd_kuiken, .9)],
              [S(bd_schaap, .75), S(bd_hooi, .9), S(bd_hooi, .9)], [S(bd_hek, .9), S(bd_hek, .9)]])
def boerderij_plak(sh):
    head(sh, "Op de boerderij")
    sh.circle_r(176, 44, 12, "y")
    sh.region(cloud_path(120, 46, 12), "-")
    sh.region("M0 258V122Q60 108 120 120T200 116V258Z", "l")
    sh.rect_r(14, 72, 64, 56, "r"); sh.poly_r([(8, 74), (46, 40), (84, 74)], "w")
    sh.rect_r(34, 92, 24, 36, "w"); sh.line("M34 92L58 128M58 92L34 128")
    sh.circle_r(46, 60, 6, "-")
    sh.region("M118 258C120 236 146 220 200 216V258Z", "b")
    for x, y in [(140, 244), (166, 236), (184, 248)]: sh.line(f"M{x - 6} {y}q3 -3 6 0t6 0", "l", "stroke-width:1.2")
    for x in (20, 70, 96): sh.line(f"M{x} 200l2 -6l2 6M{x + 6} 200l2 -5l2 5", "l", "stroke-width:1.2")
    sh.text(100, 271, "Welke dieren wonen op jouw boerderij?", 6.5)
collage("boerderij-collage-plakken", "Boerderij-collage: knippen en plakken", "Boerderij: knipvel", boerderij_knip, boerderij_plak, "boerderij", "4-6", [
    "Kleur de koe, het varken, het schaap, de kip, de eend en de kuikens in. Vergeet de trekker, het hooi en het hekje niet.",
    "Kleur ook het plakvel: de schuur, het gras en de sloot.",
    "Knip alles uit langs de streepjeslijn.",
    "Plak de dieren in de wei. De eend mag in de sloot zwemmen en de trekker staat bij de schuur.",
    "Weet je welk geluid elk dier maakt? Doe ze maar na!"], minutes=30)

# ---------- bos ----------
def bs_den(pc):
    pc.add(rect(-5, 20, 10, 12), "w")
    for y, w in [(22, 26), (6, 21), (-10, 16)]: pc.add([(-w, y), (0, y - 26), (w, y)], "g")
def bs_loof(pc):
    pc.add(sample("M-6 34L-4 4L-14 -6L-10 -8L-2 0L0 -10L4 -10L4 0L12 -8L14 -6L5 4L6 34Z"), "w")
    pc.add(union([circ(x, y, r) for x, y, r in [(0, -22, 15), (-15, -12, 12), (15, -12, 12), (-8, -2, 11), (8, -2, 11)]]), "l")
def bs_paddo(pc, s=1):
    pc.add(sample("M-6 0Q-8 12 -8 16H8Q8 12 6 0Z"), "-")
    pc.add(sample("M-20 2C-20 -14 -10 -20 0 -20C10 -20 20 -14 20 2Z"), "r")
    for x, y, r in [(-10, -6, 3), (0, -13, 3.2), (10, -6, 3), (2, -3, 2.2)]: pc.add(circ(x * s, y, r), "-", sil=False)
def bs_egel(pc):
    pts = []
    for k in range(15):
        a = 180 + k * 180 / 14; r = 24 if k % 2 == 0 else 17
        pts.append((ept(0, 4, r, r * .85, a)))
    pc.add(pts + [(18, 4)], "w")
    pc.add(sample("M4 6C4 -6 14 -8 20 -2L30 4L20 8C14 10 4 10 4 6Z"), "k")
    pc.add(circ(30, 4, 2.4), "x"); pc.dot(19, 0, 1.5)
    for x in (-10, 8): pc.add(ellp(x, 9, 4, 2.5), "k")
    pc.sil(rect(-22, 2, 30, 8))
def bs_eekhoorn(pc):
    pc.add(sample("M-6 14C-24 18 -30 0 -22 -12C-16 -22 -20 -30 -12 -32C-4 -34 2 -26 -6 -20C-12 -14 -8 -4 -4 2Z"), "o")
    pc.add(ellp(4, 8, 10, 13), "o")
    pc.add(ellp(5, 11, 5, 8), "-", sil=False)
    pc.add(circ(8, -10, 9), "o"); pc.add(ellp(6, -18, 3.2, 6, -10), "o")
    pc.dot(11, -11, 1.5); pc.add(circ(16.5, -8, 1.6), "x", sil=False)
    pc.add(ellp(11, 4, 4, 4.5), "w"); pc.add(ellp(11, 0, 4.5, 2), "w")
    pc.add(ellp(4, 21, 8, 3.5), "o")
def bs_uil(pc):
    pc.add(rect(-24, 22, 48, 5), "w")
    pc.add([(-15, -18), (-14, -30), (-6, -21)], "w"); pc.add([(15, -18), (14, -30), (6, -21)], "w")
    pc.add(ellp(0, 0, 17, 22), "w")
    pc.add(ellp(0, 8, 10, 12), "y", sil=False)
    for s in (-1, 1): pc.add(circ(s * 7, -10, 6.5), "-", sil=False); pc.dot(s * 7, -10, 2.6)
    pc.add([(-2.5, -5), (2.5, -5), (0, 0)], "o", sil=False)
    for s in (-1, 1): pc.add(sample(f"M{s * 14} -4Q{s * 22} 6 {s * 14} 16Z"), "w", sil=False)
    for x in (-5, 5): pc.ln([(x - 2, 22), (x, 19), (x + 2, 22)], style="stroke-width:1.2")
def bs_vos(pc):
    pc.add(sample("M4 22C20 32 38 22 34 4C33 -2 28 -6 24 -4C28 4 28 14 20 16C14 18 8 16 4 12Z"), "o")
    pc.add(sample("M24 -4C28 -6 33 -2 34 4C31 6 29 5 27 3C27 1 26 -2 24 -4Z"), "-", sil=False)
    pc.add(ellp(0, 12, 13, 15), "o"); pc.add(ellp(0, 14, 6.5, 10), "-", sil=False)
    for x in (-6, 6): pc.add(ellp(x, 26, 5, 3), "o")
    pc.add([(-16, -12), (-14, -30), (-5, -20), (5, -20), (14, -30), (16, -12), (0, 2)], "o")
    pc.add([(-13, -26), (-7, -19), (-13, -16)], "x", sil=False); pc.add([(13, -26), (7, -19), (13, -16)], "x", sil=False)
    pc.add([(-16, -12), (-6, -6), (0, 2)], "-", sil=False); pc.add([(16, -12), (6, -6), (0, 2)], "-", sil=False)
    pc.dot(-6, -12, 1.6); pc.dot(6, -12, 1.6); pc.add(circ(0, 0, 2.2), "x", sil=False)
def bs_konijn(pc):
    pc.add(circ(-16, 6, 5), "-")
    pc.add(ellp(-2, 6, 15, 11), "z")
    pc.add(ellp(6, -24, 3.6, 12, 10), "z"); pc.add(ellp(14, -22, 3.6, 12, 25), "z")
    pc.add(circ(12, -6, 9), "z"); pc.add(ellp(7, 16, 7, 3), "z")

    pc.dot(14, -8, 1.5); pc.add(circ(20.5, -4, 1.4), "k", sil=False)
def bs_blad(pc, code="o"):
    pc.add(sample(leaf_path(0, 0, 9, 14)), code); pc.ln([(0, -12), (0, 18)], style="stroke-width:1.2"); pc.sil(rect(-1, 12, 2, 6))
def bs_eikel(pc):
    pc.add(ellp(0, 4, 6, 8), "w"); pc.add(sample("M-8 -1C-8 -8 8 -8 8 -1Z"), "w"); pc.add(rect(-1, -9, 2, 4), "w")
def bos_knip(sh):
    sh.text(100, 25, "Kleur de bomen en de dieren, knip ze uit en maak een bos.", 6)
    pack(sh, [[bs_den, bs_loof, S(bs_den, .78), bs_uil],
              [bs_vos, bs_eekhoorn, bs_konijn, S(bs_egel, .95)],
              [bs_paddo, S(bs_paddo, .8), L(bs_blad, "o"), L(bs_blad, "y"), L(bs_blad, "r"), bs_eikel, bs_eikel],
              [S(bs_den, .8), S(bs_loof, .8), S(bs_egel, .8), S(bs_konijn, .8), S(bs_paddo, .8)]])
def bos_plak(sh):
    head(sh, "In het bos")
    sh.circle_r(30, 48, 11, "y")
    sh.region("M0 160Q50 120 100 150T200 130V258H0Z", "g")
    sh.region("M0 180Q60 160 120 176T200 170V258H0Z", "l")
    sh.region("M72 258C80 230 120 214 110 180Q118 180 124 182C136 216 112 238 128 258Z", "y")
    for x, y in [(20, 214), (170, 206), (40, 244), (176, 248), (150, 228)]: sh.line(f"M{x} {y}l2 -6l2 6M{x + 6} {y}l2 -5l2 5", "l", "stroke-width:1.2")
    sh.text(100, 271, "Wie woont er in jouw bos?", 6.5)
collage("bos-collage-plakken", "Bos-collage: knippen en plakken", "Bos: knipvel", bos_knip, bos_plak, "natuur", "4-6", [
    "Kleur de bomen, de paddenstoelen, de bladeren en de dieren in: de uil, de vos, de eekhoorn, het konijn en de egel.",
    "Kleur op het plakvel de heuvels groen en het paadje geel of bruin.",
    "Knip alles uit langs de streepjeslijn.",
    "Plak eerst de bomen op het plakvel en daarna de dieren. De uil kan op een tak zitten en de egel tussen de bladeren.",
    "Teken er nog meer bij: een vogelnest, bessen of een beekje."], minutes=30)

# =====================================================================
# Sorteerbladen (2, 3 of 4 vakken) met plaatjes van 40x40
# =====================================================================
def wrap(fn, k, dx, dy):
    def g(p):
        p.sc, p.dx, p.dy = p.sc * k, p.dx + dx * p.sc, p.dy + dy * p.sc; fn(p)
    return g
# vliegen
def ic_vogel(p):
    p.add([(9, 20), (2, 14), (3, 26)], "b"); p.add(ellp(18, 22, 11, 8), "b"); p.add(circ(28, 15, 6.5), "b")
    p.add([(33.5, 13), (39, 16), (33.5, 18)], "o"); p.add(sample("M11 20Q18 10 25 21Q18 26 11 20Z"), "n"); p.dot(29.5, 14, 1.3)
    p.ln([(16, 30), (15, 36)], style="stroke-width:1.4"); p.ln([(21, 30), (22, 36)], style="stroke-width:1.4")
def ic_vlinder(p):
    for x, y, rx, ry, c in [(11, 14, 9, 8, "p"), (29, 14, 9, 8, "p"), (12, 28, 7, 6, "m"), (28, 28, 7, 6, "m")]: p.add(ellp(x, y, rx, ry), c)
    p.add(ellp(20, 21, 2.8, 12), "x"); p.ln(sample("M19 10Q16 4 13 3", 4), style="stroke-width:1.3"); p.ln(sample("M21 10Q24 4 27 3", 4), style="stroke-width:1.3")
def ic_bij(p):
    p.add(ellp(16, 12, 6, 8, -20), "-"); p.add(ellp(25, 12, 6, 8, 20), "-")
    p.add(ellp(22, 24, 12, 8), "y")
    for x in (19, 26): p.ln(sample(f"M{x} 16.5Q{x + 2} 24 {x} 31.5", 4), style="stroke-width:2.6")
    p.add([(34, 22), (39, 24), (34, 26)], "x"); p.add(circ(9, 23, 5.5), "x"); p.add(circ(8, 22, 1.3), "-")
def ic_vleermuis(p):
    p.add(sample("M20 14L2 10Q6 16 4 22Q9 19 12 24Q15 20 18 26Z"), "z"); p.add(sample("M20 14L38 10Q34 16 36 22Q31 19 28 24Q25 20 22 26Z"), "z")
    p.add(ellp(20, 20, 5.5, 9), "x"); p.add([(16, 12), (16.5, 6), (19, 11)], "x"); p.add([(24, 12), (23.5, 6), (21, 11)], "x")
    p.add(circ(18, 15, 1.3), "-"); p.add(circ(22, 15, 1.3), "-")
# zwemmen
def ic_vis(p): p.add(sample(fish_path(17, 20, 13)), "o"); p.dot(9, 18, 1.6); p.ln(sample("M13 13Q16 20 13 27", 4), style="stroke-width:1.3")
def ic_kwal(p):
    for x in (12, 17, 23, 28): p.ln(sample(f"M{x} 20Q{x - 3} 26 {x} 30Q{x + 3} 34 {x} 38", 6), style="stroke-width:1.6")
    p.add(sample("M6 21C6 6 34 6 34 21Q27 18 20 21Q13 18 6 21Z"), "m"); p.dot(16, 15, 1.3); p.dot(24, 15, 1.3)
def ic_walvis(p):
    p.add(sample("M32 20L37 11Q39 16 38 18Q40 20 38 25Z"), "n")
    p.add(sample("M3 22C3 11 20 9 30 16C34 19 34 23 32 26C26 33 8 33 3 22Z"), "n")
    p.add(sample("M5 25C10 31 24 31 30 26C24 28 10 28 5 25Z"), "b", sil=False); p.dot(10, 19, 1.4)
    for d in ("M12 9Q10 4 7 3", "M13 9V2", "M14 9Q16 4 19 3"): p.ln(sample(d, 4), style="stroke-width:1.3")
def ic_octopus(p):
    for k, x in enumerate((7, 13, 20, 27, 33)):
        c = sample(f"M{20 + (x - 20) * .4} 20Q{x} 28 {x + (3 if k % 2 else -3)} 34", 6); p.add(taper(c, 2.6, 1.2), "p")
    p.add(ellp(20, 14, 11, 11), "p"); p.dot(16, 15, 1.6); p.dot(24, 15, 1.6); p.ln(sample("M17 20Q20 22 23 20", 4), style="stroke-width:1.2")
# lopen
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
# groot / klein
def ic_beer(p):
    for x in (9, 31): p.add(circ(x, 9, 5.5), "w")
    p.add(circ(20, 21, 14), "w"); p.add(ellp(20, 27, 6.5, 5), "-"); p.add(ellp(20, 24.5, 2.6, 2), "x")
    p.dot(14, 18, 1.6); p.dot(26, 18, 1.6)
def ic_dino(p):
    p.add(sample("M4 30C6 22 12 18 20 18C24 18 27 14 28 8C28 4 30 2 33 2C37 2 38 6 35 7C33 8 32 10 32 14C31 22 30 28 26 30L26 37H22L21 31H14L13 37H9L9 31Q6 33 1 33Q2 31 4 30Z"), "g")
    p.dot(34, 4.5, 1.2)
def ic_mier(p):
    for x0 in (14, 21):
        for s in (-1, 1): p.ln([(x0, 22), (x0 - 3 * s, 30)], style="stroke-width:1.2"); p.ln([(x0, 22), (x0 + 4 * s, 15)], style="stroke-width:1.2") if False else None
    for x0, x1 in [(13, 9), (18, 18), (23, 27)]: p.ln([(x0, 22), (x1, 31)], style="stroke-width:1.2")
    p.add(ellp(29, 21, 7, 5.5), "x"); p.add(circ(19, 21, 3.5), "x"); p.add(circ(11, 18, 4.5), "x")
    p.ln(sample("M9 15Q6 9 3 9", 4), style="stroke-width:1.2"); p.ln(sample("M11 14Q11 8 8 6", 4), style="stroke-width:1.2")
def ic_lhb(p):
    p.add(circ(20, 10, 5.5), "x"); p.add(circ(20, 23, 13), "r"); p.ln([(20, 10), (20, 36)], style="stroke-width:1.4")
    for x, y in [(13, 18), (27, 18), (12, 27), (28, 27), (20, 15) if False else (16, 32), (24, 32)]: p.add(circ(x, y, 2.4), "x", sil=False)
def ic_slak(p):
    p.add(sample("M3 32C3 28 6 27 9 28L32 28C36 28 37 32 35 33L5 34Z"), "y")
    p.add(bar(7, 28, 5, 20, .9), "y"); p.add(circ(5, 19, 1.8), "y"); p.add(bar(9, 28, 10, 20, .9), "y"); p.add(circ(10, 19, 1.8), "y")
    p.add(circ(23, 19, 10), "w"); p.ln(sample("M23 19C26 19 26 15 22 15C18 15 17 21 22 23C28 25 32 18 29 13", 10), style="stroke-width:1.4")
def ic_nijlpaard(p):
    for x in (9, 16, 24): p.add(rect(x - 3, 26, 6, 8), "z")
    p.add(ellp(17, 21, 14, 10), "z"); p.add(rrect(24, 12, 15, 16, 6), "z")
    for x in (26, 33): p.add(circ(x, 12, 2.6), "z")
    p.dot(29, 17, 1.3); p.dot(36, 22, 1); p.ln(sample("M30 25Q34 27 38 24", 4), style="stroke-width:1.2")
ic_kuiken = wrap(bd_kuiken, 1.4, 19, 22)
# rond / hoekig
def ic_bal(p):
    p.add(circ(20, 20, 15), "-")
    for i, c in enumerate("ryb"):
        a1, a2 = -90 + i * 120, -30 + i * 120; p.region = None
        p.add([(20, 20)] + ellp(20, 20, 15, 15, a0=a1, a1=a2, n=48), c, sil=False)
    p.add(circ(20, 20, 4), "-", sil=False)
def ic_klok(p):
    p.add(circ(20, 21, 15), "b"); p.add(circ(20, 21, 11.5), "-", sil=False)
    for k in range(12):
        t = math.radians(k * 30); p.ln([(20 + 9 * math.cos(t), 21 + 9 * math.sin(t)), (20 + 10.5 * math.cos(t), 21 + 10.5 * math.sin(t))], style="stroke-width:1")
    p.ln([(20, 21), (20, 14)], style="stroke-width:1.6"); p.ln([(20, 21), (25, 23)], style="stroke-width:1.6")
def ic_donut(p):
    p.add(circ(20, 20, 15), "w"); p.add(sample("M7 18C7 8 33 8 33 18C33 26 30 22 27 26C24 30 22 25 18 28C14 31 13 24 10 26C6 28 7 22 7 18Z"), "m", sil=False)
    p.add(circ(20, 19, 5), "-", sil=False)
    for x, y, a in [(12, 13, 30), (27, 13, -30), (12, 21, -20), (28, 21, 40), (20, 10, 90)]:
        t = math.radians(a); p.ln([(x - 1.5 * math.cos(t), y - 1.5 * math.sin(t)), (x + 1.5 * math.cos(t), y + 1.5 * math.sin(t))], style="stroke-width:1.4")
def ic_pizza(p):
    p.add(circ(20, 20, 16), "w"); p.add(circ(20, 20, 13), "y", sil=False)
    for a in (0, 60, 120): t = math.radians(a); p.ln([(20 - 13 * math.cos(t), 20 - 13 * math.sin(t)), (20 + 13 * math.cos(t), 20 + 13 * math.sin(t))], style="stroke-width:1.2")
    for x, y in [(14, 13), (26, 13), (13, 25), (27, 26), (20, 21) if False else (20, 30)]: p.add(circ(x, y, 2.6), "r", sil=False)
def ic_knoop(p):
    p.add(circ(20, 20, 14), "b"); p.add(circ(20, 20, 10), "b", sil=False)
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3)]: p.add(circ(20 + dx, 20 + dy, 1.6), "-", sil=False)
def ic_sinaas(p):
    p.add(circ(20, 22, 14), "o"); p.add(ellp(25, 7, 5, 2.4, -25), "g"); p.ln([(20, 8), (21, 10)], style="stroke-width:1.2")
    for x, y in [(14, 17), (25, 20), (17, 27), (27, 28)]: p.dot(x, y, .8)
def ic_boek(p):
    p.add(rect(8, 6, 24, 30), "r"); p.add(rect(8, 6, 4, 30), "r", sil=False)
    p.add(rect(16, 12, 12, 7), "-", sil=False)
def ic_cadeau(p):
    p.add(rect(6, 15, 28, 21), "p"); p.add(rect(4, 10, 32, 6), "p")
    p.add(rect(18, 10, 4, 26), "y", sil=False)
    p.add(sample("M20 10C14 2 8 6 12 10Z"), "y"); p.add(sample("M20 10C26 2 32 6 28 10Z"), "y")
def ic_dobbel(p):
    p.add(rrect(7, 7, 26, 26, 3), "-")
    for x, y in [(13, 13), (20, 20), (27, 27), (27, 13), (13, 27)]: p.dot(x, y, 2.2)
def ic_envelop(p):
    p.add(rect(4, 10, 32, 22), "-"); p.ln([(4, 10), (20, 23), (36, 10)], style="stroke-width:1.6"); p.add(rect(28, 13, 5, 6), "r", sil=False)
def ic_raam(p):
    p.add(rect(7, 5, 26, 30), "w"); p.add(rect(10, 8, 20, 24), "b", sil=False)
    p.ln([(20, 8), (20, 32)], style="stroke-width:1.8"); p.ln([(10, 20), (30, 20)], style="stroke-width:1.8")
def ic_tv(p):
    p.add(rect(4, 6, 32, 24), "z"); p.add(rect(8, 10, 24, 16), "b", sil=False)
    p.add(rect(15, 30, 10, 3), "z"); p.add(rect(10, 33, 20, 3), "z")
# seizoenen
def ic_tulp(p):
    p.add(bar(20, 18, 20, 38, 1.2), "g"); p.add(ellp(13, 30, 7, 2.8, -40), "g"); p.add(ellp(27, 30, 7, 2.8, 40), "g")
    p.add(sample("M11 4L16 10L20 3L24 10L29 4C31 16 26 21 20 21C14 21 9 16 11 4Z"), "r")
def ic_nest(p):
    for x in (13, 20, 27): p.add(ellp(x, 18, 4.5, 6), "b")
    p.add(sample("M3 20H37C36 30 28 34 20 34C12 34 4 30 3 20Z"), "w")
    for y in (25, 29): p.ln(sample(f"M7 {y}Q20 {y + 3} 33 {y}", 6), style="stroke-width:1")
def ic_ijsje(p):
    p.add([(12, 18), (28, 18), (20, 38)], "w"); p.ln([(14, 22), (24, 32)], style="stroke-width:1"); p.ln([(26, 22), (17, 30)], style="stroke-width:1")
    p.add(circ(20, 13, 8.5), "k"); p.add(circ(20, 4.5, 3), "r")
def ic_emmer(p):
    p.add(sample("M10 14Q20 2 30 14", 6) + sample("M30 14Q20 5 10 14", 6), "-") if False else p.ln(sample("M10 15Q20 1 30 15", 8), style="stroke-width:1.6")
    p.add([(8, 15), (32, 15), (29, 36), (11, 36)], "r"); p.ln([(8.5, 19), (31.5, 19)], style="stroke-width:1.2")
    p.add(bar(30, 34, 37, 6, 1.2), "y"); p.add(sample("M34 6C33 1 41 1 40 6L38 12L35 11Z"), "y")
def ic_zonnebril(p):
    p.add(bar(4, 14, 9, 18, 1), "x"); p.add(bar(36, 14, 31, 18, 1), "x")
    p.add(sample("M17 18Q20 15 23 18", 4) + [(23, 20), (17, 20)], "x")
    p.add(sample("M5 17H18C18 26 15 29 11 29C7 29 5 25 5 17Z"), "x"); p.add(sample("M22 17H35C35 25 33 29 29 29C25 29 22 26 22 17Z"), "x")
def ic_herfstblad(p):
    p.add(sample(leaf_path(20, 18, 12, 16)), "o"); p.ln([(20, 4), (20, 38)], style="stroke-width:1.4")
    for y in (12, 18, 24): p.ln([(20, y + 4), (13, y)], style="stroke-width:1"); p.ln([(20, y + 4), (27, y)], style="stroke-width:1")
def ic_paddo(p):
    p.add(sample("M15 22Q14 32 13 36H27Q26 32 25 22Z"), "-")
    p.add(sample("M3 23C3 10 12 4 20 4C28 4 37 10 37 23Z"), "r")
    for x, y, r in [(11, 15, 2.8), (20, 9, 3), (29, 15, 2.8), (21, 18, 2.2)]: p.add(circ(x, y, r), "-", sil=False)
def ic_eikel(p):
    p.add(ellp(20, 25, 9, 12), "w"); p.add(sample("M9 19C8 8 32 8 31 19Z"), "w"); p.add(rect(19, 5, 3, 6), "w")
    for x in (14, 20, 26): p.ln([(x, 12), (x - 2, 18)], style="stroke-width:1")
def ic_sneeuwpop(p):
    p.add(circ(20, 28, 10), "-"); p.add(circ(20, 13, 7.5), "-"); p.add(rect(13, 1, 14, 7), "x"); p.add(rect(10, 7, 20, 3), "x")
    p.add([(20, 13.5), (25, 15), (20, 16)], "o"); p.dot(17.5, 11, 1.2); p.dot(22.5, 11, 1.2)
    p.add(rect(12, 19, 16, 3.5), "r", sil=False)
def ic_want(p):
    p.add(sample("M12 28C10 20 9 12 14 7C19 3 26 6 27 12L28 16C30 12 35 13 34 18C33 22 30 25 28 28Z"), "r")
    p.add(rect(10, 28, 20, 9), "-"); p.ln([(14, 28), (14, 37)], style="stroke-width:1"); p.ln([(20, 28), (20, 37)], style="stroke-width:1"); p.ln([(26, 28), (26, 37)], style="stroke-width:1")
def ic_vlok(p):
    for a in (0, 60, 120):
        t = math.radians(a + 90); p.ln([(20 - 16 * math.cos(t), 20 - 16 * math.sin(t)), (20 + 16 * math.cos(t), 20 + 16 * math.sin(t))], style="stroke-width:2")
        for sgn in (-1, 1):
            bx, by = 20 + sgn * 10 * math.cos(t), 20 + sgn * 10 * math.sin(t)
            for d in (-1, 1): u = t + d * .7 + (0 if sgn > 0 else math.pi); p.ln([(bx, by), (bx + 5 * math.cos(u), by + 5 * math.sin(u))], style="stroke-width:1.6")

def sorteer(slug, name, heading, cats, cat, age, steps, seed, diff=1):
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
    sh.text(100, 26, "Knip de kaartjes los en leg ze in het goede vak.", 6.5)
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

sorteer("sorteren-vliegt-zwemt-loopt", "Sorteren: vliegt, zwemt of loopt het?", "Vliegt, zwemt of loopt?", [
    ("Vliegt", [ic_vogel, ic_vlinder, ic_bij, ic_vleermuis], ic_vogel),
    ("Zwemt", [ic_vis, ic_kwal, ic_walvis, ic_octopus], ic_vis),
    ("Loopt", [ic_hond, ic_olifant, ic_muis, ic_giraf], ic_hond)], "dieren", "4-6", [
    "Kleur de dieren in en knip de kaartjes los langs de streepjeslijnen.",
    "Hoe komt elk dier vooruit? Vliegt het door de lucht, zwemt het in het water of loopt het op pootjes? Leg het kaartje in het goede vak."], 4)
sorteer("sorteren-groot-of-klein", "Sorteren: groot of klein dier?", "Groot of klein?", [
    ("Groot", [ic_olifant, ic_giraf, ic_walvis, ic_beer, ic_nijlpaard, ic_dino], None),
    ("Klein", [ic_muis, ic_mier, ic_lhb, ic_slak, ic_bij, ic_kuiken], None)], "dieren", "2-4", [
    "Kleur de dieren in en knip de kaartjes los langs de streepjeslijnen.",
    "Op de kaartjes zijn alle dieren even groot, maar in het echt niet! Is het dier in het echt groter of kleiner dan jij? Leg het in het goede vak."], 6)
sorteer("sorteren-rond-of-hoekig", "Sorteren: rond of hoekig?", "Rond of hoekig?", [
    ("Rond", [ic_bal, ic_klok, ic_donut, ic_pizza, ic_knoop, ic_sinaas], None),
    ("Hoekig", [ic_boek, ic_cadeau, ic_dobbel, ic_envelop, ic_raam, ic_tv], None)], "vormen", "2-4", [
    "Kleur de plaatjes in en knip de kaartjes los langs de streepjeslijnen.",
    "Voel met je vinger langs de rand van elk plaatje. Is het rond, of heeft het hoeken? Leg het in het goede vak."], 8)
sorteer("sorteren-vier-seizoenen", "Sorteren: lente, zomer, herfst of winter?", "Welk seizoen?", [
    ("Lente", [ic_tulp, ic_kuiken, ic_nest], None),
    ("Zomer", [ic_ijsje, ic_emmer, ic_zonnebril], None),
    ("Herfst", [ic_herfstblad, ic_paddo, ic_eikel], None),
    ("Winter", [ic_sneeuwpop, ic_want, ic_vlok], None)], "natuur", "4-6", [
    "Kleur de plaatjes in en knip de kaartjes los langs de streepjeslijnen.",
    "Bij welk seizoen past elk plaatje het best? Leg het in het goede vak: lente, zomer, herfst of winter.",
    "Praat erover: wat doe jij graag in elk seizoen?"], 2, diff=2)

# ---------- beroepen en hun gereedschap koppelen ----------
def bust(p, coat="b", hat=None):
    p.add(sample("M-17 30C-17 18 -9 13 0 13C9 13 17 18 17 30Z"), coat)
    p.add(circ(0, 0, 11), "-"); p.dot(-4, -1, 1.4); p.dot(4, -1, 1.4); p.ln(sample("M-4 4Q0 7 4 4", 4), style="stroke-width:1.2")
    if hat: hat(p)
def hat_kok(p):
    p.add(sample("M-10 -8C-18 -10 -16 -24 -8 -22C-6 -30 6 -30 8 -22C16 -24 18 -10 10 -8Z"), "-"); p.add(rect(-10, -11, 20, 5), "-")
def hat_brand(p):
    p.add(sample("M-12 -6C-12 -16 -6 -20 0 -20C6 -20 12 -16 12 -6Z"), "r"); p.add(sample("M-16 -6H16L14 -3H-14Z"), "r")
    p.add(sample("M-3 -19H3L2 -10H-2Z"), "y")
def hat_dokter(p):
    p.add(sample("M-11 -2C-12 -12 -6 -12 0 -12C6 -12 12 -12 11 -2C9 -8 -9 -8 -11 -2Z"), "w")
    p.add(circ(0, -10, 4.5), "z"); p.add(circ(0, -10, 2), "-", sil=False)
    p.ln(sample("M-7 14Q-8 24 0 25Q8 24 7 14", 8), style="stroke-width:1.2"); p.add(circ(0, 26, 2), "z")
def hat_schilder(p):
    p.add(sample("M-11 -4C-11 -14 -5 -16 0 -16C5 -16 11 -14 11 -4Z"), "-"); p.add(sample("M4 -5H20Q20 -2 16 -2H4Z"), "-")
    p.add(circ(-4, -10, 1.8), "r", sil=False); p.add(circ(3, -12, 1.6), "b", sil=False)
def hat_bouw(p):
    p.add(sample("M-11 -5C-11 -16 -5 -19 0 -19C5 -19 11 -16 11 -5Z"), "y"); p.add(rrect(-15, -6, 30, 4, 2), "y"); p.add(rect(-2, -18, 4, 12), "o", sil=False)
def hat_tuin(p):
    p.add(ellp(0, -7, 19, 4), "y"); p.add(sample("M-9 -8C-9 -17 9 -17 9 -8Z"), "y"); p.add(rect(-9, -11, 18, 3), "r", sil=False)
def ic_pan(p):
    p.add(bar(26, 22, 39, 16, 2), "x"); p.add(ellp(15, 22, 13, 6), "z"); p.add(sample("M2 22C2 30 28 30 28 22C26 26 4 26 2 22Z"), "z")
    for x in (11, 15, 19): p.ln(sample(f"M{x} 15Q{x - 2} 10 {x} 6", 4), style="stroke-width:1.1")
def ic_blusser(p):
    p.add(rrect(12, 10, 14, 27, 5), "r"); p.add(rect(16, 5, 6, 6), "x"); p.add(bar(22, 7, 30, 5, 1.6), "x")
    p.ln(sample("M16 8Q8 10 9 22", 6), style="stroke-width:1.6"); p.add(rect(14, 18, 10, 8), "-", sil=False)
def ic_tas(p):
    p.ln(sample("M14 14V8Q14 5 17 5H23Q26 5 26 8V14", 6), style="stroke-width:1.8")
    p.add(rrect(4, 13, 32, 22, 4), "w"); p.add(sample("M17 17H23V21H27V27H23V31H17V27H13V21H17Z"), "r", sil=False)
def ic_roller(p):
    p.add(rrect(6, 4, 28, 10, 3), "y"); p.ln([(34, 9), (37, 9), (37, 19), (20, 19), (20, 24)], style="stroke-width:1.8"); p.add(rrect(17, 24, 6, 14, 2), "r")
def ic_hamer(p):
    p.add(bar(10, 36, 24, 12, 2.6), "w"); p.add(sample("M14 6L32 16L30 20L26 18L24 22L12 15L14 11L10 9Z"), "z")
def ic_gieter(p):
    p.add(bar(28, 22, 38, 10, 1.6), "g"); p.add(ellp(38, 9, 2.5, 4, 45), "g")
    p.add(sample("M7 12Q12 4 20 4Q28 4 30 12", 8) + [(30, 13), (28, 13)] + sample("M28 13Q26 7 20 7Q13 7 9 13", 8), "g")
    p.add(rect(6, 12, 24, 24), "g")
def beroepen_koppelen():
    beroepen = [("kok", "-", hat_kok, ic_pan), ("brandweer", "n", hat_brand, ic_blusser), ("dokter", "-", hat_dokter, ic_tas),
                ("schilder", "-", hat_schilder, ic_roller), ("bouwvakker", "o", hat_bouw, ic_hamer), ("tuinman", "g", hat_tuin, ic_gieter)]
    def page(answer):
        sh = Sheet(); head(sh, "Antwoorden" if answer else "Wie heeft wat nodig?")
        if not answer: sh.text(100, 26, "Knip de kaartjes onderaan los en plak ze bij het goede beroep.", 6)
        for i, (naam, coat, hat, tool) in enumerate(beroepen):
            col, row = i % 2, i // 2
            x0, y0 = 8 + col * 94, 34 + row * 58
            sh.rect_line(x0, y0, 90, 54, "l", 4, "stroke-width:1")
            icon_at(sh, lambda p, c=coat, h=hat: bust(p, c, h), x0 + 23, y0 + 23, .7)
            sh.text(x0 + 23, y0 + 51, naam, 6)
            sh.rect_line(x0 + 46, y0 + 8, 38, 38, "l", 2, "stroke-width:.8;stroke-dasharray:2 2")
            if answer: icon_at(sh, tool, x0 + 49, y0 + 11, .8)
            else: sh.text(x0 + 65, y0 + 29, "plak hier", 5, cls="tip")
        if not answer:
            order = [3, 0, 5, 1, 4, 2]; C = 32; gx = 100 - 3 * C; gy = 220
            for k, j in enumerate(order): icon_at(sh, beroepen[j][3], gx + k * C + 2.5, gy + 2.5, .68)
            sh.seg(gx, gy, gx + 6 * C, gy, "cut"); sh.seg(gx, gy + C, gx + 6 * C, gy + C, "cut")
            for k in range(7): sh.seg(gx + k * C, gy, gx + k * C, gy + C, "cut")
            sh.text(100, 214, "Kleur de kaartjes en knip ze los:", 6)
            sh.legend(["cut"], 277)
        return sh
    write(OUT, "beroepen-en-gereedschap-koppelen", page(False), {"category": "beroepen", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 20,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": "Beroepen en hun gereedschap: knippen en plakken", "steps": [
            "Kijk naar de zes mensen. Wat voor werk doen ze? Lees samen de namen: kok, brandweer, dokter, schilder, bouwvakker en tuinman.",
            "Kleur de kaartjes onderaan in en knip ze los langs de streepjeslijnen.",
            "Wie heeft welk gereedschap nodig? Leg elk kaartje in het vak naast het goede beroep.",
            "Kijk na met het antwoordblad en plak de kaartjes vast. Kleur de mensen ook in."]}}},
        [("antwoorden", "Antwoorden", page(True))])
beroepen_koppelen()

# =====================================================================
# Op volgorde: vier plaatjes knippen en in de goede volgorde plakken
# =====================================================================
CW, CH = 62, 50
def frame_at(sh, fn, x, y):
    sh.raw(f'<g transform="translate({f(float(x))} {f(float(y))})">'); fn(Pc(sh)); sh.raw("</g>")
def volgorde(slug, name, heading, scenes, shuffled, cat, age, steps, diff=1):
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

def soil(p, sky=True):
    p.add(rect(0, 38, CW, 12), "w")
    for x, y in [(8, 44), (22, 46), (40, 43), (54, 46)]: p.dot(x, y, .8)
def zb1(p):
    soil(p); p.add(ellp(31, 43, 4, 2.6, -20), "y")
    for x, y in [(22, 22), (31, 27), (40, 22)]: p.add(sample(f"M{x} {y - 4}Q{x + 2.5} {y} {x} {y + 1.5}Q{x - 2.5} {y} {x} {y - 4}Z"), "b")
    p.add(union([circ(25, 8, 5), circ(31, 5, 6), circ(37, 8, 5), rect(22, 8, 18, 5)]), "-")
def zb2(p):
    soil(p); p.add(ellp(31, 43, 4, 2.6, -20), "y"); p.ln([(31, 41), (31, 30)], style="stroke-width:1.6")
    p.add(ellp(26, 29, 5, 2.5, 20), "g"); p.add(ellp(36, 29, 5, 2.5, -20), "g")
    p.add(circ(52, 10, 5), "y")
def zb3(p):
    soil(p); p.ln([(31, 38), (31, 14)], style="stroke-width:1.6")
    for y, s in [(32, -1), (26, 1), (20, -1)]: p.add(ellp(31 + s * 6, y, 6, 2.8, -25 * s), "g")
    p.add(sample("M27 14C26 8 29 4 31 2C33 4 36 8 35 14Z"), "g"); p.add(circ(52, 10, 5), "y")
def zb4(p):
    soil(p); p.ln([(31, 38), (31, 20)], style="stroke-width:1.6")
    for y, s in [(32, -1), (27, 1)]: p.add(ellp(31 + s * 6, y, 6, 2.8, -25 * s), "g")
    for k in range(8):
        a = math.radians(k * 45); p.add(ellp(31 + 7 * math.cos(a), 14 + 7 * math.sin(a), 4.5, 2.6, k * 45), "r")
    p.add(circ(31, 14, 4), "y"); p.add(circ(52, 9, 5), "y")
    for a in range(0, 360, 60): t = math.radians(a); p.ln([(52 + 7 * math.cos(t), 9 + 7 * math.sin(t)), (52 + 9 * math.cos(t), 9 + 9 * math.sin(t))], style="stroke-width:1")
def leafbig(p): p.add(sample("M4 40C10 22 34 14 58 22C46 38 22 46 4 40Z"), "g"); p.ln(sample("M4 40Q30 30 58 22", 6), style="stroke-width:1")
def rv1(p):
    leafbig(p)
    for x, y in [(24, 30), (28, 28), (32, 29), (27, 32), (31, 32)]: p.add(circ(x, y, 1.8), "-", sil=False)
    p.add(circ(10, 10, 5), "y")
def rv2(p):
    p.add(sample("M4 40C10 22 34 14 58 22C56 26 52 26 52 30C48 30 46 34 44 36C30 42 18 44 4 40Z"), "g")
    for k in range(6): p.add(circ(14 + k * 5.5, 29 - math.sin(k * 1.1) * 2, 3.4 if k < 5 else 4.2), "l")
    p.dot(42.5, 27, .9)
    p.ln([(43, 24), (45, 20)], style="stroke-width:1"); p.ln([(41, 24), (40, 20)], style="stroke-width:1")
def rv3(p):
    p.add(rect(2, 6, 58, 4), "w"); p.add(ellp(36, 12, 8, 3.5, 20), "g")
    p.ln([(24, 10), (24, 14)], style="stroke-width:1.2")
    p.add(sample("M24 14C30 16 30 30 27 38C25 42 23 42 21 38C18 30 18 16 24 14Z"), "w")
    for y in (20, 26, 32): p.ln(sample(f"M19.5 {y}Q24 {y + 2} 28.5 {y}", 4), style="stroke-width:.9")
def rv4(p):
    for x, y, rx, ry, c in [(21, 18, 11, 9, "o"), (41, 18, 11, 9, "o"), (23, 33, 8, 7, "y"), (39, 33, 8, 7, "y")]: p.add(ellp(x, y, rx, ry, (-20 if x < 31 else 20)), c)
    for x, y in [(19, 17), (43, 17)]: p.add(circ(x, y, 3), "-", sil=False)
    p.add(ellp(31, 25, 2.6, 13), "x"); p.ln(sample("M30 13Q27 6 23 5", 4), style="stroke-width:1"); p.ln(sample("M32 13Q35 6 39 5", 4), style="stroke-width:1")
def nest(p):
    p.add(sample("M10 34H52C51 44 42 48 31 48C20 48 11 44 10 34Z"), "w")
    for y in (39, 43): p.ln(sample(f"M14 {y}Q31 {y + 3} 48 {y}", 6), style="stroke-width:.9")
def ek1(p): p.add(ellp(31, 26, 9, 12), "-"); nest(p)
def ek2(p):
    p.add(ellp(31, 26, 9, 12), "-"); p.ln([(24, 24), (28, 21), (31, 25), (34, 20), (38, 23)], style="stroke-width:1.2")
    nest(p)
    for x, y, d in [(19, 16, "M17 14l-3 -3M19 12v-4"), (44, 14, "M45 12l3 -3M47 15h4")]: p.ln(PL(sample(d.split("M")[1] and "M" + d.split("M")[1], 2)) and [] or [], style="stroke-width:1") if False else None
    for d in ("M18 18L13 14", "M19 14L18 8", "M44 16L49 12", "M45 20L51 20"): p.ln(sample(d, 2), style="stroke-width:1.2")
def ek3(p):
    p.add(sample("M22 30L22 40H40V30L37 33L34 30L31 33L28 30L25 33Z"), "-")
    p.add(circ(31, 22, 8), "y"); p.add([(38, 21), (43, 23), (38, 25)], "o"); p.dot(34, 20, 1.2)
    p.add(sample("M46 40L44 34L47 31L50 34L53 31L54 40Z"), "-")
    nest(p)
def ek4(p):
    p.add(rect(0, 42, CW, 8), "l")
    w = wrap(bd_kip, 1.05, 30, 25); w(p)
def tb1(p):
    p.add(rect(0, 40, CW, 10), "w")
    p.add(sample("M6 40V18L10 12H22L26 18V40Z"), "-"); p.text(16, 31, "MEEL", 4.6)
    p.add(rect(30, 18, 12, 22), "b"); p.add([(30, 18), (36, 11), (42, 18)], "b"); p.text(36, 31, "MELK", 4.6, rotate=-90)
    p.add(ellp(52, 34, 5, 6.5), "-"); p.add(ellp(52, 25, 4.5, 3), "y") if False else None
def tb2(p):
    p.add(rect(0, 40, CW, 10), "w")
    p.add(bar(40, 30, 50, 6, 1.4), "z"); p.add(ellp(51, 4, 3, 5, 25), "z")
    p.add(sample("M10 26H52C50 38 42 42 31 42C20 42 12 38 10 26Z"), "r"); p.add(ellp(31, 26, 21, 4), "y")
def tb3(p):
    p.add(rect(8, 4, 46, 42), "z"); p.add(rect(12, 14, 38, 26), "x", sil=False); p.add(rect(16, 18, 30, 18), "o", sil=False)
    p.add(sample("M20 32V28Q31 22 42 28V32Z"), "y"); for_k = [p.add(circ(16 + k * 10, 9, 2.2), "-") for k in range(4)]
def tb4(p):
    p.add(rect(4, 42, 54, 4), "z")
    p.add(rrect(12, 24, 38, 18, 3), "m"); p.add(sample("M12 24H50V28Q46 32 43 28Q40 32 37 28Q34 32 31 28Q28 32 25 28Q22 32 19 28Q16 32 12 28Z"), "-", sil=False)
    for x in (20, 31, 42):
        p.add(rect(x - 1.8, 12, 3.6, 12), "b"); p.add(sample(f"M{x} 4C{x + 3} 8 {x + 2.5} 11 {x} 11C{x - 2.5} 11 {x - 3} 8 {x} 4Z"), "y")
volgorde("volgorde-zaadje-wordt-bloem", "Op volgorde: van zaadje tot bloem", "Van zaadje tot bloem", [zb1, zb2, zb3, zb4], [2, 0, 3, 1], "natuur", "4-6", [
    "Waar zie je het zaadje? En waar is de bloem al open?", "Eerst het zaadje in de grond, dan komt er een sprietje uit, dan groeit de plant en tot slot gaat de bloem open."])
volgorde("volgorde-rups-wordt-vlinder", "Op volgorde: van rups tot vlinder", "Van rups tot vlinder", [rv1, rv2, rv3, rv4], [3, 1, 0, 2], "dieren", "4-6", [
    "Zoek de eitjes op het blad, de rups, de cocon en de vlinder.", "Uit het eitje komt een rups. De rups eet en eet, maakt een cocon om zich heen en daar komt een vlinder uit."])
volgorde("volgorde-ei-wordt-kip", "Op volgorde: van ei tot kip", "Van ei tot kip", [ek1, ek2, ek3, ek4], [1, 3, 2, 0], "boerderij", "4-6", [
    "Zie je het ei in het nest, het ei met barstjes, het kuiken en de kip?", "Eerst ligt het ei in het nest, dan krijgt het barstjes, dan kruipt het kuiken eruit en het kuiken groeit uit tot een kip."])
volgorde("volgorde-taart-bakken", "Op volgorde: een taart bakken", "Een taart bakken", [tb1, tb2, tb3, tb4], [2, 3, 0, 1], "eten", "4-6", [
    "Wat doe je eerst als je een taart bakt? En wat het laatst?", "Eerst pak je meel, melk en een ei. Dan roer je het beslag in een kom, dan gaat de taart in de oven en tot slot versier je hem met kaarsjes."])

# =====================================================================
# Legpuzzels (kolommen x rijen) met legbord
# =====================================================================
def put(sh, fn, x, y, k=1): fn(Pc(sh, x, y, k))
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
def puzzle(slug, name, cols, rows, c, draw, cat, age, diff, seed, numbers=True, minutes=25):
    W, H = cols * c, rows * c; x0, y0 = (200 - W) / 2, 36 if rows * c > 200 else 40
    sh = Sheet(); head(sh, name.split(": ")[-1][0].upper() + name.split(": ")[-1][1:])
    sh.text(100, 28, "Kleur de tekening, knip de stukjes los en leg de puzzel.", 6)
    draw(sh, x0, y0, W, H)
    sh.line(jigsaw_lines(cols, rows, x0, y0, c, seed), "cut"); sh.rect_line(x0, y0, W, H, "cut")
    if numbers:
        for i in range(cols * rows):
            r, k = divmod(i, cols); bx, by = x0 + k * c + 6.5, y0 + r * c + 6.5
            sh.circle_r(bx, by, 4.6, "-"); sh.text(bx, by + 2, str(i + 1), 5.5)
    sh.legend(["cut"], 277)
    lb = Sheet(); head(lb, "Legbord")
    lb.text(100, 28, "Leg elk stukje op het vak met hetzelfde nummer." if numbers else "Leg de stukjes op hun plek. Begin met de hoeken en de randen.", 6.5)
    lb.line(jigsaw_lines(cols, rows, x0, y0, c, seed), "l", "stroke-width:1"); lb.rect_line(x0, y0, W, H, "l", 0, "stroke-width:1.6")
    if numbers:
        for i in range(cols * rows):
            r, k = divmod(i, cols); lb.text(x0 + k * c + c / 2, y0 + r * c + c / 2 + 5, str(i + 1), 14 if c > 50 else 11)
    steps = ["Kleur de tekening helemaal in.",
             "Knip eerst langs de rechte buitenrand en daarna de stukjes los langs de streepjeslijnen.",
             "Hussel de stukjes door elkaar."]
    steps.append("Leg de puzzel op het legbord: elk stukje hoort op het vak met hetzelfde nummer. Wil je hem bewaren? Plak de stukjes vast." if numbers else
                 "Leg de puzzel op het legbord. Zoek eerst de vier hoekstukjes en de randstukjes met een rechte kant, en vul daarna het midden. Wil je hem bewaren? Plak de stukjes vast.")
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": minutes, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, {"slug": "stevig-papier", "optional": True}, {"slug": "lijmstift", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Op stevig papier gaat de puzzel langer mee. Print het legbord op gewoon papier.", "steps": steps}}},
        [("extra", "Legbord", lb)])

def sc_raket(p):
    for s in (-1, 1): p.add([(s * 10, 14), (s * 20, 30), (s * 10, 26)], "r")
    p.add(sample("M-6 30Q0 46 6 30Z"), "o"); p.add(sample("M-3 30Q0 38 3 30Z"), "y", sil=False)
    p.add(sample("M-10 30V-6C-10 -20 -4 -30 0 -34C4 -30 10 -20 10 -6V30Z"), "-")
    p.add(sample("M-10 -6C-10 -20 -4 -30 0 -34C4 -30 10 -20 10 -6Z"), "r", sil=False)
    p.add(circ(0, 6, 5.5), "b"); p.add(rect(-10, 20, 20, 4), "z", sil=False)
def ruimte_scene(sh, x0, y0, W, H):
    X = lambda v: x0 + v * W / 100; Y = lambda v: y0 + v * H / 100
    sh.rect_r(x0, y0, W, H, "n")
    sh.region(f"M{X(100)} {Y(80)}C{X(76)} {Y(80)} {X(60)} {Y(90)} {X(56)} {Y(100)}H{X(100)}Z", "z")
    for x, y, r in [(80, 90, 4), (92, 85, 2.5), (70, 95, 2.4)]: sh.circle_r(X(x), Y(y), r * W / 100 * 1.4, "z")
    put(sh, rs_planeet, X(24), Y(14), 1.3)
    sh.circle_r(X(86), Y(10), 9, "o"); sh.line(f"M{X(86) - 7} {Y(10) - 3}Q{X(86)} {Y(10) + 1} {X(86) + 8} {Y(10) - 4}", "l", "stroke-width:1.2")
    put(sh, lambda p: (setattr(p, "polys", []), sc_raket(p)), X(55), Y(46), 1.5)
    put(sh, rs_astronaut, X(20), Y(62), 1.1)
    put(sh, rs_komeet, X(66), Y(22), 1)
    put(sh, rs_alien, X(84), Y(64), .9)
    for x, y in [(10, 40), (48, 10), (40, 92), (92, 40), (10, 90), (30, 40), (80, 50), (52, 82)]: sh.region(star_path(X(x), Y(y), 4.5, 1.9), "y")
puzzle("puzzel-ruimte-12-stukjes", "Puzzel knippen: ruimte (12 stukjes)", 3, 4, 55, ruimte_scene, "ruimte", "4-6", 2, 21)

def palm(p):
    p.add(taper(sample("M0 0C3 -14 -2 -28 2 -44", 10), 4.5, 3.2), "w")
    for k in range(4, 40, 7): p.ln([(-3 + k * .05, -k), (3.5 + k * .05, -k - 2)], style="stroke-width:1")
    for ex, ey in [(-22, -36), (-18, -54), (24, -36), (20, -56), (2, -62)]:
        p.add(sample(f"M2 -44Q{(2 + ex) / 2 + (6 if ex < 0 else -6)} {(-44 + ey) / 2 - 8} {ex} {ey}Q{(2 + ex) / 2} {(-44 + ey) / 2 + 2} 2 -44Z"), "g")
def giraf_big(p):
    for x in (-14, -7, 9, 16): p.add(rect(x - 2.2, 4, 4.4, 30), "y")
    p.add(ellp(0, 0, 21, 12), "y")
    p.add([(12, -6), (26, -50), (34, -48), (21, 2)], "y")
    p.ln(sample("M-20 -2Q-28 4 -27 14", 4), style="stroke-width:1.4")
    for x in (27, 32): p.add(bar(x, -60, x, -66, 1), "w"); p.add(circ(x, -67, 2), "w")
    p.add(ellp(36, -56, 11, 6, 20), "y"); p.add(ellp(25, -58, 4, 2, -30), "y"); p.dot(34, -59, 1.6)
    p.dot(44, -52, 1)
    for x, y, r in [(-12, -4, 4), (-2, 2, 4.5), (8, -6, 3.5), (-14, 6, 3), (4, -3, 0) if False else (13, 3, 3), (22, -22, 3), (27, -36, 2.6), (19, -10, 2.6)]:
        p.add(sample(f"M{x - r} {y}L{x - r * .3} {y - r}L{x + r} {y - r * .5}L{x + r * .7} {y + r * .8}L{x - r * .5} {y + r}Z"), "w", sil=False)
def olifant_big(p):
    for x in (-18, -8, 8, 18): p.add(rrect(x - 4.5, 4, 9, 22, 2), "z")
    p.ln(sample("M-26 -4Q-31 2 -30 10", 4), style="stroke-width:1.4")
    p.add(ellp(0, -2, 27, 18), "z")
    p.add(taper(sample("M30 -6C38 0 40 12 38 22C37 26 34 26 33 23", 12), 6, 3), "z")
    p.add(circ(26, -12, 13), "z")
    p.add(sample("M16 -22C6 -24 4 -10 6 0C8 8 16 8 20 2Z"), "z")
    p.dot(30, -15, 1.7); p.add(sample("M32 -2Q38 0 40 -4L36 -4Z"), "-")
def nijlpaard_kop(p):
    p.add(rrect(-14, -8, 28, 14, 6), "z"); p.add(ellp(0, -10, 10, 7), "z")
    for x in (-7, 7): p.add(circ(x, -16, 3), "z"); p.add(circ(x * .6, -12, 2.6), "-", sil=False); p.dot(x * .6, -12, 1.2)
    p.dot(-6, 0, 1.1); p.dot(6, 0, 1.1)
def zoo_scene(sh, x0, y0, W, H):
    X = lambda v: x0 + v * W / 100; Y = lambda v: y0 + v * H / 100
    sh.rect_r(x0, y0, W, H, "b")
    sh.circle_r(X(88), Y(12), 9, "y")
    sh.region(f"M{X(46)} {Y(14)}C{X(46)} {Y(8)} {X(54)} {Y(6)} {X(57)} {Y(10)}C{X(60)} {Y(5)} {X(70)} {Y(7)} {X(70)} {Y(13)}C{X(74)} {Y(13)} {X(74)} {Y(18)} {X(70)} {Y(18)}H{X(48)}C{X(43)} {Y(18)} {X(43)} {Y(14)} {X(46)} {Y(14)}Z", "-")
    sh.region(f"M{x0} {Y(60)}Q{X(50)} {Y(52)} {X(100)} {Y(58)}V{Y(100)}H{x0}Z", "l")
    for k in range(10): sh.rect_r(X(1 + k * 10.6), Y(46), 3, 16, "w")
    sh.rect_r(x0, Y(48), W, 2.6, "w"); sh.rect_r(x0, Y(54), W, 2.6, "w")
    put(sh, palm, X(90), Y(74), 1.05)
    put(sh, giraf_big, X(24), Y(52), .95)
    put(sh, olifant_big, X(62), Y(68), .95)
    sh.region(f"M{X(4)} {Y(90)}C{X(4)} {Y(82)} {X(44)} {Y(80)} {X(48)} {Y(88)}C{X(50)} {Y(96)} {X(8)} {Y(98)} {X(4)} {Y(90)}Z", "t")
    put(sh, nijlpaard_kop, X(26), Y(87), .9)
    put(sh, ic_vogel, X(70), Y(34), .7)
    for x in (60, 94): sh.region(f"M{X(x)} {Y(97)}C{X(x) - 3} {Y(94)} {X(x) - 2} {Y(91)} {X(x)} {Y(94)}C{X(x) + 2} {Y(91)} {X(x) + 3} {Y(94)} {X(x)} {Y(97)}Z", "m")
puzzle("puzzel-dierentuin-9-stukjes", "Puzzel knippen: dierentuin (9 stukjes)", 3, 3, 56, zoo_scene, "dieren", "4-6", 1, 5)

def sc_schildpad(p):
    for x, y in [(-12, 8), (12, 8), (-12, -8), (12, -8)]: p.add(ellp(x * 1.1, y * 1.1, 6, 3.5, 30 if x * y > 0 else -30), "l")
    p.add(ellp(22, 0, 7, 5), "l"); p.dot(25, -1.5, 1.2)
    p.add(ellp(0, 0, 17, 13), "g")
    p.add([(-6, -5), (6, -5), (9, 3), (0, 8), (-9, 3)], "l", sil=False)
def sc_krab(p):
    for s in (-1, 1):
        for k in range(3): p.add(bar(s * 10, 4 + k * 3, s * 20, 10 + k * 4, 1.5), "r")
        p.add(bar(s * 9, -2, s * 15, -10, 2), "r"); p.add(circ(s * 16, -13, 5), "r")
        p.add(bar(s * 4, -8, s * 6, -14, .9), "r"); p.add(circ(s * 6, -15, 2.4), "-")
    p.add(ellp(0, 2, 13, 9), "r"); p.dot(-6, -15, 1.1); p.dot(6, -15, 1.1)
def sc_kist(p):
    p.add(rect(-16, -4, 32, 18), "w"); p.add(sample("M-16 -4C-16 -16 16 -16 16 -4Z"), "w")
    p.add(rect(-3, -6, 6, 7), "y", sil=False); p.ln([(-16, -4), (16, -4)])
    for x in (-10, 10): p.ln([(x, -12), (x, 14)], style="stroke-width:1.2")
def sc_wier(p, h=60, code="g"):
    for dx, hh in [(-5, h), (3, h * .8), (9, h * .6)]:
        c = sample(f"M{dx} 0Q{dx - 8} {-hh / 4} {dx} {-hh / 2}Q{dx + 8} {-hh * .75} {dx} {-hh}", 12); p.add(taper(c, 3, 1.2), code)
def onderwater_scene(sh, x0, y0, W, H):
    X = lambda v: x0 + v * W / 100; Y = lambda v: y0 + v * H / 100
    sh.rect_r(x0, y0, W, H, "b")
    sh.region(f"M{x0} {Y(8)}" + "".join(f"Q{X(k * 12.5 + 6.25)} {Y(4 if k % 2 else 12)} {X((k + 1) * 12.5)} {Y(8)}" for k in range(8)) + f"V{y0}H{x0}Z", "t")
    sh.region(f"M{x0} {Y(86)}Q{X(30)} {Y(80)} {X(60)} {Y(86)}T{X(100)} {Y(84)}V{Y(100)}H{x0}Z", "y")
    put(sh, L(sc_wier, 70, "g"), X(6), Y(92), 1); put(sh, L(sc_wier, 50, "l"), X(92), Y(92), 1); put(sh, L(sc_wier, 36, "g"), X(50), Y(90), 1)
    sh.region(f"M{X(64)} {Y(90)}V{Y(80)}L{X(60)} {Y(72)}L{X(63)} {Y(70)}L{X(66)} {Y(77)}L{X(68)} {Y(68)}L{X(71)} {Y(68)}L{X(70)} {Y(78)}L{X(74)} {Y(72)}L{X(77)} {Y(74)}L{X(72)} {Y(82)}V{Y(90)}Z", "m")
    put(sh, sc_kist, X(30), Y(88), 1.2)
    put(sh, sc_krab, X(80), Y(93), .8)
    sh.poly_r(star_pts(X(50), Y(96), 7, 3), "o")
    put(sh, sc_schildpad, X(64), Y(62), 1.2)
    put(sh, lambda p: (p.add(sample(fish_path(0, 0, 12)), "o"), p.dot(-7, -1.5, 1.5)), X(22), Y(24), 1.5)
    put(sh, lambda p: (p.add(sample(fish_path(0, 0, 10)), "y"), p.dot(-6, -1.5, 1.3)), X(56), Y(30), 1.4)
    put(sh, lambda p: (p.add(sample(fish_path(0, 0, 9)), "r"), p.dot(-5.5, -1.3, 1.2)), X(28), Y(46), 1.3)
    put(sh, lambda p: (p.add(sample(fish_path(0, 0, 8)), "p"), p.dot(-5, -1.2, 1.1)), X(84), Y(44), 1.2)
    put(sh, ic_kwal, X(66), Y(4), 1.1)
    put(sh, ic_octopus, X(8), Y(56), 1.2)
    for x, y, r in [(40, 18, 2.5), (42, 12, 1.8), (72, 22, 2.2), (74, 16, 1.6), (90, 30, 2), (44, 60, 2.4)]: sh.circle_r(X(x), Y(y), r, "-")
puzzle("puzzel-onderwater-20-stukjes", "Puzzel knippen: onderwaterwereld (20 stukjes)", 4, 5, 42, onderwater_scene, "zee", "9+", 3, 13, numbers=False, minutes=40)

# =====================================================================
# Vingerpoppetjes: kopje met een ringstrook eronder
# =====================================================================
HK = 1.55  # schaal van het hoofdje
def sub(p, k):
    q = Pc(p.sh, p.dx, p.dy, p.sc * k); q.polys = p.polys; return q
def face(q, cheeks=True):
    q.add(circ(0, 0, 11), "-"); q.dot(-4, -1, 1.3); q.dot(4, -1, 1.3); q.ln(sample("M-4 4Q0 7 4 4", 4), style="stroke-width:1.1")

def ring(p, code="-", extra=None):
    p.add(rect(-33, 15, 66, 14), code)
    p.sh.raw(f'<rect class="glue" x="{f(p.dx + 21 * p.sc)}" y="{f(p.dy + 15.8 * p.sc)}" width="{f(11.2 * p.sc)}" height="{f(12.4 * p.sc)}"/>')
    if extra: extra(p)
def hat_politie(p):
    p.add(sample("M-12 -6C-13 -14 -8 -16 0 -16C8 -16 13 -14 12 -6Z"), "n"); p.add(sample("M-12 -6H12L14 -3H-14Z"), "x")
    p.add(star_pts(0, -10, 3.5, 1.5), "y", sil=False)
def hat_piloot(p):
    p.add(sample("M-12 -6C-13 -13 -8 -15 0 -15C8 -15 13 -13 12 -6Z"), "n"); p.add(rect(-12, -7, 24, 3), "y")
    p.add(sample("M-8 -6H8L10 -2H-10Z"), "x"); p.add(sample("M-5 -11L0 -9L5 -11L3 -13H-3Z"), "y", sil=False)
def puppet(face_fn, hat=None, coat="-", extra=None, behind=None):
    def fn(p):
        q = sub(p, HK)
        if behind: behind(q)
        ring(p, coat, extra)
        face_fn(q)
        if hat: hat(q)
    return fn
def tie(p): p.add([(-3, 15), (3, 15), (2, 19), (4, 27), (0, 29), (-4, 27), (-2, 19)], "r", sil=False)
def badge(p): p.add(star_pts(-14, 22, 4.5, 2), "y", sil=False)
def steto(p): p.ln(sample("M-10 15Q-12 24 -4 25Q4 24 2 15", 6), style="stroke-width:1.1"); p.add(circ(-4, 25.5, 2), "z", sil=False)
def buttons(p): [p.add(circ(-12, y, 1.3), "y", sil=False) for y in (19, 25)]
def stripes(p): p.add(rect(-33, 20, 54, 4), "y", sil=False)
def vinger_sheet(slug, name, heading, figs, cat, steps_intro):
    sh = Sheet(); head(sh, heading)
    sh.text(100, 26, "Kleur de poppetjes in en knip ze uit, samen met hun strookje.", 6)
    pack(sh, [figs[0:2], figs[2:4], figs[4:6]], y0=30, ymax=268, gap=6)
    sh.legend(["cut", "glue"], 277)
    write(OUT, slug, sh, {"category": cat, "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": name, "steps": [
            "Kleur de zes poppetjes in. " + steps_intro,
            "Knip elk poppetje uit langs de streepjeslijn. Het kopje en het strookje blijven aan elkaar vast.",
            "Leg het strookje om je vinger en plak het einde op het grijze vakje. Niet te strak: je vinger moet er makkelijk in en uit kunnen.",
            "Steek je vingers in de poppetjes en speel een toneelstukje!"]}}})

def hair_short(q): q.add(sample("M-11 -2C-13 -12 -6 -14 0 -14C6 -14 13 -12 11 -2C8 -8 -8 -8 -11 -2Z"), "w")
vinger_sheet("vingerpoppetjes-beroepen", "Vingerpoppetjes: beroepen", "Vingerpoppetjes: beroepen", [
    puppet(face, hat_kok, "-", buttons), puppet(face, hat_brand, "n", stripes), puppet(lambda q: (face(q), q.add(sample("M-11 -2C-12 -12 -6 -12 0 -12C6 -12 12 -12 11 -2C9 -8 -9 -8 -11 -2Z"), "w"), q.add(circ(0, -10, 4.5), "z"), q.add(circ(0, -10, 2), "-", sil=False)), None, "-", steto),
    puppet(face, hat_politie, "n", badge), puppet(face, hat_bouw, "o", stripes), puppet(face, hat_piloot, "n", tie)], "beroepen",
    "De kok, de brandweer, de dokter, de politie, de bouwvakker en de piloot.")

def crown(q, y=-9, w=11, code="y"):
    q.add([(-w, y), (-w, y - 9), (-w / 2, y - 4), (0, y - 11), (w / 2, y - 4), (w, y - 9), (w, y)], code)
    for x in (-w, 0, w): q.add(circ(x, y - 10 if x == 0 else y - 9, 1.6), "r", sil=False)
def koning_face(q):
    q.add(sample("M-10 2C-10 14 -4 18 0 18C4 18 10 14 10 2Q0 8 -10 2Z"), "w")
    q.add(circ(0, -2, 11), "-"); q.dot(-4, -4, 1.3); q.dot(4, -4, 1.3)
    q.add(sample("M-10 2C-10 14 -4 18 0 18C4 18 10 14 10 2Q0 8 -10 2Z"), "w", sil=False); q.ln(sample("M-3 6Q0 8 3 6", 4), style="stroke-width:1.1")
    crown(q, -10, 11)
def prinses_hair(q): q.add(sample("M-12 -2C-15 -16 15 -16 12 -2L14 18H-14Z"), "y")
def prinses_face(q):
    face(q); q.add(sample("M-11 -2C-12 -12 -4 -13 0 -12C4 -13 12 -12 11 -2C8 -7 2 -8 0 -6C-2 -8 -8 -7 -11 -2Z"), "y")
    q.add([(-6, -10), (-6, -15), (-3, -12), (0, -17), (3, -12), (6, -15), (6, -10)], "m"); q.add(circ(0, -14, 1.4), "b", sil=False)
def heks_face(q):
    q.add(sample("M-12 -4C-16 4 -14 14 -12 18L-8 16C-10 8 -10 2 -8 -2ZM12 -4C16 4 14 14 12 18L8 16C10 8 10 2 8 -2Z"), "x") if False else None
    for s in (-1, 1): q.add(sample(f"M{s * 9} -4C{s * 15} 4 {s * 14} 12 {s * 13} 17L{s * 9} 15C{s * 10} 8 {s * 10} 2 {s * 7} -2Z"), "x")
    q.add(circ(0, 0, 11), "l"); q.dot(-4, -1, 1.3); q.dot(4, -1, 1.3); q.ln(sample("M-4 5Q0 7 4 5", 4), style="stroke-width:1.1")
    q.add(ellp(0, 2, 2, 3), "l", sil=False)
    q.add(ellp(0, -6, 18, 3.5), "x"); q.add(sample("M-9 -7C-8 -16 0 -22 8 -34C6 -22 9 -14 9 -7Z"), "x"); q.add(rect(-9, -10, 18, 3), "p", sil=False)
def ridder_face(q):
    q.add(sample("M-1 -18C2 -26 10 -28 14 -24C8 -24 6 -20 4 -14Z"), "r")
    q.add(sample("M-12 12V-4C-12 -14 -6 -18 0 -18C6 -18 12 -14 12 -4V12Z"), "z")
    q.add(rect(-12, -4, 24, 5), "x", sil=False); q.ln([(0, 1), (0, 12)], style="stroke-width:1.2")
    for x in (-5, 5): [q.dot(x + dx, 7, .7) for dx in (-1.5, 1.5)]
def draak_face(q):
    for s in (-1, 1): q.add([(s * 3, -9), (s * 10, -23), (s * 10, -6)], "y")
    for x in (-4, 0, 4): q.add([(x - 2.5, -10), (x, -15), (x + 2.5, -10)], "g")
    q.add(circ(0, 0, 11), "g")
    q.add(ellp(0, 6, 9, 6), "l"); q.dot(-3, 5, 1); q.dot(3, 5, 1)
    for s in (-1, 1): q.add(circ(s * 5, -4, 3), "-", sil=False); q.dot(s * 5, -4, 1.4)
    q.ln(sample("M-6 10Q0 13 6 10", 4), style="stroke-width:1.1")
    for x in (-3, 3): q.add([(x - 1.2, 10.5), (x, 13), (x + 1.2, 10.5)], "-", sil=False)
def kabouter_face(q):
    q.add(circ(0, 0, 11), "-"); q.dot(-4, -1, 1.3); q.dot(4, -1, 1.3)
    q.add(sample("M-11 2C-12 12 -6 20 0 22C6 20 12 12 11 0Q6 6 0 4Q-6 6 -11 0Z"), "-")
    q.add(circ(0, 2, 3), "k")
    q.add(sample("M-12 -6C-12 -14 -6 -20 2 -34C4 -22 12 -14 12 -6Z"), "r"); q.add(rrect(-13, -9, 26, 5, 2), "r")
def kikker_face(q):
    for s in (-1, 1): q.add(circ(s * 7, -8, 5.5), "g")
    q.add(ellp(0, 1, 13, 10), "g")
    for s in (-1, 1): q.add(circ(s * 7, -8, 3), "-", sil=False); q.dot(s * 7, -8, 1.5)
    q.ln(sample("M-8 3Q0 9 8 3", 6), style="stroke-width:1.1")
    crown(q, -12, 6)
vinger_sheet("vingerpoppetjes-sprookjes", "Vingerpoppetjes: sprookjesfiguren", "Vingerpoppetjes: sprookjes", [
    puppet(koning_face, None, "r", buttons), puppet(prinses_face, None, "m", None, prinses_hair), puppet(heks_face, None, "p"),
    puppet(ridder_face, None, "z", badge), puppet(kabouter_face, None, "b", buttons), puppet(kikker_face, None, "l")], "sprookjes",
    "De koning, de prinses, de heks, de ridder, de kabouter en de kikker met een kroontje.")

# =====================================================================
# Hoofdbanden: drie lange stroken (samen ruim genoeg voor elk hoofd)
# =====================================================================
SL = 244  # lengte van een strook (ongeveer 25,5 cm)
def band_strip(sh, x, y, w, label, deco, glue=True, spikes=None):
    pc = Pc(sh, x, y)
    pc.add(rect(0, 0, w, SL), "-")
    if spikes:
        n = int(SL // 20)
        for k in range(n):
            y0 = 2 + k * 20 + (SL - 4 - n * 20) / 2
            pc.add([(w, y0), (w + spikes, y0 + 10), (w, y0 + 20)], "yo"[k % 2])
    if glue: glue_rect(sh, x + 1, y + 1, w - 2, 12)
    deco(pc, w)
    sh.text(x + w / 2, y + (24 if glue else 10), label, 8)
    for lp in outline(pc.polys, 2.5, .25): sh.line(P(lp), "cut")
def eenhoorn_band():
    sh = Sheet(); head(sh, "Eenhoorn-hoofdband")
    def deco_a(pc, w):
        pc.add(rect(w / 2 - 10, SL / 2 - 20, 20, 40), "-", sil=False); pc.text(w / 2, SL / 2 + 2, "hoorn", 5, cls="tip")
        for k, y in enumerate([30, 60, 90, 154, 184, 214]): pc.add(sample(heart_path(w / 2, y, 7)) if k % 2 else star_pts(w / 2, y, 7, 3), "m" if k % 2 else "y", sil=False)
    def deco_b(pc, w):
        for k, y in enumerate(range(44, SL - 10, 30)): pc.add(sample(heart_path(w / 2, y, 7)) if k % 2 else star_pts(w / 2, y, 7, 3), "m" if k % 2 else "y", sil=False)
    band_strip(sh, 8, 24, 24, "A", deco_a, glue=False)
    band_strip(sh, 40, 24, 24, "B", deco_b)
    band_strip(sh, 72, 24, 24, "C", deco_b)
    def hoorn(pc):
        pc.add([(-16, 60), (0, 0), (16, 60)], "y")
        for k in range(1, 5): yy = k * 12; pc.ln([(-16 * yy / 60, yy - 2), (16 * (yy + 6) / 60, yy + 6)], style="stroke-width:1.4")
        pc.add(rect(-16, 60, 32, 16), "-"); pc.text(0, 70.5, "lijm achter", 4.6, cls="tip")
    def oor(pc):
        pc.add(sample("M-11 30C-14 14 -6 4 0 0C6 4 14 14 11 30Z"), "-"); pc.add(sample("M-6 26C-8 16 -3 9 0 6C3 9 8 16 6 26Z"), "k", sil=False)
        pc.add(rect(-11, 30, 22, 10), "-"); pc.text(0, 37, "lijm", 4.6, cls="tip")
    def bloem(code):
        def fn(pc):
            pc.add(union([circ(8 * math.cos(math.radians(a)), 8 * math.sin(math.radians(a)), 6) for a in range(0, 360, 72)]), code)
            pc.add(circ(0, 0, 4.5), "y")
        return fn
    def blad(pc): pc.add(sample(leaf_path(0, 0, 6, 11)), "g"); pc.ln([(0, -9), (0, 9)], style="stroke-width:1")
    place(sh, S(hoorn, 1.2), 124, 26)
    place(sh, oor, 104, 128); place(sh, oor, 150, 128)
    flow(sh, [S(bloem(c), .85) for c in "mpbr"] + [blad, blad, blad], 101, 172, 199, 1)
    sh.legend(["cut", "glue"], 277)
    write(OUT, "eenhoorn-hoofdband", sh, {"category": "sprookjes", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 30, "adultHelp": True,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "plakband", "optional": True}],
        "i18n": {"nl": {"name": "Eenhoorn-hoofdband", "printNote": "Print op ware grootte (100%), dan zijn de stroken samen lang genoeg.", "steps": [
            "Kleur de stroken, de hoorn, de oortjes en de bloemen in.",
            "Knip alles uit langs de streepjeslijn.",
            "Plak strook B aan strook A: lijm op het grijze vakje van B en leg het einde van A erop. Plak strook C op dezelfde manier aan B.",
            "Leg de band om het hoofd, met strook A in het midden van je voorhoofd. Plak hem op de goede maat vast en knip het stuk dat te lang is eraf.",
            "Smeer lijm op de achterkant van het witte vakje onder de hoorn en plak de hoorn op het vak 'hoorn' op strook A. Plak de oortjes links en rechts ernaast.",
            "Plak de bloemen en blaadjes onder de hoorn. Klaar: je bent een eenhoorn!"]}}})
eenhoorn_band()

def dinokroon():
    sh = Sheet(); head(sh, "Dinokroon met stekels")
    def deco(pc, w):
        for y in range(40, SL - 10, 26): pc.add(circ(w / 2, y, 4.5), "g", sil=False)
    def deco_c(pc, w):
        for y in range(40, SL - 10, 26): pc.add(circ(w / 2, y, 4.5), "g", sil=False)
    band_strip(sh, 8, 24, 20, "A", deco, glue=False, spikes=18)
    band_strip(sh, 54, 24, 20, "B", deco, spikes=18)
    band_strip(sh, 100, 24, 20, "C", deco_c)
    def ogen(pc):
        for s in (-1, 1): pc.add(circ(s * 13, 0, 11), "-"); pc.add(circ(s * 13 + 2, 1, 5), "g", sil=False); pc.dot(s * 13 + 2, 1, 2.4)
        pc.add(rect(-13, -2, 26, 4), "-")
    place(sh, ogen, 134, 40)
    sh.text(163, 76, "ogen: plak ze", 6); sh.text(163, 84, "voorop strook A", 6)
    for k, (x, y) in enumerate([(162, 110), (148, 150), (178, 150)]):
        place(sh, lambda pc, c="yrp"[k]: (pc.add(ellp(0, 0, 10, 13), "-"), pc.add(sample("M-9 -4L-4 1L0 -5L4 1L9 -4L10 0L-10 0Z"), c, sil=False)), x - 13, y - 16)
    sh.text(163, 192, "dino-eitjes: plak", 6); sh.text(163, 200, "ze op de band", 6)
    sh.legend(["cut", "glue"], 277)
    write(OUT, "dinokroon-met-stekels", sh, {"category": "dinos", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 30, "adultHelp": True,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "plakband", "optional": True}],
        "i18n": {"nl": {"name": "Dinokroon met stekels", "printNote": "Print op ware grootte (100%), dan zijn de stroken samen lang genoeg.", "steps": [
            "Kleur de stroken, de stekels, de ogen en de eitjes in.",
            "Knip alles uit langs de streepjeslijn. Knip de stekels netjes langs de punten.",
            "Plak strook B aan strook A: lijm op het grijze vakje van B en leg het einde van A erop. Plak strook C op dezelfde manier aan B.",
            "Leg de band om het hoofd met de stekels naar boven. Plak hem op de goede maat vast en knip het stuk dat te lang is eraf.",
            "Plak de ogen voorop strook A en versier de band met de eitjes. Grrr, je bent een dinosaurus!"]}}})
dinokroon()

# =====================================================================
# Maskers
# =====================================================================
def masker(slug, name, build, colors_step):
    sh = Sheet(); head(sh, name.split(": ")[-1][0].upper() + name.split(": ")[-1][1:] + "masker")
    pc = Pc(sh, 100, 110); build(pc); pc.cut(2.5)
    for s in (-1, 1):
        sh.raw(f'<ellipse class="cut" cx="{100 + s * 28}" cy="104" rx="13" ry="9" fill="none"/>')
        sh.circle_line(100 + s * 66, 106, 2.4, "cut")
    sh.text(100, 200, "Ooggaten en gaatjes voor het elastiek: laat een volwassene helpen.", 6)
    sh.legend(["cut"], 277)
    write(OUT, slug, sh, {"category": "dieren", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, {"slug": "elastiek"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier (160 gram), dan blijft het masker beter in vorm.", "steps": [
            colors_step,
            "Knip het masker uit langs de buitenste streepjeslijn.",
            "Een volwassene knipt de ooggaten uit (prik eerst een gaatje in het midden) en prikt de twee kleine gaatjes aan de zijkant.",
            "Knoop aan elke kant een stuk elastiek vast, zo lang dat het masker goed om je hoofd past. Probeer of je goed kunt kijken."]}}})
def tijger(p):
    for s in (-1, 1): p.add(circ(s * 54, -52, 18), "o"); p.add(circ(s * 54, -52, 9), "-", sil=False)
    p.add(sample("M-78 -14C-78 -52 -40 -68 0 -68C40 -68 78 -52 78 -14L88 2L76 10L84 26L68 30L66 46C52 62 26 70 0 70C-26 70 -52 62 -66 46L-68 30L-84 26L-76 10L-88 2Z"), "o")
    for x, h in [(0, 26), (-14, 18), (14, 18)]: p.add([(x - 5, -67), (x, -67 + h), (x + 5, -67)], "x", sil=False)
    for s in (-1, 1):
        for y, l in [(-30, 22), (-14, 26), (2, 20)]: p.add([(s * 78, y - 4), (s * (78 - l), y + 1), (s * 78, y + 5)], "x", sil=False)
        p.add(ellp(s * 28, -6, 21, 15), "-", sil=False)
    for s in (-1, 1): p.add(ellp(s * 15, 36, 20, 15), "-", sil=False)
    p.add(sample("M-10 18H10Q10 26 0 30Q-10 26 -10 18Z"), "m", sil=False)
    p.ln([(0, 30), (0, 40)]); p.ln(sample("M-14 44Q-6 48 0 40Q6 48 14 44", 8))
    for s in (-1, 1):
        for y in (32, 38): p.dot(s * 14, y, 1.3) if False else p.dot(s * (12 + (y - 32)), y, 1.4)
def panda(p):
    for s in (-1, 1): p.add(circ(s * 54, -50, 20), "x")
    p.add(ellp(0, 0, 78, 66), "-")
    for s in (-1, 1): p.add(ellp(s * 28, -4, 24, 18, s * 20), "x", sil=False); p.add(circ(s * 46, 30, 8), "k", sil=False)
    p.add(ellp(0, 24, 10, 7), "x", sil=False); p.ln([(0, 31), (0, 38)]); p.ln(sample("M-12 40Q-6 46 0 38Q6 46 12 40", 8))
    p.add(ellp(0, 46, 0, 0), "-", sil=False) if False else None
masker("masker-tijger", "Masker: tijger", tijger, "Kleur de tijger oranje met zwarte strepen. Laat de snuit en de plekken rond de ogen wit.")
masker("masker-panda", "Masker: panda", panda, "Kleur de oren en de vlekken rond de ogen zwart en de wangen roze. De rest van de panda blijft wit.")

# =====================================================================
# Papieren telefoon met insteekschermen
# =====================================================================
def tel_status(p):
    p.text(10, 13, "12:00", 4.6, anchor="start"); p.add(rrect(43, 9, 9, 4.5, 1), "-", sil=False); p.add(rect(44, 10, 5, 2.5), "l", sil=False)
def scr_bellen(p):
    tel_status(p); p.text(30, 26, "Oma belt...", 6.5)
    p.add(circ(30, 48, 13), "b"); p.add(circ(30, 45, 6), "-"); p.add(sample("M19 56Q30 46 41 56Q36 61 30 61Q24 61 19 56Z"), "-")
    p.add(sample("M24 41Q30 36 36 41Q34 38 30 38Q26 38 24 41Z"), "z")
    p.dot(28, 44, .9); p.dot(32, 44, .9)
    p.add(circ(17, 80, 7), "g"); p.add(circ(43, 80, 7), "r")
    p.ln([(13.5, 80), (16.5, 83), (21, 77)], style="stroke-width:1.6"); p.ln([(40, 77), (46, 83)], style="stroke-width:1.6"); p.ln([(46, 77), (40, 83)], style="stroke-width:1.6")
def scr_foto(p):
    tel_status(p); p.text(30, 26, "Foto's", 6.5)
    p.add(rect(10, 32, 40, 40), "b"); p.add(rect(10, 60, 40, 12), "l", sil=False)
    put(p.sh, ic_hond, p.dx + 13, p.dy + 30, .85)
    for k in range(3): p.add(rect(10 + k * 14, 76, 12, 12), "-")
def scr_muziek(p):
    tel_status(p); p.text(30, 26, "Muziek", 6.5)
    p.add(rrect(14, 32, 32, 30, 4), "p")
    p.add(sample("M26 54C22 54 21 58 24 59C27 60 29 58 29 55V40L37 38V51C33 50 32 54 35 55C38 56 40 54 40 51V35L27 38V54Z"), "-")
    p.ln([(12, 70), (48, 70)], style="stroke-width:1.2"); p.add(circ(24, 70, 2.2), "-")
    p.add([(26, 76), (26, 86), (34, 81)], "x"); p.add([(12, 78), (17, 81), (12, 84)], "x"); p.add([(48, 78), (43, 81), (48, 84)], "x")
def scr_weer(p):
    tel_status(p); p.text(30, 26, "Het weer", 6.5)
    p.add(circ(24, 42, 9), "y")
    for a in range(0, 360, 45):
        t = math.radians(a); p.ln([(24 + 12 * math.cos(t), 42 + 12 * math.sin(t)), (24 + 15 * math.cos(t), 42 + 15 * math.sin(t))], style="stroke-width:1.2")
    p.add(union([circ(34, 50, 6), circ(40, 46, 7), circ(46, 51, 5), rect(32, 50, 16, 6)]), "-")
    p.text(30, 76, "21 graden", 7); p.text(30, 87, "zonnig", 5.5)
def scr_berichten(p):
    tel_status(p); p.text(30, 26, "Berichtjes", 6.5)
    p.add(rrect(8, 32, 30, 12, 4), "l"); p.text(23, 40, "Hoi!", 5.5)
    p.add(rrect(18, 50, 34, 18, 4), "b"); p.text(35, 58, "Kom je", 5); p.text(35, 64.5, "spelen?", 5)
    p.add(rrect(8, 74, 22, 12, 4), "l"); p.add(sample(heart_path(19, 80, 4)), "r", sil=False)
def scr_leeg(p):
    tel_status(p); p.text(30, 26, "Mijn app", 6.5); p.text(30, 88, "teken zelf!", 5, cls="tip")
def telefoon():
    sh = Sheet(); head(sh, "Papieren telefoon")
    x0, y0, w, h = 20, 30, 70, 124
    # achterkant + lijmflapjes
    sh.rect_r(x0 + w + 2.5, y0 + 2.5, w - 5, h - 5, "-", 3)
    glue_rect(sh, x0 + 2 * w, y0 + 4, 7, h - 8); glue_rect(sh, x0 + w + 4, y0 + h, w - 8, 7)
    tabs = f"M{x0 + 2 * w} {y0}L{x0 + 2 * w + 7} {y0 + 6}V{y0 + h - 6}L{x0 + 2 * w} {y0 + h}"
    btab = f"M{x0 + 2 * w} {y0 + h}L{x0 + 2 * w - 6} {y0 + h + 7}H{x0 + w + 6}L{x0 + w} {y0 + h}"
    sh.line(f"M{x0} {y0}H{f(x0 + 55 - 6 - 20)}" if False else "", "cut") if False else None
    # voorkant
    sh.rect_r(x0 + 2.5, y0 + 2.5, w - 5, h - 5, "x", 6)
    sh.line(f"M{x0 + 12} {y0 + 6}h12", "l", "stroke-width:2"); sh.circle_r(x0 + w - 12, y0 + 6, 2.2, "-")
    sh.circle_r(x0 + w / 2, y0 + 110, 6, "-")
    sh.raw(f'<rect class="cut" x="{x0 + 8}" y="{y0 + 12}" width="{w - 16}" height="84" rx="3" fill="none"/>')
    sh.text(x0 + w / 2, y0 + 56, "knip dit", 5.5, cls="tip"); sh.text(x0 + w / 2, y0 + 63, "venster uit", 5.5, cls="tip")
    # achterkant versiering
    bx = x0 + w
    sh.rect_r(bx + 6, y0 + 6, 20, 20, "z", 4); sh.circle_r(bx + 12, y0 + 12, 4, "x"); sh.circle_r(bx + 20, y0 + 20, 4, "x"); sh.circle_r(bx + 20, y0 + 12, 1.8, "y")
    for k, (xx, yy) in enumerate([(bx + 18, y0 + 46), (bx + 50, y0 + 22), (bx + 50, y0 + 58), (bx + 18, y0 + 80), (bx + 34, y0 + 104), (bx + 50, y0 + 92)]):
        sh.region(heart_path(xx, yy, 7), "m") if k % 2 == 0 else sh.poly_r(star_pts(xx, yy, 8, 3.4), "y")
    sh.seg(x0 + w, y0, x0 + w, y0 + h, "fold")
    sh.seg(x0 + 2 * w, y0, x0 + 2 * w, y0 + h, "fold"); sh.seg(x0 + w, y0 + h, x0 + 2 * w, y0 + h, "fold")
    # kniplijn rondom (met duimgleuf bovenin de voorkant)
    n = 12; cx = x0 + w / 2; r = 7
    arc = " ".join(f"L{f(cx - r * math.cos(math.pi * k / n))} {f(y0 + r * math.sin(math.pi * k / n))}" for k in range(n + 1))
    sh.line(f"M{x0} {y0 + h}V{y0}H{f(cx - r)}{arc}H{x0 + 2 * w}L{x0 + 2 * w + 7} {y0 + 6}V{y0 + h - 6}L{x0 + 2 * w} {y0 + h}L{x0 + 2 * w - 6} {y0 + h + 7}H{x0 + w + 6}L{x0 + w} {y0 + h}Z", "cut")
    sh.text(x0 + w / 2, y0 + h + 10, "voorkant", 6, cls="tip"); sh.text(x0 + 1.5 * w, y0 + h + 15, "achterkant", 6, cls="tip")
    # uitleg
    sh.text(100, 186, "Zo maak je hem:", 7)
    for i, t in enumerate(["1. Knip de telefoon uit. Een volwassene knipt het venster eruit.",
                           "2. Vouw de grijze flapjes naar achteren en smeer er lijm op.",
                           "3. Vouw de achterkant achter de voorkant en druk goed aan.",
                           "4. Kleur de schermpjes op blad 2, knip ze los en schuif",
                           "er eentje van bovenaf in de telefoon. Tring tring!"]):
        sh.text(16 if i < 4 else 22, 198 + i * 10, t, 6, "start")
    sh.legend(["cut", "fold", "glue"], 277)
    p2 = Sheet(); head(p2, "Schermpjes")
    p2.text(100, 26, "Kleur de schermpjes, knip ze los en schuif ze in je telefoon.", 6)
    gx, gy, CWd, CHt = 10, 32, 60, 112
    for k, fn in enumerate([scr_bellen, scr_foto, scr_muziek, scr_weer, scr_berichten, scr_leeg]):
        col, row = k % 3, k // 3; frame_at(p2, fn, gx + col * CWd, gy + row * CHt)
    for r in range(3): p2.seg(gx, gy + r * CHt, gx + 3 * CWd, gy + r * CHt, "cut")
    for c in range(4): p2.seg(gx + c * CWd, gy, gx + c * CWd, gy + 2 * CHt, "cut")
    p2.legend(["cut"], 277)
    write(OUT, "papieren-telefoon", sh, {"category": "thuis", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 30, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Papieren telefoon met schermpjes", "printNote": "Print blad 1 het liefst op stevig papier; de schermpjes op blad 2 mogen op gewoon papier.", "steps": [
            "Kleur de telefoon in: de voorkant, de achterkant met hartjes en sterren, en de zes schermpjes op blad 2.",
            "Knip de telefoon uit langs de streepjeslijn. Een volwassene knipt het venster uit de voorkant.",
            "Vouw de twee grijze flapjes naar achteren, naar de witte kant van het papier, en smeer er lijm op.",
            "Vouw de achterkant op de middelste vouwlijn achter de voorkant en druk de flapjes goed aan. Bovenin blijft de telefoon open: dat is het zakje voor de schermpjes.",
            "Knip de schermpjes los en schuif er eentje van bovenaf in. Met het halve rondje bovenin pak je hem er weer uit.",
            "Wie bel jij? Op het lege schermpje teken je je eigen app."]}}},
        [("extra", "Schermpjes", p2)])
telefoon()

# =====================================================================
# Papieren fototoestel: foto's schuiven er onderaan uit
# =====================================================================
def foto_frame(p, label=True):
    p.add(rect(5, 5, 50, 52), "b", sil=False)
    if label: p.ln([(10, 82), (50, 82)], style="stroke-width:.8")
def ft_strand(p):
    foto_frame(p); p.add(rect(5, 38, 50, 19), "y", sil=False); p.add(sample("M5 38Q17 34 30 38Q43 42 55 38V44H5Z"), "n", sil=False)
    p.add(circ(42, 16, 6), "y"); p.add(sample("M14 40L22 20L30 40Z"), "-", sil=False) if False else None
    p.add(bar(16, 52, 22, 26, .9), "w"); p.add(sample("M8 28Q22 14 36 28Z"), "r")
def ft_hond(p): foto_frame(p); put(p.sh, ic_hond, p.dx + 10, p.dy + 10, 1.0)
def ft_taart(p):
    foto_frame(p); p.add(rrect(14, 32, 32, 18, 3), "m"); p.add(rect(10, 50, 40, 3), "z")
    for x in (20, 30, 40): p.add(rect(x - 1.5, 22, 3, 10), "b"); p.add(sample(f"M{x} 14C{x + 3} 18 {x + 2.5} 21 {x} 21C{x - 2.5} 21 {x - 3} 18 {x} 14Z"), "y")
def ft_huis(p):
    foto_frame(p); p.add(rect(12, 32, 24, 22), "r"); p.add([(9, 32), (24, 18), (39, 32)], "w"); p.add(rect(21, 42, 6, 12), "w")
    p.add(rect(44, 38, 4, 16), "w"); p.add(circ(46, 32, 8), "g"); p.add(circ(46, 12, 4.5), "y")
def ft_bloem(p):
    foto_frame(p); p.ln([(30, 54), (30, 30)], style="stroke-width:1.6"); p.add(ellp(24, 46, 6, 2.6, 25), "g")
    p.add(union([circ(30 + 8 * math.cos(math.radians(a)), 24 + 8 * math.sin(math.radians(a)), 5.5) for a in range(0, 360, 60)]), "r"); p.add(circ(30, 24, 4.5), "y")
    p.add(ellp(12, 14, 4, 3), "o") if False else None
def ft_leeg(p): foto_frame(p); p.text(30, 33, "teken zelf", 5, cls="tip")
def fototoestel():
    sh = Sheet(); head(sh, "Papieren fototoestel")
    x0, w, yt, h = 30, 140, 28, 84; yf = yt + h; yb = yf + h; t = 7
    # achterkant (bovenste helft, op z'n kop)
    sh.rect_r(x0 + 2.5, yt + 2.5, w - 5, h - 2.5, "z", 4)
    sh.raw(f'<g transform="rotate(180 100 {yt + h / 2})">')
    sh.rect_r(x0 + 16, yt + 12, 22, 16, "x", 3); sh.rect_r(x0 + 20, yt + 15, 14, 10, "b", 2)
    sh.text(100, yt + 50, "achterkant", 6, cls="tip")
    for k in range(6): sh.seg(x0 + 96 + k * 6, yt + 34, x0 + 96 + k * 6, yt + 64, "l", "stroke-width:1.2")
    sh.raw("</g>")
    for s in (-1, 1):
        ex = x0 if s < 0 else x0 + w
        glue_rect(sh, min(ex, ex + s * t), yt + 6, t, h - 12)
    # voorkant
    sh.rect_r(x0 + 2.5, yf, w - 5, h - 2.5, "r", 4)
    sh.rect_r(x0 + 2.5, yf, w - 5, 14, "x", 0)
    sh.rect_r(x0 + 12, yf + 22, 22, 12, "-", 2); sh.text(x0 + 23, yf + 30.5, "flits", 4.8, cls="tip")
    sh.rect_r(x0 + w - 30, yf + 22, 18, 12, "b", 2)
    sh.circle_r(x0 + w - 21, yf + 48, 6, "y")
    for r, c in [(23, "z"), (17, "x"), (11, "b")]: sh.circle_r(100, yf + 38, r, c)
    sh.circle_r(95, yf + 33, 3, "-")
    sh.rect_r(x0 + 22, yb - 12, w - 44, 5, "x", 2)
    sh.text(100, yb - 15, "hier komt de foto uit", 4.8, cls="tip")
    # vouw- en kniplijnen
    sh.seg(x0, yf, x0 + w, yf, "fold"); sh.seg(x0, yt, x0, yf, "fold"); sh.seg(x0 + w, yt, x0 + w, yf, "fold")
    sh.line(f"M{x0} {yb}V{yf}L{x0 - t} {yf - 6}V{yt + 6}L{x0} {yt}H{x0 + w}L{x0 + w + t} {yt + 6}V{yf - 6}L{x0 + w} {yf}V{yb}Z", "cut")
    sh.text(100, 210, "Zo maak je hem:", 7)
    for i, tx in enumerate(["1. Knip het fototoestel uit langs de streepjeslijn.",
                            "2. Vouw de grijze flapjes naar achteren en smeer er lijm op.",
                            "3. Vouw de achterkant naar achteren, achter de voorkant.",
                            "4. Schuif een foto van onderen in het toestel. Klik!"]):
        sh.text(18, 222 + i * 10, tx, 6, "start")
    sh.legend(["cut", "fold", "glue"], 277)
    p2 = Sheet(); head(p2, "Foto's")
    p2.text(100, 26, "Kleur de foto's, knip ze los en schuif ze in je fototoestel.", 6)
    gx, gy = 10, 34
    for k, fn in enumerate([ft_strand, ft_hond, ft_taart, ft_huis, ft_bloem, ft_leeg]):
        col, row = k % 3, k // 3; frame_at(p2, fn, gx + col * 60, gy + row * 96)
    for r in range(3): p2.seg(gx, gy + r * 96, gx + 180, gy + r * 96, "cut")
    for c in range(4): p2.seg(gx + c * 60, gy, gx + c * 60, gy + 192, "cut")
    p2.text(100, 240, "Schrijf onder elke foto wat erop staat.", 6)
    p2.legend(["cut"], 277)
    write(OUT, "papieren-fototoestel", sh, {"category": "thuis", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 30, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Papieren fototoestel met foto's", "printNote": "Print blad 1 het liefst op stevig papier; de foto's op blad 2 mogen op gewoon papier.", "steps": [
            "Kleur het fototoestel en de foto's op blad 2 in.",
            "Knip het fototoestel uit langs de streepjeslijn.",
            "Vouw de twee grijze flapjes naar achteren, naar de witte kant van het papier, en smeer er lijm op.",
            "Vouw de achterkant op de lange vouwlijn naar achteren, achter de voorkant, en druk de flapjes goed aan. Onderaan blijft het toestel open.",
            "Knip de foto's los en schuif ze van onderen in het toestel, met de plaatjes naar voren. De witte rand blijft eronder uitsteken.",
            "Richt je toestel, zeg 'klik!' en trek een foto tevoorschijn. Op de lege foto teken je zelf iets."]}}},
        [("extra", "Foto's", p2)])
fototoestel()

# =====================================================================
# Draaischijf: wat eten we vandaag?
# =====================================================================
def m_pannenkoek(p):
    for y in (8, 3, -2, -7): p.add(ellp(0, y, 15, 4.5), "y")
    p.add(sample("M-6 -10C-2 -12 6 -12 8 -8L9 -2C8 0 7 0 7 -2L6 -6Q0 -6 -6 -7Z"), "w")
    p.add(rect(-2, -16, 4, 4), "-") if False else p.add(rrect(-3, -14, 6, 4, 1), "y")
def m_pizza(p): wrap(ic_pizza, .9, -20, -20)(p)
def m_spaghetti(p):
    p.add(ellp(0, 4, 16, 9), "-"); p.add(ellp(0, 2, 11, 5.5), "y", sil=False)
    for k in range(4): p.ln(sample(f"M{-9 + k * 4} 0Q{-7 + k * 4} -3 {-5 + k * 4} 1Q{-3 + k * 4} 4 {-1 + k * 4} 0", 6), style="stroke-width:1")
    for x, y in [(-4, -1), (4, 3)]: p.add(circ(x, y, 2.6), "w", sil=False)
    p.add(bar(10, -2, 15, -14, .8), "z")
def m_soep(p):
    p.add(sample("M-15 -2H15C15 9 8 14 0 14C-8 14 -15 9 -15 -2Z"), "o"); p.add(ellp(0, -2, 15, 3), "y")
    p.add(bar(6, -3, 16, -13, 1.4), "z"); p.add(ellp(3, -1, 4, 2.2, -45), "z")
def m_patat(p):
    for k, x in enumerate((-7, -3, 1, 5, 9)): p.add(rect(x - 1.6, -16 + (k % 2) * 3, 3.2, 14), "y")
    p.add(sample("M-11 -4H11L8 15H-8Z"), "r"); p.add(sample("M-5 3Q0 0 5 3", 4) + [(5, 6), (-5, 6)], "y", sil=False)
def m_zelf(p): p.add(circ(0, 0, 14), "-"); p.text(0, 6, "?", 16)
def eetschijf():
    sh = Sheet(); head(sh, "Wat eten we vandaag?")
    bx, by, BR = 66, 92, 62
    tx, ty, TR = 134, 206, 57
    MR, WR = 34, 15
    sh.circle_r(bx, by, BR, "-")
    for k in range(6): sh.seg(bx + 21 * math.cos(math.radians(k * 60)), by + 21 * math.sin(math.radians(k * 60)), bx + BR * math.cos(math.radians(k * 60)), by + BR * math.sin(math.radians(k * 60)), "l", "stroke-width:.8")
    meals = [m_pannenkoek, m_pizza, m_spaghetti, m_soep, m_patat, m_zelf]
    for k, fn in enumerate(meals):
        a = -90 + 30 + k * 60
        sh.raw(f'<g transform="rotate({a + 90} {bx} {by})">'); put(sh, fn, bx, by - MR, 1); sh.raw("</g>")
    sh.circle_line(bx, by, BR + 3, "cut"); sh.circle_line(bx, by, 1.8, "cut")
    sh.text(bx, by + BR + 11, "onderste schijf", 5.5, cls="tip")
    # bovenste schijf
    sh.circle_r(tx, ty, TR, "-")
    for k in range(20): sh.region(arc_path(tx, ty, TR - 7, TR, k * 18 - 90, (k + 1) * 18 - 90), "r" if k % 2 == 0 else "-")
    sh.circle_r(tx, ty - MR, WR + 5, "-")
    sh.raw(f'<circle class="cut" cx="{tx}" cy="{ty - MR}" r="{WR}" fill="none"/>')
    for s in (-1, 1):
        fx = tx + s * 34; y1 = ty - 14
        if s < 0:
            sh.rect_r(fx - 1.5, y1 + 12, 3, 22, "z"); sh.region(f"M{fx - 4} {y1}V{y1 + 8}Q{fx} {y1 + 14} {fx + 4} {y1 + 8}V{y1}Z", "z")
            for d in (-1.5, 1.5): sh.seg(fx + d, y1, fx + d, y1 + 6, "l", "stroke-width:.8")
        else:
            sh.rect_r(fx - 1.5, y1 + 14, 3, 20, "z"); sh.region(f"M{fx - 1.5} {y1 + 14}V{y1}Q{fx + 5} {y1 + 4} {fx + 2} {y1 + 14}Z", "z")
    sh.text(tx, ty + 14, "Wat eten", 8); sh.text(tx, ty + 24, "we vandaag?", 8)
    sh.circle_r(tx, ty, 4, "x"); sh.circle_line(tx, ty, 1.8, "cut")
    sh.circle_line(tx, ty, TR + 3, "cut")
    sh.text(tx, ty + TR + 10, "bovenste schijf: knip ook het bordje uit", 5.5, cls="tip")
    for i, t in enumerate(["Draai de", "onderste schijf", "en kijk wat er", "op je bord", "komt!"]): sh.text(164, 48 + i * 9, t, 6.5)
    for i, t in enumerate(["Op het vraagteken", "mag jij kiezen", "wat jullie eten."]): sh.text(36, 196 + i * 9, t, 6)
    sh.legend(["cut"], 277)
    write(OUT, "draaischijf-wat-eten-we-vandaag", sh, {"category": "eten", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, SPLIT, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Draaischijf: wat eten we vandaag?", "printNote": "Op stevig papier draait de schijf het mooist.", "steps": [
            "Kleur de zes gerechten op de onderste schijf en het tafelkleed en bestek op de bovenste schijf in.",
            "Knip beide schijven uit langs de streepjeslijn. Een volwassene knipt het rondje van het bordje uit de bovenste schijf.",
            "Prik een gaatje in het midden van allebei de schijven. Leg de bovenste schijf op de onderste en steek een splitpen door de gaatjes. Buig de pootjes aan de achterkant open, niet te strak.",
            "Draai aan de onderste schijf: welk eten komt er op je bord? Kies samen wat jullie vandaag eten."]}}})
eetschijf()

# =====================================================================
# Vouwboekje van één vel: wie woont waar?
# =====================================================================
PW, PH = 61.5, 90
def bk_text(p, *lines):
    for i, t in enumerate(lines): p.text(PW / 2, 72 + i * 8, t, 5.6)
def bk_voor(p):
    p.text(PW / 2, 18, "Wie woont", 8.5); p.text(PW / 2, 28, "waar?", 8.5)
    put(p.sh, st_huis, PW / 2, 66, .62)
def bk_vogel(p):
    p.add(rect(0, 44, 40, 5), "w"); p.add(sample("M12 44H40C39 52 32 55 26 55C20 55 13 52 12 44Z"), "w")
    put(p.sh, ic_vogel, 10, 6, .85)
    bk_text(p, "De vogel woont", "in een nest.")
def bk_konijn(p):
    p.add(sample("M0 62C6 36 26 26 46 30C56 32 61.5 40 61.5 46V62Z"), "l"); p.add(ellp(44, 52, 9, 6), "x")
    put(p.sh, bs_konijn, 20, 46, .55)
    bk_text(p, "Het konijn woont", "in een hol.")
def bk_bij(p):
    p.add(rect(34, 10, 3, 8), "w")
    p.add(sample("M16 60C14 40 20 18 36 18C52 18 58 40 56 60Z"), "y")
    for y in (26, 34, 42, 50): p.ln([(36 - (y - 12) * .8, y), (36 + (y - 12) * .8, y)] if False else sample(f"M{17 + (60 - y) * .04} {y}Q36 {y + 3} {55 - (60 - y) * .04} {y}", 6), style="stroke-width:1")
    p.add(ellp(36, 54, 4, 4.5), "x")
    put(p.sh, ic_bij, -2, 4, .45); put(p.sh, ic_bij, 0, 30, .4)
    bk_text(p, "De bij woont", "in een korf.")
def bk_vis(p):
    p.add(sample("M0 18Q8 14 15 18Q23 22 31 18Q38 14 46 18Q54 22 61.5 18V62H0Z"), "b")
    put(p.sh, ic_vis, 10, 22, 1.1)
    for x, y in [(50, 30), (53, 24)]: p.add(circ(x, y, 2), "-")
    bk_text(p, "De vis woont", "in het water.")
def bk_spin(p):
    cx, cy = 30, 34
    for k in range(8):
        t = math.radians(k * 45); p.ln([(cx, cy), (cx + 26 * math.cos(t), cy + 26 * math.sin(t))], style="stroke-width:.9")
    for r in (8, 15, 22): p.ln([(cx + r * math.cos(math.radians(k * 45)), cy + r * math.sin(math.radians(k * 45))) for k in range(9)], style="stroke-width:.9")
    for s in (-1, 1):
        for k in range(4): p.ln(sample(f"M{cx + 10} {cy + 4}Q{cx + 10 + s * 6} {cy + 4 - 4 + k * 3} {cx + 10 + s * 9} {cy + 4 + k * 3}", 4), style="stroke-width:1.2")
    p.add(circ(cx + 10, cy + 4, 4.5), "x"); p.add(circ(cx + 10, cy - 1, 2.6), "x")
    bk_text(p, "De spin woont", "in een web.")
def bk_jij(p):
    p.add(rrect(6, 8, PW - 12, 54, 3), "-")
    p.text(PW / 2, 36, "teken hier", 5, cls="tip")
    bk_text(p, "En waar woon jij?", "Teken je huis!")
def bk_achter(p):
    p.text(PW / 2, 30, "Gemaakt door:", 6.5)
    p.ln([(8, 44), (PW - 8, 44)], style="stroke-width:.8"); p.ln([(8, 58), (PW - 8, 58)], style="stroke-width:.8")
    p.add(star_pts(PW / 2, 74, 7, 3), "y")
def vouwboekje():
    sh = Sheet(); head(sh, "Vouwboekje: wie woont waar?", 10)
    X0, Y0 = 12, 10  # liggende coördinaten; met rotate(-90) wordt (X, Y) -> (Y, 280 - X)
    order = {1: bk_voor, 2: bk_vogel, 3: bk_konijn, 4: bk_bij, 5: bk_vis, 6: bk_spin, 7: bk_jij, 8: bk_achter}
    slots = {(0, 0): 5, (1, 0): 4, (2, 0): 3, (3, 0): 2, (0, 1): 6, (1, 1): 7, (2, 1): 8, (3, 1): 1}
    sh.raw('<g transform="translate(0 280) rotate(-90)">')
    for (c, r), n in slots.items():
        x, y = X0 + c * PW, Y0 + r * PH
        rot = f' rotate(180 {f(PW / 2)} {f(PH / 2)})' if r == 0 else ""
        sh.raw(f'<g transform="translate({f(x)} {f(y)}){rot}">'); order[n](Pc(sh))
        if n not in (1, 8): sh.text(PW / 2, PH - 2, str(n), 5, cls="tip")
        sh.raw("</g>")
    W4, H2 = 4 * PW, 2 * PH
    sh.rect_line(X0, Y0, W4, H2, "cut")
    for c in (1, 2, 3): sh.seg(X0 + c * PW, Y0, X0 + c * PW, Y0 + H2, "fold")
    sh.seg(X0, Y0 + PH, X0 + PW, Y0 + PH, "fold"); sh.seg(X0 + 3 * PW, Y0 + PH, X0 + W4, Y0 + PH, "fold")
    sh.seg(X0 + PW, Y0 + PH, X0 + 3 * PW, Y0 + PH, "cut", "stroke-width:1.6")
    sh.raw("</g>")
    sh.legend(["cut", "fold"], 277)
    write(OUT, "vouwboekje-wie-woont-waar", sh, {"category": "dieren", "age": "4-6", "kind": "vouwblad", "difficulty": 2, "minutes": 25, "adultHelp": True,
        "materials": [KLEUR, SCHAAR],
        "i18n": {"nl": {"name": "Vouwboekje: wie woont waar?", "printNote": "Gewoon printpapier werkt het best: dan vouwt het boekje makkelijk.", "steps": [
            "Kleur alle plaatjes in. Sommige staan op hun kop: dat hoort zo.",
            "Knip langs de buitenste streepjeslijn de witte rand eraf.",
            "Vouw het vel op alle stippellijnen heen en weer, zodat je acht vakjes ziet. Vouw het weer open.",
            "Vouw het vel dubbel over de lange middellijn, met de tekeningen aan de buitenkant. Een volwassene knipt de dikke streepjeslijn in het midden in, vanaf de vouw tot aan het volgende vakje.",
            "Pak de twee uiteinden vast en duw ze naar elkaar toe. Het gat in het midden gaat open en er ontstaan vier flappen.",
            "Vouw de flappen plat tot een boekje met de voorkant 'Wie woont waar?' bovenop. Lees het boekje voor en teken op bladzijde 7 je eigen huis."]}}})
vouwboekje()

# =====================================================================
# Geheime vouwbrief
# =====================================================================
def vouwbrief():
    sh = Sheet(); head(sh, "Geheime vouwbrief")
    x0, y0, S_ = 15, 26, 170; cx, cy = x0 + S_ / 2, y0 + S_ / 2
    T_, R_, B_, L_ = (cx, y0), (x0 + S_, cy), (cx, y0 + S_), (x0, cy)
    corners = [((x0, y0), -45), ((x0 + S_, y0), 45), ((x0 + S_, y0 + S_), 135), ((x0, y0 + S_), -135)]
    for k, ((qx, qy), ang) in enumerate(corners):
        mx, my = qx + (cx - qx) * .3, qy + (cy - qy) * .3
        sh.raw(f'<g transform="rotate({ang + 180 if False else ang} {f(mx)} {f(my)})">')
        sh.text(mx, my + 2, "Geheim!", 7)
        sh.raw("</g>")
        for j, (dx, dy) in enumerate([(.14, .07), (.07, .14)]):
            px, py = qx + (cx - qx) * dx * 2.2, qy + (cy - qy) * dy * 2.2
            sh.region(heart_path(px, py, 4.5), "m") if (k + j) % 2 == 0 else sh.poly_r(star_pts(px, py, 5, 2.1), "y")
    sh.text(cx, y0 + 46, "Geheime brief", 7); sh.text(cx, y0 + 55, "voor: ...............", 6)
    for y in range(int(y0 + 68), int(y0 + 132), 10):
        hw = (S_ / 2) - abs(y - cy) - 8
        sh.seg(cx - hw, y, cx + hw, y, "l", "stroke-width:.6")
    sh.text(cx, y0 + 142, "van: ...............", 6)
    sh.rect_line(x0, y0, S_, S_, "cut")
    sh.line(f"M{T_[0]} {T_[1]}L{R_[0]} {R_[1]}L{B_[0]} {B_[1]}L{L_[0]} {L_[1]}Z", "fold")
    # zegels
    sh.text(100, 212, "Zegels: knip er een uit om je brief dicht te plakken.", 6)
    for k, x in enumerate((60, 100, 140)):
        sh.circle_r(x, 236, 12, "r" if k != 1 else "y")
        if k == 0: sh.region(heart_path(x, 236, 7), "-")
        elif k == 1: sh.poly_r(star_pts(x, 237, 8, 3.4), "-")
        else: sh.circle_r(x, 233, 3.2, "-"); sh.poly_r([(x - 2, 235), (x + 2, 235), (x + 3, 242), (x - 3, 242)], "-")
        sh.circle_line(x, 236, 14.5, "cut")
    sh.legend(["cut", "fold"], 277)
    write(OUT, "geheime-vouwbrief", sh, {"category": "thuis", "age": "6-9", "kind": "vouwblad", "difficulty": 1, "minutes": 15,
        "materials": [SCHAAR, {"slug": "potlood"}, KLEUR, LIJM],
        "i18n": {"nl": {"name": "Geheime vouwbrief met zegel", "steps": [
            "Knip het grote vierkant en de drie zegels uit langs de streepjeslijn.",
            "Schrijf je geheime boodschap op de lijntjes in het midden. Vul in voor wie de brief is en van wie.",
            "Kleur de hoeken in en vouw dan de vier hoeken naar het midden, op de schuine stippellijnen. De punten raken elkaar in het midden.",
            "Plak een zegel op de plek waar de punten samenkomen, zodat de brief dicht blijft.",
            "Schrijf op de buitenkant voor wie de brief is en geef hem stiekem aan die persoon!"]}}})
vouwbrief()
