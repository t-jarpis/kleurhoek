"""Bouwplaten van veelvlakken: 3D-model -> uitslag (net) met vouwlijnen en lijmflappen.

De uitslag wordt berekend uit het 3D-model, dus aansluitende randen kloppen altijd: elk paar randen dat
na het vouwen samenkomt krijgt precies één lijmflap. Overlap in de uitslag of van flappen wordt
gecontroleerd met shapely.
"""
import math, itertools
from collections import deque
from shapely.geometry import Polygon
from shapely.ops import unary_union
from kit import f

def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def norm(a): return math.sqrt(dot(a, a))
def scale(a, s): return tuple(x * s for x in a)

def _edge_faces(faces):
    ef = {}
    for fi, fc in enumerate(faces):
        for i in range(len(fc)):
            ef.setdefault(frozenset((fc[i], fc[(i + 1) % len(fc)])), []).append(fi)
    assert all(len(v) == 2 for v in ef.values()), "niet gesloten"
    return ef

def _tree(faces, ef, root, order=None, dfs=False, rng=None):
    """Opspannende boom over de vlakken: lijst (ouder, kind, rand) in plaatsingsvolgorde."""
    def nbrs(p):
        pf = faces[p]; out = []
        for i in range(len(pf)):
            ed = frozenset((pf[i], pf[(i + 1) % len(pf)]))
            out += [(ch, ed) for ch in ef[ed] if ch != p]
        if order: out.sort(key=lambda t: order(p, t[0]))
        if rng: rng.shuffle(out)
        return out
    seen = {root}; tree = []
    if dfs:
        stack = [root]
        while stack:
            p = stack[-1]
            nxt = next(((ch, ed) for ch, ed in nbrs(p) if ch not in seen), None)
            if nxt is None: stack.pop(); continue
            ch, ed = nxt; seen.add(ch); tree.append((p, ch, ed)); stack.append(ch)
    else:
        q = deque([root])
        while q:
            p = q.popleft()
            for ch, ed in nbrs(p):
                if ch in seen: continue
                seen.add(ch); tree.append((p, ch, ed)); q.append(ch)
    assert len(seen) == len(faces)
    return tree

def unfold(verts, faces, root=0, order=None, dfs=False, rng=None):
    """Geeft {vlak: {hoekpunt: 2D-punt}}, de boomranden en rand->vlakken."""
    ef = _edge_faces(faces)
    fc = faces[root]; a, b = verts[fc[0]], verts[fc[1]]
    e = scale(sub(b, a), 1 / norm(sub(b, a)))
    c = verts[fc[2]]; w = sub(sub(c, a), scale(e, dot(sub(c, a), e))); w = scale(w, 1 / norm(w))
    pos = {root: {v: (dot(sub(verts[v], a), e), dot(sub(verts[v], a), w)) for v in fc}}
    tree = _tree(faces, ef, root, order, dfs, rng)
    for p, ch, ed in tree:
        va, vb = tuple(ed); pf = faces[p]
        A, B = pos[p][va], pos[p][vb]
        a3, b3 = verts[va], verts[vb]
        e3 = scale(sub(b3, a3), 1 / norm(sub(b3, a3)))
        u = ((B[0] - A[0]) / math.dist(A, B), (B[1] - A[1]) / math.dist(A, B))
        pc = (sum(pos[p][v][0] for v in pf) / len(pf), sum(pos[p][v][1] for v in pf) / len(pf))
        perp = (-u[1], u[0])
        if (pc[0] - A[0]) * perp[0] + (pc[1] - A[1]) * perp[1] > 0: perp = (-perp[0], -perp[1])
        pos[ch] = {}
        for v in faces[ch]:
            d = sub(verts[v], a3); along = dot(d, e3); off = norm(sub(d, scale(e3, along)))
            pos[ch][v] = (A[0] + u[0] * along + perp[0] * off, A[1] + u[1] * along + perp[1] * off)
    return pos, tree, ef

def net_polys(faces, pos):
    return [[pos[i][v] for v in fc] for i, fc in enumerate(faces)]

def no_overlap(polys, tol=1e-3):
    ps = [Polygon(p) for p in polys]
    return abs(sum(p.area for p in ps) - unary_union(ps).area) < tol * max(1, sum(p.area for p in ps))

def tab_poly(p, q, inside, depth, shrink=.25):
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    if (inside[0] - mx) * nx + (inside[1] - my) * ny > 0: nx, ny = -nx, -ny
    s = min(shrink, depth / L * 1.0) if shrink <= .25 else shrink
    a = (p[0] + dx * s + nx * depth, p[1] + dy * s + ny * depth); b = (q[0] - dx * s + nx * depth, q[1] - dy * s + ny * depth)
    return [p, a, b, q]

def layout(verts, faces, root=0, order=None, depth=0.18, dfs=False, rng=None):
    """Uitslag + flappen; geeft (faces2d, tabs2d, folds, cuts) in modelmaat. Gooit fout bij overlap."""
    pos, tree, edge_faces = unfold(verts, faces, root, order, dfs, rng)
    polys = net_polys(faces, pos)
    assert no_overlap(polys), "uitslag overlapt"
    tree_edges = {t[2] for t in tree}
    mean_edge = sum(math.dist(pos[i][fc[k]], pos[i][fc[(k + 1) % len(fc)]]) for i, fc in enumerate(faces) for k in range(len(fc))) / sum(len(fc) for fc in faces)
    d = depth * mean_edge
    folds, cuts, tabs = [], [], []
    union = unary_union([Polygon(p) for p in polys])
    for ed, (f1, f2) in edge_faces.items():
        v1, v2 = tuple(ed)
        if ed in tree_edges:
            folds.append((pos[f1][v1], pos[f1][v2])); continue
        # randpaar: probeer de flap aan f1, anders aan f2, zonder overlap met de rest of andere flappen
        placed = False
        for fa, dd, sk in [(fa, dd, sk) for dd, sk in ((d, .25), (d * .7, .38), (d * .5, .45), (d * .35, .45)) for fa in (max(f1, f2), min(f1, f2))]:
            P, Q = pos[fa][v1], pos[fa][v2]
            cen = (sum(x for x, _ in polys[fa]) / len(polys[fa]), sum(y for _, y in polys[fa]) / len(polys[fa]))
            tp = tab_poly(P, Q, cen, dd, sk)
            tpoly = Polygon(tp)
            if placed: break
            if tpoly.intersection(union).area < 1e-6 and all(tpoly.intersection(Polygon(t)).area < 1e-6 for t, _ in tabs):
                tabs.append((tp, fa)); folds.append((P, Q))
                other = f2 if fa == f1 else f1
                cuts.append((pos[other][v1], pos[other][v2])); placed = True; break
        assert placed, "geen plek voor een lijmflap"
    return polys, [t for t, _ in tabs], folds, cuts

def search(verts, faces, tries=4000, seed=1, depth=0.18):
    """Zoekt een uitslag zonder overlap: eerst de gewone (BFS vanaf elk vlak), daarna willekeurige DFS-bomen."""
    import random
    rng = random.Random(seed)
    for t in range(tries):
        if t < len(faces): args = dict(root=t)
        else: args = dict(root=rng.randrange(len(faces)), dfs=t % 2 == 0, rng=random.Random(rng.random()))
        try:
            return layout(verts, faces, depth=depth, **args), args
        except AssertionError:
            continue
    raise AssertionError("geen uitslag gevonden")

def draw(sh, verts, faces, codes, box, root=0, order=None, depth=0.18, find=False):
    """Tekent de uitslag geschaald in box (x, y, w, h). Geeft de schaal en de vlakken (in velmaat) terug."""
    if find: (polys, tabs, folds, cuts), _ = search(verts, faces, depth=depth)
    else: polys, tabs, folds, cuts = layout(verts, faces, root, order, depth)
    allp = [p for poly in polys + tabs for p in poly]
    mnx, mxx = min(x for x, _ in allp), max(x for x, _ in allp); mny, mxy = min(y for _, y in allp), max(y for _, y in allp)
    bx, by, bw, bh = box
    rot = (mxx - mnx) < (mxy - mny) and bw > bh or (mxx - mnx) > (mxy - mny) and bh > bw
    tr = (lambda p: (p[1], p[0])) if rot else (lambda p: p)
    if rot: mnx, mxx, mny, mxy = mny, mxy, mnx, mxx
    sc = min(bw / (mxx - mnx), bh / (mxy - mny))
    ox = bx + (bw - (mxx - mnx) * sc) / 2; oy = by + (bh - (mxy - mny) * sc) / 2
    T = lambda p: (ox + (tr(p)[0] - mnx) * sc, oy + (tr(p)[1] - mny) * sc)
    for poly, code in zip(polys, codes):
        d = "M" + " L".join(f"{f(T(p)[0])} {f(T(p)[1])}" for p in poly) + "Z"
        sh.raw(f'<path class="r" style="stroke:none" d="{d}"/>', code)
    for tp in tabs:
        d = "M" + " L".join(f"{f(T(p)[0])} {f(T(p)[1])}" for p in tp)
        sh.raw(f'<path class="glue" d="{d}Z"/>'); sh.line(d, "cut")
    for a, b in folds: sh.seg(*T(a), *T(b), "fold")
    for a, b in cuts: sh.seg(*T(a), *T(b), "cut")
    return sc, [[T(p) for p in poly] for poly in polys]

# ---------- modellen ----------
def prism(n, r=1.0, h=1.5):
    verts = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), 0) for k in range(n)] + \
            [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), h) for k in range(n)]
    faces = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))] + [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    return verts, faces
def pyramid(n, r=1.0, h=1.5):
    verts = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), 0) for k in range(n)] + [(0, 0, h)]
    faces = [list(range(n - 1, -1, -1))] + [[k, (k + 1) % n, n] for k in range(n)]
    return verts, faces
def frustum(n, r1=1.0, r2=.6, h=1.0):
    verts = [(r1 * math.cos(2 * math.pi * k / n + math.pi / n), r1 * math.sin(2 * math.pi * k / n + math.pi / n), 0) for k in range(n)] + \
            [(r2 * math.cos(2 * math.pi * k / n + math.pi / n), r2 * math.sin(2 * math.pi * k / n + math.pi / n), h) for k in range(n)]
    faces = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))] + [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    return verts, faces
def bipyramid(n, r=1.0, h=1.2):
    verts = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), 0) for k in range(n)] + [(0, 0, h), (0, 0, -h)]
    faces = [[k, (k + 1) % n, n] for k in range(n)] + [[(k + 1) % n, k, n + 1] for k in range(n)]
    return verts, faces
def antiprism(n, r=1.0):
    h = math.sqrt(max(0.0, (2 * r * math.sin(math.pi / n)) ** 2 - (2 * r * math.sin(math.pi / (2 * n))) ** 2 * 1.0 + 0)) if False else None
    s = 2 * r * math.sin(math.pi / n)  # zijde
    # hoogte zodat de driehoeken gelijkzijdig zijn
    d2 = (r * math.cos(0) - r * math.cos(math.pi / n)) ** 2 + (0 - r * math.sin(math.pi / n)) ** 2
    h = math.sqrt(s * s - d2)
    verts = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), 0) for k in range(n)] + \
            [(r * math.cos(2 * math.pi * k / n + math.pi / n), r * math.sin(2 * math.pi * k / n + math.pi / n), h) for k in range(n)]
    faces = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
    for k in range(n):
        faces.append([k, (k + 1) % n, n + k]); faces.append([(k + 1) % n, n + (k + 1) % n, n + k])
    return verts, faces
def cuboctahedron():
    verts = []
    for a, b in itertools.product((1, -1), repeat=2):
        verts += [(a, b, 0), (a, 0, b), (0, a, b)]
    return hull_faces(verts)
def truncated_tetrahedron():
    base = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    verts = []
    for i, p in enumerate(base):
        for j, q in enumerate(base):
            if i != j: verts.append(tuple(p[k] * 2 / 3 + q[k] / 3 for k in range(3)))
    return hull_faces(verts)
def hull_faces(verts):
    """Vlakken van het convexe omhulsel (kleine modellen): groepeer punten op steunvlakken."""
    n = len(verts); faces = set(); out = []
    cen = tuple(sum(v[k] for v in verts) / n for k in range(3))
    for i, j, k in itertools.combinations(range(n), 3):
        a, b, c = verts[i], verts[j], verts[k]
        nrm = (lambda u, v: (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]))(sub(b, a), sub(c, a))
        if norm(nrm) < 1e-9: continue
        side = [dot(sub(v, a), nrm) for v in verts]
        if all(s <= 1e-9 for s in side) or all(s >= -1e-9 for s in side):
            on = tuple(sorted(m for m, s in enumerate(side) if abs(s) < 1e-9))
            if on in faces: continue
            faces.add(on)
            if dot(sub(cen, a), nrm) > 0: nrm = scale(nrm, -1)
            fc = [verts[m] for m in on]; fcen = tuple(sum(v[q] for v in fc) / len(fc) for q in range(3))
            e1 = sub(fc[0], fcen); e1 = scale(e1, 1 / norm(e1)); e2 = (lambda u, v: (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]))(nrm, e1); e2 = scale(e2, 1 / norm(e2))
            ordered = sorted(on, key=lambda m: math.atan2(dot(sub(verts[m], fcen), e2), dot(sub(verts[m], fcen), e1)))
            out.append(ordered)
    return verts, out
