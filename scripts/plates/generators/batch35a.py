"""Batch 35a: nieuwe kleurplaten (eigen tekeningen, 200x200) rond feestdagen en het jaar rond: mensen die samen iets vieren."""
import math, random
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from shapes import heart_path, star_path, moon_path, cloud_path, leaf_path, drop_path


# ---------- hulpjes (overgenomen uit batch 10a, niet geïmporteerd) ----------
def limb(sh, x1, y1, x2, y2, code, w=9):
    """Arm of been als balk met afgeronde uiteinden van (x1,y1) naar (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * w / 2, dx / d * w / 2
    r = w / 2
    sh.region(f"M{f(x1 + nx)} {f(y1 + ny)}L{f(x2 + nx)} {f(y2 + ny)}A{f(r)} {f(r)} 0 0 0 {f(x2 - nx)} {f(y2 - ny)}L{f(x1 - nx)} {f(y1 - ny)}A{f(r)} {f(r)} 0 0 0 {f(x1 + nx)} {f(y1 + ny)}Z", code)

def blob(cx, cy, rx, ry, n=9, bulge=.62, start=0):
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
    elif style == "back":
        sh.circle_r(cx, hy, r, code)
    else:
        sh.region(top + f"Q{f(cx + 8 * s)} {f(hy - 9 * s)} {f(cx - 2 * s)} {f(hy - 7 * s)}Q{f(cx - 10 * s)} {f(hy - 6 * s)} {f(cx - r)} {f(hy)}Z", code)

def person(sh, cx, top, shirt="-", pants="-", hands=None, hair="w", style="short", legs=None, cap=False, shoes="x",
           face=True, s=1, skirt=None, arms=None, arms_front=False, draw_legs=True, draw_hands=True, hand="-"):
    """Kind/volwassene van voren (of van achteren met style="back"). top = bovenkant hoofd, s = schaal."""
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

def beanie(sh, cx, hy, code, rim="-", s=1):
    sh.region(f"M{f(cx - 16 * s)} {f(hy - 2 * s)}Q{f(cx - 16 * s)} {f(hy - 20 * s)} {f(cx)} {f(hy - 20 * s)}Q{f(cx + 16 * s)} {f(hy - 20 * s)} {f(cx + 16 * s)} {f(hy - 2 * s)}Z", code)
    sh.rect_r(cx - 17 * s, hy - 6 * s, 34 * s, 7 * s, rim, 3 * s)
    sh.circle_r(cx, hy - 21 * s, 5 * s, rim)

def scarf(sh, cx, hy, code, s=1):
    sh.region(f"M{f(cx + 3 * s)} {f(hy + 17 * s)}L{f(cx + 6 * s)} {f(hy + 36 * s)}H{f(cx + 13 * s)}L{f(cx + 10 * s)} {f(hy + 17 * s)}Z", code)
    sh.rect_r(cx - 12 * s, hy + 12 * s, 24 * s, 7 * s, code, 3 * s)

def sun(sh, x, y, r=12, rays=True):
    sh.circle_r(x, y, r, "y")
    if rays:
        for k in range(8):
            a = math.radians(k * 45 + 22)
            sh.seg(x + (r + 3) * math.cos(a), y + (r + 3) * math.sin(a), x + (r + 8) * math.cos(a), y + (r + 8) * math.sin(a))

def bird(sh, x, y, w=6):
    sh.line(f"M{f(x - w)} {f(y)}Q{f(x - w / 2)} {f(y - w * .6)} {f(x)} {f(y)}Q{f(x + w / 2)} {f(y - w * .6)} {f(x + w)} {f(y)}")

def sheep(sh, x, y, s=1, face_left=False):
    d = -1 if face_left else 1
    for dx in (-12, -5, 6, 12): sh.rect_r(x + dx * s - 2 * s, y + 8 * s, 4 * s, 12 * s, "x")
    sh.region(blob(x, y, 20 * s, 12 * s, 11, .7), "-")
    sh.ellipse_r(x + d * 20 * s, y - 6 * s, 7 * s, 9 * s, "z")
    sh.ellipse_r(x + d * 14 * s, y - 10 * s, 5 * s, 2.4 * s, "z")
    eye(sh, x + d * 22 * s, y - 8 * s, 1.4 * s)


# ---------- nieuwe hulpjes ----------
def face(sh, cx, hy, s=1, mouth="smile"):
    eye(sh, cx - 5 * s, hy + 3 * s, 1.8 * s); eye(sh, cx + 5 * s, hy + 3 * s, 1.8 * s)
    if mouth == "open": sh.ellipse_r(cx, hy + 9 * s, 3 * s, 2.6 * s, "-")
    else: smile(sh, cx, hy + 8 * s, 4 * s)

def headscarf(sh, cx, hy, s, code):
    """Hoofddoek over het hoofd (teken person met hair=None, face=False)."""
    sh.region(f"M{f(cx - 17 * s)} {f(hy + 4 * s)}Q{f(cx - 19 * s)} {f(hy - 19 * s)} {f(cx)} {f(hy - 19 * s)}Q{f(cx + 19 * s)} {f(hy - 19 * s)} {f(cx + 17 * s)} {f(hy + 4 * s)}L{f(cx + 17 * s)} {f(hy + 22 * s)}Q{f(cx)} {f(hy + 28 * s)} {f(cx - 17 * s)} {f(hy + 22 * s)}Z", code)
    sh.ellipse_r(cx, hy + 2 * s, 11 * s, 12.5 * s, "-")
    face(sh, cx, hy, s * .9)

def angisa(sh, cx, hy, s, code):
    """Gevouwen hoofddoek (angisa): een bolle doek om het hoofd met een gesteven, schuin opstaande punt opzij."""
    sh.region(f"M{f(cx + 2 * s)} {f(hy - 16 * s)}L{f(cx + 20 * s)} {f(hy - 36 * s)}L{f(cx + 28 * s)} {f(hy - 22 * s)}L{f(cx + 16 * s)} {f(hy - 8 * s)}Z", code)
    sh.line(f"M{f(cx + 9 * s)} {f(hy - 12 * s)}L{f(cx + 24 * s)} {f(hy - 29 * s)}", "l", "stroke-width:1.1")
    sh.region(f"M{f(cx - 16 * s)} {f(hy + 2 * s)}C{f(cx - 20 * s)} {f(hy - 16 * s)} {f(cx - 10 * s)} {f(hy - 24 * s)} {f(cx + 1 * s)} {f(hy - 23 * s)}C{f(cx + 12 * s)} {f(hy - 22 * s)} {f(cx + 20 * s)} {f(hy - 14 * s)} {f(cx + 16 * s)} {f(hy + 2 * s)}Q{f(cx)} {f(hy - 8 * s)} {f(cx - 16 * s)} {f(hy + 2 * s)}Z", code)
    sh.line(f"M{f(cx - 15 * s)} {f(hy - 7 * s)}Q{f(cx - 2 * s)} {f(hy - 17 * s)} {f(cx + 14 * s)} {f(hy - 12 * s)}M{f(cx - 12 * s)} {f(hy - 16 * s)}Q{f(cx)} {f(hy - 22 * s)} {f(cx + 10 * s)} {f(hy - 19 * s)}", "l", "stroke-width:1.1")
    sh.circle_r(cx + 15 * s, hy - 10 * s, 3 * s, code)

def party_hat(sh, cx, hy, s, code, dots="y"):
    sh.region(f"M{f(cx - 10 * s)} {f(hy - 11 * s)}L{f(cx + 1 * s)} {f(hy - 36 * s)}L{f(cx + 11 * s)} {f(hy - 10 * s)}Q{f(cx)} {f(hy - 14 * s)} {f(cx - 10 * s)} {f(hy - 11 * s)}Z", code)
    sh.circle_r(cx + 1 * s, hy - 37 * s, 3.5 * s, dots)
    sh.line(f"M{f(cx - 6 * s)} {f(hy - 20 * s)}L{f(cx + 7 * s)} {f(hy - 22 * s)}", "l", "stroke-width:1")

def bunting(sh, x1, y1, x2, y2, n, codes, sag=10, size=9):
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2 + 2 * sag
    sh.line(f"M{f(x1)} {f(y1)}Q{f(cx)} {f(cy)} {f(x2)} {f(y2)}")
    P = lambda t: ((1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t * t * x2, (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t * t * y2)
    for i in range(n):
        a, b, m = P((i + .12) / n), P((i + .88) / n), P((i + .5) / n)
        sh.poly_r([a, b, (m[0], m[1] + size)], codes[i % len(codes)])

def balloon(sh, x, y, r, code, end):
    sh.line(f"M{f(x)} {f(y + r * 1.25)}Q{f(x - 6)} {f((y + end[1]) / 2)} {f(end[0])} {f(end[1])}", "l", "stroke-width:1.2")
    sh.poly_r([(x, y + r * 1.15), (x - 2.5, y + r * 1.25 + 3), (x + 2.5, y + r * 1.25 + 3)], code)
    sh.ellipse_r(x, y, r, r * 1.2, code)
    sh.line(f"M{f(x - r * .5)} {f(y - r * .4)}Q{f(x - r * .4)} {f(y - r * .8)} {f(x)} {f(y - r * .85)}", "l", "stroke-width:1.2")

def present(sh, x, y, w, h, code, ribbon="r"):
    """Pakje met (x,y) = linksboven van de doos."""
    sh.rect_r(x, y, w, h, code, 1)
    sh.rect_r(x - 2, y - 6, w + 4, 7, code, 1)
    sh.rect_r(x + w / 2 - 3, y - 6, 6, h + 6, ribbon)
    sh.region(f"M{f(x + w / 2)} {f(y - 6)}C{f(x + w / 2 - 12)} {f(y - 18)} {f(x + w / 2 - 14)} {f(y - 4)} {f(x + w / 2)} {f(y - 6)}Z", ribbon)
    sh.region(f"M{f(x + w / 2)} {f(y - 6)}C{f(x + w / 2 + 12)} {f(y - 18)} {f(x + w / 2 + 14)} {f(y - 4)} {f(x + w / 2)} {f(y - 6)}Z", ribbon)

def burst(sh, x, y, r, code, n=10):
    for k in range(n):
        a = 360 * k / n
        sh.raw(f'<g transform="rotate({f(float(a))} {f(float(x))} {f(float(y))})">')
        sh.region(f"M{f(x)} {f(y - r * .25)}Q{f(x + r * .14)} {f(y - r * .6)} {f(x)} {f(y - r)}Q{f(x - r * .14)} {f(y - r * .6)} {f(x)} {f(y - r * .25)}Z", code)
        sh.raw("</g>")
        a2 = math.radians(a + 180 / n)
        sh.dot(x + r * .8 * math.sin(a2), y - r * .8 * math.cos(a2), 1.2)
    sh.circle_r(x, y, r * .14, code)

def diya(sh, x, y, s=1, bowl="o", flame="y"):
    sh.region(drop_path(x, y - 9 * s, 3 * s), flame)
    sh.region(f"M{f(x - 10 * s)} {f(y - 3 * s)}Q{f(x - 9 * s)} {f(y + 5 * s)} {f(x)} {f(y + 5 * s)}Q{f(x + 9 * s)} {f(y + 5 * s)} {f(x + 10 * s)} {f(y - 3 * s)}Q{f(x)} {f(y)} {f(x - 10 * s)} {f(y - 3 * s)}Z", bowl)
    sh.dot(x - 4 * s, y + 1.5 * s, .9); sh.dot(x, y + 2.2 * s, .9); sh.dot(x + 4 * s, y + 1.5 * s, .9)

def egg(sh, x, y, s, code, pattern=0):
    rx, ry = 7 * s, 9 * s
    sh.region(f"M{f(x)} {f(y - ry)}C{f(x + rx * 1.1)} {f(y - ry)} {f(x + rx * 1.1)} {f(y + ry)} {f(x)} {f(y + ry)}C{f(x - rx * 1.1)} {f(y + ry)} {f(x - rx * 1.1)} {f(y - ry)} {f(x)} {f(y - ry)}Z", code)
    if pattern == 1:
        sh.line(f"M{f(x - rx * .8)} {f(y)}L{f(x - rx * .4)} {f(y - 2.5 * s)}L{f(x)} {f(y)}L{f(x + rx * .4)} {f(y - 2.5 * s)}L{f(x + rx * .8)} {f(y)}", "l", "stroke-width:1")
    elif pattern == 2:
        for dx, dy in ((-3, -3), (2, -5), (3, 1), (-2, 4)): sh.dot(x + dx * s, y + dy * s, 1.1 * s)
    elif pattern == 3:
        sh.line(f"M{f(x - rx * .8)} {f(y - 2 * s)}Q{f(x)} {f(y - 4 * s)} {f(x + rx * .8)} {f(y - 2 * s)}M{f(x - rx * .8)} {f(y + 3 * s)}Q{f(x)} {f(y + 1 * s)} {f(x + rx * .8)} {f(y + 3 * s)}", "l", "stroke-width:1")

def dove(sh, x, y, s=1, branch=True):
    """Duif naar rechts vliegend."""
    S = lambda v: v * s
    sh.region(f"M{f(x - S(12))} {f(y)}L{f(x - S(30))} {f(y - S(8))}L{f(x - S(28))} {f(y + S(8))}Z", "-")
    sh.region(f"M{f(x - S(16))} {f(y + S(2))}Q{f(x - S(4))} {f(y + S(12))} {f(x + S(12))} {f(y + S(4))}Q{f(x + S(20))} {f(y - S(2))} {f(x + S(14))} {f(y - S(8))}Q{f(x)} {f(y - S(6))} {f(x - S(16))} {f(y + S(2))}Z", "-")
    sh.circle_r(x + S(16), y - S(8), S(6), "-")
    sh.poly_r([(x + S(21), y - S(10)), (x + S(28), y - S(7)), (x + S(21), y - S(5))], "o")
    eye(sh, x + S(17), y - S(9), S(1.2))
    sh.region(f"M{f(x - S(6))} {f(y - S(2))}Q{f(x - S(12))} {f(y - S(30))} {f(x + S(10))} {f(y - S(36))}Q{f(x + S(6))} {f(y - S(18))} {f(x + S(8))} {f(y - S(4))}Z", "-")
    sh.line(f"M{f(x - S(3))} {f(y - S(14))}Q{f(x + S(2))} {f(y - S(20))} {f(x + S(6))} {f(y - S(26))}", "l", "stroke-width:1")
    if branch:
        sh.line(f"M{f(x + S(26))} {f(y - S(7))}Q{f(x + S(36))} {f(y - S(4))} {f(x + S(44))} {f(y + S(2))}")
        for t, rot in ((.35, -40), (.6, 50), (.85, -30)):
            bx, by = x + S(26 + 18 * t), y - S(7) + S(9 * t * t)
            leaf_at(sh, bx, by + (S(-4) if rot < 0 else S(4)), S(2.6), S(4.6), rot, "g")

def dog_sit(sh, x, y, s=1, code="w", ear="w", bow=None):
    """Zittende hond van voren, (x,y) = onderkant midden."""
    S = lambda v: v * s
    sh.region(f"M{f(x + S(14))} {f(y - S(6))}Q{f(x + S(30))} {f(y - S(10))} {f(x + S(28))} {f(y - S(26))}Q{f(x + S(24))} {f(y - S(14))} {f(x + S(14))} {f(y - S(14))}Z", code)
    sh.region(f"M{f(x - S(18))} {f(y)}Q{f(x - S(20))} {f(y - S(34))} {f(x)} {f(y - S(38))}Q{f(x + S(20))} {f(y - S(34))} {f(x + S(18))} {f(y)}Z", code)
    sh.ellipse_r(x, y - S(14), S(8), S(12), "-")
    for dx in (-8, 8): sh.ellipse_r(x + S(dx), y - S(2), S(6), S(4), code)
    sh.circle_r(x, y - S(48), S(15), code)
    for d in (-1, 1):
        sh.region(f"M{f(x + d * S(10))} {f(y - S(60))}Q{f(x + d * S(24))} {f(y - S(62))} {f(x + d * S(20))} {f(y - S(38))}Q{f(x + d * S(14))} {f(y - S(40))} {f(x + d * S(10))} {f(y - S(60))}Z", ear)
    sh.ellipse_r(x, y - S(42), S(8), S(6), "-")
    sh.ellipse_r(x, y - S(45), S(3), S(2.2), "x")
    sh.line(f"M{f(x)} {f(y - S(43))}V{f(y - S(40))}M{f(x - S(4))} {f(y - S(39))}Q{f(x)} {f(y - S(36))} {f(x + S(4))} {f(y - S(39))}", "l", "stroke-width:1.2")
    eye(sh, x - S(6), y - S(52), S(1.8)); eye(sh, x + S(6), y - S(52), S(1.8))
    if bow:
        sh.region(f"M{f(x)} {f(y - S(32))}L{f(x - S(8))} {f(y - S(36))}V{f(y - S(28))}Z", bow); sh.region(f"M{f(x)} {f(y - S(32))}L{f(x + S(8))} {f(y - S(36))}V{f(y - S(28))}Z", bow)
        sh.circle_r(x, y - S(32), S(2), bow)

def cat_sit(sh, x, y, s=1, code="o"):
    S = lambda v: v * s
    sh.line(f"M{f(x + S(12))} {f(y - S(3))}Q{f(x + S(30))} {f(y - S(4))} {f(x + S(26))} {f(y - S(22))}", "l", "stroke-width:4;stroke-linecap:round")
    sh.region(f"M{f(x - S(14))} {f(y)}Q{f(x - S(16))} {f(y - S(28))} {f(x)} {f(y - S(30))}Q{f(x + S(16))} {f(y - S(28))} {f(x + S(14))} {f(y)}Z", code)
    for dx in (-6, 6): sh.ellipse_r(x + S(dx), y - S(2), S(5), S(3.5), code)
    for d in (-1, 1): sh.poly_r([(x + d * S(4), y - S(52)), (x + d * S(12), y - S(56)), (x + d * S(12), y - S(42))], code)
    sh.circle_r(x, y - S(40), S(13), code)
    eye(sh, x - S(5), y - S(42), S(1.7)); eye(sh, x + S(5), y - S(42), S(1.7))
    sh.poly_r([(x - S(2), y - S(37)), (x + S(2), y - S(37)), (x, y - S(35))], "k")
    sh.line(f"M{f(x)} {f(y - S(35))}Q{f(x - S(3))} {f(y - S(32))} {f(x - S(5))} {f(y - S(34))}M{f(x)} {f(y - S(35))}Q{f(x + S(3))} {f(y - S(32))} {f(x + S(5))} {f(y - S(34))}", "l", "stroke-width:1")
    sh.line(f"M{f(x - S(6))} {f(y - S(36))}H{f(x - S(18))}M{f(x + S(6))} {f(y - S(36))}H{f(x + S(18))}", "l", "stroke-width:.9")

def sit_legs(sh, cx, y, s, code):
    """Kleermakerszit: gekruiste benen onder een zittend figuur (person met draw_legs=False)."""
    for d in (-1, 1):
        limb(sh, cx + d * 8 * s, y - 10 * s, cx + d * 26 * s, y, code, 12 * s)
    for d in (-1, 1):
        limb(sh, cx + d * 26 * s, y, cx - d * 6 * s, y + 6 * s, code, 11 * s)
    for d in (-1, 1):
        sh.ellipse_r(cx - d * 10 * s, y + 7 * s, 6 * s, 3.5 * s, "x")

def lantern_paper(sh, x, y, r, code, stick=True):
    """Ronde papieren lampion aan een stokje (met ledlampje)."""
    if stick: sh.line(f"M{f(x)} {f(y - r - 4)}V{f(y - r - 10)}")
    sh.ellipse_r(x, y, r, r * .85, code)
    sh.rect_r(x - r * .45, y - r * .85 - 3, r * .9, 4, "-", 1); sh.rect_r(x - r * .45, y + r * .85 - 1, r * .9, 4, "-", 1)
    for k in (-.5, 0, .5): sh.line(f"M{f(x + r * k)} {f(y - r * .8)}Q{f(x + r * k * 1.6)} {f(y)} {f(x + r * k)} {f(y + r * .8)}", "l", "stroke-width:1")


# ---------- oud en nieuw ----------
def vuurwerk_stad(sh):
    sh.rect_r(0, 0, 200, 142, "n")
    for x, y in ((14, 14), (92, 60), (186, 14), (150, 76), (24, 70)): sparkle(sh, x, y, 3.5, "y")
    sh.line("M44 140Q40 100 44 64M112 140Q116 96 112 52M170 140Q166 100 168 60", "l", "stroke-width:1.2;stroke-dasharray:2 4")
    burst(sh, 44, 40, 26, "r", 12); burst(sh, 112, 30, 21, "y", 10); burst(sh, 168, 42, 19, "m", 9)
    # skyline
    sh.rect_r(0, 98, 30, 44, "z")
    sh.rect_r(30, 92, 28, 50, "w"); sh.poly_r([(30, 92), (44, 74), (58, 92)], "w")
    sh.rect_r(58, 104, 28, 38, "b")
    sh.rect_r(86, 92, 20, 50, "z"); sh.poly_r([(84, 92), (96, 60), (108, 92)], "g"); sh.line("M96 60V52M93 55H99")
    sh.circle_r(96, 104, 6, "-"); sh.line("M96 104V99.5M96 104V100", "l", "stroke-width:1.4")
    sh.region("M106 142V96H112V90H118V84H128V90H134V96H140V142Z", "o")
    sh.rect_r(140, 102, 30, 40, "w")
    sh.rect_r(170, 94, 30, 48, "z"); sh.poly_r([(170, 94), (185, 76), (200, 94)], "z")
    lit = random.Random(35)
    for x0, x1, y0 in ((4, 26, 104), (34, 54, 98), (62, 82, 110), (110, 136, 102), (144, 166, 108), (174, 196, 100)):
        n = int((x1 - x0) // 9)
        for row in range(3):
            for c in range(n):
                xx = x0 + 2 + c * (x1 - x0) / n
                sh.rect_r(xx, y0 + row * 11, 5, 6, "y" if lit.random() < .45 else "-")
    sh.rect_r(90, 116, 12, 26, "-", 5)
    # water en kade
    sh.rect_r(0, 142, 200, 24, "b")
    for x in range(6, 200, 34): sh.line(f"M{x} {150 + (x % 3) * 4}Q{x + 7} {146 + (x % 3) * 4} {x + 14} {150 + (x % 3) * 4}", "l", "stroke-width:1.2")
    sh.rect_r(0, 166, 200, 34, "z")
    for x in range(0, 200, 25): sh.seg(x, 186, x + 12, 186, "l", "stroke-width:1")
    # kijkers van achteren
    person(sh, 64, 128, "r", "n", hands=((50, 162), (82, 120)), style="back", hair="w", s=.55, legs=((60, 178), (68, 178)))
    person(sh, 102, 120, "g", "x", hands=((84, 160), (120, 160)), style="back", hair="x", s=.68, legs=((97, 180), (107, 180)))
    person(sh, 140, 130, "y", "p", hands=((126, 160), (154, 160)), style="back", hair="o", s=.5, legs=((136, 177), (144, 177)))
    sh.seg(0, 172, 200, 172)
    for x in range(10, 200, 30): sh.rect_r(x - 2, 172, 4, 22, "x")

def aftellen(sh):
    bunting(sh, 0, 6, 200, 6, 10, ["r", "y", "b", "g", "m"], 6, 10)
    sh.circle_r(100, 66, 46, "o"); sh.circle_r(100, 66, 38, "-")
    for k in range(12):
        a = math.radians(k * 30)
        sh.seg(100 + 33 * math.sin(a), 66 - 33 * math.cos(a), 100 + 37 * math.sin(a), 66 - 37 * math.cos(a), "l", "stroke-width:1.6")
    sh.text(100, 43, "12", 9); sh.text(126, 69, "3", 9); sh.text(100, 95, "6", 9); sh.text(74, 69, "9", 9)
    limb(sh, 100, 66, 100, 48, "x", 3.4); limb(sh, 100, 66, 100, 55, "x", 5)
    sh.circle_r(100, 66, 3.5, "r")
    sh.rect_r(92, 16, 16, 6, "o", 2)
    sh.text(18, 36, "3", 12, "start"); sh.text(30, 50, "2", 12, "start"); sh.text(160, 36, "1", 12, "start")
    sh.text(150, 54, "Proost!", 7, "start")
    # kinderen met feesthoedjes
    hy = person(sh, 50, 116, "p", "n", hands=((28, 170), (60, 140)), style="curly", hair="x", s=.72, face=False)
    party_hat(sh, 50, hy, .72, "y", "r"); eye(sh, 46.4, hy + 2, 1.3); eye(sh, 53.6, hy + 2, 1.3)
    sh.region(f"M50 {f(hy + 6)}L72 {f(hy - 2)}V{f(hy + 16)}Z", "g"); sh.line(f"M58 {f(hy + 3)}L60 {f(hy + 11)}M65 {f(hy + 1)}L67 {f(hy + 13)}", "l", "stroke-width:1")
    sh.line(f"M76 {f(hy - 2)}L82 {f(hy - 8)}M77 {f(hy + 7)}L85 {f(hy + 7)}M76 {f(hy + 15)}L82 {f(hy + 21)}", "l", "stroke-width:1.2")
    hy = person(sh, 150, 116, "t", "r", hands=((126, 100), (174, 100)), style="long", hair="w", s=.72, face=False)
    party_hat(sh, 150, hy, .72, "m", "y"); face(sh, 150, hy, .72, "open")
    for x, y, c, r in ((70, 128, "r", 20), (124, 128, "b", -30), (16, 128, "y", 40), (186, 130, "g", -10), (96, 130, "m", 60), (80, 178, "y", 15), (120, 182, "b", -40)):
        sh.raw(f'<g transform="rotate({r} {x} {y})">'); sh.rect_r(x - 3, y - 2, 6, 4, c); sh.raw("</g>")
    sh.line("M86 120Q92 112 98 120T110 120M100 150Q106 142 112 150T124 150", "l", "stroke-width:1.2")
    sh.rect_r(0, 196, 200, 4, "w")


# ---------- Chinees Nieuwjaar ----------
def dumplings(sh):
    sh.line("M0 8H200", "l", "stroke-width:1.4")
    for x in (22, 178):
        sh.line(f"M{x} 8V16"); sh.ellipse_r(x, 30, 13, 13, "r"); sh.rect_r(x - 7, 15, 14, 4, "y", 1); sh.rect_r(x - 7, 41, 14, 4, "y", 1)
        sh.line(f"M{x} 22Q{x - 8} 30 {x} 38M{x} 22Q{x + 8} 30 {x} 38", "l", "stroke-width:1"); sh.line(f"M{x - 3} 45V54M{x} 45V56M{x + 3} 45V54", "l", "stroke-width:1.2")
    # raam met pruimenbloesem
    sh.rect_r(70, 10, 60, 40, "b", 2); sh.seg(100, 10, 100, 50, "l", "stroke-width:1.4")
    sh.line("M72 44Q90 34 96 22M86 36Q92 38 100 34Q110 30 126 32")
    for x, y in ((96, 22), (84, 30), (108, 30), (122, 30)): flower(sh, x, y, 3, "k", "y")
    # grootmoeder en twee kinderen achter de tafel
    person(sh, 48, 52, "r", "-", hands=((30, 116), (66, 112)), style="bun", hair="z", s=.82, draw_legs=False, arms_front=True, draw_hands=False)
    person(sh, 100, 64, "y", "-", hands=((90, 118), (112, 118)), style="short", hair="x", s=.7, draw_legs=False, arms_front=True, draw_hands=False)
    person(sh, 152, 60, "g", "-", hands=((136, 116), (168, 116)), style="braids", hair="x", s=.74, draw_legs=False, arms_front=True, draw_hands=False)
    sh.rect_r(0, 118, 200, 10, "w"); sh.rect_r(0, 128, 200, 72, "w")
    sh.line("M0 128H200")
    # op tafel
    sh.ellipse_r(100, 150, 34, 12, "-"); sh.ellipse_r(100, 150, 26, 8, "-")
    def dumpling(x, y, s=1):
        sh.region(f"M{f(x - 9 * s)} {f(y + 3 * s)}Q{f(x)} {f(y - 12 * s)} {f(x + 9 * s)} {f(y + 3 * s)}Q{f(x)} {f(y + 6 * s)} {f(x - 9 * s)} {f(y + 3 * s)}Z", "-")
        sh.line(f"M{f(x - 4 * s)} {f(y - 3 * s)}L{f(x - 3 * s)} {f(y + 1 * s)}M{f(x)} {f(y - 5 * s)}V{f(y)}M{f(x + 4 * s)} {f(y - 3 * s)}L{f(x + 3 * s)} {f(y + 1 * s)}", "l", "stroke-width:1")
    for x, y in ((86, 150), (100, 147), (114, 150), (93, 155), (107, 155)): dumpling(x, y, .9)
    # bamboe stoommandje
    sh.rect_r(150, 136, 40, 20, "y", 3); sh.ellipse_r(170, 136, 20, 5, "y"); sh.line("M150 144H190M150 150H190", "l", "stroke-width:1")
    sh.circle_r(170, 131, 3, "w")
    # deegrollertje en deegrondjes
    limb(sh, 14, 176, 60, 168, "w", 6); sh.rect_r(8, 174, 6, 6, "w", 2)
    for x, y in ((30, 150), (52, 146), (40, 160)): sh.ellipse_r(x, y, 9, 4.5, "-")
    # mandarijnen in schaal
    sh.region("M128 182H188Q186 196 158 196Q130 196 128 182Z", "b")
    for x, y in ((140, 178), (152, 176), (164, 177), (176, 178), (158, 168)): sh.circle_r(x, y, 6, "o")
    sh.line("M158 162L161 159", "l", "stroke-width:1.2")
    # handen
    for x, y in ((66, 112), (30, 116), (90, 118), (112, 118), (136, 116), (168, 116)): sh.circle_r(x, y, 3.8, "-")
    dumpling(76, 182, 1.2); dumpling(98, 186, 1.2)

def drakendans(sh):
    sh.line("M90 4Q145 14 200 4", "l", "stroke-width:1.4")
    for x in (110, 145, 180):
        y = 4 + 10 * (1 - ((x - 145) / 55) ** 2) * .5
        sh.line(f"M{x} {f(y)}V{f(y + 3)}"); sh.ellipse_r(x, y + 9, 5.5, 5.5, "r"); sh.rect_r(x - 3, y + 2.5, 6, 2, "y"); sh.rect_r(x - 3, y + 14, 6, 2, "y")
    sh.rect_r(0, 186, 200, 14, "z")
    # kinderen met stokken
    kids = [(52, "r", "x", "short"), (114, "y", "n", "pony"), (168, "r", "x", "curly")]
    hands_up = {}
    for cx, shirt, hair, style in kids:
        s = .66; top = 186 - 4 - 101 * s
        hy = top + 15 * s
        hands_up[cx] = (cx + 11, hy - 6)
        person(sh, cx, top, shirt, "n", hands=((cx + 11, hy - 6), (cx + 11, hy + 18)), style=style, hair=hair, s=s)
    # lijf van de draak
    def cy(x): return 66 + 12 * math.sin((x - 70) / 120 * 2 * math.pi)
    xs = [70 + i * 3 for i in range(42)]
    for cx, *_ in kids:
        px = cx + 11
        top_y = cy(px) + 12 if px > 72 else 84
        sh.seg(px, top_y, px, hands_up[cx][1] + 30, "l", "stroke-width:3")
    for i, x in enumerate(xs[2:-2:4]):
        y = cy(x) - 11
        sh.poly_r([(x - 3, y + 2), (x, y - 8), (x + 4, y + 2)], "y")
    top = [(x, cy(x) - 12) for x in xs]; bot = [(x, cy(x) + 12) for x in reversed(xs)]
    sh.poly_r(top + [(196, cy(196) - 4), (196, cy(196) + 4)] + bot, "r")
    sh.region(f"M194 {f(cy(194) - 8)}Q200 {f(cy(194) - 20)} 199 {f(cy(194) - 2)}Q200 {f(cy(194) + 16)} 194 {f(cy(194) + 8)}Z", "o")
    for x in range(78, 192, 10):
        y = cy(x)
        sh.line(f"M{f(x - 4)} {f(y - 3)}Q{f(x)} {f(y + 4)} {f(x + 4)} {f(y - 3)}", "l", "stroke-width:1")
    sh.line("M" + " L".join(f"{x} {f(cy(x) + 7)}" for x in xs[::2]), "l", "stroke-width:1")
    # kop
    for k in range(6):
        a = math.radians(-150 + k * 34)
        sh.region(f"M{f(56 + 14 * math.cos(a))} {f(62 + 14 * math.sin(a))}L{f(56 + 32 * math.cos(a + .18))} {f(62 + 32 * math.sin(a + .18))}L{f(56 + 18 * math.cos(a + .4))} {f(62 + 18 * math.sin(a + .4))}Z", "o")
    sh.region("M44 40Q36 22 50 14Q44 26 52 38Z", "y"); sh.region("M60 38Q62 20 78 16Q66 28 68 40Z", "y")
    sh.region("M28 58C30 40 48 34 64 40C80 46 82 70 70 80C58 90 34 88 26 80Z", "r")
    sh.region("M10 66C10 56 22 54 32 58L36 80C26 84 12 80 10 66Z", "r")
    sh.line("M13 74Q24 82 35 73", "l", "stroke-width:2")
    sh.dot(15, 63, 1.4); sh.dot(22, 61, 1.4)
    sh.circle_r(46, 54, 8, "-"); sh.circle_r(48, 55, 3.4, "x"); sh.dot(46.5, 53.5, .8)
    sh.line("M38 44Q46 40 54 44", "l", "stroke-width:2")
    sh.line("M14 70Q2 74 4 88M18 72Q12 90 2 96", "l", "stroke-width:1.4")
    sh.region("M44 84Q48 98 40 104Q52 100 56 86Z", "y")


# ---------- Valentijn ----------
def brievenbus(sh):
    grass(sh, 184)
    for x, y, s, c in ((22, 30, 10, "r"), (176, 26, 8, "m"), (34, 76, 6, "m"), (100, 14, 6, "r"), (182, 110, 7, "r"), (18, 128, 6, "k")):
        sh.region(heart_path(x, y, s), c)
    sh.rect_r(92, 124, 16, 66, "w")
    sh.region("M54 128V82A46 40 0 0 1 146 82V128Z", "r")
    sh.rect_r(50, 124, 100, 8, "r", 2)
    sh.line("M64 120V84A36 30 0 0 1 136 84V120Z", "l", "stroke-width:1.4")
    sh.rect_r(78, 72, 44, 6, "x", 2)
    # brief in de gleuf
    sh.raw('<g transform="rotate(-8 100 60)">')
    sh.rect_r(80, 46, 40, 28, "-", 1); sh.line("M80 47L100 62L120 47", "l", "stroke-width:1.4")
    sh.region(heart_path(100, 62, 5), "m")
    sh.raw("</g>")
    sh.circle_r(100, 104, 5, "y")
    # vlaggetje met hart
    sh.rect_r(146, 66, 4, 40, "y"); sh.rect_r(150, 66, 22, 16, "y", 2); sh.region(heart_path(161, 74, 5), "r")
    flower(sh, 30, 176, 6, "m"); flower(sh, 52, 184, 5, "y", "o"); flower(sh, 158, 180, 6, "r"); flower(sh, 178, 172, 5, "k")
    for x in (30, 158, 178): sh.line(f"M{x} {184 if x != 178 else 178}V194")


# ---------- carnaval ----------
def verkleedkinderen(sh):
    bunting(sh, 0, 4, 200, 4, 9, ["r", "y", "g"], 5, 10)
    for x, y, c, r in ((20, 40, "r", 20), (180, 36, "b", -30), (100, 22, "y", 40), (60, 30, "m", 10), (140, 26, "g", -20), (10, 90, "p", 30), (190, 92, "o", 0)):
        sh.raw(f'<g transform="rotate({r} {x} {y})">'); sh.rect_r(x - 3, y - 2, 6, 4, c); sh.raw("</g>")
    sh.line("M40 60Q46 52 50 60T60 60M150 54Q156 46 160 54T170 54", "l", "stroke-width:1.2")
    s = .88; top = 194 - 4 - 101 * s
    # clown
    hy = person(sh, 38, top + 8, "y", "b", hands=((18, top + 60), (56, top + 76)), style="curly", hair="o", s=s, cap=True, face=False)
    for dx, dy in ((-6, 30), (6, 40), (-4, 48)): sh.circle_r(38 + dx, hy + dy, 2.4, "r")
    sh.region(" ".join([f"M{f(38 - 18)} {f(hy + 14)}"] + [f"L{f(38 - 18 + i * 4.5)} {f(hy + (19 if i % 2 else 13))}" for i in range(1, 9)]) + f"L{f(38 + 18)} {f(hy + 22)}L{f(38 - 18)} {f(hy + 22)}Z", "-")
    party_hat(sh, 38, hy, s, "g", "r")
    face(sh, 38, hy, s); sh.circle_r(38, hy + 5, 2.6, "r")
    # lieveheersbeestje
    hy = person(sh, 100, top, "r", "x", hands=((72, top + 34), (128, top + 34)), style="short", hair="w", s=s)
    sh.line(f"M100 {f(hy + 13)}V{f(hy + 45)}", "l", "stroke-width:1.4")
    for dx, dy in ((-7, 24), (7, 24), (-8, 36), (8, 36)): sh.circle_r(100 + dx, hy + dy, 2.6, "x")
    sh.line(f"M94 {f(hy - 11)}Q90 {f(hy - 24)} 84 {f(hy - 26)}M106 {f(hy - 11)}Q110 {f(hy - 24)} 116 {f(hy - 26)}")
    sh.circle_r(84, hy - 26, 3, "x"); sh.circle_r(116, hy - 26, 3, "x")
    # draakje
    cx = 162
    sh.region(f"M{cx + 10} {f(top + 66)}Q{cx + 40} {f(top + 70)} {cx + 34} {f(top + 96)}Q{cx + 30} {f(top + 80)} {cx + 12} {f(top + 78)}Z", "g")
    hy = person(sh, cx, top + 4, "g", "g", hands=((cx - 22, top + 50), (cx + 24, top + 22)), hair=None, s=s, face=False)
    for k in range(5):
        a = math.radians(-150 + k * 30)
        sh.poly_r([(cx + 13 * math.cos(a - .2), hy + 13 * math.sin(a - .2)), (cx + 20 * math.cos(a), hy + 20 * math.sin(a)), (cx + 13 * math.cos(a + .2), hy + 13 * math.sin(a + .2))], "y")
    sh.circle_r(cx, hy, 14, "g"); sh.ellipse_r(cx, hy + 2, 9, 9.5, "-"); face(sh, cx, hy, .7)
    sh.ellipse_r(cx, hy + 38, 8, 12, "l")

def optochtwagen(sh):
    bunting(sh, 0, 6, 200, 10, 9, ["r", "y", "g"], 6, 9)
    for x, y, c, r in ((30, 34, "r", 20), (176, 40, "b", -30), (70, 38, "y", 40), (12, 64, "m", 10), (190, 70, "g", -20)):
        sh.raw(f'<g transform="rotate({r} {x} {y})">'); sh.rect_r(x - 3, y - 2, 6, 4, c); sh.raw("</g>")
    sh.rect_r(0, 186, 200, 14, "z")
    sh.line("M0 192H200", "l", "stroke-width:1")
    # trekker
    sh.rect_r(6, 140, 34, 22, "g", 3); sh.rect_r(28, 112, 30, 50, "g", 3); sh.rect_r(34, 118, 18, 18, "b", 2)
    sh.rect_r(12, 130, 4, 10, "z"); sh.circle_r(14, 127, 2, "-")
    sh.circle_r(44, 168, 16, "x"); sh.circle_r(44, 168, 6, "y"); sh.circle_r(16, 174, 10, "x"); sh.circle_r(16, 174, 4, "y")
    hy = 124; sh.circle_r(43, hy, 6, "-"); sh.region("M37 122A6 6 0 0 1 49 122Z", "w"); sh.dot(41, 125, 1); sh.dot(45, 125, 1)
    sh.line("M58 156H70")
    # wagen
    sh.rect_r(68, 150, 130, 10, "o")
    sh.region("M68 160H198V168" + "".join(f"Q{193 - k * 13 + 6.5} 176 {193 - k * 13} 168" for k in range(10)) + "Z", "y")
    sh.circle_r(92, 176, 9, "x"); sh.circle_r(176, 176, 9, "x")
    # reuzenkikker
    sh.ellipse_r(132, 128, 44, 24, "l")
    sh.ellipse_r(132, 132, 26, 16, "y")
    for x in (96, 168): sh.region(f"M{x - 12} 150Q{x} 136 {x + 12} 150Z", "l")
    sh.ellipse_r(132, 92, 46, 28, "l")
    for x in (108, 156):
        sh.circle_r(x, 66, 14, "l"); sh.circle_r(x, 66, 9, "-"); sh.circle_r(x + 2, 67, 4, "x")
    sh.line("M100 98Q132 120 164 98")
    sh.ellipse_r(98, 92, 6, 4, "k"); sh.ellipse_r(166, 92, 6, 4, "k")
    sh.dot(126, 84, 1.4); sh.dot(138, 84, 1.4)
    sh.region("M118 58L120 40L128 50L132 36L136 50L144 40L146 58Z", "y")
    for x in (120, 132, 144): sh.circle_r(x, 38 if x != 132 else 34, 2.5, "r")
    # kinderen op de wagen
    s = .44
    person(sh, 80, 150 - 101 * s - 2, "m", "n", hands=((70, 122), (88, 110)), style="pony", hair="w", s=s, legs=((76, 145), (84, 145)))
    person(sh, 186, 150 - 101 * s - 2, "b", "n", hands=((176, 112), (196, 124)), style="curly", hair="x", s=s, legs=((182, 145), (190, 145)))

# ---------- Holi ----------
def holi(sh):
    sh.region(blob(62, 44, 34, 24, 9), "m"); sh.region(blob(140, 40, 30, 22, 9, .62, .3), "y"); sh.region(blob(102, 80, 20, 16, 8), "t")
    sh.region(blob(170, 92, 16, 12, 7), "g"); sh.region(blob(24, 96, 16, 12, 7), "o")
    rnd = random.Random(7)
    for _ in range(26):
        x, y = rnd.uniform(8, 192), rnd.uniform(8, 116)
        sh.circle_r(x, y, rnd.uniform(1.2, 2.4), rnd.choice("mytgop"))
    grass(sh, 184)
    s = .8; top = 190 - 4 - 101 * s
    hy = person(sh, 52, top, "-", "-", hands=((28, top + 60), (78, top + 2)), style="long", hair="x", s=s)
    for dx, dy, c in ((-7, 26, "m"), (6, 34, "y"), (-3, 44, "t"), (8, 20, "g")): sh.circle_r(52 + dx, hy + dy, 2.6, c)
    sh.circle_r(64, hy - 6, 2, "m"); sh.circle_r(44, hy + 6, 1.8, "y")
    hy = person(sh, 148, top, "-", "-", hands=((122, top + 4), (172, top + 58)), style="short", hair="w", s=s)
    for dx, dy, c in ((7, 26, "t"), (-6, 34, "m"), (3, 44, "o"), (-8, 20, "y")): sh.circle_r(148 + dx, hy + dy, 2.6, c)
    sh.circle_r(156, hy + 6, 1.8, "g")
    # kommen met kleurpoeder
    for x, c in ((80, "m"), (100, "y"), (120, "t")):
        sh.region(f"M{x - 9} 182Q{x - 6} 174 {x} 172Q{x + 6} 174 {x + 9} 182Z", c)
        sh.region(f"M{x - 11} 182H{x + 11}Q{x + 9} 194 {x} 194Q{x - 9} 194 {x - 11} 182Z", "w")


# ---------- Suikerfeest en Offerfeest ----------
def suikerfeest_maaltijd(sh):
    sh.line("M0 6Q100 22 200 6", "l", "stroke-width:1.2")
    for k in range(1, 12):
        x = k * 200 / 12; y = 6 + 16 * (1 - ((x - 100) / 100) ** 2) * .5 * 2 * .5
        sh.ellipse_r(x, y + 5, 3, 4, "y" if k % 2 else "o")
    sh.region("M74 76V40Q74 18 100 18Q126 18 126 40V76Z", "n")
    sh.region(moon_path(96, 40, 11), "y"); sh.region(star_path(114, 34, 5, 2.2), "y")
    sh.seg(74, 56, 126, 56, "l", "stroke-width:1.4")
    sh.line("M30 14V24"); sh.region("M24 30L30 24L36 30V44L30 50L24 44Z", "o"); sh.rect_r(26.5, 32, 7, 10, "y", 1); sh.circle_r(30, 54, 2, "o")
    sh.line("M170 14V24"); sh.region("M164 30L170 24L176 30V44L170 50L164 44Z", "t"); sh.rect_r(166.5, 32, 7, 10, "y", 1); sh.circle_r(170, 54, 2, "t")
    # familie
    s = .74
    person(sh, 34, 66, "p", "-", hands=((20, 126), (48, 124)), hair=None, s=s, face=False, draw_legs=False, arms_front=True)
    headscarf(sh, 34, 66 + 15 * s, s, "m")
    person(sh, 76, 60, "g", "-", hands=((62, 124), (88, 124)), style="short", hair="x", s=.78, draw_legs=False, arms_front=True)
    person(sh, 126, 74, "y", "-", hands=((112, 124), (140, 122)), style="braids", hair="x", s=.66, draw_legs=False, arms_front=True)
    person(sh, 168, 70, "r", "-", hands=((152, 124), (184, 120)), style="curly", hair="w", s=.66, draw_legs=False, arms_front=True)
    # tafel met kleed
    sh.rect_r(0, 124, 200, 10, "-")
    sh.region("M0 134H200V166" + "".join(f"Q{195 - k * 10} 174 {190 - k * 10} 166" for k in range(20)) + "Z", "t")
    for x in range(10, 200, 30): flower(sh, x, 152, 3, "y", "o")
    for x in (20, 180): sh.rect_r(x - 3, 166, 6, 30, "w")
    sh.rect_r(0, 196, 200, 4, "w")
    # gerechten
    sh.ellipse_r(100, 124, 28, 7, "-"); sh.region("M78 122Q100 96 122 122Z", "y")
    for x, y in ((92, 112), (102, 108), (110, 114), (98, 117)): sh.ellipse_r(x, y, 3, 1.6, "o")
    sh.ellipse_r(42, 126, 14, 4, "b")
    for x in (34, 40, 46, 52): sh.ellipse_r(x, 122, 2.8, 4.2, "w")
    sh.region("M140 126H160V112Q160 104 150 104Q140 104 140 112Z", "y"); sh.line("M160 112Q168 108 166 104", "l", "stroke-width:2"); sh.line("M140 112Q134 114 136 120", "l", "stroke-width:2"); sh.circle_r(150, 102, 2.4, "y")
    for x in (170, 182): sh.region(f"M{x - 4} 126L{x - 5} 114H{x + 5}L{x + 4} 126Z", "-"); sh.rect_r(x - 4.5, 119, 9, 4, "o")
    for (x, y), c in zip(((64, 128), (124, 128), (12, 128)), "kmk"):
        sh.ellipse_r(x, y, 8, 3, c)
        sh.circle_r(x - 3, y - 3, 2.6, "w"); sh.circle_r(x + 3, y - 3, 2.6, "w")

def offerfeest_bezoek(sh):
    sh.region(moon_path(30, 26, 12), "y"); sh.region(star_path(50, 18, 5, 2.2), "y")
    for x, y in ((80, 14), (100, 32), (16, 56)): sparkle(sh, x, y, 3.5, "y")
    sh.rect_r(0, 188, 200, 12, "z")
    for x in range(0, 200, 20): sh.seg(x, 188, x, 200, "l", "stroke-width:1")
    # huis
    sh.rect_r(118, 54, 82, 134, "o")
    sh.poly_r([(112, 56), (160, 20), (206, 56)], "r")
    sh.line("M120 60Q140 70 160 60T200 60", "l", "stroke-width:1.2")
    for k in range(7): sh.circle_r(124 + k * 12, 64 + (3 if k % 2 else 0), 2.6, "y")
    sh.rect_r(176, 76, 20, 24, "b", 1); sh.seg(186, 76, 186, 100, "l", "stroke-width:1.2")
    sh.rect_r(134, 90, 38, 98, "-")
    sh.region("M134 90L122 96V184L134 188Z", "g")
    # opa in de deur
    s = .76
    person(sh, 154, 186 - 4 - 101 * s, "b", "x", hands=((138, 140), (174, 112)), style="short", hair="z", s=s)
    # moeder met schaal
    s = .84; top = 188 - 4 - 101 * s
    person(sh, 40, top, "t", "n", hands=((26, top + 56), (58, top + 56)), hair=None, s=s, face=False, skirt="t", arms_front=True)
    headscarf(sh, 40, top + 15 * s, s, "p")
    sh.ellipse_r(42, top + 56, 22, 5, "y"); sh.region(f"M24 {f(top + 55)}Q42 {f(top + 36)} 60 {f(top + 55)}Z", "-"); sh.circle_r(42, top + 41, 2.5, "-")
    # kinderen met cadeautje
    s = .58; top = 188 - 4 - 101 * s
    person(sh, 84, top, "m", "n", hands=((74, top + 52), (94, top + 52)), style="long", hair="w", s=s)
    present(sh, 74, top + 46, 20, 16, "y", "r")
    s = .54; top = 188 - 4 - 101 * s
    person(sh, 110, top, "r", "x", hands=((98, top + 40), (124, top + 4)), style="curly", hair="x", s=s)


# ---------- Pasen ----------
def eieren_zoeken(sh):
    sun(sh, 172, 22, 11); sh.region(cloud_path(56, 22, 11), "-")
    sh.region("M0 200V128H200V200Z", "l")
    for x in range(4, 200, 14): sh.region(f"M{x} 130V108L{x + 5} 102L{x + 10} 108V130Z", "-")
    sh.rect_r(0, 112, 200, 5, "-"); sh.rect_r(0, 122, 200, 5, "-")
    sh.region(blob(36, 146, 32, 22, 9), "g")
    sh.region("M154 182C158 160 158 120 156 92H170C168 120 168 160 174 182Z", "w")
    sh.region(blob(164, 70, 32, 30, 9), "g")
    for x, y in ((150, 56), (176, 64), (162, 84), (184, 82), (146, 78)): flower(sh, x, y, 3.2, "k", "y")
    egg(sh, 54, 166, 1, "b", 1); egg(sh, 184, 178, .9, "m", 2); egg(sh, 130, 186, .9, "y", 3)
    egg(sh, 20, 104, .7, "o", 2)
    # bloempot met ei
    sh.region("M100 178H124L120 196H104Z", "o"); sh.rect_r(98, 174, 28, 5, "o", 1); egg(sh, 112, 170, .75, "p", 1)
    for x, c in ((104, "r"), (120, "y")): sh.line(f"M{x} 174V160"); flower(sh, x, 156, 3.5, c)
    # kind met mandje
    s = .78; top = 194 - 4 - 101 * s
    hy = person(sh, 86, top, "y", "n", hands=((62, top + 74), (108, top + 44)), style="pony", hair="w", s=s)
    sh.region(f"M48 {f(top + 74)}H76L72 {f(top + 92)}H52Z", "w"); sh.line(f"M48 {f(top + 74)}Q62 {f(top + 52)} 76 {f(top + 74)}")
    sh.line(f"M50 {f(top + 82)}H74M51 {f(top + 87)}H73", "l", "stroke-width:1")
    egg(sh, 56, top + 70, .55, "r", 0); egg(sh, 66, top + 69, .55, "g", 0)
    sh.circle_r(62, top + 74, 3.6, "-")


# ---------- Koningsdag ----------
def zaklopen(sh):
    bunting(sh, 0, 6, 200, 6, 12, ["r", "-", "n", "o"], 6, 10)
    grass(sh, 176)
    sh.region(cloud_path(100, 40, 10), "-")
    # finishlint
    sh.rect_r(184, 110, 5, 70, "w")
    sh.poly_r([(189, 110), (200, 114), (189, 118)], "o")
    def sack_kid(cx, top, shirt, hair, style, s, lift):
        hy = top + 15 * s
        sh.ellipse_r(cx, 190, 22 * s, 3.5, "z") if lift else None
        person(sh, cx, top, shirt, "-", hands=((cx - 18 * s, hy + 44 * s), (cx + 18 * s, hy + 44 * s)), style=style, hair=hair, s=s, draw_legs=False, draw_hands=False)
        sh.region(f"M{f(cx - 20 * s)} {f(hy + 42 * s)}Q{f(cx - 26 * s)} {f(hy + 80 * s)} {f(cx - 20 * s)} {f(hy + 96 * s)}H{f(cx + 20 * s)}Q{f(cx + 26 * s)} {f(hy + 80 * s)} {f(cx + 20 * s)} {f(hy + 42 * s)}Q{f(cx)} {f(hy + 48 * s)} {f(cx - 20 * s)} {f(hy + 42 * s)}Z", "w")
        sh.line(f"M{f(cx - 8 * s)} {f(hy + 60 * s)}L{f(cx - 4 * s)} {f(hy + 70 * s)}M{f(cx + 10 * s)} {f(hy + 76 * s)}L{f(cx + 6 * s)} {f(hy + 86 * s)}", "l", "stroke-width:1")
        for d in (-1, 1): sh.circle_r(cx + d * 18 * s, hy + 44 * s, 4.5 * s, "-")
        return hy
    hy = sack_kid(64, 40, "o", "w", "short", .9, True)
    sh.line("M28 140H40M24 150H38M30 160H42", "l", "stroke-width:1.4")
    hy = sack_kid(136, 62, "o", "x", "braids", .82, False)
    sh.region(f"M124 {f(hy - 12)}L126 {f(hy - 24)}L131 {f(hy - 16)}L136 {f(hy - 26)}L141 {f(hy - 16)}L146 {f(hy - 24)}L148 {f(hy - 12)}Z", "o")
    sh.line("M104 176Q112 170 120 176M150 176Q158 170 166 176", "l", "stroke-width:1.4")

def koekhappen(sh):
    sh.rect_r(10, 20, 6, 170, "w"); sh.rect_r(184, 20, 6, 170, "w")
    sh.line("M13 26Q100 40 187 26")
    for x, l, c in ((48, 34, "w"), (100, 30, "w"), (152, 38, "w")):
        y0 = 26 + 14 * (1 - ((x - 100) / 87) ** 2)
        sh.line(f"M{x} {f(y0)}V{f(y0 + l)}", "l", "stroke-width:1.2")
        sh.rect_r(x - 10, y0 + l, 20, 14, c, 2); sh.dot(x - 5, y0 + l + 5, 1); sh.dot(x + 4, y0 + l + 9, 1); sh.dot(x, y0 + l + 4, 1)
    bunting(sh, 16, 16, 184, 16, 8, ["r", "-", "n"], -2, 8)
    grass(sh, 186)
    s = 1.0; top = 82
    hy = person(sh, 100, top, "o", "n", hands=((88, top + 70), (112, top + 70)), style="curly", hair="x", s=s, face=False, draw_hands=False)
    sh.region(f"M86 {f(hy - 8)}L88 {f(hy - 24)}L94 {f(hy - 14)}L100 {f(hy - 26)}L106 {f(hy - 14)}L112 {f(hy - 24)}L114 {f(hy - 8)}Z", "o")
    eye(sh, 95, hy + 1, 1.8); eye(sh, 105, hy + 1, 1.8)
    sh.line(f"M91 {f(hy - 4)}Q95 {f(hy - 7)} 98 {f(hy - 4)}M102 {f(hy - 4)}Q105 {f(hy - 7)} 109 {f(hy - 4)}", "l", "stroke-width:1.2")
    sh.ellipse_r(100, hy + 9, 4, 3.6, "r")
    flower(sh, 34, 186, 5, "o"); flower(sh, 170, 188, 5, "y", "o")
    sh.line("M76 104Q70 100 72 94M124 104Q130 100 128 94", "l", "stroke-width:1.2")


# ---------- Bevrijdingsdag ----------
def vlag_uithangen(sh):
    sh.region(cloud_path(64, 22, 9), "-")
    dove(sh, 132, 46, .8)
    grass(sh, 186)
    sh.rect_r(20, 70, 100, 118, "o")
    for y in range(80, 188, 10): sh.seg(20, y, 120, y, "l", "stroke-width:.7")
    sh.poly_r([(12, 72), (70, 34), (128, 72)], "r")
    sh.rect_r(58, 46, 24, 18, "-", 1); sh.seg(70, 46, 70, 64, "l", "stroke-width:1.2")
    # raam met kind
    sh.rect_r(32, 82, 76, 40, "-", 1)
    hy = person(sh, 70, 84, "b", "-", hands=((48, 98), (92, 104)), style="pony", hair="y", s=.6, draw_legs=False, arms_front=True)
    sh.rect_r(30, 116, 80, 6, "w")
    sh.rect_r(30, 122, 80, 8, "w")
    # vlag
    sh.line("M100 112L170 54", "l", "stroke-width:3")
    sh.raw('<g transform="rotate(-39.6 170 54)">')
    sh.rect_r(124, 54, 46, 10, "r"); sh.rect_r(124, 64, 46, 10, "-"); sh.rect_r(124, 74, 46, 10, "n")
    sh.raw("</g>")
    sh.circle_r(171, 53, 2.5, "y")
    sh.circle_r(100, 112, 3, "z")
    # deur en ramen beneden
    sh.rect_r(34, 142, 24, 46, "g", 1); sh.dot(52, 166, 1.3)
    sh.rect_r(70, 142, 38, 26, "-", 1); sh.seg(89, 142, 89, 168, "l", "stroke-width:1.2")
    sh.rect_r(68, 168, 42, 8, "w")
    for x, c in ((76, "r"), (84, "-"), (92, "r"), (100, "o")): sh.line(f"M{x} 168V162"); sh.region(f"M{x - 3} 162V157L{x - 1.5} 159L{x} 156L{x + 1.5} 159L{x + 3} 157V162Z", c)
    sh.rect_r(173, 150, 6, 38, "w"); sh.region(blob(176, 136, 18, 18, 8), "g")
    for x, y in ((140, 182), (156, 186)): flower(sh, x, y, 4, "m")


# ---------- Moederdag en Vaderdag ----------
def ontbijt_op_bed(sh):
    sh.rect_r(146, 12, 44, 40, "b", 2); sh.seg(168, 12, 168, 52, "l", "stroke-width:1.4"); sh.seg(146, 32, 190, 32, "l", "stroke-width:1.4")
    sun(sh, 160, 24, 5, False)
    sh.rect_r(14, 14, 34, 26, "-", 1); sh.region(heart_path(31, 28, 7), "r")
    sh.region("M10 128V60Q10 40 30 40H110Q130 40 130 60V128Z", "w")
    sh.rect_r(30, 74, 80, 30, "-", 12)
    s = .84
    person(sh, 70, 52, "m", "-", hands=((54, 106), (86, 106)), style="long", hair="o", s=s, draw_legs=False, arms_front=True)
    sh.rect_r(56, 94, 28, 22, "y", 1); sh.region(heart_path(70, 104, 6), "r")
    sh.circle_r(54, 106, 3.8, "-"); sh.circle_r(86, 106, 3.8, "-")
    sh.region("M2 120H140V176H2Z", "b")
    for x in range(14, 140, 24):
        for y in (132, 156): sh.region(heart_path(x + (12 if y == 156 else 0), y, 4), "k")
    sh.rect_r(0, 176, 142, 10, "w"); sh.rect_r(4, 186, 8, 12, "w"); sh.rect_r(130, 186, 8, 12, "w")
        # kind met dienblad
    s = .74; top = 196 - 4 - 101 * s
    hy = person(sh, 158, top, "y", "g", hands=((134, top + 52), (180, top + 52)), style="curly", hair="x", s=s)
    ty = top + 48
    sh.rect_r(124, ty, 64, 5, "w", 2)
    sh.ellipse_r(138, ty - 3, 10, 3, "-"); sh.region(f"M132 {f(ty - 4)}V{f(ty - 12)}Q138 {f(ty - 16)} 144 {f(ty - 12)}V{f(ty - 4)}Z", "o")
    sh.region(f"M152 {f(ty)}L150 {f(ty - 6)}H158L156 {f(ty)}Z", "b"); sh.ellipse_r(154, ty - 10, 4, 5, "-")
    sh.region(f"M164 {f(ty)}L163 {f(ty - 14)}H171L170 {f(ty)}Z", "-"); sh.rect_r(163.5, ty - 10, 7, 8, "o")
    sh.region(f"M178 {f(ty)}Q174 {f(ty - 6)} 178 {f(ty - 10)}H182Q186 {f(ty - 6)} 182 {f(ty)}Z", "t")
    sh.line(f"M180 {f(ty - 10)}V{f(ty - 20)}"); flower(sh, 180, ty - 23, 3.2, "r")

def vaderdag_vliegeren(sh):
    sh.region(cloud_path(52, 30, 12), "-"); sh.region(cloud_path(110, 60, 8), "-")
    bird(sh, 96, 24); bird(sh, 108, 32, 5)
    grass(sh, 150, "l")
    sh.region("M0 200V172Q100 160 200 176V200Z", "g")
    # vlieger
    sh.poly_r([(156, 14), (178, 40), (156, 74), (134, 40)], "r")
    sh.line("M156 14V74M134 40H178", "l", "stroke-width:1.2")
    sh.region(heart_path(156, 42, 6), "y")
    sh.line("M156 74Q150 94 162 108Q172 122 164 136", "l", "stroke-width:1.2")
    for x, y, c in ((153, 90, "b"), (163, 112, "y"), (166, 130, "m")):
        sh.poly_r([(x - 5, y - 3), (x, y), (x - 5, y + 3)], c); sh.poly_r([(x + 5, y - 3), (x, y), (x + 5, y + 3)], c)
    # papa en kind
    s = 1.0; top = 192 - 4 - 101 * s
    hy = person(sh, 64, top, "t", "n", hands=((40, top + 66), (94, top + 70)), style="short", hair="w", s=s, face=False)
    eye(sh, 59, hy + 2, 1.8); eye(sh, 69, hy + 2, 1.8)
    sh.region(f"M51 {f(hy + 4)}Q52 {f(hy + 18)} 64 {f(hy + 18)}Q76 {f(hy + 18)} 77 {f(hy + 4)}Q72 {f(hy + 12)} 64 {f(hy + 12)}Q56 {f(hy + 12)} 51 {f(hy + 4)}Z", "w")
    smile(sh, 64, hy + 9, 3)
    s = .66; top = 192 - 4 - 101 * s
    hy = person(sh, 108, top, "r", "b", hands=((94, top + 54), (126, top + 6)), style="curly", hair="x", s=s)
    sh.line(f"M126 {f(top + 6)}Q140 {f(top - 30)} 156 74", "l", "stroke-width:1")
    sh.region(f"M120 {f(top + 2)}H132V{f(top + 10)}H120Z", "w")
    flower(sh, 22, 186, 5, "y", "o"); flower(sh, 176, 186, 5, "m")


# ---------- Hemelvaart / Pinksteren ----------
def cyclist(sh, ox, oy, s, shirt, pants, hair, helmet, basket=True, bike="b"):
    P = lambda x, y: f"{f(ox + x * s)} {f(oy + y * s)}"
    for wx in (-22, 22):
        sh.circle_r(ox + wx * s, oy - 12 * s, 12 * s, "-"); sh.circle_r(ox + wx * s, oy - 12 * s, 2.4 * s, "z")
    sh.line(f"M{P(-22, -12)}L{P(-2, -12)}L{P(-8, -34)}ZM{P(-2, -12)}L{P(16, -34)}L{P(-8, -34)}M{P(16, -34)}L{P(22, -12)}M{P(16, -34)}L{P(18, -42)}L{P(24, -42)}")
    sh.rect_r(ox - 14 * s, oy - 38 * s, 12 * s, 4 * s, "x", 2 * s)
    limb(sh, ox - 8 * s, oy - 40 * s, ox + 2 * s, oy - 28 * s, pants, 9 * s); limb(sh, ox + 2 * s, oy - 28 * s, ox - 4 * s, oy - 14 * s, pants, 8 * s)
    limb(sh, ox - 8 * s, oy - 40 * s, ox + 6 * s, oy - 30 * s, pants, 10 * s); limb(sh, ox + 6 * s, oy - 30 * s, ox + 4 * s, oy - 13 * s, pants, 9 * s)
    sh.ellipse_r(ox + 7 * s, oy - 11 * s, 6 * s, 3 * s, "x")
    limb(sh, ox - 8 * s, oy - 40 * s, ox - 2 * s, oy - 62 * s, shirt, 15 * s)
    limb(sh, ox, oy - 58 * s, ox + 20 * s, oy - 43 * s, shirt, 7 * s); sh.circle_r(ox + 21 * s, oy - 42 * s, 3.4 * s, "-")
    sh.circle_r(ox + 2 * s, oy - 74 * s, 10 * s, "-")
    if helmet: sh.region(f"M{P(-9, -75)}A11 11 0 0 1 {P(13, -77)}L{P(10, -74)}Q{P(2, -80)} {P(-9, -75)}Z".replace("A11 11", f"A{f(11 * s)} {f(11 * s)}"), helmet)
    else: sh.region(f"M{P(-8, -72)}A{f(10 * s)} {f(10 * s)} 0 0 1 {P(12, -76)}Q{P(2, -82)} {P(-8, -72)}Z", hair)
    if hair and helmet: sh.region(f"M{P(-7, -70)}Q{P(-14, -60)} {P(-6, -58)}Q{P(-8, -64)} {P(-4, -68)}Z", hair)
    eye(sh, ox + 7 * s, oy - 74 * s, 1.3 * s); sh.line(f"M{P(5, -69)}Q{P(8, -67)} {P(10, -70)}", "l", "stroke-width:1.3")
    if basket:
        for k, c in enumerate("rym"):
            x = 26 + k * 5
            sh.line(f"M{P(x, -44)}L{P(x - 1, -52)}", "l", "stroke-width:1.2"); flower(sh, ox + (x - 1) * s, oy - 55 * s, 2.6 * s, c)
        sh.region(f"M{P(22, -44)}H{P(42, -44)}L{P(40, -32)}H{P(24, -32)}Z", "w")
        sh.line(f"M{P(23, -38)}H{P(41, -38)}", "l", "stroke-width:1")

def fietstocht(sh):
    sun(sh, 26, 24, 11); sh.region(cloud_path(110, 22, 11), "-"); bird(sh, 160, 22); bird(sh, 174, 30, 5)
    sh.region("M0 112Q100 100 200 112V150H0Z", "l")
    for k in range(3):
        y = 120 + k * 9; c = "rym"[k]
        for x in range(4 + (k % 2) * 6, 200, 12):
            sh.region(f"M{x - 2.5} {y}V{y - 4}L{x - 1.2} {y - 2.6}L{x} {y - 4.6}L{x + 1.2} {y - 2.6}L{x + 2.5} {y - 4}V{y}Z", c)
    sh.region(blob(170, 80, 18, 16, 8), "g"); sh.rect_r(167, 92, 6, 20, "w")
    sh.rect_r(16, 70, 14, 42, "-"); sh.poly_r([(16, 70), (23, 58), (30, 70)], "z")
    for a in (30, 120, 210, 300):
        r = math.radians(a); sh.line(f"M23 74L{f(23 + 18 * math.cos(r))} {f(74 + 18 * math.sin(r))}")
    sh.circle_r(23, 74, 2.2, "z")
    sh.region("M0 150H200V184H0Z", "z")
    sh.line("M0 167H24M44 167H68M88 167H112M132 167H156M176 167H200", "l", "stroke-width:1.2")
    sh.region("M0 184H200V200H0Z", "g")
    for x in (14, 70, 130, 186): flower(sh, x, 192, 4, "y", "o")
    cyclist(sh, 126, 180, 1.3, "r", "n", "w", "y")
    cyclist(sh, 44, 182, 1.0, "g", "b", "x", "m", basket=False)

def lammetjes(sh):
    sun(sh, 172, 24, 11); sh.region(cloud_path(60, 26, 12), "-")
    grass(sh, 120, "l")
    for x in (10, 60, 110, 160): sh.rect_r(x - 3, 92, 6, 40, "w")
    sh.rect_r(0, 100, 200, 5, "w"); sh.rect_r(0, 114, 200, 5, "w")
    sheep(sh, 150, 154, 1.6, True)
    s = .9; top = 192 - 4 - 101 * s
    person(sh, 64, top, "m", "n", hands=((44, top + 70), (94, top + 50)), style="braids", hair="o", s=s)
    for x, y, c in ((24, 186, "y"), (110, 188, "m"), (180, 190, "y"), (16, 140, "k")): flower(sh, x, y, 4.5, c, "o" if c == "y" else "y")
    sh.region(heart_path(100, 66, 6), "r")


# ---------- Keti Koti ----------
def keti_koti(sh):
    bunting(sh, 0, 6, 200, 6, 10, ["r", "y", "g", "o", "b"], 6, 10)
    sun(sh, 172, 40, 10)
    grass(sh, 188)
    def dancer(cx, top, blouse, kotocode, wrap, s, up):
        hy = top + 15 * s
        hands = ((cx - 26 * s, hy - 6 * s), (cx + 26 * s, hy + 30 * s)) if up else ((cx - 26 * s, hy + 30 * s), (cx + 26 * s, hy - 6 * s))
        person(sh, cx, top, blouse, "-", hands=hands, hair="x", style="short", s=s, draw_legs=False, cap=True)
        sh.region(f"M{f(cx - 16 * s)} {f(hy + 40 * s)}C{f(cx - 32 * s)} {f(hy + 62 * s)} {f(cx - 36 * s)} {f(hy + 82 * s)} {f(cx - 30 * s)} {f(hy + 88 * s)}H{f(cx + 30 * s)}C{f(cx + 36 * s)} {f(hy + 82 * s)} {f(cx + 32 * s)} {f(hy + 62 * s)} {f(cx + 16 * s)} {f(hy + 40 * s)}Z", kotocode)
        for k in (-1, 0, 1): sh.line(f"M{f(cx + k * 8 * s)} {f(hy + 44 * s)}Q{f(cx + k * 20 * s)} {f(hy + 70 * s)} {f(cx + k * 22 * s)} {f(hy + 88 * s)}", "l", "stroke-width:1")
        sh.region(f"M{f(cx - 32 * s)} {f(hy + 74 * s)}Q{f(cx)} {f(hy + 82 * s)} {f(cx + 32 * s)} {f(hy + 74 * s)}L{f(cx + 31 * s)} {f(hy + 80 * s)}Q{f(cx)} {f(hy + 88 * s)} {f(cx - 31 * s)} {f(hy + 80 * s)}Z", "y")
        sh.ellipse_r(cx - 8 * s, hy + 90 * s, 7 * s, 3.5 * s, "x"); sh.ellipse_r(cx + 8 * s, hy + 90 * s, 7 * s, 3.5 * s, "x")
        angisa(sh, cx, hy, s, wrap)
    dancer(48, 90, "-", "r", "y", .9, True)
    dancer(114, 98, "-", "p", "o", .82, False)
    # trommelaar
    s = .78; top = 190 - 4 - 101 * s
    hy = person(sh, 170, top, "g", "x", hands=((154, top + 46), (188, top + 40)), style="short", hair="x", s=s)
    sh.region(f"M150 {f(top + 56)}H190V{f(top + 80)}H150Z", "o"); sh.ellipse_r(170, top + 80, 20, 5, "o"); sh.ellipse_r(170, top + 56, 20, 5, "-")
    sh.line(f"M152 {f(top + 62)}L164 {f(top + 80)}L176 {f(top + 62)}L188 {f(top + 80)}", "l", "stroke-width:1")
    sh.line(f"M154 {f(top + 46)}L164 {f(top + 54)}M188 {f(top + 40)}L178 {f(top + 52)}", "l", "stroke-width:2")
    for x, y in ((150, 86), (192, 92), (82, 60)):
        sh.line(f"M{x} {y}V{y - 10}L{x + 6} {y - 12}V{y - 2}", "l", "stroke-width:1.2"); sh.ellipse_r(x - 2, y, 2.4, 1.8, "x"); sh.ellipse_r(x + 4, y - 2, 2.4, 1.8, "x")


# ---------- School ----------
def eerste_schooldag(sh):
    sun(sh, 26, 22, 10); sh.region(cloud_path(150, 18, 10), "-")
    sh.rect_r(18, 56, 164, 130, "r")
    sh.rect_r(90, 30, 20, 26, "r"); sh.poly_r([(86, 32), (100, 18), (114, 32)], "z"); sh.circle_r(100, 43, 5, "y")
    sh.rect_r(14, 52, 172, 6, "z")
    sh.rect_r(60, 62, 80, 14, "-", 2); sh.text(100, 72.5, "SCHOOL", 9)
    for x in (30, 150):
        sh.rect_r(x, 84, 22, 22, "b", 1); sh.seg(x + 11, 84, x + 11, 106, "l", "stroke-width:1.2")
        sh.rect_r(x, 124, 22, 22, "b", 1); sh.seg(x + 11, 124, x + 11, 146, "l", "stroke-width:1.2")
    sh.region("M84 186V112Q100 98 116 112V186Z", "g"); sh.seg(100, 106, 100, 186, "l", "stroke-width:1.4"); sh.dot(96, 150, 1.3); sh.dot(104, 150, 1.3)
    sh.rect_r(0, 186, 200, 14, "z")
    # kind met grote rugzak
    s = .86; cx = 62; top = 194 - 4 - 101 * s; hy = top + 15 * s
    sh.rect_r(cx - 22 * s, hy + 18 * s, 44 * s, 40 * s, "y", 8 * s)
    person(sh, cx, top, "t", "n", hands=((cx - 24 * s, hy + 50 * s), (cx + 26 * s, hy - 10 * s)), style="curly", hair="x", s=s)
    sh.line(f"M{f(cx - 10 * s)} {f(hy + 16 * s)}V{f(hy + 46 * s)}M{f(cx + 10 * s)} {f(hy + 16 * s)}V{f(hy + 46 * s)}", "l", "stroke-width:2.6")
    sh.region(f"M{f(cx - 37 * s)} {f(hy + 52 * s)}H{f(cx - 17 * s)}V{f(hy + 66 * s)}H{f(cx - 37 * s)}Z", "m"); sh.line(f"M{f(cx - 31 * s)} {f(hy + 52 * s)}Q{f(cx - 27 * s)} {f(hy + 46 * s)} {f(cx - 23 * s)} {f(hy + 52 * s)}", "l", "stroke-width:1.4")
    sh.circle_r(cx - 24 * s, hy + 50 * s, 4.5 * s, "-")
    flower(sh, 156, 180, 5, "y", "o"); flower(sh, 172, 186, 4, "m")


# ---------- Dierendag ----------
def dierendag(sh):
    for x, y, s in ((30, 30, 7), (170, 26, 6), (100, 16, 5)): sh.region(heart_path(x, y, s), "r")
    sh.rect_r(0, 184, 200, 16, "w")
    dog_sit(sh, 40, 186, 1.3, "w", "x", "r")
    cat_sit(sh, 166, 186, 1.25, "o")
    s = .95; top = 186 - 4 - 101 * s
    hy = person(sh, 104, top, "g", "n", hands=((80, 118), (128, top + 70)), style="long", hair="w", s=s)
    limb(sh, 62, 112, 76, 118, "-", 4.5)
    for x, y in ((62, 112), (76, 118)): sh.circle_r(x - 1.5, y - 2, 3, "-"); sh.circle_r(x + 1.5, y + 2, 3, "-")
    sh.circle_r(80, 118, 4.3, "-")
    sh.region("M124 180H152L148 188H128Z", "b"); sh.ellipse_r(138, 180, 14, 3, "-")
    sh.region("M130 178Q136 170 144 176L148 172V182L144 178Q136 184 130 178Z", "t")


# ---------- Halloween ----------
def pumpkin(sh, x, y, r, code="o", carved=False):
    sh.rect_r(x - 2.5, y - r * .9 - 6, 5, 8, "g", 1)
    sh.ellipse_r(x - r * .5, y, r * .6, r * .8, code); sh.ellipse_r(x + r * .5, y, r * .6, r * .8, code)
    sh.ellipse_r(x, y, r * .55, r * .85, code)
    if carved:
        sh.poly_r([(x - r * .5, y - r * .1), (x - r * .32, y - r * .4), (x - r * .14, y - r * .1)], "y")
        sh.poly_r([(x + r * .14, y - r * .1), (x + r * .32, y - r * .4), (x + r * .5, y - r * .1)], "y")
        sh.region(f"M{f(x - r * .55)} {f(y + r * .15)}Q{f(x)} {f(y + r * .7)} {f(x + r * .55)} {f(y + r * .15)}Q{f(x)} {f(y + r * .35)} {f(x - r * .55)} {f(y + r * .15)}Z", "y")

def pompoenen_uithollen(sh):
    sh.rect_r(14, 12, 50, 40, "n", 2); sh.seg(39, 12, 39, 52, "l", "stroke-width:1.4"); sh.seg(14, 32, 64, 32, "l", "stroke-width:1.4")
    sh.region(moon_path(26, 22, 6), "y")
    sh.region("M44 42Q48 36 52 40Q54 36 56 40Q60 36 62 42Q56 40 53 44Q50 40 44 42Z", "x")
    sh.line("M120 8Q140 22 160 8Q180 22 200 8", "l", "stroke-width:1.2")
    for x in (130, 150, 170, 190): sh.poly_r([(x - 5, 12 + (x % 20) * .3), (x + 5, 12 + (x % 20) * .3), (x, 22)], "o")
    s = .86
    person(sh, 104, 52, "p", "-", hands=((70, 118), (128, 132)), style="pony", hair="o", s=s, draw_legs=False, arms_front=True, draw_hands=False)
    sh.rect_r(0, 140, 200, 60, "w"); sh.line("M0 140H200")
    sh.ellipse_r(84, 146, 60, 6, "-")
    # pompoen die wordt uitgehold
    pumpkin(sh, 66, 124, 26, "o")
    sh.ellipse_r(66, 104, 14, 4, "y")
    sh.ellipse_r(22, 136, 12, 5, "o"); sh.rect_r(20, 126, 4, 7, "g", 1)
    limb(sh, 70, 118, 70, 100, "z", 3.2); sh.ellipse_r(70, 98, 4, 3, "z")
    sh.circle_r(70, 118, 3.8, "-")
    # lepel en kom met pitten
    sh.region("M96 170H140Q138 186 118 186Q98 186 96 170Z", "b"); sh.ellipse_r(118, 170, 22, 4, "-")
    for x, y in ((110, 168), (118, 167), (126, 169), (114, 172), (122, 172)): sh.ellipse_r(x, y, 2.2, 1.2, "y")
    # klaar: lachende lantaarn
    pumpkin(sh, 160, 124, 24, "o", True)
    sh.circle_r(128, 132, 3.8, "-")
    for x, y in ((40, 170), (60, 178), (160, 180)): sh.ellipse_r(x, y, 2.4, 1.3, "y")

def langs_de_deuren(sh):
    sh.rect_r(0, 0, 200, 186, "n")
    sh.circle_r(30, 28, 14, "y")
    for x, y in ((70, 16), (110, 30), (54, 48)): sh.region(star_path(x, y, 4, 1.8), "y")
    for x, y in ((90, 56), (64, 76)):
        sh.region(f"M{x - 10} {y}Q{x - 6} {y - 6} {x - 2} {y - 2}Q{x} {y - 5} {x + 2} {y - 2}Q{x + 6} {y - 6} {x + 10} {y}Q{x + 5} {y - 1} {x + 2} {y + 3}Q{x} {y} {x - 2} {y + 3}Q{x - 5} {y - 1} {x - 10} {y}Z", "x")
    sh.rect_r(0, 186, 200, 14, "z")
    # huis met deur
    sh.rect_r(124, 30, 76, 156, "w")
    sh.rect_r(140, 80, 40, 106, "y"); sh.region("M140 80L130 86V180L140 186Z", "r")
    sh.rect_r(184, 40, 14, 22, "y", 1)
    sh.rect_r(130, 66, 6, 10, "-", 2)
    s = .76
    person(sh, 160, 186 - 4 - 101 * s, "g", "x", hands=((142, 132), (176, 138)), style="long", hair="w", s=s)
    sh.region("M128 130H158Q156 140 143 140Q130 140 128 130Z", "b")
    for x, c in ((134, "r"), (142, "m"), (150, "y")): sh.circle_r(x, 128, 3.4, c)
    pumpkin(sh, 196, 176, 10, "o", True)
    # spookje
    sx = 40
    sh.region(f"M{sx - 22} 186V120Q{sx - 22} 92 {sx} 92Q{sx + 22} 92 {sx + 22} 120V186L{sx + 14} 178L{sx + 7} 186L{sx} 178L{sx - 7} 186L{sx - 14} 178Z", "-")
    sh.ellipse_r(sx - 7, 112, 3.5, 4.5, "x"); sh.ellipse_r(sx + 7, 112, 3.5, 4.5, "x"); sh.ellipse_r(sx, 124, 3, 3.6, "x")
    sh.region(f"M{sx + 20} 140L{sx + 28} 144L{sx + 22} 150Z", "-")
    sh.region(f"M{sx + 22} 146H{sx + 38}L{sx + 36} 168H{sx + 24}Z", "o"); sh.line(f"M{sx + 24} 146Q{sx + 30} 138 {sx + 36} 146", "l", "stroke-width:1.4")
    # heksje
    s = .7; cx = 96; top = 188 - 4 - 101 * s; hy = top + 15 * s
    sh.region(f"M{f(cx - 12 * s)} {f(hy + 14 * s)}L{f(cx - 30 * s)} {f(hy + 90 * s)}H{f(cx + 30 * s)}L{f(cx + 12 * s)} {f(hy + 14 * s)}Z", "p")
    person(sh, cx, top, "p", "x", hands=((cx - 26 * s, hy + 46 * s), (cx + 30 * s, hy + 40 * s)), style="long", hair="o", s=s, cap=True)
    sh.region(f"M{f(cx - 26 * s)} {f(hy - 8 * s)}H{f(cx + 26 * s)}L{f(cx + 22 * s)} {f(hy - 4 * s)}H{f(cx - 22 * s)}Z", "x")
    sh.region(f"M{f(cx - 12 * s)} {f(hy - 8 * s)}L{f(cx + 8 * s)} {f(hy - 44 * s)}L{f(cx + 12 * s)} {f(hy - 8 * s)}Z", "x")
    sh.rect_r(cx - 11 * s, hy - 14 * s, 22 * s, 5 * s, "g")
    pumpkin(sh, cx + 30 * s, hy + 52 * s, 9, "o")
    sh.line(f"M{f(cx + 23 * s)} {f(hy + 44 * s)}Q{f(cx + 30 * s)} {f(hy + 34 * s)} {f(cx + 37 * s)} {f(hy + 44 * s)}", "l", "stroke-width:1.4")


# ---------- Divali ----------
def rangoli(sh):
    sh.rect_r(0, 0, 200, 140, "o")
    for x in range(0, 200, 40): sh.seg(x, 0, x, 140, "l", "stroke-width:.6")
    sh.rect_r(70, 30, 60, 110, "w"); sh.seg(100, 30, 100, 140, "l", "stroke-width:1.4"); sh.dot(94, 90, 1.3); sh.dot(106, 90, 1.3)
    sh.rect_r(64, 24, 72, 6, "y")
    for k in range(10):
        x = 68 + k * 7; y = 33 + (3 if k % 2 else 0)
        sh.circle_r(x, y, 3.4, "o" if k % 2 else "y")
    for x in (78, 122): sh.line(f"M{x} 36V44"); sh.poly_r([(x - 3, 44), (x + 3, 44), (x, 50)], "g")
    sh.line("M0 12Q30 24 60 12M140 12Q170 24 200 12", "l", "stroke-width:1.2")
    for x in (10, 20, 30, 40, 50, 150, 160, 170, 180, 190):
        y = 12 + 12 * (1 - ((x % 140 if x > 100 else x) - 30) ** 2 / 900) * .5 * 1.0
        sh.ellipse_r(x, y + 4, 2.6, 3.4, "y")
    sh.rect_r(0, 140, 200, 60, "-")
    sh.seg(0, 140, 200, 140)
    # rangoli (platte bloem, schuin van bovenaf)
    cx, cy, k = 100, 172, .42
    M = lambda x, y: f"{f(cx + x)} {f(cy + y * k)}"
    sh.ellipse_r(cx, cy, 52, 52 * k, "p")
    for i in range(12):
        a = math.radians(i * 30); ca, sa = math.cos(a), math.sin(a)
        R = lambda r, t: (r * math.cos(a + t), r * math.sin(a + t))
        p0, p1, p2, p3 = R(26, -.22), R(46, 0), R(26, .22), R(36, 0)
        sh.region(f"M{M(*p0)}Q{M(*R(42, -.2))} {M(*p1)}Q{M(*R(42, .2))} {M(*p2)}Q{M(*p3)} {M(*p0)}Z", "y" if i % 2 else "o")
    sh.ellipse_r(cx, cy, 26, 26 * k, "m")
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        sh.region(f"M{M(0, 0)}Q{M(18 * math.cos(a - .5), 18 * math.sin(a - .5))} {M(22 * math.cos(a), 22 * math.sin(a))}Q{M(18 * math.cos(a + .5), 18 * math.sin(a + .5))} {M(0, 0)}Z", "r" if i % 2 else "t")
    sh.ellipse_r(cx, cy, 6, 6 * k, "y")
    for i in range(16):
        a = math.radians(i * 22.5); sh.dot(cx + 50 * math.cos(a) * 1.08, cy + 50 * math.sin(a) * k * 1.12, 1.2)
    for x, y in ((40, 162), (160, 162), (30, 186), (170, 186)): diya(sh, x, y, 1.0)
    # meisje met lichtje
    s = .78; top = 160 - 4 - 101 * s; hy = top + 15 * s
    person(sh, 32, top, "m", "y", hands=((24, hy + 52 * s), (40, hy + 52 * s)), style="long", hair="x", s=s, skirt="m", arms_front=True)
    diya(sh, 32, hy + 50 * s, .8)
    # jongen met schaal snoepjes
    s = .72; top = 160 - 4 - 101 * s; hy = top + 15 * s
    person(sh, 168, top, "t", "w", hands=((154, hy + 40 * s), (182, hy + 40 * s)), style="short", hair="x", s=s, arms_front=True)
    sh.region(f"M150 {f(hy + 34 * s)}H186Q184 {f(hy + 46 * s)} 168 {f(hy + 46 * s)}Q152 {f(hy + 46 * s)} 150 {f(hy + 34 * s)}Z", "y")
    for x in (157, 165, 173, 181, 161, 177): sh.circle_r(x, hy + 30 * s - (4 if x in (161, 177) else 0), 3.2, "o")


# ---------- Sint-Maarten ----------
def sint_maarten_deur(sh):
    sh.rect_r(0, 0, 200, 188, "n")
    sh.region(moon_path(174, 24, 12), "y")
    for x, y in ((30, 20), (80, 12), (130, 28)): sh.region(star_path(x, y, 4, 1.8), "y")
    sh.rect_r(0, 188, 200, 12, "z")
    for x, y, c, r in ((20, 194, "o", 40), (70, 192, "r", -30), (160, 194, "y", 80)): leaf_at(sh, x, y, 4, 6, r, c)
    sh.rect_r(0, 50, 72, 138, "r")
    for y in range(60, 188, 10): sh.seg(0, y, 72, y, "l", "stroke-width:.7")
    sh.rect_r(14, 88, 46, 100, "-")
    sh.rect_r(20, 64, 34, 18, "y", 2); sh.line("M37 64V82", "l", "stroke-width:1.2")
    s = .72
    person(sh, 38, 188 - 4 - 101 * s, "b", "x", hands=((24, 150), (58, 134)), style="bun", hair="z", s=s)
    sh.region("M44 128H76Q74 140 60 140Q46 140 44 128Z", "-")
    for x, c in ((52, "o"), (60, "o"), (68, "o"), (56, "r")): sh.circle_r(x, 126 - (4 if c == "r" else 0), 3.6, c)
    # kinderen met lampionnen die zingen
    s = .74; top = 192 - 4 - 101 * s
    hy = person(sh, 112, top, "y", "g", hands=((92, top + 34), (132, top + 58)), style="curly", hair="w", s=s, face=False)
    beanie(sh, 112, hy, "r", "-", s); face(sh, 112, hy, s, "open")
    sh.line(f"M92 {f(top + 34)}L86 {f(top + 6)}"); sh.line(f"M86 {f(top + 6)}V{f(top + 14)}", "l", "stroke-width:1.2")
    lantern_paper(sh, 86, top + 26, 10, "y", False)
    s = .66; top = 192 - 4 - 101 * s
    hy = person(sh, 160, top, "p", "n", hands=((144, top + 56), (178, top + 30)), style="braids", hair="x", s=s, face=False)
    face(sh, 160, hy, s, "open")
    sh.line(f"M178 {f(top + 30)}L184 {f(top + 2)}")
    sh.line(f"M184 {f(top + 2)}V{f(top + 8)}", "l", "stroke-width:1.2")
    sh.region(star_path(184, top + 20, 11, 6, 6), "o")
    for x, y in ((104, 74), (130, 60), (152, 80)):
        sh.line(f"M{x} {y}V{y - 10}L{x + 6} {y - 12}V{y - 2}", "l", "stroke-width:1.2"); sh.ellipse_r(x - 2, y, 2.4, 1.8, "-"); sh.ellipse_r(x + 4, y - 2, 2.4, 1.8, "-")


# ---------- Sinterklaas ----------
def schoen_zetten(sh):
    sh.rect_r(0, 186, 200, 14, "w")
    sh.rect_r(24, 50, 152, 12, "w", 2)
    sh.rect_r(34, 62, 132, 124, "r")
    for y in range(72, 186, 10):
        sh.seg(34, y, 166, y, "l", "stroke-width:.7")
        for x in range(34 + (10 if (y // 10) % 2 else 0), 166, 20): sh.seg(x, y - 10, x, y, "l", "stroke-width:.7")
    sh.region("M60 186V104Q60 88 76 88H124Q140 88 140 104V186Z", "x")
    sh.line("M70 176H130M76 166V176M88 166V176M100 166V176M112 166V176M124 166V176")
    # op de schoorsteenmantel
    sh.rect_r(40, 34, 8, 16, "-", 1); sh.region(drop_path(44, 28, 2.4), "y")
    sh.region("M140 50Q138 38 152 38Q166 38 164 50Z", "b")
    for x, y in ((144, 36), (150, 34), (156, 35), (153, 31), (160, 37)): sh.circle_r(x, y, 2.6, "w")
    # wortel en tekening in de schoen
    sh.raw('<g transform="rotate(-20 58 150)">'); sh.region("M52 158L58 120L64 158Z", "o"); sh.line("M55 146H60M56 136H60", "l", "stroke-width:1")
    sh.region("M58 120Q50 110 54 104Q58 112 58 118Q60 108 66 104Q66 114 58 120Z", "g"); sh.raw("</g>")
    sh.raw('<g transform="rotate(12 86 140)">'); sh.rect_r(72, 124, 30, 40, "-", 1)
    sh.region("M80 148V136Q87 126 94 136V148Z", "r"); sh.line("M87 130V136M84 133H90M80 148H94", "l", "stroke-width:1.2")
    sh.raw("</g>")
    # schoen
    sh.region("M44 194V170Q44 156 58 156H86Q96 156 102 166L128 172Q142 176 140 194Z", "b")
    sh.rect_r(42, 192, 100, 6, "-", 2)
    sh.line("M70 160L80 168M78 158L88 166M86 158L94 166", "l", "stroke-width:1.2")
    # pepernoten
    for x, y in ((156, 190), (166, 192), (176, 190), (170, 184)): sh.circle_r(x, y, 3.2, "w")

def pakjesavond(sh):
    sh.rect_r(0, 0, 200, 186, "-")
    sh.rect_r(150, 10, 42, 46, "n", 2); sh.seg(171, 10, 171, 56, "l", "stroke-width:1.4"); sh.seg(150, 33, 192, 33, "l", "stroke-width:1.4")
    sh.region(moon_path(184, 20, 6), "y"); sh.region("M152 56V46L162 40L172 46H180V40H186V46L190 50V56Z", "x")
    sh.rect_r(12, 12, 30, 24, "-", 1); sh.region("M20 32V22Q27 14 34 22V32Z", "r"); sh.line("M27 16V22M24 19H30", "l", "stroke-width:1.2")
    sh.rect_r(0, 186, 200, 14, "w")
    # bank met ouders
    sh.rect_r(46, 54, 104, 60, "g", 10)
    person(sh, 76, 44, "r", "n", hands=((66, 108), (88, 108)), style="long", hair="w", s=.72, draw_legs=False, arms_front=True)
    person(sh, 122, 40, "b", "n", hands=((112, 100), (134, 100)), style="short", hair="x", s=.76, draw_legs=False, arms_front=True)
    sh.rect_r(112, 86, 22, 16, "-", 1); sh.line("M115 90H131M115 94H131M115 98H125", "l", "stroke-width:.9"); sh.circle_r(112, 100, 3, "-"); sh.circle_r(134, 100, 3, "-")
    sh.rect_r(40, 108, 120, 22, "g", 6); sh.rect_r(36, 84, 16, 48, "g", 6); sh.rect_r(148, 84, 16, 48, "g", 6)
    for x in (44, 152): sh.rect_r(x, 132, 6, 8, "w")
    # jute zak
    sh.region("M164 186Q160 150 172 132L168 124H192L188 132Q200 150 196 186Z", "w")
    sh.line("M168 128H192"); present(sh, 172, 120, 14, 8, "m", "y")
    # kinderen op de grond met pakjes
    s = .64
    hy = person(sh, 60, 118, "y", "n", hands=((40, 164), (80, 164)), style="pony", hair="o", s=s, draw_legs=False, arms_front=False)
    sit_legs(sh, 60, 182, s, "n")
    sh.rect_r(42, 156, 36, 22, "t", 1); sh.region("M42 156L36 146L62 150Z", "t")
    sh.region("M50 156Q50 146 56 146Q62 146 62 156Z", "w"); sh.circle_r(56, 148, 2.2, "w")
    for x, y in ((40, 164), (80, 164)): sh.circle_r(x, y, 3, "-")
    hy = person(sh, 128, 120, "o", "z", hands=((112, 156), (142, 140)), style="curly", hair="x", s=s, draw_legs=False)
    sit_legs(sh, 128, 182, s, "z")
    sh.raw('<g transform="rotate(-12 150 150)">'); sh.region("M140 160V140H160V160Z", "p"); sh.region("M140 158L160 142M144 160L160 148", "-"); sh.raw("</g>")
    sh.circle_r(142, 140, 3, "-"); sh.circle_r(112, 156, 3, "-")
    # chocoladeletter en pepernoten
    sh.region("M8 186V160H26V166H14V170H24V176H14V180H26V186Z", "w")
    sh.region("M88 186Q90 176 104 176Q118 176 120 186Z", "b")
    for x in (96, 103, 110, 100, 107): sh.circle_r(x, 176 - (3 if x in (100, 107) else 0), 2.6, "w")
    for x, y, r, c in ((30, 140, 20, "r"), (98, 150, -30, "y"), (174, 104, 40, "b")):
        sh.raw(f'<g transform="rotate({r} {x} {y})">'); sh.region(f"M{x - 6} {y - 4}L{x + 6} {y - 6}L{x + 5} {y + 4}L{x - 5} {y + 5}Z", c); sh.raw("</g>")


# ---------- Chanoeka ----------
def draaitol(sh):
    sh.rect_r(0, 0, 200, 120, "-")
    sh.rect_r(56, 8, 88, 52, "n", 2); sh.rect_r(52, 60, 96, 6, "w")
    sh.rect_r(70, 52, 60, 4, "y"); sh.rect_r(98, 40, 4, 12, "y")
    for i in range(9):
        x = 72 + i * 7 if i < 4 else (100 if i == 4 else 72 + i * 7)
        y = 40 if i != 4 else 30
        sh.rect_r(x - 1.6, y, 3.2, 52 - y, "b"); sh.region(drop_path(x, y - 4, 2), "y")
    sh.rect_r(0, 120, 200, 80, "w")
    sh.region("M20 196L40 132H160L180 196Z", "r")
    sh.region("M36 186L50 142H150L164 186Z", "y")
    # opa en twee kinderen
    s = .66
    person(sh, 38, 78, "g", "x", hands=((20, 134), (56, 134)), style="short", hair="z", s=.72, draw_legs=False)
    sit_legs(sh, 38, 139, .72, "x")
    person(sh, 162, 92, "p", "n", hands=((142, 144), (182, 144)), style="long", hair="w", s=s, draw_legs=False)
    sit_legs(sh, 162, 148, s, "n")
    person(sh, 100, 64, "o", "b", hands=((84, 112), (116, 112)), style="curly", hair="x", s=.6, draw_legs=False, face=False)
    face(sh, 100, 64 + 9, .6, "open")
    sit_legs(sh, 100, 114, .6, "b")
    # draaitol
    sh.region("M100 178L88 160V146H112V160Z", "b")
    sh.rect_r(97, 138, 6, 8, "b", 1)
    sh.text(100, 160, "נ", 9)
    sh.line("M80 152Q74 160 80 168M120 152Q126 160 120 168", "l", "stroke-width:1.2")
    # munten en donuts
    for x, y in ((62, 172), (68, 168), (74, 174), (130, 172), (138, 168)): sh.circle_r(x, y, 4.5, "y"); sh.circle_r(x, y, 2, "-")
    sh.ellipse_r(124, 152, 12, 4, "-")
    for x in (118, 130): sh.ellipse_r(x, 148, 6, 4, "w"); sh.dot(x, 147, 1.2)


# ---------- Kerst ----------
def kerstboom_versieren(sh):
    sh.rect_r(0, 186, 200, 14, "w")
    sh.rect_r(10, 12, 36, 30, "b", 1); sh.seg(28, 12, 28, 42, "l", "stroke-width:1.2"); sh.seg(10, 27, 46, 27, "l", "stroke-width:1.2")
    for x, y in ((18, 20), (36, 34), (40, 18)): sh.circle_r(x, y, 1.6, "-")
    cx = 118
    sh.rect_r(cx - 6, 168, 12, 10, "w"); sh.rect_r(cx - 14, 176, 28, 10, "r", 2)
    for k, (y0, w, h) in enumerate(((168, 54, 40), (136, 44, 38), (106, 34, 36), (78, 24, 34))):
        sh.region(f"M{cx - w} {y0}Q{cx - w / 2} {y0 - 6} {cx} {y0 - h}Q{cx + w / 2} {y0 - 6} {cx + w} {y0}Q{cx} {y0 - 8} {cx - w} {y0}Z", "g")
    sh.line("M80 152Q118 140 156 150M90 122Q118 112 146 120M100 94Q118 86 136 92", "l", "stroke-width:1.4")
    for x, y, c in ((92, 158, "r"), (130, 156, "y"), (150, 162, "b"), (110, 128, "m"), (136, 128, "r"), (118, 100, "y")):
        sh.circle_r(x, y, 4.5, c); sh.rect_r(x - 1.5, y - 6.5, 3, 2.5, "z")
    sh.region(star_path(cx, 40, 10, 4.5), "y")
    # kind dat een bal ophangt
    s = .78; top = 194 - 4 - 101 * s
    person(sh, 42, top, "r", "n", hands=((20, top + 60), (68, top + 6)), style="curly", hair="x", s=s)
    sh.line(f"M68 {f(top + 2)}V{f(top + 10)}", "l", "stroke-width:1"); sh.circle_r(68, top + 15, 5, "t")
    # kind met slinger
    s = .68; top = 194 - 4 - 101 * s
    person(sh, 172, top, "y", "g", hands=((154, top + 44), (188, top + 52)), style="braids", hair="w", s=s)
    sh.line(f"M154 {f(top + 44)}Q160 {f(top + 64)} 170 {f(top + 60)}Q180 {f(top + 56)} 188 {f(top + 52)}", "l", "stroke-width:3;stroke-dasharray:3 2")
    # doos met ballen
    sh.rect_r(70, 172, 30, 14, "o", 1)
    for x, c in ((76, "r"), (85, "b"), (94, "y")): sh.circle_r(x, 170, 4, c)
    present(sh, 140, 172, 18, 14, "b", "y")

def kerstmarkt(sh):
    for x, y in ((14, 10), (60, 6), (110, 14), (156, 8), (190, 22), (34, 30), (86, 30), (136, 30)):
        sh.line(f"M{x - 2.5} {y}H{x + 2.5}M{x - 1.2} {y - 2.2}L{x + 1.2} {y + 2.2}M{x + 1.2} {y - 2.2}L{x - 1.2} {y + 2.2}", "l", "stroke-width:1")
    # huizen op de achtergrond
    for x0, w, top, c in ((0, 36, 44, "w"), (36, 30, 36, "z"), (66, 34, 46, "w"), (100, 32, 34, "z"), (132, 36, 42, "w"), (168, 32, 38, "z")):
        sh.rect_r(x0, top + 16, w, 80 - top, c)
        sh.poly_r([(x0, top + 16), (x0 + w / 2, top - 2), (x0 + w, top + 16)], c)
        sh.region(f"M{f(x0 + w * .2)} {f(top + 9)}L{f(x0 + w / 2)} {f(top - 2)}L{f(x0 + w * .8)} {f(top + 9)}Q{f(x0 + w / 2)} {f(top + 5)} {f(x0 + w * .2)} {f(top + 9)}Z", "-")
        sh.rect_r(x0 + w / 2 - 4, top + 22, 8, 10, "y", 1)
    sh.line("M0 70Q50 84 100 70Q150 84 200 70", "l", "stroke-width:1.2")
    for k in range(1, 16):
        x = k * 12.5; xx = x % 100; y = 70 + 14 * (1 - ((xx - 50) / 50) ** 2) * .5
        sh.circle_r(x, y + 3, 2.2, "ryb"[k % 3])
    sh.rect_r(0, 96, 200, 104, "-")
    # kraampjes
    def stall(x0, w, code, goods):
        sh.rect_r(x0 + 2, 98, 4, 52, "w"); sh.rect_r(x0 + w - 6, 98, 4, 52, "w")
        sh.region(f"M{x0 - 4} 100L{x0 + w / 2} 80L{x0 + w + 4} 100Z", code)
        sh.region(f"M{x0 + 4} 92Q{x0 + w / 2} 84 {x0 + w - 4} 92L{x0 + w / 2} 81Z", "-")
        sh.region(f"M{x0 - 4} 100H{x0 + w + 4}V104" + "".join(f"Q{f(x0 + w + 4 - (k + .5) * (w + 8) / 6)} 112 {f(x0 + w + 4 - (k + 1) * (w + 8) / 6)} 104" for k in range(6)) + "Z", code)
        sh.rect_r(x0, 134, w, 24, "w"); sh.line(f"M{x0} 142H{x0 + w}M{x0} 150H{x0 + w}", "l", "stroke-width:.8")
        goods(x0, w)
    def hearts(x0, w):
        for i, x in enumerate((x0 + 10, x0 + 22, x0 + 34, x0 + 46)):
            sh.line(f"M{x} 106V{112 + (i % 2) * 4}", "l", "stroke-width:1"); sh.region(heart_path(x, 118 + (i % 2) * 4, 5), "w"); sh.line(f"M{x - 3} {118 + (i % 2) * 4}Q{x} {120 + (i % 2) * 4} {x + 3} {118 + (i % 2) * 4}", "l", "stroke-width:.8")
        for x in (x0 + 12, x0 + 26, x0 + 40): sh.circle_r(x, 130, 4, "o")
    def candles(x0, w):
        for i, x in enumerate((x0 + 10, x0 + 20, x0 + 30, x0 + 40, x0 + 50)):
            h = 14 + (i % 3) * 4; sh.rect_r(x - 3, 134 - h, 6, h, "rpybt"[i]); sh.region(drop_path(x, 134 - h - 4, 1.8), "y")
    def baubles(x0, w):
        for i, x in enumerate((x0 + 10, x0 + 21, x0 + 32, x0 + 43, x0 + 54)):
            yy = 112 + (i % 2) * 8; sh.line(f"M{x} 104V{yy - 5}", "l", "stroke-width:1"); sh.circle_r(x, yy, 4.5, "rbmyt"[i])
        sh.ellipse_r(x0 + 32, 130, 12, 4, "o"); sh.ellipse_r(x0 + 32, 126, 6, 3, "o")
    stall(4, 60, "r", hearts); stall(70, 62, "g", candles); stall(138, 60, "r", baubles)
    # mensen op de markt
    s = .58
    hy = person(sh, 60, 200 - 4 - 101 * s - 2, "n", "x", hands=((46, 176), (82, 166)), style="long", hair="w", s=s, cap=True, face=False)
    beanie(sh, 60, hy, "g", "-", s); scarf(sh, 60, hy, "r", s); face(sh, 60, hy, s)
    s = .44
    hy = person(sh, 92, 200 - 4 - 101 * s - 2, "y", "n", hands=((84, 166), (106, 172)), style="short", hair="x", s=s, cap=True, face=False)
    beanie(sh, 92, hy, "r", "-", s); scarf(sh, 92, hy, "b", s); face(sh, 92, hy, s)
    sh.line("M106 172V160", "l", "stroke-width:1.2"); sh.region(heart_path(106, 158, 4.5), "w")
    s = .56
    hy = person(sh, 150, 200 - 4 - 101 * s - 2, "p", "x", hands=((134, 168), (166, 166)), style="curly", hair="x", s=s, cap=True, face=False)
    beanie(sh, 150, hy, "b", "-", s); face(sh, 150, hy, s)
    sh.rect_r(162, 158, 8, 9, "r", 1); sh.line("M170 160Q174 162 170 165", "l", "stroke-width:1.2")
    s = .42
    hy = person(sh, 182, 200 - 4 - 101 * s - 2, "t", "g", hands=((172, 176), (194, 176)), style="braids", hair="o", s=s, cap=True, face=False)
    beanie(sh, 182, hy, "m", "-", s); face(sh, 182, hy, s)
    sh.region(blob(18, 186, 14, 10, 7), "-"); sh.circle_r(18, 168, 8, "-"); sh.dot(15, 166, 1); sh.dot(21, 166, 1); sh.poly_r([(18, 169), (25, 170), (18, 171)], "o")


# ---------- Verjaardag ----------
def cadeautje_uitpakken(sh):
    for x, y, c, end in ((26, 34, "r", (40, 110)), (174, 30, "b", (160, 110)), (44, 20, "y", (40, 110))):
        balloon(sh, x, y, 13, c, end)
    sh.rect_r(0, 186, 200, 14, "w")
    s = .9; top = 52
    hy = person(sh, 100, top, "g", "n", hands=((62, 136), (138, 136)), style="pony", hair="w", s=s, draw_legs=False, face=False)
    party_hat(sh, 100, hy, s, "m", "y"); face(sh, 100, hy, s, "open")
    # doos open, deksel opzij
    sh.rect_r(60, 130, 80, 56, "y", 1)
    sh.rect_r(96, 130, 8, 56, "r")
    sh.region("M66 130Q72 116 84 118Q78 124 76 130Z", "-"); sh.region("M134 130Q128 116 116 118Q122 124 124 130Z", "-")
    for x in (62, 138): sh.circle_r(x, 136, 4.5 * s, "-")
    for x, y in ((80, 150), (120, 168), (76, 174), (122, 146)): sh.region(star_path(x, y, 4.5, 2), "-")
    sh.raw('<g transform="rotate(-18 170 168)">'); sh.rect_r(146, 160, 44, 10, "y", 1); sh.rect_r(164, 160, 8, 10, "r"); sh.raw("</g>")
    sh.region("M100 120C88 104 92 98 100 104C108 98 112 104 100 120Z", "r")
    for x, y in ((40, 160), (28, 176), (176, 140)): sparkle(sh, x, y, 5, "y")

def tuinfeest(sh):
    sh.region(blob(20, 70, 26, 24, 8), "g"); sh.rect_r(16, 84, 8, 50, "w")
    sh.region(blob(180, 66, 26, 24, 8), "g"); sh.rect_r(176, 80, 8, 54, "w")
    bunting(sh, 26, 76, 174, 72, 9, ["r", "y", "b", "m", "g"], 10, 9)
    sh.region(cloud_path(100, 20, 11), "-")
    sh.region("M0 200V132H200V200Z", "l")
    for x in range(0, 200, 12): sh.region(f"M{x} 132V112L{x + 6} 106L{x + 12} 112V132Z", "w") if x not in (12, 168, 180) else None
    sh.region("M0 132V134H200V132Z", "-")
    # tafel met taart
    sh.rect_r(60, 120, 80, 8, "b"); sh.region("M60 128H140V146" + "".join(f"Q{135 - k * 10} 152 {130 - k * 10} 146" for k in range(8)) + "Z", "b")
    sh.rect_r(66, 146, 4, 30, "w"); sh.rect_r(130, 146, 4, 30, "w")
    sh.rect_r(84, 104, 32, 16, "k", 2); sh.rect_r(84, 104, 32, 5, "-", 2)
    for x in (92, 100, 108): sh.rect_r(x - 1.5, 94, 3, 10, "rbg"[(x - 92) // 8]); sh.region(drop_path(x, 90, 1.8), "y")
    sh.region("M124 120L122 106H132L130 120Z", "o"); sh.region("M66 120L64 108H72L70 120Z", "t")
    # ballonnen aan het hek
    for x, y, c in ((10, 96, "r"), (24, 88, "y"), (176, 92, "m"), (190, 100, "b")):
        balloon(sh, x, y, 8, c, (x + (8 if x < 100 else -8), 124))
    # kinderen
    s = .66
    hy = person(sh, 34, 196 - 4 - 101 * s, "r", "n", hands=((18, 156), (52, 136)), style="curly", hair="x", s=s, cap=True, face=False)
    sh.region(f"M{f(34 - 11 * s)} {f(hy - 8 * s)}L{f(34 - 9 * s)} {f(hy - 22 * s)}L{f(34 - 3 * s)} {f(hy - 14 * s)}L34 {f(hy - 24 * s)}L{f(34 + 3 * s)} {f(hy - 14 * s)}L{f(34 + 9 * s)} {f(hy - 22 * s)}L{f(34 + 11 * s)} {f(hy - 8 * s)}Z", "y")
    face(sh, 34, hy, s)
    present(sh, 44, 136, 14, 12, "g", "y")
    s = .6
    hy = person(sh, 104, 196 - 4 - 101 * s, "y", "p", hands=((88, 168), (122, 150)), style="pony", hair="o", s=s, cap=True, face=False)
    party_hat(sh, 104, hy, s, "b", "r"); face(sh, 104, hy, s)
    s = .62
    hy = person(sh, 166, 196 - 4 - 101 * s, "t", "n", hands=((150, 162), (184, 132)), style="braids", hair="w", s=s, legs=((158, 178), (178, 172)), cap=True, face=False)
    party_hat(sh, 166, hy, s, "m", "y"); face(sh, 166, hy, s, "open")
    balloon(sh, 192, 112, 8, "g", (184, 132))


PLATES = [
    ("vuurwerk-boven-de-stad", "Vuurwerk boven de stad", "feest", "9+", 3, vuurwerk_stad, "oudnieuw"),
    ("aftellen-naar-nieuwjaar", "Aftellen naar het nieuwe jaar", "feest", "4-6", 2, aftellen, "oudnieuw"),
    ("dumplings-maken", "Dumplings maken voor Chinees Nieuwjaar", "feest", "6-9", 2, dumplings, "chinees"),
    ("drakendans", "Drakendans", "feest", "6-9", 3, drakendans, "chinees"),
    ("brievenbus-met-hartjes", "Brievenbus met hartjes", "feest", "2-4", 1, brievenbus, "valentijn"),
    ("verkleedkinderen-carnaval", "Verkleed voor carnaval", "feest", "4-6", 2, verkleedkinderen, "carnaval"),
    ("carnavalswagen", "Carnavalswagen in de optocht", "feest", "6-9", 2, optochtwagen, "carnaval"),
    ("holi-kleurpoeder", "Holi: spelen met kleurpoeder", "feest", "4-6", 2, holi, "holi"),
    ("suikerfeest-familiemaaltijd", "Suikerfeest: samen eten", "feest", "6-9", 3, suikerfeest_maaltijd, "suikerfeest"),
    ("offerfeest-op-bezoek", "Offerfeest: op bezoek bij opa", "feest", "4-6", 2, offerfeest_bezoek, "offerfeest"),
    ("paaseieren-zoeken", "Paaseieren zoeken", "feest", "4-6", 2, eieren_zoeken, "pasen"),
    ("zaklopen", "Zaklopen op Koningsdag", "sport", "4-6", 2, zaklopen, "koningsdag"),
    ("koekhappen", "Koekhappen", "feest", "2-4", 1, koekhappen, "koningsdag"),
    ("vlag-uithangen", "De vlag hangt uit", "feest", "4-6", 2, vlag_uithangen, "bevrijding"),
    ("ontbijt-op-bed", "Ontbijt op bed voor mama", "thuis", "4-6", 2, ontbijt_op_bed, "moederdag"),
    ("vliegeren-met-papa", "Vliegeren met papa", "feest", "4-6", 2, vaderdag_vliegeren, "vaderdag"),
    ("fietstocht-met-bloemen", "Fietstocht langs de bloemen", "natuur", "6-9", 3, fietstocht, "hemelvaart"),
    ("lammetje-aaien", "Een lammetje aaien", "boerderij", "2-4", 1, lammetjes, "pinksteren"),
    ("keti-koti-dansen", "Keti Koti: dansen en trommelen", "feest", "6-9", 3, keti_koti, "ketikoti"),
    ("eerste-schooldag", "De eerste schooldag", "leren", "2-4", 1, eerste_schooldag, "school"),
    ("dierendag-traktatie", "Een traktatie op Dierendag", "dieren", "2-4", 1, dierendag, "dierendag"),
    ("pompoenen-uithollen", "Pompoenen uithollen", "feest", "4-6", 2, pompoenen_uithollen, "halloween"),
    ("halloween-langs-de-deuren", "Verkleed langs de deuren", "feest", "6-9", 2, langs_de_deuren, "halloween"),
    ("rangoli-en-lichtjes", "Rangoli en lichtjes", "feest", "6-9", 3, rangoli, "divali"),
    ("sint-maarten-zingen", "Zingen aan de deur met Sint-Maarten", "feest", "4-6", 2, sint_maarten_deur, "sintmaarten"),
    ("schoen-zetten", "Je schoen zetten", "feest", "2-4", 1, schoen_zetten, "sinterklaas"),
    ("pakjesavond", "Pakjesavond", "feest", "6-9", 3, pakjesavond, "sinterklaas"),
    ("draaitol-spelen", "Draaitol spelen met Chanoeka", "feest", "4-6", 2, draaitol, "chanoeka"),
    ("kerstboom-versieren", "De kerstboom versieren", "feest", "4-6", 2, kerstboom_versieren, "kerst"),
    ("kerstmarkt", "Op de kerstmarkt", "feest", "9+", 3, kerstmarkt, "kerst"),
    ("cadeautje-uitpakken", "Een cadeautje uitpakken", "feest", "2-4", 1, cadeautje_uitpakken, "verjaardag"),
    ("verjaardagsfeest-in-de-tuin", "Verjaardagsfeestje in de tuin", "feest", "6-9", 2, tuinfeest, "verjaardag"),
]

if __name__ == "__main__":
    for slug, name, cat, age, diff, draw, hol in PLATES:
        kp(slug, name, cat, age, diff, draw, hol)
