"""Batch 7b: knip-, plak- en knutselbladen (knipplaat) en vouwbladen (vouwblad), A4."""
import math, re, random
from lib_gen import *
from shapes import heart_path

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
    if y > 270: print("LET OP: flow loopt over de rand", y)
    return y

def ept(cx, cy, rx, ry, a):
    t = math.radians(a); return (cx + rx * math.cos(t), cy + ry * math.sin(t))

def head(sh, t, size=11):
    title(sh, t, 15, size)

# =====================================================================
# Aankleedfiguren (beer en hond) met eigen kleren en flapjes
# =====================================================================
BODY = (55, 132, 30, 44)  # romp-ellips
HEAD = (55, 64, 22)

def doll(pc, kind):
    bx, by, brx, bry = BODY; hx, hy, hr = HEAD
    fur = "w" if kind == "beer" else "o"
    pc.add(rect(28, 219, 54, 24), "l")
    pc.ln([(28, 219), (82, 219)], cls="fold")
    for x in (43, 67): pc.add(ellp(x, 194, 12, 22), fur)
    for x in (42, 68): pc.add(ellp(x, 212, 14, 8), fur)
    pc.add(ellp(28, 120, 9, 27, 20), fur); pc.add(ellp(82, 120, 9, 27, -20), fur)
    pc.add(ellp(bx, by, brx, bry), fur)
    pc.add(ellp(bx, 140, 17, 25), "-" if kind == "beer" else "y")
    if kind == "beer":
        for x in (37, 73): pc.add(circ(x, 44, 9), fur); pc.add(circ(x, 44, 4.5), "k", sil=False)
    pc.add(circ(hx, hy, hr), fur)
    if kind == "hond":
        pc.add(ellp(32, 70, 8, 17, 18), "w"); pc.add(ellp(78, 70, 8, 17, -18), "w")
    pc.add(ellp(55, 73, 10, 7.5), "-")
    pc.add(ellp(55, 68, 4, 3), "x")
    pc.dot(47, 59, 2.4); pc.dot(63, 59, 2.4)
    pc.ln([(55, 71), (55, 75)]); pc.ln(sample("M49 75Q55 80 61 75", 6))
    for x in (42, 68): pc.ln([(x - 4, 216), (x - 4, 219)], style="stroke-width:1"); pc.ln([(x + 4, 216), (x + 4, 219)], style="stroke-width:1")

def coat_body(bottom=178, collar=True):
    bx, by, brx, bry = BODY
    top = ellp(bx, by, brx + 1.5, bry + 1.5, a0=180, a1=360, n=60)
    return top + [(bx + brx + 1.5, by + 8), (bx + brx + 2, bottom - 8), (bx + brx - 2, bottom), (bx - brx + 2, bottom), (bx - brx - 2, bottom - 8), (bx - brx - 1.5, by + 8)]
def shoulder_tabs(pc):
    bx, by, brx, bry = BODY
    for a1, a2 in [(236, 250), (290, 304)]:
        pc.tab(ept(bx, by, brx + 1.5, bry + 1.5, a1), ept(bx, by, brx + 1.5, bry + 1.5, a2), 6, (bx, by))
def side_tabs(pc, a_list):
    bx, by, brx, bry = BODY
    for a1, a2 in a_list:
        pc.tab(ept(bx, by, brx + 1.5, bry + 1.5, a1), ept(bx, by, brx + 1.5, bry + 1.5, a2), 6, (bx, by))
def sleeves(pc, code, short=False):
    if short:
        pc.add(ellp(34, 104, 10, 13, 35), code); pc.add(ellp(76, 104, 10, 13, -35), code)
    else:
        pc.add(ellp(28, 120, 11, 29, 20), code); pc.add(ellp(82, 120, 11, 29, -20), code)
        for s in (-1, 1):
            cx = 55 + s * 27; pc.add(ellp(55 + s * (27 + 9.2 * .34), 120 + 26 * .94, 9.5, 3.5, -20 * s), "-")

def head_tabs(pc, y1, y2):
    hx, hy, hr = HEAD
    for s in (-1, 1):
        p1 = (hx + s * math.sqrt(hr * hr - (y1 - hy) ** 2), y1); p2 = (hx + s * math.sqrt(hr * hr - (y2 - hy) ** 2), y2)
        pc.tab(p1, p2, 6, (hx, hy))

# ---- kledingstukken (coördinaten op de pop) ----
def muts(pc):
    head_tabs(pc, 51, 59)
    pc.add(sample("M33.5 52C33 38 44 31 55 31C66 31 77 38 76.5 52Z"), "b")
    pc.add(rrect(32.5, 50, 45, 10, 3), "n")
    pc.add(circ(55, 29, 6.5), "y")
    for x in (44, 55, 66): pc.ln(sample(f"M{x} 50Q{x + 2} 41 {x + 1} 33", 6) if x != 55 else [(55, 36), (55, 50)])
def sjaal(pc):
    pc.tab((44, 87.5), (44, 95.5), 6, (55, 92)); pc.tab((66, 87.5), (66, 95.5), 6, (55, 92))
    pc.add(rect(56, 92, 11, 30), "r")
    pc.add(rrect(43, 86, 24, 11, 4), "r")
    for y in (100, 108): pc.ln([(56, y), (67, y)])
    for x in (58, 61.5, 65): pc.ln([(x, 122), (x, 127)])
    pc.sil(rect(56, 122, 11, 5))
def winterjas(pc):
    shoulder_tabs(pc)
    sleeves(pc, "g")
    bx, by, brx, bry = BODY
    pc.add(coat_body(178), "g")
    pc.add(sample("M46 90L55 104L64 90Q55 86 46 90Z"), "-")
    pc.ln([(55, 104), (55, 178)])
    for y in (118, 136, 154): pc.add(circ(59.5, y, 2.2), "y", sil=False)
    for x in (34, 66): pc.ln([(x, 150), (x + 10, 150)])
def laars(pc, x, code="w", rain=False):
    s = -1 if x < 55 else 1
    pc.tab((x + s * 12, 197), (x + s * 12, 205), 6, (x, 200))
    pc.add(rect(x - 12, 194, 24, 18), code)
    pc.add(ellp(x - s * 1, 213, 15, 9), code)
    if not rain: pc.add(rrect(x - 13.5, 191, 27, 7, 3), "-")
    else: pc.ln([(x - 12, 200), (x + 12, 200)])
def zonnehoed(pc):
    pc.add(sample("M38 47C38 34 45 30 55 30C65 30 72 34 72 47Z"), "y")
    pc.add(ellp(55, 48, 28, 6.5), "y")
    pc.add(rect(38.5, 40, 33, 6), "r", sil=False)
    for s in (-1, 1): pc.tab((55 + s * 27.6, 46), (55 + s * 27.6, 51), 5, (55, 48))
def zonnebril(pc):
    for s in (-1, 1):
        pc.add(bar(55 + s * 13, 58, 55 + s * 21.3, 58, 1.5), "x")
        pc.tab((55 + s * 21.3, 56.2), (55 + s * 21.3, 59.8), 5, (55, 58))
    pc.add(bar(51, 57, 59, 57, 1.3), "x")
    pc.add(ellp(47, 59, 7.5, 6), "n"); pc.add(ellp(63, 59, 7.5, 6), "n")
def tshirt(pc, code="m"):
    shoulder_tabs(pc)
    sleeves(pc, code, short=True)
    bx, by, brx, bry = BODY
    pc.add(coat_body(146), code)
    pc.add(sample("M46 90Q55 100 64 90Q55 86 46 90Z"), "-")
    pc.add(star_pts(55, 122, 9, 4), "y", sil=False)
def korte_broek(pc, code="n"):
    side_tabs(pc, [(162, 172), (8, 18)])
    bx, by, brx, bry = BODY
    pc.add(sample("M25.2 146C24 160 28 178 30 190L52 190L55 172L58 190L80 190C82 178 86 160 84.8 146Z"), code)
    pc.ln([(26, 152), (84, 152)])
    pc.add(rect(52, 146, 6, 6), "-", sil=False)
def regenjas(pc):
    shoulder_tabs(pc)
    sleeves(pc, "y")
    pc.add(coat_body(192), "y")
    pc.add(sample("M46 90L55 102L64 90Q55 86 46 90Z"), "-")
    pc.ln([(55, 102), (55, 192)])
    for y in (116, 134, 152, 170): pc.add(rrect(50, y - 1.5, 7, 3, 1.5), "w", sil=False)
    for x in (32, 68): pc.ln([(x, 160), (x + 10, 160), (x + 10, 168)])
# beroepen
def koksmuts(pc):
    head_tabs(pc, 50, 58)
    pc.add(sample("M36 50C24 44 26 20 40 22C40 10 70 10 70 22C84 20 86 44 74 50Z"), "-")
    pc.add(rrect(35, 46, 40, 12, 2), "-")
    for x in (46, 55, 64): pc.ln(sample(f"M{x} 46Q{x - 2} 34 {x} 24", 6))
def schort(pc):
    side_tabs(pc, [(176, 186), (354, 364)])
    pc.add(sample("M44 104L66 104L66 134L84 134C86 150 84 170 78 182L32 182C26 170 24 150 26 134L44 134Z"), "b")
    pc.add(rrect(46, 144, 18, 14, 2), "-", sil=False)
    for x in (37, 47, 57, 67): pc.add(circ(x + 3, 170, 2.5), "r", sil=False)
def brandweerhelm(pc):
    head_tabs(pc, 50, 58)
    pc.add(sample("M33 52C33 30 45 24 55 24C65 24 77 30 77 52Z"), "r")
    pc.add(sample("M28 52Q55 60 82 52L82 56Q55 64 28 56Z"), "r")
    pc.add(sample("M50 26L60 26L58 44L52 44Z"), "y")
    pc.add(star_pts(55, 36, 5, 2.2), "-", sil=False)
def brandweerjas(pc):
    shoulder_tabs(pc)
    sleeves(pc, "n")
    pc.add(coat_body(184), "n")
    pc.add(sample("M46 90L55 102L64 90Q55 86 46 90Z"), "-")
    for y in (150, 166):
        pc.add(rect(26, y, 58, 6), "y", sil=False)
    pc.ln([(55, 102), (55, 150)]); pc.ln([(55, 172), (55, 184)])
def doktersjas(pc):
    shoulder_tabs(pc)
    sleeves(pc, "-")
    pc.add(coat_body(190), "-")
    pc.add(sample("M46 90L52 112L55 100L58 112L64 90Q55 86 46 90Z"), "t")
    pc.ln([(55, 112), (55, 190)])
    pc.ln(sample("M47 92C40 110 44 124 50 128C54 130 58 130 62 126", 10), style="stroke-width:1.4")
    pc.add(circ(62, 126, 3.2), "z", sil=False)
    pc.add(rect(64, 108, 12, 9), "-", sil=False); pc.ln([(66, 104), (66, 110)]); pc.add(rect(65, 102, 2, 4), "r", sil=False)
    for y in (122, 140, 158): pc.dot(57.5, y, 1.5)
def bouwhelm(pc):
    head_tabs(pc, 50, 58)
    pc.add(sample("M33 50C33 32 44 26 55 26C66 26 77 32 77 50Z"), "y")
    pc.add(rrect(29, 48, 52, 8, 3), "y")
    pc.add(rect(51, 27, 8, 21), "o", sil=False)
def hesje(pc):
    shoulder_tabs(pc)
    pc.add(coat_body(176), "o")
    pc.add(sample("M44 89L55 116L66 89Q74 92 72 104L72 176L38 176L38 104Q36 92 44 89Z"), "-")
    pc.add(sample("M38 104Q36 92 44 89L50 102L44 104Z"), "o", sil=False)
    pc.add(sample("M72 104Q74 92 66 89L60 102L66 104Z"), "o", sil=False)
    for y in (136, 156):
        pc.add(rect(25, y, 13, 6), "y", sil=False); pc.add(rect(72, y, 13, 6), "y", sil=False)

def aankleed(slug, name, kind, p1items, p2items, cat, intro2, steps_extra):
    sh = Sheet()
    head(sh, name.split(": ")[0])
    place(sh, lambda pc: doll(pc, kind), 4, 26)
    for fn, x, y in p1items: place(sh, fn, x, y)
    sh.legend(["cut", "fold"], 276)
    p2 = Sheet()
    head(p2, intro2)
    for fn, x, y in p2items: place(p2, fn, x, y)
    p2.legend(["cut", "fold"], 276)
    write(OUT, slug, sh, {"category": cat, "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 40, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier (160 gram), dan blijft de pop beter staan en gaan de flapjes minder snel stuk.", "steps": [
            "Kleur de " + ("beer" if kind == "beer" else "hond") + " en alle kleren in.",
            "Knip alles uit langs de streepjeslijn. Knip de witte flapjes niet af: die heb je nodig.",
            "Vouw het grasstrookje onder de voeten naar achteren, dan blijft de " + ("beer" if kind == "beer" else "hond") + " staan.",
            "Leg een kledingstuk op de " + ("beer" if kind == "beer" else "hond") + " en vouw de witte flapjes om de rand naar achteren. Zo blijft het zitten.",
        ] + steps_extra}}}, [("extra", intro2, p2)])

def L(fn, *a): return lambda pc: fn(pc, *a)
aankleed("aankleedbeer-seizoenen", "Aankleedbeer: winter, zomer en regen", "beer",
    [(muts, 98, 26), (sjaal, 156, 24), (winterjas, 98, 80), (L(laars, 42), 104, 196), (L(laars, 68), 150, 196)],
    [(tshirt, 6, 26), (regenjas, 6, 100), (zonnehoed, 108, 26), (zonnebril, 114, 64), (korte_broek, 110, 86), (L(laars, 42, "y", True), 104, 150), (L(laars, 68, "y", True), 150, 150)],
    "dieren", "Zomer- en regenkleren", ["Wat trekt de beer vandaag aan? Kijk naar buiten en kies kleren die bij het weer passen."])
aankleed("aankleedhond-beroepen", "Aankleedhond: wat wil jij worden?", "hond",
    [(koksmuts, 106, 26), (schort, 104, 76), (brandweerhelm, 104, 190)],
    [(brandweerjas, 6, 26), (doktersjas, 6, 146), (bouwhelm, 112, 26), (hesje, 108, 70)],
    "beroepen", "Nog meer werkkleren", ["Kies een beroep: kok, brandweer, bouwvakker of dokter. Welke kleren horen erbij?"])

# =====================================================================
# Knip-en-plak-collages: een knipvel met losse stukjes en een plakvel
# =====================================================================
def collage(slug, name, heading, pieces_page, glue_page, cat, age, steps, minutes=30, holiday=None, diff=2):
    sh = Sheet(); head(sh, heading)
    pieces_page(sh); sh.legend(["cut"], 276)
    pv = Sheet(); glue_page(pv)
    meta = {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": minutes,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": name, "printNote": "Print beide pagina's: de eerste is het knipvel, de tweede het plakvel.", "steps": steps}}}
    if holiday: meta["holiday"] = holiday
    write(OUT, slug, sh, meta, [("extra", "Plakvel", pv)])

# ---------- gezicht ----------
FX, FY, FRX, FRY = 100, 140, 44, 56
def eye_round(pc):
    pc.add(circ(0, 0, 9), "-"); pc.add(circ(1, 1, 4.6), "n"); pc.dot(1, 1, 2)
def eye_almond(pc):
    pc.add(sample("M-12 0Q0 -10 12 0Q0 10 -12 0Z"), "-"); pc.add(circ(0, 0, 4.4), "g"); pc.dot(0, 0, 1.9)
def eye_sleepy(pc):
    pc.add(sample("M-11 0Q0 11 11 0Z"), "-")
    pc.ln(sample("M-11 0Q0 11 11 0", 8))
    for x in (-7, 0, 7):
        b = bar(x, 7 if x == 0 else 5, x * 1.4, 11.5 if x == 0 else 9.5, .6); pc.sil(b); pc.ln([(x, 7 if x == 0 else 5), (x * 1.4, 11.5 if x == 0 else 9.5)], style="stroke-width:1.4")
def nose_round(pc): pc.add(circ(0, 0, 7), "k")
def nose_tri(pc): pc.add(sample("M0 -10Q2 0 7 6Q0 9 -7 6Q-2 0 0 -10Z"), "o")
def nose_carrot(pc):
    pc.add(sample("M-4 -6L22 0L-4 6Z"), "o")
    for x in (3, 10): pc.ln([(x, -3.5 + x * .15), (x + 1.5, 0)])
def mouth_smile(pc): pc.add(sample("M-18 0Q0 18 18 0Q0 8 -18 0Z"), "r")
def mouth_open(pc):
    pc.add(ellp(0, 0, 12, 9), "x"); pc.add(sample("M-7 4Q0 -2 7 4Q4 8 0 8Q-4 8 -7 4Z"), "m", sil=False)
def mouth_teeth(pc):
    pc.add(sample("M-16 -4H16Q14 12 0 12Q-14 12 -16 -4Z"), "-")
    pc.ln([(-15, 2.5), (15, 2.5)])
    for x in (-8, 0, 8): pc.ln([(x, -4), (x, 2.5)])
def ear(pc, s=1):
    pc.add(ellp(0, 0, 9, 15, a0=90, a1=270) if s > 0 else ellp(0, 0, 9, 15, a0=-90, a1=90), "-")
    pc.ln(sample(f"M0 -8Q{-6 * s} -6 {-5 * s} 0Q{-4 * s} 6 0 8", 8), style="stroke-width:1.6")
def brow(pc): pc.add(sample("M-12 3Q0 -8 12 3L12 6.5Q0 -3 -12 6.5Z"), "w")
def cheek(pc): pc.add(circ(0, 0, 6.5), "k")
def snor(pc): pc.add(sample("M0 -2C6 -8 16 -6 20 2C14 -1 8 6 0 2C-8 6 -14 -1 -20 2C-16 -6 -6 -8 0 -2Z"), "w")
def strik(pc):
    pc.add(sample("M0 0L-18 -10L-18 10Z"), "r"); pc.add(sample("M0 0L18 -10L18 10Z"), "r")
    pc.add(rrect(-4, -5, 8, 10, 2), "r")
    for x, y in [(-12, -2), (-10, 4), (12, -2), (10, 4)]: pc.dot(x, y, 1.2)
def hair_cap():
    return ellp(FX, FY, FRX + 3, FRY + 3, a0=180, a1=360, n=60) + sample(f"M{FX + FRX + 3} {FY + 4}L{FX + FRX - 9} {FY + 4}Q{FX + FRX - 10} {FY - 36} {FX + 26} {FY - 40}Q{FX + 12} {FY - 32} {FX} {FY - 44}Q{FX - 12} {FY - 32} {FX - 26} {FY - 40}Q{FX - FRX + 10} {FY - 36} {FX - FRX + 9} {FY + 4}L{FX - FRX - 3} {FY + 4}", 8)
def hair_curls(pc):
    for a in range(170, 375, 14):
        x, y = ept(FX, FY, FRX + 2, FRY + 2, a); pc.add(circ(x, y, 11), "w")
    pc.add(hair_cap(), "w")
def hair_spikes(pc):
    for k, a in enumerate(range(185, 360, 15)):
        x, y = ept(FX, FY, FRX, FRY, a); xo, yo = ept(FX, FY, FRX + 12, FRY + 12, a + 3)
        x1, y1 = ept(FX, FY, FRX, FRY, a - 9); x2, y2 = ept(FX, FY, FRX, FRY, a + 9)
        pc.add([(x1, y1), (xo, yo), (x2, y2)], "y")
    pc.add(hair_cap(), "y")
def two(fn): return [fn, fn]
def gezicht_knip(sh):
    sh.text(100, 25, "Kleur de stukjes, knip ze uit en maak een grappig gezicht.", 6)
    y1 = flow(sh, [hair_curls, hair_spikes], 2, 28, 122, 2)
    y2 = flow(sh, [L(ear, 1), L(ear, -1), snor, strik] + two(eye_round) + two(eye_almond) + two(eye_sleepy), 122, 28, 198, 1)
    flow(sh, [nose_round, nose_tri, nose_carrot, mouth_smile, mouth_open, mouth_teeth] + two(brow) + two(cheek), 2, max(y1, y2), 198, 1)
def gezicht_plak(sh):
    head(sh, "Plak een gezicht")
    sh.region(f"M36 280C36 236 70 220 100 220C130 220 164 236 164 280Z", "-")
    sh.rect_r(88, FY + FRY - 6, 24, 30, "-")
    sh.ellipse_r(FX, FY, FRX, FRY, "-")
    sh.text(100, 262, "Dit is: ..................................", 7)
codes_note = None
collage("plak-een-gezicht", "Plak een gezicht: knippen en plakken", "Gezicht: knipvel", gezicht_knip, gezicht_plak, "vormen", "4-6", [
    "Kleur alle stukjes in: haar, ogen, neus, mond en de rest.",
    "Knip de stukjes uit langs de streepjeslijn.",
    "Leg ze eerst los op het hoofd op het plakvel en probeer verschillende gezichten uit.",
    "Vind je hem mooi? Plak de stukjes vast met de lijmstift en geef je gezicht een naam."])

# ---------- aquarium ----------
def fish_a(pc, code="o"):
    pc.add(sample("M-20 0C-12 -12 6 -12 12 -2L22 -10L22 10L12 2C6 12 -12 12 -20 0Z"), code)
    pc.add(sample("M-4 -9Q2 -16 8 -8Z"), code); pc.dot(-12, -2, 1.8)
    pc.ln(sample("M-6 -7Q-2 0 -6 7", 6)); pc.ln(sample("M0 -8Q4 0 0 8", 6))
def fish_b(pc):
    pc.add(sample("M15 -4L26 -12L24 0L26 12L15 4Z"), "b")
    pc.add(ellp(0, 0, 17, 14), "t")
    for x in (-4, 4): pc.add(sample(f"M{x - 2} -13.5Q{x + 2} 0 {x - 2} 13.5L{x + 2} 13.5Q{x + 6} 0 {x + 2} -13.5Z"), "n", sil=False)
    pc.dot(-10, -3, 2); pc.ln(sample("M-16 4Q-13 6 -11 4", 4))
def fish_c(pc):
    pc.add(sample("M-26 0C-18 -8 10 -8 18 -2L28 -8L26 0L28 8L18 2C10 8 -18 8 -26 0Z"), "y")
    for x in (-12, -4, 4, 12): pc.add(circ(x, 0, 2.2), "r", sil=False)
    pc.dot(-19, -1, 1.5)
def pufferfish(pc):
    for k in range(12):
        a = math.radians(k * 30 + 15)
        pc.add([(14 * math.cos(a - .18), 14 * math.sin(a - .18)), (20 * math.cos(a), 20 * math.sin(a)), (14 * math.cos(a + .18), 14 * math.sin(a + .18))], "y")
    pc.add(circ(0, 0, 15), "l"); pc.add(circ(-5, -4, 4), "-", sil=False); pc.dot(-5, -4, 2); pc.add(circ(5, -4, 4), "-", sil=False); pc.dot(5, -4, 2)
    pc.add(ellp(0, 6, 3.5, 2.5), "r", sil=False)
def crab(pc):
    for s in (-1, 1):
        for k in range(3): pc.add(bar(s * 10, 4 + k * 3, s * 22, 10 + k * 4, 1.5), "r")
        pc.add(bar(s * 9, -2, s * 16, -12, 2), "r")
        pc.add(sample(f"M{s * 16} -10C{s * 8} -16 {s * 12} -24 {s * 18} -24C{s * 24} -24 {s * 26} -16 {s * 20} -12L{s * 17} -18Z"), "r")
        pc.add(bar(s * 4, -8, s * 6, -15, .9), "r"); pc.add(circ(s * 6, -16, 2.6), "-")
    pc.add(ellp(0, 2, 14, 10), "r"); pc.dot(-6, -16, 1.3); pc.dot(6, -16, 1.3)
    pc.ln(sample("M-5 5Q0 9 5 5", 4))
def starfish(pc):
    pc.add(star_pts(0, 0, 18, 8), "o")
    for k in range(5):
        a = math.radians(k * 72); pc.dot(9 * math.sin(a), -9 * math.cos(a), 1.2)
def shell(pc):
    pc.add(sample("M0 14L-16 -4C-14 -16 14 -16 16 -4Z"), "k")
    for x in (-10, -5, 0, 5, 10): pc.ln([(0, 14), (x * 1.3, -12 + abs(x) * .3)])
    pc.add(rrect(-5, 12, 10, 5, 2), "k")
def plant(pc, code="g"):
    pc.add(rect(-12, 50, 24, 6), "w")
    for x, h, b in [(-6, 54, -10), (0, 64, 8), (6, 48, 12)]:
        pc.add(sample(f"M{x - 3} 50C{x - 6 + b * .3} 30 {x + b} {50 - h * .6} {x + b * .5} {50 - h}C{x + b + 4} {50 - h * .6} {x + 4} 30 {x + 3} 50Z"), code)
def castle(pc):
    pc.add(rect(-14, -6, 28, 34), "z")
    pc.add(sample("M-14 -6V-14H-8V-9H-3V-14H3V-9H8V-14H14V-6Z"), "z")
    pc.add(sample("M-6 28V16Q0 8 6 16V28Z"), "x")
    pc.add(rect(-3, -1, 6, 7), "x", sil=False)
    for x, y in [(-10, 4), (8, 10), (-8, 20)]: pc.ln([(x, y), (x + 4, y)])
def snail(pc):
    pc.add(sample("M-18 8C-18 2 -14 0 -10 2L16 2C20 2 22 6 20 8Z"), "y")
    pc.add(bar(-14, 2, -18, -8, 1), "y"); pc.add(circ(-18, -9, 2), "y")
    pc.add(circ(4, -6, 11), "w")
    pc.ln(sample("M4 -6C8 -6 8 -12 3 -12C-3 -12 -4 -2 4 0C12 2 16 -10 10 -15", 10))
def aquarium_knip(sh):
    sh.text(100, 25, "Kleur de dieren en planten, knip ze uit en maak je eigen aquarium.", 6)
    y = flow(sh, [L(plant, "g"), S(L(plant, "l"), .9), S(castle, 1.2), S(crab, 1.2)], 2, 28, 198, 5)
    y = flow(sh, [S(L(fish_a, "o"), 1.4), S(fish_b, 1.3), fish_c], 2, y, 198, 3)
    y = flow(sh, [S(pufferfish, 1.2), S(L(fish_a, "r"), 1.1), S(snail, 1.3)], 2, y, 198, 5)
    flow(sh, [starfish, S(shell, 1.1), S(starfish, .9), S(shell, .9)], 2, y, 198, 6)
def aquarium_plak(sh):
    head(sh, "Mijn aquarium")
    x0, y0, w, h = 14, 46, 172, 196
    sh.rect_r(x0 - 4, y0 - 8, w + 8, 10, "z", 2)
    sh.region(f"M{x0} {y0 + 12}" + "".join(f"Q{x0 + k * 21.5 + 10.75} {y0 + (6 if k % 2 == 0 else 18)} {x0 + (k + 1) * 21.5} {y0 + 12}" for k in range(8)) + f"V{y0 + h - 30}H{x0}Z", "b")
    sh.region(f"M{x0} {y0 + h - 34}Q{x0 + 40} {y0 + h - 46} {x0 + 86} {y0 + h - 36}T{x0 + w} {y0 + h - 38}V{y0 + h}H{x0}Z", "y")
    for x, y in [(40, 238), (90, 228), (150, 236), (120, 232)]: sh.ellipse_r(x, y, 7, 4, "z")
    sh.rect_line(x0, y0, w, h, "l", 3)
    sh.rect_r(x0 + 10, y0 + h, w - 20, 22, "w", 2)
    sh.rect_r(x0 + 20, y0 + h + 4, w - 40, 14, "w", 2)
    for x, y, r in [(160, 160, 4), (166, 140, 3), (158, 122, 2.5), (40, 130, 3), (46, 112, 2.2)]: sh.circle_r(x, y, r, "-")
collage("aquarium-plakken", "Aquarium knippen en plakken", "Aquarium: knipvel", aquarium_knip, aquarium_plak, "zee", "4-6", [
    "Kleur de vissen, de krab, de planten en de andere stukjes in.",
    "Kleur op het plakvel het water blauw en het zand geel.",
    "Knip alle stukjes uit langs de streepjeslijn.",
    "Plak eerst de planten en het kasteeltje op het zand, daarna de dieren in het water. Klaar is je aquarium!"])

# ---------- huis van vormen ----------
HOUSE = {  # naam: (vorm, x, y, w, h, code)
    "muur": ("rect", 46, 132, 84, 72, "r"), "dak": ("tri", 36, 82, 104, 50, "w"), "deur": ("rect", 78, 162, 20, 42, "w"),
    "raam1": ("rect", 54, 144, 20, 20, "b"), "raam2": ("rect", 104, 144, 20, 20, "b"), "schoorsteen": ("rect", 108, 84, 12, 26, "z"),
    "stam": ("rect", 152, 156, 12, 48, "w"), "kruin": ("circ", 158, 136, 24, 0, "g"), "zon": ("circ", 32, 46, 15, 0, "y"),
}
def house_pts(k):
    kind, x, y, w, h, _ = HOUSE[k]
    if kind == "rect": return rect(x, y, w, h)
    if kind == "tri": return [(x, y + h), (x + w / 2, y), (x + w, y + h)]
    return circ(x, y, w)
def house_piece(k, label):
    def fn(pc):
        pts = house_pts(k); pc.add(pts, HOUSE[k][5])
        cx = sum(x for x, _ in pts) / len(pts); cy = sum(y for _, y in pts) / len(pts)
        if label: pc.text(cx, cy + (8 if k == "dak" else 2), label, 5, cls="tip")
    return fn
def huis_knip(sh):
    sh.text(100, 25, "Kleur de vormen, knip ze uit en bouw een huis op het plakvel.", 6)
    y = flow(sh, [house_piece("dak", "driehoek"), house_piece("muur", "rechthoek")], 4, 30, 196, 2)
    y = flow(sh, [house_piece("kruin", "cirkel"), house_piece("zon", "cirkel"), house_piece("stam", ""), house_piece("deur", ""), house_piece("schoorsteen", "")], 4, y + 2, 196, 6)
    flow(sh, [house_piece("raam1", ""), house_piece("raam2", "")], 4, y + 2, 196, 10)
def huis_plak(sh):
    head(sh, "Bouw een huis")
    sh.text(100, 26, "Plak elke vorm op het grijze lijntje dat erbij past.", 6.5)
    sh.region("M0 280V204Q50 198 100 204T200 204V280Z", "l")
    for k in ("dak", "muur", "schoorsteen", "deur", "raam1", "raam2", "stam", "kruin", "zon"):
        sh.line(P(house_pts(k)), "guide", "stroke-width:1.2;stroke-dasharray:3 2")
    sh.region("M140 60C140 50 152 46 158 52C162 42 178 44 178 56C186 56 186 66 178 66H146C138 66 136 60 140 60Z", "-")
    for x in (20, 60, 180): sh.line(f"M{x} 226q4 -6 8 0", "l", "stroke-width:1.4")
    sh.text(100, 262, "Wie woont er in jouw huis?", 7)
collage("huis-van-vormen-plakken", "Huis van vormen knippen en plakken", "Huis van vormen", huis_knip, huis_plak, "vormen", "4-6", [
    "Kleur de vormen in: de muur, het dak, de ramen, de deur, de boom en de zon.",
    "Knip de vormen uit langs de streepjeslijn. Rechte stukken knip je in één keer door.",
    "Zoek op het plakvel het grijze lijntje dat bij elke vorm past. Plak eerst de muur en het dak, dan de deur, de ramen en de schoorsteen.",
    "Plak de boom en de zon erbij en teken nog bloemen in het gras."], minutes=25, diff=1)

# ---------- verjaardagstaart ----------
def cake_layer(w, h, code, icing="-"):
    def fn(pc):
        pc.add(rrect(-w / 2, 0, w, h, 3), code)
        n = int(w // 14); dw = w / n
        d = f"M{-w / 2} 0H{w / 2}V5"
        for k in range(n):
            x = w / 2 - k * dw
            d += f"Q{x - dw * .25} {12 if k % 2 == 0 else 8} {x - dw * .5} 5Q{x - dw * .75} 3 {x - dw} 5"
        d += "Z"
        pc.add(sample(d, 6), icing)
        for k in range(n - 1): pc.add(circ(-w / 2 + dw * (k + 1), h * .62, 2.6), "r", sil=False)
    return fn
def candle(code):
    def fn(pc):
        pc.add(rect(-3.5, 0, 7, 26), code)
        for y in (6, 13, 20): pc.ln([(-3.5, y + 3), (3.5, y)])
        pc.add(bar(0, 0, 0, -3, .4), "-"); pc.ln([(0, 0), (0, -3)])
        pc.add(sample("M0 -14C4 -9 4 -4 0 -3C-4 -4 -4 -9 0 -14Z"), "y")
    return fn
def strawberry(pc):
    pc.add(sample("M0 12C-10 4 -10 -6 -6 -7C-3 -8 3 -8 6 -7C10 -6 10 4 0 12Z"), "r")
    pc.add(sample("M-6 -7L-3 -11L0 -8L3 -11L6 -7Z"), "g")
    for x, y in [(-3, -2), (3, -2), (0, 3), (-4, 3), (4, 3)]: pc.dot(x, y, .9)
def cream(pc): pc.add(sample("M-8 6C-12 6 -12 0 -7 -1C-8 -6 -2 -9 0 -10C2 -9 8 -6 7 -1C12 0 12 6 8 6Z"), "-"); pc.ln(sample("M-6 1Q0 -3 6 1", 4))
def cherry(pc):
    pc.add(circ(0, 4, 6), "r"); pc.add(bar(0, -1, 4, -10, .8), "g"); pc.ln([(0, -1), (4, -10)]); pc.add(ellp(7, -10, 4, 2, -20), "g")
def topper_star(pc):
    pc.add(rect(-1.2, 10, 2.4, 20), "w"); pc.add(star_pts(0, 4, 11, 5), "y")
def taart_knip(sh):
    sh.text(100, 25, "Kleur alles in, knip het uit en maak de mooiste taart.", 6)
    y = flow(sh, [cake_layer(120, 34, "m")], 4, 30, 196)
    y = flow(sh, [cake_layer(96, 30, "k"), cake_layer(72, 28, "w")], 4, y + 2, 196, 4)
    y = flow(sh, [candle(c) for c in "rbgpyrbgo"], 4, y + 2, 196, 3)
    y = flow(sh, [strawberry] * 4 + [cherry] * 3, 4, y + 2, 196, 3)
    flow(sh, [cream] * 5 + [topper_star], 4, y + 2, 196, 3)
def taart_plak(sh):
    head(sh, "Mijn verjaardagstaart")
    sh.text(100, 28, "Plak de lagen op het taartplateau en zet er kaarsjes op.", 6.5)
    sh.region("M0 280V236H200V280Z", "w")
    sh.region("M24 212H176Q176 222 160 222H40Q24 222 24 212Z", "z")
    sh.region("M88 222H112L118 236H82Z", "z")
    for x, c in [(12, "r"), (52, "y"), (148, "b"), (188, "g")]:
        sh.region(f"M{x - 8} 40Q{x} 52 {x + 8} 40Q{x} 28 {x - 8} 40Z", c) if False else None
    d = "M0 34" + "".join(f"Q{k * 25 + 12.5} 54 {(k + 1) * 25} 34" for k in range(8))
    sh.line(d, "l", "stroke-width:1.4")
    for k in range(8): sh.poly_r([(k * 25 + 6, 39 + 6 * 0), (k * 25 + 19, 39), (k * 25 + 12.5, 52)], "rybgpmot"[k])
    outline_text(sh, 100, 262, "Ik word ...... jaar!", 14)
collage("verjaardagstaart-plakken", "Verjaardagstaart knippen en plakken", "Taart: knipvel", taart_knip, taart_plak, "feest", "4-6", [
    "Kleur de taartlagen, kaarsjes, aardbeien en de rest in.",
    "Knip alles uit langs de streepjeslijn.",
    "Plak op het plakvel eerst de grootste laag op het taartplateau, daarboven de middelste en dan de kleinste.",
    "Zet er net zoveel kaarsjes op als je jaren wordt en versier de taart met aardbeien, kersen en slagroom. Schrijf onderaan hoe oud je wordt."],
    holiday="verjaardag")

# ---------- trein ----------
def wheel(r, code="z"):
    def fn(pc):
        pc.add(circ(0, 0, r), code); pc.add(circ(0, 0, r * .35), "-", sil=False)
        for k in range(6):
            a = math.radians(k * 60); pc.ln([(r * .35 * math.cos(a), r * .35 * math.sin(a)), (r * .85 * math.cos(a), r * .85 * math.sin(a))], style="stroke-width:1.2")
    return fn
def loc_boiler(pc):
    pc.add(rrect(0, 0, 56, 28, 10), "g"); pc.add(rect(-4, 4, 6, 20), "z")
    for x in (16, 30, 44): pc.ln([(x, 0), (x, 28)])
def loc_cab(pc):
    pc.add(rect(0, 0, 34, 44), "r"); pc.add(rrect(7, 7, 20, 16, 2), "b"); pc.ln([(0, 32), (34, 32)])
def loc_roof(pc): pc.add(rrect(0, 0, 42, 7, 3), "x")
def chimney(pc): pc.add([(0, 0), (16, 0), (12, 8), (12, 22), (4, 22), (4, 8)], "x")
def cowcatcher(pc): pc.add([(0, 0), (16, 0), (16, 14)], "y"); pc.ln([(5, 0), (16, 9)]); pc.ln([(10, 0), (16, 5)])
def wagon(code, load):
    def fn(pc):
        pc.add(rect(0, 0, 50, 26), code); pc.ln([(0, 8), (50, 8)])
        for x in (12.5, 25, 37.5): pc.ln([(x, 8), (x, 26)])
    return fn
def logs(pc):
    for x, y in [(8, 8), (22, 8), (36, 8), (15, -4), (29, -4)]: pc.add(circ(x, y, 7), "w"); pc.add(circ(x, y, 3.2), "o", sil=False)
def crates(pc):
    for x, y, s in [(0, 0, 18), (20, 4, 14), (4, -16, 14)]:
        pc.add(rect(x, y, s, s), "o"); pc.ln([(x, y), (x + s, y + s)]); pc.ln([(x + s, y), (x, y + s)])
def puff(pc): pc.add(sample("M-14 6C-20 6 -20 -2 -13 -2C-14 -10 -4 -12 -1 -6C2 -12 14 -10 12 -2C20 -2 20 6 14 6Z"), "-")
def trein_knip(sh):
    sh.text(100, 25, "Kleur de stukjes, knip ze uit en bouw een lange trein.", 6)
    y = flow(sh, [loc_boiler, loc_cab, loc_roof, chimney, cowcatcher], 4, 30, 196, 4)
    y = flow(sh, [wagon("b", None), wagon("y", None), logs], 4, y + 4, 196, 4)
    y = flow(sh, [crates, puff, puff, puff], 4, y + 4, 196, 4)
    flow(sh, [wheel(11)] * 2 + [wheel(8)] * 4, 4, y + 4, 196, 4)
def trein_plak(sh):
    head(sh, "Bouw een trein")
    sh.circle_r(170, 50, 14, "y")
    sh.region("M0 200V150Q40 110 90 140T200 120V200Z", "l")
    sh.region("M0 200V170Q60 150 120 172T200 160V200Z", "g")
    sh.region("M0 200H200V280H0Z", "-")
    for x in range(4, 200, 14): sh.rect_r(x, 210, 8, 8, "w")
    sh.seg(0, 212, 200, 212, "l"); sh.seg(0, 216, 200, 216, "l")
    sh.text(100, 250, "Zet de wielen op het spoor en plak de trein erboven.", 6.5)
    sh.text(100, 264, "Waar rijdt jouw trein naartoe? ..............................", 6.5)
collage("trein-plakken", "Trein knippen en plakken", "Trein: knipvel", trein_knip, trein_plak, "voertuigen", "4-6", [
    "Kleur de locomotief, de wagons, de wielen en de lading in.",
    "Knip alle stukjes uit langs de streepjeslijn.",
    "Plak op het plakvel eerst de wielen op het spoor. Plak de cabine en de ketel van de locomotief erboven, dan het dak, de schoorsteen en de gele neus vooraan.",
    "Plak de wagons achter de locomotief en zet er boomstammen of kisten op. Rookwolkjes boven de schoorsteen: tuut tuut!"])

# =====================================================================
# Legpuzzels met genummerde stukjes en een legbord
# =====================================================================
def jig_edge(a, b, sgn):
    (ax, ay), (bx, by) = a, b; ux, uy = bx - ax, by - ay; nx, ny = -uy * sgn, ux * sgn
    def p(t, h): return f"{f(ax + ux * t + nx * h)} {f(ay + uy * t + ny * h)}"
    return f"L{p(.36, 0)}C{p(.40, 0)} {p(.42, -.05)} {p(.39, -.11)}C{p(.33, -.25)} {p(.67, -.25)} {p(.61, -.11)}C{p(.58, -.05)} {p(.60, 0)} {p(.64, 0)}L{p(1, 0)}"
def jigsaw_lines(n, x0, y0, S, seed):
    rnd = random.Random(seed); c = S / n; d = []
    for k in range(1, n):
        x = x0 + k * c; d.append(f"M{f(x)} {f(y0)}" + "".join(jig_edge((x, y0 + r * c), (x, y0 + (r + 1) * c), rnd.choice((-1, 1))) for r in range(n)))
        y = y0 + k * c; d.append(f"M{f(x0)} {f(y)}" + "".join(jig_edge((x0 + r * c, y), (x0 + (r + 1) * c, y), rnd.choice((-1, 1))) for r in range(n)))
    return "".join(d)
def puzzle(slug, name, n, draw, cat, age, diff, seed, extra_step):
    x0, y0, S = 15, 40, 170
    order = list(range(1, n * n + 1))
    sh = Sheet(); head(sh, name.split(": ")[-1][0].upper() + name.split(": ")[-1][1:])
    sh.text(100, 28, "Kleur de tekening, knip de stukjes los en leg ze op het legbord.", 6)
    draw(sh, x0, y0, S)
    sh.line(jigsaw_lines(n, x0, y0, S, seed), "cut"); sh.rect_line(x0, y0, S, S, "cut")
    c = S / n
    for i in range(n * n):
        r, k = divmod(i, n); bx, by = x0 + k * c + 6.5, y0 + r * c + 6.5
        sh.circle_r(bx, by, 4.6, "-"); sh.text(bx, by + 2, str(order[i]), 5.5)
    sh.legend(["cut"], 276)
    lb = Sheet(); head(lb, "Legbord")
    lb.text(100, 28, "Leg elk stukje op het vak met hetzelfde nummer.", 6.5)
    lb.line(jigsaw_lines(n, x0, y0, S, seed), "l", "stroke-width:1"); lb.rect_line(x0, y0, S, S, "l", 0, "stroke-width:1.6")
    for i in range(n * n):
        r, k = divmod(i, n); lb.text(x0 + k * c + c / 2, y0 + r * c + c / 2 + 5, str(order[i]), 14 if n == 3 else 11)
    lb.text(100, 236, "Lukt het ook zonder legbord? Probeer het maar!", 6)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": 25, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, {"slug": "stevig-papier", "optional": True}, {"slug": "lijmstift", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Op stevig papier gaat de puzzel langer mee. Print het legbord op gewoon papier.", "steps": [
            "Kleur de tekening helemaal in.",
            "Knip eerst langs de rechte buitenrand en daarna de stukjes los langs de streepjeslijnen. " + extra_step,
            "Hussel de stukjes door elkaar.",
            "Leg de puzzel op het legbord: elk stukje hoort op het vak met hetzelfde nummer. Wil je hem bewaren? Plak de stukjes vast."]}}},
        [("extra", "Legbord", lb)])

def farm_scene(sh, x0, y0, S):
    X = lambda v: x0 + v * S / 100; Y = lambda v: y0 + v * S / 100
    sh.rect_r(x0, y0, S, S, "b")
    sh.circle_r(X(82), Y(16), S * .09, "y")
    sh.region(f"M{X(4)} {Y(22)}C{X(4)} {Y(14)} {X(14)} {Y(12)} {X(18)} {Y(16)}C{X(22)} {Y(10)} {X(34)} {Y(12)} {X(34)} {Y(20)}C{X(38)} {Y(20)} {X(38)} {Y(26)} {X(32)} {Y(26)}H{X(8)}C{X(2)} {Y(26)} {X(2)} {Y(22)} {X(4)} {Y(22)}Z", "-")
    sh.region(f"M{x0} {Y(56)}Q{X(30)} {Y(40)} {X(60)} {Y(52)}T{X(100)} {Y(46)}V{Y(100)}H{x0}Z", "l")
    sh.region(f"M{x0} {Y(76)}Q{X(50)} {Y(66)} {X(100)} {Y(74)}V{Y(100)}H{x0}Z", "g")
    # schuur
    sh.rect_r(X(10), Y(42), S * .34, S * .3, "r")
    sh.poly_r([(X(6), Y(43)), (X(27), Y(24)), (X(48), Y(43))], "w")
    sh.rect_r(X(20), Y(56), S * .14, S * .16, "w")
    sh.line(f"M{X(20)} {Y(56)}L{X(34)} {Y(72)}M{X(34)} {Y(56)}L{X(20)} {Y(72)}")
    sh.circle_r(X(27), Y(35), S * .035, "y")
    # boom
    sh.rect_r(X(82), Y(44), S * .05, S * .2, "w"); sh.circle_r(X(84.5), Y(38), S * .1, "g")
    # hek
    for k in range(6): sh.rect_r(X(52 + k * 7), Y(60), S * .025, S * .12, "w")
    sh.rect_r(X(51), Y(62.5), S * .4, S * .02, "w"); sh.rect_r(X(51), Y(67.5), S * .4, S * .02, "w")
    # kip
    cx, cy = X(62), Y(86)
    sh.region(f"M{cx - 9} {cy}C{cx - 9} {cy - 8} {cx + 2} {cy - 9} {cx + 4} {cy - 4}C{cx + 4} {cy - 12} {cx + 12} {cy - 12} {cx + 12} {cy - 6}C{cx + 12} {cy + 6} {cx + 4} {cy + 8} {cx} {cy + 8}C{cx - 6} {cy + 8} {cx - 9} {cy + 6} {cx - 9} {cy}Z", "-")
    sh.poly_r([(cx + 12, cy - 7), (cx + 17, cy - 5), (cx + 12, cy - 3)], "o"); sh.dot(cx + 8, cy - 7, 1.2)
    sh.region(f"M{cx + 6} {cy - 11}Q{cx + 8} {cy - 15} {cx + 10} {cy - 11}Z", "r")
    sh.line(f"M{cx} {cy + 8}V{cy + 12}M{cx + 4} {cy + 8}V{cy + 12}")
    for x in (14, 30, 88):
        sh.region(f"M{X(x)} {Y(94)}C{X(x) - 4} {Y(90)} {X(x) - 2} {Y(86)} {X(x)} {Y(90)}C{X(x) + 2} {Y(86)} {X(x) + 4} {Y(90)} {X(x)} {Y(94)}Z", "m")
puzzle("puzzel-boerderij-9-stukjes", "Puzzel knippen: boerderij (9 stukjes)", 3, farm_scene, "boerderij", "4-6", 1, 7, "")

def castle_scene(sh, x0, y0, S):
    X = lambda v: x0 + v * S / 100; Y = lambda v: y0 + v * S / 100
    sh.rect_r(x0, y0, S, S, "b")
    sh.circle_r(X(12), Y(12), S * .07, "y")
    sh.region(f"M{X(60)} {Y(14)}C{X(60)} {Y(8)} {X(68)} {Y(6)} {X(71)} {Y(10)}C{X(74)} {Y(5)} {X(84)} {Y(7)} {X(84)} {Y(13)}C{X(88)} {Y(13)} {X(88)} {Y(18)} {X(84)} {Y(18)}H{X(62)}C{X(57)} {Y(18)} {X(57)} {Y(14)} {X(60)} {Y(14)}Z", "-")
    sh.region(f"M{x0} {Y(70)}Q{X(25)} {Y(58)} {X(50)} {Y(66)}T{X(100)} {Y(62)}V{Y(100)}H{x0}Z", "l")
    sh.region(f"M{x0} {Y(84)}Q{X(50)} {Y(76)} {X(100)} {Y(84)}V{Y(94)}Q{X(50)} {Y(88)} {x0} {Y(94)}Z", "n")
    def tower(cx, w, top, code):
        sh.rect_r(X(cx - w / 2), Y(top), S * w / 100, Y(80) - Y(top), code)
        sh.poly_r([(X(cx - w / 2 - 2), Y(top)), (X(cx), Y(top - 16)), (X(cx + w / 2 + 2), Y(top))], "r")
        sh.line(f"M{X(cx)} {Y(top - 16)}V{Y(top - 24)}"); sh.poly_r([(X(cx), Y(top - 24)), (X(cx + 7), Y(top - 21.5)), (X(cx), Y(top - 19))], "y")
        sh.region(f"M{X(cx - 2.5)} {Y(top + 12)}V{Y(top + 8)}Q{X(cx)} {Y(top + 5)} {X(cx + 2.5)} {Y(top + 8)}V{Y(top + 12)}Z", "x")
    sh.rect_r(X(28), Y(46), S * .44, Y(80) - Y(46), "z")
    for k in range(6): sh.rect_r(X(28 + k * 8), Y(42), S * .045, S * .045, "z")
    tower(22, 14, 36, "z"); tower(78, 14, 36, "z"); tower(50, 12, 26, "z")
    sh.region(f"M{X(42)} {Y(80)}V{Y(66)}Q{X(50)} {Y(56)} {X(58)} {Y(66)}V{Y(80)}Z", "w")
    for k in range(3): sh.line(f"M{X(44.5 + k * 5.5)} {Y(64 if k == 1 else 66)}V{Y(80)}")
    sh.poly_r([(X(42), Y(80)), (X(58), Y(80)), (X(60), Y(90)), (X(40), Y(90))], "w")
    for x in (8, 92, 30, 70):
        sh.region(f"M{X(x)} {Y(98)}C{X(x) - 4} {Y(94)} {X(x) - 2} {Y(90)} {X(x)} {Y(94)}C{X(x) + 2} {Y(90)} {X(x) + 4} {Y(94)} {X(x)} {Y(98)}Z", "y" if x < 50 else "m")
puzzle("puzzel-kasteel-16-stukjes", "Puzzel knippen: kasteel (16 stukjes)", 4, castle_scene, "sprookjes", "6-9", 2, 11, "")

# =====================================================================
# Harmonica knippen: kettingen die aan elkaar vast blijven
# =====================================================================
def chain_strip(sh, y, pw, h, n, polys, details, code_hint=None):
    x0 = (200 - pw * n) / 2
    sh.rect_line(x0, y, pw * n, h, "cut")
    for k in range(1, n): sh.seg(x0 + k * pw, y, x0 + k * pw, y + h, "fold")
    ps = [T(p, x0, y) for p in polys]
    for lp in outline(ps, 0, .25):
        for part in clip_x(lp, x0, x0 + pw): sh.line(PL(part), "cut")
    details(sh, x0, y)
    sh.raw(f'<rect class="glue" x="{f(x0 + pw + 1)}" y="{f(y + 1)}" width="0" height="0"/>') if False else None
    return x0

def elephant_polys():
    return [ellp(18, 36, 15, 13), circ(31, 24, 10), ellp(25, 25, 8, 12),
            sample("M36 17C44 20 44 32 43 38L48 38L48 47L37 47C37 40 37 34 33 30Z"), rect(5, 40, 8, 20), rect(21, 40, 8, 20), bar(-4, 30, 5, 32, 2.6)]
EK = 60 / 44
def elephant_details(sh, x0, y0):
    sh.line(PL(T(sample("M30 18C22 10 14 22 20 32C22 37 28 37 31 33", 10), x0, y0, EK)), "l", "stroke-width:1.4")
    sh.dot(x0 + 36 * EK, y0 + 21 * EK, 1.6)
    sh.line(PL(T([(38, 36), (40.5, 40), (42.5, 38)], x0, y0, EK)), "l", "stroke-width:1.2")
def kettingolifanten():
    sh = Sheet(); head(sh, "Olifantenketting")
    sh.text(100, 27, "Vouw een strook als een harmonica en knip de olifant uit.", 6)
    for i, y in enumerate((32, 120)):
        chain_strip(sh, y, 60, 80, 3, [T(p, 0, -6, EK) for p in elephant_polys()], lambda sh, x, y: elephant_details(sh, x, y - 6))
    # uitleg: zigzag
    sh.text(100, 214, "Zo vouw je de strook:", 7)
    sh.line("M67 242" + "".join(f"L{67 + (k + 1) * 22} {224 if k % 2 == 0 else 242}" for k in range(3)), "l", "stroke-width:1.4")
    sh.text(100, 254, "Knip alleen langs de streepjes. De slurf en het staartje", 6)
    sh.text(100, 262, "raken de vouwlijn: daar knip je niet, zo blijven ze aan elkaar vast.", 6)
    sh.legend(["cut", "fold"], 276)
    write(OUT, "olifantenketting-knippen", sh, {"category": "dieren", "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 20, "adultHelp": True,
        "materials": [SCHAAR, KLEUR],
        "i18n": {"nl": {"name": "Olifantenketting knippen", "printNote": "Gewoon printpapier werkt het best: dik papier is gevouwen te lastig om te knippen.", "steps": [
            "Knip een strook uit langs de buitenste streepjeslijn.",
            "Vouw de strook als een harmonica: op de eerste stippellijn naar achteren en op de tweede naar voren. Het vak met de olifant ligt nu bovenop.",
            "Houd de vouwen goed vast en knip langs de streepjes door alle lagen heen. Knip niet langs de vouwlijn bij de slurf en het staartje.",
            "Vouw de strook open: drie olifanten aan elkaar! Plak meer stroken aan elkaar voor een lange rij. Ze staan om en om slurf aan slurf en staart aan staart. Kleur ze in en maak ze allemaal anders."]}}})
kettingolifanten()

def heart_polys(pw, h):
    hp = sample(heart_path(pw / 2, h / 2 - 3, 28), 14)
    return [hp]
def star_polys(pw, h):
    return [star_pts(pw / 2, h / 2 + 3, 27, 11.5), rect(-4, h / 2 + 3 - 27 * math.cos(math.radians(72)) - 2.5, pw + 8, 7)]
def flower_polys(pw, h):
    cx, cy = pw / 2, h / 2
    return [circ(cx, cy, 8)] + [circ(cx + 13 * math.cos(math.radians(a)), cy + 13 * math.sin(math.radians(a)), 7.5) for a in range(30, 360, 60)] + [rect(-4, cy - 3, pw + 8, 6)]
def slingers():
    sh = Sheet(); head(sh, "Slingers knippen")
    sh.text(100, 27, "Vouw een strook als een harmonica en knip de vorm uit.", 6)
    pw = 44
    for y, (polys, det) in zip((36, 104, 172), [
        (heart_polys(pw, 56), lambda sh, x0, y0: None),
        (star_polys(pw, 56), lambda sh, x0, y0: None),
        (flower_polys(pw, 56), lambda sh, x0, y0: sh.circle_line(x0 + pw / 2, y0 + 28, 3.5, "l"))]):
        chain_strip(sh, y, pw, 56, 4, polys, det)
    sh.text(100, 246, "Waar de vorm de vouwlijn raakt, knip je niet. Zo blijft de slinger heel.", 6)
    sh.text(100, 255, "Plak een paar slingers aan elkaar voor een hele lange!", 6)
    sh.legend(["cut", "fold"], 276)
    write(OUT, "slingers-knippen-harmonica", sh, {"category": "feest", "age": "6-9", "kind": "vouwblad", "difficulty": 2, "minutes": 25, "adultHelp": True,
        "materials": [SCHAAR, KLEUR, {"slug": "plakband", "optional": True}],
        "i18n": {"nl": {"name": "Slingers knippen: hartjes, sterren en bloemen", "printNote": "Gewoon printpapier werkt het best; dik papier is gevouwen te lastig om te knippen.", "steps": [
            "Knip de drie stroken los langs de buitenste streepjeslijn.",
            "Vouw een strook als een harmonica: op de eerste stippellijn naar achteren, op de volgende naar voren en de laatste weer naar achteren. Het vak met de tekening ligt bovenop.",
            "Knip langs de streepjes door alle lagen heen. Knip niet over de vouwlijnen waar de vorm ze raakt.",
            "Vouw open en kleur je slinger in. Plak de slingers met plakband aan elkaar en hang ze op."]}}})
slingers()

# =====================================================================
# Halve vormen: dubbelvouwen en knippen
# =====================================================================
HALF = [
    ("hart", lambda: [sample(heart_path(0, -1, 32), 14)]),
    ("ster", lambda: [star_pts(0, 3, 33, 13.5)]),
    ("vlinder", lambda: [ellp(-15, -9, 17, 12, 35), ellp(15, -9, 17, 12, -35), ellp(-11, 13, 12, 8, -30), ellp(11, 13, 12, 8, 30), ellp(0, 2, 4, 22)]),
    ("appel", lambda: [circ(-9, 6, 18), circ(9, 6, 18), rect(-2, -22, 4, 12)]),
    ("tulp", lambda: [sample("M-16 -26L-7 -16L0 -28L7 -16L16 -26C19 -4 10 4 0 4C-10 4 -19 -4 -16 -26Z"), rect(-4, 2, 8, 28), ellp(-10, 20, 11, 4, -30), ellp(10, 20, 11, 4, 30)]),
    ("dennenboom", lambda: [[(-14, -12), (0, -32), (14, -12)], [(-20, 2), (0, -22), (20, 2)], [(-26, 18), (0, -8), (26, 18)], rect(-5, 17, 10, 12)]),
]
def halve_vormen():
    sh = Sheet(); head(sh, "Halve vormen knippen")
    sh.text(100, 27, "Vouw elk kaartje dubbel op de stippellijn en knip de halve vorm uit.", 6)
    ans = Sheet(); head(ans, "Wat werd het?")
    for i, (word, fn) in enumerate(HALF):
        col, row = i % 2, i // 2
        bx, by, w, h = 10 + col * 92, 34 + row * 78, 88, 74
        sh.rect_line(bx, by, w, h, "cut")
        cx, cy = bx + w / 2, by + h / 2
        sh.seg(cx, by, cx, by + h, "fold")
        ps = [T(p, cx, cy) for p in fn()]
        for lp in outline(ps, 0, .25):
            for part in clip_x(lp, cx, 400): sh.line(PL(part), "cut")
        sh.text(bx + 4, by + h - 4, str(i + 1), 6, "start", cls="tip")
        ax, ay = 52 + col * 96, 70 + row * 70
        for lp in outline([T(p, ax, ay) for p in fn()], 0, .3): ans.line(P(lp), "l", "stroke-width:1.6")
        ans.text(ax, ay + 40, f"{i + 1}. {word}", 7)
    sh.legend(["cut", "fold"], 276)
    write(OUT, "halve-vormen-knippen", sh, {"category": "vormen", "age": "4-6", "kind": "vouwblad", "difficulty": 1, "minutes": 20,
        "materials": [SCHAAR, KLEUR],
        "i18n": {"nl": {"name": "Halve vormen: vouwen en knippen", "steps": [
            "Knip een kaartje uit langs de rechte streepjeslijn.",
            "Vouw het dubbel op de stippellijn, met de tekening aan de buitenkant.",
            "Knip langs de halve vorm, door beide lagen heen. Bij de vouw knip je niet.",
            "Vouw open: een hele vorm! Raad eerst wat het wordt en kijk daarna op het antwoordblad."]}}},
        [("antwoorden", "Wat werd het?", ans)])
halve_vormen()

# =====================================================================
# Bloem knippen uit gevouwen papier (8 blaadjes)
# =====================================================================
def vouwbloem():
    sh = Sheet(); head(sh, "Bloem knippen")
    sh.text(100, 27, "Vouw het vierkant drie keer en knip door alle lagen: een bloem!", 6)
    x0, y0, Sz = 25, 36, 150; cx, cy = x0 + Sz / 2, y0 + Sz / 2
    pol = lambda r, th: (cx + r * math.sin(th), cy - r * math.cos(th))
    sh.poly_r([(cx, cy), (cx, y0), (x0 + Sz, y0)], "y")
    sh.rect_line(x0, y0, Sz, Sz, "cut")
    sh.line(f"M{x0} {cy}H{x0 + Sz}M{cx} {y0}V{y0 + Sz}M{x0} {y0 + Sz}L{x0 + Sz} {y0}M{x0} {y0}L{x0 + Sz} {y0 + Sz}", "fold")
    R = 70; q = math.pi / 4
    sh.line(PL([pol(R * (.62 + .38 * math.sin(4 * th)), th) for th in [q * k / 40 for k in range(41)]]), "cut")
    sh.line(PL([pol(7, q * k / 12) for k in range(13)]), "cut")
    sh.line(PL([(cx + 4 * math.sin(math.pi * k / 12), cy - 30 + 4 * math.cos(math.pi * k / 12)) for k in range(13)]), "cut")
    dx, dy = math.sin(q), -math.cos(q)
    m = (cx + 34 * dx, cy + 34 * dy); nrm = (-dy, dx)  # loodrecht op de schuine lijn, naar het gele vak
    nrm = (-nrm[0], -nrm[1]) if (cx - m[0]) * nrm[0] + (y0 - m[1]) * nrm[1] < 0 else nrm
    sh.line(PL([(m[0] + 4.5 * math.cos(math.pi * k / 12) * dx + 4.5 * math.sin(math.pi * k / 12) * nrm[0], m[1] + 4.5 * math.cos(math.pi * k / 12) * dy + 4.5 * math.sin(math.pi * k / 12) * nrm[1]) for k in range(13)]), "cut")
    for t, x, y in [("1", x0 - 6, cy + 2), ("2", cx, y0 + Sz + 8), ("3", x0 + Sz - 10, y0 + Sz - 2)]:
        sh.circle_r(x, y - 2, 4.5, "-"); sh.text(x, y, t, 6)
    # stappen in plaatjes
    k = .18; sy = 204
    def mini(ox, poly, wedge, lab):
        sh.line(P([(ox + x * k, sy + y * k) for x, y in poly]), "l", "stroke-width:1.2")
        sh.poly_r([(ox + x * k, sy + y * k) for x, y in wedge], "-")
        sh.text(ox + 13.5, sy + 40, lab, 5, cls="tip")
    W = [(75, 75), (75, 0), (150, 0)]
    mini(10, [(0, 0), (150, 0), (150, 150), (0, 150)], W, "begin")
    mini(56, [(0, 0), (150, 0), (150, 75), (0, 75)], W, "na 1")
    mini(102, [(75, 0), (150, 0), (150, 75), (75, 75)], W, "na 2")
    mini(148, [(75, 0), (150, 0), (75, 75)], W, "na 3")
    for x in (42, 88, 134): sh.line(f"M{x} {sy + 14}h8m-3 -3l3 3l-3 3", "l", "stroke-width:1")
    sh.text(100, 258, "Steeds naar achteren vouwen: het gele vakje blijft bovenop.", 6)
    sh.legend(["cut", "fold"], 276)
    write(OUT, "bloem-knippen-uit-gevouwen-papier", sh, {"category": "natuur", "age": "6-9", "kind": "vouwblad", "difficulty": 2, "minutes": 20, "adultHelp": True,
        "materials": [SCHAAR, KLEUR],
        "i18n": {"nl": {"name": "Bloem knippen uit gevouwen papier", "printNote": "Gewoon printpapier knipt het makkelijkst; stevig papier is te dik als het gevouwen is.", "steps": [
            "Knip het vierkant uit langs de buitenste streepjeslijn. Leg het neer met het gele vakje boven.",
            "Vouw 1: vouw de onderste helft naar achteren, op de liggende stippellijn.",
            "Vouw 2: vouw de linkerhelft naar achteren, op de staande stippellijn.",
            "Vouw 3: vouw het onderste driehoekje naar achteren, op de schuine stippellijn. Nu ligt alleen het gele driehoekje bovenop.",
            "Knip door alle lagen langs de streepjes in het gele vakje: de bolle lijn, het hoekje in de punt en de twee halve rondjes. Knip niet over de vouwen heen.",
            "Vouw voorzichtig open: een bloem met acht blaadjes en gaatjes! Kleur hem in of plak hem op het raam."]}}})
vouwbloem()

# =====================================================================
# Zoemschijf met touw
# =====================================================================
def zoemer():
    sh = Sheet(); head(sh, "Zoemschijf")
    sh.text(100, 26, "Twee zoemers: plak steeds twee schijven op elkaar.", 6)
    R = 34
    discs = [(55, 70), (145, 70), (55, 152), (145, 152)]
    for i, (cx, cy) in enumerate(discs):
        if i == 0:
            for k, c in enumerate("royg bp".replace(" ", "n")):
                sh.region(arc_path(cx, cy, 0, R, k * 360 / 7 - 90, (k + 1) * 360 / 7 - 90), c)
        elif i == 1:
            for k in range(6): sh.region(arc_path(cx, cy, R - (k + 1) * R / 6, R - k * R / 6, -90, 270) if False else P(circ(cx, cy, R - k * R / 6, 60)), "nyny-y"[k] if k < 5 else "-")
        elif i == 2:
            for k in range(2): sh.region(arc_path(cx, cy, 0, R, k * 180 - 90, (k + 1) * 180 - 90), "yb"[k])
        else:
            sh.circle_r(cx, cy, R, "-")
            for arm in range(3):
                pts_a = [(cx + (4 + t * (R - 4)) * math.cos(math.radians(arm * 120 + t * 260)), cy + (4 + t * (R - 4)) * math.sin(math.radians(arm * 120 + t * 260))) for t in [k / 40 for k in range(41)]]
                pts_b = [(cx + (4 + t * (R - 4)) * math.cos(math.radians(arm * 120 + 45 + t * 260)), cy + (4 + t * (R - 4)) * math.sin(math.radians(arm * 120 + 45 + t * 260))) for t in [k / 40 for k in range(41)]][::-1]
                sh.poly_r(pts_a + pts_b, "x")
        sh.circle_r(cx, cy, 9, "-")
        for dx in (-4.5, 4.5): sh.circle_line(cx + dx, cy, 1.6, "cut")
        sh.circle_line(cx, cy, R + 3, "cut")
    sh.text(55, 115, "zoemer 1: voorkant", 5.5, cls="tip"); sh.text(145, 115, "zoemer 1: achterkant", 5.5, cls="tip")
    sh.text(55, 197, "zoemer 2: voorkant", 5.5, cls="tip"); sh.text(145, 197, "zoemer 2: achterkant", 5.5, cls="tip")
    # zo gebruik je hem
    sh.text(100, 210, "Zo gebruik je hem:", 7)
    cy = 236
    sh.circle_r(100, cy, 12, "-"); sh.circle_line(97, cy, 1.2, "l"); sh.circle_line(103, cy, 1.2, "l")
    sh.line(f"M97 {cy}C80 {cy - 4} 50 {cy - 6} 30 {cy - 2}M97 {cy}C80 {cy + 4} 50 {cy + 6} 30 {cy + 2}", "l", "stroke-width:1")
    sh.line(f"M103 {cy}C120 {cy - 4} 150 {cy - 6} 170 {cy - 2}M103 {cy}C120 {cy + 4} 150 {cy + 6} 170 {cy + 2}", "l", "stroke-width:1")
    for x, s in ((24, -1), (176, 1)): sh.ellipse_r(x, cy, 7, 9, "-"); sh.line(f"M{x - 4 * s} {cy - 8}v-4m{2 * s} 4v-5m{2 * s} 5v-4", "l", "stroke-width:1.4")
    sh.line(f"M40 {cy + 14}h-10m3 -3l-3 3l3 3M160 {cy + 14}h10m-3 -3l3 3l-3 3", "l", "stroke-width:1.2")
    sh.text(100, 264, "Trek, laat los, trek, laat los... hoor je hem zoemen?", 6)
    sh.legend(["cut"], 276)
    write(OUT, "zoemschijf-met-touw", sh, {"category": "vormen", "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 25, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "touw"}, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": "Zoemschijf met touw", "printNote": "Print op stevig papier of plak het vel op karton: een stevige schijf zoemt het best.", "steps": [
            "Kleur de schijven in. De regenboogschijf wordt bij het draaien bijna wit, geel en blauw worden samen groen!",
            "Knip de vier schijven uit langs de streepjeslijn.",
            "Plak de voorkant en de achterkant van een zoemer met de witte kanten op elkaar, zo dat de gaatjes precies over elkaar liggen. Laat de lijm goed drogen.",
            "Een volwassene prikt de twee gaatjes door, bijvoorbeeld met een satéprikker.",
            "Steek een touw van ongeveer een meter door het ene gaatje en terug door het andere. Knoop de uiteinden aan elkaar.",
            "Schuif de schijf naar het midden, houd in elke hand een lus en zwaai de schijf rond tot het touw gedraaid is. Trek je handen dan uit elkaar en laat weer een beetje los: de schijf draait en zoemt!"]}}})
zoemer()

# =====================================================================
# Splitpennen: skelet, weerschijf, klok, windmolen
# =====================================================================
def skull_torso(pc):
    pc.add(circ(0, 0, 15), "-"); pc.add(rrect(-9, 8, 18, 11, 4), "-")
    pc.add(bar(0, 18, 0, 28, 3), "-")
    for s in (-1, 1): pc.add(circ(s * 19, 31, 6), "-")
    pc.add(ellp(0, 46, 19, 19), "-")
    pc.add(bar(0, 60, 0, 78, 3.5), "-")
    pc.add(sample("M-16 76Q0 70 16 76L18 86Q10 96 0 90Q-10 96 -18 86Z"), "-")
    for s in (-1, 1): pc.add(circ(s * 12, 86, 6), "-")
    for s in (-1, 1): pc.add(ellp(s * 6, -1, 4.5, 5), "x", sil=False)
    pc.add([(0, 5), (-2.5, 9), (2.5, 9)], "x", sil=False)
    for x in (-6, -2, 2, 6): pc.ln([(x, 13), (x, 18)], style="stroke-width:1.2")
    pc.ln([(0, 30), (0, 62)], style="stroke-width:1.6")
    for k, y in enumerate((36, 44, 52)):
        w = 14 - abs(k - 1) * 2
        for s in (-1, 1): pc.ln(sample(f"M0 {y}Q{s * w} {y - 4} {s * (w + 3)} {y + 3}", 6), style="stroke-width:1.4")
    for y in (64, 68, 72): pc.ln([(-3, y), (3, y)], style="stroke-width:1")
    for x, y in [(-19, 31), (19, 31), (-12, 86), (12, 86)]: pc.hole(x, y)
def long_bone(L, w=3, r=5.5, top_hole=True, bot_hole=True):
    def fn(pc):
        pc.add(bar(0, 0, 0, L, w), "-")
        for y in (0, L):
            for dx in (-2.2, 2.2): pc.add(circ(dx, y, r * .75), "-")
        if top_hole: pc.hole(0, 0)
        if bot_hole: pc.hole(0, L)
    return fn
def forearm(s):
    def fn(pc):
        pc.add(bar(0, 0, 0, 30, 2.6), "-")
        for dx in (-2, 2): pc.add(circ(dx, 0, 4), "-")
        pc.add(ellp(0, 35, 6, 6.5), "-")
        for k, a in enumerate((-30, -10, 10, 30)):
            t = math.radians(a); pc.add(bar(3 * math.sin(t), 38, 12 * math.sin(t) * 1.2, 38 + 11 * math.cos(t), 1.4), "-")
        pc.add(bar(-5 * s, 33, -11 * s, 38, 1.5), "-")
        pc.hole(0, 0)
    return fn
def shin(s):
    def fn(pc):
        pc.add(bar(0, 0, 0, 38, 3), "-")
        for dx in (-2.2, 2.2): pc.add(circ(dx, 0, 4.5), "-")
        pc.add(sample(f"M{-4 * s} 36Q{-4 * s} 46 {4 * s} 46L{14 * s} 46Q{18 * s} 46 {16 * s} 41Q{8 * s} 38 {4 * s} 36Z"), "-")
        pc.hole(0, 0)
    return fn
def skelet():
    sh = Sheet(); head(sh, "Beweegbaar skelet")
    sh.text(100, 26, "Knip alle botjes uit en zet ze vast met splitpennen op de rondjes.", 6)
    place(sh, S(skull_torso, 1.25), 66, 30)
    y = flow(sh, [S(long_bone(32), 1.2), S(long_bone(32), 1.2), S(forearm(1), 1.2), S(forearm(-1), 1.2)], 2, 168, 198, 8)
    flow(sh, [S(long_bone(40, 3.4, 6), 1.15), S(long_bone(40, 3.4, 6), 1.15), S(shin(-1), 1.15), S(shin(1), 1.15)], 2, y, 198, 8) if False else None
    for i, fn in enumerate([S(long_bone(40, 3.4, 6), 1.1), S(long_bone(40, 3.4, 6), 1.1)]): place(sh, fn, 8 + i * 22, 36)
    for i, fn in enumerate([S(shin(-1), 1.1), S(shin(1), 1.1)]): place(sh, fn, 140 + i * 26, 36)
    sh.text(100, 268, "8 splitpennen: schouders, ellebogen, heupen en knieën.", 6)
    sh.legend(["cut"], 277)
    write(OUT, "beweegbaar-skelet", sh, {"category": "feest", "holiday": "halloween", "age": "6-9", "kind": "knipplaat", "difficulty": 3, "minutes": 40, "adultHelp": True, "paperGsm": 160,
        "materials": [SCHAAR, SPLIT, {"slug": "stevig-papier"}, {"slug": "touw", "optional": True}],
        "i18n": {"nl": {"name": "Beweegbaar skelet met splitpennen", "printNote": "Print op stevig papier (160 gram), dan scheuren de gaatjes niet zo snel.", "steps": [
            "Knip het hoofd met de romp en alle botjes uit langs de streepjeslijn.",
            "Een volwassene prikt een gaatje in elk rondje met een kruisje, bijvoorbeeld met de punt van een potlood op een gum.",
            "Leg een bovenarm achter een schouder, zo dat de gaatjes over elkaar liggen. Steek er een splitpen door en buig de pootjes aan de achterkant opzij. Doe hetzelfde met de andere arm.",
            "Zet de onderarmen met de handjes vast aan de onderkant van de bovenarmen.",
            "Zet de bovenbenen vast aan de heupen en de onderbenen met de voetjes aan de knieën.",
            "Klaar! Laat het skelet zwaaien en dansen. Met een touwtje door het hoofd kun je het ophangen."]}}})
skelet()

def weer_pic(sh, k, cx, cy):
    """Plaatje in het bovenste kwart van de schijf (wordt over k*90 graden gedraaid)."""
    px, py = cx, cy - 33
    sh.raw(f'<g transform="rotate({k * 90} {cx} {cy})">')
    if k == 0:
        sh.circle_r(px, py, 8, "y")
        for a in range(0, 360, 45):
            t = math.radians(a); sh.seg(px + 11 * math.cos(t), py + 11 * math.sin(t), px + 15 * math.cos(t), py + 15 * math.sin(t), "l", "stroke-width:1.6")
        word = "zon"
    else:
        sh.region(f"M{px - 14} {py + 2}C{px - 18} {py + 2} {px - 18} {py - 5} {px - 12} {py - 5}C{px - 12} {py - 12} {px - 2} {py - 13} {px} {py - 8}C{px + 3} {py - 14} {px + 13} {py - 12} {px + 12} {py - 5}C{px + 18} {py - 5} {px + 18} {py + 2} {px + 13} {py + 2}Z", "z" if k != 3 else "-")
        if k == 1:
            for dx, dy in [(-8, 9), (0, 12), (8, 9)]: sh.region(f"M{px + dx} {py + dy - 4}Q{px + dx + 2.5} {py + dy} {px + dx} {py + dy + 1.5}Q{px + dx - 2.5} {py + dy} {px + dx} {py + dy - 4}Z", "b")
            word = "regen"
        elif k == 2:
            for dx, dy in [(-8, 9), (0, 12), (8, 9)]:
                for a in (0, 60, 120): t = math.radians(a); sh.seg(px + dx - 2.6 * math.cos(t), py + dy - 2.6 * math.sin(t), px + dx + 2.6 * math.cos(t), py + dy + 2.6 * math.sin(t), "l", "stroke-width:1")
            word = "sneeuw"
        else:
            for dy, w in [(7, 22), (11, 16)]: sh.line(f"M{px - 14} {py + dy}H{px + w - 14}q4 0 4 -3t-3 -3", "l", "stroke-width:1.4")
            word = "wind"
    sh.text(px, cy - 17, word, 5)
    sh.raw("</g>")
def weerschijf():
    sh = Sheet(); head(sh, "Weerschijf")
    fx, fy, FR = 100, 82, 54
    dx_, dy_ = 100, 210
    # voorkant met venster
    sh.circle_r(fx, fy, FR, "-")
    for k in range(12):
        a1 = k * 30 - 90
        sh.region(arc_path(fx, fy, FR - 8, FR, a1, a1 + 30), "rybg"[k % 4])
    sh.line(arc_path(fx, fy, 13, 46, -135, -45), "cut")
    sh.text(fx, fy + 20, "Het weer", 9); sh.text(fx, fy + 31, "van vandaag", 7)
    sh.circle_line(fx, fy, FR + 3, "cut"); sh.circle_line(fx, fy, 1.8, "cut")
    sh.text(fx, fy + FR + 10, "voorkant: knip ook het venster eruit", 5.5, cls="tip")
    # draaischijf
    DR = 58
    sh.circle_r(dx_, dy_, DR, "-")
    for k in range(4): sh.seg(dx_ + 12 * math.cos(math.radians(45 + 90 * k)), dy_ + 12 * math.sin(math.radians(45 + 90 * k)), dx_ + DR * math.cos(math.radians(45 + 90 * k)), dy_ + DR * math.sin(math.radians(45 + 90 * k)), "l", "stroke-width:1")
    for k in range(4): weer_pic(sh, k, dx_, dy_)
    sh.circle_line(dx_, dy_, DR + 3, "cut"); sh.circle_line(dx_, dy_, 1.8, "cut")
    sh.legend(["cut"], 277)
    write(OUT, "weerschijf-draaien", sh, {"category": "natuur", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, SPLIT, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Weerschijf om te draaien", "printNote": "Op stevig papier draait de schijf het mooist.", "steps": [
            "Kleur de rand van de voorkant en de vier weerplaatjes op de schijf in.",
            "Knip de voorkant en de schijf uit langs de streepjeslijn. Een volwassene knipt het venster uit de voorkant.",
            "Prik een gaatje in het midden van allebei (bij het kruisje). Leg de voorkant op de schijf en steek een splitpen door de twee gaatjes. Buig de pootjes aan de achterkant open.",
            "Kijk elke ochtend naar buiten en draai het goede weer achter het venster: zon, regen, sneeuw of wind?"]}}})
weerschijf()

def klok():
    sh = Sheet(); head(sh, "Klok met draaiende wijzers")
    cx, cy, R = 100, 100, 66
    sh.circle_r(cx, cy, R, "-")
    for k in range(12): sh.region(arc_path(cx, cy, R - 7, R, k * 30 - 105, k * 30 - 75), "rbyg"[k % 4])
    sh.circle_r(cx, cy, R - 7, "-")
    for m in range(60):
        t = math.radians(m * 6 - 90); r1 = R - 13 if m % 5 == 0 else R - 10
        sh.seg(cx + r1 * math.cos(t), cy + r1 * math.sin(t), cx + (R - 8) * math.cos(t), cy + (R - 8) * math.sin(t), "l", "stroke-width:" + ("1.4" if m % 5 == 0 else ".7"))
    for h in range(1, 13):
        t = math.radians(h * 30 - 90); sh.text(cx + 44 * math.cos(t), cy + 44 * math.sin(t) + 4, str(h), 11)
    sh.circle_line(cx, cy, R + 3, "cut")
    sh.circle_r(cx, cy, 5, "x"); sh.circle_line(cx, cy, 1.6, "l")
    def hand(L, w, code):
        def fn(pc):
            pc.add(circ(0, 0, 6), code)
            pc.add([(0, -w), (L - 9, -w), (L - 9, -w - 3.5), (L, 0), (L - 9, w + 3.5), (L - 9, w), (0, w)], code)
            pc.hole(0, 0)
        return fn
    place(sh, hand(56, 2.4, "n"), 30, 182)
    place(sh, hand(38, 3.6, "r"), 30, 206)
    sh.text(118, 191, "grote wijzer: de minuten", 6, "start"); sh.text(118, 215, "kleine wijzer: de uren", 6, "start")
    sh.text(100, 238, "Zet de klok op: 3 uur - half 8 - kwart over 10 - kwart voor 6", 6)
    sh.text(100, 250, "Hoe laat sta jij op? En hoe laat ga je slapen?", 6)
    sh.legend(["cut"], 276)
    write(OUT, "klok-maken-met-wijzers", sh, {"category": "leren", "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 25, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, SPLIT, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Klok maken met draaiende wijzers", "printNote": "Print op stevig papier, of plak de klok op karton (bijvoorbeeld een oude doos).", "steps": [
            "Kleur de rand van de klok en de twee wijzers in.",
            "Knip de klok en de wijzers uit langs de streepjeslijn.",
            "Een volwassene prikt een gaatje in het midden van de klok en in het rondje van elke wijzer.",
            "Leg eerst de kleine wijzer en dan de grote wijzer op de klok en steek de splitpen door alle gaatjes. Buig de pootjes aan de achterkant open, niet te strak: de wijzers moeten kunnen draaien.",
            "Oefen samen: zet de klok op 3 uur, half 8, kwart over 10 en kwart voor 6. De grote wijzer wijst de minuten, de kleine de uren."]}}})
klok()

def molen_body(pc):
    pc.add(rect(-40, 150, 80, 12), "l")
    pc.add([(-26, 150), (-17, 40), (17, 40), (26, 150)], "w")
    pc.add(rect(-34, 92, 68, 5), "x")
    for x in (-30, -20, 20, 30): pc.add(rect(x - 1, 97, 2, 10), "x", sil=False)
    pc.add(sample("M-20 42Q-22 18 0 12Q22 18 20 42Z"), "z")
    pc.add(sample("M-8 150V132Q0 122 8 132V150Z"), "g")
    for x, y in [(-6, 60), (-8, 112)]: pc.add(rect(x, y, 12 if y < 100 else 16, 12), "b", sil=False)
    pc.ln([(0, 60), (0, 72)]); pc.ln([(-6, 66), (6, 66)])
    pc.ln([(-14, 52), (14, 52)], style="stroke-width:1.2")
    pc.add(circ(0, 30, 6), "x"); pc.hole(0, 30)
def wieken(pc):
    for k in range(4):
        a = math.radians(k * 90 + 45); ca, sa = math.cos(a), math.sin(a)
        rot = lambda x, y: (x * ca - y * sa, x * sa + y * ca)
        pc.add([rot(x, y) for x, y in rect(4, -2, 62, 4)], "w")
        frame = [rot(x, y) for x, y in rect(18, 2, 48, 13)]
        pc.add(frame, "-")
        for k2 in range(1, 6): pc.ln([rot(18 + k2 * 8, 2), rot(18 + k2 * 8, 15)], style="stroke-width:1")
        pc.ln([rot(18, 8.5), rot(66, 8.5)], style="stroke-width:1")
    pc.add(circ(0, 0, 7), "x"); pc.hole(0, 0)
def windmolen():
    sh = Sheet(); head(sh, "Draaiende windmolen")
    place(sh, S(wieken, .95), 82, 22)
    place(sh, S(molen_body, 1.05), 2, 104)
    for x, c in [(150, "r"), (166, "y"), (182, "m")]:
        sh.seg(x, 254, x, 236, "l", "stroke-width:1.6")
        sh.region(f"M{x - 5} 224L{x - 2.5} 229L{x} 222L{x + 2.5} 229L{x + 5} 224Q{x + 6} 236 {x} 236Q{x - 6} 236 {x - 5} 224Z", c)
        sh.region(f"M{x} 248Q{x + 8} 238 {x + 10} 242Q{x + 6} 250 {x} 250Z", "g")
    sh.text(148, 160, "Blaas maar eens:", 6.5); sh.text(148, 169, "draaien de wieken?", 6.5)
    sh.legend(["cut"], 276)
    write(OUT, "draaiende-windmolen", sh, {"category": "wereld", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25, "adultHelp": True, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, SPLIT, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Windmolen met draaiende wieken", "printNote": "Op stevig papier draaien de wieken het mooist.", "steps": [
            "Kleur de molen en de wieken in. De wieken mogen alle kleuren krijgen!",
            "Knip de molen en de wieken uit langs de streepjeslijn.",
            "Een volwassene prikt een gaatje in het zwarte rondje van de molen en in het midden van de wieken.",
            "Leg de wieken op de molen en steek een splitpen door beide gaatjes. Buig de pootjes aan de achterkant open, niet te strak.",
            "Draai de wieken rond met je vinger, of plak de molen op een raam waar het tocht."]}}})
windmolen()

# =====================================================================
# Sorteerbladen: knip de plaatjes uit en sorteer ze in de vakken
# =====================================================================
def ic_appel(p): p.add(sample("M20 12C12 6 4 12 6 22C8 32 14 36 20 33C26 36 32 32 34 22C36 12 28 6 20 12Z"), "r"); p.ln([(20, 12), (21, 5)]); p.add(ellp(26, 7, 5, 2.5, -20), "g")
def ic_banaan(p): p.add(sample("M6 12C8 28 22 36 34 28L36 30C24 40 4 32 4 12Z"), "y"); p.ln([(4, 12), (6, 9)])
def ic_peer(p): p.add(sample("M20 6C15 6 15 14 14 18C8 22 8 34 20 34C32 34 32 22 26 18C25 14 25 6 20 6Z"), "l"); p.ln([(20, 6), (21, 2)])
def ic_druiven(p):
    for x, y in [(14, 12), (20, 12), (26, 12), (17, 18), (23, 18), (14, 24) if False else (20, 24), (17, 30) if False else (20, 30)]: p.add(circ(x, y, 3.6), "p")
    for x, y in [(11, 18), (29, 18), (14, 24), (26, 24)]: pass
    p.ln([(20, 8), (22, 3)]); p.add(ellp(26, 5, 4, 2, -20), "g")
def ic_aardbei(p): p.add(sample("M20 34C10 26 8 16 12 12C16 9 24 9 28 12C32 16 30 26 20 34Z"), "r"); p.add(sample("M12 12L15 7L20 10L25 7L28 12Z"), "g"); [p.dot(x, y, .9) for x, y in [(16, 17), (24, 17), (20, 22), (16, 25), (24, 25)]]
def ic_kersen(p): p.add(circ(12, 28, 6), "r"); p.add(circ(27, 30, 6), "r"); p.ln(sample("M12 22Q14 10 22 5Q22 16 27 24", 8)); p.add(ellp(25, 6, 5, 2.4, 20), "g")
def ic_wortel(p): p.add(sample("M16 12L24 12L21 36Q20 38 19 36Z"), "o"); [p.ln([(16.5 + k * .3, 18 + k * 6), (19, 18 + k * 6)]) for k in range(3)]; p.add(sample("M20 12Q14 4 16 2Q20 6 20 12Q22 3 26 3Q24 8 20 12Z"), "g")
def ic_broccoli(p): p.add(sample("M17 22L15 36H25L23 22Z"), "l"); [p.add(circ(x, y, 6), "g") for x, y in [(12, 18), (20, 12), (28, 18), (20, 20)]]
def ic_sla(p): p.add(circ(20, 22, 13), "l"); p.ln(sample("M20 34Q14 22 20 10", 8)); p.ln(sample("M20 34Q28 24 30 14", 8)); p.ln(sample("M20 34Q10 26 9 16", 8))
def ic_ui(p):
    p.add(sample("M20 8C22 14 32 17 32 25C32 32 26 35 20 35C14 35 8 32 8 25C8 17 18 14 20 8Z"), "w")
    p.ln(sample("M16 16Q12 24 15 33", 6), style="stroke-width:1.4"); p.ln(sample("M24 16Q28 24 25 33", 6), style="stroke-width:1.4")
    for x in (17, 20, 23): p.ln([(20, 35), (x, 39)], style="stroke-width:1.4")
    p.ln(sample("M20 8Q19 4 21 2", 4))
def ic_radijs(p): p.add(circ(20, 24, 9), "m"); p.ln([(20, 33), (20, 38)]); p.add(ellp(15, 9, 3.5, 7, -20), "g"); p.add(ellp(25, 9, 3.5, 7, 20), "g")
def ic_prei(p):
    p.add(sample("M23 17C27 9 30 5 36 2C33 8 30 14 27 20Z"), "g"); p.add(sample("M23 17C21 9 22 5 24 1C27 7 28 13 27 20Z"), "l")
    p.add(bar(10, 34, 25, 19, 4), "-")
    for d in (-2, 0, 2): p.ln([(8 + d, 36 - d), (5 + d, 39 - d)], style="stroke-width:1.2")
def ic_zon(p):
    p.add(circ(20, 20, 8), "y")
    for a in range(0, 360, 45): t = math.radians(a); p.ln([(20 + 11 * math.cos(t), 20 + 11 * math.sin(t)), (20 + 16 * math.cos(t), 20 + 16 * math.sin(t))])
def ic_kampvuur(p):
    p.add(bar(8, 34, 32, 28, 2.5), "w"); p.add(bar(8, 28, 32, 34, 2.5), "w")
    p.add(sample("M20 4C28 12 30 20 28 26C26 32 14 32 12 26C10 20 14 18 16 12C18 16 20 16 20 4Z"), "r"); p.add(sample("M20 16C24 20 25 24 23 27C21 29 18 29 17 27C16 24 18 22 20 16Z"), "y")
def steam(p, xs, y): [p.ln(sample(f"M{x} {y}Q{x - 3} {y - 4} {x} {y - 7}Q{x + 3} {y - 10} {x} {y - 13}", 6)) for x in xs]
def ic_mok(p): p.add(rect(8, 16, 18, 20), "b"); p.add(sample("M26 20C34 20 34 32 26 32L26 29C30 29 30 23 26 23Z"), "b"); steam(p, (13, 21), 13)
def ic_kaars(p): p.add(rect(15, 18, 10, 20), "m"); p.ln([(20, 18), (20, 14)]); p.add(sample("M20 3C25 9 24 14 20 14C16 14 15 9 20 3Z"), "y")
def ic_soep(p): p.add(sample("M4 20H36C36 30 28 36 20 36C12 36 4 30 4 20Z"), "o"); p.add(ellp(20, 20, 16, 2.5), "y"); steam(p, (13, 20, 27), 16)
def ic_strijkijzer(p): p.add(sample("M6 32C8 20 18 18 34 18V32Z"), "t"); p.add(sample("M16 18Q16 10 22 10H32V18H29V13H22Q19 13 19 18Z"), "z"); steam(p, (12, 20), 36) if False else [p.ln(sample(f"M{x} 31Q{x - 2} 35 {x} 38", 4)) for x in (12, 20, 28)]
def ic_ijsje(p): p.add([(13, 18), (27, 18), (20, 38)], "w"); p.ln([(15, 22), (24, 30)]); p.ln([(25, 22), (17, 30)]); p.add(circ(20, 13, 8), "k"); p.add(circ(20, 6, 3), "r")
def ic_lolly(p): p.add(rect(19, 28, 3, 10), "w"); p.add(sample("M12 30V10C12 2 28 2 28 10V30Z"), "o"); p.ln([(12, 16), (28, 16)])
def ic_sneeuwpop(p): p.add(circ(20, 28, 9), "-"); p.add(circ(20, 14, 6.5), "-"); p.add(rect(14, 4, 12, 5), "x"); p.add(rect(12, 8, 16, 2), "x"); p.add([(20, 14), (26, 15), (20, 16)], "o"); p.dot(18, 12, 1); p.dot(22, 12, 1)
def ic_vlok(p):
    for a in (0, 60, 120):
        t = math.radians(a); p.ln([(20 - 15 * math.cos(t), 20 - 15 * math.sin(t)), (20 + 15 * math.cos(t), 20 + 15 * math.sin(t))])
        for s in (-1, 1):
            bx, by = 20 + s * 10 * math.cos(t), 20 + s * 10 * math.sin(t)
            for d in (-1, 1): u = t + d * .7 + (0 if s > 0 else math.pi); p.ln([(bx, by), (bx + 4 * math.cos(u), by + 4 * math.sin(u))])
def ic_ijsblok(p): p.add([(8, 16), (20, 10), (32, 16), (32, 30), (20, 36), (8, 30)], "b"); p.ln([(8, 16), (20, 22), (32, 16)]); p.ln([(20, 22), (20, 36)])
def ic_koelkast(p): p.add(rrect(10, 3, 20, 34, 3), "-"); p.ln([(10, 14), (30, 14)]); p.ln([(26, 7), (26, 11)]); p.ln([(26, 18), (26, 24)]); ic_mini_vlok(p, 18, 25)
def ic_mini_vlok(p, x, y):
    for a in (0, 60, 120): t = math.radians(a); p.ln([(x - 4 * math.cos(t), y - 4 * math.sin(t)), (x + 4 * math.cos(t), y + 4 * math.sin(t))], style="stroke-width:1")
def ic_auto(p): p.add(sample("M3 28V20L10 18L15 11H27L33 18L37 20V28Z"), "r"); p.add(sample("M17 13H25L29 18H15Z"), "b"); p.add(circ(11, 29, 4.5), "x"); p.add(circ(29, 29, 4.5), "x")
def ic_fiets(p):
    for x in (9, 31): p.circle = None; p.ln(circ(x, 27, 7), closed=True)
    p.ln([(9, 27), (16, 16), (28, 16), (31, 27)]); p.ln([(16, 16), (20, 27), (28, 16)]); p.ln([(14, 12), (19, 12)]); p.ln([(28, 16), (27, 11), (31, 10)])
def ic_trein(p): p.add(rect(4, 12, 20, 16), "g"); p.add(rect(24, 6, 12, 22), "r"); p.add(rect(27, 9, 6, 6), "b"); p.add(rect(8, 6, 5, 6), "x"); [p.add(circ(x, 30, 4), "x") for x in (10, 20, 30)]
def ic_bus(p): p.add(rrect(3, 10, 34, 18, 3), "y"); [p.add(rect(6 + k * 8, 13, 6, 6), "b") for k in range(4)]; p.add(circ(10, 29, 4), "x"); p.add(circ(30, 29, 4), "x")
def ic_zeilboot(p): p.add(sample("M4 28H36L31 35H9Z"), "w"); p.ln([(20, 28), (20, 4)]); p.add([(21, 5), (33, 25), (21, 25)], "r"); p.add([(19, 9), (19, 25), (9, 25)], "-"); p.ln(sample("M2 38Q6 35 10 38Q14 41 18 38Q22 35 26 38Q30 41 34 38", 4), style="stroke-width:1.2")
def ic_duikboot(p): p.add(ellp(20, 24, 17, 8), "y"); p.add(rect(15, 10, 9, 8), "y"); p.ln([(19, 10), (19, 5), (23, 5)]); [p.add(circ(x, 24, 2.5), "b") for x in (12, 20, 28)]; p.add([(2, 18), (5, 24), (2, 30)], "y")
def ic_kano(p): p.add(sample("M2 24Q20 34 38 24Q20 28 2 24Z"), "o"); p.add(circ(20, 18, 3.5), "k"); p.add(bar(10, 30, 30, 10, 1.2), "w"); p.add(ellp(30, 10, 4, 2, -45), "w"); p.ln(sample("M2 36Q6 33 10 36Q14 39 18 36Q22 33 26 36Q30 39 34 36", 4), style="stroke-width:1.2")
def ic_vrachtschip(p): p.add(sample("M2 22H38L33 32H7Z"), "n"); p.add(rect(26, 10, 9, 12), "-"); [p.add(rect(6 + k * 6, 16, 6, 6), "rgy"[k % 3]) for k in range(3)]; p.ln(sample("M2 36Q6 33 10 36Q14 39 18 36Q22 33 26 36Q30 39 34 36", 4), style="stroke-width:1.2")
def ic_vliegtuig(p): p.add(sample("M3 20Q3 16 8 16H32L37 20L32 24H8Q3 24 3 20Z"), "-"); p.add([(16, 18), (24, 4), (28, 4), (24, 18)], "b"); p.add([(16, 22), (24, 36), (28, 36), (24, 22)], "b"); p.add([(5, 17), (3, 10), (8, 10), (11, 16)], "r")
def ic_heli(p): p.add(ellp(16, 24, 11, 8), "r"); p.add(bar(26, 22, 37, 20, 2), "r"); p.add(sample("M10 22Q10 18 16 18V24H10Z"), "b"); p.ln([(4, 12), (28, 12)]); p.ln([(16, 12), (16, 16)]); p.ln([(8, 34), (24, 34)]); p.ln([(12, 32), (12, 34)]); p.ln([(20, 32), (20, 34)])
def ic_ballon(p): p.add(sample("M20 26C8 20 6 4 20 4C34 4 32 20 20 26Z"), "m"); p.ln(sample("M20 4Q14 14 20 26", 6)); p.ln(sample("M20 4Q26 14 20 26", 6)); p.add(rect(16, 30, 8, 7), "w"); p.ln([(18, 25), (17, 30)]); p.ln([(22, 25), (23, 30)])
def ic_raket(p): p.add(sample("M14 30V14Q20 2 26 14V30Z"), "-"); p.add(circ(20, 16, 3.2), "b"); p.add([(14, 22), (8, 32), (14, 30)], "r"); p.add([(26, 22), (32, 32), (26, 30)], "r"); p.add(sample("M16 30Q20 40 24 30Z"), "y")

def icon_at(sh, fn, x, y, k):
    sh.raw(f'<g transform="translate({f(float(x))} {f(float(y))}) scale({k})">'); fn(Pc(sh)); sh.raw("</g>")
def sorteer(slug, name, heading, cats, cat, age, steps, seed):
    def boxes(sh):
        n = len(cats); bw = (188 - (n - 1) * 4) / n
        for i, (label, _, icon) in enumerate(cats):
            bx = 6 + i * (bw + 4)
            sh.rect_line(bx, 32, bw, 118, "l", 4, "stroke-width:1.4")
            sh.text(bx + bw / 2 + 6, 46, label, 8)
            icon_at(sh, icon, bx + bw / 2 - len(label) * 2.6 - 14, 36, .32)
        return bw
    sh = Sheet(); head(sh, heading)
    sh.text(100, 26, "Knip de kaartjes los en leg ze in het goede vak.", 6.5)
    bw = boxes(sh)
    items = [(fn, i) for i, (_, fns, _) in enumerate(cats) for fn in fns]
    random.Random(seed).shuffle(items)
    C = 36; cols = 4; gx = 100 - cols * C / 2; gy = 160
    for k, (fn, _) in enumerate(items):
        r, c = divmod(k, cols)
        icon_at(sh, fn, gx + c * C + 3, gy + r * C + 3, .75)
    rows = (len(items) + cols - 1) // cols
    for r in range(rows + 1): sh.seg(gx, gy + r * C, gx + cols * C, gy + r * C, "cut")
    for c in range(cols + 1): sh.seg(gx + c * C, gy, gx + c * C, gy + rows * C, "cut")
    sh.legend(["cut"], 277)
    an = Sheet(); head(an, "Antwoorden")
    boxes(an)
    n = len(cats); C2 = 28
    for i, (_, fns, _) in enumerate(cats):
        bx = 6 + i * (bw + 4); per = 3 if n == 2 else 2
        for k, fn in enumerate(fns):
            r, c = divmod(k, per)
            x = bx + bw / 2 - per * C2 / 2 + c * C2 + 1; y = 56 + r * C2
            an.rect_line(x, y, C2 - 2, C2 - 2, "l", 2, "stroke-width:.6")
            icon_at(an, fn, x + 1, y + 1, .6)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": 1, "minutes": 20,
        "materials": [KLEUR, SCHAAR, {"slug": "lijmstift", "optional": True}],
        "i18n": {"nl": {"name": name, "steps": steps + ["Kijk samen na met het antwoordblad. Klopt alles? Plak de kaartjes dan vast."]}}},
        [("antwoorden", "Antwoorden", an)])

sorteer("sorteren-groente-of-fruit", "Sorteren: groente of fruit?", "Groente of fruit?", [
    ("Groente", [ic_wortel, ic_broccoli, ic_sla, ic_ui, ic_radijs, ic_prei], ic_wortel),
    ("Fruit", [ic_appel, ic_banaan, ic_peer, ic_druiven, ic_aardbei, ic_kersen], ic_appel)], "eten", "4-6", [
    "Kleur de plaatjes in en knip de kaartjes los langs de streepjeslijnen.",
    "Kijk naar elk kaartje: is het groente of fruit? Leg het in het goede vak."], 3)
sorteer("sorteren-warm-of-koud", "Sorteren: warm of koud?", "Warm of koud?", [
    ("Warm", [ic_zon, ic_kampvuur, ic_mok, ic_kaars, ic_soep, ic_strijkijzer], ic_zon),
    ("Koud", [ic_ijsje, ic_lolly, ic_sneeuwpop, ic_vlok, ic_ijsblok, ic_koelkast], ic_vlok)], "thuis", "4-6", [
    "Kleur de plaatjes in en knip de kaartjes los langs de streepjeslijnen.",
    "Is het warm of koud? Leg elk kaartje in het goede vak. Pas op: aan iets heets brand je je!"], 5)
sorteer("sorteren-land-water-lucht", "Sorteren: over land, op het water of in de lucht?", "Land, water of lucht?", [
    ("Land", [ic_auto, ic_fiets, ic_trein, ic_bus], ic_auto),
    ("Water", [ic_zeilboot, ic_duikboot, ic_kano, ic_vrachtschip], ic_zeilboot),
    ("Lucht", [ic_vliegtuig, ic_heli, ic_ballon, ic_raket], ic_vliegtuig)], "voertuigen", "4-6", [
    "Kleur de voertuigen in en knip de kaartjes los langs de streepjeslijnen.",
    "Waar rijdt, vaart of vliegt het? Leg elk kaartje in het goede vak: land, water of lucht."], 9)

# =====================================================================
# Harmonica-dieren
# =====================================================================
def acc_strip(sh, x0, y, L, h, step, codes, glue_start=False, glue_end=False, feet=False):
    n = round(L / step)
    for k in range(n):
        sh.rect_r(x0 + k * step, y, step, h, codes[k % len(codes)])
    if glue_start: sh.raw(f'<rect class="glue" x="{f(x0 + 1)}" y="{f(y + 1)}" width="{f(step - 2)}" height="{f(h - 2)}"/>')
    if glue_end: sh.raw(f'<rect class="glue" x="{f(x0 + L - step + 1)}" y="{f(y + 1)}" width="{f(step - 2)}" height="{f(h - 2)}"/>')
    for k in range(1, n): sh.seg(x0 + k * step, y, x0 + k * step, y + h, "fold")
    sh.rect_line(x0 - 2.5, y - 2.5, L + 5, h + 5, "cut")
def rups_head(pc):
    for s in (-1, 1): pc.add(bar(s * 6, -14, s * 13, -30, 1.3), "x"); pc.add(circ(s * 13, -31, 3.5), "r")
    pc.add(circ(0, 0, 20), "l")
    for s in (-1, 1): pc.add(circ(s * 7, -4, 5), "-"); pc.dot(s * 7 + 1, -3, 2.4); pc.add(circ(s * 13, 7, 3.5), "k", sil=False)
    pc.ln(sample("M-7 8Q0 15 7 8", 6))
def rups_tail(pc):
    pc.add(sample("M-14 0C-14 -10 6 -12 16 0C6 12 -14 10 -14 0Z"), "l")
    for x in (-6, 2): pc.add(circ(x, 0, 2.5), "y", sil=False)
def rups():
    sh = Sheet(); head(sh, "Harmonica-rups")
    sh.text(100, 26, "Vouw de stroken als een harmonica en plak de kop en staart eraan.", 6)
    place(sh, rups_head, 30, 32); place(sh, rups_tail, 120, 50)
    sh.text(54, 108, "kop", 6, cls="tip"); sh.text(138, 86, "staart", 6, cls="tip")
    for i, y in enumerate((120, 160, 200)):
        acc_strip(sh, 12, y, 176, 26, 16, "lg" if i != 1 else "gl", glue_start=(i > 0))
        for k in range(11): sh.line(f"M{12 + k * 16 + 5} {y + 26}v-4M{12 + k * 16 + 11} {y + 26}v-4", "l", "stroke-width:1")
    sh.text(100, 246, "Grijs vakje: daar komt lijm op, om de stroken aan elkaar te plakken.", 6)
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "harmonica-rups", sh, {"category": "dieren", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": "Harmonica-rups", "steps": [
            "Kleur de kop, de staart en de stroken in.",
            "Knip alles uit langs de streepjeslijn.",
            "Plak de stroken achter elkaar: smeer lijm op het grijze vakje en leg het einde van de vorige strook erop. Zo krijg je één lange strook.",
            "Vouw de lange strook als een harmonica: op de eerste stippellijn naar achteren, op de volgende naar voren, en zo verder.",
            "Plak de kop op het eerste vakje en de staart op het laatste. Trek de rups uit en duw hem weer in: hij kruipt!"]}}})
rups()

def teckel_front(pc):
    pc.add(bar(28, 30, 40, 16, 6), "w")
    for x in (16, 30): pc.add(rrect(x, 44, 9, 18, 3), "w"); pc.add(ellp(x + 6, 62, 7, 3.5), "w")
    pc.add(rrect(8, 24, 36, 26, 11), "w")
    pc.add(circ(42, 14, 12), "w"); pc.add(ellp(55, 19, 9, 6), "w"); pc.add(ellp(62, 17, 3, 2.5), "x")
    pc.add(ellp(36, 18, 5.5, 11, 15), "w"); pc.dot(46, 10, 1.8)
    pc.ln(sample("M52 24Q56 26 60 23", 4))
    pc.add(bar(30, 27, 38, 23, 2), "r", sil=False)
def teckel_rear(pc):
    pc.add(bar(6, 30, -10, 12, 2.8), "w")
    for x in (6, 20): pc.add(rrect(x, 44, 9, 18, 3), "w"); pc.add(ellp(x + 6, 62, 7, 3.5), "w")
    pc.add(rrect(0, 24, 36, 26, 11), "w")
def teckel():
    sh = Sheet(); head(sh, "Harmonica-teckel")
    sh.text(100, 26, "Een hond met een uitrekbare buik! Vouw de buik als een harmonica.", 6)
    place(sh, S(teckel_front, 1.4), 104, 36); place(sh, S(teckel_rear, 1.4), 24, 56)
    sh.text(150, 152, "voorkant", 6, cls="tip"); sh.text(54, 152, "achterkant", 6, cls="tip")
    for i, y in enumerate((166, 210)):
        acc_strip(sh, 10, y, 180, 36, 15, "wo" if i == 0 else "ow", glue_start=True, glue_end=(i == 1))
    sh.text(100, 260, "Plak de twee buikstroken aan elkaar voor een extra lange teckel.", 6)
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "harmonica-teckel", sh, {"category": "dieren", "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 30, "paperGsm": 160,
        "materials": [KLEUR, SCHAAR, LIJM, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Harmonica-teckel met uitrekbare buik", "printNote": "Op stevig papier blijft de hond beter staan.", "steps": [
            "Kleur de voorkant, de achterkant en de buikstroken van de teckel in.",
            "Knip alles uit langs de streepjeslijn.",
            "Plak de twee buikstroken aan elkaar: lijm op het grijze vakje aan het begin van de onderste strook en leg het einde van de bovenste strook erop.",
            "Vouw de lange strook als een harmonica: steeds om en om naar achteren en naar voren.",
            "Plak het eerste vakje achter de borst van de voorkant en het laatste grijze vakje achter de billen van de achterkant. De pootjes staan op tafel.",
            "Trek voorzichtig aan de kop: de teckel wordt langer en langer!"]}}})
teckel()

# springkikker met heksentrap
def frog(pc):
    for s in (-1, 1):
        pc.add(ellp(s * 24, 16, 10, 16, s * 30), "g")
        pc.add(sample(f"M{s * 30} 26L{s * 40} 30L{s * 38} 34L{s * 26} 32Z"), "g")
    pc.add(ellp(0, 6, 24, 20), "g")
    for s in (-1, 1):
        pc.add(sample(f"M{s * 8} 18L{s * 12} 32L{s * 20} 34L{s * 18} 30L{s * 14} 28L{s * 12} 20Z"), "l")
        pc.add(circ(s * 11, -14, 8), "g"); pc.add(circ(s * 11, -14, 4.5), "-", sil=False); pc.dot(s * 11, -14, 2.2)
    pc.ln(sample("M-12 2Q0 10 12 2", 6))
    pc.add(ellp(0, 12, 10, 6), "y", sil=False)
def lilypad(pc):
    pc.add(sample("M0 0L-4 -26C-30 -26 -44 -14 -44 0C-44 16 -24 26 0 26C24 26 44 16 44 0C44 -14 30 -26 4 -26Z"), "l")
    for a in (-60, -20, 20, 60, 100, 140): t = math.radians(a); pc.ln([(0, 0), (34 * math.cos(t) * .9, 20 * math.sin(t))], style="stroke-width:1")
    pc.raw = None
    pc.sh.raw(f'<rect class="glue" x="{f(pc.dx - 8 * pc.sc)}" y="{f(pc.dy - 8 * pc.sc)}" width="{f(16 * pc.sc)}" height="{f(16 * pc.sc)}"/>')
def springkikker():
    sh = Sheet(); head(sh, "Springkikker")
    sh.text(100, 26, "Een kikker op een papieren veer: druk hem in en laat los!", 6)
    place(sh, S(frog, 1.15), 10, 34); place(sh, lilypad, 104, 46)
    for i, (y, c) in enumerate(((132, "g"), (158, "y"))):
        acc_strip(sh, 13, y, 174, 14, 14.5, c, glue_start=True)
        sh.text(8, y + 10, "ab"[i].upper(), 7, "end")
    # uitleg heksentrap
    sh.text(100, 190, "Zo vlecht je de veer:", 7)
    ox = 30
    for k, lab in enumerate(["1. plak een hoek", "2. B over A", "3. A over B", "4. herhaal"]):
        bx = 14 + k * 46; by = 202
        if k == 0:
            sh.rect_r(bx + 6, by + 14, 30, 7, "g"); sh.rect_r(bx + 6, by + 14 - 14, 7, 21, "y")
        elif k == 1:
            sh.rect_r(bx + 6, by + 14, 30, 7, "g"); sh.rect_r(bx + 6, by + 14, 7, 21, "y")
        elif k == 2:
            sh.rect_r(bx + 6, by + 14, 7, 21, "y"); sh.rect_r(bx - 4, by + 14, 17, 7, "g")
        else:
            for j in range(4): sh.rect_r(bx + 12 - j * 1.2, by + 22 - j * 6, 12, 6, "gy"[j % 2])
        sh.text(bx + 21, by + 46, lab, 4.6)
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "springkikker-heksentrap", sh, {"category": "dieren", "age": "6-9", "kind": "knipplaat", "difficulty": 3, "minutes": 30,
        "materials": [KLEUR, SCHAAR, LIJM],
        "i18n": {"nl": {"name": "Springkikker op een papieren veer", "steps": [
            "Kleur de kikker, het blad en de twee stroken A en B in.",
            "Knip alles uit langs de streepjeslijn.",
            "Smeer lijm op het grijze vakje van strook A en plak het begin van strook B er haaks op, zodat ze samen een hoek maken.",
            "Vouw strook B over strook A heen, en dan strook A over strook B. Ga zo om en om door tot het einde: dit heet een heksentrap.",
            "Plak de laatste vakjes op elkaar. Plak één kant van de veer op het grijze vakje van het blad en de andere kant onder de kikker.",
            "Druk de kikker naar beneden en laat los: hij springt omhoog!"]}}})
springkikker()

# =====================================================================
# Vallende helikopter (propeller van papier)
# =====================================================================
def helikopters():
    sh = Sheet(); head(sh, "Vallende helikopters")
    sh.text(100, 26, "Laat ze van hoog naar beneden vallen: ze draaien rond!", 6.5)
    W, RH, BH, BF = 48, 92, 66, 18  # breedte, wieken, romp, onderflap
    for i in range(3):
        x0 = 14 + i * (W + 10); y0 = 36; cx = x0 + W / 2; yb = y0 + RH
        c1, c2 = "rbg"[i], "ytp"[i]
        sh.rect_r(x0 + 2.5, y0 + 2.5, W / 2 - 6, RH - 5, c1); sh.rect_r(cx + 3.5, y0 + 2.5, W / 2 - 6, RH - 5, c2)
        for k in range(1, 4): sh.seg(x0 + 3, y0 + k * 18, cx - 3, y0 + k * 18 + 6, "l", "stroke-width:1"); sh.seg(cx + 3, y0 + k * 18 + 6, x0 + W - 3, y0 + k * 18, "l", "stroke-width:1")
        sh.rect_r(x0 + W / 3 + 2.5, yb + 7, W / 3 - 5, BH - 10, "-")
        sh.circle_r(cx, yb + 20, 5, "b")
        sh.rect_r(x0 + 2.5, yb + BH + 2.5, W - 5, BF - 5, "z")
        # knippen en vouwen
        sh.rect_line(x0, y0, W, RH + BH + BF, "cut")
        sh.seg(cx, y0, cx, yb, "cut")
        sh.seg(x0, yb + 4, x0 + W / 3, yb + 4, "cut"); sh.seg(x0 + W * 2 / 3, yb + 4, x0 + W, yb + 4, "cut")
        sh.seg(x0, yb, cx, yb, "fold"); sh.seg(cx, yb, x0 + W, yb, "fold")
        sh.seg(x0 + W / 3, yb + 4, x0 + W / 3, yb + BH, "fold"); sh.seg(x0 + W * 2 / 3, yb + 4, x0 + W * 2 / 3, yb + BH, "fold")
        sh.seg(x0, yb + BH, x0 + W, yb + BH, "fold")
        sh.text(x0 + W / 4, y0 + RH - 6, "A", 7); sh.text(x0 + W * 3 / 4, y0 + RH - 6, "B", 7)
    sh.text(100, 222, "A naar voren, B naar achteren vouwen.", 6.5)
    sh.text(100, 232, "Zijkanten naar binnen en de grijze onderkant omhoog.", 6.5)
    sh.text(100, 242, "Zwaarder maken? Zet een paperclip op de onderkant.", 6)
    sh.legend(["cut", "fold"], 276)
    write(OUT, "vallende-helikopters", sh, {"category": "voertuigen", "age": "6-9", "kind": "vouwblad", "difficulty": 1, "minutes": 15,
        "materials": [KLEUR, SCHAAR],
        "i18n": {"nl": {"name": "Vallende helikopters vouwen", "printNote": "Gewoon printpapier werkt het best: dan draaien de helikopters het snelst.", "steps": [
            "Kleur de helikopters in en knip ze uit langs de buitenste streepjeslijn.",
            "Knip de lange lijn in het midden van de bovenkant in, tot aan de vouwlijn. Zo krijg je twee wieken: A en B.",
            "Knip aan beide kanten het korte lijntje net onder de wieken in.",
            "Vouw de twee zijkanten van de romp naar binnen, over elkaar heen. Vouw de grijze onderkant omhoog.",
            "Vouw wiek A naar voren en wiek B naar achteren, zodat ze recht opzij staan.",
            "Houd de helikopter hoog boven je hoofd aan de onderkant vast en laat los: hij draait rondjes naar beneden!"]}}})
helikopters()
