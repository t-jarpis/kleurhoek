import math, random, itertools
from lib_gen import *
from shapes import heart_path

def refl(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay; t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    fx, fy = ax + t * dx, ay + t * dy
    return (2 * fx - px, 2 * fy - py)
def P(points): return "M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in points) + "Z"

# ---------- happertje ----------
def happertje():
    sh = Sheet()
    title(sh, "Happertje", 16)
    sh.text(100, 27, "Kleur de hoeken, knip het vierkant uit en vouw je eigen happertje.", 6)
    L, T, S = 10, 40, 180; cx, cy = L + S / 2, T + S / 2
    Mt, Mr, Mb, Ml = (cx, T), (L + S, cy), (cx, T + S), (L, cy)
    q = S / 4
    i_tl, i_tr, i_br, i_bl = (cx - q, cy - q), (cx + q, cy - q), (cx + q, cy + q), (cx - q, cy + q)
    cols = [("rood", "r", (L, T), Mt, Ml), ("blauw", "b", (L + S, T), Mt, Mr), ("groen", "g", (L + S, T + S), Mr, Mb), ("geel", "y", (L, T + S), Ml, Mb)]
    for word, code, c, m1, m2 in cols:
        sh.poly_r([c, m1, m2], code)
        # woorden op de stukjes die na het vouwen aan de buitenkant komen
        g = ((c[0] + m1[0] + m2[0]) / 3, (c[1] + m1[1] + m2[1]) / 3)
        for m in (m1, m2):
            sh.text(m[0] * .6 + g[0] * .4, m[1] * .6 + g[1] * .4 + 2, word, 5.5)
    O = (cx, cy)
    ring = [(Mt, i_tl, (cx, cy - q)), (Mt, i_tr, (cx, cy - q)), (Mr, i_tr, (cx + q, cy)), (Mr, i_br, (cx + q, cy)),
            (Mb, i_br, (cx, cy + q)), (Mb, i_bl, (cx, cy + q)), (Ml, i_bl, (cx - q, cy)), (Ml, i_tl, (cx - q, cy))]
    rot = [180, 180, 270, 270, 0, 0, 90, 90]
    for k, tri in enumerate(ring):
        sh.poly_r(list(tri), "-")
        gx = sum(p[0] for p in tri) / 3; gy = sum(p[1] for p in tri) / 3
        sh.text(gx, gy + 3.5, str(k + 1), 10, rotate=rot[k])
    fortunes = [("Doe tien", "sprongen"), ("Zing een", "liedje"), ("Geef een", "high five"), ("Vertel een", "grapje"),
                ("Doe een", "dansje"), ("Je krijgt", "een knuffel"), ("Tel tot", "twintig"), ("Trek een", "gekke snoet")]
    inner = [(O, i_tl, (cx, cy - q)), (O, i_tr, (cx, cy - q)), (O, i_tr, (cx + q, cy)), (O, i_br, (cx + q, cy)),
             (O, i_br, (cx, cy + q)), (O, i_bl, (cx, cy + q)), (O, i_bl, (cx - q, cy)), (O, i_tl, (cx - q, cy))]
    for k, tri in enumerate(inner):
        sh.poly_r(list(tri), "-")
        gx = sum(p[0] for p in tri) / 3; gy = sum(p[1] for p in tri) / 3
        a, b = fortunes[k]
        sh.raw(f'<g transform="rotate({rot[k]} {f(gx)} {f(gy)})">'); sh.text(gx, gy - 1, a, 4.6); sh.text(gx, gy + 5, b, 4.6); sh.raw('</g>')
    for a, b in [((L, T), (L + S, T + S)), ((L + S, T), (L, T + S)), (Mt, Mb), (Ml, Mr)]: sh.seg(*a, *b, "fold")
    sh.line(P([Mt, Mr, Mb, Ml]), "fold"); sh.line(P([i_tl, i_tr, i_br, i_bl]), "fold")
    sh.rect_line(L, T, S, S, "cut")
    sh.legend(["cut", "fold"], 274)
    write(OUT, "happertje", sh, {"category": "vormen", "age": "6-9", "kind": "vouwblad", "difficulty": 2, "minutes": 20,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR],
        "i18n": {"nl": {"name": "Happertje vouwen", "steps": [
            "Kleur de vier hoeken in de kleur die erop staat en knip het vierkant uit.",
            "Vouw alle stippellijnen één keer heen en terug, dan gaat het vouwen straks makkelijker.",
            "Leg het vel met de tekening naar beneden en vouw de vier hoeken naar het midden.",
            "Draai het om en vouw weer de vier hoeken naar het midden. Nu zie je de cijfers.",
            "Vouw het dubbel, steek je duimen en wijsvingers onder de gekleurde vakjes en duw de punten naar het midden.",
            "Laat iemand een kleur kiezen en spel die: bij elke letter open en dicht. Dan een cijfer tellen, nog een cijfer kiezen en het flapje optillen. Doe wat er staat!"]}}})
happertje()

# ---------- origami met stappen ----------
def origami(slug, name, steps, texts, cat, age, diff, paper_code):
    sh = Sheet()
    title(sh, cap(name.split(": ", 1)[-1]), 16)
    sh.text(100, 27, "Knip het vierkant uit, kleur het en vouw het stap voor stap.", 6)
    sh.rect_r(52, 34, 96, 96, paper_code)
    sh.rect_line(52, 34, 96, 96, "cut")
    sh.text(100, 86, "jouw vouwpapier", 6, cls="tip")
    for i, draw in enumerate(steps):
        col, row = i % 3, i // 3
        bx, by = 13 + col * 60, 140 + row * 66
        sh.rect_line(bx, by, 58, 60, "l", 3, "stroke-width:.6")
        sh.text(bx + 5, by + 8, str(i + 1), 7, "start")
        sh.raw(f'<g transform="translate({bx + 4} {by + 6}) scale(.5)">'); draw(sh); sh.raw('</g>')
    sh.legend(["cut", "fold"], 276)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "vouwblad", "difficulty": diff, "minutes": 15,
        "materials": [SCHAAR, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Liever gekleurd vouwpapier? Elk vierkant velletje werkt ook.", "steps": texts}}})
def arrow(sh, x1, y1, x2, y2, bend=-12):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2; dx, dy = x2 - x1, y2 - y1; n = math.hypot(dx, dy)
    qx, qy = mx - dy / n * bend, my + dx / n * bend
    sh.line(f"M{f(x1)} {f(y1)}Q{f(qx)} {f(qy)} {f(x2)} {f(y2)}", "l", "stroke-width:1.4")
    ang = math.atan2(y2 - qy, x2 - qx)
    a1 = (x2 - 6 * math.cos(ang - .5), y2 - 6 * math.sin(ang - .5)); a2 = (x2 - 6 * math.cos(ang + .5), y2 - 6 * math.sin(ang + .5))
    sh.line(f"M{f(a1[0])} {f(a1[1])}L{f(x2)} {f(y2)}L{f(a2[0])} {f(a2[1])}", "l", "stroke-width:1.4")
def shape(sh, ptsl, fill=True):
    sh.line(P(ptsl), "l", "stroke-width:1.6")

# hond: vierkant als ruit -> driehoek -> oren omlaag -> kin omhoog -> gezicht
A, B, C = (8, 30), (92, 30), (50, 72)
PL, QL = (30, 30), (8 + 42 * .45, 30 + 42 * .45)
PR, QR = (70, 30), (92 - 42 * .45, 30 + 42 * .45)
AL, BR = refl(A, PL, QL), refl(B, PR, QR)
chin_y = 62; Cc = (50, 2 * chin_y - 72)
def d1(sh): shape(sh, [(50, 4), (96, 50), (50, 96), (4, 50)]); sh.seg(4, 50, 96, 50, "fold"); arrow(sh, 50, 12, 50, 86, 16)
def d2(sh): shape(sh, [A, B, C]); sh.seg(*PL, *QL, "fold"); sh.seg(*PR, *QR, "fold"); arrow(sh, 12, 34, AL[0], AL[1], 10); arrow(sh, 88, 34, BR[0], BR[1], -10)
def body(sh):
    shape(sh, [PL, PR, QR, C, QL]); shape(sh, [PL, AL, QL]); shape(sh, [PR, BR, QR])
def d3(sh): body(sh); sh.seg(QL[0] + 6, chin_y, QR[0] - 6, chin_y, "fold"); arrow(sh, 50, 70, 50, 54, -10)
def face(sh):
    xl = 50 - (72 - chin_y) * 42 / 42; xr = 50 + (72 - chin_y)
    shape(sh, [PL, PR, QR, (xr, chin_y), (xl, chin_y), QL]); shape(sh, [PL, AL, QL]); shape(sh, [PR, BR, QR])
    shape(sh, [(xl, chin_y), (xr, chin_y), Cc])
def d4(sh): face(sh); sh.raw('<path class="l" d="M44 62L50 66L56 62" style="stroke-width:1"/>') if False else None
def d5(sh):
    face(sh); sh.dot(40, 42, 2.6); sh.dot(60, 42, 2.6); sh.ellipse_r(50, 54, 4.5, 3.4, "k")
origami("origami-hondje", "Origami: hondenkopje", [d1, d2, d3, d5], [
    "Knip het vierkant uit. Kleur het eerst als je wilt: de kleur komt aan de buitenkant.",
    "Leg het vierkant als een ruit voor je en vouw de bovenste punt naar de onderste punt. Je hebt nu een driehoek met de punt naar beneden.",
    "Vouw de linker- en rechterpunt schuin naar beneden: dat zijn de flaporen.",
    "Vouw het puntje onderaan een klein stukje omhoog: de snuit.",
    "Draai hem om als dat mooier is en teken ogen en een neus. Klaar is je hondje!"], "dieren", "4-6", 1, "o")

# bekertje: driehoek punt omhoog, linkerhoek naar rechterkant, rechterhoek naar linkerkant, flappen omlaag
A2, B2, C2 = (10, 80), (90, 80), (50, 40)
def solve_cup():
    best = None
    for k in range(1, 400):
        t = k / 400
        D = (B2[0] + (C2[0] - B2[0]) * t, B2[1] + (C2[1] - B2[1]) * t)
        mid = ((A2[0] + D[0]) / 2, (A2[1] + D[1]) / 2); dx, dy = D[0] - A2[0], D[1] - A2[1]
        # vouwlijn = middelloodlijn; snijpunt met AC
        dirx, diry = -dy, dx
        # AC: A2 + s*(C2-A2)
        ux, uy = C2[0] - A2[0], C2[1] - A2[1]
        det = dirx * uy - diry * ux
        if abs(det) < 1e-9: continue
        s = ((A2[0] - mid[0]) * diry - (A2[1] - mid[1]) * dirx) / -det if False else None
        # los mid + r*dir = A2 + s*u op
        r_, s_ = None, None
        a11, a12, a21, a22 = dirx, -ux, diry, -uy; b1, b2 = A2[0] - mid[0], A2[1] - mid[1]
        dd = a11 * a22 - a12 * a21; r_ = (b1 * a22 - a12 * b2) / dd; s_ = (a11 * b2 - b1 * a21) / dd
        E = (A2[0] + s_ * ux, A2[1] + s_ * uy)
        err = abs(E[1] - D[1])
        if 0 < s_ < 1 and (best is None or err < best[0]): best = (err, D, E, mid, (dirx, diry))
    return best
_, D2, E2, M2, dir2 = solve_cup()
# vouwlijn E2 -> F2 op de basis
s_f = (A2[1] - E2[1]) / dir2[1]; F2 = (E2[0] + s_f * dir2[0], A2[1])
D2r, E2r, F2r = (200 - D2[0] - 100, D2[1]), (200 - E2[0] - 100, E2[1]), (200 - F2[0] - 100, F2[1])
def c1(sh): shape(sh, [(50, 4), (96, 50), (50, 96), (4, 50)]); sh.seg(4, 50, 96, 50, "fold"); arrow(sh, 50, 86, 50, 12, -16)
def c2(sh): shape(sh, [A2, B2, C2]); sh.seg(*E2, *F2, "fold"); arrow(sh, 14, 76, D2[0], D2[1], 14)
def c3(sh):
    shape(sh, [F2, B2, C2, E2]); shape(sh, [E2, F2, D2]); sh.seg(*E2r, *F2r, "fold"); arrow(sh, 86, 76, D2r[0], D2r[1], -14)
def c4(sh):
    top = E2[1]
    shape(sh, [F2, F2r, E2r, E2]); shape(sh, [E2, F2, D2]); shape(sh, [E2r, F2r, D2r]); shape(sh, [E2, E2r, C2])
    sh.seg(E2[0], top, E2r[0], top, "fold"); arrow(sh, 50, 46, 50, 66, 10)
def c5(sh):
    top = E2[1]
    shape(sh, [F2, F2r, E2r, E2]); shape(sh, [E2, F2, D2]); shape(sh, [E2r, F2r, D2r]); shape(sh, [E2, E2r, (50, 2 * top - C2[1])])
origami("origami-bekertje", "Origami: bekertje", [c1, c2, c3, c4, c5], [
    "Knip het vierkant uit en kleur het als je wilt.",
    "Leg het als een ruit en vouw de onderste punt naar de bovenste punt: een driehoek met de punt omhoog.",
    "Vouw de linkerhoek naar de rechterkant, zo dat de bovenkant van het flapje recht ligt.",
    "Vouw de rechterhoek op dezelfde manier naar de linkerkant.",
    "Vouw het bovenste puntje naar voren over de flapjes heen, draai om en doe het andere puntje naar achteren.",
    "Duw het bekertje open: klaar! Het is van papier, dus alleen voor even een slokje (of om spulletjes in te bewaren)."], "thuis", "6-9", 2, "b")

# ---------- sjablonen zonder losse binnenvormen ----------
from shapes import stencil, star_path, cloud_path, drop_path, fish_path
def bolt(x, y): return P([(x + 4, y - 30), (x - 14, y + 4), (x - 2, y + 4), (x - 8, y + 30), (x + 14, y - 6), (x + 2, y - 6), (x + 10, y - 30)])
def umbrella(x, y): return f"M{x - 28} {y}A28 26 0 0 1 {x + 28} {y}Q{x + 21} {y - 5} {x + 14} {y}Q{x + 7} {y - 5} {x + 2} {y}V{y + 22}Q{x + 2} {y + 28} {x - 6} {y + 28}Q{x - 12} {y + 28} {x - 12} {y + 22}H{x - 8}Q{x - 8} {y + 24} {x - 6} {y + 24}Q{x - 2} {y + 24} {x - 2} {y + 22}V{y}Q{x - 7} {y - 5} {x - 14} {y}Q{x - 21} {y - 5} {x - 28} {y}Z"
def sun(x, y):
    p = []
    for i in range(24):
        r = 26 if i % 2 == 0 else 15
        a = math.pi * i / 12; p.append((x + r * math.cos(a), y + r * math.sin(a)))
    return P(p)
def snowman(x, y): return f"M{x - 6} {y - 14}A10 10 0 1 1 {x + 6} {y - 14}A16 16 0 1 1 {x - 6} {y - 14}Z"
stencil("sjablonen-weer", "Sjablonen: het weer", [lambda x, y: cloud_path(x, y + 6, 18), sun, lambda x, y: drop_path(x, y + 4, 15), bolt, umbrella, snowman], "natuur", "6-9")
def shell(x, y):
    p = [(x, y + 26)]
    for i in range(9):
        a = math.radians(200 + i * 17.5); p.append((x + 28 * math.cos(a), y + 8 + 28 * math.sin(a)))
    return P(p)
def whale(x, y): return f"M{x - 30} {y + 4}C{x - 30} {y - 18} {x + 4} {y - 22} {x + 16} {y - 4}L{x + 26} {y - 16}Q{x + 30} {y - 6} {x + 24} {y + 2}Q{x + 30} {y + 10} {x + 26} {y + 18}L{x + 16} {y + 8}C{x + 6} {y + 20} {x - 30} {y + 22} {x - 30} {y + 4}Z"
def starfish(x, y): return star_path(x, y, 28, 11)
def wave(x, y): return f"M{x - 32} {y + 18}C{x - 30} {y - 10} {x + 6} {y - 26} {x + 22} {y - 8}Q{x + 6} {y - 10} {x + 4} {y + 4}Q{x + 18} {y + 4} {x + 32} {y + 18}Z"
def boat(x, y): return P([(x - 30, y + 4), (x + 30, y + 4), (x + 20, y + 20), (x - 20, y + 20)]) + P([(x - 2, y), (x - 2, y - 28), (x - 24, y)])
stencil("sjablonen-zee", "Sjablonen: aan zee", [lambda x, y: fish_path(x - 4, y, 20), shell, whale, starfish, wave, boat], "zee", "6-9")
def car(x, y): return f"M{x - 32} {y + 10}V{y - 2}Q{x - 32} {y - 6} {x - 26} {y - 6}L{x - 16} {y - 20}H{x + 12}L{x + 22} {y - 6}H{x + 28}Q{x + 32} {y - 6} {x + 32} {y - 2}V{y + 10}H{x + 26}A8 8 0 0 0 {x + 10} {y + 10}H{x - 10}A8 8 0 0 0 {x - 26} {y + 10}Z"
def plane(x, y):
    half = [(32, 0), (26, -4), (6, -4), (-6, -26), (-12, -26), (-4, -4), (-22, -4), (-28, -12), (-32, -12), (-28, 0)]
    return P([(x + a, y + b) for a, b in half] + [(x + a, y - b) for a, b in reversed(half[1:-1])])
def rocket(x, y): return f"M{x} {y - 32}Q{x + 12} {y - 18} {x + 10} {y + 10}L{x + 20} {y + 26}H{x - 20}L{x - 10} {y + 10}Q{x - 12} {y - 18} {x} {y - 32}Z"
def train(x, y): return P([(x - 32, y + 16), (x - 32, y - 6), (x - 14, y - 6), (x - 14, y - 22), (x + 6, y - 22), (x + 6, y - 6), (x + 18, y - 6), (x + 18, y - 18), (x + 26, y - 18), (x + 26, y - 6), (x + 32, y - 6), (x + 32, y + 16)])
stencil("sjablonen-vervoer", "Sjablonen: vervoer", [car, lambda x, y: boat(x, y - 6), plane, rocket, train, lambda x, y: P([(x - 32, y + 12), (x - 32, y - 16), (x + 10, y - 16), (x + 10, y - 8), (x + 22, y - 8), (x + 32, y + 2), (x + 32, y + 12)])], "voertuigen", "6-9")

# ---------- lijnenkunst: zelf lijnen trekken tussen genummerde stippen ----------
def lijnenkunst(slug, name, axes, pairs, n, rule, age, diff, short):
    """axes: lijsten (start, eind) waarop stippen 1..n-1 staan; pairs: (as_a, as_b, f) met f(j) = stip op as_b."""
    sh, ex = Sheet(), Sheet()
    title(sh, cap(name.split(": ", 1)[-1]), 16); title(ex, "Zo kan hij worden", 16)
    sh.text(100, 27, short, 6)
    oy = 40
    for a, b in axes:
        for sht in (sh, ex): sht.seg(a[0], a[1] + oy, b[0], b[1] + oy, "l", "stroke-width:1.2")
        dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy); nx, ny = -dy / ln, dx / ln
        for j in range(1, n):
            x, y = a[0] + dx * j / n, a[1] + dy * j / n + oy
            sh.dot(x, y, 1.3)
            sh.text(x + nx * 5, y + ny * 5 + 1.6, str(j), 4.6)
    def pt(ax, j):
        a, b = axes[ax]; return a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n + oy
    for ia, ib, fn in pairs:
        for j in range(1, n):
            k = fn(j)
            if 1 <= k < n: ex.seg(*pt(ia, j), *pt(ib, k), "l", "stroke-width:.6")
    write(OUT, slug, sh, {"category": "patronen", "age": age, "kind": "tekenles", "difficulty": diff, "minutes": 30,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": name, "description": "Je trekt alleen rechte lijnen, en toch ontstaan er bochten.", "steps": [
            "Pak een liniaal en een scherp potlood.", rule,
            "Werk netjes van 1 naar het laatste cijfer, as voor as.",
            "Kleur daarna de vakjes tussen de lijnen in verlopende tinten. Op de tweede bladzijde zie je hoe het kan worden."]}}},
        [("extra", "Zo kan hij worden", ex)])
def radial(k, r=88, off=-90):
    return [((100, 100), (100 + r * math.cos(math.radians(off + i * 360 / k)), 100 + r * math.sin(math.radians(off + i * 360 / k)))) for i in range(k)]
lijnenkunst("lijnenkunst-ster", "Lijnenkunst: ster van rechte lijnen", radial(4), [(i, (i + 1) % 4, lambda j: 12 - j) for i in range(4)], 12,
    "Verbind een stip met een stip op de as ernaast, zo dat de cijfers samen 12 zijn: 1 met 11, 2 met 10 enzovoort.", "9+", 2, "Verbind stippen op assen naast elkaar die samen 12 zijn.")
lijnenkunst("lijnenkunst-zeshoek", "Lijnenkunst: ster met zes punten", radial(6), [(i, (i + 1) % 6, lambda j: 12 - j) for i in range(6)], 12,
    "Verbind telkens een stip met een stip op de as ernaast, zo dat de cijfers samen 12 zijn.", "12+", 3, "Verbind stippen op assen naast elkaar die samen 12 zijn.")
sq = [((10, 10), (190, 10)), ((190, 10), (190, 190)), ((190, 190), (10, 190)), ((10, 190), (10, 10))]
lijnenkunst("lijnenkunst-hoeken", "Lijnenkunst: vier hoeken", sq, [(i, (i + 1) % 4, lambda j: j) for i in range(4)], 14,
    "Verbind elk cijfer met hetzelfde cijfer op de zijde rechts ervan (met de klok mee): 1 met 1, 2 met 2 enzovoort.", "12+", 3, "Verbind elk cijfer met hetzelfde cijfer op de zijde rechts ervan.")

# ---------- 12+: isometrische kubussen ----------
def iso():
    sh = Sheet(200)
    s = 16; h = s * math.sqrt(3) / 2
    for row in range(-1, 9):
        for col in range(-1, 8):
            cx = col * 2 * h + (h if row % 2 else 0) + 12; cy = row * 1.5 * s + 12
            top = [(cx, cy - s), (cx + h, cy - s / 2), (cx, cy), (cx - h, cy - s / 2)]
            left = [(cx - h, cy - s / 2), (cx, cy), (cx, cy + s), (cx - h, cy + s / 2)]
            right = [(cx, cy), (cx + h, cy - s / 2), (cx + h, cy + s / 2), (cx, cy + s)]
            for poly, code in ((top, "y"), (left, "b"), (right, "n")):
                if all(-0.5 <= x <= 200.5 and -0.5 <= y <= 200.5 for x, y in poly): sh.poly_r(poly, code)
    write(OUT, "patroon-kubussen", sh, {"category": "patronen", "age": "12+", "kind": "kleurplaat", "difficulty": 2,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}],
        "i18n": {"nl": {"name": "Patroon: kubussen in 3D", "description": "Kleur alle bovenkanten licht, alle linkerkanten middel en alle rechterkanten donker: dan worden het blokken die van het papier lijken te komen."}}})
iso()

# ---------- 12+: op-art ringen ----------
def opart():
    sh = Sheet(200)
    n = 12
    for i in range(n, 0, -1):
        r = i * 8
        for k in range(16):
            sh.region(arc_path(100 + (n - i) * 1.6, 100, max(r - 8, 0.01) if i > 1 else 0.01, r, k * 22.5, (k + 1) * 22.5), "k" if (i + k) % 2 else "-")
    write(OUT, "op-art-ringen", sh, {"category": "patronen", "age": "12+", "kind": "kleurplaat", "difficulty": 3,
        "materials": [{"slug": "stiften"}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": "Op-art: verschoven ringen", "description": "Kleur de vakjes om en om zwart en wit (of in twee kleuren). Doordat de ringen een beetje verschoven zijn, lijkt het vel te bollen."}}})
opart()

# ---------- mandala's (nieuwe opbouw) ----------
mandala("mandala-druppels", "Mandala met druppels", [("seg", 0, 12, 1, "y"), ("petal", 12, 40, 8, "bt"), ("dot", 40, 50, 16, "y"), ("petal", 50, 82, 16, "nb"), ("tri", 82, 96, 32, "t")])
mandala("mandala-ruiten", "Mandala met ruiten", [("seg", 0, 10, 1, "r"), ("tri", 10, 30, 6, "o"), ("seg", 30, 44, 12, "yo"), ("tri", 44, 70, 12, "rk"), ("petal", 58, 84, 24, "m", 7.5), ("seg", 84, 96, 48, "ko")])

# ---------- kaarten ----------
def front_juf(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Bedankt juf of meester!", 12)
    sh.circle_r(78, y0 + 78, 24, "r"); sh.region(f"M78 {y0 + 54}Q84 {y0 + 40} 96 {y0 + 42}Q90 {y0 + 54} 78 {y0 + 54}Z", "g"); sh.line(f"M78 {y0 + 56}V{y0 + 46}")
    sh.raw(f'<g transform="rotate(-25 136 {y0 + 80})">'); sh.rect_r(130, y0 + 50, 12, 52, "y"); sh.poly_r([(130, y0 + 102), (142, y0 + 102), (136, y0 + 114)], "w"); sh.rect_r(130, y0 + 44, 12, 6, "k"); sh.raw('</g>')
card("bedankkaart-juf-meester", "Bedankkaart voor de juf of meester", front_juf, "Bedankt voor het fijne jaar!", "feest", "4-6", ["Schrijf binnenin wat je het leukst vond dit jaar."])
def front_baby(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Welkom kleintje!", 15)
    cx, cy = 100, y0 + 76
    sh.circle_r(cx, cy - 16, 16, "y")
    for k in range(6): a = math.radians(k * 60); sh.circle_r(cx + 22 * math.cos(a), cy - 16 + 22 * math.sin(a), 5, "b" if k % 2 else "k")
    sh.rect_r(cx - 3, cy, 6, 34, "o", 3); sh.circle_r(cx, cy + 36, 6, "o")
card("geboortekaart-rammelaar", "Kaart voor een nieuwe baby", front_baby, "Gefeliciteerd met de baby!", "feest", "6-9", ["Schrijf binnenin de naam van de baby en een lieve wens."])
def front_geslaagd(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Geslaagd!", 18)
    cx, cy = 100, y0 + 66
    sh.poly_r([(cx - 40, cy - 6), (cx, cy - 22), (cx + 40, cy - 6), (cx, cy + 10)], "n"); sh.region(f"M{cx - 22} {cy + 2}V{cy + 18}Q{cx} {cy + 30} {cx + 22} {cy + 18}V{cy + 2}L{cx} {cy + 10}Z", "n")
    sh.line(f"M{cx} {cy - 6}L{cx + 30} {cy + 4}V{cy + 22}"); sh.circle_r(cx + 30, cy + 25, 3, "y")
    sh.rect_r(cx - 50, cy + 36, 100, 14, "w", 7); sh.rect_r(cx - 8, cy + 34, 16, 18, "r")
card("felicitatiekaart-geslaagd", "Felicitatiekaart: geslaagd!", front_geslaagd, "Wat knap van je!", "feest", "9+", ["Schrijf binnenin voor wie de kaart is en waar diegene voor geslaagd is."])
def front_opa(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Voor opa en oma", 14)
    for cx, c, hair in [(72, "k", "w"), (128, "k", "w")]:
        cy = y0 + 76
        sh.circle_r(cx, cy, 20, c)
        sh.region(f"M{cx - 21} {cy - 2}Q{cx - 22} {cy - 26} {cx} {cy - 24}Q{cx + 22} {cy - 26} {cx + 21} {cy - 2}Q{cx + 12} {cy - 16} {cx} {cy - 16}Q{cx - 12} {cy - 16} {cx - 21} {cy - 2}Z", hair)
        sh.circle_line(cx - 7, cy, 5); sh.circle_line(cx + 7, cy, 5); sh.seg(cx - 2, cy, cx + 2, cy)
        sh.line(f"M{cx - 7} {cy + 10}Q{cx} {cy + 15} {cx + 7} {cy + 10}")
    sh.region(f"M100 {y0 + 110}C87 {y0 + 101} 91 {y0 + 91} 100 {y0 + 97}C109 {y0 + 91} 113 {y0 + 101} 100 {y0 + 110}Z", "r")
card("kaart-opa-en-oma", "Kaart voor opa en oma", front_opa, "Ik vind jullie lief!", "feest", "4-6", ["Teken binnenin iets wat je samen met opa en oma doet."])

# ---------- tekenlessen ----------
from lib_gen import C, E
lesson("tekenles-vogel", "Tekenles: een vogeltje", [
    [E(48, 55, 26, 20)], [C(70, 36, 13)], ["M82 32L94 37L82 42", C(73, 33, 2)], ["M30 52Q46 40 60 56Q46 66 30 52"],
    ["M24 52L6 42M24 58L6 60", "M44 74V86M54 74V86M40 86H48M50 86H58"], ["M4 88H96", "M70 88Q80 80 88 82"]], [
    "Teken een ovaal lijf.", "Een rond kopje erop, rechtsboven.", "Een snavel en een oog.", "Een vleugel op het lijf.", "Een staart en twee pootjes.", "Een tak om op te zitten."], "4-6", 1, "dieren")
lesson("tekenles-boom", "Tekenles: een appelboom", [
    ["M42 92V56H58V92"], ["M36 56Q16 56 18 40Q12 22 32 20Q40 4 56 10Q76 6 78 24Q92 34 80 48Q76 58 64 56"], ["M50 74L38 62M50 68L62 58"],
    [C(34, 36, 4), C(58, 26, 4), C(68, 42, 4), C(44, 46, 4)], ["M8 92H92", "M20 92L22 86L24 92M74 92L76 86L78 92"], [C(90, 10, 6)]], [
    "Teken een stam.", "Een wolkige kruin erop.", "Twee takjes in de stam.", "Appels in de boom.", "Gras onder de boom.", "Een zonnetje erbij."], "4-6", 1, "natuur")
lesson("tekenles-olifant", "Tekenles: een olifant", [
    [E(58, 56, 30, 20)], [C(28, 44, 16)], ["M30 30Q48 24 46 46Q44 60 30 56"], ["M14 50Q6 66 10 80Q16 84 18 78Q14 66 22 56"],
    ["M36 72V90H46V76M68 75V90H78V70"], [C(23, 40, 2), "M88 52Q96 56 94 66"]], [
    "Teken een groot ovaal lijf.", "Een rond hoofd links ervan.", "Een groot oor.", "Een lange slurf naar beneden.", "Dikke poten.", "Een oog en een staartje."], "6-9", 2, "dieren")
lesson("tekenles-bloem", "Tekenles: een bloem in een pot", [
    [C(50, 30, 8)], [C(50, 13, 8), C(65, 22, 8), C(65, 39, 8), C(50, 47, 8), C(35, 39, 8), C(35, 22, 8)], ["M50 55Q48 72 50 90"],
    ["M50 72Q34 60 28 70Q38 78 50 72", "M50 80Q66 68 72 78Q62 86 50 80"], ["M32 90H68L63 104H37Z"], ["M80 18L86 13L86 23Z", "M80 18L74 13L74 23Z"]], [
    "Teken een rondje: het hart van de bloem.", "Zes blaadjes eromheen.", "Een steel naar beneden.", "Twee blaadjes aan de steel.", "Een bloempot.", "Een vlindertje dat langs komt."], "4-6", 1, "natuur")

# ---------- sudoku's ----------
def solve(g, n, bh, bw, limit=2):
    sols = [0]
    def ok(r, c, v):
        if v in g[r] or any(g[i][c] == v for i in range(n)): return False
        r0, c0 = r - r % bh, c - c % bw
        return all(g[i][j] != v for i in range(r0, r0 + bh) for j in range(c0, c0 + bw))
    def rec():
        for r in range(n):
            for c in range(n):
                if g[r][c] == 0:
                    for v in range(1, n + 1):
                        if ok(r, c, v):
                            g[r][c] = v; rec(); g[r][c] = 0
                            if sols[0] >= limit: return
                    return
        sols[0] += 1
    rec(); return sols[0]
def make(n, bh, bw, givens, rng):
    base = [[(bw * (r % bh) + r // bh + c) % n + 1 for c in range(n)] for r in range(n)]
    perm = list(range(1, n + 1)); rng.shuffle(perm)
    sol = [[perm[v - 1] for v in row] for row in base]
    rows = [b * bh + i for b in rng.sample(range(n // bh), n // bh) for i in rng.sample(range(bh), bh)]
    cols = [b * bw + i for b in rng.sample(range(n // bw), n // bw) for i in rng.sample(range(bw), bw)]
    sol = [[sol[r][c] for c in cols] for r in rows]
    puz = [row[:] for row in sol]
    cells = [(r, c) for r in range(n) for c in range(n)]; rng.shuffle(cells)
    for r, c in cells:
        if sum(v != 0 for row in puz for v in row) <= givens: break
        keep = puz[r][c]; puz[r][c] = 0
        if solve([row[:] for row in puz], n, bh, bw) != 1: puz[r][c] = keep
    assert solve([row[:] for row in puz], n, bh, bw) == 1
    return puz, sol
def grid(sh, x, y, cell, n, bh, bw, vals, fill_ans=None):
    for i in range(n + 1):
        thick = "stroke-width:1.6" if i % bw == 0 else "stroke-width:.6"
        sh.seg(x + i * cell, y, x + i * cell, y + n * cell, "l", thick)
        thick = "stroke-width:1.6" if i % bh == 0 else "stroke-width:.6"
        sh.seg(x, y + i * cell, x + n * cell, y + i * cell, "l", thick)
    for r in range(n):
        for c in range(n):
            v = vals[r][c]
            if v: sh.text(x + c * cell + cell / 2, y + r * cell + cell * .68, str(v), cell * .55, weight=700 if fill_ans is None or fill_ans[r][c] else None)
def sudoku_sheet(slug, name, n, bh, bw, count, givens, age, diff, seed, intro):
    rng = random.Random(seed)
    ps = [make(n, bh, bw, givens, rng) for _ in range(count)]
    sh, ans = Sheet(), Sheet()
    title(sh, cap(name.split(": ", 1)[-1]), 16); title(ans, "Antwoorden", 16)
    sh.text(100, 27, intro, 6)
    per_row = 2; size = 80 if n == 4 else 84; cell = size / n
    for k, (p, s) in enumerate(ps):
        x = 14 + (k % per_row) * (size + 16); y = 42 + (k // per_row) * (size + 26)
        sh.text(x, y - 4, f"Puzzel {k + 1}", 6, "start"); ans.text(x, y - 4, f"Puzzel {k + 1}", 6, "start")
        grid(sh, x, y, cell, n, bh, bw, p)
        grid(ans, x, y, cell, n, bh, bw, s, p)
    write(OUT, slug, sh, {"category": "leren", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 10 + diff * 5, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            f"Elke rij, elke kolom en elk vak met een dikke rand krijgt de cijfers 1 tot en met {n}, elk cijfer precies één keer.",
            "Zoek een rij, kolom of vak waar nog maar één cijfer mist en vul dat in.",
            "Schrijf met potlood, dan kun je gummen. Vast? Kijk op de antwoordbladzijde."]}}}, [("antwoorden", "Antwoorden", ans)])
sudoku_sheet("sudoku-4x4-start", "Sudoku: 4 bij 4 om te beginnen", 4, 2, 2, 4, 9, "6-9", 1, 41, "Vul de lege hokjes met 1, 2, 3 of 4.")
sudoku_sheet("sudoku-4x4-pittig", "Sudoku: 4 bij 4, iets pittiger", 4, 2, 2, 4, 5, "6-9", 2, 42, "Minder hulpcijfers: kijk goed naar rij, kolom en vak tegelijk.")
sudoku_sheet("sudoku-6x6", "Sudoku: 6 bij 6", 6, 2, 3, 4, 14, "9+", 3, 43, "Vul 1 tot en met 6 in. Elk vak is 2 hoog en 3 breed.")
