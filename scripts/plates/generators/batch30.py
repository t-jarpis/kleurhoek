"""Batch 30: knipoefeningen voor de kleinsten (knippen in franjes, krullen en vormen)."""
import math
from lib_gen import *
from shapes import heart_path, star_path

SCH = [{"slug": "kinderschaar"}, {"slug": "kleurpotloden", "optional": True}]
def knip(slug, name, sub, draw, age, diff, steps, cat="vormen"):
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16); sh.text(100, 27, sub, 6.5)
    draw(sh); sh.legend(["cut"], 274)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "knipplaat", "difficulty": diff, "minutes": 10, "materials": SCH,
        "i18n": {"nl": {"name": name, "steps": ["Houd de schaar met je duim boven en je vingers onder."] + steps}}})

def haren(sh):
    cx, cy = 100, 170; R = 58
    sh.circle_r(cx, cy, 50, "k"); sh.dot(cx - 18, cy - 6, 4); sh.dot(cx + 18, cy - 6, 4); sh.line(f"M{cx - 16} {cy + 18}Q{cx} {cy + 32} {cx + 16} {cy + 18}")
    sh.region(f"M{cx - R} {cy - 30}A{R} {R} 0 0 1 {cx + R} {cy - 30}Z", "w")
    for k in range(1, 14):
        x = cx - R + k * (2 * R / 14)
        top = cy - 30 - math.sqrt(max(0, R * R - (x - cx) ** 2))
        sh.seg(x, top, x, cy - 36, "cut")
    # buitenrand: haar bovenaan, gezicht onderaan
    sh.line(f"M{cx - R} {cy - 30}A{R} {R} 0 0 1 {cx + R} {cy - 30}L{cx + 40} {cy - 30}A50 50 0 1 1 {cx - 40} {cy - 30}Z", "cut")
knip("knippen-haren-knippen", "Knippen: kappertje spelen", "Knip het hoofd uit en knip dan in de haren.", haren, "2-4", 1,
     ["Knip eerst het hele hoofd uit langs de buitenrand.", "Knip dan van de bovenkant naar beneden langs elk streepje in het haar. Stop aan het eind van het streepje!", "Krul de haren om een potlood, of knip een pony."], "beroepen")
def leeuw(sh):
    cx, cy = 100, 150
    sh.circle_r(cx, cy, 80, "o")
    for k in range(24):
        a = 2 * math.pi * k / 24
        sh.seg(cx + 44 * math.cos(a), cy + 44 * math.sin(a), cx + 80 * math.cos(a), cy + 80 * math.sin(a), "cut")
    sh.circle_r(cx, cy, 42, "y"); sh.circle_r(cx - 30, cy - 34, 9, "y"); sh.circle_r(cx + 30, cy - 34, 9, "y")
    sh.circle_r(cx, cy, 42, "y")
    sh.dot(cx - 14, cy - 8, 3.5); sh.dot(cx + 14, cy - 8, 3.5); sh.region(f"M{cx - 7} {cy + 6}H{cx + 7}L{cx} {cy + 14}Z", "w"); sh.line(f"M{cx} {cy + 14}V{cy + 20}M{cx - 10} {cy + 24}Q{cx} {cy + 30} {cx + 10} {cy + 24}")
knip("knippen-leeuwenmanen", "Knippen: manen voor de leeuw", "Knip in de manen langs de streepjes, rondom het hoofd.", leeuw, "2-4", 1,
     ["Knip eerst de grote cirkel uit, langs de buitenrand.", "Knip dan langs elk streepje naar het gezicht toe. Stop bij het gezicht!", "Buig de manen een beetje op: je leeuw krijgt een wilde kuif."], "dieren")
def gras(sh):
    for row in range(3):
        y = 60 + row * 70
        sh.rect_r(16, y, 168, 50, "l" if row % 2 else "g", 2)
        for k in range(1, 21): sh.seg(16 + k * 8, y, 16 + k * 8, y + 34, "cut")
        sh.rect_line(16, y, 168, 50, "cut", 2)
knip("knippen-gras-franjes", "Knippen: gras met franjes", "Knip de stroken uit en knip er gras in: kleine knipjes!", gras, "2-4", 1,
     ["Knip eerst een strook uit langs de buitenste streepjeslijn.", "Knip daarna steeds een klein stukje in langs de korte streepjes: het gras.", "Plak je grasstroken onderaan een tekening, of zet ze rechtop als tuintje."], "natuur")
def krullen(sh):
    for i in range(4):
        y = 60 + i * 50
        if i == 0: d = f"M20 {y}" + "".join(f"Q{30 + k * 20} {y + (-16 if k % 2 == 0 else 16)} {40 + k * 20} {y}" for k in range(8))
        elif i == 1: d = f"M20 {y}" + "".join(f"A10 10 0 1 1 {40 + k * 20} {y}" for k in range(8))
        elif i == 2: d = f"M20 {y}" + "".join(f"Q{40 + k * 40} {y + (-26 if k % 2 == 0 else 26)} {60 + k * 40} {y}" for k in range(4))
        else: d = f"M20 {y}" + "".join(f"A16 16 0 1 0 {52 + k * 32} {y}" for k in range(5))
        sh.line(d, "cut")
        sh.raw(f'<g transform="translate(12 {y}) scale(.3)"><circle class="l" cx="-8" cy="-6" r="6" fill="none"/><circle class="l" cx="-8" cy="6" r="6" fill="none"/><path class="l" d="M-3 -4L20 4M-3 4L20 -4"/></g>')
knip("knipoefenen-krullen-en-bogen", "Knippen oefenen: bogen en krullen", "Knip langzaam over de lijn en draai het papier mee.", krullen, "4-6", 2,
     ["Begin bij de schaar en knip langzaam over de streepjeslijn.", "Bij een bocht draai je het papier, niet de schaar.", "Lukt het? Probeer de volgende lijn."])
def vormen(sh):
    shapes_ = [lambda: sh.raw('<circle class="cut" cx="52" cy="80" r="30"/>'), lambda: sh.rect_line(118, 50, 60, 60, "cut"),
               lambda: sh.line("M52 130L84 190H20Z", "cut"), lambda: sh.line(star_path(148, 160, 34, 15), "cut"),
               lambda: sh.line(heart_path(52, 238, 26), "cut"), lambda: sh.line("M148 205L180 238L148 271L116 238Z", "cut")]
    for f_ in shapes_: f_()
    for x, y, w in ((52, 80, "rondje"), (148, 82, "vierkant"), (52, 172, "driehoek"), (148, 162, "ster"), (52, 240, "hart"), (148, 240, "ruit")): sh.text(x, y + 2, w, 6)
knip("knipoefenen-vormen", "Knippen oefenen: vormen", "Knip de vormen uit. Welke is het makkelijkst?", vormen, "4-6", 2,
     ["Knip eerst grof rondom een vorm, dan heb je een klein stukje papier in je hand.", "Knip daarna precies over de streepjeslijn.", "Leg je vormen samen tot een plaatje: een huisje, een robot of een bloem!"])
