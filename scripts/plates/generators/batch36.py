"""Batch 36: knip-en-plakbladen (knipvel met plakvel op blad 2)."""
import math, random
from lib_gen import *
from shapes import heart_path, star_path, leaf_path, fish_path, cloud_path

MAT = [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}]
def knipvel(slug, name, title_knip, draw_knip, title_plak, draw_plak, cat, age, diff, steps, answer=None):
    sh = Sheet(); title(sh, title_knip, 16); draw_knip(sh); sh.legend(["cut"], 276)
    pl = Sheet(); title(pl, title_plak, 16); draw_plak(pl)
    pages = [("extra", title_plak, pl)]
    if answer: pages.append(("antwoorden", "Zo kan het", answer))
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": 20, "materials": MAT,
        "i18n": {"nl": {"name": name, "steps": steps}}}, pages)
def cutbox(sh, x, y, w, h): sh.rect_line(x, y, w, h, "cut", 4)

# ---------- fruitgezicht ----------
def fruit_knip(sh):
    sh.text(100, 27, "Kleur het fruit, knip het uit en maak een grappig gezicht.", 6.5)
    items = [lambda x, y: (sh.circle_r(x, y, 12, "o")), lambda x, y: (sh.circle_r(x, y, 12, "o")),
             lambda x, y: sh.region(f"M{x - 22} {y - 4}Q{x} {y + 18} {x + 22} {y - 4}Q{x} {y + 6} {x - 22} {y - 4}Z", "y"),
             lambda x, y: (sh.circle_r(x, y, 9, "r"), sh.line(f"M{x} {y - 9}Q{x + 3} {y - 15} {x + 6} {y - 16}")),
             lambda x, y: (sh.circle_r(x - 6, y, 7, "p"), sh.circle_r(x + 6, y, 7, "p"), sh.circle_r(x, y - 9, 7, "p")),
             lambda x, y: sh.region(f"M{x - 20} {y}Q{x - 10} {y - 14} {x} {y}Q{x + 10} {y - 14} {x + 20} {y}Q{x} {y + 8} {x - 20} {y}Z", "l"),
             lambda x, y: (sh.region(leaf_path(x - 8, y, 6, 10), "g"), sh.region(leaf_path(x + 8, y, 6, 10), "g")),
             lambda x, y: sh.region(f"M{x - 8} {y - 12}C{x + 14} {y - 12} {x + 14} {y + 12} {x - 8} {y + 12}Q{x + 4} {y} {x - 8} {y - 12}Z", "y")]
    labels = ["sinaasappel", "sinaasappel", "banaan", "kers", "druiven", "kiwi", "blaadjes", "citroen"]
    for i, (f_, lab) in enumerate(zip(items, labels)):
        x, y = 40 + (i % 3) * 60, 60 + (i // 3) * 64
        cutbox(sh, x - 27, y - 24, 54, 52); f_(x, y); sh.text(x, y + 23, lab, 5)
def fruit_plak(sh):
    sh.text(100, 27, "Plak het fruit op het bord: ogen, neus, mond en haar!", 6.5)
    sh.circle_r(100, 150, 84, "-"); sh.circle_r(100, 150, 70, "-")
    sh.region(f"M150 250L160 150Q164 140 168 150L174 250Z", "z") if False else None
knipvel("fruitgezicht-plakken", "Knippen en plakken: een gezicht van fruit", "Fruitgezicht: knipvel", fruit_knip, "Plak je fruitgezicht", fruit_plak, "eten", "4-6", 1,
        ["Kleur het fruit in en knip de kaartjes uit, of knip precies langs het fruit.", "Leg het fruit op het bord op blad 2: wat worden de ogen, de neus, de mond en het haar?", "Ben je tevreden? Plak alles vast. Smakelijk!"])

# ---------- boeket ----------
def boeket_knip(sh):
    sh.text(100, 27, "Kleur de bloemen, knip ze uit en maak een boeket.", 6.5)
    for i in range(9):
        x, y = 36 + (i % 3) * 64, 58 + (i // 3) * 66
        cutbox(sh, x - 28, y - 22, 56, 60)
        kind = i % 3; c = "mrybpo"[i % 6]
        sh.line(f"M{x} {y + 6}V{y + 34}")
        if kind == 0:
            for k in range(6): a = math.radians(k * 60); sh.circle_r(x + 7 * math.cos(a), y + 7 * math.sin(a), 5.5, c)
            sh.circle_r(x, y, 4, "y")
        elif kind == 1: sh.region(f"M{x - 9} {y + 6}V{y - 8}L{x - 4} {y - 2}L{x} {y - 10}L{x + 4} {y - 2}L{x + 9} {y - 8}V{y + 6}Q{x} {y + 12} {x - 9} {y + 6}Z", c)
        else:
            for k in range(12): a = math.radians(k * 30); sh.region(leaf_path(x + 9 * math.cos(a), y + 9 * math.sin(a), 2.6, 5), c) if False else sh.circle_r(x + 9 * math.cos(a), y + 9 * math.sin(a), 3.2, c)
            sh.circle_r(x, y, 6, "w")
        sh.region(leaf_path(x + 7, y + 22, 4, 7), "g")
def boeket_plak(sh):
    sh.text(100, 27, "Plak de bloemen boven de vaas. Voor wie is je boeket?", 6.5)
    sh.region("M60 170H140L128 262H72Z", "b"); sh.rect_r(56, 160, 88, 12, "n", 3)
    sh.text(100, 274, "Voor: .........................................", 7)
knipvel("bloemenboeket-plakken", "Knippen en plakken: een bloemenboeket", "Bloemen: knipvel", boeket_knip, "Mijn boeket", boeket_plak, "natuur", "4-6", 1,
        ["Kleur de bloemen in vrolijke kleuren.", "Knip ze uit langs de streepjeslijn.", "Plak ze met de steeltjes naar beneden boven de vaas op blad 2. Een mooi cadeau voor Moederdag, Vaderdag of een verjaardag!"])

# ---------- getallentrein ----------
def trein_knip(sh):
    sh.text(100, 27, "Knip de wagons uit en zet ze op volgorde van 1 tot 10.", 6.5)
    r = random.Random(9); nums = list(range(1, 11)); r.shuffle(nums)
    for i, n in enumerate(nums):
        x, y = 30 + (i % 4) * 46, 50 + (i // 4) * 50
        cutbox(sh, x - 20, y - 18, 40, 40)
        sh.rect_r(x - 15, y - 12, 30, 22, "rybgo"[n % 5], 3); sh.circle_r(x - 8, y + 14, 4, "x"); sh.circle_r(x + 8, y + 14, 4, "x")
        sh.text(x, y + 4, str(n), 12)
def trein_plak(sh):
    sh.text(100, 27, "Plak de wagons achter de locomotief: 1, 2, 3 … 10.", 6.5)
    sh.rect_r(10, 50, 30, 26, "r", 3); sh.rect_r(20, 38, 10, 12, "x"); sh.circle_r(18, 80, 5, "x"); sh.circle_r(32, 80, 5, "x")
    for i in range(10):
        if i < 4: x, y = 44 + i * 38, 46
        else: x, y = 10 + (i - 4) * 31, 110
        w = 34 if i < 4 else 28
        sh.raw(f'<rect class="ans" x="{x}" y="{y}" width="{w}" height="34" rx="3"/>')
    sh.seg(0, 86, 200, 86, "l", "stroke-width:1.4"); sh.seg(0, 150, 200, 150, "l", "stroke-width:1.4")
knipvel("getallentrein-plakken", "Knippen en plakken: de getallentrein", "Getallentrein: knipvel", trein_knip, "Plak de trein op volgorde", trein_plak, "leren", "4-6", 1,
        ["Kleur de wagons en knip ze uit.", "Zoek wagon 1 en plak hem achter de locomotief. Dan 2, dan 3 … tot 10.", "Lees de getallen hardop als je klaar bent."])

# ---------- groot middel klein ----------
def beer(sh, x, y, s, c="w"):
    sh.circle_r(x, y + 14 * s, 13 * s, c); sh.circle_r(x, y - 4 * s, 10 * s, c); sh.circle_r(x - 8 * s, y - 12 * s, 4 * s, c); sh.circle_r(x + 8 * s, y - 12 * s, 4 * s, c)
    sh.dot(x - 3.5 * s, y - 5 * s, 1.2 * s); sh.dot(x + 3.5 * s, y - 5 * s, 1.2 * s); sh.ellipse_r(x, y + s, 2.5 * s, 2 * s, "x")
def gmk_knip(sh):
    sh.text(100, 27, "Knip de beren, de stoelen en de kommen uit.", 6.5)
    for row, s in enumerate((1.15, .85, .55)):
        y = 60 + row * 70
        cutbox(sh, 12, y - 32, 56, 64); beer(sh, 40, y - 4, s)
        cutbox(sh, 72, y - 32, 56, 64); sh.rect_r(100 - 14 * s, y - 24 * s, 5 * s, 20 * s, "r"); sh.rect_r(100 - 14 * s, y - 6 * s, 28 * s, 6 * s, "r"); sh.rect_r(100 - 13 * s, y, 4 * s, 22 * s, "r"); sh.rect_r(100 + 9 * s, y, 4 * s, 22 * s, "r")
        cutbox(sh, 132, y - 32, 56, 64); sh.region(f"M{160 - 14 * s} {y}H{160 + 14 * s}Q{160 + 12 * s} {y + 14 * s} {160} {y + 14 * s}Q{160 - 12 * s} {y + 14 * s} {160 - 14 * s} {y}Z", "b")
def gmk_plak(sh):
    sh.text(100, 27, "Plak de grote spullen bij de grote beer, enzovoort.", 6.5)
    for i, (lab, h) in enumerate((("groot", 70), ("middel", 60), ("klein", 50))):
        y = 40 + i * 76
        sh.rect_line(10, y, 180, h + 6, "l", 4, "stroke-width:.8"); sh.text(14, y + 9, lab, 7, "start")
knipvel("groot-middel-klein-beren", "Knippen en plakken: groot, middel en klein", "Groot, middel, klein: knipvel", gmk_knip, "Wie hoort waar?", gmk_plak, "vormen", "2-4", 1,
        ["Kleur de beren, stoelen en kommen in. Een volwassene helpt met knippen.", "Zoek de grootste beer, de grootste stoel en de grootste kom en plak ze bij 'groot'.", "Doe hetzelfde met middel en klein."])
