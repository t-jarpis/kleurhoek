"""Batch 17a: nieuwe kleurplaten (eigen tekeningen, 200x200): dieren en natuur.
Huisdieren, vogels, kleine beestjes, zeedieren, dieren van de wereld, dierenfamilies en natuurtaferelen."""
import math
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from shapes import heart_path, star_path, moon_path, cloud_path, leaf_path, fish_path


# ---------- hulpjes ----------
def limb(sh, x1, y1, x2, y2, code, w=9):
    """Poot of arm als balk met afgeronde uiteinden van (x1,y1) naar (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * w / 2, dx / d * w / 2
    r = w / 2
    sh.region(f"M{f(x1 + nx)} {f(y1 + ny)}L{f(x2 + nx)} {f(y2 + ny)}A{f(r)} {f(r)} 0 0 0 {f(x2 - nx)} {f(y2 - ny)}L{f(x1 - nx)} {f(y1 - ny)}A{f(r)} {f(r)} 0 0 0 {f(x1 + nx)} {f(y1 + ny)}Z", code)

def flower(sh, x, y, r=5, petal="m", heart="y"):
    for k in range(5):
        a = math.radians(k * 72 - 90)
        sh.circle_r(x + r * math.cos(a), y + r * math.sin(a), r * .7, petal)
    sh.circle_r(x, y, r * .55, heart)

def sparkle(sh, x, y, r=5, code="y"):
    sh.region(f"M{f(x)} {f(y - r)}Q{f(x + r * .2)} {f(y - r * .2)} {f(x + r)} {f(y)}Q{f(x + r * .2)} {f(y + r * .2)} {f(x)} {f(y + r)}Q{f(x - r * .2)} {f(y + r * .2)} {f(x - r)} {f(y)}Q{f(x - r * .2)} {f(y - r * .2)} {f(x)} {f(y - r)}Z", code)

def wool(sh, cx, cy, rx, ry, n, code="-", bulge=.62):
    """Wolk-/wolvorm: ellips met bolletjes langs de rand."""
    p = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
    d = f"M{f(p[0][0])} {f(p[0][1])}"
    for i in range(n):
        x1, y1 = p[i]; x2, y2 = p[(i + 1) % n]
        r = math.hypot(x2 - x1, y2 - y1) * bulge
        d += f"A{f(r)} {f(r)} 0 0 1 {f(x2)} {f(y2)}"
    sh.region(d + "Z", code)

def band(center, widths):
    """Polygoon langs een middenlijn met een breedte per punt."""
    left, right = [], []
    for i, (x, y) in enumerate(center):
        a = center[max(i - 1, 0)]; b = center[min(i + 1, len(center) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d * widths[i] / 2, dx / d * widths[i] / 2
        left.append((x + nx, y + ny)); right.append((x - nx, y - ny))
    return left, right

def sun(sh, x, y, r=13, rays=True):
    sh.circle_r(x, y, r, "y")
    if rays:
        for k in range(8):
            a = math.radians(k * 45 + 22)
            sh.seg(x + (r + 4) * math.cos(a), y + (r + 4) * math.sin(a), x + (r + 10) * math.cos(a), y + (r + 10) * math.sin(a))

def waves(sh, y, n=5, x0=8, step=42, w=20):
    for k in range(n):
        x = x0 + k * step
        sh.line(f"M{x} {y}Q{x + w / 2} {y - 6} {x + w} {y}")

def ellipse_pts(cx, cy, rx, ry, a1, a2, n=40):
    return [(cx + rx * math.cos(math.radians(a1 + (a2 - a1) * i / n)), cy + ry * math.sin(math.radians(a1 + (a2 - a1) * i / n))) for i in range(n + 1)]

def lilypad(sh, x, y, rx, ry, code="g"):
    sh.poly_r([(x, y)] + ellipse_pts(x, y, rx, ry, -60, 250), code)

def bird_m(sh, x, y, s=6):
    sh.line(f"M{f(x - s)} {f(y)}Q{f(x - s / 2)} {f(y - s * .6)} {f(x)} {f(y)}Q{f(x + s / 2)} {f(y - s * .6)} {f(x + s)} {f(y)}")

def mirror(sh, draw):
    """Teken iets en daarna gespiegeld rond x = 100."""
    draw()
    sh.raw('<g transform="translate(200 0) scale(-1 1)">'); draw(); sh.raw("</g>")


# ---------- huisdieren ----------
def cavia(sh):
    grass(sh, 172, "l")
    sun(sh, 30, 30, 13)
    flower(sh, 20, 160, 6, "m"); sh.line("M20 166V176"); flower(sh, 38, 168, 5, "y", "o"); sh.line("M38 173V180")
    for x in (64, 140): sh.ellipse_r(x, 160, 10, 5, "k")
    sh.region("M30 150C24 112 52 86 96 84C136 82 164 98 172 124C176 142 166 158 140 158H52C38 158 32 156 30 150Z", "o")
    sh.region("M52 108C60 94 82 92 92 102C98 116 86 130 70 130C56 130 48 120 52 108Z", "-")
    sh.region("M100 92C110 88 122 92 124 102C124 112 112 118 104 112C98 106 96 98 100 92Z", "w")
    sh.region("M128 96C120 82 134 74 144 84C142 92 136 96 128 96Z", "k")
    sh.circle_r(150, 110, 4.5, "-"); eye(sh, 151, 110, 3)
    sh.ellipse_r(172, 126, 3.5, 2.8, "k")
    sh.line("M170 133Q166 138 160 136"); sh.line("M174 125L192 118M174 128L194 128M172 131L190 138")
    sh.line("M40 120Q48 118 52 124")
    # sla-blaadje
    sh.region("M166 178C160 160 174 150 188 154C198 160 196 174 184 180Z", "g"); sh.line("M168 176Q178 166 190 158")

def goudvis_in_kom(sh):
    sh.rect_r(6, 176, 188, 10, "w", 2); sh.rect_r(16, 186, 8, 14, "w"); sh.rect_r(176, 186, 8, 14, "w")
    sh.region("M64 52Q60 60 52 68Q22 100 30 140Q40 176 100 176Q160 176 170 140Q178 100 148 68Q140 60 136 52Z", "-")
    sh.ellipse_r(100, 52, 36, 6, "-")
    sh.region("M42 88H158Q174 112 168 138Q158 172 100 172Q42 172 32 138Q26 112 42 88Z", "b")
    sh.region("M140 168C134 150 146 136 138 114C152 128 154 150 150 168Z", "g")
    sh.region("M152 166C152 154 160 144 158 132C166 144 166 156 160 166Z", "l")
    for x, y, r, c in ((62, 164, 6, "z"), (76, 166, 5, "o"), (116, 166, 6, "r"), (130, 164, 5, "z"), (92, 167, 4.5, "y")): sh.circle_r(x, y, r, c)
    # goudvis
    sh.region("M80 112C86 98 102 96 110 110Z", "o")
    sh.region("M84 134C88 148 98 148 104 136Z", "o")
    sh.region(fish_path(92, 124, 26), "o")
    sh.circle_r(76, 118, 5, "-"); eye(sh, 75, 118, 2.6)
    sh.line("M68 130Q71 132 74 130")
    for x in (94, 104): sh.line(f"M{x} 112Q{x + 7} 124 {x} 136")
    sh.line("M124 116L132 124L124 132")
    for x, y, r in ((62, 104, 3), (56, 94, 2.4), (62, 84, 2)): sh.circle_r(x, y, r, "-")
    sh.line("M46 104Q40 120 46 138")

def parkiet(sh):
    sh.line("M62 0V146M138 0V146")
    sh.region("M94 140L84 194H100L106 140Z", "n"); sh.line("M92 150L90 190")
    sh.region("M80 76C66 100 72 136 94 150H110C130 136 132 100 120 76Z", "l")
    sh.region("M110 90C126 94 134 118 126 142L108 150C116 128 114 108 110 90Z", "g")
    for y in (104, 116, 128): sh.line(f"M{116 + (y - 104) * .1} {y}Q{122 + (y - 104) * .1} {y + 3} {127} {y - 1}")
    sh.circle_r(100, 64, 22, "y")
    sh.line("M84 52Q88 48 92 52Q96 48 100 52Q104 48 108 52Q112 48 116 52")
    for x in (91, 109): sh.circle_r(x, 62, 4.5, "-"); eye(sh, x, 62, 2.4)
    sh.region("M94 70Q100 66 106 70Q106 80 100 85Q94 80 94 70Z", "o")
    sh.ellipse_r(100, 69, 6, 3, "n")
    sh.circle_r(84, 76, 3.2, "p"); sh.circle_r(116, 76, 3.2, "p")
    for x in (93, 100, 107): sh.dot(x, 82 if x != 100 else 88, 1.8)
    sh.rect_r(56, 146, 88, 7, "w", 3)
    sh.ellipse_r(92, 146, 5.5, 3, "m"); sh.ellipse_r(108, 146, 5.5, 3, "m")
    sh.line("M138 153V162"); sh.region("M130 176C130 164 134 160 138 160C142 160 146 164 146 176Z", "y"); sh.circle_r(138, 178, 2.5, "y")
    for x, y in ((30, 40), (170, 60), (24, 120), (176, 130)): sparkle(sh, x, y, 5, "-")

# ---------- vogels ----------
def merel(sh):
    grass(sh, 170, "l")
    sun(sh, 172, 28, 12)
    flower(sh, 160, 150, 7, "m"); sh.line("M160 157V178"); flower(sh, 182, 160, 5, "y", "o"); sh.line("M182 165V180")
    sh.region("M126 108L174 86L182 98L132 126Z", "x")
    for x, y in ((92, 140), (108, 140)):
        sh.line(f"M{x} {y}L{x - 2} 170M{x - 2} 170L{x - 10} 174M{x - 2} 170L{x + 6} 174")
    sh.region("M50 100C54 82 80 74 100 82C118 88 132 100 136 116C138 132 126 142 104 142C76 142 52 128 50 100Z", "x")
    sh.region("M84 100C100 94 122 102 130 118C118 128 100 128 88 118C82 112 80 106 84 100Z", "x")
    sh.line("M96 112Q108 116 118 112M100 120Q110 124 122 120")
    sh.circle_r(58, 86, 20, "x")
    sh.circle_r(54, 82, 5, "y"); eye(sh, 54, 82, 2.4)
    sh.region("M40 84L18 92L40 98Z", "o")
    sh.region("M20 94C12 110 28 120 20 136C14 150 26 160 22 172L30 172C34 160 22 150 28 138C36 120 20 110 28 96Z", "k")
    sh.line("M20 120h7M22 150h7")

def mus(sh):
    sun(sh, 30, 30, 13)
    sh.region(cloud_path(150, 40, 18), "-")
    sh.region("M138 126L176 104L182 118L146 142Z", "w"); sh.line("M150 118L176 108M152 126L178 114")
    sh.ellipse_r(110, 126, 42, 30, "w")
    sh.ellipse_r(102, 136, 28, 15, "z")
    sh.region("M106 110C130 102 150 114 152 134C138 140 118 136 106 124Z", "w")
    sh.line("M116 116Q130 112 142 122M114 124Q128 122 144 130")
    sh.circle_r(76, 92, 24, "w")
    sh.region("M56 79A24 24 0 0 1 99 85Q80 76 56 79Z", "z")
    sh.ellipse_r(82, 100, 10, 7, "-")
    sh.region("M58 106Q70 114 88 112Q84 122 72 122Q62 118 58 106Z", "x")
    sh.circle_r(64, 90, 3.6, "-"); eye(sh, 63, 90, 2.2)
    sh.region("M54 89L38 95L55 100Z", "x")
    sh.rect_r(0, 152, 200, 14, "w", 2); sh.line("M20 159H60M120 158H170")
    for x in (20, 168): sh.rect_r(x, 166, 12, 34, "w")
    for x in (96, 116): sh.line(f"M{x - 5} 152L{x} 147L{x + 5} 152")

def meeuw(sh):
    sh.rect_r(0, 130, 200, 70, "b")
    for y, x0 in ((150, 4), (170, 24), (190, 8)): waves(sh, y, 4, x0, 50, 22)
    sun(sh, 34, 34, 13)
    sh.region(cloud_path(160, 36, 16), "-")
    # bootje aan de horizon
    sh.region("M142 122H178L172 130H148Z", "r"); sh.line("M160 122V96"); sh.region("M162 98L176 118H162Z", "-")
    bird_m(sh, 120, 60, 7); bird_m(sh, 140, 70, 5)
    sh.rect_r(80, 122, 40, 78, "w", 3); sh.ellipse_r(100, 122, 20, 5, "w"); sh.line("M90 140V196M110 150V190")
    for x1, x2 in ((96, 94), (106, 108)):
        sh.line(f"M{x1} 110L{x2} 120"); sh.region(f"M{x2 - 6} 122L{x2} 118L{x2 + 6} 122Z", "o")
    sh.region("M58 88C60 72 76 66 92 70C110 74 130 82 150 84L176 80L168 94C152 104 130 112 106 112C80 112 58 104 58 88Z", "-")
    sh.region("M86 82C110 76 140 80 168 84L160 96C136 100 110 100 90 94Z", "z")
    sh.region("M150 83L176 80L168 94L154 96Z", "x")
    sh.line("M104 86Q120 90 140 88")
    sh.circle_r(64, 72, 16, "-")
    eye(sh, 60, 68, 2.4)
    sh.region("M50 70L28 74L30 78L50 79Z", "y"); sh.circle_r(34, 77, 2.2, "r")

def reiger(sh):
    sh.rect_r(0, 150, 200, 50, "b")
    waves(sh, 170, 4, 10, 52, 20); waves(sh, 188, 4, 30, 52, 20)
    for x, h in ((16, 70), (28, 90), (182, 80), (192, 100)):
        sh.line(f"M{x} 152V{h}"); sh.ellipse_r(x, h - 8, 4, 11, "w")
    sh.region(leaf_path(22, 120, 6, 26), "g")
    sh.line("M110 118L104 160M122 118L126 160")
    sh.line("M98 160Q104 156 110 160M120 160Q126 156 132 160")
    sh.region("M84 86C96 70 128 68 148 82C160 92 168 108 172 124L150 116C140 124 120 128 104 120C88 112 80 100 84 86Z", "z")
    sh.region("M100 84C120 76 146 82 160 100L170 120C150 112 124 112 104 104Z", "z")
    sh.line("M120 92Q136 96 150 108M118 100Q134 104 152 116")
    sh.region("M82 98C64 86 60 70 70 58C76 50 76 44 68 40L76 32C88 40 88 54 82 64C76 72 80 82 94 90Z", "-")
    sh.line("M76 62L74 70M72 76L72 84", "l", "stroke-dasharray:2 2")
    sh.ellipse_r(70, 34, 11, 8, "-")
    sh.region("M76 30C86 26 98 28 108 22C100 32 88 34 78 36Z", "x")
    sh.region("M70 28C66 28 64 30 66 32H76Z", "x")
    eye(sh, 66, 33, 1.8)
    sh.region("M60 31L26 40L60 38Z", "y")
    sh.region(fish_path(52, 176, 9), "o"); eye(sh, 46, 175, 1.3)


# ---------- kleine beestjes ----------
def libel(sh):
    sh.rect_r(0, 156, 200, 44, "b"); waves(sh, 176, 4, 12, 50, 20)
    for x, h in ((14, 104), (28, 124), (176, 112), (190, 92)):
        sh.line(f"M{x} 158V{h}"); sh.ellipse_r(x, h - 8, 4, 11, "w")
    lilypad(sh, 150, 180, 22, 8)
    def wings():
        sh.region("M96 58C70 36 24 34 14 48C10 60 40 68 96 64Z", "b")
        sh.region("M96 68C70 72 30 86 26 100C32 108 62 96 96 74Z", "b")
        sh.line("M94 61C70 52 40 48 20 50M94 70C70 80 46 90 30 98", "l", "stroke-width:.9")
    mirror(sh, wings)
    sh.region("M95 74C93 110 95 140 100 170C105 140 107 110 105 74Z", "t")
    for y in range(86, 166, 12): sh.line(f"M{95 + (y - 74) * .04} {y}H{105 - (y - 74) * .04}")
    sh.ellipse_r(100, 66, 9, 12, "t")
    sh.circle_r(100, 46, 10, "t")
    for x in (92, 108): sh.circle_r(x, 41, 6.5, "g"); eye(sh, x, 41, 2.6)
    smile(sh, 100, 50, 4)
    sun(sh, 172, 24, 11)

def sprinkhaan(sh):
    grass(sh, 166, "l")
    sun(sh, 30, 28, 12)
    for x in (10, 30, 178, 192):
        sh.region(f"M{x - 4} 172Q{x} 120 {x + 8} 96Q{x + 4} 130 {x + 6} 172Z", "g")
    sh.line("M150 84Q134 44 96 34"); sh.line("M156 84Q154 46 130 28")
    limb(sh, 56, 80, 72, 146, "g", 5); sh.ellipse_r(76, 148, 7, 3, "g")
    for k in range(4): sh.seg(60 + k * 3.4, 94 + k * 13, 56 + k * 3.4, 96 + k * 13)
    for x1, x2 in ((132, 140), (122, 120), (112, 102)):
        limb(sh, x1, 112, x2, 146, "g", 5); sh.ellipse_r(x2 + 2, 148, 5, 2.5, "g")
    sh.region("M40 106C40 96 60 90 92 92L138 94C150 98 150 114 138 118L92 120C62 122 40 116 40 106Z", "l")
    for x in (48, 58, 68): sh.line(f"M{x} {95 + (78 - x) * .05}Q{x + 3} 107 {x} {118 - (78 - x) * .04}")
    sh.region("M54 98C80 88 112 88 128 94L126 102C108 100 82 102 54 104Z", "g")
    sh.region("M116 92C124 88 134 88 140 92L142 112C134 117 124 117 116 112Z", "l")
    sh.line("M120 100Q129 104 138 100")
    sh.region("M136 86C150 74 170 80 174 100C174 112 162 118 148 116C140 110 134 98 136 86Z", "g")
    sh.ellipse_r(156, 94, 6, 7, "-"); eye(sh, 157, 95, 3)
    sh.line("M168 108Q164 112 158 110")
    c = [(112 - 56 * t, 108 - 30 * t - 8 * math.sin(math.pi * t)) for t in [i / 16 for i in range(17)]]
    lft, rgt = band(c, [18 - 11 * (i / 16) ** .8 for i in range(17)])
    sh.poly_r(lft + rgt[::-1], "l")
    sh.line("M" + " L".join(f"{f(x)} {f(y)}" for x, y in c[2:15]), "l", "stroke-width:.9")
    sh.circle_r(*c[-1], 4, "g")

def hommel(sh):
    sh.line("M40 150Q60 110 30 90Q14 80 20 60", "l", "stroke-dasharray:3 4")
    sh.line("M160 200V158"); sh.region(leaf_path(150, 180, 7, 12), "g"); sh.region(leaf_path(172, 176, 7, 12), "g")
    flower(sh, 160, 150, 13, "p", "y")
    sh.ellipse_r(104, 64, 15, 24, "-"); sh.ellipse_r(130, 62, 15, 24, "-")
    for x in (90, 112, 132): sh.line(f"M{x} 134L{x - 4} 148")
    cx, cy, rx, ry = 116, 108, 50, 36
    sh.ellipse_r(cx, cy, rx, ry, "y")
    def stripe(x1, x2, code):
        def yt(x): return cy - ry * math.sqrt(max(0, 1 - ((x - cx) / rx) ** 2))
        def yb(x): return cy + ry * math.sqrt(max(0, 1 - ((x - cx) / rx) ** 2))
        sh.region(f"M{f(x1)} {f(yt(x1))}A{rx} {ry} 0 0 1 {f(x2)} {f(yt(x2))}L{f(x2)} {f(yb(x2))}A{rx} {ry} 0 0 1 {f(x1)} {f(yb(x1))}Z", code)
    stripe(102, 120, "x"); stripe(136, 150, "x"); stripe(158, 166, "-")
    sh.line("M76 64Q66 46 74 36M86 64Q86 46 98 40"); sh.circle_r(74, 34, 3, "x"); sh.circle_r(99, 39, 3, "x")
    sh.circle_r(72, 102, 26, "x")
    for x in (63, 81): sh.circle_r(x, 96, 6, "-"); eye(sh, x + 1, 97, 3)
    sh.region("M64 110Q72 118 80 110Z", "r")
    sh.circle_r(56, 108, 3.5, "m"); sh.circle_r(88, 108, 3.5, "m")

def vuurvlieg(sh, x, y, s=1.0, flip=False):
    if flip: sh.raw(f'<g transform="translate({f(2 * x)} 0) scale(-1 1)">')
    for k in range(8):
        a = math.radians(k * 45)
        tx, ty = x - 11 * s, y + 3 * s
        sh.seg(tx + 12 * s * math.cos(a), ty + 12 * s * math.sin(a), tx + 17 * s * math.cos(a), ty + 17 * s * math.sin(a))
    sh.circle_r(x - 11 * s, y + 3 * s, 8 * s, "y")
    sh.ellipse_r(x, y, 13 * s, 6.5 * s, "w")
    sh.raw(f'<g transform="rotate(-30 {f(x - 2 * s)} {f(y - 8 * s)})">'); sh.region(leaf_path(x - 2 * s, y - 14 * s, 5 * s, 10 * s), "-"); sh.raw("</g>")
    sh.raw(f'<g transform="rotate(20 {f(x + 3 * s)} {f(y - 8 * s)})">'); sh.region(leaf_path(x + 3 * s, y - 14 * s, 5 * s, 10 * s), "-"); sh.raw("</g>")
    sh.circle_r(x + 13 * s, y - 1 * s, 6 * s, "o")
    sh.circle_r(x + 15 * s, y - 2 * s, 2.2 * s, "-"); eye(sh, x + 15.5 * s, y - 2 * s, 1.2 * s)
    sh.line(f"M{f(x + 16 * s)} {f(y - 6 * s)}Q{f(x + 20 * s)} {f(y - 14 * s)} {f(x + 26 * s)} {f(y - 14 * s)}")
    for k in (-4, 2, 8): sh.seg(x + k * s, y + 6 * s, x + (k - 2) * s, y + 11 * s)
    if flip: sh.raw("</g>")

def vuurvliegjes(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region(moon_path(166, 30, 15), "y")
    for x, y in ((30, 20), (80, 14), (120, 34), (190, 70)): sh.region(star_path(x, y, 4.5, 2), "y")
    sh.region("M0 200V160Q50 148 100 158T200 150V200Z", "g")
    for x in range(6, 200, 14):
        h = 120 + (x * 37) % 30
        sh.region(f"M{x - 4} 200Q{x - 2} {h + 20} {x + 3} {h}Q{x + 2} {h + 24} {x + 4} 200Z", "g")
    vuurvlieg(sh, 66, 84, 1.6)
    vuurvlieg(sh, 140, 112, 1.25, True)
    vuurvlieg(sh, 60, 140, .9, True)


# ---------- zee ----------
def zee_egel(sh):
    sh.region("M0 200V164Q50 154 100 162T200 158V200Z", "y")
    sh.region("M110 166C110 140 130 130 160 134C186 138 194 152 192 166Z", "z")
    sh.region("M6 168C6 150 22 142 40 146C56 150 60 160 58 168Z", "z")
    for x, h in ((24, 70), (40, 96), (176, 80)):
        sh.region(f"M{x - 4} 150C{x - 12} {h + 50} {x + 8} {h + 30} {x} {h}C{x + 14} {h + 30} {x + 6} {h + 50} {x + 4} 150Z", "g")
    cx, cy, r = 100, 150, 30
    for k in range(15):
        a = math.radians(180 + k * 180 / 14)
        bx, by = cx + r * .92 * math.cos(a), cy + r * .92 * math.sin(a)
        tx, ty = cx + (r + 24) * math.cos(a), cy + (r + 24) * math.sin(a)
        px, py = -math.sin(a) * 3.2, math.cos(a) * 3.2
        sh.poly_r([(bx + px, by + py), (tx, ty), (bx - px, by - py)], "p")
    sh.region(f"M{cx - r} {cy}A{r} {r} 0 0 1 {cx + r} {cy}Q{cx} {cy + 12} {cx - r} {cy}Z", "p")
    for x in (90, 110): sh.circle_r(x, 140, 4.5, "-"); eye(sh, x, 141, 2.3)
    smile(sh, 100, 147, 5)
    sh.region(fish_path(150, 70, 11), "o"); eye(sh, 142, 69, 1.4)
    sh.raw('<g transform="translate(110 0) scale(-1 1) translate(-110 0)">')
    sh.region(fish_path(60, 46, 9), "y"); eye(sh, 53, 45, 1.3)
    sh.raw("</g>")
    for x, y, rr in ((128, 104, 3), (134, 92, 2.4), (130, 80, 2)): sh.circle_r(x, y, rr, "-")
    sh.region(star_path(70, 182, 9, 4), "o")
    sh.region("M150 186C150 176 162 172 168 180Z", "k"); sh.line("M156 185L156 179M161 185L162 178")

def heremietkreeft(sh):
    sh.region("M0 200V168Q60 158 120 166T200 162V200Z", "y")
    for x, y in ((30, 188), (150, 184), (176, 192)): sh.ellipse_r(x, y, 3, 2, "z")
    sun(sh, 172, 28, 12)
    for x, y, rr in ((40, 60, 3), (48, 46, 2.4), (44, 34, 2)): sh.circle_r(x, y, rr, "-")
    sh.region("M70 150C66 106 98 74 140 76C172 80 186 116 172 152C150 166 96 166 70 150Z", "o")
    sh.line("M150 94C134 92 124 110 138 120C150 126 160 112 150 104C144 100 138 108 144 112")
    sh.line("M168 104Q150 132 112 140M176 128Q150 150 108 156M128 84Q106 98 96 124")
    sh.ellipse_r(88, 142, 18, 14, "w")
    for x1, y1, x2, y2 in ((68, 150, 46, 172), (76, 154, 62, 176), (84, 156, 80, 178)):
        limb(sh, x1, y1, x2, y2, "r", 6)
    sh.line("M70 128L64 106M80 127L84 104")
    for x, y in ((64, 102), (84, 100)): sh.circle_r(x, y, 6.5, "-"); eye(sh, x, y, 3)
    sh.region("M56 146C54 132 66 124 80 126C94 130 96 146 86 154C76 158 60 156 56 146Z", "r")
    smile(sh, 72, 141, 4)
    limb(sh, 62, 142, 44, 138, "r", 8)
    sh.region("M38 134C30 126 20 124 14 128C20 132 28 136 34 140Z", "r")
    sh.region("M34 142C26 146 18 150 12 150C18 156 30 154 38 148Z", "r")
    sh.ellipse_r(40, 140, 10, 8, "r")

# ---------- dieren van de wereld ----------
def tapir(sh):
    grass(sh, 176, "l")
    sun(sh, 172, 28, 12)
    for x, y, w, h in ((14, 60, 12, 34), (186, 70, 12, 30), (178, 116, 10, 24)): sh.region(leaf_path(x, y, w, h), "g")
    sh.line("M14 94V180M186 100V176")
    for x1, x2, w in ((66, 64, 14), (86, 88, 14), (134, 132, 14), (152, 156, 14)):
        limb(sh, x1, 124, x2, 172, "x", w); sh.rect_r(x2 - 7, 170, 14, 6, "z", 2)
    sh.region("M100 71C76 70 54 78 50 96C46 116 54 136 72 136H104C100 114 98 92 100 71Z", "x")
    sh.region("M100 71C130 70 162 80 168 104C170 124 156 136 130 136H104C100 114 98 92 100 71Z", "-")
    sh.line("M168 104Q176 106 176 114")
    sh.ellipse_r(58, 74, 8, 11, "x"); sh.region("M52 66Q58 60 64 66Q58 64 52 66Z", "-")
    sh.region("M60 82C44 74 28 82 24 96C20 108 14 114 8 122L14 128C22 122 30 120 40 120C54 118 66 108 66 96Z", "x")
    sh.circle_r(40, 92, 4, "-"); eye(sh, 39, 92, 2)
    sh.line("M28 112Q34 116 40 114")

def okapi(sh):
    grass(sh, 180, "l")
    for x, y, w, h in ((176, 40, 14, 36), (190, 90, 10, 26), (12, 120, 10, 30)): sh.region(leaf_path(x, y, w, h), "g")
    sh.line("M176 76V184M12 150V184")
    for x1, x2 in ((70, 68), (84, 86), (134, 134), (150, 152)):
        limb(sh, x1, 112, x2, 176, "-", 12); sh.rect_r(x2 - 6, 174, 12, 6, "x", 2)
        if x1 > 100:
            for y in range(122, 160, 9): sh.rect_r(x2 - 6 - (x1 - x2) * 0, y, 12, 4, "w")
        else:
            for y in range(122, 140, 8): sh.rect_r(min(x1, x2) - 6, y, 12 + abs(x1 - x2), 3.5, "w")
    sh.region("M60 92C64 74 86 70 110 72C136 74 156 80 160 96C164 112 152 122 132 122H76C64 122 58 108 60 92Z", "w")
    for k in range(3):
        x = 140 + k * 7
        sh.region(f"M{x} {84 + k}Q{x - 8} 98 {x} {114 - k}L{x + 3} {113 - k}Q{x - 4} 98 {x + 3} {85 + k}Z", "-")
    sh.line("M160 94Q168 110 164 130"); sh.region("M160 128C160 136 168 136 168 128L164 124Z", "x")
    sh.region("M78 84C68 66 62 52 56 40L72 32C78 48 88 64 100 76Z", "w")
    sh.region("M76 30C84 26 92 30 90 36C86 38 80 36 76 30Z", "w")
    sh.line("M64 30L62 20M70 30L70 20"); sh.circle_r(62, 19, 2.5, "w"); sh.circle_r(70, 19, 2.5, "w")
    sh.region("M54 28C64 26 74 32 74 40C72 50 54 58 40 66C30 70 22 66 24 58C28 48 46 36 54 28Z", "-")
    sh.circle_r(56, 40, 3.5, "-"); eye(sh, 56, 40, 1.8); sh.dot(29, 60, 1.4)
    sh.line("M26 66Q32 66 36 62")

def wombat(sh):
    grass(sh, 168, "l")
    sun(sh, 30, 30, 13)
    sh.region("M134 172C134 132 158 110 180 110C196 110 204 120 204 130V172Z", "w")
    sh.region("M150 172C150 148 162 136 176 136C190 136 200 148 200 172Z", "x")
    for x1, x2 in ((52, 50), (76, 76), (122, 122), (140, 142)):
        limb(sh, x1, 150, x2, 170, "z", 14)
    sh.region("M30 146C24 108 60 84 100 86C140 88 160 108 160 138C160 156 150 164 132 164H52C38 164 32 158 30 146Z", "z")
    sh.line("M100 98Q118 100 132 112M112 120Q126 124 136 136")
    for x in (42, 66): sh.region(f"M{x - 7} 96C{x - 8} 84 {x + 2} 80 {x + 7} 88Z", "z")
    sh.circle_r(52, 114, 24, "z")
    sh.ellipse_r(34, 122, 10, 8, "x")
    eye(sh, 44, 106, 2.6); eye(sh, 62, 108, 2.6)
    sh.line("M36 132Q42 136 48 132")
    sh.region(leaf_path(110, 182, 8, 10), "g"); sh.region(leaf_path(96, 186, 6, 8), "g")

def ringstaartmaki(sh):
    sun(sh, 30, 30, 12)
    for x, y, w, h in ((176, 40, 12, 28), (150, 60, 9, 20), (40, 150, 10, 26)): sh.region(leaf_path(x, y, w, h), "g")
    sh.line("M164 70L176 64M40 176V190")
    # staart met ringen
    pts_c = []
    for i in range(29):
        t = i / 28
        pts_c.append((116 + 16 * math.sin(t * math.pi * 1.3), 106 + t * 82))
    lft, rgt = band(pts_c, [12] * len(pts_c))
    for i in range(0, 28, 2):
        code = "x" if (i // 2) % 2 else "-"
        sh.poly_r([lft[i], lft[i + 2], rgt[i + 2], rgt[i]], code)
    ex, ey = pts_c[-1]; sh.circle_r(ex, ey, 6, "x")
    sh.region("M0 122L200 98L200 110L0 134Z", "w"); sh.line("M30 124L60 118M130 110L170 104")
    sh.ellipse_r(96, 86, 22, 26, "z")
    sh.ellipse_r(96, 90, 12, 17, "-")
    limb(sh, 80, 72, 70, 108, "z", 8); limb(sh, 112, 72, 124, 104, "z", 8)
    sh.ellipse_r(68, 112, 6, 4, "x"); sh.ellipse_r(126, 106, 6, 4, "x")
    sh.ellipse_r(84, 112, 7, 4.5, "x"); sh.ellipse_r(106, 110, 7, 4.5, "x")
    for x in (80, 112):
        d = -1 if x < 96 else 1
        sh.region(f"M{x} 46L{x + 14 * d} 28L{x + 4 * d} 52Z", "z")
    sh.circle_r(96, 52, 18, "z")
    sh.region("M80 48C84 40 108 40 112 48C114 58 106 68 96 70C86 68 78 58 80 48Z", "-")
    for x in (88, 104):
        sh.ellipse_r(x, 52, 6, 5, "x"); sh.circle_r(x, 52, 3.5, "o"); eye(sh, x, 52, 1.8)
    sh.ellipse_r(96, 64, 4, 3, "x")

def kolibrie(sh):
    sh.line("M22 200C10 160 8 120 16 82")
    sh.region(leaf_path(28, 150, 6, 14), "g"); sh.line("M14 156L24 150")
    sh.region(leaf_path(6, 120, 5, 12), "g")
    sh.region("M14 77L36 71C38 62 48 58 51 65C55 70 55 90 51 95C48 102 38 98 36 89L14 84Z", "m")
    sh.ellipse_r(50, 80, 4, 14, "k")
    sh.line("M20 78L34 74M20 83L34 87", "l", "stroke-width:.9")
    sh.region(leaf_path(150, 176, 8, 14), "g"); sh.region(leaf_path(196, 150, 6, 12), "g")
    flower(sh, 176, 170, 9, "o", "y"); sh.line("M176 179V200M150 190V200")
    sh.region("M108 76C104 50 112 26 132 12C134 32 128 56 118 78Z", "t")
    sh.line("M114 70L126 26M118 74L130 40", "l", "stroke-width:.9")
    sh.region("M140 112L172 120L180 136L166 128L160 140Z", "g")
    sh.region("M78 86C84 72 102 68 118 76C134 84 140 100 146 114C136 122 120 124 100 116C84 108 76 98 78 86Z", "g")
    sh.region("M86 98C98 110 120 118 140 116C126 124 102 122 90 112Z", "-")
    sh.region("M116 82C126 58 146 42 168 38C158 58 142 76 124 90Z", "t")
    sh.line("M124 84L158 46M128 88L162 56", "l", "stroke-width:.9")
    for y in (30, 40): sh.line(f"M{176} {y}h10")
    sh.circle_r(86, 80, 13, "g")
    sh.region("M76 88C80 96 90 98 98 92C94 100 82 102 76 94Z", "r")
    sh.circle_r(83, 77, 3.5, "-"); eye(sh, 82, 77, 2)
    sh.region("M74 77L54 80L75 83Z", "x")

def poolvos(sh):
    sh.rect_r(0, 0, 200, 150, "b")
    sh.region(moon_path(168, 30, 13), "y")
    sh.region("M0 150Q60 136 120 146T200 140V200H0Z", "-")
    for x, y in ((30, 30), (34, 74), (168, 76), (186, 116), (16, 118), (110, 20)):
        for k in range(3):
            a = math.radians(k * 60)
            sh.seg(x - 4 * math.cos(a), y - 4 * math.sin(a), x + 4 * math.cos(a), y + 4 * math.sin(a))
    sh.region("M128 160C160 150 180 168 162 184C142 194 92 192 64 182C80 176 110 178 128 172Z", "-")
    sh.region("M70 176C62 140 72 104 100 100C128 104 138 140 130 176Z", "-")
    sh.line("M90 120Q100 126 110 120M92 134Q100 138 108 134")
    sh.ellipse_r(88, 178, 9, 5, "-"); sh.ellipse_r(112, 178, 9, 5, "-")
    for x in (72, 128):
        d = 1 if x < 100 else -1
        sh.region(f"M{x} 62L{x + 2 * d} 36L{x + 18 * d} 50Z", "-")
        sh.region(f"M{x + 4 * d} 56L{x + 5 * d} 44L{x + 13 * d} 51Z", "k")
    sh.region("M64 70C64 52 82 44 100 44C118 44 136 52 136 70C138 82 124 92 112 100L100 104L88 100C76 92 62 82 64 70Z", "-")
    sh.line("M66 76L60 82L70 82M134 76L140 82L130 82")
    for x in (86, 114): sh.ellipse_r(x, 70, 4, 5, "-"); eye(sh, x, 71, 2.6)
    sh.ellipse_r(100, 88, 5, 4, "x"); sh.line("M100 92V96M94 98Q100 101 106 98")

def sneeuwuil(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region(moon_path(30, 30, 15), "y")
    for x, y in ((170, 24), (140, 14), (186, 60), (60, 16), (16, 90)): sh.region(star_path(x, y, 4, 1.8), "y")
    sh.region("M0 200V176Q50 166 100 172T200 168V200Z", "-")
    for x, h in ((20, 120), (44, 136), (160, 126), (184, 112)):
        sh.region(f"M{x} {h}L{x + 16} {h + 46}H{x - 16}Z", "g")
        sh.region(f"M{x} {h}L{x + 7} {h + 20}Q{x} {h + 16} {x - 7} {h + 20}Z", "-")
        sh.rect_r(x - 3, h + 46, 6, 10, "w")
    def wing():
        sh.region("M86 82C64 60 32 54 4 62C12 70 12 76 8 82C18 82 22 90 18 96C28 94 34 100 32 106C42 102 50 106 52 112C62 104 76 98 88 102Z", "-")
        for x, y in ((24, 70), (40, 74), (56, 80), (34, 86), (50, 92), (66, 90)): sh.region(f"M{x - 4} {y}Q{x} {y + 4} {x + 4} {y}", "x")
        sh.line("M28 66Q60 70 84 88", "l", "stroke-width:.9")
    mirror(sh, wing)
    sh.line("M88 132L84 142M94 134L92 144M106 134L108 144M112 132L116 142")
    sh.ellipse_r(100, 106, 20, 28, "-")
    for x, y in ((92, 104), (104, 100), (98, 114), (110, 116), (90, 122), (102, 126)): sh.line(f"M{x - 3} {y}Q{x} {y + 3} {x + 3} {y}")
    sh.circle_r(100, 70, 20, "-")
    sh.line("M100 66C90 56 80 62 82 74M100 66C110 56 120 62 118 74")
    for x in (91, 109): sh.circle_r(x, 68, 6, "y"); eye(sh, x, 68, 3)
    sh.region("M96 76L104 76L100 84Z", "x")

def stokstaartje(sh, x, base, h=1.0, look=0):
    s = h
    limb(sh, x + 8 * s, base - 14 * s, x + 20 * s, base + 1 * s, "w", 5 * s)
    sh.ellipse_r(x - 7 * s, base, 8 * s, 4 * s, "w"); sh.ellipse_r(x + 7 * s, base, 8 * s, 4 * s, "w")
    sh.region(f"M{f(x - 13 * s)} {f(base)}C{f(x - 17 * s)} {f(base - 30 * s)} {f(x - 12 * s)} {f(base - 58 * s)} {f(x - 6 * s)} {f(base - 68 * s)}H{f(x + 6 * s)}C{f(x + 12 * s)} {f(base - 58 * s)} {f(x + 17 * s)} {f(base - 30 * s)} {f(x + 13 * s)} {f(base)}Z", "w")
    sh.region(f"M{f(x - 7 * s)} {f(base - 4 * s)}C{f(x - 9 * s)} {f(base - 26 * s)} {f(x - 6 * s)} {f(base - 46 * s)} {f(x)} {f(base - 54 * s)}C{f(x + 6 * s)} {f(base - 46 * s)} {f(x + 9 * s)} {f(base - 26 * s)} {f(x + 7 * s)} {f(base - 4 * s)}Z", "-")
    limb(sh, x - 10 * s, base - 56 * s, x - 6 * s, base - 42 * s, "w", 6 * s)
    limb(sh, x + 10 * s, base - 56 * s, x + 6 * s, base - 42 * s, "w", 6 * s)
    hx, hy = x + look * 4 * s, base - 78 * s
    sh.circle_r(hx - 10 * s, hy - 4 * s, 3.5 * s, "x"); sh.circle_r(hx + 10 * s, hy - 4 * s, 3.5 * s, "x")
    sh.region(f"M{f(hx - 11 * s)} {f(hy - 2 * s)}C{f(hx - 11 * s)} {f(hy - 12 * s)} {f(hx + 11 * s)} {f(hy - 12 * s)} {f(hx + 11 * s)} {f(hy - 2 * s)}C{f(hx + 10 * s)} {f(hy + 6 * s)} {f(hx + 4 * s)} {f(hy + 12 * s)} {f(hx)} {f(hy + 14 * s)}C{f(hx - 4 * s)} {f(hy + 12 * s)} {f(hx - 10 * s)} {f(hy + 6 * s)} {f(hx - 11 * s)} {f(hy - 2 * s)}Z", "w")
    for d in (-1, 1):
        sh.ellipse_r(hx + d * 5 * s + look * 1.5 * s, hy - 1 * s, 3.4 * s, 4 * s, "x")
        sh.circle_r(hx + d * 5 * s + look * 1.5 * s, hy - 1.5 * s, 1.3 * s, "-")
    sh.ellipse_r(hx + look * 2 * s, hy + 11 * s, 2.4 * s, 1.8 * s, "x")

def stokstaartjes(sh):
    sun(sh, 160, 34, 16)
    sh.region("M0 200V172Q40 160 100 160T200 170V200Z", "y")
    sh.region("M118 172C130 150 168 146 186 172Z", "o"); sh.region("M140 172C142 160 160 158 164 172Z", "x")
    sh.line("M20 172C18 150 26 134 22 120M20 150L10 140M22 136L32 128")
    for x, y in ((188, 150), (178, 156)): sh.region(leaf_path(x, y, 5, 12), "g")
    sh.line("M184 172V160")
    stokstaartje(sh, 50, 168, 1.15, -1)
    stokstaartje(sh, 100, 164, 1.3, 0)
    stokstaartje(sh, 148, 170, 1.0, 1)

def bizon(sh):
    grass(sh, 178, "y")
    sh.region("M0 120L40 86L70 110L110 78L150 108L180 90L200 104V140H0Z", "z")
    sh.region("M110 78L122 88L112 90L104 84Z", "-")
    sun(sh, 170, 32, 13)
    sh.rect_r(0, 140, 200, 40, "y")
    for x in (6, 178): sh.line(f"M{x} 176Q{x + 2} 166 {x + 6} 160M{x + 4} 176Q{x + 4} 168 {x} 162")
    sh.line("M164 104Q178 110 178 128"); sh.region("M174 126C172 136 184 136 182 126L178 122Z", "w")
    for x1, x2, w in ((76, 74, 15), (98, 100, 15), (140, 138, 12), (156, 160, 12)):
        limb(sh, x1, 118, x2, 172, "w", w); sh.rect_r(x2 - w / 2, 170, w, 6, "x", 2)
    sh.region("M100 84C122 80 152 82 166 96C172 110 166 126 148 130H102Z", "w")
    sh.region("M34 134L32 154L38 148L42 158L47 148L52 154L56 134Z", "w")
    sh.region("M72 84C52 78 34 90 30 110C28 124 34 138 46 142C58 144 68 132 72 118Z", "w")
    sh.region("M50 88C42 84 38 74 44 66C44 74 48 80 56 84Z", "z")
    edge = [(84, 132), (72, 116), (66, 96), (70, 74), (84, 58), (102, 52)]
    zz = []
    for i in range(len(edge) - 1):
        (x1, y1), (x2, y2) = edge[i], edge[i + 1]
        for k in range(3):
            t = k / 3; x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy)
            o = -4 if k % 2 else 0
            zz.append((x + dy / d * o, y - dx / d * o))
    zz.append(edge[-1])
    d = "M116 132L" + " L".join(f"{f(x)} {f(y)}" for x, y in zz) + "C118 54 126 72 126 92C126 110 122 124 116 132Z"
    sh.region(d, "w")
    for x, y in ((90, 66), (104, 62), (112, 78), (84, 84), (100, 96), (110, 112), (82, 104)): sh.line(f"M{x} {y}q4 6 0 12")
    sh.line("M44 86q-4 6 0 10M56 84q-4 6 0 10M64 90q-4 6 0 10")
    sh.circle_r(44, 108, 3.5, "-"); eye(sh, 43, 108, 1.8); sh.dot(34, 130, 1.6)
    sh.line("M36 136Q40 138 44 135")

# ---------- dierenfamilies ----------
def schaap_met_lam(sh):
    grass(sh, 176, "l")
    sun(sh, 30, 30, 13)
    sh.region(cloud_path(150, 34, 16), "-")
    for x in (58, 74, 100, 114): limb(sh, x, 130, x, 172, "x", 9)
    wool(sh, 84, 110, 50, 32, 12, "-")
    sh.ellipse_r(126, 82, 8, 4, "x")
    sh.ellipse_r(142, 92, 15, 19, "z")
    sh.ellipse_r(158, 84, 8, 4, "x")
    eye(sh, 137, 88, 2.4); eye(sh, 148, 88, 2.4); sh.line("M138 102Q142 106 146 102")
    for x in (152, 160, 172, 180): limb(sh, x, 158, x, 178, "x", 6)
    wool(sh, 166, 150, 24, 15, 9, "-")
    sh.ellipse_r(148, 134, 5, 3, "x")
    sh.ellipse_r(140, 142, 9, 11, "z")
    eye(sh, 137, 140, 1.8); eye(sh, 144, 140, 1.8); sh.line("M138 148Q141 150 144 148")
    flower(sh, 20, 170, 6, "m"); flower(sh, 192, 186, 5, "y", "o")

def olifant_met_kalf(sh):
    grass(sh, 180, "y")
    sun(sh, 30, 30, 13)
    sh.region(cloud_path(110, 30, 16), "-")
    for x in (90, 110, 140, 158): limb(sh, x, 128, x, 178, "z", 18)
    for x in (98, 118, 148, 166): sh.line(f"M{x - 13} 178h4M{x - 8} 178h4")
    sh.region("M76 100C76 70 100 56 130 58C150 60 160 72 162 90C164 116 154 136 130 138H92C80 136 76 120 76 100Z", "z")
    sh.line("M78 96Q70 104 74 118"); sh.region("M70 116C66 122 72 126 76 122L74 116Z", "x")
    sh.region("M150 66C170 62 186 74 186 92C186 104 182 112 184 130C186 148 190 160 196 166L188 172C178 162 172 146 170 132C166 120 156 114 150 104Z", "z")
    sh.region("M152 68C134 66 124 84 128 100C132 112 146 116 158 108C162 96 160 80 152 68Z", "k")
    eye(sh, 172, 86, 2.4)
    sh.line("M176 102Q174 110 168 112")
    # kalfje dat de staart vasthoudt
    for x in (22, 32, 44, 54): limb(sh, x, 148, x, 180, "z", 10)
    sh.region("M12 138C12 122 24 114 38 114C52 114 60 122 60 136C60 148 54 156 44 156H24C16 156 12 148 12 138Z", "z")
    sh.line("M14 132Q8 138 10 146")
    limb(sh, 66, 132, 72, 120, "z", 6)
    sh.circle_r(58, 126, 13, "z")
    sh.ellipse_r(52, 126, 7, 10, "k")
    eye(sh, 63, 122, 2)

# ---------- natuurtaferelen ----------
def frog(sh, x, y, s=1.0):
    sh.ellipse_r(x - 14 * s, y + 10 * s, 10 * s, 5 * s, "g"); sh.ellipse_r(x + 14 * s, y + 10 * s, 10 * s, 5 * s, "g")
    sh.ellipse_r(x, y, 18 * s, 14 * s, "l")
    sh.ellipse_r(x, y + 3 * s, 10 * s, 8 * s, "-")
    for d in (-1, 1):
        sh.circle_r(x + d * 10 * s, y - 13 * s, 7 * s, "l"); sh.circle_r(x + d * 10 * s, y - 13 * s, 4 * s, "-"); eye(sh, x + d * 10 * s, y - 13 * s, 2.2 * s)
    sh.line(f"M{f(x - 9 * s)} {f(y - 4 * s)}Q{f(x)} {f(y + 2 * s)} {f(x + 9 * s)} {f(y - 4 * s)}")
    sh.ellipse_r(x - 8 * s, y + 13 * s, 5 * s, 3 * s, "g"); sh.ellipse_r(x + 8 * s, y + 13 * s, 5 * s, 3 * s, "g")

def vijver_met_kikkers(sh):
    sh.rect_r(0, 0, 200, 200, "l")
    sun(sh, 30, 28, 12)
    sh.region("M10 120C10 90 60 82 100 84C150 86 194 96 194 128C194 166 150 186 100 186C50 186 10 160 10 120Z", "b")
    for x, h in ((170, 40), (182, 54), (192, 70)):
        sh.line(f"M{x} 100V{h}"); sh.ellipse_r(x, h - 8, 4, 11, "w")
    sh.region(leaf_path(178, 80, 6, 24), "g")
    lilypad(sh, 70, 140, 34, 14)
    lilypad(sh, 150, 110, 22, 9); flower(sh, 150, 104, 6, "m", "y")
    lilypad(sh, 140, 162, 18, 7)
    frog(sh, 70, 124, 1.2)
    # kikker die uit het water kijkt
    for d in (-1, 1): sh.circle_r(124 + d * 8, 136, 6, "l"); sh.circle_r(124 + d * 8, 136, 3.5, "-"); eye(sh, 124 + d * 8, 136, 2)
    sh.region("M110 142Q124 134 138 142Q124 146 110 142Z", "l")
    sh.line("M104 146Q124 152 144 146")
    waves(sh, 106, 2, 30, 50, 18)
    # libelle
    for x in (118, 132): sh.ellipse_r(x, 43, 6, 3.5, "-"); sh.ellipse_r(x, 57, 6, 3.5, "-")
    sh.line("M112 50H150", "l", "stroke-width:2.4"); sh.circle_r(110, 50, 3.5, "t")
    flower(sh, 20, 180, 5, "y", "o"); flower(sh, 186, 186, 5, "m")

def bloesemboom(sh):
    grass(sh, 178, "l")
    sh.region("M88 182C92 160 94 130 90 110L80 96L86 92L96 104L100 86L108 88L106 108L120 96L124 102L110 116C106 136 108 160 116 182Z", "w")
    wool(sh, 100, 70, 74, 50, 14, "k")
    for x, y in ((60, 54), (96, 40), (138, 52), (74, 84), (118, 78), (150, 88), (46, 92)):
        flower(sh, x, y, 7, "m", "y")
    for x, y in ((40, 140), (150, 130), (30, 166), (130, 156)):
        sh.region(heart_path(x, y, 4), "m")
    # vogeltje in het gras
    sh.region("M176 168L190 160L188 170Z", "b")
    sh.ellipse_r(170, 172, 11, 7.5, "b"); sh.circle_r(160, 164, 6, "b")
    sh.region("M155 163L148 165L155 167Z", "y"); eye(sh, 159, 163, 1.4)
    sh.line("M168 180V184M174 180V184")
    sun(sh, 182, 20, 10, False)

def mushroom(sh, x, base, h, w, sw, cap="r", stem="-", spots=True, ch=None):
    ch = ch or w * .9
    cy = base - h
    sh.region(f"M{f(x - sw)} {f(base)}C{f(x - sw * 1.2)} {f(base - h * .5)} {f(x - sw * .8)} {f(cy)} {f(x - sw * .7)} {f(cy)}H{f(x + sw * .7)}C{f(x + sw * .8)} {f(cy)} {f(x + sw * 1.2)} {f(base - h * .5)} {f(x + sw)} {f(base)}Z", stem)
    sh.region(f"M{f(x - w)} {f(cy)}C{f(x - w)} {f(cy - ch * 1.3)} {f(x + w)} {f(cy - ch * 1.3)} {f(x + w)} {f(cy)}Q{f(x)} {f(cy + ch * .25)} {f(x - w)} {f(cy)}Z", cap)
    if spots:
        for dx, dy, r in ((-.5, -.35, .14), (.1, -.65, .16), (.55, -.3, .12), (-.1, -.25, .1)):
            sh.ellipse_r(x + dx * w, cy + dy * ch, r * w, r * w * .8, "-")

def fern(sh, x, y, length, ang, n=8, code="g"):
    a = math.radians(ang)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a)
    mx, my = (x + ex) / 2 + 6 * math.sin(a), (y + ey) / 2 - 6 * math.cos(a)
    sh.line(f"M{f(x)} {f(y)}Q{f(mx)} {f(my)} {f(ex)} {f(ey)}")
    for i in range(1, n + 1):
        t = i / (n + 1)
        px = (1 - t) ** 2 * x + 2 * (1 - t) * t * mx + t * t * ex
        py = (1 - t) ** 2 * y + 2 * (1 - t) * t * my + t * t * ey
        L = (1 - t) * 12 + 3
        for side in (-1, 1):
            b = a + side * math.radians(60)
            cx, cy = px + L / 2 * math.cos(b), py + L / 2 * math.sin(b)
            sh.raw(f'<g transform="rotate({f(math.degrees(b) + 90)} {f(cx)} {f(cy)})">')
            sh.region(leaf_path(cx, cy, L * .28, L / 2), code)
            sh.raw("</g>")

def paddenstoelen_in_het_bos(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    for x, w in ((66, 16), (128, 12)):
        sh.rect_r(x - w / 2, 0, w, 146, "z")
        sh.line(f"M{x - 2} 30q3 6 0 12M{x + 2} 80q-3 6 0 12")
    sh.region("M0 0H30V150C30 160 36 166 44 170H0Z", "w")
    sh.region("M200 0H174V146C174 156 166 164 156 168H200Z", "w")
    for y in (20, 48, 80, 112): sh.line(f"M{8 + (y % 7)} {y}q4 8 0 16M{186 - (y % 5)} {y + 6}q-4 8 0 16")
    sh.region("M0 200V150Q50 140 100 146T200 144V200Z", "w")
    sh.line("M100 158q6 4 12 0M150 166q6 4 12 0")
    fern(sh, 22, 162, 54, -70); fern(sh, 30, 164, 44, -40, 6)
    fern(sh, 180, 158, 50, -110); fern(sh, 172, 162, 40, -140, 6)
    sh.region("M134 178V146C134 138 170 138 170 146V178Z", "w"); sh.ellipse_r(152, 146, 18, 6, "o")
    sh.circle_line(152, 146, 3.5); sh.line("M140 152V172M162 154V174")
    for x, hh in ((140, 14), (150, 20), (162, 12)):
        mushroom(sh, x, 142, hh, 7, 2.4, "o", "-", False)
    mushroom(sh, 70, 192, 40, 32, 9, "r", "-", True)
    sh.region("M60 172Q70 176 80 172L81 177Q70 181 59 177Z", "-")
    mushroom(sh, 116, 194, 26, 22, 10, "w", "y", False)
    mushroom(sh, 30, 194, 14, 12, 4, "m", "-", True)
    sh.region("M170 194C170 188 180 186 190 188C194 190 196 194 192 196H172Z", "k")
    sh.circle_r(180, 186, 8, "o"); sh.line("M180 186m-4 0a4 4 0 1 1 4 4")
    sh.line("M190 188L192 180M193 190L198 184")
    for x, y, c in ((96, 176, "o"), (146, 192, "y"), (16, 184, "r")):
        sh.region(leaf_path(x, y, 5, 8), c)
    for x, y in ((132, 184), (98, 190)):
        sh.ellipse_r(x, y + 3, 4, 3.5, "w"); sh.region(f"M{x - 5} {y + 1}Q{x} {y - 5} {x + 5} {y + 1}Z", "w"); sh.line(f"M{x} {y - 3}v-3")
    for x, y, c, rot in ((48, 176, "o", 40), (154, 186, "r", -30), (88, 170, "y", 70), (190, 172, "o", 20)):
        sh.raw(f'<g transform="rotate({rot} {x} {y})">'); sh.region(leaf_path(x, y, 5, 8), c); sh.line(f"M{x} {y - 8}V{y + 8}", "l", "stroke-width:.8"); sh.raw("</g>")
    for x in (52, 102, 124): sh.line(f"M{x} 160l-3 -8M{x + 3} 160v-9M{x + 6} 160l3 -8")

def zonsopkomst_bij_zee(sh):
    sh.rect_r(0, 0, 200, 120, "k")
    for k in range(9):
        a = math.radians(180 + 10 + k * 20)
        cx, cy = 100, 120
        p1 = (cx + 34 * math.cos(a - .08), cy + 34 * math.sin(a - .08))
        p2 = (cx + 34 * math.cos(a + .08), cy + 34 * math.sin(a + .08))
        tip = (cx + 56 * math.cos(a), cy + 56 * math.sin(a))
        sh.poly_r([p1, tip, p2], "o")
    sh.region("M70 120A30 30 0 0 1 130 120Z", "y")
    sh.region(cloud_path(36, 50, 16), "-"); sh.region(cloud_path(166, 36, 14), "-")
    bird_m(sh, 150, 70, 7); bird_m(sh, 168, 80, 5)
    sh.rect_r(0, 120, 200, 80, "b")
    for y, w in ((128, 26), (138, 20), (148, 14)):
        sh.rect_r(100 - w, y, 2 * w, 3, "y", 1.5)
    waves(sh, 160, 4, 10, 50, 20)
    # zeilbootje
    sh.region("M150 112H186L180 120H156Z", "r"); sh.line("M168 112V84"); sh.region("M170 86L184 110H170Z", "-"); sh.region("M166 90L154 110H166Z", "-")
    # strand
    sh.region("M0 200V168Q50 160 100 172T200 176V200Z", "y")
    sh.region("M40 190C40 180 52 176 58 186Z", "m"); sh.line("M46 189L46 183M51 189L52 182")
    sh.region(star_path(150, 188, 7, 3), "o")

def sterrenhemel(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region(moon_path(164, 34, 16), "y")
    # vallende ster met staart
    sh.region("M40 26L118 62L114 70Z", "y")
    sh.region("M44 36L112 70L110 74Z", "o")
    sh.region(star_path(120, 70, 12, 5), "y")
    # sterrenbeeld (steelpan)
    cons = [(30, 96), (50, 92), (66, 100), (82, 106), (88, 124), (114, 126), (110, 106)]
    sh.line("M" + " L".join(f"{x} {y}" for x, y in cons + [(82, 106)]), "l", "stroke-dasharray:2 3")
    for x, y in cons: sh.region(star_path(x, y, 4.5, 2), "y")
    for x, y in ((150, 80), (180, 100), (140, 120), (20, 130), (60, 60), (100, 20), (186, 66), (16, 60), (170, 140)):
        sh.region(star_path(x, y, 3, 1.3), "y")
    for x, y in ((90, 46), (130, 40), (40, 150), (156, 108), (8, 20), (194, 120), (76, 140)): sh.dot(x, y, 1.2)
    sh.region("M0 200V160Q40 140 90 152T200 146V200Z", "g")
    sh.region("M150 150L162 118L174 150Z", "g"); sh.region("M156 136L162 104L168 136Z", "g"); sh.rect_r(159, 150, 6, 8, "w")
    sh.region("M20 160L32 126L44 160Z", "g"); sh.rect_r(29, 160, 6, 8, "w")
    # tentje
    sh.region("M70 182L96 150L122 182Z", "o"); sh.region("M90 182L96 164L102 182Z", "y")


def kameleon(sh):
    sun(sh, 30, 28, 12)
    for x, y, w, h in ((170, 180, 8, 16), (110, 176, 7, 13), (14, 170, 7, 14)): sh.region(leaf_path(x, y, w, h), "g")
    sh.region("M0 160L200 140V150L0 170Z", "w"); sh.line("M40 160L60 158M140 148L170 146")
    cx, cy = 30, 124
    center = []
    for i in range(41):
        t = i / 40
        a = math.radians(-25 + t * 470)
        r = 24 - 18 * t
        center.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    center.insert(0, (58, 110))
    lft, rgt = band(center, [14] + [14 - 10 * i / 40 for i in range(41)])
    sh.poly_r(lft + rgt[::-1], "g")
    limb(sh, 72, 116, 66, 153, "g", 8); sh.ellipse_r(66, 154, 7, 4, "g")
    limb(sh, 124, 116, 130, 147, "g", 8); sh.ellipse_r(130, 148, 7, 4, "g")
    sh.region("M50 108C50 84 72 70 100 70C122 70 136 80 144 92C148 106 140 120 124 122H70C58 122 50 116 50 108Z", "g")
    sh.region("M56 112C70 104 110 102 140 108C134 118 128 122 124 122H70C62 122 58 118 56 112Z", "y")
    for x, y, r in ((72, 88, 3), (88, 94, 2.4), (104, 86, 3), (120, 96, 2.4), (62, 98, 2.4), (96, 80, 2)): sh.circle_r(x, y, r, "l")
    sh.line("M60 76L64 72L68 75L72 71L76 74L80 70L84 73L88 69L92 72L96 68L100 71")
    sh.region("M136 86C144 66 162 60 172 66L180 90C178 100 168 106 152 106C142 104 136 96 136 86Z", "g")
    sh.line("M146 96Q162 100 178 92")
    sh.circle_r(156, 82, 9, "l"); sh.circle_line(156, 82, 5); eye(sh, 157, 82, 2.4)
    sh.line("M178 92Q192 70 186 46", "l", "stroke-width:3"); sh.circle_r(186, 44, 4, "m")
    sh.ellipse_r(179, 26, 6, 3.5, "-"); sh.ellipse_r(193, 26, 6, 3.5, "-"); sh.ellipse_r(186, 32, 3.5, 5, "x")

PLATES = [
    ("cavia", "Cavia met een slablaadje", "dieren", "2-4", 1, cavia),
    ("goudvis-in-kom", "Goudvis in een kom", "dieren", "2-4", 1, goudvis_in_kom),
    ("parkiet", "Parkiet op een schommeltje", "dieren", "4-6", 2, parkiet),
    ("merel", "Merel met een wormpje", "dieren", "4-6", 2, merel),
    ("mus", "Mus op het hek", "dieren", "2-4", 1, mus),
    ("meeuw", "Meeuw op een paal", "zee", "4-6", 2, meeuw),
    ("reiger", "Reiger in het water", "dieren", "6-9", 2, reiger),
    ("libel", "Libel boven de vijver", "dieren", "4-6", 2, libel),
    ("sprinkhaan", "Sprinkhaan", "dieren", "6-9", 3, sprinkhaan),
    ("hommel", "Hommel bij een bloem", "dieren", "2-4", 1, hommel),
    ("vuurvliegjes", "Vuurvliegjes in de nacht", "natuur", "4-6", 2, vuurvliegjes),
    ("zee-egel", "Zee-egel op de zeebodem", "zee", "4-6", 2, zee_egel),
    ("heremietkreeft", "Heremietkreeft in zijn schelp", "zee", "4-6", 2, heremietkreeft),
    ("tapir", "Tapir", "dieren", "6-9", 2, tapir),
    # ("okapi", "Okapi", "dieren", "6-9", 2, okapi),
    ("wombat", "Wombat bij zijn hol", "dieren", "4-6", 2, wombat),
    ("ringstaartmaki", "Ringstaartmaki op een tak", "dieren", "6-9", 2, ringstaartmaki),
    ("kolibrie", "Kolibrie bij een bloem", "dieren", "6-9", 2, kolibrie),
    ("poolvos", "Poolvos in de sneeuw", "dieren", "4-6", 2, poolvos),
    ("sneeuwuil", "Vliegende sneeuwuil", "dieren", "9+", 3, sneeuwuil),
    ("stokstaartjes", "Stokstaartjes op de uitkijk", "dieren", "6-9", 2, stokstaartjes),
    ("bizon", "Bizon op de prairie", "dieren", "6-9", 2, bizon),
    # ("kameleon", "Kameleon op een tak", "dieren", "9+", 3, kameleon),
    ("schaap-met-lam", "Schaap met lammetje", "boerderij", "2-4", 1, schaap_met_lam),
    ("olifant-met-kalf", "Olifant met kalfje", "dieren", "4-6", 2, olifant_met_kalf),
    ("vijver-met-kikkers", "Vijver met kikkers", "natuur", "4-6", 2, vijver_met_kikkers),
    ("bloesemboom", "Bloeiende boom", "natuur", "2-4", 1, bloesemboom),
    ("paddenstoelen-in-het-bos", "Paddenstoelen in het bos", "natuur", "9+", 3, paddenstoelen_in_het_bos),
    ("zonsopkomst-bij-zee", "Zonsopkomst bij de zee", "natuur", "4-6", 2, zonsopkomst_bij_zee),
    ("sterrenhemel-vallende-ster", "Sterrenhemel met een vallende ster", "natuur", "6-9", 2, sterrenhemel),
]

for slug, name, cat, age, diff, draw in PLATES:
    kp(slug, name, cat, age, diff, draw)
