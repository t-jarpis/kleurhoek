"""Batch 47: Sinterklaas-knutsels (A4): een schoen om echt te zetten, de pakjesboot en een schoorsteendoosje als
bouwplaat, vingerpoppetjes, een verlanglijstje en een slinger.

Piet is altijd Roetveegpiet (baret met veer, kraag, alleen roetvegen). Geen bekende figuren of merken.

De schoen is een band met twee zijkanten: het zijprofiel wordt uitgerekend als lijn, de band is precies zo lang als
de omtrek van dat profiel (zonder de opening) en is in drie stroken verdeeld. Het script controleert dat de stroken
samen even lang zijn als de rand van de zijkant, dat de knik bij de hak op de goede plek zit en dat de neus niet
scherper buigt dan de tandjes aankunnen.

De pakjesboot en het schoorsteendoosje gebruiken de uitslag uit polyhedra (zelfde aanpak als batch37v; de helpers zijn
hieronder overgenomen omdat batch37v bij import schrijft).

Gebruik: OUT=/tmp/sint3 python3 batch47_sint.py [slug ...]
"""
import math, random, re, sys
from lib_gen import *
import polyhedra as ph
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely.ops import unary_union
from shapes import star_path
from batch5_kit import eye, smile
from batch44_sint import mitre, staff, beret, soot, sint, pepernoot

ONLY = set(sys.argv[1:])
MAT = [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}, {"slug": "stevig-papier", "optional": True}]


def P(points): return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in points) + "Z"
def PL(points): return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in points)
def gpath(g):
    """Shapely-vlak (of het grootste deel ervan) als pad."""
    if g.geom_type != "Polygon": g = max(g.geoms, key=lambda q: q.area)
    return P(list(g.exterior.coords)[:-1])
def cubic(p0, p1, p2, p3, n=40):
    out = []
    for k in range(n + 1):
        t = k / n; u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out
def inner_region(sh, g, code, outer):
    """Vlak zonder eigen rand; alleen de randen binnen `outer` krijgen een lijn (de buitenrand blijft een kniplijn)."""
    sh.raw(f'<path class="r" style="stroke:none" d="{gpath(g)}"/>', code)
    edge = g.boundary.difference(outer.exterior.buffer(.25))
    for ln in getattr(edge, "geoms", [edge]):
        if ln.length > .5: sh.line(PL(list(ln.coords)), "l", "stroke-width:1.2")
def cut_around(sh, geoms, d=2.5):
    """Kniplijn rond een of meer vormen, d naar buiten."""
    g = unary_union(geoms).buffer(d, join_style=1)
    sh.line(gpath(g), "cut")
    return g
def gift_box(sh, x, y, w, h, code, ribbon="y", dots=None):
    """Pakje met strik, (x, y) = linksboven van de doos; schaalt mee met w."""
    s = w / 24
    sh.rect_r(x, y, w, h, code, s)
    sh.rect_r(x - s * 1.5, y - s * 5, w + s * 3, s * 6, code, s)
    sh.rect_r(x + w / 2 - s * 2.5, y - s * 5, s * 5, h + s * 5, ribbon)
    for d in (-1, 1):
        sh.region(f"M{f(x + w / 2)} {f(y - s * 5)}C{f(x + w / 2 + d * s * 10)} {f(y - s * 15)} {f(x + w / 2 + d * s * 12)} {f(y - s * 3)} {f(x + w / 2)} {f(y - s * 5)}Z", ribbon)
    if dots:
        for dx, dy in ((.2, .35), (.8, .35), (.22, .78), (.78, .78)):
            sh.circle_r(x + w * dx, y + h * dy, s * 2, dots)


# ======================================================================================
# 1. Schoen om te zetten (band + twee zijkanten, twee vellen)
# ======================================================================================
# Zijprofiel in mm-achtige eenheden (1 eenheid = 1,05 mm op A4), x naar voren (neus), y omhoog.
OF, T1, T2, T3, H0, HT = (64, 78), (128, 46), (166, 20), (144, 0), (0, 0), (0, 82)
W = 62             # breedte van de schoen = breedte van de band
TOOTH = (8.5, 4.5, 6.5, 10)  # basis, top, diepte, steek van de tandjes
FLAP = 9           # overlap (lijmstuk) aan het begin van strook 2 en 3
SOLE_Y, HEEL_X, HEEL_Y, CAP_X = 7, 24, 14, 118
J1_X, J2_X = 126, 22  # naden van de band op de zool


def shoe_band_line():
    """Rand van het profiel waar de band op komt: van de opening voor, over wreef, neus en zool, de hak omhoog."""
    pts = cubic(OF, (88, 76), (110, 60), T1) + cubic(T1, (140.6, 36.2), (166, 42), T2)[1:] + cubic(T2, (166, 8), (156, 0), T3)[1:]
    pts += [(x, 0) for x in range(140, -1, -4)] + [(0, y) for y in range(4, HT[1], 4)] + [HT]
    return pts


def arclen(pts):
    s = [0.0]
    for a, b in zip(pts, pts[1:]): s.append(s[-1] + math.dist(a, b))
    return s


def shoe_geometry():
    pts = shoe_band_line(); s = arclen(pts)
    S = s[-1]
    # kleinste kromtestraal (alleen op de bochten): de tandjes moeten er nog omheen passen
    rmin = 1e9
    for i in range(2, len(pts) - 2):
        a, b, c = pts[i - 2], pts[i], pts[i + 2]
        ab, bc, ca = math.dist(a, b), math.dist(b, c), math.dist(c, a)
        cr = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        if cr > 1e-6 and b[1] > 0.5 and b[0] > 0.5: rmin = min(rmin, ab * bc * ca / (2 * cr))
    assert rmin > TOOTH[2] * 1.8, f"neus te scherp: straal {rmin:.1f}"

    def s_at(pred, start=0):
        for i in range(start, len(pts)):
            if pred(pts[i]): return s[i], i
        raise AssertionError("punt niet gevonden")
    s_t3, i_t3 = s_at(lambda p: p == T3)
    s_cap, _ = s_at(lambda p: p[0] >= CAP_X)
    s_sole, _ = s_at(lambda p: p[1] <= SOLE_Y and p[0] > 100)
    s_j1 = s_t3 + (T3[0] - J1_X); s_j2 = s_t3 + (T3[0] - J2_X); s_corner = s_t3 + T3[0]
    assert abs(S - (s_corner + HT[1])) < 1e-6
    # controle: lengte van de band = rand van de zijkant (polygoon zonder de bovenrand van de opening)
    side = Polygon(pts)  # sluit vanzelf met de opening HT -> OF
    assert abs(side.length - math.dist(HT, OF) - S) < 1e-6
    return dict(pts=pts, S=S, rmin=rmin, s_cap=s_cap, s_sole=s_sole, s_j1=s_j1, s_j2=s_j2, s_corner=s_corner)


def shoe_side(sh, x0, base, mirror):
    """Zijkant van de schoen (bedrukt aan de buitenkant). mirror: neus naar links."""
    g = shoe_geometry()
    X = (lambda x: x0 + 166 - x) if mirror else (lambda x: x0 + x)
    Y = lambda y: base - y
    T = lambda p: (X(p[0]), Y(p[1]))
    prof = Polygon([T(p) for p in g["pts"]])
    sh.raw(f'<path class="r" style="stroke:none" d="{gpath(prof)}"/>', "r")
    sh.raw('<g style="--sw:1.2">')
    sole = prof.intersection(unary_union([Polygon([T((-5, -5)), T((200, -5)), T((200, SOLE_Y)), T((-5, SOLE_Y))]),
                                           Polygon([T((-5, -5)), T((HEEL_X, -5)), T((HEEL_X, HEEL_Y)), T((-5, HEEL_Y))])]))
    cap = prof.intersection(Polygon([T((CAP_X, SOLE_Y)), T((200, SOLE_Y)), T((200, 100)), T((CAP_X + 14, 100))])).difference(sole)
    inner_region(sh, cap, "y", prof)
    inner_region(sh, sole, "w", prof)
    # naad van het hielstuk en stiksel langs de neus
    seam = [T(p) for p in cubic((8, 80), (30, 60), (40, 30), (52, SOLE_Y))]
    sh.line(PL(seam), "l", "stroke-width:.9")
    # gouden ster en twee pepernoten als versiering
    cx, cy = T((86, 40))
    sh.region(star_path(cx, cy, 13, 5.5), "y")
    for (px, py) in ((60, 22), (104, 20)):
        a, b = T((px, py)); sh.circle_r(a, b, 5, "w")
    sh.raw('</g>')
    sh.line(gpath(prof), "cut")
    # naden van de band: streepje en letter
    for xx, lab in ((J1_X, "A"), (J2_X, "B")):
        sh.seg(X(xx), Y(0), X(xx), Y(4.5), "l", "stroke-width:.9")
        sh.text(X(xx) + 3.6, Y(1.3), lab, 5, weight="800")
    return prof


def shoe_strip(sh, x0, y0, L, flap, regions, folds_at=(), label=None, end_label=None, start_label=None, deco=None):
    """Strook van de band: lengte L (zonder overlap), breedte W, tandjes boven en onder. regions = [(s0, s1, code)]."""
    xb = x0 + flap  # s = 0
    top, bot = y0, y0 + W
    for s0, s1, code in regions:
        sh.raw(f'<path class="r" style="stroke:none" d="{P([(xb + s0, top), (xb + s1, top), (xb + s1, bot), (xb + s0, bot)])}"/>', code)
    sh.raw('<g style="--sw:1.2">')
    for s0, s1, code in regions[1:]: sh.seg(xb + s0, top, xb + s0, bot, "l", "stroke-width:1.2")
    if deco: deco(xb, top)
    sh.raw('</g>')
    # tandjes per stuk tussen knikken
    b, t, d, pitch = TOOTH
    cuts = []
    breaks = [0] + list(folds_at) + [L]
    teeth = []
    for a, z in zip(breaks, breaks[1:]):
        a1, z1 = a + 1.2, z - 1.2
        n = int((z1 - a1 + (pitch - b)) // pitch)
        if n <= 0: continue
        span = n * pitch - (pitch - b); st = a1 + (z1 - a1 - span) / 2
        teeth += [st + k * pitch for k in range(n)]
    for edge, dirn in ((top, -1), (bot, 1)):
        prev = xb - (flap if flap else 0)
        for st in teeth:
            xa = xb + st
            poly = [(xa, edge), (xa + (b - t) / 2, edge + dirn * d), (xa + (b + t) / 2, edge + dirn * d), (xa + b, edge)]
            sh.raw(f'<path class="glue" d="{P(poly)}"/>')
            sh.line(PL(poly), "cut")
            sh.seg(xa, edge, xa + b, edge, "fold")
            cuts.append((prev, edge, xa, edge)); prev = xa + b
        cuts.append((prev, edge, xb + L, edge))
    for x1, y1, x2, y2 in cuts:
        if x2 - x1 > .05: sh.seg(x1, y1, x2, y2, "cut")
    if flap:
        sh.raw(f'<rect class="glue" x="{f(x0)}" y="{f(top)}" width="{f(flap)}" height="{f(W)}"/>')
        sh.seg(x0, top, x0, bot, "cut")
        sh.text(x0 + flap / 2, top + W / 2 + 2, start_label, 6, weight="800")
    else:
        sh.seg(xb, top, xb, bot, "cut")
    sh.seg(xb + L, top, xb + L, bot, "cut")
    for fs in folds_at: sh.seg(xb + fs, top, xb + fs, bot, "fold")
    if label: sh.text(xb + 5, top + 6.5, label, 6, weight="800")
    if end_label: sh.text(xb + L - 4, top + W / 2 + 2, end_label, 5, weight="800", cls="tip")
    return teeth


def schoen():
    g = shoe_geometry()
    S, sj1, sj2, sc = g["S"], g["s_j1"], g["s_j2"], g["s_corner"]
    L1, L2, L3 = sj1, sj2 - sj1, S - sj2
    assert abs(L1 + L2 + L3 - S) < 1e-9 and max(L1, L2, L3) + FLAP <= 184, (L1, L2, L3)
    # --- vel 1: twee zijkanten, kaartje en wortel ---
    sh = Sheet(); title(sh, "Schoen om te zetten", 16); sh.text(100, 27, "Een echte schoen voor een wortel en een tekening.", 6.5)
    x0 = (200 - 166) / 2
    p1 = shoe_side(sh, x0, 34 + 82 + 2, mirror=False)
    p2 = shoe_side(sh, x0, 34 + 82 + 2 + 90, mirror=True)
    assert not p1.intersects(p2)
    # kaartje voor Sinterklaas (past door de opening)
    cx, cy, cw, chh = 20, 218, 66, 46
    sh.raw(f'<rect class="r" style="stroke:none" x="{cx}" y="{cy}" width="{cw}" height="{chh}" rx="3"/>', "-")
    sh.rect_line(cx, cy, cw, chh, "cut", 3)
    sh.text(cx + cw / 2, cy + 8.5, "Voor Sinterklaas", 5.5, weight="800")
    sh.rect_line(cx + 6, cy + 12, cw - 12, chh - 17, "guide", 2)
    sh.raw('<g style="--sw:1.2">')
    for x in (cx + 6, cx + cw - 6): sh.region(star_path(x, cy + 6.5, 3.6, 1.5), "y")
    sh.raw('</g>')
    # wortel voor het paard
    sh.raw('<g style="--sw:1.4">')
    wx, wy = 142, 240
    body = cubic((wx - 20, wy - 6), (wx + 8, wy - 12), (wx + 34, wy - 6), (wx + 50, wy + 2), 24) + cubic((wx + 50, wy + 2), (wx + 34, wy + 8), (wx + 8, wy + 12), (wx - 20, wy + 6), 24)[1:]
    leaves = [cubic((wx - 21, wy - 2), (wx - 30, wy - 14), (wx - 38, wy - 16), (wx - 40, wy - 12), 16) + cubic((wx - 40, wy - 12), (wx - 34, wy - 8), (wx - 28, wy - 4), (wx - 21, wy - 2), 16)[1:],
              cubic((wx - 21, wy), (wx - 34, wy - 2), (wx - 42, wy + 2), (wx - 42, wy + 6), 16) + cubic((wx - 42, wy + 6), (wx - 34, wy + 6), (wx - 28, wy + 4), (wx - 21, wy), 16)[1:],
              cubic((wx - 21, wy + 2), (wx - 30, wy + 12), (wx - 36, wy + 18), (wx - 34, wy + 21), 16) + cubic((wx - 34, wy + 21), (wx - 28, wy + 16), (wx - 24, wy + 10), (wx - 21, wy + 2), 16)[1:]]
    for lf in leaves: sh.poly_r(lf, "g")
    sh.poly_r(body, "o")
    sh.line(f"M{wx - 6} {wy - 5}l3 4M{wx + 12} {wy - 6}l2 4M{wx + 28} {wy + 5}l3 -3M{wx + 4} {wy + 7}l2 -3", "l", "stroke-width:.8")
    sh.raw('</g>')
    cut_around(sh, [Polygon(body)] + [Polygon(lf).buffer(.8) for lf in leaves], 3)
    sh.legend(["cut", "fold", "glue"], 274)

    # --- vel 2: de band in drie stroken ---
    pg = Sheet(); title(pg, "Schoen om te zetten", 16)
    sole_start = g["s_sole"]
    def laces(xb, top):
        # wreef met veters: zes oogjes in twee rijen, gekruiste veters en een strik
        ys = (top + W / 2 - 13, top + W / 2 + 13)
        xs = [xb + 16 + k * 11 for k in range(4)]
        pg.region(f"M{f(xb + 8)} {f(top + 9)}H{f(xb + 54)}Q{f(xb + 62)} {f(top + W / 2)} {f(xb + 54)} {f(top + W - 9)}H{f(xb + 8)}Z", "b")
        d = ""
        for k in range(3):
            d += f"M{f(xs[k])} {f(ys[0])}L{f(xs[k + 1])} {f(ys[1])}M{f(xs[k])} {f(ys[1])}L{f(xs[k + 1])} {f(ys[0])}"
        d += f"M{f(xs[0])} {f(ys[0])}L{f(xb + 6)} {f(top + W / 2)}M{f(xs[0])} {f(ys[1])}L{f(xb + 6)} {f(top + W / 2)}"
        pg.line(d, "l", "stroke-width:1")
        for x in xs:
            for y in ys: pg.circle_r(x, y, 2.2, "y")
        for dy in (-1, 1):
            pg.region(f"M{f(xb + 6)} {f(top + W / 2)}C{f(xb + 2)} {f(top + W / 2 + dy * 12)} {f(xb + 14)} {f(top + W / 2 + dy * 13)} {f(xb + 6)} {f(top + W / 2)}Z", "-")
        pg.circle_r(xb + 6, top + W / 2, 2, "-")
    def tread(xb, top, s0, s1):
        d = "".join(f"M{f(xb + s)} {f(top + 6)}V{f(top + W - 6)}" for s in range(int(s0) + 6, int(s1) - 2, 8))
        pg.line(d, "l", "stroke-width:.6")
    y1, y2, y3 = 36, 36 + W + 16, 36 + 2 * (W + 16)
    xs1 = (200 - L1) / 2
    shoe_strip(pg, xs1, y1, L1, 0, [(0, g["s_cap"], "r"), (g["s_cap"], sole_start, "y"), (sole_start, L1, "w")],
               label="1", end_label="A", deco=lambda xb, top: (laces(xb, top), tread(xb, top, sole_start + 4, L1)))
    xs2 = (200 - L2 - FLAP) / 2
    shoe_strip(pg, xs2, y2, L2, FLAP, [(0, L2, "w")], label="2", end_label="B", start_label="A",
               deco=lambda xb, top: tread(xb, top, 0, L2))
    xs3 = (200 - L3 - FLAP) / 2
    corner = sc - sj2
    shoe_strip(pg, xs3, y3, L3, FLAP, [(0, corner + HEEL_Y, "w"), (corner + HEEL_Y, L3, "r")], folds_at=(corner,), label="3", start_label="B",
               deco=lambda xb, top: tread(xb, top, 0, corner))
    pg.legend(["cut", "fold", "glue"], 274)
    write(OUT, "schoen-om-te-zetten", sh, {"category": "feest", "age": "6-9", "kind": "bouwplaat", "difficulty": 3, "minutes": 45, "paperGsm": 160,
        "adultHelp": True, "holiday": "sinterklaas", "materials": MAT,
        "i18n": {"nl": {"name": "Schoen om te zetten", "printNote": "Print beide vellen op ware grootte, het liefst op stevig papier (160 gram): dan blijft de schoen goed staan.",
            "steps": [
                "Kleur de twee zijkanten, de drie stroken van de band, het kaartje en de wortel. De stroken zijn de bovenkant, de neus, de zool en de hak.",
                "Knip alles uit langs de streepjeslijnen. Knip ook tussen de grijze tandjes door, tot aan de stippellijn.",
                "Vouw alle tandjes naar achteren langs de stippellijn, weg van de tekening. Vouw strook 3 ook op de stippellijn dwars over de strook: dat wordt de hoek bij de hak.",
                "Maak één lange band: plak het grijze stuk A van strook 2 onder het einde A van strook 1, en het grijze stuk B van strook 3 onder het einde B van strook 2.",
                "Leg het begin van strook 1, met de veters, bij de opening voorop. Plak de tandjes één voor één aan de binnenkant van een zijkant. De naden komen bij de streepjes A en B op de zool; bij de neus buig je de band rustig mee.",
                "Plak de tweede zijkant op dezelfde manier aan de andere kant van de band. Druk de tandjes van binnenuit aan, door de opening.",
                "Laat de lijm goed drogen. Zet je schoen bij de deur of de kachel, met een wortel voor het paard en een tekening op het kaartje voor Sinterklaas."],
            "pageTitles": ["De band in drie stroken"]}}}, pages=[("extra", "De band in drie stroken", pg)])
    return g


# ======================================================================================
# helpers voor uitslagen (overgenomen uit batch37v)
# ======================================================================================
def cross(u, v): return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
def unit(v): n = ph.norm(v); return tuple(x / n for x in v)
def rotk(p, k):
    if isinstance(k, float): c, si = math.cos(k), math.sin(k); return (c * p[0] - si * p[1], si * p[0] + c * p[1])
    for _ in range(k % 4): p = (-p[1], p[0])
    return p
def front_down(verts, faces, polys, upright):
    fi = max(range(len(faces)), key=lambda i: ph.dot(unit(cross(ph.sub(verts[faces[i][1]], verts[faces[i][0]]), ph.sub(verts[faces[i][2]], verts[faces[i][0]]))), upright))
    fc = faces[fi]; zmin = min(verts[u][2] for u in fc); lo = [k for k, v in enumerate(fc) if verts[v][2] < zmin + 1e-9]
    q = polys[fi]; bot = tuple(sum(q[k][j] for k in lo) / len(lo) for j in (0, 1)); cen = tuple(sum(p[j] for p in q) / len(q) for j in (0, 1))
    return (bot[0] - cen[0], bot[1] - cen[1])
def best_layout(verts, faces, box, depth, tries, upright=None, penalty=.86):
    bw, bh = box[2], box[3]; best = None; rng = random.Random(7)
    cands = [dict(root=r) for r in range(len(faces))] + [dict(root=rng.randrange(len(faces)), dfs=k % 2 == 0, rng=random.Random(rng.random())) for k in range(tries)]
    for args in cands:
        try: lay = ph.layout(verts, faces, depth=depth, **args)
        except AssertionError: continue
        polys, tabs = lay[0], lay[1]
        allp = [p for poly in polys + tabs for p in poly]
        w = max(x for x, _ in allp) - min(x for x, _ in allp); h = max(y for _, y in allp) - min(y for _, y in allp)
        dv = front_down(verts, faces, polys, upright) if upright else None
        opts = list(range(4))
        if dv: opts.append(-math.pi / 2 - math.atan2(dv[1], dv[0]))
        for k in opts:
            if isinstance(k, float):
                rp = [rotk(p, k) for p in allp]
                ww = max(x for x, _ in rp) - min(x for x, _ in rp); hh = max(y for _, y in rp) - min(y for _, y in rp)
            else: ww, hh = (h, w) if k % 2 else (w, h)
            sc = min(bw / ww, bh / hh); score = sc
            if dv:
                d = rotk(dv, k)
                if not (d[1] < -abs(d[0]) * 9): score *= penalty
                elif isinstance(k, float) and abs(k % (math.pi / 2)) > .02 and abs(k % (math.pi / 2) - math.pi / 2) > .02: score *= .97
            if best is None or score > best[0] + 1e-9: best = (score, sc, lay, k)
    assert best, "geen uitslag"
    return best[1:]
class Face: pass
def build_net(sh, verts, faces, codes, box, draw_face, depth=.17, tries=150, style="--sw:1.2", upright=None, pre=None):
    sc, (polys, tabs, folds, cuts), kk = pre or best_layout(verts, faces, box, depth, tries, upright)
    R = lambda p: rotk(p, kk)
    allp = [R(p) for poly in polys + tabs for p in poly]
    mnx, mxx = min(x for x, _ in allp), max(x for x, _ in allp); mny, mxy = min(y for _, y in allp), max(y for _, y in allp)
    bx, by, bw, bh = box
    ox = bx + (bw - (mxx - mnx) * sc) / 2; oy = by + (bh - (mxy - mny) * sc) / 2
    T = lambda p: (ox + (R(p)[0] - mnx) * sc, oy + (mxy - R(p)[1]) * sc)
    spolys = [[T(p) for p in poly] for poly in polys]
    for poly, code in zip(spolys, codes):
        sh.raw(f'<path class="r" style="stroke:none" d="{P(poly)}"/>', code)
    for fi, (fc, sp) in enumerate(zip(faces, spolys)):
        V = [verts[v] for v in fc]
        n = unit(cross(ph.sub(V[1], V[0]), ph.sub(V[2], V[0])))
        cen = tuple(sum(v[k] for v in verts) / len(verts) for k in range(3))
        fcen = tuple(sum(v[k] for v in V) / len(V) for k in range(3))
        if ph.dot(n, ph.sub(fcen, cen)) < 0: raise AssertionError(f"vlak {fi} niet buitenwaarts")
        area = sum(sp[i][0] * sp[(i + 1) % len(sp)][1] - sp[(i + 1) % len(sp)][0] * sp[i][1] for i in range(len(sp)))
        assert area < 0, "uitslag gespiegeld"
        if abs(n[2]) > .95: up = (0, 1, 0)
        else: up = unit(ph.sub((0, 0, 1), ph.scale(n, n[2])))
        right = cross(up, n)
        e1, e2 = ph.sub(V[1], V[0]), ph.sub(V[2], V[0]); s1, s2 = (sp[1][0] - sp[0][0], sp[1][1] - sp[0][1]), (sp[2][0] - sp[0][0], sp[2][1] - sp[0][1])
        g11, g12, g22 = ph.dot(e1, e1), ph.dot(e1, e2), ph.dot(e2, e2); det = g11 * g22 - g12 * g12
        def M(v):
            b1, b2 = ph.dot(v, e1), ph.dot(v, e2); a = (b1 * g22 - b2 * g12) / det; b = (g11 * b2 - g12 * b1) / det
            return (a * s1[0] + b * s2[0], a * s1[1] + b * s2[1])
        Rv, Uv = M(right), M(up)
        assert Rv[0] * Uv[1] - Rv[1] * Uv[0] < 0, "tekening gespiegeld"
        lr = [ph.dot(ph.sub(v, fcen), right) for v in V]; lu = [ph.dot(ph.sub(v, fcen), up) for v in V]
        cr, cu = (max(lr) + min(lr)) / 2, (max(lu) + min(lu)) / 2
        c3 = tuple(fcen[k] + right[k] * cr + up[k] * cu for k in range(3))
        cs = M(ph.sub(c3, V[0])); cs = (sp[0][0] + cs[0], sp[0][1] + cs[1])
        F = Face(); F.n = n; F.c3 = c3; F.idx = fi; F.sc = sc
        F.w = (max(lr) - min(lr)) * sc; F.h = (max(lu) - min(lu)) * sc
        F.poly = [((a - cr) * sc, -(b - cu) * sc) for a, b in zip(lr, lu)]
        F.z = fcen[2]
        ru = (Rv[0] / sc, Rv[1] / sc); du = (-Uv[0] / sc, -Uv[1] / sc)
        sh.raw(f'<g transform="matrix({f(ru[0])} {f(ru[1])} {f(du[0])} {f(du[1])} {f(cs[0])} {f(cs[1])})" style="{style}">')
        draw_face(sh, F)
        sh.raw('</g>')
    for tp in tabs:
        d = "M" + " L".join(f"{f(T(p)[0])} {f(T(p)[1])}" for p in tp)
        sh.raw(f'<path class="glue" d="{d}Z"/>'); sh.line(d, "cut")
    for a, b in folds: sh.seg(*T(a), *T(b), "fold")
    for a, b in cuts: sh.seg(*T(a), *T(b), "cut")
    allt = [T(p) for poly in polys + tabs for p in poly]
    return sc, (min(x for x, _ in allt), min(y for _, y in allt), max(x for x, _ in allt), max(y for _, y in allt))
def side(F, tol=.3):
    x, y, z = F.n
    if z > .95: return "top"
    if z < -.95: return "bottom"
    h = "front" if abs(y) >= abs(x) and y < 0 else "back" if abs(y) >= abs(x) else "left" if x < 0 else "right"
    return h if abs(z) < tol else ("roof_" + h if z > 0 else "low_" + h)
def clip(poly, x0, y0, x1, y1):
    g = Polygon(poly).intersection(sbox(x0, y0, x1, y1))
    if g.is_empty or g.area < 1e-3: return None
    if g.geom_type != "Polygon": g = max(g.geoms, key=lambda q: q.area)
    return list(g.exterior.coords)[:-1]
def band(sh, F, y0, y1, code, x0=-1e3, x1=1e3):
    c = clip(F.poly, x0, y0, x1, y1)
    if c: sh.poly_r(c, code)
def bricks(sh, F, rows, y0=None, y1=None, sw=.45):
    """Voegen: horizontale lijnen plus verspringende stootvoegen."""
    y0 = -F.h / 2 if y0 is None else y0; y1 = F.h / 2 if y1 is None else y1
    step = (y1 - y0) / rows; d = ""
    xs_all = [p[0] for p in F.poly]; xa, xz = min(xs_all), max(xs_all)
    for k in range(rows):
        ya, yb = y0 + k * step, y0 + (k + 1) * step
        if k: d += f"M{f(xa + .6)} {f(ya)}H{f(xz - .6)}"
        x = xa + (step * 1.1 if k % 2 else step * 2.2)
        while x < xz - step * .6:
            d += f"M{f(x)} {f(ya + .4)}V{f(yb - .4)}"; x += step * 2.2
    sh.line(d, "l", f"stroke-width:{sw}")
def box_model(w, d, h):
    return ph.hull_faces([(x, y, z) for x in (0, w) for y in (0, d) for z in (0, h)])
def profile_y(prof, d):
    return ph.hull_faces([(x, y, z) for x, z in prof for y in (0, d)])
def prof_map(F, prof):
    xs = [p[0] for p in prof]; zs = [p[1] for p in prof]
    cx, cz = (min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2; k = 1 if F.n[1] < 0 else -1
    return (lambda mx: k * (mx - cx) * F.sc), (lambda mz: -(mz - cz) * F.sc), k
class Part:
    def __init__(self, model, codes, draw, box, upright=(0, -1, 0), label=None, depth=.17, tries=150):
        self.model, self.codes, self.draw, self.box, self.upright, self.label, self.depth, self.tries = model, codes, draw, box, upright, label, depth, tries
def face_codes(model, codes_fn):
    verts, faces = model; tmp = Face(); out = []
    for fc in faces:
        V = [verts[v] for v in fc]; tmp.n = unit(cross(ph.sub(V[1], V[0]), ph.sub(V[2], V[0]))); tmp.z = sum(v[2] for v in V) / len(V)
        tmp.c3 = tuple(sum(v[k] for v in V) / len(V) for k in range(3))
        out.append(codes_fn(tmp))
    return out
def nets(sh, parts):
    """Uitslagen van een of meer delen op dezelfde schaal. Geeft schaal en kaders terug."""
    pres = [best_layout(*p.model, p.box, p.depth, p.tries, p.upright) for p in parts]
    s = min(pr[0] for pr in pres); pres = [(s,) + tuple(pr[1:]) for pr in pres]
    out = []
    for p, pr in zip(parts, pres):
        out.append(build_net(sh, *p.model, face_codes(p.model, p.codes), p.box, p.draw, p.depth, p.tries, upright=p.upright, pre=pr)[1])
    return s, out


# ======================================================================================
# 2. Pakjesboot (romp, hut en schoorsteen)
# ======================================================================================
HULL = [(0, .55), (.4, 0), (5.0, 0), (6.4, 1.5), (0, 1.5)]
HULL_D = 2.2
CABIN = (2.6, 1.4, 1.35)
FUNNEL = (.8, .8, 1.25)


def romp(sh, F):
    x, y, z = F.n; s = F.sc
    if abs(y) > .9:
        X, Y, k = prof_map(F, HULL)
        band(sh, F, Y(.42), 1e3, "r")
        band(sh, F, Y(1.5), Y(1.3), "y")
        for mx in (.9, 1.75, 2.6, 3.45, 4.3):
            sh.circle_r(X(mx), Y(.88), s * .17, "b"); sh.circle_line(X(mx), Y(.88), s * .24, "l", "stroke-width:.6")
        # anker voorop
        ax = X(5.15); ay = Y(.92); r = s * .18
        sh.line(f"M{f(ax)} {f(ay - r * 1.4)}V{f(ay + r * 1.2)}M{f(ax - r)} {f(ay - r * .6)}H{f(ax + r)}"
                f"M{f(ax - r * 1.2)} {f(ay + r * .4)}Q{f(ax - r)} {f(ay + r * 1.5)} {f(ax)} {f(ay + r * 1.2)}Q{f(ax + r)} {f(ay + r * 1.5)} {f(ax + r * 1.2)} {f(ay + r * .4)}", "l", "stroke-width:.8")
        sh.circle_line(ax, ay - r * 1.7, r * .35, "l", "stroke-width:.7")
    elif z > .95:
        # dek: plek voor de hut (gestippeld) en twee pakjes
        cw, cd = CABIN[0] * s, CABIN[1] * s
        hx = (2.3 - 3.2) * s  # hut tussen x = 1.0 en 3.6 op het dek
        sh.rect_line(hx - cw / 2, -cd / 2, cw, cd, "l", 0, "stroke-width:.7;stroke-dasharray:1.5 1.5")
        sh.line("".join(f"M{f(xx)} {f(-F.h / 2 + 1)}V{f(F.h / 2 - 1)}" for xx in [(-3.2 + t * .5) * s for t in range(1, 13)] if abs(xx - hx) > cw / 2 + 1), "l", "stroke-width:.35")
        for (gx, gy, c, r) in ((1.05, -.5, "g", .26), (1.15, .4, "p", .3), (1.75, -.05, "y", .26)):
            sh.rect_r(gx * s - s * r, gy * s - s * r, s * r * 2, s * r * 2, c, .6)
            sh.seg(gx * s, gy * s - s * r, gx * s, gy * s + s * r, "l", "stroke-width:.7")
            sh.seg(gx * s - s * r, gy * s, gx * s + s * r, gy * s, "l", "stroke-width:.7")
    elif x > .5:  # boeg: zelfde gouden rand en rode waterlijn als de zijkanten (z loopt van 1,5 boven tot 0 onder)
        zy = lambda zz: F.h / 2 - zz / 1.5 * F.h
        band(sh, F, zy(.42), 1e3, "r"); band(sh, F, -1e3, zy(1.3), "y")
    elif x < -.9:  # spiegel (achterkant): vlaggetje
        sh.rect_r(-F.w * .18, -F.h * .25, F.w * .36, F.h * .3, "y", .5)
        sh.circle_r(0, -F.h * .1, F.h * .08, "r")


def hut(sh, F):
    s_ = side(F); w, h = F.w, F.h
    if s_ in ("front", "back"):
        band(sh, F, -h / 2, -h / 2 + h * .16, "y")
        for k in range(4):
            xx = -w * .36 + k * w * .24
            sh.rect_r(xx - w * .08, -h * .12, w * .16, h * .4, "b", .8)
            sh.seg(xx, -h * .12, xx, h * .28, "l", "stroke-width:.5")
        # vlaggenlijn langs de dakrand
        n = 7
        for k in range(n):
            xx = -w / 2 + (k + .5) * w / n
            sh.poly_r([(xx - w * .045, -h / 2 + h * .16), (xx + w * .045, -h / 2 + h * .16), (xx, -h / 2 + h * .34)], "rny"[k % 3])
    elif s_ in ("left", "right"):
        band(sh, F, -h / 2, -h / 2 + h * .16, "y")
        sh.rect_r(-w * .22, -h * .1, w * .44, h * .6, "w", .8)
        sh.circle_r(w * .12, h * .22, w * .04, "y")
        sh.rect_r(-w * .14, -h * .02, w * .28, h * .18, "b", .5)
    elif s_ == "top":
        fw = FUNNEL[0] * F.sc
        sh.rect_line(w * .18 - fw / 2, -fw / 2, fw, fw, "l", 0, "stroke-width:.7;stroke-dasharray:1.5 1.5")
        sh.circle_r(-w * .25, 0, h * .14, "r"); sh.circle_r(-w * .25, 0, h * .06, "-")  # reddingsboei
        for a in range(4):
            ang = a * math.pi / 2 + math.pi / 4
            sh.seg(-w * .25 + math.cos(ang) * h * .06, math.sin(ang) * h * .06, -w * .25 + math.cos(ang) * h * .14, math.sin(ang) * h * .14, "l", "stroke-width:.5")


def pijp(sh, F):
    s_ = side(F); w, h = F.w, F.h
    if s_ in ("front", "back", "left", "right"):
        band(sh, F, -h / 2, -h / 2 + h * .2, "x")
        band(sh, F, -h * .12, h * .06, "y")
        if s_ == "front":
            sh.region(star_path(0, h * .26, w * .16, w * .07), "y")
    elif s_ == "top":
        sh.rect_r(-w * .3, -h * .3, w * .6, h * .6, "x")


def pakjesboot():
    sh = Sheet(); title(sh, "Pakjesboot", 16); sh.text(100, 27, "Een stoomboot met een hut en een schoorsteen.", 6.5)
    parts = [Part(profile_y(HULL, HULL_D), lambda F: "-" if F.n[2] < -.95 else "w" if F.n[2] > .95 else "n", romp, (8, 34, 184, 138)),
             Part(box_model(*CABIN), lambda F: "-" if side(F) == "bottom" else "w" if side(F) == "top" else "-", hut, (8, 178, 116, 90), upright=(0, -1, 0)),
             Part(box_model(*FUNNEL), lambda F: "-" if side(F) == "bottom" else "r", pijp, (128, 178, 64, 90), upright=(0, -1, 0))]
    nets(sh, parts)
    sh.legend(["cut", "fold", "glue"], 274)
    steps = ["Kleur alle vlakken en tekeningen. Knip de drie delen uit langs de streepjeslijnen; de grijze flapjes blijven eraan.",
             "Vouw alle stippellijnen naar binnen, ook de flapjes: de tekening blijft aan de buitenkant. Met een liniaal en een lege balpen eerst krassen vouwt het strakker.",
             "Maak eerst de romp: de twee lange vlakken met de patrijspoorten zijn de zijkanten, de punt is de voorkant. Het vlak met de pakjes is het dek.",
             "Maak daarna de hut en de schoorsteen. Plak de flapjes één voor één vast aan de binnenkant van de rand ernaast.",
             "Lijm de hut op het gestippelde vak op het dek en de schoorsteen op het gestippelde vakje op het dak van de hut. Laat alles goed drogen: de pakjesboot kan varen!"]
    write(OUT, "bouwplaat-pakjesboot", sh, {"category": "feest", "age": "6-9", "kind": "bouwplaat", "difficulty": 2, "minutes": 40, "paperGsm": 160,
        "adultHelp": True, "holiday": "sinterklaas", "materials": MAT,
        "i18n": {"nl": {"name": "Bouwplaat: pakjesboot", "printNote": "Op stevig papier (160 gram) wordt hij het mooist.", "steps": steps}}})


# ======================================================================================
# 3. Schoorsteendoosje met Piet die eruit kijkt
# ======================================================================================
CHIM = (2.2, 2.2, 3.3)


def schoorsteen_face(sh, F):
    s_ = side(F); w, h = F.w, F.h
    if s_ in ("front", "back", "left", "right"):
        roof = h * .24
        band(sh, F, -h / 2, -h / 2 + h * .1, "z")
        bricks(sh, F, 7, -h / 2 + h * .1, h / 2 - roof, .5)
        # dakpannen onderaan: de schoorsteen staat op een dak
        sh.region(f"M{f(-w / 2)} {f(h / 2 - roof)}H{f(w / 2)}V{f(h / 2)}H{f(-w / 2)}Z", "o")
        sh.line("".join(f"M{f(-w / 2 + .5)} {f(h / 2 - roof + k * roof / 3)}H{f(w / 2 - .5)}" for k in (1, 2)) +
                "".join(f"M{f(-w / 2 + (j + (.5 if k % 2 else 0)) * w / 5)} {f(h / 2 - roof + k * roof / 3 + .4)}v{f(roof / 3 - .8)}" for k in range(3) for j in range(1, 5)), "l", "stroke-width:.5")
        if s_ == "front":
            sh.rect_r(-w * .2, -h * .05, w * .4, h * .18, "-", 1)
            sh.text(0, h * .05, "Voor:", 5, weight="700")
    elif s_ == "top":
        sh.rect_r(-w * .36, -h * .36, w * .72, h * .72, "x")


def piet_kop(sh, cx, cy, s, hair="x", cap="g", feather="y"):
    """Kop van Roetveegpiet met kraag en twee handen op de rand (cx, cy = midden van het gezicht)."""
    S = lambda v: v * s
    for d in (-1, 1):
        sh.circle_r(cx + d * S(14), cy - S(1), S(4.8), hair); sh.circle_r(cx + d * S(13.5), cy + S(7), S(4.4), hair)
    sh.region(f"M{f(cx - S(14))} {f(cy + S(14))}Q{f(cx - S(8))} {f(cy + S(24))} {f(cx)} {f(cy + S(20))}Q{f(cx + S(8))} {f(cy + S(24))} {f(cx + S(14))} {f(cy + S(14))}"
              f"Q{f(cx)} {f(cy + S(17))} {f(cx - S(14))} {f(cy + S(14))}Z", "-")
    sh.circle_r(cx, cy, S(14), "-")
    eye(sh, cx - S(5), cy + S(1), S(1.8)); eye(sh, cx + S(5), cy + S(1), S(1.8)); smile(sh, cx, cy + S(6), S(4.5))
    x, y = cx - S(9.5), cy + S(3.2)  # één lichte roetveeg op de wang (zoals piet(light_soot=True))
    sh.region(f"M{f(x - S(2.6))} {f(y)}Q{f(x)} {f(y - S(1.8))} {f(x + S(2.6))} {f(y)}Q{f(x)} {f(y + S(1.2))} {f(x - S(2.6))} {f(y)}Z", "z")
    beret(sh, cx, cy, s, cap, feather)
    sh.circle_r(cx + S(7), cy - S(14), S(2.6), "y")


def schoorsteendoosje():
    sh = Sheet(); title(sh, "Schoorsteendoosje", 16); sh.text(100, 27, "Een surprisedoosje met Piet die uit de schoorsteen kijkt.", 6.5)
    sc, boxes = nets(sh, [Part(box_model(*CHIM), lambda F: "-" if side(F) == "bottom" else "z" if side(F) == "top" else "r", schoorsteen_face, (8, 34, 184, 186))])
    # Piet om achter op te plakken
    fw = CHIM[0] * sc
    cx, cy = 48, 232
    s = fw / 40
    sh.raw('<g style="--sw:1.4">')
    glue_h = 10
    sh.raw(f'<rect class="glue" x="{f(cx - fw * .36)}" y="{f(cy + s * 16)}" width="{f(fw * .72)}" height="{f(glue_h)}"/>')
    piet_kop(sh, cx, cy, s)
    for d in (-1, 1): sh.circle_r(cx + d * s * 21, cy + s * 14, s * 4.5, "-")
    sh.raw('</g>')
    sil = [Point(cx, cy).buffer(s * 14), Point(cx - s * 14, cy + s * 3).buffer(s * 5.5), Point(cx + s * 14, cy + s * 3).buffer(s * 5.5),
           Polygon([(cx - s * 6, cy - s * 13), (cx - s * 20, cy - s * 8), (cx - s * 18, cy - s * 22), (cx + s * 18, cy - s * 28), (cx + s * 33, cy - s * 34), (cx + s * 31, cy - s * 26), (cx + s * 20, cy - s * 12)]),
           Polygon([(cx - s * 15, cy + s * 13), (cx + s * 15, cy + s * 13), (cx + s * 10, cy + s * 23), (cx - s * 10, cy + s * 23)]),
           Point(cx - s * 21, cy + s * 14).buffer(s * 4.5), Point(cx + s * 21, cy + s * 14).buffer(s * 4.5),
           sbox(cx - fw * .36, cy + s * 16, cx + fw * .36, cy + s * 16 + glue_h)]
    cut_around(sh, sil, 2.5)
    sh.legend(["cut", "fold", "glue"], 274)
    steps = ["Kleur de stenen, het dak en Piet. Knip de schoorsteen en Piet uit langs de streepjeslijnen; de grijze flapjes blijven eraan.",
             "Vouw alle stippellijnen naar binnen, ook de flapjes: de stenen blijven aan de buitenkant.",
             "Plak de flapjes één voor één vast aan de binnenkant van de rand ernaast. Stop er een klein cadeautje of een paar pepernoten in voordat je het zwarte vlak bovenop dichtplakt.",
             "Schrijf op het bordje voor wie het is. Plak Piet met het grijze stukje tegen de achterkant, zo dat zijn hoofd boven de schoorsteen uitkijkt."]
    write(OUT, "surprise-schoorsteendoosje", sh, {"category": "feest", "age": "4-6", "kind": "bouwplaat", "difficulty": 1, "minutes": 25, "paperGsm": 160,
        "adultHelp": True, "holiday": "sinterklaas", "materials": MAT,
        "i18n": {"nl": {"name": "Bouwplaat: schoorsteendoosje", "printNote": "Op stevig papier (160 gram) wordt hij het mooist.", "steps": steps}}})



# ======================================================================================
# vormen opnemen tijdens het tekenen (voor kniplijnen rond figuren)
# ======================================================================================
_TOK = re.compile(r"[MLHVCQZ]|-?\d*\.?\d+(?:e-?\d+)?")
def path_pts(d, n=10):
    """Absoluut SVG-pad (M L H V C Q Z) naar punten; None als het iets anders bevat."""
    if re.search(r"[A-BD-GI-KN-PR-UW-Ya-z]", d): return None
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
            pts += cubic(p0, p1, p2, p3, n)[1:]; cur = p3
        elif cmd == "Q":
            p0 = cur; p1 = (num(), num()); p2 = (num(), num())
            for k in range(1, n + 1):
                t = k / n; u = 1 - t
                pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
            cur = p2
    return pts


class RecSheet(Sheet):
    """Sheet die van elk vlak ook de vorm onthoudt (zonder transform), voor een kniplijn rondom."""
    def __init__(self, *a):
        super().__init__(*a); self.shapes = []; self.rec = True
    def region(self, d, code="-"):
        super().region(d, code)
        if self.rec:
            pts = path_pts(d)
            if pts and len(pts) >= 3: self.shapes.append(Polygon(pts).buffer(0))
    def circle_r(self, cx, cy, r, code="-"):
        super().circle_r(cx, cy, r, code)
        if self.rec: self.shapes.append(Point(cx, cy).buffer(r))
    def ellipse_r(self, cx, cy, rx, ry, code="-"):
        super().ellipse_r(cx, cy, rx, ry, code)
        if self.rec: self.shapes.append(Polygon([(cx + rx * math.cos(t / 24 * math.pi), cy + ry * math.sin(t / 24 * math.pi)) for t in range(48)]))
    def rect_r(self, x, y, w, h, code="-", rx=0):
        if rx:
            super().rect_r(x, y, w, h, code, rx)
            if self.rec: self.shapes.append(sbox(x, y, x + w, y + h))
        else:
            self.region(P([(x, y), (x + w, y), (x + w, y + h), (x, y + h)]), code)
    def take(self):
        out = self.shapes; self.shapes = []; return out


# ======================================================================================
# 4. Vingerpoppetjes: Sinterklaas, twee Pieten en het paard
# ======================================================================================
def piet_head(sh, cx, cy, s, hair="x", cap="g", feather="y", curls=True):
    S = lambda v: v * s
    for d in (-1, 1):
        if curls:
            sh.circle_r(cx + d * S(14), cy - S(1), S(4.8), hair); sh.circle_r(cx + d * S(13.5), cy + S(7), S(4.4), hair)
        else:
            sh.region(f"M{f(cx + d * S(10))} {f(cy - S(9))}Q{f(cx + d * S(20))} {f(cy - S(5))} {f(cx + d * S(19))} {f(cy + S(12))}H{f(cx + d * S(12.5))}Q{f(cx + d * S(13.5))} {f(cy)} {f(cx + d * S(10))} {f(cy - S(9))}Z", hair)
    sh.circle_r(cx, cy, S(14), "-")
    eye(sh, cx - S(5), cy + S(1), S(1.8)); eye(sh, cx + S(5), cy + S(1), S(1.8)); smile(sh, cx, cy + S(6), S(4.5))
    x, y = cx - S(9.5), cy + S(3.2)  # één lichte roetveeg op de wang
    sh.region(f"M{f(x - S(2.6))} {f(y)}Q{f(x)} {f(y - S(1.8))} {f(x + S(2.6))} {f(y)}Q{f(x)} {f(y + S(1.2))} {f(x - S(2.6))} {f(y)}Z", "z")
    beret(sh, cx, cy, s, cap, feather)
    sh.circle_r(cx + S(7), cy - S(14), S(2.6), "y")


def piet_puppet(sh, cx, base, s, suit, cap, curls=True, hair="x"):
    S = lambda v: v * s
    # schouders met pofmouwen en kraag
    sh.region(f"M{f(cx - S(22))} {f(base)}V{f(base - S(12))}Q{f(cx - S(22))} {f(base - S(24))} {f(cx - S(8))} {f(base - S(26))}H{f(cx + S(8))}Q{f(cx + S(22))} {f(base - S(24))} {f(cx + S(22))} {f(base - S(12))}V{f(base)}Z", suit)
    for d in (-1, 1): sh.ellipse_r(cx + d * S(20), base - S(16), S(7), S(8), cap)
    for k in range(2): sh.circle_r(cx, base - S(9) + k * S(6), S(1.8), "y")
    cy = base - S(44)
    sh.region(f"M{f(cx - S(14))} {f(cy + S(14))}Q{f(cx - S(8))} {f(cy + S(24))} {f(cx)} {f(cy + S(20))}Q{f(cx + S(8))} {f(cy + S(24))} {f(cx + S(14))} {f(cy + S(14))}"
              f"Q{f(cx)} {f(cy + S(17))} {f(cx - S(14))} {f(cy + S(14))}Z", "-")
    piet_head(sh, cx, cy, s, hair, cap, "y", curls)


def sint_puppet(sh, cx, base, s):
    S = lambda v: v * s
    sh.region(f"M{f(cx - S(26))} {f(base)}V{f(base - S(14))}Q{f(cx - S(24))} {f(base - S(30))} {f(cx - S(8))} {f(base - S(32))}H{f(cx + S(8))}Q{f(cx + S(24))} {f(base - S(30))} {f(cx + S(26))} {f(base - S(14))}V{f(base)}Z", "r")
    for d in (-1, 1): sh.region(f"M{f(cx + d * S(4))} {f(base - S(30))}L{f(cx + d * S(8))} {f(base)}H{f(cx + d * S(2))}L{f(cx + d * S(1))} {f(base - S(30))}Z", "y")
    sint(sh, cx, base - S(100), s, staff_side=0, face_only=True)


def horse_puppet(sh, cx, base, s, code="-", mane="z"):
    """Paardenhoofd met hals, naar rechts kijkend, met hoofdstel."""
    S = lambda v: v * s
    bx, by = cx - S(40), base - S(2)
    neck = (f"M{f(bx + S(12))} {f(by)}C{f(bx + S(16))} {f(by - S(26))} {f(bx + S(26))} {f(by - S(48))} {f(bx + S(38))} {f(by - S(62))}"
            f"L{f(bx + S(58))} {f(by - S(50))}C{f(bx + S(50))} {f(by - S(34))} {f(bx + S(48))} {f(by - S(16))} {f(bx + S(54))} {f(by)}Z")
    hx, hy, ang = bx + S(56), by - S(54), 38
    rot = lambda p: (hx + (p[0] - hx) * math.cos(math.radians(ang)) - (p[1] - hy) * math.sin(math.radians(ang)),
                     hy + (p[0] - hx) * math.sin(math.radians(ang)) + (p[1] - hy) * math.cos(math.radians(ang)))
    for ex in (0, 8):  # oren
        sh.region(f"M{f(bx + S(34 + ex))} {f(by - S(62 + ex * .4))}L{f(bx + S(36 + ex))} {f(by - S(80 + ex * .4))}L{f(bx + S(46 + ex))} {f(by - S(64 + ex * .4))}Z", code)
    sh.region(neck, code)
    sh.raw(f'<g transform="rotate({ang} {f(hx)} {f(hy)})">'); sh.rec = False
    sh.rect_r(hx - S(14), hy - S(12), S(40), S(23), code, S(10))
    sh.rect_r(hx + S(2), hy - S(12), S(4), S(23), "r", S(1))
    sh.rect_r(hx + S(17), hy - S(11.5), S(3.4), S(22), "r", S(1))
    sh.rec = True; sh.raw("</g>")
    sh.shapes.append(Polygon([rot(p) for p in [(hx - S(14), hy - S(12)), (hx + S(26), hy - S(12)), (hx + S(26), hy + S(11)), (hx - S(14), hy + S(11))]]).buffer(-S(6)).buffer(S(6)))
    # manen met golfjes en een plukje tussen de oren
    d = f"M{f(bx + S(36))} {f(by - S(66))}"
    pts = [(bx + S(36) - k * S(4.2), by - S(66) + k * S(9.4)) for k in range(1, 8)]
    for k, (x, y) in enumerate(pts):
        d += f"Q{f(x - S(6))} {f(y - S(6))} {f(x)} {f(y)}"
    d += f"H{f(bx + S(20))}C{f(bx + S(22))} {f(by - S(24))} {f(bx + S(30))} {f(by - S(46))} {f(bx + S(44))} {f(by - S(60))}Z"
    sh.region(d, mane)
    sh.region(f"M{f(bx + S(40))} {f(by - S(62))}Q{f(bx + S(44))} {f(by - S(74))} {f(bx + S(52))} {f(by - S(66))}Q{f(bx + S(50))} {f(by - S(60))} {f(bx + S(46))} {f(by - S(58))}Z", mane)
    ex, ey = rot((hx - S(2), hy - S(4)))
    eye(sh, ex, ey, S(2.2))
    nx, ny = rot((hx + S(21), hy - S(2)))
    sh.dot(nx, ny, S(1.4))
    m1, m2 = rot((hx + S(14), hy + S(7))), rot((hx + S(22), hy + S(5)))
    sh.line(f"M{f(m1[0])} {f(m1[1])}Q{f((m1[0] + m2[0]) / 2)} {f((m1[1] + m2[1]) / 2 + S(2))} {f(m2[0])} {f(m2[1])}", "l", "stroke-width:1")


def vingerpoppetjes():
    sh = RecSheet(); title(sh, "Vingerpoppetjes", 16)
    sh.text(100, 27, "Sinterklaas, twee Pieten en het paard, elk met een strookje.", 6.5)
    figs = [lambda cx, b: sint_puppet(sh, cx, b, .78), lambda cx, b: piet_puppet(sh, cx, b, .9, "o", "g"),
            lambda cx, b: piet_puppet(sh, cx, b, .9, "b", "p", curls=False, hair="w"), lambda cx, b: horse_puppet(sh, cx, b, .82)]
    SW, SH, GL = 74, 15, 11
    for k, fig in enumerate(figs):
        cx = 52 + (k % 2) * 96; base = 112 + (k // 2) * 118
        sh.raw('<g style="--sw:1.6">')
        sh.raw(f'<path class="r" style="stroke:none" d="{P([(cx - SW / 2, base), (cx + SW / 2 - GL, base), (cx + SW / 2 - GL, base + SH), (cx - SW / 2, base + SH)])}"/>', "y")
        sh.raw(f'<rect class="glue" x="{f(cx + SW / 2 - GL)}" y="{f(base)}" width="{GL}" height="{SH}"/>')
        for x in (cx - SW / 2 + 7, cx + SW / 2 - GL - 7): sh.region(star_path(x, base + SH / 2, 4.2, 1.8), "r")
        sh.take()
        fig(cx, base + 1)
        shapes = sh.take()
        sh.raw('</g>')
        cut_around(sh, shapes + [sbox(cx - SW / 2 - 2.5, base - 2.5, cx + SW / 2 + 2.5, base + SH + 2.5).buffer(-2.5)], 2.5)
    sh.legend(["cut", "glue"], 274)
    write(OUT, "vingerpoppetjes-sint-en-piet", sh, {"category": "feest", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25, "holiday": "sinterklaas",
        "adultHelp": False, "materials": [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Vingerpoppetjes: Sinterklaas en Piet", "steps": [
            "Kleur Sinterklaas, de twee Pieten en het paard in. Kies voor de Pieten je eigen kleuren.",
            "Knip elk poppetje uit langs de streepjeslijn. Het poppetje en het strookje blijven aan elkaar vast.",
            "Leg het strookje om je vinger en plak het einde op het grijze vakje. Niet te strak: je vinger moet er makkelijk in en uit kunnen.",
            "Steek je vingers in de poppetjes en speel de intocht of pakjesavond na!"]}}})


# ======================================================================================
# 5. Verlanglijstje om in te kleuren en in te vullen
# ======================================================================================
def mini_shoe(sh, x0, base, k, code="r"):
    """Kleine schoen (zelfde profiel als de bouwplaat), neus naar rechts, met een wortel erin."""
    T = lambda p: (x0 + p[0] * k, base - p[1] * k)
    sh.poly_r([T(p) for p in [(14, 128), (40, 132), (36, 60), (26, 58)]], "o")
    top = T((27, 131))
    for dx in (-14, 0, 14): sh.line(f"M{f(top[0])} {f(top[1])}l{f(dx * k)} {f(-22 * k)}", "l", "stroke-width:1")
    sh.poly_r([T(p) for p in shoe_band_line()], code)
    sh.poly_r([T((0, 0)), T((140, 0)), T((140, 9)), T((0, 9))], "w")


def verlanglijstje():
    sh = Sheet(); title(sh, "Mijn verlanglijstje", 21, 13)
    sh.raw('<g style="--sw:1.6">')
    mitre(sh, 24, 32, .55)
    gift_box(sh, 166, 17, 20, 15, "b", "y")
    sh.raw('</g>')
    sh.text(20, 44, "Lieve Sinterklaas,", 7.5, "start", weight="700")
    fw, fh = 76, 62
    for k in range(4):
        x = 20 + (k % 2) * 84; y = 52 + (k // 2) * 86
        sh.rect_line(x, y, fw, fh, "l", 4, "stroke-width:1.4")
        sh.raw('<g style="--sw:1.4">'); sh.region(star_path(x + 5, y + 5, 9, 4), "-"); sh.raw('</g>')
        sh.text(x + 5, y + 7.8, str(k + 1), 7, weight="800")
        sh.seg(x + 2, y + fh + 11, x + fw - 2, y + fh + 11, "guide")
    sh.text(20, 231, "Groetjes van:", 7.5, "start", weight="700")
    sh.seg(74, 231, 180, 231, "guide")
    # versiering onderaan: pakjes, pepernoten, een schoen en de staf
    sh.raw('<g style="--sw:1.6">')
    gift_box(sh, 18, 250, 22, 17, "r", "y", dots="y")
    for (x, y) in ((52, 262), (60, 258), (68, 263), (58, 266), (48, 266), (66, 268)): pepernoot(sh, x, y, 3.6)
    mini_shoe(sh, 86, 269, .21, "r")
    gift_box(sh, 132, 249, 20, 18, "g", "r")
    for (x, y, r) in ((168, 256, 5), (184, 250, 3.5), (180, 265, 4)): sh.region(star_path(x, y, r, r * .42), "y")
    sh.raw('</g>')
    write(OUT, "verlanglijstje-voor-sinterklaas", sh, {"category": "feest", "age": "4-6", "kind": "werkblad", "difficulty": 1, "minutes": 20, "holiday": "sinterklaas",
        "adultHelp": False, "materials": [{"slug": "kleurpotloden"}, {"slug": "potlood"}, {"slug": "stiften", "optional": True}],
        "i18n": {"nl": {"name": "Verlanglijstje voor Sinterklaas", "printNote": "Gewoon printpapier is goed. Print er een paar als er broertjes of zusjes zijn.",
            "steps": [
                "Kleur de mijter, de pakjes, de pepernoten en de schoen in.",
                "Teken in elk vak iets wat je graag zou willen hebben. Kun je al schrijven? Schrijf het dan op de lijn eronder, of vraag een grote om te helpen.",
                "Schrijf je naam bij 'Groetjes van'.",
                "Vouw je verlanglijstje dubbel en stop het in je schoen, samen met een wortel voor het paard."]}}})


# ======================================================================================
# 6. Slinger met mijters, pakjes en meer
# ======================================================================================
def slinger():
    sh = Sheet(); title(sh, "Sinterklaasslinger", 16); sh.text(100, 27, "Knip de vlaggetjes uit en hang ze aan een touw.", 6.5)
    FW, BH, PT, FL = 56, 60, 36, 11  # breedte, recht stuk, punt, flap
    cols = (36, 100, 164); rows = (34, 150)
    flags = "yrbybr"
    def mitre_d(cx, cy): mitre(sh, cx, cy + 25, .9, "r", "y")
    def gift_d(cx, cy): gift_box(sh, cx - 16, cy - 2, 32, 25, "b", "y", dots="y")
    def nootjes_d(cx, cy):
        for (x, y) in ((-11, 6), (0, 2), (11, 6), (-6, 15), (6, 15), (-16, 17), (16, 17), (0, 25), (-9, -6), (9, -6), (0, -14)): pepernoot(sh, cx + x, cy + y, 5)
    def shoe_d(cx, cy): mini_shoe(sh, cx - 23, cy + 24, .28, "r")
    def staff_d(cx, cy):
        staff(sh, cx + 5, cy - 20, cy + 34, .9)
        for (x, y) in ((-12, -10), (14, 12)): sh.region(star_path(cx + x, cy + y, 5, 2.1), "y")
    def beret_d(cx, cy): beret(sh, cx - 8, cy + 22, .95, "p", "y"); sh.circle_r(cx - 1.4, cy + 8.6, 2.6, "y")
    draws = [mitre_d, gift_d, nootjes_d, shoe_d, staff_d, beret_d]
    for k, d in enumerate(draws):
        cx = cols[k % 3]; top = rows[k // 3]; y0 = top + FL
        body = [(cx - FW / 2, y0), (cx + FW / 2, y0), (cx + FW / 2, y0 + BH), (cx, y0 + BH + PT), (cx - FW / 2, y0 + BH)]
        sh.raw(f'<path class="r" style="stroke:none" d="{P(body)}"/>', flags[k])
        sh.raw(f'<rect class="glue" x="{f(cx - FW / 2)}" y="{f(top)}" width="{FW}" height="{FL}"/>')
        sh.raw('<g style="--sw:1.6">'); d(cx, y0 + BH / 2 - 2); sh.raw('</g>')
        sh.line(PL([(cx - FW / 2, y0), (cx - FW / 2, top), (cx + FW / 2, top), (cx + FW / 2, y0)]) + PL(body[1:] + [body[0]])[0:], "cut")
        sh.seg(cx - FW / 2, y0, cx + FW / 2, y0, "fold")
    sh.text(100, 266, "Print het vel nog een keer voor een langere slinger.", 6, cls="tip")
    sh.legend(["cut", "fold", "glue"], 274)
    write(OUT, "sinterklaasslinger", sh, {"category": "feest", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 30, "holiday": "sinterklaas",
        "adultHelp": False, "materials": [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}, {"slug": "touw"}],
        "i18n": {"nl": {"name": "Sinterklaasslinger", "printNote": "Print het vel twee of drie keer voor een lange slinger.",
            "steps": [
                "Kleur de zes vlaggetjes in: een mijter, een pakje, pepernoten, een schoen, de staf en een Pietenbaret.",
                "Knip de vlaggetjes uit langs de streepjeslijnen. Het grijze strookje bovenaan blijft eraan.",
                "Vouw het grijze strookje naar achteren langs de stippellijn.",
                "Leg een lang touw in de vouw. Doe lijm op het strookje, vouw het over het touw naar achteren en druk het vast tegen de achterkant van het vlaggetje.",
                "Schuif de vlaggetjes een stukje uit elkaar en hang de slinger op."]}}})

if __name__ == "__main__":
    for slug, fn in (("schoen-om-te-zetten", schoen), ("bouwplaat-pakjesboot", pakjesboot), ("surprise-schoorsteendoosje", schoorsteendoosje),
                     ("vingerpoppetjes-sint-en-piet", vingerpoppetjes), ("verlanglijstje-voor-sinterklaas", verlanglijstje), ("sinterklaasslinger", slinger)):
        if not ONLY or slug in ONLY: fn()
