"""Batch 13e: gedetailleerde, rustgevende kleurplaten voor tieners en volwassenen (12+).

Alles wordt opgebouwd als een vlakverdeling (shapely): elk nieuw vlak wordt 'bovenop' gelegd en uit de
vlakken eronder geknipt, zodat er nooit overlappende of verstopte kleurvlakken zijn. Te kleine snippers
worden bij hun buurvlak gevoegd.
"""
import math, random, json, os, sys
from lib_gen import *
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, MultiPoint, box, GeometryCollection
from shapely.ops import unary_union, polygonize, substring
from shapely import affinity, delaunay_triangles, voronoi_polygons
from shapely.geometry.polygon import orient
from shapely.strtree import STRtree

MAT = [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}]
ONLY = set(sys.argv[1:])
PAGE = box(0, 0, 200, 200)

# ---------------------------------------------------------------- geometrie
def polys(g):
    if g is None or g.is_empty: return []
    if isinstance(g, Polygon): return [g]
    if hasattr(g, "geoms"):
        out = []
        for x in g.geoms: out += polys(x)
        return out
    return []

def ring_d(coords):
    c = list(coords)[:-1]
    return "M" + " L".join(f"{f(round(x, 1))} {f(round(y, 1))}" for x, y in c) + "Z"

def poly_d(p):
    p = orient(p, 1.0)
    return ring_d(p.exterior.coords) + "".join(ring_d(i.coords) for i in p.interiors)

class Canvas:
    """Schilder-volgorde: wat je later neerlegt ligt bovenop en wordt uit de rest geknipt."""
    def __init__(self, clip=PAGE):
        self.items = []; self.clip = clip
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
    def finish(self, sh, minw=1.4, mina=8, simplify=.12):
        parts = []
        for g, c in self.items:
            for p in polys(g):
                if p.area > .05: parts.append([p, c])
        # kleine of dunne snippers samenvoegen met de buur waar ze het langst aan grenzen
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
        for p, c in parts:
            # 'opening': haalt spriets en naden weg die smaller zijn dan de lijn (die dekt de naad toch af)
            p = p.buffer(-.45, join_style=2, mitre_limit=3).buffer(.45, join_style=2, mitre_limit=3)
            p = p.simplify(simplify, preserve_topology=True)
            if p.is_empty: continue
            p = unary_union([Polygon(q.exterior, [i for i in q.interiors if Polygon(i).area > 4]) for q in polys(p)])
            for q in polys(p): sh.region(poly_d(q), c)
        return len(parts)

def circle(cx, cy, r, res=24): return Point(cx, cy).buffer(r, res)
def ellipse(cx, cy, rx, ry, rot=0):
    e = affinity.scale(Point(0, 0).buffer(1, 32), rx, ry)
    return affinity.translate(affinity.rotate(e, rot, origin=(0, 0)), cx, cy)
def P(points): return Polygon(points).buffer(0)
def mirror(half, cx=100):
    """Rechterhelft (van boven naar onder) spiegelen tot een symmetrische veelhoek."""
    return P(list(half) + [(2 * cx - x, y) for x, y in reversed(half)])
def bez(p0, p1, p2, p3, n=16):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0],
             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]) for t in [i / n for i in range(n + 1)]]
def qbez(p0, p1, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]
def leaf(base, tip, w, bend=0.0, n=20):
    """Blad van base naar tip, breedte w (spits aan beide kanten)."""
    (x0, y0), (x1, y1) = base, tip
    L = math.dist(base, tip); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    left, right = [], []
    for i in range(n + 1):
        t = i / n; s = math.sin(math.pi * t) ** .9 * (1 - .25 * t) * w / 2; b = bend * math.sin(math.pi * t) * L
        cx, cy = x0 + ux * L * t + nx * b, y0 + uy * L * t + ny * b
        left.append((cx + nx * s, cy + ny * s)); right.append((cx - nx * s, cy - ny * s))
    return P(left + right[::-1])
def split_lines(g, lines):
    """Vlak g opdelen met lijnen (LineStrings)."""
    u = unary_union([g.boundary] + [ln.intersection(g.buffer(.01)) for ln in lines])
    out = []
    for p in polygonize(u):
        if g.contains(p.representative_point()): out.append(p)
    return out
def wedges(cx, cy, n, r=400, a0=-90):
    return [P([(cx, cy)] + [(cx + r * math.cos(math.radians(a0 + (i + t / 6) * 360 / n)), cy + r * math.sin(math.radians(a0 + (i + t / 6) * 360 / n))) for t in range(7)]) for i in range(n)]
def poisson(region, d, seed, tries=3000):
    rnd = random.Random(seed); pts = []
    x0, y0, x1, y1 = region.bounds
    for _ in range(tries):
        p = (rnd.uniform(x0, x1), rnd.uniform(y0, y1))
        if region.contains(Point(p)) and all(math.dist(p, q) >= d for q in pts): pts.append(p)
    return pts

# ---------------------------------------------------------------- patronen om een vlak mee te vullen
def pat_stripes(g, w, angle, codes, off=0):
    c = g.centroid; out = []
    for k in range(-40, 40):
        b = box(-300, off + k * w, 300, off + (k + 1) * w)
        b = affinity.translate(affinity.rotate(b, angle, origin=(0, 0)), c.x, c.y)
        x = b.intersection(g)
        if not x.is_empty: out.append((x, codes[k % len(codes)]))
    return out
def pat_waves(g, w, amp, wl, codes, angle=0):
    c = g.centroid; out = []
    for k in range(-30, 30):
        top = [(x, k * w + amp * math.sin(x / wl * 2 * math.pi)) for x in range(-260, 261, 3)]
        bot = [(x, (k + 1) * w + amp * math.sin(x / wl * 2 * math.pi)) for x in range(260, -261, -3)]
        b = affinity.translate(affinity.rotate(P(top + bot), angle, origin=(0, 0)), c.x, c.y)
        x = b.intersection(g)
        if not x.is_empty: out.append((x, codes[k % len(codes)]))
    return out
def pat_checker(g, s, angle, codes):
    c = g.centroid; out = []
    for i in range(-20, 20):
        for j in range(-20, 20):
            b = affinity.translate(affinity.rotate(box(i * s, j * s, (i + 1) * s, (j + 1) * s), angle, origin=(0, 0)), c.x, c.y)
            if not b.intersects(g): continue
            x = b.intersection(g)
            if not x.is_empty: out.append((x, codes[(i + j) % len(codes)]))
    return out
def pat_rings(g, cx, cy, w, codes, r0=0):
    out = []; prev = Point(cx, cy).buffer(r0, 32) if r0 else None
    if prev is not None: out.append((prev.intersection(g), codes[-1]))
    for k in range(60):
        a = Point(cx, cy).buffer(r0 + (k + 1) * w, 48)
        ring = a.difference(prev) if prev is not None else a
        x = ring.intersection(g)
        if not x.is_empty: out.append((x, codes[k % len(codes)]))
        prev = a
        if a.contains(g): break
    return out
def pat_rays(g, cx, cy, n, codes, a0=-90):
    return [(w.intersection(g), codes[i % len(codes)]) for i, w in enumerate(wedges(cx, cy, n, a0=a0)) if w.intersects(g)]
def pat_dots(g, s, r, code_dot, code_bg, stagger=True):
    c = g.centroid; dots = []
    for j in range(-20, 21):
        for i in range(-20, 21):
            x = c.x + i * s + (s / 2 if stagger and j % 2 else 0); y = c.y + j * s * (.866 if stagger else 1)
            d = circle(x, y, r, 16)
            if g.buffer(-.6).contains(d): dots.append(d)
    bg = g.difference(unary_union(dots)) if dots else g
    return [(bg, code_bg)] + [(d, code_dot if isinstance(code_dot, str) and len(code_dot) == 1 else code_dot[k % len(code_dot)]) for k, d in enumerate(dots)]
def pat_scales(g, r, codes, angle=0):
    c = g.centroid; cv = Canvas(g)
    for j in range(-16, 17):
        for i in range(-16, 17):
            x = i * 2 * r * .9 + (r * .9 if j % 2 else 0); y = j * r * .75
            d = affinity.translate(affinity.rotate(Point(x, y).buffer(r, 24), angle, origin=(0, 0)), c.x, c.y)
            if d.intersects(g): cv.put(d, codes[(i + j) % len(codes)])
    return cv.items
def pat_hex(g, r, codes, inner=None):
    c = g.centroid; out = []; h = r * math.sqrt(3)
    for j in range(-16, 17):
        for i in range(-16, 17):
            x = c.x + i * 1.5 * r; y = c.y + j * h + (h / 2 if i % 2 else 0)
            hx = P([(x + r * math.cos(math.radians(60 * k)), y + r * math.sin(math.radians(60 * k))) for k in range(6)])
            if not hx.intersects(g): continue
            code = codes[(i + 2 * j) % len(codes)]
            if inner:
                ih = affinity.scale(hx, inner, inner)
                out.append((hx.difference(ih).intersection(g), code)); out.append((ih.intersection(g), "-"))
            else: out.append((hx.intersection(g), code))
    return out
def pat_tris(g, s, codes, angle=0):
    c = g.centroid; out = []; h = s * math.sqrt(3) / 2
    for j in range(-20, 21):
        for k in range(-40, 41):
            x = k * s / 2; y = j * h
            up = (k + j) % 2 == 0
            t = P([(x, y + h), (x + s / 2, y), (x + s, y + h)] if up else [(x, y), (x + s, y), (x + s / 2, y + h)])
            t = affinity.translate(affinity.rotate(t, angle, origin=(0, 0)), c.x, c.y)
            if t.intersects(g): out.append((t.intersection(g), codes[(k + 2 * j) % len(codes)]))
    return out
def pat_bricks(g, w, h, codes, angle=0):
    c = g.centroid; out = []
    for j in range(-30, 31):
        for i in range(-20, 21):
            x = i * w + (w / 2 if j % 2 else 0)
            b = affinity.translate(affinity.rotate(box(x, j * h, x + w, (j + 1) * h), angle, origin=(0, 0)), c.x, c.y)
            if b.intersects(g): out.append((b.intersection(g), codes[(i + j) % len(codes)]))
    return out
def pat_voronoi(g, d, codes, seed):
    pts = poisson(g, d, seed)
    if len(pts) < 3: return [(g, codes[0])]
    vor = voronoi_polygons(MultiPoint(pts), extend_to=g.envelope.buffer(20))
    return [(v.intersection(g), codes[k % len(codes)]) for k, v in enumerate(vor.geoms) if v.intersects(g)]
def pat_flowers(g, s, codes):
    """Kleine bloemetjes (5 rondjes + hart) op een raster; de rest is achtergrond."""
    c = g.centroid; fl = []
    for j in range(-12, 13):
        for i in range(-12, 13):
            x = c.x + i * s + (s / 2 if j % 2 else 0); y = c.y + j * s * .87
            flower = unary_union([circle(x + s * .2 * math.cos(math.radians(72 * k - 90)), y + s * .2 * math.sin(math.radians(72 * k - 90)), s * .17) for k in range(5)])
            if g.buffer(-.6).contains(flower): fl.append((flower, circle(x, y, s * .11)))
    out = [(g.difference(unary_union([a for a, _ in fl])) if fl else g, codes[0])]
    for a, b in fl: out += [(a.difference(b), codes[1]), (b, codes[2])]
    return out

def kp12(slug, name, desc, cv_fn, cat="patronen", diff=3, holiday=None):
    if ONLY and slug not in ONLY: return
    sh = Sheet(200)
    extra = cv_fn(sh)
    meta = {"category": cat, "age": "12+", "kind": "kleurplaat", "difficulty": diff, "materials": MAT, "i18n": {"nl": {"name": name, "description": desc}}}
    if holiday: meta["holiday"] = holiday
    write(OUT, slug, sh, meta)


# ================================================================ dieren in facetten (low-poly)
def densify(poly, step):
    c = list(poly.exterior.coords); out = []
    for a, b in zip(c, c[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out
def facets(region, pts):
    tri = delaunay_triangles(MultiPoint(pts))
    return [t.intersection(region) for t in tri.geoms if t.intersects(region) and t.intersection(region).area > .5]
def tone(cx, cy, seed, codes, lx=-1, ly=-1, cx0=100, cy0=100, spread=110):
    v = ((cx - cx0) * lx + (cy - cy0) * ly) / spread + random.Random(seed).uniform(-.45, .45)
    k = 0 if v > .25 else (1 if v > -.35 else 2)
    return codes[min(k, len(codes) - 1)]

def bg_facets(cv, fg, codes, d=20, seed=1, lx=-1, ly=-1):
    pts = poisson(PAGE.buffer(-.1), d, seed) + [(x, y) for x in (0, 200) for y in (0, 200)] + [(x, 0) for x in range(25, 200, 25)] + [(x, 200) for x in range(25, 200, 25)] + [(0, y) for y in range(25, 200, 25)] + [(200, y) for y in range(25, 200, 25)]
    pts += densify(fg.buffer(2), 16)
    rest = PAGE.difference(fg)
    for i, t in enumerate(facets(rest, pts)):
        c = t.centroid; cv.put(t, tone(c.x, c.y, seed * 1000 + i, codes, lx, ly))

def low_poly(cv, region, zones, inner_d, seed, extra_pts=(), out_step=10):
    """zones: lijst (polygoon, tonen) - eerste die het midden van een facet bevat bepaalt de tonen."""
    pts = densify(region, out_step) + poisson(region.buffer(-3), inner_d, seed) + list(extra_pts)
    for i, t in enumerate(facets(region, pts)):
        c = t.centroid; codes = zones[-1][1]
        for z, cs in zones:
            if z.contains(c): codes = cs; break
        cv.put(t, tone(c.x, c.y, seed + i, codes))

def vos(sh):
    cv = Canvas()
    half = [(100, 58), (118, 54), (152, 8), (164, 60), (172, 84), (196, 118), (170, 126), (150, 142), (122, 168), (104, 184)]
    head = mirror(half)
    cv.put_many(pat_rays(PAGE, 100, 100, 36, "lg"))
    ear_r = P([(126, 54), (150, 18), (158, 62)]); ear_l = affinity.scale(ear_r, -1, 1, origin=(100, 0))
    tips = box(0, 0, 200, 26)
    white = mirror([(100, 152), (110, 148), (124, 130), (150, 114), (198, 118), (198, 200), (100, 200)])
    zones = [(tips, "xxx"), (ear_r, "---"), (ear_l, "---"), (white, "---"), (PAGE, "yor")]
    low_poly(cv, head, zones, 12, 31, [(100, 100), (100, 130), (76, 102), (124, 102), (100, 75)], 12)
    for s in (1, -1):
        e = P([(100 + s * 13, 104), (100 + s * 22, 97), (100 + s * 35, 99), (100 + s * 29, 108), (100 + s * 19, 110)])
        cv.put(e, "y"); cv.put(ellipse(100 + s * 23.5, 103.5, 2, 4.6), "x")
    cv.put(P([(90, 158), (110, 158), (100, 170)]), "x")
    cv.finish(sh)
    sh.line(poly_d(head), "l", "stroke-width:2.6")
kp12("vos-in-facetten", "Vos in facetten", "Een vossenkop opgebouwd uit driehoekjes, als een geslepen edelsteen. Kleur de facetten aan de lichte kant (linksboven) lichter en rechtsonder donkerder: zo krijgt de kop diepte.", vos, "dieren")

def strip_segments(line, w, step, codes, cap=True):
    """Een buis (gewei, tak, steel) langs een lijn, opgedeeld in stukjes van lengte step."""
    ln = LineString(line); tube = ln.buffer(w / 2, cap_style=1 if cap else 2, join_style=1)
    L = ln.length; cuts = []
    for k in range(1, int(L / step)):
        p = ln.interpolate(k * step); q = ln.interpolate(min(L, k * step + .5))
        dx, dy = q.x - p.x, q.y - p.y; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d * w, dx / d * w
        cuts.append(LineString([(p.x - nx, p.y - ny), (p.x + nx, p.y + ny)]))
    parts = split_lines(tube, cuts) if cuts else [tube]
    parts.sort(key=lambda g: ln.project(g.centroid))
    return [(g, codes[i % len(codes)]) for i, g in enumerate(parts)]

def hert(sh):
    cv = Canvas()
    cv.put_many(pat_rings(PAGE, 100, 120, 12, "bt"))
    half = [(100, 72), (118, 68), (132, 78), (137, 96), (130, 124), (121, 150), (113, 170), (104, 184)]
    head = mirror(half)
    ear_r = P([(128, 82), (152, 68), (184, 64), (166, 84), (142, 96), (132, 96)]); ear_l = affinity.scale(ear_r, -1, 1, origin=(100, 0))
    for s in (1, -1):
        beam = [(100 + s * 12, 76), (100 + s * 20, 52), (100 + s * 34, 34), (100 + s * 52, 22), (100 + s * 72, 18)]
        tines = [[(100 + s * 19, 54), (100 + s * 11, 36), (100 + s * 11, 20)], [(100 + s * 33, 35), (100 + s * 31, 18), (100 + s * 35, 6)],
                 [(100 + s * 52, 22), (100 + s * 60, 8)], [(100 + s * 27, 43), (100 + s * 48, 41), (100 + s * 64, 35)]]
        ant = unary_union([LineString(beam).buffer(3.6, join_style=1)] + [LineString(t).buffer(2.9, join_style=1) for t in tines])
        low_poly(cv, ant, [(PAGE, "yww")], 30, 70 + s, (), 7)
    for e in (ear_r, ear_l):
        cv.put(e, "w"); cv.put(e.buffer(-4.5), "k")
    white = mirror([(100, 156), (110, 152), (118, 160), (118, 200), (100, 200)])
    zones = [(white, "---"), (PAGE, "oww")]
    low_poly(cv, head, zones, 11, 52, [(100, 120), (100, 150), (80, 108), (120, 108)], 10)
    for s in (1, -1):
        cv.put(ellipse(100 + s * 21, 107, 6.5, 4.6, s * 20), "x"); cv.put(circle(100 + s * 19.5, 105.5, 1.8, 10), "-")
    cv.put(ellipse(100, 177, 11, 7), "x")
    cv.finish(sh)
    sh.line(poly_d(head), "l", "stroke-width:2.4")
kp12("hert-in-facetten", "Hert in facetten", "Een hertenkop van geslepen vlakjes met een groot gewei. Geef het gewei afwisselend licht- en donkerbruin en kleur de ringen erachter als een avondlucht.", hert, "dieren")

def uil(sh):
    cv = Canvas()
    cv.put_many(pat_voronoi(PAGE, 24, "nbp", 3))
    cv.put(circle(150, 46, 34, 48), "y")
    for x, y, r in ((140, 36, 6), (160, 56, 5), (156, 32, 3.5)): cv.put(circle(x, y, r), "z")
    body = unary_union([ellipse(100, 124, 52, 60), ellipse(100, 74, 50, 40)])
    tuft_r = P([(130, 52), (146, 20), (150, 58)]); tuft_l = affinity.scale(tuft_r, -1, 1, origin=(100, 0))
    for t in (tuft_r, tuft_l): cv.put_many(pat_stripes(t, 5, 70 if t is tuft_r else -70, "wo"))
    cv.put_many(pat_scales(body, 7, "woy"))
    belly = ellipse(100, 138, 30, 40)
    cv.put_many(pat_scales(belly, 5, "-k"))
    for s in (1, -1):
        wing = leaf((100 + s * 40, 92), (100 + s * 30, 182), 34, -.12 * s)
        cv.put_many(pat_stripes(wing, 6, s * 12, "wo"))
    face = unary_union([circle(78, 80, 25, 48), circle(122, 80, 25, 48)])
    cv.put(face, "y")
    for cx in (78, 122):
        ring = circle(cx, 80, 23, 48).difference(circle(cx, 80, 13, 48))
        cv.put_many(pat_rays(ring, cx, 80, 18, "oy"))
        cv.put(circle(cx, 80, 12.5, 40), "o"); cv.put(circle(cx, 80, 7, 32), "x"); cv.put(circle(cx - 2.5, 77, 2.4, 12), "-")
    cv.put(P([(92, 92), (108, 92), (100, 110)]), "o")
    branch = P([(0, 178), (60, 172), (140, 176), (200, 168), (200, 186), (140, 190), (60, 188), (0, 194)])
    cv.put_many(pat_stripes(branch, 5.5, -3, "wo"))
    for lx, ly, a in ((22, 172, -30), (176, 166, 210)):
        lf = leaf((lx, ly), (lx + 26 * math.cos(math.radians(a)), ly - 26 * math.sin(math.radians(a))), 13)
        cv.put_many([(g, "gl"[i % 2]) for i, g in enumerate(split_lines(lf, [LineString([(lx, ly), (lx + 30 * math.cos(math.radians(a)), ly - 30 * math.sin(math.radians(a)))])]))])
    for fx in (86, 114):
        for k in (-5, 0, 5): cv.put(ellipse(fx + k, 176, 2.6, 5), "y")
    cv.finish(sh)
kp12("uil-met-veren", "Uil met verenpatroon", "Een uil op een tak voor de volle maan, met honderden kleine veertjes. Kleur de veertjes in drie bruintinten door elkaar en de lucht in donkerblauw en paars.", uil, "dieren")

def vis(sh):
    cv = Canvas()
    cv.put_many(pat_waves(PAGE, 16, 4, 70, "bt"))
    for x, y, r in ((30, 40, 6), (40, 24, 4), (34, 12, 3), (172, 150, 5), (180, 136, 3.5)): cv.put(circle(x, y, r), "-"); cv.put(circle(x - r * .35, y - r * .35, r * .3, 10), "-")
    for x0, h in ((14, 96), (186, 48), (64, 52), (124, 40)):
        pts = [(x0 + 7 * math.sin(t / 11), 202 - t) for t in range(0, h, 3)]
        cv.put_many(strip_segments(pts, 9, 10, "gl"))
    body = P(bez((30, 100), (40, 52), (120, 40), (156, 92), 24) + bez((156, 92), (158, 96), (158, 100), (156, 106), 4)[1:] + bez((156, 106), (120, 158), (40, 150), (30, 100), 24)[1:])
    tail = P([(150, 99), (190, 60), (182, 100), (190, 140)])
    cv.put_many(pat_rays(tail, 150, 99, 40, "ory", a0=-60))
    top = P(bez((60, 64), (70, 30), (110, 22), (130, 66), 16))
    cv.put_many(pat_rays(top, 100, 90, 60, "yo", a0=-160))
    bot = P(bez((80, 130), (90, 162), (118, 168), (124, 124), 16))
    cv.put_many(pat_rays(bot, 100, 110, 60, "yo", a0=40))
    cv.put_many(pat_scales(body, 6.5, "oyr"))
    head = body.intersection(Point(-20, 100).buffer(74, 64))
    cv.put(head, "o")
    cv.put(circle(44, 92, 9, 32), "y"); cv.put(circle(44, 92, 5, 24), "x"); cv.put(circle(42.5, 90.5, 1.6, 10), "-")
    lip = P([(30, 100), (38, 104), (34, 108)])
    side = P(bez((80, 104), (86, 92), (100, 92), (104, 106), 12) + bez((104, 106), (96, 112), (88, 112), (80, 104), 12)[1:])
    cv.put_many(pat_stripes(side, 4, 60, "ky"))
    cv.finish(sh)
    sh.line("M32 106Q37 108 41 104", "l")
kp12("vis-met-schubben", "Vis met schubben", "Een dikke vis met heel veel schubben tussen golvend water en wiergroen. Kleur de schubben van donker op de rug naar licht op de buik.", vis, "zee")

# ================================================================ botanisch
def pinna(base, tip, w, lobes, codes, bend=0.0):
    """Varenblaadje: blad in lobjes langs de as, plus een nerf in het midden."""
    lf = leaf(base, tip, w, bend)
    L = math.dist(base, tip); ux, uy = (tip[0] - base[0]) / L, (tip[1] - base[1]) / L; nx, ny = -uy, ux
    cuts = [LineString([base, tip])]
    for k in range(1, lobes):
        t = k / lobes; px, py = base[0] + ux * L * t, base[1] + uy * L * t
        cuts.append(LineString([(px, py), (px + (ux * .35 + nx) * w, py + (uy * .35 + ny) * w)]))
        cuts.append(LineString([(px, py), (px + (ux * .35 - nx) * w, py + (uy * .35 - ny) * w)]))
    parts = split_lines(lf, cuts)
    return [(g, codes[i % len(codes)]) for i, g in enumerate(parts)]

def frond(cv, pts, maxlen, w0, codes, lobes=4, side_angle=55, step=11):
    ln = LineString(pts); L = ln.length
    n = int(L / step); last = 0
    for k in range(1, n):
        t = k / n; p = ln.interpolate(t * L); q = ln.interpolate(min(L, t * L + 1))
        dx, dy = q.x - p.x, q.y - p.y; d = math.hypot(dx, dy) or 1; ux, uy = dx / d, dy / d
        size = maxlen * (1 - t) ** .8 * (.6 + .4 * min(1, t * 5))
        if size < 8: continue
        last = t
        for s in (1, -1):
            a = math.radians(side_angle) * s
            vx, vy = ux * math.cos(a) - uy * math.sin(a), ux * math.sin(a) + uy * math.cos(a)
            tip = (p.x + vx * size, p.y + vy * size)
            cv.put_many(pinna((p.x, p.y), tip, max(6, w0 * min(1, size / maxlen * 1.4)), max(2, round(lobes * size / maxlen)), codes, .1 * s))
    cv.put(substring(ln, 0, last * L + 4).buffer(1.8, cap_style=1), "w")

def varen(sh):
    cv = Canvas()
    arch = unary_union([box(14, 60, 186, 200), Point(100, 60).buffer(86, 64)]).intersection(PAGE)
    cv.put_many(pat_voronoi(PAGE.difference(arch), 14, "bt", 5))
    cv.put_many(pat_rings(arch, 100, 200, 34, "k-"))
    frond(cv, bez((128, 198), (150, 150), (160, 90), (180, 34), 30), 44, 12, "lg", 5, 64)
    frond(cv, bez((88, 198), (60, 150), (50, 90), (24, 30), 30), 48, 12, "gl", 5, 62)
    # opgerold jong blad (spiraal)
    sp = [(104 + r * math.cos(t), 104 + r * math.sin(t)) for t, r in [(i / 10, 16 * math.exp(-i / 60)) for i in range(0, 120)]]
    stem = bez((110, 198), (106, 160), (120, 130), (120, 104), 14)
    cv.put_many(strip_segments(stem + sp[1:70], 6, 7, "gl"))
    cv.finish(sh)
kp12("varens-in-een-boog", "Varens in een boog", "Twee grote varens en een opgerold jong varenblad onder een boog, met een mozaïekrand. Gebruik twee of drie groentinten en houd de achtergrond zacht.", varen, "natuur")

def veined_leaf(base, tip, w, nveins, codes, bend=0.0):
    lf = leaf(base, tip, w, bend)
    L = math.dist(base, tip); ux, uy = (tip[0] - base[0]) / L, (tip[1] - base[1]) / L; nx, ny = -uy, ux
    cuts = [LineString([(base[0] - ux, base[1] - uy), (tip[0] + ux, tip[1] + uy)])]
    for k in range(1, nveins + 1):
        t = k / (nveins + 1) * .9; px, py = base[0] + ux * L * t, base[1] + uy * L * t
        for s in (1, -1): cuts.append(LineString([(px, py), (px + (ux * .7 + s * nx) * w, py + (uy * .7 + s * ny) * w)]))
    parts = split_lines(lf, cuts)
    parts.sort(key=lambda g: (round(((g.centroid.x - base[0]) * nx + (g.centroid.y - base[1]) * ny) > 0), (g.centroid.x - base[0]) * ux + (g.centroid.y - base[1]) * uy))
    half = len(parts) // 2
    return [(g, codes[(i + (1 if i >= half else 0)) % len(codes)]) for i, g in enumerate(parts)]

def bessen(sh):
    cv = Canvas()
    cv.put_many(pat_checker(PAGE, 22, 45, "k-"))
    main = bez((-4, 186), (60, 160), (120, 120), (204, 30), 30)
    twigs = [bez((70, 152), (80, 130), (76, 112), (70, 96), 10), bez((120, 118), (140, 120), (152, 128), (164, 142), 10), bez((150, 84), (140, 64), (128, 52), (112, 44), 10)]
    for t in twigs: cv.put_many(strip_segments(t, 4, 9, "w"))
    cv.put_many(strip_segments(main, 7, 11, "w"))
    leaves = [((40, 170), (14, 132)), ((96, 136), (118, 160)), ((60, 158), (40, 196)), ((136, 104), (110, 80)), ((172, 64), (196, 92)), ((172, 64), (156, 28)), ((100, 130), (102, 90)), ((24, 180), (2, 168))]
    for b, t in leaves: cv.put_many(veined_leaf(b, t, max(12, math.dist(b, t) * .42), 3, "gl", .06))
    rnd = random.Random(9)
    for cx, cy, n in ((66, 92, 7), (166, 148, 7), (106, 40, 6), (150, 100, 4)):
        pts = [(cx, cy)]
        while len(pts) < n:
            p = (cx + rnd.uniform(-15, 15), cy + rnd.uniform(-15, 15))
            if all(math.dist(p, q) > 9 for q in pts): pts.append(p)
        for x, y in sorted(pts, key=lambda p: p[1]):
            cv.put(circle(x, y, 7.2, 32), "r"); cv.put(circle(x - 2.6, y - 2.6, 2.2, 12), "-")
    cv.finish(sh)
kp12("tak-met-bessen", "Tak met bessen", "Een takje met bladeren en trosjes ronde bessen op een ruitjesachtergrond. Laat de lichtvlekjes op de bessen wit, dan glanzen ze.", bessen, "natuur")

def fantasiebloem(sh):
    cv = Canvas()
    cv.put_many(pat_waves(PAGE, 15, 3.5, 60, "b-", 20))
    cx, cy = 100, 86
    stem = bez((100, 200), (96, 170), (104, 140), (100, 100), 16)
    cv.put_many(strip_segments(stem, 7, 12, "gl"))
    cv.put_many(veined_leaf((100, 168), (54, 136), 26, 4, "gl", -.1))
    cv.put_many(veined_leaf((101, 150), (150, 128), 24, 4, "gl", .1))
    for i in range(10):
        a = math.radians(i * 36 - 90)
        pet = leaf((cx + 14 * math.cos(a), cy + 14 * math.sin(a)), (cx + 80 * math.cos(a), cy + 80 * math.sin(a)), 34)
        cv.put_many([(g, c) for g, c in pat_rings(pet, cx, cy, 9, "mk")])
    for i in range(10):
        a = math.radians(i * 36 - 72)
        pet = leaf((cx + 12 * math.cos(a), cy + 12 * math.sin(a)), (cx + 52 * math.cos(a), cy + 52 * math.sin(a)), 24)
        mid = LineString([(cx, cy), (cx + 60 * math.cos(a), cy + 60 * math.sin(a))])
        parts = split_lines(pet, [mid] + [LineString(Point(cx, cy).buffer(r, 48).exterior.coords) for r in (28, 40)])
        cv.put_many([(g, "pm"[k % 2]) for k, g in enumerate(parts)])
    cv.put(circle(cx, cy, 22, 64), "o")
    cv.put_many(pat_rays(circle(cx, cy, 22, 64).difference(circle(cx, cy, 15, 48)), cx, cy, 24, "oy"))
    cv.put_many(pat_dots(circle(cx, cy, 15, 48), 6.2, 2.3, "w", "y"))
    cv.finish(sh)
kp12("fantasiebloem", "Fantasiebloem", "Een grote, verzonnen bloem met twee kransen bloemblaadjes vol ringen en een hart van zaadjes. Kleur de ringen afwisselend licht en donker, van binnen naar buiten.", fantasiebloem, "natuur")

# ================================================================ landschappen
def ridge(x0, x1, y, amp, seed, step=8):
    rnd = random.Random(seed); pts = []; v = 0
    for x in range(x0, x1 + 1, step):
        v = max(-1, min(1, v + rnd.uniform(-.8, .8)))
        pts.append((x, y - amp * (.5 + .5 * math.sin(x / 31 + seed) * math.cos(x / 53 + seed * 2)) - v * amp * .25))
    return pts

def bergen(sh):
    cv = Canvas()
    sky = box(0, 0, 200, 200)
    cv.put_many(pat_rays(sky, 146, 52, 30, "b-"))
    cv.put_many(pat_rings(circle(146, 52, 22, 64), 146, 52, 7, "yo"))
    for x, y, s in ((40, 34, 1), (90, 22, .7)):
        cl = unary_union([circle(x - 12 * s, y + 3 * s, 8 * s), circle(x, y - 3 * s, 11 * s), circle(x + 13 * s, y + 2 * s, 9 * s), box(x - 20 * s, y + 2 * s, x + 22 * s, y + 11 * s)])
        cv.put(cl, "-")
    rnd = random.Random(12)
    layers = [([(-6, 70), (34, 44), (78, 62), (112, 36), (160, 58), (204, 40)], 128, "pn", 16),
              ([(-10, 92), (20, 74), (66, 96), (98, 70), (140, 84), (178, 66), (212, 88)], 140, "nb", 0),
              ([(-10, 118), (44, 98), (96, 116), (150, 100), (210, 116)], 156, "tg", 0),
              ([(-10, 140), (30, 128), (80, 144), (128, 132), (176, 146), (210, 136)], 168, "lg", 0)]
    for peaks, base, codes, snow in layers:
        rp = []
        for (x1, y1), (x2, y2) in zip(peaks, peaks[1:]):
            vx = (x1 + x2) / 2 + rnd.uniform(-6, 6); vy = max(y1, y2) + rnd.uniform(10, 22)
            for t in (0, .35, .7): rp.append((x1 + (vx - x1) * t, y1 + (vy - y1) * t + (rnd.uniform(-3, 3) if t else 0)))
            for t in (0, .35, .7): rp.append((vx + (x2 - vx) * t, vy + (y2 - vy) * t + (rnd.uniform(-3, 3) if t else 0)))
        rp.append(peaks[-1])
        poly = P(rp + [(212, 205), (-12, 205)]).intersection(box(-10, 0, 210, 200))
        cuts = [LineString([p, (p[0] + 4, 210)]) for p in peaks]
        cuts += [LineString([p, (p[0] - 12, p[1] + 40)]) for p in peaks[1:-1]]
        parts = split_lines(poly, cuts)
        parts.sort(key=lambda g: g.centroid.x)
        cv.put_many([(g, codes[k % 2]) for k, g in enumerate(parts)])
        if snow:
            for px, py in peaks:
                zz = [(px - snow * 1.6, py + snow * 1.3), (px - snow * .8, py + snow * .8), (px - snow * .3, py + snow * 1.3), (px + snow * .3, py + snow * .7), (px + snow * .9, py + snow * 1.2), (px + snow * 1.7, py + snow * 1.2)]
                cap_ = P([(px - snow * 1.6, py - 30), (px + snow * 1.7, py - 30)] + zz[::-1]).intersection(poly)
                cv.put(cap_, "-")
    lake = box(0, 170, 200, 200)
    cv.put_many(pat_waves(lake, 6, 1.2, 25, "bt"))
    for tx, ty, s in ((22, 178, 1.2), (40, 186, .8), (8, 190, .7), (170, 176, 1.3), (188, 188, .8), (150, 188, .8), (60, 190, .6)):
        cv.put(box(tx - 2 * s, ty, tx + 2 * s, ty + 10 * s), "w")
        for k in range(3):
            w = (14 - k * 3) * s; yb = ty - k * 9 * s
            cv.put(P([(tx - w, yb + 2 * s), (tx, yb - 14 * s), (tx + w, yb + 2 * s)]), "g")
    cv.finish(sh)
kp12("bergen-in-lagen", "Bergen in lagen", "Vier rijen bergen achter elkaar, van ver naar dichtbij, met een meer en dennen. Maak de verste bergen het lichtst en de dichtste het donkerst, dan zie je diepte.", bergen, "natuur", 2)

def nachtstad(sh):
    cv = Canvas(); rnd = random.Random(4)
    cv.put_many(pat_rings(PAGE, 150, 36, 13, "np"))
    cv.put(circle(150, 36, 17, 64), "y")
    for x, y, r in ((144, 30, 4), (156, 42, 3), (153, 28, 2.5)): cv.put(circle(x, y, r), "z")
    for x, y in ((20, 20), (54, 40), (96, 16), (110, 52), (186, 74), (30, 64), (76, 70)):
        cv.put(P(star_pts(x, y, 6, 2.6)), "y")
    def building(x, w, top, roof, code):
        body = box(x, top, x + w, 172)
        if roof == "punt": body = unary_union([body, P([(x, top), (x + w / 2, top - w * .6), (x + w, top)])])
        if roof == "koepel": body = unary_union([body, Point(x + w / 2, top).buffer(w / 2, 32).intersection(box(x, top - w, x + w, top))])
        if roof == "trap": body = unary_union([body, box(x + w * .15, top - 8, x + w * .85, top), box(x + w * .32, top - 16, x + w * .68, top - 8)])
        if roof == "spits": body = unary_union([body, P([(x + w * .4, top), (x + w / 2, top - 30), (x + w * .6, top)])])
        cv.put(body, code)
        ww, wh, gx, gy = 4.5, 6, 3.5, 4.5
        n = int((w - gx) // (ww + gx)); m = int((172 - top - 8) // (wh + gy))
        ox = x + (w - (n * ww + (n - 1) * gx)) / 2
        for j in range(m):
            for i in range(n):
                cv.put(box(ox + i * (ww + gx), top + 6 + j * (wh + gy), ox + i * (ww + gx) + ww, top + 6 + j * (wh + gy) + wh), "y" if rnd.random() < .45 else "x")
    for x, w, top, roof in ((-4, 30, 96, "trap"), (24, 22, 112, "plat"), (44, 26, 78, "spits"), (70, 30, 104, "koepel"), (98, 22, 88, "plat"), (118, 34, 120, "punt"), (150, 24, 92, "trap"), (172, 32, 108, "plat")):
        building(x, w, top, roof, "z" if roof != "koepel" else "t")
    cv.put_many(pat_waves(box(0, 172, 200, 200), 5, 1.2, 22, "nb"))
    for x, w in ((8, 14), (30, 10), (58, 18), (88, 12), (126, 16), (160, 12), (182, 10)):
        for k in range(3): cv.put(box(x + k * 2, 177 + k * 7, x + w - k * 2, 180 + k * 7), "y")
    cv.finish(sh)
kp12("stad-bij-nacht", "Stad bij nacht", "Een skyline bij volle maan met honderden ramen en hun weerspiegeling in het water. Kies zelf welke ramen nog licht geven: geel of oranje, de rest donker.", nachtstad, "wereld")

# ================================================================ zentangle-achtig
def zt_patterns(k, g):
    c = g.centroid; x0, y0, x1, y1 = g.bounds
    opts = [
        lambda: pat_stripes(g, 4.5, 35, "py"),
        lambda: pat_checker(g, 6.5, 45, "nb"),
        lambda: pat_dots(g, 8, 2.6, "r", "k"),
        lambda: pat_scales(g, 5.5, "tb"),
        lambda: pat_rings(g, x0, y1, 4.5, "oy"),
        lambda: pat_hex(g, 5.5, "g", .5),
        lambda: pat_tris(g, 10, "mk"),
        lambda: pat_bricks(g, 10, 5, "wo", 20),
        lambda: pat_waves(g, 5, 1.6, 16, "bt", -30),
        lambda: pat_flowers(g, 13, "lmy"),
        lambda: pat_rays(g, x1, y0, 22, "yo"),
        lambda: pat_stripes(g, 3.5, -50, "gl"),
    ]
    return opts[k % len(opts)]()

def zentangle(cv, region, cuts, order, seed=0):
    parts = split_lines(region, cuts)
    parts.sort(key=lambda g: (round(g.centroid.y / 30), g.centroid.x))
    for i, g in enumerate(parts): cv.put_many(zt_patterns(order[i % len(order)], g))

def zt_blad(sh):
    cv = Canvas()
    lf = leaf((34, 186), (170, 14), 112, .05, 40)
    stem = bez((34, 186), (26, 192), (20, 196), (12, 199), 6)
    cv.put(LineString(stem).buffer(3, cap_style=1), "w")
    mid = LineString(bez((30, 192), (80, 120), (110, 80), (174, 10), 20))
    cuts = [mid]
    for t in (.18, .36, .54, .72):
        p = mid.interpolate(t, normalized=True)
        cuts.append(LineString(bez((p.x, p.y), (p.x - 20, p.y - 10), (p.x - 40, p.y - 20), (p.x - 80, p.y - 20), 10)))
        cuts.append(LineString(bez((p.x, p.y), (p.x + 16, p.y + 4), (p.x + 30, p.y + 20), (p.x + 70, p.y + 30), 10)))
    zentangle(cv, lf, cuts, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    cv.finish(sh)
    sh.line(poly_d(lf), "l", "stroke-width:2.4")
kp12("zentangle-blad", "Zentangle: blad", "Een groot blad, verdeeld in vakken met elk een eigen patroon. Kies per vak twee kleuren die bij elkaar passen, of kleur alles in groentinten en houd de patronen zichtbaar.", zt_blad)

def zt_tegel(sh):
    cv = Canvas()
    tile = box(8, 8, 192, 192).buffer(-6, join_style=1).buffer(6, join_style=1)
    border = box(0, 0, 200, 200).difference(tile)
    cv.put_many(pat_rays(border, 100, 100, 48, "nb"))
    cuts = [LineString(bez((0, 40), (80, 70), (100, 140), (200, 170), 30)), LineString(bez((60, 0), (40, 80), (140, 110), (120, 200), 30)),
            LineString(bez((0, 150), (60, 120), (150, 60), (200, 30), 30)), LineString(bez((150, 0), (170, 70), (170, 140), (200, 120), 30))]
    zentangle(cv, tile, cuts, [3, 0, 9, 1, 4, 6, 2, 8, 5, 11, 7, 10, 2, 3])
    cv.finish(sh)
kp12("zentangle-tegel", "Zentangle: tegel", "Een vierkante tegel die door vier slingerende lijnen in vakken is verdeeld, elk met een ander patroon. Kleur rustig vak voor vak; je mag patronen ook gewoon wit laten.", zt_tegel)

def zt_kat(sh):
    cv = Canvas()
    cv.put_many(pat_rings(PAGE, 100, 210, 14, "k-"))
    body = unary_union([ellipse(100, 146, 50, 46), ellipse(100, 112, 34, 30)])
    tail = LineString(bez((140, 176), (186, 176), (190, 130), (170, 112), 20)).buffer(7, cap_style=1)
    head = unary_union([ellipse(100, 70, 36, 31), P([(68, 64), (70, 24), (96, 44)]), P([(132, 64), (130, 24), (104, 44)])])
    zentangle(cv, tail, [LineString([(150, 160), (170, 190)]), LineString([(168, 150), (196, 160)]), LineString([(166, 128), (190, 116)])], [8, 1, 3, 6])
    zentangle(cv, body, [LineString(bez((50, 120), (90, 140), (110, 140), (150, 118), 20)), LineString(bez((100, 80), (90, 140), (110, 160), (100, 200), 20)),
                         LineString(bez((50, 160), (80, 170), (120, 165), (150, 175), 20))], [9, 0, 5, 3, 7, 2, 11])
    cv.put(head, "-")
    for s in (1, -1):
        ear = P([(100 + s * 30, 58), (100 + s * 30, 30), (100 + s * 10, 46)])
        cv.put_many(pat_stripes(ear.buffer(-2), 3.5, 0, "km"))
    for dx, h in ((-9, 12), (0, 16), (9, 12)):
        cv.put(P([(100 + dx - 3, 42), (100 + dx + 3, 42), (100 + dx, 42 + h)]), "w")
    for s in (1, -1):
        cv.put(ellipse(100 + s * 18, 188, 12, 7), "-")
    for s in (1, -1):
        cv.put(ellipse(100 + s * 14, 72, 7.5, 5.5), "l"); cv.put(ellipse(100 + s * 14, 72, 2, 5), "x")
    cv.put(P([(95, 82), (105, 82), (100, 87)]), "m")
    cv.finish(sh)
    sh.line("M100 87V91M100 91Q95 95 91 92M100 91Q105 95 109 92", "l")
    for s in (1, -1):
        sh.line(f"M{100 + s * 20} 84L{100 + s * 40} 80M{100 + s * 20} 88L{100 + s * 40} 90", "l", "stroke-width:1")
kp12("zentangle-kat", "Zentangle: kat", "Een zittende kat met vakjes vol patronen op zijn lijf en staart. Kleur de patronen in twee of drie tinten van dezelfde kleur, dan blijft de kat één geheel.", zt_kat, "dieren")

# ================================================================ geometrie
def ster8(sh):
    cv = Canvas(); s = 40
    for i in range(-1, 7):
        for j in range(-1, 7):
            cx, cy = i * s, j * s
            if not PAGE.intersects(box(cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2)): continue
            cv.put(box(cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), "r")
            cv.put(circle(cx, cy, 7, 24), "y")
    for i in range(-1, 6):
        for j in range(-1, 6):
            cx, cy = 20 + i * s, 20 + j * s
            R, r = s / 2, s / 2 * .7654
            st = P([(cx + (R if k % 2 == 0 else r) * math.cos(math.radians(k * 22.5)), cy + (R if k % 2 == 0 else r) * math.sin(math.radians(k * 22.5))) for k in range(16)])
            inner = [(cx + r * math.cos(math.radians(22.5 + 45 * k)), cy + r * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
            octa = P(inner)
            pieces = [(g, "n") for g in polys(st.difference(octa))]
            small = P(star_pts(cx, cy, 10, 5, 8))
            ring = octa.difference(small)
            for k, g in enumerate(split_lines(ring, [LineString([(cx, cy), (cx + 30 * math.cos(math.radians(22.5 + 45 * k)), cy + 30 * math.sin(math.radians(22.5 + 45 * k)))]) for k in range(8)])):
                pieces.append((g, "tb"[k % 2]))
            pieces.append((small, "y"))
            cv.put_many(pieces)
    cv.finish(sh)
kp12("sterpatroon-achtpunt", "Sterpatroon met achtpuntige sterren", "Een regelmatig patroon van achtpuntige sterren en kruisen, geïnspireerd op Islamitische tegelkunst. Kies een vast kleurenschema en herhaal het overal: dan gaat het patroon pas echt stralen.", ster8)

def ster6(sh):
    cv = Canvas(); r = 23; h = r * math.sqrt(3)
    for col in range(-1, 11):
        for row in range(-1, 8):
            cx = 100 + (col - 4) * 1.5 * r; cy = 100 + (row - 3) * h + (h / 2 if col % 2 else 0)
            hexa = P([(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k))) for k in range(6)])
            if not hexa.intersects(PAGE): continue
            star = P([(cx + (r if k % 2 == 0 else r / math.sqrt(3)) * math.cos(math.radians(30 * k)), cy + (r if k % 2 == 0 else r / math.sqrt(3)) * math.sin(math.radians(30 * k))) for k in range(12)])
            core = P([(cx + r / math.sqrt(3) * math.cos(math.radians(30 + 60 * k)), cy + r / math.sqrt(3) * math.sin(math.radians(30 + 60 * k))) for k in range(6)])
            small = P([(cx + 6 * math.cos(math.radians(60 * k)), cy + 6 * math.sin(math.radians(60 * k))) for k in range(6)])
            pieces = [(g, "y") for g in polys(hexa.difference(star))]
            pieces += [(g, "rp"[k % 2]) for k, g in enumerate(sorted(polys(star.difference(core)), key=lambda g: math.atan2(g.centroid.y - cy, g.centroid.x - cx)))]
            pieces += [(g, "t") for g in polys(core.difference(small))] + [(small, "n")]
            cv.put_many(pieces)
    cv.finish(sh)
kp12("sterpatroon-zespunt", "Sterpatroon met zespuntige sterren", "Zeshoeken met elk een zespuntige ster erin; samen vormen de driehoekjes ertussen nieuwe sterren. Kleur eerst alle punten van één kleur en kijk welke figuren er verschijnen.", ster6)

def vlechtring(sh):
    cv = Canvas()
    cv.put_many(pat_tris(PAGE, 20, "bt"))
    disk = circle(100, 100, 92, 96)
    cv.put(disk, "-")
    def strand(R, A, n, ph, w):
        pts = [((100 + (R + A * math.sin(n * t + ph)) * math.cos(t)), 100 + (R + A * math.sin(n * t + ph)) * math.sin(t)) for t in [k * 2 * math.pi / 720 for k in range(720)]]
        ln = LineString(pts + [pts[0]])
        return ln, ln.buffer(w / 2, join_style=1)
    for R, A, n, w, codes in ((70, 13, 9, 9, ("rm", "nb")), (36, 8, 6, 7, ("yo", "gl"))):
        lines = [strand(R, A, n, 0, w), strand(R, A, n, math.pi, w)]
        bands = [b for _, b in lines]
        # kruispunten: sin(n t) = 0
        under = [[], []]
        for j in range(2 * n):
            t = j * math.pi / n
            px, py = 100 + R * math.cos(t), 100 + R * math.sin(t)
            top = j % 2; bot = 1 - top
            under[bot].append(bands[top].buffer(1.6).intersection(circle(px, py, w * 1.6)))
        for k in (0, 1):
            g = bands[k].difference(unary_union(under[k]))
            ln = lines[k][0]
            pieces = []
            for seg in polys(g):
                halves = split_lines(seg, [ln])
                for hv in halves:
                    side = Point(100, 100).distance(hv.centroid) < Point(100, 100).distance(ln.interpolate(ln.project(hv.centroid)))
                    pieces.append((hv, codes[k][int(side)]))
            cv.put_many(pieces)
    # rozet in het midden
    for k in range(8):
        a = math.radians(k * 45 - 90)
        cv.put(leaf((100, 100), (100 + 20 * math.cos(a), 100 + 20 * math.sin(a)), 10), "p")
    cv.put(circle(100, 100, 5, 24), "y")
    cv.finish(sh)
kp12("vlechtring", "Vlechtring", "Twee ringen van banden die om en om over en onder elkaar door lopen, een eigen vlechtpatroon. Geef elke band een lichte en een donkere kant, dan lijkt de vlecht echt gedraaid.", vlechtring)

def fan_pieces(cx, cy, R, codes, n=7):
    half = Point(cx, cy).buffer(R, 64).intersection(box(cx - R - 1, cy - R - 1, cx + R + 1, cy))
    band = half.difference(Point(cx, cy).buffer(R - 4.5, 64))
    core = Point(cx, cy).buffer(R * .28, 32).intersection(half)
    mid = Point(cx, cy).buffer(R - 4.5, 64).intersection(half).difference(core)
    rays = [(w.intersection(mid), codes[1 + k % 2]) for k, w in enumerate(wedges(cx, cy, 2 * n, a0=180)) if w.intersects(mid)]
    out = [(g, codes[0]) for g in split_lines(band, [LineString([(cx, cy), (cx + 2 * R * math.cos(math.radians(180 + 180 * k / 4)), cy + 2 * R * math.sin(math.radians(180 + 180 * k / 4)))]) for k in range(1, 4)])]
    return out + rays + [(core, codes[3])]

def deco_waaiers(sh):
    cv = Canvas(); R = 25
    for j in range(-1, 18):
        y = 4 + j * R * .5
        for i in range(-1, 6):
            x = i * 2 * R + (R if j % 2 else 0)
            cv.put_many(fan_pieces(x, y + R, R, ["y", "n", "b", "o"] if j % 2 else ["o", "t", "b", "y"]))
    cv.finish(sh)
kp12("art-deco-waaiers", "Art-deco waaiers", "Rijen halfronde waaiers die als schubben over elkaar vallen, in de stijl van de jaren twintig. Kleur de randen goud of geel en wissel binnenin twee rustige kleuren af.", deco_waaiers)

def deco_zon(sh):
    cv = Canvas(); cx, cy = 100, 150
    cv.put_many(pat_rays(PAGE, cx, cy, 36, "yo", a0=-90 - 5))
    frame = PAGE.difference(P([(14, 200), (14, 54), (34, 54), (34, 34), (58, 34), (58, 14), (142, 14), (142, 34), (166, 34), (166, 54), (186, 54), (186, 200)]))
    cv.put_many(pat_stripes(frame, 5, 45, "nb"))
    cv.put_many(pat_rings(Point(cx, cy).buffer(62, 96).intersection(box(0, 0, 200, cy)).difference(Point(cx, cy).buffer(40, 96)), cx, cy, 7, "ory", 40))
    inner = Point(cx, cy).buffer(40, 96).intersection(box(0, 0, 200, cy))
    cv.put_many(pat_rays(inner.difference(Point(cx, cy).buffer(16, 64)), cx, cy, 18, "yo"))
    cv.put(Point(cx, cy).buffer(16, 64).intersection(box(0, 0, 200, cy)), "r")
    sea = box(14, cy, 186, 200)
    pieces = []
    for k in range(10):
        y0 = cy + k * 5
        zig = [(x, y0 + (2.5 if (x // 10) % 2 else 0)) for x in range(0, 201, 10)]
        zig2 = [(x, y0 + 5 + (2.5 if (x // 10) % 2 else 0)) for x in range(200, -1, -10)]
        pieces.append((P(zig + zig2).intersection(sea), "tn"[k % 2]))
    cv.put_many(pieces)
    cv.finish(sh)
kp12("art-deco-zonsopkomst", "Art-deco zonsopkomst", "Een zon die opkomt boven zigzaggende golven, omlijst door een getrapte rand zoals op oude bioscopen. Kleur de stralen om en om licht en donker voor het echte art-decogevoel.", deco_zon, diff=2)

# ================================================================ mandala's
def mandala12(slug, name, desc, rings):
    if ONLY and slug not in ONLY: return
    mandala(slug, name, rings)
    p = os.path.join(OUT, slug + ".json"); m = json.load(open(p))
    m["materials"] = MAT; m["i18n"]["nl"]["description"] = desc
    json.dump(m, open(p, "w"), ensure_ascii=False, indent=1)

mandala12("mandala-lotus", "Mandala: lotus", "Laag op laag lotusblaadjes die om en om verspringen, met een rand van stipjes en puntjes. Kleur van binnen naar buiten van licht naar donker, of juist andersom.",
          [("petal", 40, 66, 16, "pm", 11.25), ("petal", 54, 84, 16, "mk"), ("tri", 84, 97, 48, "p"), ("dot", 77, 85, 32, "y", 5.625),
           ("seg", 32, 40, 32, "yo"), ("petal", 8, 34, 8, "km", 22.5), ("petal", 10, 30, 8, "mr"), ("seg", 0, 9, 1, "y")])
mandala12("mandala-kantwerk", "Mandala: kantwerk", "Fijne ringen van boogjes, druppels en puntjes, als een kanten kleedje. Gebruik maar twee of drie kleuren en laat sommige ringen wit: dat oogt het mooist.",
          [("seg", 92, 98, 72, "tn"), ("tri", 74, 92, 36, "b"), ("dot", 66, 74, 36, "n"), ("petal", 44, 68, 18, "tb"), ("tri", 40, 52, 36, "n", 5),
           ("seg", 34, 40, 36, "bt"), ("dot", 27, 33, 18, "n"), ("petal", 8, 27, 9, "bt"), ("seg", 0, 8, 1, "n")])

def spiraal(sh):
    cv = Canvas()
    cv.put_many(pat_checker(PAGE, 25, 0, "k-"))
    disk = circle(100, 100, 94, 128)
    n, a = 16, 1.35
    def sp(k, sgn):
        return LineString([(100 + r * math.cos(2 * math.pi * k / n + sgn * a * math.log(r)), 100 + r * math.sin(2 * math.pi * k / n + sgn * a * math.log(r))) for r in [10 * 1.02 ** i for i in range(120) if 10 * 1.02 ** i < 100]])
    cuts = [sp(k, 1) for k in range(n)] + [sp(k, -1) for k in range(n)] + [LineString(circle(100, 100, 82, 128).exterior.coords)]
    parts = split_lines(disk, cuts)
    pieces = []
    for g in parts:
        c = g.centroid; r = math.hypot(c.x - 100, c.y - 100); t = math.atan2(c.y - 100, c.x - 100)
        if r > 82: pieces.append((g, "p")); continue
        u = math.floor((t - a * math.log(r)) * n / (2 * math.pi)); v = math.floor((t + a * math.log(r)) * n / (2 * math.pi))
        pieces.append((g, "lbmy"[(u % 2) * 2 + v % 2]))
    cv.put_many(pieces)
    cv.put(circle(100, 100, 14, 48), "y"); cv.put(P(star_pts(100, 100, 11, 5, 6)), "o")
    cv.finish(sh)
kp12("mandala-spiralen", "Mandala: spiralen", "Spiralen die linksom en rechtsom draaien en samen een netwerk van ruitjes vormen, zoals de pitten in een zonnebloem. Kleur één spiraal helemaal en volg hem naar buiten.", spiraal)

# ================================================================ glas-in-lood
def pointed_arch(x0, x1, ys, yb, k=1.5):
    """Spitsboog van x0 tot x1, kantel op hoogte ys, onderkant yb; k = straal / halve breedte."""
    hw = (x1 - x0) / 2; r = hw * k
    a = circle(x1 - r, ys, r, 96).intersection(circle(x0 + r, ys, r, 96)).intersection(box(x0, -100, x1, ys))
    return unary_union([a, box(x0, ys, x1, yb)])

def raam(sh):
    cv = Canvas(); rnd = random.Random(21)
    cv.put_many(pat_bricks(PAGE, 22, 11, "wo"))
    win = pointed_arch(36, 164, 92, 190)
    cv.put_many([(g, "z") for g in split_lines(win.buffer(7, join_style=2).difference(win), [LineString([(100, 100), (100 + 200 * math.cos(math.radians(a)), 100 + 200 * math.sin(math.radians(a)))]) for a in range(0, 360, 15)])])
    cv.put_many(pat_voronoi(win, 11, "bntp", 4))
    for x0, x1 in ((44, 96), (104, 156)):
        lan = pointed_arch(x0, x1, 120, 184, 1.3)
        cells = pat_voronoi(lan, 9, "x", 30 + x0)
        cv.put_many([(g, rnd.choice("rygtbo")) for g, _ in cells])
    cv.put_many([(g, "y") for g in split_lines(circle(100, 64, 30, 96).difference(circle(100, 64, 24, 96)), [LineString([(100, 64), (100 + 40 * math.cos(math.radians(a)), 64 + 40 * math.sin(math.radians(a)))]) for a in range(0, 360, 30)])])
    cv.put(circle(100, 64, 24, 96), "b")
    for k in range(8):
        a = math.radians(k * 45 - 90)
        cv.put(leaf((100 + 5 * math.cos(a), 64 + 5 * math.sin(a)), (100 + 22 * math.cos(a), 64 + 22 * math.sin(a)), 11), "rm"[k % 2])
    cv.put(circle(100, 64, 5.5, 24), "y")
    cv.put(box(24, 190, 176, 200), "z")
    cv.finish(sh)
kp12("glas-in-loodraam", "Glas-in-loodraam", "Een spitsboograam vol glasscherfjes met een roosvenster bovenin, in een bakstenen muur. Kleur de twee boogvensters bont en de rest in rustig blauw, alsof de zon erdoor schijnt.", raam, "wereld")

def vlinder(sh):
    cv = Canvas()
    cv.put_many(pat_hex(PAGE, 12, "lk", .5))
    up = P(bez((102, 92), (120, 40), (170, 10), (188, 36), 20) + bez((188, 36), (198, 60), (170, 96), (102, 102), 20)[1:])
    lo = P(bez((102, 104), (150, 102), (182, 128), (168, 160), 20) + bez((168, 160), (154, 186), (120, 170), (102, 112), 20)[1:])
    for s in (1, -1):
        for w, d, seed in ((up, 9.5, 1), (lo, 8.5, 2)):
            ww = w if s == 1 else affinity.scale(w, -1, 1, origin=(100, 0))
            cv.put(ww, "n")
            inner = ww.buffer(-7, join_style=1)
            band = ww.difference(inner)
            cv.put_many(pat_dots(band, 7.5, 2.1, "-", "n"))
            cells = pat_voronoi(inner, d, "x", seed)
            out = []
            for g, _ in cells:
                dd = Point(100, 100).distance(g.centroid)
                out.append((g, "yor"[min(2, int(dd / 30))] if seed == 1 else "ytn"[min(2, int(dd / 25))]))
            cv.put_many(out)
    cv.put_many(strip_segments([(100, 92), (100, 160)], 9, 6, "wz"))
    cv.put(ellipse(100, 98, 6, 10), "w")
    cv.put(circle(100, 84, 6, 24), "w")
    for s in (1, -1): cv.put(circle(100 + s * 22, 40, 3.2, 16), "x")
    cv.finish(sh)
    for s in (1, -1): sh.line(f"M{100 + s * 3} 79Q{100 + s * 8} 55 {100 + s * 19.5} 42", "l")
kp12("vlinder-als-glas-in-lood", "Vlinder als glas-in-lood", "Een vlinder met vleugels van kleine scherfjes en een stippelrand, op een honingraatachtergrond. Kleur de scherfjes van warm bij het lijf naar koel aan de randen.", vlinder, "dieren")

# ================================================================ landschappen (2)
def zee(sh):
    cv = Canvas()
    sky = box(0, 0, 200, 76)
    cv.put_many(pat_rays(sky, 64, 76, 26, "yk"))
    cv.put(Point(64, 76).buffer(26, 64).intersection(sky), "o")
    cv.put(Point(64, 76).buffer(16, 64).intersection(sky), "r")
    for x, y, s in ((150, 26, 1), (112, 46, .7)):
        cv.put(unary_union([circle(x - 12 * s, y + 3 * s, 7 * s), circle(x, y - 2 * s, 10 * s), circle(x + 12 * s, y + 3 * s, 7 * s), box(x - 19 * s, y + 3 * s, x + 19 * s, y + 10 * s)]), "-")
    rows = [(76, 3, 30, .2, "nb"), (90, 4, 36, 1.3, "bt"), (106, 6, 42, 2.1, "nb"), (126, 8, 52, .7, "bt"), (150, 10, 62, 2.9, "nb"), (178, 12, 74, 1.1, "bt")]
    for k, (y0, A, wl, ph, codes) in enumerate(rows):
        top = [(x, y0 - A * abs(math.sin(x / wl * math.pi + ph)) ** .6) for x in range(-4, 205, 2)]
        band = P(top + [(204, 205), (-4, 205)])
        step = 5 + k * 1.3
        lines = [LineString([(x, y + 3 + A * .35 + m * step) for x, y in top]) for m in range(0, 30) if y0 + m * step < 215]
        parts = split_lines(band.intersection(PAGE), lines)
        parts.sort(key=lambda g: g.centroid.y)
        cv.put_many([(parts[0], codes[1])] + [(g, (codes[0] + "tb"[k % 2])[m % 2]) for m, g in enumerate(parts[1:])])
        # schuimbolletjes op de toppen
        for i in range(-1, int(200 / wl) + 2):
            cx = (i + .5) * wl - ph * wl / math.pi
            if not -5 < cx < 205: continue
            for j, (dx, rr) in enumerate(((-A * .9 - 3, 2.6 + A * .12), (0, 3 + A * .18), (A * .9 + 3, 2.6 + A * .12))):
                cv.put(circle(cx + dx, y0 - A + rr * .5 + abs(dx) * .25, rr, 16), "-")
        if k == 1:
            cv.put(P([(150, 86), (176, 86), (172, 92), (154, 92)]), "w")
            cv.put(P([(162, 84), (162, 58), (176, 82)]), "-"); cv.put(P([(160, 84), (160, 62), (150, 82)]), "r")
    cv.finish(sh)
    for x, y in ((30, 30), (44, 22), (100, 18)): sh.line(f"M{x - 6} {y}Q{x - 3} {y - 4} {x} {y}Q{x + 3} {y - 4} {x + 6} {y}", "l", "stroke-width:1.2")
kp12("zee-met-golven", "Zee met golven", "Rijen golven met schuimkopjes, van de horizon tot vlak bij je voeten, en een zeilbootje bij ondergaande zon. Maak elke rij golven een tint donkerder naar voren toe.", zee, "zee")

def lappendeken(sh):
    cv = Canvas(); rnd = random.Random(8)
    sky = box(0, 0, 200, 90)
    cv.put_many(pat_stripes(sky, 12, 0, "b-"))
    cv.put(circle(160, 30, 15, 48), "y")
    for k in range(12):
        a = math.radians(k * 30)
        cv.put(P([(160 + 18 * math.cos(a - .12), 30 + 18 * math.sin(a - .12)), (160 + 26 * math.cos(a), 30 + 26 * math.sin(a)), (160 + 18 * math.cos(a + .12), 30 + 18 * math.sin(a + .12))]), "o")
    cv.put(unary_union([circle(48, 30, 9), circle(62, 24, 12), circle(76, 31, 9), box(40, 30, 84, 40)]), "-")
    hills = [(70, 14, 90, 1.0), (96, 16, 110, 2.4), (126, 18, 130, .3), (158, 16, 120, 1.7)]
    fills = [lambda g: pat_stripes(g, 4, rnd.choice((20, -20, 70, -70, 0)), rnd.choice(("ly", "gl", "yo", "lg"))),
             lambda g: pat_dots(g, 9, 2.8, "g", "l"),
             lambda g: pat_checker(g, 8, rnd.choice((30, -30)), rnd.choice(("gl", "yl"))),
             lambda g: [(g, rnd.choice("lgyo"))],
             lambda g: pat_waves(g, 5, 1.2, 18, rnd.choice(("gl", "ly")), rnd.choice((10, -15)))]
    for i, (y0, A, wl, ph) in enumerate(hills):
        top = [(x, y0 - A * math.sin(x / wl * math.pi + ph)) for x in range(-4, 205, 3)]
        hill = P(top + [(204, 205), (-4, 205)]).intersection(PAGE)
        cuts = []
        for k in range(5):
            x = 20 + k * 40 + rnd.uniform(-14, 14)
            cuts.append(LineString(bez((x, 0), (x + rnd.uniform(-20, 20), 70), (x + rnd.uniform(-20, 20), 140), (x + rnd.uniform(-30, 30), 205), 16)))
        cuts.append(LineString([(x, y + 14 + i * 2) for x, y in top]))
        for j, g in enumerate(split_lines(hill, cuts)):
            cv.put_many(fills[(i * 3 + j * 2 + rnd.randint(0, 1)) % len(fills)](g))
    for x, y, r in ((30, 82, 7), (44, 86, 5), (120, 104, 8), (178, 132, 9), (64, 150, 10), (16, 176, 8)):
        cv.put(box(x - 1.6, y, x + 1.6, y + r * 1.4), "w"); cv.put(circle(x, y - r * .3, r, 32), "g")
    cv.put(box(90, 70, 112, 86), "-"); cv.put(P([(87, 71), (101, 60), (115, 71)]), "r"); cv.put(box(98, 76, 104, 86), "w")
    cv.put(box(114, 74, 132, 86), "r"); cv.put(P([(112, 75), (123, 66), (134, 75)]), "z")
    cv.finish(sh)
kp12("lappendeken-landschap", "Lappendeken van velden", "Glooiende heuvels die verdeeld zijn in akkers, boomgaarden en weilanden, elk met een eigen patroon. Kleur elk veld in een andere tint groen, geel of oker.", lappendeken, "natuur")

def bloem5(cv, cx, cy, r, codes, rot=0):
    for k in range(5):
        a = math.radians(rot + k * 72 - 90)
        pet = leaf((cx + r * .15 * math.cos(a), cy + r * .15 * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a)), r * .75, 0, 16)
        cv.put_many([(g, codes[j % 2]) for j, g in enumerate(split_lines(pet, [LineString([(cx, cy), (cx + r * 1.2 * math.cos(a), cy + r * 1.2 * math.sin(a))])]))])
    cv.put(circle(cx, cy, r * .3, 24), codes[2])

def krans(sh):
    cv = Canvas()
    cv.put_many(pat_dots(PAGE.difference(circle(100, 100, 94.5, 128)), 9, 2.6, "k", "-"))
    cv.put_many(pat_rings(circle(100, 100, 94.5, 128), 100, 100, 10.5, "-b"))
    cv.put(circle(100, 100, 32, 96), "y")
    ring = [(100 + 64 * math.cos(math.radians(a)), 100 + 64 * math.sin(math.radians(a))) for a in range(0, 361, 4)]
    cv.put_many(strip_segments(ring, 5, 12, "w"))
    for k in range(18):
        a = k * 20 + 6
        base = (100 + 64 * math.cos(math.radians(a)), 100 + 64 * math.sin(math.radians(a)))
        side = 1 if k % 2 else -1
        ang = math.radians(a + 90 + side * 40)
        out = 64 + side * 4
        b2 = (100 + out * math.cos(math.radians(a)), 100 + out * math.sin(math.radians(a)))
        tip = (b2[0] + 30 * math.cos(ang) * 1, b2[1] + 30 * math.sin(ang))
        tip = (100 + (64 + side * 26) * math.cos(math.radians(a + 12)), 100 + (64 + side * 26) * math.sin(math.radians(a + 12)))
        cv.put_many(veined_leaf(base, tip, 13, 2, "gl", .05 * side))
    for k in range(6):
        a = math.radians(k * 60 + 30)
        cx, cy = 100 + 64 * math.cos(a), 100 + 64 * math.sin(a)
        bloem5(cv, cx, cy, 15, "mkr" if k % 2 else "oyr", k * 17)
        if k % 2 == 0:
            for j in range(3):
                b = math.radians(k * 60 + 52 + j * 6)
                bx, by = 100 + (76 + j % 2 * 7) * math.cos(b), 100 + (76 + j % 2 * 7) * math.sin(b)
                cv.put(circle(bx, by, 4.8, 20), "p")
    for k in range(8):
        a = math.radians(k * 45 - 90)
        cv.put(leaf((100 + 6 * math.cos(a), 100 + 6 * math.sin(a)), (100 + 26 * math.cos(a), 100 + 26 * math.sin(a)), 12), "tb"[k % 2])
    cv.put(circle(100, 100, 7, 24), "y")
    cv.finish(sh)
kp12("bloemenkrans", "Bloemenkrans", "Een krans van takjes, blaadjes, bloemen en bessen rond een zonnig hart. Kies twee bloemkleuren en wissel ze af, en geef de blaadjes een lichte en een donkere helft.", krans, "natuur")
