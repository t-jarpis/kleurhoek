"""Batch 27a: nieuwe kleurplaten (eigen tekeningen, 200x200) in dunne categorieën: dino's, ruimte, sport en beroepen."""
import math, re, random
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from shapes import heart_path, star_path, moon_path, cloud_path, leaf_path, fish_path


# ---------- hulpjes ----------
def limb(sh, x1, y1, x2, y2, code, w=9):
    """Arm of been als balk met afgeronde uiteinden van (x1,y1) naar (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * w / 2, dx / d * w / 2
    r = w / 2
    sh.region(f"M{f(x1 + nx)} {f(y1 + ny)}L{f(x2 + nx)} {f(y2 + ny)}A{f(r)} {f(r)} 0 0 0 {f(x2 - nx)} {f(y2 - ny)}L{f(x1 - nx)} {f(y1 - ny)}A{f(r)} {f(r)} 0 0 0 {f(x1 + nx)} {f(y1 + ny)}Z", code)

def person(sh, cx, top, shirt="-", pants="-", hands=None, hair="w", legs=None, cap=None, shoes="x", face=True):
    """Staand kind/volwassene van voren. top = bovenkant hoofd. hands/legs = absolute posities."""
    hy = top + 15
    sl, sr = (cx - 13, hy + 24), (cx + 13, hy + 24)
    hl, hr = hands or ((cx - 22, hy + 52), (cx + 22, hy + 52))
    hip_l, hip_r = (cx - 8, hy + 54), (cx + 8, hy + 54)
    fl, fr = legs or ((cx - 8, hy + 86), (cx + 8, hy + 86))
    limb(sh, *hip_l, *fl, pants, 12); limb(sh, *hip_r, *fr, pants, 12)
    sh.ellipse_r(fl[0] - 3, fl[1] + 3, 8, 4.5, shoes); sh.ellipse_r(fr[0] + 3, fr[1] + 3, 8, 4.5, shoes)
    limb(sh, *sl, *hl, shirt, 10); limb(sh, *sr, *hr, shirt, 10)
    sh.region(f"M{cx - 17} {hy + 58}V{hy + 30}Q{cx - 17} {hy + 17} {cx - 5} {hy + 16}H{cx + 5}Q{cx + 17} {hy + 17} {cx + 17} {hy + 30}V{hy + 58}Z", shirt)
    sh.circle_r(cx, hy, 15, "-")
    if hair and not cap:
        sh.region(f"M{cx - 15} {hy}A15 15 0 0 1 {cx + 15} {hy}Q{cx + 8} {hy - 9} {cx - 2} {hy - 7}Q{cx - 10} {hy - 6} {cx - 15} {hy}Z", hair)
    if face:
        eye(sh, cx - 5, hy + 3, 1.8); eye(sh, cx + 5, hy + 3, 1.8); smile(sh, cx, hy + 8, 4)
    sh.circle_r(hl[0], hl[1], 4.5, "-"); sh.circle_r(hr[0], hr[1], 4.5, "-")
    return hy

def sparkle(sh, x, y, r=5, code="y"):
    sh.region(f"M{f(x)} {f(y - r)}Q{f(x + r * .2)} {f(y - r * .2)} {f(x + r)} {f(y)}Q{f(x + r * .2)} {f(y + r * .2)} {f(x)} {f(y + r)}Q{f(x - r * .2)} {f(y + r * .2)} {f(x - r)} {f(y)}Q{f(x - r * .2)} {f(y - r * .2)} {f(x)} {f(y - r)}Z", code)

def flower(sh, x, y, r=5, petal="m", heart="y"):
    for k in range(5):
        a = math.radians(k * 72 - 90)
        sh.circle_r(x + r * math.cos(a), y + r * math.sin(a), r * .7, petal)
    sh.circle_r(x, y, r * .55, heart)

def xf(d, ox, oy, s=1.0, mx=False):
    """Verschuif/schaal/spiegel een pad met alleen M/L/C/Q/Z (absolute coördinaten)."""
    out, isx = [], True
    for t in re.findall(r"[A-Za-z]|-?\d*\.?\d+", d):
        if t.isalpha(): out.append(t); isx = True; continue
        v = float(t)
        v = ox + (-v if mx else v) * s if isx else oy + v * s
        out.append(f(round(v, 1))); isx = not isx
    return " ".join(out)

def stars(sh, pts, r=5, code="y"):
    for x, y in pts: sh.region(star_path(x, y, r, r * .45), code)

def bone(sh, x1, y1, x2, y2, w=6, code="-"):
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); nx, ny = -dy / d, dx / d
    for x, y in ((x1, y1), (x2, y2)):
        sh.circle_r(x + nx * w * .45, y + ny * w * .45, w * .55, code); sh.circle_r(x - nx * w * .45, y - ny * w * .45, w * .55, code)
    limb(sh, x1, y1, x2, y2, code, w)

def footprint(sh, x, y, s=1.0, rot=0, code="z"):
    sh.raw(f'<g transform="rotate({rot} {f(x)} {f(y)})">')
    sh.region(xf("M0 8C-5 8 -7 4 -6 0L-14 -14C-15 -17 -12 -18 -10 -16L-3 -6L-2 -20C-2 -23 2 -23 2 -20L3 -6L10 -16C12 -18 15 -17 14 -14L6 0C7 4 5 8 0 8Z", x, y, s), code)
    sh.raw("</g>")

# ---------- dino's ----------
def spinosaurus(sh):
    sh.circle_r(172, 28, 13, "y"); sh.region(cloud_path(56, 26, 12), "-")
    sh.rect_r(0, 150, 200, 50, "b")
    sh.region(fish_path(24, 86, 9), "t"); eye(sh, 18, 85, 1.3)
    sh.region("M146 104C168 104 186 114 198 132L192 138C178 124 164 120 146 124Z", "g")
    limb(sh, 96, 124, 92, 162, "g", 14); sh.ellipse_r(88, 164, 10, 4, "g")
    sh.region("M70 102A38 62 0 0 1 146 102Z", "o")
    for k in range(1, 6):
        x = 70 + k * 76 / 6; yt = 102 - 62 * math.sqrt(max(0, 1 - ((x - 108) / 38) ** 2))
        sh.seg(x, 100, x, yt + 5)
    sh.region("M58 106C58 88 82 86 108 88C136 90 154 98 154 112C154 130 132 140 104 140C78 140 58 126 58 106Z", "g")
    sh.region("M70 128Q104 146 144 124Q132 140 104 140Q80 140 70 128Z", "y")
    limb(sh, 124, 124, 128, 160, "g", 16); sh.ellipse_r(132, 162, 11, 4.5, "g")
    limb(sh, 70, 114, 60, 128, "g", 7); sh.line("M56 130L54 135M60 132L60 137")
    sh.region("M64 100C56 94 50 88 46 80L58 70C62 78 68 86 76 92Z", "g")
    sh.region("M60 74C60 62 48 60 38 64L10 72C5 74 5 80 10 82L38 86C50 88 60 84 60 74Z", "g")
    eye(sh, 46, 70, 2.4); sh.dot(13, 75, 1.2); sh.line("M10 78Q24 80 42 81")
    for x, y in ((92, 104), (112, 100), (132, 108)): sh.ellipse_r(x, y, 5, 3, "l")
    for k in range(4): sh.line(f"M{14 + k * 50} 176Q{24 + k * 50} 170 {34 + k * 50} 176")
    sh.line("M80 154Q88 150 96 154M118 154Q128 150 138 154")

def _pachy(sh, body, dome):
    limb(sh, 44, 126, 42, 168, body, 9); sh.ellipse_r(40, 171, 9, 4, body)
    sh.region("M44 106C30 100 16 94 4 96L4 103C18 106 30 114 40 122Z", body)
    sh.region("M32 116C32 102 44 94 58 94C72 94 82 104 80 118C78 130 68 136 56 136C42 136 32 128 32 116Z", body)
    for x, y in ((46, 104), (60, 101), (52, 114), (40, 114)): sh.ellipse_r(x, y, 4, 2.6, dome)
    sh.ellipse_r(58, 126, 11, 13, body); limb(sh, 60, 134, 62, 168, body, 10); sh.ellipse_r(66, 171, 10, 4.5, body)
    limb(sh, 76, 114, 84, 122, body, 5)
    sh.region("M68 100C72 92 76 88 82 84L90 92C86 96 82 102 78 108Z", body)
    sh.region("M78 84C78 74 86 68 94 70C100 72 104 80 102 88L98 98C96 102 90 102 88 100L82 94C79 91 78 88 78 84Z", body)
    sh.region("M78 82C76 68 86 60 94 62C100 64 104 72 102 80C96 76 86 76 78 82Z", dome)
    for x, y in ((77, 88), (79, 94), (75, 81)): sh.circle_r(x, y, 2.4, dome)
    eye(sh, 92, 86, 2); sh.dot(99, 93, 1); sh.line("M90 98L96 96.5")

def pachycephalosaurus(sh):
    grass(sh, 176)
    sh.circle_r(30, 28, 12, "y"); sh.region(cloud_path(150, 30, 13), "-")
    sh.raw('<g transform="translate(-2 0)">'); _pachy(sh, "g", "o"); sh.raw("</g>")
    sh.raw('<g transform="translate(202 0) scale(-1 1)">'); _pachy(sh, "t", "p"); sh.raw("</g>")
    sparkle(sh, 100, 50, 8, "y"); sh.line("M86 46L80 38M114 46L120 38M100 36V28")
    sh.ellipse_r(100, 186, 16, 6, "z")

def plesiosaurus(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.line("M0 14Q12 8 25 14T50 14T75 14T100 14T125 14T150 14T175 14T200 14")
    sh.region("M0 200V178Q50 170 100 178T200 176V200Z", "y")
    for x in (16, 184):
        sh.region(f"M{x} 180C{x - 10} 160 {x + 8} 150 {x - 2} 128C{x + 8} 140 {x + 10} 160 {x + 4} 180Z", "g")
    sh.ellipse_r(150, 186, 9, 4, "z"); sh.region(star_path(60, 188, 7, 3), "o")
    sh.region("M96 116C90 104 80 96 68 94C66 96 68 100 72 104C80 110 86 114 92 118Z", "l")
    sh.region("M132 116C134 106 140 98 148 94C150 96 150 100 146 104C142 110 138 114 136 118Z", "l")
    sh.region("M146 126C160 126 174 130 186 138L184 144C170 142 158 140 146 140Z", "g")
    sh.region("M70 130C70 116 92 110 116 112C140 114 152 124 150 134C148 146 128 150 106 150C84 150 70 142 70 130Z", "g")
    for x, y in ((96, 122), (114, 120), (130, 126)): sh.ellipse_r(x, y, 5, 3, "t")
    sh.region("M90 144C84 156 74 166 62 170C60 168 62 164 66 160C74 152 80 146 84 140Z", "l")
    sh.region("M130 146C130 158 126 168 118 174C116 172 116 168 118 162C120 154 122 148 124 144Z", "l")
    sh.region("M76 128C58 118 46 96 50 64L62 62C60 92 70 108 90 118Z", "g")
    sh.region("M56 62C48 60 44 54 47 48C50 42 60 40 68 44L84 48C87 50 85 55 80 55L68 57C64 60 60 62 56 62Z", "g")
    eye(sh, 59, 48, 2.2); sh.line("M68 52L82 51")
    for x, y, r in ((92, 46, 3), (98, 34, 4), (94, 22, 5)): sh.circle_r(x, y, r, "-")
    sh.region(fish_path(168, 70, 9), "o"); eye(sh, 162, 69, 1.3)
    sh.region(fish_path(150, 88, 6), "y"); eye(sh, 146, 87, 1)

def fern(sh, x, y, h, code="g"):
    for a in (-56, -28, 0, 28, 56):
        sh.raw(f'<g transform="rotate({a} {x} {y})">'); sh.region(leaf_path(x, y - h * .5, h * .16, h * .5), code); sh.raw("</g>")

def velociraptor(sh):
    grass(sh, 184)
    sh.circle_r(30, 30, 12, "y")
    fern(sh, 18, 186, 34); fern(sh, 184, 186, 40)
    sh.raw('<g transform="translate(0 8)">')
    limb(sh, 94, 112, 84, 136, "o", 13); limb(sh, 84, 136, 70, 154, "o", 7); limb(sh, 70, 156, 80, 166, "o", 6)
    sh.region("M4 66C30 80 60 88 84 88C100 84 116 86 126 80L136 70L148 76C144 88 138 98 132 106C128 120 114 128 98 126C86 124 78 116 74 108C52 102 28 88 4 73Z", "o")
    sh.line("M96 88L99 96M108 86L109 94M120 84L119 92M60 87L61 95M38 80L40 87")
    sh.region("M136 64C136 52 156 50 168 56L186 64C190 68 188 74 182 74L154 78C144 78 136 74 136 64Z", "o")
    sh.region("M137 62L128 54L139 56L134 47L146 53Z", "r")
    eye(sh, 152, 61, 2.4); sh.line("M156 71L184 69"); sh.line("M162 71L164 74L166 71L168 74L170 71L172 74L174 70")
    limb(sh, 108, 112, 116, 140, "o", 16); limb(sh, 116, 140, 108, 164, "o", 8); limb(sh, 108, 166, 128, 170, "o", 6)
    sh.region("M114 164Q106 154 114 151Q113 158 118 163Z", "-")
    sh.region("M124 96L146 108L138 120Z", "r"); limb(sh, 126, 100, 146, 110, "o", 7)
    sh.line("M148 108L154 106M148 112L154 113")
    sh.raw("</g>")

def dino_skelet(sh):
    sh.rect_r(0, 0, 200, 150, "k"); sh.rect_r(0, 150, 200, 50, "w")
    for x in (40, 100, 160): sh.seg(x, 150, x - 10, 200)
    sh.rect_r(12, 14, 46, 18, "-", 2); sh.text(35, 26.5, "MUSEUM", 7)
    sh.rect_r(74, 10, 38, 30, "y", 2); sh.rect_r(79, 15, 28, 20, "-"); sh.region("M81 33L90 22L96 29L100 25L106 33Z", "g")
    sh.rect_r(20, 136, 160, 14, "z", 2)
    sh.line("M70 136V96M122 136V92")
    for x in range(80, 116, 7): sh.line(f"M{x} 92Q{x + 5} 106 {x + 1} 118")
    sh.line("M76 116Q98 124 118 114")
    for a, b, w in (((70, 92), (42, 104), 7), ((42, 104), (14, 126), 5), ((70, 92), (122, 88), 8), ((122, 88), (148, 60), 7), ((148, 60), (164, 38), 6)):
        limb(sh, *a, *b, "-", w)
        n = int(math.hypot(b[0] - a[0], b[1] - a[1]) // 8)
        for k in range(1, n + 1):
            t = k / (n + 1); x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy); px, py = -dy / d * w * .5, dx / d * w * .5
            sh.seg(x + px, y + py, x - px, y - py)
    sh.ellipse_r(72, 98, 10, 7, "-")
    for (x1, y1), (x2, y2), (x3, y3) in (((66, 100), (62, 118), (66, 134)), ((80, 100), (84, 118), (80, 134)), ((116, 94), (118, 114), (116, 134)), ((128, 94), (132, 114), (132, 134))):
        limb(sh, x1, y1, x2, y2, "-", 6); limb(sh, x2, y2, x3, y3, "-", 5); sh.circle_r(x2, y2, 3.2, "-")
        sh.ellipse_r(x3 + 2, y3 + 1, 6, 2.6, "-")
    sh.region("M158 34C158 25 172 22 182 26L190 32C191 37 187 40 181 40H166C161 40 158 38 158 34Z", "-")
    sh.circle_r(170, 31, 3, "-"); sh.line("M168 37H188")
    for x in (14, 186):
        sh.rect_r(x - 3, 158, 6, 38, "y", 1); sh.circle_r(x, 157, 4.5, "y")
    sh.line("M14 160Q100 186 186 160", "l", "stroke-width:3.4")

def dinosporen(sh):
    sh.region("M0 0H200V80H0Z", "b")
    sh.circle_r(32, 28, 12, "y"); sh.region(cloud_path(110, 30, 12), "-")
    sh.region("M0 200V80Q50 72 100 80T200 76V200Z", "w")
    for x in (14, 40):
        sh.region(leaf_path(x - 6, 66, 5, 14), "g"); sh.region(leaf_path(x + 6, 66, 5, 14), "g"); sh.region(leaf_path(x, 62, 5, 16), "g")
    sh.region("M138 78C136 64 156 56 168 62C176 50 196 54 196 70C202 74 200 82 194 82H140Z", "g")
    sh.region("M150 62C148 44 164 36 176 40C186 44 188 54 182 60Z", "l")
    sh.circle_r(160, 50, 3.6, "-"); eye(sh, 161, 51, 1.6); sh.line("M168 56Q174 58 180 55")
    sh.region("M152 46L148 38L156 42Z", "o"); sh.region("M160 40L160 32L166 38Z", "o")
    for k in range(6):
        t = k / 5; s = 1.3 - t * .7
        x = 34 + t * 100 + (9 if k % 2 else -9) * s; y = 176 - t * 84 + (9 if k % 2 else -9) * s
        footprint(sh, x, y, s, 47, "z")
    sh.circle_r(160, 162, 16, "b"); sh.circle_line(160, 162, 12)
    limb(sh, 172, 174, 190, 194, "x", 7)
    for x, y in ((20, 110), (186, 120)): sh.ellipse_r(x, y, 7, 4, "z")

def _sauropod(sh, ox, oy, s, mx, body, spot):
    def L(x1, y1, x2, y2, w): limb(sh, ox + (-x1 if mx else x1) * s, oy + y1 * s, ox + (-x2 if mx else x2) * s, oy + y2 * s, body, w * s)
    sh.region(xf("M-40 -50C-56 -46 -68 -36 -76 -22L-70 -18C-60 -30 -50 -36 -36 -38Z", ox, oy, s, mx), body)
    L(-30, -42, -30, -6, 14); L(16, -42, 18, -6, 14)
    sh.region(xf("M-44 -52C-44 -72 -22 -80 0 -78C20 -76 34 -68 34 -52C34 -36 18 -30 -4 -30C-28 -30 -44 -36 -44 -52Z", ox, oy, s, mx), body)
    L(-20, -40, -22, -6, 15); L(24, -40, 26, -6, 15)
    for x, y in ((-24, -62), (-6, -66), (12, -60)):
        sh.ellipse_r(ox + (-x if mx else x) * s, oy + y * s, 6 * s, 4 * s, spot)
    sh.region(xf("M18 -66C28 -86 32 -106 38 -120L50 -116C46 -100 40 -78 32 -58Z", ox, oy, s, mx), body)
    sh.region(xf("M34 -120C32 -130 42 -136 52 -134C62 -132 66 -126 64 -120C62 -116 54 -114 46 -114C40 -114 34 -116 34 -120Z", ox, oy, s, mx), body)
    eye(sh, ox + (-50 if mx else 50) * s, oy - 127 * s, max(1.4, 2.4 * s))
    sh.line(xf("M54 -120Q58 -118 62 -121", ox, oy, s, mx))

def dino_familie(sh):
    sh.region("M0 0H200V160H0Z", "b")
    sh.region(cloud_path(160, 30, 15), "z"); sh.region(cloud_path(178, 12, 9), "z")
    sh.region("M100 166L146 52H174L200 108V166Z", "w")
    sh.region("M146 52Q160 62 174 52L172 64L166 74L162 62L158 84L152 64L148 70Z", "r")
    for x, y in ((150, 40), (170, 36), (160, 24)): sh.circle_r(x, y, 3, "o")
    grass(sh, 166, "l")
    _sauropod(sh, 64, 176, 1.0, False, "g", "t")
    _sauropod(sh, 150, 180, .5, True, "l", "y")
    _sauropod(sh, 186, 182, .38, True, "t", "y")
    sh.region(heart_path(122, 84, 6), "r")

def iguanodon(sh):
    grass(sh, 184)
    sh.circle_r(30, 30, 12, "y")
    sh.rect_r(178, 50, 14, 134, "w", 2)
    sh.region("M156 50C146 40 154 24 168 26C172 10 196 8 200 22V70C192 76 182 72 178 66C170 72 158 66 156 50Z", "g")
    sh.line("M180 92L150 96"); 
    for x, y, a in ((160, 89, -60), (170, 100, 50), (152, 100, 40)):
        sh.raw(f'<g transform="rotate({a} {x} {y})">'); sh.region(leaf_path(x, y, 5, 8), "g"); sh.raw("</g>")
    limb(sh, 72, 136, 70, 172, "l", 14); sh.ellipse_r(76, 176, 12, 5, "l")
    sh.region("M8 170C30 152 46 130 60 114C76 96 94 86 112 78L122 68L134 76C130 86 126 94 124 104C124 126 110 146 86 152C66 156 40 164 14 180Z", "l")
    sh.line("M70 108L76 114M84 96L90 103M98 88L103 95M112 80L117 87")
    sh.line("M90 140Q108 126 116 106")
    sh.region("M118 66C116 54 130 48 142 52L158 58C162 62 160 66 154 68L138 76C128 78 120 74 118 66Z", "l")
    eye(sh, 134, 60, 2.2); sh.line("M142 68L156 64")
    limb(sh, 86, 128, 92, 166, "l", 18); sh.ellipse_r(100, 172, 14, 5.5, "l")
    limb(sh, 116, 102, 142, 98, "l", 8)
    sh.circle_r(145, 97, 5, "l")
    sh.region("M144 92L147 81L150 93Z", "-")
    sh.region("M24 184C24 170 46 170 46 184Z", "g")

def archeopteryx(sh):
    sh.circle_r(30, 28, 12, "y")
    sh.region(cloud_path(166, 26, 12), "-")
    sh.region("M90 120C76 140 64 162 60 188C72 192 84 192 94 188C98 164 102 142 106 124Z", "b")
    sh.line("M98 124L78 188")
    for k in range(5):
        y = 136 + k * 11; x = 98 - (y - 124) * .31
        sh.line(f"M{f(x)} {y}L{f(x - 10)} {y + 6}M{f(x)} {y}L{f(x + 9)} {y + 4}")
    for mirror in (False, True):
        if mirror: sh.raw('<g transform="translate(200 0) scale(-1 1)">')
        sh.region("M92 100C72 82 44 68 16 66C22 74 20 80 28 86C24 92 28 96 36 98C34 104 42 108 50 108C52 114 62 116 70 114C78 114 86 112 92 108Z", "t")
        sh.line("M28 86Q60 92 88 102M36 98Q64 102 88 106M50 108Q70 110 88 108")
        sh.line("M22 66L14 58M26 68L22 58M18 70L10 66")
        if mirror: sh.raw("</g>")
    sh.region("M0 140Q100 126 200 134V146Q100 138 0 152Z", "w")
    sh.region(leaf_path(30, 126, 5, 10), "g"); sh.region(leaf_path(170, 124, 5, 10), "g")
    sh.ellipse_r(100, 108, 14, 19, "o")
    sh.line("M94 126L90 138M106 126L110 138")
    sh.line("M84 136L90 140L96 136M104 136L110 140L116 136")
    sh.circle_r(102, 82, 11, "o")
    sh.region("M110 78L130 84L110 90Z", "y"); sh.line("M114 84L128 84")
    sh.line("M116 84L117 86.5L119 84L120 86.5L122 84")
    eye(sh, 104, 79, 2.2)
    sh.region("M96 72L90 62L100 68L98 60L106 70Z", "r")

def dino_opgraving(sh):
    sh.rect_r(0, 0, 200, 96, "b")
    sh.circle_r(170, 28, 13, "y"); sh.region(cloud_path(100, 26, 11), "-")
    sh.region("M0 200V96Q100 90 200 96V200Z", "w")
    sh.rect_r(80, 108, 112, 80, "y", 3)
    sh.line("M117 108V188M155 108V188M80 148H192", "l", "stroke-width:1.2")
    for x, y in ((117, 106), (155, 106), (78, 148), (194, 148), (117, 190), (155, 190)): sh.circle_r(x, y, 2.5, "r")
    sh.region("M96 130C96 120 116 116 136 120L164 128C168 132 166 138 160 140L146 142L144 150H132L128 144C116 148 100 144 96 138Z", "-")
    sh.circle_r(116, 128, 4.5, "-"); sh.ellipse_r(140, 129, 7, 4, "-")
    sh.line("M132 142L134 146L136 142L138 146L140 142L142 146")
    bone(sh, 96, 166, 132, 172, 6); bone(sh, 150, 160, 180, 176, 5)
    for k in range(4): sh.circle_r(140 + k * 9, 108 + 70 - k * 2, 3.5, "-")
    person(sh, 40, 78, "g", "w", hands=((18, 140), (72, 138)), cap=True)
    sh.region("M20 88Q40 82 60 88Q58 92 40 92Q22 92 20 88Z", "y"); sh.region("M28 88Q28 72 40 72Q52 72 52 88Z", "y"); sh.rect_r(28, 83, 24, 5, "w", 2)
    limb(sh, 74, 136, 86, 128, "w", 4); sh.region("M84 124L92 120L96 128L88 132Z", "r")
    limb(sh, 18, 110, 18, 160, "w", 4); sh.rect_r(11, 105, 14, 5, "w", 2); sh.region("M10 160H26L24 176Q18 181 12 176Z", "z")
    sh.circle_r(18, 140, 4.5, "-")
    sh.region("M168 92L172 74H190L194 92Z", "r"); sh.line("M172 74Q181 64 190 74")


# ---------- ruimte ----------
def ruimtestation(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region("M0 200V172Q100 142 200 172V200Z", "b")
    sh.region("M30 190Q50 168 80 172Q76 188 56 196Z", "g"); sh.region("M120 170Q146 160 168 168Q160 184 136 184Z", "g")
    stars(sh, ((14, 18), (186, 20), (100, 14), (60, 150), (150, 146), (24, 150)), 4)
    sh.rect_r(14, 95, 172, 6, "z")
    for x in range(14, 186, 8): sh.seg(x, 95, x + 8, 101, "l", "stroke-width:1")
    for x0 in (14, 150):
        for y0 in (50, 106):
            sh.rect_r(x0, y0, 36, 40, "y")
            for k in (1, 2): sh.seg(x0 + k * 12, y0, x0 + k * 12, y0 + 40, "l", "stroke-width:1.2")
            for k in (1, 2, 3): sh.seg(x0, y0 + k * 10, x0 + 36, y0 + k * 10, "l", "stroke-width:1.2")
        sh.rect_r(x0 + 15, 90, 6, 16, "z")
    sh.rect_r(88, 52, 24, 92, "-", 5)
    sh.region("M92 52L96 36H104L108 52Z", "r"); sh.circle_r(100, 32, 4, "r")
    sh.rect_r(54, 86, 92, 24, "z", 6)
    for x in (66, 80, 120, 134): sh.circle_r(x, 98, 4, "b")
    sh.circle_r(100, 70, 5, "b"); sh.circle_r(100, 126, 5, "b")
    sh.line("M100 144V156"); sh.region("M92 156H108L104 164H96Z", "o")

def planeetrover(sh):
    sh.rect_r(0, 0, 200, 120, "n")
    stars(sh, ((16, 16), (60, 30), (180, 50), (110, 12)), 4)
    sh.circle_r(160, 26, 10, "z"); sh.circle_r(30, 70, 6, "k")
    sh.region("M0 130L30 104L60 122L100 96L140 118L170 100L200 116V200H0Z", "r")
    sh.region("M0 200V136Q100 124 200 140V200Z", "o")
    for x, y, r in ((24, 170, 9), (172, 182, 12), (186, 150, 6)): sh.ellipse_r(x, y, r, r * .6, "w")
    for k in range(7): sh.rect_r(8 + k * 9, 156 + k * .4, 5, 3, "w", 1)
    sh.rect_r(126, 44, 6, 44, "z"); sh.rect_r(116, 32, 26, 14, "-", 3)
    sh.circle_r(124, 39, 4, "b"); sh.circle_r(134, 39, 4, "b")
    sh.line("M66 86V64"); sh.region("M56 64Q66 72 76 64Q66 56 56 64Z", "-"); sh.circle_r(66, 62, 2, "r")
    sh.rect_r(40, 84, 116, 8, "b", 2)
    for x in range(52, 156, 12): sh.seg(x, 84, x, 92, "l", "stroke-width:1")
    sh.rect_r(52, 92, 92, 26, "-", 3); sh.rect_r(62, 98, 28, 12, "y", 2); sh.circle_r(124, 104, 5, "r")
    limb(sh, 52, 104, 30, 118, "z", 5); sh.circle_r(28, 122, 6, "z")
    sh.line("M64 118L56 134L100 134L100 118M136 118L144 134L100 134")
    for x in (56, 100, 144):
        sh.circle_r(x, 142, 13, "z"); sh.circle_r(x, 142, 5, "-")
        for a in range(0, 360, 60):
            r = math.radians(a); sh.seg(x + 5 * math.cos(r), 142 + 5 * math.sin(r), x + 11 * math.cos(r), 142 + 11 * math.sin(r), "l", "stroke-width:1.2")

def telescoop(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    stars(sh, ((20, 20), (70, 14), (110, 40), (30, 110), (186, 110), (140, 14), (90, 90)), 5)
    sh.circle_r(166, 44, 18, "y")
    for x, y, r in ((160, 38, 4), (172, 52, 3), (170, 34, 2.5)): sh.circle_r(x, y, r, "o")
    sh.region("M0 200V150Q60 122 120 140T200 130V200Z", "g")
    sh.line("M132 112L116 146M132 112L150 142M132 112L134 150")
    limb(sh, 108, 124, 156, 96, "r", 12); limb(sh, 150, 99, 164, 91, "-", 17)
    sh.rect_r(124, 104, 8, 10, "z", 1)
    limb(sh, 104, 126, 112, 122, "z", 6)
    person(sh, 72, 70, "y", "n", hands=((104, 124), (46, 72)), hair="w")

def sterrenbeelden(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    dip = [(18, 30), (44, 26), (66, 36), (88, 50), (94, 80), (130, 84), (136, 54), (88, 50)]
    cas = [(102, 128), (122, 112), (140, 128), (160, 108), (184, 118)]
    sh.line("M" + " L".join(f"{x} {y}" for x, y in dip), "l", "stroke-width:1.4;stroke-dasharray:3 3")
    sh.line("M" + " L".join(f"{x} {y}" for x, y in cas), "l", "stroke-width:1.4;stroke-dasharray:3 3")
    stars(sh, dip[:7] + cas, 7)
    sh.text(110, 100, "Steelpan", 6); sh.text(140, 146, "Cassiopeia", 6)
    for x, y in ((170, 20), (30, 80), (60, 120), (180, 70), (150, 40), (20, 140), (80, 150)): sh.region(star_path(x, y, 3, 1.4), "y")
    sh.region("M0 200V170Q50 158 100 168T200 164V200Z", "g")
    sh.rect_r(26, 150, 6, 22, "w"); sh.circle_r(29, 142, 14, "g")
    sh.rect_r(60, 152, 30, 20, "o"); sh.region("M56 154L75 138L94 154Z", "r"); sh.rect_r(70, 157, 9, 9, "y", 1)

def alienvriendje(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    stars(sh, ((16, 20), (60, 14), (186, 92), (14, 100), (150, 70)), 5)
    sh.circle_r(166, 34, 14, "o"); sh.ellipse_r(166, 34, 24, 5, "y"); sh.region("M152 32A14 14 0 0 1 180 32Z", "o")
    sh.region("M0 200V174Q100 162 200 176V200Z", "t")
    for x, y, r in ((30, 186, 8), (170, 190, 10), (120, 184, 5)): sh.ellipse_r(x, y, r, r * .4, "b")
    sh.region("M24 172V122Q24 98 38 88Q52 98 52 122V172Z", "-"); sh.region("M26 108Q28 96 38 88Q48 96 50 108Z", "r")
    sh.circle_r(38, 126, 7, "b"); sh.region("M24 150L12 172H24Z", "r"); sh.region("M52 150L64 172H52Z", "r")
    sh.line("M98 64L90 42M122 64L130 42"); sh.circle_r(90, 40, 5, "y"); sh.circle_r(130, 40, 5, "y")
    limb(sh, 98, 162, 96, 178, "g", 12); limb(sh, 122, 162, 124, 178, "g", 12)
    sh.ellipse_r(92, 180, 9, 4.5, "g"); sh.ellipse_r(128, 180, 9, 4.5, "g")
    limb(sh, 86, 128, 64, 106, "g", 9); limb(sh, 134, 128, 156, 146, "g", 9)
    for dx, dy in ((-4, -2), (0, -5), (4, -2)): sh.circle_r(62 + dx, 104 + dy, 3, "g")
    sh.region(star_path(160, 150, 9, 4), "y")
    sh.region("M82 170C76 140 86 112 110 112C134 112 144 140 138 170Z", "g")
    sh.ellipse_r(110, 146, 16, 14, "l")
    sh.ellipse_r(110, 86, 32, 26, "g")
    for x, y in ((96, 82), (110, 74), (124, 82)): sh.circle_r(x, y, 7, "-"); eye(sh, x, y + 1, 3)
    sh.line("M96 96Q110 108 124 96"); sh.region("M106 99.5H112V104H106Z", "-")
    sh.circle_r(86, 96, 4, "k"); sh.circle_r(134, 96, 4, "k")

def astronaut_maan(sh):
    sh.rect_r(0, 0, 200, 200, "x")
    sh.circle_r(40, 40, 18, "b"); sh.region("M30 30Q40 28 42 36Q36 44 28 40Z", "g"); sh.region("M44 46Q54 44 52 54Q44 56 42 50Z", "g")
    stars(sh, ((100, 16), (176, 26), (130, 40), (16, 96), (184, 90)), 4)
    sh.region("M0 200V150Q60 140 110 148T200 144V200Z", "z")
    for x, y, r in ((24, 176, 10), (176, 182, 12), (90, 190, 6)): sh.ellipse_r(x, y, r, r * .4, "-")
    for k in range(4): sh.ellipse_r(30 + k * 16, 164 - k * 2 + (k % 2) * 6, 4, 2.4, "x")
    sh.line("M152 162V70"); sh.region("M152 70H188V94H152Z", "r"); sh.region(star_path(170, 82, 7, 3), "y")
    sh.ellipse_r(152, 162, 6, 2, "x")
    sh.rect_r(78, 92, 52, 46, "z", 6)
    person(sh, 104, 61, "-", "-", hands=((80, 128), (150, 116)), hair=None, shoes="z", face=False, legs=((94, 160), (114, 160)))
    sh.circle_r(104, 76, 20, "-")
    sh.region("M90 76Q90 64 104 64Q118 64 118 76Q118 88 104 88Q90 88 90 76Z", "b")
    sh.region("M95 70Q99 66 104 67Q98 70 97 75Z", "-")
    sh.rect_r(94, 106, 20, 12, "r", 2); sh.circle_r(100, 112, 2, "-"); sh.circle_r(108, 112, 2, "-")

def raketlancering(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.region(cloud_path(40, 30, 12), "-"); sh.region(cloud_path(170, 50, 10), "-")
    sh.line("M36 170V36M56 170V36")
    for y in range(36, 170, 16): sh.line(f"M36 {y}L56 {y + 16}M56 {y}L36 {y + 16}", "l", "stroke-width:1.3")
    sh.rect_r(32, 30, 28, 6, "r"); sh.rect_r(56, 80, 40, 5, "z")
    sh.region("M98 158Q104 178 110 192Q116 178 122 158Z", "o"); sh.region("M103 158Q107 172 110 180Q113 172 117 158Z", "y")
    sh.region("M96 120L78 150L96 148Z", "r"); sh.region("M124 120L142 150L124 148Z", "r")
    sh.region("M96 150V70Q96 42 110 24Q124 42 124 70V150Z", "-")
    sh.region("M98 56Q102 38 110 24Q118 38 122 56Z", "r")
    sh.circle_r(110, 84, 7, "b"); sh.rect_r(96, 106, 28, 6, "r"); sh.seg(110, 120, 110, 148)
    sh.region("M100 150L97 158H123L120 150Z", "z")
    sh.region(cloud_path(66, 178, 22), "-"); sh.region(cloud_path(154, 180, 22), "-")
    sh.region(cloud_path(20, 190, 13), "-"); sh.region(cloud_path(184, 192, 12), "-")
    sh.region("M88 200C84 186 100 180 110 188C120 180 136 186 132 200Z", "-")

def ruimtehelm(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    stars(sh, ((18, 20), (180, 22), (16, 120), (186, 118), (30, 66)), 5)
    sh.region("M14 200C18 166 46 150 100 150C154 150 182 166 186 200Z", "-")
    sh.region(star_path(152, 182, 8, 3.5), "r"); sh.rect_r(40, 176, 26, 14, "b", 2)
    sh.ellipse_r(100, 152, 50, 12, "z")
    sh.circle_r(100, 88, 64, "-")
    sh.rect_r(150, 54, 16, 12, "y", 3); sh.line("M136 30L144 12"); sh.circle_r(145, 10, 3.5, "r")
    sh.region("M52 72Q52 42 100 42Q148 42 148 72V100Q148 130 100 130Q52 130 52 100Z", "b")
    sh.circle_r(100, 92, 30, "k")
    sh.region("M70 88C70 62 130 62 130 88Q122 74 106 76Q90 72 70 88Z", "w")
    eye(sh, 89, 92, 3); eye(sh, 111, 92, 3); smile(sh, 100, 104, 7)
    sh.circle_r(80, 102, 4, "m"); sh.circle_r(120, 102, 4, "m")
    sh.region("M60 70Q64 52 82 48Q70 58 68 74Z", "-"); sh.region("M66 84Q66 80 68 78L70 88Q68 90 66 84Z", "-")

def volle_maan(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    stars(sh, ((16, 18), (180, 172), (20, 176), (186, 90), (12, 100)), 5)
    sh.line("M24 140C40 186 160 196 186 150", "l", "stroke-width:1.2;stroke-dasharray:3 4")
    sh.circle_r(100, 100, 68, "y")
    for x, y, r in ((74, 70, 15), (126, 60, 9), (130, 116, 19), (78, 130, 11), (104, 94, 6), (56, 104, 7), (152, 88, 6), (106, 150, 8), (98, 44, 5)):
        sh.circle_r(x, y, r, "o"); sh.line(f"M{f(x - r * .75)} {f(y - r * .2)}A{f(r * .8)} {f(r * .8)} 0 0 0 {f(x + r * .2)} {f(y + r * .75)}", "l", "stroke-width:1.4")
    sh.raw('<g transform="rotate(40 168 30)">')
    sh.region("M162 46V24Q162 14 168 8Q174 14 174 24V46Z", "-"); sh.circle_r(168, 26, 3, "b")
    sh.region("M162 38L156 48H162Z", "r"); sh.region("M174 38L180 48H174Z", "r")
    sh.region("M164 46Q166 54 168 58Q170 54 172 46Z", "o")
    sh.raw("</g>")

def zonsverduistering(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    stars(sh, ((170, 20), (186, 70), (20, 130), (110, 110), (150, 50)), 4)
    sh.region(star_path(62, 62, 48, 36, 16), "y")
    sh.circle_r(62, 62, 30, "o")
    sh.circle_r(72, 56, 29, "z")
    sh.region("M0 200V160Q60 146 120 156T200 150V200Z", "g")
    person(sh, 140, 86, "r", "n", hands=((112, 80), (162, 152)), hair="w", face=False)
    sh.rect_r(124, 99, 32, 9, "-", 2); sh.ellipse_r(133, 103.5, 5.5, 3.5, "x"); sh.ellipse_r(147, 103.5, 5.5, 3.5, "x")
    smile(sh, 140, 111, 4)
    sh.region(heart_path(30, 170, 5), "r")


# ---------- sport ----------
def wielrenner(sh):
    sh.region("M0 170V120Q50 100 100 116T200 108V170Z", "l")
    for x in (176,): sh.rect_r(x - 3, 100, 6, 24, "w"); sh.circle_r(x, 94, 13, "g")
    sh.circle_r(160, 30, 13, "y")
    sh.rect_r(0, 170, 200, 30, "z")
    for x in range(10, 200, 44): sh.rect_r(x, 182, 22, 5, "-", 1)
    limb(sh, 92, 98, 108, 118, "x", 12); limb(sh, 108, 118, 88, 140, "-", 9); sh.ellipse_r(86, 143, 7, 4, "x")
    for x in (56, 148):
        sh.circle_r(x, 146, 24, "x"); sh.circle_r(x, 146, 19, "-")
        for a in range(0, 180, 30):
            r = math.radians(a); sh.seg(x - 19 * math.cos(r), 146 - 19 * math.sin(r), x + 19 * math.cos(r), 146 + 19 * math.sin(r), "l", "stroke-width:1")
        sh.circle_r(x, 146, 3, "z")
    for a, b in (((56, 146), (98, 148)), ((56, 146), (90, 104)), ((98, 148), (90, 104)), ((90, 104), (136, 104)), ((98, 148), (138, 108)), ((136, 104), (148, 146))):
        limb(sh, *a, *b, "r", 5)
    sh.circle_r(98, 148, 6, "z")
    sh.line("M134 100Q152 96 154 104Q156 114 146 114", "l", "stroke-width:3.2")
    sh.region("M78 96H102Q102 103 94 103H84Z", "x")
    limb(sh, 92, 96, 128, 76, "y", 18)
    limb(sh, 92, 98, 116, 122, "x", 12); limb(sh, 116, 122, 110, 152, "-", 9); sh.ellipse_r(112, 155, 7, 4, "x")
    sh.circle_r(141, 68, 12, "-")
    sh.region("M127 66Q128 50 144 51Q158 53 157 64Q150 60 140 62Z", "r")
    eye(sh, 147, 70, 1.7); sh.line("M146 75Q150 77 153 74")
    limb(sh, 126, 80, 146, 104, "y", 8); sh.circle_r(148, 106, 4.5, "-")
    sh.line("M12 84H38M4 98H28M14 112H34")

def skier(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.circle_r(170, 26, 12, "y")
    sh.region("M0 110L36 56L70 96L112 36L156 92L184 62L200 80V200H0Z", "z")
    for (x, y), w in (((36, 56), 9), ((112, 36), 12), ((184, 62), 7)):
        sh.region(f"M{x - w} {y + w * 1.4}L{x} {y}L{x + w * .9} {y + w * 1.2}L{x + w * .3} {y + w}L{x - w * .3} {y + w * 1.3}Z", "-")
    sh.region("M0 120Q100 120 200 186V200H0Z", "-")
    for x, y, s in ((30, 150, 1), (176, 182, .8), (150, 140, .6)):
        sh.rect_r(x - 2 * s, y, 4 * s, 10 * s, "w"); sh.region(f"M{x} {y - 30 * s}L{x + 12 * s} {y}H{x - 12 * s}Z", "g")
    sh.raw('<g transform="rotate(22 100 160)">')
    for dy in (0, 6):
        sh.region(f"M58 {160 + dy}H142Q150 {160 + dy} 152 {154 + dy}L154 {156 + dy}Q152 {164 + dy} 142 {164 + dy}H58Z", "r")
    sh.raw("</g>")
    sh.line("M80 112L62 152"); sh.ellipse_r(64, 148, 4, 1.6, "-")
    limb(sh, 98, 98, 80, 112, "r", 8); sh.circle_r(78, 114, 4.5, "g")
    limb(sh, 90, 122, 106, 136, "n", 12); limb(sh, 106, 136, 96, 154, "n", 11)
    limb(sh, 94, 126, 112, 138, "n", 12); limb(sh, 112, 138, 106, 160, "n", 11)
    sh.ellipse_r(97, 157, 7, 4, "x"); sh.ellipse_r(108, 163, 7, 4, "x")
    limb(sh, 90, 122, 100, 94, "r", 18)
    sh.circle_r(106, 80, 12, "-")
    sh.region("M94 78Q94 64 106 64Q118 64 118 78Z", "y"); sh.circle_r(106, 62, 4, "r")
    sh.region("M98 79H118V85H98Z", "t"); smile(sh, 110, 89, 3)
    sh.line("M120 116L142 160"); sh.ellipse_r(140, 156, 4, 1.6, "-")
    limb(sh, 102, 100, 118, 116, "r", 8); sh.circle_r(120, 118, 4.5, "g")
    for x, y in ((44, 150), (36, 142), (48, 140), (30, 152)): sh.circle_r(x, y, 2.5, "-")

def tafeltennis(sh):
    sh.rect_r(0, 168, 200, 32, "b")
    person(sh, 22, 70, "r", "n", hands=((44, 116), (8, 136)), hair="w")
    sh.circle_r(50, 110, 9, "r"); limb(sh, 46, 116, 42, 124, "w", 4)
    person(sh, 178, 70, "g", "x", hands=((154, 112), (192, 136)), hair="o")
    sh.circle_r(150, 104, 9, "n"); limb(sh, 154, 110, 158, 118, "w", 4)
    sh.line("M50 168V146M150 168V146M62 172V150M138 172V150")
    sh.region("M36 136H164L170 146H30Z", "g"); sh.rect_r(30, 146, 140, 5, "g")
    sh.seg(36, 141, 166, 141, "l", "stroke-width:1.4")
    sh.rect_r(97, 116, 6, 26, "-")
    for y in (122, 128, 134): sh.seg(97, y, 103, y, "l", "stroke-width:.8")
    sh.circle_r(116, 70, 4, "-")
    sh.line("M58 102Q84 52 112 68", "l", "stroke-width:1.2;stroke-dasharray:2 3")
    sparkle(sh, 100, 30, 6); sparkle(sh, 30, 40, 5)

def duiker(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.region("M0 200V180Q50 170 100 178T200 174V200Z", "y")
    for x in (18, 182):
        sh.region(f"M{x} 180C{x - 10} 160 {x + 8} 150 {x - 2} 128C{x + 8} 140 {x + 10} 160 {x + 4} 180Z", "g")
    sh.region("M140 180C138 166 144 158 150 158C150 150 160 150 160 160C166 156 170 166 166 180Z", "m")
    sh.region(star_path(50, 186, 7, 3), "o")
    sh.rect_r(78, 74, 44, 38, "y", 6)
    hy = person(sh, 100, 44, "n", "n", hands=((58, 84), (142, 84)), legs=((86, 136), (114, 136)), shoes="n", face=False)
    sh.region("M86 136L74 168Q86 174 96 166L94 136Z", "r"); sh.region("M114 136L126 168Q114 174 104 166L106 136Z", "r")
    sh.line(f"M85 {hy - 1}H115", "l", "stroke-width:3")
    sh.region(f"M89 {hy - 4}H111Q115 {hy - 4} 115 {hy + 1}V{hy + 4}Q115 {hy + 8} 111 {hy + 8}H89Q85 {hy + 8} 85 {hy + 4}V{hy + 1}Q85 {hy - 4} 89 {hy - 4}Z", "t")
    sh.seg(100, hy - 4, 100, hy + 8)
    eye(sh, 94, hy + 2, 1.8); eye(sh, 106, hy + 2, 1.8)
    sh.circle_r(100, hy + 11, 3, "z")
    limb(sh, 118, hy + 10, 118, hy - 18, "o", 4.5); sh.line(f"M103 {hy + 11}Q118 {hy + 14} 118 {hy + 8}")
    for x, y, r in ((122, 26, 3), (128, 16, 4), (122, 6, 3)): sh.circle_r(x, y, r, "-")
    sh.line(f"M88 {hy + 32}H112M88 {hy + 42}H112")
    sh.region(fish_path(176, 84, 10), "o"); eye(sh, 170, 83, 1.4)
    sh.region(fish_path(32, 60, 8), "m"); eye(sh, 27, 59, 1.2)
    sh.region(fish_path(170, 130, 6), "y"); eye(sh, 166, 129, 1)

def karate(sh):
    sh.rect_r(0, 176, 200, 24, "y"); sh.seg(100, 176, 100, 200); sh.seg(0, 188, 200, 188)
    limb(sh, 72, 120, 68, 170, "-", 13); sh.ellipse_r(64, 174, 9, 4.5, "-")
    limb(sh, 86, 116, 150, 102, "-", 13); sh.ellipse_r(158, 101, 9, 5.5, "-")
    limb(sh, 66, 80, 46, 96, "-", 9); sh.circle_r(44, 98, 5.5, "-")
    sh.region("M60 72Q78 64 96 72L100 120H56Z", "-")
    sh.line("M66 70L78 98L90 70M78 98V118")
    sh.rect_r(54, 112, 48, 7, "o"); sh.region("M74 118L68 136L74 136L78 120L82 136L88 136L82 118Z", "o")
    limb(sh, 92, 80, 112, 74, "-", 9); sh.circle_r(116, 73, 5.5, "-")
    sh.circle_r(78, 50, 15, "-")
    sh.region("M63 50A15 15 0 0 1 93 50Q86 41 76 43Q68 44 63 50Z", "w")
    sh.region("M63 46Q78 40 93 46L93 51Q78 45 63 51Z", "r"); sh.region("M63 48L52 42L54 52Z", "r")
    eye(sh, 74, 54, 1.8); eye(sh, 84, 54, 1.8); sh.line("M74 60H84")
    sh.line("M170 90L184 84M172 102H188M170 114L184 120")
    sparkle(sh, 150, 40, 7); sparkle(sh, 30, 40, 5)


# ---------- beroepen ----------
def wetenschapper(sh):
    sh.rect_r(0, 0, 200, 150, "k")
    sh.rect_r(130, 16, 56, 6, "w"); 
    for k, c in enumerate("rbg"): sh.rect_r(136 + k * 16, 0, 10, 16, c, 2)
    hy = person(sh, 60, 52, "-", "n", hands=((36, 140), (93, 104)), hair="o", face=False)
    sh.region("M45 64Q36 56 42 48Q46 54 50 52Q50 44 58 46Q60 40 68 44Q74 40 76 50Q82 48 80 58Q84 62 75 64Z", "o")
    sh.circle_r(55, hy + 3, 5, "b"); sh.circle_r(65, hy + 3, 5, "b"); sh.seg(60, hy + 3, 60, hy + 3)
    sh.line(f"M45 {hy + 2}H50M70 {hy + 2}H75")
    eye(sh, 55, hy + 3, 1.6); eye(sh, 65, hy + 3, 1.6); smile(sh, 60, hy + 9, 4)
    sh.line(f"M54 {hy + 16}L60 {hy + 34}L66 {hy + 16}")
    sh.region("M88 74H98V104Q98 110 93 110Q88 110 88 104Z", "-")
    sh.region("M88 92H98V104Q98 110 93 110Q88 110 88 104Z", "l")
    sh.circle_r(93, 104, 4.5, "-")
    for x, y, r in ((92, 66, 2.5), (96, 58, 3), (90, 50, 3.5)): sh.circle_r(x, y, r, "-")
    sh.rect_r(0, 146, 200, 8, "w"); sh.rect_r(0, 154, 200, 46, "z")
    for x in (40, 100, 160): sh.rect_r(x - 26, 162, 52, 32, "-", 2); sh.circle_r(x + 18, 178, 2.5, "x")
    sh.rect_r(112, 128, 52, 6, "w"); sh.line("M116 134V146M160 134V146")
    for k, c in enumerate("rybp"):
        x = 118 + k * 12
        sh.region(f"M{x} 108H{x + 8}V140Q{x + 8} 145 {x + 4} 145Q{x} 145 {x} 140Z", "-")
        sh.region(f"M{x} 128H{x + 8}V140Q{x + 8} 145 {x + 4} 145Q{x} 145 {x} 140Z", c)
    sh.rect_r(112, 124, 52, 5, "w")
    sh.region("M168 146L176 124V108H184V124L192 146Z", "-")
    sh.region("M171.3 138H188.7L192 146H168Z", "g")
    for x, y, r in ((180, 100, 3), (184, 90, 2.5), (178, 82, 3.5)): sh.circle_r(x, y, r, "-")

def bibliothecaris(sh):
    sh.rect_r(0, 0, 200, 140, "w")
    rnd = random.Random(27)
    for y0, y1 in ((4, 40), (46, 82), (88, 124)):
        x = 4
        cols = "rbgyotpmn"
        while x < 192:
            w = rnd.choice((8, 9, 10, 12)); h = rnd.choice((26, 30, 32, 34))
            if x + w > 196: break
            sh.rect_r(x, y1 - h, w, h, cols[rnd.randrange(len(cols))], 1)
            if w >= 10: sh.seg(x + 2, y1 - h + 6, x + w - 2, y1 - h + 6, "l", "stroke-width:1")
            x += w + 1
        sh.rect_r(0, y1, 200, 6, "w")
    hy = person(sh, 70, 62, "p", "n", hands=((52, 132), (90, 132)), hair="z", face=False)
    sh.region("M55 77A15 15 0 0 1 85 77Q86 64 70 62Q54 64 55 77Z", "z"); sh.circle_r(70, 60, 6, "z")
    sh.circle_line(65, hy + 3, 4.5); sh.circle_line(75, hy + 3, 4.5); sh.seg(69.5, hy + 3, 70.5, hy + 3)
    eye(sh, 65, hy + 3, 1.6); eye(sh, 75, hy + 3, 1.6); smile(sh, 70, hy + 9, 4)
    sh.rect_r(20, 136, 180, 10, "o"); sh.rect_r(28, 146, 164, 54, "o")
    sh.rect_r(40, 156, 50, 34, "-", 2); sh.rect_r(110, 156, 70, 34, "-", 2)
    sh.region("M48 136Q60 128 70 134Q80 128 92 136V140H48Z", "-"); sh.seg(70, 134, 70, 140)
    for k, (c, w) in enumerate((("r", 40), ("b", 34), ("y", 38), ("g", 30))):
        sh.rect_r(150 - w / 2, 128 - k * 8, w, 8, c, 1)
    sh.rect_r(112, 124, 10, 12, "w", 1); sh.ellipse_r(117, 122, 7, 3, "x")

def dirigent(sh):
    sh.rect_r(0, 0, 200, 200, "k")
    sh.rect_r(0, 168, 200, 32, "w")
    sh.region("M0 0H42Q30 60 40 120Q30 150 36 168H0Z", "r"); sh.region("M200 0H158Q170 60 160 120Q170 150 164 168H200Z", "r")
    sh.region("M0 0H200V16Q150 30 100 16Q50 30 0 16Z", "r")
    sh.rect_r(60, 150, 80, 24, "o", 2)
    person(sh, 100, 46, "x", "x", hands=((134, 62), (64, 72)), hair="z", shoes="x")
    sh.region("M95 77H105L100 92Z", "-"); sh.region("M93 76L100 80L107 76V84L100 80L93 84Z", "r")
    sh.line("M136 60L158 36", "l", "stroke-width:2")
    for x, y, c in ((40, 50, "p"), (156, 80, "b"), (30, 110, "y"), (170, 128, "m"), (56, 136, "g"), (150, 30, "o")):
        sh.raw(f'<g transform="rotate(-20 {x} {y})">'); sh.ellipse_r(x, y, 5, 3.6, c); sh.raw("</g>")
        sh.line(f"M{x + 4.5} {y - 1}V{y - 16}Q{x + 10} {y - 12} {x + 11} {y - 6}")

def timmerman(sh):
    sh.rect_r(0, 176, 200, 24, "w")
    for x in (40, 120): sh.seg(x, 176, x, 200)
    sh.rect_r(98, 122, 98, 10, "w"); sh.rect_r(104, 132, 8, 46, "w"); sh.rect_r(182, 132, 8, 46, "w"); sh.rect_r(112, 150, 70, 6, "w")
    sh.rect_r(124, 96, 34, 26, "o"); sh.region("M118 98L141 76L164 98Z", "r"); sh.circle_r(141, 106, 5, "x")
    sh.rect_r(139, 114, 4, 8, "w")
    sh.region("M160 120L190 112V120Z", "z"); sh.line("M160 120L163 117L166 120L169 116L172 120L175 115L178 120L181 114L184 120L187 113")
    sh.region("M186 104H198V120H190Z", "r")
    hy = person(sh, 54, 66, "r", "n", hands=((32, 128), (84, 92)), cap=True)
    sh.region("M40 78Q40 62 54 62Q68 62 68 78Z", "y"); sh.rect_r(38, 76, 34, 5, "y", 2)
    sh.line(f"M42 {hy + 30}H66M42 {hy + 44}H66")
    sh.rect_r(37, 132, 34, 8, "w", 2); sh.rect_r(40, 140, 8, 10, "w", 1)
    limb(sh, 80, 98, 96, 74, "w", 5)
    sh.raw('<g transform="rotate(36 98 71)">'); sh.rect_r(88, 66, 22, 10, "z", 2); sh.raw("</g>")
    sh.line("M108 64L114 58M110 72L118 72M106 56L108 50")
    for k in range(3): sh.rect_r(8 + k * 6, 112 - k * 2, 5, 64 + k * 2, "y", 1)

def imker(sh):
    grass(sh, 178)
    sh.circle_r(30, 28, 12, "y")
    sh.rect_r(130, 152, 6, 28, "w"); sh.rect_r(176, 152, 6, 28, "w")
    sh.rect_r(124, 128, 64, 24, "y"); sh.rect_r(124, 104, 64, 24, "o"); sh.rect_r(118, 96, 76, 8, "w", 1)
    sh.rect_r(146, 144, 20, 4, "x")
    hy = person(sh, 66, 64, "-", "-", hands=((40, 132), (94, 112)), cap=True, shoes="z")
    sh.line(f"M48 {hy - 3}L52 {hy + 16}M84 {hy - 3}L80 {hy + 16}")
    sh.line(f"M50 {hy + 6}H54M78 {hy + 6}H82", "l", "stroke-width:1")
    sh.region(f"M50 {hy - 4}Q50 {hy - 20} 66 {hy - 20}Q82 {hy - 20} 82 {hy - 4}Z", "y")
    sh.ellipse_r(66, hy - 4, 26, 5, "y")
    sh.rect_r(92, 92, 26, 34, "w", 1); sh.rect_r(96, 96, 18, 26, "y")
    for row in range(3):
        for col in range(2):
            cx, cy = 101 + col * 8 + (row % 2) * 4, 101 + row * 8
            if cx < 113: sh.circle_line(cx, cy, 3, "l", "stroke-width:.9")
    sh.circle_r(94, 112, 4.5, "-")
    sh.rect_r(30, 132, 18, 22, "z", 2); sh.region("M32 132L39 124L46 132Z", "z"); sh.region(cloud_path(40, 112, 9), "-")
    for x, y in ((112, 60), (150, 74), (176, 54), (20, 82), (190, 92)):
        sh.ellipse_r(x - 2, y - 5, 4, 3, "-"); sh.ellipse_r(x + 3, y - 5, 4, 3, "-")
        sh.ellipse_r(x, y, 6, 4, "y"); sh.seg(x - 1, y - 4, x - 1, y + 4); sh.seg(x + 2, y - 3.6, x + 2, y + 3.6)
    sh.rect_r(150, 168, 22, 26, "o", 3); sh.rect_r(148, 162, 26, 7, "r", 2); sh.rect_r(152, 174, 18, 10, "-", 1)
    sh.text(161, 181.5, "honing", 4.5)
    flower(sh, 104, 182, 5, "m"); flower(sh, 20, 186, 5, "p")


PLATES = [
    ("spinosaurus", "Spinosaurus vangt een vis", "dinos", "6-9", 2, spinosaurus),
    ("pachycephalosaurus", "Twee pachycephalosaurussen", "dinos", "6-9", 2, pachycephalosaurus),
    ("plesiosaurus", "Plesiosaurus in de zee", "dinos", "4-6", 2, plesiosaurus),
    ("velociraptor", "Snelle raptor", "dinos", "6-9", 2, velociraptor),
    ("dino-skelet", "Dinoskelet in het museum", "dinos", "9+", 3, dino_skelet),
    ("dinosporen", "Dinosporen in de modder", "dinos", "4-6", 2, dinosporen),
    ("dino-familie", "Dinofamilie bij de vulkaan", "dinos", "4-6", 2, dino_familie),
    # ("iguanodon", "Iguanodon eet blaadjes", "dinos", "6-9", 2, iguanodon),
    # ("archeopteryx", "Archeopteryx op een tak", "dinos", "6-9", 2, archeopteryx),
    ("dino-opgraving", "Dinobotten opgraven", "dinos", "6-9", 3, dino_opgraving),
    ("ruimtestation", "Ruimtestation", "ruimte", "6-9", 2, ruimtestation),
    ("planeetrover", "Rover op een planeet", "ruimte", "6-9", 2, planeetrover),
    ("telescoop", "Sterrenkijken met een telescoop", "ruimte", "4-6", 2, telescoop),
    ("sterrenbeelden", "Sterrenbeelden: Steelpan en Cassiopeia", "ruimte", "9+", 2, sterrenbeelden),
    ("alienvriendje", "Alienvriendje", "ruimte", "4-6", 1, alienvriendje),
    ("astronaut-op-de-maan", "Astronaut op de maan", "ruimte", "4-6", 2, astronaut_maan),
    ("raketlancering", "Raketlancering", "ruimte", "4-6", 2, raketlancering),
    ("ruimtehelm", "Kind in een ruimtehelm", "ruimte", "4-6", 1, ruimtehelm),
    ("volle-maan", "Volle maan met kraters", "ruimte", "4-6", 1, volle_maan),
    ("zonsverduistering", "Zonsverduistering", "ruimte", "6-9", 2, zonsverduistering),
    ("wielrenner", "Wielrenner", "sport", "6-9", 3, wielrenner),
    ("skier", "Skiën", "sport", "6-9", 2, skier),
    ("tafeltennis", "Tafeltennis", "sport", "6-9", 2, tafeltennis),
    ("duiker", "Duiker onder water", "sport", "4-6", 2, duiker),
    ("karate", "Karatetrap", "sport", "6-9", 2, karate),
    ("wetenschapper", "Wetenschapper met proefbuisjes", "beroepen", "6-9", 2, wetenschapper),
    ("bibliothecaris", "Bibliothecaris", "beroepen", "6-9", 3, bibliothecaris),
    ("dirigent", "Dirigent", "beroepen", "4-6", 2, dirigent),
    ("timmerman", "Timmerman", "beroepen", "6-9", 2, timmerman),
    ("imker", "Imker bij de bijenkasten", "beroepen", "6-9", 2, imker),
]

for slug, name, cat, age, diff, draw in PLATES:
    kp(slug, name, cat, age, diff, draw)
