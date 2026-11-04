"""Batch 45: kerst en winter (eigen tekeningen, 200x200) voor 2 tot en met 9+ jaar.

Kerstman (eigen ontwerp: rode jas met witte rand, muts met pompon, witte baard), elfjes met puntmuts en
puntoren, rendieren (bruine neus: geen bekend figuur), sleeën, sneeuwpoppen, peperkoek en kerstbomen.
Kinderen en elfjes met verschillende kapsels; geen tekst op de platen.
Gebruik: OUT=/tmp/kerst python3 batch45_kerst.py [slug ...]
"""
import math, sys
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from batch35a import person, present, limb, blob, sparkle, beanie, scarf, face
from batch44_sint import floor_boards
from shapes import star_path, moon_path, cloud_path, heart_path, drop_path, leaf_path

ONLY = set(sys.argv[1:])


# ---------------------------------------------------------------- kleine dingen
def snowflake(sh, x, y, r, w=1):
    """Sneeuwvlokje als lijntjes (geen vlak)."""
    d = ""
    for k in range(3):
        a = math.radians(k * 60)
        dx, dy = r * math.cos(a), r * math.sin(a)
        d += f"M{f(x - dx)} {f(y - dy)}L{f(x + dx)} {f(y + dy)}"
    sh.line(d, "l", f"stroke-width:{w}")


def flakes(sh, spots, r=3.5):
    for x, y in spots: snowflake(sh, x, y, r)


def snow_ground(sh, y, code="-", wave=8):
    sh.region(f"M0 200V{y}Q50 {y - wave} 100 {y}T200 {y}V200Z", code)


def pine(sh, x, base, h, code="g", snow=False, trunk="w"):
    sh.rect_r(x - h * .06, base - h * .12, h * .12, h * .12, trunk)
    for k in range(3):
        y0 = base - h * .12 - k * h / 3.6; w = h * (.42 - k * .1)
        sh.region(f"M{f(x - w)} {f(y0)}L{f(x)} {f(y0 - h / 2.2)}L{f(x + w)} {f(y0)}Q{f(x)} {f(y0 - h * .05)} {f(x - w)} {f(y0)}Z", code)
        if snow:
            sh.region(f"M{f(x - w * .35)} {f(y0 - h / 2.2 * .65)}L{f(x)} {f(y0 - h / 2.2)}L{f(x + w * .35)} {f(y0 - h / 2.2 * .65)}Q{f(x)} {f(y0 - h / 2.2 * .55)} {f(x - w * .35)} {f(y0 - h / 2.2 * .65)}Z", "-")


def xmas_tree(sh, cx, base, h, balls=True, star=True, code="g", pot="r"):
    """Versierde kerstboom in een pot. base = onderkant van de pot."""
    sh.rect_r(cx - h * .06, base - h * .16, h * .12, h * .06, "w")
    sh.region(f"M{f(cx - h * .14)} {f(base - h * .11)}H{f(cx + h * .14)}L{f(cx + h * .11)} {f(base)}H{f(cx - h * .11)}Z", pot)
    tiers = ((base - h * .15, h * .38, h * .34), (base - h * .4, h * .3, h * .32), (base - h * .62, h * .21, h * .3))
    for y0, w, th in tiers:
        sh.region(f"M{f(cx - w)} {f(y0)}Q{f(cx - w * .5)} {f(y0 - th * .2)} {f(cx)} {f(y0 - th)}Q{f(cx + w * .5)} {f(y0 - th * .2)} {f(cx + w)} {f(y0)}Q{f(cx)} {f(y0 - th * .18)} {f(cx - w)} {f(y0)}Z", code)
    if balls:
        cols = "rybmtno"
        for i, (y0, w, th) in enumerate(tiers):
            for k, dx in enumerate((-.55, 0, .55)):
                if i == 2 and k != 1: continue
                sh.circle_r(cx + w * dx, y0 - th * .25 + (abs(dx) * th * .1), max(2.4, h * .028), cols[(i * 3 + k) % len(cols)])
    if star:
        sh.region(star_path(cx, base - h * .9, h * .08, h * .035), "y")


def candle(sh, x, base, h, w=8, code="r", flame=True):
    sh.rect_r(x - w / 2, base - h, w, h, code, 1)
    if flame:
        sh.region(drop_path(x, base - h - w * .55, w * .32), "y")
        sh.seg(x, base - h, x, base - h - 1.4, "l", "stroke-width:.8")


def holly(sh, x, y, s=1, berries="r"):
    for a in (-35, 35):
        sh.raw(f'<g transform="rotate({a} {f(x)} {f(y)})">')
        sh.region(f"M{f(x)} {f(y)}Q{f(x - 4 * s)} {f(y - 6 * s)} {f(x - 2 * s)} {f(y - 12 * s)}Q{f(x)} {f(y - 10 * s)} {f(x + 2 * s)} {f(y - 12 * s)}Q{f(x + 4 * s)} {f(y - 6 * s)} {f(x)} {f(y)}Z", "g")
        sh.raw("</g>")
    for dx, dy in ((-2.4, 1.4), (2.4, 1.4), (0, -1.2)):
        sh.circle_r(x + dx * s, y + dy * s, 2.2 * s, berries)


def bow(sh, x, y, s=1, code="r"):
    sh.region(f"M{f(x)} {f(y)}C{f(x - 14 * s)} {f(y - 12 * s)} {f(x - 16 * s)} {f(y + 8 * s)} {f(x)} {f(y)}Z", code)
    sh.region(f"M{f(x)} {f(y)}C{f(x + 14 * s)} {f(y - 12 * s)} {f(x + 16 * s)} {f(y + 8 * s)} {f(x)} {f(y)}Z", code)
    sh.region(f"M{f(x - 2 * s)} {f(y + 1 * s)}L{f(x - 8 * s)} {f(y + 16 * s)}L{f(x - 3 * s)} {f(y + 14 * s)}Z", code)
    sh.region(f"M{f(x + 2 * s)} {f(y + 1 * s)}L{f(x + 8 * s)} {f(y + 16 * s)}L{f(x + 3 * s)} {f(y + 14 * s)}Z", code)
    sh.circle_r(x, y, 3 * s, code)


def candy_cane(sh, x, base, h, s=1, code="r"):
    """Zuurstok: steel met een haak naar rechts en schuine streepjes."""
    w, R = 7 * s, 8 * s
    ro, ri = R + w / 2, R - w / 2
    sh.region(f"M{f(x - w / 2)} {f(base)}V{f(base - h)}A{f(ro)} {f(ro)} 0 0 1 {f(x + 2 * R + w / 2)} {f(base - h)}V{f(base - h + 8 * s)}H{f(x + 2 * R - w / 2)}"
              f"V{f(base - h)}A{f(ri)} {f(ri)} 0 0 0 {f(x + w / 2)} {f(base - h)}V{f(base)}Z", "-")
    for k in range(int((h - 6 * s) / (10 * s))):
        y = base - 6 * s - k * 10 * s
        sh.region(f"M{f(x - w / 2)} {f(y)}L{f(x + w / 2)} {f(y - 4 * s)}V{f(y - 1 * s)}L{f(x - w / 2)} {f(y + 3 * s)}Z", code)


def house(sh, x, base, w, h, wall="r", roof="w", snow=True, door=True, light="y", chimney=True, skip=()):
    """Huisje met puntdak en sneeuw. Geeft de top van het dak terug."""
    sh.rect_r(x, base - h, w, h, wall)
    top = base - h - w * .5
    if chimney:
        sh.rect_r(x + w * .66, top + w * .12, w * .12, w * .3, "w")
    sh.poly_r([(x - 4, base - h), (x + w / 2, top), (x + w + 4, base - h)], roof)
    if snow:
        sh.region(f"M{f(x - 4)} {f(base - h)}L{f(x + w / 2)} {f(top)}L{f(x + w + 4)} {f(base - h)}Q{f(x + w * .8)} {f(base - h - 5)} {f(x + w * .62)} {f(base - h - w * .2)}"
                  f"Q{f(x + w / 2)} {f(top + w * .22)} {f(x + w * .38)} {f(base - h - w * .2)}Q{f(x + w * .2)} {f(base - h - 5)} {f(x - 4)} {f(base - h)}Z", "-")
    if door:
        sh.rect_r(x + w * .4, base - h * .5, w * .2, h * .5, "w", 1)
    for i, wx in enumerate((x + w * .1,) if door else (x + w * .12, x + w * .58)):
        if i not in skip: sh.rect_r(wx, base - h * .78, w * .24, h * .3, light, 1)
    if door:
        sh.rect_r(x + w * .66, base - h * .78, w * .24, h * .3, light, 1)
    return top


# ---------------------------------------------------------------- figuren
def santa(sh, cx, top, s=1, hands=None, legs=None, draw_legs=True, mitten="g", suit="r"):
    """De Kerstman van voren. top = bovenkant van de muts. Geeft de y van het gezicht terug."""
    S = lambda v: v * s
    hy = top + S(30)
    hl, hr = hands or ((cx - S(34), hy + S(54)), (cx + S(34), hy + S(54)))
    fl, fr = legs or ((cx - S(12), hy + S(96)), (cx + S(12), hy + S(96)))
    if draw_legs:
        limb(sh, cx - S(11), hy + S(62), *fl, suit, S(14)); limb(sh, cx + S(11), hy + S(62), *fr, suit, S(14))
        for (x, y), d in ((fl, -1), (fr, 1)):
            sh.rect_r(x - S(8), y - S(8), S(16), S(9), "x", S(2))
            sh.ellipse_r(x + d * S(3), y + S(3), S(10), S(5), "x")
    limb(sh, cx - S(18), hy + S(24), *hl, suit, S(13)); limb(sh, cx + S(18), hy + S(24), *hr, suit, S(13))
    # jas met dikke buik
    sh.region(f"M{f(cx - S(18))} {f(hy + S(18))}Q{f(cx - S(38))} {f(hy + S(44))} {f(cx - S(30))} {f(hy + S(70))}H{f(cx + S(30))}"
              f"Q{f(cx + S(38))} {f(hy + S(44))} {f(cx + S(18))} {f(hy + S(18))}Z", suit)
    sh.rect_r(cx - S(31), hy + S(64), S(62), S(9), "-", S(4))
    sh.rect_r(cx - S(4), hy + S(22), S(8), S(43), "-", S(2))
    sh.rect_r(cx - S(31), hy + S(44), S(62), S(8), "x", S(1))
    sh.rect_r(cx - S(7), hy + S(42), S(14), S(12), "y", S(2))
    for x, y in (hl, hr):
        sh.circle_r(x, y, S(6.5), mitten)
    for (x, y) in (hl, hr):
        dx, dy = x - cx, y - hy - S(24)
        d = math.hypot(dx, dy) or 1
        sh.circle_r(x - dx / d * S(8), y - dy / d * S(8), S(7), "-")
    # hoofd, baard, muts
    sh.circle_r(cx, hy, S(14), "-")
    sh.region(f"M{f(cx - S(15))} {f(hy - S(1))}C{f(cx - S(22))} {f(hy + S(22))} {f(cx - S(10))} {f(hy + S(36))} {f(cx)} {f(hy + S(38))}"
              f"C{f(cx + S(10))} {f(hy + S(36))} {f(cx + S(22))} {f(hy + S(22))} {f(cx + S(15))} {f(hy - S(1))}"
              f"Q{f(cx + S(10))} {f(hy + S(12))} {f(cx)} {f(hy + S(12))}Q{f(cx - S(10))} {f(hy + S(12))} {f(cx - S(15))} {f(hy - S(1))}Z", "-")
    sh.region(f"M{f(cx)} {f(hy + S(7))}Q{f(cx - S(7))} {f(hy + S(4))} {f(cx - S(12))} {f(hy + S(9))}Q{f(cx - S(6))} {f(hy + S(13))} {f(cx)} {f(hy + S(10))}"
              f"Q{f(cx + S(6))} {f(hy + S(13))} {f(cx + S(12))} {f(hy + S(9))}Q{f(cx + S(7))} {f(hy + S(4))} {f(cx)} {f(hy + S(7))}Z", "-")
    sh.circle_r(cx, hy + S(4), S(3), "k")
    eye(sh, cx - S(5), hy - S(2), S(1.7)); eye(sh, cx + S(5), hy - S(2), S(1.7))
    if s >= .5:
        sh.line(f"M{f(cx - S(6))} {f(hy + S(20))}Q{f(cx - S(6))} {f(hy + S(28))} {f(cx - S(2))} {f(hy + S(32))}M{f(cx + S(6))} {f(hy + S(20))}Q{f(cx + S(6))} {f(hy + S(28))} {f(cx + S(2))} {f(hy + S(32))}", "l", "stroke-width:.9")
    sh.region(f"M{f(cx - S(15))} {f(hy - S(8))}C{f(cx - S(13))} {f(hy - S(32))} {f(cx + S(20))} {f(hy - S(36))} {f(cx + S(32))} {f(hy - S(8))}"
              f"L{f(cx + S(26))} {f(hy - S(6))}C{f(cx + S(19))} {f(hy - S(22))} {f(cx + S(12))} {f(hy - S(16))} {f(cx + S(15))} {f(hy - S(8))}Z", suit)
    sh.rect_r(cx - S(17), hy - S(13), S(34), S(8), "-", S(4))
    sh.circle_r(cx + S(31), hy - S(5), S(5), "-")
    return hy


def elf(sh, cx, top, s=1, suit="g", trouser="r", hat="r", hands=None, legs=None, style="short", hair="w", collar="y", draw_legs=True):
    """Elfje met puntmuts, puntoren en een kraagje met punten. Geeft de y van het gezicht terug."""
    S = lambda v: v * s
    hy = top + S(15)
    for d in (-1, 1):  # puntoren
        sh.region(f"M{f(cx + d * S(13))} {f(hy - S(3))}L{f(cx + d * S(24))} {f(hy - S(8))}L{f(cx + d * S(14))} {f(hy + S(6))}Z", "-")
    person(sh, cx, top, suit, trouser, hands=hands, hair=hair, style=style, legs=legs, cap=True, s=s, draw_legs=draw_legs, shoes="g" if trouser != "g" else "r")
    # kraag met punten
    pts_ = [(cx - S(15), hy + S(15))]
    for k in range(6):
        pts_ += [(cx - S(15) + S(5) * (k + .5), hy + S(24)), (cx - S(15) + S(5) * (k + 1), hy + S(15))]
    sh.poly_r(pts_, collar)
    # puntmuts naar links met belletje
    sh.region(f"M{f(cx - S(16))} {f(hy - S(4))}C{f(cx - S(14))} {f(hy - S(24))} {f(cx - S(10))} {f(hy - S(32))} {f(cx - S(28))} {f(hy - S(36))}"
              f"C{f(cx + S(4))} {f(hy - S(38))} {f(cx + S(14))} {f(hy - S(24))} {f(cx + S(16))} {f(hy - S(4))}Z", hat)
    sh.rect_r(cx - S(17), hy - S(9), S(34), S(7), collar, S(3))
    sh.circle_r(cx - S(29), hy - S(35), S(3.6), "y")
    return hy


def reindeer(sh, x, y, s=1, flip=False, body="w", antler="o", belly="-", scarf_code=None, harness=None):
    """Rendier van opzij, naar rechts kijkend (flip: naar links). (x, y) = midden onder de hoeven."""
    S = lambda v: v * s
    g = f' transform="translate({f(2 * x)} 0) scale(-1 1)"' if flip else ""
    sh.raw(f"<g{g}>")
    bx, by = x - S(6), y - S(40)
    sh.region(blob(bx - S(31), by - S(6), S(5), S(6), 7, .7), belly)  # staartje
    for lx, d in ((bx - S(22), -2), (bx - S(12), 2), (bx + S(14), -2), (bx + S(24), 2)):
        limb(sh, lx, by + S(4), lx + S(d), y - S(5), body, S(8.5))
        sh.rect_r(lx + S(d) - S(4.5), y - S(6), S(9), S(6), "x", S(1.5))
    sh.ellipse_r(bx, by, S(32), S(15), body)
    sh.region(f"M{f(bx - S(20))} {f(by + S(8))}Q{f(bx)} {f(by + S(18))} {f(bx + S(20))} {f(by + S(8))}Q{f(bx)} {f(by + S(12))} {f(bx - S(20))} {f(by + S(8))}Z", belly)
    # nek en hoofd
    sh.region(f"M{f(bx + S(16))} {f(by - S(10))}C{f(bx + S(22))} {f(by - S(24))} {f(bx + S(26))} {f(by - S(34))} {f(bx + S(30))} {f(by - S(40))}"
              f"L{f(bx + S(42))} {f(by - S(34))}C{f(bx + S(38))} {f(by - S(22))} {f(bx + S(34))} {f(by - S(8))} {f(bx + S(28))} {f(by + S(2))}Z", body)
    hx, hy = bx + S(38), by - S(38)
    # gewei achter het hoofd
    for ox, lean in ((-S(4), -1), (S(3), 1)):
        ax, ay = hx + ox, hy - S(8)
        limb(sh, ax, ay, ax + lean * S(6) - S(4), ay - S(22), antler, S(3.6))
        limb(sh, ax + lean * S(1) - S(1), ay - S(9), ax + lean * S(10) - S(4), ay - S(14), antler, S(3.2))
        limb(sh, ax + lean * S(4) - S(3), ay - S(17), ax - S(10) + lean * S(2), ay - S(24), antler, S(3))
    sh.region(f"M{f(hx - S(6))} {f(hy - S(4))}L{f(hx - S(16))} {f(hy - S(12))}L{f(hx - S(4))} {f(hy - S(10))}Z", body)  # oor
    sh.raw(f'<g transform="rotate(28 {f(hx)} {f(hy)})">')
    sh.rect_r(hx - S(9), hy - S(9), S(29), S(17), body, S(8.5))
    sh.raw("</g>")
    sh.circle_r(hx + S(13), hy + S(11), S(3.4), "x")  # bruine/zwarte neus, geen rode
    eye(sh, hx + S(2), hy - S(2), S(1.7))
    if scarf_code:
        sh.region(f"M{f(bx + S(17))} {f(by - S(14))}Q{f(bx + S(28))} {f(by - S(8))} {f(bx + S(38))} {f(by - S(20))}L{f(bx + S(40))} {f(by - S(13))}Q{f(bx + S(28))} {f(by)} {f(bx + S(15))} {f(by - S(7))}Z", scarf_code)
    if harness:
        sh.rect_r(bx - S(6), by - S(15), S(8), S(30), harness, S(2))
        sh.region(f"M{f(bx + S(17))} {f(by - S(14))}Q{f(bx + S(28))} {f(by - S(8))} {f(bx + S(38))} {f(by - S(20))}L{f(bx + S(39))} {f(by - S(15))}Q{f(bx + S(28))} {f(by - S(3))} {f(bx + S(16))} {f(by - S(9))}Z", harness)
        if s >= .5:
            for k in range(3): sh.circle_r(bx + S(22) + k * S(6), by - S(10) - k * S(3), S(1.8), "y")
    sh.raw("</g>")


def sleigh(sh, x, y, s=1, code="r", trim="y"):
    """Arreslee naar rechts. (x, y) = midden van de glijders op de grond."""
    S = lambda v: v * s
    sh.line(f"M{f(x - S(46))} {f(y)}H{f(x + S(38))}Q{f(x + S(54))} {f(y)} {f(x + S(54))} {f(y - S(10))}Q{f(x + S(54))} {f(y - S(16))} {f(x + S(47))} {f(y - S(15))}", "l", f"stroke-width:{f(max(1.6, S(3)))}")
    for dx in (-30, 0, 28):
        sh.seg(x + S(dx), y, x + S(dx), y - S(12), "l", f"stroke-width:{f(max(1.2, S(2.2)))}")
    sh.region(f"M{f(x - S(40))} {f(y - S(12))}L{f(x - S(44))} {f(y - S(44))}Q{f(x - S(46))} {f(y - S(54))} {f(x - S(36))} {f(y - S(52))}L{f(x - S(30))} {f(y - S(48))}"
              f"Q{f(x - S(26))} {f(y - S(32))} {f(x + S(8))} {f(y - S(32))}H{f(x + S(28))}Q{f(x + S(40))} {f(y - S(32))} {f(x + S(42))} {f(y - S(42))}"
              f"Q{f(x + S(52))} {f(y - S(46))} {f(x + S(50))} {f(y - S(30))}Q{f(x + S(48))} {f(y - S(12))} {f(x + S(30))} {f(y - S(12))}Z", code)
    sh.region(f"M{f(x - S(41))} {f(y - S(20))}H{f(x + S(46))}Q{f(x + S(42))} {f(y - S(12))} {f(x + S(30))} {f(y - S(12))}H{f(x - S(40))}Z", trim)
    if s >= .5:
        for k in range(4): sh.circle_r(x - S(30) + k * S(20), y - S(26), S(2.6), trim)


def snowman(sh, cx, base, s=1, hat="x", scarf_code="r", nose="o", arms=True, buttons="x"):
    S = lambda v: v * s
    if arms:
        sh.line(f"M{f(cx - S(20))} {f(base - S(64))}L{f(cx - S(44))} {f(base - S(84))}M{f(cx - S(36))} {f(base - S(77))}L{f(cx - S(42))} {f(base - S(92))}"
                f"M{f(cx + S(20))} {f(base - S(64))}L{f(cx + S(44))} {f(base - S(80))}M{f(cx + S(37))} {f(base - S(75))}L{f(cx + S(48))} {f(base - S(72))}", "l", f"stroke-width:{f(max(1.6, S(2.6)))}")
    sh.circle_r(cx, base - S(30), S(32), "-")
    sh.circle_r(cx, base - S(76), S(23), "-")
    sh.circle_r(cx, base - S(112), S(17), "-")
    for k in range(3): sh.circle_r(cx, base - S(86) + k * S(11), S(3), buttons)
    eye(sh, cx - S(6), base - S(116), S(2.2)); eye(sh, cx + S(6), base - S(116), S(2.2))
    sh.region(f"M{f(cx)} {f(base - S(112))}L{f(cx + S(16))} {f(base - S(108))}L{f(cx)} {f(base - S(106))}Z", nose)
    for k in range(5): sh.dot(cx - S(8) + k * S(4), base - S(101) + abs(k - 2) * S(-1.2) + S(2), S(1.2))
    sh.rect_r(cx - S(18), base - S(98), S(36), S(8), scarf_code, S(4))
    sh.region(f"M{f(cx + S(6))} {f(base - S(92))}L{f(cx + S(4))} {f(base - S(70))}H{f(cx + S(13))}L{f(cx + S(14))} {f(base - S(92))}Z", scarf_code)
    sh.rect_r(cx - S(20), base - S(130), S(40), S(6), hat, S(2))
    sh.rect_r(cx - S(13), base - S(152), S(26), S(23), hat, S(2))
    sh.rect_r(cx - S(13), base - S(136), S(26), S(5), "r" if hat != "r" else "g")


def gingerbread(sh, cx, cy, s=1, code="w", buttons="rg"):
    S = lambda v: v * s
    for d in (-1, 1):
        limb(sh, cx + d * S(8), cy + S(16), cx + d * S(18), cy + S(44), code, S(16))
        limb(sh, cx + d * S(10), cy - S(2), cx + d * S(34), cy - S(10), code, S(14))
    sh.rect_r(cx - S(17), cy - S(10), S(34), S(36), code, S(10))
    sh.circle_r(cx, cy - S(24), S(17), code)
    eye(sh, cx - S(6), cy - S(27), S(2.4)); eye(sh, cx + S(6), cy - S(27), S(2.4))
    sh.line(f"M{f(cx - S(7))} {f(cy - S(19))}Q{f(cx)} {f(cy - S(13))} {f(cx + S(7))} {f(cy - S(19))}", "l", f"stroke-width:{f(max(1.2, S(1.8)))}")
    for k in range(3): sh.circle_r(cx, cy - S(2) + k * S(10), S(3.6), buttons[k % len(buttons)])
    zig = lambda x0, y0, x1, y1: sh.line(f"M{f(x0)} {f(y0)}" + "".join(f"L{f(x0 + (x1 - x0) * k / 6)} {f(y0 + (y1 - y0) * k / 6 + (S(2.4) if k % 2 else 0))}" for k in range(1, 7)), "l", "stroke-width:1")
    for d in (-1, 1):
        zig(cx + d * S(26), cy - S(16), cx + d * S(30), cy - S(4))
        zig(cx + d * S(12), cy + S(38), cx + d * S(24), cy + S(36))


def bauble(sh, cx, cy, r, code, cap="z", bands=None):
    sh.circle_r(cx, cy, r, code)
    if bands:
        for (dy, h, c) in bands:
            yy = cy + dy * r
            hw = math.sqrt(max(0, r * r - yy * yy + 2 * yy * cy - cy * cy)) if False else math.sqrt(max(0, r * r - (dy * r) ** 2))
            hw2 = math.sqrt(max(0, r * r - (dy * r + h) ** 2))
            sh.region(f"M{f(cx - hw)} {f(yy)}Q{f(cx)} {f(yy + r * .12)} {f(cx + hw)} {f(yy)}L{f(cx + hw2)} {f(yy + h)}Q{f(cx)} {f(yy + h + r * .12)} {f(cx - hw2)} {f(yy + h)}Z", c)
    sh.rect_r(cx - r * .22, cy - r - r * .2, r * .44, r * .26, cap, 1)
    sh.line(f"M{f(cx - r * .08)} {f(cy - r - r * .2)}A{f(r * .1)} {f(r * .12)} 0 1 1 {f(cx + r * .08)} {f(cy - r - r * .2)}", "l", "stroke-width:1.2")


# ================================================================ 2-4 jaar
def kerstbal(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    sh.line("M100 0V34", "l", "stroke-width:1.4")
    bauble(sh, 100, 104, 62, "r", "z", bands=((-.42, 16, "y"), (.18, 18, "g")))
    for x, y in ((74, 84), (100, 80), (126, 84)): sh.region(star_path(x, y, 7, 3), "y")
    for x, y in ((80, 140), (120, 140)): sh.region(heart_path(x, y, 8), "-")
    for x, y in ((24, 40), (178, 36), (22, 168), (180, 170)): sparkle(sh, x, y, 9, "y")
    flakes(sh, ((30, 104), (172, 104), (60, 186), (140, 188)), 5)


def vrolijke_sneeuwpop(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    snow_ground(sh, 172)
    snowman(sh, 100, 186, 1.0, hat="x", scarf_code="r", nose="o")
    pine(sh, 26, 176, 70, "g", snow=True)
    pine(sh, 176, 176, 56, "g", snow=True)
    for x, y in ((40, 24), (160, 22), (186, 80), (14, 92), (64, 70), (136, 64)): snowflake(sh, x, y, 5, 1.2)


def rendier_met_sjaal(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    snow_ground(sh, 176, "b", 6)
    reindeer(sh, 96, 184, 1.45, body="w", antler="o", scarf_code="r")
    sh.region(star_path(30, 34, 12, 5), "y")
    for x, y in ((170, 30), (186, 70), (20, 90)): snowflake(sh, x, y, 5, 1.2)
    present(sh, 160, 160, 24, 18, "g", "y")


def peperkoekmannetje(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    sh.ellipse_r(100, 176, 86, 18, "b"); sh.ellipse_r(100, 174, 72, 12, "-")
    gingerbread(sh, 100, 96, 1.6, "w", "rgy")
    candy_cane(sh, 22, 168, 80, 1.1, "r")
    holly(sh, 170, 40, 1.4)
    for x, y in ((30, 30), (176, 104), (24, 110)): sparkle(sh, x, y, 8, "y")


def kerstklokken(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    for cx, rot, code in ((74, -16, "y"), (126, 16, "y")):
        sh.raw(f'<g transform="rotate({rot} {cx} 60)">')
        sh.region(f"M{cx - 34} 140Q{cx - 30} 128 {cx - 26} 110Q{cx - 24} 66 {cx} 64Q{cx + 24} 66 {cx + 26} 110Q{cx + 30} 128 {cx + 34} 140Q{cx} 148 {cx - 34} 140Z", code)
        sh.rect_r(cx - 36, 136, 72, 10, "o", 5)
        sh.circle_r(cx, 152, 8, "z")
        sh.raw("</g>")
    bow(sh, 100, 56, 1.8, "r")
    holly(sh, 100, 40, 1.2)
    for x, y in ((24, 30), (176, 30), (20, 180), (180, 180)): sparkle(sh, x, y, 9, "y")


def kerstcadeautjes(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    sh.rect_r(0, 170, 200, 30, "w")
    sh.line("M0 180H200M0 190H200", "l", "stroke-width:.8")
    present(sh, 20, 104, 56, 66, "r", "y")
    present(sh, 120, 120, 62, 50, "n", "r")
    present(sh, 82, 140, 40, 30, "g", "y")
    # ronde doos
    sh.rect_r(72, 64, 52, 42, "m", 2); sh.ellipse_r(98, 64, 28, 8, "m"); sh.ellipse_r(98, 106, 26, 6, "m")
    bow(sh, 98, 58, 1.4, "y")
    for x, y in ((150, 40), (40, 40), (182, 96)): sh.region(star_path(x, y, 9, 4), "y")
    for x, y in ((140, 140), (160, 156)): sh.circle_r(x, y, 4, "y")


# ================================================================ 4-6 jaar
def kerstman_zwaait(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    snow_ground(sh, 168)
    pine(sh, 22, 168, 76, "g", snow=True)
    xmas_tree(sh, 170, 178, 92)
    # zak achter de Kerstman
    sh.region("M40 176Q22 150 34 122Q46 100 64 118Q74 140 66 176Z", "w")
    sh.line("M44 110Q54 104 62 112", "l", "stroke-width:1.4")
    santa(sh, 100, 44, 1.0, hands=((60, 116), (138, 54)))
    present(sh, 132, 164, 20, 16, "m", "y")
    for x, y in ((30, 20), (80, 12), (150, 14), (190, 40)): snowflake(sh, x, y, 4.5, 1.1)


def slee_vol_cadeautjes(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region(moon_path(30, 30, 14), "y")
    for x, y in ((80, 18), (120, 34), (176, 20), (150, 60), (60, 50)): sh.region(star_path(x, y, 5, 2.2), "y")
    sh.region("M0 200V150Q60 120 120 140T200 130V200Z", "-")
    pine(sh, 170, 136, 54, "g", snow=True); pine(sh, 22, 160, 44, "g", snow=True)
    present(sh, 66, 118, 26, 22, "g", "r"); present(sh, 94, 110, 22, 30, "y", "r"); present(sh, 118, 122, 24, 18, "m", "y")
    sleigh(sh, 96, 172, 1.0, "r", "y")


def elfje_pakt_in(sh):
    sh.rect_r(0, 0, 200, 150, "k")
    for x in range(14, 200, 36):
        for y in range(16, 140, 36): sh.region(star_path(x + (18 if (y // 36) % 2 else 0), y, 5, 2.2), "-")
    sh.rect_r(0, 150, 200, 50, "w"); sh.line("M0 166H200M0 182H200", "l", "stroke-width:.8")
    # tafel
    sh.rect_r(96, 120, 100, 10, "o", 2)
    sh.rect_r(104, 130, 8, 50, "o"); sh.rect_r(180, 130, 8, 50, "o")
    present(sh, 128, 92, 40, 28, "n", "y")
    # rol papier en schaar
    sh.rect_r(170, 104, 24, 16, "r", 6); sh.circle_r(188, 112, 5, "-")
    elf(sh, 64, 64, 1.0, suit="g", trouser="r", hat="r", hands=((100, 108), (118, 98)), style="braids", hair="w", collar="y")
    present(sh, 22, 160, 30, 22, "t", "r")


def kerstkrans_met_kaarsen(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    # raam met nacht
    sh.rect_r(40, 10, 120, 70, "n", 2); sh.seg(100, 10, 100, 80, "l", "stroke-width:2"); sh.seg(40, 45, 160, 45, "l", "stroke-width:2")
    sh.region(moon_path(64, 28, 10), "y")
    for x, y in ((128, 24), (146, 60), (80, 64)): sh.region(star_path(x, y, 4, 1.8), "y")
    sh.rect_r(0, 130, 200, 70, "w"); sh.line("M0 130H200", "l", "stroke-width:1.2")
    # krans van bovenaf (ovaal) met blaadjes
    sh.ellipse_r(100, 148, 78, 30, "g"); sh.ellipse_r(100, 148, 46, 14, "-")
    for k in range(14):
        a = 2 * math.pi * k / 14
        x, y = 100 + 62 * math.cos(a), 148 + 22 * math.sin(a)
        sh.circle_r(x, y, 4, "r" if k % 2 else "y")
    for x, c, h in ((48, "p", 40), (80, "p", 48), (120, "k", 44), (152, "p", 36)):
        candle(sh, x, 150 - (8 if x in (80, 120) else 0), h, 12, c)
    for x in (30, 170): holly(sh, x, 180, 1.3)


def peperkoekhuisje(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    snow_ground(sh, 170)
    # huisje
    sh.rect_r(44, 96, 112, 76, "w")
    sh.poly_r([(30, 100), (100, 34), (170, 100)], "w")
    sh.region("M30 100L100 34L170 100Q156 108 146 96Q134 110 122 96Q110 110 100 96Q88 110 76 96Q64 110 52 96Q42 108 30 100Z", "-")
    for k, (x, y) in enumerate(((70, 72), (100, 60), (130, 72), (86, 84), (116, 84))): sh.circle_r(x, y, 4.5, "rgymt"[k])
    sh.rect_r(86, 126, 28, 46, "r", 14); sh.circle_r(108, 150, 2.4, "y")
    for x in (54, 124):
        sh.rect_r(x, 112, 22, 22, "y", 2); sh.seg(x + 11, 112, x + 11, 134, "l", "stroke-width:1.4"); sh.seg(x, 123, x + 22, 123, "l", "stroke-width:1.4")
    for k in range(6): sh.circle_r(52 + k * 19.5, 100, 4, "m" if k % 2 else "g")
    candy_cane(sh, 30, 176, 54, .9, "r"); candy_cane(sh, 158, 176, 54, .9, "r")
    gingerbread(sh, 180, 150, .45, "w")
    for x, y in ((24, 24), (176, 24), (100, 14)): snowflake(sh, x, y, 5, 1.2)


def kerstliedjes_zingen(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    for x, y in ((20, 20), (70, 14), (130, 22), (184, 14), (160, 50)): snowflake(sh, x, y, 4, 1.1)
    snow_ground(sh, 172)
    # lantaarnpaal
    sh.rect_r(20, 56, 5, 116, "z"); sh.poly_r([(10, 52), (22, 40), (34, 52)], "z"); sh.rect_r(12, 52, 20, 16, "y", 2)
    kids = ((58, "r", "g", "curly", "x", "y"), (104, "t", "n", "long", "w", "r"), (150, "o", "p", "short", "y", "g"))
    for x, shirt, hat, st, hair, sc in kids:
        s = .88; top = 192 - 101 * s
        hy = person(sh, x, top, shirt, "n", hands=((x - 11, top + 56), (x + 11, top + 56)), style=st, hair=hair, s=s, cap=True, face=False)
        beanie(sh, x, hy, hat, "-", s); scarf(sh, x, hy, sc, s)
        eye(sh, x - 5 * s, hy + 3 * s, 1.6 * s); eye(sh, x + 5 * s, hy + 3 * s, 1.6 * s)
        sh.ellipse_r(x, hy + 9 * s, 3 * s, 3.4 * s, "-")
        sh.rect_r(x - 14, top + 46, 28, 18, "-", 1); sh.seg(x, top + 46, x, top + 64, "l", "stroke-width:1")
    for x, y in ((40, 90), (186, 96), (180, 130)):
        sh.line(f"M{x} {y}V{y - 12}L{x + 7} {y - 14}V{y - 3}", "l", "stroke-width:1.4"); sh.ellipse_r(x - 2, y, 3, 2.2, "y"); sh.ellipse_r(x + 5, y - 2, 3, 2.2, "y")


def schaatsen_op_het_ijs(sh):
    sh.rect_r(0, 0, 200, 110, "b")
    for x, h in ((20, 60), (50, 76), (160, 70), (186, 54)): pine(sh, x, 104, h, "g", snow=True)
    sh.region("M0 110Q100 96 200 110V200H0Z", "t")
    sh.line("M20 150Q60 140 100 152T180 146M30 176Q80 168 140 180", "l", "stroke-width:.8")
    def skater(x, top, shirt, pants, st, hair, hat, sc, hands, legs, s):
        hy = person(sh, x, top, shirt, pants, hands=hands, legs=legs, style=st, hair=hair, s=s, cap=True, face=False, shoes="w")
        beanie(sh, x, hy, hat, "-", s); scarf(sh, x, hy, sc, s); face(sh, x, hy, s)
        for fx, fy in legs: sh.seg(fx - 9 * s, fy + 8 * s, fx + 9 * s, fy + 8 * s, "l", "stroke-width:2")
    skater(70, 100, "r", "n", "braids", "x", "g", "y", ((42, 140), (98, 128)), ((60, 186), (84, 176)), .78)
    skater(140, 108, "y", "g", "short", "w", "r", "b", ((116, 124), (164, 150)), ((130, 186), (152, 184)), .7)
    for x, y in ((40, 30), (100, 20), (150, 34)): snowflake(sh, x, y, 4.5, 1.1)


PLATES = [
    ("kerstbal-met-sterren", "Kerstbal met sterren", "2-4", 1, kerstbal),
    ("vrolijke-sneeuwpop", "Vrolijke sneeuwpop", "2-4", 1, vrolijke_sneeuwpop),
    ("rendier-met-sjaal", "Rendier met een sjaal", "2-4", 1, rendier_met_sjaal),
    ("peperkoekmannetje", "Peperkoekmannetje", "2-4", 1, peperkoekmannetje),
    ("kerstklokken", "Kerstklokken met een strik", "2-4", 1, kerstklokken),
    ("kerstcadeautjes", "Cadeautjes voor kerst", "2-4", 1, kerstcadeautjes),
    ("kerstman-zwaait", "De Kerstman zwaait", "4-6", 2, kerstman_zwaait),
    ("slee-vol-cadeautjes", "Een slee vol cadeautjes", "4-6", 2, slee_vol_cadeautjes),
    ("elfje-pakt-cadeautjes-in", "Een elfje pakt cadeautjes in", "4-6", 2, elfje_pakt_in),
    ("kerstkrans-met-kaarsen", "Kerstkrans met kaarsen", "4-6", 2, kerstkrans_met_kaarsen),
    ("peperkoekhuisje", "Het peperkoekhuisje", "4-6", 2, peperkoekhuisje),
    ("kerstliedjes-zingen", "Kerstliedjes zingen", "4-6", 2, kerstliedjes_zingen),
    ("schaatsen-op-het-ijs", "Schaatsen op het ijs", "4-6", 2, schaatsen_op_het_ijs),
]


# ================================================================ 6-9 jaar
def kerstman_en_slee(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.circle_r(160, 40, 22, "y")
    for x, y in ((20, 20), (110, 40), (100, 14), (120, 60), (190, 92), (30, 80), (84, 84)): sh.region(star_path(x, y, 4.5, 2), "y")
    # daken van een dorp onderaan
    for x, w, h, wall in ((-6, 44, 26, "r"), (40, 36, 36, "o"), (78, 46, 22, "w"), (126, 38, 32, "g"), (166, 40, 24, "p")):
        house(sh, x, 204, w, h, wall, "w", snow=True, door=False)
    # leidsels
    sh.line("M96 96L122 90M110 96L160 80", "l", "stroke-width:1")
    reindeer(sh, 128, 114, .48, harness="r")
    reindeer(sh, 168, 100, .44, harness="r")
    santa(sh, 60, 34, .52, hands=((50, 84), (94, 92)), draw_legs=False)
    present(sh, 32, 64, 14, 12, "g", "y"); present(sh, 20, 74, 12, 10, "m", "y")
    sleigh(sh, 60, 122, .8, "r", "y")
    for x, y in ((14, 106), (110, 126), (130, 140)): snowflake(sh, x, y, 3, 1)


def toy_ball(sh, x, y, r):
    sh.circle_r(x, y, r, "r"); sh.region(f"M{f(x - r)} {f(y)}Q{f(x)} {f(y + r * .5)} {f(x + r)} {f(y)}Q{f(x)} {f(y - r * .1)} {f(x - r)} {f(y)}Z", "y")


def toy_car(sh, x, y, s=1, code="n"):
    S = lambda v: v * s
    sh.region(f"M{f(x - S(16))} {f(y - S(4))}V{f(y - S(10))}L{f(x - S(8))} {f(y - S(18))}H{f(x + S(6))}L{f(x + S(12))} {f(y - S(10))}H{f(x + S(16))}V{f(y - S(4))}Z", code)
    sh.rect_r(x - S(6), y - S(16), S(10), S(6), "b", S(1))
    for d in (-1, 1): sh.circle_r(x + d * S(9), y - S(3), S(4), "x")


def blocks(sh, x, y, s=1):
    S = lambda v: v * s
    sh.rect_r(x, y - S(14), S(14), S(14), "y", S(1)); sh.rect_r(x + S(14), y - S(14), S(14), S(14), "g", S(1)); sh.rect_r(x + S(7), y - S(28), S(14), S(14), "r", S(1))
    for bx, by in ((x + S(4), y - S(10)), (x + S(18), y - S(10)), (x + S(11), y - S(24))): sh.circle_r(bx + S(3), by + S(3), S(2), "-")


def elfenwerkplaats(sh):
    sh.rect_r(0, 0, 200, 160, "o")
    floor_y = 160
    sh.rect_r(0, floor_y, 200, 40, "w"); sh.line("M0 172H200M0 186H200", "l", "stroke-width:.7")
    # raam met sneeuw
    sh.rect_r(76, 12, 48, 40, "b", 2); sh.seg(100, 12, 100, 52, "l", "stroke-width:1.6"); sh.seg(76, 32, 124, 32, "l", "stroke-width:1.6")
    for x, y in ((86, 22), (112, 42), (90, 44), (116, 20)): snowflake(sh, x, y, 3, 1)
    # planken met speelgoed
    for y in (40, 78):
        sh.rect_r(4, y, 64, 5, "w"); sh.rect_r(136, y, 60, 5, "w")
    toy_ball(sh, 16, 31, 8); blocks(sh, 30, 40, .7); toy_car(sh, 160, 40, .9, "n")
    toy_car(sh, 24, 78, .9, "g"); sh.region(star_path(54, 66, 9, 4), "y")
    present(sh, 144, 62, 18, 16, "m", "y"); toy_ball(sh, 182, 70, 7)
    # werkbank
    sh.rect_r(70, 116, 80, 9, "w", 2); sh.rect_r(76, 125, 7, 36, "w"); sh.rect_r(138, 125, 7, 36, "w")
    toy_car(sh, 112, 116, 1.2, "r")
    # elfjes
    elf(sh, 46, 82, .74, suit="g", trouser="r", hat="r", hands=((70, 118), (82, 106)), style="braids", hair="x", collar="y")
    sh.rect_r(80, 92, 3, 16, "w"); sh.rect_r(76, 88, 11, 6, "z", 1)
    elf(sh, 170, 92, .7, suit="r", trouser="g", hat="g", hands=((150, 116), (186, 132)), style="pony", hair="w", collar="y")
    sh.rect_r(146, 108, 3, 10, "w"); sh.rect_r(145, 104, 5, 5, "b")
    blocks(sh, 10, 190, .8)
    present(sh, 104, 180, 22, 16, "t", "r")


def kerstdiner(sh):
    sh.rect_r(0, 0, 200, 168, "k")
    sh.rect_r(10, 10, 40, 44, "n", 2); sh.seg(30, 10, 30, 54, "l", "stroke-width:1.4"); sh.seg(10, 32, 50, 32, "l", "stroke-width:1.4")
    sh.region(moon_path(20, 20, 6), "y")
    floor_boards(sh, 168, "w", 2)
    # kerstboom naast de tafel, helemaal binnen het vel
    xmas_tree(sh, 171, 168, 66)
    # vier mensen achter de tafel
    people = ((26, "g", "bun", "z"), (54, "r", "short", "x"), (92, "y", "curly", "w"), (120, "t", "braids", "x"))
    s = .54
    for x, shirt, st, hair in people:
        top = 112 - 58 * s - 15 * s
        person(sh, x, top, shirt, "n", hands=((x - 12, 120), (x + 12, 120)), style=st, hair=hair, s=s, draw_legs=False)
    # tafel: kleed met zoom en twee poten
    sh.rect_r(16, 142, 8, 26, "w"); sh.rect_r(122, 142, 8, 26, "w")
    sh.rect_r(4, 118, 138, 22, "r")
    sh.rect_r(4, 140, 138, 4, "y")
    # schaal, kaarsen en borden
    sh.ellipse_r(73, 116, 20, 6, "z"); sh.region("M60 114Q62 98 73 96Q84 98 86 114Z", "w")
    sh.line("M65 105Q70 100 75 105M76 102Q80 98 83 103", "l", "stroke-width:1")
    candle(sh, 136, 118, 18, 6, "y")
    for x in (24, 56, 90, 124): sh.ellipse_r(x, 117, 8, 3, "-")


def kerststal(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region(star_path(100, 22, 14, 6, 8), "y")
    sh.line("M110 30L150 6M112 26L172 20", "l", "stroke-width:1")
    for x, y in ((24, 20), (56, 40), (170, 50), (186, 16), (36, 66)): sh.region(star_path(x, y, 3.5, 1.6), "y")
    sh.rect_r(0, 168, 200, 32, "w")
    # stal: palen en schuin dak
    sh.rect_r(22, 70, 8, 100, "w"); sh.rect_r(170, 70, 8, 100, "w")
    sh.region("M8 78L100 46L192 78L186 88L100 58L14 88Z", "w")
    sh.region("M30 86L100 62L170 86V168H30Z", "o")
    for x in range(44, 170, 18): sh.seg(x, 72 if x < 100 else 72, x, 168, "l", "stroke-width:.6")
    # os en ezel
    sh.ellipse_r(64, 112, 16, 12, "w"); sh.region("M48 104Q40 96 46 92Q52 98 54 104Z", "-"); sh.region("M80 104Q88 96 82 92Q76 98 74 104Z", "-")
    sh.ellipse_r(64, 122, 9, 6, "k"); eye(sh, 58, 110, 1.6); eye(sh, 70, 110, 1.6)
    sh.region("M128 100L124 82L132 98ZM140 100L146 82L144 100Z", "z")
    sh.ellipse_r(136, 112, 13, 12, "z"); sh.ellipse_r(136, 122, 8, 6, "-"); eye(sh, 131, 110, 1.6); eye(sh, 141, 110, 1.6)
    # kribbe met stro en het kindje
    sh.region("M70 150L80 132H120L130 150Z", "w")
    sh.region("M78 134Q100 120 122 134Z", "y")
    sh.ellipse_r(100, 128, 14, 6, "-"); sh.circle_r(90, 126, 5, "-")
    sh.line("M72 150L66 168M128 150L134 168", "l", "stroke-width:2")
    # Maria en Jozef
    s = .62
    person(sh, 46, 168 - 101 * s, "b", "b", hands=((60, 140), (58, 146)), style="long", hair="t", s=s, skirt="b")
    person(sh, 158, 168 - 101 * s - 4, "w", "w", hands=((176, 130), (140, 140)), style="short", hair="x", s=s, skirt="w")
    sh.rect_r(176, 96, 3, 72, "w")


def rendieren_in_het_bos(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.region(moon_path(30, 26, 12), "y")
    for x, y in ((70, 16), (120, 30), (176, 14)): snowflake(sh, x, y, 4, 1.1)
    for x, h in ((10, 90), (46, 70), (160, 96), (194, 74), (130, 60)): pine(sh, x, 140, h, "g", snow=True)
    snow_ground(sh, 136)
    reindeer(sh, 58, 184, .86, body="w", antler="o")
    reindeer(sh, 166, 176, .62, flip=True, body="w", antler="o")
    reindeer(sh, 116, 196, .4, body="o", antler="y")
    for x, y in ((24, 110), (186, 120), (92, 104)): snowflake(sh, x, y, 3.5, 1)


def bike(sh, x, y, s=1, code="r"):
    """Fiets naar rechts; (x, y) = midden tussen de wielen op de grond."""
    S = lambda v: v * s
    for d in (-1, 1):
        cx = x + d * S(30)
        sh.circle_r(cx, y - S(18), S(18), "x"); sh.circle_r(cx, y - S(18), S(14), "-")
        for k in range(4):
            a = math.radians(k * 45)
            sh.seg(cx - S(14) * math.cos(a), y - S(18) - S(14) * math.sin(a), cx + S(14) * math.cos(a), y - S(18) + S(14) * math.sin(a), "l", "stroke-width:.7")
    w = f"stroke-width:{f(max(1.6, S(3.2)))}"
    sh.line(f"M{f(x - S(30))} {f(y - S(18))}L{f(x - S(4))} {f(y - S(18))}L{f(x - S(14))} {f(y - S(44))}H{f(x + S(18))}L{f(x - S(4))} {f(y - S(18))}"
            f"M{f(x + S(30))} {f(y - S(18))}L{f(x + S(20))} {f(y - S(52))}H{f(x + S(28))}M{f(x - S(14))} {f(y - S(44))}L{f(x - S(16))} {f(y - S(50))}", "l", w)
    sh.rect_r(x - S(24), y - S(54), S(16), S(5), "x", S(2))
    sh.rect_r(x - S(56), y - S(38), S(26), S(4), code)


def kerstboom_op_de_fiets(sh):
    sh.rect_r(0, 0, 200, 200, "-")
    for x, w, h, wall in ((-4, 40, 60, "r"), (40, 36, 74, "w"), (80, 40, 56, "o"), (124, 34, 70, "z"), (162, 42, 60, "r")):
        house(sh, x, 122, w, h, wall, "z" if wall != "z" else "w", snow=True, door=x != 80, skip=(1,) if x == 80 else ())
    sh.rect_r(0, 122, 200, 78, "z"); sh.line("M0 140H200", "l", "stroke-width:.8;stroke-dasharray:6 6")
    snow_ground(sh, 184, "-", 4)
    bike(sh, 112, 184, 1.1, "r")
    # boom liggend achterop
    sh.rect_r(70, 128, 10, 6, "w")
    tip, base_x, cy = 6, 72, 122
    top_pts, bot_pts = [], []
    for k in range(6):
        x = base_x - k * (base_x - tip) / 6
        hw = 20 * (1 - k / 6)
        top_pts += [(x, cy - hw), (x - 6, cy - hw * .55)]
        bot_pts += [(x, cy + hw), (x - 6, cy + hw * .55)]
    sh.poly_r(top_pts + [(tip, cy)] + list(reversed(bot_pts)), "g")
    sh.line("M54 102L60 142M38 106L42 138", "l", "stroke-width:1.6")
    # fietser zit op het zadel
    s = .8
    hy = person(sh, 100, 120 - 54 * s - 15 * s, "n", "x", hands=((132, 124), (128, 126)), legs=((106, 162), (114, 168)), style="long", hair="w", s=s, cap=True, face=False)
    beanie(sh, 102, hy, "y", "-", s); scarf(sh, 102, hy, "r", s); face(sh, 102, hy, s)
    for x, y in ((20, 14), (60, 24), (140, 12), (184, 30)): snowflake(sh, x, y, 4, 1.1)


# ================================================================ 9+ jaar
def gable_house(sh, x, base, w, h, wall, kind="trap"):
    sh.rect_r(x, base - h, w, h, wall)
    top = base - h
    if kind == "trap":
        st = w / 6
        pts_ = [(x, top)]
        for k in range(3): pts_ += [(x + k * st, top - (k + 1) * 7), (x + (k + 1) * st, top - (k + 1) * 7)]
        for k in range(3): pts_ += [(x + w - (3 - k) * st, top - (3 - k) * 7), (x + w - (2 - k) * st, top - (3 - k) * 7)]
        pts_ += [(x + w, top)]
        sh.poly_r(pts_, wall)
    elif kind == "hals":
        sh.region(f"M{f(x)} {f(top)}Q{f(x + w * .2)} {f(top - 4)} {f(x + w * .25)} {f(top - 12)}V{f(top - 24)}H{f(x + w * .75)}V{f(top - 12)}Q{f(x + w * .8)} {f(top - 4)} {f(x + w)} {f(top)}Z", wall)
        sh.region(f"M{f(x + w * .3)} {f(top - 24)}Q{f(x + w / 2)} {f(top - 34)} {f(x + w * .7)} {f(top - 24)}Z", "-")
    else:
        sh.region(f"M{f(x)} {f(top)}C{f(x)} {f(top - 18)} {f(x + w * .3)} {f(top - 26)} {f(x + w / 2)} {f(top - 28)}C{f(x + w * .7)} {f(top - 26)} {f(x + w)} {f(top - 18)} {f(x + w)} {f(top)}Z", wall)
    for r in range(int((h - 16) / 18)):
        for k in range(2):
            sh.rect_r(x + w * (.18 + k * .42), top + 8 + r * 18, w * .22, 11, "y", 1)
    sh.rect_r(x + w * .4, base - 14, w * .2, 14, "w", 1)


def kerstdorp(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region(moon_path(176, 24, 12), "y")
    for x, y in ((20, 14), (50, 30), (90, 10), (130, 26), (150, 50), (196, 60), (12, 56)): sh.region(star_path(x, y, 3.5, 1.5), "y")
    # toren
    sh.rect_r(92, 40, 22, 76, "z"); sh.poly_r([(88, 42), (103, 6), (118, 42)], "w"); sh.circle_r(103, 58, 7, "-")
    sh.seg(103, 58, 103, 53, "l", "stroke-width:1"); sh.seg(103, 58, 107, 58, "l", "stroke-width:1")
    sh.rect_r(98, 80, 10, 14, "y", 4)
    for x, w, h, wall in ((-4, 34, 38, "r"), (28, 30, 48, "o"), (58, 32, 34, "w"), (118, 32, 42, "g"), (150, 30, 32, "r"), (178, 28, 44, "w")):
        house(sh, x, 116, w, h, wall, "x", snow=True, door=True)
    sh.region("M0 200V112Q60 104 120 116T200 112V200Z", "-")
    for x, h in ((16, 40), (180, 46), (140, 30)): pine(sh, x, 134, h, "g", snow=True)
    for x in (48, 118):
        sh.rect_r(x - 1.5, 112, 3, 34, "z"); sh.rect_r(x - 5, 106, 10, 8, "y", 2); sh.poly_r([(x - 6, 106), (x, 100), (x + 6, 106)], "z")
    # heuvel met sleetjes
    sh.region("M0 200V160Q60 140 120 170T200 176V200Z", "b")
    for x, y, c, hair, st in ((40, 132, "r", "x", "curly"), (96, 150, "y", "w", "long")):
        s = .38
        hy = person(sh, x, y, c, "n", hands=((x - 8, y + 26), (x + 8, y + 26)), style=st, hair=hair, s=s, cap=True, face=False, draw_legs=False)
        beanie(sh, x, hy, "g", "-", s); face(sh, x, hy, s)
        sh.rect_r(x - 16, y + 36, 32, 6, "w", 2); sh.line(f"M{x - 18} {y + 46}H{x + 14}Q{x + 20} {y + 46} {x + 20} {y + 40}", "l", "stroke-width:1.4")
    snowman(sh, 160, 196, .32)
    for x, y in ((70, 190), (130, 192)): snowflake(sh, x, y, 3.5, 1)


def elfenfabriek(sh):
    sh.rect_r(0, 0, 200, 200, "o")
    # lampen
    for x in (40, 160):
        sh.seg(x, 0, x, 14, "l", "stroke-width:1"); sh.region(f"M{x - 10} 22Q{x} 8 {x + 10} 22Z", "g"); sh.circle_r(x, 24, 3, "y")
    # machine met tandwielen
    sh.rect_r(10, 40, 50, 64, "z", 3)
    for gx, gy, r, c in ((26, 58, 10, "y"), (44, 74, 8, "r"), (26, 90, 7, "b")):
        sh.region("M" + " L".join(f"{f(gx + (r + (2.5 if k % 2 else 0)) * math.cos(math.pi * k / 8))} {f(gy + (r + (2.5 if k % 2 else 0)) * math.sin(math.pi * k / 8))}" for k in range(16)) + "Z", c)
        sh.circle_r(gx, gy, r * .35, "-")
    sh.rect_r(60, 60, 12, 30, "z")
    # lopende band
    sh.rect_r(60, 112, 136, 10, "x", 5)
    for x in range(68, 196, 16): sh.circle_r(x, 117, 3, "z")
    sh.rect_r(70, 122, 6, 40, "z"); sh.rect_r(180, 122, 6, 40, "z")
    for x, w, h, c, r in ((78, 20, 16, "r", "y"), (110, 16, 22, "g", "r"), (138, 22, 14, "m", "y"), (168, 16, 18, "t", "r")):
        present(sh, x, 112 - h, w, h, c, r)
    # plank met speelgoed
    sh.rect_r(110, 40, 86, 5, "w")
    toy_car(sh, 130, 40, .8, "n"); blocks(sh, 150, 40, .6); toy_ball(sh, 186, 32, 7)
    # ladder met elfje
    sh.line("M92 160L112 48M108 160L128 48", "l", "stroke-width:2")
    for k in range(7): sh.seg(94 + k * 2.8 + 0, 150 - k * 16, 110 + k * 2.8, 150 - k * 16, "l", "stroke-width:1.6")
    elf(sh, 118, 50, .46, suit="r", trouser="g", hat="g", hands=((112, 70), (134, 56)), style="short", hair="w", legs=((112, 100), (124, 96)))
    # elfjes op de vloer
    sh.rect_r(0, 162, 200, 38, "w"); sh.line("M0 176H200M0 190H200", "l", "stroke-width:.7")
    elf(sh, 34, 106, .56, suit="g", trouser="r", hat="r", hands=((16, 140), (54, 124)), style="braids", hair="x")
    sh.rect_r(52, 112, 3, 16, "w"); sh.rect_r(48, 108, 11, 6, "z", 1)
    elf(sh, 150, 124, .4, suit="b", trouser="y", hat="p", hands=((138, 150), (162, 150)), style="short", hair="w")
    present(sh, 140, 146, 20, 14, "y", "r")
    blocks(sh, 176, 194, .7)


def schaatsen_op_de_gracht(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    for x, w, h, wall, kind in ((-2, 30, 70, "r", "trap"), (28, 26, 80, "w", "hals"), (54, 30, 64, "z", "klok"), (84, 28, 76, "o", "trap"),
                                (112, 30, 68, "r", "klok"), (142, 26, 82, "w", "hals"), (168, 34, 72, "g", "trap")):
        gable_house(sh, x, 104, w, h, wall, kind)
    sh.rect_r(0, 104, 200, 8, "z")
    # brug
    sh.region("M0 120H200V132H150Q100 104 50 132H0Z", "w")
    for x in range(10, 200, 20): sh.rect_r(x, 112, 4, 8, "w")
    sh.rect_r(0, 110, 200, 3, "w")
    # bevroren gracht
    sh.region("M0 132H50Q100 104 150 132H200V200H0Z", "t")
    sh.line("M20 160Q60 150 100 162T180 156M40 186Q90 176 150 190", "l", "stroke-width:.7")
    skaters = ((40, 128, "r", "n", "long", "w", "g", "y", .44), (96, 136, "y", "g", "short", "x", "r", "b", .4), (150, 132, "p", "n", "braids", "x", "y", "r", .42), (120, 158, "g", "w", "curly", "w", "b", "r", .32))
    for x, top, shirt, pants, st, hair, hat, sc, s in skaters:
        legs = ((x - 6, top + 101 * s), (x + 14, top + 96 * s))
        hy = person(sh, x, top, shirt, pants, hands=((x - 24 * s * 2, top + 40 * s), (x + 22 * s * 2, top + 50 * s)), legs=legs, style=st, hair=hair, s=s, cap=True, face=False, shoes="w")
        beanie(sh, x, hy, hat, "-", s); scarf(sh, x, hy, sc, s); face(sh, x, hy, s)
        for fx, fy in legs: sh.seg(fx - 8 * s, fy + 8 * s, fx + 8 * s, fy + 8 * s, "l", "stroke-width:1.4")
    # koek-en-zopie
    sh.rect_r(174, 166, 24, 20, "r", 1); sh.region("M170 166L186 152L202 166Z", "y"); sh.rect_r(177, 176, 18, 4, "w")
    for x, y in ((20, 20), (70, 12), (120, 22), (180, 10)): snowflake(sh, x, y, 3.5, 1)


PLATES += [
    ("kerstman-en-de-slee", "De Kerstman en zijn slee", "6-9", 3, kerstman_en_slee),
    ("elfenwerkplaats", "De werkplaats van de elfjes", "6-9", 2, elfenwerkplaats),
    ("kerstdiner-met-de-familie", "Kerstdiner met de familie", "6-9", 2, kerstdiner),
    ("kerststal", "De kerststal", "6-9", 2, kerststal),
    ("rendieren-in-het-bos", "Rendieren in het besneeuwde bos", "6-9", 2, rendieren_in_het_bos),
    ("kerstboom-op-de-fiets", "De kerstboom op de fiets", "6-9", 2, kerstboom_op_de_fiets),
    ("kerstdorp-in-de-sneeuw", "Een kerstdorp in de sneeuw", "9+", 3, kerstdorp),
    ("de-elfenfabriek", "De elfenfabriek", "9+", 3, elfenfabriek),
    ("schaatsen-op-de-gracht", "Schaatsen op de gracht", "9+", 3, schaatsen_op_de_gracht),
]

if __name__ == "__main__":
    for slug, name, age, diff, draw in PLATES:
        if ONLY and slug not in ONLY: continue
        kp(slug, name, "feest", age, diff, draw, "kerst")
