"""Batch 37v: thema-bouwplaten (uitslag uit polyhedra, tekeningen op de vlakken): een dorp van losse huisjes,
dierendoosjes, voertuigen, feestdoosjes en twee sterveelvlakken.

De helpers hieronder zijn overgenomen uit batch29v (niet geïmporteerd: dat bestand schrijft bij import).
Elke bouwplaat is een convex 3D-model (z omhoog, voorkant = -y). De tekening op elk vlak wordt in een eigen
assenstelsel getekend (x naar rechts, y naar beneden, gezien van buiten, "onder" = naar de grond).
Een bouwplaat kan uit meer delen bestaan (bijv. kerk + toren); die krijgen dezelfde schaal zodat ze passen.
De sterveelvlakken zijn niet convex en hebben een eigen tekenfunctie (bergvouwen en dalvouwen).
"""
import math, random
from lib_gen import *
import polyhedra as ph
from shapely.geometry import Polygon, box as sbox
from shapes import heart_path, star_path, cloud_path, leaf_path

MAT = [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}, {"slug": "stevig-papier", "optional": True}]
def P(points): return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in points) + "Z"
def cross(u, v): return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
def unit(v): n = ph.norm(v); return tuple(x / n for x in v)

# ---------- uitslag kiezen en tekenen ----------
def rotk(p, k):
    """Draait over k kwartslagen, of over een hoek (radialen) als k een float is."""
    if isinstance(k, float): c, si = math.cos(k), math.sin(k); return (c * p[0] - si * p[1], si * p[0] + c * p[1])
    for _ in range(k % 4): p = (-p[1], p[0])
    return p
def front_down(verts, faces, polys, upright):
    """Richting (in uitslagcoördinaten) waarin de onderkant van het voorvlak wijst."""
    fi = max(range(len(faces)), key=lambda i: ph.dot(unit(cross(ph.sub(verts[faces[i][1]], verts[faces[i][0]]), ph.sub(verts[faces[i][2]], verts[faces[i][0]]))), upright))
    fc = faces[fi]; zmin = min(verts[u][2] for u in fc); lo = [k for k, v in enumerate(fc) if verts[v][2] < zmin + 1e-9]
    q = polys[fi]; bot = tuple(sum(q[k][j] for k in lo) / len(lo) for j in (0, 1)); cen = tuple(sum(p[j] for p in q) / len(q) for j in (0, 1))
    return (bot[0] - cen[0], bot[1] - cen[1])
def best_layout(verts, faces, box, depth, tries, upright=None, penalty=.86):
    """Probeert BFS vanaf elk vlak en willekeurige bomen in vier standen; kiest de grootste uitslag,
    met voorkeur voor een stand waarin het voorvlak rechtop staat."""
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
        if dv: opts.append(-math.pi / 2 - math.atan2(dv[1], dv[0]))  # precies rechtop
        for k in opts:
            if isinstance(k, float):
                rp = [rotk(p, k) for p in allp]
                ww = max(x for x, _ in rp) - min(x for x, _ in rp); hh = max(y for _, y in rp) - min(y for _, y in rp)
            else: ww, hh = (h, w) if k % 2 else (w, h)
            sc = min(bw / ww, bh / hh); score = sc
            if dv:
                d = rotk(dv, k)
                if not (d[1] < -abs(d[0]) * 9): score *= penalty  # model-y omhoog: onder moet naar -y wijzen
                elif isinstance(k, float) and abs(k % (math.pi / 2)) > .02 and abs(k % (math.pi / 2) - math.pi / 2) > .02: score *= .97
            if best is None or score > best[0] + 1e-9: best = (score, sc, lay, k)
    assert best, "geen uitslag"
    return best[1:]

class Face:
    pass

def build_net(sh, verts, faces, codes, box, draw_face, depth=.17, tries=150, style="--sw:1.2", upright=None, pre=None):
    """Tekent de uitslag; draw_face(sh, F) tekent per vlak in lokale coördinaten (F.w, F.h, F.poly, F.n, F.c3).
    upright: normaal van het vlak dat rechtop moet staan (anders wordt de hele uitslag 180 graden gedraaid)."""
    sc, (polys, tabs, folds, cuts), kk = pre or best_layout(verts, faces, box, depth, tries, upright)
    R = lambda p: rotk(p, kk)  # draaien (geen spiegeling)
    allp = [R(p) for poly in polys + tabs for p in poly]
    mnx, mxx = min(x for x, _ in allp), max(x for x, _ in allp); mny, mxy = min(y for _, y in allp), max(y for _, y in allp)
    bx, by, bw, bh = box
    ox = bx + (bw - (mxx - mnx) * sc) / 2; oy = by + (bh - (mxy - mny) * sc) / 2
    # y spiegelen: de uitslag van polyhedra is van binnen gezien; zo ligt de bedrukte kant buiten
    T = lambda p: (ox + (R(p)[0] - mnx) * sc, oy + (mxy - R(p)[1]) * sc)
    spolys = [[T(p) for p in poly] for poly in polys]
    for poly, code in zip(spolys, codes):
        sh.raw(f'<path class="r" style="stroke:none" d="{P(poly)}"/>', code)
    for fi, (fc, sp) in enumerate(zip(faces, spolys)):
        V = [verts[v] for v in fc]
        n = unit(cross(ph.sub(V[1], V[0]), ph.sub(V[2], V[0])))
        # buitenwaarts? (convex model: van het zwaartepunt af)
        cen = tuple(sum(v[k] for v in verts) / len(verts) for k in range(3))
        fcen = tuple(sum(v[k] for v in V) / len(V) for k in range(3))
        if ph.dot(n, ph.sub(fcen, cen)) < 0: raise AssertionError(f"vlak {fi} niet buitenwaarts")
        # zichtbaar tegen de klok in (svg: y omlaag) = van buiten gezien
        area = sum(sp[i][0] * sp[(i + 1) % len(sp)][1] - sp[(i + 1) % len(sp)][0] * sp[i][1] for i in range(len(sp)))
        assert area < 0, "uitslag gespiegeld"
        if abs(n[2]) > .95: up = (0, 1, 0)
        else: up = unit(ph.sub((0, 0, 1), ph.scale(n, n[2])))
        right = cross(up, n)
        # affiene afbeelding 3D-vlak -> vel
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
    """Naam van het vlak uit de normaal: top, bottom, front, back, left, right, roof_front, ... ."""
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
def inset(F, d):
    g = Polygon(F.poly).buffer(-d, join_style=2)
    return list(g.exterior.coords)[:-1]

MODELS = {}
def box_model(w, d, h):
    return ph.hull_faces([(x, y, z) for x in (0, w) for y in (0, d) for z in (0, h)])
def house_x(w, d, h, H):
    """Huis met zadeldak, nok evenwijdig aan de voorgevel (x)."""
    pts = [(x, y, z) for x in (0, w) for y in (0, d) for z in (0, h)] + [(0, d / 2, H), (w, d / 2, H)]
    return ph.hull_faces(pts)
def house_y(w, d, h, H):
    """Huis met zadeldak, nok van voor naar achter (topgevel voor)."""
    pts = [(x, y, z) for x in (0, w) for y in (0, d) for z in (0, h)] + [(w / 2, 0, H), (w / 2, d, H)]
    return ph.hull_faces(pts)
def profile_y(prof, d):
    """Profiel in het xz-vlak, uitgetrokken over de diepte y."""
    return ph.hull_faces([(x, y, z) for x, z in prof for y in (0, d)])
def profile_x(prof, w):
    """Profiel in het yz-vlak, uitgetrokken over de breedte x."""
    return ph.hull_faces([(x, y, z) for y, z in prof for x in (0, w)])

# ---------- kleine tekenhulpjes (lokale coördinaten) ----------
def window(sh, x, y, w, h, code="b", cross_=True):
    sh.rect_r(x - w / 2, y - h / 2, w, h, code)
    if cross_: sh.line(f"M{f(x)} {f(y - h / 2)}V{f(y + h / 2)}M{f(x - w / 2)} {f(y)}H{f(x + w / 2)}")
def tiles(sh, F, step, code=None):
    """Dakpannen: rijen boogjes over het hele vlak."""
    y = -F.h / 2 + step
    d = []; row = 0
    while y < F.h / 2 - step * .4:
        c = clip(F.poly, -1e3, y - .01, 1e3, y + .01)
        if c:
            xs = [p[0] for p in c]; x0, x1 = min(xs) + 1, max(xs) - 1
            d.append(f"M{f(x0)} {f(y)}H{f(x1)}")
            x = x0 + step * (.5 if row % 2 else 1.2)
            while x < x1 - step * .3:
                d.append(f"M{f(x)} {f(y - step + .6)}V{f(y)}")
                x += step * 1.4
        y += step; row += 1
    sh.line("".join(d), "l", "stroke-width:.7")
def flower(sh, x, y, r, petal="m", heart="y", stem=0):
    if stem: sh.line(f"M{f(x)} {f(y + r)}V{f(y + r + stem)}", "l", "stroke-width:.9")
    for k in range(5):
        a = k * 2 * math.pi / 5 - math.pi / 2
        sh.circle_r(x + math.cos(a) * r * .62, y + math.sin(a) * r * .62, r * .45, petal)
    sh.circle_r(x, y, r * .4, heart)
def bee(sh, x, y, s, flip=False):
    k = -1 if flip else 1
    sh.ellipse_r(x - k * s * .1, y - s * .55, s * .38, s * .3, "b")
    sh.ellipse_r(x + k * s * .25, y - s * .5, s * .32, s * .26, "b")
    sh.ellipse_r(x, y, s * .7, s * .45, "y")
    sh.line(f"M{f(x - s * .15)} {f(y - s * .43)}V{f(y + s * .43)}M{f(x + s * .25)} {f(y - s * .38)}V{f(y + s * .38)}", "l", "stroke-width:1")
    sh.dot(x + k * s * .5, y - s * .08, s * .08)
def wheel(sh, x, y, r, code="z", spokes=0):
    sh.circle_r(x, y, r, code); sh.circle_r(x, y, r * .38, "-")
    if spokes:
        sh.line("".join(f"M{f(x + math.cos(a) * r * .38)} {f(y + math.sin(a) * r * .38)}L{f(x + math.cos(a) * r * .92)} {f(y + math.sin(a) * r * .92)}" for a in [k * 2 * math.pi / spokes for k in range(spokes)]), "l", "stroke-width:.8")
def snowflake(sh, x, y, r):
    d = ""
    for k in range(3):
        a = k * math.pi / 3; c, s = math.cos(a) * r, math.sin(a) * r
        d += f"M{f(x - c)} {f(y - s)}L{f(x + c)} {f(y + s)}"
    sh.line(d, "l", "stroke-width:.7")


def text_fit(sh, x, y, s, w, h, weight="800", mn=4.5):
    """Tekst gecentreerd op (x, y), zo groot als past in w x h (minimaal mn)."""
    size = max(mn, min(h * .7, w / (len(s) * .62)))
    sh.text(x, y + size * .36, s, size, weight=weight)

def sign(sh, x, y, w, h, s, code="-"):
    sh.rect_r(x - w / 2, y - h / 2, w, h, code, min(1.5, h * .2)); text_fit(sh, x, y, s, w * .9, h)

def awning(sh, x0, x1, y0, hh, code="r", n=7):
    sw = (x1 - x0) / n
    for k in range(n):
        x = x0 + k * sw
        sh.region(f"M{f(x)} {f(y0)}H{f(x + sw)}V{f(y0 + hh)}A{f(sw / 2)} {f(sw / 2.6)} 0 0 1 {f(x)} {f(y0 + hh)}Z", code if k % 2 == 0 else "-")

def arch(x, yb, w, h):
    r = w / 2
    return f"M{f(x - r)} {f(yb)}V{f(yb - h + r)}A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(yb - h + r)}V{f(yb)}Z"

def arch_window(sh, x, yb, w, h, code="b", lead=True):
    sh.region(arch(x, yb, w, h), code)
    if lead:
        r = w / 2; d = f"M{f(x)} {f(yb - h)}V{f(yb)}"
        y = yb - h + r
        while y < yb - .5: d += f"M{f(x - r)} {f(y)}H{f(x + r)}"; y += w * .7
        sh.line(d, "l", "stroke-width:.6")

def door(sh, x, yb, w, h, code="g", knob_right=True, glass=True):
    sh.rect_r(x - w / 2, yb - h, w, h, code)
    if glass: sh.rect_r(x - w * .3, yb - h * .88, w * .6, h * .35, "b")
    sh.dot(x + (w * .32 if knob_right else -w * .32), yb - h * .45, max(.6, w * .06))

def clock(sh, x, y, r):
    sh.circle_r(x, y, r, "-")
    for k in range(4):
        a = k * math.pi / 2; sh.dot(x + math.cos(a) * r * .75, y + math.sin(a) * r * .75, max(.35, r * .08))
    sh.line(f"M{f(x)} {f(y)}V{f(y - r * .6)}M{f(x)} {f(y)}L{f(x + r * .45)} {f(y + r * .1)}", "l", "stroke-width:.8")

def shutters_window(sh, x, y, w, h, code="b", shut="g"):
    window(sh, x, y, w, h, code)
    for k in (-1, 1):
        x0 = x + k * (w / 2 + w * .08) - (w * .32 if k < 0 else 0)
        sh.rect_r(x0, y - h / 2, w * .32, h, shut)
        sh.line("".join(f"M{f(x0 + w * .06)} {f(y - h / 2 + j * h / 5)}H{f(x0 + w * .26)}" for j in range(1, 5)), "l", "stroke-width:.5")

def flowerbox(sh, x, y, w, colors="rmo"):
    sh.rect_r(x - w / 2, y, w, w * .18, "w")
    n = len(colors)
    for k, c in enumerate(colors): flower(sh, x - w / 2 + (k + .5) * w / n, y - w * .02, w * .1, c, "y")

def crate(sh, x, yb, w, h, fruit, fcode):
    """Kist met groente of fruit erop."""
    if fruit == "appel":
        r = w * .13
        for k in range(4): sh.circle_r(x - w * .36 + r + k * w * .23, yb - h - r * .5, r, fcode)
        for k in range(3): sh.circle_r(x - w * .25 + r + k * w * .23, yb - h - r * 1.6, r, fcode)
    elif fruit == "wortel":
        for k in range(4):
            cx = x - w * .33 + k * w * .22
            sh.poly_r([(cx - w * .07, yb - h - w * .25), (cx + w * .07, yb - h - w * .25), (cx, yb - h + w * .02)], "o")
            sh.line(f"M{f(cx)} {f(yb - h - w * .25)}l{f(-w * .05)} {f(-w * .1)}M{f(cx)} {f(yb - h - w * .25)}l{f(w * .05)} {f(-w * .1)}M{f(cx)} {f(yb - h - w * .25)}v{f(-w * .12)}", "l", "stroke-width:.7")
    elif fruit == "kool":
        for k in range(2):
            cx = x - w * .22 + k * w * .44; r = w * .22
            sh.circle_r(cx, yb - h - r * .6, r, fcode)
            sh.line(f"M{f(cx - r * .5)} {f(yb - h - r * .2)}Q{f(cx)} {f(yb - h - r * 1.3)} {f(cx + r * .5)} {f(yb - h - r * .2)}M{f(cx)} {f(yb - h - r * 1.5)}V{f(yb - h)}", "l", "stroke-width:.6")
    elif fruit == "peer":
        for k in range(4):
            cx = x - w * .33 + k * w * .22; r = w * .09
            sh.region(f"M{f(cx)} {f(yb - h - r * 3)}C{f(cx + r * .7)} {f(yb - h - r * 3)} {f(cx + r * .6)} {f(yb - h - r * 1.8)} {f(cx + r * 1.1)} {f(yb - h - r * .9)}C{f(cx + r * 1.4)} {f(yb - h)} {f(cx - r * 1.4)} {f(yb - h)} {f(cx - r * 1.1)} {f(yb - h - r * .9)}C{f(cx - r * .6)} {f(yb - h - r * 1.8)} {f(cx - r * .7)} {f(yb - h - r * 3)} {f(cx)} {f(yb - h - r * 3)}Z", fcode)
    sh.rect_r(x - w / 2, yb - h, w, h, "w")
    sh.line(f"M{f(x - w / 2)} {f(yb - h / 2)}H{f(x + w / 2)}", "l", "stroke-width:.6")

def bricks(sh, F, rows, y0=None, y1=None, sw=.45):
    y0 = -F.h / 2 if y0 is None else y0; y1 = F.h / 2 if y1 is None else y1
    step = (y1 - y0) / rows; d = ""
    for k in range(1, rows):
        y = y0 + k * step; c = clip(F.poly, -1e3, y - .01, 1e3, y + .01)
        if c:
            xs = [p[0] for p in c]; d += f"M{f(min(xs) + .6)} {f(y)}H{f(max(xs) - .6)}"
    sh.line(d, "l", f"stroke-width:{sw}")

# ---------- bouwplaat met een of meer delen ----------
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

def bouwplaat(slug, name, sub, parts, cat, age, diff, minutes, steps_extra, holiday=None, adult=None, note=None, last=None):
    if not isinstance(parts, list): parts = [parts]
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16); sh.text(100, 27, sub, 6.5)
    pres = [best_layout(*p.model, p.box, p.depth, p.tries, p.upright) for p in parts]
    if len(parts) > 1:
        s = min(pr[0] for pr in pres); pres = [(s,) + tuple(pr[1:]) for pr in pres]
    for p, pr in zip(parts, pres):
        _, bb = build_net(sh, *p.model, face_codes(p.model, p.codes), p.box, p.draw, p.depth, p.tries, upright=p.upright, pre=pr)
        if p.label:
            x, y = p.label[1] if isinstance(p.label, tuple) else ((bb[0] + bb[2]) / 2, bb[1] - 2.5 if bb[1] > 38 else bb[3] + 7)
            sh.text(x, y, p.label[0] if isinstance(p.label, tuple) else p.label, 6.5, weight="800")
    sh.legend(["cut", "fold", "glue"], 274)
    steps = ["Kleur alle vlakken en tekeningen. Knip " + ("de delen" if len(parts) > 1 else "de bouwplaat") + " uit langs de doorgetrokken lijnen; de grijze flapjes blijven eraan.",
             "Vouw alle stippellijnen naar binnen, ook de flapjes: de tekening blijft aan de buitenkant. Met een liniaal en een lege balpen eerst krassen vouwt het strakker."] + steps_extra + [
             last or "Plak de flapjes één voor één vast aan de binnenkant van de rand ernaast. Het laatste vlak sluit je als een deksel: druk het even aan tot de lijm droog is."]
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "bouwplaat", "difficulty": diff, "minutes": minutes, "paperGsm": 160,
        "adultHelp": adult if adult is not None else age in ("4-6", "6-9"), "holiday": holiday, "materials": MAT,
        "i18n": {"nl": {"name": name, "printNote": note or "Op stevig papier (160 gram) wordt hij het mooist.", "steps": steps}}})

FULL = (10, 34, 180, 232)
def hipped(w, d, h, H, a):
    """Huis met schilddak: nok evenwijdig aan de voorgevel, a = inspringing van de nok aan beide kanten."""
    return ph.hull_faces([(x, y, z) for x in (0, w) for y in (0, d) for z in (0, h)] + [(a, d / 2, H), (w - a, d / 2, H)])

# ======================= het dorp =======================
# --- kerkje met losse toren ---
SCHIP = house_y(3, 4.2, 2.8, 4.8)
TH = 4.6
TOREN = ph.hull_faces([(x, y, z) for x in (0, 1.7) for y in (0, 1.7) for z in (0, TH)] + [(.85, .85, TH + 2.8)])
def schip(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("left", "right"):
        for k in range(3):
            x = -w * .3 + k * w * .3
            arch_window(sh, x, h * .28, w * .13, h * .62)
    elif s in ("front", "back"):
        wall = h * 2.8 / 4.8; yb = h / 2
        if s == "back":
            arch_window(sh, 0, yb - wall * .2, w * .26, wall * .65)
            sh.circle_r(0, yb - wall - h * .12, w * .12, "b"); sh.circle_r(0, yb - wall - h * .12, w * .05, "y")
            sh.line("".join(f"M{f(math.cos(a) * w * .05)} {f(yb - wall - h * .12 + math.sin(a) * w * .05)}L{f(math.cos(a) * w * .12)} {f(yb - wall - h * .12 + math.sin(a) * w * .12)}" for a in [k * math.pi / 4 for k in range(8)]), "l", "stroke-width:.6")
        else:
            for x in (-w * .39, w * .39): arch_window(sh, x, yb - wall * .25, w * .1, wall * .5, lead=False)
            sh.text(0, yb - wall * .5, "toren", max(4.5, w * .07), cls="tip"); sh.text(0, yb - wall * .5 + 6, "hier", max(4.5, w * .07), cls="tip")
    elif s.startswith("roof"):
        tiles(sh, F, F.h / 5)
def toren(sh, F):
    w, h = F.w, F.h
    if F.z > TH:
        bricks(sh, F, 6, -h / 2, h / 2, .6)
        return
    s = side(F)
    if s in ("bottom",): return
    if s == "back":
        sh.text(0, 0, "achterkant", max(4.5, w * .12), cls="tip", rotate=-90); return
    # galmgat bovenin, klok eronder
    yb = h / 2
    sh.region(arch(0, -h * .3, w * .44, h * .16), "x")
    sh.line("".join(f"M{f(-w * .22)} {f(-h * .3 - k * h * .035)}H{f(w * .22)}" for k in range(1, 4)), "l", "stroke-width:.8")
    clock(sh, 0, -h * .14, w * .26)
    if s == "front":
        sh.region(arch(0, yb, w * .44, h * .2), "r"); sh.seg(0, yb - h * .2 + w * .22, 0, yb, "l", "stroke-width:.6"); sh.dot(-w * .06, yb - h * .08, .7); sh.dot(w * .06, yb - h * .08, .7)
        arch_window(sh, 0, h * .2, w * .2, h * .12, lead=False)
    else:
        for y in (h * .16, h * .38): arch_window(sh, 0, y, w * .12, h * .1, lead=False)
    for y in (-h * .42, h * .02): sh.seg(-w / 2 + .5, y, w / 2 - .5, y, "l", "stroke-width:.6")
bouwplaat("bouwplaat-kerkje", "Bouwplaat: kerkje met toren", "Een dorpskerkje en een losse toren met een klok en een spits.",
          [Part(SCHIP, lambda F: "-" if side(F) == "bottom" else "z" if side(F).startswith("roof") else "w", schip, (8, 36, 115, 228), label="de kerk"),
           Part(TOREN, lambda F: "-" if side(F) == "bottom" else "g" if F.z > TH else "w", toren, (125, 36, 67, 228), label="de toren")],
          "wereld", "6-9", 3, 45,
          ["Maak eerst de kerk: de gevels met de punt zijn voor en achter, de lange kanten met de hoge ramen zijn de zijkanten.",
           "Maak daarna de toren: vouw de vier muren rond, dan de vier driehoeken van de spits tot hun punten elkaar raken.",
           "Plak de flapjes vast. Zet de toren met zijn achterkant tegen de voorgevel van de kerk (daar staat 'toren hier') en lijm hem vast."],
          last="Laat alles goed drogen. Maak er nog meer huisjes uit het dorp bij: samen wordt het een heel dorpsplein!")

def books(sh, x0, x1, yb, hmax, colors="rnygpot"):
    """Een plank met boeken (ruggen) van x0 tot x1, staand op yb."""
    x = x0; k = 0; rng = random.Random(int(x0 * 10) + int(yb * 7))
    while x < x1 - .5:
        bw = min(x1 - x, (x1 - x0) * rng.uniform(.07, .12)); bh = hmax * rng.uniform(.7, 1)
        sh.rect_r(x, yb - bh, bw, bh, colors[k % len(colors)]); x += bw; k += 1
    sh.seg(x0 - .5, yb, x1 + .5, yb, "l", "stroke-width:1")

# --- groenteboer ---
def groenteboer(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        wall = h * 3 / 4.6; yb = h / 2; yt = yb - wall
        sh.circle_r(0, yt - (h - wall) * .38, w * .09, "b"); sh.line(f"M{f(-w * .09)} {f(yt - (h - wall) * .38)}H{f(w * .09)}M0 {f(yt - (h - wall) * .38 - w * .09)}V{f(yt - (h - wall) * .38 + w * .09)}", "l", "stroke-width:.6")
        sign(sh, 0, yt + wall * .1, w * .84, wall * .13, "GROENTE & FRUIT")
        awning(sh, -w * .46, w * .46, yt + wall * .19, wall * .1, "g", 8)
        sh.rect_r(-w * .43, yt + wall * .36, w * .54, wall * .3, "b"); sh.seg(-w * .16, yt + wall * .36, -w * .16, yt + wall * .66)
        for k in range(5): sh.line(f"M{f(-w * .38 + k * w * .11)} {f(yt + wall * .36)}v{f(wall * .05)}", "l", "stroke-width:.6"); sh.ellipse_r(-w * .38 + k * w * .11, yt + wall * .45, w * .025, wall * .04, "y")
        door(sh, w * .3, yb, w * .18, wall * .58, "g")
        for x, fr, c in ((-w * .335, "appel", "r"), (-w * .115, "wortel", "o"), (w * .105, "kool", "l")):
            crate(sh, x, yb - .3, w * .21, wall * .11, fr, c)
    elif s in ("left", "right"):
        shutters_window(sh, 0, -h * .08, w * .28, h * .3, "b", "g"); flowerbox(sh, 0, h * .08, w * .4, "rym")
        if s == "right": crate(sh, 0, h / 2 - .3, w * .34, h * .13, "appel", "g")
    elif s == "back":
        wall = h * 3 / 4.6; yb = h / 2
        door(sh, -w * .2, yb, w * .2, wall * .55, "g", glass=False)
        crate(sh, w * .22, yb - .3, w * .3, wall * .13, "peer", "l")
        window(sh, 0, yb - wall - (h - wall) * .32, w * .16, (h - wall) * .26, "b")
    elif s.startswith("roof"):
        tiles(sh, F, F.h / 5)
bouwplaat("bouwplaat-groenteboer", "Bouwplaat: groenteboer", "Een winkeltje met kisten vol appels, wortels en kool.", Part(house_y(3.6, 3, 3, 4.6),
          lambda F: "-" if side(F) == "bottom" else "w" if side(F).startswith("roof") else "k", groenteboer, FULL),
          "eten", "6-9", 2, 35, ["De gevel met de punt en de luifel is de voorkant; het dak hoort erboven."])

# --- bloemist ---
def bloemist(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sign(sh, 0, -h * .38, w * .6, h * .14, "BLOEMIST")
        awning(sh, -w * .46, w * .46, -h * .27, h * .12, "m", 9)
        sh.rect_r(-w * .43, -h * .05, w * .52, h * .38, "b")
        for k, (c, y) in enumerate((("r", .05), ("y", .0), ("p", .06))):
            x = -w * .33 + k * w * .16
            flower(sh, x, h * y, w * .05, c, "o", h * .14)
            sh.poly_r([(x - w * .045, h * .22), (x + w * .045, h * .22), (x + w * .035, h * .32), (x - w * .035, h * .32)], "t")
        door(sh, w * .29, h / 2, w * .17, h * .58, "p")
        for k, c in enumerate("rmyo"):
            x = -w * .38 + k * w * .14
            sh.poly_r([(x - w * .05, h * .4), (x + w * .05, h * .4), (x + w * .04, h / 2 - .4), (x - w * .04, h / 2 - .4)], "z")
            for j in (-1, 0, 1): flower(sh, x + j * w * .035, h * .36 - abs(j) * h * .02 - (j == 0) * h * .05, w * .028, c, "y", 0)
    elif s == "roof_front":
        sh.poly_r([(-w * .14, -h * .05), (0, -h * .36), (w * .14, -h * .05)], "z")
        sh.rect_r(-w * .1, -h * .05, w * .2, h * .32, "k"); window(sh, 0, h * .11, w * .13, h * .24, "b")
        tiles(sh, F, F.h / 4)
    elif s == "roof_back":
        tiles(sh, F, F.h / 4)
    elif s in ("left", "right"):
        wall = h * 3 / 4.4; yb = h / 2
        shutters_window(sh, 0, yb - wall * .5, w * .26, wall * .3, "b", "m"); flowerbox(sh, 0, yb - wall * .33, w * .38, "myp")
        sh.circle_r(0, yb - wall - (h - wall) * .35, w * .08, "y")
    elif s == "back":
        window(sh, -w * .2, -h * .1, w * .2, h * .3, "b"); door(sh, w * .2, h / 2, w * .16, h * .55, "p", glass=False)
        x, y = -w * .2, h * .35  # gieter
        sh.region(f"M{f(x - w * .07)} {f(y - h * .1)}H{f(x + w * .05)}V{f(y + h * .1)}H{f(x - w * .07)}Z", "g")
        sh.poly_r([(x + w * .05, y), (x + w * .16, y - h * .14), (x + w * .17, y - h * .12), (x + w * .05, y + h * .06)], "g")
        sh.line(f"M{f(x - w * .07)} {f(y - h * .06)}q{f(-w * .06)} {f(h * .06)} 0 {f(h * .12)}", "l", "stroke-width:1")
bouwplaat("bouwplaat-bloemist", "Bouwplaat: bloemist", "Een bloemenwinkel met emmers vol bloemen en een dakkapel.", Part(house_x(4, 3, 3, 4.4),
          lambda F: "-" if side(F) == "bottom" else "w" if side(F).startswith("roof") else "b", bloemist, FULL),
          "beroepen", "6-9", 2, 35, ["De kant met het bord BLOEMIST is de voorkant; het dakvlak met het raampje (de dakkapel) hoort erboven."])

# --- boekwinkel ---
BOEK = profile_y([(0, 0), (3.4, 0), (3.4, 3.2), (2.9, 4.4), (.5, 4.4), (0, 3.2)], 3)
def boekwinkel(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("front", "back"):
        wall = h * 3.2 / 4.4; yb = h / 2; yt = yb - wall; top = -h / 2
        sh.rect_r(-w / 2, yt - h * .015, w, h * .03, "z")
        if s == "front":
            sign(sh, 0, yt + wall * .12, w * .56, wall * .14, "BOEKEN")
            x0, x1 = -w * .44, w * .1
            sh.rect_r(x0, yt + wall * .26, x1 - x0, wall * .5, "b")
            for k in range(2): books(sh, x0 + 1, x1 - 1, yt + wall * (.49 + k * .25), wall * .18)
            door(sh, w * .28, yb, w * .2, wall * .6, "n")
            arch_window(sh, 0, yt - h * .04, w * .22, (yt - top) * .7, "b", False)
            sh.line(f"M{f(-w * .07)} {f(yt - h * .12)}Q{f(-w * .035)} {f(yt - h * .15)} 0 {f(yt - h * .12)}Q{f(w * .035)} {f(yt - h * .15)} {f(w * .07)} {f(yt - h * .12)}M0 {f(yt - h * .12)}V{f(yt - h * .2)}", "l", "stroke-width:.8")
        else:
            window(sh, -w * .22, yt + wall * .4, w * .2, wall * .3, "b"); window(sh, w * .22, yt + wall * .4, w * .2, wall * .3, "b")
            sh.rect_r(-w * .1, yb - wall * .25, w * .2, wall * .25, "-", 1); text_fit(sh, 0, yb - wall * .14, "lees!", w * .18, wall * .1)
            window(sh, 0, (top + yt) / 2, w * .18, (yt - top) * .45, "b")
    elif s in ("left", "right"):
        sh.rect_r(-w * .3, -h * .3, w * .6, h * .42, "b")
        books(sh, -w * .3 + 1, w * .3 - 1, -h * .1, h * .16, "ponr"); books(sh, -w * .3 + 1, w * .3 - 1, h * .1, h * .16, "gyt")
        sh.rect_r(-w * .36, h * .14, w * .72, h * .06, "w")
    elif s.startswith("roof"):
        tiles(sh, F, F.h / 3)
bouwplaat("bouwplaat-boekwinkel", "Bouwplaat: boekwinkel", "Een winkel vol boeken, met een dak als een hoge hoed.", Part(BOEK,
          lambda F: "-" if side(F) == "bottom" else "z" if F.n[2] > .3 else "t", boekwinkel, FULL),
          "beroepen", "6-9", 2, 35, ["De kant met het bord BOEKEN is de voorkant. Het dak heeft twee schuine kanten en een plat stuk bovenop."])

# --- school ---
def kidsdrawing(sh, k, x, y, r):
    if k == 0:
        sh.circle_r(x, y, r * .45, "y")
        sh.line("".join(f"M{f(x + math.cos(a) * r * .6)} {f(y + math.sin(a) * r * .6)}L{f(x + math.cos(a) * r * .9)} {f(y + math.sin(a) * r * .9)}" for a in [j * math.pi / 4 for j in range(8)]), "l", "stroke-width:.6")
    elif k == 1: sh.region(heart_path(x, y - r * .4, r * .9), "r")
    elif k == 2: flower(sh, x, y - r * .2, r * .6, "m", "y", r * .6)
    else: sh.region(star_path(x, y, r * .85, r * .36), "y")
def school(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sign(sh, 0, -h * .34, w * .26, h * .13, "SCHOOL")
        sh.rect_r(-w * .08, -h * .22, w * .16, h * .72, "g"); sh.seg(0, -h * .22, 0, h / 2)
        for k in (-1, 1): sh.rect_r(k * w * .04 - w * .025, -h * .15, w * .05, h * .25, "b"); sh.dot(k * w * .012, h * .2, .7)
        for k, x in enumerate((-w * .37, -w * .2, w * .2, w * .37)):
            sh.rect_r(x - w * .065, -h * .22, w * .13, h * .44, "b"); sh.seg(x - w * .065, h * .02, x + w * .065, h * .02, "l", "stroke-width:.6")
            sh.rect_r(x - w * .045, -h * .19, w * .09, h * .18, "-"); kidsdrawing(sh, k, x, -h * .1, h * .08)
        sh.rect_r(-w / 2, h * .42, w, h * .08, "z")
    elif s == "roof_front":
        tiles(sh, F, F.h / 4); clock(sh, 0, -h * .02, h * .22)
    elif s == "roof_back":
        tiles(sh, F, F.h / 4)
    elif s in ("left", "right"):
        wall = h * 3 / 4.6; yb = h / 2
        window(sh, 0, yb - wall * .55, w * .3, wall * .4, "b")
        sh.circle_r(0, yb - wall - (h - wall) * .35, w * .09, "y")
        if s == "right":  # fietsenrek met fiets
            y = yb - wall * .12; r = wall * .1
            for x in (-w * .18, w * .14): sh.circle_line(x, y, r, "l", "stroke-width:.9")
            sh.line(f"M{f(-w * .18)} {f(y)}L{f(-w * .06)} {f(y - r * 1.2)}H{f(w * .1)}L{f(w * .14)} {f(y)}M{f(-w * .06)} {f(y - r * 1.2)}L{f(-w * .02)} {f(y)}L{f(w * .1)} {f(y - r * 1.2)}M{f(-w * .09)} {f(y - r * 1.5)}h{f(w * .07)}M{f(w * .1)} {f(y - r * 1.2)}l{f(-w * .02)} {f(-r * .5)}h{f(w * .05)}", "l", "stroke-width:.8")
    elif s == "back":
        for x in (-w * .3, -w * .1, w * .1, w * .3): window(sh, x, -h * .15, w * .1, h * .35, "b")
        sh.line("".join(f"M{f(-w / 2 + .6 + k * w / 16)} {f(h / 2)}V{f(h * .25)}" for k in range(16)) + f"M{f(-w / 2 + .6)} {f(h * .32)}H{f(w / 2 - .6)}", "l", "stroke-width:.7")
        sh.circle_r(w * .12, h * .38, h * .09, "r"); sh.line(f"M{f(w * .12 - h * .09)} {f(h * .38)}Q{f(w * .12)} {f(h * .32)} {f(w * .12 + h * .09)} {f(h * .38)}", "l", "stroke-width:.6")
bouwplaat("bouwplaat-school", "Bouwplaat: school", "Een dorpsschool met tekeningen achter de ramen.", Part(house_x(6, 3, 3, 4.6),
          lambda F: "-" if side(F) == "bottom" else "r" if side(F).startswith("roof") else "o", school, FULL),
          "leren", "6-9", 2, 35, ["De lange kant met de deur en het bord SCHOOL is de voorkant; het dakvlak met de klok hoort erboven."], holiday="school")

# --- ziekenhuis ---
def hsign(sh, x, y, r):
    sh.rect_r(x - r, y - r, 2 * r, 2 * r, "n", r * .2); sh.rect_r(x - r * .55, y - r * .6, r * .3, r * 1.2, "-"); sh.rect_r(x + r * .25, y - r * .6, r * .3, r * 1.2, "-"); sh.rect_r(x - r * .25, y - r * .15, r * .5, r * .3, "-")
def grid_windows(sh, x0, x1, y0, y1, cols, rows, code="b"):
    cw, rh = (x1 - x0) / cols, (y1 - y0) / rows
    for i in range(cols):
        for j in range(rows): window(sh, x0 + (i + .5) * cw, y0 + (j + .5) * rh, cw * .6, rh * .6, code)
def ziekenhuis(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sign(sh, 0, -h * .42, w * .6, h * .09, "ZIEKENHUIS")
        grid_windows(sh, -w * .46, w * .46, -h * .34, h * .1, 4, 2)
        sh.rect_r(-w * .3, h * .14, w * .6, h * .05, "z")
        sh.rect_r(-w * .18, h * .19, w * .36, h * .31, "b"); sh.seg(0, h * .19, 0, h / 2)
        for k in (-1, 1): sh.seg(k * w * .03, h * .33, k * w * .07, h * .33, "l", "stroke-width:.8")
        hsign(sh, w * .36, h * .3, w * .07); hsign(sh, -w * .36, h * .3, w * .07)
    elif s == "top":
        sh.circle_r(0, 0, min(w, h) * .38, "z"); sh.circle_r(0, 0, min(w, h) * .3, "-")
        hsign(sh, 0, 0, min(w, h) * .16)
    elif s in ("left", "right"):
        grid_windows(sh, -w * .44, w * .44, -h * .42, h * .2, 2, 3)
        if s == "left": hsign(sh, 0, h * .34, w * .1)
        else: door(sh, 0, h / 2, w * .2, h * .22, "n")
    elif s == "back":
        grid_windows(sh, -w * .46, w * .46, -h * .44, h * .0, 4, 2)
        sign(sh, 0, h * .08, w * .46, h * .08, "AMBULANCE")
        sh.rect_r(-w * .25, h * .16, w * .5, h * .34, "z")
        sh.line("".join(f"M{f(-w * .25)} {f(h * .16 + k * h * .068)}H{f(w * .25)}" for k in range(1, 5)), "l", "stroke-width:.6")
bouwplaat("bouwplaat-ziekenhuis", "Bouwplaat: ziekenhuis", "Met een landingsplek voor de helikopter op het dak.", Part(box_model(4.4, 3, 4.2),
          lambda F: "-" if side(F) == "bottom" else "z" if side(F) == "top" else "b", ziekenhuis, FULL),
          "beroepen", "6-9", 2, 30, ["De kant met het bord ZIEKENHUIS en de glazen deuren is de voorkant. Het vlak met de cirkel en de H is het platte dak."])

# --- brandweerkazerne met oefentoren ---
def kazerne(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sign(sh, 0, -h * .38, w * .5, h * .14, "BRANDWEER")
        for x in (-w * .26, w * .26):
            sh.rect_r(x - w * .2, -h * .2, w * .4, h * .7, "r")
            for k in range(1, 6): sh.seg(x - w * .2, -h * .2 + k * h * .7 / 6, x + w * .2, -h * .2 + k * h * .7 / 6, "l", "stroke-width:.6")
            for k in range(4): sh.rect_r(x - w * .17 + k * w * .09, -h * .2 + h * .7 / 6 * 1.2, w * .07, h * .7 / 6 * .6, "b")
        sh.circle_r(0, -h * .1, w * .025, "b")
        sh.line(f"M{f(-w * .45)} {f(-h * .45)}L{f(-w * .38)} {f(-h * .45)}", "l", "stroke-width:.6")
    elif s in ("left", "right"):
        window(sh, -w * .2, -h * .1, w * .2, h * .3, "b")
        x, y, r = w * .2, h * .1, h * .2  # slanghaspel
        sh.circle_r(x, y, r, "r"); sh.circle_r(x, y, r * .3, "z")
        sh.line(f"M{f(x - r * .55)} {f(y)}A{f(r * .55)} {f(r * .55)} 0 1 1 {f(x)} {f(y + r * .55)}A{f(r * .75)} {f(r * .75)} 0 0 1 {f(x - r * .75)} {f(y)}", "l", "stroke-width:.7")
        sh.line(f"M{f(x)} {f(y + r)}V{f(h / 2)}", "l", "stroke-width:1.2")
    elif s == "back":
        door(sh, -w * .3, h / 2, w * .12, h * .55, "r")
        for x in (-w * .05, w * .15, w * .35): window(sh, x, -h * .1, w * .12, h * .3, "b")
    elif s == "top":
        sh.rect_r(w * .3, -h * .2, w * .1, h * .25, "r", 1); sh.text(w * .35, h * .2, "sirene", max(4.5, w * .04), cls="tip")
def oefentoren(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "top":
        sh.rect_line(-w * .35, -h * .35, w * .7, h * .7, "l", 0, "stroke-width:.8"); return
    if s == "bottom": return
    for k in range(4): window(sh, 0, -h * .38 + k * h * .19, w * .4, h * .1, "b", False)
    if s == "front": door(sh, 0, h / 2, w * .4, h * .14, "r", glass=False)
    if s == "right":
        sh.line(f"M{f(-w * .38)} {f(-h * .46)}V{f(h / 2)}M{f(-w * .18)} {f(-h * .46)}V{f(h / 2)}" + "".join(f"M{f(-w * .38)} {f(-h * .44 + k * h * .04)}H{f(-w * .18)}" for k in range(24)), "l", "stroke-width:.5")
bouwplaat("bouwplaat-brandweerkazerne", "Bouwplaat: brandweerkazerne", "Een kazerne met twee grote deuren en een losse oefentoren.",
          [Part(box_model(5, 3, 3.2), lambda F: "-" if side(F) == "bottom" else "z" if side(F) == "top" else "w", kazerne, (8, 36, 184, 150)),
           Part(box_model(1.3, 1.3, 5.6), lambda F: "-" if side(F) == "bottom" else "z" if side(F) == "top" else "w", oefentoren, (8, 194, 184, 70), upright=None)],
          "beroepen", "6-9", 2, 40,
          ["Maak eerst de kazerne: de kant met de twee grote rode deuren is de voorkant.",
           "Maak dan de hoge oefentoren: vouw de vier lange muren rond en sluit hem boven en onder.",
           "Plak de flapjes vast. Zet de toren naast de kazerne, met de kant met de ladder naar buiten. Daar oefent de brandweer met klimmen."],
          last="Laat alles goed drogen. Een brandweerauto uit een andere bouwplaat past mooi voor de deuren!")

# --- politiebureau ---
def politie(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sh.rect_r(-w / 2, -h * .12, w, h * .1, "n"); sh.rect_r(-w / 2, -h * .02, w, h * .03, "o")
        sign(sh, 0, -h * .3, w * .4, h * .14, "POLITIE")
        door(sh, 0, h / 2, w * .16, h * .42, "n")
        sh.rect_r(-w * .05, -h * .03 + .3, w * .1, h * .05, "b", .8)
        for x in (-w * .32, w * .32): window(sh, x, h * .22, w * .2, h * .3, "b")
        for x in (-w * .32, w * .32): window(sh, x, -h * .34, w * .14, h * .18, "b")
    elif s in ("left", "right"):
        sh.rect_r(-w / 2, -h * .12, w, h * .1, "n"); sh.rect_r(-w / 2, -h * .02, w, h * .03, "o")
        window(sh, 0, h * .22, w * .3, h * .3, "b"); window(sh, 0, -h * .34, w * .2, h * .18, "b")
    elif s == "back":
        sh.rect_r(-w / 2, -h * .12, w, h * .1, "n"); sh.rect_r(-w / 2, -h * .02, w, h * .03, "o")
        for x in (-w * .3, 0, w * .3): window(sh, x, -h * .34, w * .14, h * .18, "b")
        door(sh, w * .3, h / 2, w * .14, h * .4, "n", glass=False)
        for x in (-w * .3, 0): window(sh, x, h * .22, w * .16, h * .3, "b")
    elif s.startswith("roof"):
        tiles(sh, F, F.h / 4)
        if s == "roof_front": sh.rect_r(-w * .06, -h * .2, w * .12, h * .25, "b", 1)
bouwplaat("bouwplaat-politiebureau", "Bouwplaat: politiebureau", "Met een blauwe band, een lamp en een schilddak.", Part(hipped(4.6, 3, 3, 4.4, 1.3),
          lambda F: "-" if side(F) == "bottom" else "z" if side(F).startswith("roof") else "y", politie, FULL),
          "beroepen", "6-9", 2, 35, ["De kant met het bord POLITIE is de voorkant. Het dak heeft vier schuine vlakken: twee grote en twee driehoekjes aan de zijkant."])

# ======================= dierendoosjes =======================
DOOS_STEPS = ["Kijk eerst waar het gezicht zit: dat is de voorkant. Het vlak zonder tekening is de onderkant."]
def doos(slug, name, sub, model, base, draw, cat, holiday=None, extra=None, bottom="-", age="4-6", diff=1):
    codes = lambda F: bottom if side(F) == "bottom" else base
    bouwplaat(slug, name, sub, Part(model, codes, draw, FULL), cat, age, diff, 25, DOOS_STEPS + (extra or []), holiday)

def paws(sh, w, h, code, xs=(-.3, .3)):
    for x in xs:
        sh.rect_r(w * x - w * .1, h * .28, w * .2, h * .22, code)
        sh.line(f"M{f(w * x - w * .035)} {f(h / 2)}v{f(-h * .06)}M{f(w * x + w * .035)} {f(h / 2)}v{f(-h * .06)}", "l", "stroke-width:.7")

def hond(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sh.ellipse_r(-w * .2, -h * .05, w * .1, h * .1, "-"); sh.circle_r(-w * .2, -h * .04, w * .05, "x"); sh.circle_r(w * .2, -h * .04, w * .05, "x")
        for k in (-1, 1):
            sh.region(f"M{f(k * w * .3)} {f(-h * .48)}C{f(k * w * .52)} {f(-h * .48)} {f(k * w * .5)} {f(-h * .1)} {f(k * w * .44)} {f(h * .12)}C{f(k * w * .38)} {f(h * .2)} {f(k * w * .3)} {f(h * .1)} {f(k * w * .3)} {f(-h * .1)}Z", "x")
        sh.ellipse_r(0, h * .1, w * .2, h * .14, "y")
        sh.ellipse_r(0, h * .04, w * .08, h * .055, "x")
        sh.line(f"M0 {f(h * .09)}V{f(h * .15)}M{f(-w * .1)} {f(h * .14)}Q{f(-w * .05)} {f(h * .2)} 0 {f(h * .15)}Q{f(w * .05)} {f(h * .2)} {f(w * .1)} {f(h * .14)}", "l", "stroke-width:.9")
        sh.region(f"M{f(-w * .05)} {f(h * .175)}Q{f(-w * .05)} {f(h * .27)} 0 {f(h * .27)}Q{f(w * .05)} {f(h * .27)} {f(w * .05)} {f(h * .175)}Z", "m")
        sh.rect_r(-w / 2, h * .34, w, h * .07, "r")
        sh.region(f"M{f(-w * .07)} {f(h * .42)}a{f(w * .025)} {f(w * .025)} 0 1 1 {f(w * .02)} {f(-h * .02)}h{f(w * .1)}a{f(w * .025)} {f(w * .025)} 0 1 1 {f(w * .02)} {f(h * .02)}a{f(w * .025)} {f(w * .025)} 0 1 1 {f(-w * .02)} {f(h * .02)}h{f(-w * .1)}a{f(w * .025)} {f(w * .025)} 0 1 1 {f(-w * .02)} {f(-h * .02)}Z", "y")
    elif s in ("left", "right"):
        k = 1 if s == "right" else -1
        sh.ellipse_r(k * w * .1, -h * .1, w * .2, h * .16, "y")
        paws(sh, w, h, "y")
    elif s == "back":
        sh.region(f"M{f(-w * .08)} {f(h * .2)}C{f(-w * .08)} {f(-h * .1)} {f(w * .12)} {f(-h * .2)} {f(w * .1)} {f(-h * .42)}C{f(w * .3)} {f(-h * .3)} {f(w * .14)} {f(h * .0)} {f(w * .08)} {f(h * .2)}Z", "w")
        sh.line(f"M{f(w * .2)} {f(-h * .42)}l{f(w * .06)} {f(-h * .04)}M{f(w * .24)} {f(-h * .34)}l{f(w * .06)} {f(-h * .02)}", "l", "stroke-width:.7")
        paws(sh, w, h, "y")
    elif s == "top":
        sh.ellipse_r(-w * .15, -h * .1, w * .18, h * .14, "y"); sh.ellipse_r(w * .22, h * .2, w * .1, h * .08, "y")
doos("dierendoosje-hond", "Bouwplaat: hondendoosje", "Een hond met flaporen en een rode halsband.", box_model(3, 3, 3), "w", hond, "dieren",
     extra=["Het vlak met de kwispelstaart is de achterkant."])

def konijn(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        for k in (-1, 1):
            sh.ellipse_r(k * w * .17, -h * .25, w * .1, h * .23, "z"); sh.ellipse_r(k * w * .17, -h * .24, w * .05, h * .17, "k")
        sh.ellipse_r(0, h * .18, w * .38, h * .3, "z")
        for k in (-1, 1): sh.circle_r(k * w * .15, h * .1, w * .05, "x"); sh.circle_r(k * w * .15 + w * .015, h * .08, w * .015, "-")
        sh.poly_r([(-w * .045, h * .2), (w * .045, h * .2), (0, h * .25)], "k")
        sh.line(f"M0 {f(h * .25)}V{f(h * .3)}M{f(-w * .07)} {f(h * .3)}Q{f(-w * .035)} {f(h * .34)} 0 {f(h * .3)}Q{f(w * .035)} {f(h * .34)} {f(w * .07)} {f(h * .3)}", "l", "stroke-width:.9")
        sh.rect_r(-w * .04, h * .315, w * .08, h * .06, "-")
        sh.seg(0, h * .315, 0, h * .375, "l", "stroke-width:.5")
        sh.line("".join(f"M{f(k * w * .1)} {f(h * (.24 + j * .03))}L{f(k * w * .34)} {f(h * (.2 + j * .06))}" for k in (-1, 1) for j in (0, 1)), "l", "stroke-width:.6")
    elif s in ("left", "right"):
        k = 1 if s == "right" else -1
        sh.ellipse_r(k * w * .12, h * .38, w * .3, h * .1, "z"); sh.ellipse_r(-k * w * .25, h * .42, w * .1, h * .07, "z")
        sh.line(f"M{f(k * w * .3)} {f(h * .38)}l{f(k * w * .1)} 0M{f(k * w * .3)} {f(h * .41)}l{f(k * w * .1)} {f(h * .01)}", "l", "stroke-width:.6")
    elif s == "back":
        for (x, y, r) in ((0, h * .22, .16), (-w * .1, h * .14, .1), (w * .1, h * .14, .1), (-w * .12, h * .28, .09), (w * .12, h * .28, .09)): sh.circle_r(x, y, w * r, "-")
    elif s == "top":
        x, y = 0, 0  # wortel
        sh.region(f"M{f(x - w * .3)} {f(y - h * .06)}Q{f(x + w * .25)} {f(y - h * .08)} {f(x + w * .3)} {f(y)}Q{f(x + w * .25)} {f(y + h * .08)} {f(x - w * .3)} {f(y + h * .06)}Z", "o")
        sh.line(f"M{f(x + w * .3)} {f(y)}l{f(w * .1)} {f(-h * .1)}M{f(x + w * .3)} {f(y)}l{f(w * .13)} 0M{f(x + w * .3)} {f(y)}l{f(w * .1)} {f(h * .1)}", "l", "stroke-width:1")
        sh.line("".join(f"M{f(x - w * .2 + j * w * .12)} {f(y - h * .055)}v{f(h * .03)}" for j in range(4)), "l", "stroke-width:.6")
doos("dierendoosje-konijn", "Bouwplaat: konijnendoosje", "Een konijn met lange oren, een staartje en een wortel.", box_model(3, 2.6, 3.6), "-", konijn, "dieren",
     extra=["Het vlak met het pluizige staartje is de achterkant; de wortel ligt bovenop."])

def mane(sh, x, y, r, n=18, code="o"):
    sh.region("M" + " ".join(f"{'L' if k else ''}{f(x + math.cos(k * math.pi / n) * r * (1 if k % 2 == 0 else .82))} {f(y + math.sin(k * math.pi / n) * r * (1 if k % 2 == 0 else .82))}" for k in range(2 * n)) + "Z", code)
def leeuw(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        mane(sh, 0, 0, w * .47)
        for k in (-1, 1): sh.circle_r(k * w * .22, -h * .24, w * .08, "y"); sh.circle_r(k * w * .22, -h * .24, w * .04, "w")
        sh.circle_r(0, h * .02, w * .3, "y")
        for k in (-1, 1): sh.circle_r(k * w * .11, -h * .06, w * .035, "x")
        sh.ellipse_r(0, h * .14, w * .12, h * .08, "-")
        sh.poly_r([(-w * .055, h * .07), (w * .055, h * .07), (0, h * .12)], "w")
        sh.line(f"M0 {f(h * .12)}V{f(h * .16)}M{f(-w * .07)} {f(h * .17)}Q{f(-w * .035)} {f(h * .21)} 0 {f(h * .16)}Q{f(w * .035)} {f(h * .21)} {f(w * .07)} {f(h * .17)}", "l", "stroke-width:.9")
        for k in (-1, 1):
            for j in range(3): sh.dot(k * w * (.05 + j * .03), h * (.13 + (j % 2) * .03), .45)
    elif s in ("left", "right"):
        k = 1 if s == "right" else -1
        sh.region(f"M{f(-k * w / 2)} {f(-h / 2)}" + "".join(f"L{f(-k * w * (.5 - (.12 if j % 2 else .2)))} {f(-h / 2 + (j + 1) * h / 8)}" for j in range(7)) + f"L{f(-k * w / 2)} {f(h / 2)}Z", "o")
        paws(sh, w, h, "y", (-.05 * k, .3 * k))
    elif s == "back":
        sh.line(f"M{f(-w * .05)} {f(h * .3)}C{f(-w * .3)} {f(h * .1)} {f(w * .3)} {f(-h * .1)} {f(w * .05)} {f(-h * .25)}", "l", "stroke-width:2")
        sh.region(f"M{f(w * .05)} {f(-h * .25)}l{f(-w * .08)} {f(-h * .06)}l{f(w * .04)} {f(-h * .1)}l{f(w * .06)} {f(h * .05)}l{f(w * .07)} {f(-h * .04)}l{f(-w * .01)} {f(h * .12)}Z", "w")
        paws(sh, w, h, "y")
    elif s == "top":
        sh.region(f"M{f(-w / 2)} {f(h / 2)}" + "".join(f"L{f(-w / 2 + (j + 1) * w / 10)} {f(h / 2 - (h * .3 if j % 2 == 0 else h * .2))}" for j in range(9)) + f"L{f(w / 2)} {f(h / 2)}Z", "o")
doos("dierendoosje-leeuw", "Bouwplaat: leeuwendoosje", "Een leeuw met een grote manen en een staart met een plukje.", box_model(3, 3, 3), "y", leeuw, "dieren",
     extra=["De manen lopen door op de zijkanten en de bovenkant: zet die stukken bij het gezicht."])

def panda(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        for k in (-1, 1): sh.circle_r(k * w * .36, -h * .36, w * .13, "x")
        for k in (-1, 1):
            sh.raw(f'<g transform="rotate({-25 * k} {f(k * w * .18)} {f(-h * .06)})">'); sh.ellipse_r(k * w * .18, -h * .06, w * .11, h * .15, "x"); sh.raw('</g>')
            sh.circle_r(k * w * .17, -h * .08, w * .045, "-"); sh.dot(k * w * .17, -h * .08, w * .02)
        sh.ellipse_r(0, h * .12, w * .07, h * .05, "x")
        sh.line(f"M0 {f(h * .17)}V{f(h * .22)}M{f(-w * .08)} {f(h * .22)}Q{f(-w * .04)} {f(h * .27)} 0 {f(h * .22)}Q{f(w * .04)} {f(h * .27)} {f(w * .08)} {f(h * .22)}", "l", "stroke-width:.9")
        sh.circle_r(-w * .3, h * .18, w * .05, "k"); sh.circle_r(w * .3, h * .18, w * .05, "k")
    elif s in ("left", "right"):
        paws(sh, w, h, "x")
        sh.line(f"M{f(w * .3)} {f(-h * .4)}V{f(h * .25)}M{f(w * .25)} {f(-h * .2)}H{f(w * .35)}M{f(w * .25)} {f(h * .02)}H{f(w * .35)}", "l", "stroke-width:1.6")
        for j in range(3): sh.region(leaf_path(w * .3 + w * .08, -h * .3 + j * h * .22, w * .1, h * .04, -20), "g")
    elif s == "back":
        paws(sh, w, h, "x"); sh.circle_r(0, h * .1, w * .07, "-")
    elif s == "top":
        for k in (-1, 1): sh.circle_r(k * w * .36, h * .36, w * .1, "x")
doos("dierendoosje-panda", "Bouwplaat: pandadoosje", "Een panda met zwarte oogvlekken en bamboe.", box_model(3, 3, 3), "-", panda, "dieren",
     extra=["Kleur de zwarte vlekken, oren en poten zwart en laat de rest wit."])

def vos(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        for k in (-1, 1):
            sh.poly_r([(k * w * .46, -h * .48), (k * w * .14, -h * .25), (k * w * .4, -h * .1)], "o")
            sh.poly_r([(k * w * .42, -h * .4), (k * w * .22, -h * .25), (k * w * .38, -h * .16)], "x")
        sh.region(f"M{f(-w * .48)} {f(-h * .02)}Q{f(-w * .25)} {f(h * .02)} 0 {f(h * .38)}Q{f(w * .25)} {f(h * .02)} {f(w * .48)} {f(-h * .02)}L{f(w * .48)} {f(h * .2)}Q{f(w * .2)} {f(h * .3)} 0 {f(h * .48)}Q{f(-w * .2)} {f(h * .3)} {f(-w * .48)} {f(h * .2)}Z", "-")
        for k in (-1, 1):
            sh.ellipse_r(k * w * .17, -h * .1, w * .07, h * .06, "y"); sh.circle_r(k * w * .17, -h * .1, w * .035, "x")
        sh.ellipse_r(0, h * .36, w * .06, h * .045, "x")
    elif s in ("left", "right"):
        paws(sh, w, h, "x")
    elif s == "back":
        sh.region(f"M{f(-w * .05)} {f(h * .45)}C{f(-w * .45)} {f(h * .2)} {f(-w * .35)} {f(-h * .3)} {f(w * .05)} {f(-h * .42)}C{f(w * .35)} {f(-h * .2)} {f(w * .35)} {f(h * .2)} {f(w * .05)} {f(h * .45)}Z", "o")
        sh.region(f"M{f(-w * .12)} {f(-h * .28)}C{f(-w * .05)} {f(-h * .38)} {f(w * .0)} {f(-h * .42)} {f(w * .05)} {f(-h * .42)}C{f(w * .15)} {f(-h * .36)} {f(w * .2)} {f(-h * .3)} {f(w * .22)} {f(-h * .24)}Q{f(w * .05)} {f(-h * .18)} {f(-w * .12)} {f(-h * .28)}Z", "-")
        paws(sh, w, h, "x")
    elif s == "top":
        for k in (-1, 1): sh.poly_r([(k * w * .46, h * .48), (k * w * .14, h * .48), (k * w * .38, h * .2)], "o")
doos("dierendoosje-vos", "Bouwplaat: vossendoosje", "Een rode vos met een witte snuit en een dikke staart.", box_model(3, 3, 3.2), "o", vos, "dieren",
     extra=["De grote pluimstaart met het witte puntje zit op de achterkant."])

# ======================= voertuigen =======================
def prof_map(F, prof):
    """Voor het zijvlak van een profiel_y-model: modelcoördinaten (x, z) -> lokale coördinaten."""
    xs = [p[0] for p in prof]; zs = [p[1] for p in prof]
    cx, cz = (min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2; k = 1 if F.n[1] < 0 else -1
    return (lambda mx: k * (mx - cx) * F.sc), (lambda mz: -(mz - cz) * F.sc), k
def mrect(sh, X, Y, x0, x1, z0, z1, code, rx=0):
    a, b = sorted((X(x0), X(x1))); sh.rect_r(a, Y(z1), b - a, Y(z0) - Y(z1), code, rx)
def bogie(sh, X, Y, xs, z, r):
    for mx in xs: wheel(sh, X(mx), Y(z), r, "z")

# --- tram ---
TRAMP = [(0, .3), (8, .3), (8, 2.8), (7.5, 3.3), (.5, 3.3), (0, 2.8)]
def tram(sh, F):
    w, h = F.w, F.h; x, y, z = F.n
    if abs(y) > .9:
        X, Y, k = prof_map(F, TRAMP); s = F.sc
        mrect(sh, X, Y, 0.05, 7.95, 1.3, 1.5, "r")
        for mx in (2.5, 3.4, 4.3, 5.2):
            mrect(sh, X, Y, mx - .38, mx + .38, 1.8, 2.8, "b", 1)
        for mx in (1.4, 6.6):
            mrect(sh, X, Y, mx - .4, mx + .4, .45, 2.85, "y"); mrect(sh, X, Y, mx - .3, mx - .03, 1.6, 2.7, "b"); mrect(sh, X, Y, mx + .03, mx + .3, 1.6, 2.7, "b")
            sh.seg(X(mx), Y(.45), X(mx), Y(2.85), "l", "stroke-width:.7")
        for mx in (.45, 7.55): mrect(sh, X, Y, mx - .3, mx + .3, 1.8, 2.8, "b", 1)
        bogie(sh, X, Y, (2.2, 2.9, 5.1, 5.8), .62, s * .27)
    elif abs(x) > .9:
        sh.rect_r(-w * .42, -h * .4, w * .84, h * .38, "b", 2)
        sh.rect_r(-w * .2, -h * .48, w * .4, h * .07, "-", 1); text_fit(sh, 0, -h * .445, "lijn 7", w * .36, h * .07)
        for kk in (-1, 1): sh.circle_r(kk * w * .3, h * .2, w * .06, "y")
        sh.rect_r(-w * .45, h * .36, w * .9, h * .07, "z")
        sh.rect_r(-w / 2, h * .04, w, h * .06, "r")
    elif z > .95:
        sh.rect_r(-w * .15, -h * .3, w * .3, h * .6, "z", 1)
        sh.line(f"M{f(-w * .1)} {f(-h * .05)}L{f(w * .02)} {f(-h * .4)}L{f(w * .14)} {f(-h * .05)}M{f(-w * .04)} {f(-h * .4)}H{f(w * .08)}", "l", "stroke-width:1.2")
bouwplaat("bouwplaat-tram", "Bouwplaat: tram", "Een stadstram met schuifdeuren en een stroomafnemer.", Part(profile_y(TRAMP, 2.4),
          lambda F: "-" if F.n[2] < -.95 else "z" if F.n[2] > .95 else "y", tram, FULL),
          "voertuigen", "6-9", 2, 35, ["De twee grote vlakken met ramen en wielen zijn de zijkanten. De tram heeft aan beide kanten een cabine met een lijnbordje.",
                                       "De stroomafnemer (de schaar op het dak) zit op het lange vlak bovenop."])

# --- vuilniswagen ---
VUILP = [(0, .4), (7, .4), (7, 3.6), (2.2, 3.6), (.3, 2.9), (0, 2.4)]
def vuilniswagen(sh, F):
    w, h = F.w, F.h; x, y, z = F.n
    if abs(y) > .9:
        X, Y, k = prof_map(F, VUILP); s = F.sc
        a, b = sorted((X(0), X(2.1)))
        sh.poly_r([(X(0), Y(.4)), (X(2.1), Y(.4)), (X(2.1), Y(3.56)), (X(.3), Y(2.9)), (X(0), Y(2.4))], "o")
        sh.poly_r([(X(.45), Y(2.1)), (X(1.8), Y(2.1)), (X(1.8), Y(3.3)), (X(.45), Y(2.82))], "b")
        sh.line(f"M{f(X(.35))} {f(Y(2.0))}H{f(X(1.95))}V{f(Y(.9))}H{f(X(.35))}Z", "l", "stroke-width:.7"); sh.seg(X(1.6), Y(1.7), X(1.8), Y(1.7), "l", "stroke-width:1.2")
        for mx in [2.7 + j * .55 for j in range(9)]: sh.seg(X(mx), Y(.9), X(mx), Y(3.4), "l", "stroke-width:.6")
        sh.rect_r(min(X(3.2), X(5.8)), Y(2.75), abs(X(5.8) - X(3.2)), s * .8, "-", 1.5); text_fit(sh, X(4.5), Y(2.35), "AFVAL", abs(X(5.6) - X(3.4)), s * .6)
        for j in range(4): sh.poly_r([(X(6.55 + (j % 2) * 0), Y(3.4 - j * .7)), (X(6.95), Y(3.4 - j * .7)), (X(6.95), Y(3.05 - j * .7)), (X(6.55), Y(3.05 - j * .7))], "y" if j % 2 == 0 else "-")
        for mx in (1.2, 4.6, 5.8): wheel(sh, X(mx), Y(.85), s * .42, "x")
    elif x < -.9:
        sh.rect_r(-w * .3, -h * .3, w * .6, h * .35, "z"); sh.line("".join(f"M{f(-w * .3)} {f(-h * .3 + j * h * .07)}H{f(w * .3)}" for j in range(1, 5)), "l", "stroke-width:.6")
        for kk in (-1, 1): sh.circle_r(kk * w * .4, -h * .1, w * .06, "y")
        sh.rect_r(-w * .48, h * .2, w * .96, h * .15, "z")
    elif x < 0 and z > .3:
        sh.rect_r(-w * .42, -h * .3, w * .84, h * .55, "b", 2)
    elif x > .9:
        sh.rect_r(-w * .4, -h * .42, w * .8, h * .5, "x", 2)
        sh.region(f"M{f(-w * .4)} {f(h * .08)}H{f(w * .4)}L{f(w * .3)} {f(h * .25)}H{f(-w * .3)}Z", "z")
        for kk in (-1, 1): sh.rect_r(kk * w * .4 - w * .05, h * .3, w * .1, h * .08, "r")
        for kk in (-1, 1): sh.rect_r(kk * w * .2 - w * .1, h * .42, w * .2, h * .05, "z")
    elif z > .95:
        sh.circle_r(-w * .42, 0, h * .12, "o")
        sh.line("".join(f"M{f(-w * .3 + j * w * .1)} {f(-h * .4)}V{f(h * .4)}" for j in range(8)), "l", "stroke-width:.6")
bouwplaat("bouwplaat-vuilniswagen", "Bouwplaat: vuilniswagen", "Een grote vuilniswagen met een laadbak en een oranje cabine.", Part(profile_y(VUILP, 2.6),
          lambda F: "-" if F.n[2] < -.95 else "g", vuilniswagen, FULL),
          "voertuigen", "6-9", 2, 35, ["De grote vlakken met de wielen zijn de zijkanten. Het schuine vlak met het grote raam is de voorruit van de cabine; achterin zit de opening van de laadbak."])

# --- treinwagons ---
PERSP = [(0, .3), (5.6, .3), (5.6, 2.5), (5.1, 3), (.5, 3), (0, 2.5)]
def buffers(sh, w, h, yb):
    for kk in (-1, 1): sh.rect_r(kk * w * .32 - w * .05, yb, w * .1, h * .05, "z"); sh.circle_r(kk * w * .32, yb + h * .03, w * .07, "z")
    sh.rect_r(-w * .04, yb - h * .02, w * .08, h * .08, "x")
def personenwagon(sh, F):
    w, h = F.w, F.h; x, y, z = F.n
    if abs(y) > .9:
        X, Y, k = prof_map(F, PERSP); s = F.sc
        for mx in (1.5, 2.3, 3.1, 3.9): mrect(sh, X, Y, mx - .32, mx + .32, 1.6, 2.5, "b", 1)
        for mx in (.55, 5.05): mrect(sh, X, Y, mx - .3, mx + .3, .5, 2.6, "y"); mrect(sh, X, Y, mx - .18, mx + .18, 1.8, 2.45, "b")
        mrect(sh, X, Y, .05, 5.55, 1.2, 1.35, "-")
        for mx in (1.3, 4.3): wheel(sh, X(mx), Y(.6), s * .28, "z", 6)
    elif abs(x) > .9:
        sh.rect_r(-w * .18, -h * .32, w * .36, h * .72, "y"); sh.rect_r(-w * .11, -h * .26, w * .22, h * .25, "b")
        buffers(sh, w, h, h * .38)
def goederenwagon(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("front", "back"):
        sh.line("".join(f"M{f(-w / 2 + j * w / 12)} {f(-h / 2)}V{f(h * .3)}" for j in range(1, 12)), "l", "stroke-width:.5")
        sh.rect_r(-w * .2, -h * .42, w * .4, h * .68, "r")
        sh.line(f"M{f(-w * .2)} {f(-h * .42)}L{f(w * .2)} {f(h * .26)}M{f(w * .2)} {f(-h * .42)}L{f(-w * .2)} {f(h * .26)}", "l", "stroke-width:.9")
        sh.rect_r(-w / 2, h * .3, w, h * .06, "x")
        for x in (-w * .3, w * .3): wheel(sh, x, h * .38, h * .11, "z", 6)
    elif s in ("left", "right"):
        sh.line("".join(f"M{f(-w / 2 + j * w / 6)} {f(-h / 2)}V{f(h * .3)}" for j in range(1, 6)), "l", "stroke-width:.5")
        buffers(sh, w, h, h * .34)
    elif s == "top":
        sh.line("".join(f"M{f(-w / 2 + j * w / 8)} {f(-h / 2)}V{f(h / 2)}" for j in range(1, 8)), "l", "stroke-width:.5")
bouwplaat("bouwplaat-treinwagons", "Bouwplaat: twee treinwagons", "Een personenwagon en een goederenwagon met schuifdeur.",
          [Part(profile_y(PERSP, 2.2), lambda F: "-" if F.n[2] < -.95 else "z" if F.n[2] > .3 else "g", personenwagon, (8, 36, 184, 116)),
           Part(box_model(4.6, 2.2, 2.7), lambda F: "-" if F.n[2] < -.95 else "z" if F.n[2] > .95 else "w", goederenwagon, (8, 160, 184, 106))],
          "voertuigen", "6-9", 2, 45,
          ["Maak eerst de personenwagon: de lange vlakken met de ramen zijn de zijkanten, het dak heeft twee schuine randjes.",
           "Maak daarna de goederenwagon: de zijkanten hebben een schuifdeur met een kruis.",
           "Plak alle flapjes vast. Zet de wagons achter elkaar, met de buffers tegen elkaar. Met een stukje touw of een paperclip tussen de haakjes rijden ze aan elkaar vast."],
          last="Laat alles goed drogen. Heb je de bouwplaat van de locomotief? Zet hem voorop: klaar is je trein!")

# --- onderzeeër (romp + losse toren) ---
ROMPP = [(0, 1.1), (.5, .45), (1.4, .15), (6.6, .15), (7.6, .5), (8.2, 1.1), (7.6, 1.7), (6.6, 2.05), (1.4, 2.05), (.5, 1.75)]
TORENP = [(0, 0), (1.6, 0), (1.6, 1.2), (.45, 1.2), (0, .8)]
def romp(sh, F):
    w, h = F.w, F.h; x, y, z = F.n
    if abs(y) > .9:
        X, Y, k = prof_map(F, ROMPP); s = F.sc
        mrect(sh, X, Y, 1.3, 6.8, 1.05, 1.2, "y")
        for mx in (1.5, 2.5, 3.5, 4.5, 5.5): sh.circle_r(X(mx), Y(1.6), s * .22, "b"); sh.circle_line(X(mx), Y(1.6), s * .3, "l", "stroke-width:.7")
        sh.poly_r([(X(6.9), Y(1.1)), (X(7.35), Y(1.65)), (X(7.6), Y(1.6)), (X(7.45), Y(1.1)), (X(7.6), Y(.6)), (X(7.35), Y(.55))], "z")
        for dz in (.15, -.15): sh.ellipse_r(X(7.86), Y(1.1 + dz), s * .06, s * .14, "y")
        sh.circle_r(X(7.86), Y(1.1), s * .05, "z")
        for mx, mz in ((7.5, .55), (7.5, 1.65)): sh.dot(X(mx), Y(mz), .6)
        sh.circle_r(X(.75), Y(.75), s * .12, "y"); sh.circle_r(X(1.05), Y(.62), s * .12, "y")
        for mx in (2.6, 4.2): sh.circle_line(X(mx), Y(.6), s * .18, "l", "stroke-width:.6")
    elif z > .95:
        sh.rect_line(-.8 * F.sc, -.4 * F.sc, 1.6 * F.sc, .8 * F.sc, "l", 0, "stroke-width:.6;stroke-dasharray:1.5 1.5")
        sh.text(0, 2, "toren", max(4.5, F.sc * .3), cls="tip")
        sh.circle_r(1.9 * F.sc, 0, .25 * F.sc, "z"); sh.circle_r(-1.9 * F.sc, 0, .25 * F.sc, "z")
def zeetoren(sh, F):
    w, h = F.w, F.h; x, y, z = F.n
    if abs(y) > .9:
        X, Y, k = prof_map(F, TORENP); s = F.sc
        for mx in (.6, 1.05): sh.circle_r(X(mx), Y(.75), s * .16, "b")
        sh.poly_r([(X(1.1), Y(.2)), (X(1.5), Y(.2)), (X(1.5), Y(.4)), (X(1.1), Y(.4))], "y")
    elif z > .95:
        sh.circle_r(w * .15, 0, min(w, h) * .3, "z"); sh.dot(w * .15, 0, .7)
        sh.rect_r(-w * .35, -h * .1, w * .08, h * .2, "x")
bouwplaat("bouwplaat-onderzeeer", "Bouwplaat: onderzeeër", "Een duikboot met ronde raampjes en een losse toren.",
          [Part(profile_y(ROMPP, 1.8), lambda F: "-" if F.n[2] < -.95 else "o", romp, (8, 36, 184, 160)),
           Part(profile_y(TORENP, .8), lambda F: "-" if F.n[2] < -.95 else "o", zeetoren, (8, 200, 184, 66), upright=None)],
          "zee", "9+", 3, 40,
          ["Maak eerst de romp: de twee grote vlakken met de ronde raampjes zijn de zijkanten. Vouw de smalle stroken er een voor een omheen.",
           "Maak daarna de kleine toren. De schuine kant is de voorkant, net als de punt van de romp.",
           "Plak de flapjes vast. Lijm de toren op het stippelvak 'toren' bovenop de romp, met de schuine kant naar de voorkant."],
          adult=False, last="Laat alles goed drogen. Met een touwtje aan de toren kun je de onderzeeër laten zweven, alsof hij door de zee vaart.")

# ======================= feest =======================
def label_tag(sh, x, y, w, h):
    sh.rect_r(x - w / 2, y - h / 2, w, h, "-", 1.5)
    fs = max(4.5, h * .2)
    sh.text(x - w * .44, y - h * .12, "Voor:", fs, "start", weight="700"); sh.seg(x - w * .05, y - h * .12, x + w * .44, y - h * .12, "l", "stroke-width:.5")
    sh.text(x - w * .44, y + h * .3, "Van:", fs, "start", weight="700"); sh.seg(x - w * .1, y + h * .3, x + w * .44, y + h * .3, "l", "stroke-width:.5")

# --- mijterdoosje (sinterklaas) ---
def pepernoot(sh, x, y, r):
    sh.circle_r(x, y, r, "w"); sh.line(f"M{f(x - r * .4)} {f(y - r * .2)}q{f(r * .3)} {f(-r * .3)} {f(r * .7)} 0", "l", "stroke-width:.5")
def mijter(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("front", "back"):
        wall = h * 3 / 5.4; yb = h / 2
        sh.rect_r(-w / 2, yb - h * .12, w, h * .1, "y")
        sh.poly_r(clip(F.poly, -w * .07, -h / 2 + h * .1, w * .07, yb - h * .12), "y")
        if s == "front":
            sh.region(f"M0 {f(-h * .05)}l{f(w * .14)} {f(h * .1)}l{f(-w * .14)} {f(h * .1)}l{f(-w * .14)} {f(-h * .1)}Z", "y")
            sh.region(f"M0 {f(h * .0)}l{f(w * .07)} {f(h * .05)}l{f(-w * .07)} {f(h * .05)}l{f(-w * .07)} {f(-h * .05)}Z", "r")
            for x in (-w * .32, w * .32): sh.circle_r(x, yb - h * .07, w * .03, "b")
        else:
            label_tag(sh, 0, yb - wall * .5, w * .7, wall * .34)
    elif s in ("left", "right"):
        sh.rect_r(-w / 2, h * .28, w, h * .17, "y")
        if s == "left":
            for (x, y) in ((-w * .25, -h * .2), (0, -h * .28), (w * .22, -h * .15), (-w * .1, -h * .02), (w * .15, h * .08), (-w * .3, h * .1)): pepernoot(sh, x, y, w * .07)
        else:  # schoen met wortel
            x, y = 0, h * .02
            sh.region(f"M{f(x - w * .26)} {f(y - h * .3)}H{f(x - w * .1)}L{f(x - w * .18)} {f(y - h * .05)}Z", "o")
            sh.line(f"M{f(x - w * .18)} {f(y - h * .3)}l{f(-w * .06)} {f(-h * .08)}M{f(x - w * .18)} {f(y - h * .3)}v{f(-h * .1)}M{f(x - w * .18)} {f(y - h * .3)}l{f(w * .06)} {f(-h * .08)}", "l", "stroke-width:.8")
            sh.region(f"M{f(x - w * .36)} {f(y + h * .2)}V{f(y - h * .14)}H{f(x - w * .02)}L{f(x + w * .04)} {f(y - h * .01)}Q{f(x + w * .36)} {f(y + h * .02)} {f(x + w * .38)} {f(y + h * .2)}Z", "w")
            sh.seg(x - w * .36, y + h * .14, x + w * .37, y + h * .14, "l", "stroke-width:.8")
    elif s.startswith("roof"):
        for (x, y) in ((-w * .2, h * .15), (w * .2, h * .05), (0, -h * .2)): sh.region(star_path(x, y, h * .06, h * .025), "y")
bouwplaat("surprise-mijterdoosje", "Bouwplaat: mijterdoosje", "Een surprisedoosje in de vorm van een mijter.", Part(house_y(3, 2.4, 3, 5.4),
          lambda F: "-" if side(F) == "bottom" else "r", mijter, FULL),
          "feest", "6-9", 2, 30, ["De kant met de gouden ruit is de voorkant; op de achterkant schrijf je voor wie het is. De twee schuine vlakken vormen samen de punt.",
                                  "Stop er een klein cadeautje of een paar pepernoten in voordat je het laatste vlak dichtplakt."], holiday="sinterklaas")

# --- kerstcadeau ---
def kerstcadeau(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("front", "back", "left", "right"):
        rng = random.Random(F.idx)
        for k in range(8):
            x = rng.uniform(-w * .42, w * .42); y = rng.uniform(-h * .42, h * .42)
            if abs(x) < w * .15: x += w * .28 if x > 0 else -w * .28
            if s == "front" and y > h * .05 and x < 0: continue
            if k % 2: snowflake(sh, x, y, w * .05)
            else: sh.region(star_path(x, y, w * .05, w * .022), "y")
        sh.rect_r(-w * .08, -h / 2, w * .16, h, "g")
        if s == "front": label_tag(sh, -w * .29, h * .25, w * .38, h * .3)
    elif s == "top":
        sh.rect_r(-w * .08, -h / 2, w * .16, h, "g"); sh.rect_r(-w / 2, -h * .08, w, h * .16, "g")
        for a in (30, 150, 210, 330):
            sh.raw(f'<g transform="rotate({a} 0 0)">'); sh.ellipse_r(w * .17, 0, w * .17, w * .08, "g"); sh.raw('</g>')
        sh.circle_r(0, 0, w * .07, "g")
bouwplaat("kerstcadeau-kubus", "Bouwplaat: kerstcadeautje", "Een kubus met een lint, een grote strik en sterren.", Part(box_model(3, 3, 3),
          lambda F: "-" if side(F) == "bottom" else "r", kerstcadeau, FULL),
          "feest", "4-6", 1, 25, ["Het vlak met de strik is de bovenkant. Schrijf op het kaartje voor wie het cadeautje is.",
                                  "Hang het met een touwtje in de kerstboom, of stop er een klein verrassinkje in."], holiday="kerst")

# --- vleermuisdoosje ---
def vleermuis(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        for k in (-1, 1):
            sh.poly_r([(k * w * .45, -h * .48), (k * w * .1, -h * .2), (k * w * .42, -h * .05)], "z")
            sh.poly_r([(k * w * .4, -h * .38), (k * w * .2, -h * .2), (k * w * .38, -h * .12)], "k")
        sh.ellipse_r(0, h * .08, w * .38, h * .3, "z")
        for k in (-1, 1): sh.circle_r(k * w * .15, -h * .0, w * .09, "y"); sh.circle_r(k * w * .15, h * .01, w * .04, "x")
        sh.region(f"M{f(-w * .05)} {f(h * .1)}Q0 {f(h * .06)} {f(w * .05)} {f(h * .1)}L0 {f(h * .14)}Z", "k")
        sh.line(f"M{f(-w * .14)} {f(h * .2)}Q0 {f(h * .28)} {f(w * .14)} {f(h * .2)}", "l", "stroke-width:1")
        for k in (-1, 1): sh.poly_r([(k * w * .1, h * .215), (k * w * .05, h * .23), (k * w * .075, h * .29)], "-")
    elif s in ("left", "right"):
        # gevouwen vleugel
        sh.region(f"M{f(-w * .3)} {f(-h * .4)}L{f(w * .3)} {f(-h * .4)}L{f(w * .32)} {f(h * .3)}Q{f(w * .2)} {f(h * .18)} {f(w * .1)} {f(h * .36)}Q{f(0)} {f(h * .22)} {f(-w * .1)} {f(h * .36)}Q{f(-w * .2)} {f(h * .18)} {f(-w * .32)} {f(h * .3)}Z", "p")
        sh.line(f"M{f(-w * .2)} {f(-h * .38)}L{f(-w * .1)} {f(h * .3)}M{f(w * .2)} {f(-h * .38)}L{f(w * .1)} {f(h * .3)}", "l", "stroke-width:.7")
    elif s == "back":
        sh.circle_r(w * .22, -h * .25, w * .14, "y"); sh.circle_r(w * .28, -h * .29, w * .12, "z")
        for (x, y) in ((-w * .3, -h * .3), (-w * .1, -h * .1), (w * .3, h * .1), (-w * .25, h * .15)): sh.region(star_path(x, y, w * .05, w * .022), "y")
        for k in (-1, 1): sh.rect_r(k * w * .12 - w * .05, h * .38, w * .1, h * .12, "z")
    elif s == "top":
        for k in (-1, 1): sh.line(f"M{f(k * w * .12)} {f(-h * .3)}v{f(-h * .15)}M{f(k * w * .12 - w * .04)} {f(-h * .45)}h{f(w * .08)}", "l", "stroke-width:1.2")
        sh.text(0, h * .15, "hangen", max(4.5, w * .07), cls="tip"); sh.text(0, h * .15 + 6, "aan de pootjes", max(4.5, w * .07), cls="tip")
doos("vleermuisdoosje", "Bouwplaat: vleermuisdoosje", "Een vleermuis met grote oren en scherpe tandjes.", box_model(3, 3, 3), "x", vleermuis, "dieren", holiday="halloween",
     extra=["De vleugels zitten op de zijkanten. Kleur het lijf zwart of donkerpaars en laat de ogen geel.",
            "Wil je hem ondersteboven ophangen, zoals een echte vleermuis? Prik dan een touwtje door de bovenkant, bij de pootjes."])

# ======================= sterveelvlakken (niet convex) =======================
def stellate(verts, faces, k):
    """Zet op elk vlak een puntige piramide met de top op afstand k van het midden."""
    V = list(verts); F = []
    for fc in faces:
        c = tuple(sum(verts[i][j] for i in fc) / len(fc) for j in range(3)); n = ph.norm(c)
        V.append(tuple(x / n * k for x in c)); a = len(V) - 1
        for i in range(len(fc)): F.append([fc[i], fc[(i + 1) % len(fc)], a])
    return V, F
def dodecahedron():
    p = (1 + 5 ** .5) / 2
    v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    for a in (-1, 1):
        for b in (-1, 1): v += [(0, a / p, b * p), (a / p, b * p, 0), (b * p, 0, a / p)]
    return ph.hull_faces(v)
def octahedron():
    return ph.hull_faces([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)])

def star_plate(slug, name, sub, base, kfac, t, spike_code, age, diff, minutes, steps_mid, box=(8, 34, 184, 228)):
    """Uitslag van een sterveelvlak. t kiest de boom (gevonden met een zoektocht over vele bomen; zie batch-notities).
    Randen tussen twee punten (beide hoekpunten op het grondlichaam) zijn dalvouwen: die vouw je naar voren."""
    bv, bf = base; nb = len(bv)
    r = ph.norm(tuple(sum(bv[i][j] for i in bf[0]) / len(bf[0]) for j in range(3)))
    V, Fc = stellate(bv, bf, r * kfac)
    args = dict(root=t % len(Fc), dfs=t % 2 == 0)
    polys, tabs, folds, cuts = ph.layout(V, Fc, depth=.17, rng=random.Random(random.Random(t).random()), **args)
    pos, tree, _ = ph.unfold(V, Fc, rng=random.Random(random.Random(t).random()), **args)
    valley = [(pos[p][a], pos[p][b]) for p, ch, ed in tree for a, b in [tuple(ed)] if a < nb and b < nb]
    allp = [q for poly in polys + tabs for q in poly]
    best = None
    for a in range(0, 180):
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        xs = [c * x - s_ * y for x, y in allp]; ys = [s_ * x + c * y for x, y in allp]
        sc = min(box[2] / (max(xs) - min(xs)), box[3] / (max(ys) - min(ys)))
        if best is None or sc > best[0]: best = (sc, a, min(xs), max(xs), min(ys), max(ys))
    sc, a, mnx, mxx, mny, mxy = best; c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
    ox = box[0] + (box[2] - (mxx - mnx) * sc) / 2; oy = box[1] + (box[3] - (mxy - mny) * sc) / 2
    T = lambda p: (ox + (c * p[0] - s_ * p[1] - mnx) * sc, oy + (s_ * p[0] + c * p[1] - mny) * sc)
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16); sh.text(100, 27, sub, 6.5)
    for fi, poly in enumerate(polys):
        sh.raw(f'<path class="r" style="stroke:none" d="{P([T(q) for q in poly])}"/>', spike_code(V[Fc[fi][2]]))
    for tp in tabs:
        d = "M" + " L".join(f"{f(T(q)[0])} {f(T(q)[1])}" for q in tp)
        sh.raw(f'<path class="glue" d="{d}Z"/>'); sh.line(d, "cut")
    same = lambda u, v: math.dist(u, v) < 1e-6
    nvalley = 0
    for p1, p2 in folds:
        if any(same(p1, a1) and same(p2, b1) or same(p1, b1) and same(p2, a1) for a1, b1 in valley):
            sh.seg(*T(p1), *T(p2), "fold", "stroke-dasharray:5 1.6 1 1.6;stroke-width:1"); nvalley += 1
        else: sh.seg(*T(p1), *T(p2), "fold")
    assert nvalley == len(valley)
    for p1, p2 in cuts: sh.seg(*T(p1), *T(p2), "cut")
    sh.legend(["cut", "fold", "glue"], 268)
    sh.seg(20, 274, 34, 274, "fold", "stroke-dasharray:5 1.6 1 1.6;stroke-width:1"); sh.tip(37, 276, "andersom vouwen: naar voren (tussen twee punten)")
    steps = ["Kleur de vlakken: alle driehoeken van één punt krijgen dezelfde kleur. Knip de uitslag heel precies uit langs de doorgetrokken lijnen; de grijze flapjes blijven eraan.",
             "Kras alle vouwlijnen eerst met een liniaal en een lege balpen. Vouw de gewone stippellijnen naar achteren, zodat de kleur buiten blijft. De streep-puntlijnen vouw je juist naar voren: daar zit een kuiltje tussen twee punten."] + steps_mid + [
             "Plak de flapjes één voor één vast, aan de binnenkant van het vlak ernaast. De laatste punten zijn lastig: druk ze van buitenaf aan met een potlood of pincet en laat de lijm even drogen."]
    write(OUT, slug, sh, {"category": "vormen", "age": age, "kind": "bouwplaat", "difficulty": diff, "minutes": minutes, "paperGsm": 160,
        "adultHelp": False, "holiday": None, "materials": MAT,
        "i18n": {"nl": {"name": name, "printNote": "Print op stevig papier (160 gram) en print op ware grootte: de vlakjes zijn klein.", "steps": steps}}})

star_plate("sterachtvlak", "Bouwplaat: sterachtvlak", "Twee viervlakken door elkaar heen: een ster met acht punten.", octahedron(), 3, 388,
           lambda a: "y" if a[0] * a[1] * a[2] > 0 else "n", "9+", 3, 50,
           ["De ster heeft acht punten van drie driehoeken. Vouw eerst elke punt dicht en plak hem vast; zo groeit de ster punt voor punt.",
            "Kleur je de gele en de blauwe punten om en om, dan zie je de twee viervlakken die door elkaar heen steken."])
SDC = {}
def sdc_code(a):
    key = tuple(round(abs(x), 3) for x in a); s = next((x for x in a if abs(x) > 1e-6), 1)
    key = tuple(round(x * (1 if s > 0 else -1), 3) for x in a)
    return SDC.setdefault(key, "royglp"[len(SDC) % 6])
star_plate("sterdodecaeder", "Bouwplaat: sterdodecaëder", "Een twaalfvlak met een punt op elk vlak: twaalf punten.", dodecahedron(), 5 ** .5, 14722,
           sdc_code, "12+", 3, 90,
           ["De ster heeft twaalf punten van vijf lange driehoeken. Punten die recht tegenover elkaar zitten krijgen dezelfde kleur.",
            "Werk punt voor punt: vouw de vijf driehoeken van een punt naar elkaar toe en plak het flapje vast voordat je aan de volgende begint."])
