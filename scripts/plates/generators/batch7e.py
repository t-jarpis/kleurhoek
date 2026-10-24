"""Batch 7e: patronen en mandala's voor 12+."""
import math
from lib_gen import *

MAT = [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}]
def pat(slug, name, draw, desc, diff=3):
    sh = Sheet(200); draw(sh)
    write(OUT, slug, sh, {"category": "patronen", "age": "12+", "kind": "kleurplaat", "difficulty": diff, "materials": MAT,
                          "i18n": {"nl": {"name": name, "description": desc}}})

mandala("mandala-vlinders", "Mandala met blaadjes en bogen", [("seg", 0, 8, 1, "y"), ("petal", 8, 30, 12, "om"), ("seg", 30, 36, 24, "y"), ("tri", 36, 56, 24, "pm"),
        ("petal", 50, 74, 12, "k", 15), ("dot", 74, 82, 24, "y"), ("petal", 80, 98, 24, "pn")])
mandala("mandala-kristal", "Mandala als een kristal", [("tri", 0, 26, 6, "bt"), ("tri", 20, 44, 6, "n", 30), ("seg", 44, 52, 18, "bt"), ("tri", 52, 76, 18, "t"),
        ("tri", 66, 88, 18, "b", 10), ("seg", 88, 96, 36, "nb")])
mandala("mandala-hartenkrans", "Mandala met een krans van harten", [("seg", 0, 14, 1, "r"), ("heart", 14, 34, 8, "m"), ("seg", 36, 42, 32, "kr"), ("petal", 42, 68, 16, "mk"),
        ("heart", 66, 84, 16, "r"), ("dot", 86, 94, 32, "k")])
mandala("mandala-zonnewiel", "Mandala als een zonnewiel", [("seg", 0, 10, 1, "o"), ("seg", 10, 30, 16, "yo"), ("tri", 30, 50, 16, "r"), ("seg", 50, 58, 32, "yo"),
        ("petal", 58, 84, 16, "y"), ("tri", 84, 98, 32, "o", 5.625)])

def schubben(sh):
    r = 16
    for row in range(0, 22):
        y = row * r * .62
        for col in range(-1, 8):
            x = col * 2 * r * .95 + (r * .95 if row % 2 else 0)
            p = f"M{f(x - r)} {f(y)}A{r} {r} 0 0 0 {f(x + r)} {f(y)}A{r} {r} 0 0 1 {f(x - r)} {f(y)}Z" if False else None
            d = f"M{f(x - r * .95)} {f(y)}A{r} {r} 0 0 0 {f(x + r * .95)} {f(y)}L{f(x + r * .95)} {f(y - 2)}Q{f(x)} {f(y + r * .4)} {f(x - r * .95)} {f(y - 2)}Z"
            if -2 <= x - r and x + r <= 202 and y + r <= 201 and y >= 0: sh.region(f"M{f(x - r * .95)} {f(y)}A{f(r * .95)} {f(r * .95)} 0 0 0 {f(x + r * .95)} {f(y)}Z", "tbng"[(row + col) % 4])
# pat("patroon-schubben", "Patroon: schubben", schubben, "Een patroon van overlappende schubben, zoals bij een vis of een draak. Kleur ze in verlopende tinten van licht naar donker.")
def golven(sh):
    for i in range(12):
        y0 = 4 + i * 16
        d = f"M0 {y0}" + "".join(f"Q{k * 40 + 10} {y0 - 8} {k * 40 + 20} {y0}T{k * 40 + 40} {y0}" for k in range(5))
        d2 = f"L200 {y0 + 16}" + "".join(f"Q{200 - k * 40 - 10} {y0 + 16 + 8} {200 - k * 40 - 20} {y0 + 16}T{200 - k * 40 - 40} {y0 + 16}" for k in range(5)) + "Z"
        d2 = f"L200 {y0 + 16}" + "".join(f"T{200 - (k + 1) * 20} {y0 + 16}" for k in range(10)) + "Z"
        pts_top = [(k * 5, y0 + 6 * math.sin(k * 5 / 40 * 2 * math.pi + i * .6)) for k in range(41)]
        pts_bot = [(k * 5, y0 + 16 + 6 * math.sin(k * 5 / 40 * 2 * math.pi + (i + 1) * .6)) for k in range(41)]
        if i == 11: pts_bot = [(k * 5, 199) for k in range(41)]
        if i == 0: pts_top = [(k * 5, 1) for k in range(41)]
        sh.region("M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts_top) + " L" + " L".join(f"{f(x)} {f(y)}" for x, y in reversed(pts_bot)) + "Z", "bntp"[i % 4])
pat("patroon-golven", "Patroon: golvende strepen", golven, "Golvende banen die steeds een beetje verschuiven. Probeer een regenboog van boven naar beneden, of alleen blauwtinten.", 2)
def visgraat(sh):
    w, h = 40, 10
    for col in range(-1, 6):
        for row in range(-2, 22):
            x = col * w; y = row * h
            if col % 2 == 0: p = [(x, y), (x + w, y + w / 2 - h / 2 + h * 0), (x + w, y + w / 2 + h / 2), (x, y + h)]
            else: p = [(x, y + w / 2 - h / 2), (x + w, y - 0), (x + w, y + h), (x, y + w / 2 + h / 2)]
            p = [(px, py) for px, py in p]
            if all(-0.5 <= px <= 200.5 and -0.5 <= py <= 200.5 for px, py in p): sh.poly_r(p, "woy"[(row + col) % 3])
pat("patroon-visgraat", "Patroon: visgraat", visgraat, "Het visgraatpatroon ken je van parketvloeren. Kleur de planken in drie houtkleuren, of juist heel bont.", 2)
def weefsel(sh):
    s = 20
    for row in range(10):
        for col in range(10):
            x, y = col * s, row * s
            if (row + col) % 2 == 0:
                for k in range(3): sh.rect_r(x, y + k * s / 3, s, s / 3, "ry"[k % 2] if k != 1 else "o")
            else:
                for k in range(3): sh.rect_r(x + k * s / 3, y, s / 3, s, "bn"[k % 2] if k != 1 else "t")
pat("patroon-mandweefsel", "Patroon: gevlochten mand", weefsel, "Liggende en staande strookjes wisselen elkaar af, alsof ze door elkaar heen gevlochten zijn. Kies één kleur voor liggend en één voor staand.", 2)
def penrose(sh):
    c = (100, 112); R = 88; t = 22
    A = [(c[0] + R * math.cos(math.radians(a)), c[1] + R * math.sin(math.radians(a))) for a in (-90, 30, 150)]
    def lerp(p, q, s): return (p[0] + (q[0] - p[0]) * s, p[1] + (q[1] - p[1]) * s)
    # drie balken van een 'onmogelijke' driehoek: per hoek een L-vorm
    L = math.dist(A[0], A[1]); s = t / L * 1.732
    for i in range(3):
        P, Q, Rr = A[i], A[(i + 1) % 3], A[(i + 2) % 3]
        inner = [lerp(c, a, (R - t * 2) / R) for a in A]
        mid = [lerp(c, a, (R - t) / R) for a in A]
        Pi, Qi = inner[i], inner[(i + 1) % 3]; Pm, Qm = mid[i], mid[(i + 1) % 3]
        poly = [P, lerp(P, Q, 1 - s), lerp(Pm, Qm, 1 - s / 1.0) if False else Qm, Pm]
        sh.poly_r([P, Q, Qm, lerp(Pm, Pi, 0) ], "-") if False else None
    # eenvoudige, goed sluitende versie: drie vlakken van een driehoekige 'tribar'
    o = [(c[0] + R * math.cos(math.radians(a)), c[1] + R * math.sin(math.radians(a))) for a in (-90, 30, 150)]
    m = [(c[0] + (R - 2 * t) * math.cos(math.radians(a)), c[1] + (R - 2 * t) * math.sin(math.radians(a))) for a in (-90, 30, 150)]
    i_ = [(c[0] + (R - 4 * t) * math.cos(math.radians(a)), c[1] + (R - 4 * t) * math.sin(math.radians(a))) for a in (-90, 30, 150)]
    for k, code in zip(range(3), "bnt"):
        a, b = k, (k + 1) % 3
        sh.poly_r([o[a], o[b], m[b], m[a]], code)
    for k, code in zip(range(3), "bnt"):
        a, b = k, (k + 1) % 3
        sh.poly_r([m[a], lerp(m[a], m[b], .5), lerp(i_[a], i_[b], .5), i_[a]], code)
# pat("patroon-driehoek-in-driehoek", "Patroon: driehoek in driehoek", penrose, "Twee driehoekige ringen in elkaar. Kleur elke kant in een eigen tint en kijk of je diepte ziet.", 2)
