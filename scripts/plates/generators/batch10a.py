"""Batch 10a: nieuwe kleurplaten (eigen tekeningen, 200x200): kinderen die iets doen, seizoenen, Nederland, beroepen en fantasie."""
import math
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from shapes import heart_path, star_path, moon_path, cloud_path, leaf_path, fish_path, drop_path


# ---------- hulpjes ----------
def limb(sh, x1, y1, x2, y2, code, w=9):
    """Arm of been als balk met afgeronde uiteinden van (x1,y1) naar (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * w / 2, dx / d * w / 2
    r = w / 2
    sh.region(f"M{f(x1 + nx)} {f(y1 + ny)}L{f(x2 + nx)} {f(y2 + ny)}A{f(r)} {f(r)} 0 0 0 {f(x2 - nx)} {f(y2 - ny)}L{f(x1 - nx)} {f(y1 - ny)}A{f(r)} {f(r)} 0 0 0 {f(x1 + nx)} {f(y1 + ny)}Z", code)

def blob(cx, cy, rx, ry, n=9, bulge=.62, start=0):
    """Bobbelige rand (boomkruin, struik, wolk) rond een ellips."""
    p = [(cx + rx * math.cos(2 * math.pi * i / n + start), cy + ry * math.sin(2 * math.pi * i / n + start)) for i in range(n)]
    d = f"M{f(p[0][0])} {f(p[0][1])}"
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        r = math.hypot(b[0] - a[0], b[1] - a[1]) * bulge
        d += f"A{f(r)} {f(r)} 0 0 1 {f(b[0])} {f(b[1])}"
    return d + "Z"

def sparkle(sh, x, y, r=5, code="y"):
    sh.region(f"M{f(x)} {f(y - r)}Q{f(x + r * .2)} {f(y - r * .2)} {f(x + r)} {f(y)}Q{f(x + r * .2)} {f(y + r * .2)} {f(x)} {f(y + r)}Q{f(x - r * .2)} {f(y + r * .2)} {f(x - r)} {f(y)}Q{f(x - r * .2)} {f(y - r * .2)} {f(x)} {f(y - r)}Z", code)

def flower(sh, x, y, r=5, petal="m", heart="y"):
    for k in range(5):
        a = math.radians(k * 72 - 90)
        sh.circle_r(x + r * math.cos(a), y + r * math.sin(a), r * .7, petal)
    sh.circle_r(x, y, r * .55, heart)

def leaf_at(sh, x, y, w, h, rot, code):
    sh.raw(f'<g transform="rotate({rot} {f(x)} {f(y)})">'); sh.region(leaf_path(x, y, w, h), code); sh.raw("</g>")

def hair_back(sh, cx, hy, s, style, code):
    r = 15 * s
    if style == "long":
        sh.region(f"M{f(cx - r)} {f(hy)}C{f(cx - r - 5 * s)} {f(hy + 14 * s)} {f(cx - r - 5 * s)} {f(hy + 24 * s)} {f(cx - 14 * s)} {f(hy + 28 * s)}H{f(cx + 14 * s)}C{f(cx + r + 5 * s)} {f(hy + 24 * s)} {f(cx + r + 5 * s)} {f(hy + 14 * s)} {f(cx + r)} {f(hy)}A{f(r)} {f(r)} 0 0 0 {f(cx - r)} {f(hy)}Z", code)
    elif style == "curly":
        for k in range(10):
            a = math.radians(158 + k * 25)
            sh.circle_r(cx + (r + 1 * s) * math.cos(a), hy + (r + 1 * s) * math.sin(a), 6 * s, code)
    elif style == "pony":
        sh.region(f"M{f(cx + 10 * s)} {f(hy - 11 * s)}Q{f(cx + 30 * s)} {f(hy - 14 * s)} {f(cx + 25 * s)} {f(hy + 12 * s)}Q{f(cx + 21 * s)} {f(hy + 2 * s)} {f(cx + 13 * s)} {f(hy - 2 * s)}Z", code)
    elif style == "braids":
        for side in (-1, 1):
            for k in range(3):
                sh.circle_r(cx + side * 16 * s, hy + (6 + k * 7) * s, 4.2 * s, code)
            sh.circle_r(cx + side * 16 * s, hy + 28 * s, 2.2 * s, "r")
    elif style == "bun":
        sh.circle_r(cx, hy - 16 * s, 7 * s, code)

def hair_front(sh, cx, hy, s, style, code):
    r = 15 * s
    top = f"M{f(cx - r)} {f(hy)}A{f(r)} {f(r)} 0 0 1 {f(cx + r)} {f(hy)}"
    if style in ("long", "braids", "bun"):
        sh.region(top + f"Q{f(cx + 7 * s)} {f(hy - 11 * s)} {f(cx)} {f(hy - 9 * s)}Q{f(cx - 7 * s)} {f(hy - 11 * s)} {f(cx - r)} {f(hy)}Z", code)
    elif style == "curly":
        sh.region(top + f"Q{f(cx + 11 * s)} {f(hy - 3 * s)} {f(cx + 7 * s)} {f(hy - 8 * s)}Q{f(cx + 3 * s)} {f(hy - 3 * s)} {f(cx - 1 * s)} {f(hy - 8 * s)}Q{f(cx - 5 * s)} {f(hy - 3 * s)} {f(cx - 9 * s)} {f(hy - 8 * s)}Q{f(cx - 13 * s)} {f(hy - 3 * s)} {f(cx - r)} {f(hy)}Z", code)
    elif style == "back":  # achterkant van het hoofd: helemaal haar
        sh.circle_r(cx, hy, r, code)
    else:
        sh.region(top + f"Q{f(cx + 8 * s)} {f(hy - 9 * s)} {f(cx - 2 * s)} {f(hy - 7 * s)}Q{f(cx - 10 * s)} {f(hy - 6 * s)} {f(cx - r)} {f(hy)}Z", code)

def person(sh, cx, top, shirt="-", pants="-", hands=None, hair="w", style="short", legs=None, cap=False, shoes="x",
           face=True, s=1, skirt=None, arms=None, arms_front=False, draw_legs=True, draw_hands=True, hand="-"):
    """Kind/volwassene van voren (of van achteren met style="back"). top = bovenkant hoofd, s = schaal.
    hands/legs = absolute posities van handen/voeten."""
    hy = top + 15 * s
    arms = arms or shirt
    sl, sr = (cx - 13 * s, hy + 24 * s), (cx + 13 * s, hy + 24 * s)
    hl, hr = hands or ((cx - 22 * s, hy + 52 * s), (cx + 22 * s, hy + 52 * s))
    hip_l, hip_r = (cx - 8 * s, hy + 54 * s), (cx + 8 * s, hy + 54 * s)
    fl, fr = legs or ((cx - 8 * s, hy + 86 * s), (cx + 8 * s, hy + 86 * s))
    if draw_legs:
        limb(sh, *hip_l, *fl, pants, 12 * s); limb(sh, *hip_r, *fr, pants, 12 * s)
        if shoes:
            sh.ellipse_r(fl[0] - 3 * s, fl[1] + 3 * s, 8 * s, 4.5 * s, shoes); sh.ellipse_r(fr[0] + 3 * s, fr[1] + 3 * s, 8 * s, 4.5 * s, shoes)
    if not arms_front:
        limb(sh, *sl, *hl, arms, 10 * s); limb(sh, *sr, *hr, arms, 10 * s)
    sh.region(f"M{f(cx - 17 * s)} {f(hy + 58 * s)}V{f(hy + 30 * s)}Q{f(cx - 17 * s)} {f(hy + 17 * s)} {f(cx - 5 * s)} {f(hy + 16 * s)}H{f(cx + 5 * s)}Q{f(cx + 17 * s)} {f(hy + 17 * s)} {f(cx + 17 * s)} {f(hy + 30 * s)}V{f(hy + 58 * s)}Z", shirt)
    if skirt:
        sh.region(f"M{f(cx - 17 * s)} {f(hy + 46 * s)}H{f(cx + 17 * s)}L{f(cx + 25 * s)} {f(hy + 68 * s)}H{f(cx - 25 * s)}Z", skirt)
    if arms_front:
        limb(sh, *sl, *hl, arms, 10 * s); limb(sh, *sr, *hr, arms, 10 * s)
    if hair and style not in ("short", "back"):
        hair_back(sh, cx, hy, s, style, hair)
    sh.circle_r(cx, hy, 15 * s, "-")
    if hair and (not cap or style == "back"):
        hair_front(sh, cx, hy, s, style, hair)
    if face and style != "back":
        eye(sh, cx - 5 * s, hy + 3 * s, 1.8 * s); eye(sh, cx + 5 * s, hy + 3 * s, 1.8 * s); smile(sh, cx, hy + 8 * s, 4 * s)
    if draw_hands:
        sh.circle_r(hl[0], hl[1], 4.5 * s, hand); sh.circle_r(hr[0], hr[1], 4.5 * s, hand)
    return hy

def shorts(sh, cx, hy, code, s=1):
    sh.region(f"M{f(cx - 17 * s)} {f(hy + 48 * s)}H{f(cx + 17 * s)}L{f(cx + 18 * s)} {f(hy + 66 * s)}H{f(cx + 2 * s)}L{f(cx)} {f(hy + 60 * s)}L{f(cx - 2 * s)} {f(hy + 66 * s)}H{f(cx - 18 * s)}Z", code)

def beanie(sh, cx, hy, code, rim="-", s=1):
    sh.region(f"M{f(cx - 16 * s)} {f(hy - 2 * s)}Q{f(cx - 16 * s)} {f(hy - 20 * s)} {f(cx)} {f(hy - 20 * s)}Q{f(cx + 16 * s)} {f(hy - 20 * s)} {f(cx + 16 * s)} {f(hy - 2 * s)}Z", code)
    sh.rect_r(cx - 17 * s, hy - 6 * s, 34 * s, 7 * s, rim, 3 * s)
    sh.circle_r(cx, hy - 21 * s, 5 * s, rim)

def scarf(sh, cx, hy, code, s=1):
    sh.region(f"M{f(cx + 3 * s)} {f(hy + 17 * s)}L{f(cx + 6 * s)} {f(hy + 36 * s)}H{f(cx + 13 * s)}L{f(cx + 10 * s)} {f(hy + 17 * s)}Z", code)
    sh.rect_r(cx - 12 * s, hy + 12 * s, 24 * s, 7 * s, code, 3 * s)

def pine(sh, x, base, h, code="g", snow=False, trunk="w"):
    sh.rect_r(x - 3, base - 8, 6, 8, trunk)
    for k in range(3):
        y0 = base - 8 - k * h / 3.6; w = h * (.42 - k * .1)
        sh.region(f"M{f(x - w)} {f(y0)}L{f(x)} {f(y0 - h / 2.2)}L{f(x + w)} {f(y0)}Z", code)
        if snow:
            sh.region(f"M{f(x - w * .35)} {f(y0 - h / 2.2 * .65)}L{f(x)} {f(y0 - h / 2.2)}L{f(x + w * .35)} {f(y0 - h / 2.2 * .65)}Q{f(x)} {f(y0 - h / 2.2 * .55)} {f(x - w * .35)} {f(y0 - h / 2.2 * .65)}Z", "-")

def sun(sh, x, y, r=12, rays=True):
    sh.circle_r(x, y, r, "y")
    if rays:
        for k in range(8):
            a = math.radians(k * 45 + 22)
            sh.seg(x + (r + 3) * math.cos(a), y + (r + 3) * math.sin(a), x + (r + 8) * math.cos(a), y + (r + 8) * math.sin(a))

def bird(sh, x, y, w=6):
    sh.line(f"M{f(x - w)} {f(y)}Q{f(x - w / 2)} {f(y - w * .6)} {f(x)} {f(y)}Q{f(x + w / 2)} {f(y - w * .6)} {f(x + w)} {f(y)}")


# ---------- kinderen die iets doen ----------
def boomhut(sh):
    grass(sh, 184)
    sh.region(blob(100, 61, 86, 52, 12), "g")
    sh.region("M86 186C92 160 92 120 90 100H112C110 120 110 160 116 186Z", "w")
    sh.line("M76 186Q86 182 90 172M126 186Q114 182 112 172M98 140Q102 150 100 160")
    sh.line("M54 108L92 128M146 108L110 128")
    sh.rect_r(38, 100, 124, 8, "w", 1)
    sh.rect_r(58, 64, 70, 36, "o"); sh.line("M58 76H128M58 88H128")
    sh.rect_r(68, 70, 22, 18, "b", 1); sh.seg(79, 70, 79, 88); sh.seg(68, 79, 90, 79)
    sh.rect_r(104, 72, 16, 28, "r", 1); sh.dot(116, 87, 1.3)
    sh.poly_r([(50, 66), (93, 36), (136, 66)], "r")
    sh.line("M93 36V20"); sh.poly_r([(93, 20), (110, 24), (93, 29)], "y")
    # kind op het platform, zwaaiend
    person(sh, 146, 45, "m", "n", hands=((134, 76), (166, 52)), s=.55, style="curly", hair="x")
    sh.line("M38 100V108")
    # touwladder met kind dat naar boven klimt (van achteren)
    sh.line("M56 108V186M72 108V186")
    for y in range(118, 186, 12): sh.seg(56, y, 72, y)
    person(sh, 64, 128, "y", "n", hands=((57, 130), (71, 126)), legs=((59, 178), (69, 168)), s=.58, style="back", hair="w")
    sh.region(heart_path(150, 120, 6), "r")
    bird(sh, 20, 30); bird(sh, 34, 22, 5)

def voorlezen(sh):
    sh.rect_r(0, 186, 200, 14, "w")
    sh.rect_r(78, 12, 44, 32, "y", 2); sh.rect_r(84, 18, 32, 20, "-"); sh.region(heart_path(100, 28, 7), "r")
    sh.rect_r(14, 70, 172, 80, "r", 14)
    sh.line("M100 74V112")
    # volwassene links, kind rechts
    person(sh, 66, 40, "g", "n", hands=((48, 106), (82, 112)), style="long", hair="w", draw_legs=False, arms_front=True, draw_hands=False)
    person(sh, 132, 60, "y", "b", hands=((118, 112), (148, 108)), style="curly", hair="x", s=.72, draw_legs=False, arms_front=True, draw_hands=False)
    sh.rect_r(22, 110, 156, 30, "r", 8)
    sh.rect_r(4, 96, 26, 70, "r", 10); sh.rect_r(170, 96, 26, 70, "r", 10)
    for x in (12, 180): sh.rect_r(x, 166, 8, 18, "w")
    # onderbenen
    for x in (58, 74): limb(sh, x, 136, x, 176, "n", 11); sh.ellipse_r(x + (-3 if x < 66 else 3), 179, 8, 4.5, "x")
    for x in (126, 138): limb(sh, x, 136, x, 160, "b", 8.5); sh.ellipse_r(x + (-2 if x < 132 else 2), 162, 6, 3.5, "x")
    # boek
    sh.region("M100 96Q90 90 76 94V118Q90 114 100 120Z", "-"); sh.region("M100 96Q110 90 124 94V118Q110 114 100 120Z", "-")
    sh.region("M76 118Q90 114 100 120Q110 114 124 118V121Q110 117 100 123Q90 117 76 121Z", "b")
    for y in (100, 105, 110): sh.line(f"M80 {y}Q88 {y - 3} 96 {y + 1}M104 {y + 1}Q112 {y - 3} 120 {y}", "l", "stroke-width:1")
    for x, y, r in ((48, 106, 4.5), (78, 112, 4.5), (122, 110, 3.3), (148, 108, 3.3)): sh.circle_r(x, y, r, "-")
    sh.circle_r(160, 30, 6, "y"); sh.region(star_path(30, 30, 7, 3), "y")

def verstoppertje(sh):
    grass(sh, 182)
    sh.region("M20 184V70H42V184Z", "w"); sh.line("M26 120Q30 126 28 134M36 96Q34 102 36 108")
    sh.region(blob(34, 46, 30, 30, 9), "g")
    # kind dat telt, handen voor de ogen
    hy = person(sh, 72, 84, "r", "n", hands=((66, 101), (78, 101)), style="pony", hair="y", face=False, arms_front=True)
    smile(sh, 72, hy + 9, 3.5)
    sh.text(98, 74, "... 8, 9, 10!", 8, "start")
    # kind achter de struik
    hair_back(sh, 154, 112, 1, "curly", "x"); sh.circle_r(154, 112, 15, "-"); hair_front(sh, 154, 112, 1, "curly", "x")
    eye(sh, 147, 112, 2); eye(sh, 155, 112, 2)
    sh.region(blob(152, 154, 42, 30, 10), "g")
    sh.circle_r(134, 126, 4.5, "-"); sh.circle_r(170, 126, 4.5, "-")
    sh.ellipse_r(182, 182, 8, 4.5, "o"); sh.ellipse_r(192, 180, 6, 4.5, "o")
    flower(sh, 112, 176, 5, "m"); flower(sh, 104, 186, 4, "y", "o")
    sh.region("M128 30Q120 22 124 18Q130 18 130 28Q134 18 140 20Q142 26 132 32Z", "p"); sh.line("M130 30L132 34")

def zwembad(sh):
    sun(sh, 172, 24, 11); sh.region(cloud_path(120, 22, 12), "-")
    sh.rect_r(0, 96, 200, 80, "b")
    for y in (124, 146, 166):
        for x in range(8 if y != 146 else 30, 200, 44): sh.line(f"M{x} {y}Q{x + 8} {y - 4} {x + 16} {y}")
    sh.rect_r(0, 176, 200, 24, "-")
    for x in range(20, 200, 20): sh.seg(x, 176, x, 200, "l", "stroke-width:1")
    sh.seg(0, 188, 200, 188, "l", "stroke-width:1")
    # duikplank
    sh.rect_r(0, 80, 18, 96, "z"); sh.rect_r(0, 74, 66, 6, "-", 2)
    # springend kind
    hy = person(sh, 104, 6, "-", "-", hands=((84, 8), (124, 8)), legs=((88, 88), (120, 88)), shoes=None, style="short", hair="o", s=.8)
    shorts(sh, 104, hy, "n", .8)
    for x, y in ((70, 40), (138, 40), (72, 60), (136, 60)): sh.line(f"M{x} {y}h{-6 if x < 100 else 6}", "l", "stroke-width:1.4")
    # kind met zwemband
    sh.circle_r(160, 132, 10, "-"); hair_front(sh, 160, 132, .67, "long", "x"); eye(sh, 157, 133, 1.4); eye(sh, 163, 133, 1.4); smile(sh, 160, 137, 3)
    sh.region("M136 142A24 9 0 0 0 184 142A24 9 0 0 0 136 142ZM148 142A12 4 0 0 1 172 142A12 4 0 0 1 148 142Z", "r")
    sh.circle_r(140, 132, 4, "-"); sh.circle_r(180, 132, 4, "-")
    # trapje
    sh.line("M180 176V158Q180 150 188 150M192 176V158Q192 150 198 150"); sh.seg(180, 166, 192, 166)

def sneeuwballen(sh):
    sh.region("M0 200V150Q60 140 120 152T200 146V200Z", "-")
    pine(sh, 100, 150, 70, "g", True)
    for x, y in ((14, 20), (40, 40), (70, 14), (120, 30), (150, 14), (184, 36), (24, 90), (178, 92), (130, 70), (60, 66)):
        sh.circle_r(x, y, 2.4, "-")
    # gooiend kind
    hy = person(sh, 52, 76, "b", "n", hands=((30, 120), (78, 66)), cap=True, hand="r")
    beanie(sh, 52, hy, "r"); scarf(sh, 52, hy, "y")
    sh.circle_r(82, 60, 6, "-")
    # kind dat bukt
    hy = person(sh, 152, 84, "o", "p", hands=((134, 90), (172, 88)), cap=True, s=.9, face=False, hand="g")
    beanie(sh, 152, hy, "g", "-", .9); scarf(sh, 152, hy, "m", .9)
    eye(sh, 148, hy + 3, 1.7); eye(sh, 156, hy + 3, 1.7); sh.circle_r(152, hy + 9, 2.4, "-")
    # vliegende sneeuwbal
    sh.circle_r(120, 52, 6, "-"); sh.line("M96 50H108M98 57H110", "l", "stroke-width:1.4")
    for x, y in ((92, 176), (104, 176), (98, 166)): sh.circle_r(x, y, 6, "-")

def tekenen_aan_tafel(sh):
    sh.rect_r(0, 186, 200, 14, "w")
    sh.rect_r(16, 16, 40, 32, "-", 1); sh.circle_r(28, 26, 5, "y"); sh.region("M34 44V34L42 28L50 34V44Z", "r")
    sh.rect_r(146, 20, 38, 30, "-", 1); flower(sh, 165, 32, 5, "m"); sh.line("M165 38V48")
    for x, y in ((36, 14), (165, 18)): sh.rect_r(x - 5, y - 1, 10, 4, "z")
    person(sh, 100, 40, "y", "n", hands=((80, 116), (120, 112)), style="braids", hair="x", draw_legs=False, arms_front=True, draw_hands=False)
    sh.region("M24 112H176L192 134H8Z", "w"); sh.rect_r(8, 134, 184, 8, "w")
    for x in (16, 176): sh.rect_r(x, 142, 8, 44, "w")
    sh.region("M70 114H132L136 130H66Z", "-")
    sun(sh, 80, 121, 3, False); sh.line("M92 126Q100 118 108 126T124 124", "l", "stroke-width:1.4")
    limb(sh, 122, 112, 128, 124, "r", 4)
    sh.circle_r(80, 116, 4.5, "-"); sh.circle_r(120, 112, 4.5, "-")
    for (x1, y1, x2, y2), c in (((28, 126, 46, 122), "b"), ((34, 131, 54, 129), "g"), ((148, 122, 166, 126), "p")): limb(sh, x1, y1, x2, y2, c, 4)
    sh.rect_r(152, 100, 16, 16, "o", 2)
    for x, c in ((156, "r"), (160, "b"), (164, "g")): limb(sh, x, 100, x + (x - 160) * .4, 90, c, 3)

def tandenpoetsen(sh):
    for y in (32, 64, 96): sh.seg(0, y, 200, y, "l", "stroke-width:.9")
    for x in range(25, 200, 50):
        for y0 in (0, 32, 64):
            sh.seg(x + (25 if y0 == 32 else 0), y0, x + (25 if y0 == 32 else 0), y0 + 32, "l", "stroke-width:.9")
    sh.rect_r(138, 16, 52, 70, "b", 24); sh.line("M150 32L160 24M150 44L170 26", "l", "stroke-width:1.2")
    hy = person(sh, 84, 30, "t", "-", hands=((114, 60), (60, 104)), style="short", hair="w", face=False, s=1.2, draw_legs=False)
    for x, y in ((72, 92), (96, 98)): sh.region(star_path(x, y, 4, 1.7), "y")
    eye(sh, 78, hy + 2, 2.1); eye(sh, 90, hy + 2, 2.1)
    sh.ellipse_r(84, hy + 10, 4.5, 3, "-")
    limb(sh, 86, hy + 10, 112, hy + 12, "b", 4.5)
    for x, y, r in ((76, hy + 12, 2.4), (79, hy + 16, 2)): sh.circle_r(x, y, r, "-")
    sh.circle_r(114, 60, 5.4, "-")
    sh.rect_r(0, 108, 200, 12, "-")
    sh.region("M44 108V94H52V108ZM52 97H66V104H60V101H52Z", "z")
    sh.region("M36 120H144Q140 156 90 158Q40 156 36 120Z", "-"); sh.line("M54 128Q90 140 126 128", "l", "stroke-width:1.4")
    sh.rect_r(78, 158, 24, 42, "-")
    sh.rect_r(150, 90, 16, 18, "g", 2); limb(sh, 156, 90, 152, 70, "p", 3.5); sh.rect_r(148, 64, 6, 6, "-", 1)
    sh.rect_r(170, 99, 22, 9, "r", 3); sh.rect_r(192, 101, 5, 5, "-", 1)

def boodschappen(sh):
    sh.rect_r(0, 186, 200, 14, "z")
    for y in (50, 96): sh.rect_r(0, y, 200, 5, "w")
    for x, h, c in ((10, 26, "g"), (24, 30, "b"), (38, 26, "r")):
        sh.region(f"M{x} 50V{50 - h + 8}Q{x} {50 - h + 4} {x + 3} {50 - h + 2}V{50 - h}H{x + 7}V{50 - h + 2}Q{x + 10} {50 - h + 4} {x + 10} {50 - h + 8}V50Z", c)
    for x, c in ((60, "y"), (80, "o"), (100, "m")): sh.rect_r(x, 26, 18, 24, c, 1)
    for x in (126, 140, 154, 168, 182): sh.rect_r(x - 5, 36, 11, 14, "z", 2); sh.seg(x - 5, 40, x + 6, 40)
    for x in (10, 22, 34, 46): sh.circle_r(x, 89, 6, "r"); sh.line(f"M{x} 83L{x + 2} 80")
    # boodschappen in de kar
    sh.ellipse_r(120, 106, 14, 8, "w"); sh.line("M112 102L116 110M120 100L124 108M128 102L130 108")
    sh.region("M138 112V90L144 84H152L158 90V112Z", "b"); sh.seg(138, 90, 158, 90)
    sh.circle_r(166, 106, 7, "r"); sh.line("M166 99L168 95")
    sh.region("M172 110Q182 88 176 80L180 80Q190 96 178 112Z", "y")
    # winkelwagen
    sh.region("M96 110H186L176 150H108Z", "-")
    for x in range(106, 180, 10): sh.seg(x, 110, x - (x - 96) * 0.12 + 1, 150, "l", "stroke-width:1.1")
    for y in (124, 137): sh.seg(96 + (y - 110) * .3, y, 186 - (y - 110) * .25, y, "l", "stroke-width:1.1")
    sh.line("M96 110L86 98"); sh.rect_r(78, 93, 12, 7, "r", 3)
    sh.line("M108 150L112 172M176 150L172 172M104 172H182")
    sh.circle_r(112, 178, 6, "x"); sh.circle_r(172, 178, 6, "x")
    # kind
    person(sh, 56, 82, "o", "n", hands=((80, 98), (34, 128)), style="pony", hair="o", s=.95)
    sh.rect_r(22, 126, 14, 16, "-", 1); sh.line("M25 131H33M25 135H33", "l", "stroke-width:1")

def kamperen(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region("M0 200V160Q100 150 200 160V200Z", "g")
    sh.region(moon_path(170, 28, 13), "y")
    for x, y, r in ((24, 22, 5), (60, 40, 4), (110, 16, 5), (140, 50, 4), (92, 48, 3.5)): sh.region(star_path(x, y, r, r * .45), "y")
    pine(sh, 34, 164, 80, "g")
    # tent (nokje naar achteren)
    sh.region("M100 66L146 58L186 152L144 164Z", "o"); sh.line("M146 58L150 52")
    sh.region("M56 164L100 66L144 164Z", "o"); sh.line("M100 66L98 58")
    sh.region("M78 164L100 108L122 164Z", "-")
    sh.region("M100 106L78 164H90Q86 132 100 106Z", "y"); sh.region("M100 106L122 164H110Q114 132 100 106Z", "y")
    # kind in slaapzak met zaklamp
    sh.region("M88 164Q86 146 100 144Q114 146 112 164Z", "p")
    sh.circle_r(100, 138, 9, "-"); hair_front(sh, 100, 138, .6, "short", "w"); eye(sh, 97, 139, 1.3); eye(sh, 103, 139, 1.3); smile(sh, 100, 142, 2.4)
    sh.region("M60 160L70 154L74 160L66 166Z", "z")
    sh.line("M56 164L46 172M186 152L194 158")
    # kampvuurtje
    sh.line("M24 190L50 180M24 180L50 190")
    sh.region("M28 184C24 174 34 168 36 158C40 168 48 172 44 184Z", "r"); sh.region("M32 184C30 178 36 174 37 168C40 174 44 178 41 184Z", "y")

def picknick(sh):
    sh.region("M0 200V108Q100 100 200 108V200Z", "l")
    sun(sh, 176, 24, 11); sh.region(cloud_path(110, 26, 12), "-")
    sh.rect_r(26, 60, 12, 54, "w"); sh.region(blob(32, 44, 28, 24, 9), "g")
    # kinderen achter het kleed
    person(sh, 62, 74, "p", "n", hands=((42, 130), (84, 110)), style="braids", hair="w", s=.9, draw_legs=False)
    person(sh, 140, 80, "r", "n", hands=((122, 114), (160, 132)), style="short", hair="x", s=.85, draw_legs=False)
    sh.poly_r([(84, 110), (96, 98), (98, 114)], "y"); sh.line("M86 110L96 106", "l", "stroke-width:1")
    sh.circle_r(84, 110, 4, "-")
    sh.circle_r(120, 108, 6, "r"); sh.line("M120 102L122 98"); sh.circle_r(122, 114, 3.8, "-")
    # geruit kleed
    def q(u, v):
        x0, y0 = 30 + 140 * u, 140; x1, y1 = 4 + 192 * u, 196
        return (x0 + (x1 - x0) * v, y0 + (y1 - y0) * v)
    for i in range(6):
        for j in range(3):
            pts = [q(i / 6, j / 3), q((i + 1) / 6, j / 3), q((i + 1) / 6, (j + 1) / 3), q(i / 6, (j + 1) / 3)]
            sh.poly_r(pts, "r" if (i + j) % 2 == 0 else "-")
    # mand, broodjes en drinken
    sh.region("M84 150H118L114 174H88Z", "w"); sh.line("M86 158H116M87 166H115"); sh.line("M88 150Q101 132 114 150")
    sh.ellipse_r(54, 176, 16, 6, "-"); sh.poly_r([(44, 175), (56, 166), (62, 177)], "y")
    sh.circle_r(146, 174, 6, "r"); sh.circle_r(158, 178, 6, "g")
    sh.rect_r(168, 148, 10, 22, "o", 2); sh.rect_r(170, 142, 6, 6, "-")
    sh.region("M176 72Q168 64 172 60Q178 60 178 70Q182 60 188 62Q190 68 180 74Z", "y")

def zandkasteel(sh):
    sun(sh, 30, 24, 11)
    sh.rect_r(0, 66, 200, 44, "b")
    for x in range(10, 180, 46): sh.line(f"M{x} 84Q{x + 8} 80 {x + 16} 84")
    sh.poly_r([(150, 64), (156, 38), (166, 64)], "-"); sh.region("M146 64H170L166 70H150Z", "r"); sh.line("M156 38V64")
    sh.region("M0 200V108Q100 100 200 108V200Z", "y")
    # kind achter het kasteel
    person(sh, 120, 56, "g", "n", hands=((96, 64), (146, 96)), style="short", hair="w")
    sh.line("M146 96L160 64"); sh.region("M154 64L158 48Q164 44 170 50L166 66Z", "r")
    # kasteel
    sh.rect_r(92, 130, 56, 54, "w")
    for x0 in (64, 144):
        sh.region(f"M{x0} 184V108H{x0 + 6}V102H{x0 + 12}V108H{x0 + 20}V102H{x0 + 26}V108H{x0 + 32}V184Z", "w")
    for k in range(4): sh.rect_r(96 + k * 14, 124, 8, 7, "w")
    sh.region("M110 184V166Q120 154 130 166V184Z", "x")
    sh.line("M80 102V84"); sh.poly_r([(80, 84), (94, 88), (80, 93)], "r")
    sh.rect_r(74, 120, 8, 10, "-", 4); sh.rect_r(154, 120, 8, 10, "-", 4)
    sh.region("M104 148Q108 142 112 148Q108 152 104 148Z", "k"); sh.region(star_path(80, 150, 5, 2.2), "o")
    # emmer en krab
    sh.region("M20 156H48L44 184H24Z", "r"); sh.ellipse_r(34, 156, 14, 3.5, "-"); sh.line("M20 156Q34 136 48 156")
    sh.ellipse_r(182, 186, 9, 6, "o"); sh.line("M175 182L170 176M189 182L194 176")
    sh.dot(179, 184, 1.2); sh.dot(185, 184, 1.2)
    for x in (172, 192): sh.circle_r(x, 174, 3, "o")


# ---------- seizoenen ----------
def blossom_tree(sh, x, base, w, h):
    sh.region(f"M{x - 5} {base}C{x - 3} {base - h * .3} {x - 4} {base - h * .45} {x - 3} {base - h * .55}H{x + 3}C{x + 4} {base - h * .45} {x + 3} {base - h * .3} {x + 5} {base}Z", "w")
    sh.region(blob(x, base - h * .72, w, h * .32, 10), "l")
    import random
    rnd = random.Random(int(x * 7 + base))
    for _ in range(int(w / 3.5)):
        a = rnd.random() * math.tau; rr = rnd.random() ** .5 * .78
        flower(sh, x + w * rr * math.cos(a), base - h * .72 + h * .32 * rr * math.sin(a), 3, "k", "m")

def sheep(sh, x, y, s=1, face_left=False):
    d = -1 if face_left else 1
    for dx in (-12, -5, 6, 12): sh.rect_r(x + dx * s - 2 * s, y + 8 * s, 4 * s, 12 * s, "x")
    sh.region(blob(x, y, 20 * s, 12 * s, 11, .7), "-")
    sh.ellipse_r(x + d * 20 * s, y - 6 * s, 7 * s, 9 * s, "z")
    sh.ellipse_r(x + d * 14 * s, y - 10 * s, 5 * s, 2.4 * s, "z")
    eye(sh, x + d * 22 * s, y - 8 * s, 1.4 * s)

def lente_boomgaard(sh):
    grass(sh, 150, "l")
    sh.region(cloud_path(100, 24, 12), "-"); sun(sh, 176, 22, 10)
    bird(sh, 60, 22); bird(sh, 74, 30, 5)
    blossom_tree(sh, 100, 156, 30, 96)
    blossom_tree(sh, 40, 172, 36, 140); blossom_tree(sh, 162, 170, 34, 136)
    sheep(sh, 112, 166, 1.1); sheep(sh, 150, 182, .7, True)
    # bijenkorf met bijtjes
    sh.rect_r(4, 182, 40, 6, "w")
    sh.region("M8 182C6 160 14 148 24 148C34 148 42 160 40 182Z", "y")
    for y in (158, 166, 174): sh.line(f"M{8 + (182 - y) * .06 + (2 if y == 158 else 0)} {y}Q24 {y + 3} {40 - (2 if y == 158 else 0)} {y}", "l", "stroke-width:1.3")
    sh.region("M20 182V176Q24 172 28 176V182Z", "x")
    for x, y in ((56, 150), (70, 140)):
        sh.ellipse_r(x, y, 4, 3, "y"); sh.ellipse_r(x - 1, y - 4, 2.5, 2, "-"); sh.ellipse_r(x + 2, y - 4, 2.5, 2, "-")

def zomer_strand(sh):
    sun(sh, 26, 24, 12)
    bird(sh, 80, 22); bird(sh, 94, 30, 5)
    sh.rect_r(0, 66, 200, 46, "b")
    for x in range(6, 200, 44): sh.line(f"M{x} 100Q{x + 8} 96 {x + 16} 100")
    sh.poly_r([(160, 64), (168, 30), (180, 64)], "-"); sh.region("M154 64H184L178 72H160Z", "o"); sh.line("M168 30V64")
    limb(sh, 112, 92, 104, 76, "-", 6); limb(sh, 132, 92, 140, 76, "-", 6)
    sh.circle_r(122, 88, 9, "-"); hair_front(sh, 122, 88, .6, "short", "x"); eye(sh, 119, 89, 1.4); eye(sh, 125, 89, 1.4); smile(sh, 122, 92, 2.6)
    sh.line("M106 98Q122 92 138 98", "l", "stroke-width:1.6")
    sh.region("M0 200V110Q100 102 200 110V200Z", "y")
    # handdoek
    sh.region("M22 160H114L124 188H12Z", "t")
    for k in (1, 2, 3): sh.line(f"M{22 + k * 23} 160L{12 + k * 28} 188", "l", "stroke-width:1.2")
    sh.ellipse_r(40, 176, 8, 3.5, "r"); sh.ellipse_r(54, 178, 8, 3.5, "r")
    # parasol
    sh.line("M66 182L70 70")
    apex = (70, 56); bx = [24, 47, 70, 93, 116]
    for i in range(4):
        a, b = bx[i], bx[i + 1]
        sh.region(f"M{apex[0]} {apex[1]}L{a} 86Q{(a + b) / 2} 80 {b} 86Z", "r" if i % 2 == 0 else "-")
    sh.circle_r(70, 54, 3, "r")
    # strandbal en koelbox
    sh.circle_r(156, 172, 13, "-")
    sh.region("M156 159Q146 172 156 185Q150 172 156 159Z", "y"); sh.region("M156 159Q166 172 156 185Q162 172 156 159Z", "r")
    sh.region("M144 168Q156 162 168 168", "-");
    sh.rect_r(140, 124, 34, 22, "n", 2); sh.rect_r(138, 120, 38, 7, "-", 2); sh.rect_r(150, 116, 14, 4, "z", 1)
    sh.region(star_path(186, 136, 6, 2.6), "o")

def herfstwandeling(sh):
    sh.region("M0 200V172Q100 162 200 172V200Z", "w")
    # boom
    sh.region("M156 172C160 150 160 120 158 96H172C170 120 170 150 176 172Z", "w")
    sh.line("M162 104L146 86M168 100L182 84M160 120L150 112")
    sh.region(blob(164, 64, 34, 30, 9), "o")
    for x, y, c, r in ((116, 30, "r", 30), (134, 112, "y", -40), (190, 120, "o", 60), (28, 80, "r", -20), (26, 140, "y", 30), (140, 150, "o", 80)):
        leaf_at(sh, x, y, 5, 8, r, c)
    for x, y, c, r in ((20, 186, "r", 70), (60, 190, "o", -60), (180, 188, "y", 100), (150, 184, "r", 20)):
        leaf_at(sh, x, y, 5, 8, r, c)
    # plas
    sh.ellipse_r(124, 184, 24, 6, "b")
    # kind met paraplu en laarzen
    hy = person(sh, 80, 72, "y", "n", hands=((88, 112), (58, 124)), style="long", hair="o", shoes=None, legs=((74, 160), (88, 160)), arms_front=True)
    for x in (74, 88): sh.rect_r(x - 6, 150, 12, 20, "g", 1)
    sh.ellipse_r(72, 172, 8, 3.5, "g"); sh.ellipse_r(90, 172, 8, 3.5, "g")
    sh.line("M88 52V108Q88 116 82 116")
    sh.circle_r(88, 112, 4.5, "-")
    sh.region("M40 56Q88 6 136 56Q124 48 112 56Q100 48 88 56Q76 48 64 56Q52 48 40 56Z", "r")
    sh.line("M88 31L64 56M88 31L112 56M88 31V56"); sh.line("M88 31V22")
    for x, y in ((30, 70), (148, 40), (20, 110), (140, 76), (36, 30)): sh.region(drop_path(x, y, 3), "b")
    for x in (24, 38):
        sh.rect_r(x - 2, 170, 4, 8, "-"); sh.region(f"M{x - 7} 171Q{x} 160 {x + 7} 171Z", "r")

def sleetje(sh):
    sh.region("M0 150Q50 110 110 136T200 120V200H0Z", "-")
    pine(sh, 30, 136, 54, "g", True); pine(sh, 172, 128, 60, "g", True); pine(sh, 120, 140, 40, "g", True)
    sh.region("M0 200V170Q100 160 200 172V200Z", "-")
    for x, y in ((20, 24), (50, 50), (90, 20), (140, 34), (176, 60), (110, 70), (160, 14), (66, 90)):
        sh.line(f"M{x - 3} {y}H{x + 3}M{x - 1.5} {y - 2.6}L{x + 1.5} {y + 2.6}M{x + 1.5} {y - 2.6}L{x - 1.5} {y + 2.6}", "l", "stroke-width:1.2")
    hy = person(sh, 60, 80, "n", "z", hands=((40, 132), (82, 128)), cap=True, hand="r")
    beanie(sh, 60, hy, "r", "-"); scarf(sh, 60, hy, "g")
    sh.line("M82 130Q100 160 112 160")
    # slee met beer
    sh.circle_r(146, 116, 11, "w"); sh.circle_r(137, 107, 4.5, "w"); sh.circle_r(155, 107, 4.5, "w")
    sh.ellipse_r(146, 120, 4.5, 3.5, "-"); eye(sh, 142, 114, 1.6); eye(sh, 150, 114, 1.6); sh.dot(146, 119, 1.3)
    sh.region("M134 150C130 136 134 126 146 126C158 126 162 136 158 150Z", "w")
    sh.circle_r(132, 142, 4.5, "w"); sh.circle_r(160, 142, 4.5, "w")
    sh.rect_r(112, 150, 70, 8, "o", 2)
    sh.line("M120 158V168M146 158V168M172 158V168")
    sh.line("M108 168H178Q190 168 190 158Q190 152 184 152")
    sh.line("M112 154L108 160Q104 168 110 168")


# ---------- Nederland ----------
def canal_house(sh, x0, w, top, base, gable, code):
    mid = x0 + w / 2
    body = 60
    sh.rect_r(x0, top + body * .0 + 40, w, base - top - 40, code)
    y = top + 40
    if gable == "trap":
        pts = [(x0, y), (x0, y - 8), (x0 + 6, y - 8), (x0 + 6, y - 18), (x0 + 12, y - 18), (x0 + 12, y - 28), (mid - 6, y - 28), (mid - 6, y - 38), (mid + 6, y - 38), (mid + 6, y - 28), (x0 + w - 12, y - 28), (x0 + w - 12, y - 18), (x0 + w - 6, y - 18), (x0 + w - 6, y - 8), (x0 + w, y - 8), (x0 + w, y)]
        sh.poly_r(pts, code)
    elif gable == "klok":
        sh.region(f"M{x0} {y}C{x0 + 2} {y - 10} {x0 + 10} {y - 12} {x0 + 10} {y - 22}C{x0 + 10} {y - 34} {mid - 4} {y - 40} {mid} {y - 40}C{mid + 4} {y - 40} {x0 + w - 10} {y - 34} {x0 + w - 10} {y - 22}C{x0 + w - 10} {y - 12} {x0 + w - 2} {y - 10} {x0 + w} {y}Z", code)
    elif gable == "hals":
        sh.region(f"M{x0} {y}V{y - 8}Q{x0 + 10} {y - 8} {x0 + 10} {y - 18}H{x0 + 12}V{y - 34}H{x0 + w - 12}V{y - 18}H{x0 + w - 10}Q{x0 + w - 10} {y - 8} {x0 + w} {y - 8}V{y}Z", code)
        sh.region(f"M{x0 + 10} {y - 34}Q{mid} {y - 46} {x0 + w - 10} {y - 34}Z", code)
    else:
        sh.poly_r([(x0, y), (mid, y - 34), (x0 + w, y)], code)
    sh.rect_r(mid - 3, y - 26, 6, 4, "w"); sh.line(f"M{mid} {y - 22}V{y - 16}"); sh.line(f"M{mid - 2} {y - 16}Q{mid} {y - 12} {mid + 2} {y - 16}", "l", "stroke-width:1.2")
    sh.rect_r(mid - 6, y - 12, 12, 9, "-", 1)
    ww = (w - 18) / 2
    for row in range(3):
        yy = y + 6 + row * 20
        for col in range(2):
            xx = x0 + 6 + col * (ww + 6)
            if row == 2 and col == 0:
                continue
            sh.rect_r(xx, yy, ww, 14, "-", 1); sh.seg(xx, yy + 7, xx + ww, yy + 7, "l", "stroke-width:1")
    sh.rect_r(x0 + 6, base - 20, ww, 20, "g", 1); sh.dot(x0 + 6 + ww - 3, base - 10, 1.2)

def grachtenhuizen(sh):
    sh.region(cloud_path(170, 20, 10), "-"); bird(sh, 30, 16)
    canal_house(sh, 6, 46, 30, 126, "trap", "r")
    canal_house(sh, 52, 48, 22, 126, "klok", "o")
    canal_house(sh, 100, 46, 34, 126, "hals", "w")
    canal_house(sh, 146, 48, 26, 126, "tuit", "b")
    sh.rect_r(0, 126, 200, 18, "z")
    # fiets op de kade
    sh.circle_r(76, 134, 7); sh.circle_r(100, 134, 7)
    sh.line("M76 134L84 124H96L100 134M84 124L88 134L96 124M84 124L82 120M96 124L98 118H102")
    sh.rect_line(79, 118, 6, 2.4)
    sh.rect_r(0, 144, 200, 10, "w")
    for x in range(10, 200, 20): sh.seg(x, 144, x, 154, "l", "stroke-width:1")
    sh.rect_r(0, 154, 200, 46, "b")
    for x in range(4, 200, 40): sh.line(f"M{x} 192Q{x + 8} 188 {x + 16} 192")
    for x in (16, 54, 104, 150): sh.line(f"M{x} 162H{x + 22}", "l", "stroke-width:1")
    # bootje
    sh.region("M110 166H178L170 184H118Z", "r"); sh.rect_r(124, 156, 20, 10, "-", 2); sh.line("M168 166V150"); sh.poly_r([(168, 150), (180, 153), (168, 156)], "y")

def fietsen_dijk(sh):
    sun(sh, 30, 22, 10); sh.region(cloud_path(120, 20, 10), "-"); bird(sh, 70, 30)
    # dorpje achter de dijk
    sh.region(blob(150, 94, 14, 12, 7), "g"); sh.region(blob(186, 96, 12, 10, 7), "g")
    sh.rect_r(162, 62, 12, 42, "-"); sh.poly_r([(160, 62), (168, 40), (176, 62)], "g"); sh.line("M168 40V32M165 35H171")
    sh.rect_r(165, 70, 6, 8, "-", 3)
    sh.rect_r(134, 90, 18, 14, "r"); sh.poly_r([(132, 90), (143, 80), (154, 90)], "z")
    sh.rect_r(0, 102, 200, 8, "z")
    sh.region("M0 110H200V150H0Z", "l")
    sh.region("M0 200V150H200V200Z", "g")
    sh.line("M0 174Q50 170 100 176T200 172", "l", "stroke-width:1.4")
    flower(sh, 30, 186, 4, "y", "o"); flower(sh, 150, 188, 4, "m")
    sheep(sh, 38, 130, .8); sheep(sh, 176, 136, .75, True)
    # fietser
    for cx in (78, 122): sh.circle_r(cx, 92, 12, "-"); sh.circle_r(cx, 92, 2.5, "z")
    limb(sh, 92, 68, 102, 78, "n", 8); limb(sh, 102, 78, 96, 94, "n", 8); sh.ellipse_r(99, 95, 5, 2.8, "x")
    sh.line("M78 92L98 92L92 70L78 92M98 92L116 70L122 92M92 70H116M116 70L118 62H112")
    sh.rect_r(86, 66, 12, 4, "x", 2)
    limb(sh, 92, 66, 104, 82, "n", 9); limb(sh, 104, 82, 100, 96, "n", 9); sh.ellipse_r(103, 97, 6, 3, "x")
    limb(sh, 92, 66, 100, 42, "r", 15)
    limb(sh, 102, 46, 116, 62, "r", 7); sh.circle_r(117, 62, 3.6, "-")
    sh.circle_r(104, 32, 10, "-"); sh.region("M93 31A11 11 0 0 1 115 29L112 32Q104 26 93 31Z", "y")
    sh.region("M95 36Q90 44 96 46Q94 40 97 37Z", "w")
    eye(sh, 109, 32, 1.4); sh.line("M108 37Q111 39 113 36", "l", "stroke-width:1.4")
    # mandje met tulpen
    sh.region("M120 66H136L134 76H122Z", "w")
    for x, c in ((124, "r"), (129, "y"), (134, "m")): sh.line(f"M{x} 66V58"); sh.region(f"M{x - 3} 58V53L{x - 1.5} 55L{x} 52L{x + 1.5} 55L{x + 3} 53V58Z", c)

def klompen(sh):
    sh.region("M0 200V178Q100 170 200 178V200Z", "l")
    sun(sh, 172, 26, 11)
    def clog(dx, dy, code):
        P = lambda x, y: f"{x + dx} {y + dy}"
        sh.region(f"M{P(32, 156)}L{P(28, 126)}Q{P(28, 118)} {P(38, 118)}L{P(74, 118)}Q{P(92, 110)} {P(112, 116)}Q{P(140, 124)} {P(156, 128)}Q{P(170, 122)} {P(166, 136)}Q{P(160, 154)} {P(140, 156)}Z", code)
        sh.region(f"M{P(34, 120)}Q{P(54, 112)} {P(76, 119)}Q{P(54, 126)} {P(34, 120)}Z", "w")
        sh.line(f"M{P(32, 146)}Q{P(96, 150)} {P(160, 142)}", "l", "stroke-width:1.4")
        flower(sh, 112 + dx, 133 + dy, 5, "r", "y")
        leaf_at(sh, 100 + dx, 137 + dy, 3, 6, -60, "g"); leaf_at(sh, 124 + dx, 137 + dy, 3, 6, 60, "g")
    # tulpen in de achterste klomp
    for x, top, c in ((70, 52, "r"), (84, 44, "y"), (98, 58, "m")):
        sh.line(f"M{x} {top + 14}Q{x - 4} {top + 40} {x - 8} 96")
        sh.region(f"M{x - 8} {top + 2}C{x - 9} {top + 12} {x - 6} {top + 16} {x} {top + 16}C{x + 6} {top + 16} {x + 9} {top + 12} {x + 8} {top + 2}L{x + 4} {top + 6}L{x} {top}L{x - 4} {top + 6}Z", c)
    leaf_at(sh, 62, 82, 4, 12, -30, "g"); leaf_at(sh, 96, 84, 4, 12, 30, "g")
    clog(28, -24, "y")
    clog(-6, 24, "y")

def cow(sh, x, y, s=1):
    """Koe naar rechts; (x, y) = linksboven van het lijf."""
    S = lambda v: v * s
    sh.line(f"M{f(x + S(2))} {f(y + S(6))}Q{f(x - S(8))} {f(y + S(14))} {f(x - S(6))} {f(y + S(30))}")
    sh.region(f"M{f(x - S(9))} {f(y + S(30))}Q{f(x - S(6))} {f(y + S(24))} {f(x - S(3))} {f(y + S(30))}L{f(x - S(6))} {f(y + S(36))}Z", "x")
    for dx in (6, 16, 50, 60):
        sh.rect_r(x + S(dx), y + S(26), S(8), S(22), "-", S(2)); sh.rect_r(x + S(dx), y + S(44), S(8), S(5), "x", S(1))
    sh.rect_r(x, y, S(72), S(32), "-", S(12))
    sh.region(f"M{f(x + S(14))} {f(y)}Q{f(x + S(30))} {f(y + S(6))} {f(x + S(24))} {f(y + S(18))}Q{f(x + S(12))} {f(y + S(22))} {f(x + S(4))} {f(y + S(14))}Q{f(x + S(4))} {f(y + S(2))} {f(x + S(14))} {f(y)}Z", "x")
    sh.region(f"M{f(x + S(42))} {f(y + S(8))}Q{f(x + S(56))} {f(y + S(4))} {f(x + S(58))} {f(y + S(16))}Q{f(x + S(52))} {f(y + S(28))} {f(x + S(40))} {f(y + S(22))}Q{f(x + S(34))} {f(y + S(14))} {f(x + S(42))} {f(y + S(8))}Z", "x")
    sh.ellipse_r(x + S(34), y + S(34), S(8), S(5), "k")
    # kop
    sh.region(f"M{f(x + S(64))} {f(y - S(2))}C{f(x + S(70))} {f(y - S(10))} {f(x + S(86))} {f(y - S(8))} {f(x + S(88))} {f(y + S(6))}L{f(x + S(90))} {f(y + S(18))}H{f(x + S(70))}C{f(x + S(64))} {f(y + S(14))} {f(x + S(62))} {f(y + S(4))} {f(x + S(64))} {f(y - S(2))}Z", "-")
    sh.ellipse_r(x + S(84), y + S(18), S(9), S(7), "k"); sh.dot(x + S(82), y + S(18), S(1.3)); sh.dot(x + S(88), y + S(18), S(1.3))
    sh.ellipse_r(x + S(62), y - S(2), S(7), S(3.5), "-"); sh.region(f"M{f(x + S(70))} {f(y - S(6))}Q{f(x + S(70))} {f(y - S(14))} {f(x + S(76))} {f(y - S(14))}Q{f(x + S(74))} {f(y - S(8))} {f(x + S(74))} {f(y - S(5))}Z", "y")
    eye(sh, x + S(78), y + S(3), S(2))

def polder(sh):
    sh.region(cloud_path(150, 22, 12), "-"); sh.region(cloud_path(56, 30, 9), "-"); bird(sh, 100, 20); bird(sh, 112, 28, 5)
    sh.region("M0 200V92H200V200Z", "l")
    # boerderij en molentje aan de horizon
    sh.rect_r(140, 76, 30, 16, "r"); sh.poly_r([(136, 78), (155, 60), (174, 78)], "z"); sh.rect_r(150, 82, 6, 10, "-")
    sh.region(blob(186, 82, 12, 10, 7), "g"); sh.region(blob(124, 84, 9, 8, 7), "g")
    sh.region("M28 92L31 62H39L42 92Z", "-")
    for a in (20, 110, 200, 290):
        r = math.radians(a); x2, y2 = 35 + 20 * math.cos(r), 62 + 20 * math.sin(r)
        sh.line(f"M35 62L{f(x2)} {f(y2)}")
    sh.circle_r(35, 62, 2.5, "z")
    # sloot
    sh.region("M92 92H98L150 200H118Z", "b")
    sh.line("M0 112H90M0 136H80")
    cow(sh, 18, 140, .9)
    cow(sh, 140, 108, .45)
    # hek
    for x in (168, 196): sh.rect_r(x - 2, 132, 4, 50, "w")
    sh.line("M156 140H200M156 150H200M156 160H200M156 170H200M158 170L198 140")
    sh.ellipse_r(122, 150, 6, 3.5, "-"); sh.circle_r(126, 145, 2.6, "-"); sh.poly_r([(128, 145), (132, 146), (128, 147)], "o")


# ---------- beroepen ----------
def kapper(sh):
    sh.rect_r(0, 176, 200, 24, "-")
    for x in range(20, 200, 20): sh.seg(x, 176, x - 8, 200, "l", "stroke-width:1")
    sh.rect_r(24, 14, 104, 86, "b", 8); sh.line("M36 30L50 20M36 44L62 22", "l", "stroke-width:1.2")
    sh.rect_r(150, 30, 46, 5, "w")
    for x, h, c in ((156, 16, "m"), (168, 20, "g"), (182, 14, "o")): sh.rect_r(x, 30 - h, 9, h, c, 2)
    # stoel
    sh.ellipse_r(76, 184, 24, 5, "z"); sh.rect_r(72, 160, 8, 24, "z")
    # kind onder de kapmantel
    sh.region("M76 86C48 88 38 120 40 158H112C114 120 104 88 76 86Z", "t")
    for x, y in ((58, 120), (90, 112), (70, 140), (98, 140), (54, 148)): sh.circle_r(x, y, 2.4, "-")
    sh.ellipse_r(68, 164, 7, 4, "x"); sh.ellipse_r(86, 164, 7, 4, "x")
    hair_back(sh, 76, 72, 1, "curly", "w"); sh.circle_r(76, 72, 15, "-"); hair_front(sh, 76, 72, 1, "curly", "w")
    eye(sh, 71, 75, 1.8); eye(sh, 81, 75, 1.8); smile(sh, 76, 80, 4)
    # kapper
    person(sh, 150, 42, "p", "x", hands=((102, 58), (104, 86)), style="bun", hair="x", s=1, skirt=None, arms_front=False)
    sh.rect_r(140, 92, 20, 12, "-", 2); sh.line("M140 92L136 82M160 92L164 82")
    sh.circle_r(108, 50, 3.5); sh.circle_r(112, 56, 3.5); sh.line("M104 48L88 40M106 54L90 50")
    sh.rect_r(96, 84, 6, 14, "z", 1); sh.line("M96 88H92M96 92H92M96 96H92", "l", "stroke-width:1")
    for x, y in ((50, 100), (118, 130), (30, 170), (120, 172), (100, 186), (46, 188)):
        sh.line(f"M{x} {y}q3 -3 6 0", "l", "stroke-width:1.4")

def dierenarts(sh):
    sh.rect_r(0, 186, 200, 14, "w")
    sh.rect_r(20, 14, 40, 40, "-", 2); sh.ellipse_r(40, 40, 8, 7, "m")
    for x, y in ((30, 28), (36, 22), (44, 22), (50, 28)): sh.ellipse_r(x, y, 3.5, 4, "m")
    sh.line("M70 30H100", "l"); sh.rect_r(74, 18, 8, 12, "b", 1); sh.rect_r(86, 22, 10, 8, "g", 1)
    # onderzoekstafel
    sh.rect_r(14, 128, 116, 10, "z", 2); sh.rect_r(22, 138, 6, 48, "z"); sh.rect_r(116, 138, 6, 48, "z")
    # reismand met poes
    sh.rect_r(38, 150, 62, 36, "o", 4); sh.rect_r(52, 158, 34, 22, "-", 2)
    for x in (60, 69, 78): sh.seg(x, 158, x, 180, "l", "stroke-width:1.2")
    eye(sh, 64, 168, 1.6); eye(sh, 74, 168, 1.6); sh.poly_r([(55, 160), (57, 154), (61, 159)], "z"); sh.poly_r([(79, 159), (83, 154), (85, 160)], "z")
    # hond op tafel
    sh.line("M100 120Q116 116 112 102")
    sh.region("M56 128C50 104 62 90 76 90C90 90 102 104 96 128Z", "o")
    sh.rect_r(64, 106, 8, 22, "o", 3); sh.rect_r(80, 106, 8, 22, "o", 3)
    sh.rect_r(79, 112, 10, 10, "-", 1); sh.line("M82 117H86M84 115V119", "l", "stroke-width:1")
    sh.region("M58 70C46 70 46 96 54 98C60 96 62 82 62 76Z", "w"); sh.region("M94 70C106 70 106 96 98 98C92 96 90 82 90 76Z", "w")
    sh.circle_r(76, 78, 17, "o")
    sh.ellipse_r(76, 88, 8, 6, "-"); sh.ellipse_r(76, 84, 3.5, 2.5, "x"); sh.line("M72 91Q76 94 80 91")
    eye(sh, 69, 76, 2.2); eye(sh, 83, 76, 2.2)
    # dierenarts
    hy = person(sh, 150, 36, "-", "n", hands=((96, 108), (170, 104)), style="short", hair="x")
    sh.line(f"M150 {hy + 16}V{hy + 58}M146 {hy + 18}L150 {hy + 30}L154 {hy + 18}")
    sh.rect_r(154, hy + 36, 8, 8, "-", 1); sh.line(f"M157 {hy + 36}V{hy + 32}", "l", "stroke-width:1.2")
    sh.line(f"M143 {hy + 15}Q140 {hy + 34} 124 {hy + 46}Q110 {hy + 54} 100 108M157 {hy + 15}Q160 {hy + 24} 152 {hy + 30}")
    sh.circle_r(96, 108, 4, "z")
    sh.region(heart_path(176, 70, 6), "r")

def vuilnisman(sh):
    sh.rect_r(0, 178, 200, 22, "z"); sh.seg(0, 184, 200, 184)
    # achterkant vuilniswagen
    sh.rect_r(158, 20, 16, 8, "o", 3)
    sh.rect_r(130, 28, 70, 132, "g", 6)
    sh.region("M140 96H200V138H146Q140 138 140 132Z", "x")
    for x in (150, 186): sh.rect_r(x, 128, 6, 26, "z", 1)
    sh.rect_r(130, 152, 70, 12, "y")
    for x in range(136, 190, 12): sh.seg(x, 164, x + 8, 152, "l", "stroke-width:1.6")
    sh.rect_r(134, 40, 8, 14, "r", 2); sh.rect_r(134, 60, 8, 8, "o", 2)
    for y in (40, 60, 80): sh.seg(150, y, 196, y, "l", "stroke-width:1.2")
    sh.circle_r(178, 176, 12, "x"); sh.circle_r(178, 176, 4, "z")
    # container
    sh.region("M98 124H128L124 172H102Z", "g"); sh.rect_r(94, 118, 38, 7, "g", 2); sh.line("M96 118L90 112")
    sh.circle_r(104, 174, 6, "x"); sh.text(113, 150, "GFT", 6)
    # papiercontainer
    sh.region("M8 132H38L35 176H11Z", "n"); sh.rect_r(5, 126, 36, 7, "n", 2); sh.circle_r(13, 178, 5, "x")
    # vuilnisman met hesje
    hy = person(sh, 64, 64, "o", "o", hands=((92, 112), (42, 122)), cap=True, hand="g")
    sh.region(f"M50 {hy - 2}Q50 {hy - 18} 64 {hy - 18}Q78 {hy - 18} 78 {hy - 2}Z", "o"); sh.region(f"M64 {hy - 4}H86Q86 {hy} 78 {hy}H64Z", "o")
    sh.rect_r(47, hy + 36, 34, 6, "y"); sh.rect_r(47, hy + 46, 34, 4, "y")
    for x in (56, 72): sh.rect_r(x - 6, hy + 72, 12, 4, "y")
    bird(sh, 30, 30); bird(sh, 46, 22, 5)

def bouwvakker(sh):
    sh.rect_r(0, 180, 200, 20, "w")
    # kraan
    sh.line("M168 180V20M180 180V20")
    for y in range(20, 180, 16): sh.line(f"M168 {y}L180 {y + 16}M168 {y + 16}H180", "l", "stroke-width:1.1")
    sh.line("M100 14H198M100 22H198M174 4L100 14M174 4L198 14")
    for x in range(100, 196, 12): sh.line(f"M{x} 14L{x + 6} 22L{x + 12} 14", "l", "stroke-width:1.1")
    sh.rect_r(170, 8, 10, 6, "y")
    sh.line("M120 22V64"); sh.region("M116 64H124V70Q124 76 120 76Q116 76 116 72", "-")
    sh.rect_r(102, 76, 36, 8, "o", 1)
    # muur in aanbouw
    bw, bh = 20, 9
    for row in range(6):
        y = 171 - row * bh
        n = 4 if row < 4 else (3 if row == 4 else 2)
        off = 10 if row % 2 else 0
        for k in range(n):
            x = 100 + off + k * bw
            if x + bw > 196: continue
            sh.rect_r(x, y, bw, bh, "r")
    # emmer met cement
    sh.region("M16 156H46L42 180H20Z", "z"); sh.ellipse_r(31, 156, 15, 3.5, "-"); sh.line("M16 156Q31 140 46 156")
    # bouwvakker
    hy = person(sh, 66, 64, "o", "n", hands=((92, 116), (42, 118)), cap=True, style="pony", hair="w")
    sh.region(f"M50 {hy - 1}Q50 {hy - 19} 66 {hy - 19}Q82 {hy - 19} 82 {hy - 1}Z", "y"); sh.rect_r(46, hy - 3, 40, 5, "y", 2)
    sh.rect_r(49, hy + 38, 34, 5, "y")
    sh.rect_r(48, hy + 52, 36, 7, "w", 1)
    for x in (54, 64, 74): sh.rect_r(x, hy + 58, 6, 6, "z", 1)
    sh.rect_r(30, 116, 18, 9, "r")
    limb(sh, 92, 116, 98, 104, "w", 4); sh.poly_r([(96, 104), (108, 96), (104, 108)], "z")

def buschauffeur(sh):
    sh.rect_r(0, 180, 200, 20, "z"); sh.seg(0, 186, 200, 186)
    # bus van voren
    sh.rect_r(26, 162, 16, 22, "x", 3); sh.rect_r(120, 162, 16, 22, "x", 3)
    sh.rect_r(22, 26, 118, 144, "y", 14)
    sh.rect_r(34, 32, 94, 14, "-", 2); sh.text(81, 42.5, "12  Station", 7.5)
    sh.rect_r(30, 50, 102, 62, "b", 6)
    # chauffeur
    hy = person(sh, 70, 54, "n", "-", hands=((56, 104), (98, 64)), style="short", hair="w", draw_legs=False, s=.85)
    sh.ellipse_r(66, 104, 18, 5, "x"); sh.ellipse_r(66, 104, 11, 2.4, "-")
    sh.rect_r(30, 104, 102, 8, "z")
    sh.rect_r(30, 50, 102, 62, "-", 6); sh.parts[-1] = sh.parts[-1].replace('class="r"', 'class="l" fill="none"'); sh.codes.pop()
    for x in (44, 118): sh.circle_r(x, 132, 9, "-")
    for y in (124, 132, 140): sh.seg(64, y, 98, y)
    sh.rect_r(26, 150, 110, 12, "z", 4)
    for x in (12, 150): sh.rect_r(x, 54, 6, 20, "x", 2)
    sh.line("M22 58H18M140 58H144")
    # halte met wachtend kind
    sh.line("M170 184V54"); sh.rect_r(156, 40, 28, 22, "b", 3)
    sh.rect_r(162, 46, 16, 9, "-", 2); sh.circle_r(165, 56, 1.8, "-"); sh.circle_r(175, 56, 1.8, "-")
    hy = person(sh, 184, 112, "g", "n", hands=((174, 136), (194, 140)), style="braids", hair="x", s=.6)
    sh.rect_r(170, 130, 4, 10, "r", 1)

def juf(sh):
    sh.rect_r(0, 186, 200, 14, "w")
    sh.rect_r(12, 12, 132, 74, "w", 3); sh.rect_r(18, 18, 120, 62, "g", 2)
    sh.text(52, 44, "a b c", 13); sh.text(98, 68, "2 + 3 = 5", 10)
    sh.rect_r(40, 86, 30, 4, "w", 1); sh.rect_r(46, 82, 10, 4, "-", 1)
    sh.circle_r(172, 26, 13, "-"); sh.line("M172 18V26L178 30")
    for k in range(12):
        a = math.radians(k * 30); sh.seg(172 + 10 * math.cos(a), 26 + 10 * math.sin(a), 172 + 11.5 * math.cos(a), 26 + 11.5 * math.sin(a), "l", "stroke-width:1")
    # juf met aanwijsstok
    hy = person(sh, 166, 60, "m", "n", hands=((144, 86), (186, 110)), style="long", hair="x", skirt="p", legs=((160, 158), (172, 158)))
    sh.line("M144 86L118 58")
    # leerlingen van achteren
    for cx, hair, st, sh_c, up in ((48, "o", "pony", "b", True), (112, "x", "curly", "r", False)):
        sh.rect_r(cx - 34, 150, 68, 8, "w", 1)
        sh.rect_r(cx - 30, 158, 5, 28, "w"); sh.rect_r(cx + 25, 158, 5, 28, "w")
        hands = ((cx - 18, 96), (cx + 22, 152)) if up else ((cx - 22, 150), (cx + 22, 150))
        person(sh, cx, 108, sh_c, "n", hands=hands, style="back", hair=hair, s=.85, draw_legs=False)
        if st == "pony": sh.region(f"M{cx - 3} 120Q{cx + 4} 130 {cx} 142Q{cx - 6} 132 {cx - 3} 120Z", hair)


# ---------- sprookjes en fantasie ----------
def paddenstoelhuis(sh):
    grass(sh, 182); sun(sh, 30, 24, 10)
    sh.region("M70 182C74 150 72 120 76 100H124C128 120 126 150 130 182Z", "-")
    sh.region("M88 182V160Q100 146 112 160V182Z", "w"); sh.dot(108, 170, 1.4)
    sh.circle_r(100, 126, 9, "y"); sh.line("M91 126H109M100 117V135", "l", "stroke-width:1.3")
    sh.rect_r(132, 26, 12, 22, "z"); sh.circle_r(146, 18, 4, "-"); sh.circle_r(154, 10, 5, "-")
    sh.region("M28 106C28 52 78 30 100 30C122 30 172 52 172 106Q100 118 28 106Z", "r")
    for x, y, rx, ry in ((60, 70, 9, 6), (100, 50, 10, 7), (138, 72, 9, 6), (82, 92, 7, 5), (122, 94, 7, 5), (40, 96, 5, 4), (160, 96, 5, 4)):
        sh.ellipse_r(x, y, rx, ry, "-")
    for x, y in ((100, 190), (92, 196)): sh.ellipse_r(x, y, 6, 2.5, "z")
    # kabouter met lantaarn
    hy = 132
    sh.ellipse_r(152, 182, 7, 4, "x"); sh.ellipse_r(168, 182, 7, 4, "x")
    sh.region("M142 178L148 140H172L178 178Z", "g"); sh.rect_r(146, 162, 28, 5, "x")
    limb(sh, 150, 146, 140, 164, "g", 8); sh.circle_r(140, 166, 4, "-")
    sh.line("M140 170V174"); sh.rect_r(134, 174, 12, 12, "y", 2)
    sh.circle_r(160, 132, 12, "-")
    sh.region("M148 136Q160 168 172 136Q166 142 160 140Q154 142 148 136Z", "-")
    sh.circle_r(160, 136, 3, "k"); eye(sh, 156, 130, 1.6); eye(sh, 164, 130, 1.6)
    sh.region("M146 126Q160 82 182 96Q170 98 174 126Z", "r")
    # slak en bloemen
    sh.region("M20 184Q18 176 26 176H40Q46 176 46 184Z", "-"); sh.circle_r(32, 172, 8, "o"); sh.line("M32 172m-3 0a3 3 0 1 0 3 -3")
    sh.line("M44 177L46 170M41 177L41 170")
    flower(sh, 186, 172, 4, "p"); flower(sh, 60, 176, 4, "y", "o")

def zeemonster(sh):
    sun(sh, 174, 24, 10); sh.region(cloud_path(100, 26, 12), "-"); bird(sh, 140, 40)
    # nek en kop
    for k in range(4):
        y = 70 + k * 14
        sh.poly_r([(48 - k * .6, y), (36 - k * .6, y + 6), (47 - k * .6, y + 11)], "p")
    sh.region("M46 132C42 104 46 82 54 66L80 66C74 84 72 108 76 132Z", "g")
    sh.region("M40 56C40 36 56 28 72 30C92 32 100 46 96 60C92 72 80 74 68 72C56 72 40 70 40 56Z", "g")
    sh.poly_r([(52, 34), (50, 20), (60, 31)], "y"); sh.poly_r([(76, 31), (84, 18), (86, 34)], "y")
    sh.circle_r(60, 44, 6, "-"); sh.circle_r(78, 44, 6, "-"); eye(sh, 61, 45, 2.8); eye(sh, 79, 45, 2.8)
    sh.line("M56 60Q74 70 90 56"); sh.dot(88, 50, 1.2); sh.dot(92, 52, 1.2)
    for x, y in ((56, 92), (64, 108), (58, 120)): sh.ellipse_r(x, y, 3.5, 2.5, "l")
    # bulten en staart
    for x0, w, h in ((92, 36, 34), (140, 30, 24)):
        sh.region(f"M{x0} 132C{x0} {132 - h * 1.3} {x0 + w} {132 - h * 1.3} {x0 + w} 132Z", "g")
        for k in range(3):
            t = (k + 1) / 4; px = x0 + w * t
            py = 132 - h * 1.3 * 3 * t * (1 - t) * .98
            sh.poly_r([(px - 4, py + 2), (px, py - 8), (px + 4, py + 2)], "p")
    sh.region("M180 132C178 118 182 108 190 104L198 96L196 112C192 116 190 124 192 132Z", "g")
    sh.rect_r(0, 128, 200, 72, "b")
    for x in range(4, 200, 40): sh.line(f"M{x} 150Q{x + 8} 146 {x + 16} 150M{x + 20} 176Q{x + 28} 172 {x + 36} 176")
    # bootje met kind
    sh.circle_r(146, 140, 9, "-"); hair_front(sh, 146, 140, .6, "long", "w"); eye(sh, 143, 141, 1.3); eye(sh, 149, 141, 1.3); smile(sh, 146, 144, 2.4)
    limb(sh, 152, 150, 164, 138, "r", 6); sh.circle_r(165, 136, 3.2, "-")
    sh.region("M118 150H178L170 168H126Z", "o"); sh.line("M120 156H176")
    sh.region(fish_path(40, 168, 9), "y"); eye(sh, 34, 167, 1.3)

def vliegend_tapijt(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region(moon_path(166, 30, 15), "y")
    for x, y, r in ((24, 20, 5), (70, 14, 4), (120, 30, 5), (30, 70, 4), (186, 80, 4), (100, 60, 3.5)): sh.region(star_path(x, y, r, r * .45), "y")
    sh.region(cloud_path(40, 182, 22), "-"); sh.region(cloud_path(150, 184, 24), "-"); sh.region(cloud_path(100, 166, 12), "-")
    # tapijt
    sh.region("M24 128Q60 118 100 128T176 124L186 148Q150 152 112 144T34 154Z", "r")
    sh.region("M34 131Q64 124 100 132T170 128L177 143Q148 147 112 140T41 148Z", "y")
    sh.region("M92 132L102 128L114 134L104 140Z", "t"); sh.region("M60 132L68 129L76 135L68 139Z", "t"); sh.region("M136 132L144 129L152 134L144 138Z", "t")
    for x, y in ((24, 128), (26, 136), (30, 146), (34, 154)): sh.line(f"M{x} {y}l-8 -2", "l", "stroke-width:1.4")
    for x, y in ((176, 124), (180, 132), (183, 140), (186, 148)): sh.line(f"M{x} {y}l8 1", "l", "stroke-width:1.4")
    # sjaal die wappert
    sh.region("M96 86Q70 80 52 92Q62 94 58 102Q76 92 98 96Z", "g")
    hy = person(sh, 106, 64, "o", "-", hands=((84, 70), (124, 120)), style="curly", hair="x", s=.92, draw_legs=False)
    sh.region("M80 122Q106 112 132 122Q134 132 106 132Q78 132 80 122Z", "p")
    # poes
    sh.region("M150 126C146 110 150 100 160 100C170 100 172 112 168 126Z", "z")
    sh.circle_r(160, 94, 9, "z"); sh.poly_r([(152, 90), (152, 80), (158, 87)], "z"); sh.poly_r([(168, 90), (168, 80), (162, 87)], "z")
    eye(sh, 157, 93, 1.4); eye(sh, 163, 93, 1.4); sh.line("M168 122Q182 118 178 106")
    for y in (84, 104): sh.line(f"M10 {y}H36M16 {y + 8}H40", "l", "stroke-width:1.2")

def wolkenkasteel(sh):
    sh.region("M0 200V184Q30 176 70 186V200Z", "l")
    # bonenstaak met kind
    sh.line("M36 200C20 176 54 160 40 140C30 124 58 116 60 104", "l", "stroke-width:4")
    for x, y, r in ((30, 184, -40), (46, 160, 50), (34, 136, -50), (52, 116, 40)): leaf_at(sh, x, y, 5, 10, r, "g")
    person(sh, 40, 150, "r", "n", hands=((32, 150), (50, 146)), legs=((36, 190), (46, 186)), style="back", hair="y", s=.42)
    # reus naast het kasteel
    s = 1.7
    hy = person(sh, 150, 13, "g", "w", hands=((112, 104), (188, 26)), style="curly", hair="o", s=s, draw_legs=False, face=False)
    eye(sh, 141, hy + 2, 2.8); eye(sh, 159, hy + 2, 2.8); sh.line(f"M150 {hy + 4}Q147 {hy + 10} 151 {hy + 10}")
    sh.region(f"M{150 - 24} {hy + 6}Q{150 - 22} {hy + 50} 150 {hy + 54}Q{150 + 22} {hy + 50} {150 + 24} {hy + 6}Q{150 + 18} {hy + 22} 150 {hy + 22}Q{150 - 18} {hy + 22} {150 - 24} {hy + 6}Z", "o")
    sh.line(f"M143 {hy + 15}Q150 {hy + 19} 157 {hy + 15}")
    # kasteel
    sh.rect_r(62, 92, 44, 30, "-")
    for x0 in (52, 100):
        sh.rect_r(x0, 76, 18, 46, "-")
        sh.poly_r([(x0 - 3, 76), (x0 + 9, 54), (x0 + 21, 76)], "r")
        sh.line(f"M{x0 + 9} 54V44"); sh.poly_r([(x0 + 9, 44), (x0 + 19, 47), (x0 + 9, 50)], "y")
        sh.rect_r(x0 + 5, 86, 8, 11, "b", 4)
    for k in range(4): sh.rect_r(72 + k * 8, 86, 4, 6, "-")
    sh.region("M76 122V108Q85 98 94 108V122Z", "w")
    sh.region(blob(112, 130, 80, 18, 12), "-")
    sh.region(cloud_path(166, 160, 14), "-"); sh.region(cloud_path(110, 170, 9), "-")
    sh.circle_r(24, 28, 10, "y"); bird(sh, 66, 24); bird(sh, 80, 32, 5)

def robotvriendje(sh):
    grass(sh, 184)
    sun(sh, 28, 26, 11); sh.region(cloud_path(150, 22, 12), "-")
    # robot
    sh.rect_r(122, 150, 10, 30, "z"); sh.rect_r(146, 150, 10, 30, "z")
    sh.rect_r(116, 176, 20, 8, "x", 3); sh.rect_r(142, 176, 20, 8, "x", 3)
    limb(sh, 114, 108, 100, 126, "z", 9); limb(sh, 164, 108, 182, 88, "z", 9)
    sh.rect_r(110, 98, 58, 54, "b", 6)
    sh.rect_r(122, 108, 34, 26, "-", 4); sh.region(heart_path(139, 120, 8), "r")
    for x, c in ((124, "y"), (139, "g"), (154, "r")): sh.circle_r(x, 142, 3.5, c)
    sh.rect_r(132, 90, 14, 8, "z")
    sh.rect_r(114, 52, 50, 38, "b", 8); sh.rect_r(122, 60, 34, 22, "-", 5)
    eye(sh, 132, 69, 2.6); eye(sh, 146, 69, 2.6); sh.line("M132 75Q139 80 146 75")
    sh.rect_r(108, 64, 6, 12, "z", 2); sh.rect_r(164, 64, 6, 12, "z", 2)
    sh.line("M139 52V40"); sh.circle_r(139, 36, 5, "r")
    sh.circle_r(184, 84, 5, "z")
    # kind dat de robot een hand geeft
    person(sh, 66, 76, "y", "n", hands=((96, 128), (40, 92)), style="braids", hair="w")
    sh.circle_r(100, 128, 4.5, "z")
    sh.circle_r(32, 170, 11, "r"); sh.line("M21 170H43M32 159Q40 170 32 181")
    sh.region(heart_path(100, 60, 7), "m"); sh.region(heart_path(88, 44, 4.5), "m")


PLATES = [
    ("boomhut", "Spelen in de boomhut", "natuur", "6-9", 2, boomhut, None),
    ("voorlezen", "Voorlezen op de bank", "thuis", "2-4", 1, voorlezen, None),
    ("verstoppertje", "Verstoppertje spelen", "thuis", "4-6", 2, verstoppertje, None),
    ("zwembad-springen", "In het zwembad springen", "sport", "4-6", 2, zwembad, None),
    ("sneeuwballen-gooien", "Sneeuwballen gooien", "natuur", "4-6", 2, sneeuwballen, None),
    ("tekenen-aan-tafel", "Tekenen aan tafel", "thuis", "2-4", 1, tekenen_aan_tafel, None),
    ("tandenpoetsen", "Tandenpoetsen", "thuis", "2-4", 1, tandenpoetsen, None),
    ("boodschappen-doen", "Boodschappen doen", "eten", "4-6", 2, boodschappen, None),
    ("kamperen-in-de-tent", "Kamperen in de tent", "natuur", "6-9", 2, kamperen, None),
    ("picknick", "Picknick in het gras", "eten", "4-6", 2, picknick, None),
    ("zandkasteel-bouwen", "Een zandkasteel bouwen", "zee", "4-6", 2, zandkasteel, None),
    ("lente-boomgaard", "Lente in de boomgaard", "natuur", "6-9", 3, lente_boomgaard, None),
    ("zomer-aan-het-strand", "Zomer aan het strand", "zee", "6-9", 2, zomer_strand, None),
    ("herfstwandeling", "Herfstwandeling met paraplu", "natuur", "4-6", 2, herfstwandeling, None),
    ("sleetje-trekken", "Sleetje trekken in de sneeuw", "natuur", "4-6", 2, sleetje, None),
    ("grachtenhuizen", "Grachtenhuizen", "wereld", "6-9", 3, grachtenhuizen, None),
    ("fietsen-op-de-dijk", "Fietsen op de dijk", "wereld", "6-9", 2, fietsen_dijk, None),
    ("klompen", "Klompen met tulpen", "wereld", "2-4", 1, klompen, None),
    ("polder-met-koeien", "Koeien in de polder", "boerderij", "4-6", 2, polder, None),
    ("kapper", "Bij de kapper", "beroepen", "4-6", 2, kapper, None),
    ("dierenarts", "Dierenarts", "beroepen", "4-6", 2, dierenarts, None),
    ("vuilnisman", "Vuilnisman", "beroepen", "4-6", 2, vuilnisman, None),
    ("bouwvakker", "Bouwvakker", "beroepen", "4-6", 2, bouwvakker, None),
    ("buschauffeur", "Buschauffeur", "beroepen", "4-6", 2, buschauffeur, None),
    ("juf-in-de-klas", "Juf in de klas", "beroepen", "6-9", 2, juf, "school"),
    ("paddenstoelhuisje", "Kabouterhuisje in een paddenstoel", "sprookjes", "4-6", 2, paddenstoelhuis, None),
    ("zeemonster", "Lief zeemonster", "sprookjes", "4-6", 2, zeemonster, None),
    ("vliegend-tapijt", "Vliegend tapijt", "sprookjes", "6-9", 2, vliegend_tapijt, None),
    ("reus-wolkenkasteel", "Reus bij het kasteel in de wolken", "sprookjes", "6-9", 3, wolkenkasteel, None),
    ("robotvriendje", "Mijn robotvriendje", "sprookjes", "2-4", 1, robotvriendje, None),
]

for slug, name, cat, age, diff, draw, hol in PLATES:
    kp(slug, name, cat, age, diff, draw, hol)
