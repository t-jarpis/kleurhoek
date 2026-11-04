"""Batch 46: nog meer Sinterklaas (eigen tekeningen, 200x200), 2 tot en met 9+ jaar, met Roetveegpiet.

Andere scènes dan batch 44: speculaas, mijter en staf, het paard in de stal, Piet op de fiets en in de roeiboot,
pepernoten strooien, een verlanglijstje schrijven, Pietengym, Piet op de ladder, over de daken en Piet die de
weg zoekt. Piet heeft altijd alleen roetvegen; de Pieten hebben verschillende kapsels. Geen tekst op de platen.
Gebruik: OUT=/tmp/sint2 python3 batch46_sint.py [slug ...]
"""
import math, sys
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from batch35a import person, present, limb, blob, sparkle, beanie, scarf, face
from shapes import star_path, moon_path, cloud_path, heart_path, drop_path
from batch44_sint import sint, piet, mitre, staff, horse, boat, roof_row, chimney, garland, gift, window, floor_boards, wallpaper, pepernoot
from batch45_kerst import bike, house

ONLY = set(sys.argv[1:])


def speculaas_pop(sh, cx, cy, s=1, code="w"):
    """Speculaaspop: figuurtje met rok en een patroon van lijntjes en stipjes."""
    S = lambda v: v * s
    sh.region(f"M{f(cx - S(12))} {f(cy - S(20))}C{f(cx - S(30))} {f(cy - S(16))} {f(cx - S(32))} {f(cy - S(4))} {f(cx - S(22))} {f(cy)}"
              f"L{f(cx - S(30))} {f(cy + S(44))}H{f(cx + S(30))}L{f(cx + S(22))} {f(cy)}C{f(cx + S(32))} {f(cy - S(4))} {f(cx + S(30))} {f(cy - S(16))} {f(cx + S(12))} {f(cy - S(20))}Z", code)
    sh.circle_r(cx, cy - S(32), S(15), code)
    eye(sh, cx - S(5), cy - S(34), S(1.8)); eye(sh, cx + S(5), cy - S(34), S(1.8))
    sh.line(f"M{f(cx - S(5))} {f(cy - S(27))}Q{f(cx)} {f(cy - S(23))} {f(cx + S(5))} {f(cy - S(27))}", "l", "stroke-width:1.2")
    sh.line(f"M{f(cx - S(22))} {f(cy + S(14))}H{f(cx + S(22))}M{f(cx - S(25))} {f(cy + S(28))}H{f(cx + S(25))}", "l", "stroke-width:1")
    for k in range(5): sh.circle_r(cx - S(16) + k * S(8), cy + S(21), S(2.2), code)
    for k in range(3): sh.circle_r(cx, cy - S(8) + k * S(7), S(2.2), code)
    sh.region(heart_path(cx, cy + S(36), S(7)), code)


def speculaas_molen(sh, cx, cy, s=1, code="w"):
    S = lambda v: v * s
    sh.region(f"M{f(cx - S(16))} {f(cy + S(36))}L{f(cx - S(10))} {f(cy - S(10))}H{f(cx + S(10))}L{f(cx + S(16))} {f(cy + S(36))}Z", code)
    for a in (45, 135, 225, 315):
        sh.raw(f'<g transform="rotate({a} {f(cx)} {f(cy - S(10))})">')
        sh.rect_r(cx - S(4), cy - S(46), S(8), S(34), code, S(1))
        sh.raw("</g>")
    sh.circle_r(cx, cy - S(10), S(5), code)
    sh.rect_r(cx - S(5), cy + S(22), S(10), S(14), code, S(4))


# ---------------------------------------------------------------- 2-4 jaar
def speculaaspoppen(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    garland(sh, 8, 6, "ryn", 6, 14)
    sh.ellipse_r(100, 168, 92, 22, "b"); sh.ellipse_r(100, 166, 78, 15, "-")
    speculaas_pop(sh, 66, 110, 1.15)
    speculaas_molen(sh, 146, 112, 1.1)
    for x, y in ((24, 178), (36, 186), (172, 182), (182, 172)): pepernoot(sh, x, y, 5)
    sparkle(sh, 104, 52, 8, "y")


def mijter_en_staf(sh):
    sh.rect_r(0, 0, 200, 200, "k")
    for x in range(20, 200, 44):
        for y in range(20, 180, 44): sh.region(star_path(x + (22 if (y // 44) % 2 else 0), y, 6, 2.6), "-")
    sh.rect_r(0, 168, 200, 32, "w")
    sh.ellipse_r(100, 168, 74, 14, "m")
    mitre(sh, 90, 162, 2.6, "r", "y")
    staff(sh, 164, 30, 168, 1.6, "y")
    for x, c in ((70, "n"), (110, "g")): sh.circle_r(x, 150, 5, c)
    for x, y in ((14, 190), (28, 194), (172, 192), (186, 188)): pepernoot(sh, x, y, 5)


def paard_in_de_stal(sh):
    sh.rect_r(0, 0, 200, 200, "o")
    for x in range(0, 200, 25): sh.seg(x, 0, x, 160, "l", "stroke-width:.7")
    window(sh, 20, 22, 40, 30, "n")
    sh.region(moon_path(34, 34, 7), "y")
    sh.rect_r(0, 160, 200, 40, "y")
    for x, y in ((20, 172), (60, 184), (120, 176), (170, 188), (90, 194)): sh.line(f"M{x - 8} {y}L{x + 6} {y - 4}M{x - 4} {y + 2}L{x + 8} {y}", "l", "stroke-width:1")
    sh.rect_r(132, 128, 52, 34, "y", 3); sh.line("M136 140H180M136 150H180", "l", "stroke-width:1")
    horse(sh, 88, 184, 1.05)
    sh.region("M20 182L26 156H50L56 182Z", "z"); sh.ellipse_r(38, 156, 12, 4, "b")
    sh.region("M140 126L166 118L162 126Z", "o"); sh.region("M164 118L174 112L170 122Z", "g")


# ---------------------------------------------------------------- 4-6 jaar
def piet_op_de_fiets(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    for x, y, r in ((30, 24, 9), (150, 18, 7)): sh.region(cloud_path(x, y, r), "-")
    roof_row(sh, 130, [(-4, 40, 50, "trap", "w"), (34, 36, 40, "punt", "r"), (150, 54, 46, "trap", "o")])
    sh.rect_r(0, 130, 200, 70, "z")
    sh.region("M0 186Q100 178 200 186V200H0Z", "g")
    bike(sh, 104, 186, 1.1, "r")
    # mand voorop met pakjes
    sh.region("M128 120H156L152 140H132Z", "w")
    gift(sh, 132, 108, 10, 12, "m", "y"); gift(sh, 144, 112, 10, 8, "g", "y")
    hy = piet(sh, 98, 120 - 54 * .78 - 15 * .78, .78, suit="g", trouser="r", cap="p", feather="y", hands=((132, 126), (128, 128)), legs=((104, 164), (112, 170)), hair="w", curls=False, light_soot=True)
    for x, y in ((40, 160), (60, 170), (180, 166)): pepernoot(sh, x, y, 3.5)


def piet_strooit_pepernoten(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    garland(sh, 10, 8, "rny", 8, 12)
    sh.rect_r(0, 168, 200, 32, "z")
    for x in range(0, 200, 20): sh.seg(x, 168, x, 200, "l", "stroke-width:.6")
    piet(sh, 100, 44, .95, suit="r", trouser="y", cap="g", feather="-", hands=((62, 64), (130, 120)), legs=((92, 160), (108, 160)), hair="x", curls=False, light_soot=True)
    sh.region("M124 110Q144 100 156 120Q162 144 140 150Q122 150 120 130Z", "w")
    for x, y in ((40, 40), (56, 30), (76, 46), (30, 64), (60, 70), (150, 40), (170, 60), (140, 70), (186, 90), (24, 96)): pepernoot(sh, x, y, 3.6)
    for x, shirt, st, hair, hands in ((30, "m", "curly", "w", ((16, 118), (44, 112))), (172, "t", "pony", "y", ((158, 116), (186, 112)))):
        s = .6
        person(sh, x, 168 - 101 * s, shirt, "n", hands=hands, style=st, hair=hair, s=s)


def verlanglijstje_schrijven(sh):
    wallpaper(sh, 130, "k", "m", avoid=((116, 14, 176, 70), (18, 18, 72, 72)))
    window(sh, 120, 18, 52, 46, "n", "y")
    sh.region(moon_path(134, 30, 8), "y")
    for x, y in ((156, 28), (160, 52)): sh.region(star_path(x, y, 4, 1.8), "y")
    # lijstje met een mijter (een tekening aan de muur)
    sh.rect_r(22, 22, 46, 46, "w", 2); sh.rect_r(28, 28, 34, 34, "-", 1)
    mitre(sh, 45, 58, .56, "r", "y")
    # kind aan tafel
    s = .78
    person(sh, 92, 132 - 58 * s - 15 * s + 6, "y", "n", hands=((80, 128), (106, 126)), style="braids", hair="x", s=s, draw_legs=False)
    sh.rect_r(0, 130, 200, 70, "w"); sh.line("M0 130H200", "l", "stroke-width:1.2")
    sh.region("M70 126L112 122L116 150L74 154Z", "-")
    for k in range(4): sh.seg(78, 132 + k * 5, 108, 129 + k * 5, "l", "stroke-width:.7")
    sh.raw('<g transform="rotate(-30 108 126)">'); sh.rect_r(106, 104, 5, 24, "g", 1); sh.region("M106 128H111L108.5 134Z", "o"); sh.raw("</g>")
    # schoen op de grond
    sh.region("M140 188V170Q140 160 152 160H166Q172 160 176 166L188 170Q194 174 192 188Z", "r"); sh.rect_r(138, 186, 56, 6, "x", 3)
    sh.region("M160 162L170 136L176 138L168 164Z", "o"); sh.region("M170 136Q166 126 172 122Q176 130 174 136Z", "g")
    for x, y in ((30, 186), (44, 190)): pepernoot(sh, x, y, 4)


def piet_in_de_roeiboot(sh):
    sh.rect_r(0, 0, 200, 110, "-")
    sh.circle_r(170, 30, 16, "y")
    boat(sh, 50, 100, .42)
    for x, y in ((100, 30), (124, 44)): sh.line(f"M{x - 6} {y}Q{x - 3} {y - 4} {x} {y}Q{x + 3} {y - 4} {x + 6} {y}", "l", "stroke-width:1.2")
    sh.region("M0 100Q25 94 50 100T100 100T150 100T200 100V200H0Z", "b")
    for y, c in ((150, "n"), (176, "t")):
        sh.region(f"M0 {y}Q25 {y - 6} 50 {y}T100 {y}T150 {y}T200 {y}V{y + 10}Q175 {y + 4} 150 {y + 10}T100 {y + 10}T50 {y + 10}T0 {y + 10}Z", c)
    # roeiboot
    gift(sh, 128, 110, 20, 18, "r", "y"); gift(sh, 148, 116, 16, 12, "g", "y"); gift(sh, 140, 96, 14, 12, "y", "r")
    piet(sh, 84, 66, .62, suit="o", trouser="n", cap="r", feather="y", hands=((60, 120), (110, 116)), draw_legs=False, hair="w", curls=False, light_soot=True)
    sh.line("M62 118L36 156", "l", "stroke-width:3")
    sh.region("M34 120H172L158 146H48Z", "w")
    sh.region("M34 120H172L170 126H36Z", "y")
    sh.region("M30 156L44 144L50 150L36 162Z", "w")


def pietenbaret_knippen():
    """Knipplaat (A4): een Pietenbaret met veer om op te zetten, met een hoofdband van twee stroken."""
    sh = Sheet(280)
    cap = "M24 150C10 96 120 54 184 104Q174 126 150 136Q96 146 24 150Z"
    feather = "M134 112C150 60 176 34 196 30C190 54 170 84 146 116Z"
    sh.region(feather, "y")
    sh.line("M140 114Q160 76 192 34", "l", "stroke-width:1")
    sh.region(cap, "p")
    sh.circle_r(132, 112, 9, "y")
    for x, y in ((60, 120), (86, 108), (110, 124), (60, 140)): sh.region(star_path(x, y, 6, 2.6), "-")
    sh.region("M24 150Q96 142 150 136L152 156Q90 164 22 168Z", "y")
    sh.line("M16 174L12 146Q8 112 40 90Q80 64 132 62L150 66Q170 30 192 20Q202 22 200 36Q196 76 192 104Q178 132 160 142L158 162Q96 172 16 174Z", "cut")
    for y in (190, 216):
        sh.rect_r(12, y, 176, 18, "p", 2); sh.rect_line(12, y, 176, 18, "cut", 2)
        for x in range(30, 180, 30): sh.region(star_path(x, y + 9, 5, 2.2), "y")
    sh.legend(["cut"], 274)
    write(OUT, "pietenbaret-om-op-te-zetten", sh, {"category": "feest", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 25, "holiday": "sinterklaas", "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}, {"slug": "plakband"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Pietenbaret om op te zetten", "printNote": "Op stevig papier (160 gram) blijft de baret mooi staan.", "steps": [
            "Kleur de baret, de veer en de twee stroken in. Kies je eigen kleuren, net als echte Pieten.",
            "Knip de baret met de veer en de stroken uit langs de streepjeslijnen.",
            "Plak de twee stroken aan elkaar tot één lange band en meet hem om je hoofd.",
            "Plak de band dicht met plakband en plak de baret er schuin op. Klaar om pepernoten te strooien!"]}}})


# ---------------------------------------------------------------- 6-9 jaar
def over_de_daken(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.circle_r(44, 40, 24, "y")
    for x, y in ((100, 16), (130, 40), (176, 18), (190, 64), (12, 84), (84, 56)): sh.region(star_path(x, y, 5, 2.2), "y")
    tops = roof_row(sh, 190, [(-6, 44, 60, "trap", "r"), (38, 40, 44, "punt", "w"), (78, 44, 70, "trap", "o"), (122, 36, 50, "punt", "g"), (158, 48, 64, "trap", "w")])
    chimney(sh, 52, 120, 10, 16, "r"); chimney(sh, 170, 100, 10, 18, "r")
    # Sint en het paard springen van dak naar dak
    sh.raw('<g transform="rotate(-12 110 100)">')
    sint(sh, 104, 30, .4, staff_side=-1, legs=False)
    horse(sh, 112, 118, .72)
    sh.raw("</g>")
    piet(sh, 166, 44, .48, suit="m", trouser="y", cap="b", feather="y", hands=((148, 46), (186, 76)), legs=((160, 92), (172, 92)), hair="y", curls=False, light_soot=True)
    for x, y in ((40, 150), (140, 160)): sh.line(f"M{x} {y}h6M{x + 2} {y + 6}h6", "l", "stroke-width:1")


def pieten_oefenen(sh):
    sh.rect_r(0, 0, 200, 160, "b")
    for x in (40, 100, 160): sh.rect_r(x - 12, 10, 24, 14, "y", 2)
    sh.rect_r(0, 160, 200, 40, "w"); sh.line("M0 172H200M0 186H200", "l", "stroke-width:.7")
    # touw
    sh.line("M168 0V150", "l", "stroke-width:3")
    piet(sh, 152, 40, .54, suit="g", trouser="r", cap="y", feather="r", hands=((168, 30), (168, 46)), legs=((150, 112), (164, 106)), hair="w", curls=False, light_soot=True)
    # Piet op de bal die pepernoten hoog houdt
    sh.circle_r(52, 150, 20, "r"); sh.region("M32 150Q52 160 72 150Q52 146 32 150Z", "y")
    piet(sh, 52, 50, .54, suit="o", trouser="n", cap="g", feather="y", hands=((28, 58), (76, 58)), legs=((46, 128), (58, 128)), hair="w", curls=False, light_soot=True)
    for x, y in ((24, 40), (40, 24), (64, 22), (80, 40)): pepernoot(sh, x, y, 3.4)
    # Piet op zijn handen (ondersteboven)
    piet(sh, 112, 78, .5, suit="m", trouser="t", cap="p", feather="y", hands=((90, 78), (134, 78)), legs=((100, 160), (124, 160)), hair="o", curls=False, light_soot=True)
    sh.rect_r(70, 166, 84, 7, "g", 3)
    present(sh, 180, 166, 16, 14, "y", "r")


def piet_op_de_ladder(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region(moon_path(170, 30, 13), "y")
    for x, y in ((20, 16), (60, 30), (110, 12), (186, 70)): sh.region(star_path(x, y, 4.5, 2), "y")
    # gevel met dak en schoorsteen
    sh.rect_r(20, 90, 140, 110, "r")
    for r in range(3):
        for k in range(3): sh.seg(20, 104 + r * 34 + k * 0, 160, 104 + r * 34, "l", "stroke-width:.5")
    sh.poly_r([(10, 92), (90, 44), (170, 92)], "w")
    chimney(sh, 120, 50, 16, 26, "r")
    for x, y in ((34, 110), (110, 110), (34, 150)): window(sh, x, y, 30, 26, "y", "b")
    sh.rect_r(112, 150, 26, 50, "g", 2); sh.circle_r(132, 176, 2, "y")
    # kat op het dak
    sh.ellipse_r(54, 64, 9, 6, "x"); sh.circle_r(46, 58, 5, "x"); sh.region("M42 54L43 49L46 53ZM48 53L50 49L50 54Z", "x")
    sh.line("M62 64Q70 60 66 52", "l", "stroke-width:2")
    # ladder
    sh.line("M168 200L132 66M184 200L148 66", "l", "stroke-width:2.4")
    for k in range(8): sh.seg(165 - k * 4.3, 188 - k * 16, 181 - k * 4.3, 188 - k * 16, "l", "stroke-width:2")
    piet(sh, 150, 84, .5, suit="t", trouser="o", cap="r", feather="y", hands=((140, 92), (160, 90)), legs=((150, 140), (162, 136)), hair="w", curls=False, light_soot=True)
    sh.region("M164 96Q182 88 186 106Q190 126 174 128Q160 128 158 112Z", "w")
    gift(sh, 172, 88, 10, 8, "m", "y")


# ---------------------------------------------------------------- 9+ jaar
def piet_zoekt_de_weg(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.circle_r(30, 30, 16, "y")
    for x, y in ((70, 12), (100, 30), (150, 14), (186, 40), (96, 50), (140, 30)): sh.region(star_path(x, y, 3.6, 1.6), "y")
    # stad ver weg
    sh.rect_r(150, 46, 14, 54, "z"); sh.poly_r([(146, 48), (157, 22), (168, 48)], "w"); sh.circle_r(157, 60, 4, "-")
    for x, w, h, wall in ((0, 22, 34, "w"), (22, 18, 44, "r"), (40, 24, 30, "o"), (64, 20, 40, "w"), (84, 26, 28, "g"), (110, 20, 36, "r"), (130, 22, 32, "w"), (168, 32, 30, "o")):
        sh.rect_r(x, 100 - h, w, h, wall); sh.poly_r([(x - 1, 100 - h), (x + w / 2, 100 - h - 10), (x + w + 1, 100 - h)], "z")
        for k in range(2):
            wx = x + 3 + k * (w / 2)
            if not (54 < wx < 80 or 112 < wx < 136): sh.rect_r(wx, 100 - h + 8, w / 4, 6, "y")
    sh.region("M0 100Q100 92 200 100V110H0Z", "b")
    # het dak waar de Pieten op staan
    sh.region("M0 200V130L200 112V200Z", "r")
    for k in range(5):
        y = 138 + k * 14
        sh.line(f"M0 {y}L200 {y - 18}", "l", "stroke-width:.6")
    chimney(sh, 150, 84, 14, 30, "w")
    sh.region(cloud_path(158, 76, 5), "z")
    # Piet met de kaart
    piet(sh, 66, 64, .56, suit="o", trouser="g", cap="b", feather="y", hands=((40, 128), (92, 128)), legs=((60, 146), (74, 142)), hair="x", curls=False, light_soot=True)
    sh.region("M34 116L98 118L96 146L36 142Z", "-")
    sh.line("M54 116.5L52 143M76 117L76 144", "l", "stroke-width:.6")
    sh.line("M42 136Q54 124 62 132T84 122", "l", "stroke-width:1.2;stroke-dasharray:2 2")
    sh.region(star_path(86, 124, 4, 1.6), "r")
    # Piet met de verrekijker
    piet(sh, 124, 54, .5, suit="m", trouser="y", cap="g", feather="r", hands=((110, 70), (116, 72)), legs=((118, 130), (130, 126)), hair="w", curls=False, light_soot=True)
    sh.raw('<g transform="rotate(-24 112 62)">'); sh.rect_r(96, 56, 22, 8, "y", 2); sh.rect_r(88, 54, 9, 12, "w", 2); sh.raw("</g>")
    gift(sh, 168, 150, 18, 14, "t", "y")
    for x, y in ((10, 180), (24, 186), (190, 176)): pepernoot(sh, x, y, 3.5)


PLATES = [
    ("speculaaspoppen", "Speculaaspop en speculaasmolen", "2-4", 1, speculaaspoppen),
    ("mijter-en-staf", "De mijter en de staf van Sinterklaas", "2-4", 1, mijter_en_staf),
    ("paard-in-de-stal", "Het paard van Sinterklaas in de stal", "2-4", 1, paard_in_de_stal),
    ("piet-op-de-fiets", "Piet op de fiets", "4-6", 2, piet_op_de_fiets),
    ("piet-strooit-pepernoten", "Piet strooit pepernoten", "4-6", 2, piet_strooit_pepernoten),
    ("verlanglijstje-schrijven", "Een verlanglijstje schrijven", "4-6", 2, verlanglijstje_schrijven),
    ("piet-in-de-roeiboot", "Piet in de roeiboot", "4-6", 2, piet_in_de_roeiboot),
    ("over-de-daken", "Sint en het paard over de daken", "6-9", 3, over_de_daken),
    ("pieten-oefenen", "Pieten oefenen voor pakjesavond", "6-9", 2, pieten_oefenen),
    ("piet-op-de-ladder", "Piet op de ladder", "6-9", 2, piet_op_de_ladder),
    ("piet-zoekt-de-weg", "Piet zoekt de weg", "9+", 3, piet_zoekt_de_weg),
]

if __name__ == "__main__":
    for slug, name, age, diff, draw in PLATES:
        if ONLY and slug not in ONLY: continue
        kp(slug, name, "feest", age, diff, draw, "sinterklaas")
    if not ONLY or "pietenbaret-om-op-te-zetten" in ONLY:
        pietenbaret_knippen()
