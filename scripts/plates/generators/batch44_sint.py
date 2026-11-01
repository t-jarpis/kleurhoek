"""Batch 44: Sinterklaas (eigen tekeningen, 200x200) voor alle leeftijden, met Roetveegpiet.

Sinterklaas: rode mantel, witte albe, mijter met kruis, lange witte baard en een gouden staf. Piet: baret met
veer, pofmouwen, witte kraag en een paar roetvegen op zijn wangen (geen zwart gezicht). Geen tekst op de platen.
Gebruik: OUT=/tmp/sint python3 batch44_sint.py [slug ...]
"""
import math, sys
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from batch35a import person, present, limb, blob, sparkle, sit_legs
from shapes import star_path, moon_path, cloud_path, heart_path

ONLY = set(sys.argv[1:])


# ---------------------------------------------------------------- figuren
def mitre(sh, cx, base, s, code="r", trim="y"):
    """Mijter met onderkant op `base`."""
    S = lambda v: v * s
    sh.region(f"M{f(cx - S(14))} {f(base)}C{f(cx - S(17))} {f(base - S(18))} {f(cx - S(10))} {f(base - S(34))} {f(cx)} {f(base - S(44))}"
              f"C{f(cx + S(10))} {f(base - S(34))} {f(cx + S(17))} {f(base - S(18))} {f(cx + S(14))} {f(base)}Z", code)
    sh.rect_r(cx - S(15), base - S(6), S(30), S(7), trim, S(2))
    sh.region(f"M{f(cx - S(2))} {f(base - S(32))}H{f(cx + S(2))}V{f(base - S(26))}H{f(cx + S(7))}V{f(base - S(22))}H{f(cx + S(2))}V{f(base - S(12))}"
              f"H{f(cx - S(2))}V{f(base - S(22))}H{f(cx - S(7))}V{f(base - S(26))}H{f(cx - S(2))}Z", trim)


def staff(sh, x, top, bottom, s, code="y"):
    """Gouden staf met krul bovenaan (naar links)."""
    S = lambda v: v * s
    sh.rect_r(x - S(2.2), top + S(14), S(4.4), bottom - top - S(14), code, S(1.5))
    r1, r2 = S(11), S(6.5)
    cx, cy = x - S(9), top + S(12)
    sh.region(f"M{f(x + S(2.2))} {f(top + S(16))}A{f(r1)} {f(r1)} 0 1 0 {f(cx - r1 * .2)} {f(cy + r1 * .98)}"
              f"L{f(cx - r2 * .2)} {f(cy + r2 * .98)}A{f(r2)} {f(r2)} 0 1 1 {f(x - S(2.2))} {f(top + S(16))}Z", code)
    sh.circle_r(cx - r1 * .2, cy + S(8.6), S(2.6), code)


def sint(sh, cx, top, s=1, staff_side=1, wave=False, legs=True, robe="-", cape="r", trim="y", face_only=False):
    """Sinterklaas staand van voren. top = punt van de mijter. Geeft de y van het gezicht terug."""
    S = lambda v: v * s
    hy = top + S(52)
    if not face_only:
        bottom = hy + S(112) if legs else hy + S(80)
        if staff_side:
            staff(sh, cx + staff_side * S(34), top + S(14), bottom - S(2), s)
        # albe en mantel
        sh.region(f"M{f(cx - S(22))} {f(hy + S(26))}L{f(cx - S(30))} {f(bottom)}H{f(cx + S(30))}L{f(cx + S(22))} {f(hy + S(26))}Z", robe)
        sh.region(f"M{f(cx - S(16))} {f(hy + S(18))}Q{f(cx - S(40))} {f(hy + S(30))} {f(cx - S(44))} {f(bottom)}H{f(cx - S(14))}L{f(cx - S(8))} {f(hy + S(30))}Z", cape)
        sh.region(f"M{f(cx + S(16))} {f(hy + S(18))}Q{f(cx + S(40))} {f(hy + S(30))} {f(cx + S(44))} {f(bottom)}H{f(cx + S(14))}L{f(cx + S(8))} {f(hy + S(30))}Z", cape)
        for d in (-1, 1):  # gouden stola
            sh.region(f"M{f(cx + d * S(5))} {f(hy + S(26))}L{f(cx + d * S(9))} {f(bottom - S(6))}H{f(cx + d * S(3))}L{f(cx + d * S(1))} {f(hy + S(26))}Z", trim)
        # armen: mouwen van de mantel, handen
        lh = (cx - S(30), hy + S(52))
        rh = (cx + staff_side * S(34), hy + S(54)) if staff_side == 1 else (cx + S(30), hy + S(52))
        if staff_side == -1: lh = (cx - S(34), hy + S(54))
        if wave: rh = (cx + S(36), hy + S(6)) if staff_side != 1 else rh
        if wave and staff_side == 1: lh = (cx - S(36), hy + S(6))
        limb(sh, cx - S(18), hy + S(24), *lh, cape, S(13))
        limb(sh, cx + S(18), hy + S(24), *rh, cape, S(13))
        sh.circle_r(*lh, S(5.5), "-"); sh.circle_r(*rh, S(5.5), "-")
        if s >= .5:  # gouden zoom langs de mantel, kruisjes op de stola, broche en kantrand
            for d in (-1, 1):
                sh.region(f"M{f(cx + d * S(8))} {f(hy + S(30))}L{f(cx + d * S(14))} {f(bottom)}H{f(cx + d * S(20))}L{f(cx + d * S(13))} {f(hy + S(28))}Z", trim)
            sh.line(f"M{f(cx - S(28))} {f(bottom - S(9))}" + "".join(f"L{f(cx - S(28) + k * S(4))} {f(bottom - S(9) + (S(3) if k % 2 else 0))}" for k in range(1, 15)), "l", "stroke-width:.9")
        sh.rect_r(cx - S(18), bottom - S(4), S(14), S(6), "x", S(3)) if legs else None
        if legs: sh.rect_r(cx + S(4), bottom - S(4), S(14), S(6), "x", S(3))
    # hoofd
    mitre(sh, cx, hy - S(8), s * 1.05, cape, trim)
    if s >= .5:  # edelstenen op de band van de mijter
        for d in (-1, 1): sh.circle_r(cx + d * S(9), hy - S(11), S(2.2), "n" if d < 0 else "g")
    sh.circle_r(cx, hy, S(13), "-")
    # baard en snor
    sh.region(f"M{f(cx - S(13))} {f(hy + S(1))}C{f(cx - S(20))} {f(hy + S(24))} {f(cx - S(10))} {f(hy + S(40))} {f(cx)} {f(hy + S(46))}"
              f"C{f(cx + S(10))} {f(hy + S(40))} {f(cx + S(20))} {f(hy + S(24))} {f(cx + S(13))} {f(hy + S(1))}"
              f"Q{f(cx + S(9))} {f(hy + S(12))} {f(cx)} {f(hy + S(12))}Q{f(cx - S(9))} {f(hy + S(12))} {f(cx - S(13))} {f(hy + S(1))}Z", "-")
    sh.line(f"M{f(cx - S(8))} {f(hy + S(20))}Q{f(cx - S(9))} {f(hy + S(30))} {f(cx - S(4))} {f(hy + S(38))}M{f(cx + S(8))} {f(hy + S(20))}Q{f(cx + S(9))} {f(hy + S(30))} {f(cx + S(4))} {f(hy + S(38))}M{f(cx)} {f(hy + S(18))}V{f(hy + S(40))}", "l", f"stroke-width:{f(.9 * min(1.4, s * 1.3))}")
    sh.region(f"M{f(cx)} {f(hy + S(8))}Q{f(cx - S(6))} {f(hy + S(5))} {f(cx - S(11))} {f(hy + S(10))}Q{f(cx - S(6))} {f(hy + S(13))} {f(cx)} {f(hy + S(10))}"
              f"Q{f(cx + S(6))} {f(hy + S(13))} {f(cx + S(11))} {f(hy + S(10))}Q{f(cx + S(6))} {f(hy + S(5))} {f(cx)} {f(hy + S(8))}Z", "-")
    eye(sh, cx - S(5), hy - S(1), S(1.7)); eye(sh, cx + S(5), hy - S(1), S(1.7))
    sh.line(f"M{f(cx - S(8))} {f(hy - S(5))}Q{f(cx - S(5))} {f(hy - S(7))} {f(cx - S(2))} {f(hy - S(5))}M{f(cx + S(2))} {f(hy - S(5))}Q{f(cx + S(5))} {f(hy - S(7))} {f(cx + S(8))} {f(hy - S(5))}", "l", "stroke-width:1.2")
    sh.circle_r(cx, hy + S(4), S(2.4), "k")
    return hy


def beret(sh, cx, hy, s, code="n", feather="y"):
    S = lambda v: v * s
    sh.region(f"M{f(cx + S(6))} {f(hy - S(16))}C{f(cx + S(18))} {f(hy - S(36))} {f(cx + S(30))} {f(hy - S(34))} {f(cx + S(32))} {f(hy - S(28))}"
              f"C{f(cx + S(24))} {f(hy - S(28))} {f(cx + S(16))} {f(hy - S(22))} {f(cx + S(8))} {f(hy - S(13))}Z", feather)
    sh.region(f"M{f(cx - S(18))} {f(hy - S(6))}C{f(cx - S(22))} {f(hy - S(22))} {f(cx + S(18))} {f(hy - S(26))} {f(cx + S(20))} {f(hy - S(10))}"
              f"Q{f(cx)} {f(hy - S(12))} {f(cx - S(18))} {f(hy - S(6))}Z", code)


def soot(sh, cx, hy, s):
    """Twee roetvegen: kleine vegen op de wangen en één op de neus."""
    S = lambda v: v * s
    for x, y, a in ((cx - S(10), hy + S(9), -15), (cx + S(10), hy + S(8), 20)):
        sh.raw(f'<g transform="rotate({a} {f(x)} {f(y)})">')
        sh.region(f"M{f(x - S(3))} {f(y)}Q{f(x)} {f(y - S(2))} {f(x + S(3))} {f(y)}Q{f(x)} {f(y + S(1.5))} {f(x - S(3))} {f(y)}Z", "z")
        sh.raw("</g>")


def piet(sh, cx, top, s=1, suit="o", trouser="g", cap="n", feather="y", hands=None, legs=None, draw_legs=True, arms_front=False, hair="x"):
    """Roetveegpiet: baret met veer, witte kraag, pofbroek, roetvegen. Geeft de y van het gezicht terug."""
    S = lambda v: v * s
    hy = person(sh, cx, top, suit, trouser, hands=hands, hair=None, style="short", legs=legs, s=s, draw_legs=draw_legs,
                arms_front=arms_front, shoes="x")
    for d in (-1, 1):  # krullen opzij, onder de baret
        sh.circle_r(cx + d * S(15), hy - S(1), S(4.6), hair); sh.circle_r(cx + d * S(14), hy + S(7), S(4.2), hair)
    if draw_legs:  # pofbroek
        sh.region(f"M{f(cx - S(17))} {f(hy + S(52))}Q{f(cx - S(24))} {f(hy + S(66))} {f(cx - S(14))} {f(hy + S(70))}H{f(cx + S(14))}Q{f(cx + S(24))} {f(hy + S(66))} {f(cx + S(17))} {f(hy + S(52))}Z", trouser)
    if s >= .5:  # pofmouwen, knoopjes en riem met gesp
        for d in (-1, 1): sh.ellipse_r(cx + d * S(15), hy + S(24), S(7), S(6.5), trouser)
        for k in range(3): sh.circle_r(cx, hy + S(30 + k * 7), S(1.9), "y")
        sh.rect_r(cx - S(17), hy + S(48), S(34), S(5), "w", S(1)); sh.rect_r(cx - S(4), hy + S(47), S(8), S(7), "y", S(1))
    sh.region(f"M{f(cx - S(14))} {f(hy + S(14))}Q{f(cx - S(8))} {f(hy + S(24))} {f(cx)} {f(hy + S(20))}Q{f(cx + S(8))} {f(hy + S(24))} {f(cx + S(14))} {f(hy + S(14))}"
              f"Q{f(cx)} {f(hy + S(17))} {f(cx - S(14))} {f(hy + S(14))}Z", "-")
    if s >= .5:
        sh.line(f"M{f(cx - S(8))} {f(hy + S(17))}L{f(cx - S(7))} {f(hy + S(21))}M{f(cx)} {f(hy + S(18))}V{f(hy + S(20))}M{f(cx + S(8))} {f(hy + S(17))}L{f(cx + S(7))} {f(hy + S(21))}", "l", "stroke-width:.8")
    beret(sh, cx, hy, s, cap, feather)
    if s >= .5: sh.circle_r(cx + S(7), hy - S(14), S(2.6), "y")
    soot(sh, cx, hy, s)
    return hy


def pepernoot(sh, x, y, r=3):
    sh.circle_r(x, y, r, "w")


def chimney(sh, x, y, w, h, code="r"):
    sh.rect_r(x, y, w, h, code)
    sh.rect_r(x - 3, y - 6, w + 6, 7, code, 1)
    for k in range(1, int(h / 7)):
        sh.seg(x, y + k * 7, x + w, y + k * 7, "l", "stroke-width:.6")


def horse(sh, x, y, s=1, code="-", mane="z", flip=False):
    """Amerigo, het paard, van opzij naar rechts kijkend. (x, y) = midden onder de hoeven."""
    S = lambda v: v * s
    g = f' transform="translate({f(2 * x)} 0) scale(-1 1)"' if flip else ""
    sh.raw(f"<g{g}>")
    bx, by = x - S(8), y - S(44)
    # staart achter het lijf
    sh.region(f"M{f(bx - S(34))} {f(by - S(8))}C{f(bx - S(54))} {f(by - S(6))} {f(bx - S(56))} {f(by + S(22))} {f(bx - S(48))} {f(by + S(34))}"
              f"C{f(bx - S(46))} {f(by + S(18))} {f(bx - S(42))} {f(by + S(4))} {f(bx - S(32))} {f(by + S(2))}Z", mane)
    # benen met hoeven
    for lx, d in ((bx - S(26), -3), (bx - S(14), 3), (bx + S(16), -3), (bx + S(28), 3)):
        limb(sh, lx, by + S(6), lx + S(d), y - S(6), code, S(9))
        sh.rect_r(lx + S(d) - S(5.5), y - S(7), S(11), S(7), "z", S(1.5))
    sh.ellipse_r(bx, by, S(38), S(18), code)
    # nek en hoofd
    sh.region(f"M{f(bx + S(18))} {f(by - S(12))}C{f(bx + S(26))} {f(by - S(30))} {f(bx + S(34))} {f(by - S(44))} {f(bx + S(42))} {f(by - S(52))}"
              f"L{f(bx + S(56))} {f(by - S(42))}C{f(bx + S(48))} {f(by - S(30))} {f(bx + S(40))} {f(by - S(10))} {f(bx + S(34))} {f(by + S(4))}Z", code)
    hx, hy = bx + S(56), by - S(42)
    sh.raw(f'<g transform="rotate(35 {f(hx)} {f(hy)})">')
    sh.rect_r(hx - S(10), hy - S(9), S(30), S(17), code, S(8))
    sh.raw("</g>")
    sh.region(f"M{f(bx + S(42))} {f(by - S(52))}L{f(bx + S(42))} {f(by - S(66))}L{f(bx + S(50))} {f(by - S(54))}Z", code)
    # manen langs de nek
    sh.region(f"M{f(bx + S(42))} {f(by - S(54))}C{f(bx + S(32))} {f(by - S(46))} {f(bx + S(22))} {f(by - S(30))} {f(bx + S(16))} {f(by - S(12))}"
              f"L{f(bx + S(22))} {f(by - S(10))}C{f(bx + S(28))} {f(by - S(28))} {f(bx + S(36))} {f(by - S(42))} {f(bx + S(46))} {f(by - S(50))}Z", mane)
    eye(sh, hx + S(1), hy - S(2), S(1.8))
    sh.dot(hx + S(12), hy + S(14), S(1.1))
    if s >= .8:  # zadeldek met gouden rand en een hoofdstel
        sh.region(f"M{f(bx - S(18))} {f(by - S(17))}Q{f(bx)} {f(by - S(21))} {f(bx + S(14))} {f(by - S(17))}L{f(bx + S(12))} {f(by + S(8))}Q{f(bx - S(2))} {f(by + S(12))} {f(bx - S(16))} {f(by + S(8))}Z", "r")
        sh.region(f"M{f(bx - S(16))} {f(by + S(2))}Q{f(bx - S(2))} {f(by + S(6))} {f(bx + S(12))} {f(by + S(2))}L{f(bx + S(12))} {f(by + S(8))}Q{f(bx - S(2))} {f(by + S(12))} {f(bx - S(16))} {f(by + S(8))}Z", "y")
        sh.raw(f'<g transform="rotate(35 {f(hx)} {f(hy)})">'); sh.rect_r(hx + S(2), hy - S(9), S(4), S(17), "w", S(1)); sh.raw("</g>")
    sh.raw("</g>")


def boat(sh, x, y, s=1, hull="n", deck="-", funnel="r"):
    """Stoomboot naar links, (x, y) = midden van de waterlijn."""
    S = lambda v: v * s
    sh.region(f"M{f(x - S(70))} {f(y - S(26))}H{f(x + S(66))}L{f(x + S(54))} {f(y)}H{f(x - S(58))}Z", hull)
    sh.rect_r(x - S(48), y - S(46), S(80), S(20), deck, S(2))
    for k in range(5):
        sh.circle_r(x - S(38) + k * S(16), y - S(36), S(4), "b")
    sh.rect_r(x + S(8), y - S(72), S(14), S(26), funnel)
    sh.rect_r(x + S(6), y - S(76), S(18), S(5), "x", 1)
    sh.rect_r(x - S(22), y - S(68), S(12), S(22), funnel)
    sh.rect_r(x - S(24), y - S(72), S(16), S(5), "x", 1)
    for k in range(6):
        sh.circle_r(x - S(56) + k * S(22), y - S(14), S(3.2), "-")
    sh.region(cloud_path(x + S(30), y - S(92), S(9)), "-")


def roof_row(sh, y0, specs):
    """Daken van huizen: (x, w, h, roof) met roof 'punt' of 'trap'. Geeft lijst schoorsteenplekken."""
    out = []
    for x, w, h, roof, code in specs:
        sh.rect_r(x, y0 - h, w, h + 10, code)
        if roof == "plat":
            sh.rect_r(x - 2, y0 - h - 4, w + 4, 5, "z")
        elif roof == "punt":
            sh.poly_r([(x - 3, y0 - h), (x + w / 2, y0 - h - w * .55), (x + w + 3, y0 - h)], "w")
        else:
            st = w / 6
            pts_ = [(x, y0 - h)]
            for k in range(3):
                pts_ += [(x + k * st, y0 - h - (k + 1) * 8), (x + (k + 1) * st, y0 - h - (k + 1) * 8)]
            for k in range(3):
                pts_ += [(x + w - (2 - k + 1) * st, y0 - h - (3 - k) * 8), (x + w - (2 - k) * st, y0 - h - (3 - k) * 8)]
            pts_ += [(x + w, y0 - h)]
            sh.poly_r(pts_, "w")
        for wx in (x + w * .2, x + w * .6):
            sh.rect_r(wx, y0 - h + 10, w * .2, 12, "y", 1)
        out.append((x + w * .5, y0 - h))
    return out


def garland(sh, y, n=7, codes="rny", sag=12, size=10):
    """Vlaggenlijn van links naar rechts."""
    sh.line(f"M0 {y}Q100 {y + sag * 2} 200 {y}", "l", "stroke-width:1.2")
    for k in range(n):
        x = (k + .5) * 200 / n
        yy = y + sag * 2 * (x / 200) * (1 - x / 200) * 2
        sh.poly_r([(x - size * .6, yy - 1), (x + size * .6, yy - 1), (x, yy + size)], codes[k % len(codes)])


def gift(sh, x, y, w, h, code, ribbon="y", dots=None):
    """Pakje met strik; dots = kleur van stippen op het papier."""
    present(sh, x, y, w, h, code, ribbon)
    if dots:
        for i, (dx, dy) in enumerate(((.2, .3), (.78, .28), (.25, .75), (.75, .72))):
            sh.circle_r(x + w * dx, y + h * dy, min(w, h) * .09, dots)


def window(sh, x, y, w, h, glass="b", curtain=None, frame="-"):
    sh.rect_r(x - 3, y - 3, w + 6, h + 6, frame, 2)
    sh.rect_r(x, y, w, h, glass, 1)
    sh.seg(x + w / 2, y, x + w / 2, y + h, "l", "stroke-width:1.2"); sh.seg(x, y + h / 2, x + w, y + h / 2, "l", "stroke-width:1.2")
    if curtain:
        sh.region(f"M{f(x - 6.0)} {f(y - 6.0)}H{f(x + w * .3)}Q{f(x + w * .12)} {f(y + h * .5)} {f(x + 2.0)} {f(y + h + 4)}H{f(x - 6.0)}Z", curtain)
        sh.region(f"M{f(x + w + 6.0)} {f(y - 6.0)}H{f(x + w * .7)}Q{f(x + w * .88)} {f(y + h * .5)} {f(x + w - 2.0)} {f(y + h + 4)}H{f(x + w + 6.0)}Z", curtain)
    sh.rect_r(x - 6, y + h + 2, w + 12, 5, frame, 1)


def floor_boards(sh, y, code="w", n=5):
    sh.rect_r(0, y, 200, 200 - y, code)
    for k in range(1, n): sh.seg(0, y + k * (200 - y) / n, 200, y + k * (200 - y) / n, "l", "stroke-width:.7")


def wallpaper(sh, y1, code="k", motif="m", avoid=()):
    """Behang met hartjes; `avoid` = rechthoeken (x0, y0, x1, y1) waar later iets voor komt."""
    sh.rect_r(0, 0, 200, y1, code)
    for x in range(20, 200, 40):
        for y in range(18, int(y1) - 6, 36):
            hx = x + (20 if (y // 36) % 2 else 0)
            if hx > 194 or any(x0 - 8 <= hx <= x1 + 8 and y0 - 8 <= y <= y1 + 8 for x0, y0, x1, y1 in avoid): continue
            sh.region(heart_path(hx, y, 9), motif)


# ---------------------------------------------------------------- 2-4 jaar
def sint_portret(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    garland(sh, 8, 6, "ryn", 6, 14)
    sh.rect_r(0, 170, 200, 30, "b")
    sint(sh, 100, 26, 1.3, staff_side=1, legs=False)
    gift(sh, 12, 160, 30, 26, "g", "y", "y")
    for x, y in ((150, 186), (162, 190), (174, 186), (186, 191)): pepernoot(sh, x, y, 5)


def piet_zwaait(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    garland(sh, 8, 6, "oyg", 6, 14)
    grass(sh, 176, "l")
    piet(sh, 96, 40, 1.35, suit="o", trouser="p", cap="n", feather="y", hands=((56, 46), (128, 120)), legs=((86, 186), (108, 186)))
    gift(sh, 126, 112, 32, 26, "m", "y", "k")
    for x, y in ((20, 170), (34, 176), (164, 176), (180, 172)): pepernoot(sh, x, y, 5)
    for x, y in ((24, 60), (176, 70)): sparkle(sh, x, y, 9, "y")


def chocoladeletter(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    # zilverpapier achter de letter
    sh.region("M40 30L160 18L176 150L30 166Z", "z")
    sh.line("M48 44L156 34M44 80L162 70M42 118L168 106", "l", "stroke-width:.8")
    sh.ellipse_r(100, 176, 90, 18, "b"); sh.ellipse_r(100, 176, 76, 12, "-")
    # grote letter S van chocolade (een vorm, geen tekst)
    sh.region("M146 40Q146 16 100 16Q52 16 52 54Q52 90 98 96Q122 99 122 116Q122 132 100 132Q78 132 76 116H50Q50 160 100 160Q150 160 150 114Q150 78 104 72Q80 69 80 54Q80 42 100 42Q118 42 120 52Z", "w")
    sh.line("M60 44Q64 26 92 22M128 102Q142 112 138 130", "l", "stroke-width:1.4")
    for x, y in ((40, 172), (52, 180), (30, 182), (156, 176), (168, 182), (148, 184), (176, 172)): pepernoot(sh, x, y, 5)
    sparkle(sh, 20, 20, 9, "y"); sparkle(sh, 184, 30, 8, "y"); sparkle(sh, 184, 130, 7, "y")


# ---------------------------------------------------------------- 4-6 jaar
def piet_met_zak(sh):
    sh.rect_r(0, 0, 200, 190, "n")
    for x, y in ((24, 30), (60, 16), (40, 64), (120, 20)): sh.region(star_path(x, y, 5, 2.2), "y")
    sh.region(moon_path(170, 26, 12), "y")
    # huizen achter
    roof_row(sh, 180, [(-4, 40, 50, "trap", "w"), (150, 54, 44, "punt", "r")])
    chimney(sh, 172, 104, 10, 14, "w")
    grass(sh, 182, "g")
    # zak met lapjes
    sh.region("M118 70Q150 50 168 84Q180 120 150 132Q122 136 112 112Z", "w")
    sh.rect_r(140, 100, 14, 12, "y", 1); sh.rect_r(124, 112, 10, 9, "o", 1)
    sh.line("M120 74Q132 86 128 100", "l", "stroke-width:1.2")
    gift(sh, 132, 60, 18, 12, "r", "y")
    piet(sh, 84, 64, 1.1, suit="r", trouser="n", cap="g", feather="y", hands=((118, 76), (60, 140)), legs=((76, 184), (94, 184)))
    for x in (40, 52, 150, 168): pepernoot(sh, x, 188, 4)


def stoomboot(sh):
    sh.rect_r(0, 0, 200, 140, "-")
    for x, y, r in ((30, 30, 9), (150, 20, 7)): sh.region(cloud_path(x, y, r), "-")
    # kade met huizen links
    roof_row(sh, 132, [(-4, 28, 40, "trap", "o"), (24, 24, 30, "punt", "g")])
    sh.rect_r(0, 128, 52, 14, "z")
    sh.region("M0 140Q25 134 50 140T100 140T150 140T200 140V200H0Z", "b")
    for y, c in ((158, "n"), (178, "t")):
        sh.region(f"M0 {y}Q25 {y - 6} 50 {y}T100 {y}T150 {y}T200 {y}V{y + 10}Q175 {y + 4} 150 {y + 10}T100 {y + 10}T50 {y + 10}T0 {y + 10}Z", c)
    boat(sh, 120, 148, .95)
    # vlaggetjes van schoorsteen naar boeg
    sh.line("M134 80L62 120", "l", "stroke-width:1")
    for k in range(5):
        x, y = 128 - k * 15, 84 + k * 8.2
        if 70 < x < 114: continue
        sh.poly_r([(x - 4, y), (x + 4, y - 2), (x + 1, y + 8)], "ryn"[k % 3])
    sint(sh, 92, 56, .42, staff_side=1, legs=False, wave=True)
    piet(sh, 138, 82, .34, suit="m", trouser="y", cap="g", feather="-", hands=((128, 92), (148, 108)), draw_legs=False)
    for x, y in ((176, 50), (70, 20)): sh.line(f"M{x - 7} {y}Q{x - 3} {y - 5} {x} {y}Q{x + 3} {y - 5} {x + 7} {y}", "l", "stroke-width:1.2")


def piet_schoorsteen(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region(moon_path(36, 34, 14), "y")
    for x, y in ((80, 20), (112, 14), (178, 18), (184, 66)): sh.region(star_path(x, y, 6, 2.6), "y")
    sh.region("M-4 200V112L100 70L204 112V200Z", "r")
    for k in range(5):
        y = 120 + k * 16
        sh.line(f"M0 {y}H200", "l", "stroke-width:.7")
    # dakkapel
    sh.rect_r(26, 128, 40, 30, "w", 1); sh.poly_r([(20, 130), (46, 112), (72, 130)], "z")
    window(sh, 34, 134, 24, 18, "y", None, "-")
    chimney(sh, 112, 66, 44, 60, "w")
    # Piet komt uit de schoorsteen
    hy = 44
    sh.circle_r(118, 72, 7, "-"); sh.circle_r(150, 72, 7, "-")
    sh.region("M114 66V58Q134 50 154 58V66Z", "o")
    sh.circle_r(134, hy, 15, "-")
    sh.region(f"M119 {hy}A15 15 0 0 1 149 {hy}Q145 {hy - 3} 141 {hy - 8}Q137 {hy - 3} 133 {hy - 8}Q129 {hy - 3} 125 {hy - 8}Q121 {hy - 3} 119 {hy}Z", "x")
    beret(sh, 134, hy, 1, "g", "y"); sh.circle_r(141, hy - 14, 2.6, "y")
    eye(sh, 129, hy + 3, 1.8); eye(sh, 139, hy + 3, 1.8); smile(sh, 134, hy + 8, 4)
    soot(sh, 134, hy, 1)
    gift(sh, 86, 160, 34, 26, "m", "y", "k"); gift(sh, 150, 166, 26, 20, "g", "r", "l")


def amerigo_wortel(sh):
    sh.rect_r(0, 0, 200, 170, "b")
    sh.region(cloud_path(40, 30, 10), "-"); sh.region(cloud_path(150, 22, 8), "-")
    # huisje met deur, ramen en bloembak
    sh.rect_r(150, 70, 46, 100, "w"); sh.poly_r([(146, 70), (173, 44), (200, 70)], "r")
    sh.rect_r(166, 130, 16, 40, "g", 1); sh.circle_r(178, 152, 1.8, "y")
    window(sh, 156, 84, 12, 14, "y"); window(sh, 180, 84, 12, 14, "y")
    sh.rect_r(154, 104, 18, 6, "w", 1)
    for x in (157, 163, 169): sh.circle_r(x, 102, 2.6, "m")
    # hekje
    for x in range(4, 140, 14): sh.rect_r(x, 150, 6, 22, "-", 1)
    sh.rect_r(0, 156, 146, 4, "-"); sh.rect_r(0, 164, 146, 4, "-")
    grass(sh, 168, "g")
    for x in (158, 188): sh.circle_r(x, 186, 3.2, "y"); sh.circle_r(x, 186, 1.4, "o")
    horse(sh, 104, 186, 1.05, flip=True)
    # klompje met wortel, bij de neus van het paard
    sh.region("M10 194Q8 180 16 174H40Q50 176 56 184Q64 186 72 180Q76 194 62 196H14Z", "y")
    sh.ellipse_r(28, 176, 11, 3.6, "w")
    sh.region("M28 176L34 140L42 144Z", "o"); sh.line("M32 162L36 160M34 152L38 151", "l", "stroke-width:1")
    sh.region("M38 142Q36 130 42 124Q42 134 40 140Q46 132 52 132Q48 140 40 144Z", "g")


# ---------------------------------------------------------------- 6-9 jaar
def sint_op_het_dak(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.circle_r(160, 34, 20, "y")
    for x, y in ((24, 20), (60, 46), (106, 16), (128, 52), (190, 72), (14, 78)): sh.region(star_path(x, y, 5, 2.2), "y")
    roof_row(sh, 150, [(-6, 52, 40, "trap", "w"), (46, 46, 26, "punt", "o"), (92, 56, 46, "trap", "r"), (140, 66, 34, "plat", "g")])
    for x in (4, 54, 100, 150):  # deuren
        sh.rect_r(x + 12, 140, 12, 18, "w", 1)
    chimney(sh, 64, 102, 12, 22, "r")
    sh.region(cloud_path(70, 88, 5), "z")
    sh.rect_r(0, 160, 200, 40, "z")
    for x in range(0, 200, 20): sh.seg(x, 160, x, 200, "l", "stroke-width:.6")
    for x in (40, 160): sh.rect_r(x - 2, 160, 4, 28, "x"); sh.circle_r(x, 158, 6, "y")
    # Sinterklaas te paard op het platte dak
    sint(sh, 178, 38, .36, staff_side=0, legs=False)
    horse(sh, 172, 116, .62, flip=True)
    # Piet bij de schoorsteen
    piet(sh, 34, 74, .5, suit="b", trouser="m", cap="r", feather="y", hands=((24, 108), (56, 96)), legs=((30, 116), (40, 116)))
    gift(sh, 54, 86, 10, 8, "m", "y")


def bakkerij(sh):
    sh.rect_r(0, 0, 200, 140, "k")
    for x in range(0, 200, 20):
        for y in range(0, 140, 20):
            if (x // 20 + y // 20) % 2: sh.rect_r(x, y, 20, 20, "-")
    # plank met potten
    sh.rect_r(4, 22, 40, 4, "w")
    for x, c in ((10, "y"), (24, "o"), (36, "b")):
        sh.rect_r(x - 5, 8, 10, 14, c, 2); sh.rect_r(x - 6, 5, 12, 4, "w", 1)
    sh.rect_r(0, 140, 200, 60, "w")
    for k in range(1, 4): sh.seg(0, 140 + k * 15, 200, 140 + k * 15, "l", "stroke-width:.7")
    # oven
    sh.rect_r(124, 30, 70, 100, "z", 4); sh.rect_r(134, 70, 50, 40, "x", 3)
    for x in (146, 159, 172): sh.region(f"M{x - 6} 110Q{x - 7} 98 {x} 88Q{x + 7} 98 {x + 6} 110Z", "o")
    sh.rect_r(134, 40, 50, 20, "-", 2)
    for x in (146, 160, 172): sh.circle_r(x, 50, 4, "r")
    piet(sh, 60, 26, .9, suit="t", trouser="n", cap="r", feather="-", hands=((30, 112), (92, 112)), draw_legs=False, arms_front=True)
    # tafel met bakplaat vol pepernoten, deegroller en meelzak
    sh.rect_r(10, 120, 112, 10, "w"); sh.rect_r(16, 130, 8, 50, "w"); sh.rect_r(108, 130, 8, 50, "w")
    sh.rect_r(34, 110, 54, 10, "z", 1)
    for i in range(6): pepernoot(sh, 40 + i * 8.4, 106, 3.4)
    for i in range(5): pepernoot(sh, 44 + i * 8.4, 100, 3.4)
    sh.region("M100 120Q100 104 110 104Q120 104 120 120Z", "-")
    sh.rect_r(12, 114, 18, 5, "y", 2)
    sh.region("M146 196Q138 170 150 158L148 150H172L170 158Q182 170 174 196Z", "-"); sh.line("M150 154H170", "l", "stroke-width:1")
    for x, y in ((40, 170), (52, 176), (82, 168), (94, 186)): pepernoot(sh, x, y, 4)


def grote_boek(sh):
    wallpaper(sh, 150, "p", "m", avoid=((10, 10, 62, 70), (66, 10, 142, 150), (146, 46, 200, 120), (14, 76, 186, 175)))
    floor_boards(sh, 150, "w", 4)
    sh.ellipse_r(100, 182, 70, 12, "r"); sh.ellipse_r(100, 182, 54, 8, "y")
    # raam met gordijnen en maan
    window(sh, 18, 18, 36, 44, "n", "r", "-")
    sh.region(moon_path(46, 30, 6), "y")
    # Sint achter het bureau, in zijn stoel
    sh.rect_r(70, 30, 68, 80, "w", 12)
    sint(sh, 104, 16, .62, staff_side=0, legs=False)
    sh.rect_r(20, 118, 160, 14, "w", 2); sh.rect_r(30, 132, 140, 40, "w")
    sh.rect_r(50, 140, 40, 22, "-", 2); sh.rect_r(110, 140, 40, 22, "-", 2)
    for x in (70, 130): sh.circle_r(x, 151, 3, "y")
    # het boek
    sh.region("M60 120L100 112L140 120V96L100 88L60 96Z", "r")
    sh.region("M64 116L100 109V92L64 99Z", "-"); sh.region("M136 116L100 109V92L136 99Z", "-")
    for k in range(4):
        sh.line(f"M70 {102 + k * 3.4}L94 {97 + k * 3.4}M106 {97 + k * 3.4}L130 {102 + k * 3.4}", "l", "stroke-width:.7")
    # kaars, ganzenveer en stapel boeken
    sh.rect_r(160, 90, 10, 28, "-"); sh.region("M165 88Q159 80 165 72Q171 80 165 88Z", "y")
    sh.ellipse_r(165, 118, 12, 3, "y")
    sh.region("M28 116Q20 92 40 80Q36 98 32 116Z", "-")
    for k, c in enumerate("gno"): sh.rect_r(174 - k * 1, 60 - k * 8, 22, 8, c, 1)


def surprise(sh):
    wallpaper(sh, 150, "t", "-", avoid=((14, 8, 106, 56), (104, 0, 164, 124), (40, 40, 100, 124)))
    # tekeningen aan de muur
    sh.rect_r(20, 20, 40, 30, "-", 1); sh.circle_r(40, 32, 7, "y"); sh.line("M24 46L36 38L46 46L56 36", "l", "stroke-width:1")
    sh.rect_r(70, 14, 30, 36, "-", 1); sh.region(heart_path(85, 32, 10), "r")
    sh.rect_r(0, 150, 200, 50, "y")
    sh.rect_r(10, 120, 180, 10, "w"); sh.rect_r(20, 130, 8, 64, "w"); sh.rect_r(172, 130, 8, 64, "w")
    # surprise: een giraf van dozen
    sh.rect_r(112, 70, 44, 50, "o", 2); sh.rect_r(140, 20, 12, 52, "o", 2); sh.rect_r(136, 8, 24, 16, "o", 4)
    for x, y in ((118, 78), (130, 96), (146, 84), (120, 104), (144, 36), (142, 56)): sh.circle_r(x, y, 4, "w")
    eye(sh, 152, 14, 1.6); sh.rect_r(140, 2, 3, 7, "w"); sh.rect_r(150, 2, 3, 7, "w")
    # kind met kwast
    person(sh, 64, 52, "g", "n", hands=((92, 96), (50, 112)), style="pony", hair="o", s=.9, draw_legs=False)
    # verf, lijm en schaar
    for x, c in ((30, "r"), (44, "n"), (58, "y")): sh.rect_r(x - 5, 108, 10, 12, c, 2)
    sh.rect_r(80, 106, 8, 14, "-", 2); sh.rect_r(81, 102, 6, 5, "r", 1)
    sh.circle_r(176, 114, 4, "-"); sh.circle_r(184, 114, 4, "-"); sh.line("M176 110L168 96M184 110L172 96", "l", "stroke-width:1.6")
    # gedichtje als kladje (lijntjes, geen tekst) en inpakpapier
    sh.rect_r(20, 160, 50, 34, "-", 1)
    for k in range(4): sh.line(f"M26 {168 + k * 7}H{62 - (k % 2) * 10}", "l", "stroke-width:.8")
    sh.raw('<g transform="rotate(-8 130 176)">'); sh.rect_r(100, 162, 60, 28, "m", 1)
    for x in (110, 124, 138, 152): sh.region(star_path(x, 176, 4.5, 2), "y")
    sh.raw("</g>")


# ---------------------------------------------------------------- nieuw: jonge kinderen, rijker
def sint_en_piet(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    garland(sh, 6, 6, "rny", 6, 14)
    grass(sh, 180, "l")
    sint(sh, 64, 30, .9, staff_side=-1, legs=True, wave=True)
    piet(sh, 148, 66, .95, suit="g", trouser="o", cap="r", feather="y", hands=((180, 70), (124, 132)), legs=((140, 188), (156, 188)))
    for x, y in ((112, 186), (122, 190), (190, 190)): pepernoot(sh, x, y, 4.5)


def cadeautjes(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    garland(sh, 6, 5, "ym", 8, 16)
    sh.rect_r(0, 176, 200, 24, "w")
    gift(sh, 20, 124, 64, 52, "r", "y", "y")
    gift(sh, 96, 136, 52, 40, "n", "y", "b")
    gift(sh, 150, 150, 40, 26, "g", "r", "l")
    gift(sh, 44, 84, 40, 32, "m", "y", "k")
    gift(sh, 108, 100, 30, 28, "o", "n")
    for x, y in ((10, 190), (190, 120), (176, 132)): pepernoot(sh, x, y, 5)
    sparkle(sh, 170, 60, 10, "y"); sparkle(sh, 24, 60, 8, "y")


def sint_te_paard(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.region(cloud_path(40, 26, 10), "-"); sh.region(cloud_path(166, 20, 8), "-")
    grass(sh, 176, "g")
    sint(sh, 92, 46, .58, staff_side=-1, legs=False)
    horse(sh, 104, 192, 1.3)


def schoen_kachel(sh):
    wallpaper(sh, 140, "g", "y", avoid=((50, 0, 150, 144),))
    floor_boards(sh, 140, "w", 4)
    # kachel met vuur
    sh.rect_r(60, 40, 80, 104, "z", 6); sh.rect_r(52, 32, 96, 12, "x", 3); sh.rect_r(90, 0, 20, 32, "z")
    sh.rect_r(76, 76, 48, 40, "x", 4)
    for x in (88, 100, 112): sh.region(f"M{x - 7} 114Q{x - 8} 100 {x} 86Q{x + 8} 100 {x + 7} 114Z", "o")
    for x in (88, 100, 112): sh.region(f"M{x - 3} 114Q{x - 4} 106 {x} 98Q{x + 4} 106 {x + 3} 114Z", "y")
    sh.rect_r(66, 124, 68, 8, "-", 2)
    # schoen met wortel en tekening
    sh.region("M24 192V170Q24 160 34 160H58Q66 160 70 168L92 172Q104 174 102 192Z", "r")
    sh.rect_r(22, 190, 82, 6, "x", 2)
    sh.raw('<g transform="rotate(-25 40 160)">'); sh.region("M36 168L40 126L46 168Z", "o")
    sh.region("M40 126Q34 116 38 110Q42 118 40 124Q44 114 50 112Q48 122 40 126Z", "g"); sh.raw("</g>")
    sh.raw('<g transform="rotate(10 64 146)">'); sh.rect_r(52, 126, 26, 32, "-", 1); sh.region(heart_path(65, 140, 8), "m"); sh.raw("</g>")
    # suikerklontjes en een emmer water voor het paard
    for x, y in ((120, 182), (130, 184), (125, 176)): sh.rect_r(x - 4, y - 4, 8, 8, "-", 1)
    sh.region("M150 196L146 160H190L186 196Z", "b"); sh.ellipse_r(168, 160, 22, 5, "t")


def piet_muziek(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    roof_row(sh, 150, [(-4, 40, 70, "trap", "o"), (36, 36, 54, "punt", "r"), (150, 54, 64, "trap", "w")])
    garland(sh, 30, 7, "ryn", 8, 12)
    sh.rect_r(0, 150, 200, 50, "z")
    for x in range(0, 200, 16): sh.seg(x, 150, x, 200, "l", "stroke-width:.6")
    piet(sh, 100, 70, .95, suit="p", trouser="y", cap="g", feather="r", hands=((80, 138), (124, 120)), legs=((92, 196), (108, 196)))
    # trommel
    sh.ellipse_r(100, 150, 26, 7, "-"); sh.rect_r(74, 150, 52, 30, "r"); sh.ellipse_r(100, 180, 26, 7, "r")
    sh.line("M74 154L86 176L100 154L114 176L126 154", "l", "stroke-width:1.4")
    sh.rect_r(122, 110, 3, 26, "w", 1); sh.circle_r(124, 108, 4, "-")
    # muzieknoten
    for x, y in ((40, 100), (160, 90), (172, 120)):
        sh.ellipse_r(x, y, 4.5, 3.4, "x"); sh.line(f"M{x + 4} {y}V{y - 16}Q{x + 10} {y - 12} {x + 12} {y - 6}", "l", "stroke-width:1.4")


def sint_leest_voor(sh):
    wallpaper(sh, 140, "o", "y", avoid=((50, 30, 150, 140),))
    floor_boards(sh, 140, "w", 4)
    sh.ellipse_r(100, 176, 90, 18, "g")
    # stoel
    sh.rect_r(60, 50, 80, 100, "r", 14); sh.rect_r(52, 110, 96, 20, "r", 6)
    sint(sh, 100, 32, .62, staff_side=0, legs=False)
    # open boek op schoot
    sh.region("M80 122L100 116L120 122V108L100 102L80 108Z", "y")
    sh.region("M82 120L100 115V104L82 109Z", "-"); sh.region("M118 120L100 115V104L118 109Z", "-")
    # kinderen op de grond
    s = .52
    person(sh, 34, 120, "m", "n", hands=((22, 160), (46, 160)), style="pony", hair="o", s=s, draw_legs=False)
    sit_legs(sh, 34, 172, s, "n")
    person(sh, 166, 120, "y", "z", hands=((154, 160), (178, 160)), style="curly", hair="x", s=s, draw_legs=False)
    sit_legs(sh, 166, 172, s, "z")
    gift(sh, 88, 160, 24, 18, "n", "y", "b")


def haven(sh):
    sh.rect_r(0, 0, 200, 110, "-")
    for x, y, r in ((24, 20, 8), (120, 14, 7), (180, 30, 6)): sh.region(cloud_path(x, y, r), "-")
    roof_row(sh, 106, [(-4, 30, 50, "trap", "w"), (26, 26, 40, "punt", "r"), (52, 32, 60, "trap", "o"), (84, 26, 44, "punt", "g")])
    sh.rect_r(0, 100, 120, 10, "z")
    sh.rect_r(0, 110, 200, 90, "n")
    for y in (130, 150, 170, 190):
        sh.line(f"M4 {y}Q14 {y - 4} 24 {y}T44 {y}M70 {y + 4}Q80 {y} 90 {y + 4}T110 {y + 4}", "l", "stroke-width:1")
    boat(sh, 140, 170, .78)
    # meeuwen en vlaggen
    for x, y in ((150, 60), (176, 76)): sh.line(f"M{x - 7} {y}Q{x - 3} {y - 5} {x} {y}Q{x + 3} {y - 5} {x + 7} {y}", "l", "stroke-width:1.2")
    sh.rect_r(112, 40, 2, 62, "x"); sh.poly_r([(114, 40), (134, 46), (114, 52)], "r"); sh.poly_r([(114, 52), (134, 58), (114, 64)], "-")
    sh.poly_r([(114, 64), (134, 70), (114, 76)], "n")
    # kade met kinderen die zwaaien
    for x, c, h, st in ((24, "y", "o", "pony"), (52, "g", "x", "curly"), (80, "m", "w", "long")):
        person(sh, x, 64, c, "n", hands=((x - 12, 62), (x + 12, 88)), style=st, hair=h, s=.42)


def chocolademelk(sh):
    wallpaper(sh, 150, "b", "-", avoid=((0, 10, 90, 152), (92, 30, 196, 150)))
    floor_boards(sh, 150, "w", 4)
    # haard met vuur
    sh.rect_r(10, 40, 70, 112, "r"); sh.rect_r(4, 32, 82, 10, "w", 2); sh.rect_r(24, 80, 42, 72, "x", 2)
    for x in (34, 45, 56): sh.region(f"M{x - 6} 150Q{x - 7} 136 {x} 122Q{x + 7} 136 {x + 6} 150Z", "o")
    for k in range(4):
        sh.seg(10, 52 + k * 7, 24, 52 + k * 7, "l", "stroke-width:.6"); sh.seg(66, 52 + k * 7, 80, 52 + k * 7, "l", "stroke-width:.6")
    for x, c in ((20, "m"), (46, "g"), (70, "n")): sh.rect_r(x - 5, 18, 10, 14, c, 1)
    # Sint in zijn stoel met een beker
    sh.rect_r(104, 52, 80, 100, "g", 14); sh.rect_r(96, 112, 96, 20, "g", 6)
    sint(sh, 144, 34, .62, staff_side=0, legs=False)
    sh.rect_r(116, 104, 14, 16, "-", 2); sh.region("M130 108Q138 110 130 116", "-")
    for x in (120, 126): sh.line(f"M{x} 100Q{x - 3} 94 {x} 88", "l", "stroke-width:1")
    # tafeltje met speculaas en pepernoten
    sh.rect_r(92, 156, 50, 6, "w", 2); sh.rect_r(112, 162, 10, 28, "w")
    sh.rect_r(98, 146, 16, 10, "o", 1); sh.rect_r(118, 146, 16, 10, "o", 1)
    for x in (104, 128): sh.line(f"M{x - 3} 149L{x + 3} 153M{x + 3} 149L{x - 3} 153", "l", "stroke-width:.8")
    for x, y in ((160, 186), (170, 190), (180, 186)): pepernoot(sh, x, y, 4)


# ---------------------------------------------------------------- 9+ jaar
def intocht(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.region(cloud_path(40, 24, 9), "-"); sh.region(cloud_path(150, 16, 7), "-")
    # grachtenpanden
    roof_row(sh, 96, [(-4, 34, 50, "trap", "w"), (30, 30, 40, "punt", "r"), (60, 36, 56, "trap", "o"), (96, 30, 44, "punt", "g"), (126, 36, 52, "trap", "w"), (162, 42, 42, "punt", "r")])
    sh.rect_r(0, 96, 200, 10, "z")
    for x in range(0, 200, 10): sh.seg(x, 96, x, 106, "l", "stroke-width:.6")
    # water en boot
    sh.rect_r(0, 106, 200, 40, "n")
    boat(sh, 140, 140, .52)
    # kade met kinderen
    sh.rect_r(0, 146, 200, 54, "z")
    for x in range(0, 200, 16): sh.seg(x, 146, x, 200, "l", "stroke-width:.6")
    for i, (x, c, h, st) in enumerate(((20, "y", "o", "pony"), (52, "m", "x", "curly"), (148, "g", "w", "long"), (180, "p", "y", "short"))):
        person(sh, x, 150, c, "n", hands=((x - 14, 150), (x + 14, 176)), style=st, hair=h, s=.5)
    sint(sh, 96, 88, .46, staff_side=1, legs=True)
    piet(sh, 128, 146, .5, suit="r", trouser="y", cap="g", feather="-", hands=((114, 176), (142, 150)))
    # vlaggetjes
    sh.line("M0 30Q100 52 200 30", "l", "stroke-width:1")
    for k in range(9):
        x = 12 + k * 22; y = 30 + 22 * (1 - ((x - 100) / 100) ** 2) * .9
        sh.poly_r([(x - 6, y - 1), (x + 6, y - 1), (x, y + 10)], "rny"[k % 3])


def pieten_op_het_dak(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.circle_r(40, 34, 18, "y")
    for x, y in ((90, 16), (120, 40), (170, 22), (190, 60), (70, 52)): sh.region(star_path(x, y, 5, 2.2), "y")
    roof_row(sh, 170, [(-6, 60, 40, "punt", "w"), (56, 50, 70, "trap", "r"), (108, 46, 50, "punt", "o"), (156, 50, 80, "trap", "g")])
    sh.rect_r(0, 180, 200, 20, "z")
    chimney(sh, 34, 106, 14, 22, "r"); chimney(sh, 120, 92, 12, 22, "w")
    # touw tussen de daken met een klimmende Piet
    sh.line("M48 104Q100 130 160 70", "l", "stroke-width:1.4")
    piet(sh, 100, 82, .42, suit="m", trouser="t", cap="y", feather="r", hands=((92, 118), (108, 116)), legs=((96, 140), (110, 132)))
    piet(sh, 176, 58, .4, suit="o", trouser="n", cap="p", feather="y", hands=((166, 76), (190, 74)), legs=((170, 97), (184, 97)))
    present(sh, 168, 46, 14, 10, "r", "y")
    piet(sh, 30, 72, .38, suit="g", trouser="r", cap="b", feather="y", hands=((20, 94), (44, 96)), legs=((26, 104), (36, 104)))
    for x, y in ((60, 160), (90, 156), (140, 162)): sh.circle_r(x, y, 3, "w")


def mijter_knutselen():
    """Knipplaat (A4): een mijter om op te zetten, met een hoofdband van twee stroken."""
    sh = Sheet(280)
    cx, base = 100, 196
    outline = (f"M{cx - 58} {base}C{cx - 66} {base - 60} {cx - 40} {base - 130} {cx} {base - 176}"
               f"C{cx + 40} {base - 130} {cx + 66} {base - 60} {cx + 58} {base}Z")
    sh.region(outline, "r")
    sh.rect_r(cx - 60, base - 22, 120, 22, "y", 2)
    sh.region(f"M{cx - 7} {base - 140}H{cx + 7}V{base - 118}H{cx + 26}V{base - 104}H{cx + 7}V{base - 50}H{cx - 7}V{base - 104}H{cx - 26}V{base - 118}H{cx - 7}Z", "y")
    for x in (cx - 40, cx - 20, cx, cx + 20, cx + 40): sh.circle_r(x, base - 11, 4, "m")
    for x, y in ((cx - 36, base - 60), (cx + 36, base - 60), (cx - 24, base - 110), (cx + 24, base - 110)): sh.region(star_path(x, y, 6, 2.6), "y")
    sh.line(outline, "cut")
    # hoofdband: twee stroken
    for y in (214, 238):
        sh.rect_r(12, y, 176, 18, "y", 2); sh.rect_line(12, y, 176, 18, "cut", 2)
        for x in range(30, 180, 30): sh.circle_r(x, y + 9, 3.6, "r")
    sh.legend(["cut"], 274)
    write(OUT, "mijter-om-op-te-zetten", sh, {"category": "feest", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 25, "holiday": "sinterklaas", "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}, {"slug": "plakband"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Mijter om op te zetten", "printNote": "Op stevig papier (160 gram) blijft de mijter mooi rechtop staan.", "steps": [
            "Kleur de mijter en de twee stroken in. Het kruis en de rand zijn van goud: geel of goudstift.",
            "Knip de mijter en de stroken uit langs de streepjeslijnen.",
            "Plak de twee stroken aan elkaar tot één lange band en meet hem om je hoofd.",
            "Plak de band dicht met plakband en plak de mijter er van voren op. Nu ben je net Sinterklaas!"]}}})


PLATES = [
    ("sinterklaas-portret", "Sinterklaas met zijn mijter", "2-4", 1, sint_portret),
    ("roetveegpiet-zwaait", "Roetveegpiet zwaait", "2-4", 1, piet_zwaait),
    ("chocoladeletter", "Chocoladeletter en pepernoten", "2-4", 1, chocoladeletter),
    ("piet-met-de-zak", "Piet met de zak vol cadeautjes", "4-6", 2, piet_met_zak),
    ("stoomboot-komt-aan", "De stoomboot komt aan", "4-6", 2, stoomboot),
    ("piet-in-de-schoorsteen", "Piet in de schoorsteen", "4-6", 2, piet_schoorsteen),
    ("amerigo-en-de-wortel", "Het paard van Sinterklaas en een wortel", "4-6", 2, amerigo_wortel),
    ("sint-en-piet-zwaaien", "Sinterklaas en Piet zwaaien", "2-4", 1, sint_en_piet),
    ("stapel-cadeautjes", "Een stapel cadeautjes", "2-4", 1, cadeautjes),
    ("sint-rijdt-op-zijn-paard", "Sint rijdt op zijn paard", "2-4", 1, sint_te_paard),
    ("schoen-bij-de-kachel", "Je schoen bij de kachel", "4-6", 2, schoen_kachel),
    ("piet-maakt-muziek", "Piet maakt muziek", "4-6", 2, piet_muziek),
    ("sinterklaas-leest-voor", "Sinterklaas leest voor", "4-6", 2, sint_leest_voor),
    ("pakjesboot-in-de-haven", "De pakjesboot in de haven", "6-9", 2, haven),
    ("warme-chocolademelk", "Sinterklaas met warme chocolademelk", "6-9", 2, chocolademelk),
    ("sinterklaas-op-het-dak", "Sinterklaas op het dak", "6-9", 3, sint_op_het_dak),
    ("pepernotenbakkerij", "De pepernotenbakkerij", "6-9", 2, bakkerij),
    ("het-grote-boek", "Sinterklaas en het Grote Boek", "6-9", 3, grote_boek),
    ("surprise-maken", "Een surprise maken", "6-9", 2, surprise),
    ("intocht-van-sinterklaas", "De intocht van Sinterklaas", "9+", 3, intocht),
    ("pieten-op-het-dak", "Pieten op de daken", "9+", 3, pieten_op_het_dak),
]

if __name__ == "__main__":
    for slug, name, age, diff, draw in PLATES:
        if ONLY and slug not in ONLY: continue
        kp(slug, name, "feest", age, diff, draw, "sinterklaas")
    if not ONLY or "mijter-om-op-te-zetten" in ONLY:
        mijter_knutselen()
