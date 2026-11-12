"""Resultaatplaatje "Zo wordt het" bij bouwplaten (ADR 0100).

Een kleine lijntekening van het in elkaar gezette werkstuk in een eenvoudig 3/4-aanzicht, licht ingekleurd met de
kleuren van het ingekleurde voorbeeld (de kleurcodes van de plaat). Het plaatje staat in een hoek van een vel als
geneste `<svg class="kh-result">` met een eigen viewBox, met het label "Zo wordt het" erboven (vertaald via de
woordenlijst, ADR 0029). De website haalt het daar uit voor het blok "Zo wordt het" op de plaatpagina.

Het plaatje is geen kleurvlak: hier wordt elk `class="r"` omgezet naar een lijn met een vaste vulkleur, zodat het
niet meetelt in de vlakken, kleur-op-nummer of online kleuren.

Gebruik:
    cam = Camera(yaw=-32, pitch=26)
    def build(rs, s):                       # s = mm per eenheid van het model
        cam.s = s
        solid(rs, cam, model, codes_fn, draw_face)  # vlakken van een (convex) model, met de tekening van de uitslag
    place_result(sh, (x, y, w, h), build)    # past het plaatje in het kader, met label en dunne rand

Op het vel: `<g class="kh-result-box">` met kader, label en plaatje; check.mjs controleert dat daar niets van de
uitslag in ligt. Het kader is minstens 44 mm breed, zodat een langere vertaling van het label erin past.

`draw_face(sh, F)` is dezelfde functie die de uitslag tekent (lokale coördinaten, F.w, F.h, F.n, F.sc …): het
vlak wordt met een affiene afbeelding op zijn plek in het aanzicht gezet, dus de versiering klopt altijd met de
uitslag. Een plat onderdeel (Piet achter de schoorsteen) gaat met `flat()`; vrije vormen met `poly()`.
"""
import json, math, os, re
from lib_gen import Sheet, f
import polyhedra as ph

LABEL = "Zo wordt het"
_COLORS = os.path.join(os.path.dirname(__file__), "..", "..", "..", "packages", "catalog-data", "colors.json")
HEX = {c["code"]: c["hex"] for c in json.load(open(_COLORS))}
HEX["-"] = "#ffffff"
HEX["h"] = "#ffe8d8"  # lichte huid (oranje o, flink naar wit): alleen in het plaatje, geen kleurcode van platen
SHADE = "#222222"  # zelfde zwart als de kleurcode x; als dunne schaduw over vlakken die van het licht af staan


def g(v):
    """Getal met vier decimalen (voor transformaties; f() rondt af op één)."""
    return f"{v:.4f}".rstrip("0").rstrip(".") or "0"
def P(points): return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in points) + "Z"
def cross(u, v): return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
def unit(v): n = ph.norm(v); return tuple(x / n for x in v)


class Camera:
    """Parallelle projectie: eerst om de verticale as draaien (yaw, graden; negatief = rechterkant zichtbaar),
    dan van boven kijken (pitch). Model: z omhoog, voorkant = -y. Scherm: x naar rechts, y naar beneden, in mm."""
    def __init__(self, yaw=-32, pitch=26, s=1.0):
        self.yaw, self.pitch, self.s = yaw, pitch, s
        a, b = math.radians(yaw), math.radians(pitch)
        self.ca, self.sa, self.cb, self.sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
    def _r(self, p):
        x, y, z = p
        return x * self.ca - y * self.sa, x * self.sa + y * self.ca, z
    def lin(self, v):
        """Richting (zonder schaal) op het scherm."""
        x1, y1, z = self._r(v)
        return x1, -(y1 * self.sb + z * self.cb)
    def xy(self, p):
        x, y = self.lin(p); return x * self.s, y * self.s
    def depth(self, p):
        x1, y1, z = self._r(p); return y1 * self.cb - z * self.sb
    def sees(self, n):
        return self.depth(n) < -1e-9
    def light(self, n):
        """Hoeveel schaduw een vlak krijgt: licht van linksboven-voor."""
        L = unit((-.45, -.55, .7)); d = ph.dot(unit(n), L)
        return 0 if d > .55 else .1 if d > .1 else .18


class ResultSheet(Sheet):
    """Sheet voor het plaatje: onthoudt de omtrek (voor de viewBox) en zet vlakken om naar vaste kleuren."""
    def __init__(self):
        super().__init__(); self.pts = []
    def track(self, pts): self.pts += [tuple(map(float, p)) for p in pts]
    def text(self, *a, **k): pass  # tekst is op dit formaat onleesbaar (en zou niet vertaald op het plaatje staan)
    def tip(self, *a, **k): pass
    def bbox(self, m=1.2):
        xs = [p[0] for p in self.pts]; ys = [p[1] for p in self.pts]
        return min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m
    def body(self, light=0.0):
        """Alle onderdelen, met elk vlak als lijn met vulkleur (geen class="r": telt niet als kleurvlak)."""
        codes = iter(self.codes)
        def col(code):
            h = HEX[code]
            if not light or code == "-": return h
            r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
            return "#" + "".join(f"{round(c + (255 - c) * light):02x}" for c in (r, g, b))
        out = []
        for part in self.parts:
            def rep(m):
                tag = m.group(0); fill = col(next(codes))
                if ' style="' in tag: return tag.replace('class="r"', 'class="l"').replace(' style="', f' style="fill:{fill};', 1)
                return tag.replace('class="r"', f'class="l" style="fill:{fill}"')
            part = re.sub(r'<(?:path|circle|ellipse|rect|polygon)\b[^>]*class="r"[^>]*>', rep, part)
            # lijnen van de uitslag die op het werkstuk geen lijn meer zijn
            part = part.replace('class="cut"', 'class="l"')
            out.append(part)
        assert next(codes, None) is None, "kleurcodes en vlakken lopen niet gelijk"
        s = "".join(out)
        assert 'class="r"' not in s and "<text" not in s
        return s


class Face:
    pass


def face_frame(verts, fc, sc, idx=0):
    """Lokaal assenstelsel van een vlak zoals build_net het gebruikt (x naar rechts, y naar beneden, van buiten)."""
    V = [verts[v] for v in fc]
    n = unit(cross(ph.sub(V[1], V[0]), ph.sub(V[2], V[0])))
    if abs(n[2]) > .95: up = (0, 1, 0)
    else: up = unit(ph.sub((0, 0, 1), ph.scale(n, n[2])))
    right = cross(up, n)
    fcen = tuple(sum(v[k] for v in V) / len(V) for k in range(3))
    lr = [ph.dot(ph.sub(v, fcen), right) for v in V]; lu = [ph.dot(ph.sub(v, fcen), up) for v in V]
    cr, cu = (max(lr) + min(lr)) / 2, (max(lu) + min(lu)) / 2
    F = Face(); F.n = n; F.idx = idx; F.sc = sc; F.z = fcen[2]
    F.c3 = tuple(fcen[k] + right[k] * cr + up[k] * cu for k in range(3))
    F.w = (max(lr) - min(lr)) * sc; F.h = (max(lu) - min(lu)) * sc
    F.poly = [((a - cr) * sc, -(b - cu) * sc) for a, b in zip(lr, lu)]
    F.right, F.up, F.V = right, up, V
    return F


def plane(rs, cam, origin, right, down, draw, style=None):
    """Teken `draw(rs)` in een vlak: lokale (a, b) in mm wordt origin + right*a + down*b (3D, per mm)."""
    ox, oy = cam.xy(origin)
    rx, ry = cam.lin(right); dx, dy = cam.lin(down)
    rx, ry, dx, dy = rx * cam.s, ry * cam.s, dx * cam.s, dy * cam.s
    st = f' style="{style}"' if style else ""
    m = " ".join(g(v) for v in (rx, ry, dx, dy, ox, oy))
    rs.raw(f'<g transform="matrix({m})"{st}>')
    draw(rs)
    rs.raw('</g>')


def solid(rs, cam, model, codes_fn, draw_face=None, offset=(0, 0, 0), shade=True, style="--sw:.8"):
    """De zichtbare vlakken van een convex model, van achter naar voor, met de tekening van de uitslag erop."""
    verts, faces = model
    verts = [tuple(v[k] + offset[k] for k in range(3)) for v in verts]
    s = cam.s
    fs = [face_frame(verts, fc, s, i) for i, fc in enumerate(faces)]
    order = sorted((F for F in fs if cam.sees(F.n)), key=lambda F: -cam.depth(F.c3))
    for F in order:
        pts = [cam.xy(v) for v in F.V]
        rs.track(pts)
        rs.raw(f'<path class="r" style="stroke:none" d="{P(pts)}"/>', codes_fn(F))
        if draw_face:
            down = ph.scale(F.up, -1 / s); right = ph.scale(F.right, 1 / s)
            plane(rs, cam, F.c3, right, down, lambda r: draw_face(r, F), style)
        if shade and cam.light(F.n):
            rs.raw(f'<path d="{P(pts)}" style="fill:{SHADE};fill-opacity:{cam.light(F.n)};stroke:none"/>')
        rs.line(P(pts), "l")
    return fs


def poly(rs, cam, pts3, code, outline=True, shade=0):
    """Een vlak gegeven als 3D-punten (vrije vormen zoals de band van de schoen)."""
    pts = [cam.xy(p) for p in pts3]
    rs.track(pts)
    rs.raw(f'<path class="r"{"" if outline else " style=\"stroke:none\""} d="{P(pts)}"/>', code)
    if shade: rs.raw(f'<path d="{P(pts)}" style="fill:{SHADE};fill-opacity:{shade};stroke:none"/>')
    return pts


def flat(rs, cam, origin, right, down, draw, outline_pts=None):
    """Een plat onderdeel (karton) in een verticaal vlak; outline_pts (lokaal, mm) telt mee voor de viewBox."""
    plane(rs, cam, origin, right, down, draw)
    if outline_pts:
        rs.track([cam.xy(tuple(origin[k] + right[k] * a + down[k] * b for k in range(3))) for a, b in outline_pts])


def place_result(sh, box, build, label=LABEL, sw=1.2, light=0.0, pad=3, label_size=6):
    """Zet het plaatje in een kader (x, y, w, h) op het vel: dunne grijze rand, label erboven, tekening gecentreerd.
    build(rs, s) tekent met s mm per eenheid; eerst op s = 1 voor de maat, daarna op de schaal die past."""
    x, y, w, h = box
    rs = ResultSheet(); build(rs, 1.0)
    bx0, by0, bx1, by1 = rs.bbox(0)
    top = label_size + 3.5
    k = min((w - 2 * pad) / (bx1 - bx0), (h - top - pad) / (by1 - by0))
    rs = ResultSheet(); build(rs, k)
    bx0, by0, bx1, by1 = rs.bbox(sw)
    bw, bh = bx1 - bx0, by1 - by0
    ix = x + (w - bw) / 2; iy = y + top + (h - top - pad - bh) / 2 + pad / 2
    sh.raw('<g class="kh-result-box">')
    sh.rect_line(x, y, w, h, "guide", 3)
    sh.text(x + w / 2, y + label_size + 1.5, label, label_size, weight="800")
    sh.raw(f'<svg class="kh-result" x="{f(ix)}" y="{f(iy)}" width="{f(bw)}" height="{f(bh)}" viewBox="{f(bx0)} {f(by0)} {f(bw)} {f(bh)}" style="--sw:{sw}">'
           + rs.body(light) + '</svg>')
    sh.raw('</g>')
    return (ix, iy, bw, bh)
