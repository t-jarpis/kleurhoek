import math, random
from lib_gen import *

# ---------- schrijven ----------
letters("schrijven-letters-k-tot-o", "Schrijven: de letters k tot en met o", list("klmno"))
letters("schrijven-letters-p-tot-t", "Schrijven: de letters p tot en met t", list("pqrst"))
letters("schrijven-letters-u-tot-z", "Schrijven: de letters u tot en met z", list("uvwxyz"))
letters("schrijven-cijfers-0-tot-4", "Schrijven: de cijfers 0 tot en met 4", list("01234"))
letters("schrijven-cijfers-5-tot-9", "Schrijven: de cijfers 5 tot en met 9", list("56789"))

# ---------- rekenen ----------
rnd = random.Random(2024)
def uniq(gen, n):
    out = []
    while len(out) < n:
        x = gen()
        if x not in out: out.append(x)
    return out
def plus20():
    a, b = rnd.randint(2, 15), rnd.randint(2, 9)
    return (f"{a} + {b}", a + b) if a + b <= 20 else plus20()
sums_sheet("rekenen-optellen-tot-20", "Rekenen: optellen tot 20", uniq(plus20, 12), "6-9", 2, "Tel op en schrijf het antwoord in het hokje.",
           ["Lees de som, bijvoorbeeld 8 + 5.", "Handig: maak eerst 10 vol (8 + 2 = 10) en tel de rest erbij (10 + 3 = 13)."])
def min10():
    a = rnd.randint(3, 10); b = rnd.randint(1, a)
    return (f"{a} − {b}", a - b)
sums_sheet("rekenen-aftrekken-tot-10", "Rekenen: aftrekken tot 10", uniq(min10, 12), "6-9", 1, "Haal eraf en schrijf het antwoord in het hokje.",
           ["Lees de som, bijvoorbeeld 7 − 3.", "Steek 7 vingers op, doe er 3 omlaag en tel wat er over is."])
for t, age in [(2, "6-9"), (5, "6-9"), (10, "6-9")]:
    order = [3, 7, 1, 10, 5, 8, 2, 6, 9, 4, 0, 11] if t != 5 else [4, 9, 2, 6, 10, 1, 7, 3, 8, 5, 0, 12]
    sums_sheet(f"rekenen-tafel-van-{t}", f"Rekenen: de tafel van {t}", [(f"{n} × {t}", n * t) for n in order], age, 2 if t != 10 else 1,
               f"Weet je de tafel van {t}? Schrijf het antwoord in het hokje.", [f"Zeg de tafel van {t} hardop: 1 × {t} = {t}, 2 × {t} = {2 * t} …", "Vul de antwoorden in. Ze staan door elkaar!"])
def mix():
    a, b = rnd.randint(1, 10), rnd.randint(1, 5)
    return (f"{a} × {b}", a * b)
sums_sheet("rekenen-tafels-1-tot-5-door-elkaar", "Rekenen: tafels van 1 tot 5 door elkaar", uniq(mix, 12), "6-9", 3,
           "Alle tafels tot en met 5 door elkaar. Lukt het zonder te tellen?", ["Lees de som en zeg de tafel in je hoofd.", "Weet je het niet meteen? Tel in sprongen: 3 × 4 = 4, 8, 12."])
sums_sheet("rekenen-splitsen-van-10", "Rekenen: splitsen van 10", [(f"{a} +", 10 - a) for a in [3, 7, 1, 9, 5, 2, 8, 4, 6, 0, 10, 5]][:11], "6-9", 1,
           "Hoeveel moet erbij om 10 te maken?", ["Lees de som, bijvoorbeeld 3 + ? = 10.", "Tel van 3 door tot 10 op je vingers: dat zijn er 7. Schrijf 7 in het hokje."], box_w=18, eq="", after="= 10")

# ---------- klokkijken ----------
def clock(sh, cx, cy, r, h=None, m=None):
    sh.circle_r(cx, cy, r, "-")
    for i in range(12):
        a = math.radians(i * 30)
        sh.seg(cx + (r - 3) * math.sin(a), cy - (r - 3) * math.cos(a), cx + r * math.sin(a), cy - r * math.cos(a), "l", "stroke-width:1")
        sh.text(cx + (r - 8) * math.sin(a), cy - (r - 8) * math.cos(a) + 2.2, str(12 if i == 0 else i), 6)
    if h is not None:
        ha = math.radians((h % 12) * 30 + m * .5); ma = math.radians(m * 6)
        sh.seg(cx, cy, cx + r * .5 * math.sin(ha), cy - r * .5 * math.cos(ha), "l", "stroke-width:2.6")
        sh.seg(cx, cy, cx + r * .78 * math.sin(ma), cy - r * .78 * math.cos(ma), "l", "stroke-width:1.6")
    sh.dot(cx, cy, 1.8)
def tijd(h, m):
    nxt = h % 12 + 1
    return {0: f"{h} uur", 15: f"kwart over {h}", 30: f"half {nxt}", 45: f"kwart voor {nxt}"}[m]
def clock_sheet(slug, name, times, draw_hands_on_main, steps, diff):
    def page(answer):
        sh = Sheet()
        title(sh, "Antwoorden" if answer else cap(name.split(": ", 1)[-1]), 18)
        sh.text(100, 30, "Teken de wijzers in de klok." if not draw_hands_on_main and not answer else "Schrijf de tijd onder de klok.", 6.5)
        for i, (h, m) in enumerate(times):
            col, row = i % 2, i // 2
            cx, cy = 58 + col * 84, 72 + row * 72
            show = draw_hands_on_main or answer
            clock(sh, cx, cy, 26, h if show else None, m if show else None)
            sh.seg(cx - 30, cy + 42, cx + 30, cy + 42, "guide")
            if not draw_hands_on_main or answer: sh.text(cx, cy + 40, tijd(h, m), 7.5)
        return sh
    write(OUT, slug, page(False), {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": diff, "minutes": 10, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": name, "steps": steps}}}, [("antwoorden", "Antwoorden", page(True))])
clock_sheet("klokkijken-kwartieren", "Klokkijken: kwart over en kwart voor", [(2, 15), (6, 45), (10, 15), (3, 45), (8, 15), (11, 45)], True, [
    "Staat de lange wijzer op de 3? Dan is het kwart over: kwart over 2.",
    "Staat de lange wijzer op de 9? Dan is het kwart voor het volgende uur: kwart voor 7.",
    "Schrijf de tijd onder elke klok en kijk na met het antwoordblad."], 3)
clock_sheet("klokkijken-wijzers-tekenen", "Klokkijken: teken de wijzers", [(4, 0), (9, 30), (1, 0), (6, 30), (11, 0), (2, 30)], False, [
    "Lees de tijd onder de klok.",
    "Teken de lange wijzer: op de 12 bij een heel uur, op de 6 bij half.",
    "Teken de korte wijzer: bij het uur, of bij half precies tussen twee getallen in.",
    "Kijk na met het antwoordblad."], 2)

# ---------- doolhoven met thema ----------
def muis(sh, x, y):
    sh.ellipse_r(x, y, 8, 5.5, "z"); sh.circle_r(x + 6, y - 5, 3, "k"); sh.circle_r(x - 1, y - 5.5, 3, "k"); sh.dot(x + 6.5, y - 1, .9)
    sh.line(f"M{x - 8} {y + 1}Q{x - 15} {y + 4} {x - 13} {y - 4}")
def kaas(sh, x, y):
    sh.poly_r([(x - 11, y + 6), (x + 11, y + 6), (x + 11, y - 3), (x - 11, y - 8)], "y"); sh.circle_r(x - 3, y + 1, 2, "-"); sh.circle_r(x + 5, y - 1, 1.6, "-")
def raketje(sh, x, y):
    sh.region(f"M{x - 4} {y + 8}V{y - 2}Q{x} {y - 12} {x + 4} {y - 2}V{y + 8}Z", "r"); sh.circle_r(x, y - 1, 1.8, "b")
    sh.poly_r([(x - 4, y + 3), (x - 8, y + 9), (x - 4, y + 8)], "o"); sh.poly_r([(x + 4, y + 3), (x + 8, y + 9), (x + 4, y + 8)], "o")
def maantje(sh, x, y):
    r = 10; xx = x + r * .3; dy = r * math.sqrt(1 - .09)
    sh.region(f"M{f(xx)} {f(y - dy)}A{r} {r} 0 1 0 {f(xx)} {f(y + dy)}A{r * .8} {r * .8} 0 0 1 {f(xx)} {f(y - dy)}Z", "y")
def visje(sh, x, y):
    sh.region(f"M{x - 8} {y}Q{x} {y - 7} {x + 6} {y}Q{x} {y + 7} {x - 8} {y}Z", "o"); sh.poly_r([(x + 6, y), (x + 12, y - 5), (x + 12, y + 5)], "o"); sh.dot(x - 4, y - 1, .9)
def kist(sh, x, y):
    sh.rect_r(x - 11, y - 2, 22, 12, "w"); sh.region(f"M{x - 11} {y - 2}Q{x} {y - 12} {x + 11} {y - 2}Z", "w"); sh.rect_r(x - 2, y - 3, 4, 5, "y")
def ridder(sh, x, y):
    sh.region(f"M{x - 7} {y - 8}H{x + 7}V{y}Q{x + 7} {y + 7} {x} {y + 10}Q{x - 7} {y + 7} {x - 7} {y}Z", "n"); sh.seg(x, y - 8, x, y + 9); sh.seg(x - 7, y - 1, x + 7, y - 1)
def kasteel(sh, x, y):
    sh.poly_r([(x - 13, y + 8), (x - 13, y - 6), (x - 9, y - 6), (x - 9, y - 3), (x - 4, y - 3), (x - 4, y - 6), (x + 4, y - 6), (x + 4, y - 3), (x + 9, y - 3), (x + 9, y - 6), (x + 13, y - 6), (x + 13, y + 8)], "z")
    sh.region(f"M{x - 3} {y + 8}V{y + 2}Q{x} {y - 2} {x + 3} {y + 2}V{y + 8}Z", "w")
doolhof("doolhof-muis-kaas", "Doolhof: muis zoekt kaas", "Help de muis naar de kaas", 8, 9, "4-6", 1, 101, muis, kaas, "boerderij", "de muis", "de kaas")
doolhof("doolhof-raket-maan", "Doolhof: raket naar de maan", "Breng de raket naar de maan", 12, 14, "6-9", 2, 202, raketje, maantje, "ruimte", "de raket", "de maan")
doolhof("doolhof-vis-schatkist", "Doolhof: vis zoekt de schatkist", "Zwem naar de schatkist", 11, 13, "6-9", 2, 303, visje, kist, "zee", "het visje", "de schatkist")
doolhof("doolhof-ridder-kasteel", "Doolhof: ridder naar het kasteel", "Breng de ridder naar het kasteel", 18, 21, "9+", 3, 404, ridder, kasteel, "sprookjes", "de ridder", "het kasteel")

# ---------- verbind de punten ----------
huis = [(100, 52), (150, 102), (150, 214), (50, 214), (50, 102), (66, 86), (66, 60), (80, 60), (80, 72)]
def huis_extra(sh):
    sh.rect_r(88, 170, 24, 44, "w"); sh.rect_r(62, 120, 24, 22, "b"); sh.rect_r(114, 120, 24, 22, "b"); sh.circle_r(160, 40, 12, "y")
dots_sheet("verbind-de-punten-huis", "Verbind de punten: huis", outline_points(huis, 30), "4-6", 1, huis_extra, "huis", "thuis")
boot = [(60, 180), (140, 180), (126, 206), (74, 206), (60, 180), (98, 180), (98, 60), (150, 168), (98, 168), (98, 180)]
boot_pts = outline_points([(60, 180), (98, 180), (98, 60), (150, 180), (140, 180), (126, 206), (74, 206)], 20)
def boot_extra(sh):
    sh.region("M20 230Q45 220 70 230T120 230T170 230T190 230", "-") if False else sh.line("M10 226Q35 216 60 226T110 226T160 226T190 226")
    sh.circle_r(40, 60, 12, "y")
dots_sheet("verbind-de-punten-zeilboot", "Verbind de punten: zeilboot", boot_pts, "6-9", 2, boot_extra, "zeilboot", "zee")
hart = [(100 + 5.2 * 16 * math.sin(t) ** 3, 130 - 5.2 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))) for t in [i * 2 * math.pi / 16 for i in range(16)]]
dots_sheet("verbind-de-punten-hart", "Verbind de punten: hart", hart, "4-6", 1, lambda sh: [sh.poly_r(star_pts(x, y, 6, 2.6), "m") for x, y in [(28, 40), (172, 40), (30, 250), (170, 250)]], "hart", "feest")
vl = []
for i in range(24):
    t = i * 2 * math.pi / 24 + math.pi / 24
    r = (abs(math.sin(2 * t)) ** .6) * (72 if math.cos(t) > 0 else 50) + 8
    vl.append((100 + r * math.sin(t), 135 - r * math.cos(t)))
def vlinder_extra(sh):
    sh.ellipse_r(100, 135, 4, 34, "w"); sh.line("M98 102Q90 84 80 80M102 102Q110 84 120 80"); sh.circle_r(80, 80, 2.5, "x"); sh.circle_r(120, 80, 2.5, "x")
dots_sheet("verbind-de-punten-vlinder", "Verbind de punten: vlinder", vl, "6-9", 2, vlinder_extra, "vlinder", "natuur")

# ---------- mandala's en patronen ----------
mandala("mandala-hartjes", "Mandala: hartjes", [("seg", 0, 10, 1, "k"), ("heart", 12, 34, 8, "mr"), ("seg", 36, 42, 16, "kp"), ("petal", 42, 62, 16, "mk"), ("heart", 64, 82, 16, "rm"), ("dot", 84, 92, 32, "kp")], "9+", 2)
mandala("mandala-zon", "Mandala: zon", [("seg", 0, 18, 1, "y"), ("tri", 18, 40, 12, "oy"), ("seg", 40, 48, 24, "ry"), ("tri", 48, 70, 24, "yo"), ("petal", 70, 94, 24, "or")], "9+", 2)
mandala("mandala-sneeuwvlok", "Mandala: sneeuwvlok", [("seg", 0, 8, 1, "b"), ("petal", 8, 30, 6, "bt"), ("tri", 30, 46, 6, "n", 30), ("petal", 30, 56, 12, "tb"), ("dot", 58, 66, 12, "n"), ("tri", 66, 90, 12, "bt"), ("dot", 88, 94, 24, "n")], "12+", 3, holiday="kerst")
mandala("mandala-roos", "Mandala: roos", [("seg", 0, 7, 1, "r"), ("petal", 7, 22, 5, "rm"), ("petal", 14, 36, 10, "mr", 18), ("seg", 36, 40, 30, "g"), ("petal", 40, 64, 20, "kmr"), ("petal", 58, 80, 20, "gl", 9), ("seg", 82, 88, 60, "kg"), ("dot", 88, 94, 60, "mr")], "12+", 3)
tiling("patroon-honingraat", "Patroon: honingraat", "zeshoek", "9+", 2, "yoyw")
tiling("patroon-driehoeken", "Patroon: driehoeken", "driehoek", "12+", 3, "rbygtp")
tiling("patroon-sterren", "Patroon: sterren", "sterren", "6-9", 2, "ybon")
tiling("patroon-ruiten", "Patroon: ruiten", "ruit", "9+", 2, "rkmp")

# ---------- seizoenskaarten ----------
def front_schoen(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 28, "Sinterklaas!", 18)
    sh.region(f"M52 {y0 + 104}V{y0 + 62}Q52 {y0 + 50} 64 {y0 + 50}H84Q94 {y0 + 50} 94 {y0 + 62}V{y0 + 80}Q118 {y0 + 82} 140 {y0 + 92}Q150 {y0 + 98} 146 {y0 + 104}Z", "r")
    sh.rect_r(50, y0 + 104, 98, 6, "w")
    sh.region(f"M98 {y0 + 64}L112 {y0 + 40}Q116 {y0 + 36} 118 {y0 + 42}L104 {y0 + 68}Z", "o")
    sh.region(f"M112 {y0 + 40}Q108 {y0 + 30} 112 {y0 + 26}Q118 {y0 + 32} 116 {y0 + 38}Z", "g")
    sh.circle_r(160, y0 + 50, 7, "w"); sh.circle_r(30, y0 + 60, 6, "w")
card("sinterklaaskaart-schoen", "Sinterklaaskaart: schoen met wortel", front_schoen, "Fijne pakjesavond!", "feest", "4-6", ["Schrijf binnenin een gedichtje of een lief berichtje."], holiday="sinterklaas")
def front_boom(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 26, "Fijne kerst!", 18)
    for i, (yy, ww) in enumerate([(y0 + 40, 22), (y0 + 62, 34), (y0 + 84, 46)]):
        sh.poly_r([(100, yy), (100 + ww, yy + 26), (100 - ww, yy + 26)], "g")
    sh.rect_r(94, y0 + 110, 12, 10, "w"); sh.poly_r(star_pts(100, y0 + 38, 8, 3.5), "y")
    for x, y, c in [(92, y0 + 58, "r"), (110, y0 + 80, "b"), (84, y0 + 96, "y"), (118, y0 + 102, "r"), (100, y0 + 88, "p")]: sh.circle_r(x, y, 3.4, c)
card("kerstkaart-kerstboom", "Kerstkaart met kerstboom", front_boom, "Fijne feestdagen!", "feest", "4-6", ["Schrijf binnenin een kerstwens."], holiday="kerst")
def front_vuurwerk(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 26, "Gelukkig nieuwjaar!", 14)
    for cx, cy, r, c in [(60, y0 + 70, 26, "rmy"), (130, y0 + 62, 22, "btn"), (106, y0 + 100, 14, "yo")]:
        n = 12
        for k in range(n):
            a = math.radians(k * 360 / n)
            sh.seg(cx + r * .3 * math.cos(a), cy + r * .3 * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a), "l", "stroke-width:1.4")
            sh.circle_r(cx + r * 1.1 * math.cos(a), cy + r * 1.1 * math.sin(a), 2.4, c[k % len(c)])
        sh.circle_r(cx, cy, r * .22, c[0])
card("nieuwjaarskaart-vuurwerk", "Nieuwjaarskaart met vuurwerk", front_vuurwerk, "Het beste voor het nieuwe jaar!", "feest", "6-9", ["Schrijf binnenin je goede voornemens of een wens."], holiday="oudnieuw")

# ---------- kerstballen ----------
def kerstballen():
    sh = Sheet()
    title(sh, "Kerstballen", 16)
    pats = ["streep", "stip", "ster", "zigzag", "hart", "sneeuw"]
    for i in range(6):
        col, row = i % 2, i // 2
        cx, cy, r = 56 + col * 88, 72 + row * 72, 28
        sh.rect_r(cx - 6, cy - r - 8, 12, 8, "z")
        sh.circle_line(cx, cy - r - 11, 3, "cut")
        sh.circle_r(cx, cy, r, "rgbyrp"[i])
        sh.raw(f'<circle class="cut" cx="{cx}" cy="{cy}" r="{r + 4}"/>')
        p = pats[i]
        if p == "streep":
            for dy in (-10, 0, 10): sh.line(f"M{cx - math.sqrt(r * r - dy * dy)} {cy + dy}H{cx + math.sqrt(r * r - dy * dy)}")
        elif p == "stip":
            for dx, dy in [(-12, -8), (10, -10), (0, 4), (-10, 14), (12, 12)]: sh.circle_r(cx + dx, cy + dy, 4, "-")
        elif p == "ster": sh.poly_r(star_pts(cx, cy, 16, 7), "y")
        elif p == "zigzag": sh.line(f"M{cx - r + 2} {cy}" + "".join(f"L{cx - r + 2 + (k + 1) * 9} {cy + (-7 if k % 2 == 0 else 7)}" for k in range(6)))
        elif p == "hart": sh.region(f"M{cx} {cy + 13}C{cx - 19} {cy} {cx - 13} {cy - 15} {cx} {cy - 6}C{cx + 13} {cy - 15} {cx + 19} {cy} {cx} {cy + 13}Z", "k")
        else:
            for k in range(6):
                a = math.radians(k * 60); sh.seg(cx, cy, cx + 15 * math.cos(a), cy + 15 * math.sin(a))
    sh.legend(["cut"], 274)
    write(OUT, "kerstballen-knippen", sh, {"category": "feest", "holiday": "kerst", "age": "4-6", "kind": "knipplaat", "difficulty": 1, "minutes": 25, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "touw"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Kerstballen om op te hangen", "steps": [
            "Kleur de kerstballen in, elk met een eigen patroon.",
            "Knip ze uit langs de streepjeslijn rond de bal en het ophangoogje.",
            "Prik een gaatje in het rondje bovenaan en hang de bal met een touwtje in de boom of voor het raam."]}}})
# kerstballen(): niet opgenomen, lijkt te veel op de bestaande plaat "kersthangers"

# ---------- sneeuwvlok vouwen en knippen ----------
def sneeuwvlok():
    sh = Sheet()
    title(sh, "Sneeuwvlok knippen", 16)
    x0, y0, s = 20, 34, 160
    sh.rect_line(x0, y0, s, s, "cut")
    cx, cy = x0 + s / 2, y0 + s / 2
    sh.line(f"M{x0} {y0}L{x0 + s} {y0 + s}M{x0 + s} {y0}L{x0} {y0 + s}M{cx} {y0}V{y0 + s}M{x0} {cy}H{x0 + s}", "fold")
    # het bovenste achtste (driehoek midden-boven-rechts) met knipvormen
    wedge = [(cx, cy), (cx, y0), (x0 + s, y0)]
    sh.poly_r(wedge, "b")
    # knipvormen: inkepingen op de vouwen (geven gaatjes) en op de buitenrand (geven een kartelrand)
    sh.line(f"M{cx} {y0 + 52}L{cx + 14} {y0 + 44}L{cx} {y0 + 36}", "cut")
    sh.line(f"M{cx} {y0 + 24}Q{cx + 12} {y0 + 18} {cx} {y0 + 10}", "cut")
    sh.line(f"M{cx + 20} {y0}L{cx + 28} {y0 + 14}L{cx + 38} {y0}", "cut")
    sh.line(f"M{cx + 50} {y0}Q{cx + 57} {y0 + 12} {cx + 64} {y0}", "cut")
    sh.line(f"M{cx + 20} {cy - 20}L{cx + 30} {cy - 38}L{cx + 40} {cy - 40}", "cut")
    sh.line(f"M{cx + 46} {cy - 46}L{cx + 60} {cy - 66}L{cx + 64} {cy - 64}", "cut")
    sh.line(f"M{x0 + s} {y0 + 14}L{x0 + s - 14} {y0}", "cut")
    sh.text(100, y0 + s + 14, "Knip langs de streepjes in het blauwe stuk, door alle lagen heen.", 6)
    sh.legend(["cut", "fold"], 274)
    write(OUT, "sneeuwvlok-knippen", sh, {"category": "natuur", "holiday": "kerst", "age": "6-9", "kind": "vouwblad", "difficulty": 2, "minutes": 20, "adultHelp": True,
        "materials": [SCHAAR],
        "i18n": {"nl": {"name": "Sneeuwvlok vouwen en knippen", "printNote": "Gewoon printpapier knipt het makkelijkst; stevig papier is te dik als het gevouwen is.", "steps": [
            "Knip het vierkant uit langs de buitenste streepjeslijn.",
            "Vouw het dubbel van boven naar beneden, dan van rechts naar links, en dan schuin, steeds zo dat het blauwe stuk bovenop blijft liggen.",
            "Nu heb je een klein driehoekje met het blauwe stuk bovenop. Knip langs de streepjes in het blauw, door alle lagen heen. Knip niet helemaal door de vouwen.",
            "Vouw voorzichtig open: een sneeuwvlok! Plak hem op het raam of hang hem op."]}}})
# sneeuwvlok(): niet opgenomen, er is al een betere "sneeuwvlok-knippen" met zes armen

# ---------- zeeslag ----------
def zeeslag():
    sh = Sheet()
    title(sh, "Zeeslag", 16)
    def grid(x0, y0, label):
        s = 9.5
        sh.text(x0 + 4 * s + s, y0 - 6, label, 7)
        for i in range(8):
            sh.text(x0 + s * (i + 1) + s / 2, y0 + 7, "ABCDEFGH"[i], 6)
            sh.text(x0 + s / 2, y0 + s * (i + 1) + 7, str(i + 1), 6)
        for i in range(9):
            sh.seg(x0 + s, y0 + s * (i + 1), x0 + s * 9, y0 + s * (i + 1), "l", "stroke-width:.7")
            sh.seg(x0 + s * (i + 1), y0 + s, x0 + s * (i + 1), y0 + s * 9, "l", "stroke-width:.7")
    grid(6, 40, "Mijn vloot"); grid(104, 40, "Vloot van de ander")
    grid(6, 150, "Mijn vloot"); grid(104, 150, "Vloot van de ander")
    sh.text(100, 252, "Vloot: 1 schip van 4 · 2 schepen van 3 · 3 schepen van 2 hokjes", 6)
    sh.text(100, 262, "Bovenste rij: spel 1 · onderste rij: spel 2", 6)
    write(OUT, "zeeslag", sh, {"category": "zee", "age": "6-9", "kind": "spel", "difficulty": 2, "minutes": 30, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": "Zeeslag (2 spelletjes)", "printNote": "Print het vel twee keer: één voor elke speler.", "steps": [
            "Teken in 'Mijn vloot' je schepen, recht of van boven naar beneden, niet schuin. Laat het de ander niet zien!",
            "Noem om de beurt een vakje, bijvoorbeeld C5. De ander zegt 'mis', 'raak' of 'gezonken'.",
            "Zet in 'Vloot van de ander' een stip bij mis en een kruisje bij raak.",
            "Wie als eerste alle schepen van de ander tot zinken brengt, wint."]}}})
zeeslag()

# ---------- woord raden met een sneeuwpop ----------
def raden():
    sh = Sheet()
    title(sh, "Woord raden met de sneeuwpop", 15)
    for i in range(3):
        y = 40 + i * 76
        sh.rect_line(14, y, 172, 70, "l", 4, "stroke-width:.8")
        bx = 46
        for k, (cy, r) in enumerate([(y + 54, 12), (y + 36, 9), (y + 22, 6.5)]):
            sh.raw(f'<circle class="guide" cx="{bx}" cy="{cy}" r="{r}"/>')
        sh.line(f"M{bx - 7} {y + 15}H{bx + 7}M{bx - 4} {y + 15}V{y + 8}H{bx + 4}V{y + 15}", "guide")
        sh.line(f"M{bx - 9} {y + 36}L{bx - 20} {y + 28}M{bx + 9} {y + 36}L{bx + 20} {y + 28}", "guide")
        for k in range(7): sh.seg(84 + k * 13, y + 40, 94 + k * 13, y + 40, "l", "stroke-width:1.2")
        sh.text(84, y + 58, "Fout geraden: ........................", 6, "start")
    sh.text(100, 270, "Bij elke foute letter teken je één stukje van de sneeuwpop over.", 6)
    write(OUT, "woord-raden-sneeuwpop", sh, {"category": "sport", "age": "6-9", "kind": "spel", "difficulty": 1, "minutes": 15, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": "Woord raden met de sneeuwpop (3 spelletjes)", "steps": [
            "Eén speler bedenkt een woord en zet voor elke letter een streepje (gebruik er zoveel als nodig).",
            "De ander noemt letters. Zit de letter in het woord? Schrijf hem op het goede streepje.",
            "Zit hij er niet in? Schrijf hem bij 'fout geraden' en trek één stukje van de sneeuwpop over.",
            "Raad het woord voordat de sneeuwpop af is (hoed, hoofd, lijf, buik, armen): dan win je!"]}}})
raden()
print("batch 2 klaar")
