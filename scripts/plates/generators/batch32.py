"""Batch 32: tekenen voor gevorderden (perspectief, isometrisch, licht en schaduw, vergroten)."""
import math
from lib_gen import *

def iso_raster():
    sh = Sheet(); title(sh, "Isometrisch tekenen", 16)
    sh.text(100, 27, "Teken blokken door stippen te verbinden.", 5.6)
    s = 8; h = s * math.sqrt(3) / 2
    # voorbeeld: kubus en trap linksboven
    for row in range(int(220 / (s / 2)) + 1):
        y = 40 + row * s / 2
        if y > 262: break
        off = 0 if row % 2 == 0 else h
        x = 12 + off
        while x < 190: sh.dot(x, y, .7); x += 2 * h
    def P(i, j):  # roosterpunt: i langs x (2h), j langs y (s/2)
        return (12 + i * h, 40 + j * s / 2)
    def poly(pts_, code):
        sh.poly_r([P(*p) for p in pts_], code)
    # kubus (3 vlakken)
    poly([(2, 4), (4, 2), (6, 4), (4, 6)], "y"); poly([(2, 4), (4, 6), (4, 10), (2, 8)], "b"); poly([(4, 6), (6, 4), (6, 8), (4, 10)], "n")
    sh.text(P(4, 12)[0], P(4, 12)[1] + 4, "zo begin je", 5)
    write(OUT, "isometrisch-tekenen-stippenraster", sh, {"category": "patronen", "age": "12+", "kind": "tekenles", "difficulty": 2, "minutes": 30,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": "Isometrisch tekenen op een stippenraster", "steps": [
            "Kijk naar het voorbeeldblok: de bovenkant is een ruit, de zijkanten zijn schuine rechthoeken.",
            "Teken met een liniaal zelf een blok door stippen te verbinden: alleen rechte lijnen omhoog of schuin langs de stippen.",
            "Zet blokken naast en op elkaar: een trap, een toren of je eigen naam in blokken.",
            "Kleur alle bovenkanten licht, alle linkerkanten middel en alle rechterkanten donker. Dan springt het eruit."]}}})
iso_raster()

lesson("tekenles-perspectief-straat", "Tekenles: een straat in perspectief", [
    ["M0 50H100", C(50, 50, 1.5)], ["M50 50L0 100M50 50L100 100"], ["M20 70V30L50 50", "M80 70V30L50 50"],
    ["M20 30H8V82M80 30H92V82"], ["M26 42L26 60L34 55L34 46Z", "M74 42L74 60L66 55L66 46Z"], ["M50 50L50 100", "M46 60H54M44 72H56M42 86H58"]], [
    "Trek een horizon (een rechte lijn) en zet een stip in het midden: het verdwijnpunt.",
    "Teken twee lijnen vanaf het verdwijnpunt naar de hoeken onderaan: dat is de straat.",
    "Teken links en rechts een staande lijn en verbind de bovenkant met het verdwijnpunt: de gevels.",
    "Maak de huizen af met een dak en zijkant.",
    "Ramen worden kleiner naarmate ze verder weg zijn: hun schuine lijnen lopen ook naar het verdwijnpunt.",
    "Een middenstreep op de weg: de streepjes worden kleiner in de verte."], "12+", 3, "patronen")
lesson("tekenles-licht-en-schaduw-bol", "Tekenles: licht en schaduw op een bol", [
    [C(50, 50, 30)], [C(12, 12, 6), "M18 18L32 30"], [C(40, 40, 6)], ["M34 66A30 30 0 0 0 78 58", "M30 70A30 30 0 0 0 80 62"],
    ["M44 84Q70 96 98 84Q82 76 62 80Z"], ["M56 28Q72 38 74 56", "M60 22Q78 34 80 54"]], [
    "Teken een cirkel, het liefst met iets ronds als hulp.",
    "Kies waar het licht vandaan komt, bijvoorbeeld linksboven: teken een klein zonnetje.",
    "Laat aan de lichtkant een glimplek wit.",
    "Arceer de kant van de bol die van het licht af zit: hoe verder weg, hoe donkerder.",
    "Teken de schaduw op de grond, aan de andere kant dan het licht.",
    "Maak de overgang zacht met dunne lijntjes of uitvegen met je vinger."], "12+", 3, "vormen")

def vergroten(slug, name, lines, age, diff):
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16)
    sh.text(100, 27, "Teken het plaatje hokje voor hokje over in het grote raster.", 6.5)
    n = 8
    def grid(x0, y0, s):
        for i in range(n + 1):
            sh.seg(x0 + i * s, y0, x0 + i * s, y0 + n * s, "guide"); sh.seg(x0, y0 + i * s, x0 + n * s, y0 + i * s, "guide")
        for i in range(n): sh.text(x0 + i * s + s / 2, y0 - 2, "ABCDEFGH"[i], 4.8); sh.text(x0 - 3, y0 + i * s + s * .65, str(i + 1), 4.8)
    grid(70, 38, 7.5)
    for pl in lines: sh.line("M" + " L".join(f"{f(70 + x * 7.5)} {f(38 + y * 7.5)}" for x, y in pl), "l", "stroke-width:1.2")
    grid(24, 112, 19)
    write(OUT, slug, sh, {"category": "vormen", "age": age, "kind": "tekenles", "difficulty": diff, "minutes": 25, "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": name, "steps": [
            "Kijk in het kleine raster naar één hokje, bijvoorbeeld B3: welke lijnen lopen erdoor?",
            "Zoek hetzelfde hokje in het grote raster en teken daar dezelfde lijnen, alleen groter.",
            "Werk zo hokje voor hokje. Klaar? Gum de hulplijnen niet: ze horen erbij. Kleur je tekening in."]}}})
vergroten("vergroten-met-raster-uil", "Vergroten met een raster: uil", [
    [(2, 1), (3, 2), (5, 2), (6, 1), (6.5, 4), (6, 7), (4, 7.6), (2, 7), (1.5, 4), (2, 1)], [(3.4, 3.6), (3.4, 3.61)], [(2.6, 3.6), (3.4, 2.8), (4.2, 3.6), (3.4, 4.4), (2.6, 3.6)],
    [(3.8, 3.6), (4.6, 2.8), (5.4, 3.6), (4.6, 4.4), (3.8, 3.6)], [(3.7, 4.6), (4.3, 4.6), (4, 5.2), (3.7, 4.6)], [(3, 6), (4, 6.6), (5, 6)]], "9+", 2)
vergroten("vergroten-met-raster-zeilboot", "Vergroten met een raster: zeilboot", [
    [(1, 6), (7, 6), (6, 7.4), (2, 7.4), (1, 6)], [(4, 6), (4, 0.6)], [(4, 1), (6.6, 5.4), (4, 5.4)], [(3.6, 1.6), (1.6, 5.4), (3.6, 5.4), (3.6, 1.6)],
    [(4, 0.6), (5, 0.9), (4, 1.2)], [(0, 7.8), (1, 7.5), (2, 7.8), (3, 7.5), (4, 7.8), (5, 7.5), (6, 7.8), (7, 7.5), (8, 7.8)]], "9+", 2)
