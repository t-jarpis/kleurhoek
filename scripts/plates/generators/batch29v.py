"""Batch 29v: bouwplaten met een thema (uitslag uit polyhedra, tekeningen op de vlakken) en twee origami-vouwbladen.

Elke bouwplaat is een convex 3D-model (z omhoog, voorkant = -y). De uitslag komt uit polyhedra.layout; de
tekening op elk vlak wordt in een eigen assenstelsel getekend (x naar rechts, y naar beneden, gezien van buiten,
"onder" = naar de grond), zodat alles na het vouwen rechtop en aan de goede kant zit.
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

def build_net(sh, verts, faces, codes, box, draw_face, depth=.17, tries=150, style="--sw:1.2", upright=None):
    """Tekent de uitslag; draw_face(sh, F) tekent per vlak in lokale coördinaten (F.w, F.h, F.poly, F.n, F.c3).
    upright: normaal van het vlak dat rechtop moet staan (anders wordt de hele uitslag 180 graden gedraaid)."""
    sc, (polys, tabs, folds, cuts), kk = best_layout(verts, faces, box, depth, tries, upright)
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
    return sc

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

def bouwplaat(slug, name, sub, model, codes_fn, draw_face, cat, age, diff, minutes, steps_extra, holiday=None, box=(10, 34, 180, 232), depth=.17, tries=150, adult=None, note=None, upright=(0, -1, 0)):
    verts, faces = model
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16); sh.text(100, 27, sub, 6.5)
    tmp = Face()
    codes = []
    for fc in faces:
        V = [verts[v] for v in fc]; tmp.n = unit(cross(ph.sub(V[1], V[0]), ph.sub(V[2], V[0]))); tmp.z = sum(v[2] for v in V) / len(V)
        tmp.c3 = tuple(sum(v[k] for v in V) / len(V) for k in range(3))
        codes.append(codes_fn(tmp))
    build_net(sh, verts, faces, codes, box, draw_face, depth, tries, upright=upright)
    sh.legend(["cut", "fold", "glue"], 274)
    steps = ["Kleur alle vlakken en tekeningen. Knip de bouwplaat uit langs de doorgetrokken lijnen; de grijze flapjes blijven eraan.",
             "Vouw alle stippellijnen naar binnen, ook de flapjes: de tekening blijft aan de buitenkant. Met een liniaal en een lege balpen eerst krassen vouwt het strakker."] + steps_extra + [
             "Plak de flapjes één voor één vast aan de binnenkant van de rand ernaast. Het laatste vlak sluit je als een deksel: druk het even aan tot de lijm droog is."]
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "bouwplaat", "difficulty": diff, "minutes": minutes, "paperGsm": 160,
        "adultHelp": adult if adult is not None else age in ("4-6", "6-9"), "holiday": holiday, "materials": MAT,
        "i18n": {"nl": {"name": name, "printNote": note or "Op stevig papier (160 gram) wordt hij het mooist.", "steps": steps}}})

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

# ======================= bouwplaten =======================
# --- bakkerij ---
def bakkerij_codes(F):
    s = side(F)
    return {"top": "-", "bottom": "-", "roof_front": "r", "roof_back": "r"}.get(s, "y")
def bakkerij(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sh.rect_r(-w * .4, -h * .46, w * .8, h * .17, "-", 1.5)
        sh.text(0, -h * .46 + h * .17 / 2 + 2.2, "BAKKERIJ", max(5.5, h * .1), weight="800")
        n = 7; sw = w * .9 / n; y0 = -h * .25
        for k in range(n):
            x = -w * .45 + k * sw
            sh.region(f"M{f(x)} {f(y0)}H{f(x + sw)}V{f(y0 + h * .1)}A{f(sw / 2)} {f(sw / 2.6)} 0 0 1 {f(x)} {f(y0 + h * .1)}Z", "r" if k % 2 == 0 else "-")
        wx0, wx1, wy0, wy1 = -w * .42, w * .08, -h * .05, h * .3
        sh.rect_r(wx0, wy0, wx1 - wx0, wy1 - wy0, "b")
        sh.seg(wx0, wy0 + (wy1 - wy0) * .62, wx1, wy0 + (wy1 - wy0) * .62)
        ys = wy0 + (wy1 - wy0) * .62
        for k, cx in enumerate((wx0 + w * .1, wx0 + w * .25, wx0 + w * .4)):
            sh.ellipse_r(cx, ys - h * .05, w * .06, h * .05, "w")
            sh.line(f"M{f(cx - w * .03)} {f(ys - h * .08)}l{f(w * .015)} {f(h * .04)}M{f(cx)} {f(ys - h * .09)}l{f(w * .015)} {f(h * .04)}M{f(cx + w * .03)} {f(ys - h * .08)}l{f(w * .015)} {f(h * .04)}", "l", "stroke-width:.6")
        sh.circle_r(wx0 + w * .13, wy1 - h * .07, h * .045, "o"); sh.circle_r(wx0 + w * .3, wy1 - h * .07, h * .045, "m")
        sh.rect_r(w * .17, -h * .05, w * .24, h * .55, "g")
        sh.circle_r(w * .29, h * .07, w * .06, "b"); sh.dot(w * .21, h * .25, .9)
        sh.rect_r(-w * .44, h * .32, w * .5, h * .06, "z")
    elif s in ("roof_front", "roof_back"):
        tiles(sh, F, F.h / 5)
        if s == "roof_front": sh.rect_r(w * .22, -h * .45, w * .12, h * .45, "w")
    elif s in ("left", "right"):
        sh.circle_r(0, -h * .25, h * .1, "b"); sh.line(f"M{f(-h * .1)} {f(-h * .25)}H{f(h * .1)}M0 {f(-h * .35)}V{f(-h * .15)}")
        window(sh, 0, h * .15, w * .36, h * .2)
        sh.rect_r(-w * .24, h * .26, w * .48, h * .06, "w")
        for k in range(3): flower(sh, -w * .15 + k * w * .15, h * .24, w * .05, "rmo"[k], "y")
    elif s == "back":
        window(sh, -w * .2, -h * .05, w * .2, h * .32); window(sh, w * .2, -h * .05, w * .2, h * .32)
        sh.rect_r(-w * .35, h * .3, w * .7, h * .12, "w")
        sh.text(0, h * .3 + h * .09, "meel", max(4.5, h * .08), weight="700")

bouwplaat("bouwplaat-bakkerij", "Bouwplaat: bakkerij", "Een winkeltje met een luifel en verse broodjes in de etalage.", house_x(4, 3, 3, 4.4),
          bakkerij_codes, bakkerij, "beroepen", "6-9", 2, 35,
          ["De kant met de luifel en de deur is de voorkant; het dak met de schoorsteen hoort erboven."])

# --- schuur ---
def schuur_codes(F):
    s = side(F)
    return {"bottom": "-"}.get(s, "z" if s.startswith("roof") or s == "top" else "r")
def schuur(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("front", "back"):
        # wanden 2.6 hoog van 4.6: muurdeel is de onderste 2.6/4.6
        wall = h * 2.6 / 4.6; yb = h / 2; yt = yb - wall
        dw, dh = w * .46, wall * .78
        if s == "front":
            sh.rect_r(-dw / 2, yb - dh, dw, dh, "-")
            for x0 in (-dw / 2, 0):
                x1 = x0 + dw / 2; m = 1.6
                sh.rect_r(x0 + m, yb - dh + m, dw / 2 - 2 * m, dh - m, "w")
                sh.line(f"M{f(x0 + m)} {f(yb - dh + m)}L{f(x1 - m)} {f(yb)}M{f(x1 - m)} {f(yb - dh + m)}L{f(x0 + m)} {f(yb)}")
            sh.rect_r(-w * .11, yt - h * .26, w * .22, h * .2, "-"); sh.rect_r(-w * .11 + 1.4, yt - h * .26 + 1.4, w * .22 - 2.8, h * .2 - 1.4, "y")
            for k in range(4): sh.line(f"M{f(-w * .11 + 2 + k * 1.4)} {f(yt - h * .06)}l{f(.8 + k * .5)} {f(-h * .08 + k)}", "l", "stroke-width:.7")
            sh.region(f"M{f(-w * .16)} {f(yt - h * .27)}L0 {f(yt - h * .36)}L{f(w * .16)} {f(yt - h * .27)}Z", "-")
        else:
            window(sh, -w * .22, yb - wall * .55, w * .18, wall * .35, "b"); window(sh, w * .22, yb - wall * .55, w * .18, wall * .35, "b")
            sh.circle_r(0, yt - h * .2, h * .08, "-")
    elif s in ("left", "right"):
        for k in range(1, 6): sh.seg(-w / 2 + 1, -h / 2 + k * h / 6, w / 2 - 1, -h / 2 + k * h / 6, "l", "stroke-width:.5")
        for x in (-w * .28, 0, w * .28): window(sh, x, -h * .1, w * .14, h * .32, "b")
    elif s.startswith("roof"):
        for k in range(1, 4): sh.seg(-w / 2 + 1, -h / 2 + k * h / 4, w / 2 - 1, -h / 2 + k * h / 4, "l", "stroke-width:.6")
bouwplaat("bouwplaat-schuur", "Bouwplaat: rode schuur", "Een boerenschuur met een hooizolder en grote staldeuren.",
          profile_y([(0, 0), (4, 0), (4, 2.6), (3.3, 3.9), (2, 4.6), (.7, 3.9), (0, 2.6)], 4.5), schuur_codes, schuur, "boerderij", "6-9", 2, 35,
          ["De kant met de grote deuren is de voorkant. Het dak heeft vier schuine vlakken: vouw ze een voor een."])

# --- dierendoosjes ---
DOOS_STEPS = ["Kijk eerst waar het gezicht zit: dat is de voorkant. Het vlak zonder tekening is de onderkant."]
def doos(slug, name, sub, model, base, draw, cat, holiday=None, extra=None, bottom="-"):
    codes = lambda F: bottom if side(F) == "bottom" else base
    bouwplaat(slug, name, sub, model, codes, draw, cat, "4-6", 1, 25, DOOS_STEPS + (extra or []), holiday)

def kat(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sh.poly_r([(-w / 2 + 1, -h / 2 + 1), (-w * .14, -h / 2 + 1), (-w / 2 + 1, -h * .12)], "k")
        sh.poly_r([(w / 2 - 1, -h / 2 + 1), (w * .14, -h / 2 + 1), (w / 2 - 1, -h * .12)], "k")
        for x in (-w * .2, w * .2):
            sh.ellipse_r(x, -h * .1, w * .1, h * .12, "l"); sh.ellipse_r(x, -h * .1, w * .03, h * .09, "x")
        sh.poly_r([(-w * .06, h * .06), (w * .06, h * .06), (0, h * .13)], "k")
        sh.line(f"M0 {f(h * .13)}V{f(h * .18)}M{f(-w * .1)} {f(h * .2)}Q{f(-w * .05)} {f(h * .25)} 0 {f(h * .18)}Q{f(w * .05)} {f(h * .25)} {f(w * .1)} {f(h * .2)}")
        sh.line("".join(f"M{f(k * w * .14)} {f(h * (.1 + j * .06))}L{f(k * w * .42)} {f(h * (.04 + j * .1))}" for k in (-1, 1) for j in (0, 1)), "l", "stroke-width:.8")
        sh.rect_r(-w / 2, h * .34, w, h * .08, "r"); sh.circle_r(0, h * .43, h * .06, "y"); sh.dot(0, h * .45, .7)
        sh.line(f"M{f(-w * .08)} {f(-h * .38)}l{f(w * .04)} {f(h * .1)}M0 {f(-h * .4)}v{f(h * .11)}M{f(w * .08)} {f(-h * .38)}l{f(-w * .04)} {f(h * .1)}", "l", "stroke-width:1.4")
    elif s in ("left", "right"):
        k = 1 if s == "right" else -1
        for j in range(3): sh.region(f"M{f(-w * .3 + j * w * .22)} {f(-h / 2)}q{f(w * .06)} {f(h * .18)} 0 {f(h * .32)}l{f(w * .08)} {f(-h * .32)}Z", "w")
        sh.ellipse_r(-k * w * .18, h * .38, w * .17, h * .1, "o"); sh.ellipse_r(k * w * .18, h * .38, w * .17, h * .1, "o")
        for x0 in (-k * w * .18, k * w * .18): sh.line(f"M{f(x0 - w * .05)} {f(h * .32)}v{f(h * .06)}M{f(x0 + w * .05)} {f(h * .32)}v{f(h * .06)}", "l", "stroke-width:.8")
    elif s == "back":
        sh.region(f"M{f(-w * .1)} {f(h * .48)}C{f(-w * .1)} {f(h * .1)} {f(w * .3)} {f(h * .1)} {f(w * .25)} {f(-h * .2)}C{f(w * .22)} {f(-h * .38)} {f(w * .38)} {f(-h * .42)} {f(w * .38)} {f(-h * .25)}C{f(w * .42)} {f(h * .15)} {f(w * .08)} {f(h * .15)} {f(w * .08)} {f(h * .48)}Z", "o")
        for j in range(3): sh.region(f"M{f(-w * .35 + j * w * .12)} {f(-h / 2)}q{f(w * .05)} {f(h * .15)} 0 {f(h * .28)}l{f(w * .06)} {f(-h * .28)}Z", "w")
    elif s == "top":
        for j in range(3): sh.region(f"M{f(-w * .2 + j * w * .2)} {f(-h / 2)}q{f(w * .06)} {f(h * .3)} 0 {f(h * .55)}l{f(w * .08)} {f(-h * .55)}Z", "w")
doos("dierendoosje-kat", "Bouwplaat: kattendoosje", "Een rode kater met strepen en een belletje.", box_model(3, 3, 3), "o", kat, "dieren")

def uil(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sh.poly_r([(-w / 2 + 1, -h / 2 + 1), (-w * .22, -h / 2 + 1), (-w / 2 + 1, -h * .3)], "w")
        sh.poly_r([(w / 2 - 1, -h / 2 + 1), (w * .22, -h / 2 + 1), (w / 2 - 1, -h * .3)], "w")
        sh.ellipse_r(0, h * .2, w * .34, h * .26, "k")
        for j in range(3):
            for i in range(3 - (j % 2)):
                x = -w * .16 + i * w * .16 + (j % 2) * w * .08; y = h * .06 + j * h * .08
                sh.line(f"M{f(x - w * .04)} {f(y)}L{f(x)} {f(y + h * .03)}L{f(x + w * .04)} {f(y)}", "l", "stroke-width:.8")
        for x in (-w * .22, w * .22):
            sh.circle_r(x, -h * .2, w * .2, "y"); sh.circle_r(x, -h * .2, w * .12, "-"); sh.circle_r(x, -h * .2, w * .07, "x")
        sh.poly_r([(-w * .06, -h * .12), (w * .06, -h * .12), (0, h * .0)], "o")
        for x in (-w * .14, w * .14): sh.line(f"M{f(x - w * .07)} {f(h / 2 - .8)}l{f(w * .03)} {f(-h * .06)}M{f(x)} {f(h / 2 - .8)}v{f(-h * .07)}M{f(x + w * .07)} {f(h / 2 - .8)}l{f(-w * .03)} {f(-h * .06)}", "l", "stroke-width:1.4")
    elif s in ("left", "right"):
        k = -1 if s == "right" else 1
        sh.region(f"M{f(k * w * .4)} {f(-h * .3)}C{f(-k * w * .3)} {f(-h * .3)} {f(-k * w * .35)} {f(h * .25)} {f(-k * w * .1)} {f(h * .42)}C{f(k * w * .1)} {f(h * .3)} {f(k * w * .35)} {f(h * .1)} {f(k * w * .4)} {f(-h * .3)}Z", "w")
        for j in range(3): sh.line(f"M{f(-k * w * (.18 - j * .1))} {f(h * (.32 - j * .07))}Q{f(k * w * .05)} {f(h * (.05 - j * .05))} {f(k * w * .3)} {f(-h * .22)}", "l", "stroke-width:.7")
    elif s in ("back", "top"):
        r = w / 8
        for j in range(1, 5 if s == "back" else 3):
            y = -h / 2 + j * h / (5 if s == "back" else 3)
            sh.line("".join(f"M{f(-w / 2 + 2 + i * 2 * r)} {f(y)}a{f(r)} {f(r)} 0 0 0 {f(2 * r)} 0" for i in range(int((w - 4) / (2 * r)))), "l", "stroke-width:.8")
doos("dierendoosje-uil", "Bouwplaat: uilendoosje", "Een uil met grote ogen en veren op zijn rug.", box_model(3, 2.6, 4), "w", uil, "dieren")

def kikker(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "top":
        # ogen aan de voorkant van het bovenvlak (onderkant van dit vlak = voorkant van de kikker)
        for x in (-w * .22, w * .22):
            sh.circle_r(x, h * .22, h * .22, "g"); sh.circle_r(x, h * .24, h * .15, "-"); sh.circle_r(x, h * .26, h * .08, "x")
        for (x, y, r) in ((-w * .28, -h * .25, .07), (w * .05, -h * .3, .05), (w * .3, -h * .15, .06)): sh.circle_r(x, y, h * r * 1.6, "g")
    elif s == "front":
        sh.line(f"M{f(-w * .38)} {f(-h * .25)}Q0 {f(h * .2)} {f(w * .38)} {f(-h * .25)}", "l", "stroke-width:1.4")
        sh.circle_r(-w * .36, -h * .1, h * .08, "m"); sh.circle_r(w * .36, -h * .1, h * .08, "m")
        sh.dot(-w * .05, -h * .35, .8); sh.dot(w * .05, -h * .35, .8)
        for x in (-w * .3, w * .3):
            for k in (-1, 0, 1): sh.circle_r(x + k * w * .05, h * .4, h * .05, "l")
            sh.rect_r(x - w * .03, h * .2, w * .06, h * .18, "l")
    elif s in ("left", "right"):
        k = 1 if s == "right" else -1
        sh.region(f"M{f(k * w * .4)} {f(h * .45)}C{f(k * w * .4)} {f(-h * .35)} {f(-k * w * .3)} {f(-h * .35)} {f(-k * w * .3)} {f(h * .1)}L{f(-k * w * .1)} {f(h * .3)}Z", "g")
        for j in (-1, 0, 1): sh.circle_r(-k * w * .38 + j * w * .06, h * .38, h * .07, "l")
        sh.line(f"M{f(-k * w * .3)} {f(h * .1)}L{f(-k * w * .38)} {f(h * .32)}", "l", "stroke-width:1")
    elif s == "back":
        for (x, y, r) in ((-w * .3, -h * .1, .1), (0, h * .15, .08), (w * .25, -h * .2, .12), (w * .32, h * .25, .07), (-w * .15, -h * .3, .06)): sh.circle_r(x, y, h * r * 1.3, "g")
doos("dierendoosje-kikker", "Bouwplaat: kikkerdoosje", "Een vrolijke kikker met bolle ogen bovenop.", box_model(4, 3.4, 2.6), "l", kikker, "dieren",
     extra=["De bolle ogen zitten op het bovenvlak, aan de kant van de mond."])

def varken(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        sh.poly_r([(-w * .45, -h / 2 + 1), (-w * .12, -h / 2 + 1), (-w * .36, -h * .12)], "m")
        sh.poly_r([(w * .45, -h / 2 + 1), (w * .12, -h / 2 + 1), (w * .36, -h * .12)], "m")
        for x in (-w * .17, w * .17): sh.circle_r(x, -h * .1, w * .05, "-"); sh.dot(x, -h * .09, w * .03)
        sh.ellipse_r(0, h * .15, w * .22, h * .15, "m"); sh.ellipse_r(-w * .08, h * .15, w * .04, h * .06, "x"); sh.ellipse_r(w * .08, h * .15, w * .04, h * .06, "x")
        sh.line(f"M{f(-w * .12)} {f(h * .36)}Q0 {f(h * .44)} {f(w * .12)} {f(h * .36)}", "l", "stroke-width:1.2")
        sh.circle_r(-w * .36, h * .2, w * .06, "m"); sh.circle_r(w * .36, h * .2, w * .06, "m")
    elif s in ("left", "right"):
        for x in (-w * .3, w * .3): sh.rect_r(x - w * .08, h * .3, w * .16, h * .2, "k"); sh.rect_r(x - w * .08, h * .42, w * .16, h * .08, "w"); sh.seg(x, h * .42, x, h / 2)
        sh.ellipse_r(-w * .05, -h * .15, w * .12, h * .08, "w")
    elif s == "back":
        sh.line(f"M0 {f(h * .05)}c{f(w * .12)} 0 {f(w * .12)} {f(-h * .14)} {f(w * .04)} {f(-h * .14)}s{f(-w * .06)} {f(h * .1)} {f(w * .04)} {f(h * .1)}s{f(w * .12)} {f(-h * .2)} {f(w * .02)} {f(-h * .22)}", "l", "stroke-width:1.4")
        for x in (-w * .3, w * .3): sh.rect_r(x - w * .08, h * .3, w * .16, h * .2, "k"); sh.rect_r(x - w * .08, h * .42, w * .16, h * .08, "w")
    elif s == "top":
        sh.ellipse_r(w * .15, h * .1, w * .14, h * .09, "w")
doos("dierendoosje-varken", "Bouwplaat: varkensdoosje", "Een roze biggetje met een krulstaart.", box_model(3, 3, 3), "k", varken, "boerderij")

def kuiken(sh, F):
    s = side(F); w, h = F.w, F.h
    # eierschaal met zigzagrand onder op alle zijkanten
    if s in ("front", "back", "left", "right"):
        n = 6; zz = [(-w / 2, h * .1)]
        for k in range(n): zz += [(-w / 2 + (k + .5) * w / n, h * (-.02 if k % 2 == 0 else .04)), (-w / 2 + (k + 1) * w / n, h * .1)]
        sh.poly_r(zz + [(w / 2, h / 2), (-w / 2, h / 2)], "b")
        for (x, y) in ((-w * .25, h * .3), (w * .2, h * .35), (0, h * .22)): sh.circle_line(x, y, w * .04, "l", "stroke-width:.7")
    if s == "front":
        for x in (-w * .18, w * .18): sh.circle_r(x, -h * .25, w * .07, "x"); sh.circle_r(x + w * .025, -h * .27, w * .025, "-")
        sh.poly_r([(-w * .08, -h * .14), (w * .08, -h * .14), (0, -h * .03)], "o"); sh.seg(-w * .08, -h * .14, w * .08, -h * .14)
        sh.circle_r(-w * .32, -h * .12, w * .05, "m"); sh.circle_r(w * .32, -h * .12, w * .05, "m")
    elif s in ("left", "right"):
        k = 1 if s == "right" else -1
        sh.region(f"M{f(-k * w * .25)} {f(-h * .3)}C{f(k * w * .3)} {f(-h * .35)} {f(k * w * .35)} {f(-h * .1)} {f(k * w * .3)} {f(-h * .05)}L{f(k * w * .15)} {f(-h * .1)}L{f(k * w * .2)} {f(-h * .02)}C{f(0)} {f(-h * .05)} {f(-k * w * .25)} {f(-h * .15)} {f(-k * w * .25)} {f(-h * .3)}Z", "o")
    elif s == "back":
        sh.region(f"M{f(-w * .1)} {f(-h * .1)}L{f(-w * .15)} {f(-h * .32)}L{f(0)} {f(-h * .18)}L{f(w * .15)} {f(-h * .32)}L{f(w * .1)} {f(-h * .1)}Z", "o")
    elif s == "top":
        for a in (-30, 0, 30):
            sh.raw(f'<g transform="rotate({a} 0 {f(h * .15)})">'); sh.ellipse_r(0, -h * .02, w * .05, h * .17, "y"); sh.raw('</g>')
doos("paasdoosje-kuiken", "Bouwplaat: paasdoosje kuiken", "Een kuikentje dat net uit het ei komt.", box_model(3, 3, 3.4), "y", kuiken, "boerderij", holiday="pasen",
     extra=["Leuk om paaseitjes in te verstoppen: plak het bovenvlak dan niet vast, maar stop het flapje ertussen."])

# --- voertuigen en karren ---
def ijscokar(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("front", "back"):
        n = 8; sw = w / n
        for k in range(n): sh.region(f"M{f(-w / 2 + k * sw)} {f(-h / 2)}h{f(sw)}v{f(h * .12)}a{f(sw / 2)} {f(sw / 3)} 0 0 1 {f(-sw)} 0Z", "m" if k % 2 == 0 else "-")
        wheel(sh, -w * .3, h * .3, h * .16, "z", 8)
        if s == "front":
            sh.rect_r(-w * .05, -h * .22, w * .48, h * .3, "-", 2)
            sh.text(w * .19, -h * .02, "IJS", max(6, h * .16), weight="800")
            for k, c in enumerate("rym"):
                x = -w * .38 + k * w * .12; y = -h * .22
                sh.poly_r([(x - w * .04, y), (x + w * .04, y), (x, y + h * .2)], "w"); sh.circle_r(x, y - h * .02, w * .045, c)
        else:
            for k, c in enumerate("ogr"):
                x = -w * .05 + k * w * .16; y = -h * .2
                sh.poly_r([(x - w * .05, y), (x + w * .05, y), (x, y + h * .26)], "w"); sh.circle_r(x, y - h * .03, w * .055, c)
    elif s in ("left", "right"):
        if s == "right":
            sh.line(f"M{f(-w * .3)} {f(-h * .05)}L{f(w * .2)} {f(-h * .3)}", "l", "stroke-width:2"); sh.rect_r(w * .1, -h * .4, w * .25, h * .1, "x", 1)
        sh.circle_r(0, h * .3, h * .1, "z")
        if s == "left":
            for k, t in enumerate(("aardbei", "vanille", "chocola")): sh.text(0, -h * .2 + k * h * .14, t, max(4.5, h * .09), weight="600")
    elif s == "top":
        for k in range(3):
            x = -w * .32 + k * w * .32; sh.circle_r(x, 0, h * .3, "z"); sh.circle_r(x, 0, h * .08, "-")
bouwplaat("bouwplaat-ijscokar", "Bouwplaat: ijscokar", "Een karretje vol ijs, met een duwstang en een luifeltje.", box_model(5, 2.6, 3),
          lambda F: "-" if side(F) == "bottom" else "b", ijscokar, "eten", "6-9", 2, 30,
          ["De kant met het bord IJS is de voorkant; de duwstang zit op de rechterkant."])

def circuswagen(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("front", "back"):
        cx0, cx1, cy0, cy1 = -w * .38, w * .38, -h * .3, h * .2
        sh.rect_r(cx0, cy0, cx1 - cx0, cy1 - cy0, "y")
        if s == "front":
            # leeuw
            mr = h * .2; x, y = 0, -h * .05
            sh.region("M" + " ".join(f"{'L' if k else ''}{f(x + math.cos(k * math.pi / 10) * mr * (1 if k % 2 == 0 else .82))} {f(y + math.sin(k * math.pi / 10) * mr * (1 if k % 2 == 0 else .82))}" for k in range(20)) + "Z", "o")
            sh.circle_r(x, y, mr * .62, "y"); sh.dot(x - mr * .22, y - mr * .12, .9); sh.dot(x + mr * .22, y - mr * .12, .9)
            sh.poly_r([(x - mr * .12, y + mr * .08), (x + mr * .12, y + mr * .08), (x, y + mr * .2)], "w")
            sh.line(f"M{f(x)} {f(y + mr * .2)}v{f(mr * .1)}M{f(x - mr * .15)} {f(y + mr * .38)}q{f(mr * .15)} {f(mr * .1)} {f(mr * .3)} 0", "l", "stroke-width:.8")
        else:
            # beer met bal
            x, y, r = -w * .08, -h * .05, h * .15
            sh.circle_r(x - r * .7, y - r * .8, r * .35, "w"); sh.circle_r(x + r * .7, y - r * .8, r * .35, "w")
            sh.circle_r(x, y, r, "w"); sh.ellipse_r(x, y + r * .35, r * .4, r * .3, "y"); sh.dot(x, y + r * .25, .9)
            sh.dot(x - r * .35, y - r * .2, .9); sh.dot(x + r * .35, y - r * .2, .9)
            sh.circle_r(w * .2, h * .08, h * .1, "r"); sh.line(f"M{f(w * .2 - h * .1)} {f(h * .08)}H{f(w * .2 + h * .1)}", "l", "stroke-width:.8")
        sh.line("".join(f"M{f(cx0 + k * (cx1 - cx0) / 8)} {f(cy0)}V{f(cy1)}" for k in range(1, 8)), "l", "stroke-width:1")
        n = 10; sw = w / n
        sh.line("".join(f"M{f(-w / 2 + k * sw)} {f(-h / 2 + h * .08)}a{f(sw / 2)} {f(sw / 3)} 0 0 0 {f(sw)} 0" for k in range(n)), "l", "stroke-width:.8")
        for x in (-w * .3, w * .3): wheel(sh, x, h * .36, h * .13, "r", 8)
    elif s in ("left", "right"):
        sh.rect_r(-w * .25, -h * .3, w * .5, h * .55, "o", 2); sh.region(star_path(0, -h * .05, h * .13, h * .055), "y")
    elif s == "top":
        n = 8
        for k in range(n): sh.rect_r(-w / 2 + k * w / n, -h / 2, w / n, h, "r" if k % 2 == 0 else "-")
bouwplaat("bouwplaat-circuswagen", "Bouwplaat: circuswagen", "Een kooiwagen met een leeuw en een beer.", box_model(5, 2.4, 3),
          lambda F: "-" if side(F) == "bottom" else "p", circuswagen, "voertuigen", "6-9", 2, 30,
          ["Aan de ene lange kant zit de leeuw, aan de andere kant de beer. Het gestreepte vlak is het dak."])

CARAVAN = [(.5, .3), (5.5, .3), (6, .8), (6, 2.6), (5.6, 3), (.8, 3), (0, 2.2), (0, .8)]
def caravan(sh, F):
    x, y, z = F.n; w, h = F.w, F.h
    if abs(y) > .9:
        # zijkant: profiel; lokaal x loopt met model-x mee aan de voorkant (-y), gespiegeld aan de achterkant
        k = 1 if y < 0 else -1
        X = lambda mx: k * (mx - 3) * F.sc; Y = lambda mz: -(mz - 1.65) * F.sc
        sh.rect_r(min(X(.05), X(5.95)), Y(1.62), abs(X(5.95) - X(.05)), F.sc * .28, "o")
        for mx in (1.3, 4.6): window(sh, X(mx), Y(2.2), F.sc * 1.0, F.sc * .6, "b", False); sh.seg(X(mx) - F.sc * .5, Y(2.2), X(mx) + F.sc * .5, Y(2.2))
        sh.rect_r(min(X(2.6), X(3.5)), Y(2.6), F.sc * .9, F.sc * 2.0, "y", 1); sh.circle_r(X(3.05), Y(2.15), F.sc * .22, "b"); sh.dot(X(3.4 if k > 0 else 2.7), Y(1.5), .9)
        wheel(sh, X(4.3), Y(.74), F.sc * .4, "x")
    elif z > .95:
        sh.rect_r(-w * .1, -h * .25, w * .2, h * .5, "b", 1.5)
    elif x > .5 and abs(z) < .3:
        window(sh, 0, -h * .1, w * .6, h * .4, "b")
    elif x < -.5 and abs(z) < .3:
        sh.rect_r(-w * .15, -h * .2, w * .3, h * .3, "r", 1)
    elif z > .3 and x < 0:
        window(sh, 0, 0, w * .7, h * .5, "b", False)
bouwplaat("bouwplaat-caravan", "Bouwplaat: caravan", "Een caravan met een deur, ramen en een dakluik.", profile_y(CARAVAN, 2.6),
          lambda F: "-" if F.n[2] < -.95 else "y" if abs(F.n[1]) > .9 else "-", caravan, "voertuigen", "6-9", 2, 35,
          ["De grote vlakken met het wiel zijn de zijkanten. De smalle stroken vormen samen de rand eromheen: vouw ze een voor een om."])

# --- cadeaus en feest ---
def cadeau3(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("front", "back", "left", "right"):
        rng = random.Random(F.idx)
        for k in range(7):
            x = rng.uniform(-w * .42, w * .42); y = rng.uniform(-h * .4, h * .4)
            if abs(x) < w * .16: x += w * .3 if x > 0 else -w * .3
            if s == "front" and x < 0 and y > -h * .05: continue
            sh.circle_r(x, y, w * .035, "y")
        sh.rect_r(-w * .08, -h / 2, w * .16, h, "r")
        if s == "front":
            sh.rect_r(-w * .42, h * .02, w * .28, h * .3, "-", 1.5); sh.circle_line(-w * .38, h * .08, .9, "l", "stroke-width:.6")
            sh.text(-w * .28, h * .15, "Voor:", max(4.5, h * .09), weight="700"); sh.seg(-w * .39, h * .26, -w * .17, h * .26, "l", "stroke-width:.6")
    elif s == "top":
        q = F.poly; cx = sum(p[0] for p in q) / 3; cy = sum(p[1] for p in q) / 3
        for i in range(3):
            a, b = q[i], q[(i + 1) % 3]; m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            dx, dy = m[0] - cx, m[1] - cy; L = math.hypot(dx, dy); nx, ny = -dy / L * w * .07, dx / L * w * .07
            sh.poly_r([(cx + nx, cy + ny), (m[0] + nx, m[1] + ny), (m[0] - nx, m[1] - ny), (cx - nx, cy - ny)], "r")
        for a in (75, 105):
            sh.raw(f'<g transform="rotate({a} {f(cx)} {f(cy)})">'); sh.ellipse_r(cx + w * .14, cy, w * .14, w * .04, "r"); sh.raw('</g>')
        for a in (200, -20):
            sh.raw(f'<g transform="rotate({a} {f(cx)} {f(cy)})">'); sh.ellipse_r(cx + w * .17, cy, w * .17, w * .09, "m"); sh.raw('</g>')
        sh.circle_r(cx, cy, w * .06, "r")
TRI = ph.hull_faces([(x, y, z) for x, y in ((0, 0), (3, 0), (1.5, 1.5 * math.sqrt(3))) for z in (0, 2.8)])
bouwplaat("driehoekig-cadeaudoosje", "Bouwplaat: driehoekig cadeaudoosje", "Een doosje met drie kanten, een lint en een strik.", TRI,
          lambda F: "-" if side(F) == "bottom" else "b", cadeau3, "feest", "6-9", 2, 25,
          ["Het vlak met de strik is de bovenkant. Wil je er iets in stoppen? Plak de bovenkant dan als laatste, met één flapje los als klepje."], holiday="verjaardag")

def kerstpiramide(sh, F):
    s = side(F); w, h = F.w, F.h
    if s.startswith("roof"):
        sh.region(star_path(0, -h * .12, h * .085, h * .038), "y")
        y0 = h * .08
        xs = [p[0] for p in (clip(F.poly, -1e3, y0 - .1, 1e3, y0 + .1) or [(0, 0)])]
        a, b = min(xs) + 3, max(xs) - 3
        sh.line(f"M{f(a)} {f(y0 - 2)}Q{f((a + b) / 2)} {f(y0 + h * .12)} {f(b)} {f(y0 - 2)}", "l", "stroke-width:1")
        for k, c in enumerate("ryb"):
            t = (k + 1) / 4; x = a + (b - a) * t; y = (1 - t) ** 2 * (y0 - 2) + 2 * t * (1 - t) * (y0 + h * .12) + t * t * (y0 - 2)
            sh.circle_r(x, y + h * .05, h * .045, c); sh.rect_r(x - h * .015, y + h * .0, h * .03, h * .012, "z")
        for (x, y) in ((-w * .2, h * .32), (w * .2, h * .32), (0, h * .38), (-w * .07, -h * .02), (w * .08, -h * .05)): snowflake(sh, x, y, h * .035)
PYR = ph.hull_faces([(x, y, 0) for x in (-1.8, 1.8) for y in (-1.8, 1.8)] + [(0, 0, 4.4)])
bouwplaat("kerst-piramidedoosje", "Bouwplaat: kerstpiramide", "Een puntdoosje met kerstballen, sneeuwvlokjes en een ster.", PYR,
          lambda F: "-" if side(F) == "bottom" else "n", kerstpiramide, "feest", "6-9", 2, 20,
          ["Vouw de vier driehoeken omhoog tot hun punten elkaar raken. Mooi als versiering onder de kerstboom of met een touwtje aan de punt."], holiday="kerst")

def taartpunt(sh, F):
    s = side(F); w, h = F.w, F.h; x, y, z = F.n
    if abs(z) < .3:
        # lagen: biscuit, room, jam, biscuit, room
        for y0, y1, c in ((-.5, -.38, "k"), (-.38, -.12, "y"), (-.12, -.04, "r"), (-.04, .22, "y"), (.22, .3, "k"), (.3, .5, "y")):
            band(sh, F, h * y0, h * y1, c)
        if x > .9:
            for k in range(5): sh.circle_r(-w * .4 + k * w * .2, -h * .44, w * .07, "-")
    elif z > .95:
        q = F.poly; bx = max(p[0] for p in q)
        sx = bx - w * .2; r = h * .17
        sh.region(f"M{f(sx + r)} {f(0)}C{f(sx + r)} {f(-r * 1.1)} {f(sx - r * .3)} {f(-r * .9)} {f(sx - r * 1.3)} 0C{f(sx - r * .3)} {f(r * .9)} {f(sx + r)} {f(r * 1.1)} {f(sx + r)} 0Z", "r")
        sh.poly_r([(sx + r, 0), (sx + r * 1.5, -r * .5), (sx + r * 1.2, 0), (sx + r * 1.5, r * .5)], "g")
        for (u, v) in ((-.6, -.2), (-.2, .3), (.2, -.35), (.4, .2), (-.9, .1)): sh.dot(sx + u * r, v * r, .5)
        for k in range(3): sh.circle_r(bx - w * .35 - k * w * .12, h * (.12 if k % 2 else -.12) * (1 - k * .2), w * .025, "m")
TAART = ph.hull_faces([(px, py, pz) for px, py in ((0, 0), (5, -1.4), (5, 1.4)) for pz in (0, 2.4)])
bouwplaat("taartpunt-doosje", "Bouwplaat: taartpunt", "Een stuk taart met lagen room en jam, en een aardbei erop.", TAART,
          lambda F: "-" if side(F) == "bottom" else "k" if F.n[2] > .95 else "y", taartpunt, "eten", "6-9", 2, 25,
          ["Het vlak met de aardbei is de bovenkant; de brede kant met de toefjes room is de achterkant van de punt.", "Maak er een paar en leg ze in een kring: een hele taart!"], holiday="verjaardag")

# --- natuur, boerderij, zee ---
def bijenhotel(sh, F):
    s = side(F); w, h = F.w, F.h
    if s == "front":
        inner = Polygon(inset(F, 2.6)); sh.poly_r(inset(F, 2.2), "y")
        r = h * .055; dx = 2.15 * r; dy = dx * math.sqrt(3) / 2; j = 0; y = -h / 2
        while y < h / 2:
            x = -w / 2 + (dx / 2 if j % 2 else 0)
            while x < w / 2:
                if inner.contains(Polygon([(x + r * math.cos(a), y + r * math.sin(a)) for a in [k * math.pi / 4 for k in range(8)]])):
                    sh.circle_r(x, y, r, "w"); sh.dot(x, y, r * .45)
                x += dx
            y += dy; j += 1
    elif s.startswith("roof"):
        tiles(sh, F, F.h / 4)
    elif s in ("left", "right"):
        for k, c in enumerate("rmp"): flower(sh, -w * .3 + k * w * .3, h * .1 + (k % 2) * h * .1, h * .1, c, "y", h * .2)
        bee(sh, -w * .12, -h * .25, h * .16, s == "left"); bee(sh, w * .28, -h * .32, h * .13, s == "left")
    elif s == "back":
        sh.circle_line(0, -h * .32, h * .04, "l", "stroke-width:.8")
        sh.text(0, h * .05, "bijenhotel", max(5, h * .08), weight="800"); sh.region(heart_path(0, h * .22, h * .1), "r")
bouwplaat("bouwplaat-bijenhotel", "Bouwplaat: bijenhotel", "Een huisje vol gangetjes waar wilde bijen in wonen.", house_y(3.6, 2.6, 3, 4.6),
          lambda F: "-" if side(F) == "bottom" else "r" if side(F).startswith("roof") else "w", bijenhotel, "natuur", "6-9", 2, 30,
          ["De gevel met alle gaatjes is de voorkant; het puntdak hoort erboven.", "Een echt bijenhotel maak je van holle stengels of geboord hout. Dit papieren hotel is om naar te kijken: zet het binnen bij het raam."])

def melkpak(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("front", "back"):
        rng = random.Random(3 + F.idx)
        for (x, y, r) in (((-w * .3, -h * .38, .1), (w * .33, h * .2, .1), (-w * .32, h * .14, .08), (w * .2, -h * .4, .06)) if s == "front" else ((-w * .3, -h * .38, .1), (w * .3, h * .2, .1), (-w * .3, h * .22, .07), (w * .25, -h * .35, .07))):
            q = [(x + math.cos(a) * w * r * rng.uniform(.75, 1.25), y + math.sin(a) * w * r * rng.uniform(.75, 1.25)) for a in [k * math.pi / 4 for k in range(8)]]
            sh.region("M" + " ".join(f"{'Q' if k % 2 else 'L'}{f(q[k][0])} {f(q[k][1])}" if False else f"{'L' if k else ''}{f(q[k][0])} {f(q[k][1])}" for k in range(8)) + "Z", "x")
        if s == "front":
            sh.ellipse_r(0, -h * .12, w * .38, h * .11, "b"); sh.text(0, -h * .12 + h * .045, "MELK", max(6, h * .12), weight="800")
            sh.region(f"M0 {f(h * .05)}C{f(w * .14)} {f(h * .2)} {f(w * .1)} {f(h * .3)} 0 {f(h * .3)}C{f(-w * .1)} {f(h * .3)} {f(-w * .14)} {f(h * .2)} 0 {f(h * .05)}Z", "-")
        else:
            sh.text(0, -h * .1, "vers van", max(4.5, h * .06), weight="700"); sh.text(0, -h * .1 + h * .08, "de boerderij", max(4.5, h * .06), weight="700")
        sh.region(f"M{f(-w / 2)} {f(h / 2)}V{f(h * .4)}" + "".join(f"q{f(w / 16)} {f(-h * .07)} {f(w / 8)} 0" for _ in range(8)) + f"V{f(h / 2)}Z", "l")
    elif s in ("left", "right"):
        sh.region(f"M{f(-w / 2)} {f(h / 2)}V{f(h * .4)}" + "".join(f"q{f(w / 16)} {f(-h * .06)} {f(w / 8)} 0" for _ in range(8)) + f"V{f(h / 2)}Z", "l")
        flower(sh, w * .2, h * .25, h * .06, "y", "o", h * .07)
        # glas melk
        sh.region(f"M{f(-w * .22)} {f(-h * .12)}L{f(-w * .16)} {f(h * .3)}H{f(w * .06)}L{f(w * .12)} {f(-h * .12)}Z", "b"); sh.seg(-w * .2, -h * .02, w * .1, -h * .02)
    elif s.startswith("roof") and s == "roof_front":
        sh.text(0, h * .1, "hier open", max(4.5, h * .12), weight="700")
bouwplaat("bouwplaat-melkpak", "Bouwplaat: melkpak", "Een pak melk met koeienvlekken en een puntdakje.", house_x(2.6, 2.6, 4.2, 5.2),
          lambda F: "b" if side(F).startswith("roof") else "-", melkpak, "boerderij", "6-9", 2, 25,
          ["De kant met MELK is de voorkant; de twee schuine vlakken vormen samen het puntje bovenop."])

def ring(n, r, z, off):
    return [(r * math.cos(off + 2 * math.pi * k / n), r * math.sin(off + 2 * math.pi * k / n), z) for k in range(n)]
OFF6 = -math.pi / 2 - math.pi / 6  # zo wijst één vlak recht naar voren (-y)
VUUR = ph.hull_faces(ring(6, 1.4, 0, OFF6) + ring(6, 1.0, 5.2, OFF6) + ring(6, 1.0, 6.2, OFF6) + [(0, 0, 7.3)])
def vuur_codes(F):
    if F.n[2] < -.95: return "-"
    if F.z > 6.2: return "r"
    if F.z > 5.2: return "y"
    return "-"
def vuurtoren(sh, F):
    w, h = F.w, F.h
    if F.n[2] < -.95 or F.z > 6.2: return
    if F.z > 5.2:
        sh.line(f"M0 {f(-h / 2)}V{f(h / 2)}M{f(-w / 2)} {f(h * .1)}H{f(w / 2)}", "l", "stroke-width:.8"); return
    for k in range(4):
        band(sh, F, -h / 2 + (2 * k + 1) * h / 8, -h / 2 + (2 * k + 2) * h / 8, "r")
    if F.n[1] < -.9:
        sh.region(f"M{f(-w * .2)} {f(h / 2)}V{f(h * .38)}A{f(w * .2)} {f(w * .2)} 0 0 1 {f(w * .2)} {f(h * .38)}V{f(h / 2)}Z", "w")
        window(sh, 0, -h * .12, w * .22, h * .06, "b", False)
    elif F.idx % 2 == 0:
        window(sh, 0, h * .12, w * .2, h * .06, "b", False); window(sh, 0, -h * .38, w * .2, h * .06, "b", False)
bouwplaat("bouwplaat-vuurtoren", "Bouwplaat: vuurtoren", "Een rood-witte vuurtoren met een lichtkamer en een puntdak.", VUUR,
          vuur_codes, vuurtoren, "zee", "9+", 3, 45,
          ["Vouw eerst de lange wanden rond tot een koker en plak die dicht. Daarna de gele lichtkamer en als laatste het puntdak en de bodem.",
           "Zet er een led-lichtje in, dan schijnt de lichtkamer!"], box=(8, 32, 184, 236), adult=False, tries=400)

# --- edelsteen ---
OFFG = -math.pi / 2 - math.pi / 8
GEM = ph.hull_faces(ring(8, .55, .9, OFFG) + ring(8, 1.0, .45, OFFG) + [(0, 0, -1.1)])
def gem_codes(F):
    if F.n[2] > .95: return "b"
    k = round((math.atan2(F.n[1], F.n[0]) - OFFG) / (math.pi / 4)) % 2
    return ("t" if k else "b") if F.n[2] > 0 else ("n" if k else "p")
def gem(sh, F):
    w, h = F.w, F.h
    def spark(x, y, r): sh.line(f"M{f(x - r)} {f(y)}Q{f(x)} {f(y)} {f(x)} {f(y - r)}Q{f(x)} {f(y)} {f(x + r)} {f(y)}Q{f(x)} {f(y)} {f(x)} {f(y + r)}Q{f(x)} {f(y)} {f(x - r)} {f(y)}", "l", "stroke-width:.7")
    if F.n[2] > .95: spark(-w * .15, -h * .12, w * .1); spark(w * .18, h * .15, w * .06)
    elif F.idx % 3 == 0: spark(w * .1, -h * .05 if F.n[2] > 0 else -h * .2, min(w, h) * .12)
bouwplaat("bouwplaat-edelsteen", "Bouwplaat: edelsteen", "Een geslepen steen met een tafelvlak, facetten en een punt.", GEM,
          gem_codes, gem, "vormen", "9+", 3, 40,
          ["Het achthoekige vlak is de bovenkant (de tafel). De acht driehoeken vormen samen de punt aan de onderkant.", "Gebruik voor elke kleur twee tinten naast elkaar, dan lijkt de steen te schitteren."],
          upright=None, adult=False, tries=300)

# --- spookhuisje ---
def spookhuis(sh, F):
    s = side(F); w, h = F.w, F.h
    def ghost(x, y, r):
        sh.region(f"M{f(x - r)} {f(y + r)}V{f(y)}A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)}V{f(y + r)}l{f(-r / 2)} {f(-r * .3)}l{f(-r / 2)} {f(r * .3)}l{f(-r / 2)} {f(-r * .3)}Z", "-")
        sh.dot(x - r * .35, y - r * .1, r * .14); sh.dot(x + r * .35, y - r * .1, r * .14)
    def bat(x, y, r):
        sh.region(f"M{f(x)} {f(y - r * .2)}Q{f(x - r * .5)} {f(y - r * .6)} {f(x - r * 1.4)} {f(y - r * .3)}Q{f(x - r)} {f(y)} {f(x - r * .9)} {f(y + r * .3)}Q{f(x - r * .5)} {f(y)} {f(x)} {f(y + r * .3)}Q{f(x + r * .5)} {f(y)} {f(x + r * .9)} {f(y + r * .3)}Q{f(x + r)} {f(y)} {f(x + r * 1.4)} {f(y - r * .3)}Q{f(x + r * .5)} {f(y - r * .6)} {f(x)} {f(y - r * .2)}Z", "x")
    def crooked(x, y, ww, hh, a, code="y"):
        c, si = math.cos(math.radians(a)), math.sin(math.radians(a))
        q = [(x + c * u - si * v, y + si * u + c * v) for u, v in ((-ww / 2, -hh / 2), (ww / 2, -hh / 2), (ww / 2, hh / 2), (-ww / 2, hh / 2))]
        sh.poly_r(q, code)
        return q
    if s == "front":
        wall = h * 4 / 5.6; yb = h / 2; yt = yb - wall
        sh.region(f"M{f(-w * .15)} {f(yb)}V{f(yb - wall * .3)}A{f(w * .15)} {f(w * .15)} 0 0 1 {f(w * .15)} {f(yb - wall * .3)}V{f(yb)}Z", "w"); sh.dot(w * .08, yb - wall * .15, .9)
        crooked(-w * .26, yt + wall * .32, w * .26, wall * .24, -6); ghost(-w * .26, yt + wall * .31, w * .09)
        q = crooked(w * .26, yt + wall * .3, w * .24, wall * .22, 5); sh.line(f"M{f((q[0][0] + q[1][0]) / 2)} {f((q[0][1] + q[1][1]) / 2)}L{f((q[2][0] + q[3][0]) / 2)} {f((q[2][1] + q[3][1]) / 2)}")
        sh.circle_r(0, yt - h * .08, w * .12, "y"); bat(0, yt - h * .08, w * .075)
    elif s in ("left", "right"):
        crooked(0, -h * .1, w * .3, h * .3, 4 if s == "left" else -4)
        sh.rect_r(-w * .2, -h * .2, w * .4, h * .05, "w"); sh.rect_r(-w * .2, -h * .02, w * .4, h * .05, "w")
        sh.ellipse_r(w * .25, h * .38, w * .12, h * .08, "o"); sh.line(f"M{f(w * .25)} {f(h * .3)}v{f(-h * .04)}", "l", "stroke-width:1.2")
        sh.line(f"M{f(w * .19)} {f(h * .36)}l{f(w * .03)} {f(-h * .02)}l{f(w * .03)} {f(h * .02)}M{f(w * .26)} {f(h * .36)}l{f(w * .03)} {f(-h * .02)}l{f(w * .03)} {f(h * .02)}M{f(w * .19)} {f(h * .41)}q{f(w * .06)} {f(h * .03)} {f(w * .12)} 0", "l", "stroke-width:.7")
        bat(-w * .22, h * .3, w * .11)
    elif s == "back":
        wall = h * 4 / 5.6; yb = h / 2; yt = yb - wall
        crooked(0, yt + wall * .45, w * .34, wall * .3, -3)
        x0, y0 = w * .17 - 1.5, yt + wall * .3 + 1
        sh.line("".join(f"M{f(x0)} {f(y0)}l{f(-math.cos(a) * w * .12)} {f(math.sin(a) * w * .12)}" for a in (0, .5, 1.05, 1.57)) +
                "".join(f"M{f(x0 - w * k)} {f(y0)}Q{f(x0 - w * k * .8)} {f(y0 + w * k * .8)} {f(x0)} {f(y0 + w * k)}" for k in (.05, .09)), "l", "stroke-width:.6")
        ghost(-w * .22, h * .3, w * .13)
    elif s.startswith("roof"):
        tiles(sh, F, F.h / 5)
        sh.circle_r(w * .2, -h * .2, h * .1, "y") if s == "roof_left" else bat(-w * .1, 0, h * .16)
bouwplaat("spookhuisje", "Bouwplaat: spookhuisje", "Een scheef huisje met spookjes, vleermuizen en een pompoen.", house_y(3.2, 3, 4, 5.6),
          lambda F: "-" if side(F) == "bottom" else "p" if side(F).startswith("roof") else "z", spookhuis, "feest", "6-9", 2, 30,
          ["De gevel met de boogdeur is de voorkant; het puntdak hoort erboven.", "Zet er een led-lichtje in en doe het licht uit: griezelig!"], holiday="halloween")

# --- schatkist ---
KIST = profile_x([(0, 0), (2.6, 0), (2.6, 2), (2.2, 2.8), (.4, 2.8), (0, 2)], 4)
def schatkist(sh, F):
    s = side(F); w, h = F.w, F.h
    if s in ("left", "right"):
        # profiel zijkant: kist tot 2 hoog, deksel tot 2.8 (lokaal: onder = +h/2)
        yl = h / 2 - h * 2 / 2.8
        sh.seg(-w / 2 + .5, yl, w / 2 - .5, yl)
        for k in (1, 2): sh.seg(-w / 2 + .5, yl + k * (h / 2 - yl) / 3, w / 2 - .5, yl + k * (h / 2 - yl) / 3, "l", "stroke-width:.6")
        sh.circle_line(0, yl + (h / 2 - yl) * .4, h * .1, "l", "stroke-width:1.6"); sh.rect_r(-w * .08, yl + h * .05, w * .16, h * .06, "z")
        return
    for k in range(1, 4): sh.seg(-w / 2 + .5, -h / 2 + k * h / 4, w / 2 - .5, -h / 2 + k * h / 4, "l", "stroke-width:.6")
    for x in (-w * .32, w * .32): sh.rect_r(x - w * .045, -h / 2, w * .09, h, "z")
    for x in (-w * .32, w * .32):
        for y in (-h * .35, h * .35): sh.dot(x, y, .8)
    if s == "front":
        sh.rect_r(-w * .08, -h / 2, w * .16, h * .32, "y", 1); sh.circle_line(0, -h / 2 + h * .12, h * .04, "l", "stroke-width:.8"); sh.seg(0, -h / 2 + h * .15, 0, -h / 2 + h * .24, "l", "stroke-width:1")
    elif s == "roof_front":
        sh.region(f"M{f(-w * .1)} {f(0)}l{f(w * .05)} {f(-h * .25)}h{f(w * .1)}l{f(w * .05)} {f(h * .25)}l{f(-w * .1)} {f(h * .3)}Z", "r")
    elif s == "top":
        for (x, c) in ((-w * .12, "g"), (w * .12, "b")): sh.region(f"M{f(x)} {f(-h * .25)}l{f(w * .06)} {f(h * .25)}l{f(-w * .06)} {f(h * .25)}l{f(-w * .06)} {f(-h * .25)}Z", c)
bouwplaat("bouwplaat-schatkist", "Bouwplaat: schatkist", "Een houten kist met ijzeren banden, een slot en edelstenen.", KIST,
          lambda F: "-" if side(F) == "bottom" else "w", schatkist, "sprookjes", "6-9", 2, 30,
          ["Het vlak met het slot is de voorkant. De zijkanten hebben een schuin dekseltje: vouw de drie smalle vlakken daar netjes langs."])

# ======================= origami =======================
def arrow(sh, x1, y1, x2, y2, bend=-12, sw=1.6):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2; dx, dy = x2 - x1, y2 - y1; n = math.hypot(dx, dy)
    qx, qy = mx - dy / n * bend, my + dx / n * bend
    sh.line(f"M{f(x1)} {f(y1)}Q{f(qx)} {f(qy)} {f(x2)} {f(y2)}", "l", f"stroke-width:{sw}")
    ang = math.atan2(y2 - qy, x2 - qx)
    a1 = (x2 - 7 * math.cos(ang - .5), y2 - 7 * math.sin(ang - .5)); a2 = (x2 - 7 * math.cos(ang + .5), y2 - 7 * math.sin(ang + .5))
    sh.line(f"M{f(a1[0])} {f(a1[1])}L{f(x2)} {f(y2)}L{f(a2[0])} {f(a2[1])}", "l", f"stroke-width:{sw}")
def outline(sh, pts, sw=1.8): sh.line(P(pts), "l", f"stroke-width:{sw}")
def thin(sh, a, b, sw=1): sh.seg(*a, *b, "l", f"stroke-width:{sw}")
def crease(sh, a, b): sh.seg(*a, *b, "fold", "stroke-width:1.6;stroke-dasharray:3 3")
def turn(sh, x, y):
    """Omdraai-teken: rondje met pijl."""
    sh.line(f"M{f(x - 7)} {f(y)}A7 7 0 1 1 {f(x)} {f(y + 7)}", "l", "stroke-width:1.4")
    sh.line(f"M{f(x - 4)} {f(y + 4)}L{f(x)} {f(y + 7)}L{f(x - 3)} {f(y + 11)}", "l", "stroke-width:1.4")

def origami_page(slug, name, sub, paper, panels, steps, cat, age, diff, minutes, note, materials=None, holiday=None):
    """paper(sh): tekent het vouwpapier bovenaan; panels: lijst (tekenfunctie in 100x100, onderschrift)."""
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16); sh.text(100, 26, sub, 6)
    y_end = paper(sh)
    pw, ph_ = 46, 61; x0 = (200 - 4 * pw) / 2; y0 = y_end + 5
    for i, (draw, caption) in enumerate(panels):
        bx, by = x0 + (i % 4) * pw, y0 + (i // 4) * (ph_ + 2)
        sh.rect_line(bx + 1, by, pw - 2, ph_, "l", 3, "stroke-width:.6")
        sh.text(bx + 5, by + 8, str(i + 1), 7, "start", weight="800")
        sh.raw(f'<g transform="translate({f(bx + 4)} {f(by + 6)}) scale(.38)">'); draw(sh); sh.raw('</g>')
        for k, line in enumerate(caption.split(" | ")): sh.text(bx + pw / 2, by + 50 + k * 5.4, line, 4.7, weight="600")
    sh.legend(["cut", "fold"], 276)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "vouwblad", "difficulty": diff, "minutes": minutes, "holiday": holiday,
        "materials": materials or [SCHAAR, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": note, "steps": steps}}})

# --- waterbom (ballon) ---
WS = 160  # zijde van het denkbeeldige vierkant voor de diagrammen 4 tot en met 8
def wb(u, v, s=WS, base=90): return (50 + (u - s / 2), base - v)  # (u, v): u naar rechts, v omhoog vanaf de onderrand
def w1(sh):
    outline(sh, [(10, 10), (90, 10), (90, 90), (10, 90)]); crease(sh, (10, 10), (90, 90)); crease(sh, (90, 10), (10, 90))
    arrow(sh, 84, 84, 18, 18, -16)
def w2(sh):
    outline(sh, [(10, 10), (90, 10), (90, 90), (10, 90)]); crease(sh, (10, 50), (90, 50)); crease(sh, (50, 10), (50, 90))
    thin(sh, (10, 10), (90, 90), .6); thin(sh, (90, 10), (10, 90), .6)
    arrow(sh, 50, 16, 50, 84, 18); turn(sh, 84, 2)
def w3(sh):
    outline(sh, [(10, 10), (90, 10), (90, 90), (10, 90)]); crease(sh, (10, 10), (90, 90)); crease(sh, (90, 10), (10, 90))
    thin(sh, (10, 50), (90, 50), .8); thin(sh, (50, 10), (50, 90), .8)
    arrow(sh, 0, 50, 26, 50, 0); arrow(sh, 100, 50, 74, 50, 0); arrow(sh, 30, 6, 30, 44, -12); turn(sh, 84, 0)
def w4(sh):
    s = 88; T = lambda u, v: wb(u, v, s, 72)
    outline(sh, [T(0, 0), T(s, 0), T(s / 2, s / 2)]); thin(sh, T(s / 2, 0), T(s / 2, s / 2))
    crease(sh, T(s / 2, 0), T(s / 4, s / 4)); crease(sh, T(s / 2, 0), T(3 * s / 4, s / 4))
    arrow(sh, *T(6, 3), *T(s / 2 - 4, s / 2 - 8), 7); arrow(sh, *T(s - 6, 3), *T(s / 2 + 4, s / 2 - 8), -7)
def diamond(sh):
    s = WS; outline(sh, [wb(s / 2, 0), wb(s / 4, s / 4), wb(s / 2, s / 2), wb(3 * s / 4, s / 4)]); thin(sh, wb(s / 2, 0), wb(s / 2, s / 2))
def w5(sh):
    s = WS; diamond(sh)
    crease(sh, wb(3 * s / 8, s / 8), wb(3 * s / 8, 3 * s / 8)); crease(sh, wb(5 * s / 8, s / 8), wb(5 * s / 8, 3 * s / 8))
    arrow(sh, *wb(s / 4 + 3, s / 4 + 4), *wb(s / 2 - 4, s / 4 + 4), -10); arrow(sh, *wb(3 * s / 4 - 3, s / 4 + 4), *wb(s / 2 + 4, s / 4 + 4), 10)
def hexa(sh):
    s = WS
    outline(sh, [wb(s / 2, 0), wb(3 * s / 8, s / 8), wb(3 * s / 8, 3 * s / 8), wb(s / 2, s / 2), wb(5 * s / 8, 3 * s / 8), wb(5 * s / 8, s / 8)])
    thin(sh, wb(s / 2, 0), wb(s / 2, s / 2))
    for k in (1, -1):
        X = lambda u: s / 2 + k * (u - s / 2)
        outline(sh, [wb(X(3 * s / 8), s / 8), wb(X(s / 2), s / 4), wb(X(3 * s / 8), 3 * s / 8)], 1.2)
def w6(sh):
    s = WS; hexa(sh)
    crease(sh, wb(3 * s / 8, 3 * s / 8), wb(5 * s / 8, 3 * s / 8))
    arrow(sh, *wb(s / 2 - 8, s / 2 - 6), *wb(s / 2 - 8, s / 4 + 6), 9); arrow(sh, *wb(s / 2 + 8, s / 2 - 6), *wb(s / 2 + 8, s / 4 + 6), -9)
def w7(sh):
    s = WS
    outline(sh, [wb(s / 2, 0), wb(3 * s / 8, s / 8), wb(3 * s / 8, 3 * s / 8), wb(s / 2, s / 2), wb(5 * s / 8, 3 * s / 8), wb(5 * s / 8, s / 8)])
    thin(sh, wb(s / 2, 0), wb(s / 2, s / 4))
    for k in (1, -1):
        X = lambda u: s / 2 + k * (u - s / 2)
        outline(sh, [wb(X(3 * s / 8), s / 8), wb(X(s / 2), s / 4), wb(X(3 * s / 8), 3 * s / 8)], 1.2)
        outline(sh, [wb(X(3 * s / 8), 3 * s / 8), wb(X(s / 2), 3 * s / 8), wb(X(s / 2), s / 4)], 1.2)
        crease(sh, wb(X(3 * s / 8) + k * 1, 3 * s / 8 - 1), wb(X(s / 2) - k * 1, s / 4 + 1))
    arrow(sh, *wb(s / 2 - 22, s / 2 + 2), *wb(s / 2 - 12, s / 4 + 2), 12); arrow(sh, *wb(s / 2 + 22, s / 2 + 2), *wb(s / 2 + 12, s / 4 + 2), -12)
def w8(sh):
    s = WS
    outline(sh, [wb(s / 2, 20), wb(3 * s / 8 + 8, s / 8 + 14), wb(3 * s / 8 + 8, 3 * s / 8 + 4), wb(s / 2, s / 2), wb(5 * s / 8 - 8, 3 * s / 8 + 4), wb(5 * s / 8 - 8, s / 8 + 14)], 1.4)
    arrow(sh, 30, 98, 46, 72, 6)
    # bolle kubus
    sh.line(P([(66, 30), (84, 22), (100, 30), (82, 38)]), "l", "stroke-width:1.6"); sh.line(P([(66, 30), (82, 38), (82, 58), (66, 50)]), "l", "stroke-width:1.6"); sh.line(P([(82, 38), (100, 30), (100, 50), (82, 58)]), "l", "stroke-width:1.6")
def wb_paper(sh):
    sh.raw(f'<path class="r" style="stroke:none" d="{P([(52, 32), (148, 32), (148, 128), (52, 128)])}"/>', "b"); sh.rect_line(52, 32, 96, 96, "cut")
    sh.text(100, 84, "jouw vouwpapier", 6, cls="tip")
    return 128
origami_page("origami-waterbom", "Origami: waterbom", "Een papieren ballon die je opblaast tot een kubus.", wb_paper, [
    (w1, "diagonalen | vouwen"), (w2, "omdraaien, | dubbel vouwen"), (w3, "terugdraaien, | in elkaar duwen"), (w4, "punten naar | boven (2 kanten)"),
    (w5, "punten naar | het midden"), (w6, "puntjes | omlaag"), (w7, "in het zakje | stoppen"), (w8, "blazen!")], [
    "Knip het vierkant uit. Kleur het eerst als je wilt.",
    "Vouw het vierkant schuin dubbel, van hoek naar hoek, en vouw het weer open. Doe hetzelfde met de andere twee hoeken. Je ziet nu een kruis.",
    "Draai het papier om. Vouw het recht dubbel, rand op rand, en weer open. Doe dat ook de andere kant op.",
    "Draai het weer terug. Duw de linker- en rechterkant in het midden naar binnen en laat de bovenkant naar beneden vallen. Plat drukken: je hebt een driehoek met twee flappen voor en twee achter.",
    "Vouw de twee onderhoeken van de voorste flappen omhoog naar de bovenpunt. Draai om en doe het aan de achterkant ook: een ruit.",
    "Vouw de linker- en rechterpunt van de ruit naar het midden. Doe het aan de achterkant ook.",
    "Bovenaan zitten nu losse puntjes. Vouw ze naar beneden tot ze het midden raken.",
    "Stop die kleine driehoekjes in de zakjes van de driehoeken die je net naar het midden hebt gevouwen. Draai om en doe deze laatste twee stappen ook aan de achterkant.",
    "Onderaan zit een gaatje. Blaas er hard in: de waterbom wordt een bolle kubus! Duw de hoekjes voorzichtig recht."],
    "thuis", "9+", 3, 20, "Dun papier werkt het best: gewoon printpapier of vouwpapier, geen stevig papier.")

# --- springkikker ---
FA, FB = 1.0, 1.7
FSHIFT = [0.0]
def fr(u, v, k=52, top=6): return (50 - FA * k / 2 + u * k, top + (v - FSHIFT[0]) * k)
def lifted(fn):
    """Diagrammen 4-8 beginnen pas bij de driehoek: schuif ze omhoog."""
    def d(sh):
        FSHIFT[0] = FA / 2 - .05; fn(sh); FSHIFT[0] = 0.0
    return d  # (u, v): u naar rechts, v omlaag vanaf de bovenrand, in breedtes
def f1(sh):
    outline(sh, [fr(0, 0), fr(FA, 0), fr(FA, FB), fr(0, FB)]); crease(sh, fr(0, 0), fr(FA, FA)); crease(sh, fr(FA, 0), fr(0, FA))
    arrow(sh, *fr(.1, .05), *fr(.92, .85), 14)
def f2(sh):
    outline(sh, [fr(0, 0), fr(FA, 0), fr(FA, FB), fr(0, FB)]); thin(sh, fr(0, 0), fr(FA, FA), .6); thin(sh, fr(FA, 0), fr(0, FA), .6)
    crease(sh, fr(0, FA / 2), fr(FA, FA / 2)); arrow(sh, *fr(.5, .06), *fr(.5, .94), -14); turn(sh, 88, 0)
def f3(sh):
    outline(sh, [fr(0, 0), fr(FA, 0), fr(FA, FB), fr(0, FB)]); crease(sh, fr(0, 0), fr(FA, FA)); crease(sh, fr(FA, 0), fr(0, FA)); thin(sh, fr(0, FA / 2), fr(FA, FA / 2), .8)
    arrow(sh, fr(-.3, .5)[0], fr(0, .5)[1], *fr(.18, .5), 0); arrow(sh, fr(1.3, .5)[0], fr(0, .5)[1], *fr(.82, .5), 0); turn(sh, 88, 0)
def frog_tri(sh, s=1.0):
    outline(sh, [fr(0, FA), fr(FA / 2, FA / 2), fr(FA, FA)])
def f4(sh):
    frog_tri(sh); outline(sh, [fr(0, FA), fr(FA, FA), fr(FA, FB), fr(0, FB)]); thin(sh, fr(FA / 2, FA / 2), fr(FA / 2, FA))
    crease(sh, fr(FA / 2, FA), fr(FA / 4, 3 * FA / 4)); crease(sh, fr(FA / 2, FA), fr(3 * FA / 4, 3 * FA / 4))
    arrow(sh, *fr(.06, .96), *fr(.45, .56), 6); arrow(sh, *fr(.94, .96), *fr(.55, .56), -6)
def frog_head(sh):
    frog_tri(sh); outline(sh, [fr(FA / 2, FA), fr(FA / 4, 3 * FA / 4), fr(FA / 2, FA / 2), fr(3 * FA / 4, 3 * FA / 4)], 1.2); thin(sh, fr(FA / 2, FA / 2), fr(FA / 2, FA))
def f5(sh):
    frog_head(sh); outline(sh, [fr(0, FA), fr(FA, FA), fr(FA, FB), fr(0, FB)])
    crease(sh, fr(FA / 4, FA), fr(FA / 4, FB)); crease(sh, fr(3 * FA / 4, FA), fr(3 * FA / 4, FB))
    arrow(sh, *fr(.06, 1.4), *fr(.44, 1.4), -10); arrow(sh, *fr(.94, 1.4), *fr(.56, 1.4), 10)
def body(sh, bot):
    outline(sh, [fr(FA / 4, FA), fr(3 * FA / 4, FA), fr(3 * FA / 4, bot), fr(FA / 4, bot)]); thin(sh, fr(FA / 2, FA), fr(FA / 2, bot), .8)
def f6(sh):
    frog_head(sh); body(sh, FB); m = (FA + FB) / 2
    crease(sh, fr(FA / 4, m), fr(3 * FA / 4, m)); arrow(sh, *fr(.62, FB - .04), *fr(.62, FA + .06), -14)
def f7(sh):
    frog_head(sh); m = (FA + FB) / 2; body(sh, m); q = FA + (m - FA) / 2
    thin(sh, fr(FA / 4, FA + .03), fr(3 * FA / 4, FA + .03), 1.2)
    crease(sh, fr(FA / 4, q), fr(3 * FA / 4, q)); arrow(sh, *fr(.62, FA + .06), *fr(.62, m + .25), 14)
def f8(sh):
    m = (FA + FB) / 2; frog_tri(sh); outline(sh, [fr(FA / 4, FA), fr(3 * FA / 4, FA), fr(3 * FA / 4, m), fr(FA / 4, m)])
    for u in (.38, .62): sh.circle_line(*fr(u, .78), 4.5, "l", "stroke-width:1.4"); sh.dot(*fr(u, .78), 2)
    sh.line(f"M{f(fr(.4, .9)[0])} {f(fr(.4, .9)[1])}Q{f(fr(.5, .96)[0])} {f(fr(.5, .96)[1])} {f(fr(.6, .9)[0])} {f(fr(.6, .9)[1])}", "l", "stroke-width:1.2")
    arrow(sh, *fr(.5, m + .35), *fr(.5, m + .04), 0); sh.text(fr(.5, m + .2)[0] + 8, fr(.5, m + .2)[1] + 5, "duw", 13, "start", weight="600")
def frog_paper(sh):
    w, h = 62, 62 * FB; x = 100 - w / 2
    sh.raw(f'<path class="r" style="stroke:none" d="{P([(x, 32), (x + w, 32), (x + w, 32 + h), (x, 32 + h)])}"/>', "l"); sh.rect_line(x, 32, w, h, "cut")
    sh.text(100, 32 + h * .5, "jouw", 6, cls="tip"); sh.text(100, 32 + h * .5 + 7, "vouwpapier", 6, cls="tip")
    return 32 + h
origami_page("origami-springkikker", "Origami: springkikker", "Een kikker die echt springt als je op zijn rug duwt.", frog_paper, [
    (f1, "schuin vouwen, | twee kanten op"), (f2, "omdraaien, | recht vouwen"), (f3, "terugdraaien, | in elkaar duwen"), (lifted(f4), "punten naar | boven: voorpoten"),
    (lifted(f5), "zijkanten naar | het midden"), (lifted(f6), "onderkant | omhoog"), (lifted(f7), "half terug | omlaag"), (lifted(f8), "omdraaien | en springen!")], [
    "Knip de rechthoek uit. Kleur hem groen als je wilt.",
    "Vouw de linkerbovenhoek schuin naar de rechterkant en weer open. Doe hetzelfde met de rechterbovenhoek. Bovenin zie je nu een kruis.",
    "Draai het papier om. Vouw de bovenrand omlaag tot de onderkant van het kruis en weer open: de vouw gaat precies door het midden van het kruis.",
    "Draai terug. Duw de zijkanten bij die vouw naar binnen en laat de bovenkant naar beneden vallen. Plat drukken: bovenop ligt nu een driehoek.",
    "Vouw de twee onderste punten van de driehoek (alleen de bovenste laag) omhoog naar de top: dat zijn de voorpoten.",
    "Vouw de linker- en rechterkant van het lijfje naar het midden. Schuif ze een beetje onder de driehoek.",
    "Vouw de onderrand omhoog tot aan de onderkant van de driehoek.",
    "Vouw dezelfde flap weer half terug omlaag, zodat er een zigzag ontstaat: dat is de springveer.",
    "Draai de kikker om en teken ogen. Duw met je vinger op de achterkant, laat snel los … en hup, hij springt!"],
    "dieren", "6-9", 2, 15, "Gewoon printpapier werkt; met iets steviger papier (120 gram) springt hij verder.")
