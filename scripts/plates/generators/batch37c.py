"""Batch 37c: pop-upkaarten, kaarten met flapjes, vormkaarten, uitnodigingen, bedankjes, decoraties en cadeautjes (eigen ontwerpen)."""
import math
from lib_gen import *
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from shapely import affinity
from shapes import heart_path, moon_path, drop_path, cloud_path, leaf_path, fish_path

ONLY = os.environ.get("ONLY")

def P(points):
    return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in points) + "Z"
def rot(sh, deg, x, y): sh.raw(f'<g transform="rotate({f(float(deg))} {f(float(x))} {f(float(y))})">')
def end(sh): sh.raw("</g>")
def stars(sh, pts, r=5, code="y"):
    for x, y in pts: sh.poly_r(star_pts(x, y, r, r * .44), code)
def balloon(sh, x, y, s, code, string=True):
    sh.region(f"M{f(x)} {f(y + s*1.2)}C{f(x - s*1.2)} {f(y + s*.4)} {f(x - s)} {f(y - s*1.2)} {f(x)} {f(y - s*1.2)}C{f(x + s)} {f(y - s*1.2)} {f(x + s*1.2)} {f(y + s*.4)} {f(x)} {f(y + s*1.2)}Z", code)
    sh.poly_r([(x, y + s * 1.2), (x - s * .2, y + s * 1.45), (x + s * .2, y + s * 1.45)], code)
    if string: sh.line(f"M{f(x)} {f(y + s*1.45)}Q{f(x + s*.4)} {f(y + s*2.2)} {f(x - s*.1)} {f(y + s*3)}", "l", "stroke-width:1")
def flower(sh, x, y, r, petal, heart="y", n=5):
    for k in range(n):
        a = math.radians(k * 360 / n - 90)
        sh.circle_r(x + r * math.cos(a), y + r * math.sin(a), r * .72, petal)
    sh.circle_r(x, y, r * .6, heart)
def confetti(sh, pts):
    for i, (x, y) in enumerate(pts):
        if i % 3 == 0: sh.seg(x - 2.5, y - 2, x + 2.5, y + 2, "l", "stroke-width:1.2")
        elif i % 3 == 1: sh.circle_line(x, y, 1.6, "l", "stroke-width:1")
        else: sh.line(f"M{x - 3} {y}Q{x - 1.5} {y - 2.5} {x} {y}T{x + 3} {y}", "l", "stroke-width:1")
def bunting(sh, x1, x2, y, sag, n, codes, size=6):
    sh.line(f"M{x1} {y}Q{(x1 + x2) / 2} {y + 2 * sag} {x2} {y}", "l", "stroke-width:1")
    for i in range(n):
        t = (i + .5) / n; x = x1 + (x2 - x1) * t; yy = y + 2 * sag * t * (1 - t)
        sh.poly_r([(x - size, yy), (x + size, yy), (x, yy + size * 1.8)], codes[i % len(codes)])
def ring_d(coords):
    c = list(coords)[:-1]
    return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in c) + "Z"
def geom_d(g):
    gs = list(g.geoms) if hasattr(g, "geoms") else [g]
    return "".join(ring_d(p.exterior.coords) + "".join(ring_d(i.coords) for i in p.interiors) for p in gs)
def hole(sh, x, y, r=2.2):
    sh.circle_line(x, y, r, "cut", "stroke-dasharray:1.6 1.2")
def glue_rect(sh, x, y, w, h):
    sh.raw(f'<rect class="glue" x="{f(float(x))}" y="{f(float(y))}" width="{f(float(w))}" height="{f(float(h))}"/>')
def glue_path(sh, d):
    sh.raw(f'<path class="glue" d="{d}"/>')
def lines(sh, x1, x2, y, n, gap):
    for k in range(n): sh.seg(x1, y + k * gap, x2, y + k * gap, "guide")
def do(fn):
    if not ONLY or ONLY in fn.__name__: fn()
    return fn

KAART_MAT = [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "stiften", "optional": True}, {"slug": "stevig-papier", "optional": True}]
STEVIG = "Print op stevig papier (160 gram) als je het hebt; gewoon papier kan ook."

class Fig:
    """Figuur om uit te knippen: tekent kleurvlakken en onthoudt de buitenvorm."""
    def __init__(self, sh): self.sh = sh; self.g = []
    def circle(self, x, y, r, code): self.sh.circle_r(x, y, r, code); self.g.append(Point(x, y).buffer(r, 48))
    def ellipse(self, x, y, rx, ry, code): self.sh.ellipse_r(x, y, rx, ry, code); self.g.append(affinity.scale(Point(x, y).buffer(1, 48), rx, ry))
    def rect(self, x, y, w, h, code, rx=0): self.sh.rect_r(x, y, w, h, code, rx); self.g.append(box(x, y, x + w, y + h))
    def poly(self, pts, code): self.sh.poly_r(pts, code); self.g.append(Polygon(pts).buffer(0))
    def geom(self, g, code): self.sh.region(geom_d(g), code); self.g.append(g)
    def outline(self, pad=2.5): return unary_union(self.g).buffer(pad, join_style=1).simplify(.3)

def heart_geom(cx, cy, s, n=80):
    """Hartvorm als veelhoek (zelfde vorm als heart_path)."""
    k = s / 10
    def bez(p0, p1, p2, p3, t):
        return tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))
    A = (cx, cy + 9 * k); B = (cx, cy - 4 * k)
    pts = [bez(A, (cx - 13 * k, cy), (cx - 9 * k, cy - 10 * k), B, i / n) for i in range(n)]
    pts += [bez(B, (cx + 9 * k, cy - 10 * k), (cx + 13 * k, cy), A, i / n) for i in range(n)]
    return Polygon(pts).buffer(0)

# =====================================================================
# 1. POP-UPKAARTEN (doosjesmechanisme: twee sneetjes loodrecht op de vouw)
# =====================================================================
#
# De kaart gaat open als een laptop: de bovenste helft wordt de achterwand, de onderste helft de vloer.
# Tussen twee sneetjes (lengte a, loodrecht op de vouw) ligt een strookje. Dat strookje wordt
# naar binnen geduwd en vormt een trapje: het stuk boven de vouw wordt het bovenvlak, het stuk
# onder de vouw (tussen de vouw en de onderste rillijn) wordt het voorvlak, rechtop en naar de kijker.
# Op dat voorvlak (grijs) plak je de figuur. Een punt op afstand t onder de vouw komt op hoogte a - t:
# een figuur die rechtop op het vel staat, staat ook rechtop in de kaart.
# Dicht ligt het voorvlak plat tussen t = a en t = 2a; een figuur die h hoger is dan het voorvlak
# reikt dan tot 2a + h. Dat moet binnen de kaarthelft blijven: 2a + h <= H/2 - marge.

POP_X0, POP_X1, POP_TOP, POP_H2 = 14, 186, 22, 84
POP_YF = POP_TOP + POP_H2

def popup(slug, name, sw, a, wall, floor, figure, fig_name, cat, age, extra_steps, holiday=None, title_txt=None):
    dit = "dit" if fig_name in ("hart", "monster") else "deze"
    sh = Sheet()
    title(sh, title_txt or "Pop-upkaart", 13, 10)
    cx, yf = 100, POP_YF
    x0, x1, top, bot = POP_X0, POP_X1, POP_TOP, POP_YF + POP_H2
    # achterwand en vloer
    wall(sh, cx, yf, top, a, sw)
    floor(sh, cx, yf, bot, a, sw)
    # voorvlak van het strookje: hier komt de figuur
    glue_rect(sh, cx - sw / 2 + 1.5, yf + 1.5, sw - 3, a - 3)
    sh.text(cx, yf + a / 2 + 2, "plak hier", 4.8)
    # lijnen
    sh.rect_line(x0, top, x1 - x0, bot - top, "cut", 3)
    for xs in (cx - sw / 2, cx + sw / 2):
        sh.seg(xs, yf - a, xs, yf + a, "cut")                     # sneetjes: loodrecht op de vouw
    sh.seg(x0, yf, cx - sw / 2, yf, "fold"); sh.seg(cx + sw / 2, yf, x1, yf, "fold")
    sh.seg(cx - sw / 2, yf, cx + sw / 2, yf, "fold", "stroke-width:1.1;stroke-dasharray:1 2.5")
    sh.seg(cx - sw / 2, yf - a, cx + sw / 2, yf - a, "fold"); sh.seg(cx - sw / 2, yf + a, cx + sw / 2, yf + a, "fold")
    # de figuur, los uit te knippen
    fy = 266
    sh.tip(16, bot + 9, "Knip " + dit + " " + fig_name + " uit en plak hem op het grijze vlakje:")
    fg = Fig(sh)
    figure(fg, cx, fy)
    out = fg.outline()
    sh.line(geom_d(out), "cut")
    minx, miny, maxx, maxy = unary_union(fg.g).bounds
    hfig = fy - miny
    assert abs(maxy - fy) < .6, (slug, "figuur moet plat op de vloer staan", maxy)
    assert 2 * a + (hfig - a) <= POP_H2 - 3, (slug, "figuur steekt uit de dichte kaart", 2 * a + hfig - a)
    assert hfig > a and maxx - minx >= sw, (slug, "figuur dekt het voorvlak niet")
    assert out.bounds[1] > bot + 11 and out.bounds[3] < 270 and out.bounds[0] > 3 and out.bounds[2] < 197, (slug, out.bounds)
    sh.legend(["cut", "fold", "glue"], 279)
    meta = {"category": cat, "age": age, "kind": "kaart", "difficulty": 3, "minutes": 35, "adultHelp": True, "paperGsm": 160,
            "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "stevig-papier", "optional": True}],
            "i18n": {"nl": {"name": name, "printNote": "Op stevig papier (160 gram) springt het pop-upje het mooist naar voren.", "steps": [
                "Kleur de binnenkant van de kaart en " + ("het " if dit == "dit" else "de ") + fig_name + " in.",
                "Knip de kaart uit langs de buitenste streepjeslijn, en " + ("het " if dit == "dit" else "de ") + fig_name + " ook.",
                "Vouw de kaart dubbel over de lange stippellijn in het midden, met de tekening aan de buitenkant.",
                "Knip vanaf de vouw de twee korte streepjeslijnen in, door beide lagen tegelijk. Knip niet verder dan de lijn.",
                "Vouw het strookje tussen de sneetjes langs de korte stippellijn naar voren en weer terug. Zo krijgt het een scherpe vouw.",
                "Open de kaart en duw het strookje naar binnen. Vouw de kaart nu dicht met de tekening binnen en druk goed aan. Als je hem openmaakt, springt er een trapje naar voren.",
                "Smeer lijm op het grijze vlakje van het trapje en plak " + ("het " if dit == "dit" else "de ") + fig_name + " erop, met de onderkant precies op de vloer.",
            ] + extra_steps + ["De buitenkant is nog leeg: teken er een voorkant op, of plak de kaart in een dubbelgevouwen stuk gekleurd karton."]}}}
    if holiday: meta["holiday"] = holiday
    write(OUT, slug, sh, meta)

# ---------- taart ----------
@do
def popup_taart():
    def wall(sh, cx, yf, top, a, sw):
        outline_text(sh, cx, top + 22, "Hoera, je bent jarig!", 15)
        bunting(sh, 22, 178, top + 30, 5, 9, "rybgmo", 5.5)
        for x, y, c in [(34, top + 52, "r"), (52, top + 60, "b"), (150, top + 54, "y"), (168, top + 62, "m")]:
            balloon(sh, x, y, 7.5, c)
        confetti(sh, [(78, top + 48), (122, top + 46), (96, top + 58), (70, yf - 10), (130, yf - 12), (24, yf - 6), (176, yf - 8)])
    def floor(sh, cx, yf, bot, a, sw):
        # tafelkleed met stippen en twee cadeautjes opzij
        sh.region(f"M{POP_X0 + 6} {yf + 6}H{POP_X1 - 6}V{bot - 6}H{POP_X0 + 6}Z", "k") if False else None
        for x, y, c, r in [(40, yf + 22, "g", "y"), (160, yf + 24, "p", "y")]:
            sh.rect_r(x - 13, y - 9, 26, 20, c, 1.5); sh.rect_r(x - 2, y - 9, 4, 20, r)
            sh.region(f"M{x} {y - 9}Q{x - 9} {y - 18} {x - 11} {y - 10}ZM{x} {y - 9}Q{x + 9} {y - 18} {x + 11} {y - 10}Z", r)
        for k in range(9):
            sh.circle_r(30 + k * 17.5, bot - 14 + (k % 2) * 4, 2.6, "rybgm"[k % 5])
        stars(sh, [(72, yf + 46), (128, yf + 48), (100, yf + 60), (24, yf + 50), (176, yf + 54)], 4.5)
    def figure(fg, cx, by):
        sh = fg.sh
        fg.rect(cx - 40, by - 22, 80, 22, "k", 2)
        sh.line(f"M{cx - 40} {by - 15}" + "".join(f"Q{cx - 40 + (k + .5) * 10} {by - 9} {cx - 40 + (k + 1) * 10} {by - 15}" for k in range(8)), "l", "stroke-width:1.1")
        for k in range(5): sh.circle_r(cx - 30 + k * 15, by - 5.5, 2.2, "rybgo"[k])
        fg.rect(cx - 27, by - 38, 54, 16, "m", 2)
        sh.line(f"M{cx - 27} {by - 32}" + "".join(f"Q{cx - 27 + (k + .5) * 9} {by - 27} {cx - 27 + (k + 1) * 9} {by - 32}" for k in range(6)), "l", "stroke-width:1.1")
        for k in range(4):
            x = cx - 15 + k * 10
            fg.rect(x - 1.8, by - 48, 3.6, 10, "byrl"[k])
            fg.poly([(x, by - 56), (x + 2.6, by - 51), (x, by - 48.5), (x - 2.6, by - 51)], "o")
    popup("popupkaart-verjaardagstaart", "Pop-upkaart: verjaardagstaart", 40, 22, wall, floor, figure, "taart", "feest", "6-9",
          ["Schrijf onder de taart voor wie de kaart is, of hoe oud de jarige wordt."], holiday="verjaardag", title_txt="Pop-upkaart: taart")

# ---------- hart ----------
@do
def popup_hart():
    def wall(sh, cx, yf, top, a, sw):
        outline_text(sh, cx, top + 22, "Ik hou van jou!", 17)
        for k in range(7):
            x = 26 + k * 24.7
            sh.region(heart_path(x, top + 36 + (k % 2) * 4, 5.5), "mr"[k % 2])
        for x, y in [(30, top + 58), (170, top + 58), (44, yf - 10), (156, yf - 10)]:
            flower(sh, x, y, 5, "k", "y")
    def floor(sh, cx, yf, bot, a, sw):
        for x, y in [(36, yf + 20), (164, yf + 20), (60, yf + 44), (140, yf + 44), (30, bot - 16), (170, bot - 16)]:
            sh.region(heart_path(x, y, 8), "r")
        sh.text(cx, bot - 12, "Van: .................................", 7)
        for k in range(5): flower(sh, 70 + k * 15, yf + 62 - (k % 2) * 4, 3.4, "mkpkm"[k], "y")
    def figure(fg, cx, by):
        sh = fg.sh
        fg.geom(heart_geom(cx, by - 32, 32), "r")
        fg.geom(heart_geom(cx - 18, by - 46, 10), "m"); fg.geom(heart_geom(cx + 19, by - 44, 8), "k")
        fg.rect(cx - 38, by - 15, 76, 15, "y", 3)
        sh.poly_r([(cx - 38, by - 15), (cx - 48, by - 11), (cx - 44, by - 7.5), (cx - 48, by - 3), (cx - 38, by)], "o"); fg.g.append(Polygon([(cx - 38, by - 15), (cx - 48, by - 11), (cx - 44, by - 7.5), (cx - 48, by - 3), (cx - 38, by)]))
        sh.poly_r([(cx + 38, by - 15), (cx + 48, by - 11), (cx + 44, by - 7.5), (cx + 48, by - 3), (cx + 38, by)], "o"); fg.g.append(Polygon([(cx + 38, by - 15), (cx + 48, by - 11), (cx + 44, by - 7.5), (cx + 48, by - 3), (cx + 38, by)]))
        sh.text(cx, by - 5, "voor jou", 8)
    popup("popupkaart-hart", "Pop-upkaart: een groot hart", 30, 20, wall, floor, figure, "hart", "feest", "6-9",
          ["Geef de kaart aan iemand van wie je houdt: op Valentijnsdag, Moederdag of zomaar."], holiday="valentijn", title_txt="Pop-upkaart: hart")

# ---------- ster ----------
@do
def popup_ster():
    def wall(sh, cx, yf, top, a, sw):
        outline_text(sh, cx, top + 22, "Je bent een ster!", 16)
        sh.region(moon_path(36, top + 50, 13), "y")
        for k in range(14):
            x = 24 + (k * 37) % 152; y = top + 34 + (k * 23) % 34
            if abs(x - 36) < 16 and abs(y - top - 50) < 16: continue
            sh.poly_r(star_pts(x, y, 3.2, 1.4), "y")
        sh.region(cloud_path(164, yf - 14, 10), "-"); sh.region(cloud_path(40, yf - 10, 8), "-")
    def floor(sh, cx, yf, bot, a, sw):
        for k, (x, y) in enumerate([(36, yf + 22), (164, yf + 22), (26, yf + 52), (174, yf + 52), (62, bot - 14), (138, bot - 14)]):
            sh.poly_r(star_pts(x, y, 7, 3), "yo"[k % 2])
        sh.text(cx, yf + 40, "Omdat je zo goed je best deed!", 6.5)
        sh.text(cx, yf + 54, "Van: .................................", 7)
    def figure(fg, cx, by):
        sh = fg.sh
        fg.poly(star_pts(cx, by - 30, 29, 13), "y")
        sh.dot(cx - 7, by - 34, 2.4); sh.dot(cx + 7, by - 34, 2.4)
        sh.line(f"M{cx - 7} {by - 27}Q{cx} {by - 21} {cx + 7} {by - 27}", "l", "stroke-width:1.6")
        sh.circle_r(cx - 13, by - 28, 2.6, "m"); sh.circle_r(cx + 13, by - 28, 2.6, "m")
        fg.rect(cx - 30, by - 11, 60, 11, "b", 3)
        sh.text(cx, by - 3.2, "Goed gedaan!", 6.5)
        for s in (-1, 1):
            fg.poly(star_pts(cx + s * 42, by - 10, 10, 4.4), "o")
    popup("popupkaart-ster", "Pop-upkaart: je bent een ster!", 34, 18, wall, floor, figure, "ster", "feest", "6-9",
          ["Geef de kaart aan iemand die iets knaps heeft gedaan: een diploma, een spreekbeurt of gewoon heel lief zijn."], title_txt="Pop-upkaart: ster")

# ---------- monster ----------
@do
def popup_monster():
    def wall(sh, cx, yf, top, a, sw):
        outline_text(sh, cx, top + 22, "Boe! Groetjes!", 17)
        for x, y, r in [(30, top + 44, 6), (44, top + 58, 4), (168, top + 46, 7), (154, top + 62, 4), (176, yf - 12, 5), (24, yf - 14, 5)]:
            sh.circle_r(x, y, r, "l"); sh.dot(x, y, r * .35)
        for k in range(6):
            x = 30 + k * 28
            sh.line(f"M{x} {top + 30}Q{x + 7} {top + 26} {x + 14} {top + 30}", "l", "stroke-width:1") if False else None
    def floor(sh, cx, yf, bot, a, sw):
        # voetafdrukken van het monster
        for k, (x, y, d) in enumerate([(40, bot - 18, -1), (58, yf + 52, -1), (44, yf + 28, -1), (160, bot - 18, 1), (142, yf + 52, 1), (156, yf + 28, 1)]):
            sh.ellipse_r(x, y, 5.5, 7, "g")
            for j in (-1, 0, 1): sh.circle_r(x + j * 4.2, y - 9 - (j == 0) * 1.5, 2, "g")
        sh.text(cx, bot - 12, "Van: .................................", 7)
    def figure(fg, cx, by):
        sh = fg.sh
        # voeten, armen, lijf, hoorns, oog
        for s in (-1, 1):
            fg.ellipse(cx + s * 14, by - 3.5, 10, 3.5, "g")
            fg.poly([(cx + s * 26, by - 30), (cx + s * 44, by - 46), (cx + s * 48, by - 42), (cx + s * 30, by - 22)], "l")
            for j in range(3):
                ang = math.radians(-60 + j * 30) if s > 0 else math.radians(-120 - j * 30)
                fg.circle(cx + s * 46 + 4 * math.cos(ang), by - 45 + 4 * math.sin(ang), 2.2, "l")
            fg.poly([(cx + s * 8, by - 50), (cx + s * 16, by - 58), (cx + s * 18, by - 47)], "y")
        fg.geom(Point(cx, by - 26).buffer(1, 48).union(box(-1, 0, 1, 1)).intersection(Point(cx, by - 26).buffer(1, 48)) if False else
                unary_union([affinity.scale(Point(cx, by - 30).buffer(1, 64), 28, 22), box(cx - 26, by - 30, cx + 26, by - 3)]).simplify(.2), "l")
        fg.circle(cx, by - 36, 10, "-"); sh.circle_r(cx + 1.5, by - 35, 4.4, "n"); sh.dot(cx + 1.5, by - 35, 2)
        sh.region(f"M{cx - 13} {by - 20}Q{cx} {by - 8} {cx + 13} {by - 20}Z", "x")
        sh.poly_r([(cx - 8, by - 19.2), (cx - 4, by - 19.6), (cx - 6, by - 15)], "-"); sh.poly_r([(cx + 4, by - 19.6), (cx + 8, by - 19.2), (cx + 6, by - 15)], "-")
        for x, y in [(cx - 18, by - 32), (cx + 19, by - 14), (cx - 16, by - 10)]: sh.circle_r(x, y, 2.6, "t")
    popup("popupkaart-monster", "Pop-upkaart: monster zegt boe!", 34, 20, wall, floor, figure, "monster", "sprookjes", "6-9",
          ["Geef het monster een naam en schrijf hem onderaan de kaart."], title_txt="Pop-upkaart: monster")

# =====================================================================
# 2. VORMKAARTEN (vouw bovenaan of links) EN KAARTEN MET FLAPJES
# =====================================================================

def fold_card(sh, front, fold, at, code, back_fn=None):
    """Kaart in een vorm: front = voorkant (shapely). fold='top': vouw op y=at (voorkant eronder),
    fold='left': vouw op x=at (voorkant rechts). De achterkant is het spiegelbeeld."""
    if fold == "top":
        back = affinity.scale(front, 1, -1, origin=(100, at))
        line = LineString([(-10, at), (210, at)])
    else:
        back = affinity.scale(front, -1, 1, origin=(at, 100))
        line = LineString([(at, -10), (at, 300)])
    whole = unary_union([front, back]).buffer(.05, join_style=2).buffer(-.05, join_style=2)
    assert whole.geom_type == "Polygon", "voor- en achterkant moeten aan elkaar vast zitten"
    band = line.buffer(.02, cap_style=2)
    (bx0, by0, bx1, by1) = front.intersection(band).bounds
    if fold == "top": by0 = by1 = at
    else: bx0 = bx1 = at
    flen = (bx1 - bx0) if fold == "top" else (by1 - by0)
    assert flen > 40, ("vouwlijn te kort", flen)
    b = whole.bounds
    assert b[0] > 3 and b[2] < 197 and b[1] > 3 and b[3] < 272, b
    sh.region(geom_d(front), code)
    sh.line(geom_d(whole), "cut")
    sh.seg(bx0, by0, bx1, by1, "fold")
    if back_fn:
        if fold == "top":
            c = front.centroid
            sh.raw(f'<g transform="rotate(180 {f(c.x)} {f(at)})">'); back_fn(sh, front); sh.raw("</g>")
        else:
            w = front.bounds[2] - at
            sh.raw(f'<g transform="translate({f(-(front.bounds[2] - at) - (front.bounds[0] - at))} 0)">') if False else None
            sh.raw(f'<g transform="translate({f(-w)} 0)">'); back_fn(sh, front); sh.raw("</g>")
    return whole

FG = 6  # breedte van het lijmrandje van een flapje

def flap_piece(sh, x, y, w, h, side, code, draw=None):
    """Los flapje (w x h, inclusief scharnierrandje van FG aan kant side: 'l', 'r', 't' of 'b').
    Het randje wordt op het grijze strookje op de kaart geplakt; op de stippellijn vouw je het flapje open."""
    ix, iy, iw, ih = x, y, w, h
    if side == "l": ix += FG; iw -= FG; sh.seg(x + FG, y, x + FG, y + h, "fold")
    if side == "r": iw -= FG; sh.seg(x + w - FG, y, x + w - FG, y + h, "fold")
    if side == "t": iy += FG; ih -= FG; sh.seg(x, y + FG, x + w, y + FG, "fold")
    if side == "b": ih -= FG; sh.seg(x, y + h - FG, x + w, y + h - FG, "fold")
    sh.rect_r(ix, iy, iw, ih, code, 1.5)
    if draw: draw(sh, ix, iy, iw, ih)
    sh.rect_line(x, y, w, h, "cut", 1.5)

def flap_spot(sh, x, y, w, h, side):
    """Op de kaart: de stippelrand waar het flapje komt, met het grijze lijmstrookje aan de scharnierkant."""
    sh.rect_line(x, y, w, h, "guide", 1.5, "stroke-dasharray:2 2")
    if side == "l": glue_rect(sh, x, y, FG, h)
    if side == "r": glue_rect(sh, x + w - FG, y, FG, h)
    if side == "t": glue_rect(sh, x, y, w, FG)
    if side == "b": glue_rect(sh, x, y + h - FG, w, FG)

def back_details(lines_, title_=None, size=6.5):
    def fn(sh, front):
        c = front.centroid; minx, miny, maxx, maxy = front.bounds
        y = c.y - len(lines_) * 6 + 2
        if title_: outline_text(sh, c.x, y - 8, title_, 11); y += 4
        for i, k in enumerate(lines_):
            yy = y + i * 13
            sh.text(c.x - 34, yy, k, size, "start")
            sh.seg(c.x - 34 + len(k) * size * .52 + 2, yy, c.x + 36, yy, "guide")
    return fn

INVITE = ["Wanneer:", "Hoe laat:", "Waar:", "Van:"]

# ---------- pyjamafeest: kaart in de vorm van een pyjamashirt ----------
@do
def pyjamafeest():
    sh = Sheet()
    title(sh, "Uitnodiging: pyjamafeest", 13, 10)
    yf, cx = 132, 100
    rel = [(-30, 0), (30, 0), (60, 10), (82, 42), (64, 54), (52, 42), (52, 112), (-52, 112), (-52, 42), (-64, 54), (-82, 42), (-60, 10)]
    front = Polygon([(cx + x, yf + y) for x, y in rel])
    def back(sh, fr):
        outline_text(sh, cx, yf + 30, "Neem mee:", 10)
        sh.text(cx, yf + 41, "pyjama, slaapzak, knuffel", 6.5)
        for i, k in enumerate(["Wanneer:", "Waar:", "Ophalen om:", "Van:"]):
            yy = yf + 56 + i * 13
            sh.text(cx - 44, yy, k, 6.5, "start"); sh.seg(cx - 44 + len(k) * 3.4 + 3, yy, cx + 44, yy, "guide")
    fold_card(sh, front, "top", yf, "b", back)
    # kraag met twee punten, knoopjes, zakje, maantjes en sterren
    sh.poly_r([(cx - 30, yf), (cx, yf + 4), (cx - 6, yf + 20), (cx - 24, yf + 12)], "-")
    sh.poly_r([(cx + 30, yf), (cx, yf + 4), (cx + 6, yf + 20), (cx + 24, yf + 12)], "-")
    sh.seg(cx, yf + 20, cx, yf + 112, "l", "stroke-width:1.2")
    for k in range(4): sh.circle_r(cx + 4.5, yf + 30 + k * 20, 2.6, "y")
    for s in (-1, 1):
        sh.line(f"M{cx + s * 52} {yf + 42}Q{cx + s * 56} {yf + 26} {cx + s * 60} {yf + 10}", "l", "stroke-width:1")
        sh.rect_r(cx + s * 72 - 5, yf + 39 + (5 if s < 0 else 5) - 2, 10, 4, "n", 1) if False else None
    sh.rect_r(cx - 44, yf + 28, 28, 26, "y", 2); sh.seg(cx - 44, yf + 33, cx - 16, yf + 33, "l", "stroke-width:1")
    sh.region(moon_path(cx - 31, yf + 44, 6), "-")
    outline_text(sh, cx + 28, yf + 42, "Pyjama", 9.5); outline_text(sh, cx + 28, yf + 54, "feest!", 9.5)
    for k, (x, y) in enumerate([(cx - 34, yf + 70), (cx - 18, yf + 88), (cx - 40, yf + 100), (cx + 20, yf + 72), (cx + 38, yf + 92), (cx + 16, yf + 102), (cx - 66, yf + 40), (cx + 66, yf + 40)]):
            sh.poly_r(star_pts(x, y, 5, 2.2), "y") if k % 3 else sh.region(moon_path(x, y, 5), "y")
    sh.legend(["cut", "fold"], 276)
    write(OUT, "uitnodiging-pyjamafeest", sh, {"category": "feest", "age": "6-9", "kind": "kaart", "difficulty": 2, "minutes": 25, "paperGsm": 160,
        "materials": KAART_MAT,
        "i18n": {"nl": {"name": "Uitnodiging voor een pyjamafeest (kaart in de vorm van een pyjama)", "printNote": STEVIG, "steps": [
            "Kleur de pyjama in: de onderste helft is de voorkant.",
            "Knip de kaart uit langs de streepjeslijn. Let op: de twee pyjama's blijven aan de schouders aan elkaar vast.",
            "Vouw de kaart dubbel op de stippellijn bij de schouders, met de tekening aan de buitenkant.",
            "Vul op de achterkant in wanneer en waar het feest is, en hoe laat je logé wordt opgehaald.",
            "Geef de uitnodiging aan je vriendjes en vriendinnetjes."]}}})

# ---------- buschauffeur: kaart in de vorm van een bus ----------
@do
def bedank_bus():
    sh = Sheet()
    title(sh, "Bedankkaart voor de buschauffeur", 13, 10)
    yf = 120; x0, x1, H = 16, 184, 92
    body = Polygon([(x0, yf), (x1, yf), (x1, yf + H - 8), (x1 - 8, yf + H), (x0 + 8, yf + H), (x0, yf + H - 8)])
    wheels = [Point(x, yf + H).buffer(12, 48) for x in (50, 150)]
    front = unary_union([body] + wheels)
    def back(sh, fr):
        outline_text(sh, 100, yf + 30, "Dank je wel!", 13)
        sh.text(100, yf + 44, "voor alle ritjes naar school", 6.5)
        sh.text(66, yf + 62, "Van:", 7, "start"); sh.seg(84, yf + 62, 140, yf + 62, "guide")
    fold_card(sh, front, "top", yf, "y", back)
    # ramen, deur, chauffeur, lamp, wielen
    for k in range(4):
        sh.rect_r(26 + k * 28, yf + 8, 22, 22, "b", 2)
    sh.rect_r(146, yf + 8, 30, 34, "b", 2)
    # chauffeur die zwaait achter de voorruit
    hx, hy = 160, yf + 24
    sh.region(f"M{hx - 10} {yf + 42}V{hy + 12}Q{hx} {hy + 7} {hx + 10} {hy + 12}V{yf + 42}Z", "n")
    sh.circle_r(hx, hy, 7, "k"); sh.dot(hx - 2.5, hy - 1, 1.1); sh.dot(hx + 2.5, hy - 1, 1.1)
    sh.line(f"M{hx - 2.5} {hy + 2.5}Q{hx} {hy + 4.5} {hx + 2.5} {hy + 2.5}", "l", "stroke-width:.9")
    sh.region(f"M{hx - 8} {hy - 3}Q{hx - 8} {hy - 11} {hx} {hy - 11}Q{hx + 8} {hy - 11} {hx + 8} {hy - 3}Z", "n")
    sh.rect_r(hx - 9, hy - 5, 18, 3, "x", 1)
    sh.line(f"M{hx + 8} {hy + 14}L{hx + 12} {hy + 2}", "l", "stroke-width:2.6")
    sh.circle_r(hx + 12.5, hy, 2.4, "k")
    sh.circle_r(hx - 8, yf + 38, 4, "z"); sh.circle_line(hx - 8, yf + 38, 1.5, "l", "stroke-width:1")
    # kinderhoofdjes in de ramen
    for k, c in enumerate("kwkw"):
        x = 37 + k * 28
        sh.circle_r(x, yf + 24, 5, "k")
        sh.region(f"M{x - 5} {yf + 23}Q{x - 5} {yf + 17} {x} {yf + 17}Q{x + 5} {yf + 17} {x + 5} {yf + 23}Q{x} {yf + 20} {x - 5} {yf + 23}Z", "wxoy"[k])
        sh.dot(x - 1.8, yf + 24, .9); sh.dot(x + 1.8, yf + 24, .9)
    sh.rect_r(x0, yf + 36, 122, 16, "-", 0)
    sh.text(77, yf + 47.5, "Dank je wel, chauffeur!", 7.5)
    sh.rect_r(174, yf + 52, 8, 6, "o", 1.5); sh.rect_r(18, yf + 52, 6, 6, "r", 1.5)
    sh.seg(x0, yf + 58, x1, yf + 58, "l", "stroke-width:1.2")
    sh.region(f"M{x0} {yf + 64}H{x1}V{yf + 72}H{x0}Z", "r")
    sh.rect_r(146, yf + 46, 22, 36, "b", 2); sh.seg(157, yf + 46, 157, yf + 82, "l", "stroke-width:1.2")
    for x in (50, 150):
        sh.circle_r(x, yf + H, 12, "x"); sh.circle_r(x, yf + H, 5, "z")
    sh.legend(["cut", "fold"], 276)
    write(OUT, "bedankkaart-buschauffeur", sh, {"category": "voertuigen", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": KAART_MAT,
        "i18n": {"nl": {"name": "Bedankkaart voor de buschauffeur (kaart in de vorm van een bus)", "printNote": STEVIG, "steps": [
            "Kleur de bus in. Wie zitten er allemaal in de bus?",
            "Knip de kaart uit langs de streepjeslijn, met de wielen erbij.",
            "Vouw de kaart dubbel over de stippellijn op het dak, met de tekening aan de buitenkant. Nu staat de bus op zijn wielen.",
            "Schrijf op de achterkant je naam en geef de kaart aan de chauffeur van de schoolbus of de buurtbus, bijvoorbeeld voor de zomervakantie."]}}})

# ---------- zomerfeest: kaart in de vorm van een plak watermeloen ----------
@do
def zomerfeest():
    sh = Sheet()
    title(sh, "Uitnodiging: zomerfeest", 13, 10)
    yf, R, cx = 106, 84, 100
    front = Polygon([(cx + R * math.cos(math.radians(a)), yf + R * math.sin(math.radians(a))) for a in [i * 180 / 120 for i in range(121)]])
    def back(sh, fr):
        outline_text(sh, cx, yf + 20, "Kom je ook?", 12)
        for i, k in enumerate(INVITE):
            yy = yf + 34 + i * 12
            sh.text(cx - 40, yy, k, 6.5, "start"); sh.seg(cx - 40 + len(k) * 3.4 + 3, yy, cx + 40, yy, "guide")
    fold_card(sh, front, "top", yf, "g", back)
    def half(r): return P([(cx + r * math.cos(math.radians(a)), yf + r * math.sin(math.radians(a))) for a in [i * 180 / 90 for i in range(91)]])
    sh.region(half(R - 7), "l"); sh.region(half(R - 12), "r")
    seeds = [(-56, 40), (-38, 52), (-16, 62), (8, 66), (30, 60), (50, 48), (62, 32), (-60, 20), (-30, 36), (-6, 46), (18, 44), (40, 34), (-46, 56), (-8, 28)]
    for x, y in seeds:
        x, y = cx + x, yf + y
        a = math.degrees(math.atan2(y - yf, x - cx)) - 90
        sh.raw(f'<g transform="rotate({f(a)} {f(x)} {f(y)})">'); sh.region(drop_path(x, y, 2.3), "x"); sh.raw("</g>")
    outline_text(sh, cx, yf + 17, "Zomerfeest!", 13)
    sh.legend(["cut", "fold"], 276)
    write(OUT, "uitnodiging-zomerfeest-watermeloen", sh, {"category": "eten", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": KAART_MAT,
        "i18n": {"nl": {"name": "Uitnodiging voor een zomerfeest (kaart als plak watermeloen)", "printNote": STEVIG, "steps": [
            "Kleur de watermeloen: een groene schil, een lichtgroen randje, rood vruchtvlees en zwarte pitjes.",
            "Knip de kaart uit langs de streepjeslijn: een hele ronde meloen.",
            "Vouw hem dubbel op de stippellijn, met de tekening aan de buitenkant. Nu heb je een plak meloen die rechtop staat.",
            "Vul op de achterkant in wanneer en waar het zomerfeest is, en geef de kaart weg."]}}})

# ---------- speelafspraak: kaart in de vorm van een huisje, met een deur om open te doen ----------
@do
def speelafspraak():
    sh = Sheet()
    title(sh, "Uitnodiging: kom je spelen?", 13, 10)
    xf, W, peak, eave, bot = 100, 84, 22, 80, 200
    front = Polygon([(xf, bot), (xf, eave), (xf + W / 2, peak), (xf + W + 4, eave + 2), (xf + W, eave + 2), (xf + W, bot)])
    def back(sh, fr):
        outline_text(sh, xf + W / 2, eave + 26, "Kom je", 12); outline_text(sh, xf + W / 2, eave + 40, "spelen?", 12)
        for i, k in enumerate(["Wanneer:", "Hoe laat:", "Adres:", "Van:"]):
            yy = eave + 60 + i * 14
            sh.text(xf + 8, yy, k, 6, "start"); sh.seg(xf + 10 + len(k) * 3.2, yy, xf + W - 6, yy, "guide")
    fold_card(sh, front, "left", xf, "y", back)
    # dak, schoorsteen, raam, deur
    sh.region(f"M{xf} {eave}L{xf + W / 2} {peak}L{xf + W + 4} {eave + 2}L{xf + W} {eave + 8}L{xf + W / 2} {peak + 10}L{xf} {eave + 6}Z", "r")
    # raam boven
    wx, wy, ww, wh = xf + 26, eave + 16, 32, 26
    sh.rect_r(wx, wy, ww, wh, "b", 2)
    sh.seg(wx + ww / 2, wy, wx + ww / 2, wy + wh, "l", "stroke-width:1.4"); sh.seg(wx, wy + wh / 2, wx + ww, wy + wh / 2, "l", "stroke-width:1.4")
    sh.rect_r(wx - 3, wy + wh, ww + 6, 4, "-", 1)
    flower(sh, wx + 6, wy + wh - 4, 2.6, "m", "y"); flower(sh, wx + ww - 6, wy + wh - 4, 2.6, "r", "y")
    # deuropening met wat erachter zit
    dx, dy, dw, dh = xf + 22, bot - 66, 40, 66
    sh.rect_r(dx, dy, dw, dh, "-", 0)
    sh.text(dx + dw / 2, dy + 10, "Kom je bij", 6.2); sh.text(dx + dw / 2, dy + 18, "mij spelen?", 6.2)
    # speelgoed achter de deur: bal, blokken, beer
    sh.circle_r(dx + 10, dy + 56, 6, "r"); sh.line(f"M{dx + 4} {dy + 56}Q{dx + 10} {dy + 52} {dx + 16} {dy + 56}", "l", "stroke-width:1")
    sh.rect_r(dx + 21, dy + 52, 9, 9, "b"); sh.rect_r(dx + 30, dy + 52, 9, 9, "y"); sh.rect_r(dx + 25.5, dy + 43, 9, 9, "g")
    bx, by = dx + 20, dy + 31
    for s in (-1, 1): sh.circle_r(bx + s * 6, by - 6, 3, "w")
    sh.circle_r(bx, by, 7.5, "w"); sh.ellipse_r(bx, by + 2.5, 3.2, 2.4, "o")
    sh.dot(bx - 2.6, by - 1.5, 1); sh.dot(bx + 2.6, by - 1.5, 1); sh.dot(bx, by + 1.6, .9)
    flap_spot(sh, dx - FG - 1, dy - 1, dw + FG + 2, dh + 1, "l")
    # stoep, bloemetjes
    for x in (xf + 8, xf + 74): sh.line(f"M{x} {bot}V{bot - 10}", "l", "stroke-width:1.1"); flower(sh, x, bot - 13, 2.8, "p", "y")
    # de deur om op te plakken (scharnier links)
    def deur(sh, x, y, w, h):
        sh.rect_r(x + 8, y + 6, w - 14, h * .38, "-", 2); sh.rect_r(x + 8, y + h * .5, w - 14, h * .4, "-", 2)
        sh.circle_r(x + w - 6, y + h * .48, 2.2, "y")
        sh.region(heart_path(x + w / 2 + 1, y + 6 + h * .19, 5), "r")
    fw, fh = dw + FG + 2, dh + 1
    pcx, pcy = 100, 240
    sh.tip(16, 220, "De deur:")
    rot(sh, -90, pcx, pcy)
    flap_piece(sh, pcx - fw / 2, pcy - fh / 2, fw, fh, "l", "g", deur)
    end(sh)
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "uitnodiging-speelafspraak-huisje", sh, {"category": "thuis", "age": "4-6", "kind": "kaart", "difficulty": 2, "minutes": 25, "paperGsm": 160,
        "materials": KAART_MAT + [{"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Uitnodiging voor een speelafspraak: huisje met een deur die opengaat", "printNote": STEVIG, "steps": [
            "Kleur het huisje en de losse deur in. De rechterhelft is de voorkant van de kaart.",
            "Knip het dubbele huisje uit langs de streepjeslijn, en de deur ook.",
            "Vouw het smalle randje van de deur om langs de stippellijn. Smeer lijm op het grijze strookje links naast de deuropening en plak het randje van de deur erop, zodat de deur precies over de opening valt.",
            "Vouw de kaart dubbel op de stippellijn in het midden, met de tekening aan de buitenkant.",
            "Vul op de achterkant in wanneer je vriendje of vriendinnetje kan komen spelen. Wie de deur opendoet, ziet de vraag!"]}}})

def rect_card(sh, top, h2, back_fn):
    """Rechthoekige kaart (172 breed), vouw horizontaal; de voorkant is de onderste helft."""
    x0, w = 14, 172
    yf = top + h2
    sh.rect_line(x0, top, w, 2 * h2, "cut", 3)
    sh.seg(x0, yf, x0 + w, yf, "fold")
    sh.raw(f'<g transform="rotate(180 100 {f(yf - h2 / 2)})">'); back_fn(sh, yf - h2 / 2); sh.raw("</g>")
    return yf

def invite_back(head, rows, size=6.5):
    def fn(sh, cy):
        outline_text(sh, 100, cy - 24, head, 12)
        for i, k in enumerate(rows):
            yy = cy - 6 + i * 13
            sh.text(46, yy, k, size, "start"); sh.seg(46 + len(k) * size * .52 + 3, yy, 154, yy, "guide")
    return fn

# ---------- logeerpartij: raam met gordijntjes die open kunnen ----------
@do
def logeerpartij():
    sh = Sheet()
    title(sh, "Uitnodiging: kom je logeren?", 13, 10)
    yf = rect_card(sh, 16, 88, invite_back("Logeerfeest!", ["Wanneer:", "Ophalen om:", "Waar:", "Van:"]))
    bot = yf + 88
    sh.rect_r(14, yf, 172, 96, "k", 0) if False else None
    # muur met bakstenen
    for r in range(6):
        y = yf + 6 + r * 13
        for c in range(9):
            x = 18 + c * 20 + (10 if r % 2 else 0)
            if 46 < x + 16 and x < 154: continue
            if x + 16 > 183: continue
            sh.rect_r(x, y, 16, 9, "or"[(r + c) % 2] if False else "o", 1)
    sh.text(100, yf + 9, "Psst... kijk achter de gordijntjes!", 5.6) if False else None
    # raamkozijn en wat je erachter ziet
    wx0, wx1, wy0, wy1 = 54, 146, yf + 12, bot - 10
    sh.rect_r(wx0 - 5, wy0 - 5, wx1 - wx0 + 10, wy1 - wy0 + 10, "w", 2)
    sh.rect_r(wx0, wy0, wx1 - wx0, wy1 - wy0, "n")
    sh.region(moon_path(wx0 + 14, wy0 + 13, 7), "y")
    stars(sh, [(wx0 + 34, wy0 + 9), (wx1 - 12, wy0 + 10), (wx1 - 30, wy0 + 8)], 3.4)
    sh.rect_r(wx0 + 14, wy0 + 18, 64, 13, "-", 3)
    sh.text(100, wy0 + 27, "Kom je logeren?", 6.4)
    # bed met twee kinderen onder één dekbed
    by = wy1 - 4
    sh.rect_r(wx0 + 8, by - 26, 6, 26, "w", 1); sh.rect_r(wx1 - 14, by - 18, 6, 18, "w", 1)
    sh.rect_r(wx0 + 14, by - 22, 22, 9, "-", 3)
    for k, (hx, hair) in enumerate([(wx0 + 22, "x"), (wx0 + 34, "o")]):
        hy = by - 22
        sh.circle_r(hx, hy, 5.5, "k")
        sh.region(f"M{hx - 5.5} {hy - 1}Q{hx - 5.5} {hy - 6.5} {hx} {hy - 6.5}Q{hx + 5.5} {hy - 6.5} {hx + 5.5} {hy - 1}Q{hx} {hy - 4} {hx - 5.5} {hy - 1}Z", hair)
        sh.line(f"M{hx - 3} {hy + 1}h2M{hx + 1} {hy + 1}h2", "l", "stroke-width:.9")
    sh.region(f"M{wx0 + 14} {by - 4}V{by - 16}Q{wx0 + 40} {by - 20} {wx1 - 14} {by - 14}V{by - 4}Z", "t")
    for k in range(4): sh.circle_r(wx0 + 30 + k * 13, by - 10, 2, "y")
    # plekken voor de gordijntjes (scharnier aan de buitenkant)
    half = (wx1 - wx0) / 2
    flap_spot(sh, wx0 - FG, wy0 - 1, half + FG, wy1 - wy0 + 2, "l")
    flap_spot(sh, wx0 + half, wy0 - 1, half + FG, wy1 - wy0 + 2, "r")
    # vensterbank met plantjes
    sh.rect_r(wx0 - 9, wy1 + 4, wx1 - wx0 + 18, 4, "-", 1)
    # de gordijntjes
    def gordijn(side):
        def d(sh, x, y, w, h):
            for k in range(1, 4):
                xx = x + k * w / 4
                sh.line(f"M{f(xx)} {y + 2}Q{f(xx + 2)} {y + h / 2} {f(xx)} {y + h - 2}", "l", "stroke-width:.9")
            for k in range(6):
                sh.poly_r(star_pts(x + w / 8 + (k % 2) * w / 2 + w / 8, y + 8 + k * (h - 14) / 5, 3, 1.3), "y")
            sh.rect_r(x, y, w, 5, "p", 1)
        return d
    fw, fh = half + FG, wy1 - wy0 + 2
    sh.tip(16, bot + 9, "De gordijntjes:")
    for i, (pcx, side) in enumerate([(58, "l"), (142, "r")]):
        pcy = bot + 40
        rot(sh, -90, pcx, pcy)
        flap_piece(sh, pcx - fw / 2, pcy - fh / 2, fw, fh, side, "t", gordijn(side))
        end(sh)
    sh.legend(["cut", "fold", "glue"], 279)
    write(OUT, "uitnodiging-logeerpartij-gordijntjes", sh, {"category": "thuis", "age": "6-9", "kind": "kaart", "difficulty": 2, "minutes": 30, "paperGsm": 160,
        "materials": KAART_MAT + [{"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Uitnodiging voor een logeerpartij: raam met gordijntjes die opengaan", "printNote": STEVIG, "steps": [
            "Kleur de voorkant van de kaart (de onderste helft) en de twee gordijntjes in.",
            "Knip de kaart en de gordijntjes uit langs de streepjeslijnen.",
            "Vouw bij elk gordijntje het smalle randje om langs de stippellijn.",
            "Smeer lijm op de grijze strookjes links en rechts van het raam. Plak het randje van elk gordijntje erop, zodat de gordijntjes in het midden tegen elkaar aan sluiten.",
            "Vouw de kaart dubbel op de lange stippellijn, met de tekening aan de buitenkant, en vul de achterkant in.",
            "Wie de gordijntjes openschuift, ziet de vraag!"]}}})

# ---------- kerstdiner: kaart met een stolp die je optilt ----------
@do
def kerstdiner():
    sh = Sheet()
    title(sh, "Uitnodiging: kerstdiner", 13, 10)
    yf = rect_card(sh, 16, 92, invite_back("Kom je eten?", ["Wanneer:", "Hoe laat:", "Waar:", "Van:"]))
    bot = yf + 92
    outline_text(sh, 100, yf + 15, "Kerstdiner!", 12)
    # tafelkleed
    ty = bot - 18
    sh.region(f"M18 {ty}H182V{bot - 4}H18Z", "r")
    for k in range(8): sh.seg(22 + k * 22.5, ty + 2, 22 + k * 22.5, bot - 6, "l", "stroke-width:.8")
    # kandelaars
    for x in (32, 168):
        sh.rect_r(x - 6, ty - 4, 12, 4, "y", 1); sh.rect_r(x - 2.5, ty - 30, 5, 26, "-")
        sh.region(drop_path(x, ty - 35, 2.6), "o")
    # bord met kerstkrans eronder (onder de stolp)
    cx, base = 100, ty - 1
    sh.ellipse_r(cx, base - 3, 40, 5, "-")
    sh.ellipse_r(cx, base - 16, 28, 12, "w"); sh.ellipse_r(cx, base - 17, 11, 4.5, "-")
    for k in range(7):
        a = math.radians(-180 + k * 30 - 0)
        sh.circle_r(cx + 20 * math.cos(math.radians(200 + k * 23)), base - 16 + 8 * math.sin(math.radians(200 + k * 23)) + 0, 2.4, "r")
    sh.region(f"M{cx} {base - 6}l-8 -4v8Zm0 0l8 -4v8Z", "g")
    sh.text(cx, base - 36, "Kom je mee-eten?", 6.2)
    # de stolp: scharnier onderaan (op de rand), optillen bij het knopje
    W2, H = 42, 50
    def dome(x0, y0):
        top = y0
        return unary_union([affinity.scale(Point(0, 0).buffer(1, 64), W2, H - 6).intersection(box(-W2, -H, W2, 0)).buffer(0), Point(0, -H + 4).buffer(5, 32)])
    d = dome(0, 0)
    spot = affinity.translate(d, cx, base - FG + 1)
    sh.line(geom_d(spot), "guide", "stroke-dasharray:2 2")
    glue_rect(sh, cx - W2 - 2, base - FG + 1, 2 * W2 + 4, FG)
    sh.rect_line(cx - W2 - 2, base - FG + 1, 2 * W2 + 4, FG, "guide", 0, "stroke-dasharray:2 2")
    # de losse stolp
    px, py = 100, bot + 58
    piece = unary_union([affinity.translate(d, px, py), box(px - W2 - 2, py, px + W2 + 2, py + FG)])
    sh.region(geom_d(affinity.translate(d, px, py)), "z")
    sh.line(f"M{px - W2 + 10} {py - 16}Q{px - W2 + 14} {py - 34} {px - 10} {py - 40}", "l", "stroke-width:1.4")
    sh.circle_r(px, py - H + 4, 3, "y")
    sh.seg(px - W2 - 2, py, px + W2 + 2, py, "fold")
    sh.line(geom_d(piece.buffer(.01)), "cut")
    sh.tip(16, bot + 9, "De stolp:")
    stars(sh, [(26, yf + 30), (174, yf + 30), (44, yf + 50), (156, yf + 50)], 4)
    sh.legend(["cut", "fold", "glue"], 279)
    assert piece.bounds[1] > bot + 4 and piece.bounds[3] < 272
    write(OUT, "uitnodiging-kerstdiner-stolp", sh, {"category": "eten", "age": "6-9", "kind": "kaart", "difficulty": 2, "minutes": 25, "holiday": "kerst", "paperGsm": 160,
        "materials": KAART_MAT + [{"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Uitnodiging voor een kerstdiner: wat zit er onder de stolp?", "printNote": STEVIG, "steps": [
            "Kleur de voorkant van de kaart (de onderste helft) en de losse stolp in.",
            "Knip de kaart en de stolp uit langs de streepjeslijnen. Het smalle randje onder de stolp blijft eraan vast.",
            "Vouw het randje van de stolp om langs de stippellijn.",
            "Smeer lijm op het grijze strookje onder het bord en plak het randje van de stolp erop. Nu kun je de stolp optillen: daaronder staat een kerstkrans.",
            "Vouw de kaart dubbel op de lange stippellijn, met de tekening aan de buitenkant, en vul de achterkant in."]}}})

# ---------- bedankt voor het logeren: kaart in de vorm van een koffer ----------
@do
def koffer():
    sh = Sheet()
    title(sh, "Bedankkaart: logeren bij opa en oma", 13, 10)
    xf, W, top, bot = 100, 84, 48, 222
    body = Polygon([(xf, top)] + [(xf + W - 8 + 8 * math.cos(math.radians(a)), top + 8 + 8 * math.sin(math.radians(a))) for a in range(-90, 1, 10)]
                   + [(xf + W - 8 + 8 * math.cos(math.radians(a)), bot - 8 + 8 * math.sin(math.radians(a))) for a in range(0, 91, 10)] + [(xf, bot)])
    handle = box(xf + 26, top - 16, xf + 58, top + 1)
    wheels = [Point(x, bot + 2).buffer(6.5, 32) for x in (xf + 14, xf + W - 14)]
    front = unary_union([body, handle] + wheels)
    def back(sh, fr):
        outline_text(sh, xf + W / 2, top + 26, "Lieve opa", 11); outline_text(sh, xf + W / 2, top + 40, "en oma,", 11)
        for k in range(6): sh.seg(xf + 8, top + 58 + k * 14, xf + W - 8, top + 58 + k * 14, "guide")
        sh.text(xf + 8, bot - 18, "Liefs van:", 6.5, "start"); sh.seg(xf + 44, bot - 18, xf + W - 8, bot - 18, "guide")
    fold_card(sh, front, "left", xf, "r", back)
    sh.rect_r(xf + 26, top - 16, 32, 17, "x", 4); sh.rect_r(xf + 32, top - 10, 20, 11, "-", 2)
    for x in (xf + 14, xf + W - 14): sh.circle_r(x, bot + 2, 6.5, "x"); sh.circle_r(x, bot + 2, 2.4, "z")
    for x in (xf + 18, xf + W - 18): sh.rect_r(x - 4, top, 8, bot - top, "w")
    sh.rect_r(xf + 8, top + 18, W - 16, 30, "-", 3)
    sh.text(xf + W / 2, top + 29, "Bedankt voor", 7); sh.text(xf + W / 2, top + 40, "het logeren!", 7)
    # stickers
    sh.region(heart_path(xf + 26, top + 66, 10), "m")
    sh.poly_r(star_pts(xf + 60, top + 70, 11, 5), "y")
    sh.circle_r(xf + 42, top + 96, 11, "b"); sh.region(moon_path(xf + 40, top + 96, 7), "y")
    sh.rect_r(xf + 12, top + 116, 34, 20, "l", 3); sh.text(xf + 29, top + 128.5, "opa & oma", 5.2)
    sh.circle_r(xf + 64, top + 126, 9, "o")
    for k in range(8):
        a = math.radians(k * 45)
        sh.seg(xf + 64 + 11 * math.cos(a), top + 126 + 11 * math.sin(a), xf + 64 + 14 * math.cos(a), top + 126 + 14 * math.sin(a), "l", "stroke-width:1.1")
    flower(sh, xf + 22, top + 154, 5, "p", "y"); flower(sh, xf + 62, top + 156, 5, "k", "y")
    sh.legend(["cut", "fold"], 276)
    write(OUT, "bedankkaart-logeren-koffer", sh, {"category": "thuis", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": KAART_MAT,
        "i18n": {"nl": {"name": "Bedankkaart voor opa en oma na het logeren (kaart in de vorm van een koffer)", "printNote": STEVIG, "steps": [
            "Kleur de koffer en alle stickers erop in. De rechterhelft is de voorkant.",
            "Knip de dubbele koffer uit langs de streepjeslijn, met het handvat en de wieltjes erbij.",
            "Vouw de kaart dubbel op de stippellijn in het midden, met de tekening aan de buitenkant.",
            "Schrijf op de achterkant wat je het leukste vond bij opa en oma, of teken het.",
            "Geef de kaart als je weer naar huis gaat, of stuur hem op."]}}})

# ---------- tandarts ----------
def front_tandarts(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Dank je wel, tandarts!", 13)
    cx, cy = 92, y0 + 72
    sh.region(f"M{cx - 30} {cy - 26}Q{cx - 30} {cy - 40} {cx - 16} {cy - 40}Q{cx - 8} {cy - 40} {cx} {cy - 34}Q{cx + 8} {cy - 40} {cx + 16} {cy - 40}Q{cx + 30} {cy - 40} {cx + 30} {cy - 26}"
              f"Q{cx + 30} {cy - 4} {cx + 24} {cy + 10}Q{cx + 20} {cy + 38} {cx + 12} {cy + 40}Q{cx + 6} {cy + 40} {cx + 4} {cy + 20}Q{cx} {cy + 10} {cx - 4} {cy + 20}"
              f"Q{cx - 6} {cy + 40} {cx - 12} {cy + 40}Q{cx - 20} {cy + 38} {cx - 24} {cy + 10}Q{cx - 30} {cy - 4} {cx - 30} {cy - 26}Z", "-")
    sh.dot(cx - 9, cy - 16, 2.4); sh.dot(cx + 9, cy - 16, 2.4)
    sh.line(f"M{cx - 9} {cy - 6}Q{cx} {cy + 2} {cx + 9} {cy - 6}", "l", "stroke-width:1.6")
    sh.circle_r(cx - 17, cy - 9, 3, "m"); sh.circle_r(cx + 17, cy - 9, 3, "m")
    for x, y, r in [(cx - 34, cy - 38, 5), (cx + 36, cy - 30, 4)]:
        sh.line(f"M{x - r} {y}H{x + r}M{x} {y - r}V{y + r}", "l", "stroke-width:1.4")
    # tandenborstel
    rot(sh, -35, 150, y0 + 82)
    sh.rect_r(146, y0 + 70, 6, 50, "t", 3); sh.rect_r(144, y0 + 52, 10, 20, "-", 1)
    for k in range(5): sh.rect_r(144 + k * 2, y0 + 44, 2, 8, "b") if False else sh.seg(145 + k * 2, y0 + 44, 145 + k * 2, y0 + 52, "l", "stroke-width:1.1")
    end(sh)
    stars(sh, [(30, y0 + 46), (34, y0 + 100), (170, y0 + 48), (168, y0 + 110)], 4.5)
    sh.text(100, y0 + 120, "Mijn tanden zijn weer schoon en sterk!", 6.5)
card("bedankkaart-tandarts", "Bedankkaart voor de tandarts", front_tandarts, "Bedankt voor de goede zorg!", "beroepen", "4-6",
     ["Schrijf binnenin je naam en neem de kaart mee naar je volgende controle. Je kunt hem ook aan de huisarts geven: verander dan het woord tandarts."]) if (not ONLY or ONLY in "tandarts") else None

# ---------- harmonica-uitnodiging voor pakjesavond ----------
@do
def harmonica_sint():
    sh = Sheet()
    title(sh, "Harmonica-uitnodiging: pakjesavond", 13, 10)
    PW, PH, X0, T = 56, 110, 8, 10
    rows = [22, 148]
    def mijter(cx, by, s=1):
        sh.region(f"M{cx - 16*s} {by}V{by - 30*s}Q{cx - 14*s} {by - 48*s} {cx} {by - 58*s}Q{cx + 14*s} {by - 48*s} {cx + 16*s} {by - 30*s}V{by}Z", "r")
        sh.rect_r(cx - 16 * s, by - 8 * s, 32 * s, 8 * s, "y")
        sh.rect_r(cx - 2.5 * s, by - 44 * s, 5 * s, 22 * s, "y"); sh.rect_r(cx - 9 * s, by - 37 * s, 18 * s, 5 * s, "y")
    def p1(x, y):
        outline_text(sh, x + PW / 2, y + 18, "Kom je?", 11)
        mijter(x + PW / 2, y + 88, .9)
        sh.text(x + PW / 2, y + 100, "Uitnodiging", 6)
    def p2(x, y):
        outline_text(sh, x + PW / 2, y + 16, "Pakjes-", 9.5); outline_text(sh, x + PW / 2, y + 27, "avond!", 9.5)
        for gx, gy, gw, gh, c in [(x + 6, y + 70, 24, 26, "g"), (x + 28, y + 76, 22, 20, "b"), (x + 14, y + 48, 20, 22, "p")]:
            sh.rect_r(gx, gy, gw, gh, c, 1); sh.rect_r(gx + gw / 2 - 2, gy, 4, gh, "y")
        sh.region(f"M{x + 24} {y + 48}Q{x + 16} {y + 40} {x + 14} {y + 47}ZM{x + 24} {y + 48}Q{x + 32} {y + 40} {x + 34} {y + 47}Z", "y")
    def p3(x, y):
        outline_text(sh, x + PW / 2, y + 16, "Wanneer?", 9)
        sh.rect_r(x + 12, y + 26, 32, 30, "-", 2); sh.rect_r(x + 12, y + 26, 32, 8, "r", 2)
        sh.circle_r(x + 20, y + 26, 1.8, "z"); sh.circle_r(x + 36, y + 26, 1.8, "z")
        sh.text(x + PW / 2, y + 50, "dec", 7)
        lines(sh, x + 6, x + PW - 6, y + 72, 3, 12)
    def p4(x, y):
        outline_text(sh, x + PW / 2, y + 16, "Waar?", 9.5)
        sh.poly_r([(x + 12, y + 40), (x + 28, y + 26), (x + 44, y + 40)], "r"); sh.rect_r(x + 14, y + 40, 28, 20, "y")
        sh.rect_r(x + 24, y + 48, 8, 12, "w"); sh.rect_r(x + 34, y + 30, 5, 8, "w")
        sh.region(f"M{x + 36.5} {y + 28}Q{x + 34} {y + 24} {x + 38} {y + 21}", "-") if False else None
        lines(sh, x + 6, x + PW - 6, y + 72, 3, 12)
    def p5(x, y):
        outline_text(sh, x + PW / 2, y + 16, "Neem mee:", 8.5)
        for i, k in enumerate(["een surprise", "een gedicht", "een liedje"]):
            sh.rect_line(x + 6, y + 26 + i * 11, 6, 6, "l", 1, "stroke-width:1")
            sh.text(x + 15, y + 31.5 + i * 11, k, 5, "start")
        # schoen met wortel
        sx, sy = x + 26, y + 96
        sh.region(f"M{sx - 18} {sy}V{sy - 10}Q{sx - 18} {sy - 16} {sx - 10} {sy - 16}H{sx - 2}Q{sx + 6} {sy - 8} {sx + 18} {sy - 6}Q{sx + 22} {sy - 4} {sx + 22} {sy}Z", "w")
        sh.region(f"M{sx - 12} {sy - 15}L{sx - 4} {sy - 34}Q{sx - 1} {sy - 36} {sx} {sy - 33}L{sx - 4} {sy - 15}Z", "o")
        sh.line(f"M{sx - 3} {sy - 34}Q{sx - 6} {sy - 42} {sx - 10} {sy - 40}M{sx - 2} {sy - 35}Q{sx + 2} {sy - 42} {sx + 5} {sy - 39}", "l", "stroke-width:1.2")
    def p6(x, y):
        outline_text(sh, x + PW / 2, y + 18, "Tot dan!", 10)
        # stoomboot
        bx, by = x + PW / 2, y + 74
        sh.region(f"M{bx - 24} {by}H{bx + 24}L{bx + 18} {by + 12}H{bx - 18}Z", "n")
        sh.rect_r(bx - 14, by - 12, 26, 12, "-"); sh.rect_r(bx + 2, by - 26, 7, 14, "r")
        for k in range(3): sh.circle_r(bx - 9 + k * 7, by - 6, 2, "b")
        sh.circle_line(bx + 8, by - 32, 3, "l", "stroke-width:1"); sh.circle_line(bx + 13, by - 38, 4, "l", "stroke-width:1")
        sh.line(f"M{x + 4} {by + 16}Q{x + 11} {by + 12} {x + 18} {by + 16}T{x + 32} {by + 16}T{x + 46} {by + 16}", "l", "stroke-width:1.1")
        for k in range(5): sh.circle_r(x + 10 + k * 9, y + 100, 2.6, "w")
    panels = [p1, p2, p3, p4, p5, p6]
    for r, y in enumerate(rows):
        xr = X0 + 3 * PW
        out = f"M{X0} {y}H{xr}" + (f"L{xr + T} {y + 6}V{y + PH - 6}L{xr} {y + PH}" if r == 0 else f"V{y + PH}") + f"H{X0}Z"
        sh.line(out, "cut")
        if r == 0:
            glue_path(sh, f"M{xr} {y}L{xr + T} {y + 6}V{y + PH - 6}L{xr} {y + PH}Z"); sh.seg(xr, y, xr, y + PH, "fold")
        for k in (1, 2): sh.seg(X0 + k * PW, y, X0 + k * PW, y + PH, "fold")
        for k in range(3):
            panels[r * 3 + k](X0 + k * PW, y)
            sh.text(X0 + k * PW + PW - 5, y + PH - 4, str(r * 3 + k + 1), 4.8)
    sh.tip(X0 + 3 * PW + 13, 160, "plak hier", "start") if False else None
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "harmonica-uitnodiging-pakjesavond", sh, {"category": "feest", "age": "6-9", "kind": "kaart", "difficulty": 2, "minutes": 30, "holiday": "sinterklaas", "paperGsm": 160,
        "materials": KAART_MAT + [{"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Harmonica-uitnodiging voor pakjesavond", "printNote": STEVIG, "steps": [
            "Kleur alle zes de vakjes in en vul in wanneer en waar jullie pakjesavond vieren. Kruis aan wat je gasten mee moeten nemen.",
            "Knip de twee stroken uit langs de streepjeslijn. Het grijze flapje blijft aan vakje 3 vast.",
            "Smeer lijm op het grijze flapje en leg vakje 4 erop, met de linkerrand van vakje 4 precies op de stippellijn. Nu heb je één lange strook van 1 tot 6.",
            "Vouw de strook als een harmonica: de eerste stippellijn naar achteren, de volgende naar voren, en zo om en om.",
            "Vouw hem dicht met vakje 1 bovenop. Wie de kaart uittrekt, leest de hele uitnodiging."]}}})

# =====================================================================
# 3. DECORATIES
# =====================================================================

def bird(sh, cx, cy, s, code, wing, facing=1):
    """Vogeltje (kijkt naar rechts bij facing=1). Geeft de buitenvorm terug."""
    k = s / 20
    def X(x): return cx + facing * x * k
    def Y(y): return cy + y * k
    body = affinity.scale(Point(cx, cy).buffer(1, 48), 20 * k, 14 * k)
    head = Point(X(14), Y(-10)).buffer(9 * k, 32)
    tail = Polygon([(X(-16), Y(-2)), (X(-32), Y(-14)), (X(-30), Y(2)), (X(-14), Y(6))])
    beak = Polygon([(X(21), Y(-13)), (X(29), Y(-9)), (X(21), Y(-6))])
    sh.poly_r(list(tail.exterior.coords)[:-1], code)
    sh.region(geom_d(unary_union([body, head])), code)
    sh.poly_r(list(beak.exterior.coords)[:-1], "o")
    sh.dot(X(16), Y(-12), 1.6 * k + .4)
    sh.region(f"M{f(X(-8))} {f(Y(-2))}Q{f(X(2))} {f(Y(-20))} {f(X(12))} {f(Y(-4))}Q{f(X(4))} {f(Y(8))} {f(X(-8))} {f(Y(-2))}Z", wing)
    sh.circle_r(X(6), Y(4), 2 * k, "-") if False else None
    return unary_union([body, head, tail, beak])

# ---------- welkomstbord voor de voordeur ----------
@do
def welkomstbord():
    sh = Sheet()
    shape = unary_union([box(16, 70, 184, 262), affinity.scale(Point(100, 70).buffer(1, 96), 84, 46).intersection(box(0, 0, 200, 70))])
    sh.region(geom_d(shape), "b")
    sh.line(geom_d(shape), "cut")
    inner = shape.buffer(-9)
    sh.region(geom_d(inner), "-")
    # zon in de boog
    sh.circle_r(100, 52, 13, "y")
    for k in range(12):
        a = math.radians(180 + k * 180 / 11)
        sh.seg(100 + 17 * math.cos(a), 52 + 17 * math.sin(a), 100 + 22 * math.cos(a), 52 + 22 * math.sin(a), "l", "stroke-width:1.4")
    sh.dot(95, 50, 1.5); sh.dot(105, 50, 1.5); sh.line("M95 56Q100 60 105 56", "l", "stroke-width:1.2")
    outline_text(sh, 100, 104, "Welkom!", 28)
    sh.text(100, 122, "Hier wonen:", 8)
    for k in range(4): sh.seg(46, 140 + k * 17, 154, 140 + k * 17, "guide")
    # bloemen en vogeltjes
    for k, x in enumerate([34, 62, 138, 166]):
        sh.line(f"M{x} 250V{226}", "l", "stroke-width:1.4")
        sh.region(leaf_path(x + 5, 240, 3, 6), "g")
        flower(sh, x, 220, 5.5, "rmpo"[k], "y")
    bird(sh, 50, 64, 13, "r", "o", 1); bird(sh, 150, 64, 13, "t", "y", -1)
    sh.region(heart_path(100, 228, 12), "r")
    for x in (66, 134): hole(sh, x, 36, 2.6)
    sh.legend(["cut"], 276)
    write(OUT, "welkomstbord-voordeur", sh, {"category": "thuis", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 25, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}, {"slug": "stiften", "optional": True}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Welkomstbord voor de voordeur", "printNote": "Op stevig papier (160 gram) blijft het bord mooi hangen. Hangt het buiten? Schuif het in een plastic insteekhoes.", "steps": [
            "Schrijf de namen op van iedereen die bij jullie woont: mensen en dieren.",
            "Kleur de rand, de zon, de vogeltjes en de bloemen in.",
            "Knip het bord uit langs de streepjeslijn.",
            "Prik de twee gaatjes bovenin door (vraag een volwassene om hulp) en knoop er een touwtje door.",
            "Hang het bord aan de voordeur of bij je kamerdeur."]}}})

# ---------- verjaardagskalender: 12 maanden op één vel ----------
@do
def kalender():
    sh = Sheet()
    sh.rect_line(6, 4, 188, 266, "cut", 4)
    title(sh, "Verjaardagskalender", 18, 12)
    sh.text(100, 27, "Schrijf in elke maand wie er jarig is, en op welke dag.", 5.6)
    names = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]
    def ic(i, x, y):
        if i == 0:
            for k in range(3):
                a = math.radians(k * 60)
                sh.seg(x - 6 * math.cos(a), y - 6 * math.sin(a), x + 6 * math.cos(a), y + 6 * math.sin(a), "l", "stroke-width:1.3")
        elif i == 1: sh.region(heart_path(x, y, 7), "r")
        elif i == 2:
            sh.seg(x, y + 2, x, y + 8, "l", "stroke-width:1.2")
            sh.region(f"M{x - 5} {y - 6}L{x - 2.5} {y - 2}L{x} {y - 7}L{x + 2.5} {y - 2}L{x + 5} {y - 6}V{y}Q{x + 5} {y + 3} {x} {y + 3}Q{x - 5} {y + 3} {x - 5} {y}Z", "r")
        elif i == 3:
            sh.ellipse_r(x, y + 1, 5, 6.5, "b"); sh.line(f"M{x - 5} {y + 1}l2.5 -2 2.5 2 2.5 -2 2.5 2", "l", "stroke-width:.9")
        elif i == 4: flower(sh, x, y, 3.2, "m", "y")
        elif i == 5:
            sh.region(f"M{x - 5} {y - 3}Q{x - 6} {y + 4} {x} {y + 7}Q{x + 6} {y + 4} {x + 5} {y - 3}Q{x} {y - 5} {x - 5} {y - 3}Z", "r")
            sh.region(f"M{x - 4} {y - 4}L{x} {y - 2}L{x + 4} {y - 4}L{x} {y - 7}Z", "g")
        elif i == 6:
            sh.circle_r(x, y, 4, "y")
            for k in range(8):
                a = math.radians(k * 45); sh.seg(x + 5.5 * math.cos(a), y + 5.5 * math.sin(a), x + 7.5 * math.cos(a), y + 7.5 * math.sin(a), "l", "stroke-width:1")
        elif i == 7:
            sh.poly_r([(x - 4, y), (x + 4, y), (x, y + 9)], "w"); sh.circle_r(x, y - 2, 4.4, "k")
        elif i == 8:
            sh.circle_r(x, y + 1, 5.5, "r"); sh.line(f"M{x} {y - 4}V{y - 7}", "l", "stroke-width:1.2"); sh.region(leaf_path(x + 3, y - 6, 1.8, 3), "g")
        elif i == 9:
            sh.region(leaf_path(x, y, 4.5, 7.5), "o"); sh.seg(x, y - 6, x, y + 8, "l", "stroke-width:.9")
        elif i == 10:
            sh.region(f"M{x - 7} {y}Q{x - 6} {y - 7} {x} {y - 7}Q{x + 6} {y - 7} {x + 7} {y}Z", "r"); sh.rect_r(x - 2.5, y, 5, 6, "-")
        else:
            sh.poly_r(star_pts(x, y, 7, 3), "y")
    for i, nm in enumerate(names):
        c, r = i % 3, i // 3
        x, y, w, h = 11 + c * 60, 32 + r * 58, 58, 55
        sh.rect_line(x, y, w, h, "l", 3, "stroke-width:1")
        sh.rect_r(x + 3, y + 3, w - 6, 12, "ytgobmrplkno"[i] if False else "rmglyotbwonb"[i], 2)
        sh.text(x + 6, y + 12, nm, 6.2, "start")
        ic(i, x + w - 10, y + 25)
        for k in range(3):
            yy = y + 30 + k * 9.5
            sh.seg(x + 5, yy, x + w - (20 if k == 0 else 5), yy, "guide")
    sh.legend(["cut"], 277)
    write(OUT, "verjaardagskalender-12-maanden", sh, {"category": "feest", "age": "6-9", "kind": "kaart", "difficulty": 1, "minutes": 30, "holiday": "verjaardag", "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "potlood"}, SCHAAR, {"slug": "plakband", "optional": True}],
        "i18n": {"nl": {"name": "Verjaardagskalender: alle 12 maanden op één vel", "printNote": "Op stevig papier (160 gram) gaat de kalender jaren mee.", "steps": [
            "Kleur de balkjes met de namen van de maanden en de plaatjes in.",
            "Vraag aan je familie en vriendjes wanneer ze jarig zijn.",
            "Schrijf bij de goede maand de dag en de naam, bijvoorbeeld: 12 – oma.",
            "Knip de kalender uit langs de streepjeslijn en hang hem op een plek waar je hem elke dag ziet, zoals in de keuken of op de wc."]}}})

# ---------- naamkaartjes voor aan tafel ----------
@do
def naamkaartjes():
    sh = Sheet()
    title(sh, "Naamkaartjes voor aan tafel", 13, 12)
    sh.text(100, 21, "Schrijf op beide kanten dezelfde naam: dan kan iedereen hem lezen.", 5.5)
    def ballon(x, y): balloon(sh, x - 3, y - 4, 5.5, "r", False); balloon(sh, x + 5, y - 2, 5, "b", False)
    def ster(x, y): sh.poly_r(star_pts(x, y, 9, 4), "y")
    def bloem(x, y): flower(sh, x, y, 4.5, "m", "y")
    def hart(x, y): sh.region(heart_path(x, y, 9), "r")
    def taart(x, y):
        sh.rect_r(x - 9, y - 2, 18, 9, "k", 1.5); sh.rect_r(x - 1, y - 9, 2, 7, "b"); sh.region(drop_path(x, y - 11, 1.6), "o")
    def kroon(x, y): sh.poly_r([(x - 9, y + 6), (x - 9, y - 5), (x - 4.5, y + 1), (x, y - 8), (x + 4.5, y + 1), (x + 9, y - 5), (x + 9, y + 6)], "y")
    icons = [ballon, ster, bloem, hart, taart, kroon]
    for i, icf in enumerate(icons):
        c, r = i % 2, i // 2
        x, y, w, hh = 12 + c * 90, 28 + r * 80, 86, 37
        sh.rect_line(x, y, w, 2 * hh, "cut", 2)
        sh.seg(x, y + hh, x + w, y + hh, "fold")
        code = "tymrkg"[i]
        for side in (0, 1):
            if side == 1: sh.raw(f'<g transform="rotate(180 {x + w / 2} {y + hh / 2})">'); oy = y
            else: oy = y + hh
            if side == 0: sh.region(f"M{x + 3} {oy + 3}H{x + w - 3}V{oy + hh - 3}H{x + 3}Z", code)
            else: sh.region(f"M{x + 3} {oy + hh - 3}H{x + w - 3}V{oy + 3}H{x + 3}Z", code)
            sh.rect_r(x + 27, oy + 9, w - 32, hh - 18, "-", 3)
            icf(x + 13, oy + hh / 2)
            sh.seg(x + 31, oy + hh / 2 + 4, x + w - 10, oy + hh / 2 + 4, "guide")
            if side == 1: sh.raw("</g>")
    sh.legend(["cut", "fold"], 276)
    write(OUT, "naamkaartjes-tafel", sh, {"category": "eten", "age": "6-9", "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "stiften"}, SCHAAR, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Naamkaartjes voor aan tafel", "printNote": "Op stevig papier (160 gram) blijven de kaartjes goed staan.", "steps": [
            "Schrijf op elk kaartje een naam, op allebei de helften.",
            "Kleur de randjes en de plaatjes in.",
            "Knip de kaartjes los langs de streepjeslijnen.",
            "Vouw elk kaartje dubbel op de stippellijn, met de tekening aan de buitenkant. Zet het als een dakje bij een bord: zo weet iedereen waar hij zit, bij een verjaardag, kerstdiner of zomaar."]}}})

# ---------- boekenleggers in nieuwe thema's ----------
def bookmarks(slug, name, title_, makers, cat, age):
    sh = Sheet()
    title(sh, title_, 13, 12)
    for i, mk in enumerate(makers):
        x, y, w, h = 12 + i * 45, 24, 41, 238
        code = mk(sh, x, y, w, h)
        sh.rect_line(x, y, w, h, "cut", 4)
        hole(sh, x + w / 2, y + 9, 2.6)
    sh.legend(["cut"], 276)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw", "optional": True}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Op stevig papier (160 gram) blijven de boekenleggers langer mooi.", "steps": [
            "Kleur de vier boekenleggers in.",
            "Knip ze uit langs de streepjeslijn.",
            "Wil je een kwastje? Prik het gaatje bovenin door (vraag een volwassene om hulp) en knoop er een stukje touw of wol door.",
            "Leg er een in je boek, en geef de andere aan iemand die ook graag leest."]}}})

def bm_raket(sh, x, y, w, h):
    sh.region(f"M{x} {y}H{x + w}V{y + h}H{x}Z", "n")
    cx = x + w / 2
    for k, (sx, sy) in enumerate([(6, 22), (34, 40), (10, 70), (30, 170), (8, 200), (32, 226), (20, 120)]):
        sh.poly_r(star_pts(x + sx, y + sy, 3.6, 1.6), "y")
    by = y + 140
    sh.region(f"M{cx} {by - 70}Q{cx + 14} {by - 52} {cx + 13} {by}H{cx - 13}Q{cx - 14} {by - 52} {cx} {by - 70}Z", "-")
    sh.region(f"M{cx - 13} {by - 14}L{cx - 19} {by + 4}H{cx - 13}ZM{cx + 13} {by - 14}L{cx + 19} {by + 4}H{cx + 13}Z", "r")
    sh.circle_r(cx, by - 38, 6, "b")
    sh.region(f"M{cx} {by - 70}Q{cx + 8} {by - 62} {cx + 10} {by - 54}H{cx - 10}Q{cx - 8} {by - 62} {cx} {by - 70}Z", "r")
    sh.region(f"M{cx - 8} {by}Q{cx} {by + 30} {cx + 8} {by}Z", "o"); sh.region(f"M{cx - 4} {by}Q{cx} {by + 16} {cx + 4} {by}Z", "y")
def bm_planeten(sh, x, y, w, h):
    sh.region(f"M{x} {y}H{x + w}V{y + h}H{x}Z", "p")
    cx = x + w / 2
    sh.circle_r(cx, y + 50, 14, "o"); sh.line(f"M{cx - 20} {y + 54}Q{cx} {y + 42} {cx + 20} {y + 46}", "l", "stroke-width:1.6")
    sh.circle_r(cx - 6, y + 104, 9, "t"); sh.circle_r(cx + 8, y + 134, 6, "r")
    sh.circle_r(cx, y + 186, 13, "b"); sh.circle_line(cx - 4, y + 182, 3, "l", "stroke-width:1"); sh.circle_line(cx + 5, y + 192, 2, "l", "stroke-width:1")
    stars(sh, [(x + 8, y + 24), (x + 33, y + 84), (x + 8, y + 150), (x + 33, y + 216), (x + 30, y + 160)], 3.6)
def bm_astronaut(sh, x, y, w, h):
    sh.region(f"M{x} {y}H{x + w}V{y + h}H{x}Z", "x")
    cx, cy = x + w / 2, y + 96
    sh.rect_r(cx - 11, cy + 12, 9, 26, "-", 3); sh.rect_r(cx + 2, cy + 12, 9, 26, "-", 3)
    sh.rect_r(cx - 14, cy - 14, 28, 32, "-", 6)
    sh.rect_r(cx - 7, cy - 6, 14, 10, "b", 2)
    sh.rect_r(cx - 20, cy - 12, 7, 22, "-", 3); sh.rect_r(cx + 13, cy - 12, 7, 22, "-", 3)
    sh.circle_r(cx, cy - 26, 14, "-"); sh.ellipse_r(cx, cy - 25, 10, 8, "b")
    sh.region(moon_path(cx - 4, y + 196, 14), "y")
    stars(sh, [(x + 8, y + 26), (x + 32, y + 40), (x + 30, y + 160), (x + 8, y + 140), (x + 32, y + 224)], 3.6)
def bm_maan(sh, x, y, w, h):
    sh.region(f"M{x} {y}H{x + w}V{y + h}H{x}Z", "n")
    cx = x + w / 2
    sh.circle_r(cx, y + 56, 15, "z")
    for dx, dy, r in [(-5, -6, 3.5), (6, 2, 2.6), (-2, 8, 2)]: sh.circle_line(cx + dx, y + 56 + dy, r, "l", "stroke-width:1")
    # vliegende schotel
    sy = y + 130
    sh.ellipse_r(cx, sy - 6, 9, 8, "b"); sh.ellipse_r(cx, sy, 18, 6, "g")
    for k in (-10, 0, 10): sh.circle_r(cx + k, sy, 1.8, "y")
    sh.poly_r([(cx - 8, sy + 6), (cx + 8, sy + 6), (cx + 14, sy + 30), (cx - 14, sy + 30)], "y")
    stars(sh, [(x + 8, y + 26), (x + 34, y + 96), (x + 8, y + 196), (x + 30, y + 214), (x + 10, y + 100)], 3.6)
    sh.circle_r(cx, y + 222, 4, "r")
@do
def boekenleggers_ruimte():
    bookmarks("boekenleggers-ruimte", "Boekenleggers: de ruimte in", "Boekenleggers: de ruimte in", [bm_raket, bm_planeten, bm_astronaut, bm_maan], "ruimte", "6-9")

def bm_vissen(sh, x, y, w, h):
    sh.region(f"M{x} {y}H{x + w}V{y + h}H{x}Z", "b")
    for k, (dy, c, s, d) in enumerate([(40, "o", 12, 1), (92, "y", 10, -1), (140, "r", 12, 1), (196, "p", 10, -1)]):
        cx = x + w / 2
        sh.raw(f'<g transform="translate({f(2 * cx)} 0) scale(-1 1)">') if d < 0 else None
        sh.region(fish_path(cx, y + dy, s), c); sh.dot(cx - 5, y + dy - 1, 1.3)
        sh.raw("</g>") if d < 0 else None
    for dx, dy, r in [(8, 66, 2.4), (32, 120, 2), (10, 172, 2.6), (30, 226, 2)]: sh.circle_line(x + dx, y + dy, r, "l", "stroke-width:1")
def bm_octopus(sh, x, y, w, h):
    sh.region(f"M{x} {y}H{x + w}V{y + h}H{x}Z", "t")
    cx, cy = x + w / 2, y + 80
    for k in range(5):
        xx = cx - 14 + k * 7
        sh.line(f"M{xx} {cy + 10}Q{xx + (6 if k % 2 else -6)} {cy + 40} {xx} {cy + 60}Q{xx - 3} {cy + 68} {xx + 3} {cy + 70}", "l", "stroke-width:4")
    sh.region(f"M{cx - 16} {cy + 14}V{cy - 6}Q{cx - 16} {cy - 30} {cx} {cy - 30}Q{cx + 16} {cy - 30} {cx + 16} {cy - 6}V{cy + 14}Z", "m")
    sh.dot(cx - 6, cy - 4, 2.2); sh.dot(cx + 6, cy - 4, 2.2); sh.line(f"M{cx - 4} {cy + 4}Q{cx} {cy + 8} {cx + 4} {cy + 4}", "l", "stroke-width:1.2")
    sh.region(f"M{x + 4} {y + h}Q{x + 10} {y + h - 30} {x + 8} {y + h - 50}Q{x + 16} {y + h - 30} {x + 16} {y + h}Z", "g")
    sh.region(f"M{x + 22} {y + h}Q{x + 30} {y + h - 24} {x + 34} {y + h - 40}Q{x + 36} {y + h - 20} {x + 34} {y + h}Z", "g")
    for dx, dy, r in [(10, 24, 2.4), (30, 36, 2), (28, 180, 2.6)]: sh.circle_line(x + dx, y + dy, r, "l", "stroke-width:1")
def bm_schildpad(sh, x, y, w, h):
    sh.region(f"M{x} {y}H{x + w}V{y + h}H{x}Z", "n")
    cx, cy = x + w / 2, y + 110
    for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        sh.ellipse_r(cx + sx * 14, cy + sy * 16, 5, 8, "l")
    sh.circle_r(cx, cy - 32, 7, "l"); sh.dot(cx - 3, cy - 33, 1.3); sh.dot(cx + 3, cy - 33, 1.3)
    sh.ellipse_r(cx, cy, 15, 24, "g")
    sh.poly_r([(cx, cy - 10), (cx + 8, cy - 4), (cx + 8, cy + 6), (cx, cy + 12), (cx - 8, cy + 6), (cx - 8, cy - 4)], "y")
    sh.region(f"M{x} {y + h - 20}Q{x + w / 2} {y + h - 30} {x + w} {y + h - 20}V{y + h}H{x}Z", "y")
    for dx, dy, r in [(10, 30, 2.4), (30, 44, 2), (32, 170, 2.6), (8, 190, 2)]: sh.circle_line(x + dx, y + dy, r, "l", "stroke-width:1")
def bm_kwal(sh, x, y, w, h):
    sh.region(f"M{x} {y}H{x + w}V{y + h}H{x}Z", "b")
    for cy, s, c in [(70, 1, "p"), (160, .8, "k")]:
        cx = x + w / 2; cy = y + cy
        for k in range(4):
            xx = cx - 9 * s + k * 6 * s
            sh.line(f"M{xx} {cy + 4}q{4 * s} {10 * s} 0 {20 * s}t0 {20 * s}", "l", "stroke-width:1.4")
        sh.region(f"M{cx - 16 * s} {cy + 4}Q{cx - 16 * s} {cy - 18 * s} {cx} {cy - 18 * s}Q{cx + 16 * s} {cy - 18 * s} {cx + 16 * s} {cy + 4}Q{cx + 8 * s} {cy} {cx} {cy + 4}Q{cx - 8 * s} {cy} {cx - 16 * s} {cy + 4}Z", c)
        sh.dot(cx - 5 * s, cy - 5 * s, 1.4); sh.dot(cx + 5 * s, cy - 5 * s, 1.4)
    for dx, dy, r in [(8, 30, 2.4), (32, 120, 2), (10, 220, 2.6)]: sh.circle_line(x + dx, y + dy, r, "l", "stroke-width:1")
@do
def boekenleggers_onderwater():
    bookmarks("boekenleggers-onderwater", "Boekenleggers: onder water", "Boekenleggers: onder water", [bm_vissen, bm_octopus, bm_schildpad, bm_kwal], "zee", "4-6")

# ---------- cadeaulabels: dierenkopjes ----------
@do
def labels_dieren():
    sh = Sheet()
    title(sh, "Cadeaulabels: dierenkopjes", 13, 12)
    R = 30
    SC = 25 / 30
    def head(kind, cx, cy):
        parts = [Point(cx, cy).buffer(R, 64)]
        if kind == "beer": parts += [Point(cx + s * 22, cy - 22).buffer(10, 32) for s in (-1, 1)]
        if kind == "kat": parts += [Polygon([(cx + s * 26, cy - 14), (cx + s * 24, cy - 40), (cx + s * 6, cy - 28)]) for s in (-1, 1)]
        if kind == "konijn": parts += [affinity.rotate(affinity.scale(Point(cx + s * 12, cy - 38).buffer(1, 32), 7, 18), -s * 12, origin=(cx + s * 12, cy - 22)) for s in (-1, 1)]
        if kind == "vos": parts += [Polygon([(cx + s * 28, cy - 10), (cx + s * 26, cy - 42), (cx + s * 8, cy - 28)]) for s in (-1, 1)]
        if kind == "muis": parts += [Point(cx + s * 26, cy - 22).buffer(14, 32) for s in (-1, 1)]
        if kind == "uil": parts += [Polygon([(cx + s * 22, cy - 18), (cx + s * 26, cy - 38), (cx + s * 8, cy - 28)]) for s in (-1, 1)]
        return unary_union(parts)
    prev = []
    kinds = [("beer", "w"), ("kat", "z"), ("konijn", "-"), ("vos", "o"), ("muis", "z"), ("uil", "w")]
    for i, (kind, c) in enumerate(kinds):
        col, row = i % 2, i // 2
        cx, cy = 56 + col * 88, 76 + row * 84
        sh.raw(f'<g transform="translate({f(cx)} {f(cy)}) scale({SC}) translate({f(-cx)} {f(-cy)})">')
        g = head(kind, cx, cy)
        sh.region(geom_d(g), c)
        # binnenoren
        if kind == "beer":
            for s in (-1, 1): sh.circle_r(cx + s * 22, cy - 22, 5, "k")
        if kind == "muis":
            for s in (-1, 1): sh.circle_r(cx + s * 26, cy - 22, 8, "k")
        if kind in ("kat", "vos"):
            for s in (-1, 1): sh.poly_r([(cx + s * 22, cy - 20), (cx + s * 22, cy - 34), (cx + s * 11, cy - 26)], "k" if kind == "kat" else "x")
        if kind == "konijn":
            for s in (-1, 1):
                sh.raw(f'<g transform="rotate({-s * 12} {cx + s * 12} {cy - 22})">'); sh.ellipse_r(cx + s * 12, cy - 38, 3.5, 13, "k"); sh.raw("</g>")
            sh.circle_r(cx, cy, R, "-")
        # gezichtje bovenin het kopje
        ey = cy - 12
        if kind == "uil":
            for s in (-1, 1): sh.circle_r(cx + s * 9, ey, 7, "y"); sh.dot(cx + s * 9, ey, 2.4)
            sh.poly_r([(cx - 3, ey + 4), (cx + 3, ey + 4), (cx, ey + 9)], "o")
        else:
            if kind == "vos": sh.region(f"M{cx - 28} {cy - 4}Q{cx - 12} {cy - 6} {cx} {cy + 4}Q{cx + 12} {cy - 6} {cx + 28} {cy - 4}Q{cx + 22} {cy + 24} {cx} {cy + 30}Q{cx - 22} {cy + 24} {cx - 28} {cy - 4}Z", "-")
            sh.dot(cx - 9, ey, 2.2); sh.dot(cx + 9, ey, 2.2)
            sh.ellipse_r(cx, ey + 6, 3, 2.2, "x" if kind in ("beer", "vos") else "k")
            if kind in ("kat", "muis", "konijn"):
                sh.line(f"M{cx - 5} {ey + 6}H{cx - 17}M{cx + 5} {ey + 6}H{cx + 17}", "l", "stroke-width:.8")
        sh.rect_r(cx - 22, cy + 3, 44, 20, "-", 3)
        sh.text(cx - 19, cy + 11, "Voor: ..........", 6, "start")
        sh.text(cx - 19, cy + 19.5, "Van: ...........", 6, "start")
        hole(sh, cx, cy - R + 6, 2.6)
        sh.line(geom_d(g.buffer(3, join_style=1)), "cut")
        sh.raw("</g>")
        gs = affinity.scale(g.buffer(3), SC, SC, origin=(cx, cy))
        assert gs.bounds[3] < 273 and gs.bounds[1] > 18, gs.bounds
        if i >= 2: assert not gs.intersects(prev[i - 2]), kind
        prev.append(gs)
    sh.legend(["cut"], 279)
    write(OUT, "cadeaulabels-dierenkopjes", sh, {"category": "dieren", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Cadeaulabels: zes dierenkopjes", "printNote": "Print op stevig papier (160 gram) als je het hebt.", "steps": [
            "Kleur de dierenkopjes in: een beer, een kat, een konijn, een vos, een muis en een uil.",
            "Schrijf op voor wie het cadeautje is en van wie.",
            "Knip de kopjes uit langs de streepjeslijn.",
            "Prik het gaatje bovenin door (vraag een volwassene om hulp) en bind het label met een touwtje of lintje aan het cadeau."]}}})

# ---------- cadeaulabels: lente ----------
@do
def labels_lente():
    sh = Sheet()
    title(sh, "Cadeaulabels: lente", 13, 12)
    def tulp(x, y):
        sh.line(f"M{x} {y - 2}V{y + 12}", "l", "stroke-width:1.4"); sh.region(leaf_path(x + 4, y + 8, 2.6, 5), "g")
        sh.region(f"M{x - 6} {y - 12}L{x - 3} {y - 7}L{x} {y - 13}L{x + 3} {y - 7}L{x + 6} {y - 12}V{y - 5}Q{x + 6} {y} {x} {y}Q{x - 6} {y} {x - 6} {y - 5}Z", "r")
    def vlinder(x, y):
        for s in (-1, 1):
            sh.ellipse_r(x + s * 7, y - 5, 6.5, 6, "p"); sh.ellipse_r(x + s * 6, y + 6, 4.5, 4.5, "m")
        sh.ellipse_r(x, y, 2, 10, "x")
        sh.line(f"M{x - 1} {y - 9}Q{x - 4} {y - 15} {x - 6} {y - 15}M{x + 1} {y - 9}Q{x + 4} {y - 15} {x + 6} {y - 15}", "l", "stroke-width:1")
    def bij(x, y):
        sh.ellipse_r(x - 2, y - 9, 5, 4, "b"); sh.ellipse_r(x + 4, y - 9, 5, 4, "b")
        sh.ellipse_r(x, y, 11, 7.5, "y")
        sh.line(f"M{x - 3} {y - 7}V{y + 7}M{x + 3} {y - 7}V{y + 7}", "l", "stroke-width:2.2")
        sh.dot(x + 8, y - 1, 1.2); sh.poly_r([(x - 11, y - 1), (x - 15, y), (x - 11, y + 1)], "x")
    def kuiken(x, y):
        sh.circle_r(x, y + 3, 9, "y"); sh.circle_r(x + 6, y - 7, 6, "y")
        sh.dot(x + 8, y - 8, 1.2); sh.poly_r([(x + 11, y - 7), (x + 15, y - 5), (x + 11, y - 4)], "o")
        sh.line(f"M{x - 2} {y + 12}v3M{x + 3} {y + 12}v3", "l", "stroke-width:1.2")
    def lieveheer(x, y):
        sh.circle_r(x, y - 9, 4, "x"); sh.ellipse_r(x, y + 1, 10, 10, "r")
        sh.seg(x, y - 9, x, y + 11, "l", "stroke-width:1.2")
        for dx, dy in [(-5, -2), (5, -2), (-4, 6), (4, 6)]: sh.dot(x + dx, y + dy, 1.7)
    def regenboog(x, y):
        for i, c in enumerate("ryb"):
            r = 13 - i * 3.5
            sh.region(f"M{f(x - r)} {y + 4}A{f(r)} {f(r)} 0 0 1 {f(x + r)} {y + 4}H{f(x + r - 3.5)}A{f(r - 3.5)} {f(r - 3.5)} 0 0 0 {f(x - r + 3.5)} {y + 4}Z", c)
        sh.region(cloud_path(x - 10, y + 5, 4), "-"); sh.region(cloud_path(x + 10, y + 5, 4), "-")
    pics = [tulp, vlinder, bij, kuiken, lieveheer, regenboog]
    for i, pic in enumerate(pics):
        col, row = i % 2, i // 2
        x, y, w, h = 14 + col * 88, 28 + row * 80, 84, 70
        outline = f"M{x + 16} {y}H{x + w}V{y + h}H{x + 16}L{x} {y + h - 16}V{y + 16}Z"
        sh.region(outline, "lkybtm"[i])
        sh.rect_r(x + 12, y + 8, w - 18, h - 16, "-", 4)
        pic(x + 29, y + h / 2)
        sh.text(x + 48, y + 26, "Voor:", 6, "start"); sh.seg(x + 48, y + 38, x + w - 9, y + 38, "guide")
        sh.text(x + 48, y + 48, "Van:", 6, "start"); sh.seg(x + 48, y + 58, x + w - 9, y + 58, "guide")
        sh.line(outline, "cut")
        hole(sh, x + 6, y + h / 2, 2.4)
        for k in range(3): sh.circle_r(x + 22 + k * 8, y + h - 12, 1.6, "y") if False else None
    sh.legend(["cut"], 276)
    write(OUT, "cadeaulabels-lente", sh, {"category": "natuur", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 15, "holiday": "pasen", "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Cadeaulabels met lenteplaatjes", "printNote": "Print op stevig papier (160 gram) als je het hebt.", "steps": [
            "Kleur de plaatjes en de randjes in: een tulp, een vlinder, een bij, een kuiken, een lieveheersbeestje en een regenboog.",
            "Schrijf op voor wie het cadeau is en van wie.",
            "Knip de labels uit langs de streepjeslijn.",
            "Prik het gaatje aan de punt door (vraag een volwassene om hulp) en bind het label met een touwtje aan je cadeau, bijvoorbeeld met Pasen of Moederdag."]}}})

# ---------- mobiel: wolk met vogeltjes (symmetrisch, dus in balans) ----------
@do
def mobiel():
    sh = Sheet()
    title(sh, "Mobiel: wolk met vogeltjes", 13, 12)
    cx = 100
    half = [Point(cx, 70).buffer(30, 64), Point(cx - 32, 78).buffer(24, 64), Point(cx - 62, 88).buffer(18, 64), box(cx - 78, 88, cx, 108)]
    left = unary_union(half)
    cloud = unary_union([left, affinity.scale(left, -1, 1, origin=(cx, 0))]).intersection(box(0, 0, 200, 108))
    mir = affinity.scale(cloud, -1, 1, origin=(cx, 0))
    assert cloud.symmetric_difference(mir).area < 1, "wolk is niet symmetrisch"
    sh.region(geom_d(cloud), "-")
    sh.dot(cx - 10, 76, 2.4); sh.dot(cx + 10, 76, 2.4); sh.line(f"M{cx - 9} {86}Q{cx} {94} {cx + 9} {86}", "l", "stroke-width:1.6")
    sh.circle_r(cx - 20, 86, 3.4, "k"); sh.circle_r(cx + 20, 86, 3.4, "k")
    sh.line(geom_d(cloud.buffer(3, join_style=1)), "cut")
    hole(sh, cx, 46, 2.6)                                         # ophangen: midden boven, recht boven het zwaartepunt
    assert abs(cloud.centroid.x - cx) < .2
    xs = [cx - 56, cx - 28, cx, cx + 28, cx + 56]
    for x in xs: hole(sh, x, 101, 2.2)
    # vijf vogels: paren zijn spiegelbeelden van elkaar (even zwaar)
    spots = [(44, 150, 1, "r"), (156, 150, -1, "r"), (62, 214, 1, "b"), (138, 214, -1, "b"), (100, 250, 1, "y")]
    sizes = [17, 17, 15, 15, 13]
    for (x, y, d, c), s in zip(spots, sizes):
        g = bird(sh, x, y, s * 1.3, c, "o" if c != "o" else "y", d)
        cut = g.buffer(3, join_style=1)
        sh.line(geom_d(cut), "cut")
        gx = g.centroid.x
        hy = g.bounds[1] + 3
        while not g.buffer(-.5).contains(Point(gx, hy).buffer(3.2)): hy += .5
        hole(sh, gx, hy, 2)
        assert cut.bounds[3] < 271 and cut.bounds[1] > 112, cut.bounds
    sh.legend(["cut"], 277)
    write(OUT, "mobiel-wolk-met-vogeltjes", sh, {"category": "dieren", "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 35, "adultHelp": True, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Mobiel: wolk met vijf vogeltjes", "printNote": "Print op stevig papier (160 gram): dan draaien de vogeltjes mooi en hangt de wolk recht.", "steps": [
            "Kleur de wolk en de vogeltjes in. Kleur de twee grote vogels hetzelfde, en de twee middelste ook: dan ziet de mobiel er netjes uit.",
            "Knip alles uit langs de streepjeslijnen.",
            "Laat een volwassene alle gaatjes doorprikken: één bovenin de wolk, vijf onderin de wolk en één in elk vogeltje.",
            "Knoop aan elk vogeltje een draadje. Hang de grote vogels aan de buitenste gaatjes, de middelste vogels aan de gaatjes ernaast en het kleine vogeltje in het midden.",
            "Maak de draadjes links en rechts even lang, dan blijft de wolk recht hangen. Knoop een draadje door het gaatje bovenin en hang de mobiel op, bijvoorbeeld boven een bed."]}}})

# ---------- slinger voor de slaapkamer: sterren en manen ----------
@do
def slaapslinger():
    sh = Sheet()
    title(sh, "Slinger: sterren en maan", 13, 12)
    sh.text(100, 22, "Rijg een touw door de gaatjes: van voren erin, van achteren eruit.", 5.5)
    def ster(cx, cy, code):
        g = Polygon(star_pts(cx, cy, 34, 15))
        sh.region(geom_d(g), code)
        sh.dot(cx - 7, cy + 2, 1.8); sh.dot(cx + 7, cy + 2, 1.8)
        sh.line(f"M{cx - 5} {cy + 9}Q{cx} {cy + 13} {cx + 5} {cy + 9}", "l", "stroke-width:1.3")
        return g
    def maan(cx, cy, code):
        g = Point(cx, cy).buffer(32, 64).difference(Point(cx, cy - 18).buffer(28, 64))
        sh.region(geom_d(g), code)
        # slapend gezichtje aan de onderkant
        sh.line(f"M{cx - 12} {cy + 18}Q{cx - 9} {cy + 21} {cx - 6} {cy + 18}M{cx + 6} {cy + 18}Q{cx + 9} {cy + 21} {cx + 12} {cy + 18}", "l", "stroke-width:1.3")
        sh.line(f"M{cx - 4} {cy + 25}Q{cx} {cy + 27} {cx + 4} {cy + 25}", "l", "stroke-width:1.1")
        return g
    def wolk(cx, cy, code):
        g = unary_union([Point(cx - 16, cy + 4).buffer(14, 48), Point(cx, cy - 6).buffer(19, 48), Point(cx + 18, cy + 3).buffer(15, 48), box(cx - 28, cy + 4, cx + 30, cy + 18)])
        sh.region(geom_d(g), code)
        sh.dot(cx - 6, cy + 4, 1.8); sh.dot(cx + 6, cy + 4, 1.8)
        sh.text(cx, cy + 14, "z z z", 6)
        return g
    items = [(ster, "y"), (maan, "y"), (ster, "o"), (wolk, "b"), (ster, "y"), (maan, "y")]
    for i, (fn, code) in enumerate(items):
        col, row = i % 2, i // 2
        cx, cy = 56 + col * 88, 72 + row * 78
        g = fn(cx, cy, code)
        sh.line(geom_d(g.buffer(3, join_style=1)), "cut")
        # twee gaatjes op dezelfde hoogte, zo hoog mogelijk
        hy = g.bounds[1] + 4
        dx = 7 if fn is not maan else 22
        while not all(g.buffer(-.5).contains(Point(cx + s * dx, hy).buffer(3)) for s in (-1, 1)): hy += .5
        for s in (-1, 1): hole(sh, cx + s * dx, hy, 2)
    sh.legend(["cut"], 276)
    write(OUT, "slaapkamerslinger-sterren-en-maan", sh, {"category": "ruimte", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 25, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Slinger voor de slaapkamer: sterren, manen en een slaapwolkje", "printNote": "Op stevig papier (160 gram) blijft de slinger mooi plat hangen. Print het vel twee keer voor een lange slinger.", "steps": [
            "Kleur de sterren, de manen en het wolkje in. Ze hebben allemaal hun ogen dicht: ze slapen al!",
            "Knip ze uit langs de streepjeslijn.",
            "Prik in elk stuk de twee gaatjes door (vraag een volwassene om hulp).",
            "Rijg een touw door de gaatjes: van voren erin bij het ene gaatje, van achteren eruit bij het andere. Wissel sterren, manen en het wolkje af.",
            "Hang de slinger boven je bed of voor je raam."]}}})

# =====================================================================
# 4. CADEAUTJES EN BOUWPLATEN
# =====================================================================

def box_net(sh, cx, cy, s, h, T, code_base, code_wall, deco_wall=None, deco_base=None):
    """Open doosje: bodem s x s, vier wanden van hoogte h, lijmflapjes (T breed) aan de boven- en onderwand.
    Geeft de buitenrand terug (shapely)."""
    x0, y0 = cx - s / 2, cy - s / 2
    base = box(x0, y0, x0 + s, y0 + s)
    walls = {"n": box(x0, y0 - h, x0 + s, y0), "s": box(x0, y0 + s, x0 + s, y0 + s + h),
             "w": box(x0 - h, y0, x0, y0 + s), "e": box(x0 + s, y0, x0 + s + h, y0 + s)}
    tabs = []
    for side, wy0, wy1 in [("n", y0 - h, y0), ("s", y0 + s, y0 + s + h)]:
        for sx, d in [(x0, -1), (x0 + s, 1)]:
            ins = 1.5
            tabs.append(Polygon([(sx, wy0 + ins), (sx + d * T, wy0 + ins + 2), (sx + d * T, wy1 - 2), (sx, wy1)] if side == "n" else
                                [(sx, wy0), (sx + d * T, wy0 + 2), (sx + d * T, wy1 - ins - 2), (sx, wy1 - ins)]))
    sh.region(geom_d(base), code_base)
    for k, w in walls.items(): sh.region(geom_d(w), code_wall)
    for t in tabs: glue_path(sh, geom_d(t))
    if deco_base: deco_base(x0, y0)
    if deco_wall: deco_wall(walls)
    out = unary_union([base] + list(walls.values()) + tabs)
    sh.line(geom_d(out.buffer(.01, join_style=2)), "cut")
    for x1, y1, x2, y2 in [(x0, y0, x0 + s, y0), (x0, y0 + s, x0 + s, y0 + s), (x0, y0, x0, y0 + s), (x0 + s, y0, x0 + s, y0 + s),
                           (x0, y0 - h, x0, y0), (x0 + s, y0 - h, x0 + s, y0), (x0, y0 + s, x0, y0 + s + h), (x0 + s, y0 + s, x0 + s, y0 + s + h)]:
        sh.seg(x1, y1, x2, y2, "fold")
    return out

@do
def tandendoosje():
    sh = Sheet()
    title(sh, "Doosje voor een tandje", 13, 12)
    s, h, S, H, T = 48, 26, 50.5, 14, 8
    assert S - s >= 2, "het deksel moet net over het doosje passen"
    assert H < h, "het deksel moet lager zijn dan het doosje"
    def tooth(cx, cy, k, face=True):
        sh.region(f"M{cx - 13*k} {cy - 9*k}Q{cx - 13*k} {cy - 16*k} {cx - 7*k} {cy - 16*k}Q{cx - 3*k} {cy - 16*k} {cx} {cy - 13*k}Q{cx + 3*k} {cy - 16*k} {cx + 7*k} {cy - 16*k}Q{cx + 13*k} {cy - 16*k} {cx + 13*k} {cy - 9*k}"
                  f"Q{cx + 13*k} {cy} {cx + 10*k} {cy + 5*k}Q{cx + 8*k} {cy + 16*k} {cx + 5*k} {cy + 16*k}Q{cx + 2*k} {cy + 16*k} {cx + 1.5*k} {cy + 8*k}Q{cx} {cy + 5*k} {cx - 1.5*k} {cy + 8*k}"
                  f"Q{cx - 2*k} {cy + 16*k} {cx - 5*k} {cy + 16*k}Q{cx - 8*k} {cy + 16*k} {cx - 10*k} {cy + 5*k}Q{cx - 13*k} {cy} {cx - 13*k} {cy - 9*k}Z", "-")
        if face:
            sh.dot(cx - 4.5 * k, cy - 6 * k, 1.2 * k); sh.dot(cx + 4.5 * k, cy - 6 * k, 1.2 * k)
            sh.line(f"M{cx - 4*k} {cy - 1*k}Q{cx} {cy + 2.5*k} {cx + 4*k} {cy - 1*k}", "l", "stroke-width:1.2")
    # het doosje
    bcx, bcy = 72, 92
    def wall_deco(walls):
        n = walls["s"].bounds
        mx = (n[0] + n[2]) / 2   # de onderwand klapt omhoog: tekst op zijn kop, dan staat hij straks rechtop
        sh.text(mx, n[1] + 9, "Mijn tandje", 7, rotate=180)
        sh.text(mx, n[1] + 20, "datum: ..........", 5.5, rotate=180)
        for k in ("n", "w", "e"):
            b = walls[k].bounds; mx, my = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            sh.poly_r(star_pts(mx, my, 5.5, 2.4), "y")
    box_net(sh, bcx, bcy, s, h, T, "b", "k", wall_deco)
    sh.tip(bcx, bcy + s / 2 + h + 10, "het doosje", "middle")
    # het deksel
    lcx, lcy = 72, 204
    def lid_top(x0, y0): tooth(lcx, lcy, 1.1)
    def lid_walls(walls):
        for k, w in walls.items():
            b = w.bounds; mx, my = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            for j in (-1, 0, 1):
                if k in ("n", "s"): sh.circle_r(mx + j * 12, my, 2, "y")
                else: sh.circle_r(mx, my + j * 12, 2, "y")
    box_net(sh, lcx, lcy, S, H, 6, "t", "b", lid_walls, lid_top)
    sh.tip(lcx, lcy + S / 2 + H + 10, "het deksel", "middle")
    # briefje voor in het doosje
    nx, ny, nw, nh = 134, 50, 58, 84
    sh.rect_line(nx, ny, nw, nh, "cut", 3)
    tooth(nx + nw / 2, ny + 22, .9)
    sh.text(nx + nw / 2, ny + 46, "Mijn tandje is los!", 5.4)
    for i, k in enumerate(["Naam:", "Datum:", "Welke tand:"]):
        sh.text(nx + 5, ny + 58 + i * 9, k, 4.8, "start"); sh.seg(nx + 8 + len(k) * 2.6, ny + 58 + i * 9, nx + nw - 5, ny + 58 + i * 9, "guide")
    sh.tip(nx + nw / 2, ny + nh + 9, "briefje voor in het doosje", "middle")
    for x, y in [(150, 186), (178, 206), (156, 236), (182, 250)]: sh.poly_r(star_pts(x, y, 6, 2.6), "y")
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "doosje-voor-een-tandje", sh, {"category": "thuis", "age": "6-9", "kind": "bouwplaat", "difficulty": 3, "minutes": 35, "adultHelp": True, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": "Bouwplaat: doosje voor een tandje, met tand op het deksel", "printNote": "Print op stevig papier (160 gram), dan blijft het doosje stevig. Print op ware grootte (100 %), anders past het deksel niet.", "steps": [
            "Kleur het doosje, het deksel met de tand en het briefje in. Vul het briefje in.",
            "Knip het doosje en het deksel uit langs de streepjeslijnen. Knip niet in de stippellijnen.",
            "Vouw alle stippellijnen naar binnen, met de tekening aan de buitenkant.",
            "Doosje: zet de wanden rechtop. Smeer lijm op de grijze flapjes en plak ze aan de binnenkant van de zijwanden. Houd even vast tot het droog is.",
            "Maak het deksel op dezelfde manier. Het deksel is net iets groter, zodat het over het doosje past.",
            "Leg je tandje en het opgevouwen briefje in het doosje en doe het deksel erop."]}}})

# ---------- 3D-bloemen in een potje voor Moederdag (in elkaar schuiven) ----------
@do
def schuifbloemen():
    sh = Sheet()
    title(sh, "Bloemen voor Moederdag", 13, 12)
    sh.text(100, 22, "Twee platte bloemen in elkaar geschoven: een bloem die zelf blijft staan!", 5.4)
    PH = 106
    def tulp_geom(cx, top):
        bot = top + PH
        pot = Polygon([(cx - 22, bot - 30), (cx + 22, bot - 30), (cx + 17, bot), (cx - 17, bot)])
        rim = box(cx - 25, bot - 36, cx + 25, bot - 28)
        stem = box(cx - 5, top + 34, cx + 5, bot - 34)
        leaves = [Polygon([(cx, bot - 40), (cx + s * 26, bot - 72), (cx + s * 22, bot - 56), (cx + s * 4, bot - 44)]) for s in (-1, 1)]
        cup = [(cx + 20 * math.cos(math.radians(a)), top + 20 + 18 * math.sin(math.radians(a))) for a in range(0, 181, 10)]
        head = Polygon([(cx - 20, top + 4), (cx - 10, top + 15), (cx, top), (cx + 10, top + 15), (cx + 20, top + 4)] + cup).buffer(0)
        return dict(pot=pot, rim=rim, stem=stem, leaves=leaves, head=head)
    def madelief_geom(cx, top):
        g = tulp_geom(cx, top)
        hc = (cx, top + 26)
        petals = [affinity.rotate(affinity.scale(Point(hc[0], hc[1] - 15).buffer(1, 32), 6, 11), k * 30, origin=hc) for k in range(12)]
        g["head"] = unary_union(petals + [Point(*hc).buffer(10, 32)])
        g["heart"] = Point(*hc).buffer(9, 32)
        return g
    pieces = [(tulp_geom, "top", "r"), (tulp_geom, "bot", "r"), (madelief_geom, "top", "-"), (madelief_geom, "bot", "-")]
    for i, (gf, slit, hcode) in enumerate(pieces):
        col, row = i % 2, i // 2
        cx, top = 56 + col * 88, 32 + row * 118
        g = gf(cx, top)
        for lf in g["leaves"]: sh.region(geom_d(lf), "g")
        sh.region(geom_d(g["stem"]), "g")
        sh.region(geom_d(g["head"]), hcode)
        if "heart" in g: sh.region(geom_d(g["heart"]), "y")
        sh.region(geom_d(g["pot"]), "o"); sh.region(geom_d(g["rim"]), "o")
        for k in (-9, 9): sh.region(heart_path(cx + k, top + PH - 14, 5), "m")
        sh.text(cx - 17, top + PH - 30, "A" if slit == "top" else "B", 6.5)
        whole = unary_union([g["pot"], g["rim"], g["stem"], g["head"]] + g["leaves"])
        sh.line(geom_d(whole.buffer(2, join_style=1)), "cut")
        mid = top + PH / 2
        if slit == "top": sh.seg(cx, top - 2, cx, mid, "cut", "stroke-width:1.4")
        else: sh.seg(cx, mid, cx, top + PH + 2, "cut", "stroke-width:1.4")
        assert g["stem"].bounds[1] < mid < g["stem"].bounds[3], "de sneetjes moeten in de steel samenkomen"
    sh.legend(["cut"], 276)
    write(OUT, "schuifbloemen-moederdag", sh, {"category": "natuur", "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 30, "holiday": "moederdag", "adultHelp": True, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": "Bloemen voor Moederdag: twee 3D-bloemen in een potje", "printNote": "Print op stevig papier (160 gram), anders blijven de bloemen niet staan.", "steps": [
            "Kleur de vier delen in. De twee tulpen horen bij elkaar, en de twee madeliefjes ook. Kleur ze aan beide kanten als je wilt.",
            "Knip de vier delen uit langs de streepjeslijn.",
            "Knip het dikke streepjeslijntje in het midden in: bij deel A (letter A op de pot) van boven tot halverwege, bij deel B van onder tot halverwege. Knip precies op de lijn.",
            "Schuif deel A van boven over deel B, sneetje in sneetje, tot de onderkanten gelijk staan. Draai ze zo dat ze een kruis vormen.",
            "Zet de bloem neer: hij blijft vanzelf staan. Geef hem op Moederdag, samen met een kaart of een knuffel."]}}})

# ---------- fotolijstje met standaard ----------
@do
def fotolijstje():
    sh = Sheet()
    title(sh, "Fotolijstje met standaard", 13, 12)
    x0, w, top, H = 16, 92, 24, 112
    yf = top + H
    # voorkant (onder de vouw) met venster, achterkant (boven de vouw, op zijn kop)
    win = (x0 + 16, yf + 16, w - 32, H - 40)
    frame = box(x0, yf, x0 + w, yf + H).difference(box(win[0], win[1], win[0] + win[2], win[1] + win[3]))
    sh.raw(f'<path class="r" fill-rule="evenodd" d="{geom_d(frame)}"/>', "y")
    sh.rect_line(x0, top, w, 2 * H, "cut", 2)
    sh.rect_line(win[0], win[1], win[2], win[3], "cut")
    sh.seg(x0, yf, x0 + w, yf, "fold")
    for k in range(6):
        sh.region(heart_path(x0 + 9, yf + 14 + k * 17, 4.5), "rm"[k % 2]); sh.region(heart_path(x0 + w - 9, yf + 14 + k * 17, 4.5), "mr"[k % 2])
    for k in range(4): flower(sh, win[0] + 6 + k * (win[2] - 12) / 3, yf + 8, 3, "pb"[k % 2], "y")
    sh.text(x0 + w / 2, yf + H - 12, "Voor jou!", 7.5)
    # achterkant (op zijn kop, zodat hij na het vouwen rechtop staat); de standaard komt bovenaan, vlak bij de vouw
    cxm = x0 + w / 2
    glue_rect(sh, cxm - 12, yf - 20, 24, 14)
    sh.text(cxm, yf - 24, "standaard", 5, rotate=180)
    sh.text(cxm, top + 56, "Gemaakt door:", 6.5, rotate=180); sh.seg(x0 + 16, top + 44, x0 + w - 16, top + 44, "guide")
    sh.text(cxm, top + 30, "Datum:", 6.5, rotate=180); sh.seg(x0 + 16, top + 18, x0 + w - 16, top + 18, "guide")
    # standaard: strook met lijmflap
    sx, sy, sw_, sl = 124, 30, 24, 96
    sh.rect_r(sx, sy + 14, sw_, sl - 14, "w", 1)
    glue_rect(sh, sx + .8, sy + .8, sw_ - 1.6, 12.4)
    sh.line(f"M{sx} {sy}H{sx + sw_}V{sy + sl}H{sx}Z", "cut")
    sh.seg(sx, sy + 14, sx + sw_, sy + 14, "fold")
    sh.tip(sx + sw_ + 4, sy + 50, "standaard", "start")
    # tekenvel dat precies achter het venster past
    dx, dy, dw, dh = 118, 150, win[2] + 12, win[3] + 12
    sh.rect_line(dx, dy, dw, dh, "cut", 1)
    sh.rect_line(dx + 6, dy + 6, win[2], win[3], "guide", 0, "stroke-dasharray:2 2")
    sh.text(dx + dw / 2, dy + dh / 2 - 2, "Teken hier", 6); sh.text(dx + dw / 2, dy + dh / 2 + 7, "of plak een foto", 5.4)
    sh.tip(dx + dw / 2, dy + dh + 9, "tekening", "middle")
    assert dx + dw < 196 and dy + dh < 266
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "fotolijstje-met-standaard", sh, {"category": "thuis", "age": "6-9", "kind": "bouwplaat", "difficulty": 2, "minutes": 35, "adultHelp": True, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": "Fotolijstje met standaard: een cadeautje om te maken", "printNote": "Print op stevig papier (160 gram), dan blijft het lijstje goed staan.", "steps": [
            "Kleur de rand van het lijstje in. Maak een tekening in het losse vel, of plak er een foto op.",
            "Knip alles uit langs de streepjeslijnen. Laat een volwassene het venster eruit knippen: prik een gaatje in het midden en knip naar de hoeken.",
            "Leg je tekening achter het venster, met de tekening naar voren. Plak de randjes vast met een beetje lijm.",
            "Vouw het lijstje dubbel op de stippellijn, zodat de achterkant achter je tekening komt. Plak de achterkant vast.",
            "Vouw het flapje van de standaard om, smeer lijm op het grijze flapje en plak het op het grijze vlak aan de achterkant. Klap de standaard uit en zet het lijstje neer.",
            "Een mooi cadeautje voor opa en oma, voor Moederdag of Vaderdag!"]}}})

# ---------- menukaart voor het kerstdiner (staande kaart) ----------
@do
def menukaart():
    sh = Sheet()
    title(sh, "Menukaart: kerstdiner", 13, 12)
    x0, w, top, h2 = 14, 172, 22, 112
    yf = top + h2
    sh.rect_line(x0, top, w, 2 * h2, "cut", 3)
    sh.seg(x0, yf, x0 + w, yf, "fold")
    def side(oy, menu):
        sh.region(f"M{x0 + 5} {oy + 5}H{x0 + w - 5}V{oy + h2 - 5}H{x0 + 5}Z", "g")
        sh.rect_r(x0 + 12, oy + 12, w - 24, h2 - 24, "-", 4)
        if menu:
            outline_text(sh, 100, oy + 32, "Menu", 18)
            for i, k in enumerate(["Voorgerecht", "Hoofdgerecht", "Toetje"]):
                yy = oy + 48 + i * 18
                sh.text(100, yy, k, 6.5); sh.seg(48, yy + 9, 152, yy + 9, "guide")
        else:
            outline_text(sh, 100, oy + 40, "Eet smakelijk!", 15)
            cx, cy = 100, oy + 70
            sh.poly_r([(cx, cy - 18), (cx + 18, cy + 12), (cx - 18, cy + 12)], "g"); sh.rect_r(cx - 3, cy + 12, 6, 6, "w")
            sh.poly_r(star_pts(cx, cy - 20, 5, 2.2), "y")
            for dx, dy, c in [(-6, 0, "r"), (5, 6, "b"), (-9, 9, "y"), (7, -6, "y")]: sh.circle_r(cx + dx, cy + dy, 1.8, c)
            sh.text(100, oy + 96, "Fijne kerstdagen!", 6.5)
        for (px, py) in [(x0 + 22, oy + 22), (x0 + w - 22, oy + 22), (x0 + 22, oy + h2 - 22), (x0 + w - 22, oy + h2 - 22)]:
            for s in (-1, 1):
                rot(sh, s * 55, px, py); sh.region(leaf_path(px, py - 7, 3, 6.5), "g"); end(sh)
            for d in (-1.9, 1.9): sh.circle_r(px + d, py + 1, 2, "r")
    side(yf, True)
    sh.raw(f'<g transform="rotate(180 100 {top + h2 / 2})">'); side(top, False); sh.raw("</g>")
    sh.legend(["cut", "fold"], 276)
    write(OUT, "menukaart-kerstdiner", sh, {"category": "eten", "age": "6-9", "kind": "kaart", "difficulty": 1, "minutes": 20, "holiday": "kerst", "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "potlood"}, SCHAAR, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Menukaart voor het kerstdiner (staande kaart)", "printNote": "Op stevig papier (160 gram) blijft de kaart goed rechtop staan.", "steps": [
            "Vraag wat er gegeten wordt en schrijf het voorgerecht, het hoofdgerecht en het toetje op.",
            "Kleur de randen, de hulst en de kerstboom in.",
            "Knip de kaart uit langs de streepjeslijn en vouw hem dubbel op de stippellijn, met de tekening aan de buitenkant.",
            "Zet de kaart als een dakje midden op tafel: aan de ene kant staat het menu, aan de andere kant 'Eet smakelijk!'."]}}})

# ---------- bedankkaart voor de dokter: dokterstas met een klep die opengaat ----------
@do
def dokterstas():
    sh = Sheet()
    title(sh, "Bedankkaart voor de dokter", 13, 10)
    yf = rect_card(sh, 16, 88, invite_back("Dank je wel!", ["Voor dokter:", "Van:"]))
    bot = yf + 88
    outline_text(sh, 100, yf + 15, "Dank je wel, dokter!", 12)
    # tas
    bx0, bx1, by0, by1 = 50, 150, yf + 34, bot - 8
    sh.region(f"M{bx0 + 8} {yf + 34}V{yf + 24}Q{bx0 + 8} {yf + 20} {bx0 + 12} {yf + 20}H{bx0 + 30}Q{bx0 + 34} {yf + 20} {bx0 + 34} {yf + 24}V{yf + 34}", "-") if False else None
    sh.region(f"M86 {by0}V{by0 - 8}Q86 {by0 - 12} 90 {by0 - 12}H110Q114 {by0 - 12} 114 {by0 - 8}V{by0}H109V{by0 - 7}H91V{by0}Z", "x")
    sh.rect_r(bx0, by0, bx1 - bx0, by1 - by0, "w", 5)
    # wat er in de tas zit (onder de klep)
    ix0, iy0 = bx0 + 6, by0 + 6
    sh.rect_r(ix0, iy0, bx1 - bx0 - 12, by1 - by0 - 12, "-", 3)
    sh.line(f"M{ix0 + 10} {iy0 + 6}Q{ix0 + 6} {iy0 + 26} {ix0 + 18} {iy0 + 30}Q{ix0 + 30} {iy0 + 26} {ix0 + 26} {iy0 + 6}", "l", "stroke-width:1.6")
    sh.line(f"M{ix0 + 18} {iy0 + 30}V{iy0 + 36}", "l", "stroke-width:1.6"); sh.circle_r(ix0 + 18, iy0 + 39, 3.4, "z")
    rot(sh, -25, ix0 + 50, iy0 + 22)
    sh.rect_r(ix0 + 40, iy0 + 18, 22, 8, "k", 3.5); sh.rect_r(ix0 + 47, iy0 + 18, 8, 8, "y", 1)
    end(sh)
    rot(sh, 20, ix0 + 72, iy0 + 22)
    sh.rect_r(ix0 + 69, iy0 + 6, 5, 28, "-", 2.5); sh.circle_r(ix0 + 71.5, iy0 + 34, 3, "r")
    end(sh)
    sh.region(heart_path(ix0 + 52, iy0 + 38, 6), "r")
    # plek voor de klep (scharnier bovenaan)
    fx, fy, fw, fh = bx0 - 1, by0 - 1, bx1 - bx0 + 2, by1 - by0 + 2
    flap_spot(sh, fx, fy, fw, fh, "t")
    for x, y in [(28, yf + 40), (172, yf + 40), (30, bot - 20), (170, bot - 20)]:
        sh.poly_r([(x - 2.5, y - 7), (x + 2.5, y - 7), (x + 2.5, y - 2.5), (x + 7, y - 2.5), (x + 7, y + 2.5), (x + 2.5, y + 2.5), (x + 2.5, y + 7), (x - 2.5, y + 7), (x - 2.5, y + 2.5), (x - 7, y + 2.5), (x - 7, y - 2.5), (x - 2.5, y - 2.5)], "r")
    def klep(sh, x, y, w, h):
        sh.rect_r(x + w / 2 - 12, y + h / 2 - 12, 24, 24, "-", 3)
        sh.rect_r(x + w / 2 - 4, y + h / 2 - 9, 8, 18, "r"); sh.rect_r(x + w / 2 - 9, y + h / 2 - 4, 18, 8, "r")
        sh.rect_r(x + w / 2 - 6, y + h - 7, 12, 5, "y", 1)
    sh.tip(16, bot + 9, "De klep van de tas:")
    flap_piece(sh, 100 - fw / 2, bot + 14, fw, fh, "t", "w", klep)
    assert bot + 14 + fh < 268
    sh.legend(["cut", "fold", "glue"], 279)
    write(OUT, "bedankkaart-dokter-dokterstas", sh, {"category": "beroepen", "age": "4-6", "kind": "kaart", "difficulty": 2, "minutes": 25, "paperGsm": 160,
        "materials": KAART_MAT + [{"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Bedankkaart voor de dokter: dokterstas met een klep die opengaat", "printNote": STEVIG, "steps": [
            "Kleur de voorkant van de kaart (de onderste helft) en de losse klep in.",
            "Knip de kaart en de klep uit langs de streepjeslijnen.",
            "Vouw het smalle randje bovenaan de klep om langs de stippellijn.",
            "Smeer lijm op het grijze strookje bovenaan de tas en plak het randje van de klep erop. Til de klep op: wat zit er in de tas?",
            "Vouw de kaart dubbel op de lange stippellijn, met de tekening aan de buitenkant. Schrijf op de achterkant voor welke dokter de kaart is en van wie."]}}})
