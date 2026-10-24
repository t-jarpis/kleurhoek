"""Batch 43a: kleurplaten (eigen tekeningen, 200x200) met dieren uit de hele wereld in hun leefomgeving:
savanne, jungle, poolgebied, woestijn, bos, bergen en rivier. Elk dier in een kleine scène."""
import math
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from shapes import star_path, moon_path, cloud_path, leaf_path


# ---------- hulpjes ----------
def P(x, y): return f"{f(float(x))} {f(float(y))}"

def smooth(pts, closed=True, t=1.0):
    """Vloeiende lijn (Catmull-Rom als bezier) door de punten."""
    n = len(pts)
    d = "M" + P(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[0]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * t, p1[1] + (p2[1] - p0[1]) / 6 * t)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * t, p2[1] - (p3[1] - p1[1]) / 6 * t)
        d += "C" + P(*c1) + " " + P(*c2) + " " + P(*p2)
    return d + ("Z" if closed else "")

def sm(sh, pts, code="-"): sh.region(smooth(pts), code)
def sl(sh, pts): sh.line(smooth(pts, False))
def poly(sh, pts, code="-"): sh.poly_r(pts, code)

def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        u = i / n; a = (1 - u) ** 3; b = 3 * (1 - u) ** 2 * u; c = 3 * (1 - u) * u * u; e = u ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return out

def tube(sh, ctrl, w0, w1, code="-", n=24):
    """Gebogen buis (staart, nek, slang) langs een kubische bezier, van dikte w0 naar w1, ronde uiteinden."""
    pts = bez(*ctrl, n=n)
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n)]
        dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1
        w = (w0 + (w1 - w0) * i / n) / 2
        L.append((x - dy / d * w, y + dx / d * w)); R.append((x + dy / d * w, y - dx / d * w))
    r1, r0 = max(w1 / 2, .3), max(w0 / 2, .3)
    d = "M" + " L".join(P(*p) for p in L) + f"A{f(r1)} {f(r1)} 0 0 0 {P(*R[-1])}" + "L" + " L".join(P(*p) for p in R[::-1]) + f"A{f(r0)} {f(r0)} 0 0 0 {P(*L[0])}Z"
    sh.region(d, code)

def limb(sh, x1, y1, x2, y2, code, w=9):
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * w / 2, dx / d * w / 2; r = w / 2
    sh.region(f"M{P(x1 + nx, y1 + ny)}L{P(x2 + nx, y2 + ny)}A{f(r)} {f(r)} 0 0 0 {P(x2 - nx, y2 - ny)}L{P(x1 - nx, y1 - ny)}A{f(r)} {f(r)} 0 0 0 {P(x1 + nx, y1 + ny)}Z", code)

def leg(sh, pts, code, w):
    """Poot met knik: aaneengesloten balken."""
    for a, b in zip(pts, pts[1:]): limb(sh, a[0], a[1], b[0], b[1], code, w)

def blob(cx, cy, rx, ry, n=9, bulge=.62, start=0):
    p = [(cx + rx * math.cos(2 * math.pi * i / n + start), cy + ry * math.sin(2 * math.pi * i / n + start)) for i in range(n)]
    d = "M" + P(*p[0])
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        r = math.hypot(b[0] - a[0], b[1] - a[1]) * bulge
        d += f"A{f(r)} {f(r)} 0 0 1 {P(*b)}"
    return d + "Z"

def sun(sh, x, y, r=12, rays=True):
    sh.circle_r(x, y, r, "y")
    if rays:
        for k in range(8):
            a = math.radians(k * 45 + 22)
            sh.seg(x + (r + 3) * math.cos(a), y + (r + 3) * math.sin(a), x + (r + 8) * math.cos(a), y + (r + 8) * math.sin(a))

def tuft(sh, x, y, h=10):
    sh.line(f"M{P(x - 5, y)}Q{P(x - 4, y - h * .6)} {P(x - 8, y - h)}M{P(x, y)}Q{P(x + 1, y - h * .7)} {P(x, y - h * 1.2)}M{P(x + 5, y)}Q{P(x + 5, y - h * .6)} {P(x + 9, y - h)}")

def bird_m(sh, x, y, s=6):
    sh.line(f"M{P(x - s, y)}Q{P(x - s / 2, y - s * .7)} {P(x, y)}Q{P(x + s / 2, y - s * .7)} {P(x + s, y)}")

def acacia(sh, x, base, top, w=60, code="g", trunk="w"):
    tube(sh, [(x, base), (x - 2, base - (base - top) * .4), (x + 4, top + 16), (x + 2, top + 6)], 9, 5, trunk)
    sh.line(f"M{P(x + 1, top + 24)}Q{P(x - 10, top + 16)} {P(x - 18, top + 8)}M{P(x + 2, top + 20)}Q{P(x + 12, top + 14)} {P(x + 20, top + 8)}")
    sh.region(blob(x, top, w / 2, 9, 11, .7), code)

def pine(sh, x, base, h, code="g", trunk="w"):
    sh.rect_r(x - 3, base - h * .18, 6, h * .18, trunk)
    w = h * .36
    sh.poly_r([(x, base - h), (x + w * .55, base - h * .62), (x + w * .3, base - h * .62), (x + w, base - h * .18), (x - w, base - h * .18), (x - w * .3, base - h * .62), (x - w * .55, base - h * .62)], code)

def cactus(sh, x, base, h, code="g"):
    sh.region(f"M{P(x - 7, base)}V{f(base - h + 7)}A7 7 0 0 1 {P(x + 7, base - h + 7)}V{f(base)}Z", code)
    sh.region(f"M{P(x - 7, base - h * .45)}H{f(x - 16)}A4.5 4.5 0 0 1 {P(x - 20, base - h * .45 - 4)}V{f(base - h * .72)}A4 4 0 0 1 {P(x - 12, base - h * .72)}V{f(base - h * .55)}H{f(x - 7)}Z", code)
    sh.region(f"M{P(x + 7, base - h * .6)}H{f(x + 16)}A4.5 4.5 0 0 0 {P(x + 20, base - h * .6 - 4)}V{f(base - h * .85)}A4 4 0 0 0 {P(x + 12, base - h * .85)}V{f(base - h * .7)}H{f(x + 7)}Z", code)

def snow(sh, x, y, r=4):
    for k in range(3):
        a = math.radians(k * 60)
        sh.seg(x - r * math.cos(a), y - r * math.sin(a), x + r * math.cos(a), y + r * math.sin(a))

def waves(sh, y, xs, w=14):
    for x in xs: sh.line(f"M{P(x, y)}q{f(w / 4)} -3 {f(w / 2)} 0t{f(w / 2)} 0")

def reed(sh, x, base, h, code="w"):
    sh.line(f"M{P(x, base)}Q{P(x + 2, base - h * .5)} {P(x + 1, base - h)}")
    sh.region(f"M{P(x - 2.5, base - h + 4)}C{P(x - 3, base - h - 6)} {P(x + 5, base - h - 6)} {P(x + 4.5, base - h + 4)}C{P(x + 5, base - h + 14)} {P(x - 2, base - h + 14)} {P(x - 2.5, base - h + 4)}Z", code)

def rot(sh, a, cx, cy): sh.raw(f'<g transform="rotate({f(float(a))} {f(float(cx))} {f(float(cy))})">')
def end(sh): sh.raw("</g>")
def flip(sh): sh.raw('<g transform="translate(200 0) scale(-1 1)">')


# =================== SAVANNE ===================
def jachtluipaard(sh):
    sh.region("M0 150Q60 132 120 142T200 136V200H0Z", "l")
    sun(sh, 166, 32, 13)
    acacia(sh, 22, 146, 34, 54)
    sh.region("M0 200V178Q100 170 200 178V200Z", "y")
    leg(sh, [(138, 112), (144, 148), (138, 178)], "y", 8)
    limb(sh, 90, 116, 94, 178, "y", 8)
    TL = [(158, 100), (178, 110), (176, 156), (192, 150)]
    tube(sh, TL, 7, 6, "y")
    pts = bez(*TL)
    for i in (17, 20, 23):
        x, y = pts[i]; sh.seg(x - 4, y + 1, x + 3, y - 4)
    leg(sh, [(150, 108), (160, 146), (154, 178)], "y", 9)
    limb(sh, 72, 116, 66, 178, "y", 9)
    sm(sh, [(68, 124), (58, 112), (50, 98), (58, 84), (74, 88), (94, 86), (114, 92), (136, 87), (154, 93), (161, 106), (154, 120), (138, 123), (118, 118), (96, 124), (80, 126)], "y")
    sh.circle_r(58, 74, 4.5, "y")
    sm(sh, [(38, 80), (50, 74), (60, 78), (64, 88), (60, 98), (48, 102), (38, 100), (32, 94), (32, 88)], "y")
    sh.region("M32 88L37 88L35 92Z", "x")
    eye(sh, 44, 85, 2.2); sh.line("M42 86Q39 92 41 99M35 92V96M33 98Q37 100 42 99")
    for x, y in ((72, 96), (84, 104), (98, 96), (112, 104), (126, 96), (140, 104), (148, 96), (90, 116), (106, 114), (124, 110), (78, 112), (64, 104), (144, 116), (56, 90), (68, 136), (92, 146), (157, 132), (142, 128)):
        sh.dot(x, y, 2)

def hyena(sh):
    sun(sh, 176, 28, 12)
    sh.region("M0 140Q100 128 200 140V200H0Z", "y")
    sh.region("M6 140C8 112 14 82 22 76C28 84 32 114 36 140Z", "w")
    sh.line("M16 104Q22 100 28 106M14 122Q22 118 32 124")
    tube(sh, [(56, 104), (48, 112), (46, 126), (48, 138)], 6, 11, "x")
    leg(sh, [(62, 118), (60, 150), (56, 176)], "y", 9)
    leg(sh, [(76, 122), (80, 150), (78, 176)], "y", 9)
    limb(sh, 106, 120, 104, 178, "y", 10)
    limb(sh, 120, 114, 124, 178, "y", 10)
    sm(sh, [(52, 114), (58, 102), (80, 96), (100, 86), (116, 78), (130, 76), (140, 94), (130, 116), (108, 128), (82, 128), (60, 126)], "y")
    sh.line("M62 100L65 94L69 98L72 92L76 96L80 89L84 93L88 86L92 90L96 83L100 86L104 79L108 83L112 76L116 80L120 74L124 78")
    sh.circle_r(132, 64, 8, "y"); sh.circle_r(132, 64, 4, "w")
    sm(sh, [(132, 72), (144, 66), (158, 72), (172, 80), (172, 90), (160, 96), (142, 96), (132, 86)], "y")
    sh.circle_r(140, 66, 8, "y"); sh.circle_r(140, 66, 4, "w")
    sh.region("M164 78C170 76 175 80 173 86L166 86Z", "x")
    eye(sh, 152, 78, 2.4); sh.line("M150 90Q162 94 172 90")
    for x, y in ((72, 106), (86, 112), (100, 100), (112, 108), (96, 118), (122, 98), (66, 114), (74, 140), (106, 140), (122, 150), (60, 150)): sh.dot(x, y, 2.2)
    sh.region("M0 200V180Q100 172 200 180V200Z", "y")
    tuft(sh, 20, 182); tuft(sh, 184, 182)

def gnoe(sh):
    sh.region("M0 140Q50 120 100 132T200 124V200H0Z", "l")
    for x, y in ((60, 30), (76, 22), (150, 40)): bird_m(sh, x, y, 6)
    sun(sh, 172, 28, 12)
    acacia(sh, 178, 140, 70, 44)
    sh.region("M0 200V176Q100 168 200 176V200Z", "y")
    tube(sh, [(150, 96), (160, 108), (162, 126), (160, 140)], 5, 5, "z")
    sh.region(blob(160, 146, 5, 8, 7, .7), "x")
    limb(sh, 142, 112, 146, 176, "z", 8); limb(sh, 132, 114, 130, 176, "z", 8)
    limb(sh, 86, 118, 90, 176, "z", 8); limb(sh, 72, 118, 68, 176, "z", 8)
    for x in (146, 130, 90, 68): sh.rect_r(x - 4.5, 172, 9, 6, "x", 2)
    sm(sh, [(66, 126), (58, 106), (60, 84), (72, 70), (90, 68), (112, 78), (136, 86), (152, 96), (154, 114), (140, 122), (110, 120), (86, 126)], "z")
    sh.region("M60 84C64 72 72 66 86 66C80 74 78 78 74 84C70 88 64 90 60 84Z", "x")
    for k in range(5): sh.seg(86 + k * 10, 74 + k * 3.5, 82 + k * 10, 80 + k * 3.5)
    sh.region("M58 102L54 112L60 110L58 120L64 116L64 126L70 120L70 128L74 118Z", "x")
    tube(sh, [(46, 66), (30, 66), (24, 54), (32, 42)], 7, 3, "-")
    tube(sh, [(54, 64), (66, 60), (70, 50), (64, 40)], 7, 3, "-")
    sm(sh, [(42, 64), (56, 60), (64, 70), (58, 92), (52, 108), (40, 112), (30, 106), (32, 90), (36, 74)], "z")
    sh.ellipse_r(36, 106, 8, 7, "x")
    sh.region("M38 66C46 60 56 62 58 68C52 70 44 70 38 66Z", "x")
    sh.region("M60 74L74 70L64 80Z", "z")
    eye(sh, 44, 80, 2.3); eye(sh, 56, 80, 2)
    sh.line("M32 106Q36 102 40 104")

def wrattenzwijn(sh):
    sh.rect_r(0, 0, 200, 150, "-")
    sun(sh, 40, 34, 14)
    sh.region(blob(184, 140, 24, 16, 9, .7), "g")
    sh.region("M0 150Q100 140 200 150V200H0Z", "y")
    sh.ellipse_r(110, 182, 80, 12, "w")
    tube(sh, [(160, 104), (168, 90), (170, 76), (174, 64)], 3, 3, "w")
    sh.region(blob(175, 60, 5, 7, 7, .7), "x")
    for x in (76, 94, 130, 148): limb(sh, x, 130, x + (2 if x > 100 else -2), 172, "w", 12)
    sm(sh, [(64, 104), (92, 86), (130, 86), (158, 98), (162, 124), (146, 140), (100, 142), (70, 136)], "w")
    sh.region("M74 92L78 82L84 88L90 78L96 84L102 76L108 82L114 75L120 82L126 77L130 85L136 80L138 88C120 86 94 86 74 94Z", "x")
    sm(sh, [(80, 96), (62, 88), (44, 94), (30, 112), (20, 130), (20, 146), (34, 152), (54, 146), (72, 136), (82, 118)], "w")
    sh.region("M66 92L74 74L80 96Z", "w"); sh.region("M70 90L74 80L76 92Z", "k")
    sh.ellipse_r(21, 145, 6, 8, "k"); sh.dot(19, 142, 1.3); sh.dot(19, 149, 1.3)
    tube(sh, [(34, 146), (22, 140), (16, 128), (22, 114)], 6, 2.5, "-")
    tube(sh, [(42, 146), (34, 140), (32, 130), (38, 122)], 5, 2, "-")
    sh.region(blob(44, 126, 5, 4, 6, .7), "w"); sh.region(blob(58, 104, 4, 3, 6, .7), "w")
    eye(sh, 50, 104, 2.6); sh.line("M44 100Q50 97 56 100")

def gazelle(sh):
    sh.region("M0 130Q50 112 100 122T200 116V200H0Z", "l")
    sun(sh, 40, 32, 12)
    acacia(sh, 36, 130, 64, 50)
    sh.region("M0 200V176Q100 168 200 176V200Z", "y")
    tuft(sh, 176, 178); tuft(sh, 16, 180)
    for pts in (((70, 114), (66, 146), (68, 176)), ((84, 116), (88, 146), (88, 176)), ((124, 114), (124, 146), (122, 176)), ((134, 112), (138, 146), (140, 176))):
        leg(sh, pts, "o", 5.5); x2, y2 = pts[-1]; sh.poly_r([(x2 - 3.5, y2), (x2 + 3.5, y2), (x2 + 2.5, y2 + 4), (x2 - 2.5, y2 + 4)], "x")
    sh.region("M64 104L54 110L62 113Z", "x")
    tube(sh, [(128, 106), (136, 92), (142, 80), (148, 70)], 20, 11, "o")
    sm(sh, [(62, 112), (68, 100), (90, 96), (112, 96), (128, 92), (140, 98), (142, 112), (134, 122), (110, 124), (84, 124), (68, 122)], "o")
    sh.region("M66 115C80 111 110 112 140 110L141 114C110 117 82 118 67 119Z", "x")
    sh.region("M67 119C82 118 110 117 141 114C140 118 136 122 132 123C110 125 84 125 70 122Z", "-")
    tube(sh, [(150, 62), (148, 48), (144, 40), (150, 28)], 5, 2.5, "x")
    tube(sh, [(156, 62), (156, 48), (154, 40), (160, 30)], 5, 2.5, "x")
    for y in (54, 48, 42): sh.seg(144, y + 2, 151, y); sh.seg(152, y + 1, 159, y - 1)
    sm(sh, [(142, 70), (150, 60), (160, 62), (170, 74), (172, 82), (164, 84), (148, 80)], "o")
    sh.region(leaf_path(144, 60, 4, 9), "o")
    sh.line("M156 70Q162 76 170 80"); eye(sh, 156, 69, 2.2); sh.dot(170, 79, 1.4)

def buffel(sh):
    sh.rect_r(0, 0, 200, 140, "-")
    sh.region("M0 140Q60 120 110 132T200 124V200H0Z", "l")
    sun(sh, 40, 32, 13)
    sh.region("M0 200V172Q100 164 200 172V200Z", "y")
    sh.ellipse_r(64, 188, 56, 8, "b")
    tube(sh, [(164, 100), (172, 112), (174, 128), (172, 140)], 5, 5, "x"); sh.region(blob(172, 146, 5, 8, 7, .7), "x")
    for x in (82, 98, 140, 156): limb(sh, x, 124, x + (3 if x > 120 else -2), 174, "x", 13)
    sm(sh, [(70, 116), (78, 90), (100, 74), (130, 78), (160, 90), (170, 112), (156, 132), (110, 136), (82, 134)], "x")
    sm(sh, [(44, 96), (68, 96), (76, 112), (72, 132), (66, 144), (46, 144), (40, 132), (36, 112)], "x")
    sh.ellipse_r(56, 140, 13, 8, "z"); sh.dot(51, 140, 1.6); sh.dot(61, 140, 1.6)
    sh.region("M42 88C24 84 12 92 10 106C10 116 16 120 20 112C22 100 30 96 44 100Z", "z")
    sh.region("M70 88C88 84 100 92 102 106C102 116 96 120 92 112C90 100 82 96 68 100Z", "z")
    sh.region("M40 92C42 80 70 80 72 92C66 100 46 100 40 92Z", "z")
    sh.region("M38 104C28 102 20 108 22 114C28 116 36 112 40 110Z", "x"); sh.region("M74 104C84 102 92 108 90 114C84 116 76 112 72 110Z", "x")
    eye(sh, 46, 114, 2.3); eye(sh, 66, 114, 2.3)
    sh.region("M118 72C120 64 132 62 136 68C140 74 134 80 124 80L114 78Z", "w")
    sh.region("M136 68L146 70L136 73Z", "r"); eye(sh, 130, 68, 1.6)
    sh.region("M118 72C110 70 104 72 100 76L114 78Z", "w")
    sh.line("M122 80L120 84M128 80L128 84")

def secretarisvogel(sh):
    sh.region("M0 150Q60 136 120 144T200 138V200H0Z", "l")
    sun(sh, 40, 30, 12)
    acacia(sh, 172, 150, 60, 46)
    sh.region("M0 200V180Q100 172 200 180V200Z", "y")
    for x in (14, 40, 160, 188): tuft(sh, x, 182, 14)
    tube(sh, [(122, 112), (150, 120), (170, 128), (188, 136)], 7, 4, "x")
    tube(sh, [(122, 108), (150, 114), (168, 118), (186, 122)], 7, 4, "z")
    leg(sh, [(96, 130), (94, 154), (90, 182)], "y", 4); leg(sh, [(110, 130), (114, 156), (112, 182)], "y", 4)
    sh.line("M90 182H80M90 182L84 186M112 182H122M112 182L118 186")
    tube(sh, [(94, 118), (94, 128), (95, 134), (96, 140)], 12, 8, "x")
    tube(sh, [(110, 118), (110, 128), (110, 134), (110, 140)], 12, 8, "x")
    sm(sh, [(78, 96), (88, 82), (110, 82), (128, 96), (130, 112), (116, 124), (94, 126), (80, 114)], "z")
    sh.region("M96 88C110 86 126 96 128 108C116 106 104 100 96 88Z", "x")
    tube(sh, [(84, 92), (80, 80), (74, 70), (70, 62)], 14, 11, "z")
    for k, (dx, dy) in enumerate(((22, -6), (24, 2), (22, 10), (18, 16))):
        sh.region(f"M{P(74, 54 + k * 2)}Q{P(74 + dx * .6, 50 + dy * .6 + k * 2)} {P(74 + dx, 50 + dy)}Q{P(74 + dx * .6, 52 + dy * .6 + k * 2)} {P(76, 58 + k * 2)}Z", "x")
    sm(sh, [(58, 52), (66, 44), (78, 46), (82, 56), (78, 66), (66, 66)], "z")
    sh.region("M60 54C62 48 70 48 72 54C70 60 62 60 60 54Z", "o")
    eye(sh, 66, 54, 2)
    sh.region("M60 54L48 56Q44 58 46 62L50 60L60 59Z", "z")

def gier(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sun(sh, 48, 40, 16)
    sh.region("M0 150L40 120L70 136L110 104L150 130L180 116L200 126V200H0Z", "l")
    for x, y in ((150, 36), (170, 54)): bird_m(sh, x, y, 7)
    sh.region("M0 200V176Q100 168 200 176V200Z", "y")
    tube(sh, [(160, 200), (154, 170), (150, 150), (126, 140)], 14, 9, "w")
    tube(sh, [(156, 160), (176, 150), (186, 132), (190, 118)], 7, 4, "w")
    tube(sh, [(20, 150), (60, 148), (110, 144), (150, 152)], 10, 13, "w")
    sh.region("M94 148L104 120L110 146Z", "x") if False else None
    sm(sh, [(80, 144), (74, 120), (82, 96), (100, 86), (122, 92), (136, 112), (140, 132), (124, 146), (104, 150)], "w")
    sh.region("M112 96C132 100 146 124 150 152C136 146 122 136 112 120Z", "x")
    sh.region("M86 150L80 160L90 158L92 164L98 156L104 162L106 150Z", "x") if False else None
    for x in (92, 112): sh.line(f"M{x} 144V152M{x - 4} 152H{x + 4}")
    sh.region(blob(92, 90, 18, 10, 10, .7), "-")
    tube(sh, [(90, 88), (86, 76), (78, 70), (72, 70)], 7, 6, "k")
    sm(sh, [(64, 64), (72, 60), (82, 64), (82, 74), (74, 78), (64, 76)], "k")
    sh.region("M64 66L52 68Q48 72 52 76L56 72L64 74Z", "z")
    eye(sh, 72, 67, 2.2)

PLATES = [
    ("jachtluipaard-op-de-savanne", "Jachtluipaard op de savanne", "dieren", "6-9", 2, jachtluipaard),
    ("hyena-bij-de-termietenheuvel", "Hyena bij de termietenheuvel", "dieren", "6-9", 2, hyena),
    ("gnoe-op-de-vlakte", "Gnoe op de vlakte", "dieren", "6-9", 2, gnoe),
    ("wrattenzwijn-bij-de-modderpoel", "Wrattenzwijn bij de modderpoel", "dieren", "4-6", 1, wrattenzwijn),
    ("gazelle-onder-de-acacia", "Gazelle onder de acacia", "dieren", "4-6", 1, gazelle),
    ("buffel-met-vogeltje", "Buffel met een vogeltje op zijn rug", "dieren", "4-6", 1, buffel),
    ("secretarisvogel", "Secretarisvogel in het hoge gras", "dieren", "6-9", 2, secretarisvogel),
    ("gier-op-een-tak", "Gier op een dode tak", "dieren", "4-6", 1, gier),
]

if __name__ == "__main__":
    import sys
    only = set(sys.argv[1:])
    for slug, name, cat, age, diff, draw in PLATES:
        if only and slug not in only: continue
        kp(slug, name, cat, age, diff, draw)
