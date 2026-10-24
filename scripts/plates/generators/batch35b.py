"""Batch 35b: nieuwe kleurplaten (eigen tekeningen, 200x200): voertuigen, eten, thuis, wereld en sport."""
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
    elif style == "back":
        sh.circle_r(cx, hy, r, code)
    else:
        sh.region(top + f"Q{f(cx + 8 * s)} {f(hy - 9 * s)} {f(cx - 2 * s)} {f(hy - 7 * s)}Q{f(cx - 10 * s)} {f(hy - 6 * s)} {f(cx - r)} {f(hy)}Z", code)

def head(sh, cx, hy, s=1, style="short", hair="w", face=True):
    if hair and style not in ("short", "back"): hair_back(sh, cx, hy, s, style, hair)
    sh.circle_r(cx, hy, 15 * s, "-")
    if hair: hair_front(sh, cx, hy, s, style, hair)
    if face and style != "back":
        eye(sh, cx - 5 * s, hy + 3 * s, 1.8 * s); eye(sh, cx + 5 * s, hy + 3 * s, 1.8 * s); smile(sh, cx, hy + 8 * s, 4 * s)

def person(sh, cx, top, shirt="-", pants="-", hands=None, hair="w", style="short", legs=None, cap=False, shoes="x",
           face=True, s=1, skirt=None, arms=None, arms_front=False, draw_legs=True, draw_hands=True, hand="-"):
    """Kind/volwassene van voren. top = bovenkant hoofd, s = schaal. hands/legs = absolute posities."""
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

def sun(sh, x, y, r=12, rays=True):
    sh.circle_r(x, y, r, "y")
    if rays:
        for k in range(8):
            a = math.radians(k * 45 + 22)
            sh.seg(x + (r + 3) * math.cos(a), y + (r + 3) * math.sin(a), x + (r + 8) * math.cos(a), y + (r + 8) * math.sin(a))

def bird(sh, x, y, w=6):
    sh.line(f"M{f(x - w)} {f(y)}Q{f(x - w / 2)} {f(y - w * .6)} {f(x)} {f(y)}Q{f(x + w / 2)} {f(y - w * .6)} {f(x + w)} {f(y)}")

def wheel(sh, x, y, r, tire="x", hub="z"):
    sh.circle_r(x, y, r, tire); sh.circle_r(x, y, r * .45, hub)

def waves(sh, y0, y1, step=22, x0=4):
    for i, y in enumerate(range(y0, y1, step)):
        for x in range(x0 + (i % 2) * 20, 200, 44): sh.line(f"M{x} {y}Q{x + 6} {y - 4} {x + 12} {y}")


# ---------- voertuigen ----------
def veerpont(sh):
    sun(sh, 172, 24, 10); sh.region(cloud_path(40, 24, 12), "-"); bird(sh, 110, 30)
    # overkant met huisjes en boom
    sh.region("M0 96V78Q50 70 100 78T200 74V96Z", "g")
    for x, c in ((20, "r"), (44, "y")):
        sh.rect_r(x, 62, 18, 18, c); sh.poly_r([(x - 2, 62), (x + 9, 52), (x + 20, 62)], "w"); sh.rect_r(x + 6, 70, 6, 10, "-")
    sh.rect_r(166, 60, 5, 16, "w"); sh.region(blob(168, 52, 13, 11, 8), "g")
    sh.rect_r(0, 96, 200, 104, "b")
    waves(sh, 112, 200, 26)
    # pont
    sh.region("M16 150H184L174 172H26Z", "o"); sh.line("M22 160H178")
    sh.poly_r([(16, 150), (2, 142), (2, 146), (16, 154)], "z")
    sh.poly_r([(184, 150), (198, 142), (198, 146), (184, 154)], "z")
    sh.rect_r(16, 146, 168, 4, "z")
    # stuurhuisje
    sh.rect_r(138, 104, 34, 42, "-", 2); sh.rect_r(134, 98, 42, 8, "r", 2)
    sh.rect_r(144, 112, 10, 10, "b", 1); sh.rect_r(158, 112, 10, 10, "b", 1)
    sh.line("M155 98V86"); sh.poly_r([(155, 86), (168, 89), (155, 93)], "r")
    # auto op de pont
    sh.region("M28 146V130Q28 124 34 124H44L52 112H82L92 124H102Q108 124 108 130V146Z", "g")
    sh.poly_r([(55, 115), (66, 115), (66, 124), (49, 124)], "b"); sh.poly_r([(70, 115), (80, 115), (87, 124), (70, 124)], "b")
    wheel(sh, 44, 146, 7); wheel(sh, 92, 146, 7)
    # fietser met fiets
    sh.circle_r(114, 140, 6, "x"); sh.circle_r(132, 140, 6, "x"); sh.line("M114 140L122 130L132 140M122 130H130M130 130L132 140M120 126H126")
    person(sh, 124, 100, "y", "n", hands=((114, 120), (134, 126)), style="pony", hair="w", s=.42, draw_legs=False)

def takelwagen(sh):
    sh.rect_r(0, 168, 200, 32, "z"); sh.line("M10 186H34M60 186H84M110 186H134M160 186H184", "l", "stroke-width:3")
    sh.region(cloud_path(150, 28, 13), "-"); sh.region(cloud_path(40, 34, 9), "-")
    # oplegger
    sh.rect_r(60, 130, 136, 12, "y", 2); sh.poly_r([(196, 142), (196, 130), (199, 150)], "y")
    sh.rect_r(60, 142, 128, 10, "z")
    # cabine
    sh.region("M8 152V108Q8 98 18 96L30 72H62V152Z", "y")
    sh.poly_r([(33, 78), (56, 78), (56, 100), (22, 100)], "b")
    sh.rect_r(40, 106, 12, 4, "z", 1)
    sh.rect_r(4, 140, 12, 10, "z", 2); sh.circle_r(10, 124, 4, "-")
    sh.rect_r(36, 64, 18, 8, "o", 3)
    wheel(sh, 32, 156, 13); wheel(sh, 110, 156, 13); wheel(sh, 160, 156, 13)
    # auto op de oplegger
    sh.region("M74 130V114Q74 106 82 106H96L110 88H148L164 106H176Q184 106 184 114V130Z", "r")
    sh.poly_r([(113, 92), (127, 92), (127, 106), (101, 106)], "b"); sh.poly_r([(132, 92), (146, 92), (158, 106), (132, 106)], "b")
    sh.circle_r(180, 114, 3.5, "y")
    wheel(sh, 96, 130, 9); wheel(sh, 160, 130, 9)

def tuktuk(sh):
    sh.rect_r(0, 168, 200, 32, "w"); sun(sh, 28, 22, 10); sh.region(cloud_path(150, 22, 12), "-"); bird(sh, 96, 22)
    # dak en stijlen
    sh.rect_r(44, 46, 126, 14, "y", 6)
    sh.line("M60 60L56 112M164 60V126", "l", "stroke-width:3.5")
    # bank achterin
    sh.rect_r(146, 86, 14, 36, "r", 3); sh.rect_r(114, 106, 46, 12, "r", 3)
    # bestuurder
    hy = person(sh, 98, 66, "t", "n", hands=((66, 104), (80, 100)), style="short", hair="x", s=.62, draw_legs=False)
    # carrosserie
    sh.region("M28 150Q26 126 44 114L52 72Q54 64 62 64H66L62 116H172V150Z", "g")
    sh.poly_r([(58, 70), (64, 70), (60, 110), (52, 110)], "b")
    sh.region("M86 116H172V130H86Z", "-")
    sh.rect_r(70, 76, 12, 6, "x", 2)
    sh.circle_r(34, 130, 6, "y")
    sh.region("M24 150Q26 134 44 134Q62 134 64 150Z", "g")
    wheel(sh, 44, 154, 13)
    sh.region("M128 150Q130 132 148 132Q166 132 168 150Z", "g")
    wheel(sh, 148, 156, 13)
    sh.line("M180 136Q188 136 190 142", "l")

def hoogwerker(sh):
    sh.rect_r(0, 176, 200, 24, "z")
    sh.region(cloud_path(40, 26, 12), "-")
    # lantaarnpaal
    sh.rect_r(174, 54, 6, 122, "z"); sh.region("M177 56Q177 40 160 40H148V46H160Q171 46 171 56Z", "z")
    sh.region("M140 44H160L156 54H144Z", "y")
    for a in (-30, 0, 30): sh.line(f"M{150 + 10 * math.sin(math.radians(a))} {58 + 10 * math.cos(math.radians(a))}l{4 * math.sin(math.radians(a))} {4 * math.cos(math.radians(a))}", "l", "stroke-width:1.6")
    # wagen
    sh.region("M8 168V132H118V168Z", "o")
    sh.region("M118 168V112H142L156 132V168Z", "o"); sh.poly_r([(124, 118), (140, 118), (150, 132), (124, 132)], "b")
    sh.rect_r(150, 150, 8, 8, "y", 2)
    sh.line("M8 150H118")
    sh.rect_r(14, 168, 10, 8, "z"); sh.rect_r(98, 168, 10, 8, "z")
    sh.line("M19 176V184M103 176V184"); sh.rect_r(12, 184, 14, 4, "x", 1); sh.rect_r(96, 184, 14, 4, "x", 1)
    wheel(sh, 44, 170, 11); wheel(sh, 132, 170, 11)
    # arm
    sh.rect_r(46, 120, 24, 14, "z", 2)
    limb(sh, 58, 126, 88, 84, "y", 11); limb(sh, 88, 84, 122, 66, "y", 9)
    sh.circle_r(58, 126, 4, "-"); sh.circle_r(88, 84, 4, "-")
    # bak met monteur
    hy = person(sh, 126, 30, "o", "n", hands=((142, 54), (112, 66)), style="short", hair=None, s=.62, draw_legs=False)
    sh.region(f"M113 {hy - 2}Q113 {hy - 14} 126 {hy - 14}Q139 {hy - 14} 139 {hy - 2}Z", "y"); sh.rect_r(110, hy - 4, 32, 4, "y", 2)
    sh.rect_r(108, 62, 36, 22, "r", 2); sh.line("M108 70H144")

def oldtimer(sh):
    sh.region("M0 200V160H200V200Z", "z")
    sh.region("M0 160V146Q50 138 100 146T200 144V160Z", "l")
    sh.rect_r(20, 70, 8, 76, "w"); sh.region(blob(24, 56, 22, 24, 9), "g")
    sh.circle_r(170, 30, 12, "y")
    # treeplank en spatborden
    sh.rect_r(60, 146, 86, 6, "x", 2)
    # cabine
    sh.rect_r(52, 80, 70, 70, "r", 4); sh.rect_r(46, 72, 82, 10, "x", 4)
    sh.rect_r(60, 90, 24, 24, "b", 3); sh.rect_r(90, 90, 24, 24, "b", 3)
    sh.line("M87 116V146"); sh.rect_r(92, 122, 8, 3, "z", 1)
    # motorkap
    sh.rect_r(122, 112, 52, 34, "r", 3); sh.line("M130 120V138M136 120V138M142 120V138")
    sh.rect_r(172, 104, 9, 42, "z", 2); sh.line("M176.5 108V142", "l", "stroke-width:1.4")
    sh.circle_r(176, 98, 7, "y")
    sh.rect_r(170, 148, 18, 5, "z", 2); sh.rect_r(30, 140, 18, 5, "z", 2)
    sh.circle_r(40, 116, 13, "x"); sh.circle_r(40, 116, 6, "z")
    for x0 in (40, 150):
        sh.region(f"M{x0 - 26} 152Q{x0 - 24} 124 {x0} 124Q{x0 + 24} 124 {x0 + 26} 152Z", "r")
        sh.circle_r(x0, 158, 16, "x"); sh.circle_r(x0, 158, 10, "-")
        for k in range(6):
            a = math.radians(k * 60); sh.seg(x0 + 3 * math.cos(a), 158 + 3 * math.sin(a), x0 + 10 * math.cos(a), 158 + 10 * math.sin(a), "l", "stroke-width:1.5")
        sh.circle_r(x0, 158, 3, "z")

def ijscowagen(sh):
    sh.rect_r(0, 172, 200, 28, "w")
    sh.region(cloud_path(166, 24, 12), "-"); sun(sh, 26, 24, 10)
    # bus
    sh.region("M56 160V66Q56 58 64 58H156Q164 58 168 66L190 110V160Z", "b")
    sh.poly_r([(164, 68), (172, 68), (186, 108), (164, 108)], "-")
    sh.rect_r(66, 82, 76, 40, "-", 2)
    for k in range(6):
        sh.region(f"M{62 + k * 14} 74H{76 + k * 14}V80Q{69 + k * 14} 88 {62 + k * 14} 80Z", "m" if k % 2 == 0 else "-")
    sh.rect_r(62, 122, 84, 6, "w", 2)
    # ijsjes in de toonbank
    for x, c in ((80, "k"), (96, "y"), (112, "w")):
        sh.poly_r([(x - 5, 108), (x + 5, 108), (x, 120)], "o"); sh.circle_r(x, 104, 6, c)
    # ijsjes-verkoper
    hy = person(sh, 128, 84, "-", "-", hands=((118, 116), (140, 118)), style="short", hair="w", s=.55, draw_legs=False, draw_hands=False)
    # groot ijsje op het dak
    sh.poly_r([(102, 44), (122, 44), (112, 60)], "o"); sh.line("M106 48L116 56M118 48L110 56", "l", "stroke-width:1.2")
    sh.circle_r(106, 38, 8, "m"); sh.circle_r(118, 38, 8, "y"); sh.circle_r(112, 29, 8, "k")
    sh.rect_r(176, 132, 10, 8, "y", 2); sh.rect_r(56, 150, 134, 6, "z")
    wheel(sh, 84, 160, 12); wheel(sh, 164, 160, 12)
    # kind met ijsje
    hy = person(sh, 30, 92, "r", "n", hands=((50, 82), (14, 140)), style="braids", hair="x", s=.75, legs=((24, 166), (36, 166)))
    sh.poly_r([(46, 80), (54, 80), (50, 92)], "o"); sh.circle_r(50, 75, 5.5, "k")

def monstertruck(sh):
    sh.region("M0 200V178Q40 170 70 178L100 186L130 178Q170 170 200 178V200Z", "w")
    sh.region(cloud_path(40, 24, 12), "-"); sh.region(cloud_path(160, 30, 10), "-")
    # carrosserie
    sh.region("M20 110V88Q20 80 28 80H70L88 52H138L154 80H178Q186 80 186 90V110Z", "r")
    sh.poly_r([(92, 58), (110, 58), (110, 80), (78, 80)], "b"); sh.poly_r([(116, 58), (134, 58), (146, 80), (116, 80)], "b")
    sh.region("M28 96Q40 86 50 96T72 96", "l") if False else None
    for x in (34, 54): sh.region(f"M{x} 104Q{x - 4} 92 {x + 4} 84Q{x + 6} 94 {x + 10} 90Q{x + 12} 98 {x + 8} 104Z", "y")
    sh.rect_r(180, 86, 8, 8, "y", 2); sh.rect_r(16, 88, 6, 10, "o", 2)
    # vering
    sh.line("M52 110L60 128M64 110L56 128M146 110L154 128M158 110L150 128")
    sh.rect_r(40, 110, 128, 8, "z", 2)
    # reuzenwielen
    for x0 in (52, 152):
        sh.circle_r(x0, 146, 34, "x")
        for k in range(12):
            a = math.radians(k * 30); sh.seg(x0 + 28 * math.cos(a), 146 + 28 * math.sin(a), x0 + 34 * math.cos(a), 146 + 34 * math.sin(a), "l", "stroke-width:2")
        sh.circle_r(x0, 146, 15, "z"); sh.circle_r(x0, 146, 5, "-")
    # modderspetters
    for x, y, r in ((12, 168, 4), (6, 156, 3), (190, 166, 4), (196, 154, 3), (100, 172, 3)): sh.circle_r(x, y, r, "w")

def driemaster(sh):
    sh.region(cloud_path(36, 22, 10), "-"); bird(sh, 160, 18); bird(sh, 176, 26, 4)
    sh.rect_r(0, 150, 200, 50, "b")
    # kluiverzeil en boegspriet
    sh.line("M176 114L198 104"); sh.poly_r([(146, 46), (196, 104), (156, 108)], "-")
    # masten
    for x in (52, 100, 146): sh.rect_r(x - 2, 20, 4, 122, "w")
    # zeilen
    for x, top, n in ((52, 38, 3), (100, 26, 3), (146, 38, 3)):
        y = top
        for k in range(n):
            ww = (14 + k * 3)
            h = 22 + (k == n - 1) * 4
            sh.region(f"M{x - ww} {y}Q{x} {y - 3} {x + ww} {y}Q{x + ww + 3} {y + h / 2} {x + ww} {y + h}H{x - ww}Q{x - ww + 3} {y + h / 2} {x - ww} {y}Z", "-")
            sh.seg(x - ww - 2, y, x + ww + 2, y, "l", "stroke-width:2.6")
            y += h + 4
        sh.poly_r([(x, top - 18), (x + 14, top - 15), (x, top - 12)], "r")
    # kluiverzeil
    # romp
    sh.region("M10 112H180L196 122Q186 154 160 160H40Q18 154 10 112Z", "w")
    sh.rect_r(8, 106, 34, 8, "w", 2)
    sh.line("M14 126H186")
    for x in range(40, 170, 22): sh.circle_r(x, 138, 4, "y")
    sh.rect_r(10, 120, 6, 6, "-")
    waves(sh, 172, 200, 18, 8)
    sh.line("M0 154Q20 150 40 156M160 158Q180 150 200 154")


# ---------- eten ----------
def strawberry(sh, x, y, s=1, code="r"):
    sh.region(f"M{f(x)} {f(y + 12 * s)}C{f(x - 12 * s)} {f(y + 4 * s)} {f(x - 11 * s)} {f(y - 8 * s)} {f(x)} {f(y - 6 * s)}C{f(x + 11 * s)} {f(y - 8 * s)} {f(x + 12 * s)} {f(y + 4 * s)} {f(x)} {f(y + 12 * s)}Z", code)
    sh.region(f"M{f(x - 7 * s)} {f(y - 6 * s)}L{f(x - 2 * s)} {f(y - 9 * s)}L{f(x)} {f(y - 13 * s)}L{f(x + 2 * s)} {f(y - 9 * s)}L{f(x + 7 * s)} {f(y - 6 * s)}L{f(x)} {f(y - 5 * s)}Z", "g")
    for dx, dy in ((-4, -1), (3, 0), (0, 5), (-3, 7), (4, 6)): sh.dot(x + dx * s, y + dy * s, .9 * s)

def fruitschaal(sh):
    sh.rect_r(0, 160, 200, 40, "w"); sh.line("M0 172H200")
    # druiven
    for x, y in ((132, 74), (144, 74), (156, 74), (138, 84), (150, 84), (162, 84), (144, 94), (156, 94), (150, 104)): sh.circle_r(x, y, 7, "p")
    sh.line("M146 68Q148 58 156 54"); leaf_at(sh, 162, 58, 6, 10, 60, "g")
    # banaan
    sh.region("M26 118Q36 72 96 58Q102 60 98 66Q52 80 40 120Z", "y"); sh.line("M96 58L102 54")
    # peer
    sh.region("M100 124C76 124 78 98 90 90C92 78 95 70 100 70C105 70 108 78 110 90C122 98 124 124 100 124Z", "l")
    sh.line("M100 70Q100 64 104 60"); leaf_at(sh, 110, 62, 5, 9, 70, "g")
    # appel en sinaasappel
    sh.region("M64 92C52 84 38 92 40 110C42 126 56 132 64 126C72 132 86 126 88 110C90 92 76 84 64 92Z", "r")
    sh.line("M64 92Q64 84 68 80"); leaf_at(sh, 72, 84, 5, 9, 50, "g")
    sh.circle_r(140, 116, 18, "o"); sh.dot(146, 106, 1.6)
    for dx, dy in ((-8, 4), (4, 10), (-2, -6)): sh.dot(140 + dx, 116 + dy, .8)
    # schaal
    sh.region("M24 120H176Q172 160 100 164Q28 160 24 120Z", "b")
    sh.line("M40 136Q55 128 70 136T100 136T130 136T160 136")
    sh.rect_r(76, 160, 48, 8, "b", 3)
    strawberry(sh, 186, 166, .9); strawberry(sh, 14, 168, .8)

def groentesoep(sh):
    for y in (20, 44, 68, 92): sh.seg(0, y, 200, y, "l", "stroke-width:1")
    for i, y in enumerate((0, 20, 44, 68, 92)):
        for x in range(0 if i % 2 else 20, 200, 40): sh.seg(x, y, x, min(y + 24, 116) if y else 20, "l", "stroke-width:1")
    sh.rect_r(0, 116, 200, 84, "-"); sh.rect_r(0, 116, 200, 26, "z")
    for x in (24, 60, 140, 176): sh.circle_r(x, 166, 7, "x")
    sh.rect_r(10, 180, 180, 6, "z", 3)
    # pan
    sh.rect_r(6, 92, 22, 8, "x", 3); sh.rect_r(150, 92, 22, 8, "x", 3)
    sh.region("M24 88V128Q24 140 36 140H142Q154 140 154 128V88Z", "z")
    sh.ellipse_r(89, 88, 66, 16, "z")
    sh.ellipse_r(89, 88, 58, 11, "y")
    # pollepel
    limb(sh, 120, 86, 160, 26, "w", 6)
    sh.ellipse_r(116, 90, 10, 5, "w")
    for x, y, c, r in ((54, 86, "o", 4.5), (70, 92, "o", 4.5), (88, 84, "g", 3), (96, 92, "g", 3), (64, 82, "g", 3), (100, 86, "o", 4.5), (80, 94, "r", 3.5), (138, 88, "r", 3.5)):
        sh.circle_r(x, y, r, c)
    sh.rect_r(40, 88, 6, 5, "w", 1); sh.rect_r(128, 82, 6, 5, "w", 1)
    for x in (60, 84, 108): sh.line(f"M{x} 66Q{x - 6} 56 {x} 48Q{x + 6} 40 {x} 30")

def boterham(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    for x in range(0, 200, 20): sh.seg(x, 0, x, 200, "l", "stroke-width:.8")
    def slice_(x, y, w, h, code="o"):
        r = w * .26
        sh.region(f"M{x} {y + h}V{y + r}Q{x - 4} {y} {x + r} {y + 2}Q{x + w / 2} {y - 6} {x + w - r} {y + 2}Q{x + w + 4} {y} {x + w} {y + r}V{y + h}Z", code)
        k = 6
        sh.region(f"M{x + k} {y + h - k}V{y + r + 2}Q{x + k - 3} {y + k} {x + r} {y + k + 2}Q{x + w / 2} {y + k - 4} {x + w - r} {y + k + 2}Q{x + w - k + 3} {y + k} {x + w - k} {y + r + 2}V{y + h - k}Z", "y" if code == "o" else "-")
    # bord
    sh.circle_r(100, 104, 92, "b"); sh.circle_r(100, 104, 76, "-")
    # boterham met kaas, sla, tomaat en komkommer
    slice_(22, 40, 76, 86, "w")
    sh.poly_r([(30, 64), (92, 58), (94, 120), (32, 122)], "y")
    for x, y, r in ((40, 114, 3), (86, 66, 2.5), (66, 96, 2.5)): sh.circle_r(x, y, r, "-")
    for x, y, c, r in ((48, 78, "r", 10), (76, 84, "g", 9), (50, 102, "g", 9), (78, 108, "r", 9)):
        sh.circle_r(x, y, r, c); sh.circle_r(x, y, r * .55, "-" if c == "g" else "o")
    # boterham met hagelslag
    slice_(104, 52, 76, 86, "w")
    import random
    rnd = random.Random(5)
    for k in range(40):
        x = rnd.uniform(116, 168); y = rnd.uniform(72, 128); a = rnd.uniform(0, 180)
        sh.raw(f'<g transform="rotate({a:.0f} {x:.1f} {y:.1f})">'); sh.rect_r(x - 3, y - 1, 6, 2.2, "x", 1); sh.raw("</g>")
    # mes
    sh.region("M104 150L158 170Q164 174 158 176L102 158Z", "z"); limb(sh, 158, 172, 186, 182, "r", 8)

def ontbijttafel(sh):
    sh.rect_r(62, 10, 76, 52, "w", 2); sh.rect_r(68, 16, 64, 40, "b"); sh.seg(100, 16, 100, 56); sh.circle_r(118, 30, 7, "y")
    sh.circle_r(28, 34, 14, "-"); sh.line("M28 26V34L34 38")
    sh.region(blob(176, 46, 12, 10, 7), "g"); sh.region("M166 52H186L182 72H170Z", "o"); sh.rect_r(158, 72, 36, 5, "w", 1)
    # tafel
    sh.region("M0 150H200V182Q190 190 180 182Q170 190 160 182Q150 190 140 182Q130 190 120 182Q110 190 100 182Q90 190 80 182Q70 190 60 182Q50 190 40 182Q30 190 20 182Q10 190 0 182Z", "k")
    for x in range(10, 200, 40): sh.region(heart_path(x + 10, 168, 6), "m")
    # eitje in eierdopje
    sh.ellipse_r(28, 102, 13, 17, "-"); sh.line("M15 98L19 93L23 98L28 93L33 98L37 93L41 98", "l", "stroke-width:1.4")
    sh.region("M12 110Q14 128 28 130Q42 128 44 110Z", "y"); sh.rect_r(23, 129, 10, 11, "y"); sh.rect_r(14, 140, 28, 10, "y", 3)
    # glas sap
    sh.region("M52 84H82L78 150H56Z", "-"); sh.region("M53.5 98H80.5L77 148H57Z", "o")
    sh.region("M80 100A9 9 0 0 1 80 82Z", "o") if False else None
    # croissant op een bordje
    # broodmandje
    for x, y, a in ((106, 112, -15), (134, 112, 15), (120, 106, 0)):
        sh.raw(f'<g transform="rotate({a} {x} {y})">'); sh.ellipse_r(x, y, 15, 10, "o"); sh.line(f"M{x - 7} {y - 2}Q{x} {y - 6} {x + 7} {y - 2}", "l", "stroke-width:1.6"); sh.raw("</g>")
    sh.region("M92 116H148L142 150H98Z", "w")
    sh.line("M94 127H146M96 139H144"); sh.line("M106 116L108 150M120 116V150M134 116L132 150", "l", "stroke-width:1.4")
    # kom met muesli en lepel
    limb(sh, 172, 116, 188, 86, "z", 5)
    for x in (152, 162, 172): sh.circle_r(x, 116, 5, "w")
    sh.region("M146 116H190Q188 146 168 146Q148 146 146 116Z", "b"); sh.rect_r(158, 144, 20, 6, "b", 2)

def taartjes_vitrine(sh):
    sh.rect_r(6, 30, 188, 20, "r", 3); sh.region("M6 50H194L188 60H12Z", "w")
    sh.rect_r(10, 60, 180, 112, "w", 3); sh.rect_r(18, 66, 164, 100, "-")
    sh.rect_r(18, 112, 164, 5, "w"); sh.rect_r(6, 172, 188, 24, "w", 3); sh.rect_r(70, 178, 60, 12, "-", 2)
    for x in (28, 70, 110, 150, 182): pass
    # bovenste plank
    sh.region("M26 112V88L60 80V112Z", "k"); sh.line("M26 96L60 88M26 104L60 96"); sh.region("M26 88L60 80L60 84Q50 86 43 84Q36 90 26 90Z", "-")
    strawberry(sh, 46, 78, .6)
    sh.rect_r(70, 96, 32, 16, "y", 2); sh.rect_r(70, 92, 32, 6, "m", 2); sh.line("M70 104H102")
    sh.region("M118 112L114 96H138L134 112Z", "b"); sh.line("M120 98L122 112M126 98V112M132 98L130 112", "l", "stroke-width:1.2")
    sh.region("M112 96Q110 84 126 80Q142 84 140 96Z", "k"); sh.region("M118 86Q126 76 134 86", "l") if False else None
    sh.circle_r(126, 78, 3.5, "r")
    sh.region("M150 112Q150 98 164 98Q178 98 178 112Z", "w"); sh.line("M154 106Q164 100 174 106"); sh.circle_r(158, 96, 3, "-"); sh.circle_r(170, 96, 3, "-")
    # onderste plank
    sh.region("M24 166V148Q24 140 52 140Q80 140 80 148V166Z", "y"); sh.ellipse_r(52, 146, 28, 7, "o")
    for dx, c in ((-16, "r"), (-6, "p"), (4, "r"), (14, "p")): sh.circle_r(52 + dx, 145, 3.2, c)
    for x in (92, 118): sh.region(f"M{x} 166V158Q{x} 150 {x + 10} 150H{x + 14}Q{x + 24} 150 {x + 24} 158V166Z", "w"); sh.region(f"M{x + 2} 156Q{x + 12} 148 {x + 22} 156V159H{x + 2}Z", "x")
    for x, c in ((150, "m"), (164, "g"), (178, "y")):
        sh.ellipse_r(x, 162, 6, 3, c); sh.ellipse_r(x, 156, 6, 3, c); sh.rect_r(x - 5.5, 158.2, 11, 1.6, "-")
    # glans op het glas
    sh.line("M30 70L22 80M38 70L24 86M168 118L158 130M176 118L162 136", "l", "stroke-width:1.2")

def dumplings(sh):
    sh.rect_r(0, 150, 200, 50, "w"); sh.line("M0 164H200M0 184H60M100 184H200", "l", "stroke-width:1.2")
    # mandje
    sh.ellipse_r(84, 106, 64, 18, "o"); sh.ellipse_r(84, 106, 56, 13, "-")
    for x, y in ((60, 104), (104, 102), (82, 110), (40, 112), (126, 112)):
        sh.region(f"M{x - 15} {y}Q{x - 14} {y - 18} {x} {y - 19}Q{x + 14} {y - 18} {x + 15} {y}Q{x} {y + 4} {x - 15} {y}Z", "-")
        sh.line(f"M{x - 5} {y - 16}Q{x - 2} {y - 10} {x - 3} {y - 6}M{x} {y - 19}V{y - 7}M{x + 5} {y - 16}Q{x + 2} {y - 10} {x + 3} {y - 6}", "l", "stroke-width:1.2")
    sh.region("M20 108V148Q84 172 148 148V108Q140 124 84 124Q28 124 20 108Z", "o")
    sh.line("M20 128Q84 148 148 128", "l", "stroke-width:1.4")
    for x in range(32, 140, 14): sh.seg(x, 124 + (abs(x - 84) < 50) * 2, x, 154 - abs(x - 84) * .12, "l", "stroke-width:1.2")
    for x in (64, 84, 104): sh.line(f"M{x} 78Q{x - 5} 68 {x} 60Q{x + 5} 52 {x} 44")
    # stokjes en schaaltje
    limb(sh, 140, 176, 196, 120, "w", 5); limb(sh, 150, 180, 198, 134, "w", 5)
    sh.region("M156 150Q158 168 176 168Q194 168 196 150Z", "b"); sh.ellipse_r(176, 150, 20, 5, "w")

def tacos(sh):
    sh.ellipse_r(100, 162, 94, 26, "-"); sh.ellipse_r(100, 162, 76, 18, "b")
    def taco(cx, y, r, shell):
        sh.region(f"M{cx - r + 2} {y}Q{cx - r + 4} {y - 22} {cx - r + 16} {y - 16}Q{cx - r + 22} {y - 30} {cx - 8} {y - 20}Q{cx} {y - 32} {cx + 10} {y - 20}Q{cx + r - 18} {y - 30} {cx + r - 12} {y - 14}Q{cx + r - 2} {y - 18} {cx + r - 2} {y}Z", "l")
        for dx, dy in ((-r * .5, -10), (-r * .1, -14), (r * .35, -10)): sh.rect_r(cx + dx, y + dy, 7, 7, "r", 1.5)
        sh.region(f"M{cx - r * .7} {y}Q{cx - r * .3} {y - 8} {cx} {y - 4}Q{cx + r * .3} {y - 9} {cx + r * .7} {y}Z", "w")
        sh.line(f"M{cx - r * .6} {y - 6}l6 -6M{cx + r * .2} {y - 8}l6 -7M{cx - r * .1} {y - 4}l-4 -8", "l", "stroke-width:1.6")
        sh.region(f"M{cx - r} {y}A{r} {r} 0 0 0 {cx + r} {y}Z", shell)
        for k in (-r * .5, 0, r * .5): sh.dot(cx + k, y + r * .45, 1.3)
    taco(140, 120, 40, "y"); taco(62, 112, 44, "y")
    # partje limoen en salsa
    sh.region("M154 168A16 16 0 0 0 186 168Z", "l"); sh.line("M170 168L160 178M170 168V184M170 168L180 178", "l", "stroke-width:1.2")
    sh.region("M20 170Q22 186 36 186Q50 186 52 170Z", "w"); sh.ellipse_r(36, 170, 16, 4, "r")
    sun(sh, 178, 22, 10)

def smoothie(sh):
    sh.rect_r(0, 172, 200, 28, "w")
    for x in range(0, 200, 25):
        sh.rect_r(x, 0, 25, 172, "k" if (x // 25) % 2 == 0 else "-")
    # rietje achter de rand
    limb(sh, 110, 90, 130, 26, "b", 7); limb(sh, 130, 26, 144, 20, "b", 7)
    sh.region("M60 52H140L128 168H72Z", "-")
    sh.region("M63 74Q80 66 100 74T137 74L132 120H68Z", "y")
    sh.region("M68 120Q84 112 100 120T132 120L128 164H72Z", "m")
    sh.rect_r(70, 164, 60, 6, "-", 2)
    # partje sinaasappel en aardbei op de rand
    sh.region("M118 54A16 16 0 0 1 150 54Z", "o"); sh.line("M134 54L124 44M134 54V38M134 54L144 44", "l", "stroke-width:1.2")
    strawberry(sh, 64, 46, 1.1)
    for x, y in ((90, 92), (106, 100), (84, 140), (112, 136), (96, 150)): sh.circle_r(x, y, 3, "-")
    # fruit op tafel
    sh.region("M150 186Q172 186 192 162Q196 166 192 170Q178 196 150 192Z", "y")
    strawberry(sh, 28, 182, .9); strawberry(sh, 46, 186, .8)


# ---------- thuis ----------
def duck(sh, x, y, s=1, code="y", flip=False):
    d = -1 if flip else 1
    sh.region(f"M{f(x - 12 * s * d)} {f(y)}Q{f(x - 16 * s * d)} {f(y - 12 * s)} {f(x - 10 * s * d)} {f(y - 8 * s)}Q{f(x)} {f(y - 10 * s)} {f(x + 8 * s * d)} {f(y - 6 * s)}Q{f(x + 14 * s * d)} {f(y)} {f(x + 6 * s * d)} {f(y + 6 * s)}H{f(x - 6 * s * d)}Q{f(x - 12 * s * d)} {f(y + 4 * s)} {f(x - 12 * s * d)} {f(y)}Z", code)
    sh.circle_r(x + 5 * s * d, y - 13 * s, 7 * s, code)
    sh.region(f"M{f(x + 11 * s * d)} {f(y - 14 * s)}L{f(x + 18 * s * d)} {f(y - 12 * s)}L{f(x + 11 * s * d)} {f(y - 9 * s)}Z", "o")
    eye(sh, x + 7 * s * d, y - 15 * s, 1.3 * s)
    sh.line(f"M{f(x - 4 * s * d)} {f(y - 2 * s)}Q{f(x + 2 * s * d)} {f(y + 2 * s)} {f(x + 6 * s * d)} {f(y - 3 * s)}", "l", "stroke-width:1.4")

def in_bad(sh):
    for y in range(20, 112, 23): sh.seg(0, y, 200, y, "l", "stroke-width:.9")
    for x in range(25, 200, 25): sh.seg(x, 0, x, 112, "l", "stroke-width:.9")
    sh.rect_r(0, 176, 200, 24, "w")
    # douche en plankje
    sh.line("M182 112V30Q182 22 174 22H160", "l", "stroke-width:3.5"); sh.region("M148 18H164L168 30H144Z", "z")
    for x in (150, 156, 162): sh.seg(x, 36, x - 1, 42, "l", "stroke-width:1.4")
    sh.rect_r(14, 52, 46, 5, "w", 1)
    sh.rect_r(18, 30, 12, 22, "m", 3); sh.rect_r(21, 26, 6, 4, "-"); sh.rect_r(34, 36, 12, 16, "g", 3); sh.circle_r(53, 46, 6, "o")
    # kind in bad
    head(sh, 96, 76, 1, "curly", "x")
    limb(sh, 80, 104, 66, 76, "-", 10); limb(sh, 112, 104, 128, 78, "-", 10)
    sh.region("M78 112V100Q78 92 88 92H104Q114 92 114 100V112Z", "-")
    sh.circle_r(66, 72, 5, "-"); sh.circle_r(130, 74, 5, "-")
    duck(sh, 140, 68, .9)
    # bad
    sh.region("M12 112H188V128Q188 160 156 160H44Q12 160 12 128Z", "t")
    sh.rect_r(6, 106, 188, 10, "-", 5)
    for x in (40, 160): sh.region(f"M{x - 8} 158Q{x - 10} 176 {x - 2} 178H{x + 2}Q{x + 10} 176 {x + 8} 158Z", "y")
    # schuim
    for x, y, r in ((30, 104, 9), (44, 100, 11), (60, 104, 9), (72, 98, 8), (120, 100, 9), (136, 104, 10), (152, 100, 8), (166, 104, 9), (96, 104, 7)):
        sh.circle_r(x, y, r, "-")
    for x, y, r in ((40, 84, 4), (54, 70, 3), (150, 84, 3.5), (120, 54, 3)): sh.circle_r(x, y, r, "-")
    duck(sh, 46, 92, .8, "y"); duck(sh, 160, 92, .7, "o", True)
    sh.line("M186 106V96Q186 90 180 90H172"); sh.circle_r(186, 92, 3, "z")

def slapen(sh):
    sh.rect_r(0, 168, 200, 32, "w")
    sh.rect_r(10, 12, 64, 54, "w", 2); sh.rect_r(16, 18, 52, 42, "n")
    sh.region(moon_path(34, 34, 9), "y")
    for x, y, r in ((54, 28, 4), (58, 48, 3), (24, 52, 3)): sh.region(star_path(x, y, r, r * .45), "y")
    sh.region("M0 10H14V72H0Z", "p") if False else None
    # lamp en Zzz
    for x, y, sz in ((112, 72, 9), (124, 60, 11), (138, 46, 13)): sh.text(x, y, "Z", sz)
    sh.rect_r(172, 112, 22, 56, "w", 2); sh.rect_r(176, 120, 14, 8, "-", 2)
    sh.rect_r(180, 96, 6, 16, "z"); sh.region("M170 96L176 76H190L196 96Z", "y")
    # bed
    sh.rect_r(10, 80, 20, 92, "w", 4)
    sh.rect_r(150, 112, 14, 60, "w", 4)
    sh.rect_r(22, 124, 136, 22, "-", 3)
    sh.ellipse_r(52, 116, 26, 11, "-")
    head(sh, 58, 104, .95, "short", "o", face=False)
    sh.line("M50 106Q53 109 56 106M60 106Q63 109 66 106", "l", "stroke-width:1.8"); sh.line("M55 112Q58 114 61 112", "l", "stroke-width:1.6")
    # knuffelbeer
    for dx in (-8, 8): sh.circle_r(92 + dx, 92, 5, "w")
    sh.circle_r(92, 100, 11, "w"); sh.ellipse_r(92, 104, 5, 4, "-"); sh.dot(92, 102, 1.5); eye(sh, 88, 97, 1.4); eye(sh, 96, 97, 1.4)
    sh.circle_r(80, 112, 4, "w")
    # deken
    sh.region("M38 150V118Q46 108 66 114Q84 110 104 116Q130 112 156 114V150Z", "b")
    for x, y in ((60, 132), (90, 126), (118, 136), (140, 124), (80, 142)): sh.region(star_path(x, y, 5, 2.2), "y")
    # konijntje op het voeteneind
    for dx in (-4, 4): sh.ellipse_r(132 + dx, 82, 3.5, 11, "k")
    sh.circle_r(132, 96, 9, "k"); eye(sh, 129, 95, 1.2); eye(sh, 135, 95, 1.2); sh.dot(132, 99, 1.2)
    sh.ellipse_r(132, 110, 9, 7, "k")
    sh.rect_r(30, 172, 120, 8, "-") if False else None
    sh.ellipse_r(90, 186, 60, 8, "r")

def samen_koken(sh):
    sh.rect_r(0, 0, 200, 34, "w")
    for x in (0, 50, 100, 150): sh.rect_r(x + 4, 4, 42, 26, "-", 2); sh.rect_r(x + 22, 24, 6, 3, "z", 1)
    for y in (52, 72, 92, 112): sh.seg(0, y, 200, y, "l", "stroke-width:.9")
    # volwassene en kind
    person(sh, 56, 40, "g", "n", hands=((84, 118), (96, 106)), style="bun", hair="w")
    sh.region("M44 80H68V108H44Z", "-") if False else None
    hy = person(sh, 146, 66, "y", "n", hands=((116, 104), (126, 118)), style="short", hair="x", s=.8, cap=True)
    sh.region(f"M132 {hy - 6}Q128 {hy - 22} 136 {hy - 24}Q140 {hy - 34} 148 {hy - 30}Q156 {hy - 36} 160 {hy - 24}Q166 {hy - 20} 160 {hy - 6}Z", "-")
    sh.rect_r(132, hy - 10, 28, 6, "-", 2)
    # aanrecht
    sh.rect_r(0, 128, 200, 10, "w"); sh.rect_r(0, 138, 200, 62, "-")
    for x in (4, 70, 136): sh.rect_r(x, 144, 60, 52, "-", 3); sh.rect_r(x + 26, 150, 8, 3, "z", 1)
    # kom, lepel en garde
    limb(sh, 116, 104, 104, 120, "w", 4)
    sh.region("M70 108H126Q124 128 98 128Q72 128 70 108Z", "b"); sh.ellipse_r(98, 108, 28, 4, "k")
    for x, y in ((84, 118), (96, 106), (116, 104), (126, 118)): sh.circle_r(x, y, 4.5 if x < 110 else 3.6, "-")
    # eieren en meel
    sh.ellipse_r(18, 120, 6, 8, "-"); sh.ellipse_r(32, 122, 6, 8, "w")
    sh.region("M164 128V100L168 94H188L192 100V128Z", "-"); sh.text(178, 116, "MEEL", 6)
    sh.circle_r(150, 124, 4, "y") if False else None

def was_ophangen(sh):
    grass(sh, 180)
    sun(sh, 174, 24, 10); sh.region(cloud_path(56, 26, 12), "-")
    for x in (14, 186): sh.rect_r(x - 3, 86, 6, 100, "w")
    def ry(x):
        t = (x - 14) / 172; return 92 + 88 * t * (1 - t)
    sh.line("M14 92Q100 136 186 92")
    # wasgoed
    def peg(x): sh.rect_r(x - 2, ry(x) - 5, 4, 8, "w", 1)
    x, y = 40, ry(40)
    sh.region(f"M{x - 12} {y}L{x - 22} {y + 8}L{x - 18} {y + 16}L{x - 12} {y + 13}V{y + 38}H{x + 12}V{y + 13}L{x + 18} {y + 16}L{x + 22} {y + 8}L{x + 12} {y}Q{x} {y + 6} {x - 12} {y}Z", "r")
    peg(x - 10); peg(x + 10)
    x, y = 70, ry(70)
    sh.region(f"M{x - 11} {y - 1}H{x + 11}V{y + 34}H{x + 2}L{x} {y + 14}L{x - 2} {y + 34}H{x - 11}Z", "n"); peg(x - 8); peg(x + 8)
    x, y = 146, ry(146)
    sh.region(f"M{x - 14} {y + 1}L{x + 14} {y - 2}L{x + 16} {y + 36}L{x - 12} {y + 38}Z", "y"); sh.line(f"M{x - 12} {y + 30}L{x + 15} {y + 28}", "l", "stroke-width:1.4"); peg(x - 10); peg(x + 10)
    for x0, c in ((166, "m"), (176, "p")):
        y = ry(x0)
        sh.region(f"M{x0 - 3} {y}H{x0 + 3}V{y + 16}Q{x0 + 3} {y + 22} {x0 - 3} {y + 22}H{x0 - 8}Q{x0 - 10} {y + 16} {x0 - 3} {y + 15}Z", c); peg(x0)
    # kind dat een sok ophangt
    hy = person(sh, 108, 100, "o", "b", hands=((94, ry(94) + 2), (122, ry(122) + 2)), style="back", hair="w", s=.8)
    sh.region(f"M124 {ry(124)}H130V{ry(124) + 16}Q130 {ry(124) + 22} 124 {ry(124) + 22}H119Q117 {ry(124) + 16} 124 {ry(124) + 15}Z", "g")
    sh.circle_r(94, ry(94) + 2, 3.6, "-"); sh.circle_r(122, ry(122) + 2, 3.6, "-")
    # wasmand
    sh.region("M20 156H72L66 186H26Z", "w"); sh.line("M22 166H70M24 176H68")
    sh.region("M24 156Q30 144 40 150Q48 140 58 150Q66 144 70 156Z", "t")

def poes_vensterbank(sh):
    sh.rect_r(0, 0, 200, 200, "k")
    sh.rect_r(34, 18, 132, 118, "w", 2); sh.rect_r(42, 26, 116, 102, "b")
    sh.seg(100, 26, 100, 128); sh.seg(42, 77, 158, 77)
    sh.region(cloud_path(130, 46, 11), "-"); sh.circle_r(70, 48, 10, "y"); bird(sh, 120, 100); bird(sh, 136, 108, 4)
    # gordijnen
    sh.region("M24 8H58Q52 60 64 88Q50 96 40 92Q30 130 24 140Z", "m")
    sh.region("M176 8H142Q148 60 136 88Q150 96 160 92Q170 130 176 140Z", "m")
    sh.rect_r(16, 4, 168, 6, "w", 3)
    # vensterbank
    sh.rect_r(16, 136, 168, 10, "w", 2)
    # radiator
    sh.rect_r(40, 160, 120, 34, "-", 3)
    for x in range(52, 160, 12): sh.seg(x, 164, x, 190, "l", "stroke-width:1.4")
    # plant
    for a, c in ((-40, "g"), (0, "l"), (40, "g"), (-15, "g"), (20, "l")):
        leaf_at(sh, 150 + 12 * math.sin(math.radians(a)), 106 - 10 * math.cos(math.radians(a)), 6, 14, a, c)
    sh.region("M138 112H162L158 136H142Z", "o")
    # poes
    sh.region("M70 136C58 136 56 112 66 100C70 92 92 92 96 100C106 112 104 136 92 136Z", "z")
    sh.region("M94 134Q110 134 110 146Q110 168 100 172Q94 174 94 168Q102 160 100 148Q100 142 92 140Z", "z")
    sh.poly_r([(68, 86), (66, 64), (78, 74)], "z"); sh.poly_r([(94, 86), (96, 64), (84, 74)], "z")
    sh.circle_r(81, 84, 16, "z")
    sh.poly_r([(69, 74), (68, 66), (74, 71)], "k"); sh.poly_r([(93, 74), (94, 66), (88, 71)], "k")
    sh.ellipse_r(75, 82, 3, 4, "g"); sh.ellipse_r(87, 82, 3, 4, "g"); sh.dot(75, 82, 1.3); sh.dot(87, 82, 1.3)
    sh.poly_r([(78, 89), (84, 89), (81, 92)], "m"); sh.line("M81 92Q78 96 75 94M81 92Q84 96 87 94", "l", "stroke-width:1.4")
    sh.line("M66 90L52 88M66 94L52 96M96 90L110 88M96 94L110 96", "l", "stroke-width:1.2")
    sh.ellipse_r(72, 134, 7, 4, "z"); sh.ellipse_r(90, 134, 7, 4, "z")


# ---------- wereld ----------
def giraffe(sh, x, gy, s=1):
    def P(dx, dy): return (x + dx * s, gy - dy * s)
    for dx in (-20, 16): limb(sh, *P(dx, 46), *P(dx + 1, 2), "y", 6 * s)
    sh.line(f"M{f(P(-26, 62)[0])} {f(P(-26, 62)[1])}Q{f(P(-34, 50)[0])} {f(P(-34, 50)[1])} {f(P(-32, 38)[0])} {f(P(-32, 38)[1])}")
    sh.region("M{} {}Q{} {} {} {}Q{} {} {} {}Q{} {} {} {}Q{} {} {} {}Z".format(*map(f, (*P(-28, 50), *P(-30, 68), *P(-10, 70), *P(16, 76), *P(28, 74), *P(32, 64), *P(30, 46), *P(0, 42), *P(-28, 50)))), "y")
    sh.region("M{} {}L{} {}Q{} {} {} {}L{} {}Z".format(*map(f, (*P(16, 74), *P(44, 146), *P(52, 148), *P(54, 140), *P(30, 62)))), "y")
    hx, hyy = P(52, 150)
    sh.region(f"M{f(hx - 6 * s)} {f(hyy - 4 * s)}Q{f(hx + 4 * s)} {f(hyy - 8 * s)} {f(hx + 18 * s)} {f(hyy + 2 * s)}Q{f(hx + 20 * s)} {f(hyy + 8 * s)} {f(hx + 14 * s)} {f(hyy + 8 * s)}Q{f(hx)} {f(hyy + 10 * s)} {f(hx - 6 * s)} {f(hyy + 4 * s)}Z", "y")
    for dx in (-2, 4): sh.line(f"M{f(hx + dx * s)} {f(hyy - 5 * s)}V{f(hyy - 13 * s)}"); sh.circle_r(hx + dx * s, hyy - 14 * s, 2 * s, "w")
    sh.ellipse_r(hx - 7 * s, hyy - 2 * s, 5 * s, 2.5 * s, "y")
    eye(sh, hx + 4 * s, hyy - 1 * s, 1.4 * s)
    for dx, dy, r in ((-14, 58, 5), (0, 62, 6), (14, 64, 5), (-4, 50, 4), (22, 56, 4), (30, 84, 3.5), (38, 104, 3.5), (44, 124, 3)):
        sh.circle_r(*P(dx, dy), r * s, "o")
    for dx in (-14, 22): limb(sh, *P(dx, 46), *P(dx - 1, 2), "y", 6 * s)

def savanne(sh):
    sh.circle_r(52, 92, 30, "o")
    sh.region("M0 120Q60 110 110 118T200 114V200H0Z", "y")
    # verre acacia's
    for x, w in ((24, 20), (176, 16)):
        sh.line(f"M{x} 120V108"); sh.region(f"M{x - w} 108Q{x} 94 {x + w} 108Z", "g")
    # grote acacia
    sh.region("M118 186C122 160 120 130 112 104L104 80H112L120 98L128 72H136L128 104C130 130 132 160 138 186Z", "w")
    sh.region("M60 76Q66 52 96 54Q120 36 150 50Q186 48 192 74Q150 84 120 80Q90 84 60 76Z", "g")
    giraffe(sh, 52, 190, .82)
    bird(sh, 160, 24); bird(sh, 176, 32, 5)
    for x in (14, 96, 160, 188): sh.line(f"M{x - 6} 196L{x - 4} 186M{x} 196V184M{x + 6} 196L{x + 4} 186", "l", "stroke-width:1.6")

def noorderlicht(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region("M0 70Q40 30 80 60T160 40T200 30V54Q170 64 160 64Q120 64 80 84Q40 100 0 94Z", "l")
    sh.region("M0 94Q40 100 80 84Q120 64 160 64Q170 64 200 54V70Q170 84 150 82Q110 84 80 104Q40 120 0 114Z", "t")
    for k in range(8):
        x = 12 + k * 25; sh.line(f"M{x} {66 - 18 * math.sin(k * .8)}V{98 - 10 * math.sin(k * .8)}", "l", "stroke-width:1")
    for x, y in ((10, 12), (110, 6), (186, 14), (46, 52), (130, 30), (188, 90), (10, 140), (120, 96)): sh.region(star_path(x, y, 3.5, 1.5), "y")
    # bergen
    sh.region("M0 150L40 106L70 132L110 96L150 132L176 112L200 130V200H0Z", "z")
    sh.region("M28 120L40 106L52 117L44 114L38 122Z", "-"); sh.region("M98 107L110 96L122 108L114 104L106 112Z", "-")
    sh.region("M0 200V160Q60 148 120 160T200 156V200Z", "-")
    # huisje
    sh.rect_r(70, 136, 56, 40, "w")
    for y in (144, 152, 160, 168): sh.seg(70, y, 126, y, "l", "stroke-width:1.2")
    sh.rect_r(110, 112, 8, 20, "w"); sh.poly_r([(62, 140), (98, 112), (134, 140)], "r")
    sh.region("M62 140L98 112L134 140L130 140L98 116L66 140Z", "-")
    sh.rect_r(80, 148, 14, 12, "y", 1); sh.seg(87, 148, 87, 160); sh.rect_r(104, 152, 12, 24, "o", 1)
    sh.line("M114 106Q108 96 116 88Q124 80 118 70", "l", "stroke-width:1.6")
    # dennen met sneeuw
    for x, h in ((26, 50), (160, 56), (186, 44)):
        sh.rect_r(x - 3, 184 - 8, 6, 8, "w")
        for k in range(3):
            y0 = 176 - k * h / 3.6; w = h * (.42 - k * .1)
            sh.region(f"M{f(x - w)} {f(y0)}L{f(x)} {f(y0 - h / 2.2)}L{f(x + w)} {f(y0)}Z", "g")
            sh.region(f"M{f(x - w * .35)} {f(y0 - h / 2.2 * .65)}L{f(x)} {f(y0 - h / 2.2)}L{f(x + w * .35)} {f(y0 - h / 2.2 * .65)}Q{f(x)} {f(y0 - h / 2.2 * .55)} {f(x - w * .35)} {f(y0 - h / 2.2 * .65)}Z", "-")

def fishing_boat(sh, x, y, s, hull, cabin):
    X = lambda dx: f(x + dx * s); Y = lambda dy: f(y + dy * s)
    sh.line(f"M{X(-10)} {Y(0)}V{Y(-60)}M{X(-10)} {Y(-56)}L{X(-40)} {Y(-4)}M{X(-10)} {Y(-56)}L{X(30)} {Y(-32)}", "l", "stroke-width:2")
    sh.region(f"M{X(2)} {Y(0)}V{Y(-28)}H{X(32)}V{Y(0)}Z", cabin)
    sh.rect_r(x + 7 * s, y - 22 * s, 9 * s, 9 * s, "b", 1); sh.rect_r(x + 19 * s, y - 22 * s, 9 * s, 9 * s, "b", 1)
    sh.rect_r(x, y - 32 * s, 34 * s, 5 * s, "x", 1)
    sh.region(f"M{X(-48)} {Y(-4)}H{X(48)}L{X(40)} {Y(22)}H{X(-40)}Z", hull)
    sh.line(f"M{X(-46)} {Y(4)}H{X(46)}", "l", "stroke-width:1.6")
    sh.circle_r(x - 26 * s, y + 12 * s, 3.5 * s, "-"); sh.circle_r(x + 20 * s, y + 12 * s, 3.5 * s, "-")

def vissershaven(sh):
    sh.region(cloud_path(150, 20, 11), "-"); bird(sh, 40, 24); bird(sh, 56, 18, 4); bird(sh, 120, 40, 5)
    # huizen aan de overkant
    xs = [(0, 22, "r"), (22, 20, "y"), (42, 24, "b"), (66, 20, "o"), (86, 22, "m"), (108, 20, "t"), (128, 22, "y"), (150, 24, "r"), (174, 26, "g")]
    for x, w, c in xs:
        h = 26 + (x * 7) % 12
        sh.region(f"M{x} 84V{84 - h}L{x + w / 2} {84 - h - 10}L{x + w} {84 - h}V84Z", c)
        sh.rect_r(x + w / 2 - 4, 84 - h + 6, 8, 8, "-", 1)
    sh.rect_r(0, 84, 200, 6, "z")
    sh.rect_r(0, 90, 200, 80, "b")
    waves(sh, 102, 166, 22, 6)
    fishing_boat(sh, 54, 128, .9, "r", "-"); fishing_boat(sh, 146, 142, 1, "g", "y")
    # kade
    sh.rect_r(0, 170, 200, 30, "z")
    for x in range(0, 200, 25): sh.seg(x, 170 + (x // 25 % 2) * 15, x, 185 + (x // 25 % 2) * 15, "l", "stroke-width:1.2")
    sh.seg(0, 185, 200, 185, "l", "stroke-width:1.2")
    sh.region("M20 170V160Q20 156 26 156Q32 156 32 160V170Z", "x")
    for k, (x, c) in enumerate(((110, "w"), (132, "w"))):
        sh.rect_r(x, 150, 20, 20, c, 1); sh.line(f"M{x} 160H{x + 20}", "l", "stroke-width:1.2")
        sh.region(fish_path(x + 10, 150, 6), "t")
    sh.line("M20 158Q40 150 54 150", "l", "stroke-width:1.6")

def fruitmarkt(sh):
    sh.rect_r(0, 178, 200, 22, "z")
    def stall(x0, w, stripe, items, behind=None):
        sh.line(f"M{x0 + 4} 54V160M{x0 + w - 4} 54V160", "l", "stroke-width:3.5")
        n = 5; sw = w / n
        for k in range(n):
            sh.region(f"M{f(x0 + k * sw)} 36H{f(x0 + (k + 1) * sw)}V58Q{f(x0 + (k + .5) * sw)} 66 {f(x0 + k * sw)} 58Z", stripe if k % 2 == 0 else "-")
        sh.region(f"M{x0 - 4} 36L{x0 + 6} 24H{x0 + w - 6}L{x0 + w + 4} 36Z", stripe)
        if behind: behind()
        sh.rect_r(x0, 132, w, 46, "w"); sh.line(f"M{x0} 146H{x0 + w}M{x0} 162H{x0 + w}", "l", "stroke-width:1.4")
        for i, kind in enumerate(items):
            cx = x0 + w * (i + .5) / len(items)
            sh.region(f"M{cx - 20} 132V118H{cx + 20}V132Z", "w")
            if kind == "appel":
                for dx, dy in ((-12, 112), (0, 112), (12, 112), (-6, 102), (6, 102)): sh.circle_r(cx + dx, dy, 6.5, "r")
            elif kind == "sinaas":
                for dx, dy in ((-12, 112), (0, 112), (12, 112), (-6, 101), (6, 101)): sh.circle_r(cx + dx, dy, 6.5, "o")
            elif kind == "banaan":
                for dy in (0, 8):
                    sh.region(f"M{cx - 18} {108 + dy}Q{cx} {122 + dy} {cx + 18} {104 + dy}Q{cx + 16} {112 + dy} {cx} {116 + dy}Q{cx - 12} {116 + dy} {cx - 18} {108 + dy}Z", "y")
            elif kind == "druif":
                for dx, dy in ((-10, 112), (-2, 112), (6, 112), (-6, 104), (2, 104), (-2, 96), (14, 112), (10, 104)): sh.circle_r(cx + dx, dy, 4.5, "p")
    stall(8, 88, "r", ("appel", "banaan"), lambda: person(sh, 52, 68, "b", "n", hands=((30, 96), (74, 98)), style="short", hair="x", draw_legs=False))
    stall(110, 84, "g", ("sinaas", "druif"))
    # kind met een tas
    hy = person(sh, 104, 112, "y", "n", hands=((90, 150), (118, 146)), style="long", hair="o", s=.62, legs=((100, 170), (108, 170)))
    sh.region("M112 146H128L126 166H114Z", "-"); sh.line("M114 146Q120 138 126 146", "l", "stroke-width:1.6")
    sh.rect_r(140, 64, 30, 18, "-", 2); sh.text(155, 76, "€ 1", 7)

def kabelbaan(sh):
    sh.region(cloud_path(40, 22, 11), "-")
    sh.region("M0 120L50 50L84 90L130 30L200 110V200H0Z", "z")
    sh.region("M38 67L50 50L62 64L54 60L46 70Z", "-"); sh.region("M116 50L130 30L146 50L136 44L126 54Z", "-")
    sh.region("M0 200V136Q60 120 120 140T200 130V200Z", "l")
    # kabel en masten
    sh.line("M20 150L176 42", "l", "stroke-width:1.6"); sh.line("M20 156L176 48", "l", "stroke-width:1.6")
    sh.region("M96 98L92 136H104L100 98Z", "z") if False else None
    sh.rect_r(94, 96, 4, 44, "z"); sh.rect_r(88, 94, 16, 4, "z")
    # gondel
    sh.line("M128 76V90", "l", "stroke-width:2.5"); sh.rect_r(124, 72, 8, 6, "z", 1)
    sh.rect_r(110, 90, 36, 32, "r", 5); sh.rect_r(114, 94, 12, 14, "b", 2); sh.rect_r(130, 94, 12, 14, "b", 2)
    sh.circle_r(120, 104, 4, "-"); sh.circle_r(136, 104, 4, "-")
    # stations
    sh.rect_r(4, 140, 30, 26, "w"); sh.poly_r([(0, 142), (19, 128), (38, 142)], "r")
    sh.rect_r(166, 34, 28, 22, "w"); sh.poly_r([(162, 36), (180, 24), (198, 36)], "r")
    # chalets
    for x, y, c in ((60, 168, "o"), (110, 176, "y"), (156, 164, "o")):
        sh.rect_r(x - 16, y - 24, 32, 24, c)
        sh.poly_r([(x - 22, y - 22), (x, y - 40), (x + 22, y - 22)], "w")
        sh.rect_r(x - 10, y - 18, 8, 8, "b", 1); sh.rect_r(x + 3, y - 16, 7, 16, "w", 1)
        sh.line(f"M{x - 16} {y - 8}H{x - 2}", "l", "stroke-width:1.2")
    for x, h in ((20, 30), (84, 26), (186, 30), (134, 24)):
        sh.rect_r(x - 2, 194 - 6, 4, 6, "w")
        sh.region(f"M{x - h * .32} 188L{x} {188 - h}L{x + h * .32} 188Z", "g")


# ---------- sport ----------
def oar(sh, x1, y1, x2, y2):
    limb(sh, x1, y1, x2, y2, "w", 4)
    a = math.degrees(math.atan2(y2 - y1, x2 - x1))
    sh.raw(f'<g transform="rotate({a:.1f} {x2} {y2})">'); sh.ellipse_r(x2, y2, 11, 5, "w"); sh.raw("</g>")

def roeien(sh):
    sh.region(cloud_path(150, 22, 12), "-"); sun(sh, 34, 24, 10)
    sh.region("M0 96V80Q50 70 100 78T200 74V96Z", "g")
    for x, r in ((150, 14), (176, 11), (24, 12)):
        sh.rect_r(x - 2, 70, 4, 14, "w"); sh.region(blob(x, 62, r, r * .9, 8), "g")
    sh.rect_r(0, 96, 200, 104, "b")
    waves(sh, 110, 200, 24)
    # kinderen in de boot
    person(sh, 72, 76, "r", "n", hands=((58, 126), (66, 122)), style="pony", hair="o", s=.72, draw_legs=False, draw_hands=False)
    person(sh, 128, 78, "y", "n", hands=((134, 122), (142, 126)), style="short", hair="x", s=.72, draw_legs=False, draw_hands=False)
    # boot
    sh.region("M20 128Q100 142 180 128L166 160Q100 168 34 160Z", "o")
    sh.line("M26 140Q100 152 174 140", "l", "stroke-width:1.6")
    oar(sh, 62, 122, 14, 172); oar(sh, 138, 122, 186, 172)
    for x, y in ((58, 126), (66, 122), (134, 122), (142, 126)): sh.circle_r(x, y, 3.4, "-")
    # eendjes en riet
    for x, y in ((40, 104), (54, 108)):
        sh.ellipse_r(x, y, 6, 3.5, "w"); sh.circle_r(x + 5, y - 4, 2.8, "w"); sh.poly_r([(x + 7.5, y - 4.5), (x + 11, y - 3.5), (x + 7.5, y - 2.5)], "o")
    for x in (184, 192): sh.line(f"M{x} 112V86"); sh.ellipse_r(x, 90, 2.5, 6, "w")

def piece(sh, kind, x, base, h, code):
    w = h * .32
    sh.region(f"M{f(x - w * 1.25)} {f(base)}V{f(base - h * .12)}Q{f(x)} {f(base - h * .2)} {f(x + w * 1.25)} {f(base - h * .12)}V{f(base)}Z", code)
    if kind == "pion":
        sh.region(f"M{f(x - w)} {f(base - h * .14)}L{f(x - w * .4)} {f(base - h * .6)}H{f(x + w * .4)}L{f(x + w)} {f(base - h * .14)}Z", code)
        sh.circle_r(x, base - h * .74, w * .7, code)
    elif kind == "toren":
        sh.rect_r(x - w * .8, base - h * .8, w * 1.6, h * .66, code)
        sh.region(f"M{f(x - w)} {f(base - h * .78)}V{f(base - h)}H{f(x - w * .45)}V{f(base - h * .9)}H{f(x - w * .15)}V{f(base - h)}H{f(x + w * .15)}V{f(base - h * .9)}H{f(x + w * .45)}V{f(base - h)}H{f(x + w)}V{f(base - h * .78)}Z", code)
    elif kind == "paard":
        sh.region(f"M{f(x - w)} {f(base - h * .14)}Q{f(x - w * 1.1)} {f(base - h * .5)} {f(x - w * .3)} {f(base - h * .7)}L{f(x - w * 1.1)} {f(base - h * .62)}Q{f(x - w * 1.3)} {f(base - h * .74)} {f(x - w * .4)} {f(base - h * .96)}L{f(x)} {f(base - h * 1.04)}Q{f(x + w * 1.2)} {f(base - h * .9)} {f(x + w)} {f(base - h * .14)}Z", code)
        sh.dot(x - w * .2, base - h * .82, h * .03)
    elif kind in ("koning", "dame"):
        sh.region(f"M{f(x - w)} {f(base - h * .14)}L{f(x - w * .45)} {f(base - h * .7)}H{f(x + w * .45)}L{f(x + w)} {f(base - h * .14)}Z", code)
        sh.rect_r(x - w * .7, base - h * .76, w * 1.4, h * .08, code, 1)
        if kind == "koning":
            sh.region(f"M{f(x - w * .5)} {f(base - h * .76)}Q{f(x)} {f(base - h * .98)} {f(x + w * .5)} {f(base - h * .76)}Z", code)
            sh.rect_r(x - h * .03, base - h * 1.12, h * .06, h * .2, code); sh.rect_r(x - h * .09, base - h * 1.05, h * .18, h * .06, code)
        else:
            sh.region(f"M{f(x - w * .6)} {f(base - h * .76)}L{f(x - w * .7)} {f(base - h * .96)}L{f(x - w * .3)} {f(base - h * .86)}L{f(x)} {f(base - h)}L{f(x + w * .3)} {f(base - h * .86)}L{f(x + w * .7)} {f(base - h * .96)}L{f(x + w * .6)} {f(base - h * .76)}Z", code)
            sh.circle_r(x, base - h * 1.04, h * .05, code)

def schaken(sh):
    sh.rect_r(0, 0, 200, 100, "-"); sh.rect_r(140, 14, 44, 36, "o", 2); sh.rect_r(146, 20, 32, 24, "-"); sh.line("M150 40L158 28L164 36L168 30L174 40")
    sh.rect_r(16, 20, 26, 26, "-", 13); sh.line("M29 24V33L35 37")
    # kind dat nadenkt
    hy = person(sh, 100, 38, "g", "n", hands=((112, 60), (70, 106)), style="curly", hair="w", draw_legs=False)
    # tafel en bord
    sh.region("M14 104H186L200 200H0Z", "w")
    def q(u, v):
        x0 = 44 + 112 * u; x1 = 14 + 172 * u
        return (x0 + (x1 - x0) * v, 110 + 78 * v)
    for i in range(8):
        for j in range(8):
            sh.poly_r([q(i / 8, j / 8), q((i + 1) / 8, j / 8), q((i + 1) / 8, (j + 1) / 8), q(i / 8, (j + 1) / 8)], "z" if (i + j) % 2 else "-")
    def at(i, j, kind, code, h=None):
        x, y = q((i + .5) / 8, (j + .7) / 8); hh = h or (14 + 10 * j / 8) * (1.35 if kind in ("koning", "dame") else 1.15 if kind in ("paard", "toren") else 1)
        piece(sh, kind, x, y, hh, code)
    for i, j, k, c in ((1, 0, "toren", "x"), (4, 0, "koning", "x"), (6, 1, "pion", "x"), (2, 1, "pion", "x"), (5, 2, "paard", "x"), (3, 3, "pion", "x"),
                       (4, 4, "pion", "-"), (2, 5, "paard", "-"), (6, 5, "pion", "-"), (1, 6, "pion", "-"), (3, 7, "dame", "-"), (5, 7, "koning", "-"), (7, 7, "toren", "-")):
        at(i, j, k, c)
    sh.circle_r(70, 106, 4.5, "-")

def klimmuur(sh):
    sh.rect_r(0, 0, 200, 186, "b"); sh.rect_r(0, 186, 200, 14, "z")
    for x in (50, 100, 150): sh.seg(x, 0, x, 186, "l", "stroke-width:1")
    for y in (62, 124): sh.seg(0, y, 200, y, "l", "stroke-width:1")
    holds = [(20, 30, "r"), (64, 20, "y"), (122, 34, "g"), (176, 18, "o"), (34, 84, "p"), (140, 70, "r"), (182, 96, "y"), (20, 140, "g"), (60, 160, "o"), (130, 150, "p"), (166, 136, "g"), (112, 104, "y")]
    for x, y, c in holds: sh.region(blob(x, y, 7, 5, 6, .6, .4), c)
    # touw
    sh.circle_r(96, 4, 4, "z")
    sh.line("M92 4L86 96M100 4Q130 80 160 140", "l", "stroke-width:1.8")
    # klimmer van achteren
    sh.region(blob(68, 58, 7, 5, 6, .6, .4), "o"); sh.region(blob(108, 72, 7, 5, 6, .6), "m")
    sh.region(blob(76, 140, 7, 5, 6, .6), "y"); sh.region(blob(102, 124, 7, 5, 6, .6), "r")
    hy = person(sh, 88, 60, "r", "n", hands=((68, 58), (108, 72)), legs=((76, 134), (102, 120)), style="back", hair="w", s=.9, cap=True)
    sh.region(f"M75 {hy - 2}Q75 {hy - 15} 88 {hy - 15}Q101 {hy - 15} 101 {hy - 2}Z", "y")
    sh.rect_r(73, hy + 46, 30, 6, "x", 2); sh.circle_r(88, hy + 52, 3, "z")
    # zekeraar
    person(sh, 166, 108, "g", "n", hands=((156, 136), (176, 146)), style="long", hair="x", s=.72)
    sh.rect_r(154, 150, 24, 5, "x", 2)

def rolschaatsen(sh):
    sh.region("M0 200V160H200V200Z", "z"); sh.line("M0 160H200")
    sh.region("M0 160V136Q50 128 100 134T200 132V160Z", "l")
    for x, r in ((26, 18), (176, 16)): sh.rect_r(x - 3, 110, 6, 30, "w"); sh.region(blob(x, 96, r, r, 9), "g")
    sun(sh, 150, 26, 10); sh.region(cloud_path(52, 26, 12), "-")
    def skate(x, y, c):
        sh.region(f"M{x - 8} {y + 6}V{y - 8}H{x + 2}V{y - 2}Q{x + 12} {y - 1} {x + 12} {y + 6}Z", c)
        for dx in (-5, 1, 7): sh.circle_r(x + dx, y + 10, 3.4, "x")
        sh.rect_r(x - 10, y + 5, 24, 3, "z", 1)
    hy = person(sh, 98, 32, "m", "p", hands=((60, 82), (138, 72)), legs=((80, 140), (120, 132)), style="braids", hair="x", s=1.05, shoes=None, cap=True)
    sh.region(f"M82 {hy - 2}Q82 {hy - 20} 98 {hy - 20}Q114 {hy - 20} 114 {hy - 2}Z", "r")
    sh.line(f"M88 {hy - 18}L92 {hy - 4}M108 {hy - 18}L104 {hy - 4}", "l", "stroke-width:1.4")
    for x, y in ((86, 112), (114, 108)): sh.ellipse_r(x, y, 7, 5, "b")
    skate(78, 146, "t"); skate(122, 138, "t")
    for y in (90, 104, 118): sh.line(f"M30 {y}H50", "l", "stroke-width:1.6")

def honkbal(sh):
    sh.rect_r(0, 0, 200, 120, "-")
    for x in range(0, 200, 16): sh.seg(x, 60, x, 120, "l", "stroke-width:1")
    sh.seg(0, 60, 200, 60, "l", "stroke-width:1.4"); sh.seg(0, 90, 200, 90, "l", "stroke-width:1")
    sh.region("M0 120H200V200H0Z", "l")
    sh.region("M60 200L100 150L140 200Z", "w"); sh.poly_r([(90, 182), (110, 182), (110, 188), (100, 194), (90, 188)], "-")
    # slagman
    limb(sh, 112, 86, 170, 36, "w", 7); sh.circle_r(170, 36, 5, "w")
    hy = person(sh, 86, 70, "n", "-", hands=((108, 90), (114, 84)), legs=((70, 176), (104, 172)), style="short", hair=None, s=1, cap=True)
    sh.region(f"M71 {hy}Q71 {hy - 16} 86 {hy - 16}Q101 {hy - 16} 101 {hy}Z", "r"); sh.region(f"M98 {hy - 4}H114Q114 {hy + 2} 98 {hy + 1}Z", "r")
    sh.text(86, hy + 42, "7", 12)
    # bal
    sh.circle_r(184, 22, 8, "-"); sh.line("M179 16Q183 22 179 28M189 16Q185 22 189 28", "l", "stroke-width:1.2")
    sh.line("M150 14H166M154 24H168M148 32H162", "l", "stroke-width:1.6")

def racket(sh, x1, y1, x2, y2, code):
    limb(sh, x1, y1, x2, y2, "x", 4)
    a = math.degrees(math.atan2(y2 - y1, x2 - x1)) + 90
    sh.raw(f'<g transform="rotate({a:.1f} {x2} {y2})">')
    sh.ellipse_r(x2, y2 - 10, 9, 12, code)
    for k in (-4, 0, 4): sh.seg(x2 + k, y2 - 21, x2 + k, y2 + 1, "l", "stroke-width:.9"); sh.seg(x2 - 8, y2 - 10 + k * 1.6, x2 + 8, y2 - 10 + k * 1.6, "l", "stroke-width:.9")
    sh.raw("</g>")

def badminton(sh):
    grass(sh, 170)
    sh.region("M0 172Q50 164 100 172T200 170V200H0Z", "l") if False else None
    sh.region(cloud_path(40, 24, 12), "-"); sun(sh, 170, 26, 10)
    # net
    for x in (74, 126): sh.rect_r(x - 2, 96, 4, 84, "w")
    sh.rect_r(76, 100, 48, 30, "-")
    for x in range(82, 124, 6): sh.seg(x, 100, x, 130, "l", "stroke-width:.9")
    for y in range(106, 130, 6): sh.seg(76, y, 124, y, "l", "stroke-width:.9")
    sh.rect_r(74, 98, 52, 4, "w", 1)
    # kinderen
    person(sh, 40, 78, "o", "n", hands=((60, 72), (22, 130)), style="long", hair="w", s=.85)
    racket(sh, 60, 72, 68, 52, "r")
    person(sh, 156, 84, "t", "p", hands=((134, 132), (172, 114)), style="short", hair="x", s=.85)
    racket(sh, 172, 114, 178, 94, "y")
    # shuttle
    sh.region("M98 42L108 22Q118 24 122 34L102 48Z", "-"); sh.line("M100 45L112 25M101 47L117 29", "l", "stroke-width:1")
    sh.circle_r(99, 47, 4.5, "r")
    sh.line("M86 54Q78 60 76 68", "l", "stroke-width:1.2")


PLATES = [
    ("veerpont", "Met de pont naar de overkant", "voertuigen", "6-9", 2, veerpont),
    ("takelwagen", "Takelwagen met auto", "voertuigen", "4-6", 2, takelwagen),
    ("tuktuk", "Tuktuk", "voertuigen", "4-6", 2, tuktuk),
    ("hoogwerker", "Hoogwerker bij de lantaarnpaal", "voertuigen", "6-9", 2, hoogwerker),
    # ("oldtimer", "Oldtimer", "voertuigen", "6-9", 2, oldtimer),
    ("ijscowagen", "IJscowagen", "voertuigen", "4-6", 2, ijscowagen),
    ("monstertruck", "Monstertruck", "voertuigen", "2-4", 1, monstertruck),
    ("driemaster", "Zeilschip met drie masten", "voertuigen", "9+", 3, driemaster),
    ("fruitschaal", "Fruitschaal", "eten", "2-4", 1, fruitschaal),
    ("groentesoep", "Groentesoep in de pan", "eten", "4-6", 2, groentesoep),
    ("boterham-met-beleg", "Boterhammen met beleg", "eten", "2-4", 1, boterham),
    ("ontbijttafel", "Ontbijt op tafel", "eten", "4-6", 2, ontbijttafel),
    ("taartjes-in-de-vitrine", "Taartjes in de vitrine", "eten", "6-9", 3, taartjes_vitrine),
    ("dumplings", "Dumplings in een stoommandje", "eten", "4-6", 2, dumplings),
    # ("tacos", "Taco's", "eten", "4-6", 2, tacos),
    ("smoothie", "Fruitsmoothie", "eten", "2-4", 1, smoothie),
    ("in-bad-met-eendjes", "In bad met eendjes", "thuis", "2-4", 1, in_bad),
    ("slapen-met-knuffels", "Slapen met knuffels", "thuis", "2-4", 1, slapen),
    ("samen-koken", "Samen koken", "thuis", "4-6", 2, samen_koken),
    ("was-ophangen", "De was ophangen", "thuis", "4-6", 2, was_ophangen),
    ("poes-in-de-vensterbank", "Poes in de vensterbank", "thuis", "2-4", 1, poes_vensterbank),
    ("savanne", "Savanne met acaciaboom", "wereld", "6-9", 2, savanne),
    ("noorderlicht", "Noorderlicht boven een houten huisje", "wereld", "6-9", 2, noorderlicht),
    ("vissershaven", "Vissershaven", "wereld", "6-9", 3, vissershaven),
    ("fruitmarkt", "Fruitmarkt", "wereld", "4-6", 2, fruitmarkt),
    ("bergdorp-met-kabelbaan", "Bergdorp met kabelbaan", "wereld", "6-9", 2, kabelbaan),
    ("roeien", "Roeien op het meer", "sport", "6-9", 2, roeien),
    ("schaken", "Schaken", "sport", "9+", 3, schaken),
    ("klimmuur", "Klimmen op de klimmuur", "sport", "6-9", 2, klimmuur),
    ("rolschaatsen", "Rolschaatsen", "sport", "4-6", 2, rolschaatsen),
    ("honkbal", "Honkbal", "sport", "6-9", 2, honkbal),
    ("badminton", "Badminton", "sport", "4-6", 2, badminton),
]

for slug, name, cat, age, diff, draw in PLATES:
    kp(slug, name, cat, age, diff, draw)
