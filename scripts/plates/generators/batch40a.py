"""Batch 40a: kleurplaten voor peuters (2-4, eigen tekeningen, 200x200).
Eén groot onderwerp per plaat, dikke eenvoudige vormen en weinig, grote kleurvlakken:
speelgoed, kleding, eten, dagelijkse dingen, eenvoudige dieren en voertuigen."""
import math
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from shapes import heart_path, star_path, moon_path, cloud_path, leaf_path, fish_path, drop_path


# ---------- hulpjes ----------
def limb(sh, x1, y1, x2, y2, code, w=9):
    """Balk met afgeronde uiteinden van (x1,y1) naar (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * w / 2, dx / d * w / 2
    r = w / 2
    sh.region(f"M{f(x1 + nx)} {f(y1 + ny)}L{f(x2 + nx)} {f(y2 + ny)}A{f(r)} {f(r)} 0 0 0 {f(x2 - nx)} {f(y2 - ny)}L{f(x1 - nx)} {f(y1 - ny)}A{f(r)} {f(r)} 0 0 0 {f(x1 + nx)} {f(y1 + ny)}Z", code)

def blob(cx, cy, rx, ry, n=9, bulge=.62):
    """Bobbelige rand (pompon, wol) rond een ellips."""
    p = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
    d = f"M{f(p[0][0])} {f(p[0][1])}"
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        r = math.hypot(b[0] - a[0], b[1] - a[1]) * bulge
        d += f"A{f(r)} {f(r)} 0 0 1 {f(b[0])} {f(b[1])}"
    return d + "Z"

def sun(sh, x, y, r=12, rays=True):
    sh.circle_r(x, y, r, "y")
    if rays:
        for k in range(8):
            a = math.radians(k * 45 + 22)
            sh.seg(x + (r + 3) * math.cos(a), y + (r + 3) * math.sin(a), x + (r + 8) * math.cos(a), y + (r + 8) * math.sin(a))

def rot_ellipse(sh, cx, cy, rx, ry, a, code):
    sh.raw(f'<g transform="rotate({f(float(a))} {f(float(cx))} {f(float(cy))})">'); sh.ellipse_r(cx, cy, rx, ry, code); sh.raw("</g>")

def rot_leaf(sh, cx, cy, w, h, a, code="g", vein=True):
    sh.raw(f'<g transform="rotate({f(float(a))} {f(float(cx))} {f(float(cy))})">'); sh.region(leaf_path(cx, cy, w, h), code)
    if vein: sh.line(f"M{f(cx)} {f(cy - h * .7)}V{f(cy + h * .8)}")
    sh.raw("</g>")

def floor(sh, y=180, code="w"):
    sh.rect_r(0, y, 200, 200 - y, code)


# ---------- speelgoed ----------
def strandbal(sh):
    sh.region("M0 200V168Q100 156 200 168V200Z", "y")
    sun(sh, 172, 28, 12)
    sh.ellipse_r(104, 166, 52, 7, "z")
    C, R, P = (100, 98), 64, (84, 80)
    def rim(a): return C[0] + R * math.cos(math.radians(a)), C[1] + R * math.sin(math.radians(a))
    def ctrl(a):
        q = rim(a); mx, my = (P[0] + q[0]) / 2, (P[1] + q[1]) / 2
        dx, dy = q[0] - P[0], q[1] - P[1]; d = math.hypot(dx, dy)
        return mx - dy / d * 12, my + dx / d * 12
    codes = ["r", "-", "b", "-", "y", "-"]
    for k in range(6):
        a1, a2 = -100 + k * 60, -40 + k * 60
        p1, p2 = rim(a1), rim(a2); c1, c2 = ctrl(a1), ctrl(a2)
        sh.region(f"M{f(P[0])} {f(P[1])}Q{f(c1[0])} {f(c1[1])} {f(p1[0])} {f(p1[1])}A{R} {R} 0 0 1 {f(p2[0])} {f(p2[1])}Q{f(c2[0])} {f(c2[1])} {f(P[0])} {f(P[1])}Z", codes[k])
    sh.circle_r(P[0], P[1], 10, "-")
    sh.line("M140 70Q148 84 148 100")

def stapelringen(sh):
    floor(sh, 178, "w")
    sh.rect_r(34, 156, 132, 24, "p", 8)
    y = 156
    for w, c in ((124, "r"), (104, "o"), (86, "y"), (68, "g"), (52, "b")):
        sh.rect_r(100 - w / 2, y - 22, w, 22, c, 11); y -= 22
    sh.circle_r(100, 32, 16, "m")
    eye(sh, 94, 30, 2); eye(sh, 106, 30, 2); smile(sh, 100, 36, 4)

def trekeendje(sh):
    floor(sh, 182, "k")
    sh.line("M56 146Q30 150 26 170")
    sh.circle_r(22, 172, 8, "b")
    sh.poly_r([(140, 104), (166, 80), (156, 120)], "y")
    sh.ellipse_r(104, 116, 48, 28, "y")
    sh.region("M92 110Q114 96 138 110Q124 132 98 124Z", "o")
    sh.circle_r(70, 74, 23, "y")
    sh.region("M50 74L26 82L50 90Z", "o")
    eye(sh, 64, 68, 3)
    sh.rect_r(52, 138, 104, 14, "w", 5)
    for x in (74, 134):
        sh.circle_r(x, 158, 18, "r"); sh.circle_r(x, 158, 6, "y")

def pop_in_kinderwagen(sh):
    grass(sh, 184)
    sh.line("M84 146L66 168M122 146L140 168")
    for x in (66, 140):
        sh.circle_r(x, 170, 16, "z"); sh.circle_r(x, 170, 5, "-")
    sh.circle_r(124, 86, 16, "-")
    sh.region("M108 82A16 16 0 0 1 140 82Q132 74 122 78Q114 74 108 82Z", "w")
    eye(sh, 118, 88, 2); eye(sh, 130, 88, 2); smile(sh, 124, 94, 3)
    sh.region("M38 100H166Q166 150 124 152H80Q38 150 38 100Z", "k")
    sh.rect_r(98, 96, 70, 16, "b", 7)
    sh.region("M38 100A64 64 0 0 1 102 36V100Z", "m")
    sh.line("M102 100L56 55M102 100L80 42")
    sh.line("M166 100L182 72", "l", "stroke-width:3")
    limb(sh, 176, 70, 192, 64, "x", 9)

def xylofoon(sh):
    def top(x): return 66 + (x - 39) * 6 / 24
    def bot(x): return 154 - (x - 39) * 6 / 24
    limb(sh, 22, top(22), 178, top(178), "w", 10)
    limb(sh, 22, bot(22), 178, bot(178), "w", 10)
    for i, c in enumerate("royg bp".replace(" ", "")):
        x = 30 + i * 24
        sh.rect_r(x, 50 + 6 * i, 18, 120 - 12 * i, c, 4)
        sh.dot(x + 9, top(x + 9), 2); sh.dot(x + 9, bot(x + 9), 2)
    limb(sh, 30, 194, 100, 182, "w", 5); sh.circle_r(106, 181, 9, "r")
    limb(sh, 188, 196, 146, 188, "w", 5); sh.circle_r(140, 187, 9, "b")

def emmer_en_schep(sh):
    sun(sh, 30, 30, 12)
    sh.region(cloud_path(150, 36, 16), "-")
    sh.region("M0 200V146Q100 132 200 146V200Z", "y")
    sh.line("M50 96Q95 30 140 96", "l", "stroke-width:3")
    sh.region("M50 96H140L130 182H60Z", "r")
    sh.rect_r(44, 88, 102, 14, "o", 6)
    sh.region(star_path(95, 140, 22, 10), "y")
    limb(sh, 152, 66, 166, 148, "b", 9)
    sh.region("M152 144H184L180 176Q168 190 156 176Z", "g")

def loopfiets(sh):
    grass(sh, 184)
    sun(sh, 30, 30, 12)
    for x in (50, 150):
        sh.circle_r(x, 150, 32, "z"); sh.circle_r(x, 150, 21, "-"); sh.circle_r(x, 150, 6, "y")
    limb(sh, 80, 108, 76, 86, "z", 7)
    sh.region("M44 146L78 102H132L156 146L146 150L126 116H86L54 152Z", "r")
    limb(sh, 132, 106, 124, 70, "r", 9)
    limb(sh, 110, 66, 142, 70, "z", 7)
    limb(sh, 102, 64, 116, 66, "x", 10)
    sh.ellipse_r(76, 82, 20, 7, "x")

def hobbelpaard(sh):
    floor(sh, 188, "k")
    for x, y in ((66, 176), (80, 178), (124, 178), (138, 176)):
        limb(sh, x, 118, x, y, "w", 11)
    sh.region("M16 160Q100 204 184 160L188 170Q100 214 12 170Z", "r")
    sh.region("M146 104Q174 96 180 126Q168 116 150 118Z", "y")
    sh.ellipse_r(102, 110, 50, 22, "w")
    sh.region("M70 112L46 64Q52 44 70 46L96 100Z", "w")
    sh.poly_r([(58, 46), (64, 26), (72, 46)], "w")
    rot_ellipse(sh, 46, 62, 24, 14, -18, "w")
    sh.region("M70 44Q86 56 92 96Q84 100 80 94Q74 64 62 48Z", "y")
    eye(sh, 52, 56, 2.6); sh.dot(29, 68, 1.6)
    sh.region("M94 92Q108 84 124 92L126 112Q108 120 92 112Z", "r")

def knuffelkonijn(sh):
    sh.ellipse_r(100, 186, 84, 12, "l")
    for cx, a in ((80, -12), (120, 12)):
        rot_ellipse(sh, cx, 50, 14, 34, a, "k"); rot_ellipse(sh, cx, 52, 7, 24, a, "m")
    for x in (58, 142): sh.ellipse_r(x, 136, 11, 19, "k")
    sh.ellipse_r(100, 142, 44, 40, "k")
    sh.ellipse_r(100, 150, 26, 26, "-")
    for x in (72, 128):
        sh.ellipse_r(x, 178, 19, 11, "k"); sh.circle_r(x, 178, 6, "m")
    sh.circle_r(100, 88, 34, "k")
    eye(sh, 88, 84, 3.4); eye(sh, 112, 84, 3.4)
    sh.region(heart_path(100, 95, 7), "m")
    sh.line("M100 101V104M93 106Q100 110 107 106")
    sh.poly_r([(100, 122), (80, 112), (80, 132)], "b"); sh.poly_r([(100, 122), (120, 112), (120, 132)], "b")
    sh.circle_r(100, 122, 6, "b")


# ---------- kleding ----------
def muts_en_wanten(sh):
    sh.region(blob(100, 18, 13, 12, 9), "y")
    sh.region("M52 84Q52 26 100 26Q148 26 148 84Z", "r")
    sh.region(star_path(100, 56, 16, 7.5), "y")
    sh.rect_r(46, 76, 108, 20, "y", 9)
    for x in range(58, 146, 12): sh.seg(x, 80, x, 92)
    for x, s in ((52, -1), (148, 1)):
        rot_ellipse(sh, x + s * 20, 148, 8, 14, s * 40, "b")
        sh.region(f"M{x - 20} 182V142C{x - 20} 126 {x - 10} 118 {x} 118C{x + 10} 118 {x + 20} 126 {x + 20} 142V182Z", "b")
        sh.rect_r(x - 23, 176, 46, 16, "y", 5)
        sh.region(heart_path(x, 150, 10), "r")

def winterjas(sh):
    sh.line("M100 36V24Q100 14 108 14Q116 16 113 24")
    sh.line("M100 36L54 54H146Z")
    sh.region("M62 54L40 66L28 144H52L60 100Z", "r"); sh.region("M138 54L160 66L172 144H148L140 100Z", "r")
    sh.rect_r(26, 140, 28, 12, "y", 4); sh.rect_r(146, 140, 28, 12, "y", 4)
    sh.region("M62 54Q80 66 100 66Q120 66 138 54L144 100V186H56V100Z", "r")
    sh.region("M62 54Q80 72 100 74Q120 72 138 54L128 44Q114 56 100 56Q86 56 72 44Z", "y")
    sh.seg(100, 74, 100, 186)
    sh.rect_r(64, 140, 26, 22, "y", 4); sh.rect_r(110, 140, 26, 22, "y", 4)
    for y in (96, 118): sh.circle_r(110, y, 5.5, "w")

def pyjama(sh):
    sh.region("M70 26Q85 34 100 34Q115 34 130 26L172 48L160 76L142 68V106H58V68L40 76L28 48Z", "b")
    sh.region("M84 29L100 50L116 29Q100 36 84 29Z", "-")
    for y in (62, 78, 94): sh.dot(100, y, 2.4)
    sh.region(moon_path(74, 82, 13), "y")
    sh.region(star_path(126, 84, 13, 6), "y")
    sh.rect_r(58, 114, 84, 12, "n", 4)
    sh.region("M60 126H140L148 192H108L100 150L92 192H52Z", "b")
    sh.region(star_path(76, 166, 11, 5), "y"); sh.region(star_path(124, 166, 11, 5), "y")

def sokken_aan_de_lijn(sh):
    grass(sh, 184)
    sun(sh, 100, 26, 11)
    sh.rect_r(6, 48, 8, 140, "w"); sh.rect_r(186, 48, 8, 140, "w")
    sh.line("M14 56Q100 76 186 56")
    def sock(x, t, body, cuff, toe, stripes=None):
        sh.region(f"M{x - 14} {t}V{t + 60}Q{x - 14} {t + 82} {x + 4} {t + 82}H{x + 24}Q{x + 36} {t + 82} {x + 36} {t + 70}Q{x + 36} {t + 56} {x + 20} {t + 56}H{x + 14}V{t}Z", body)
        sh.region(f"M{x + 20} {t + 56}Q{x + 36} {t + 56} {x + 36} {t + 70}Q{x + 36} {t + 82} {x + 24} {t + 82}Q{x + 16} {t + 70} {x + 20} {t + 56}Z", toe)
        if stripes:
            for y in (t + 24, t + 40): sh.rect_r(x - 14, y, 28, 8, stripes)
        sh.rect_r(x - 14, t, 28, 14, cuff)
        sh.rect_r(x - 4, t - 8, 8, 16, "w", 2)
    sock(48, 66, "r", "-", "-")
    sock(100, 70, "y", "g", "g", "g")
    sock(146, 66, "b", "-", "n")


# ---------- eten ----------
def brood(sh):
    sh.rect_r(0, 166, 200, 34, "b")
    sh.rect_r(10, 140, 146, 22, "w", 9)
    sh.region("M18 142C14 100 40 74 82 74C124 74 150 100 146 142Z", "o")
    sh.line("M54 92Q64 106 58 122M84 84Q94 100 88 118M114 92Q122 106 116 122")
    sh.region("M146 188V148C134 142 136 120 150 116C160 108 176 108 186 116C200 120 202 142 190 148V188Z", "o")
    sh.region("M153 182V144C145 140 145 126 155 123C163 117 173 117 181 123C191 126 191 140 183 144V182Z", "-")

def eitje_in_eierdopje(sh):
    sh.ellipse_r(100, 170, 88, 20, "b"); sh.ellipse_r(100, 168, 64, 12, "-")
    limb(sh, 152, 178, 186, 162, "z", 6); sh.ellipse_r(146, 180, 10, 6, "z")
    sh.ellipse_r(100, 164, 30, 8, "r")
    sh.rect_r(90, 138, 20, 28, "r")
    sh.region("M100 32C122 32 140 66 140 98H60C60 66 78 32 100 32Z", "-")
    sh.region("M58 98H142Q142 146 100 146Q58 146 58 98Z", "r")
    for x, y in ((80, 114), (100, 128), (120, 114)): sh.circle_r(x, y, 6, "-")

def koekjes(sh):
    sh.ellipse_r(100, 120, 92, 62, "b"); sh.ellipse_r(100, 120, 72, 46, "-")
    sh.circle_r(64, 106, 28, "o")
    for dx, dy in ((-12, -8), (8, -14), (-4, 8), (14, 6), (-16, 14), (2, -2)): sh.dot(64 + dx, 106 + dy, 3)
    sh.region(heart_path(136, 106, 32), "m"); sh.region(heart_path(136, 106, 20), "k")
    sh.region(star_path(100, 152, 28, 14), "y")

def beker_melk(sh):
    floor(sh, 172, "w")
    sh.circle_r(30, 172, 18, "o")
    for dx, dy in ((-6, -4), (5, -8), (2, 4)): sh.dot(30 + dx, 172 + dy, 2.6)
    limb(sh, 108, 64, 136, 12, "r", 9)
    sh.region("M146 82C184 82 184 142 146 142V126C164 126 164 98 146 98Z", "b")
    sh.region("M54 62H146V156Q146 176 126 176H74Q54 176 54 156Z", "b")
    sh.ellipse_r(100, 62, 46, 10, "b"); sh.ellipse_r(100, 62, 39, 7, "-")
    sh.region(heart_path(100, 118, 26), "r")

def kommetje_pap(sh):
    sh.ellipse_r(100, 172, 94, 22, "k")
    sh.rect_r(76, 160, 48, 14, "y", 4)
    limb(sh, 132, 96, 180, 36, "z", 9)
    sh.region("M28 96H172Q172 164 100 166Q28 164 28 96Z", "y")
    for x in (64, 100, 136): sh.region(heart_path(x, 128, 12), "r")
    sh.ellipse_r(100, 96, 72, 14, "-")
    for x, y in ((80, 93), (98, 89), (116, 94)): sh.circle_r(x, y, 8, "p")
    sh.line("M64 70Q56 58 64 48Q72 38 64 26M100 66Q92 54 100 44Q108 34 100 22")

def druiven(sh):
    sh.ellipse_r(100, 180, 84, 14, "b")
    limb(sh, 100, 50, 106, 22, "w", 7)
    rot_leaf(sh, 132, 34, 15, 24, 62, "g")
    rows = ((60, (49, 83, 117, 151)), (89, (66, 100, 134)), (118, (83, 117)), (147, (100,)))
    for y, xs in rows:
        for x in xs:
            sh.circle_r(x, y, 18, "p"); sh.line(f"M{x - 10} {y - 4}Q{x - 9} {y - 10} {x - 4} {y - 12}")

def tomaat(sh):
    sh.rect_r(8, 164, 184, 22, "w", 8)
    sh.ellipse_r(88, 116, 64, 56, "r")
    limb(sh, 88, 64, 94, 40, "l", 7)
    sh.region(star_path(88, 66, 26, 9, 6), "g")
    sh.line("M48 98Q52 82 64 76")
    sh.ellipse_r(164, 154, 26, 22, "r")
    sh.region(star_path(164, 134, 12, 4, 5), "g")

def lolly(sh):
    sh.rect_r(94, 130, 12, 66, "-", 4)
    cx, cy, R = 100, 80, 62
    sh.circle_r(cx, cy, R, "y")
    T = 5 * math.pi; k = R / T
    n = 160
    outer = [(cx + k * t * math.cos(t), cy + k * t * math.sin(t)) for t in (math.pi + (T - math.pi) * i / n for i in range(n + 1))]
    inner = [(cx + k * (t - math.pi) * math.cos(t), cy + k * (t - math.pi) * math.sin(t)) for t in (math.pi + (T - math.pi) * i / n for i in range(n, -1, -1))]
    sh.region("M" + " L".join(f"{f(x)} {f(y)}" for x, y in outer + inner) + "Z", "r")
    sh.poly_r([(100, 156), (74, 144), (74, 168)], "m"); sh.poly_r([(100, 156), (126, 144), (126, 168)], "m")
    sh.circle_r(100, 156, 6, "m")
    sh.region(star_path(30, 160, 14, 6), "y"); sh.region(star_path(172, 168, 12, 5), "b")

def stuk_kaas(sh):
    sh.rect_r(8, 150, 184, 28, "w", 9)
    sh.region("M26 128L132 66L182 96Z", "y")
    sh.region("M26 128L182 96V158H26Z", "y")
    sh.ellipse_r(126, 92, 11, 5, "o")
    for x, y, rx, ry in ((60, 140, 11, 8), (106, 128, 14, 11), (156, 136, 10, 13), (128, 148, 7, 5)): sh.ellipse_r(x, y, rx, ry, "o")


# ---------- dagelijkse dingen ----------
def tandenborstel(sh):
    for x, y, r in ((40, 56, 11), (68, 34, 8), (26, 28, 6), (170, 30, 9)): sh.circle_r(x, y, r, "-")
    sh.region("M18 126Q18 116 30 116H138L150 118H190V134H150L138 136H30Q18 136 18 126Z", "g")
    sh.rect_r(40, 116, 44, 20, "l", 8)
    sh.rect_r(146, 92, 44, 26, "-", 3)
    for x in range(152, 188, 7): sh.seg(x, 104, x, 118)
    sh.region("M146 96C140 76 160 72 168 82C176 68 198 74 192 96Z", "b")
    sh.region("M24 166Q20 172 24 178L30 186H120Q128 186 128 178V166Q128 158 120 158H30Z", "b")
    sh.rect_r(128, 162, 22, 20, "r", 4)
    sh.region(star_path(76, 172, 11, 5), "y")

def bedje(sh):
    sh.rect_r(132, 22, 52, 46, "n", 4)
    sh.region(moon_path(150, 44, 13), "y"); sh.region(star_path(172, 34, 7, 3), "y")
    floor(sh, 186, "w")
    sh.region("M16 186V88Q16 66 30 66Q44 66 44 88V186Z", "w")
    sh.region("M160 186V118Q160 102 172 102Q184 102 184 118V186Z", "w")
    sh.ellipse_r(66, 118, 24, 13, "-")
    sh.circle_r(74, 108, 16, "-")
    sh.region("M58 108A16 16 0 0 1 90 108Q82 98 72 102Q64 98 58 108Z", "o")
    sh.line("M66 110Q69 113 72 110M77 110Q80 113 83 110")
    sh.region("M68 120Q110 108 164 118V158H68Z", "b")
    for x, y in ((96, 136), (124, 132), (148, 140)): sh.region(star_path(x, y, 10, 4.5), "y")
    sh.rect_r(40, 156, 124, 12, "w", 3)
    sh.text(104, 86, "z z z", 10)

def babyfles(sh):
    for x, y, r in ((40, 60, 12), (160, 80, 10), (36, 150, 10), (164, 160, 12)): sh.region(star_path(x, y, r, r * .45), "y")
    sh.region("M84 52C84 36 90 22 100 22C110 22 116 36 116 52Z", "o")
    sh.rect_r(72, 50, 56, 24, "b", 5)
    sh.rect_r(70, 74, 60, 112, "-", 18)
    sh.region("M70 112H130V168Q130 186 112 186H88Q70 186 70 168Z", "-")
    for y in (90, 106, 122, 138, 154): sh.seg(118, y, 128, y)
    sh.region(heart_path(94, 146, 14), "m")

def glijbaan(sh):
    sun(sh, 30, 30, 12)
    sh.region(cloud_path(150, 34, 16), "-")
    grass(sh, 184)
    limb(sh, 104, 64, 104, 186, "y", 8); limb(sh, 150, 150, 150, 186, "y", 8)
    limb(sh, 38, 186, 66, 62, "b", 8); limb(sh, 64, 186, 92, 62, "b", 8)
    for k in range(1, 6):
        t = k / 6; sh.seg(38 + 28 * t + 3, 186 - 124 * t, 64 + 28 * t - 3, 186 - 124 * t)
    sh.rect_r(64, 56, 46, 10, "y", 3)
    sh.region("M106 56C138 56 146 150 190 166V182C134 170 128 78 104 72Z", "r")
    sh.circle_r(30, 176, 11, "g")

def zandbak(sh):
    sh.rect_r(0, 96, 200, 104, "l")
    sun(sh, 30, 30, 12)
    sh.poly_r([(8, 150), (40, 104), (160, 104), (192, 150)], "w")
    sh.poly_r([(28, 143), (50, 113), (150, 113), (172, 143)], "y")
    sh.rect_r(8, 150, 184, 26, "w")
    sh.seg(8, 163, 192, 163)
    limb(sh, 166, 60, 156, 118, "b", 7)
    sh.region("M146 114H166L163 134Q156 140 149 134Z", "g")
    sh.region("M92 138V102H101V92H110V102H122V92H131V102H140V138Z", "o")
    sh.region("M108 138V126Q116 116 124 126V138Z", "w")
    sh.region("M44 106H76L71 138H49Z", "r"); sh.rect_r(41, 100, 38, 9, "r", 4)
    sh.region(star_path(40, 186, 11, 5.5), "p")


# ---------- natuur en dieren ----------
def bloempot(sh):
    sun(sh, 172, 26, 11)
    sh.rect_r(0, 186, 200, 14, "w")
    limb(sh, 100, 130, 100, 70, "g", 7)
    rot_leaf(sh, 80, 108, 10, 20, -50, "g"); rot_leaf(sh, 120, 100, 10, 20, 50, "g")
    for k in range(6):
        a = math.radians(k * 60 - 90)
        sh.circle_r(100 + 24 * math.cos(a), 56 + 24 * math.sin(a), 17, "m")
    sh.circle_r(100, 56, 16, "y")
    eye(sh, 94, 53, 2); eye(sh, 106, 53, 2); smile(sh, 100, 60, 4)
    sh.region("M64 138H136L126 188H74Z", "o")
    sh.rect_r(56, 124, 88, 18, "o", 4)

def otter(sh):
    sun(sh, 172, 28, 12)
    sh.region("M156 122Q184 122 196 102Q192 132 160 136Z", "w")
    for x in (150, 168): sh.ellipse_r(x, 98, 8, 13, "w")
    sh.ellipse_r(106, 122, 64, 24, "w")
    sh.ellipse_r(110, 112, 46, 13, "-")
    for x in (24, 56): sh.circle_r(x, 82, 6, "w")
    sh.ellipse_r(40, 104, 30, 25, "w")
    sh.ellipse_r(32, 114, 17, 11, "-"); sh.ellipse_r(26, 108, 6, 4, "x")
    sh.line("M15 112L3 108M15 117L3 119M49 112L60 108M49 117L60 119")
    eye(sh, 32, 96, 3); eye(sh, 52, 98, 3)
    sh.region("M90 108A20 20 0 0 1 130 108Z", "k"); sh.line("M110 108V90M110 108L97 95M110 108L123 95")
    sh.ellipse_r(88, 110, 7, 6, "w"); sh.ellipse_r(132, 110, 7, 6, "w")
    sh.region("M0 200V136Q25 128 50 136T100 136T150 136T200 136V200Z", "b")
    for y, x0 in ((152, 14), (172, 40), (190, 8)):
        for x in range(x0, 200, 56): sh.line(f"M{x} {y}Q{x + 8} {y - 5} {x + 16} {y}")

def kalkoen(sh):
    grass(sh, 184)
    cols = "royroyr"
    for i, a in enumerate(range(-165, -14, 25)):
        cx = 100 + 46 * math.cos(math.radians(a)); cy = 112 + 46 * math.sin(math.radians(a))
        rot_ellipse(sh, cx, cy, 15, 40, a + 90, cols[i])
    for s in (-1, 1): limb(sh, 100 + s * 12, 160, 100 + s * 14, 182, "o", 5)
    sh.line("M76 184L86 180L96 184M104 184L114 180L124 184")
    sh.ellipse_r(100, 128, 40, 40, "w")
    for s in (-1, 1): rot_ellipse(sh, 100 + s * 30, 132, 11, 24, -s * 20, "o")
    sh.line("M86 140Q93 146 100 140Q107 146 114 140M90 154Q100 160 110 154")
    sh.circle_r(100, 82, 19, "w")
    eye(sh, 93, 77, 2.4); eye(sh, 107, 77, 2.4)
    sh.region("M94 84L100 96L106 84Z", "y")
    sh.region("M104 90Q114 100 106 110Q98 104 101 92Z", "r")

def regenworm(sh):
    sun(sh, 30, 30, 12)
    sh.rect_r(0, 104, 200, 96, "w")
    sh.region("M0 110V98Q50 90 100 98T200 98V110Z", "g")
    for x, y, r in ((30, 160, 9), (150, 176, 11), (110, 146, 7)): sh.circle_r(x, y, r, "z")
    sh.ellipse_r(66, 112, 28, 8, "x")
    P = [(66, 114), (60, 30), (144, 22), (150, 66)]
    def B(t): return tuple((1 - t) ** 3 * P[0][i] + 3 * (1 - t) ** 2 * t * P[1][i] + 3 * (1 - t) * t * t * P[2][i] + t ** 3 * P[3][i] for i in (0, 1))
    n, w = 60, 13
    cen = [B(i / n) for i in range(n + 1)]
    L, Rt = [], []
    for i, (x, y) in enumerate(cen):
        a, b = cen[max(i - 1, 0)], cen[min(i + 1, n)]
        dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy)
        L.append((x - dy / d * w, y + dx / d * w)); Rt.append((x + dy / d * w, y - dx / d * w))
    sh.region("M" + " L".join(f"{f(x)} {f(y)}" for x, y in L + Rt[::-1]) + "Z", "m")
    for i in range(8, 52, 8):
        sh.line(f"M{f(L[i][0])} {f(L[i][1])}L{f(Rt[i][0])} {f(Rt[i][1])}")
    sh.region("M38 112Q66 124 94 112Q66 130 38 112Z", "w")
    sh.circle_r(152, 72, 19, "m")
    eye(sh, 145, 72, 2.6); eye(sh, 159, 72, 2.6); smile(sh, 152, 79, 5)

def mier(sh):
    sun(sh, 30, 28, 12)
    sh.rect_r(0, 172, 200, 28, "l")
    sh.line("M88 130L76 150L68 172M100 134L100 154L96 172M112 130L124 150L130 172", "l", "stroke-width:3")
    sh.line("M108 120L118 98L126 82", "l", "stroke-width:3")
    rot_leaf(sh, 112, 58, 22, 46, 68, "g")
    sh.ellipse_r(56, 126, 32, 24, "w")
    sh.ellipse_r(100, 124, 17, 13, "w")
    sh.line("M144 96Q146 72 136 60M154 100Q164 80 176 76")
    sh.circle_r(136, 58, 5, "w"); sh.circle_r(178, 74, 5, "w")
    sh.circle_r(140, 112, 22, "w")
    sh.circle_r(148, 106, 8, "-"); eye(sh, 150, 106, 3.4)
    smile(sh, 150, 120, 6)

def roodborstje(sh):
    sun(sh, 30, 28, 12)
    rot_leaf(sh, 176, 142, 9, 18, -30, "g"); rot_leaf(sh, 22, 142, 9, 18, 30, "g")
    sh.region("M126 132L158 170L140 180L114 144Z", "w")
    limb(sh, -6, 160, 206, 160, "w", 14)
    sh.ellipse_r(100, 106, 46, 44, "w")
    sh.region("M56 104C56 84 64 72 74 66C88 86 96 120 128 132C116 146 102 150 94 150C72 148 56 128 56 104Z", "o")
    sh.region("M110 92Q146 92 148 128Q130 134 110 122Z", "w")
    sh.circle_r(76, 86, 7, "-"); eye(sh, 74, 86, 3.2)
    sh.region("M58 92L42 98L58 104Z", "x")
    sh.line("M92 149V154M108 149V154")

def feestjurk(sh):
    sh.line("M100 36V22Q100 12 108 12Q116 14 113 22")
    sh.line("M100 36L56 50H144Z")
    sh.ellipse_r(62, 56, 17, 13, "k"); sh.ellipse_r(138, 56, 17, 13, "k")
    sh.region("M74 40Q86 52 100 52Q114 52 126 40L138 48V100H62V48Z", "m")
    sh.region("M62 106H138L178 182Q100 194 22 182Z", "m")
    sh.region("M22 182Q100 194 178 182L184 192Q100 204 16 192Z", "k")
    for x, y in ((66, 150), (134, 150), (100, 168)): sh.region(heart_path(x, y, 13), "r")
    sh.rect_r(58, 98, 84, 12, "r", 4)
    sh.poly_r([(100, 104), (80, 94), (80, 114)], "r"); sh.poly_r([(100, 104), (120, 94), (120, 114)], "r")
    sh.circle_r(100, 104, 6, "r")


# ---------- voertuigen ----------
def duikboot(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.region("M0 200V178Q50 168 100 176T200 172V200Z", "y")
    rot_leaf(sh, 20, 156, 8, 26, 0, "g", False); rot_leaf(sh, 182, 152, 8, 28, 0, "g", False)
    for x, y, r in ((150, 40, 7), (162, 24, 5), (172, 54, 6)): sh.circle_r(x, y, r, "-")
    sh.region(fish_path(48, 40, 14), "o"); eye(sh, 40, 38, 1.6)
    sh.rect_r(104, 38, 7, 34, "z"); sh.rect_r(104, 34, 24, 8, "z", 3)
    sh.rect_r(82, 62, 48, 36, "y", 8)
    sh.ellipse_r(28, 110, 6, 13, "o"); sh.ellipse_r(28, 138, 6, 13, "o")
    sh.region("M34 124Q34 96 64 96H146Q178 96 178 124Q178 152 146 152H64Q34 152 34 124Z", "y")
    sh.circle_r(30, 124, 6, "o")
    for x in (72, 106, 140): sh.circle_r(x, 124, 11, "t")

def taxi(sh):
    sun(sh, 28, 28, 12)
    sh.rect_r(0, 172, 200, 28, "z")
    for x in (10, 70, 130, 190): sh.seg(x, 188, x + 30, 188, "l", "stroke-width:2.5")
    sh.rect_r(86, 56, 36, 16, "-", 3); sh.text(104, 67.5, "TAXI", 8, weight="bold")
    sh.region("M14 150V124Q14 114 26 112L50 108L70 80Q74 72 84 72H128Q136 72 142 80L160 108L178 112Q188 114 188 124V150Q188 158 180 158H22Q14 158 14 150Z", "y")
    sh.region("M80 82H102V106H62Z", "b"); sh.region("M110 82H130Q134 82 136 86L150 106H110Z", "b")
    sh.seg(106, 108, 106, 156); sh.line("M114 124H124", "l", "stroke-width:3")
    sh.circle_r(180, 124, 6, "o"); sh.rect_r(14, 120, 8, 12, "r", 2)
    for x in (54, 150): sh.circle_r(x, 158, 18, "x"); sh.circle_r(x, 158, 7, "-")


PLATES = [
    ("strandbal", "Strandbal", "zee", strandbal),
    ("stapelringen", "Stapeltoren met ringen", "thuis", stapelringen),
    ("trekeendje", "Trekeendje op wieltjes", "thuis", trekeendje),
    ("pop-in-kinderwagen", "Pop in de kinderwagen", "thuis", pop_in_kinderwagen),
    ("xylofoon", "Xylofoon", "thuis", xylofoon),
    ("emmer-en-schep", "Emmer en schep", "zee", emmer_en_schep),
    ("loopfiets", "Loopfiets", "voertuigen", loopfiets),
    ("hobbelpaard", "Hobbelpaard", "thuis", hobbelpaard),
    ("knuffelkonijn", "Knuffelkonijn", "thuis", knuffelkonijn),
    ("muts-en-wanten", "Muts en wanten", "thuis", muts_en_wanten),
    ("winterjas", "Winterjas", "thuis", winterjas),
    ("pyjama", "Pyjama met sterren", "thuis", pyjama),
    ("sokken-aan-de-lijn", "Sokken aan de waslijn", "thuis", sokken_aan_de_lijn),
    ("brood", "Brood", "eten", brood),
    ("eitje-in-eierdopje", "Eitje in een eierdopje", "eten", eitje_in_eierdopje),
    ("koekjes", "Koekjes op een bord", "eten", koekjes),
    ("beker-melk", "Beker melk", "eten", beker_melk),
    ("kommetje-pap", "Kommetje pap", "eten", kommetje_pap),
    # ("druiven", "Druiven", "eten", druiven),  # bestaat al
    ("tomaat", "Tomaat", "eten", tomaat),
    ("lolly", "Lolly", "eten", lolly),
    ("stuk-kaas", "Stuk kaas", "eten", stuk_kaas),
    ("tandenborstel", "Tandenborstel en tandpasta", "thuis", tandenborstel),
    ("bedje", "Slapen in bed", "thuis", bedje),
    ("babyfles", "Babyfles", "thuis", babyfles),
    ("glijbaan", "Glijbaan", "sport", glijbaan),
    ("zandbak", "Zandbak", "thuis", zandbak),
    ("bloempot", "Bloem in een pot", "natuur", bloempot),
    # ("otter", "Otter in het water", "dieren", otter),
    ("kalkoen", "Kalkoen", "boerderij", kalkoen),
    ("regenworm", "Regenworm", "natuur", regenworm),
    # ("mier", "Mier met een blaadje", "dieren", mier),
    ("roodborstje", "Roodborstje op een tak", "dieren", roodborstje),
    ("feestjurk", "Feestjurk", "thuis", feestjurk),
    ("duikboot", "Duikboot", "voertuigen", duikboot),
    ("taxi", "Taxi", "voertuigen", taxi),
]

for slug, name, cat, draw in PLATES:
    kp(slug, name, cat, "2-4", 1, draw)
