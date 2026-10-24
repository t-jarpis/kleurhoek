"""Batch 11c: kaarten, decoraties en cadeautjes (eigen ontwerpen)."""
import math
from lib_gen import *
from lib_gen import C, E
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
from shapes import fish_path, heart_path, star_path, moon_path, drop_path, cloud_path, leaf_path

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
def party_hat(sh, x, y, w, hgt, code="r", tilt=0):
    rot(sh, tilt, x, y)
    sh.poly_r([(x - w / 2, y), (x + w / 2, y), (x, y - hgt)], code)
    sh.line(f"M{f(x - w * .3)} {f(y - hgt * .4)}L{f(x + w * .18)} {f(y - hgt * .1)}M{f(x - w * .12)} {f(y - hgt * .75)}L{f(x + w * .3)} {f(y - hgt * .45)}", "l", "stroke-width:1")
    sh.circle_r(x, y - hgt - 2.5, 3, "y")
    end(sh)
def cake(sh, cx, by, w=40, candles=3, codes="kmy"):
    sh.rect_r(cx - w / 2, by - 18, w, 18, codes[0], 2)
    sh.line(f"M{cx - w / 2} {by - 12}" + "".join(f"Q{cx - w / 2 + (k + .5) * w / 6} {by - 6 - (k % 2) * 0} {cx - w / 2 + (k + 1) * w / 6} {by - 12}" for k in range(6)), "l", "stroke-width:1")
    sh.rect_r(cx - w * .35, by - 32, w * .7, 14, codes[1], 2)
    sh.ellipse_r(cx, by + 1, w / 2 + 6, 3, "-")
    for k in range(candles):
        x = cx - w * .25 + k * (w * .5 / max(1, candles - 1)) if candles > 1 else cx
        sh.rect_r(x - 1.6, by - 42, 3.2, 10, codes[2])
        sh.region(drop_path(x, by - 46, 2), "o")

# =====================================================================
# 1. KAARTEN
# =====================================================================

def front_dino(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Rawr! Je bent jarig!", 13)
    gy = y0 + 116
    sh.seg(20, gy, 180, gy)
    # staart, lijf, nek en kop
    sh.region(f"M58 {gy - 36}Q34 {gy - 30} 20 {gy - 12}Q40 {gy - 16} 60 {gy - 20}Z", "g")
    for k in range(5):
        x = 62 + k * 10
        sh.poly_r([(x - 5, gy - 44 - (2 if k in (1, 2, 3) else 0)), (x + 5, gy - 44 - (2 if k in (1, 2, 3) else 0)), (x, gy - 55 - (3 if k in (1, 2, 3) else 0))], "o")
    for x in (64, 76, 96, 108):
        sh.rect_r(x - 5, gy - 22, 10, 22, "g", 3)
    sh.ellipse_r(86, gy - 30, 32, 19, "g")
    sh.ellipse_r(86, gy - 24, 20, 9, "l")
    sh.region(f"M102 {gy - 44}Q114 {gy - 48} 116 {gy - 52}H131Q128 {gy - 38} 114 {gy - 24}Z", "g")
    hy = gy - 56
    sh.ellipse_r(128, hy, 16, 11, "g")
    sh.dot(132, hy - 3, 2.4); sh.dot(142, hy, 1)
    sh.line(f"M131 {hy + 6}Q137 {hy + 10} 142 {hy + 5}", "l", "stroke-width:1.4")
    sh.circle_r(124, hy + 4, 2.6, "k")
    party_hat(sh, 124, hy - 9, 12, 16, "r", -14)
    # ballon aan de staart en taart
    balloon(sh, 34, y0 + 46, 9, "b", False)
    sh.line(f"M34 {y0 + 59}Q30 {y0 + 78} 26 {gy - 14}", "l", "stroke-width:1")
    cake(sh, 160, gy - 1, 34, 3, "kmy")
    confetti(sh, [(60, y0 + 40), (150, y0 + 40), (96, y0 + 46), (172, y0 + 56), (52, y0 + 62), (82, y0 + 58)])
card("verjaardagskaart-dino", "Verjaardagskaart met dino", front_dino, "Een brul van een verjaardag!", "dinos", "4-6",
     ["Schrijf binnenin voor wie de kaart is en hoe oud diegene wordt."], holiday="verjaardag")

def front_ruimte(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Jarig? Hoera!", 16)
    # planeet met ring
    sh.circle_r(46, y0 + 72, 18, "p")
    sh.line(f"M24 {y0 + 78}Q46 {y0 + 64} 68 {y0 + 66}", "l", "stroke-width:1.2")
    sh.region(f"M20 {y0 + 82}Q14 {y0 + 74} 30 {y0 + 68}L32 {y0 + 72}Q24 {y0 + 76} 26 {y0 + 79}Q40 {y0 + 82} 62 {y0 + 72}L64 {y0 + 64}Q74 {y0 + 60} 74 {y0 + 64}Q76 {y0 + 74} 46 {y0 + 84}Q26 {y0 + 90} 20 {y0 + 82}Z", "y")
    sh.circle_r(36, y0 + 64, 3, "k"); sh.circle_r(52, y0 + 82, 2, "k")
    # raket schuin omhoog
    rot(sh, 35, 118, y0 + 76)
    cx, cy = 118, y0 + 76
    sh.region(f"M{cx - 10} {cy + 22}L{cx - 22} {cy + 36}V{cy + 22}L{cx - 10} {cy + 6}Z", "r")
    sh.region(f"M{cx + 10} {cy + 22}L{cx + 22} {cy + 36}V{cy + 22}L{cx + 10} {cy + 6}Z", "r")
    sh.region(f"M{cx - 6} {cy + 28}Q{cx} {cy + 48} {cx + 6} {cy + 28}Z", "o")
    sh.region(f"M{cx} {cy - 34}Q{cx + 16} {cy - 18} {cx + 12} {cy + 28}H{cx - 12}Q{cx - 16} {cy - 18} {cx} {cy - 34}Z", "-")
    sh.region(f"M{cx - 9} {cy - 18}Q{cx} {cy - 28} {cx + 9} {cy - 18}Q{cx} {cy - 22} {cx - 9} {cy - 18}Z", "r")
    sh.circle_r(cx, cy - 2, 6.5, "b")
    sh.rect_r(cx - 12, cy + 20, 24, 8, "z", 1)
    end(sh)
    # sterren en kleine planeet
    stars(sh, [(150, y0 + 42), (172, y0 + 78), (28, y0 + 40), (84, y0 + 44), (164, y0 + 108), (80, y0 + 108)], 5)
    sh.circle_r(164, y0 + 52, 8, "t"); sh.circle_line(161, y0 + 50, 2.2, "l", "stroke-width:1")
    for x, y in [(60, y0 + 100), (100, y0 + 112), (176, y0 + 36), (140, y0 + 112)]: sh.dot(x, y, 1.3)
card("verjaardagskaart-ruimte", "Verjaardagskaart: raket in de ruimte", front_ruimte, "Een verjaardag om nooit te vergeten!", "ruimte", "4-6",
     ["Schrijf binnenin een wens die net zo ver gaat als de sterren."], holiday="verjaardag")

def front_zeemeermin(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Hiep hiep hoera!", 16)
    gy = y0 + 118
    sh.line(f"M18 {gy - 2}Q30 {gy - 8} 42 {gy - 2}T66 {gy - 2}M146 {gy - 2}Q158 {gy - 8} 170 {gy - 2}T182 {gy - 3}", "l", "stroke-width:1.4")
    # rots
    sh.region(f"M70 {gy}Q72 {gy - 24} 102 {gy - 26}Q134 {gy - 26} 142 {gy}Z", "z")
    sh.line(f"M84 {gy - 8}Q90 {gy - 14} 98 {gy - 12}M120 {gy - 6}Q126 {gy - 12} 132 {gy - 10}", "l", "stroke-width:1")
    # staart over de rots, vin rechts omhoog
    sh.region(f"M93 {gy - 40}Q89 {gy - 22} 112 {gy - 20}Q132 {gy - 18} 146 {gy - 28}L162 {gy - 30}Q154 {gy - 38} 154 {gy - 52}Q146 {gy - 44} 142 {gy - 37}Q128 {gy - 31} 113 {gy - 31}Q106 {gy - 32} 108 {gy - 40}Z", "t")
    for k in range(3):
        x = 100 + k * 12
        sh.line(f"M{x} {gy - 29 + k * .5}Q{x + 5} {gy - 24} {x + 10} {gy - 29 + k * .5}", "l", "stroke-width:.9")
    sh.line(f"M146 {gy - 30}L152 {gy - 42}M146 {gy - 30}L156 {gy - 33}", "l", "stroke-width:.9")
    # haar achter het hoofd, lang over de rug
    sh.region(f"M111 {gy - 72}Q112 {gy - 86} 101 {gy - 86}Q88 {gy - 86} 89 {gy - 72}Q88 {gy - 58} 82 {gy - 46}Q92 {gy - 46} 96 {gy - 56}Q98 {gy - 62} 104 {gy - 62}Q110 {gy - 64} 111 {gy - 72}Z", "o")
    # lijf
    sh.region(f"M95 {gy - 40}Q93 {gy - 54} 96 {gy - 63}H106Q109 {gy - 54} 107 {gy - 40}Z", "k")
    sh.region(f"M95.5 {gy - 57}Q98 {gy - 60} 101 {gy - 57}Q104 {gy - 60} 106.5 {gy - 57}L106.8 {gy - 53}H95.2Z", "p")
    # hoofd
    sh.circle_r(101, gy - 72, 9, "k")
    sh.region(f"M92 {gy - 73}Q93 {gy - 83} 101 {gy - 82}Q109 {gy - 83} 110 {gy - 73}Q104 {gy - 78} 92 {gy - 73}Z", "o")
    sh.dot(97.5, gy - 71, 1.4); sh.dot(104.5, gy - 71, 1.4)
    sh.line(f"M98 {gy - 67}Q101 {gy - 64.5} 104 {gy - 67}", "l", "stroke-width:1")
    sh.poly_r(star_pts(108, gy - 82, 4.5, 2), "y")
    # arm met cadeautje
    sh.region(f"M105 {gy - 60}Q112 {gy - 56} 116 {gy - 60}L118 {gy - 56}Q111 {gy - 50} 104 {gy - 54}Z", "k")
    sh.rect_r(114, gy - 70, 14, 12, "r", 1); sh.rect_r(119.5, gy - 70, 3, 12, "y")
    sh.region(f"M121 {gy - 70}Q115 {gy - 78} 114 {gy - 72}ZM121 {gy - 70}Q127 {gy - 78} 128 {gy - 72}Z", "y")
    # bubbels, visjes en schelp
    for x, y, r in [(136, y0 + 50, 3), (142, y0 + 40, 2), (66, y0 + 52, 2.6), (60, y0 + 42, 1.8)]: sh.circle_line(x, y, r, "l", "stroke-width:1")
    from shapes import fish_path
    sh.region(fish_path(42, y0 + 80, 11), "y"); sh.dot(36, y0 + 78, 1.3)
    sh.region(fish_path(164, y0 + 46, 9), "m"); sh.dot(159, y0 + 44, 1.2)
    sx, sy = 166, gy - 8
    sh.region(f"M{sx - 11} {sy + 4}Q{sx - 11} {sy - 11} {sx} {sy - 11}Q{sx + 11} {sy - 11} {sx + 11} {sy + 4}Z", "k")
    for k in (-6, 0, 6): sh.seg(sx, sy + 4, sx + k * 1.3, sy - 9, "l", "stroke-width:1")
    sh.poly_r(star_pts(34, gy - 10, 8, 3.8), "o")
card("verjaardagskaart-zeemeermin", "Verjaardagskaart met zeemeermin", front_zeemeermin, "Een zee vol wensen voor jou!", "sprookjes", "4-6",
     ["Schrijf binnenin voor wie de kaart is."], holiday="verjaardag")

def front_voetbal(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Goal! Je bent jarig!", 13)
    gy = y0 + 116
    sh.region(f"M18 {gy - 8}Q100 {gy - 16} 182 {gy - 8}V{gy}H18Z", "l")
    # doel
    gx0, gx1, gt = 96, 176, y0 + 50
    sh.region(f"M{gx0} {gy - 10}V{gt}H{gx1}V{gy - 10}H{gx1 - 4}V{gt + 4}H{gx0 + 4}V{gy - 10}Z", "-")
    for k in range(1, 8):
        x = gx0 + 4 + k * (gx1 - gx0 - 8) / 8
        sh.seg(x, gt + 4, x, gy - 11, "l", "stroke-width:.6")
    for k in range(1, 6):
        y = gt + 4 + k * (gy - 14 - gt) / 6
        sh.seg(gx0 + 4, y, gx1 - 4, y, "l", "stroke-width:.6")
    # bal vliegt het doel in
    bx, by, r = 132, y0 + 76, 13
    sh.circle_r(bx, by, r, "-")
    pent = [(bx + 5.5 * math.sin(math.radians(72 * k)), by - 5.5 * math.cos(math.radians(72 * k))) for k in range(5)]
    sh.poly_r(pent, "x")
    for x, y in pent:
        dx, dy = x - bx, y - by; d = math.hypot(dx, dy)
        sh.seg(x, y, bx + dx / d * r, by + dy / d * r, "l", "stroke-width:1")
    for k in range(3):
        sh.line(f"M{bx - 18 - k * 2} {by - 8 + k * 8}Q{bx - 34} {by - 10 + k * 9} {bx - 48 + k * 4} {by - 6 + k * 7}", "l", "stroke-width:1.1")
    # vlaggetjes en confetti
    sh.line(f"M18 {y0 + 36}Q50 {y0 + 46} 86 {y0 + 36}", "l", "stroke-width:1")
    for i in range(4):
        x = 26 + i * 16; yy = y0 + 38 + 5 * math.sin(math.pi * (x - 18) / 68)
        sh.poly_r([(x - 6, yy), (x + 6, yy), (x, yy + 11)], "ryb"[i % 3])
    # beker
    tx, ty = 52, gy - 12
    sh.rect_r(tx - 12, ty - 6, 24, 6, "w", 1)
    sh.rect_r(tx - 3, ty - 16, 6, 10, "y")
    sh.region(f"M{tx - 14} {ty - 42}H{tx + 14}Q{tx + 14} {ty - 18} {tx} {ty - 16}Q{tx - 14} {ty - 18} {tx - 14} {ty - 42}Z", "y")
    sh.line(f"M{tx - 14} {ty - 38}Q{tx - 24} {ty - 36} {tx - 13} {ty - 26}M{tx + 14} {ty - 38}Q{tx + 24} {ty - 36} {tx + 13} {ty - 26}", "l", "stroke-width:1.6")
    sh.poly_r(star_pts(tx, ty - 31, 5, 2.2), "o")
card("verjaardagskaart-voetbal", "Verjaardagskaart: goal!", front_voetbal, "Gefeliciteerd, kampioen!", "sport", "6-9",
     ["Schrijf binnenin voor wie de kaart is en hoe oud diegene wordt."], holiday="verjaardag")

def front_eenhoorn(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Een magische dag!", 14)
    cx, cy = 92, y0 + 78
    # manen achter
    sh.region(f"M{cx + 10} {cy - 30}Q{cx + 34} {cy - 30} {cx + 34} {cy - 6}Q{cx + 46} {cy + 6} {cx + 36} {cy + 22}Q{cx + 40} {cy + 36} {cx + 24} {cy + 42}Q{cx + 20} {cy + 20} {cx + 12} {cy + 4}Z", "p")
    sh.region(f"M{cx + 12} {cy - 22}Q{cx + 26} {cy - 18} {cx + 26} {cy - 2}Q{cx + 34} {cy + 10} {cx + 26} {cy + 22}Q{cx + 22} {cy + 10} {cx + 14} {cy + 2}Z", "m")
    # hals en hoofd
    sh.region(f"M{cx - 2} {cy - 4}Q{cx + 6} {cy + 22} {cx + 2} {cy + 40}H{cx + 26}Q{cx + 20} {cy + 18} {cx + 16} {cy - 14}Z", "-")
    sh.region(f"M{cx + 14} {cy - 24}Q{cx - 4} {cy - 30} {cx - 18} {cy - 12}Q{cx - 30} {cy + 2} {cx - 26} {cy + 10}Q{cx - 20} {cy + 18} {cx - 8} {cy + 12}Q{cx + 6} {cy + 6} {cx + 16} {cy - 4}Q{cx + 22} {cy - 16} {cx + 14} {cy - 24}Z", "-")
    sh.dot(cx - 20, cy + 6, 1.3)
    sh.line(f"M{cx - 4} {cy - 10}Q{cx + 1} {cy - 6} {cx + 6} {cy - 10}", "l", "stroke-width:1.4")
    sh.circle_r(cx - 6, cy + 2, 3, "k")
    # oor en hoorn
    sh.poly_r([(cx + 6, cy - 24), (cx + 12, cy - 38), (cx + 14, cy - 22)], "-")
    sh.poly_r([(cx - 4, cy - 26), (cx + 4, cy - 27), (cx - 6, cy - 50)], "y")
    sh.line(f"M{cx - 3} {cy - 32}L{cx + 2} {cy - 33}M{cx - 4} {cy - 38}L{cx} {cy - 39}M{cx - 5} {cy - 44}L{cx - 2} {cy - 45}", "l", "stroke-width:.9")
    # pony
    sh.region(f"M{cx + 4} {cy - 26}Q{cx - 8} {cy - 26} {cx - 6} {cy - 16}Q{cx + 2} {cy - 22} {cx + 8} {cy - 18}Z", "b")
    # regenboog en wolkjes
    for i, c in enumerate("roy"):
        r = 26 - i * 6
        r = 22 - i * 5
        sh.region(f"M{40 - r} {y0 + 112}A{r} {r} 0 0 1 {40 + r} {y0 + 112}H{40 + r - 5}A{r - 5} {r - 5} 0 0 0 {40 - r + 5} {y0 + 112}Z", c)
    sh.region(cloud_path(40, y0 + 110, 10), "-")
    stars(sh, [(150, y0 + 44), (164, y0 + 72), (146, y0 + 100), (36, y0 + 46), (60, y0 + 56)], 5)
    for x, y in [(170, y0 + 104), (128, y0 + 42), (176, y0 + 46)]: sh.region(heart_path(x, y, 5), "m")
card("verjaardagskaart-eenhoorn", "Verjaardagskaart met eenhoorn", front_eenhoorn, "Fijne verjaardag, vol toverkracht!", "sprookjes", "4-6",
     ["Schrijf binnenin voor wie de kaart is en een toverwens."], holiday="verjaardag")

def front_ooievaar(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Welkom, kleine baby!", 13)
    # wolkjes
    sh.region(cloud_path(40, y0 + 108, 14), "-"); sh.region(cloud_path(164, y0 + 50, 11), "-")
    cx, cy = 96, y0 + 66
    # vleugel achter
    sh.region(f"M{cx - 4} {cy - 4}Q{cx + 10} {cy - 34} {cx + 40} {cy - 38}Q{cx + 30} {cy - 20} {cx + 18} {cy - 2}Z", "-")
    sh.line(f"M{cx + 40} {cy - 38}L{cx + 34} {cy - 26}M{cx + 32} {cy - 34}L{cx + 28} {cy - 22}", "l", "stroke-width:1")
    # lijf
    sh.region(f"M{cx - 30} {cy - 2}Q{cx - 10} {cy - 14} {cx + 14} {cy - 6}Q{cx + 36} {cy} {cx + 50} {cy + 8}Q{cx + 30} {cy + 14} {cx + 10} {cy + 10}Q{cx - 16} {cy + 10} {cx - 30} {cy - 2}Z", "-")
    sh.region(f"M{cx + 50} {cy + 8}L{cx + 64} {cy + 4}L{cx + 62} {cy + 12}L{cx + 48} {cy + 12}Z", "x")
    # nek en kop
    sh.region(f"M{cx - 26} {cy - 4}Q{cx - 36} {cy - 14} {cx - 40} {cy - 22}L{cx - 32} {cy - 26}Q{cx - 26} {cy - 14} {cx - 16} {cy - 8}Z", "-")
    sh.circle_r(cx - 38, cy - 28, 7, "-")
    sh.dot(cx - 39, cy - 30, 1.4)
    sh.poly_r([(cx - 44, cy - 30), (cx - 66, cy - 22), (cx - 43, cy - 25)], "o")
    # poten naar achteren
    sh.line(f"M{cx + 30} {cy + 12}L{cx + 54} {cy + 22}M{cx + 24} {cy + 12}L{cx + 50} {cy + 26}", "l", "stroke-width:1.4")
    # vleugel voor
    sh.region(f"M{cx - 6} {cy}Q{cx + 4} {cy + 26} {cx + 34} {cy + 34}Q{cx + 30} {cy + 16} {cx + 18} {cy + 2}Z", "-")
    sh.line(f"M{cx + 34} {cy + 34}L{cx + 26} {cy + 24}M{cx + 24} {cy + 30}L{cx + 18} {cy + 20}", "l", "stroke-width:1")
    # doek met baby aan de snavel
    bx, by = cx - 56, cy + 2
    sh.line(f"M{cx - 56} {cy - 24}L{bx - 8} {by}M{cx - 56} {cy - 24}L{bx + 8} {by}", "l", "stroke-width:1.2")
    sh.region(f"M{bx - 12} {by}Q{bx - 16} {by + 26} {bx} {by + 28}Q{bx + 16} {by + 26} {bx + 12} {by}Q{bx} {by + 6} {bx - 12} {by}Z", "b")
    sh.circle_r(bx, by + 8, 6, "k")
    sh.line(f"M{bx - 3} {by + 7}Q{bx - 2} {by + 8} {bx - 1} {by + 7}M{bx + 1} {by + 7}Q{bx + 2} {by + 8} {bx + 3} {by + 7}", "l", "stroke-width:.8")
    sh.region(heart_path(bx, by + 19, 4), "m")
    stars(sh, [(150, y0 + 104), (176, y0 + 82), (124, y0 + 112), (176, y0 + 112), (140, y0 + 40)], 4.5)
card("geboortekaart-ooievaar", "Kaart voor een nieuwe baby: ooievaar", front_ooievaar, "Gefeliciteerd met jullie baby!", "dieren", "6-9",
     ["Schrijf binnenin de naam van de baby en een lieve wens voor het nieuwe gezin."])

def front_sterkte(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Heel veel sterkte", 14)
    sh.text(100, y0 + 34, "Ik denk aan je.", 7)
    cx = 100
    # regen links, zon rechts
    for x in (26, 38, 50, 32, 44):
        y = y0 + 50 + (x % 3) * 8
        sh.region(drop_path(x, y, 2.6), "b")
    sh.region(cloud_path(40, y0 + 46, 12), "z")
    sh.circle_r(164, y0 + 52, 10, "y")
    for k in range(8):
        a = math.radians(k * 45)
        sh.seg(164 + 13 * math.cos(a), y0 + 52 + 13 * math.sin(a), 164 + 18 * math.cos(a), y0 + 52 + 18 * math.sin(a), "l", "stroke-width:1.2")
    # paraplu met twee figuurtjes eronder
    top = y0 + 52
    sh.region(f"M{cx - 40} {top + 24}Q{cx - 38} {top - 4} {cx} {top - 6}Q{cx + 38} {top - 4} {cx + 40} {top + 24}Q{cx + 33} {top + 18} {cx + 27} {top + 24}Q{cx + 20} {top + 18} {cx + 13} {top + 24}Q{cx + 6} {top + 18} {cx} {top + 24}Q{cx - 6} {top + 18} {cx - 13} {top + 24}Q{cx - 20} {top + 18} {cx - 27} {top + 24}Q{cx - 33} {top + 18} {cx - 40} {top + 24}Z", "r")
    sh.line(f"M{cx} {top - 6}Q{cx - 8} {top + 6} {cx - 13} {top + 24}M{cx} {top - 6}Q{cx + 8} {top + 6} {cx + 13} {top + 24}M{cx} {top - 6}Q{cx - 22} {top} {cx - 27} {top + 24}M{cx} {top - 6}Q{cx + 22} {top} {cx + 27} {top + 24}", "l", "stroke-width:1")
    sh.seg(cx, top - 6, cx, top - 11, "l", "stroke-width:1.6")
    sh.line(f"M{cx} {top + 24}V{top + 52}Q{cx} {top + 57} {cx + 4} {top + 56}", "l", "stroke-width:1.6")
    gy = y0 + 118
    for px, c, hgt in [(cx - 18, "t", 1.0), (cx + 18, "y", .86)]:
        hy = gy - 54 * hgt
        sh.circle_r(px, hy, 8 * hgt, "k")
        sh.dot(px - 3 * hgt, hy - 1, 1.1); sh.dot(px + 3 * hgt, hy - 1, 1.1)
        sh.line(f"M{px - 2.5 * hgt} {hy + 3}Q{px} {hy + 5} {px + 2.5 * hgt} {hy + 3}", "l", "stroke-width:.9")
        sh.region(f"M{px - 9 * hgt} {gy - 12}L{px - 6 * hgt} {hy + 9 * hgt}H{px + 6 * hgt}L{px + 9 * hgt} {gy - 12}Z", c)
        sh.rect_r(px - 6 * hgt, gy - 12, 4.5 * hgt, 12, "n"); sh.rect_r(px + 1.5 * hgt, gy - 12, 4.5 * hgt, 12, "n")
    sh.region(heart_path(cx, gy - 30, 6), "m")
    sh.seg(20, gy, 180, gy)
card("sterktekaart-paraplu", "Sterktekaart: samen onder de paraplu", front_sterkte, "Je staat er niet alleen voor.", "feest", "6-9",
     ["Schrijf binnenin een lief berichtje of teken iets om iemand een hart onder de riem te steken.",
      "Een sterktekaart stuur je als iemand het moeilijk heeft, bijvoorbeeld als iemand verdrietig of ziek is."])

def front_opa_oma(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Hoera voor opa of oma!", 12)
    gy = y0 + 116
    # tafel met grote taart
    sh.rect_r(30, gy - 8, 140, 6, "w", 2)
    sh.seg(42, gy - 2, 42, gy + 2, "l", "stroke-width:2"); sh.seg(158, gy - 2, 158, gy + 2, "l", "stroke-width:2")
    cx = 100
    sh.rect_r(cx - 34, gy - 32, 68, 24, "k", 3)
    sh.rect_r(cx - 24, gy - 48, 48, 16, "m", 3)
    for k in range(5):
        x = cx - 16 + k * 8
        sh.rect_r(x - 1.5, gy - 57, 3, 9, "byrlp"[k])
        sh.region(drop_path(x, gy - 60, 1.8), "o")
    sh.circle_r(cx, gy - 19, 10, "-")
    sh.text(cx, gy - 13.5, "jaar", 4.5)
    sh.line(f"M{cx - 34} {gy - 26}" + "".join(f"Q{cx - 34 + (k + .5) * 68 / 8} {gy - 21} {cx - 34 + (k + 1) * 68 / 8} {gy - 26}" for k in range(8)), "l", "stroke-width:1")
    # theepot links, cadeau rechts, bloemen in vaas
    tx, ty = 48, gy - 8
    sh.region(f"M{tx - 12} {ty}Q{tx - 16} {ty - 18} {tx} {ty - 20}Q{tx + 16} {ty - 18} {tx + 12} {ty}Z", "b")
    sh.region(f"M{tx + 13} {ty - 12}L{tx + 22} {ty - 20}L{tx + 23} {ty - 17}L{tx + 12} {ty - 5}Z", "b")
    sh.line(f"M{tx - 13} {ty - 14}Q{tx - 22} {ty - 12} {tx - 13} {ty - 5}", "l", "stroke-width:1.6")
    sh.ellipse_r(tx, ty - 21, 6, 2, "b"); sh.circle_r(tx, ty - 24, 2, "y")
    sh.rect_r(140, gy - 26, 22, 18, "g", 1); sh.rect_r(149, gy - 26, 4, 18, "y")
    sh.region(f"M151 {gy - 26}Q143 {gy - 36} 141 {gy - 28}ZM151 {gy - 26}Q159 {gy - 36} 161 {gy - 28}Z", "y")
    # slinger
    sh.line(f"M18 {y0 + 34}Q100 {y0 + 46} 182 {y0 + 34}", "l", "stroke-width:1")
    for i in range(8):
        x = 28 + i * 20.5; t = (x - 18) / 164; yy = (1 - t) ** 2 * (y0 + 34) + 2 * t * (1 - t) * (y0 + 46) + t * t * (y0 + 34)
        sh.poly_r([(x - 6, yy - .5), (x + 6, yy + .5), (x, yy + 11)], "rybglm"[i % 6])
    sh.text(cx, gy - 74 + 0, "", 6)
card("verjaardagskaart-opa-oma", "Verjaardagskaart voor opa of oma", front_opa_oma, "Fijne verjaardag! Ik vier het graag met je mee.", "feest", "4-6",
     ["Schrijf in het rondje op de taart hoe oud opa of oma wordt.", "Schrijf of teken binnenin iets wat jullie samen graag doen."], holiday="verjaardag")

def front_juf(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Fijne verjaardag!", 15)
    sh.text(100, y0 + 33, "voor de liefste juf of meester", 6.5)
    # schoolbord
    bx, by, bw, bh = 50, y0 + 42, 100, 58
    sh.rect_r(bx - 5, by - 5, bw + 10, bh + 10, "w", 3)
    sh.rect_r(bx, by, bw, bh, "g", 2)
    sh.raw(f'<text class="l" style="stroke-width:.9" x="100" y="{f(by + 26)}" font-size="16" text-anchor="middle" font-weight="800">Hoera!</text>')
    sh.text(100, by + 40, "Lieve juf of meester:", 5.6)
    sh.seg(68, by + 50, 132, by + 50, "guide")
    sh.rect_r(bx + 6, by + bh + 5, bw - 12, 4, "w", 1)
    sh.rect_r(bx + 14, by + bh + 1, 10, 4, "-", 1); sh.rect_r(bx + 28, by + bh + 1, 8, 4, "y", 1)
    sh.seg(bx + 20, by + bh + 9, bx + 14, y0 + 120, "l", "stroke-width:1.6"); sh.seg(bx + bw - 20, by + bh + 9, bx + bw - 14, y0 + 120, "l", "stroke-width:1.6")
    # appel links, potloden rechts
    ax, ay = 30, y0 + 100
    sh.region(f"M{ax} {ay - 8}C{ax - 10} {ay - 14} {ax - 15} {ay - 2} {ax - 12} {ay + 6}C{ax - 9} {ay + 14} {ax - 2} {ay + 14} {ax} {ay + 11}C{ax + 2} {ay + 14} {ax + 9} {ay + 14} {ax + 12} {ay + 6}C{ax + 15} {ay - 2} {ax + 10} {ay - 14} {ax} {ay - 8}Z", "r")
    sh.line(f"M{ax} {ay - 8}Q{ax} {ay - 14} {ax + 3} {ay - 17}", "l", "stroke-width:1.4")
    sh.region(f"M{ax + 2} {ay - 13}Q{ax + 10} {ay - 20} {ax + 14} {ay - 14}Q{ax + 8} {ay - 9} {ax + 2} {ay - 13}Z", "g")
    for i, c in enumerate("byr"):
        px = 164 + i * 6; top = y0 + 78 + i * 4
        sh.rect_r(px - 2.6, top, 5.2, 30 - i * 4, c)
        sh.poly_r([(px - 2.6, top), (px + 2.6, top), (px, top - 6)], "w")
        sh.poly_r([(px - .9, top - 3.6), (px + .9, top - 3.6), (px, top - 6)], "x")
    sh.rect_r(159, y0 + 102, 22, 16, "o", 2)
    stars(sh, [(30, y0 + 50), (170, y0 + 52), (34, y0 + 72)], 4.5)
card("verjaardagskaart-juf-meester", "Verjaardagskaart voor de juf of meester", front_juf, "Gefeliciteerd! Fijn dat je mijn juf of meester bent.", "feest", "4-6",
     ["Schrijf de naam van je juf of meester op het schoolbord.", "Neem de kaart mee naar school op de verjaardag (of op de juffen- en meestersdag)."], holiday="verjaardag")

def front_pleisterbeer(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Beterschap!", 18)
    cx, cy = 100, y0 + 70
    def pleister(x, y, deg, L=24):
        rot(sh, deg, x, y)
        sh.rect_r(x - L / 2, y - 4, L, 8, "y", 3.5); sh.rect_r(x - 4, y - 4, 8, 8, "o", 1)
        for dx in (-1.5, 1.5):
            for dy in (-1.5, 1.5): sh.dot(x + dx, y + dy, .5)
        end(sh)
    # kussen en hoofd
    sh.rect_r(cx - 46, cy - 22, 92, 40, "b", 10)
    for x, y in [(cx - 38, cy - 12), (cx + 38, cy - 12), (cx - 38, cy + 8), (cx + 38, cy + 8)]: sh.dot(x, y, 1.4)
    for s in (-1, 1):
        sh.circle_r(cx + s * 22, cy - 24, 8, "w"); sh.circle_r(cx + s * 22, cy - 24, 4, "k")
    sh.circle_r(cx, cy - 4, 26, "w")
    sh.ellipse_r(cx, cy + 8, 10, 7, "k")
    sh.ellipse_r(cx, cy + 4, 4, 3, "x")
    sh.line(f"M{cx} {cy + 7}V{cy + 9}M{cx - 4} {cy + 10}Q{cx} {cy + 13} {cx + 4} {cy + 10}", "l", "stroke-width:1.2")
    sh.dot(cx - 10, cy - 6, 2.4); sh.dot(cx + 10, cy - 6, 2.4)
    sh.circle_r(cx - 17, cy + 4, 3.2, "m"); sh.circle_r(cx + 17, cy + 4, 3.2, "m")
    pleister(cx + 11, cy - 19, 35, 18); pleister(cx + 11, cy - 19, -55, 18)
    # deken met pootjes erop
    by = cy + 20
    sh.region(f"M{cx - 56} {y0 + 118}V{by + 4}Q{cx} {by - 6} {cx + 56} {by + 4}V{y0 + 118}Z", "t")
    sh.line(f"M{cx - 56} {by + 12}Q{cx} {by + 2} {cx + 56} {by + 12}", "l", "stroke-width:1")
    for k in range(5):
        x = cx - 40 + k * 20
        sh.region(heart_path(x, by + 18 + (k % 2) * 3, 3.6), "m")
    sh.ellipse_r(cx - 20, by + 2, 9, 6.5, "w"); sh.ellipse_r(cx + 20, by + 2, 9, 6.5, "w")
    # kop thee en hartjes
    tx, ty = 170, y0 + 112
    sh.region(f"M{tx - 10} {ty - 16}H{tx + 8}V{ty - 6}Q{tx + 8} {ty + 1} {tx - 1} {ty + 1}Q{tx - 10} {ty + 1} {tx - 10} {ty - 6}Z", "y")
    sh.line(f"M{tx + 8} {ty - 13}Q{tx + 14} {ty - 12} {tx + 8} {ty - 6}", "l", "stroke-width:1.3")
    sh.line(f"M{tx - 4} {ty - 20}Q{tx - 7} {ty - 24} {tx - 4} {ty - 28}M{tx + 2} {ty - 20}Q{tx - 1} {ty - 24} {tx + 2} {ty - 28}", "l", "stroke-width:1")
    for x, y in [(30, y0 + 48), (168, y0 + 48), (30, y0 + 98), (26, y0 + 74), (172, y0 + 74)]: sh.region(heart_path(x, y, 6), "r")
card("beterschapskaart-pleisterbeer", "Beterschapskaart met pleisterbeer", front_pleisterbeer, "Word maar gauw weer helemaal beter!", "feest", "4-6",
     ["Schrijf binnenin een lief berichtje en geef of stuur de kaart aan iemand die ziek is."])

def front_nieuwjaar(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Gelukkig nieuwjaar!", 14)
    cx, cy, r = 100, y0 + 74, 32
    # klok die bijna twaalf uur slaat
    sh.rect_r(cx - 6, cy - r - 9, 12, 6, "z", 2)
    sh.region(f"M{cx - 24} {cy - r - 2}Q{cx - 34} {cy - r - 8} {cx - 30} {cy - r + 4}Z", "y"); sh.region(f"M{cx + 24} {cy - r - 2}Q{cx + 34} {cy - r - 8} {cx + 30} {cy - r + 4}Z", "y")
    sh.circle_r(cx, cy, r, "y")
    sh.circle_r(cx, cy, r - 6, "-")
    for k in range(12):
        a = math.radians(k * 30 - 90)
        r1 = r - 9 if k % 3 == 0 else r - 8
        sh.seg(cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a), "l", "stroke-width:1.4" if k % 3 == 0 else "stroke-width:.9")
    sh.text(cx, cy - r + 17, "12", 6)
    sh.seg(cx, cy, cx, cy - 18, "l", "stroke-width:1.8")
    a = math.radians(-93)
    sh.seg(cx, cy, cx + 12 * math.cos(a), cy + 12 * math.sin(a), "l", "stroke-width:2.4")
    sh.circle_r(cx, cy, 2.2, "x")
    sh.rect_r(cx - 22, cy + r - 2, 8, 6, "z", 2); sh.rect_r(cx + 14, cy + r - 2, 8, 6, "z", 2)
    # pieptoeters, ballonnen en confetti
    for x, s in [(36, 1), (164, -1)]:
        yy = y0 + 104
        rot(sh, -25 * s, x, yy)
        sh.poly_r([(x - 16 * s, yy - 2), (x + 10 * s, yy - 7), (x + 10 * s, yy + 7), (x - 16 * s, yy + 2)], "p" if s > 0 else "t")
        sh.line(f"M{x + 10 * s} {yy}Q{x + 18 * s} {yy - 10} {x + 22 * s} {yy - 2}", "l", "stroke-width:1")
        end(sh)
    balloon(sh, 34, y0 + 56, 10, "r"); balloon(sh, 166, y0 + 58, 10, "b")
    confetti(sh, [(56, y0 + 42), (146, y0 + 42), (60, y0 + 84), (142, y0 + 86), (58, y0 + 112), (140, y0 + 114), (76, y0 + 116), (124, y0 + 116), (178, y0 + 92), (22, y0 + 88)])
card("nieuwjaarskaart-klok", "Nieuwjaarskaart: bijna twaalf uur!", front_nieuwjaar, "Ik wens je een heel fijn nieuw jaar!", "feest", "6-9",
     ["Schrijf binnenin je wens voor het nieuwe jaar, of een goed voornemen."], holiday="oudnieuw")

def front_pinksteren(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Fijne Pinksteren!", 15)
    gy = y0 + 116
    sh.region(f"M18 {gy - 10}Q100 {gy - 22} 182 {gy - 10}V{gy}H18Z", "l")
    def duif(x, y, flip=False):
        if flip: sh.raw(f'<g transform="translate({2 * x} 0) scale(-1 1)">')
        sh.poly_r([(x - 10, y + 1), (x - 22, y - 4), (x - 23, y + 9), (x - 10, y + 6)], "-")
        sh.region(f"M{x - 13} {y + 3}Q{x - 2} {y - 8} {x + 10} {y - 4}Q{x + 13} {y + 7} {x} {y + 8}Q{x - 8} {y + 8} {x - 13} {y + 3}Z", "-")
        sh.region(f"M{x - 4} {y - 1}Q{x - 10} {y - 18} {x + 4} {y - 24}Q{x + 2} {y - 12} {x + 7} {y - 3}Z", "-")
        sh.line(f"M{x - 4} {y - 12}L{x + 2} {y - 9}M{x - 2} {y - 18}L{x + 3} {y - 15}", "l", "stroke-width:.8")
        sh.circle_r(x + 11, y - 6, 5, "-")
        sh.poly_r([(x + 15.5, y - 7.5), (x + 20, y - 5.5), (x + 15.5, y - 4)], "o")
        sh.dot(x + 12, y - 7, 1)
        if flip: end(sh)
    duif(60, y0 + 56); duif(140, y0 + 50, True)
    for i, (x, c) in enumerate([(34, "m"), (62, "y"), (90, "p"), (118, "r"), (146, "o"), (170, "b")]):
        top = gy - 30 - (i % 2) * 8
        sh.line(f"M{x} {gy - 10}V{top}", "l", "stroke-width:1.4")
        sh.raw(f'<g transform="rotate({-30 if i % 2 else 30} {x} {gy - 16})">'); sh.region(leaf_path(x + (5 if i % 2 == 0 else -5), gy - 16, 3, 6), "g"); sh.raw("</g>")
        if i % 3 == 0:
            sh.region(f"M{x - 7} {top}V{top - 10}L{x - 3.5} {top - 6}L{x} {top - 11}L{x + 3.5} {top - 6}L{x + 7} {top - 10}V{top}Q{x} {top + 6} {x - 7} {top}Z", c)
        else:
            flower(sh, x, top - 3, 5, c)
    sh.circle_r(30, y0 + 44, 8, "y")
    for x, y in [(100, y0 + 40), (172, y0 + 70), (108, y0 + 64)]:
        sh.line(f"M{x - 4} {y}Q{x - 2} {y - 3} {x} {y}Q{x + 2} {y - 3} {x + 4} {y}", "l", "stroke-width:1")
card("pinksterkaart-lente", "Pinksterkaart: lente vol bloemen", front_pinksteren, "Fijne Pinksterdagen!", "feest", "4-6",
     ["Schrijf binnenin een wens of teken wat jij met Pinksteren gaat doen."], holiday="pinksteren")

def front_carnaval(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Fijn carnaval!", 16)
    cx, cy = 100, y0 + 74
    # stokje
    sh.line(f"M{cx + 30} {cy + 10}L{cx + 54} {cy + 44}", "l", "stroke-width:2.6")
    # veren
    for k, (dx, c) in enumerate([(-30, "t"), (-14, "p"), (14, "m"), (30, "y")]):
        rot(sh, dx * 1.1, cx + dx * .5, cy - 16)
        sh.region(f"M{cx + dx * .5} {cy - 14}Q{cx + dx * .5 - 9} {cy - 34} {cx + dx * .5} {cy - 50}Q{cx + dx * .5 + 9} {cy - 34} {cx + dx * .5} {cy - 14}Z", c)
        sh.seg(cx + dx * .5, cy - 16, cx + dx * .5, cy - 44, "l", "stroke-width:.8")
        end(sh)
    # masker
    sh.region(f"M{cx - 44} {cy - 14}Q{cx - 24} {cy - 22} {cx} {cy - 12}Q{cx + 24} {cy - 22} {cx + 44} {cy - 14}Q{cx + 46} {cy + 8} {cx + 28} {cy + 16}Q{cx + 12} {cy + 18} {cx + 4} {cy + 6}Q{cx} {cy + 2} {cx - 4} {cy + 6}Q{cx - 12} {cy + 18} {cx - 28} {cy + 16}Q{cx - 46} {cy + 8} {cx - 44} {cy - 14}Z", "r")
    for s in (-1, 1):
        sh.region(f"M{cx + s * 32} {cy - 2}Q{cx + s * 22} {cy - 12} {cx + s * 10} {cy - 4}Q{cx + s * 20} {cy + 8} {cx + s * 32} {cy - 2}Z", "-")
    sh.region(heart_path(cx, cy - 7, 5), "y")
    for s in (-1, 1):
        for k in range(3): sh.circle_r(cx + s * (16 + k * 10), cy + 10 - k * 2 + (2 if k == 2 else 0), 1.8, "y")
    # slingers, serpentines en confetti
    for x, y, c in [(30, y0 + 56, "g")]:
        sh.line(f"M{x - 10} {y - 14}Q{x + 10} {y - 10} {x} {y}T{x} {y + 14}T{x + 6} {y + 26}", "l", "stroke-width:1.4")
    stars(sh, [(150, y0 + 46), (40, y0 + 106), (172, y0 + 64)], 5)
    confetti(sh, [(60, y0 + 40), (140, y0 + 38), (70, y0 + 110), (124, y0 + 112), (26, y0 + 84), (54, y0 + 96), (150, y0 + 108), (96, y0 + 112)])
card("carnavalskaart-masker", "Carnavalskaart met masker", front_carnaval, "Veel plezier met verkleden!", "feest", "6-9",
     ["Kleur het masker zo bont als je wilt.", "Schrijf binnenin als wat jij je gaat verkleden."], holiday="carnaval")

def front_chinees(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Gelukkig nieuwjaar!", 14)
    sh.text(100, y0 + 33, "Fijn Chinees Nieuwjaar", 6.5)
    # tak met bloesem bovenin
    sh.line(f"M18 {y0 + 50}Q50 {y0 + 46} 70 {y0 + 54}Q86 {y0 + 60} 104 {y0 + 54}", "l", "stroke-width:2")
    sh.line(f"M50 {y0 + 48}Q56 {y0 + 42} 64 {y0 + 43}", "l", "stroke-width:1.4")
    for x, y in [(34, y0 + 47), (65, y0 + 43), (86, y0 + 58), (103, y0 + 52)]:
        flower(sh, x, y, 3.2, "k", "y")
    # drie ronde lantaarns
    def lantaarn(x, top, s, c):
        sh.seg(x, top - 10 * s, x, top, "l", "stroke-width:1.2")
        sh.rect_r(x - 7 * s, top, 14 * s, 4 * s, "y", 1)
        sh.ellipse_r(x, top + 18 * s, 18 * s, 15 * s, c)
        sh.line(f"M{x} {top + 4 * s}Q{x - 9 * s} {top + 18 * s} {x} {top + 32 * s}M{x} {top + 4 * s}Q{x + 9 * s} {top + 18 * s} {x} {top + 32 * s}", "l", "stroke-width:1")
        sh.rect_r(x - 7 * s, top + 31 * s, 14 * s, 4 * s, "y", 1)
        for k in (-4, -1.5, 1, 3.5):
            sh.seg(x + k * s, top + 35 * s, x + k * s * 1.2, top + 46 * s, "l", "stroke-width:1")
    sh.line(f"M112 {y0 + 40}Q146 {y0 + 50} 184 {y0 + 40}", "l", "stroke-width:1.2")
    lantaarn(132, y0 + 52, 1.0, "r"); lantaarn(166, y0 + 48, .8, "r")
    lantaarn(48, y0 + 68, .9, "o")
    # mandarijnen op een schaal
    sh.ellipse_r(110, y0 + 112, 26, 5, "b")
    for x, y in [(98, y0 + 103), (122, y0 + 103), (110, y0 + 96)]:
        sh.circle_r(x, y, 8, "o"); sh.region(leaf_path(x + 3, y - 9, 2.4, 3.5), "g")
    confetti(sh, [(30, y0 + 102), (150, y0 + 108), (178, y0 + 96), (80, y0 + 108)])
card("chinees-nieuwjaarskaart-lantaarns", "Kaart voor Chinees Nieuwjaar met lantaarns", front_chinees, "Een gelukkig en gezond nieuw jaar!", "wereld", "6-9",
     ["Chinees Nieuwjaar (het Lentefeest) valt elk jaar op een andere dag in januari of februari.",
      "Rood en goud zijn feestkleuren: kleur de lantaarns rood en de randjes geel.", "Schrijf binnenin een wens voor het nieuwe jaar."], holiday="chinees")

def splash(cx, cy, r, n, seed):
    import random
    rnd = random.Random(seed)
    d = ""
    pts = []
    for k in range(n * 2):
        a = math.radians(k * 180 / n + rnd.uniform(-6, 6))
        rr = r * (1.0 if k % 2 == 0 else .62) * rnd.uniform(.85, 1.1)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    m0 = mid(pts[-1], pts[0])
    d = f"M{f(m0[0])} {f(m0[1])}"
    for i in range(len(pts)):
        p = pts[i]; m = mid(p, pts[(i + 1) % len(pts)])
        d += f"Q{f(p[0])} {f(p[1])} {f(m[0])} {f(m[1])}"
    return d + "Z"
def front_holi(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Fijne Holi!", 18)
    sh.text(100, y0 + 33, "het feest van de kleuren", 6.5)
    spl = [(42, y0 + 60, 18, "m"), (100, y0 + 66, 22, "y"), (158, y0 + 58, 18, "t"), (64, y0 + 100, 16, "l"), (138, y0 + 102, 17, "p"), (100, y0 + 108, 10, "o")]
    for i, (x, y, r, c) in enumerate(spl):
        sh.region(splash(x, y, r, 7, i + 3), c)
    for x, y, r, c in [(22, y0 + 82, 3, "m"), (178, y0 + 84, 3, "t"), (78, y0 + 44, 2.4, "y"), (124, y0 + 42, 2.6, "y"), (100, y0 + 90, 2.4, "o"), (24, y0 + 42, 2.6, "p"), (176, y0 + 40, 2.6, "l")]:
        sh.circle_r(x, y, r, c)
    # kleine poederschaaltjes
    for x, c in [(32, "r"), (168, "b")]:
        yy = y0 + 108
        sh.region(f"M{x - 10} {yy}H{x + 10}Q{x + 8} {yy + 9} {x} {yy + 9}Q{x - 8} {yy + 9} {x - 10} {yy}Z", "w")
        sh.region(f"M{x - 8} {yy}Q{x} {yy - 8} {x + 8} {yy}Z", c)
card("holikaart-kleurspatten", "Holikaart met kleurspatten", front_holi, "Een kleurrijk feest gewenst!", "wereld", "4-6",
     ["Met Holi gooien mensen in India en over de hele wereld met gekleurd poeder en vieren ze de lente.",
      "Kleur elke spat in een andere felle kleur. Je mag ook stiften of verf gebruiken.", "Schrijf binnenin een kleurrijke wens."], holiday="holi")

def front_offer(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Fijn Offerfeest!", 15)
    sh.text(100, y0 + 33, "Eid Mubarak", 6.5)
    gy = y0 + 116
    sh.region(f"M18 {gy - 8}Q100 {gy - 16} 182 {gy - 8}V{gy}H18Z", "l")
    # maan en sterren
    sh.region(moon_path(160, y0 + 58, 15), "y")
    stars(sh, [(136, y0 + 44), (172, y0 + 86), (30, y0 + 46), (60, y0 + 40)], 4.5)
    # schaapje (vriendelijk, staand)
    sx, sy = 70, gy - 34
    sh.rect_r(sx - 16, sy + 8, 6, 18, "x", 2); sh.rect_r(sx - 4, sy + 8, 6, 18, "x", 2); sh.rect_r(sx + 8, sy + 8, 6, 18, "x", 2)
    wool = [(sx - 22, sy + 6), (sx - 26, sy - 4), (sx - 18, sy - 14), (sx - 6, sy - 18), (sx + 8, sy - 16), (sx + 18, sy - 8), (sx + 20, sy + 4), (sx + 10, sy + 12), (sx - 4, sy + 13), (sx - 16, sy + 12)]
    d = f"M{wool[-1][0]} {wool[-1][1]}" + "".join(f"A7 7 0 0 1 {x} {y}" for x, y in wool) + "Z"
    sh.region(d, "-")
    sh.ellipse_r(sx + 22, sy - 8, 9, 11, "x")
    sh.ellipse_r(sx + 14, sy - 14, 6, 3, "x")
    sh.circle_r(sx + 24, sy - 11, 2.2, "-"); sh.dot(sx + 24.6, sy - 11, 1.1)
    # cadeautjes en een schaal met eten om te delen
    sh.rect_r(112, gy - 30, 22, 18, "r", 1); sh.rect_r(121, gy - 30, 4, 18, "y")
    sh.region(f"M123 {gy - 30}Q115 {gy - 40} 113 {gy - 32}ZM123 {gy - 30}Q131 {gy - 40} 133 {gy - 32}Z", "y")
    sh.ellipse_r(160, gy - 14, 20, 5, "t")
    for x in (150, 160, 170): sh.ellipse_r(x, gy - 21, 5.5, 4, "w")
card("offerfeestkaart-schaapje", "Offerfeestkaart met schaapje en maan", front_offer, "Een gezegend feest met familie en vrienden!", "feest", "4-6",
     ["Met het Offerfeest delen moslims eten met familie, buren en mensen die het minder goed hebben.", "Schrijf binnenin een wens voor het feest."], holiday="offerfeest")

def front_gereedschap(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Papa, jij kunt alles!", 13)
    gy = y0 + 116
    # gereedschapskist
    sh.rect_r(52, gy - 40, 96, 40, "r", 3)
    sh.rect_r(52, gy - 40, 96, 10, "o", 2)
    sh.region(f"M86 {gy - 40}V{gy - 50}Q86 {gy - 54} 90 {gy - 54}H110Q114 {gy - 54} 114 {gy - 50}V{gy - 40}H109V{gy - 48}H91V{gy - 40}Z", "z")
    sh.rect_r(94, gy - 26, 12, 8, "z", 1)
    sh.raw(f'<text class="l" style="stroke-width:.8" x="100" y="{f(gy - 6)}" font-size="9" text-anchor="middle" font-weight="800">TOP</text>')
    # hamer uit de kist
    rot(sh, -30, 68, gy - 46)
    sh.rect_r(65, gy - 72, 6, 30, "w", 2); sh.rect_r(58, gy - 80, 20, 9, "z", 2)
    end(sh)
    # sleutel
    rot(sh, 28, 132, gy - 52)
    sh.region(f"M129 {gy - 36}V{gy - 64}A9 9 0 1 1 135 {gy - 64}V{gy - 36}Q132 {gy - 33} 129 {gy - 36}Z", "z")
    sh.rect_r(129.5, gy - 77, 5, 9, "-")
    end(sh)
    # schroevendraaier
    rot(sh, -8, 100, gy - 60)
    sh.rect_r(96, gy - 72, 8, 18, "y", 3); sh.rect_r(98.8, gy - 86, 2.4, 14, "z")
    end(sh)
    # duimstok en schroefjes
    sh.rect_r(22, gy - 8, 54, 8, "y", 1)
    for k in range(1, 9): sh.seg(22 + k * 6, gy - 8, 22 + k * 6, gy - 4, "l", "stroke-width:.8")
    for x, y in [(160, gy - 6), (172, gy - 4), (166, gy - 14)]:
        sh.circle_r(x, y, 3, "z"); sh.seg(x - 2, y, x + 2, y, "l", "stroke-width:.8")
    sh.seg(18, gy, 182, gy)
    for x, y in [(30, y0 + 50), (170, y0 + 48)]: sh.region(heart_path(x, y, 7), "r")
    stars(sh, [(40, y0 + 76), (160, y0 + 80)], 5)
card("vaderdagkaart-gereedschap", "Vaderdagkaart met gereedschapskist", front_gereedschap, "Fijne vaderdag! Je bent top!", "feest", "6-9",
     ["Schrijf binnenin wat jullie samen gemaakt of gerepareerd hebben, of wat je nog eens samen wilt doen."], holiday="vaderdag")

def front_buren(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 22, "Dank je wel, buren!", 14)
    gy = y0 + 116
    sh.seg(18, gy, 182, gy)
    for hx, c, dc in [(56, "y", "g"), (144, "b", "r")]:
        sh.poly_r([(hx - 34, gy - 50), (hx, gy - 80), (hx + 34, gy - 50)], "r" if c == "y" else "w")
        sh.rect_r(hx - 28, gy - 50, 56, 50, c)
        sh.rect_r(hx - 8, gy - 26, 16, 26, dc, 2); sh.dot(hx + 4, gy - 13, 1.3)
        sh.rect_r(hx - 23, gy - 44, 12, 12, "-", 1); sh.rect_r(hx + 11, gy - 44, 12, 12, "-", 1)
        sh.seg(hx - 17, gy - 44, hx - 17, gy - 32, "l", "stroke-width:.8"); sh.seg(hx + 17, gy - 44, hx + 17, gy - 32, "l", "stroke-width:.8")
        sh.rect_r(hx - 24, gy - 31, 14, 3, "w", 1); sh.rect_r(hx + 10, gy - 31, 14, 3, "w", 1)
        sh.circle_r(hx - 17, gy - 34, 2, "m"); sh.circle_r(hx + 17, gy - 34, 2, "o")
    # hartjeslijn tussen de huizen
    sh.line(f"M84 {gy - 40}Q100 {gy - 56} 116 {gy - 40}", "l", "stroke-width:1;stroke-dasharray:2 2.5")
    sh.region(heart_path(100, gy - 62, 9), "r")
    # heg en bloemetjes
    sh.region(f"M86 {gy}V{gy - 12}Q90 {gy - 18} 95 {gy - 12}Q100 {gy - 18} 105 {gy - 12}Q110 {gy - 18} 114 {gy - 12}V{gy}Z", "g")
    for x in (30, 170):
        flower(sh, x, gy - 10, 3, "p")
    sh.circle_r(170, y0 + 44, 7, "y")
card("bedankkaart-buren", "Bedankkaart voor de buren", front_buren, "Fijn dat jullie onze buren zijn!", "thuis", "4-6",
     ["Schrijf binnenin waarvoor je de buren wilt bedanken, bijvoorbeeld voor het water geven van de plantjes of het oppassen.",
      "Doe de kaart samen in de brievenbus bij de buren."])


# =====================================================================
# 2. DECORATIES EN CADEAUTJES
# =====================================================================

def ring_d(coords):
    c = list(coords)[:-1]
    return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in c) + "Z"
def geom_d(g):
    gs = list(g.geoms) if hasattr(g, "geoms") else [g]
    return "".join(ring_d(p.exterior.coords) + "".join(ring_d(i.coords) for i in p.interiors) for p in gs)
def region_holes(sh, g, code):
    sh.raw(f'<path class="r" fill-rule="evenodd" d="{geom_d(g)}"/>', code)
KNIP = [{"slug": "kleurpotloden"}, SCHAAR]
def hole(sh, x, y, r=2.2):
    sh.circle_line(x, y, r, "cut", "stroke-dasharray:1.6 1.2")

# ---------- paasslinger ----------
def paasslinger():
    sh = Sheet()
    title(sh, "Paasslinger", 14)
    sh.text(100, 25, "Knip de vlaggen uit en hang ze aan een touw.", 5.5)
    def kuiken_ei(cx, cy):
        sh.circle_r(cx, cy - 8, 11, "y")
        sh.region(f"M{cx - 9.5} {cy - 13}L{cx - 6} {cy - 22}L{cx - 2} {cy - 16}L{cx + 2} {cy - 23}L{cx + 6} {cy - 16}L{cx + 9.5} {cy - 13}Q{cx} {cy - 17} {cx - 9.5} {cy - 13}Z", "-")
        sh.dot(cx - 4, cy - 8, 1.5); sh.dot(cx + 4, cy - 8, 1.5)
        sh.poly_r([(cx - 3, cy - 4), (cx + 3, cy - 4), (cx, cy - 1)], "o")
        zz = "".join(f"L{f(cx - 16 + (k + 1) * 32 / 8)} {f(cy + (0 if k % 2 == 0 else 6))}" for k in range(8))
        sh.region(f"M{cx - 16} {cy + 4}" + zz.replace(f"L{f(cx + 16)} {f(cy + 6)}", f"L{f(cx + 16)} {f(cy + 4)}") + f"A16 18 0 0 1 {cx - 16} {cy + 4}Z", "-")
    def ei(cx, cy):
        sh.ellipse_r(cx, cy + 2, 15, 20, "b")
        sh.line(f"M{cx - 14} {cy - 4}" + "".join(f"L{f(cx - 14 + (k + 1) * 28 / 6)} {cy - 4 + (-4 if k % 2 == 0 else 0)}" for k in range(6)), "l", "stroke-width:1.2")
        sh.line(f"M{cx - 14} {cy + 10}Q{cx - 7} {cy + 5} {cx} {cy + 10}T{cx + 14} {cy + 10}", "l", "stroke-width:1.2")
        for dx in (-7, 0, 7): sh.circle_r(cx + dx, cy + 3.5, 2, "y")
        sh.region(heart_path(cx, cy - 13, 4), "m")
    def haas(cx, cy):
        for s in (-1, 1):
            rot(sh, s * 12, cx + s * 6, cy - 6)
            sh.ellipse_r(cx + s * 6, cy - 16, 5, 13, "-"); sh.ellipse_r(cx + s * 6, cy - 15, 2.4, 9, "k")
            end(sh)
        sh.circle_r(cx, cy + 6, 13, "-")
        sh.dot(cx - 5, cy + 3, 1.6); sh.dot(cx + 5, cy + 3, 1.6)
        sh.poly_r([(cx - 2, cy + 8), (cx + 2, cy + 8), (cx, cy + 10)], "k")
        sh.line(f"M{cx} {cy + 10}V{cy + 12}M{cx - 4} {cy + 13}Q{cx} {cy + 15} {cx + 4} {cy + 13}", "l", "stroke-width:1")
        sh.line(f"M{cx - 4} {cy + 10}L{cx - 14} {cy + 8}M{cx - 4} {cy + 11}L{cx - 14} {cy + 13}M{cx + 4} {cy + 10}L{cx + 14} {cy + 8}M{cx + 4} {cy + 11}L{cx + 14} {cy + 13}", "l", "stroke-width:.7")
    def tulp(cx, cy):
        sh.line(f"M{cx} {cy - 4}V{cy + 22}", "l", "stroke-width:1.6")
        sh.region(f"M{cx} {cy + 20}Q{cx - 14} {cy + 14} {cx - 14} {cy + 2}Q{cx - 4} {cy + 8} {cx} {cy + 20}Z", "g")
        sh.region(f"M{cx} {cy + 16}Q{cx + 14} {cy + 10} {cx + 14} {cy - 2}Q{cx + 4} {cy + 4} {cx} {cy + 16}Z", "g")
        sh.region(f"M{cx - 10} {cy - 20}L{cx - 5} {cy - 13}L{cx} {cy - 22}L{cx + 5} {cy - 13}L{cx + 10} {cy - 20}V{cy - 8}Q{cx + 10} {cy - 1} {cx} {cy - 1}Q{cx - 10} {cy - 1} {cx - 10} {cy - 8}Z", "r")
    def nest(cx, cy):
        for dx, dy, c in [(-9, 0, "k"), (9, 0, "t"), (0, -4, "y")]:
            sh.ellipse_r(cx + dx, cy + dy, 7, 9.5, c)
        sh.region(f"M{cx - 20} {cy + 2}Q{cx} {cy + 8} {cx + 20} {cy + 2}Q{cx + 18} {cy + 20} {cx} {cy + 20}Q{cx - 18} {cy + 20} {cx - 20} {cy + 2}Z", "w")
        sh.line(f"M{cx - 16} {cy + 9}Q{cx} {cy + 15} {cx + 16} {cy + 9}M{cx - 12} {cy + 15}Q{cx} {cy + 19} {cx + 12} {cy + 15}", "l", "stroke-width:.9")
    def kuiken(cx, cy):
        sh.line(f"M{cx - 4} {cy + 14}V{cy + 20}L{cx - 8} {cy + 22}M{cx - 4} {cy + 20}L{cx} {cy + 22}M{cx + 4} {cy + 14}V{cy + 20}L{cx} {cy + 22}M{cx + 4} {cy + 20}L{cx + 8} {cy + 22}", "l", "stroke-width:1.2")
        sh.ellipse_r(cx, cy + 4, 14, 12, "y")
        sh.circle_r(cx + 4, cy - 12, 9, "y")
        sh.region(f"M{cx + 2} {cy - 21}Q{cx} {cy - 26} {cx + 4} {cy - 26}Q{cx + 4} {cy - 23} {cx + 5} {cy - 21}Z", "y")
        sh.dot(cx + 7, cy - 13, 1.5)
        sh.poly_r([(cx + 12, cy - 12), (cx + 17, cy - 10), (cx + 12, cy - 8)], "o")
        sh.region(f"M{cx - 10} {cy + 2}Q{cx - 2} {cy - 4} {cx + 4} {cy + 4}Q{cx - 2} {cy + 10} {cx - 10} {cy + 2}Z", "y")
    pics = [kuiken_ei, ei, haas, tulp, nest, kuiken]
    for i, pic in enumerate(pics):
        col, row = i % 3, i // 3
        x, y, w = 13 + col * 60, 32 + row * 122, 54
        flap = 12; b = y + flap
        shape = f"M{x} {b}H{x + w}V{b + 60}L{x + w / 2} {b + 100}L{x} {b + 60}Z"
        sh.line(f"M{x} {y}H{x + w}V{b + 60}L{x + w / 2} {b + 100}L{x} {b + 60}Z", "cut")
        sh.seg(x, b, x + w, b, "fold")
        sh.raw(f'<rect class="glue" x="{x + 2}" y="{y + 2}" width="{w - 4}" height="{flap - 4}"/>')
        sh.region(shape, "kbylmt"[i])
        sh.circle_r(x + w / 2, b + 38, 24, "-")
        pic(x + w / 2, b + 38)
        for k in range(3): sh.circle_r(x + w / 2 - 8 + k * 8, b + 72, 2, "my"[k % 2] if k != 1 else "o")
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "paasslinger-kuikens-en-eieren", sh, {"category": "feest", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 25, "holiday": "pasen",
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "touw"}],
        "i18n": {"nl": {"name": "Paasslinger met kuikens en eieren", "steps": [
            "Kleur de vlaggen en de plaatjes in.",
            "Knip de vlaggen uit langs de streepjeslijn.",
            "Leg een touw langs de stippellijnen, smeer lijm op de grijze randjes en vouw ze over het touw.",
            "Print het vel twee keer als je een lange slinger wilt. Hang hem op bij het raam of boven de paastafel."]}}})
paasslinger()

# ---------- raamhangers ----------
def raamhangers():
    sh = Sheet()
    title(sh, "Raamhangers: ster en maan", 14)
    sh.text(100, 25, "Knip de rand en de vensters uit en plak er doorschijnend papier achter.", 5.2)
    # ster
    cx, cy = 100, 100
    outer = Polygon(star_pts(cx, cy, 68, 31))
    inner = Polygon(star_pts(cx, cy + 3, 45, 19))
    win2 = Point(cx, cy + 3).buffer(8)
    frame = outer.difference(inner)
    region_holes(sh, frame, "y")
    sh.line(geom_d(outer), "cut"); sh.line(geom_d(inner), "cut")
    for k in range(5):
        a = math.radians(k * 72)
        x, y = cx + 56 * math.sin(a), cy - 56 * math.cos(a)
        if k == 0: continue
        sh.circle_r(x, y, 2.4, "o")
    hole(sh, cx, cy - 54, 2.6)
    assert outer.contains(Point(cx, cy - 54).buffer(4.5)) and not inner.intersects(Point(cx, cy - 54).buffer(4.5))
    # maan (sikkel) met drie sterrenvensters
    mcx, mcy, R = 96, 222, 46
    moon = Point(mcx, mcy).buffer(R, 64).difference(Point(mcx + 22, mcy - 13).buffer(38.6, 64))
    wins = [Polygon(star_pts(x, y, 8, 3.6)) for x, y in [(mcx - 31, mcy - 4), (mcx - 20, mcy + 21), (mcx + 4, mcy + 34)]]
    holed = moon
    for wpoly in wins: holed = holed.difference(wpoly)
    region_holes(sh, holed, "b")
    sh.line(geom_d(moon), "cut")
    for wpoly in wins: sh.line(geom_d(wpoly), "cut")
    # ophanggat zo hoog mogelijk boven het zwaartepunt (de dikke kant), zodat de maan bijna rechtop hangt
    cxm = moon.centroid.x
    hx, hy = min(((x, y) for y in range(mcy - R, mcy + R) for x in range(int(cxm) - 24, int(cxm) + 1) if moon.contains(Point(x, y).buffer(6))), key=lambda q: q[1] + .4 * abs(q[0] - cxm))
    assert moon.contains(Point(hx, hy).buffer(6)), "ophanggat valt buiten de maan"
    hole(sh, hx, hy, 2.6)
    # klein extra sterretje
    sx, sy = 168, 196
    sh.poly_r(star_pts(sx, sy, 16, 7), "y"); sh.line(P(star_pts(sx, sy, 16, 7)), "cut")
    hole(sh, sx, sy - 7, 2)
    sh.legend(["cut"], 276)
    write(OUT, "raamhangers-ster-en-maan", sh, {"category": "ruimte", "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 30, "adultHelp": True, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "touw"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Raamhangers: ster en maan met vensters", "printNote": "Op stevig papier (160 gram) blijven de raamhangers mooi plat.", "steps": [
            "Kleur de rand van de ster en de maan in.",
            "Knip de vormen uit langs de buitenste streepjeslijn.",
            "Laat een volwassene helpen met de vensters: prik een gaatje in het midden, knip naar de lijn en knip het venster eruit.",
            "Plak aan de achterkant een stukje doorschijnend papier (vliegerpapier, bakpapier of een stukje plastic zakje) over de vensters.",
            "Prik het ophanggaatje door, rijg er een touwtje door en hang ze voor het raam. Als de zon schijnt, gloeien ze op!"]}}})
raamhangers()

# ---------- deurhanger slapen / wakker ----------
def deurhanger_slaap():
    sh = Sheet()
    title(sh, "Deurhanger: slaap of wakker", 14)
    for i in range(2):
        x, y, w, h = 18 + i * 88, 28, 76, 236
        wave = "".join(f"Q{f(x + w - (k + .5) * w / 4)} {y + h + (6 if k % 2 == 0 else -2)} {f(x + w - (k + 1) * w / 4)} {y + h}" for k in range(4))
        outline = f"M{x} {y + 10}Q{x} {y} {x + 10} {y}H{x + w - 10}Q{x + w} {y} {x + w} {y + 10}V{y + h}{wave}Z"
        sh.region(outline, "n" if i == 0 else "b")
        sh.line(outline, "cut")
        sh.raw(f'<circle class="cut" cx="{x + w / 2}" cy="{y + 30}" r="19"/>')
        sh.seg(x + w / 2, y + 49, x + w / 2, y + 62, "cut")
        cx = x + w / 2
        if i == 0:
            sh.region(moon_path(cx - 4, y + 104, 26), "y")
            sh.line(f"M{cx - 20} {y + 102}Q{cx - 16} {y + 106} {cx - 12} {y + 102}", "l", "stroke-width:1.2")
            sh.text(cx + 18, y + 86, "z", 9); sh.text(cx + 25, y + 76, "z", 7); sh.text(cx + 30, y + 68, "z", 5.5)
            sh.rect_r(x + 6, y + 144, w - 12, 24, "-", 4)
            sh.text(cx, y + 154, "Ik slaap,", 8); sh.text(cx, y + 164, "sst!", 8)
            stars(sh, [(x + 14, y + 74), (x + w - 12, y + 126), (x + 16, y + 186), (x + w - 16, y + 194), (cx, y + 212), (x + 14, y + 130)], 5)
        else:
            sh.circle_r(cx, y + 104, 18, "y")
            for k in range(12):
                a = math.radians(k * 30)
                sh.seg(cx + 22 * math.cos(a), y + 104 + 22 * math.sin(a), cx + 29 * math.cos(a), y + 104 + 29 * math.sin(a), "l", "stroke-width:1.6")
            sh.dot(cx - 6, y + 101, 2); sh.dot(cx + 6, y + 101, 2)
            sh.line(f"M{cx - 7} {y + 108}Q{cx} {y + 115} {cx + 7} {y + 108}", "l", "stroke-width:1.4")
            sh.rect_r(x + 6, y + 144, w - 12, 24, "-", 4)
            sh.text(cx, y + 154, "Ik ben", 8); sh.text(cx, y + 164, "wakker!", 8)
            sh.region(cloud_path(x + 20, y + 196, 9), "-"); sh.region(cloud_path(x + w - 20, y + 210, 8), "-")
            balloon(sh, cx, y + 186, 7, "r")
        sh.text(cx, y + 226, "", 6)
    sh.legend(["cut"], 276)
    write(OUT, "deurhanger-slaap-of-wakker", sh, {"category": "thuis", "age": "6-9", "kind": "kaart", "difficulty": 2, "minutes": 25, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": "Deurhanger: ik slaap of ik ben wakker", "printNote": "Op stevig papier (160 gram) blijft hij mooi hangen.", "steps": [
            "Kleur beide kanten in: de nachtkant donker met een gele maan, de dagkant licht met een zon.",
            "Knip ze uit langs de streepjeslijn, ook het rondje bovenin en het sneetje eronder.",
            "Plak ze met de achterkanten precies op elkaar, zodat de rondjes over elkaar vallen.",
            "Schuif het rondje over de deurklink. 's Avonds draai je hem naar de maan, 's ochtends naar de zon."]}}})
deurhanger_slaap()

# ---------- boomhangers met winterdieren ----------
def boomhangers():
    sh = Sheet()
    title(sh, "Boomhangers: dieren in de winter", 14)
    def schulp(cx, cy, R):
        n = 180
        return P([(cx + (R + 2.2 * math.cos(14 * 2 * math.pi * k / n)) * math.sin(2 * math.pi * k / n), cy - (R + 2.2 * math.cos(14 * 2 * math.pi * k / n)) * math.cos(2 * math.pi * k / n)) for k in range(n)])
    def muts(x, y, w, c="r", tilt=0):
        rot(sh, tilt, x, y)
        sh.region(f"M{x - w / 2} {y}Q{x - w / 2} {y - w * .8} {x + w * .1} {y - w * .9}Q{x + w * .5} {y - w * .9} {x + w * .7} {y - w * .5}Q{x + w * .4} {y - w * .6} {x + w / 2} {y}Z", c)
        sh.rect_r(x - w / 2 - 1, y - 2.5, w + 2, 5, "-", 2.5)
        sh.circle_r(x + w * .72, y - w * .48, 3, "-")
        end(sh)
    def pinguin(cx, cy):
        sh.ellipse_r(cx - 6, cy + 18, 5, 2.5, "o"); sh.ellipse_r(cx + 6, cy + 18, 5, 2.5, "o")
        sh.ellipse_r(cx, cy + 2, 14, 17, "n")
        sh.ellipse_r(cx, cy + 5, 9.5, 12.5, "-")
        sh.region(f"M{cx - 14} {cy}Q{cx - 22} {cy + 8} {cx - 18} {cy + 14}Q{cx - 14} {cy + 8} {cx - 12} {cy + 4}Z", "n")
        sh.region(f"M{cx + 14} {cy}Q{cx + 22} {cy + 8} {cx + 18} {cy + 14}Q{cx + 14} {cy + 8} {cx + 12} {cy + 4}Z", "n")
        sh.dot(cx - 4, cy - 6, 1.5); sh.dot(cx + 4, cy - 6, 1.5)
        sh.poly_r([(cx - 3, cy - 3), (cx + 3, cy - 3), (cx, cy + 1)], "o")
        sh.region(f"M{cx - 11} {cy + 3}Q{cx} {cy + 8} {cx + 11} {cy + 3}V{cy + 7}Q{cx} {cy + 12} {cx - 11} {cy + 7}Z", "r")
        sh.rect_r(cx + 4, cy + 7, 4, 9, "r", 1)
    def ijsbeer(cx, cy):
        sh.circle_r(cx - 13, cy - 8, 5, "-"); sh.circle_r(cx + 13, cy - 8, 5, "-")
        sh.circle_r(cx, cy + 4, 17, "-")
        sh.ellipse_r(cx, cy + 11, 8, 6, "-")
        sh.ellipse_r(cx, cy + 8, 3, 2.2, "x")
        sh.line(f"M{cx} {cy + 10}V{cy + 12}M{cx - 3} {cy + 13}Q{cx} {cy + 15} {cx + 3} {cy + 13}", "l", "stroke-width:1")
        sh.dot(cx - 6, cy + 1, 1.6); sh.dot(cx + 6, cy + 1, 1.6)
        muts(cx - 1, cy - 9, 22, "t", -6)
    def uil(cx, cy):
        sh.line(f"M{cx - 22} {cy + 20}H{cx + 22}", "l", "stroke-width:2.2")
        sh.region(f"M{cx - 14} {cy - 14}L{cx - 12} {cy - 22}L{cx - 6} {cy - 16}H{cx + 6}L{cx + 12} {cy - 22}L{cx + 14} {cy - 14}Q{cx + 18} {cy + 4} {cx + 12} {cy + 18}H{cx - 12}Q{cx - 18} {cy + 4} {cx - 14} {cy - 14}Z", "w")
        sh.ellipse_r(cx, cy + 8, 8, 9, "y")
        for s in (-1, 1):
            sh.circle_r(cx + s * 6, cy - 7, 6, "-"); sh.dot(cx + s * 6, cy - 7, 2)
        sh.poly_r([(cx - 2, cy - 2), (cx + 2, cy - 2), (cx, cy + 2)], "o")
        for dx in (-3, 0, 3): sh.line(f"M{cx + dx - 2} {cy + 7}Q{cx + dx} {cy + 9} {cx + dx + 2} {cy + 7}", "l", "stroke-width:.8")
        sh.line(f"M{cx - 6} {cy + 18}V{cy + 21}M{cx + 6} {cy + 18}V{cy + 21}", "l", "stroke-width:1.4")
    def vos(cx, cy):
        sh.region(f"M{cx - 18} {cy - 16}L{cx - 8} {cy - 8}H{cx + 8}L{cx + 18} {cy - 16}L{cx + 18} {cy + 2}L{cx} {cy + 18}L{cx - 18} {cy + 2}Z", "o")
        sh.poly_r([(cx - 15, cy - 11), (cx - 10, cy - 7), (cx - 15, cy - 4)], "x")
        sh.poly_r([(cx + 15, cy - 11), (cx + 10, cy - 7), (cx + 15, cy - 4)], "x")
        sh.region(f"M{cx - 18} {cy + 2}Q{cx - 8} {cy + 2} {cx} {cy + 10}Q{cx + 8} {cy + 2} {cx + 18} {cy + 2}L{cx} {cy + 18}Z", "-")
        sh.ellipse_r(cx, cy + 15, 3, 2.4, "x")
        sh.dot(cx - 7, cy - 2, 1.7); sh.dot(cx + 7, cy - 2, 1.7)
        sh.region(f"M{cx - 14} {cy + 18}Q{cx} {cy + 26} {cx + 14} {cy + 18}V{cy + 23}Q{cx} {cy + 31} {cx - 14} {cy + 23}Z", "g")
    def egel(cx, cy):
        pts = []
        for i in range(17):
            a = math.radians(180 + i * 180 / 16); r = 22 if i % 2 == 0 else 16
            pts.append((cx - 2 + r * math.cos(a), cy + 14 + r * math.sin(a) * .95))
        sh.poly_r(pts, "w")
        sh.region(f"M{cx + 4} {cy + 14}Q{cx + 4} {cy - 2} {cx + 14} {cy}Q{cx + 22} {cy + 6} {cx + 26} {cy + 12}Q{cx + 20} {cy + 15} {cx + 4} {cy + 14}Z", "k")
        sh.circle_r(cx + 26, cy + 12, 1.8, "x")
        sh.dot(cx + 17, cy + 6, 1.4)
        sh.line(f"M{cx - 20} {cy + 14}H{cx + 24}", "l", "stroke-width:1.4")
        muts(cx + 8, cy + 1, 12, "r", 15)
    def rendier(cx, cy):
        for s in (-1, 1):
            sh.line(f"M{cx + s * 6} {cy - 10}Q{cx + s * 10} {cy - 17} {cx + s * 16} {cy - 19}M{cx + s * 9} {cy - 15}Q{cx + s * 8} {cy - 19} {cx + s * 9} {cy - 22}M{cx + s * 13} {cy - 18}Q{cx + s * 16} {cy - 22} {cx + s * 18} {cy - 21}", "l", "stroke-width:2")
            rot(sh, s * 30, cx + s * 14, cy - 5)
            sh.ellipse_r(cx + s * 14, cy - 5, 6, 3.4, "w")
            end(sh)
        sh.region(f"M{cx - 11} {cy - 8}Q{cx - 13} {cy + 6} {cx - 8} {cy + 14}Q{cx} {cy + 22} {cx + 8} {cy + 14}Q{cx + 13} {cy + 6} {cx + 11} {cy - 8}Q{cx} {cy - 16} {cx - 11} {cy - 8}Z", "w")
        sh.ellipse_r(cx, cy + 12, 7, 6, "k")
        sh.circle_r(cx, cy + 9, 4, "r")
        sh.dot(cx - 5, cy - 1, 1.6); sh.dot(cx + 5, cy - 1, 1.6)
    animals = [pinguin, ijsbeer, uil, vos, egel, rendier]
    for i, a in enumerate(animals):
        col, row = i % 2, i // 2
        cx, cy, R = 56 + col * 88, 66 + row * 82, 35
        d = schulp(cx, cy, R)
        sh.region(d, "bkyltm"[i])
        sh.line(d, "cut")
        sh.circle_r(cx, cy + 3, 27, "-")
        a(cx, cy + 5)
        hole(sh, cx, cy - R + 5, 2.4)
    sh.legend(["cut"], 276)
    write(OUT, "boomhangers-winterdieren", sh, {"category": "dieren", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 25, "holiday": "kerst", "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Boomhangers met winterdieren", "printNote": "Op stevig papier (160 gram) blijven de hangers mooi plat.", "steps": [
            "Kleur de dieren en de randjes in.",
            "Knip de hangers uit langs de golfjesrand.",
            "Prik een gaatje in het kleine rondje bovenin (vraag een volwassene om hulp).",
            "Rijg er een touwtje of lintje door en hang ze in de kerstboom, aan een tak of voor het raam."]}}})
boomhangers()

# ---------- herfstslinger met bladeren ----------
def herfstslinger():
    sh = Sheet()
    title(sh, "Herfstslinger met bladeren", 14)
    sh.text(100, 25, "Knip de bladeren uit en rijg ze door de gaatjes aan een touw.", 5.5)
    def pinnate(cx, top, bot, n=3, reach=12):
        v = [f"M{cx} {f(top + 5)}L{cx} {f(bot - 3)}"]
        for k in range(n):
            yy = top + (bot - top) * (.32 + k * .5 / max(1, n - 1))
            for s in (-1, 1): v.append(f"M{cx} {f(yy)}Q{f(cx + s * reach * .5)} {f(yy - 2)} {f(cx + s * reach)} {f(yy - reach * .7)}")
        return v
    def eik(cx, cy):
        parts = [affinity.scale(Point(cx, cy).buffer(1, 48), 10, 30)]
        for dy, r in [(-21, 7.5), (-8, 9), (6, 10), (18, 8.5)]:
            for s in (-1, 1):
                parts.append(Point(cx + s * (9 + r * .55), cy + dy + s * 1.5).buffer(r, 32))
        parts.append(Point(cx, cy - 29).buffer(7, 32))
        return unary_union(parts), pinnate(cx, cy - 36, cy + 30, 4, 13)
    def esdoorn(cx, cy):
        lobes, v = [], []
        for ang, L, wid in [(-90, 36, 13), (-35, 33, 12), (-145, 33, 12), (25, 21, 9), (-205, 21, 9)]:
            a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
            pts = [(cx + nx * wid * .5, cy + ny * wid * .5)]
            for t, wv in [(.4, 1.0), (.55, .55), (.7, .8), (.85, .3)]:
                pts.append((cx + ux * L * t + nx * wid * wv, cy + uy * L * t + ny * wid * wv))
            pts.append((cx + ux * L, cy + uy * L))
            for t, wv in [(.85, .3), (.7, .8), (.55, .55), (.4, 1.0)]:
                pts.append((cx + ux * L * t - nx * wid * wv, cy + uy * L * t - ny * wid * wv))
            pts.append((cx - nx * wid * .5, cy - ny * wid * .5))
            lobes.append(Polygon(pts))
            v.append(f"M{cx} {cy + 8}L{f(cx + ux * L * .8)} {f(cy + uy * L * .8)}")
        lobes.append(Point(cx, cy).buffer(11, 32))
        return unary_union(lobes), v
    def kastanje(cx, cy):
        base = (cx, cy + 24)
        parts, v = [Point(*base).buffer(4, 24)], []
        for ang, L in [(-90, 44), (-58, 40), (-122, 40), (-28, 30), (-152, 30)]:
            a = math.radians(ang)
            e = affinity.scale(Point(0, 0).buffer(1, 48), L / 2, 7 if L > 35 else 6)
            e = affinity.rotate(e, ang, origin=(0, 0))
            parts.append(affinity.translate(e, base[0] + math.cos(a) * (L / 2 + 2), base[1] + math.sin(a) * (L / 2 + 2)))
            v.append(f"M{base[0]} {base[1]}L{f(base[0] + math.cos(a) * (L - 2))} {f(base[1] + math.sin(a) * (L - 2))}")
        return unary_union(parts), v
    def beuk(cx, cy):
        pts = []
        for k in range(120):
            t = 2 * math.pi * k / 120
            r = 1 + .035 * math.cos(16 * t)
            x = 15 * math.sin(t) * r; y = -29 * math.cos(t) * r
            if y < 0: x *= .85 + .15 * (1 + y / 29)
            pts.append((cx + x, cy + y))
        return Polygon(pts).buffer(0), pinnate(cx, cy - 29, cy + 29, 4, 10)
    def ginkgo(cx, cy):
        b = (cx, cy + 18)
        pts = [b]
        for k in range(41):
            a = math.radians(-145 + k * 110 / 40)
            r = 42 - (8 if abs(k - 20) <= 1 else 0) + 1.2 * math.cos(k * 1.3)
            pts.append((b[0] + r * math.cos(a), b[1] + r * math.sin(a)))
        v = [f"M{b[0]} {b[1] - 3}L{f(b[0] + 36 * math.cos(math.radians(a)))} {f(b[1] + 36 * math.sin(math.radians(a)))}" for a in (-135, -118, -102, -78, -62, -45)]
        return Polygon(pts).buffer(1.5).buffer(-1), v
    def berk(cx, cy):
        pts = []
        n = 40
        for k in range(n):
            t = k / n
            if t < .5:
                u = t / .5; x = cx + 19 * math.sin(math.pi * u) ** .8 * (1 - .35 * u); y = cy - 32 + 58 * u
            else:
                u = (t - .5) / .5; x = cx - 19 * math.sin(math.pi * (1 - u)) ** .8 * (1 - .35 * (1 - u)); y = cy + 26 - 58 * u
            off = 1.8 if k % 2 else 0
            pts.append((x + (off if x > cx else -off), y))
        return Polygon(pts).buffer(0), pinnate(cx, cy - 32, cy + 26, 4, 12)
    leaves = [("eik", eik, "w"), ("esdoorn", esdoorn, "r"), ("kastanje", kastanje, "g"), ("beuk", beuk, "o"), ("ginkgo", ginkgo, "y"), ("berk", berk, "y")]
    for i, (nm, fn, code) in enumerate(leaves):
        col, row = i % 2, i // 2
        cx, cy = 56 + col * 88, 72 + row * 77
        g, veins = fn(cx, cy)
        g = Polygon(g.exterior) if g.geom_type == "Polygon" else g
        top, bot = g.bounds[1], g.bounds[3]
        sh.line(f"M{cx} {f(bot - 2)}Q{cx + 3} {f(bot + 5)} {cx - 2} {f(bot + 10)}", "l", "stroke-width:2.2")
        cutg = unary_union([g, box(cx - 4, bot - 4, cx + 4, bot + 11)]).buffer(4, join_style=1).simplify(.4)
        sh.line(geom_d(cutg), "cut")
        sh.region(geom_d(g), code)
        for d in veins: sh.line(d, "l", "stroke-width:.9")
        hy = top + 8
        while not all(g.buffer(-1).contains(Point(cx + s * 7, hy).buffer(3.5)) for s in (-1, 1)): hy += 1
        for s in (-1, 1): hole(sh, cx + s * 7, hy)
        assert cutg.bounds[0] > 4 and cutg.bounds[2] < 196 and cutg.bounds[1] > 28 and cutg.bounds[3] < 268, (nm, cutg.bounds)
    sh.legend(["cut"], 276)
    write(OUT, "herfstslinger-bladeren", sh, {"category": "natuur", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}, {"slug": "waskrijtjes", "optional": True}],
        "i18n": {"nl": {"name": "Herfstslinger met zes soorten bladeren", "steps": [
            "Kleur de bladeren in herfstkleuren: rood, oranje, geel, bruin en een beetje groen.",
            "Knip ze uit langs de streepjeslijn rond elk blad.",
            "Prik de twee gaatjes bovenin elk blad door (vraag een volwassene om hulp).",
            "Rijg een touw van voren door het ene gaatje en van achteren door het andere. Schuif de bladeren op een rij en hang de slinger op.",
            "Weet je welke bladeren het zijn? Eik, esdoorn, kastanje, beuk, ginkgo en berk. Zoek ze buiten!"]}}})
herfstslinger()

# ---------- mini-wenskaartjes (4 per vel) ----------
def mini_kaartjes():
    sh = Sheet()
    title(sh, "Mini-wenskaartjes", 14)
    sh.text(100, 24, "Vier kleine kaartjes: knippen, dubbelvouwen en geven!", 5.5)
    def m_hoera(cx, cy):
        for dx, dy, c in [(-12, 2, "r"), (0, -3, "y"), (12, 2, "b")]:
            balloon(sh, cx + dx, cy + dy, 6, c, False)
            sh.line(f"M{cx + dx} {cy + dy + 8.7}L{cx} {cy + 22}", "l", "stroke-width:.8")
    def m_dank(cx, cy):
        sh.region(heart_path(cx, cy + 4, 20), "r")
        flower(sh, cx - 6, cy, 3, "y", "o"); flower(sh, cx + 6, cy + 6, 3, "-", "y")
    def m_succes(cx, cy):
        for k in range(4):
            a = k * 90
            sh.raw(f'<path class="r" transform="rotate({a} {cx} {cy + 2})" d="{heart_path(cx, cy - 6, 8)}"/>', "g")
        sh.line(f"M{cx} {cy + 2}Q{cx + 4} {cy + 14} {cx + 10} {cy + 20}", "l", "stroke-width:1.6")
    def m_beter(cx, cy):
        sh.circle_r(cx, cy + 2, 11, "y")
        for k in range(10):
            a = math.radians(k * 36)
            sh.seg(cx + 14 * math.cos(a), cy + 2 + 14 * math.sin(a), cx + 18 * math.cos(a), cy + 2 + 18 * math.sin(a), "l", "stroke-width:1.2")
        sh.dot(cx - 4, cy, 1.3); sh.dot(cx + 4, cy, 1.3)
        sh.line(f"M{cx - 4} {cy + 5}Q{cx} {cy + 8} {cx + 4} {cy + 5}", "l", "stroke-width:1")
        rot(sh, -30, cx + 6, cy - 5)
        sh.rect_r(cx + 1, cy - 7, 10, 4, "k", 2)
        end(sh)
    cards = [("Hoera!", m_hoera), ("Dank je!", m_dank), ("Succes!", m_succes), ("Beterschap!", m_beter)]
    for i, (word, pic) in enumerate(cards):
        col, row = i % 2, i // 2
        x, y, w, h = 14 + col * 88, 30 + row * 122, 84, 118
        mid = y + h / 2
        sh.rect_line(x, y, w, h, "cut", 3)
        sh.seg(x, mid, x + w, mid, "fold")
        sh.raw(f'<g transform="rotate(180 {x + w / 2} {y + h / 4})">')
        sh.text(x + w / 2, y + h / 4 - 6, "Voor: ........................", 5.5)
        sh.text(x + w / 2, y + h / 4 + 8, "Van: .........................", 5.5)
        sh.raw('</g>')
        outline_text(sh, x + w / 2, mid + 14, word, 10.5 if len(word) < 9 else 9)
        pic(x + w / 2, mid + 32)
        for sx, sy in [(x + 9, mid + 50), (x + w - 9, mid + 50)]: sh.poly_r(star_pts(sx, sy, 3.6, 1.6), "y")
    sh.legend(["cut", "fold"], 276)
    write(OUT, "mini-wenskaartjes", sh, {"category": "feest", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Mini-wenskaartjes: hoera, dank je, succes en beterschap", "printNote": "Print op stevig papier (160 gram) als je het hebt; gewoon papier kan ook.", "steps": [
            "Kleur de voorkantjes in (de onderste helft van elk kaartje).",
            "Knip de vier kaartjes los langs de streepjeslijnen.",
            "Vouw elk kaartje dubbel op de stippellijn, met de tekening aan de buitenkant.",
            "Schrijf op de achterkant voor wie het is en van wie, en binnenin een berichtje. Leuk bij een cadeautje of zomaar in een broodtrommel!"]}}})
mini_kaartjes()

# ---------- enveloppe voor de grote kaarten ----------
CARD_W, CARD_H = 172, 125  # gevouwen kaart van card(): 172 breed, 250 / 2 hoog
def enveloppe():
    sh = Sheet()
    L, R, T, B = 10, 190, 74, 204         # middenvlak (voorkant van de enveloppe)
    assert R - L >= CARD_W + 6 and B - T >= CARD_H + 4, "de kaart past niet in de enveloppe"
    top_tip, bot_tip = 4, 270
    assert (T - top_tip) + (bot_tip - B) >= (B - T) + 6, "de flappen sluiten niet"
    # vlakken (kleurbaar) en lijnen
    topflap = f"M{L} {T}L36 12Q40 {top_tip} 50 {top_tip}H150Q160 {top_tip} 164 12L{R} {T}Z"
    botflap = f"M{L} {B}L32 {bot_tip}H168L{R} {B}Z"
    lflap = f"M{L} {T + 4}L{L - 8} {T + 16}V{B - 16}L{L} {B - 4}Z"
    rflap = f"M{R} {T + 4}L{R + 8} {T + 16}V{B - 16}L{R} {B - 4}Z"
    # flappen: alleen een versierd binnenvlak, zodat de vouwlijnen goed zichtbaar blijven
    sh.region(f"M{L + 14} {T - 6}L40 20Q43 14 52 14H148Q157 14 160 20L{R - 14} {T - 6}Z", "b")
    sh.region(f"M{L + 14} {B + 6}L38 {bot_tip - 14}H162L{R - 14} {B + 6}Z", "b")
    sh.raw(f'<path class="glue" d="{lflap}"/>'); sh.raw(f'<path class="glue" d="{rflap}"/>')
    sh.line(f"M{L} {T}L36 12Q40 {top_tip} 50 {top_tip}H150Q160 {top_tip} 164 12L{R} {T}V{T + 4}L{R + 8} {T + 16}V{B - 16}L{R} {B - 4}V{B}L168 {bot_tip}H32L{L} {B}V{B - 4}L{L - 8} {B - 16}V{T + 16}L{L} {T + 4}Z", "cut")
    for x1, y1, x2, y2 in [(L, T, R, T), (L, B, R, B), (L, T, L, B), (R, T, R, B)]: sh.seg(x1, y1, x2, y2, "fold")
    # lijmstrook op de onderflap (daar komt de bovenflap overheen)
    sh.raw(f'<rect class="glue" x="64" y="{bot_tip - 10}" width="72" height="7"/>')
    # voorkant: adres en postzegel
    sh.text(26, T + 30, "Voor:", 8, "start")
    for k in range(3): sh.seg(56, T + 30 + k * 18, 140, T + 30 + k * 18, "guide")
    sx, sy = 152, T + 10
    sh.region(f"M{sx} {sy}" + "".join(f"Q{sx + 2.5 + k * 5} {sy + 2.5} {sx + 5 + k * 5} {sy}" for k in range(5)) + f"V{sy + 32}" + "".join(f"Q{sx + 22.5 - k * 5} {sy + 29.5} {sx + 20 - k * 5} {sy + 32}" for k in range(5)) + "Z", "-")
    sh.region(heart_path(sx + 12.5, sy + 15, 7), "r")
    sh.tip(sx + 12.5, sy + 40, "postzegel", "middle")
    for x, y in [(30, B - 18), (44, B - 12), (170, B - 14)]: sh.poly_r(star_pts(x, y, 4.5, 2), "y")
    # achterkant-versiering op de flappen (op zijn kop, zodat hij na het vouwen rechtop staat)
    sh.raw(f'<g transform="rotate(180 100 40)">')
    sh.text(100, 30, "Van: ...................................", 7)
    for x in (66, 134): sh.region(heart_path(x, 46, 6), "m")
    sh.raw("</g>")
    for k in range(5):
        x, y = 52 + k * 24, B + 28 + (k % 2) * 8
        sh.raw(f'<g transform="rotate(180 {x} {y})">'); sh.region(heart_path(x, y, 5), "m"); sh.raw("</g>")
    sh.legend(["cut", "fold", "glue"], 279)
    write(OUT, "enveloppe-vouwen", sh, {"category": "feest", "age": "6-9", "kind": "vouwblad", "difficulty": 2, "minutes": 15,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Enveloppe om te vouwen (past om een gevouwen kaart)", "printNote": "Print de enveloppe op gewoon papier en met dezelfde printerinstellingen als je kaart: dan past een gevouwen Kleurhoek-kaart er precies in.", "steps": [
            "Schrijf op de voorkant voor wie de post is en teken een eigen postzegel. Kleur de flappen in.",
            "Knip de enveloppe uit langs de streepjeslijn.",
            "Vouw alle stippellijnen naar achteren, zodat de tekening aan de buitenkant blijft. Vouw ze daarna weer open.",
            "Vouw de twee smalle zijflapjes naar achteren en smeer lijm op de grijze vlakjes.",
            "Vouw de onderflap omhoog over de zijflapjes en druk hem goed aan.",
            "Stop je kaart erin. Smeer lijm op de grijze strook van de onderflap en vouw de bovenflap eroverheen. Klaar om te geven!"]}}})
enveloppe()

# ---------- cadeautasje (bouwplaat) ----------
def cadeautasje():
    sh = Sheet()
    title(sh, "Cadeautasje", 14)
    sh.text(100, 24, "Een tasje met een dichte bodem en twee hengsels.", 5.5)
    W, D, H, G = 58, 30, 108, 8          # voor/achter, zijkant, hoogte, lijmflap
    x0, top = 8, 34
    bot = top + H
    xs = [x0, x0 + W, x0 + W + D, x0 + 2 * W + D, x0 + 2 * W + 2 * D]   # voor | zij | achter | zij | lijmflap
    xg = xs[4] + G
    assert xg <= 194
    # panelen
    codes = ["k", "y", "k", "y"]
    for i in range(4):
        sh.raw(f'<path class="r" style="stroke:none" d="M{xs[i]} {top}H{xs[i + 1]}V{bot}H{xs[i]}Z"/>', codes[i])
    # bodemflappen: voor (bodem), achter (bodem, overlapt), zijkanten (half, eerst naar binnen)
    fb = f"M{xs[0]} {bot}V{bot + D - 1}H{xs[1]}V{bot}"
    bb = f"M{xs[2]} {bot}V{bot + D - 1}H{xs[3]}V{bot}"
    sb1 = f"M{xs[1]} {bot}L{xs[1] + 3} {bot + D / 2}H{xs[2] - 3}L{xs[2]} {bot}"
    sb2 = f"M{xs[3]} {bot}L{xs[3] + 3} {bot + D / 2}H{xs[4] - 3}L{xs[4]} {bot}"
    sh.raw(f'<path class="glue" d="{fb}Z"/>')
    sh.raw(f'<path class="glue" d="M{xs[4]} {top + 3}L{xg} {top + 8}V{bot - 5}L{xs[4]} {bot - 2}Z"/>')
    # buitenrand = knippen
    sh.line(f"M{xs[0]} {top}H{xs[4]}L{xg} {top + 8}V{bot - 5}L{xs[4]} {bot - 2}V{bot}"
            f"L{xs[4] - 3} {bot + D / 2}H{xs[3] + 3}L{xs[3]} {bot}V{bot + D - 1}H{xs[2]}V{bot}"
            f"L{xs[2] - 3} {bot + D / 2}H{xs[1] + 3}L{xs[1]} {bot}V{bot + D - 1}H{xs[0]}Z", "cut")
    # vouwlijnen
    for x in xs[1:]: sh.seg(x, top, x, bot, "fold")
    sh.seg(xs[0], bot, xs[4], bot, "fold")
    # versiering voorkant
    fx = (xs[0] + xs[1]) / 2
    sh.region(heart_path(fx, top + 46, 30), "r")
    sh.text(fx, top + 48, "Voor jou!", 6.5)
    for dx, dy in [(-18, 12), (18, 12), (-18, 90), (18, 92), (0, 98), (-8, 20), (8, 20)]: sh.circle_r(fx + dx, top + dy, 2.6, "y")
    # achterkant: sterren
    bx = (xs[2] + xs[3]) / 2
    for k, (dx, dy, r) in enumerate([(0, 24, 13), (-15, 54, 9), (15, 56, 9), (0, 80, 8), (-14, 98, 5), (14, 98, 5)]):
        sh.poly_r(star_pts(bx + dx, top + dy, r, r * .44), "y" if k % 2 == 0 else "o")
    # zijkanten: stippen
    for sx in ((xs[1] + xs[2]) / 2, (xs[3] + xs[4]) / 2):
        for k in range(5): sh.circle_r(sx + (-6 if k % 2 else 6), top + 14 + k * 20, 4.5, "b")
    # hengsels en kaartje
    hy = bot + D + 18
    for i in range(2):
        y = hy + i * 18
        sh.rect_line(24, y, 100, 8, "cut")
        sh.raw(f'<rect class="glue" x="24.5" y="{y + .5}" width="11" height="7"/>'); sh.raw(f'<rect class="glue" x="{124 - 11.5}" y="{y + .5}" width="11" height="7"/>')
        sh.seg(36, y + 4, 112, y + 4, "l", "stroke-width:.8;stroke-dasharray:5 3")
    tx, ty = 140, hy - 2
    sh.line(f"M{tx} {ty}H{tx + 40}V{ty + 30}H{tx}L{tx - 8} {ty + 15}Z", "cut")
    hole(sh, tx - 2, ty + 15, 2)
    sh.text(tx + 20, ty + 12, "Voor:", 6); sh.text(tx + 20, ty + 24, "Van:", 6)
    sh.tip(74, hy - 4, "2 hengsels", "middle")
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "cadeautasje", sh, {"category": "feest", "age": "9+", "kind": "bouwplaat", "difficulty": 3, "minutes": 35, "adultHelp": True, "paperGsm": 160, "holiday": "verjaardag",
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": "Bouwplaat: cadeautasje met hengsels", "printNote": "Print op stevig papier (160 gram), dan blijft het tasje goed staan.", "steps": [
            "Kleur het tasje, de hengsels en het kaartje in. Schrijf op het kaartje voor wie het cadeau is.",
            "Knip alles uit langs de streepjeslijnen. De grijze lijmflappen blijven aan het tasje vast.",
            "Kras de stippellijnen met een liniaal en een lege balpen en vouw ze allemaal naar binnen.",
            "Smeer lijm op de lange lijmflap rechts en plak hem aan de binnenkant van de rand van de voorkant (het vlak met het hart). Nu heb je een koker.",
            "Bodem: vouw eerst de twee kleine zijflapjes naar binnen, dan de flap onder het hart. Smeer lijm op die flap (de grijze kant) en vouw de flap onder de achterkant eroverheen. Druk goed aan.",
            "Plak de uiteinden van elk hengsel aan de binnenkant van de voor- en achterkant, en hang het kaartje met een touwtje aan een hengsel."]}}})
cadeautasje()

# ---------- servetringen ----------
def servetringen():
    sh = Sheet()
    title(sh, "Servetringen voor een feestmaal", 14)
    sh.text(100, 24, "Schrijf op elke ring een naam: dan weet iedereen waar hij zit.", 5.5)
    L, Hh, G = 150, 30, 12
    x0 = (200 - L - G) / 2
    def m_ballon(x, y):
        for dx, c in [(-6, "r"), (5, "b")]: balloon(sh, x + dx, y - 3, 4.5, c, False)
    def m_bloem(x, y): flower(sh, x, y, 4.2, "m")
    def m_ster(x, y): sh.poly_r(star_pts(x, y, 9, 4), "y")
    def m_hart(x, y): sh.region(heart_path(x, y, 9), "r")
    def m_cupcake(x, y):
        sh.region(f"M{x - 7} {y + 1}H{x + 7}L{x + 5} {y + 9}H{x - 5}Z", "p")
        sh.region(f"M{x - 8} {y + 1}Q{x - 9} {y - 6} {x - 3} {y - 6}Q{x} {y - 11} {x + 3} {y - 6}Q{x + 9} {y - 6} {x + 8} {y + 1}Z", "k")
        sh.circle_r(x, y - 10, 2, "r")
    themes = [(m_ballon, "y"), (m_bloem, "l"), (m_ster, "b"), (m_hart, "k"), (m_cupcake, "t")]
    for i, (m, band) in enumerate(themes):
        y = 36 + i * 46
        sh.raw(f'<path class="r" style="stroke:none" d="M{x0} {y}H{x0 + L}V{y + Hh}H{x0}Z"/>', band)
        sh.raw(f'<rect class="glue" x="{x0 + L}" y="{y}" width="{G}" height="{Hh}"/>')
        sh.rect_line(x0, y, L + G, Hh, "cut")
        for k in (0, 2): m(x0 + 16 + k * 59, y + Hh / 2 + 1)
        sh.rect_r(x0 + 34, y + 8, 82, 14, "-", 3)
        sh.text(x0 + 75, y + 17.2, "Naam: ......................", 5.5)
    sh.legend(["cut", "glue"], 276)
    write(OUT, "servetringen-met-naam", sh, {"category": "eten", "age": "6-9", "kind": "knipplaat", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Servetringen met naam", "printNote": "Op stevig papier (160 gram) blijven de ringen mooi rond.", "steps": [
            "Schrijf op elke strook de naam van iemand die mee-eet en kleur de strook in.",
            "Knip de stroken uit langs de streepjeslijn.",
            "Buig een strook rond tot een ring. Smeer lijm op het grijze stukje en plak het andere uiteinde eroverheen, met de tekening aan de buitenkant.",
            "Rol een servet op, schuif de ring eromheen en leg hem bij het bord. Print nog een vel als jullie met meer zijn."]}}})
servetringen()

# ---------- bladwijzer-hoekjes ----------
def bladwijzer_hoekjes():
    sh = Sheet()
    title(sh, "Bladwijzer-hoekjes: monsters", 14)
    sh.text(100, 24, "Het hoekje schuif je over de hoek van een bladzijde.", 5.5)
    Lg = 66
    def piece(cx, base, kind):
        # B = voorkant (rechts), F = achterkant (links), lijmflap onder F
        A = (cx, base - Lg)
        sh.raw(f'<path class="r" style="stroke:none" d="M{cx} {base}H{cx - Lg}L{A[0]} {A[1]}Z"/>', "z" if kind == 0 else "b")
        for k in range(5):
            for j in range(5 - k):
                sh.circle_r(cx - 8 - j * 11 - (k % 2) * 5, base - 8 - k * 11, 2, "-") if j * 11 + 8 + (k % 2) * 5 + k * 11 < Lg - 8 else None
        flap = f"M{cx - Lg + 2} {base}L{cx - Lg + 13} {base + 9}H{cx - 2}L{cx - 2} {base}"
        sh.region(flap + "Z", "z" if kind == 0 else "b")
        # voorkant: monster, getekend op zijn kop zodat het rechtop staat als de rechte hoek rechtsboven zit
        gx, gy = cx + Lg / 3, base - Lg / 3
        ax, ty = cx + 2 * Lg / 3, base - 2 * Lg / 3          # in het ontwerp: rechte hoek rechtsboven
        sh.raw(f'<g transform="rotate(180 {f(gx)} {f(gy)})">')
        sh.raw(f'<path class="r" d="M{f(ax - Lg)} {f(ty)}H{f(ax)}V{f(ty + Lg)}Z"/>', "l" if kind == 0 else "p")
        n = (1 / math.sqrt(2), -1 / math.sqrt(2))
        Pp = lambda t, o: (ax - Lg + t * Lg + o * n[0], ty + t * Lg + o * n[1])
        S0, S1, Qc = Pp(.12, 2.5), Pp(.88, 2.5), Pp(.5, 24)
        sh.region(f"M{f(S0[0])} {f(S0[1])}L{f(S1[0])} {f(S1[1])}Q{f(Qc[0])} {f(Qc[1])} {f(S0[0])} {f(S0[1])}Z", "r")
        for k in range(6):
            t = .2 + k * .12
            a, b, c = Pp(t - .035, 2.5), Pp(t + .035, 2.5), Pp(t, 8)
            sh.poly_r([a, b, c], "-")
        if kind == 0:
            sh.circle_r(ax - 17, ty + 20, 8.5, "-"); sh.circle_r(ax - 15.5, ty + 21.5, 3.6, "x")
        else:
            for ex, ey in [(ax - 30, ty + 17), (ax - 12, ty + 33)]:
                sh.circle_r(ex, ey, 5.5, "-"); sh.dot(ex + 1, ey + 1.2, 2.2)
            sh.circle_r(ax - 11, ty + 15, 3, "m") 
        sh.raw("</g>")
        sh.raw(f'<path class="glue" d="M{cx + 3} {base - 1}H{cx + Lg - 4}L{cx + Lg - 12} {base - 8.5}H{cx + 3}Z"/>')
        # lijnen
        sh.line(f"M{cx} {base}H{cx + Lg}L{A[0]} {A[1]}L{cx - Lg} {base}", "cut")
        sh.line(flap, "cut")
        sh.seg(cx, base - Lg, cx, base, "fold"); sh.seg(cx - Lg, base, cx, base, "fold")
    piece(100, 112, 0)
    piece(100, 232, 1)
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "bladwijzer-hoekjes-monsters", sh, {"category": "thuis", "age": "6-9", "kind": "knipplaat", "difficulty": 2, "minutes": 20,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Bladwijzer-hoekjes: twee hongerige monsters", "steps": [
            "Kleur de monsters en de stippeltjes in.",
            "Knip elk hoekje uit langs de streepjeslijn. Het smalle flapje onderaan blijft vast.",
            "Vouw de linker driehoek over de middelste stippellijn naar achteren, achter het monster.",
            "Smeer lijm op het grijze strookje van het monster en vouw het flapje van achteren naar voren eroverheen.",
            "Laat de lijm drogen. Schuif het hoekje over de hoek van een bladzijde: het monster eet je bladzijde op!"]}}})
bladwijzer_hoekjes()
print("klaar")
