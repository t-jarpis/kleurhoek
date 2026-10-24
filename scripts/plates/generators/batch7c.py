"""Batch 7c: kaarten en decoraties, tekenlessen, maak-af-bladen en sjablonen (eigen ontwerpen)."""
import math
from lib_gen import *
from lib_gen import C, E
from shapes import stencil, heart_path, star_path, moon_path, drop_path, cloud_path

def P(points):
    return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in points) + "Z"

# =====================================================================
# 1. KAARTEN
# =====================================================================

def front_moeder(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Lieve mama!", 17)
    cy = y0 + 70
    sh.region(heart_path(100, cy, 52), "k")
    for fx, fy, c in [(80, cy - 10, "r"), (120, cy - 10, "p"), (100, cy + 14, "o")]:
        for k in range(5):
            a = math.radians(k * 72 - 90)
            sh.circle_r(fx + 7.5 * math.cos(a), fy + 7.5 * math.sin(a), 5.2, c)
        sh.circle_r(fx, fy, 4, "y")
    for lx, ly, rot in [(100, cy - 6, -30), (84, cy + 12, 30), (116, cy + 12, -30)]:
        sh.raw(f'<g transform="rotate({rot} {lx} {ly})">'); sh.region(f"M{lx - 7} {ly}Q{lx} {ly - 6} {lx + 7} {ly}Q{lx} {ly + 6} {lx - 7} {ly}Z", "g"); sh.raw("</g>")
    for x, y in [(36, y0 + 52), (164, y0 + 52), (40, y0 + 108), (160, y0 + 108)]:
        sh.region(heart_path(x, y, 7), "r")
card("moederdagkaart-bloemenhart", "Moederdagkaart: hart vol bloemen", front_moeder, "Fijne moederdag!", "feest", "4-6",
     ["Schrijf binnenin waarom jouw mama (of iemand anders die voor je zorgt) zo lief is."], holiday="moederdag")

def lantern(sh, cx, top, s, body="o", win="y"):
    sh.seg(cx, top - 14 * s, cx, top, "l", "stroke-width:1.2")
    sh.poly_r([(cx - 8 * s, top + 8 * s), (cx + 8 * s, top + 8 * s), (cx, top)], body)
    sh.region(f"M{f(cx - 10 * s)} {f(top + 8 * s)}H{f(cx + 10 * s)}L{f(cx + 14 * s)} {f(top + 22 * s)}L{f(cx + 10 * s)} {f(top + 40 * s)}H{f(cx - 10 * s)}L{f(cx - 14 * s)} {f(top + 22 * s)}Z", body)
    sh.region(f"M{f(cx - 5 * s)} {f(top + 13 * s)}H{f(cx + 5 * s)}L{f(cx + 8 * s)} {f(top + 23 * s)}L{f(cx + 5 * s)} {f(top + 35 * s)}H{f(cx - 5 * s)}L{f(cx - 8 * s)} {f(top + 23 * s)}Z", win)
    sh.poly_r([(cx - 6 * s, top + 40 * s), (cx + 6 * s, top + 40 * s), (cx, top + 48 * s)], body)
def front_suiker(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Fijn Suikerfeest!", 15)
    sh.region(moon_path(66, y0 + 80, 32), "y")
    sh.poly_r(star_pts(96, y0 + 58, 9, 3.8), "y")
    sh.line(f"M112 {y0 + 36}Q146 {y0 + 46} 184 {y0 + 36}", "l", "stroke-width:1.2")
    lantern(sh, 136, y0 + 58, 1.0, "t", "y")
    lantern(sh, 166, y0 + 52, .75, "p", "y")
    for x, y in [(30, y0 + 46), (118, y0 + 106), (176, y0 + 104), (34, y0 + 116)]:
        sh.poly_r(star_pts(x, y, 5, 2.2), "y")
card("suikerfeestkaart-maan-lantaarns", "Suikerfeestkaart met maan en lantaarns", front_suiker, "Een fijn feest gewenst!", "feest", "4-6",
     ["Schrijf binnenin een lieve wens voor het feest."], holiday="suikerfeest")

def diya(sh, x, y, c="o"):
    sh.region(f"M{x - 20} {y}H{x + 18}L{x + 26} {y - 6}L{x + 22} {y + 4}Q{x + 14} {y + 18} {x} {y + 18}Q{x - 16} {y + 18} {x - 20} {y}Z", c)
    sh.region(f"M{x - 20} {y}Q{x} {y + 6} {x + 18} {y}", "-") if False else None
    sh.line(f"M{x - 12} {y + 8}H{x + 10}")
    sh.region(drop_path(x, y - 10, 5), "y"); sh.region(drop_path(x, y - 7, 2.4), "o")
def front_divali(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Fijne Divali!", 18)
    cx, cy = 100, y0 + 60
    for k in range(8):
        a = math.radians(k * 45)
        sh.circle_r(cx + 13 * math.cos(a), cy + 13 * math.sin(a), 6, "mp"[k % 2])
    sh.circle_r(cx, cy, 7, "y")
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        sh.dot(cx + 24 * math.cos(a), cy + 24 * math.sin(a), 1.6)
    for x in (46, 100, 154): diya(sh, x, y0 + 102, "o" if x != 100 else "r")
    for x, y in [(30, y0 + 50), (170, y0 + 50), (34, y0 + 80), (166, y0 + 80)]:
        sh.poly_r(star_pts(x, y, 5, 2.2), "y")
card("divalikaart-lichtjes", "Divalikaart met lichtjes", front_divali, "Een stralende Divali!", "feest", "6-9",
     ["Schrijf binnenin een wens vol licht."], holiday="divali")

def front_chanoeka(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Fijne Chanoeka!", 16)
    sh.rect_r(95, y0 + 40, 10, 14, "z", 2)
    sh.rect_r(78, y0 + 54, 44, 38, "n", 4)
    sh.poly_r([(78, y0 + 92), (122, y0 + 92), (100, y0 + 116)], "b")
    sh.line(P([(100, y0 + 61), (110, y0 + 79), (90, y0 + 79)]), "l", "stroke-width:1.6")
    sh.line(P([(100, y0 + 85), (110, y0 + 67), (90, y0 + 67)]), "l", "stroke-width:1.6")
    for x, y, r in [(44, y0 + 98, 11), (60, y0 + 110, 9)]:
        sh.circle_r(x, y, r, "y"); sh.circle_line(x, y, r - 3.5, "l", "stroke-width:1")
    sh.ellipse_r(152, y0 + 102, 20, 12, "w"); sh.ellipse_r(152, y0 + 98, 7, 3.5, "r")
    for dx, dy in [(-12, 2), (10, 4), (-4, 8), (14, -4), (-14, -4)]: sh.dot(152 + dx, y0 + 102 + dy, 1)
    for x, y in [(40, y0 + 54), (160, y0 + 56), (138, y0 + 44)]:
        sh.poly_r(star_pts(x, y, 6, 2.6), "y")
card("chanoekakaart-draaitol", "Chanoekakaart met draaitol", front_chanoeka, "Een lichtjesfeest vol warmte!", "feest", "6-9",
     ["Schrijf binnenin een wens voor de acht feestdagen."], holiday="chanoeka")

def front_ketikoti(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 26, "Keti Koti", 20)
    sh.text(100, y0 + 38, "de ketenen zijn gebroken", 7)
    cy = y0 + 118
    for k in range(9):
        a = math.radians(180 + k * 22.5)
        sh.seg(100 + 30 * math.cos(a), cy + 30 * math.sin(a), 100 + 40 * math.cos(a), cy + 40 * math.sin(a), "l", "stroke-width:1.6")
    sh.region(f"M74 {cy}A26 26 0 0 1 126 {cy}Z", "y")
    sh.seg(40, cy, 160, cy, "l", "stroke-width:1.6")
    ly = y0 + 58
    for side in (-1, 1):
        for i in range(4):
            x = 100 + side * (20 + i * 17)
            if i % 2 == 0:
                sh.ellipse_r(x, ly, 11, 6.5, "z"); sh.ellipse_r(x, ly, 6, 2.4, "-")
            else:
                sh.rect_r(x - 10, ly - 2.2, 20, 4.4, "z", 2.2)
        sh.line(f"M{100 + side * 7} {ly - 8}L{100 + side * 3} {ly - 13}M{100 + side * 7} {ly + 8}L{100 + side * 3} {ly + 13}", "l", "stroke-width:1.2")
    for x in (30, 170):
        for k in range(5):
            a = math.radians(k * 72 - 90)
            sh.circle_r(x + 6 * math.cos(a), y0 + 100 + 6 * math.sin(a), 4.2, "r")
        sh.circle_r(x, y0 + 100, 3.2, "y")
card("keti-koti-kaart", "Keti Kotikaart: gebroken ketenen", front_ketikoti, "Samen vieren we vrijheid!", "wereld", "9+",
     ["Op 1 juli vieren we Keti Koti: het einde van de slavernij in Suriname en op de Antillen.", "Schrijf binnenin wat vrijheid voor jou betekent."], holiday="ketikoti")

def front_koning(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Fijne Koningsdag!", 15)
    sy = lambda x: y0 + 36 + 10 * math.sin(math.pi * (x - 20) / 160)
    sh.line(f"M20 {f(sy(20))}Q100 {f(y0 + 56)} 180 {f(sy(180))}", "l", "stroke-width:1.2")
    for i in range(7):
        x = 32 + i * 22; t = (x - 20) / 160; yy = (1 - t) ** 2 * sy(20) + 2 * t * (1 - t) * (y0 + 56) + t * t * sy(180)
        sh.poly_r([(x - 8, yy), (x + 8, yy), (x, yy + 14)], "orbn"[i % 4] if i % 4 != 2 else "-")
    cy = y0 + 94
    sh.poly_r([(68, cy + 14), (68, cy - 18), (84, cy - 2), (100, cy - 26), (116, cy - 2), (132, cy - 18), (132, cy + 14)], "o")
    sh.rect_r(64, cy + 12, 72, 12, "y", 3)
    for x, y in [(68, cy - 20), (100, cy - 28), (132, cy - 20)]: sh.circle_r(x, y, 4, "y")
    for x, c in [(80, "r"), (100, "b"), (120, "g")]: sh.circle_r(x, cy + 18, 3.4, c)
    sh.region(heart_path(100, cy + 1, 9), "r")
card("koningsdagkaart-kroon", "Koningsdagkaart met kroon en vlaggetjes", front_koning, "Hoera, het is Koningsdag!", "feest", "4-6",
     ["Kleur de kroon oranje, en de vlaggetjes rood, wit, blauw en oranje.", "Schrijf binnenin wat jij op Koningsdag gaat doen."], holiday="koningsdag")

def ghost(sh, x, y, s):
    k = s
    sh.region(f"M{f(x - 16*k)} {f(y + 24*k)}V{f(y)}Q{f(x - 16*k)} {f(y - 22*k)} {f(x)} {f(y - 22*k)}Q{f(x + 16*k)} {f(y - 22*k)} {f(x + 16*k)} {f(y)}V{f(y + 24*k)}"
              + "".join(f"L{f(x + 16*k - (j + 1) * 32*k / 6)} {f(y + (18 if j % 2 == 0 else 24)*k)}" for j in range(6)) + "Z", "-")
    sh.ellipse_r(x - 6 * k, y - 6 * k, 3 * k, 4 * k, "x"); sh.ellipse_r(x + 6 * k, y - 6 * k, 3 * k, 4 * k, "x")
    sh.ellipse_r(x, y + 6 * k, 3.6 * k, 4.6 * k, "x")
def front_halloween(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 28, "Boe!", 26)
    sh.circle_r(156, y0 + 50, 16, "y")
    bx, by = 148, y0 + 48
    sh.region(f"M{bx} {by}Q{bx - 6} {by - 8} {bx - 14} {by - 6}Q{bx - 12} {by - 2} {bx - 16} {by + 2}Q{bx - 8} {by} {bx - 4} {by + 4}L{bx} {by + 1}L{bx + 4} {by + 4}Q{bx + 8} {by} {bx + 16} {by + 2}Q{bx + 12} {by - 2} {bx + 14} {by - 6}Q{bx + 6} {by - 8} {bx} {by}Z", "x")
    ghost(sh, 76, y0 + 82, 1.2)
    ghost(sh, 124, y0 + 92, .85)
    px, py = 40, y0 + 104
    sh.ellipse_r(px, py, 16, 12, "o"); sh.line(f"M{px} {py - 12}Q{px - 7} {py} {px} {py + 12}M{px} {py - 12}Q{px + 7} {py} {px} {py + 12}")
    sh.rect_r(px - 2, py - 18, 4, 6, "g", 1)
    sh.seg(20, y0 + 118, 180, y0 + 118)
card("halloweenkaart-spookjes", "Halloweenkaart met spookjes", front_halloween, "Fijne Halloween!", "feest", "6-9",
     ["Schrijf binnenin een griezelig (of grappig) berichtje."], holiday="halloween")

def front_maarten(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Fijne Sint-Maarten!", 14)
    sh.region(moon_path(46, y0 + 56, 14), "y")
    for x, y in [(80, y0 + 46), (28, y0 + 84), (176, y0 + 50), (66, y0 + 70)]:
        sh.poly_r(star_pts(x, y, 5, 2.2), "y")
    lx = 146
    sh.line(f"M30 {y0 + 120}L{lx - 8} {y0 + 40}Q{lx - 3} {y0 + 36} {lx} {y0 + 42}", "l", "stroke-width:2.2")
    sh.seg(lx, y0 + 42, lx, y0 + 58, "l", "stroke-width:1.2")
    cy = y0 + 84
    sh.rect_r(lx - 12, y0 + 58, 24, 6, "z", 2)
    sh.ellipse_r(lx, cy, 26, 21, "o")
    sh.ellipse_r(lx, cy, 15, 21, "y"); sh.ellipse_r(lx, cy, 5, 21, "o")
    sh.rect_r(lx - 12, cy + 19, 24, 6, "z", 2)
    sh.region(drop_path(116, cy + 2, 4), "-") if False else None
card("sint-maartenkaart-lampion", "Sint-Maartenkaart met lampion", front_maarten, "Zing je mee langs de deuren?", "feest", "4-6",
     ["Schrijf binnenin voor wie de kaart is, of welk liedje jij zingt."], holiday="sintmaarten")

def front_dieren(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Fijne Dierendag!", 15)
    dx, cy = 66, y0 + 76
    sh.ellipse_r(dx - 20, cy + 2, 8, 16, "w"); sh.ellipse_r(dx + 20, cy + 2, 8, 16, "w")
    sh.circle_r(dx, cy, 20, "o"); sh.ellipse_r(dx, cy + 10, 10, 7, "-")
    sh.ellipse_r(dx, cy + 5, 4, 3, "x"); sh.dot(dx - 8, cy - 5, 2.4); sh.dot(dx + 8, cy - 5, 2.4)
    sh.line(f"M{dx - 4} {cy + 12}Q{dx} {cy + 16} {dx + 4} {cy + 12}")
    cx = 134
    sh.poly_r([(cx - 18, cy - 8), (cx - 16, cy - 28), (cx - 4, cy - 16)], "z"); sh.poly_r([(cx + 18, cy - 8), (cx + 16, cy - 28), (cx + 4, cy - 16)], "z")
    sh.circle_r(cx, cy, 19, "z")
    sh.dot(cx - 7, cy - 3, 2.4); sh.dot(cx + 7, cy - 3, 2.4); sh.poly_r([(cx - 3, cy + 4), (cx + 3, cy + 4), (cx, cy + 7)], "k")
    sh.line(f"M{cx - 6} {cy + 8}L{cx - 22} {cy + 5}M{cx - 6} {cy + 11}L{cx - 22} {cy + 13}M{cx + 6} {cy + 8}L{cx + 22} {cy + 5}M{cx + 6} {cy + 11}L{cx + 22} {cy + 13}", "l", "stroke-width:1")
    sh.region(heart_path(100, y0 + 52, 8), "r")
    by = y0 + 110
    sh.region(f"M{dx - 14} {by - 2}H{dx + 14}A4 4 0 1 1 {dx + 16} {by + 2}A4 4 0 1 1 {dx + 14} {by + 6}H{dx - 14}A4 4 0 1 1 {dx - 16} {by + 2}A4 4 0 1 1 {dx - 14} {by - 2}Z", "-")
    sh.region(f"M{cx - 14} {by + 2}Q{cx - 2} {by - 8} {cx + 8} {by + 2}L{cx + 16} {by - 4}V{by + 8}L{cx + 8} {by + 2}Q{cx - 2} {by + 12} {cx - 14} {by + 2}Z", "b")
card("dierendagkaart-hond-en-kat", "Dierendagkaart met hond en kat", front_dieren, "Voor het liefste dier van de wereld!", "dieren", "4-6",
     ["Geef de kaart aan iemand met een huisdier, of hang hem op bij het hok of de mand van jouw dier."], holiday="dierendag")

def front_verhuis(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Nieuw huis!", 18)
    gy = y0 + 116
    sh.rect_r(124, y0 + 44, 8, 18, "r")
    sh.poly_r([(76, y0 + 66), (110, y0 + 38), (144, y0 + 66)], "r")
    sh.rect_r(82, y0 + 66, 56, gy - y0 - 66, "y")
    sh.rect_r(102, gy - 26, 16, 26, "w", 2); sh.dot(114, gy - 13, 1.4)
    sh.rect_r(88, y0 + 74, 12, 12, "b"); sh.rect_r(120, y0 + 74, 12, 12, "b")
    for x, y, bw, bh in [(26, gy - 22, 30, 22), (32, gy - 42, 24, 20), (58, gy - 18, 16, 18)]:
        sh.rect_r(x, y, bw, bh, "w"); sh.seg(x + bw / 2, y, x + bw / 2, y + 6, "l", "stroke-width:1.2")
    sh.rect_r(160, gy - 14, 14, 14, "o"); sh.circle_r(167, gy - 26, 12, "g")
    sh.seg(18, gy, 182, gy)
card("verhuiskaart-nieuw-huis", "Verhuiskaart: nieuw huis", front_verhuis, "Kom je een keer langs?", "thuis", "6-9",
     ["Schrijf binnenin jullie nieuwe adres en wanneer jullie verhuizen."])

def front_welkom(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Welkom thuis!", 17)
    gy = y0 + 116
    sh.rect_r(76, y0 + 42, 48, gy - y0 - 46, "w", 3)
    sh.rect_r(82, y0 + 48, 36, 26, "-", 2); sh.rect_r(82, y0 + 78, 36, 28, "-", 2)
    sh.region(heart_path(100, y0 + 61, 8), "r")
    sh.circle_r(114, y0 + 90, 2.4, "y")
    sh.rect_r(68, gy - 4, 64, 6, "o", 2)
    for bx, by, c, side in [(40, y0 + 56, "r", -1), (160, y0 + 56, "b", 1), (54, y0 + 76, "y", -1), (148, y0 + 80, "l", 1)]:
        sh.line(f"M{bx} {by + 15}Q{bx + side * 4} {(by + gy) / 2} {100 + side * 36} {gy - 2}", "l", "stroke-width:1")
        sh.ellipse_r(bx, by, 10, 13, c); sh.poly_r([(bx - 3, by + 15), (bx + 3, by + 15), (bx, by + 12)], c)
card("welkom-thuis-kaart", "Kaart: welkom thuis!", front_welkom, "Fijn dat je er weer bent!", "thuis", "4-6",
     ["Leg de kaart klaar voor iemand die thuiskomt: van vakantie, uit het ziekenhuis of van een lange reis."])

def front_sneeuwpop(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Vrolijk kerstfeest!", 14)
    gy = y0 + 116
    sh.region(f"M18 {gy}Q100 {gy - 10} 182 {gy}V{gy + 6}H18Z", "b")
    cx = 96
    sh.circle_r(cx, gy - 20, 21, "-"); sh.circle_r(cx, gy - 51, 13, "-")
    sh.rect_r(cx - 13, gy - 66, 26, 4, "x", 1); sh.rect_r(cx - 8, gy - 81, 16, 15, "x", 2); sh.rect_r(cx - 8, gy - 71, 16, 4, "r")
    sh.dot(cx - 5, gy - 55, 1.8); sh.dot(cx + 5, gy - 55, 1.8)
    sh.poly_r([(cx, gy - 51), (cx + 13, gy - 48), (cx, gy - 47)], "o")
    sh.region(f"M{cx - 14} {gy - 41}Q{cx} {gy - 35} {cx + 14} {gy - 41}V{gy - 35}Q{cx} {gy - 29} {cx - 14} {gy - 35}Z", "g")
    sh.rect_r(cx + 5, gy - 34, 6, 14, "g", 1)
    for y in (gy - 26, gy - 16): sh.dot(cx, y, 2)
    sh.line(f"M{cx - 20} {gy - 26}L{cx - 36} {gy - 40}M{cx - 30} {gy - 35}L{cx - 34} {gy - 30}M{cx + 20} {gy - 26}L{cx + 36} {gy - 40}M{cx + 30} {gy - 35}L{cx + 34} {gy - 30}")
    sh.rect_r(136, gy - 24, 24, 20, "r", 2); sh.rect_r(146, gy - 24, 4, 20, "y"); sh.region(f"M148 {gy - 24}Q140 {gy - 34} 138 {gy - 26}ZM148 {gy - 24}Q156 {gy - 34} 158 {gy - 26}Z", "y")
    sh.rect_r(162, gy - 16, 16, 12, "n", 2)
    for x, y in [(34, y0 + 48), (164, y0 + 52), (40, y0 + 84), (150, y0 + 78)]:
        sh.line(f"M{x - 5} {y}H{x + 5}M{x} {y - 5}V{y + 5}M{x - 3.5} {y - 3.5}L{x + 3.5} {y + 3.5}M{x - 3.5} {y + 3.5}L{x + 3.5} {y - 3.5}", "l", "stroke-width:1.1")
card("kerstkaart-sneeuwpop", "Kerstkaart met sneeuwpop", front_sneeuwpop, "Warme wensen voor de feestdagen!", "feest", "4-6",
     ["Schrijf binnenin een kerstwens voor iemand die je lief vindt."], holiday="kerst")

# =====================================================================
# 2. DECORATIES
# =====================================================================

def letterslinger():
    sh = Sheet()
    title(sh, "Letterslinger: HOERA!", 14)
    sh.text(100, 25, "Knip de vlaggen uit en hang ze in de goede volgorde aan een touw.", 5.5)
    letters_ = ["H", "O", "E", "R", "A", "!"]
    for i, ch in enumerate(letters_):
        col, row = i % 3, i // 3
        x, y, w = 13 + col * 60, 32 + row * 120, 54
        flap = 12; b = y + flap
        sh.line(f"M{x} {y}H{x + w}V{b + 96}L{x + w / 2} {b + 80}L{x} {b + 96}Z", "cut")
        sh.seg(x, b, x + w, b, "fold")
        sh.raw(f'<rect class="glue" x="{x + 2}" y="{y + 2}" width="{w - 4}" height="{flap - 4}"/>')
        sh.region(f"M{x} {b}H{x + w}V{b + 96}L{x + w / 2} {b + 80}L{x} {b + 96}Z", "oytmlb"[i])
        sh.region(f"M{x + 7} {b + 8}H{x + w - 7}V{b + 66}H{x + 7}Z", "-") if False else None
        sh.circle_r(x + w / 2, b + 40, 21, "-")
        outline_text(sh, x + w / 2, b + 53, ch, 36)
        for k in range(4):
            sh.dot(x + 8 + k * (w - 16) / 3, b + 8, 1.6)
        sh.poly_r(star_pts(x + w / 2, b + 72, 5, 2.2), "y")
    sh.legend(["cut", "fold", "glue"], 276)
    write(OUT, "letterslinger-hoera", sh, {"category": "feest", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 25, "holiday": "verjaardag",
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}, {"slug": "touw"}],
        "i18n": {"nl": {"name": "Letterslinger: HOERA!", "steps": [
            "Kleur de vlaggen in, en de letters in een kleur die goed opvalt.",
            "Knip de vlaggen uit langs de streepjeslijn.",
            "Leg ze op volgorde: H, O, E, R, A en het uitroepteken.",
            "Leg een touw langs de stippellijnen, smeer lijm op de grijze randjes en vouw ze over het touw.",
            "Hang de slinger op bij het feest."]}}})
letterslinger()

def placemat():
    sh = Sheet()
    # liggend ontwerp (280 breed, 200 hoog) gedraaid op het staande vel
    sh.raw('<g transform="translate(200 0) rotate(90)">')
    sh.rect_line(6, 6, 268, 188, "cut", 8)
    for k in range(22):
        x = 18 + k * 11.6
        sh.circle_r(x, 14, 3.2, "ryg"[k % 3]); sh.circle_r(x, 186, 3.2, "gyr"[k % 3])
    for k in range(13):
        y = 26 + k * 12.3
        sh.circle_r(14, y, 3.2, "ygr"[k % 3]); sh.circle_r(266, y, 3.2, "rgy"[k % 3])
    outline_text(sh, 140, 40, "Eet smakelijk!", 18)
    sh.circle_r(140, 112, 50, "b"); sh.circle_r(140, 112, 37, "-")
    sh.text(140, 116, "mijn bord", 7)
    fx = 72
    sh.region(f"M{fx - 9} 70V88Q{fx - 9} 96 {fx - 2} 98V154Q{fx} 158 {fx + 2} 154V98Q{fx + 9} 96 {fx + 9} 88V70H{fx + 6}V88H{fx + 2}V70H{fx - 2}V88H{fx - 6}V70Z", "z")
    kx = 212
    sh.region(f"M{kx - 3} 154V70Q{kx + 9} 76 {kx + 8} 108L{kx + 3} 110V154Q{kx} 158 {kx - 3} 154Z", "z")
    sh.region(f"M224 32H252L248 60H228Z", "t"); sh.region("M228 40H248L247 48H229Z", "b")
    # fruit in de hoeken
    sh.region("M36 34C26 28 20 38 22 46C24 56 32 58 36 55C40 58 48 56 50 46C52 38 46 28 36 34Z", "r")
    sh.line("M36 34Q36 28 39 24"); sh.region("M38 29Q44 22 50 26Q44 32 38 29Z", "g")
    sh.region("M20 176Q32 162 38 148Q46 142 52 150Q46 162 20 176Z", "o"); sh.line("M30 164L34 166M36 156L40 158")
    sh.line("M44 146L42 136M47 146L52 137M50 148L59 144")
    sh.region("M240 152C228 152 226 172 240 178C254 172 252 152 240 152Z", "r"); sh.region("M232 152Q240 146 248 152Q240 156 232 152Z", "g")
    for dx, dy in [(-4, 160), (4, 162), (0, 170), (-6, 168), (6, 170)]: sh.dot(240 + dx, dy, .9)
    sh.text(104, 178, "Naam: ......................", 7)
    sh.raw("</g>")
    write(OUT, "placemat-eet-smakelijk", sh, {"category": "eten", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 20,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "stiften", "optional": True}],
        "i18n": {"nl": {"name": "Placemat om te kleuren: eet smakelijk!", "printNote": "Print liggend. Wil je hem vaker gebruiken? Schuif hem in een insteekhoes of laat hem plastificeren.", "steps": [
            "Schrijf je naam op de placemat.",
            "Kleur het bord, het bestek, de beker en het fruit in.",
            "Maak de rand vrolijk met de rondjes in drie kleuren.",
            "Leg de placemat op tafel: zet je bord op het bord en je bestek op het bestek!"]}}})
placemat()

def winterlabels():
    sh = Sheet()
    title(sh, "Cadeaulabels: winter", 14)
    def want(cx, cy):
        sh.region(f"M{cx - 7} {cy + 6}V{cy - 4}Q{cx - 7} {cy - 12} {cx} {cy - 12}Q{cx + 7} {cy - 12} {cx + 7} {cy - 4}V{cy + 6}Z", "r")
        sh.region(f"M{cx - 7} {cy - 2}Q{cx - 13} {cy - 6} {cx - 12} {cy - 1}Q{cx - 11} {cy + 3} {cx - 7} {cy + 2}Z", "r")
        sh.rect_r(cx - 8, cy + 6, 16, 5, "-", 1)
    def vlok(cx, cy):
        for k in range(6):
            a = math.radians(k * 60)
            ex, ey = cx + 11 * math.cos(a), cy + 11 * math.sin(a)
            sh.seg(cx, cy, ex, ey, "l", "stroke-width:1.4")
            mx, my = cx + 7 * math.cos(a), cy + 7 * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(40)
                sh.seg(mx, my, mx + 3.5 * math.cos(b), my + 3.5 * math.sin(b), "l", "stroke-width:1.2")
    def muts(cx, cy):
        sh.region(f"M{cx - 11} {cy + 6}Q{cx - 11} {cy - 10} {cx} {cy - 10}Q{cx + 11} {cy - 10} {cx + 11} {cy + 6}Z", "b")
        sh.rect_r(cx - 12, cy + 4, 24, 6, "n", 2); sh.circle_r(cx, cy - 12, 4, "-")
    def bal(cx, cy):
        sh.rect_r(cx - 3, cy - 13, 6, 4, "y"); sh.circle_r(cx, cy, 10, "r")
        sh.line(f"M{cx - 10} {cy}Q{cx - 5} {cy - 4} {cx} {cy}T{cx + 10} {cy}", "l", "stroke-width:1.2")
    def ster(cx, cy): sh.poly_r(star_pts(cx, cy, 12, 5), "y")
    def boom(cx, cy):
        sh.poly_r([(cx, cy - 12), (cx + 10, cy + 6), (cx - 10, cy + 6)], "g"); sh.rect_r(cx - 2, cy + 6, 4, 5, "w")
        sh.dot(cx - 3, cy, 1.4); sh.dot(cx + 3, cy + 3, 1.4)
    decos = [want, vlok, muts, bal, ster, boom]
    for i, d in enumerate(decos):
        col, row = i % 2, i // 2
        cx, cy = 56 + col * 88, 68 + row * 82
        sh.circle_line(cx, cy, 38, "cut")
        sh.circle_line(cx, cy - 28.5, 2.4, "cut")
        sh.circle_line(cx, cy, 34, "l", "stroke-width:.8")
        d(cx, cy - 9)
        sh.text(cx, cy + 13, "Voor: ..............", 6)
        sh.text(cx, cy + 23, "Van: .............", 6)
    sh.legend(["cut"], 274)
    write(OUT, "cadeaulabels-winter", sh, {"category": "feest", "age": "6-9", "kind": "kaart", "difficulty": 1, "minutes": 15, "paperGsm": 160, "holiday": "kerst",
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}],
        "i18n": {"nl": {"name": "Ronde cadeaulabels met winterplaatjes", "printNote": "Print op stevig papier (160 gram) als je het hebt.", "steps": [
            "Kleur de plaatjes en schrijf op voor wie het cadeau is en van wie.",
            "Knip de rondjes uit langs de streepjeslijn.",
            "Prik een gaatje in het kleine rondje (vraag een volwassene om hulp) en bind het label met touw of lint aan het cadeau."]}}})
winterlabels()

# =====================================================================
# 3. TEKENLESSEN IN ZES STAPPEN
# =====================================================================

lesson("tekenles-paard", "Tekenles: een paard", [
    [E(46, 54, 26, 15)],
    ["M62 42.2Q66 28 74 16M70 60Q80 46 86 30", "M74 16Q80 8 88 12L97 26Q98 32 92 32L86 30"],
    ["M24 62V94H30V65.8M34 67.3V94H40V68.6M56 67.8V94H62V65.8M64 64.8V94H70V59.8"],
    ["M74 15Q66 20 66 28Q62 32 62 40", "M20 50Q8 54 10 76Q16 68 22 60"],
    [C(85, 18, 1.6), "M80 12L80 3L85 10", C(94, 27, 1)],
    ["M2 95H98", "M84 95Q86 88 90 86M88 95Q90 90 94 90"]], [
    "Teken een liggend ovaal: het lijf.", "Een lange hals schuin omhoog en een hoofd met een lange neus.",
    "Vier lange benen met een plat stukje onderaan.", "Manen in de nek en een golvende staart.",
    "Een oog, een puntig oor en een neusgat.", "De grond met een paar sprietjes gras."], "6-9", 2, "boerderij")

def _spikes():
    pts = []
    for i in range(15):
        a = math.radians(180 - i * (130 / 14)); r = 1.0 if i % 2 == 0 else 1.28
        pts.append((50 + 36 * r * math.cos(a), 80 - 38 * r * math.sin(a)))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
lesson("tekenles-egel", "Tekenles: een egel", [
    ["M14 80A36 38 0 0 1 80 59"],
    ["M80 59Q90 66 97 75Q97 80 90 80H14"],
    [_spikes()],
    [C(83, 66, 1.8), C(96, 76, 2.2)],
    ["M28 80V86H36V80M62 80V86H70V80"],
    [C(46, 28, 7), "M46 21V16", "M4 88H98"]], [
    "Teken een grote boog: de rug.", "Een spits snuitje rechts en een rechte buik.",
    "Zigzag stekels over de hele rug.", "Een oogje en een rond neusje.", "Twee korte pootjes.", "Een appel op de stekels en de grond."], "4-6", 1, "dieren")

lesson("tekenles-vrachtwagen", "Tekenles: een vrachtwagen", [
    ["M6 28H62V70H6Z"],
    ["M62 40H82L96 56V70H62"],
    [C(22, 74, 8), C(80, 74, 8)],
    ["M68 46H80L89 56H68Z"],
    [C(22, 74, 3), C(80, 74, 3), "M91 62H96M70 62H76"],
    ["M2 86H98", "M10 92H22M40 92H52M70 92H82"]], [
    "Teken een grote rechthoek: de laadbak.", "Een cabine rechts met een schuine voorkant.",
    "Twee grote wielen.", "Een raam in de cabine.", "Doppen op de wielen, een lamp en een handvat.", "De weg met strepen."], "4-6", 1, "voertuigen")

lesson("tekenles-zeilboot", "Tekenles: een zeilboot", [
    ["M10 62H92L80 78H22Z"],
    ["M50 62V6"],
    ["M53 10Q74 32 86 58H53Z"],
    ["M47 18V58H20Z"],
    ["M50 6L62 10L50 14", C(34, 70, 2.5), C(50, 70, 2.5), C(66, 70, 2.5)],
    ["M2 84Q10 78 18 84T34 84T50 84T66 84T82 84T98 84", C(14, 16, 7)]], [
    "Teken de romp: een brede vorm die onderaan smaller wordt.", "Een lange mast recht omhoog.",
    "Een groot zeil rechts van de mast.", "Een kleiner zeil links.", "Een vlaggetje bovenin en ronde raampjes.", "Golven en een zon."], "4-6", 1, "voertuigen")

lesson("tekenles-dinosaurus", "Tekenles: een dinosaurus met lange nek", [
    [E(48, 60, 26, 16)],
    ["M64 47.4Q76 36 75 19M74 60Q88 48 89 22.5", E(85, 16, 11, 7)],
    ["M24 54Q8 58 2 74Q14 70 26 66"],
    ["M32 72.6V92H40V75.2M56 75.2V92H64V72.6"],
    [C(89, 13, 1.5), "M88 19Q92 20 95 17", C(42, 54, 4), C(54, 50, 3), C(58, 62, 3)],
    ["M2 93H98", "M80 93V74M80 74Q72 70 68 76M80 74Q88 68 94 74M80 74Q78 66 72 66M80 74Q84 66 90 66"]], [
    "Teken een groot ovaal lijf.", "Een lange nek omhoog met een klein hoofd.", "Een lange staart naar links.",
    "Vier dikke poten (je ziet er twee).", "Een oog, een lachje en vlekken.", "De grond en een palmboom."], "6-9", 2, "dinos")

lesson("tekenles-pinguin", "Tekenles: een pinguïn", [
    ["M50 16C72 16 78 50 76 70C74 86 26 86 24 70C22 50 28 16 50 16Z"],
    ["M50 32C62 32 64 56 62 70C60 80 40 80 38 70C36 56 38 32 50 32Z"],
    ["M26 44Q12 58 18 72Q24 62 26 56M74 44Q88 58 82 72Q76 62 74 56"],
    [C(43, 28, 2), C(57, 28, 2), "M45 34L50 40L55 34Z"],
    [E(40, 86, 8, 3), E(60, 86, 8, 3)],
    ["M6 90H94L88 98H12Z", C(10, 14, 1.5), C(88, 10, 1.5), C(92, 34, 1.5)]], [
    "Teken een groot eivormig lijf.", "Een witte buik in het midden.", "Twee vleugels aan de zijkant.",
    "Twee ogen en een snavel.", "Twee platte voeten.", "Een ijsschots en sneeuwvlokjes."], "4-6", 1, "dieren")

lesson("tekenles-kasteel", "Tekenles: een kasteel", [
    ["M24 40H76V94H24Z"],
    ["M8 30H24V94H8ZM76 30H92V94H76Z"],
    ["M6 30L16 10L26 30M74 30L84 10L94 30"],
    ["M24 40V33H33V40M45.5 40V33H54.5V40M67 40V33H76V40"],
    ["M42 94V74Q50 64 58 74V94", "M14 44H18V54H14ZM82 44H86V54H82Z", "M46 50H54V58H46Z"],
    ["M16 10V2L24 5L16 8M84 10V2L92 5L84 8", "M2 94H98"]], [
    "Teken een grote rechthoek: de muur.", "Twee hoge torens links en rechts.", "Puntdaken op de torens.",
    "Kantelen bovenop de muur.", "Een poort en raampjes.", "Vlaggetjes op de torens en de grond."], "6-9", 2, "sprookjes")

lesson("tekenles-robot", "Tekenles: een robot", [
    ["M28 44H72V80H28Z"],
    ["M36 16H64V38H36Z", "M46 38V44M54 38V44"],
    ["M50 16V8", C(50, 6, 3), C(44, 26, 3.5), C(56, 26, 3.5)],
    ["M43 33H57", "M38 52H62V68H38Z", C(44, 74, 2), C(56, 74, 2)],
    ["M28 50H16V66M12 66Q16 72 20 66M72 50H84V36M80 36Q84 30 88 36"],
    ["M36 80V94H46V80M54 80V94H64V80", "M30 96H50M50 96H70"]], [
    "Teken een vierkant lijf.", "Een hoofd erop met een korte nek.", "Een antenne en twee ronde ogen.",
    "Een mond en een paneel met knopjes.", "Armen met grijpers: een omlaag, een omhoog.", "Benen met voeten."], "4-6", 1, "ruimte")

# =====================================================================
# 4. MAAK DE TEKENING AF
# =====================================================================

def afmaak(slug, name, panels, cat, age, intro):
    sh = Sheet()
    title(sh, cap(name.split(": ", 1)[-1]), 16)
    sh.text(100, 26, intro, 6)
    for i, (prompt, draw) in enumerate(panels):
        col, row = i % 2, i // 2
        x, y, w, h = 12 + col * 90, 32 + row * 120, 86, 114
        sh.rect_line(x, y, w, h, "l", 4, "stroke-width:.8")
        for j, ln in enumerate(prompt.split("|")):
            sh.text(x + w / 2, y + 10 + j * 7.5, ln, 6)
        draw(sh, x, y, w, h)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "tekenles", "difficulty": 1, "minutes": 20,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": name, "steps": [
            "Lees de opdracht boven elk vak, of laat hem voorlezen.",
            "Teken erbij wat er nog mist. Er is geen goed of fout: verzin het zelf!",
            "Kleur daarna alles in."]}}})

def p_ballon(sh, x, y, w, h):
    kx, ky = x + w / 2, y + h - 14
    for k, (ex, ey) in enumerate([(-28, 44), (-12, 34), (6, 40), (22, 32), (30, 50)]):
        sh.line(f"M{kx} {ky}Q{kx + ex * .3} {ky - 30} {kx + ex} {y + ey}", "l", "stroke-width:1")
        sh.poly_r([(kx + ex - 2, y + ey + 2.5), (kx + ex + 2, y + ey + 2.5), (kx + ex, y + ey - .5)], "-")
    sh.region(f"M{kx} {ky}l-6 -3v6Zm0 0l6 -3v6Z", "r")
def p_taart(sh, x, y, w, h):
    cx, by = x + w / 2, y + h - 14
    sh.ellipse_r(cx, by, 38, 6, "-")
    sh.region(f"M{cx - 30} {by - 2}V{by - 24}H{cx + 30}V{by - 2}Z", "-")
    sh.region(f"M{cx - 22} {by - 24}V{by - 42}H{cx + 22}V{by - 24}Z", "-")
def p_cadeau(sh, x, y, w, h):
    cx, by = x + w / 2, y + h - 12
    sh.rect_r(cx - 24, by - 40, 48, 40, "-")
    sh.rect_r(cx - 4, by - 40, 8, 40, "-")
    sh.raw(f'<g transform="rotate(-24 {cx + 26} {by - 46})">'); sh.rect_r(cx - 4, by - 56, 32, 10, "-", 1); sh.raw("</g>")
def p_hoed(sh, x, y, w, h):
    cx, cy = x + w / 2, y + h - 34
    sh.region(f"M{cx - 30} {y + h - 2}Q{cx - 30} {cy + 18} {cx} {cy + 18}Q{cx + 30} {cy + 18} {cx + 30} {y + h - 2}Z", "-")
    sh.circle_r(cx, cy, 20, "-")
    sh.dot(cx - 7, cy - 2, 2.2); sh.dot(cx + 7, cy - 2, 2.2); sh.line(f"M{cx - 7} {cy + 7}Q{cx} {cy + 13} {cx + 7} {cy + 7}")
    sh.region(f"M{cx - 20} {cy - 2}Q{cx - 20} {cy - 20} {cx} {cy - 20}Q{cx + 20} {cy - 20} {cx + 20} {cy - 2}Q{cx + 10} {cy - 12} {cx} {cy - 12}Q{cx - 10} {cy - 12} {cx - 20} {cy - 2}Z", "-")
afmaak("maak-af-feestje", "Maak de tekening af: feestje", [
    ("Teken ballonnen|aan de touwtjes.", p_ballon), ("Versier de taart|en zet er kaarsjes op.", p_taart),
    ("Wat zit er|in het cadeau?", p_cadeau), ("Zet een feestmuts|op zijn hoofd.", p_hoed)], "feest", "4-6",
    "In elk vak mist nog iets. Teken het erbij!")

def p_vlinder(sh, x, y, w, h):
    cx, cy = x + w / 2, y + 66
    sh.ellipse_r(cx, cy, 4, 24, "-"); sh.circle_r(cx, cy - 28, 5, "-")
    sh.line(f"M{cx - 2} {cy - 32}Q{cx - 8} {cy - 42} {cx - 14} {cy - 42}M{cx + 2} {cy - 32}Q{cx + 8} {cy - 42} {cx + 14} {cy - 42}", "l", "stroke-width:1.2")
def p_kom(sh, x, y, w, h):
    cx, cy = x + w / 2, y + 70
    sh.line(f"M{cx - 22} {cy - 34}Q{cx - 44} {cy - 10} {cx - 34} {cy + 16}Q{cx - 26} {cy + 34} {cx} {cy + 34}Q{cx + 26} {cy + 34} {cx + 34} {cy + 16}Q{cx + 44} {cy - 10} {cx + 22} {cy - 34}")
    sh.ellipse_r(cx, cy - 34, 22, 4, "-")
    sh.line(f"M{cx - 35} {cy - 14}Q{cx - 18} {cy - 18} {cx} {cy - 14}T{cx + 35} {cy - 14}", "l", "stroke-width:1")
    sh.region(f"M{cx - 30} {cy + 24}Q{cx} {cy + 16} {cx + 30} {cy + 24}Q{cx + 20} {cy + 34} {cx} {cy + 34}Q{cx - 20} {cy + 34} {cx - 30} {cy + 24}Z", "y")
    sh.line(f"M{cx + 16} {cy + 22}Q{cx + 10} {cy + 10} {cx + 16} {cy}Q{cx + 22} {cy - 6} {cx + 18} {cy - 10}", "l", "stroke-width:1.4")
def p_boom(sh, x, y, w, h):
    cx = x + w / 2
    sh.region(f"M{cx - 12} {y + h - 6}V{y + 60}L{cx - 30} {y + 30}M{cx - 12} {y + 60}", "-") if False else None
    sh.region(f"M{cx - 13} {y + h - 6}L{cx - 10} {y + 58}L{cx - 32} {y + 34}L{cx - 26} {y + 30}L{cx - 4} {y + 50}L{cx - 2} {y + 26}H{cx + 4}L{cx + 6} {y + 48}L{cx + 26} {y + 30}L{cx + 30} {y + 36}L{cx + 10} {y + 58}L{cx + 13} {y + h - 6}Z", "w")
    sh.ellipse_r(cx, y + 78, 7, 9, "x")
    sh.seg(x + 6, y + h - 6, x + w - 6, y + h - 6)
def p_moestuin(sh, x, y, w, h):
    for k in range(3):
        yy = y + 50 + k * 22
        sh.region(f"M{x + 8} {yy + 8}Q{x + w / 2} {yy - 4} {x + w - 8} {yy + 8}Z", "w")
        for j in range(4):
            sx = x + 18 + j * 17; t = (sx - x - 8) / (w - 16); base = yy + 8 - 24 * t * (1 - t)
            sh.line(f"M{f(sx)} {f(base)}V{f(base - 7)}", "l", "stroke-width:1.2")
    sh.circle_r(x + w - 14, y + 28, 7, "y")
afmaak("maak-af-natuur", "Maak de tekening af: in de natuur", [
    ("Teken de vleugels|van de vlinder.", p_vlinder), ("Wat zwemt er|in de vissenkom?", p_kom),
    ("Wie woont er|in het gat in de boom?", p_boom), ("Wat groeit er|in de moestuin?", p_moestuin)], "natuur", "4-6",
    "In elk vak mist nog iets. Teken het erbij!")

# =====================================================================
# 5. TEKEN DE ANDERE HELFT (vrij, zonder hokjes)
# =====================================================================

HALVES = [
    ("kat", ["M0 30Q-28 30 -31 6Q-33 -10 -27 -20L-30 -40L-13 -28Q-6 -30 0 -30", C(-12, -6, 4), "M0 7L-4 3H0", "M-10 12L-30 8M-10 16L-30 18", "M0 9Q-3 15 -8 13"]),
    ("lieveheersbeestje", ["M0 -24Q-30 -24 -30 6Q-30 32 0 32", "M0 -24Q-13 -24 -13 -33Q-13 -42 0 -42", "M-6 -40L-13 -50", C(-14, -51, 2), C(-16, -6, 5), C(-14, 16, 4), "M-27 -6L-38 -12M-30 8L-40 8M-26 22L-36 30"]),
    ("raket", ["M0 -46Q-16 -30 -16 0V28H0", "M-16 8L-28 26V36L-16 28", "M0 -20A8 8 0 0 0 0 -4", "M-8 28Q-10 38 -4 44Q-2 38 0 46"]),
    ("pompoen", ["M0 -24Q-10 -30 -24 -26Q-40 -20 -40 4Q-40 30 -20 32Q-8 34 0 30", "M-14 -26Q-24 2 -12 32", "M0 -24V-34H-4", "M-6 -6H-18L-12 -14Z", "M0 12H-20Q-14 22 0 22"]),
]
def andere_helft():
    def page(full):
        sh = Sheet()
        title(sh, "Zo zien ze er heel uit" if full else "Teken de andere helft", 16)
        if not full: sh.text(100, 26, "De stippellijn is een spiegel. Teken rechts de andere helft.", 5.6)
        for i, (_, paths) in enumerate(HALVES):
            col, row = i % 2, i // 2
            bx, by = 12 + col * 90, 34 + row * 116
            sh.rect_line(bx, by, 86, 110, "l", 4, "stroke-width:.8")
            cx, cy = bx + 43, by + 58
            sh.seg(cx, by + 6, cx, by + 104, "l", "stroke-width:.8;stroke-dasharray:3 3")
            for d in paths:
                sh.raw(f'<path class="l" style="stroke-width:1.8" transform="translate({cx} {cy})" d="{d}" fill="none"/>')
                if full: sh.raw(f'<path class="l" style="stroke-width:1.8" transform="translate({cx} {cy}) scale(-1 1)" d="{d}" fill="none"/>')
        return sh
    write(OUT, "teken-de-andere-helft", page(False), {"category": "leren", "age": "6-9", "kind": "tekenles", "difficulty": 2, "minutes": 15,
        "materials": POTLOOD,
        "i18n": {"nl": {"name": "Teken de andere helft: kat, lieveheersbeestje, raket en pompoen", "steps": [
            "Kijk goed naar de halve tekening links van de stippellijn.",
            "Teken rechts precies hetzelfde, maar dan gespiegeld. Wat links naar links wijst, wijst rechts naar rechts.",
            "Begin met de grote lijnen en teken daarna de kleine dingen, zoals ogen en stippen.",
            "Klaar? Kleur de tekeningen in. Op de tweede bladzijde zie je hoe ze heel worden."]}}},
        [("extra", "Zo zien ze er heel uit", page(True))])
andere_helft()

# =====================================================================
# 6. SJABLONEN (alleen een buitenvorm, geen losse binnenstukjes)
# =====================================================================

def T(points, x, y): return P([(x + a, y + b) for a, b in points])
def langnek(x, y): return (f"M{x - 34} {y + 8}Q{x - 22} {y - 4} {x - 8} {y - 6}Q{x + 4} {y - 10} {x + 10} {y - 6}Q{x + 14} {y - 20} {x + 18} {y - 26}"
    f"Q{x + 22} {y - 32} {x + 28} {y - 30}Q{x + 34} {y - 28} {x + 30} {y - 23}Q{x + 26} {y - 22} {x + 24} {y - 18}Q{x + 22} {y - 6} {x + 20} {y + 2}"
    f"Q{x + 22} {y + 8} {x + 18} {y + 12}V{y + 26}H{x + 11}V{y + 14}H{x - 4}V{y + 26}H{x - 11}V{y + 12}Q{x - 22} {y + 12} {x - 34} {y + 8}Z")
def trex(x, y): return T([(-34, 6), (-14, -6), (0, -10), (6, -20), (10, -26), (28, -26), (31, -20), (24, -17), (29, -12), (15, -12), (12, -6), (16, -2), (19, 1), (13, 1), (9, 4), (8, 12),
    (12, 26), (4, 26), (0, 16), (-6, 14), (-4, 26), (-12, 26), (-12, 10), (-20, 6)], x, y)
def stego(x, y):
    pts = [(-34, 12)]
    for k, (px, py) in enumerate([(-24, 2), (-18, -14), (-12, -2), (-6, -22), (0, -6), (6, -24), (12, -6), (18, -16), (22, -2)]): pts.append((px, py))
    pts += [(28, 0), (33, 6), (28, 10), (22, 10), (20, 24), (13, 24), (12, 14), (-6, 14), (-8, 24), (-15, 24), (-16, 14), (-24, 14)]
    return T(pts, x, y)
def tricera(x, y): return T([(-34, 8), (-24, -6), (-6, -12), (2, -12), (4, -20), (12, -26), (18, -22), (25, -30), (24, -18), (30, -14), (32, -20), (34, -10), (36, -4), (28, 0), (20, 4), (18, 12), (18, 24), (11, 24), (10, 14), (-8, 14), (-8, 24), (-15, 24), (-16, 12), (-24, 10)], x, y)
def ptero(x, y): return T([(-34, -10), (-10, -4), (-2, -8), (2, -16), (10, -22), (6, -14), (16, -14), (8, -8), (4, -2), (34, -10), (14, 6), (4, 6), (2, 18), (-2, 6), (-14, 6)], x, y)
def voetafdruk(x, y): return (f"M{x - 12} {y + 26}Q{x - 22} {y + 14} {x - 14} {y}L{x - 28} {y - 18}Q{x - 30} {y - 26} {x - 22} {y - 24}L{x - 6} {y - 6}L{x - 6} {y - 26}Q{x} {y - 34} {x + 6} {y - 26}"
    f"L{x + 6} {y - 6}L{x + 22} {y - 24}Q{x + 30} {y - 26} {x + 28} {y - 18}L{x + 14} {y}Q{x + 22} {y + 14} {x + 12} {y + 26}Z")
stencil("sjablonen-dinos", "Sjablonen: dino's", [langnek, trex, stego, tricera, ptero, voetafdruk], "dinos", "6-9")

def koe(x, y): return T([(-34, -14), (-30, -12), (16, -12), (18, -20), (22, -14), (30, -14), (34, -4), (30, 2), (22, 0), (20, 10), (20, 24), (13, 24), (12, 12), (2, 12), (-2, 16), (-8, 12), (-16, 12),
    (-16, 24), (-23, 24), (-24, 10), (-28, 4), (-30, -8), (-34, 6), (-36, 4)], x, y)
def varken(x, y): return (f"M{x - 26} {y + 12}V{y + 24}H{x - 18}V{y + 16}H{x + 8}V{y + 24}H{x + 16}V{y + 12}Q{x + 22} {y + 6} {x + 24} {y}H{x + 32}V{y - 10}H{x + 24}"
    f"Q{x + 22} {y - 16} {x + 18} {y - 18}L{x + 20} {y - 26}L{x + 10} {y - 20}Q{x - 6} {y - 26} {x - 22} {y - 18}Q{x - 30} {y - 14} {x - 30} {y - 4}L{x - 36} {y - 10}L{x - 32} {y + 2}Q{x - 30} {y + 8} {x - 26} {y + 12}Z")
def kip(x, y): return T([(-28, -12), (-18, -2), (-4, 0), (8, -8), (8, -20), (12, -26), (14, -22), (18, -28), (20, -22), (24, -22), (22, -16), (30, -12), (22, -8), (20, 2), (14, 14), (6, 18), (6, 24), (12, 26), (0, 26), (-2, 18),
    (-10, 18), (-10, 26), (-16, 26), (-16, 16), (-24, 8), (-30, -4), (-34, -16)], x, y)
def schaap(x, y):
    d = f"M{x - 24} {y + 10}"
    pts = [(-24, 10), (-30, 0), (-24, -12), (-10, -18), (4, -16), (16, -12), (22, 0), (16, 10)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        d += f"A7 7 0 0 1 {x + bx} {y + by}"
    d += f"L{x + 22} {y - 6}L{x + 32} {y - 4}L{x + 32} {y + 6}L{x + 24} {y + 10}L{x + 14} {y + 12}V{y + 26}H{x + 8}V{y + 14}H{x - 12}V{y + 26}H{x - 18}V{y + 12}Z"
    return d
def eend(x, y): return (f"M{x - 30} {y - 2}L{x - 22} {y + 2}Q{x - 22} {y - 6} {x - 8} {y - 4}Q{x + 6} {y - 4} {x + 8} {y - 10}Q{x + 2} {y - 18} {x + 8} {y - 26}"
    f"Q{x + 16} {y - 32} {x + 22} {y - 24}L{x + 32} {y - 22}L{x + 24} {y - 16}Q{x + 18} {y - 12} {x + 22} {y - 2}Q{x + 26} {y + 12} {x + 8} {y + 18}H{x - 18}Q{x - 30} {y + 14} {x - 30} {y - 2}Z")
def konijn(x, y): return (f"M{x - 22} {y + 26}Q{x - 30} {y + 6} {x - 14} {y - 4}Q{x - 2} {y - 8} {x + 8} {y - 6}Q{x + 2} {y - 14} {x + 8} {y - 18}L{x + 4} {y - 32}Q{x + 6} {y - 36} {x + 10} {y - 32}L{x + 14} {y - 20}"
    f"L{x + 18} {y - 32}Q{x + 21} {y - 35} {x + 23} {y - 31}L{x + 22} {y - 18}Q{x + 28} {y - 12} {x + 22} {y - 4}Q{x + 18} {y + 2} {x + 14} {y + 4}Q{x + 18} {y + 16} {x + 12} {y + 26}Z")
stencil("sjablonen-boerderijdieren", "Sjablonen: boerderijdieren", [koe, varken, kip, schaap, eend, konijn], "boerderij", "6-9")

def ballon(x, y): return f"M{x} {y - 30}C{x + 20} {y - 30} {x + 24} {y - 8} {x + 15} {y + 6}Q{x + 8} {y + 15} {x + 2} {y + 17}L{x + 6} {y + 26}H{x - 6}L{x - 2} {y + 17}Q{x - 8} {y + 15} {x - 15} {y + 6}C{x - 24} {y - 8} {x - 20} {y - 30} {x} {y - 30}Z"
def cadeau(x, y): return (f"M{x - 24} {y + 26}V{y - 6}H{x - 6}Q{x - 22} {y - 10} {x - 20} {y - 22}Q{x - 16} {y - 30} {x} {y - 12}Q{x + 16} {y - 30} {x + 20} {y - 22}Q{x + 22} {y - 10} {x + 6} {y - 6}H{x + 24}V{y + 26}Z")
def kroon(x, y): return T([(-30, 20), (-30, -16), (-15, 0), (0, -26), (15, 0), (30, -16), (30, 20)], x, y)
def muts(x, y): return f"M{x - 22} {y + 26}L{x - 3} {y - 16}A8 8 0 1 1 {x + 3} {y - 16}L{x + 22} {y + 26}Z"
def ijsje(x, y): return f"M{x - 16} {y - 4}L{x} {y + 30}L{x + 16} {y - 4}A9 9 0 0 0 {x + 10} {y - 18}A11 11 0 0 0 {x - 10} {y - 18}A9 9 0 0 0 {x - 16} {y - 4}Z"
def taart(x, y): return (f"M{x - 28} {y + 24}V{y + 4}H{x - 22}V{y - 8}H{x - 3}V{y - 18}Q{x - 6} {y - 24} {x} {y - 32}Q{x + 6} {y - 24} {x + 3} {y - 18}V{y - 8}H{x + 22}V{y + 4}H{x + 28}V{y + 24}Z")
stencil("sjablonen-feest", "Sjablonen: feest", [ballon, cadeau, kroon, muts, ijsje, taart], "feest", "6-9")
print("klaar")
