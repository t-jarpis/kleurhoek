import math, random
from lib_gen import *

# ---------- knipoefenbladen ----------
def knipoefen(slug, name, kind, age, diff):
    sh = Sheet()
    title(sh, cap(name.split(": ", 1)[-1]), 16)
    sh.text(100, 27, "Knip precies over de streepjeslijn. Begin bij de schaar.", 6.5)
    rows = 6 if kind != "spiraal" else 1
    for i in range(rows):
        y = 48 + i * 36
        if kind == "recht": d = f"M24 {y}H184"
        elif kind == "golf": d = f"M24 {y}" + "".join(f"Q{24 + k * 40 + 20} {y + (-12 if k % 2 == 0 else 12)} {24 + (k + 1) * 40} {y}" for k in range(4))
        elif kind == "zigzag": d = f"M24 {y}" + "".join(f"L{24 + (k + 1) * 16} {y + (-9 if k % 2 == 0 else 9)}" for k in range(10)).replace(f"L184 {y + 9}", f"L184 {y}")
        elif kind == "trap": d = f"M24 {y}" + "".join(f"H{24 + (k + 1) * 32}V{y + (-10 if k % 2 == 0 else 0)}" for k in range(5))
        if kind != "spiraal":
            sh.line(d, "cut")
            # schaartje bij het begin
            sh.raw(f'<g transform="translate(12 {y}) scale(.32)"><circle class="l" cx="-8" cy="-6" r="6" fill="none"/><circle class="l" cx="-8" cy="6" r="6" fill="none"/><path class="l" d="M-3 -4L20 4M-3 4L20 -4"/></g>')
    if kind == "spiraal":
        pts = []
        for k in range(0, 900):
            t = k / 900 * 3.2 * 2 * math.pi
            r = 92 - t * 4.4
            pts.append((100 + r * math.cos(t), 148 + r * math.sin(t)))
        sh.line("M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts[::6]), "cut")
        sh.raw('<g transform="translate(196 148) scale(.32) rotate(180)"><circle class="l" cx="-8" cy="-6" r="6" fill="none"/><circle class="l" cx="-8" cy="6" r="6" fill="none"/><path class="l" d="M-3 -4L20 4M-3 4L20 -4"/></g>')
        sh.circle_r(100, 148, 8, "y")
        sh.text(100, 270, "Knip van buiten naar binnen. Hang je slang op aan een draadje!", 6)
    write(OUT, slug, sh, {"category": "vormen", "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": 10, "materials": [SCHAAR],
        "i18n": {"nl": {"name": name, "steps": [
            "Houd de schaar met je duim boven en je vingers onder.",
            "Knip langzaam over de streepjeslijn, van links naar rechts. Draai het papier, niet de schaar.",
            "Gaat het goed? Probeer de volgende lijn een beetje sneller."]}}})
knipoefen("knipoefenen-rechte-lijnen", "Knippen oefenen: rechte lijnen", "recht", "2-4", 1)
knipoefen("knipoefenen-golven", "Knippen oefenen: golven", "golf", "4-6", 1)
knipoefen("knipoefenen-zigzag", "Knippen oefenen: zigzag", "zigzag", "4-6", 2)
knipoefen("knipoefenen-trapjes", "Knippen oefenen: trapjes", "trap", "4-6", 2)
knipoefen("knipoefenen-spiraal", "Knippen oefenen: spiraal-slang", "spiraal", "6-9", 3)

# ---------- knip-en-leg-puzzels (stroken op volgorde) ----------
def strip_puzzle(slug, name, draw, cat, age, n=6):
    sh = Sheet()
    title(sh, cap(name.split(": ", 1)[-1]), 16)
    x0, y0, w, h = 20, 36, 160, 200
    draw(sh, x0, y0, w, h)
    sw = w / n
    for k in range(1, n):
        sh.seg(x0 + k * sw, y0, x0 + k * sw, y0 + h, "cut")
    sh.rect_line(x0, y0, w, h, "cut")
    for k in range(n):
        sh.raw(f'<rect class="ans" x="{f(x0 + k * sw + sw / 2 - 6)}" y="{y0 + h + 6}" width="12" height="11" rx="2"/>')
        sh.text(x0 + k * sw + sw / 2, y0 + h + 14.5, str(k + 1), 8)
    sh.legend(["cut"], 274)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": 2, "minutes": 20,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift", "optional": True}],
        "i18n": {"nl": {"name": name, "steps": [
            "Kleur de tekening helemaal in.",
            "Knip de rand en daarna de stroken los langs de streepjeslijnen (de nummers onderaan blijven aan de stroken vast als je onder de tekening doorknipt).",
            "Hussel de stroken door elkaar en leg de tekening weer in elkaar. Kijk op de nummers als het lastig is.",
            "Wil je hem bewaren? Plak de stroken in de goede volgorde op een vel papier."]}}})
def vis_scene(sh, x0, y0, w, h):
    sh.rect_r(x0, y0, w, h, "b")
    sh.region(f"M{x0 + 20} {y0 + 110}Q{x0 + 70} {y0 + 50} {x0 + 120} {y0 + 110}Q{x0 + 70} {y0 + 170} {x0 + 20} {y0 + 110}Z", "o")
    sh.poly_r([(x0 + 118, y0 + 110), (x0 + 150, y0 + 84), (x0 + 150, y0 + 136)], "y")
    sh.circle_r(x0 + 44, y0 + 102, 7, "-"); sh.dot(x0 + 44, y0 + 102, 3)
    for k in range(3): sh.line(f"M{x0 + 66 + k * 14} {y0 + 92}Q{x0 + 74 + k * 14} {y0 + 110} {x0 + 66 + k * 14} {y0 + 128}")
    for cx, cy, r in [(x0 + 22, y0 + 60, 6), (x0 + 30, y0 + 40, 4), (x0 + 36, y0 + 24, 3)]: sh.circle_r(cx, cy, r, "t")
    sh.region(f"M{x0} {y0 + h}V{y0 + 176}Q{x0 + 40} {y0 + 166} {x0 + 80} {y0 + 176}T{x0 + w} {y0 + 176}V{y0 + h}Z", "y")
    for sx in (x0 + 128, x0 + 146): sh.region(f"M{sx} {y0 + 178}C{sx - 10} {y0 + 150} {sx + 10} {y0 + 140} {sx} {y0 + 112}C{sx + 14} {y0 + 140} {sx + 6} {y0 + 160} {sx + 8} {y0 + 178}Z", "g")
strip_puzzle("knippuzzel-vis", "Knippuzzel: vis in de zee", vis_scene, "zee", "4-6")
def raket_scene(sh, x0, y0, w, h):
    sh.rect_r(x0, y0, w, h, "n")
    for x, y in [(x0 + 20, y0 + 22), (x0 + 140, y0 + 30), (x0 + 14, y0 + 116), (x0 + 130, y0 + 170), (x0 + 78, y0 + 14)]: sh.poly_r(star_pts(x, y, 7, 3), "y")
    sh.circle_r(x0 + 128, y0 + 80, 18, "p"); sh.region(f"M{x0 + 104} {y0 + 84}Q{x0 + 128} {y0 + 70} {x0 + 152} {y0 + 76}", "-") if False else sh.line(f"M{x0 + 106} {y0 + 86}Q{x0 + 128} {y0 + 72} {x0 + 150} {y0 + 76}")
    cx = x0 + 62
    sh.region(f"M{cx - 16} {y0 + 150}V{y0 + 80}Q{cx} {y0 + 36} {cx + 16} {y0 + 80}V{y0 + 150}Z", "r")
    sh.circle_r(cx, y0 + 92, 8, "b")
    sh.poly_r([(cx - 16, y0 + 124), (cx - 34, y0 + 158), (cx - 16, y0 + 150)], "o"); sh.poly_r([(cx + 16, y0 + 124), (cx + 34, y0 + 158), (cx + 16, y0 + 150)], "o")
    sh.region(f"M{cx - 10} {y0 + 150}Q{cx - 6} {y0 + 176} {cx} {y0 + 186}Q{cx + 6} {y0 + 176} {cx + 10} {y0 + 150}Z", "y")
strip_puzzle("knippuzzel-raket", "Knippuzzel: raket in de ruimte", raket_scene, "ruimte", "4-6")

# ---------- vingerpoppetjes ----------
def vingerpoppen():
    sh = Sheet()
    title(sh, "Vingerpoppetjes", 16)
    heads = ["kat", "hond", "uil", "kikker", "beer", "muis"]
    for i, kind in enumerate(heads):
        col, row = i % 3, i // 3
        cx, cy = 38 + col * 62, 74 + row * 112
        # ring-strook onder het kopje
        sh.rect_r(cx - 28, cy + 24, 56, 14, "-")
        sh.raw(f'<rect class="glue" x="{cx + 18}" y="{cy + 25}" width="9" height="12"/>')
        c = {"kat": "o", "hond": "w", "uil": "w", "kikker": "g", "beer": "w", "muis": "z"}[kind]
        if kind == "kat":
            sh.poly_r([(cx - 18, cy - 10), (cx - 16, cy - 30), (cx - 4, cy - 18)], c); sh.poly_r([(cx + 18, cy - 10), (cx + 16, cy - 30), (cx + 4, cy - 18)], c)
        if kind in ("beer", "muis"):
            sh.circle_r(cx - 15, cy - 16, 8, c); sh.circle_r(cx + 15, cy - 16, 8, c)
        if kind == "hond":
            sh.ellipse_r(cx - 19, cy, 5, 12, "w"); sh.ellipse_r(cx + 19, cy, 5, 12, "w")
        if kind == "kikker":
            sh.circle_r(cx - 10, cy - 18, 7, c); sh.circle_r(cx + 10, cy - 18, 7, c)
        if kind == "uil":
            sh.poly_r([(cx - 18, cy - 12), (cx - 20, cy - 28), (cx - 8, cy - 18)], c); sh.poly_r([(cx + 18, cy - 12), (cx + 20, cy - 28), (cx + 8, cy - 18)], c)
        sh.circle_r(cx, cy, 20, c)
        if kind == "uil":
            for ex in (cx - 8, cx + 8): sh.circle_r(ex, cy - 3, 6.5, "y"); sh.dot(ex, cy - 3, 2.4)
            sh.poly_r([(cx - 3, cy + 5), (cx + 3, cy + 5), (cx, cy + 10)], "o")
        elif kind == "kikker":
            sh.dot(cx - 10, cy - 18, 2.6); sh.dot(cx + 10, cy - 18, 2.6); sh.line(f"M{cx - 10} {cy + 6}Q{cx} {cy + 13} {cx + 10} {cy + 6}")
        else:
            sh.dot(cx - 7, cy - 4, 2); sh.dot(cx + 7, cy - 4, 2)
            sh.ellipse_r(cx, cy + 5, 3.5, 2.6, "x" if kind != "muis" else "k")
            sh.line(f"M{cx} {cy + 7.5}V{cy + 10}M{cx - 5} {cy + 12}Q{cx} {cy + 14} {cx + 5} {cy + 12}")
            if kind in ("kat", "muis"): sh.line(f"M{cx - 6} {cy + 6}H{cx - 18}M{cx + 6} {cy + 6}H{cx + 18}")
        sh.line(f"M{cx - 28} {cy + 38}H{cx + 28}V{cy + 24}H{cx + 27}V{cy - 12}A27 27 0 0 0 {cx - 27} {cy - 12}V{cy + 24}H{cx - 28}Z", "cut")
    sh.text(100, 258, "Knip het kopje en de strook uit (ze blijven aan elkaar vast).", 6)
    sh.legend(["cut", "glue"], 274)
    write(OUT, "vingerpoppetjes-dieren", sh, {"category": "dieren", "age": "4-6", "kind": "knipplaat", "difficulty": 2, "minutes": 25,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Vingerpoppetjes: zes dieren", "steps": [
            "Kleur de dierenkopjes in.",
            "Knip elk kopje uit samen met de strook eronder (knip niet tussen kopje en strook door).",
            "Leg de strook om je vinger en plak het grijze stukje vast, zodat er een ringetje ontstaat.",
            "Steek het poppetje op je vinger en speel een toneelstukje!"]}}})
vingerpoppen()

# ---------- kaarten ----------
def front_uitnodiging(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Kom je ook?", 16)
    for i, (k, v) in enumerate([("Feestje van:", ""), ("Datum:", ""), ("Tijd:", ""), ("Adres:", "")]):
        sh.text(30, y0 + 46 + i * 16, k, 7, "start"); sh.seg(78, y0 + 46 + i * 16, 170, y0 + 46 + i * 16, "guide")
    for x, c in [(26, "r"), (174, "b")]:
        sh.region(f"M{x} {y0 + 40}C{x - 10} {y0 + 32} {x - 9} {y0 + 16} {x} {y0 + 16}C{x + 9} {y0 + 16} {x + 10} {y0 + 32} {x} {y0 + 40}Z", c)
    sh.raw(f'<rect class="r" x="34" y="{f(y0 + 112)}" width="132" height="8" rx="2"/>', "y")
card("uitnodiging-kinderfeestje", "Uitnodiging voor een kinderfeestje", front_uitnodiging, "Tot dan!", "feest", "6-9",
     ["Vul in voor wie het feestje is, wanneer en waar.", "Maak er een paar en geef ze aan je vriendjes en vriendinnetjes."], holiday="verjaardag")
def front_vaderdag(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 26, "Liefste papa!", 16)
    cx, cy = 100, y0 + 80
    sh.poly_r([(cx - 40, cy - 30), (cx - 14, cy - 30), (cx, cy - 18), (cx + 14, cy - 30), (cx + 40, cy - 30), (cx + 40, cy + 34), (cx - 40, cy + 34)], "b")
    sh.poly_r([(cx - 7, cy - 22), (cx + 7, cy - 22), (cx + 4, cy - 14), (cx - 4, cy - 14)], "r")
    sh.poly_r([(cx - 4, cy - 14), (cx + 4, cy - 14), (cx + 8, cy + 24), (cx, cy + 32), (cx - 8, cy + 24)], "r")
    for yy in (cy - 4, cy + 10): sh.dot(cx + 22, yy, 1.6)
card("vaderdagkaart-stropdas", "Vaderdagkaart met stropdas", front_vaderdag, "Fijne vaderdag!", "feest", "4-6", ["Schrijf binnenin waarom jouw papa (of opa) de liefste is."], holiday="vaderdag")
def front_beter(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 26, "Word snel beter!", 15)
    cx, cy = 100, y0 + 76
    sh.circle_r(cx, cy, 28, "y")
    for k in range(12):
        a = math.radians(k * 30); sh.seg(cx + 33 * math.cos(a), cy + 33 * math.sin(a), cx + 42 * math.cos(a), cy + 42 * math.sin(a), "l", "stroke-width:1.6")
    sh.dot(cx - 9, cy - 6, 2.4); sh.dot(cx + 9, cy - 6, 2.4); sh.line(f"M{cx - 12} {cy + 8}Q{cx} {cy + 18} {cx + 12} {cy + 8}")
    sh.circle_r(cx - 16, cy + 6, 4, "k"); sh.circle_r(cx + 16, cy + 6, 4, "k")
card("beterschapskaart-zon", "Beterschapskaart met zonnetje", front_beter, "Beterschap!", "feest", "4-6", ["Schrijf binnenin een lief berichtje en breng de kaart langs."])
def front_valentijn(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Voor jou", 18)
    for cx, cy, k, c in [(100, y0 + 76, 3.2, "r"), (52, y0 + 56, 1.4, "k"), (150, y0 + 60, 1.6, "m"), (60, y0 + 104, 1.1, "m"), (146, y0 + 106, 1.2, "k")]:
        sh.region(f"M{cx} {cy + 9*k}C{cx - 13*k} {cy} {cx - 9*k} {cy - 10*k} {cx} {cy - 4*k}C{cx + 9*k} {cy - 10*k} {cx + 13*k} {cy} {cx} {cy + 9*k}Z", c)
card("valentijnskaart-hartjes", "Valentijnskaart met hartjes", front_valentijn, "Je bent lief!", "feest", "4-6", ["Schrijf binnenin voor wie je kaart is (of houd het geheim)."], holiday="valentijn")
def front_pasen(sh, x0, y0, w, h):
    outline_text(sh, 100, y0 + 24, "Vrolijk Pasen!", 16)
    for i, (cx, c) in enumerate([(62, "k"), (100, "y"), (138, "b")]):
        cy = y0 + 82 + (i % 2) * 8
        sh.ellipse_r(cx, cy, 16, 22, c)
        sh.line(f"M{cx - 15} {cy - 4}" + "".join(f"L{cx - 15 + (k + 1) * 5} {cy + (-8 if k % 2 == 0 else -4)}" for k in range(6)))
        sh.line(f"M{cx - 14} {cy + 8}Q{cx} {cy + 2} {cx + 14} {cy + 8}")
    sh.region(f"M30 {y0 + 112}Q100 {y0 + 100} 170 {y0 + 112}V{y0 + 118}H30Z", "l")
card("paaskaart-eieren", "Paaskaart met eieren", front_pasen, "Fijne paasdagen!", "feest", "4-6", ["Schrijf binnenin een paaswens."], holiday="pasen")

# deurhanger
def deurhanger():
    sh = Sheet()
    title(sh, "Deurhanger", 16)
    for i, (txt, c) in enumerate([("Kom binnen!", "g"), ("Niet storen", "r")]):
        x, y, w, h = 18 + i * 86, 30, 78, 230
        sh.line(f"M{x} {y + 10}Q{x} {y} {x + 10} {y}H{x + w - 10}Q{x + w} {y} {x + w} {y + 10}V{y + h - 10}Q{x + w} {y + h} {x + w - 10} {y + h}H{x + 10}Q{x} {y + h} {x} {y + h - 10}Z", "cut")
        sh.raw(f'<circle class="cut" cx="{x + w / 2}" cy="{y + 34}" r="22"/>')
        sh.seg(x + w / 2, y + 56, x + w / 2, y + 70, "cut")
        sh.rect_r(x + 8, y + 80, w - 16, 26, c, 4)
        sh.text(x + w / 2, y + 97, txt, 9)
        for k in range(4): sh.poly_r(star_pts(x + 16 + k * 15, y + 136 + (k % 2) * 12, 6, 2.6), "y")
        sh.text(x + w / 2, y + 180, "Naam:", 7); sh.seg(x + 10, y + 200, x + w - 10, y + 200, "guide")
    sh.legend(["cut"], 274)
    write(OUT, "deurhanger-kom-binnen", sh, {"category": "thuis", "age": "6-9", "kind": "kaart", "difficulty": 2, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "stevig-papier"}],
        "i18n": {"nl": {"name": "Deurhanger: kom binnen of niet storen", "printNote": "Op stevig papier (160 gram) blijft hij mooi hangen.", "steps": [
            "Kleur beide deurhangers in en schrijf je naam erop.",
            "Knip ze uit langs de streepjeslijn, ook het rondje bovenin en het sneetje eronder.",
            "Plak ze met de achterkanten op elkaar: één kant Kom binnen, andere kant Niet storen.",
            "Schuif het rondje over de deurklink en draai hem om wanneer je wilt."]}}})
deurhanger()

# naamlabels
def naamlabels():
    sh = Sheet()
    title(sh, "Naamlabels voor je spullen", 15)
    icons = ["potlood", "boek", "ster", "hart", "bal", "appel", "vis", "bloem"]
    for i in range(8):
        col, row = i % 2, i // 2
        x, y, w, h = 14 + col * 88, 30 + row * 56, 84, 48
        sh.rect_line(x, y, w, h, "cut", 6)
        cx, cy = x + 16, y + 24
        ic = icons[i]
        if ic == "ster": sh.poly_r(star_pts(cx, cy, 10, 4.4), "y")
        elif ic == "hart": sh.region(f"M{cx} {cy + 9}C{cx - 13} {cy} {cx - 9} {cy - 10} {cx} {cy - 4}C{cx + 9} {cy - 10} {cx + 13} {cy} {cx} {cy + 9}Z", "r")
        elif ic == "bal": sh.circle_r(cx, cy, 9, "b"); sh.line(f"M{cx - 9} {cy}H{cx + 9}")
        elif ic == "appel": sh.circle_r(cx, cy + 1, 8.5, "r"); sh.region(f"M{cx} {cy - 7}Q{cx + 4} {cy - 13} {cx + 8} {cy - 11}Q{cx + 4} {cy - 6} {cx} {cy - 7}Z", "g")
        elif ic == "vis": sh.region(f"M{cx - 9} {cy}Q{cx} {cy - 8} {cx + 6} {cy}Q{cx} {cy + 8} {cx - 9} {cy}Z", "o"); sh.poly_r([(cx + 6, cy), (cx + 11, cy - 5), (cx + 11, cy + 5)], "o")
        elif ic == "bloem":
            for k in range(5): a = math.radians(k * 72); sh.circle_r(cx + 5 * math.cos(a), cy + 5 * math.sin(a), 4.2, "m")
            sh.circle_r(cx, cy, 3, "y")
        elif ic == "boek": sh.rect_r(cx - 9, cy - 8, 18, 16, "n"); sh.line(f"M{cx} {cy - 8}V{cy + 8}")
        else: sh.raw(f'<g transform="rotate(-40 {cx} {cy})"><rect class="r" x="{cx - 3}" y="{cy - 11}" width="6" height="17"/><path class="r" d="M{cx - 3} {cy + 6}L{cx} {cy + 12}L{cx + 3} {cy + 6}Z"/></g>', None); sh.codes += ["y", "w"]
        sh.text(x + 32, y + 21, "Dit is van:", 6, "start"); sh.seg(x + 32, y + 36, x + w - 6, y + 36, "guide")
    sh.legend(["cut"], 274)
    write(OUT, "naamlabels-schoolspullen", sh, {"category": "thuis", "age": "6-9", "kind": "kaart", "difficulty": 1, "minutes": 15,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "plakband", "optional": True}],
        "i18n": {"nl": {"name": "Naamlabels voor je schoolspullen", "steps": [
            "Kleur de plaatjes en schrijf je naam op de lijn.",
            "Knip de labels uit langs de streepjeslijn.",
            "Plak ze op je etui, schriften of bakjes (met plakband eroverheen blijven ze mooi)."]}}})
naamlabels()

# boekenleggers dieren
def bookmarks_dieren():
    sh = Sheet()
    title(sh, "Boekenleggers met dieren", 14)
    for i, kind in enumerate(["kat", "uil", "vis", "giraf"]):
        x, y, w, h = 14 + i * 44, 24, 40, 230
        sh.rect_line(x, y, w, h, "cut", 3)
        cx = x + w / 2
        if kind == "kat":
            sh.poly_r([(cx - 14, y + 30), (cx - 12, y + 12), (cx - 3, y + 24)], "o"); sh.poly_r([(cx + 14, y + 30), (cx + 12, y + 12), (cx + 3, y + 24)], "o")
            sh.circle_r(cx, y + 38, 15, "o"); sh.dot(cx - 5, y + 35, 1.8); sh.dot(cx + 5, y + 35, 1.8); sh.ellipse_r(cx, y + 42, 2.4, 1.8, "k")
            sh.region(f"M{cx - 14} {y + 52}H{cx + 14}V{y + 200}Q{cx} {y + 214} {cx - 14} {y + 200}Z", "o")
            for k in range(5): sh.seg(cx - 14, y + 74 + k * 26, cx + 14, y + 78 + k * 26)
        elif kind == "uil":
            sh.ellipse_r(cx, y + 60, 16, 30, "w")
            for ex in (cx - 7, cx + 7): sh.circle_r(ex, y + 46, 6.5, "y"); sh.dot(ex, y + 46, 2.2)
            sh.poly_r([(cx - 3, y + 54), (cx + 3, y + 54), (cx, y + 60)], "o")
            for k in range(6): sh.line(f"M{cx - 10} {y + 100 + k * 18}Q{cx} {y + 108 + k * 18} {cx + 10} {y + 100 + k * 18}")
        elif kind == "vis":
            for k in range(5):
                cy = y + 30 + k * 40; c = "obtyp"[k]
                sh.region(f"M{cx - 13} {cy}Q{cx - 2} {cy - 10} {cx + 8} {cy}Q{cx - 2} {cy + 10} {cx - 13} {cy}Z", c); sh.poly_r([(cx + 8, cy), (cx + 15, cy - 6), (cx + 15, cy + 6)], c); sh.dot(cx - 7, cy - 1, 1.2)
        else:
            sh.region(f"M{cx - 6} {y + 50}V{y + 220}H{cx + 6}V{y + 50}Z", "y")
            sh.ellipse_r(cx + 2, y + 38, 12, 9, "y"); sh.dot(cx + 5, y + 35, 1.6)
            sh.line(f"M{cx - 4} {y + 30}V{y + 22}M{cx + 4} {y + 30}V{y + 22}")
            for k in range(7): sh.circle_r(cx + (-2 if k % 2 else 2), y + 70 + k * 22, 3.6, "w")
    sh.legend(["cut"], 274)
    write(OUT, "boekenleggers-dieren", sh, {"category": "dieren", "age": "4-6", "kind": "kaart", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kleurpotloden"}, SCHAAR, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Boekenleggers met dieren", "steps": [
            "Kleur de kat, de uil, de vissen en de giraf.",
            "Knip de vier boekenleggers uit langs de streepjeslijn.",
            "Leg ze in je leesboek. Leuk om ook cadeau te geven!"]}}})
bookmarks_dieren()

# ---------- tekenlessen ----------
lesson("tekenles-hond", "Tekenles: een hond", [
    [E(50, 32, 20, 17)], ["M31 26C20 26 18 48 26 52C32 52 32 36 31 26", "M69 26C80 26 82 48 74 52C68 52 68 36 69 26"],
    [C(43, 28, 2.5), C(57, 28, 2.5), E(50, 38, 5, 3.5), "M50 41V45M44 46Q50 50 56 46"], [E(52, 72, 26, 16)],
    ["M34 84V96M44 86V96M60 86V96M70 84V96", "M78 66Q90 56 88 46"], ["M40 50H60", C(50, 54, 3)]], [
    "Teken een ovaal hoofd.", "Twee lange flaporen opzij.", "Ogen, een neus en een mond.", "Een liggend lijf onder het hoofd.", "Vier pootjes en een kwispelstaart.", "Een halsband met een penning."], "4-6", 1, "dieren")
lesson("tekenles-schildpad", "Tekenles: een schildpad", [
    ["M20 70Q20 30 50 30Q80 30 80 70Z"], ["M80 64Q92 58 94 66Q92 74 80 70", C(89, 63, 1.5)], ["M28 70V80H38V70", "M62 70V80H72V70", "M20 68L12 72L20 72"],
    ["M50 30V70M30 50H70"], ["M36 40L42 50L36 60M64 40L58 50L64 60"], ["M8 86H94"]], [
    "Teken een halve cirkel als schild.", "Een kopje met een oog.", "Pootjes en een klein staartje.", "Lijnen kruislings over het schild.", "Nog meer lijntjes: het patroon.", "De grond waar hij over loopt."], "4-6", 1, "dieren")
lesson("tekenles-huis", "Tekenles: een huis", [
    ["M20 46H80V92H20Z"], ["M14 48L50 16L86 48"], ["M42 92V66H58V92", C(54, 80, 1.5)], ["M26 54H38V64H26Z", "M62 54H74V64H62Z", "M32 54V64M26 59H38M68 54V64M62 59H74"],
    ["M64 28V14H72V35"], ["M66 10Q70 4 74 8Q78 2 82 6", "M4 92H96"]], [
    "Teken een rechthoek.", "Een puntdak erop.", "Een deur met een knop.", "Twee ramen met een kruis.", "Een schoorsteen.", "Rook en de grond."], "4-6", 1, "thuis")
lesson("tekenles-auto", "Tekenles: een auto", [
    ["M10 62H90V78H10Z"], ["M24 62L34 42H66L76 62"], [C(28, 80, 9), C(72, 80, 9), C(28, 80, 3), C(72, 80, 3)],
    ["M38 46H49V60H34Z", "M53 46H64L70 60H53Z"], ["M84 66H90V70H84Z", "M10 66H14V70H10Z", "M50 64V76"], ["M2 90H98", "M4 84H0"]], [
    "Teken een lange rechthoek.", "Een dak erop met schuine kanten.", "Twee wielen.", "Twee raampjes.", "Lampen voor en achter en een deur.", "De weg."], "4-6", 1, "voertuigen")

# ---------- spiegeltekenen ----------
def spiegel(slug, name, half, cat, age, diff):
    """half: lijnen (in vakjes) voor de linkerkant; de rechterkant tekent het kind zelf."""
    sh = Sheet()
    title(sh, cap(name.split(": ", 1)[-1]), 16)
    sh.text(100, 27, "Teken de andere helft precies gespiegeld. Tel de hokjes!", 6.5)
    n = 12; s = 13; x0 = 100 - n / 2 * s; y0 = 38
    for i in range(n + 1):
        sh.seg(x0 + i * s, y0, x0 + i * s, y0 + n * s, "guide"); sh.seg(x0, y0 + i * s, x0 + n * s, y0 + i * s, "guide")
    sh.seg(100, y0 - 4, 100, y0 + n * s + 4, "l", "stroke-width:1.4;stroke-dasharray:4 3")
    for poly in half:
        sh.line("M" + " L".join(f"{f(x0 + gx * s)} {f(y0 + gy * s)}" for gx, gy in poly), "l", "stroke-width:2")
    ans = Sheet()
    title(ans, "Zo ziet hij er heel uit", 16)
    for i in range(n + 1):
        ans.seg(x0 + i * s, y0, x0 + i * s, y0 + n * s, "guide"); ans.seg(x0, y0 + i * s, x0 + n * s, y0 + i * s, "guide")
    for poly in half:
        ans.line("M" + " L".join(f"{f(x0 + gx * s)} {f(y0 + gy * s)}" for gx, gy in poly), "l", "stroke-width:2")
        ans.line("M" + " L".join(f"{f(x0 + (n - gx) * s)} {f(y0 + gy * s)}" for gx, gy in poly), "l", "stroke-width:2")
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "tekenles", "difficulty": diff, "minutes": 15, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            "De stippellijn in het midden is een spiegel.",
            "Kijk naar een hoekpunt links en tel hoeveel hokjes het van de spiegel af ligt. Zet aan de rechterkant een stipje even ver van de spiegel.",
            "Verbind de stipjes. Klaar? Kleur de tekening in en kijk op het antwoordblad."]}}}, [("antwoorden", "Zo ziet hij er heel uit", ans)])
spiegel("spiegeltekenen-vlinder", "Spiegeltekenen: vlinder", [[(6, 3), (5, 2), (2, 1), (1, 3), (2, 6), (5, 6), (2, 8), (2, 10), (4, 11), (6, 9)], [(6, 3), (6, 10)], [(6, 3), (5, 1)]], "natuur", "6-9", 2)
spiegel("spiegeltekenen-kasteel", "Spiegeltekenen: kasteel", [[(6, 11), (1, 11), (1, 3), (2, 3), (2, 4), (3, 4), (3, 3), (4, 3), (4, 6), (5, 6), (5, 5), (6, 5)], [(6, 11), (6, 8), (5, 8), (5, 11)], [(2, 6), (3, 6), (3, 8), (2, 8), (2, 6)]], "sprookjes", "6-9", 2)
spiegel("spiegeltekenen-robot", "Spiegeltekenen: robot", [[(6, 1), (4, 1), (4, 4), (2, 4), (2, 9), (4, 9), (4, 11), (6, 11)], [(6, 4), (4, 4)], [(5, 2), (5, 3), (4, 3)], [(4, 5), (1, 5), (1, 8), (2, 8)], [(6, 6), (5, 6), (5, 7), (6, 7)], [(6, 1), (6, 0)]], "ruimte", "6-9", 2)

