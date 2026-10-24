import os
import math
from kit import *
OUT = os.environ.get("OUT", "concepten/batch1")

# ---------- Tekenlessen: 6 stappen, nieuw = zwart, eerder = grijs; daaronder ruimte om zelf te tekenen ----------
def lesson(slug, name, steps_draw, step_texts, age, diff, cat):
    sh = Sheet()
    title(sh, name.split(": ", 1)[-1][0].upper() + name.split(": ", 1)[-1][1:], 16)
    sh.text(100, 26, "Teken het zwarte stukje van elke stap. Het grijze heb je al.", 6)
    cw, chh = 58, 58
    for i in range(6):
        col, row = i % 3, i // 3
        bx, by = 13 + col * 60, 33 + row * 70
        sh.rect_line(bx, by, cw, chh, "l", 3, "stroke-width:.8")
        sh.text(bx + 5, by + 8, str(i + 1), 7, "start")
        # tekening in een vak van 58: schaal 0.5 vanaf een ontwerp in 100x100
        k = .46; ox, oy = bx + 6, by + 6
        for j in range(i + 1):
            cls = "l" if j == i else "guide"
            style = "stroke-width:1.2" if j == i else "stroke-width:1.1"
            for d in steps_draw[j]:
                sh.raw(f'<path class="{cls}" style="{style}" transform="translate({f(ox)} {f(oy)}) scale({k})" d="{d}" fill="none"/>')
    sh.rect_line(13, 176, 174, 92, "l", 4, "stroke-width:.8")
    sh.text(19, 186, "Nu jij!", 7, "start")
    write(OUT, slug, sh, {
        "category": cat, "age": age, "kind": "tekenles", "difficulty": diff, "minutes": 15,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": name, "steps": step_texts + ["Teken het nu zelf groot in het vak onderaan, eerst dun met potlood.", "Klaar? Trek de lijnen mooi over en kleur je tekening in."]}},
    })

uil = [
    ["M50 18C28 18 22 40 24 62C26 84 40 94 50 94C60 94 74 84 76 62C78 40 72 18 50 18Z"],
    ["M37 44m-11 0a11 11 0 1 0 22 0a11 11 0 1 0 -22 0", "M63 44m-11 0a11 11 0 1 0 22 0a11 11 0 1 0 -22 0"],
    ["M37 44m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0", "M63 44m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0", "M46 56L50 64L54 56Z"],
    ["M28 22L34 8L40 22", "M60 22L66 8L72 22"],
    ["M26 60C16 66 18 80 30 84", "M74 60C84 66 82 80 70 84", "M40 70Q44 74 48 70M52 70Q56 74 60 70M44 78Q48 82 52 78"],
    ["M40 94L36 100M44 94V100M56 94V100M60 94L64 100", "M10 100H90"],
]
lesson("tekenles-uil", "Tekenles: een uil", uil, [
    "Teken een groot ei als lijf.", "Twee grote rondjes voor de ogen.", "Pupillen in de ogen en een snavel in het midden.",
    "Twee puntige oortjes bovenop.", "Vleugels opzij en een paar veertjes op de buik.", "Pootjes en een tak om op te zitten."], "4-6", 1, "dieren")

kat = [
    ["M50 22m-20 0a20 18 0 1 0 40 0a20 18 0 1 0 -40 0"],
    ["M33 12L30 -4L42 6", "M67 12L70 -4L58 6"],
    ["M43 20m-2.5 0a2.5 3 0 1 0 5 0a2.5 3 0 1 0 -5 0", "M57 20m-2.5 0a2.5 3 0 1 0 5 0a2.5 3 0 1 0 -5 0", "M47 28L50 31L53 28Z", "M50 31V34M44 36Q50 39 56 36"],
    ["M36 38C24 50 24 84 36 92H64C76 84 76 50 64 38"],
    ["M40 92V84M60 92V84", "M64 86C86 88 92 70 82 60"],
    ["M30 30H16M30 33L17 37M70 30H84M70 33L83 37", "M42 60Q50 66 58 60"],
]
lesson("tekenles-kat", "Tekenles: een kat", kat, [
    "Teken een rond hoofd.", "Twee puntige oren bovenop.", "Ogen, een neusje en een mondje.",
    "Een lijf als een peer onder het hoofd.", "Pootjes en een lange staart.", "Snorharen en een strikje."], "4-6", 1, "dieren")

vis = [
    ["M15 50C25 25 65 25 75 50C65 75 25 75 15 50Z"],
    ["M75 50L95 32V68Z"],
    ["M28 45m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0", "M18 56Q22 58 26 56"],
    ["M40 30Q48 16 60 30", "M42 70Q48 80 56 70"],
    ["M40 40Q46 50 40 60M50 38Q56 50 50 62M60 40Q66 50 60 60"],
    ["M10 30m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0", "M6 18m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0", "M5 90Q20 84 35 90T65 90T95 90"],
]
lesson("tekenles-vis", "Tekenles: een vis", vis, [
    "Teken een lijf als een citroen op zijn kant.", "Een staart als een driehoek.", "Een oog en een mondje.",
    "Een vin boven en een vin onder.", "Schubben als boogjes op het lijf.", "Belletjes en golfjes erbij."], "4-6", 1, "zee")

raket = [
    ["M38 30H62V78H38Z"],
    ["M38 30Q50 4 62 30"],
    ["M50 46m-8 0a8 8 0 1 0 16 0a8 8 0 1 0 -16 0", "M50 46m-5 0a5 5 0 1 0 10 0a5 5 0 1 0 -10 0"],
    ["M38 60L24 82L38 78", "M62 60L76 82L62 78"],
    ["M42 78Q44 92 50 98Q56 92 58 78"],
    ["M14 20L16 14L18 20L24 22L18 24L16 30L14 24L8 22Z", "M80 14L82 9L84 14L89 16L84 18L82 23L80 18L75 16Z", "M84 60m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"],
]
lesson("tekenles-raket", "Tekenles: een raket", raket, [
    "Teken een lange rechthoek.", "Een punt bovenop als neus.", "Een rond raampje.",
    "Twee vinnen opzij.", "Vuur onder de raket.", "Sterren en een planeetje eromheen."], "6-9", 2, "ruimte")

# ---------- Sjablonen (stencils): vormen zonder losse binnendelen ----------
from shapes import heart_path, star_path, moon_path, drop_path, cloud_path, leaf_path, fish_path, stencil
stencil("sjablonen-hart-ster-maan", "Sjablonen: hart, ster, maan en meer", [
    lambda x, y: heart_path(x, y, 20), lambda x, y: star_path(x, y, 26, 11), lambda x, y: moon_path(x, y, 24), lambda x, y: fish_path(x, y, 18),
    lambda x, y: drop_path(x, y, 16), lambda x, y: cloud_path(x, y, 18)], "vormen", "6-9")
stencil("sjablonen-bladeren", "Sjablonen: natuur", [
    lambda x, y: leaf_path(x, y, 20, 28), lambda x, y: leaf_path(x, y, 12, 30), lambda x, y: heart_path(x, y, 18), lambda x, y: leaf_path(x, y, 24, 22),
    lambda x, y: star_path(x, y, 26, 18, 7), lambda x, y: drop_path(x, y, 18)], "natuur", "6-9")
print("teken klaar")
