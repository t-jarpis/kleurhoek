"""Batch 40b: drukke, gedetailleerde scènes voor kinderen van 9+ (eigen tekeningen, 200x200).

Zoals batch 13e is alles een vlakverdeling met shapely: wat later wordt neergelegd ligt bovenop en wordt
uit de vlakken eronder geknipt, zodat kleurvlakken nooit overlappen. Figuren (mensen, dieren, voertuigen)
worden als 'groep' getekend en met stamp() geplaatst, geschaald en eventueel gespiegeld. Kleine details
(ogen, monden, naden) zijn lijnen of stipjes die mee worden afgeknipt als er iets voor komt te liggen.
"""
import math, random, sys
from lib_gen import *
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, MultiPoint, box, GeometryCollection
from shapely.ops import unary_union, polygonize
from shapely import affinity
from shapely.geometry.polygon import orient

MAT = [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}]
ONLY = set(sys.argv[1:])
PAGE = box(0, 0, 200, 200)


# ================================================================ geometrie
def polys(g):
    if g is None or g.is_empty: return []
    if isinstance(g, Polygon): return [g]
    if hasattr(g, "geoms"):
        out = []
        for x in g.geoms: out += polys(x)
        return out
    return []

def lines_of(g):
    if g is None or g.is_empty: return []
    if isinstance(g, LineString): return [g]
    if hasattr(g, "geoms"):
        out = []
        for x in g.geoms: out += lines_of(x)
        return out
    return []

def ring_d(coords):
    c = list(coords)[:-1]
    return "M" + " L".join(f"{f(round(x, 1))} {f(round(y, 1))}" for x, y in c) + "Z"

def poly_d(p):
    p = orient(p, 1.0)
    return ring_d(p.exterior.coords) + "".join(ring_d(i.coords) for i in p.interiors)

def line_d(ln):
    return "M" + " L".join(f"{f(round(x, 1))} {f(round(y, 1))}" for x, y in ln.coords)

def circle(cx, cy, r, res=24): return Point(cx, cy).buffer(r, res)
def ellipse(cx, cy, rx, ry, rot=0):
    e = affinity.scale(Point(0, 0).buffer(1, 32), rx, ry)
    return affinity.translate(affinity.rotate(e, rot, origin=(0, 0)), cx, cy)
def P(points): return Polygon(points).buffer(0)
def rbox(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, 8) if r else box(x0, y0, x1, y1)
def limb(x1, y1, x2, y2, w):
    if (x1, y1) == (x2, y2): return circle(x1, y1, w / 2)
    return LineString([(x1, y1), (x2, y2)]).buffer(w / 2, 12)
def tube(pts, w, cap=1):
    return LineString(pts).buffer(w / 2, 12, cap_style=cap, join_style=1)
def bez(p0, p1, p2, p3, n=16):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0],
             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]) for t in [i / n for i in range(n + 1)]]
def qbez(p0, p1, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]
def leaf(base, tip, w, bend=0.0, n=20):
    (x0, y0), (x1, y1) = base, tip
    L = math.dist(base, tip); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    left, right = [], []
    for i in range(n + 1):
        t = i / n; s = math.sin(math.pi * t) ** .9 * (1 - .25 * t) * w / 2; b = bend * math.sin(math.pi * t) * L
        cx, cy = x0 + ux * L * t + nx * b, y0 + uy * L * t + ny * b
        left.append((cx + nx * s, cy + ny * s)); right.append((cx - nx * s, cy - ny * s))
    return P(left + right[::-1])
def split_lines(g, lines):
    u = unary_union([g.boundary] + [ln.intersection(g.buffer(.01)) for ln in lines])
    return [p for p in polygonize(u) if g.contains(p.representative_point())]
def blob(cx, cy, rx, ry, n=9, bump=.38, seed=0):
    """Bobbelige wolk/kruin: ellips met bolletjes op de rand."""
    rnd = random.Random(seed)
    parts = [ellipse(cx, cy, rx * .82, ry * .82)]
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-.15, .15)
        r = min(rx, ry) * bump * rnd.uniform(.85, 1.15)
        parts.append(circle(cx + (rx - r * .7) * math.cos(a), cy + (ry - r * .7) * math.sin(a), r))
    return unary_union(parts)
def star_poly(cx, cy, r1, r2, n=5, rot=0):
    return P([(cx + (r1 if i % 2 == 0 else r2) * math.sin(math.pi * i / n + rot), cy - (r1 if i % 2 == 0 else r2) * math.cos(math.pi * i / n + rot)) for i in range(2 * n)])
def stripes(g, w, angle, codes, off=0):
    c = g.centroid; out = []
    for k in range(-60, 60):
        b = box(-400, off + k * w, 400, off + (k + 1) * w)
        b = affinity.translate(affinity.rotate(b, angle, origin=(0, 0)), c.x, c.y)
        x = b.intersection(g)
        if not x.is_empty and x.area > .3: out.append((x, codes[k % len(codes)]))
    return out
def wavy_band(y0, y1, amp, wl, ph=0, x0=-5, x1=205):
    top = [(x, y0 + amp * math.sin((x / wl + ph) * 2 * math.pi)) for x in range(x0, x1 + 1, 3)]
    bot = [(x, y1 + amp * math.sin((x / wl + ph + .5) * 2 * math.pi)) for x in range(x1, x0 - 1, -3)]
    return P(top + bot)
def hill(y, amp, wl, ph=0, bottom=205):
    pts = [(x, y - amp * math.sin((x / wl + ph) * 2 * math.pi)) for x in range(-5, 206, 3)]
    return P(pts + [(205, bottom), (-5, bottom)])


# ================================================================ canvas en groepen
class Group:
    """Een figuur in eigen coördinaten: vlakken (in tekenvolgorde), stipjes en detaillijnen."""
    def __init__(self):
        self.items = []
    def add(self, g, code="-"):
        self.items.append(("g", g, code)); return self
    def dot(self, x, y, r=1.0):
        self.items.append(("dot", Point(x, y), r)); return self
    def ln(self, pts, w=1.2):
        self.items.append(("ln", LineString(pts), w)); return self
    def ext(self, other):
        self.items += other.items; return self

class Canvas:
    def __init__(self, clip=PAGE):
        self.items = []; self.deco = []; self.clip = clip
    def put(self, g, code="-"):
        g = g.buffer(0).intersection(self.clip)
        if g.is_empty: return
        self._cut(g); self.items.append((g, code))
    def put_many(self, pieces):
        pieces = [(g.buffer(0).intersection(self.clip), c) for g, c in pieces]
        pieces = [(g, c) for g, c in pieces if not g.is_empty]
        if not pieces: return
        self._cut(unary_union([g for g, _ in pieces]))
        self.items += pieces
    def _cut(self, g):
        new = []
        for h, c in self.items:
            if h.intersects(g):
                d = h.difference(g)
                if not d.is_empty: new.append((d, c))
            else: new.append((h, c))
        self.items = new
        nd = []
        for kind, h, w in self.deco:
            if not h.intersects(g): nd.append((kind, h, w)); continue
            if kind == "dot": continue
            d = h.difference(g)
            for l in lines_of(d):
                if l.length > .8: nd.append((kind, l, w))
        self.deco = nd
    def dot(self, x, y, r=1.0):
        self.deco.append(("dot", Point(x, y), r))
    def ln(self, pts, w=1.2):
        ln = LineString(pts).intersection(self.clip)
        for l in lines_of(ln): self.deco.append(("ln", l, w))
    def stamp(self, grp, x=0, y=0, s=1.0, flip=False, rot=0):
        sx = -s if flip else s
        def T(g):
            g = affinity.scale(g, sx, s, origin=(0, 0))
            if rot: g = affinity.rotate(g, rot, origin=(0, 0))
            return affinity.translate(g, x, y)
        for kind, g, v in grp.items:
            if kind == "g": self.put(T(g), v)
            elif kind == "dot":
                p = T(g); self.dot(p.x, p.y, v * s)
            else:
                self.ln(list(T(g).coords), v * max(.7, min(1.2, s)))
    def finish(self, sh, minw=1.4, mina=8, simplify=.12):
        parts = []
        for g, c in self.items:
            for p in polys(g):
                if p.area > .05: parts.append([p, c])
        for _ in range(6):
            small = [i for i, (p, c) in enumerate(parts) if p.area < mina or p.buffer(-minw).is_empty]
            if not small: break
            alive = [True] * len(parts)
            for i in sorted(small, key=lambda i: parts[i][0].area):
                if not alive[i]: continue
                p = parts[i][0]; best, bl = None, 0.05
                pb = p.buffer(.08)
                for j, (q, c) in enumerate(parts):
                    if j == i or not alive[j] or not q.intersects(pb): continue
                    L = q.boundary.intersection(pb).length
                    if L > bl: best, bl = j, L
                alive[i] = False
                if best is not None:
                    parts[best][0] = unary_union([parts[best][0], p.buffer(.06)]).buffer(-.06)
            parts = [x for k, x in enumerate(parts) if alive[k]]
            parts = [[p, c] for g, c in parts for p in polys(g)]
        n = 0
        for p, c in parts:
            p = p.buffer(-.45, join_style=2, mitre_limit=3).buffer(.45, join_style=2, mitre_limit=3)
            p = p.simplify(simplify, preserve_topology=True)
            if p.is_empty: continue
            p = unary_union([Polygon(q.exterior, [i for i in q.interiors if Polygon(i).area > 4]) for q in polys(p)])
            for q in polys(p): sh.region(poly_d(q), c); n += 1
        for kind, g, w in self.deco:
            if kind == "dot": sh.dot(g.x, g.y, w)
            else: sh.line(line_d(g), "l", f"stroke-width:{f(round(w, 2))}")
        return n

def kp9(slug, name, desc, fn, cat, diff=3):
    if ONLY and slug not in ONLY: return
    sh = Sheet(200); cv = Canvas()
    fn(cv)
    cv.finish(sh)
    meta = {"category": cat, "age": "9+", "kind": "kleurplaat", "difficulty": diff, "materials": MAT, "i18n": {"nl": {"name": name, "description": desc}}}
    write(OUT, slug, sh, meta)
    print(f"{slug}: {len(sh.codes)} vlakken")


# ================================================================ bouwstenen: mensen
HANDS = {"down": ((-12, -23), (12, -23)), "up": ((-15, -64), (15, -64)), "wave": ((-12, -23), (16, -60)),
         "hold": ((-6, -31), (6, -31)), "hips": ((-12, -33), (12, -33)), "walk": ((-13, -25), (11, -22)),
         "point": ((-12, -23), (23, -45)), "carry": ((-10, -40), (10, -40)), "side": ((-20, -36), (20, -36))}

def person(shirt="r", pants="n", hair="w", style="short", pose="down", skirt=None, hat=None, shoes="x", face=True, back=False, legs=True, hands=None):
    """Persoon van voren, voeten op (0,0), ongeveer 62 hoog."""
    g = Group()
    hl, hr = hands or HANDS.get(pose, HANDS["down"])
    feet = ((-4.5, -2.5), (4.5, -2.5)) if pose != "walk" else ((-7, -2.5), (6, -2.5))
    front_arms = pose in ("hold", "carry")
    if style == "long" and not hat:
        g.add(rbox(-10, -59, 10, -39, 5), hair)
    if style == "pony" and not hat:
        g.add(ellipse(10, -54, 3.4, 7, -25), hair)
    if style == "braids" and not hat:
        for s in (-1, 1): g.add(tube([(s * 8, -52), (s * 10, -44), (s * 10.5, -40)], 3.6), hair)
    if legs:
        for (fx, fy), sx in zip(feet, (-1, 1)): g.add(limb(sx * 4.2, -24, fx, fy - 1.5, 6.6), pants)
        if shoes:
            for fx, fy in feet: g.add(ellipse(fx + (-1.5 if fx < 0 else 1.5), fy, 4.6, 2.6), shoes)
    if not front_arms:
        for (hx, hy), sx in zip((hl, hr), (-1, 1)): g.add(limb(sx * 7.5, -42, hx, hy, 5.4), shirt)
    g.add(rbox(-9, -46, 9, -21, 4), shirt)
    if skirt: g.add(P([(-9, -28), (9, -28), (13.5, -15), (-13.5, -15)]), skirt)
    if front_arms:
        for (hx, hy), sx in zip((hl, hr), (-1, 1)): g.add(limb(sx * 7.5, -42, hx, hy, 5.4), shirt)
    for hx, hy in (hl, hr): g.add(circle(hx, hy, 2.8), "-")
    g.add(circle(0, -53, 8), "-")
    if back: g.add(circle(0, -53, 8.4), hair)
    elif hat in ("helmet", "beanie", "chef", "cap", "pirate", "crown"):
        pass
    elif style == "curly":
        g.add(unary_union([circle(8 * math.cos(math.radians(a)), -53 + 8 * math.sin(math.radians(a)), 3.4) for a in range(170, 380, 26)]).difference(ellipse(0, -50, 6.4, 5.4)), hair)
    elif style == "bald":
        pass
    else:
        g.add(circle(0, -53, 8.8).difference(ellipse(0, -50.2, 7.6, 6.6)), hair)
    if style == "bun" and not hat: g.add(circle(0, -63.5, 3.8), hair)
    if hat == "cap":
        g.add(Point(0, -53).buffer(8.8, 24).intersection(box(-12, -66, 12, -54)), "r"); g.add(ellipse(8, -54.5, 6, 1.6), "r")
    elif hat == "helmet":
        g.add(Point(0, -53).buffer(9.4, 24).intersection(box(-12, -66, 12, -54)).union(rbox(-10.6, -56, 10.6, -53, 1)), "y")
    elif hat == "beanie":
        g.add(Point(0, -54).buffer(9, 24).intersection(box(-12, -66, 12, -55)).union(rbox(-9.6, -57, 9.6, -53.5, 1.5)), "r"); g.add(circle(0, -63.5, 2.6), "-")
    elif hat == "chef":
        g.add(unary_union([box(-7, -66, 7, -57), circle(-5, -67, 4.5), circle(5, -67, 4.5), circle(0, -70, 5)]), "-")
    elif hat == "straw":
        g.add(unary_union([ellipse(0, -59, 15, 2.6), rbox(-7, -67, 7, -59, 2)]), "y")
    elif hat == "pirate":
        g.add(P([(-14, -56), (0, -68), (14, -56), (0, -59)]), "x")
    elif hat == "crown":
        g.add(P([(-8, -57), (-9, -67), (-4.5, -62), (0, -68), (4.5, -62), (9, -67), (8, -57)]), "y")
    if face and not back:
        g.dot(-3, -51.6, .95); g.dot(3, -51.6, .95)
        g.ln(qbez((-2.4, -48.2), (0, -46.6), (2.4, -48.2), 6), .9)
    return g

def knight(code="z", plume="r", shield="r", horse=False):
    g = Group()
    g.add(limb(-7.5, -42, -10, -24, 5.6), code)
    g.add(tube([(7.5, -42), (13, -30), (16, -46)], 5.4), code)
    g.add(tube([(16, -43), (17, -75)], 3), "z")
    g.add(P([(15, -44), (19, -44), (17, -49)]), "z")
    for s in (-1, 1): g.add(limb(s * 4.2, -24, s * 4.5, -4, 6.6), code)
    for s in (-1, 1): g.add(ellipse(s * 6, -2.5, 4.6, 2.6), "x")
    g.add(rbox(-9, -46, 9, -21, 4), code)
    g.add(P([(-9, -30), (9, -30), (10, -20), (-10, -20)]), "y")
    g.add(Point(0, -54).buffer(8.6, 24).union(box(-8.6, -54, 8.6, -45)), code)
    g.add(box(-6, -55.5, 6, -53), "x")
    g.add(tube(qbez((0, -62), (-6, -70), (-12, -62), 8), 3.5), plume)
    sh_ = P([(-17, -44), (-3, -44), (-3, -32), (-10, -22), (-17, -32)])
    g.add(sh_, shield); g.add(P([(-11.5, -42), (-8.5, -42), (-8.5, -36), (-4, -36), (-4, -33), (-8.5, -33), (-8.5, -26), (-11.5, -26), (-11.5, -33), (-16, -33), (-16, -36), (-11.5, -36)]).intersection(sh_.buffer(-1.5)), "y")
    return g

# ================================================================ bouwstenen: natuur
def tree(h=60, crown="g", trunk="w", seed=1, w=None):
    """Loofboom, voet op (0,0)."""
    w = w or h * .45
    g = Group()
    g.add(P([(-3.5, 0), (-2.6, -h * .45), (2.6, -h * .45), (3.5, 0)]), trunk)
    g.add(blob(0, -h * .62, w, h * .36, 9, .4, seed), crown)
    rnd = random.Random(seed)
    for k in range(3):
        x = rnd.uniform(-w * .45, w * .45); y = -h * .62 + rnd.uniform(-h * .15, h * .15)
        g.ln(qbez((x - 4, y), (x, y + 3), (x + 4, y), 5), 1)
    return g

def pine(h=50, code="g", trunk="w", snow=False):
    g = Group(); g.add(box(-2.6, -h * .18, 2.6, 0), trunk)
    for k in range(3):
        y0 = -h * .14 - k * h * .26; w = h * (.38 - k * .09)
        g.add(P([(-w, y0), (0, y0 - h * .4), (w, y0)]), code)
        if snow:
            tip = y0 - h * .4
            g.add(P([(-w * .32, tip + h * .13), (0, tip), (w * .32, tip + h * .13), (w * .1, tip + h * .1), (-w * .08, tip + h * .14)]), "-")
    return g

def palm(h=60, lean=8, code="g"):
    g = Group()
    pts = qbez((0, 0), (lean * .2, -h * .5), (lean, -h), 12)
    g.add(tube(pts, 5.5, 2), "w")
    for i in range(1, 6):
        a, b = pts[int(i * 2) - 1], pts[int(i * 2)]
        g.ln([(a[0] - 3, a[1] + .5), (a[0] + 3, a[1] - .5)], .9)
    top = pts[-1]
    for ang in (200, 240, 285, 320, 350, 20):
        a = math.radians(ang)
        tip = (top[0] + 26 * math.cos(a), top[1] + 26 * math.sin(a) * .7 + 8)
        g.add(leaf(top, tip, 9, .12 if ang < 270 else -.12), code)
    for dx in (-2.5, 2.5): g.add(circle(top[0] + dx, top[1] + 3, 2.6), "w")
    return g

def bush(w=20, h=12, code="g", seed=2, berries=None):
    g = Group(); g.add(blob(0, -h / 2, w / 2, h / 2, 7, .45, seed).intersection(box(-w, -h * 2, w, 0)), code)
    if berries:
        rnd = random.Random(seed)
        for k in range(3): g.add(circle(rnd.uniform(-w * .3, w * .3), -h * rnd.uniform(.35, .7), 1.8), berries)
    return g

def flower(x, y, r=3, petal="m", heart="y", stem=8):
    g = Group()
    if stem: g.ln([(x, y), (x, y + stem)], 1)
    g.add(unary_union([circle(x + r * math.cos(math.radians(72 * k - 90)), y + r * math.sin(math.radians(72 * k - 90)), r * .75) for k in range(5)]), petal)
    g.add(circle(x, y, r * .55), heart)
    return g

def cloud(cx, cy, w, seed=3):
    return blob(cx, cy, w / 2, w / 4.2, 7, .5, seed).intersection(box(cx - w, cy - w, cx + w, cy + w / 6))

def sun_rays(cv, x, y, r=12, n=10, code="y", ray_code="o"):
    for k in range(n):
        a = 2 * math.pi * k / n
        cv.put(P([(x + (r + 2) * math.cos(a - .12), y + (r + 2) * math.sin(a - .12)), (x + (r + 9) * math.cos(a), y + (r + 9) * math.sin(a)), (x + (r + 2) * math.cos(a + .12), y + (r + 2) * math.sin(a + .12))]), ray_code)
    cv.put(circle(x, y, r, 32), code)

def grass_tufts(cv, xs, y):
    for x in xs: cv.ln([(x - 2, y), (x - 3, y - 4)], .9); cv.ln([(x, y), (x, y - 5)], .9); cv.ln([(x + 2, y), (x + 3, y - 4)], .9)


# ================================================================ bouwstenen: gebouwen
def facade(w, h, code="o", roof="punt", roof_code="r", win="b", cols=None, rows=None, door=True, door_code="w", shop=None, awning=None):
    """Huis van voren, linksonder op (0,0)."""
    g = Group()
    if roof == "punt": g.add(P([(-3, -h), (w / 2, -h - w * .55), (w + 3, -h)]), roof_code)
    elif roof == "trap":
        g.add(unary_union([box(w * .1, -h - 8, w * .9, -h), box(w * .25, -h - 15, w * .75, -h - 8), box(w * .4, -h - 21, w * .6, -h - 15)]), code)
    elif roof == "hals":
        g.add(unary_union([box(w * .15, -h - 10, w * .85, -h), Point(w / 2, -h - 10).buffer(w * .35, 24).intersection(box(0, -h - 30, w, -h - 10))]), code)
    elif roof == "plat":
        g.add(box(-1.5, -h - 3, w + 1.5, -h), roof_code)
    g.add(box(0, -h, w, 0), code)
    cols = cols or max(1, int(w // 12)); rows = rows or max(1, int((h - (22 if (door or shop) else 6)) // 15))
    ww = min(8, w / cols * .55); wh = 9
    top = -h + 6
    for r in range(rows):
        for c in range(cols):
            x = w * (c + .5) / cols
            y = top + r * 15
            g.add(box(x - ww / 2, y, x + ww / 2, y + wh), win)
            g.ln([(x, y), (x, y + wh)], .8); g.ln([(x - ww / 2, y + wh / 2), (x + ww / 2, y + wh / 2)], .8)
    if shop:
        g.add(box(3, -19, w - 3, -1), shop)
        if awning:
            n = max(3, int(w // 6))
            for k in range(n):
                g.add(P([(1 + (w - 2) * k / n, -24), (1 + (w - 2) * (k + 1) / n, -24), (1 + (w - 2) * (k + 1) / n, -19), (1 + (w - 2) * (k + .5) / n, -17.5), (1 + (w - 2) * k / n, -19)]), awning[k % len(awning)])
        if door: g.add(box(w - 12, -17, w - 5, -1), door_code)
    elif door:
        g.add(rbox(w / 2 - 4.5, -16, w / 2 + 4.5, 0, 1.5), door_code)
        g.dot(w / 2 + 2.5, -8, .7)
    return g


# ================================================================ bouwstenen: dieren (van opzij, kijkend naar rechts, poten op y=0)
def legs4(xs, top, w, code, foot=None, far=False):
    g = Group()
    for x in xs:
        g.add(rbox(x - w / 2, top, x + w / 2, 0, w * .35), code)
        if foot: g.add(box(x - w / 2 - .3, -2.4, x + w / 2 + .3, 0.2).intersection(rbox(x - w / 2, top, x + w / 2, 0, w * .35)), foot)
    return g

def cow(main="-", spot="x"):
    g = Group()
    g.ext(legs4((-7, 13), -16, 4.4, main, "x"))
    g.ln([(-16, -24), (-18.5, -15), (-19, -10)], 1.4); g.add(ellipse(-19, -8, 2.2, 3.4), "x")
    body = rbox(-17, -28, 15, -11, 7)
    sil = unary_union([body, P([(9, -27), (17, -32), (21, -22), (12, -14)]), rbox(15, -34, 25, -20, 4), legs4((-12, 8), -16, 4.6, main).items[0][1], legs4((8,), -16, 4.6, main).items[0][1]])
    g.add(sil, main)
    for x, y, rx, ry in ((-9, -21, 5.5, 4.5), (4, -24, 4, 3.4), (-1, -14, 3.6, 2.6)): g.add(ellipse(x, y, rx, ry).intersection(body), spot)
    g.ext(legs4((-12, 8), -3, 4.6, main, "x"))
    g.add(ellipse(1, -10.5, 4, 2.3), "k")
    g.add(ellipse(23, -21.5, 4.6, 3.6), "k"); g.dot(22.2, -21.5, .6); g.dot(25, -21.5, .6)
    g.add(ellipse(13.5, -31, 4, 1.8, -20), main)
    g.add(tube(qbez((17, -33), (16.5, -38), (20.5, -39), 5), 2.8), "y")
    g.dot(19, -28.5, .9)
    return g

def horse(main="w", mane="x", zebra=False):
    g = Group()
    g.ext(legs4((-8, 12), -20, 4, main, "x"))
    g.add(P([(-15, -30), (-21, -26), (-23, -11), (-19, -13), (-17, -24)]), mane)
    body = rbox(-17, -34, 15, -18, 7.5)
    neck = P([(3, -32), (10, -47), (19, -48), (14, -23)])
    head = unary_union([ellipse(20, -42, 9, 4.8, 42), circle(16, -46, 4.4)])
    legs = unary_union([rbox(x - 2, -20, x + 2, 0, 1.2) for x in (-12, 8)])
    sil = unary_union([body, neck, head, legs])
    g.add(sil, main)
    if zebra:
        for k in range(-4, 5):
            band = P([(k * 6.5 - 1, -60), (k * 6.5 + 1, -60), (k * 6.5 + 3.6, -12), (k * 6.5 + 1.6, -12)])
            g.add(band.intersection(unary_union([body, neck]).buffer(-.3)), "x")
    g.add(P([(1.5, -33), (8.5, -48.5), (12.5, -49.5), (6.5, -31)]).buffer(.6), mane)
    g.add(P([(13, -48), (13.5, -54), (17, -49)]), main)
    for x in (-12, 8): g.add(box(x - 2.4, -2.4, x + 2.4, .2).intersection(legs), "x")
    g.dot(18.5, -45.5, .95); g.dot(25.8, -37, .65)
    return g

def pig(main="k"):
    g = Group()
    g.ext(legs4((-5, 10), -6, 4.4, main))
    g.ln([(-14, -14), (-17, -16), (-18, -13), (-16, -12), (-17.5, -17.5)], 1)
    sil = unary_union([ellipse(0, -12, 14, 8.5), circle(12, -14, 6.2), rbox(-11.2, -6, -6.8, 0, 1.5), rbox(5.8, -6, 10.2, 0, 1.5)])
    g.add(sil, main)
    g.add(ellipse(18.5, -13, 2.4, 3.4), "m"); g.dot(18.5, -14.4, .5); g.dot(18.5, -11.6, .5)
    g.add(P([(9, -18), (13, -24), (15.5, -17)]), main)
    g.dot(14.5, -15.5, .9)
    return g

def sheep(main="-", face="x"):
    g = Group()
    g.ext(legs4((-5, 9), -8, 3, face))
    g.ext(legs4((-9, 5), -8, 3, face))
    g.add(blob(0, -15, 13, 8.5, 11, .42, 4), main)
    g.add(ellipse(14, -19, 4.8, 3.6, 25), face)
    g.add(ellipse(10.5, -20.5, 3.2, 1.5, -20), face)
    g.add(blob(10, -23, 3.5, 2.5, 5, .5, 2), main)
    g.dot(15, -20.2, .7)
    return g

def goat(main="-"):
    g = Group()
    g.ext(legs4((-5, 10), -14, 2.8, main, "x"))
    g.add(P([(-12, -21), (-15, -25), (-12, -18)]), main)
    body = rbox(-12, -23, 11, -12, 5)
    sil = unary_union([body, P([(5, -22), (11, -33), (16, -31), (11, -15)]), ellipse(16, -30, 5.5, 3.2, 30), unary_union([rbox(x - 1.4, -14, x + 1.4, 0, 1) for x in (-8, 7)])])
    g.add(sil, main)
    for x in (-8, 7): g.add(box(x - 1.7, -2.2, x + 1.7, .2).intersection(sil), "x")
    g.add(tube(qbez((12, -33), (10, -40), (5, -38), 6), 3), "z")
    g.add(ellipse(10, -31.5, 3, 1.4, 20), main)
    g.add(P([(17, -26.5), (20, -26), (18, -21)]), main)
    g.dot(15.5, -31.5, .8)
    return g

def dog(main="o", ear="w"):
    g = Group()
    g.ext(legs4((-4, 9), -10, 3.2, main))
    g.add(tube(qbez((-10, -14), (-15, -18), (-14, -25), 6), 3.4), main)
    sil = unary_union([ellipse(0, -13, 11, 5.5), circle(11, -20, 4.8), ellipse(15.5, -18.5, 4, 2.6), unary_union([rbox(x - 1.7, -10, x + 1.7, 0, 1) for x in (-7, 6)])])
    g.add(sil, main)
    g.add(ellipse(8.5, -19.5, 2.4, 4.6, 15), ear)
    g.add(circle(19.3, -19, 1.4), "x")
    g.dot(12.5, -21.5, .8)
    return g

def cat(main="z"):
    g = Group()
    g.add(tube(bez((-7, -6), (-15, -5), (-15, -17), (-11, -20), 10), 3.4), main)
    sil = unary_union([ellipse(0, -6.5, 8.5, 6.5), circle(4, -16, 5.2), P([(-.5, -18), (0, -24.5), (3.5, -20)]), P([(4.5, -20), (8, -24.5), (8.7, -18)]), ellipse(-3.5, -.9, 3, 1.6), ellipse(4, -.9, 3, 1.6)])
    g.add(sil, main)
    g.dot(2.2, -16.5, .7); g.dot(6, -16.5, .7)
    g.ln([(8, -14), (12, -15)], .6); g.ln([(8, -13), (12, -12)], .6)
    return g

def rabbit(main="-"):
    g = Group()
    g.add(circle(-8.5, -7, 2.8), "-")
    sil = unary_union([ellipse(0, -6.5, 8.5, 6.2), circle(6.5, -11, 4.6), ellipse(5, -18, 1.9, 6.2, 12), ellipse(8.2, -17.5, 1.9, 6.2, 28), ellipse(4.5, -.9, 3.6, 1.6)])
    g.add(sil, main)
    g.add(ellipse(5, -18, .8, 4, 12), "k")
    g.dot(8.2, -11.8, .7)
    return g

def chicken(main="-", comb="r"):
    g = Group()
    g.ln([(-1, -4.5), (-1.5, 0)], 1.2); g.ln([(2, -4.5), (3, 0)], 1.2)
    sil = unary_union([ellipse(0, -8.5, 8, 5.5), circle(6, -14.5, 3.8), P([(-6, -9), (-13, -17), (-11, -6)])])
    g.add(sil, main)
    g.add(unary_union([circle(4.6, -18.5, 1.5), circle(6.6, -19, 1.5), circle(8.4, -18, 1.3)]), comb)
    g.add(P([(9.4, -15.5), (12.6, -14.4), (9.4, -13.2)]), "o")
    g.add(ellipse(10, -11.6, 1.2, 1.8), comb)
    g.add(ellipse(-1, -8.5, 4.6, 2.8, -12), main)
    g.dot(7, -15.4, .7)
    return g

def duck(main="-", bill="o"):
    g = Group()
    sil = unary_union([ellipse(0, -5, 10, 5), circle(7, -12.5, 4.2), P([(-8, -5), (-13, -10), (-7, -9)])])
    g.add(sil, main)
    g.add(ellipse(12, -11.6, 3.6, 1.7), bill)
    g.add(ellipse(-1, -6, 5.5, 2.6, -8), main)
    g.dot(8, -13.6, .7)
    return g

def bird(main="b", wing=None, beak="o"):
    g = Group()
    sil = unary_union([ellipse(0, -4.5, 7, 4.5), circle(5.5, -8.5, 3.6), P([(-5, -5), (-12, -7), (-11, -2)])])
    g.add(sil, main)
    g.add(P([(8.6, -9.6), (12.2, -8.5), (8.6, -7.3)]), beak)
    g.add(ellipse(-1, -4.5, 4.2, 2.3, -15), wing or main); g.dot(6.5, -9.5, .7)
    return g

def fish(body="o", fin="y", band=None):
    g = Group()
    g.add(P([(-8, 0), (-15, -6.5), (-13, 0), (-15, 6.5)]), fin)
    g.add(P([(-4, -5), (1, -9.5), (5, -5)]), fin)
    b = ellipse(0, 0, 10, 6)
    g.add(b, body)
    if band:
        for x in (-4, 2): g.add(box(x - 1.5, -8, x + 1.5, 8).intersection(b), band)
    g.ln([(5, -4.5), (4, 0), (5, 4.5)], .8)
    g.dot(7, -1.5, .8)
    return g

def giraffe(main="y", spot="w"):
    g = Group()
    g.ext(legs4((-6, 13), -26, 4.2, main, "x"))
    g.ln([(-15, -34), (-18, -23)], 1.3); g.add(ellipse(-18, -22, 1.8, 3), "x")
    body = ellipse(0, -33, 16, 9, -8)
    neck = P([(3, -37), (15, -72), (23, -70), (14, -28)])
    head = unary_union([ellipse(22, -72, 8, 4.4, 25), circle(18, -75, 4)])
    legs = unary_union([rbox(x - 2.1, -30, x + 2.1, 0, 1.2) for x in (-10, 9)])
    sil = unary_union([body, neck, head, legs])
    g.add(sil, main)
    pts = [(-9, -35), (1, -37), (-3, -28), (9, -31), (11, -44), (15, -56), (-13, -29)]
    rnd = random.Random(5)
    for x, y in pts:
        sp = P([(x + 3.2 * math.cos(a) * rnd.uniform(.8, 1.15), y + 2.8 * math.sin(a) * rnd.uniform(.8, 1.15)) for a in [k * math.pi / 3 for k in range(6)]])
        g.add(sp.intersection(unary_union([body, neck]).buffer(-1.8)), spot)
    for x in (-10, 9): g.add(box(x - 2.5, -2.6, x + 2.5, .2).intersection(legs), "x")
    for dx in (0, 3.5): g.ln([(16 + dx, -78), (15.5 + dx, -82)], 1.3); g.add(circle(15.5 + dx, -83, 1.8), "w")
    g.add(ellipse(13, -76, 3.4, 1.6, -15), main)
    g.dot(19.5, -75, 1)
    return g

def elephant(main="z"):
    g = Group()
    g.ext(legs4((-6, 14), -14, 7, main))
    g.add(tube([(-17, -26), (-21, -16)], 1.4), main)
    sil = unary_union([ellipse(0, -24, 18, 13), circle(17, -30, 9.5), tube(bez((23, -29), (30, -24), (28, -12), (32, -6), 10), 5.5), unary_union([rbox(x - 3.6, -14, x + 3.6, 0, 1.5) for x in (-11, 8)])])
    g.add(sil, main)
    g.add(ellipse(11, -27, 7, 9.5, 10), main)
    g.add(tube(qbez((22.5, -22), (25, -18), (29, -19), 6), 2.2), "-")
    g.dot(19.5, -32, 1)
    for x in (-11, 8):
        for d in (-2, 0, 2): g.ln([(x + d, -1), (x + d, -.2)], .8)
    return g

def lion(main="o", mane="w"):
    g = Group()
    g.ext(legs4((-5, 11), -10, 4, main))
    g.ln(qbez((-13, -15), (-20, -14), (-21, -6), 8), 1.4); g.add(ellipse(-21, -4, 2.4, 3.2), mane)
    sil = unary_union([ellipse(0, -15, 14, 7.5), unary_union([rbox(x - 2, -10, x + 2, 0, 1.2) for x in (-9, 7)])])
    g.add(sil, main)
    g.add(blob(14, -21, 9, 9, 11, .4, 7), mane)
    g.add(circle(16, -20.5, 5.6), main)
    g.add(circle(13.5, -25.5, 2), main)
    g.add(ellipse(20.5, -18.5, 2.3, 1.8), main)
    g.dot(17.5, -22, .85); g.dot(22.4, -19.2, .7)
    return g

def tiger(main="o"):
    g = Group()
    g.ext(legs4((-6, 12), -9, 4, main))
    g.add(tube(qbez((-14, -13), (-22, -16), (-24, -24), 8), 3.4), main)
    body = ellipse(0, -13, 15, 6.8)
    sil = unary_union([body, circle(16, -17, 5.8), unary_union([rbox(x - 2, -9, x + 2, 0, 1.2) for x in (-10, 8)])])
    g.add(sil, main)
    for k in range(-3, 4):
        g.add(P([(k * 4.2 - 1.2, -21), (k * 4.2 + 1.2, -21), (k * 4.2 + .5, -12)]).intersection(body.buffer(-.4)), "x")
    g.add(P([(14, -23.5), (13, -27), (16.5, -24)]), main); g.add(P([(17.5, -23.5), (19, -26.5), (20, -22)]), main)
    g.add(ellipse(21, -15.5, 2.2, 1.8), "-")
    g.dot(17.6, -18.6, .85); g.dot(23, -16, .7)
    return g

def monkey(main="w", face="k"):
    """Zittend aapje van voren, zitvlak op (0,0)."""
    g = Group()
    g.add(tube(bez((6, -3), (16, -2), (17, -14), (12, -18), 10), 2), main)
    for s in (-1, 1): g.add(tube([(s * 4, -4), (s * 8, -1)], 3.6), main)
    g.add(ellipse(0, -9, 7, 8.5), main)
    g.add(ellipse(0, -7.5, 4, 5.5), face)
    for s in (-1, 1): g.add(tube([(s * 5, -14), (s * 9, -6)], 3), main)
    for s in (-1, 1): g.add(circle(s * 8, -24, 2.8), main)
    g.add(circle(0, -23, 7), main)
    g.add(unary_union([circle(-2.3, -24.5, 2.7), circle(2.3, -24.5, 2.7), ellipse(0, -20.5, 4.4, 3)]), face)
    for s in (-1, 1): g.add(circle(s * 8, -24, 1.2), face)
    g.dot(-2.2, -24.5, .8); g.dot(2.2, -24.5, .8)
    g.ln(qbez((-1.8, -20), (0, -18.8), (1.8, -20), 5), .7)
    return g

def penguin(main="x"):
    g = Group()
    g.add(ellipse(-2.5, -1, 3, 1.4), "o"); g.add(ellipse(2.5, -1, 3, 1.4), "o")
    g.add(unary_union([ellipse(0, -10, 6.5, 9.5), circle(0, -21, 5)]), main)
    g.add(ellipse(0, -9.5, 4.5, 7.5).union(ellipse(0, -20, 3.4, 3)), "-")
    for s in (-1, 1): g.add(ellipse(s * 6.5, -11, 1.8, 6, s * -12), main)
    g.add(P([(-1.5, -19.5), (1.5, -19.5), (0, -17)]), "o")
    g.dot(-1.4, -21.5, .7); g.dot(1.4, -21.5, .7)
    return g

def flamingo(main="m"):
    g = Group()
    g.ln([(0, 0), (0, -16)], 1.2); g.ln([(0, -10), (-5, -13), (0, -15)], 1.2)
    g.add(unary_union([ellipse(0, -20, 8.5, 5, -10), P([(-6, -21), (-13, -19), (-7, -17)])]), main)
    g.add(leaf((5, -22), (-8, -19), 5.5, .05), main)
    g.add(tube(bez((6, -21), (11, -27), (2, -32), (5, -38), 10), 3.2), main)
    g.add(circle(6.5, -39, 2.8), main)
    g.add(P([(8.4, -40.5), (11.5, -38), (10.5, -34.5), (8.8, -37)]), "x")
    g.dot(6, -39.6, .55)
    return g

def parrot(main="r", wing="b"):
    g = Group()
    g.add(P([(-3, -3), (-7, 13), (-3, 11.5), (0, 14), (2, -2)]), wing)
    g.add(ellipse(0, -6, 5, 8, 12), main)
    g.add(leaf((1, -10), (-3, 4), 6, .05), wing)
    g.add(circle(2, -14.5, 4.2), main)
    g.add(P([(5.5, -16.5), (8.8, -14.5), (8, -11.5), (5.8, -12)]), "-")
    g.add(ellipse(2.8, -15, 1.8, 1.6), "-"); g.dot(3, -15, .65)
    return g

def toucan(main="x", bill="o"):
    g = Group()
    g.add(P([(-2, 0), (-4, 9), (0, 9), (1, 0)]), main)
    g.add(ellipse(0, -6, 4.8, 7.5, 12), main)
    g.add(ellipse(2.4, -9, 2.6, 3.6), "-")
    g.add(circle(1.5, -13.5, 3.8), main)
    g.add(P([(4, -16), (12, -14), (14, -11), (4.5, -11)]), bill)
    g.dot(2.5, -14.4, .7)
    return g

def frog(main="g"):
    g = Group()
    g.add(ellipse(-6, -1.5, 4, 2), main); g.add(ellipse(6, -1.5, 4, 2), main)
    g.add(ellipse(0, -5, 7.5, 5), main)
    for s in (-1, 1): g.add(circle(s * 3.6, -10, 2.8), main); g.add(circle(s * 3.6, -10, 1.4), "-")
    g.dot(-3.6, -10, .6); g.dot(3.6, -10, .6)
    g.ln(qbez((-3.5, -5), (0, -3), (3.5, -5), 6), .8)
    return g

def snake(pts, main="l", band="g", w=4.4):
    g = Group(); ln = LineString(pts); body = ln.buffer(w / 2, 12, cap_style=1)
    g.add(body, main)
    L = ln.length
    for k in range(1, int(L / 7)):
        p = ln.interpolate(k * 7); q = ln.interpolate(min(L, k * 7 + .6))
        dx, dy = q.x - p.x, q.y - p.y; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d * w, dx / d * w
        g.add(LineString([(p.x - nx, p.y - ny), (p.x + nx, p.y + ny)]).buffer(1, cap_style=2).intersection(body), band)
    end = pts[-1]; prev = pts[-2]
    a = math.atan2(end[1] - prev[1], end[0] - prev[0])
    g.add(ellipse(end[0] + math.cos(a) * 2, end[1] + math.sin(a) * 2, 4.2, 3, math.degrees(a)), main)
    g.dot(end[0] + math.cos(a) * 3 - math.sin(a) * 1.4, end[1] + math.sin(a) * 3 - 1.4 * math.cos(a), .6)
    return g

def turtle(shell="g", main="l"):
    g = Group()
    for x, y in ((-7, 3), (7, 3), (-8, -4), (8, -4)): g.add(ellipse(x, y, 4.5, 2.2, 30 if x > 0 else -30), main)
    g.add(ellipse(12, -1, 4, 3), main)
    sh_ = ellipse(0, -1, 10, 7)
    g.add(sh_, shell)
    g.add(P([(-4, -4), (0, -6), (4, -4), (4, 1), (0, 3), (-4, 1)]), "y")
    g.dot(13.5, -2, .7)
    return g

def crab(main="r"):
    g = Group()
    for s in (-1, 1):
        for k in range(3): g.ln([(s * 5, -2 + k * 1.5), (s * 10, 1 + k * 2), (s * 11, 4 + k * 2)], 1.3)
        g.add(tube([(s * 6, -5), (s * 10, -10)], 3), main)
        g.add(P([(s * 9, -9), (s * 14.5, -17), (s * 13.5, -11), (s * 10.5, -13), (s * 11.5, -16)]).buffer(1.4), main)
    g.add(ellipse(0, -2, 8.5, 5.5), main)
    for s in (-1, 1): g.ln([(s * 2, -6), (s * 3, -9)], 1); g.add(circle(s * 3, -10.5, 2), "-")
    g.dot(-3, -10.5, .6); g.dot(3, -10.5, .6)
    return g

def octopus(main="p", spots=None):
    g = Group()
    for k in range(6):
        x0 = -7.5 + k * 3
        g.add(tube(bez((x0, -4), (x0 + (k - 2.5) * 2, 2), (x0 + (k - 2.5) * 4 - 3, 6), (x0 + (k - 2.5) * 5, 9), 10), 3.2), main)
    g.add(unary_union([ellipse(0, -11, 9, 10), box(-9, -10, 9, -3).buffer(.5)]), main)
    if spots:
        for x, y in ((-4, -15), (3, -17), (5, -10)): g.add(circle(x, y, 1.5), spots)
    for s in (-1, 1): g.add(circle(s * 3.4, -8, 2.2), "-"); g.dot(s * 3.4, -8, .8)
    return g

def jelly(main="m"):
    g = Group()
    for k in range(4): g.ln(bez((-5 + k * 3.4, 0), (-7 + k * 3.4, 6), (-3 + k * 3.4, 10), (-5 + k * 3.4, 16), 10), 1)
    g.add(Point(0, 0).buffer(8, 24).intersection(box(-9, -9, 9, 0)).union(box(-8, -1, 8, 1)), main)
    return g

def taper(pts, r0, r1):
    n = len(pts)
    return unary_union([circle(x, y, r0 + (r1 - r0) * i / (n - 1), 12) for i, (x, y) in enumerate(pts)] + [LineString(pts[i:i + 2]).buffer(r0 + (r1 - r0) * i / (n - 1), 8) for i in range(n - 1)])

def seahorse(main="y", fin="o"):
    g = Group()
    g.add(P([(-4, -9), (-9, -6), (-8, 0), (-4, -1)]), fin)
    spine = bez((-1, -10), (-5, -4), (-4, 3), (1, 6), 12) + [(3, 8), (3, 11), (0, 12), (-1, 10), (.5, 9)]
    body = unary_union([taper(spine, 4.2, 1), circle(0, -14, 4), taper([(0, -14), (4, -13.5), (7, -13)], 2, 1.4), P([(-3, -17), (-1, -21), (1, -17.5)])])
    g.add(body, main)
    for k in (2, 4, 6, 8): x, y = spine[k]; g.ln([(x + 2.5, y), (x + 4.4, y)], .7)
    g.dot(.5, -15, .7)
    return g

def starfish(main="o"):
    g = Group(); g.add(star_poly(0, 0, 7, 3, 5).buffer(1.1, 8), main); g.dot(0, 0, .6); return g

def mole(main="x"):
    g = Group()
    g.add(ellipse(0, -6, 10, 6), main)
    g.add(ellipse(10, -6.5, 4, 3), main)
    g.add(circle(14.5, -6.5, 1.6), "k")
    for x in (-5, 5): g.add(ellipse(x, -.8, 3.4, 1.6), "k")
    g.dot(9.5, -8, .6)
    return g

def worm(pts, main="k"):
    g = Group(); g.add(tube(pts, 2.6), main); return g


# ================================================================ bouwstenen: voertuigen
def wheel(x, y, r, code="x", hub="z"):
    g = Group(); g.add(circle(x, y, r), code); g.add(circle(x, y, r * .45), hub); return g

def car(w=34, code="r", win="b", kind="auto"):
    """Auto van opzij, wielen op y=0, van x=0 tot w, kijkt naar rechts."""
    g = Group()
    h = 9
    body = rbox(0, -h - 4, w, -3, 3)
    if kind == "auto":
        cab = P([(w * .22, -h - 3), (w * .32, -h - 11), (w * .68, -h - 11), (w * .8, -h - 3)])
        g.add(unary_union([body, cab]), code)
        g.add(P([(w * .27, -h - 3.5), (w * .35, -h - 9), (w * .49, -h - 9), (w * .49, -h - 3.5)]), win)
        g.add(P([(w * .53, -h - 3.5), (w * .53, -h - 9), (w * .66, -h - 9), (w * .75, -h - 3.5)]), win)
    elif kind == "busje":
        g.add(unary_union([body, rbox(0, -h - 13, w * .85, -h, 2)]), code)
        for k in range(3): g.add(box(w * (.06 + k * .22), -h - 10, w * (.24 + k * .22), -h - 3), win)
        g.add(P([(w * .74, -h - 10), (w * .83, -h - 10), (w * .9, -h - 3), (w * .74, -h - 3)]), win)
    g.add(box(w - 3, -h - 1, w, -h + 2.5), "y"); g.add(box(0, -h - 1, 2.5, -h + 2.5), "r" if code != "r" else "o")
    for x in (w * .22, w * .78): g.ext(wheel(x, -3.5, 4.2))
    return g

def bike(code="r", rider=None):
    g = Group()
    for x in (-9, 9):
        g.add(circle(x, -6.5, 6.5).difference(circle(x, -6.5, 5)), "x")
        g.ln([(x, -6.5), (x, -6.5)], .1)
    g.ln([(-9, -6.5), (-2, -6.5), (5, -15), (-4, -15), (-2, -6.5)], 1.6)
    g.ln([(9, -6.5), (5, -15), (5, -19), (8, -19)], 1.6)
    g.ln([(-4, -15), (-5, -18)], 1.6); g.ln([(-7, -18.5), (-3, -18.5)], 2)
    return g


# ================================================================ SCÈNES
def tractor(code="g", cab="b"):
    g = Group()
    g.add(rbox(-14, -22, 12, -8, 2), code)
    g.add(P([(-14, -22), (-14, -40), (2, -40), (4, -22)]), code)
    g.add(P([(-11, -24), (-11, -37), (0, -37), (2, -24)]), cab)
    g.add(box(4, -18, 16, -9), code); g.add(box(14, -24, 16.5, -18), "z")
    g.ext(wheel(-8, -11, 11)); g.ext(wheel(10, -6, 6))
    return g

def boerenerf(cv):
    cv.put(box(0, 0, 200, 200), "b")
    sun_rays(cv, 172, 22, 10, 10)
    cv.put(cloud(40, 22, 36, 1), "-"); cv.put(cloud(112, 14, 28, 5), "-")
    far = hill(70, 6, 160, .2)
    cv.put_many(stripes(far, 7, -8, "lgy"))
    cv.put(hill(82, 4, 120, .6), "l")
    cv.stamp(tree(48, "g", seed=3), 188, 86)
    cv.stamp(facade(40, 26, "-", "punt", "r", "b", cols=3, rows=1), 132, 88)
    cv.put(box(160, 52, 165, 62), "w")
    cv.stamp(tree(40, "l", seed=5), 124, 88)
    # schuur
    cv.put(P([(4, 104), (4, 56), (32, 34), (60, 56), (60, 104)]), "r")
    cv.put(P([(0, 58), (32, 30), (64, 58), (60, 61), (32, 37), (4, 61)]), "z")
    cv.put(box(14, 72, 50, 104), "-")
    for a, b in (((14, 72), (50, 104)), ((50, 72), (14, 104))): cv.ln([a, b], 1.4)
    cv.ln([(32, 72), (32, 104)], 1.4)
    cv.put(box(25, 44, 39, 58), "y"); cv.ln([(25, 51), (39, 51)], 1)
    # hek
    for x in range(68, 204, 14): cv.put(box(x, 82, x + 3.4, 104), "w")
    cv.put(box(62, 87, 200, 91), "w"); cv.put(box(62, 95, 200, 99), "w")
    # erf
    cv.put(box(0, 104, 200, 200), "l")
    cv.put(P([(18, 104), (54, 104), (96, 200), (8, 200)]), "y")
    cv.put(ellipse(156, 180, 38, 14), "b")
    for x, y in ((134, 184), (176, 188)): cv.ln(qbez((x - 5, y), (x, y - 2), (x + 5, y), 5), 1)
    cv.put(ellipse(114, 140, 20, 6), "w")
    cv.stamp(horse("w", "x"), 88, 120, .95)
    cv.stamp(cow(), 166, 136, 1.0, flip=True)
    cv.stamp(tractor("g"), 34, 140, 1.0)
    cv.stamp(pig(), 112, 140, .95)
    cv.stamp(sheep(), 186, 170, .85, flip=True)
    cv.stamp(sheep(), 138, 162, .8)
    cv.stamp(goat(), 64, 150, .85)
    for x, y, fl, c in ((58, 176, False, "-"), (72, 190, True, "w"), (46, 194, False, "o")): cv.stamp(chicken(c), x, y, 1.05, fl)
    cv.stamp(duck("-"), 150, 184, .9); cv.stamp(duck("y"), 174, 178, .7, True)
    cv.stamp(dog("o"), 118, 196, .95, True)
    cv.stamp(cat("z"), 140, 87, .75)
    cv.put(tube([(14, 116), (13, 176)], 2.8), "w")
    cv.ln([(11, 116), (11, 108)], 1.2); cv.ln([(14, 116), (14, 107)], 1.2); cv.ln([(17, 116), (17, 108)], 1.2); cv.ln([(10.5, 116), (17.5, 116)], 1.2)
    cv.stamp(person("b", "n", "o", "short", "hands", hat="straw", hands=((-13, -38), (10, -26))), 24, 196, .75)
    for x in (100, 196): grass_tufts(cv, [x], 198)

kp9("boerenerf-met-alle-dieren", "Boerenerf met alle dieren", "Een druk boerenerf met een schuur, een tractor, een paard, een koe, schapen, een geit, een varken in de modder, kippen, een hond, een kat en eenden in de vijver. Wie zie je allemaal?", boerenerf, "boerderij")

# ---------------------------------------------------------------- stad
def tram(w=130, code="y", band="r", win="b", heads=True):
    """Tram van opzij, wielen op y=0, van x=0 tot w, rijdt naar rechts."""
    g = Group()
    body = unary_union([rbox(0, -36, w - 6, -5, 3), P([(w - 8, -36), (w - 2, -33), (w + 1, -20), (w + 1, -5), (w - 8, -5)])])
    g.add(body, code)
    g.add(box(1, -15, w, -11).intersection(body), band)
    g.add(P([(w - 6, -32), (w - 2, -30), (w - .5, -20), (w - 6, -20)]), win)
    ndoor = 2; doors = [w * .3, w * .68]
    xs = [x for x in [6 + k * 13 for k in range(int((w - 16) / 13))] if all(abs(x + 4.5 - d) > 9 for d in doors)]
    rnd = random.Random(7)
    for x in xs:
        g.add(box(x, -31, x + 9, -19), win)
        if heads and rnd.random() < .55:
            hx = x + 4.5; g.add(circle(hx, -21.5, 3.2).intersection(box(x, -31, x + 9, -19)), "-")
            g.add(circle(hx, -21.5, 3.6).difference(ellipse(hx, -20.2, 3, 2.5)).intersection(box(x, -31, x + 9, -19)), rnd.choice("wxoy"))
    for d in doors:
        g.add(box(d - 6, -31, d + 6, -5), win); g.ln([(d, -31), (d, -5)], 1.2)
    for x in (12, w * .5, w - 14):
        g.add(Point(x, -3).buffer(3.4, 16).intersection(box(x - 5, -6, x + 5, 0)).union(box(x - 3.4, -5, x + 3.4, -3)), "x")
    g.add(box(w * .45, -39, w * .58, -36), "z")
    g.ln([(w * .48, -39), (w * .56, -47), (w * .5, -53)], 1.2); g.ln([(w * .44, -53), (w * .6, -53)], 1.4)
    g.add(rbox(w - 14, -35, w - 4, -31, 1), "-")
    return g

def lamp_post(h=40, code="x", lamp="y"):
    g = Group(); g.add(box(-1.6, -h, 1.6, 0), code); g.add(box(-3, -3, 3, 0), code)
    g.add(P([(-4.5, -h - 1), (4.5, -h - 1), (3, -h - 8), (-3, -h - 8)]), lamp); g.add(P([(-5.5, -h - 8), (5.5, -h - 8), (0, -h - 12)]), code)
    return g

def traffic_light():
    g = Group(); g.add(box(-1.4, -40, 1.4, 0), "z"); g.add(rbox(-4.5, -58, 4.5, -38, 2), "x")
    for k, c in enumerate("ryg"): g.add(circle(0, -54 + k * 6, 2.3), c)
    return g

def stad(cv):
    cv.put(box(0, 0, 200, 200), "b")
    cv.put(cloud(150, 16, 34, 2), "-"); cv.put(cloud(60, 10, 26, 6), "-")
    rows = [(0, 30, 76, "trap", "o", "r"), (30, 26, 64, "hals", "y", "g"), (56, 30, 84, "punt", "w", "r"), (86, 24, 70, "trap", "k", "t"),
            (110, 30, 60, "plat", "z", "b"), (140, 28, 78, "hals", "o", "y"), (168, 32, 68, "punt", "m", "g")]
    shops = {1: ("b", "-r"), 3: ("y", "-g"), 5: ("b", "-o"), 6: ("y", "-b")}
    for i, (x, w, h, roof, code, rc) in enumerate(rows):
        shop = shops.get(i)
        cv.stamp(facade(w, h, code, roof, rc, "b", cols=2 if w < 28 else 3, door=True, shop=shop[0] if shop else None, awning=shop[1] if shop else None, door_code="w"), x, 122)
    cv.put(box(0, 120, 200, 134), "z")
    for x in range(0, 200, 16): cv.ln([(x, 120), (x - 2, 134)], .9)
    cv.put(box(0, 134, 200, 200), "-")
    for y in (176, 182): cv.ln([(0, y), (200, y)], 1.4)
    for x in range(4, 200, 9): cv.ln([(x, 176), (x, 182)], .7)
    cv.ln([(0, 128), (200, 128)], .1)
    # bovenleiding
    cv.ln([(0, 117), (200, 117)], 1.1)
    # tram
    cv.stamp(tram(124, "y", "r", "b"), 54, 176)
    # zebrapad links
    for k in range(6): cv.put(box(6, 140 + k * 10, 40, 145 + k * 10), "-")
    cv.put(box(4, 136, 42, 200), "z")
    for k in range(6): cv.put(box(6, 140 + k * 10, 40, 145 + k * 10), "-")
    # verkeerslicht, lantaarns, boom
    cv.stamp(traffic_light(), 46, 134)
    cv.stamp(lamp_post(46), 186, 134)
    cv.put(box(126, 124, 142, 134), "w")
    cv.stamp(tree(46, "g", seed=8, w=16), 134, 125)
    # mensen op de stoep
    cv.stamp(person("r", "n", "w", "short", "walk"), 70, 133, .48)
    cv.stamp(person("p", "z", "x", "long", "hold", skirt="m"), 96, 133, .46)
    cv.stamp(person("g", "b", "y", "pony", "wave"), 112, 133, .38)
    cv.stamp(person("o", "n", "w", "bun", "down"), 158, 133, .48)
    cv.put(rbox(150, 118, 154, 126, 1), "-"); cv.ln([(152, 118), (151, 112)], .8); cv.put(circle(151, 109, 3), "r")
    # oversteken
    cv.stamp(person("t", "n", "o", "curly", "walk"), 16, 168, .5)
    cv.stamp(person("y", "x", "w", "short", "hold"), 32, 194, .5)
    cv.stamp(person("m", "n", "x", "braids", "down"), 22, 198, .36)
    # fietser en auto onder
    cv.stamp(car(36, "r", "b"), 140, 199, 1.0)
    cv.stamp(car(36, "g", "b", "busje"), 92, 199, .95)
    for x, y, fl in ((58, 131, False), (176, 131, True)): cv.stamp(bird("z", beak="o"), x, y, .6, fl)

kp9("drukke-stad-met-tram", "Drukke stad met tram", "Een gele tram rijdt door een drukke winkelstraat met grachtenhuizen, mensen die oversteken, auto's, een verkeerslicht en duiven op de stoep. Geef elk huis een eigen kleur.", stad, "wereld")

# ---------------------------------------------------------------- onderwaterwereld
def coral_branch(x, y, h, code, seed):
    rnd = random.Random(seed); parts = []
    def br(x0, y0, a, L, w, d):
        x1, y1 = x0 + L * math.cos(a), y0 + L * math.sin(a)
        parts.append(tube([(x0, y0), (x1, y1)], w))
        parts.append(circle(x1, y1, w / 2 + .6))
        if d > 0:
            for s in (-1, 1): br(x1, y1, a + s * rnd.uniform(.3, .6), L * .72, w * .8, d - 1)
    br(x, y, -math.pi / 2, h * .42, 7, 2)
    g = Group(); g.add(unary_union(parts), code); return g

def kelp(x, y, h, codes, seed):
    rnd = random.Random(seed)
    pts = [(x + 4 * math.sin(t / 9 + seed), y - t) for t in range(0, int(h), 2)]
    ln = LineString(pts); band = ln.buffer(3, 8, cap_style=1)
    cuts = [LineString([(px - 6, py + 1.5), (px + 6, py - 1.5)]) for px, py in pts[4::5]]
    g = Group()
    for k, p in enumerate(split_lines(band, cuts)): g.add(p, codes[k % len(codes)])
    for k, (px, py) in enumerate(pts[6::7]):
        s = 1 if k % 2 else -1
        g.add(leaf((px, py), (px + s * 9, py - 7), 4.5, .1 * s), codes[(k + 1) % len(codes)])
    return g

def onderwater(cv):
    for k in range(5): cv.put(wavy_band(-12 + k * 40, 28 + k * 40, 3, 90, k * .23), "bt"[k % 2])
    cv.put(hill(170, 6, 120, .1), "y")
    for x, y in ((20, 188), (60, 194), (120, 192), (176, 194)): cv.ln(qbez((x - 4, y), (x, y - 2), (x + 4, y), 5), .9)
    # wrak
    hull = P([(100, 182), (108, 140), (204, 118), (204, 176), (150, 184)])
    cv.put(hull, "w")
    for k in range(1, 5): cv.ln([(102 + k * 2, 182 - k * 9), (204, 174 - k * 12)], 1)
    cv.put(P([(108, 140), (204, 118), (204, 110), (107, 133)]), "o")
    cv.put(P([(150, 129), (148, 108), (186, 100), (190, 120)]), "w")
    cv.put(box(160, 108, 170, 117), "b"); cv.put(box(174, 105, 183, 114), "b")
    cv.put(P([(132, 136), (126, 76), (133, 75), (139, 134)]), "w")
    cv.put(P([(126, 80), (112, 74), (114, 70), (128, 76)]).buffer(.8), "w")
    for x, y in ((122, 154), (146, 150), (186, 140)): cv.put(circle(x, y, 4.4), "b")
    # schatkist
    cv.put(rbox(80, 176, 104, 192, 1.5), "w"); cv.put(P([(80, 176), (104, 176), (108, 163), (85, 163)]), "w")
    cv.put(box(90, 176, 94, 192), "y"); cv.put(box(80, 182, 104, 185), "y")
    for x, y in ((86, 174), (93, 172), (100, 174), (96, 168)): cv.put(circle(x, y, 2.8), "y")
    # koraal en wier links
    cv.stamp(kelp(8, 200, 130, "gl", 1)); cv.stamp(kelp(70, 200, 90, "lg", 3))
    cv.stamp(coral_branch(30, 190, 60, "m", 4)); cv.stamp(coral_branch(52, 194, 40, "o", 6))
    cv.put(blob(16, 188, 13, 9, 8, .4, 2), "r")
    for k in range(3): cv.ln(qbez((7 + k * 6, 189 + k), (10 + k * 6, 183), (13 + k * 6, 189 + k), 5), .9)
    cv.put(Point(66, 200).buffer(14, 32).intersection(box(50, 180, 82, 200)), "p")
    for a in range(200, 345, 24):
        r = math.radians(a); cv.ln([(66, 200), (66 + 14 * math.cos(r), 200 + 14 * math.sin(r))], .9)
    for k in range(7):
        a = math.radians(-160 + k * 22)
        cv.put(tube([(42, 200), (42 + 11 * math.cos(a), 200 + 11 * math.sin(a))], 3.4), "k")
    cv.put(Point(42, 200).buffer(5, 16), "m")
    cv.put(ellipse(186, 194, 14, 7), "z")
    # dieren
    cv.stamp(turtle("g", "l"), 64, 56, 1.7)
    cv.stamp(octopus("p"), 122, 186, 1.15)
    cv.stamp(crab("r"), 172, 192, 1.0)
    cv.stamp(jelly("m"), 176, 22, 1.4); cv.stamp(jelly("k"), 148, 40, 1.0)
    cv.stamp(seahorse("y"), 98, 128, 1.3)
    cv.stamp(starfish("o"), 146, 194, 1.0)
    for x, y, b, f_, bd, s_, fl in ((24, 26, "o", "y", "-", 1.3, False), (112, 18, "y", "n", None, 1.0, True), (32, 112, "r", "o", "-", 1.1, True), (64, 92, "t", "y", None, 1.1, False),
                                   (178, 62, "o", "r", None, .8, True), (162, 78, "o", "r", None, .8, True), (184, 88, "o", "r", None, .8, True), (100, 50, "k", "m", None, 1.0, False), (160, 152, "y", "b", "o", .8, True)):
        cv.stamp(fish(b, f_, bd), x, y, s_, fl)
    for x, y, r in ((42, 46, 2.8), (46, 36, 2.2), (42, 28, 1.9), (102, 98, 2.4), (106, 88, 2), (144, 90, 2.6), (148, 80, 2.1)): cv.put(circle(x, y, r), "-")

def diver():
    g = Group()
    g.add(rbox(-7, -46, 7, -28, 3), "y")
    g.ext(person("x", "x", "x", "short", "side", shoes=None, face=False))
    for s in (-1, 1): g.add(P([(s * 2, -3), (s * 9, -3), (s * 11, 6), (s * 3, 6)]), "y")
    g.add(rbox(-6.5, -57, 6.5, -50, 2.5), "b"); g.ln([(0, -57), (0, -50)], .8)
    g.add(tube([(7, -55), (11, -60), (11, -68)], 2.8), "y")
    return g

kp9("onderwaterwereld-met-scheepswrak", "Onderwaterwereld met scheepswrak", "Diep onder water ligt een oud scheepswrak met een schatkist. Er zwemmen vissen, een schildpad, een octopus, een zeepaardje, kwallen en een duiker tussen het koraal en het wier.", onderwater, "zee")

# ---------------------------------------------------------------- dierentuin
def balloon(x, y, code="r", string_to=None):
    g = Group(); g.add(ellipse(x, y, 4.6, 5.6), code); g.add(P([(x - 1.3, y + 6.8), (x + 1.3, y + 6.8), (x, y + 5)]), code)
    if string_to: g.ln([(x, y + 6.8), string_to], .8)
    return g

def signpost(boards=(("o", 1), ("g", -1), ("y", 1))):
    g = Group(); g.add(box(-1.8, -40, 1.8, 0), "w")
    for k, (c, d) in enumerate(boards):
        y = -38 + k * 8
        g.add(P([(0, y), (d * 15, y), (d * 18, y + 3), (d * 15, y + 6), (0, y + 6)]) if d > 0 else P([(0, y), (-15, y), (-18, y + 3), (-15, y + 6), (0, y + 6)]), c)
    return g

def rock(cx, cy, rx, ry, seed=1):
    rnd = random.Random(seed); n = 9
    pts = [(cx + rx * math.cos(math.pi + math.pi * k / (n - 1)) * rnd.uniform(.88, 1.05), cy + ry * math.sin(math.pi + math.pi * k / (n - 1)) * rnd.uniform(.8, 1.1)) for k in range(n)]
    return P(pts + [(cx + rx, cy + 2), (cx - rx, cy + 2)])

def dierentuin(cv):
    cv.put(box(0, 0, 200, 200), "b")
    cv.put(cloud(110, 18, 30, 3), "-"); sun_rays(cv, 24, 22, 9, 9)
    cv.put(hill(92, 3, 140, .3), "l")
    for x, h, c, sd in ((8, 52, "g", 1), (110, 44, "g", 4), (146, 50, "g", 2), (196, 48, "g", 5)): cv.stamp(tree(h, c, seed=sd), x, 96)
    cv.put(box(0, 118, 200, 200), "l")
    # giraffe en olifant achter een hek
    cv.stamp(giraffe("y", "w"), 26, 128, 1.0)
    cv.stamp(elephant("z"), 76, 128, 1.1)
    for x in range(2, 106, 8): cv.put(box(x, 110, x + 3, 132), "w")
    cv.put(box(0, 114, 106, 117.5), "w"); cv.put(box(0, 124, 106, 127.5), "w")
    # leeuwenrots
    rk = unary_union([rock(162, 124, 42, 30, 3), rock(186, 110, 18, 26, 5)])
    cv.put(rk, "z")
    for a, b in (((132, 112), (142, 106)), ((174, 120), (186, 112)), ((180, 96), (190, 92)), ((150, 104), (158, 100))): cv.ln([a, b], 1)
    cv.stamp(lion("o", "w"), 160, 98, 1.1, True)
    # pinguïnbad
    cv.put(ellipse(150, 146, 44, 12), "w"); cv.put(ellipse(150, 146, 38, 8.5), "b")
    for x in (128, 142, 168): cv.ln(qbez((x - 4, 147), (x, 145), (x + 4, 147), 5), .9)
    cv.stamp(penguin("x"), 116, 144, 1.1); cv.stamp(penguin("x"), 184, 146, 1.05)
    cv.put(ellipse(156, 144, 8, 3), "-"); cv.stamp(penguin("x"), 156, 145, .75)
    # pad
    cv.put(P([(-5, 156), (60, 150), (110, 160), (110, 186), (60, 178), (-5, 184)]), "y")
    # flamingovijver
    cv.put(ellipse(28, 194, 34, 9), "t")
    cv.stamp(flamingo("m"), 16, 194, 1.0); cv.stamp(flamingo("m"), 44, 196, .9, True)
    # klimrek met aapjes
    for x in (152, 194): cv.put(box(x - 2, 162, x + 2, 200), "w")
    cv.put(box(148, 164, 198, 168), "w"); cv.put(box(150, 182, 196, 185), "w")
    cv.stamp(monkey("w", "k"), 172, 163, .95)
    cv.stamp(monkey("w", "k"), 170, 182, .75)
    # bezoekers
    cv.stamp(signpost(), 128, 198)
    cv.stamp(person("g", "n", "w", "short", "hold", hands=((-12, -24), (13, -32))), 62, 178, .5)
    cv.stamp(person("y", "b", "o", "pony", "wave", skirt="r"), 77, 180, .38)
    cv.stamp(balloon(86, 130, "r", (83.1, 157.2)))
    cv.stamp(person("p", "z", "x", "curly", "point"), 96, 183, .46)
    for x in (70, 146): grass_tufts(cv, [x], 197)
    for x, y, c in ((86, 194, "m"), (100, 197, "y"), (106, 190, "r")): cv.stamp(flower(x, y, 2.6, c, "y", 0))

kp9("dag-in-de-dierentuin", "Een dag in de dierentuin", "Een giraf, een olifant, een leeuw op de rots, pinguïns in het bad, flamingo's in de vijver en aapjes in het klimrek. En op het pad lopen de bezoekers. Welk dier vind jij het leukst?", dierentuin, "dieren")

# ---------------------------------------------------------------- jungle
def croc(main="g"):
    """Krokodil die half boven het water uitsteekt; waterlijn op y=0."""
    g = Group()
    body = unary_union([P([(-40, 0), (-20, -5), (0, -7), (16, -6), (34, -4), (36, 0)]), circle(12, -8, 3.6)])
    g.add(body, main)
    g.add(circle(12, -8.5, 1.8), "y"); g.dot(12.4, -8.5, .7)
    for x in (-30, -22, -14, -6, 2): g.add(P([(x - 2, -4.5 if x > -24 else -2.5), (x, -8.5 if x > -24 else -6), (x + 2, -4.5 if x > -24 else -2.5)]).buffer(.5), main)
    g.ln([(18, -3), (34, -2.2)], .9)
    g.dot(32, -4.6, .5)
    return g

def butterfly(a="o", b="y"):
    g = Group()
    for s in (-1, 1):
        g.add(ellipse(s * 5, -4, 5, 6, s * 25), a); g.add(ellipse(s * 4, 4, 3.4, 4, -s * 25), b)
        g.add(circle(s * 5.5, -5, 1.8), b)
    g.add(ellipse(0, 0, 1.6, 7), "x")
    g.ln([(0, -6), (-3, -11)], .8); g.ln([(0, -6), (3, -11)], .8)
    return g

def big_leaf(base, tip, w, c1, c2, bend=0.0):
    lf = leaf(base, tip, w, bend)
    halves = split_lines(lf, [LineString([base, tip]).parallel_offset(0, "left") if False else LineString([(base[0] - (tip[0] - base[0]) * .05, base[1] - (tip[1] - base[1]) * .05), (tip[0] + (tip[0] - base[0]) * .05, tip[1] + (tip[1] - base[1]) * .05)])])
    g = Group()
    for k, h in enumerate(halves): g.add(h, (c1, c2)[k % 2])
    L = math.dist(base, tip); ux, uy = (tip[0] - base[0]) / L, (tip[1] - base[1]) / L
    for t in (.3, .5, .7):
        px, py = base[0] + ux * L * t, base[1] + uy * L * t
        for s in (-1, 1): g.ln([(px, py), (px + (ux * .5 - s * uy) * w * .35, py + (uy * .5 + s * ux) * w * .35)], .8)
    return g

def jungle(cv):
    cv.put(box(0, 0, 200, 200), "b")
    # lagen begroeiing
    rnd = random.Random(11)
    for k, (x, y, rx, ry) in enumerate(((20, 10, 34, 22), (70, 4, 30, 18), (130, 6, 34, 20), (184, 12, 30, 24), (40, 48, 34, 22), (160, 52, 34, 22), (100, 40, 26, 14),
                                         (10, 92, 26, 30), (190, 96, 24, 30), (54, 96, 24, 20), (148, 98, 24, 18))):
        cv.put(blob(x, y, rx, ry, 10, .38, k + 1), "gl"[k % 2])
    pts = []
    for _ in range(3000):
        p = (rnd.uniform(0, 200), rnd.uniform(0, 140))
        if 70 < p[0] < 132 and p[1] > 50: continue
        if all(math.dist(p, q) > 15 for q in pts): pts.append(p)
    for i, (x, y) in enumerate(pts):
        a = rnd.uniform(0, 2 * math.pi); L = rnd.uniform(9, 13)
        cv.put(leaf((x, y), (x + L * math.cos(a), y + L * math.sin(a)), L * .5, rnd.uniform(-.1, .1)), "gl"[i % 2])
    # waterval
    cliff = P([(74, 150), (76, 72), (88, 56), (114, 56), (126, 72), (128, 150)])
    cuts = [LineString(l) for l in (((70, 84), (90, 92)), ((70, 112), (90, 104)), ((70, 136), (90, 130)), ((110, 80), (130, 90)), ((110, 112), (130, 118)), ((110, 134), (130, 128)), ((80, 70), (90, 76)), ((112, 74), (124, 64)))]
    cv.put_many([(q, "zw"[k % 2]) for k, q in enumerate(split_lines(cliff, cuts))])
    fall = P([(90, 60), (112, 60), (116, 150), (86, 150)])
    cv.put_many(stripes(fall, 5.5, 90, "b-"))
    # rivier
    cv.put(P([(-5, 150), (205, 150), (205, 205), (-5, 205)]), "t")
    cv.put(ellipse(101, 152, 24, 5.5), "-")
    for x, y in ((20, 172), (60, 188), (140, 180), (176, 194), (112, 198)): cv.ln(qbez((x - 6, y), (x, y - 2.5), (x + 6, y), 5), 1)
    # oevers
    cv.put(P([(-5, 132), (40, 136), (66, 150), (60, 160), (-5, 162)]), "w")
    cv.put(P([(205, 128), (150, 134), (136, 148), (150, 156), (205, 160)]), "w")
    # bomen
    for x0, x1 in ((4, 22), (174, 192)):
        cv.put(P([(x0 - 2, 162), (x0 + 2, 0), (x1 - 2, 0), (x1 + 2, 162)]), "w")
        for y in (30, 70, 110): cv.ln(qbez((x0 + 3, y), ((x0 + x1) / 2, y + 4), (x1 - 3, y), 5), .9)
    cv.put(tube([(20, 58), (60, 54), (80, 46)], 6), "w")
    cv.put(tube([(176, 64), (140, 60), (120, 50)], 6), "w")
    # lianen
    for pts in (qbez((40, 0), (52, 60), (44, 106), 16), qbez((150, 0), (160, 40), (156, 90), 16), qbez((100, 0), (96, 20), (100, 40), 10)):
        cv.put(tube(pts, 3.4), "w")
        for k in range(2, len(pts) - 1, 4):
            px, py = pts[k]; s = 1 if k % 8 else -1
            cv.put(leaf((px, py), (px + s * 9, py + 4), 5.5), "l")
    # dieren
    cv.stamp(tiger("o"), 168, 140, 1.05, True)
    cv.stamp(monkey("w", "k"), 64, 55, .95)
    cv.stamp(parrot("r", "b"), 150, 59, 1.15)
    cv.stamp(toucan("x", "o"), 126, 49, 1.05)
    cv.stamp(snake(bez((22, 58), (10, 66), (32, 74), (20, 84), 16) + [(18, 92), (26, 96)], "y", "o", 4))
    cv.stamp(croc("g"), 70, 176, 1.0)
    cv.put(ellipse(150, 186, 12, 4), "l"); cv.stamp(frog("g"), 150, 186, .9)
    cv.put(ellipse(28, 190, 10, 3.4), "l")
    cv.stamp(butterfly("o", "y"), 112, 110, .9, rot=-15); cv.stamp(butterfly("m", "p"), 54, 120, .7, rot=20)
    for x, y, c in ((60, 140, "r"), (36, 132, "m")):
        cv.put(unary_union([ellipse(x + 4.5 * math.cos(math.radians(a)), y + 4.5 * math.sin(math.radians(a)), 3.6, 2.6, a) for a in range(-90, 270, 72)]), c); cv.put(circle(x, y, 1.8), "y")
    # bladeren op de voorgrond
    for base, tip, w, c in (((-4, 200), (36, 156), 22, ("g", "l")), ((-4, 120), (26, 100), 16, ("l", "g")), ((204, 200), (170, 160), 22, ("l", "g")), ((204, 110), (178, 96), 14, ("g", "l")), ((96, 204), (88, 176), 12, ("g", "l")), ((106, 204), (120, 180), 12, ("l", "g"))):
        cv.stamp(big_leaf(base, tip, w, *c))

kp9("jungle-vol-dieren", "Jungle vol dieren", "Diep in de jungle stort een waterval in de rivier. Een tijger op de oever, een krokodil in het water, een aap, een papegaai, een toekan, een slang en vlinders tussen de lianen.", jungle, "dieren")

# ---------------------------------------------------------------- treinstation
def train_car(w=70, code="r", win="b", loco=False, nose=False):
    g = Group(); h = 30
    if loco:
        body = unary_union([rbox(0, -h - 4, w - 14, -4, 3), P([(w - 16, -h - 4), (w - 6, -h - 1), (w + 2, -18), (w + 2, -4), (w - 16, -4)])])
    else:
        body = rbox(0, -h - 4, w, -4, 3)
    g.add(body, code)
    g.add(box(0, -12, w + 2, -9).intersection(body), "-")
    xs = range(5, int(w - (20 if loco else 8)), 11)
    for x in xs: g.add(rbox(x, -28, x + 8, -18, 1.5), win)
    if loco:
        g.add(P([(w - 13, -h - 1), (w - 6, -h + 1), (w - .5, -20), (w - 13, -20)]), win)
        g.add(circle(w - 1, -7, 1.8), "y")
    else:
        g.add(box(w / 2 - 5, -29, w / 2 + 5, -6), win); g.ln([(w / 2, -29), (w / 2, -6)], 1)
    for x in (8, 16, w - 16, w - 8): g.add(circle(x, -3, 3.4), "x")
    return g

def clock(r=9):
    g = Group(); g.add(circle(0, 0, r + 2.5), "x"); g.add(circle(0, 0, r), "-")
    for k in range(12):
        a = math.radians(k * 30); g.ln([(r * .78 * math.cos(a), r * .78 * math.sin(a)), (r * .92 * math.cos(a), r * .92 * math.sin(a))], .8)
    g.ln([(0, 0), (0, -r * .7)], 1.2); g.ln([(0, 0), (r * .45, r * .2)], 1.4)
    return g

def suitcase(code="r"):
    g = Group(); g.add(rbox(-6, -11, 6, 0, 1.5), code); g.ln([(-2.5, -11), (-2.5, -14), (2.5, -14), (2.5, -11)], 1.1)
    g.ln([(-6, -5), (6, -5)], .8); return g

def station(cv):
    cv.put(box(0, 0, 200, 200), "b")
    # overkapping met boog
    arch = Point(100, 120).buffer(130, 96).intersection(box(0, 0, 200, 70))
    cv.put(box(0, 0, 200, 70), "z")
    inner = Point(100, 120).buffer(120, 96).intersection(box(0, 0, 200, 70))
    cuts = [LineString([(100, 120), (100 + 200 * math.cos(math.radians(a)), 120 + 200 * math.sin(math.radians(a)))]) for a in range(-160, -15, 12)]
    cuts += [LineString(Point(100, 120).buffer(r, 96).exterior.coords) for r in (98, 108)]
    panes = split_lines(inner.buffer(-2.5), cuts)
    cv.put_many([(p, "b") for p in panes])
    cv.put(box(0, 60, 200, 66), "x")
    # achterwand
    cv.put(box(0, 66, 200, 128), "o")
    for x in range(0, 200, 10):
        for y in range(70, 128, 6): cv.ln([(x + (5 if (y // 6) % 2 else 0), y), (x + (5 if (y // 6) % 2 else 0), y + 6)], .6)
    for y in range(72, 128, 6): cv.ln([(0, y), (200, y)], .6)
    for x in (16, 156):
        cv.put(unary_union([box(x, 82, x + 28, 112), Point(x + 14, 82).buffer(14, 24)]), "b"); cv.ln([(x + 14, 68), (x + 14, 112)], 1); cv.ln([(x, 94), (x + 28, 94)], 1)
    cv.stamp(clock(7.5), 100, 77)
    cv.put(rbox(64, 90, 136, 99, 2), "x")
    for k in range(2): cv.put(box(67 + k * 35, 92.5, 98 + k * 35, 96.5), "y")
    # sporen en trein
    cv.put(box(0, 128, 200, 140), "w")
    for x in range(2, 200, 9): cv.put(box(x, 133, x + 5, 139), "w")
    cv.ln([(0, 134), (200, 134)], 1.4)
    cv.stamp(train_car(60, "y", "b"), -14, 134); cv.stamp(train_car(60, "y", "b"), 50, 134); cv.stamp(train_car(62, "y", "b", loco=True), 114, 134)
    for x in (-14, 50, 114): cv.put(box(x + 2, 102, x + 58, 106), "n") if False else None
    # perron
    cv.put(box(0, 140, 200, 200), "-")
    cv.put(box(0, 140, 200, 145), "y")
    for x in range(0, 200, 20): cv.ln([(x, 145), (x - 6, 200)], .7)
    for y in (162, 182): cv.ln([(0, y), (200, y)], .7)
    # bank, mensen, koffers, duiven
    cv.put(rbox(132, 168, 170, 173, 1.5), "w"); cv.put(rbox(132, 158, 170, 163, 1.5), "w")
    for x in (136, 166): cv.put(box(x - 1.5, 173, x + 1.5, 182), "x")
    cv.stamp(person("m", "n", "x", "long", "hold", legs=True), 144, 182, .44)
    cv.stamp(person("t", "z", "w", "short", "down", hands=((-12, -23), (13, -24))), 30, 192, .56)
    cv.stamp(suitcase("r"), 44, 192, .9)
    cv.stamp(person("y", "n", "o", "pony", "wave"), 62, 194, .42)
    cv.stamp(person("p", "b", "w", "bun", "walk"), 92, 186, .52)
    cv.stamp(suitcase("g"), 104, 186, .8)
    cv.stamp(person("g", "x", "y", "short", "point", hat="cap"), 186, 196, .52)
    cv.put(rbox(8, 150, 22, 168, 2), "n"); cv.put(box(13.5, 168, 16.5, 192), "z")
    for x, y, fl in ((120, 196, False), (160, 194, True)): cv.stamp(bird("z", "z", "o"), x, y, .8, fl)

kp9("treinstation-met-perrons", "Treinstation", "Een groot station met een glazen overkapping, een stationsklok en een bord met vertrektijden. De trein staat klaar en op het perron wachten reizigers met hun koffers.", station, "voertuigen")

# ---------------------------------------------------------------- haven
def container(x0, y0, w, h, code):
    g = Group(); g.add(box(x0, y0, x0 + w, y0 + h), code)
    for k in range(1, int(w / 4.4)): g.ln([(x0 + k * 4.4, y0 + 1.6), (x0 + k * 4.4, y0 + h - 1.6)], .55)
    return g

def gull():
    g = Group(); g.ln(qbez((-6, 0), (-3, -3.5), (0, 0), 5) + qbez((0, 0), (3, -3.5), (6, 0), 5)[1:], 1.2); return g

def lighthouse(h=60):
    g = Group()
    body = P([(-8, 0), (-5, -h), (5, -h), (8, 0)])
    for k, c in enumerate("r-r-r"):
        g.add(box(-10, -h * (k + 1) / 5, 10, -h * k / 5).intersection(body), c)
    g.add(box(-6, -h - 9, 6, -h), "y"); g.ln([(0, -h - 9), (0, -h)], .8)
    g.add(P([(-8, -h - 9), (8, -h - 9), (0, -h - 17)]), "x")
    g.add(box(-8.5, -h - 1.5, 8.5, -h + 1.5), "x")
    g.add(rbox(-2.5, -9, 2.5, 0, 1), "w")
    return g

def tug(code="r"):
    g = Group()
    g.add(P([(-20, -8), (22, -8), (16, 2), (-16, 2)]), "x")
    g.add(box(-21, -11, 23, -8), code)
    g.add(rbox(-10, -24, 8, -11, 1.5), "-")
    for x in (-7, -1, 5): g.add(box(x - 1.8, -21, x + 1.8, -16), "b")
    g.add(box(-6, -34, 0, -24), code); g.add(box(-6.5, -36, .5, -33), "x")
    for x in (-15, 18): g.add(circle(x, -4, 2.6).difference(circle(x, -4, 1.2)), "o") if False else g.add(circle(x, -4, 2.6), "o")
    return g

def sailboat(code="-", sail="r"):
    g = Group()
    g.add(P([(-16, -6), (16, -6), (11, 2), (-12, 2)]), code)
    g.add(box(-.8, -40, .8, -6), "w")
    g.add(P([(1.5, -39), (1.5, -9), (18, -9)]), sail); g.add(P([(-1.5, -34), (-1.5, -9), (-13, -9)]), "y")
    return g

def haven(cv):
    cv.put(box(0, 0, 200, 200), "b")
    cv.put(cloud(40, 16, 34, 2), "-"); cv.put(cloud(112, 10, 24, 4), "-")
    for x, w, h in ((60, 12, 20), (72, 10, 14), (82, 14, 26), (96, 10, 16)):
        cv.put(box(x, 92 - h, x + w, 92), "z")
        for k in range(int(h / 7)): cv.put(box(x + 3, 92 - h + 3 + k * 7, x + w - 3, 92 - h + 6 + k * 7), "y")
    # kade rechts met kraan
    cv.put(box(146, 92, 200, 200), "z")
    for y in range(100, 200, 12): cv.ln([(146, y), (200, y)], .6)
    cv.put(box(144, 92, 202, 97), "x")
    for x in (156, 188): cv.put(box(x - 3, 26, x + 3, 92), "y")
    cv.put(box(106, 22, 200, 30), "y"); cv.put(box(182, 6, 190, 22), "y")
    cv.ln([(186, 6), (112, 22)], 1.1); cv.ln([(186, 6), (200, 18)], 1.1)
    for x in range(159, 185, 8): cv.ln([(x, 30), (x + 8, 46)], 1); cv.ln([(x + 8, 30), (x, 46)], 1)
    cv.put(box(156, 46, 188, 51), "y")
    cv.put(rbox(162, 30, 178, 44, 1.5), "b") if False else cv.put(rbox(150, 32, 162, 44, 1.5), "b")
    cv.ln([(124, 30), (124, 52)], 1.1); cv.put(box(118, 52, 130, 56), "x")
    cv.stamp(container(0, 0, 22, 10, "g"), 113, 56)
    for k, (x, y, c) in enumerate(((150, 62, "r"), (172, 62, "b"), (150, 72, "o"), (172, 72, "g"), (150, 82, "n"), (172, 82, "y"))):
        cv.stamp(container(0, 0, 22, 10, c), x, y)
    for x in (152, 172, 192): cv.put(rbox(x - 3, 98, x + 3, 104, 1.5), "x")
    # water
    for k in range(4): cv.put(wavy_band(92 + k * 28, 120 + k * 28, 2, 50, k * .3, -5, 146), "bt"[k % 2])
    # containerschip
    hull = P([(0, 108), (132, 108), (124, 140), (0, 140)])
    cv.put(hull, "r"); cv.put(box(0, 130, 140, 140).intersection(hull), "x")
    cv.put(box(0, 104, 134, 108), "-")
    cv.ln([(0, 120), (128, 120)], .1)
    for i in range(5):
        for j in range(3):
            c = "gyobm"[(i + j * 2) % 5]
            cv.stamp(container(0, 0, 18, 9.5, c), 4 + i * 19, 94.5 - j * 9.6)
    cv.put(box(100, 58, 126, 104), "-")
    for y in (64, 76, 88): cv.put(box(103, y, 123, y + 6), "b")
    cv.put(box(110, 44, 120, 58), "o"); cv.put(box(109, 42, 121, 45), "x")
    for x in (20, 40, 60, 80): cv.put(circle(x, 115, 2.6), "-")
    # sleepboot, zeilboot, vuurtoren, boeien
    cv.stamp(tug("r"), 96, 174, 1.15)
    cv.stamp(sailboat("-", "m"), 46, 194, 1.0)
    cv.put(P([(-5, 156), (24, 158), (30, 170), (-5, 170)]), "z")
    cv.stamp(lighthouse(54), 12, 158, .95)
    cv.put(circle(130, 190, 5.5), "r"); cv.put(box(125.5, 186, 134.5, 188.5), "-")
    cv.put(P([(126, 156), (134, 156), (136, 166), (124, 166)]), "y"); cv.ln([(130, 156), (130, 150)], 1)
    # op de kade
    cv.stamp(person("o", "n", "w", "short", "point", hat="helmet"), 160, 128, .5)
    cv.stamp(car(44, "b", "b", "busje"), 152, 166, .95)
    cv.stamp(person("r", "x", "x", "curly", "wave"), 168, 198, .44)
    cv.stamp(person("y", "n", "o", "pony", "hold"), 188, 196, .4)
    for x, y in ((44, 38), (58, 32), (72, 46), (30, 62)): cv.stamp(gull(), x, y)

kp9("haven-met-vrachtschepen", "Haven met vrachtschepen", "In de haven ligt een groot vrachtschip vol containers. Een kraan zet containers op de kade, een sleepboot vaart voorbij en bij de vuurtoren zeilt een bootje. Welke kleur geef jij de containers?", haven, "voertuigen")

# ---------------------------------------------------------------- kasteel
def tower(x, w, top, base, code="z", roof="r", flag="y", windows=2):
    g = Group()
    g.add(box(x, top, x + w, base), code)
    g.add(P([(x - 3, top), (x + w / 2, top - w * 1.2), (x + w + 3, top)]), roof)
    g.add(box(x + w / 2 - .7, top - w * 1.2 - 12, x + w / 2 + .7, top - w * 1.2), "x") if False else None
    g.ln([(x + w / 2, top - w * 1.2), (x + w / 2, top - w * 1.2 - 10)], 1.1)
    g.add(P([(x + w / 2 + .6, top - w * 1.2 - 10), (x + w / 2 + 10, top - w * 1.2 - 7.5), (x + w / 2 + .6, top - w * 1.2 - 5)]), flag)
    for k in range(windows):
        y = top + 8 + k * 16
        g.add(unary_union([box(x + w / 2 - 2.6, y + 2.6, x + w / 2 + 2.6, y + 9), circle(x + w / 2, y + 2.6, 2.6)]), "x" if False else "y")
    return g

def battlement(x0, x1, y, h=5, w=5):
    parts = [box(x0, y, x1, y + h)]
    k = 0; x = x0
    while x + w <= x1 + .1:
        if k % 2 == 0: parts.append(box(x, y - h, x + w, y))
        x += w; k += 1
    return unary_union(parts)

def kasteel(cv):
    cv.put(box(0, 0, 200, 200), "b")
    cv.put(cloud(150, 12, 26, 1), "-"); cv.put(cloud(56, 10, 24, 3), "-")
    cv.put(hill(84, 4, 160, .4), "g")
    cv.put(unary_union([box(30, 54, 170, 104), battlement(30, 170, 54, 5, 7)]), "z")
    for y in range(60, 104, 7):
        for x in range(30 + (6 if (y // 7) % 2 else 0), 170, 12): cv.ln([(x, y), (x, y + 7)], .6)
        cv.ln([(30, y), (170, y)], .6)
    gate = unary_union([box(84, 74, 116, 104), Point(100, 74).buffer(16, 32)])
    cv.put(gate, "w")
    for x in range(88, 114, 6): cv.ln([(x, 58), (x, 104)], 1)
    for y in (72, 82, 92): cv.ln([(84, y), (116, y)], 1)
    cv.stamp(tower(6, 26, 50, 104, "z", "r", "y", 3)); cv.stamp(tower(168, 26, 50, 104, "z", "r", "b", 3)); cv.stamp(tower(88, 24, 30, 56, "z", "n", "r", 1))
    for x, c in ((52, "r"), (148, "b")):
        cv.put(P([(x - 7, 64), (x + 7, 64), (x + 7, 84), (x, 89), (x - 7, 84)]), c)
        cv.put(star_poly(x, 74, 4.5, 2), "y")
    # gracht met brug
    cv.put(P([(-5, 104), (205, 104), (205, 118), (-5, 118)]), "t")
    for x in (20, 60, 150, 186): cv.ln(qbez((x - 5, 111), (x, 109), (x + 5, 111), 5), .9)
    cv.put(P([(84, 104), (116, 104), (120, 120), (80, 120)]), "w")
    for x in (92, 100, 108): cv.ln([(x, 105), (x, 120)], .8)
    cv.ln([(84, 104), (72, 74)], 1); cv.ln([(116, 104), (128, 74)], 1)
    # tuin
    cv.put(box(0, 118, 200, 200), "l")
    cv.put(P([(80, 120), (120, 120), (126, 152), (74, 152)]), "y")
    cv.put(ellipse(100, 172, 52, 24), "y")
    cv.put(P([(60, 186), (140, 186), (150, 200), (50, 200)]), "y")
    cv.put(ellipse(100, 172, 26, 8), "z"); cv.put(ellipse(100, 171, 21, 5.5), "b")
    cv.put(box(97, 150, 103, 171), "z"); cv.put(ellipse(100, 150, 10, 3), "z"); cv.put(ellipse(100, 149, 7, 1.8), "b")
    for sgn in (-1, 1): cv.ln(qbez((100, 144), (100 + sgn * 12, 136), (100 + sgn * 16, 166), 10), 1.1)
    cv.ln([(100, 150), (100, 140)], 1.1)
    for x0, sgn in ((0, 1), (200, -1)):
        bed = P([(x0, 124), (x0 + sgn * 68, 124), (x0 + sgn * 60, 146), (x0, 146)])
        cv.put(bed, "w")
        for k in range(6):
            cv.stamp(flower(x0 + sgn * (8 + k * 9.5), 130 + (k % 2) * 9, 3, "mrpyok"[k], "y", 0))
        cv.put(rbox(min(x0, x0 + sgn * 46), 152, max(x0, x0 + sgn * 46), 162, 4).intersection(PAGE), "g")
        for k in range(3): cv.put(circle(x0 + sgn * (8 + k * 14), 157, 2.4), "r")
    for x in (66, 142): cv.put(circle(x, 154, 7), "g"); cv.put(box(x - 1.5, 161, x + 1.5, 165), "w")
    # ridders en prinses
    cv.stamp(horse("-", "y"), 34, 198, .95)
    cv.put(P([(20, 167), (40, 167), (38, 182), (22, 182)]), "r"); cv.put(box(20, 167, 40, 170), "y")
    cv.stamp(knight("z", "r", "b"), 30, 171, .5)
    cv.stamp(knight("z", "b", "r"), 170, 198, .56, True)
    cv.stamp(person("m", "m", "y", "long", "wave", skirt="p", hat="crown"), 132, 196, .48)
    cv.stamp(person("y", "n", "o", "short", "down"), 76, 196, .36)
    cv.stamp(dog("-", "w"), 94, 198, .7)

kp9("kasteel-met-tuin-en-ridders", "Kasteel met tuin en ridders", "Een kasteel met torens, vlaggen en een ophaalbrug over de gracht. In de kasteeltuin staan een fontein, bloemperken en heggen, en er rijdt een ridder op zijn paard.", kasteel, "sprookjes")

# ---------------------------------------------------------------- ruimtebasis
def astronaut(suit="-", visor="b", pose="wave"):
    g = person(suit, suit, "x", "bald", pose, shoes="z", face=False)
    g.items.insert(0, ("g", rbox(-11, -46, 11, -26, 3), "z"))
    g.add(circle(0, -53, 11), suit); g.add(ellipse(0, -53, 6.6, 5.2), visor)
    g.ln([(-3.5, -56), (-1.5, -58)], 1)
    g.add(rbox(-5, -40, 5, -33, 1.5), "r")
    return g

def rocket(code="-", fin="r", win="b"):
    g = Group()
    for s in (-1, 1): g.add(P([(s * 7, -26), (s * 15, -10), (s * 15, 0), (s * 7, -8)]), fin)
    body = unary_union([rbox(-8, -62, 8, -6, 3), P([(-8, -60), (0, -82), (8, -60)])])
    g.add(body, code)
    g.add(P([(-8, -60), (0, -82), (8, -60)]).buffer(-.2).intersection(body), fin)
    g.add(box(-9, -30, 9, -26).intersection(body.buffer(1)), fin)
    g.add(circle(0, -48, 4.6), "z"); g.add(circle(0, -48, 3), win)
    g.add(P([(-4, -6), (4, -6), (6, 0), (-6, 0)]), "z")
    return g

def dome(cx, base, r, glass="b", frame="z"):
    g = Group()
    d = Point(cx, base).buffer(r, 48).intersection(box(cx - r, base - r, cx + r, base))
    cuts = [LineString([(cx + r * math.cos(math.radians(a)) * 1.1, base + 1), (cx, base - r * 1.2)]) for a in ()]
    cuts = [LineString([(cx, base), (cx + 2 * r * math.cos(math.radians(a)), base + 2 * r * math.sin(math.radians(a)))]) for a in (-150, -120, -90, -60, -30)]
    cuts += [LineString(Point(cx, base).buffer(r * .6, 48).exterior.coords)]
    for k, p in enumerate(split_lines(d, cuts)): g.add(p, glass)
    g.add(box(cx - r - 2, base - 3, cx + r + 2, base + 2), frame)
    return g

def solar(x, y, w=26, h=14, code="n"):
    g = Group(); g.add(box(x - 1, y + h, x + 1, y + h + 10), "z")
    pnl = P([(x - w / 2, y), (x + w / 2, y), (x + w / 2 + 4, y + h), (x - w / 2 - 4, y + h)])
    cuts = [LineString([(x - w / 2 + k * w / 4 - (k - 2) * .0, y - 1), (x - w / 2 - 4 + k * (w + 8) / 4, y + h + 1)]) for k in range(1, 4)] + [LineString([(x - 30, y + h / 2), (x + 30, y + h / 2)])]
    for k, p in enumerate(split_lines(pnl, cuts)): g.add(p, code)
    return g

def rover(code="-"):
    g = Group()
    g.add(rbox(-16, -16, 16, -7, 2.5), code)
    g.add(P([(-10, -16), (-7, -24), (6, -24), (10, -16)]), "b")
    g.ln([(12, -16), (14, -28)], 1); g.add(Point(14, -28).buffer(4, 16).intersection(box(8, -34, 20, -28)), "z")
    for x in (-11, 0, 11): g.add(circle(x, -5, 4.6), "x"); g.add(circle(x, -5, 1.8), "z")
    return g

def saucer(code="t"):
    g = Group()
    g.add(Point(0, -3).buffer(8, 24).intersection(box(-9, -12, 9, -3)), "b")
    g.add(ellipse(0, 0, 18, 5), code)
    for x in (-10, 0, 10): g.add(circle(x, .5, 1.8), "y")
    return g

def satellite():
    g = Group()
    for s in (-1, 1):
        pnl = box(s * 7, -4, s * 22, 4) if s > 0 else box(-22, -4, -7, 4)
        for k, q in enumerate(split_lines(pnl, [LineString([(s * 12, -6), (s * 12, 6)]), LineString([(s * 17, -6), (s * 17, 6)])])): g.add(q, "n")
    g.add(rbox(-6, -6, 6, 6, 1.5), "y"); g.ln([(0, -6), (0, -11)], 1); g.add(circle(0, -12, 1.8), "r")
    return g

def ruimtebasis(cv):
    cv.put(box(0, 0, 200, 200), "n")
    ring = ellipse(150, 40, 42, 9, -12).difference(ellipse(150, 40, 30, 5.2, -12))
    cv.put(ring, "y")
    pl = circle(150, 40, 22, 48)
    cv.put_many(stripes(pl, 7, -12, "opr"))
    below = affinity.rotate(box(0, 40, 300, 200), -12, origin=(150, 40))
    cv.put(ring.intersection(below), "y")
    cv.put(circle(36, 30, 12, 32), "-"); cv.put(circle(32, 26, 3, 12), "z"); cv.put(circle(40, 34, 2.4, 12), "z")
    for x, y in ((80, 14), (14, 66), (70, 58), (186, 82), (60, 34), (188, 10), (104, 8), (120, 70)):
        cv.put(star_poly(x, y, 4, 1.7), "y")
    cv.put(star_poly(18, 96, 4, 1.7), "y"); cv.ln([(22, 94), (40, 84)], 1); cv.ln([(22, 97), (42, 89)], 1)
    cv.stamp(saucer("t"), 92, 46, 1.0, rot=-8)
    cv.stamp(satellite(), 108, 86, .8, rot=20)
    # grond
    cv.put(hill(118, 5, 150, .3), "o")
    cv.put(hill(150, 4, 110, .7), "w")
    for x, y, rx in ((24, 128, 12), (100, 124, 8), (110, 186, 16), (40, 180, 10), (176, 190, 12)):
        cv.put(ellipse(x, y, rx, rx * .34), "z"); cv.put(ellipse(x, y + rx * .1, rx * .7, rx * .18), "x")
    cv.stamp(solar(132, 98, 22, 10, "n"))
    cv.put(box(40, 122, 120, 130), "z")
    for x in (64, 84, 104): cv.ln([(x, 122), (x, 130)], .8)
    cv.stamp(dome(46, 132, 26, "b"))
    cv.put(ellipse(46, 120, 5, 7), "g"); cv.put(box(45, 126, 47, 130), "w")
    cv.stamp(dome(112, 134, 18, "t"))
    cv.put(rbox(104, 124, 112, 133, 1), "y")
    cv.put(box(82, 102, 85, 122), "z")
    cv.put(Point(84, 100).buffer(12, 32).intersection(box(68, 100, 100, 120)).difference(Point(84, 96).buffer(10, 32)), "-")
    cv.ln([(84, 106), (90, 94)], 1); cv.put(circle(90, 93, 1.8), "r")
    # lanceerplatform met raket
    cv.put(P([(140, 166), (204, 166), (204, 176), (146, 176)]), "z")
    cv.put(box(186, 86, 192, 166), "z")
    for y in range(92, 166, 12): cv.ln([(186, y), (192, y + 12)], .8)
    cv.put(box(178, 120, 186, 124), "z")
    cv.stamp(rocket("-", "r", "b"), 166, 166, 1.0)
    # rover en astronauten
    cv.stamp(rover("-"), 82, 176, 1.0)
    cv.stamp(astronaut("-", "b", "wave"), 30, 190, .66)
    cv.stamp(astronaut("-", "t", "hold"), 130, 198, .6)
    for x, y in ((186, 196), (10, 152), (62, 196)): cv.put(ellipse(x, y, 5, 2.4), "z")

kp9("ruimtebasis-op-een-planeet", "Ruimtebasis op een planeet", "Op een verre planeet staat een ruimtebasis met glazen koepels, zonnepanelen en een schotel. Een raket staat klaar op het platform en astronauten rijden rond met de maanwagen.", ruimtebasis, "ruimte")

# ---------------------------------------------------------------- boomhutdorp
def trunk_tree(cv, x, w, top_y, crown_c, seed):
    cv.put(P([(x - w / 2 - 3, 200), (x - w / 2, top_y + 20), (x + w / 2, top_y + 20), (x + w / 2 + 3, 200)]), "w")
    for y in range(int(top_y) + 40, 200, 22): cv.ln(qbez((x - w / 2 + 2, y), (x, y + 4), (x + w / 2 - 2, y), 5), .9)

def hut(x, base, w, h, code="o", roof="r", win="b", door=True):
    g = Group()
    g.add(box(x, base - h, x + w, base), code)
    for k in range(1, int(h / 5)): g.ln([(x, base - h + k * 5), (x + w, base - h + k * 5)], .6)
    g.add(P([(x - 4, base - h), (x + w / 2, base - h - w * .45), (x + w + 4, base - h)]), roof)
    g.add(box(x + w * .2, base - h + 5, x + w * .2 + 7, base - h + 12), win); g.ln([(x + w * .2 + 3.5, base - h + 5), (x + w * .2 + 3.5, base - h + 12)], .7)
    if door: g.add(rbox(x + w * .62, base - 13, x + w * .62 + 7, base, 1.5), "w")
    g.add(box(x - 6, base, x + w + 6, base + 3.5), "w")
    return g

def boomhutdorp(cv):
    cv.put(box(0, 0, 200, 200), "b")
    cv.put(hill(160, 4, 150, .2), "l")
    # kruinen boven
    for k, (x, y, rx, ry) in enumerate(((22, 18, 40, 30), (100, 8, 50, 26), (178, 20, 40, 32), (60, 50, 26, 18), (140, 52, 26, 18))):
        cv.put(blob(x, y, rx, ry, 11, .36, k + 3), "gl"[k % 2])
    # stammen
    for x, w in ((30, 22), (100, 18), (170, 24)):
        cv.put(P([(x - w / 2 - 4, 200), (x - w / 2, 40), (x + w / 2, 40), (x + w / 2 + 4, 200)]), "w")
        for y in range(70, 190, 26): cv.ln(qbez((x - w / 2 + 2, y), (x, y + 4), (x + w / 2 - 2, y), 5), .9)
    # hutten
    cv.stamp(hut(10, 82, 34, 22, "o", "r", "b"))
    cv.stamp(hut(84, 64, 30, 20, "y", "g", "b"))
    cv.stamp(hut(152, 98, 36, 24, "o", "p", "b"))
    cv.stamp(hut(84, 132, 28, 18, "k", "r", "b"))
    # hangbruggen
    for (x0, y0), (x1, y1) in (((50, 84), (78, 66)), ((120, 66), (146, 100)), ((118, 134), (146, 100))):
        n = 6
        for k in range(n):
            t0, t1 = k / n + .01, (k + 1) / n - .01
            def pt(t): return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + 6 * math.sin(math.pi * t))
            a, b = pt(t0), pt(t1)
            cv.put(P([(a[0], a[1]), (b[0], b[1]), (b[0], b[1] + 3), (a[0], a[1] + 3)]), "w")
        cv.ln([(x0, y0 - 9)] + [(x0 + (x1 - x0) * t, y0 - 9 + (y1 - y0) * t + 6 * math.sin(math.pi * t)) for t in [i / 10 for i in range(1, 11)]], 1)
        for k in range(1, n): 
            t = k / n; cv.ln([(x0 + (x1 - x0) * t, y0 - 9 + (y1 - y0) * t + 6 * math.sin(math.pi * t)), (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + 6 * math.sin(math.pi * t))], .8)
    # ladders en touw
    for x0, y0, y1 in ((22, 86, 158), (172, 102, 158)):
        cv.ln([(x0, y0), (x0, y1)], 1.3); cv.ln([(x0 + 10, y0), (x0 + 10, y1)], 1.3)
        for y in range(int(y0) + 8, int(y1), 9): cv.ln([(x0, y), (x0 + 10, y)], 1.1)
    cv.ln([(130, 140), (130, 176)], 1.1); cv.put(box(122, 176, 140, 180), "r")
    # glijbaan van de lage hut
    cv.put(tube(qbez((112, 138), (124, 160), (150, 172), 12), 6), "r")
    # mensen en dieren
    cv.stamp(person("r", "n", "w", "short", "wave"), 32, 80, .4)
    cv.stamp(person("y", "b", "x", "curly", "hold"), 104, 62, .36)
    cv.stamp(person("g", "n", "o", "braids", "up"), 172, 96, .42)
    cv.stamp(person("p", "n", "y", "pony", "down", hands=((-12, -23), (13, -40))), 62, 92, .36)
    cv.stamp(person("t", "z", "w", "short", "hold"), 131, 178, .34)
    cv.stamp(person("o", "n", "w", "bun", "up", hands=((-6, -64), (6, -64))), 27, 190, .44)
    cv.stamp(bird("r", "o"), 142, 40, 1.0); cv.stamp(bird("b", "n"), 60, 30, .9, True)
    # bosbodem
    cv.put(box(0, 182, 200, 200).difference(box(0, 0, 200, 182)), "l")
    for x, c in ((60, "r"), (74, "o"), (150, "r")):
        cv.put(Point(x, 190).buffer(6, 24).intersection(box(x - 7, 183, x + 7, 190)), c); cv.put(box(x - 2, 190, x + 2, 197), "-")
        cv.put(circle(x - 2, 187, 1.4), "-")
    cv.stamp(rabbit("w"), 92, 196, .9); cv.stamp(bush(26, 12, "g", 4, "r"), 196, 200); cv.stamp(bush(20, 10, "g", 6), 112, 200)

kp9("boomhutdorp-in-het-bos", "Boomhutdorp in het bos", "Hoog in de bomen staan boomhutten met ladders, hangbruggen en een glijbaan. Kinderen klimmen, zwaaien en spelen, en beneden tussen de paddenstoelen hupt een konijn.", boomhutdorp, "natuur")

# ---------------------------------------------------------------- speeltuin
def speeltuin(cv):
    cv.put(box(0, 0, 200, 200), "b")
    cv.put(cloud(150, 20, 36, 2), "-"); sun_rays(cv, 30, 24, 10, 10)
    cv.stamp(tree(54, "g", seed=2), 182, 104); cv.stamp(tree(44, "l", seed=7), 8, 100)
    cv.put(box(0, 100, 200, 200), "l")
    # hek achter
    for x in range(0, 200, 8): cv.put(P([(x + 1, 108), (x + 4, 104), (x + 7, 108), (x + 7, 116), (x + 1, 116)]), "-")
    cv.put(box(0, 109, 200, 111.5), "-")
    # schommel
    cv.ln([(14, 48), (8, 128)], 3.4); cv.ln([(14, 48), (22, 128)], 3.4)
    cv.ln([(80, 48), (74, 128)], 3.4); cv.ln([(80, 48), (88, 128)], 3.4)
    cv.put(rbox(10, 44, 84, 50, 2), "r")
    cv.ln([(32, 50), (28, 98)], 1); cv.ln([(46, 50), (46, 98)], 1); cv.put(rbox(24, 98, 50, 102, 1), "y")
    cv.stamp(person("m", "n", "w", "pony", "up", hands=((-8, -45), (8, -45)), legs=True), 37, 116, .42)
    cv.ln([(60, 50), (66, 88)], 1); cv.ln([(72, 50), (80, 88)], 1); cv.put(rbox(62, 88, 84, 92, 1), "y")
    # glijbaan met klimtoren
    cv.put(box(108, 60, 112, 140), "w"); cv.put(box(132, 60, 136, 140), "w")
    cv.put(box(104, 82, 140, 88), "w")
    cv.put(P([(104, 60), (122, 40), (140, 60)]), "r")
    for y in range(94, 140, 9): cv.put(box(112, y, 132, y + 2.8), "y")
    slide = P(qbez((136, 82), (160, 96), (176, 140), 14) + qbez((188, 140), (168, 96), (140, 86), 14)[::-1][::-1] if False else qbez((136, 82), (160, 94), (174, 140), 14) + [(190, 140), (190, 134)] + qbez((180, 134), (164, 92), (140, 88), 14)[1:] )
    cv.put(slide, "t")
    cv.stamp(person("y", "b", "x", "curly", "up"), 122, 82, .34)
    cv.stamp(person("o", "n", "o", "short", "side", legs=True), 172, 134, .36)
    # wipwap
    cv.put(P([(20, 160), (24, 148), (28, 160)]), "z")
    cv.put(affinity.rotate(rbox(-30, -2, 30, 2, 1), -12, origin=(0, 0)).buffer(0).union(box(0, 0, 0, 0)).buffer(0), "o") if False else None
    plank = affinity.translate(affinity.rotate(rbox(-30, -2.2, 30, 2.2, 1), -14, origin=(0, 0)), 24, 146)
    cv.put(plank, "o")
    cv.stamp(person("g", "n", "w", "short", "hold"), 2, 158, .34)
    cv.stamp(person("r", "x", "y", "braids", "up"), 46, 140, .34)
    # zandbak
    cv.put(rbox(66, 152, 140, 188, 3), "w"); cv.put(rbox(70, 156, 136, 184, 2), "y")
    cv.stamp(person("b", "n", "x", "short", "hold", legs=False), 92, 176, .36)
    cv.put(P([(108, 168), (120, 168), (118, 180), (110, 180)]), "r"); cv.ln([(110, 168), (114, 162), (118, 168)], 1)
    cv.put(Point(126, 178).buffer(6, 24).intersection(box(118, 172, 134, 178)), "y")
    cv.put(P([(78, 176), (88, 172), (86, 182)]), "b")
    # draaimolen
    cv.put(ellipse(170, 176, 26, 8), "p"); cv.put(ellipse(170, 172, 26, 8), "m")
    cv.put(box(168, 152, 172, 172), "z")
    cv.ln([(150, 168), (170, 154), (190, 168)], 1.4)
    cv.stamp(person("t", "n", "w", "bun", "hold"), 160, 176, .3)
    cv.stamp(person("y", "z", "o", "short", "hold"), 182, 176, .3)
    # bankje met ouder
    cv.put(rbox(4, 178, 44, 182, 1), "w"); cv.put(rbox(4, 170, 44, 174, 1), "w")
    for x in (8, 40): cv.put(box(x - 1.4, 182, x + 1.4, 192), "x")
    cv.stamp(person("p", "n", "w", "long", "hold"), 24, 192, .38)
    cv.put(circle(56, 192, 5), "r"); cv.ln([(51, 192), (61, 192)], .9)
    cv.stamp(dog("o", "w"), 140, 198, .8, True)

kp9("drukke-speeltuin", "Drukke speeltuin", "Wat een drukte in de speeltuin: kinderen schommelen, glijden, wippen, draaien rond en bouwen in de zandbak. Ga jij ook spelen?", speeltuin, "sport")
