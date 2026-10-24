"""Batch 28: stippen en stempelen (vingerverf, stempelstift of stickers) voor de kleinsten."""
import math
from lib_gen import *
from shapes import heart_path, star_path, fish_path

def stip_sheet(slug, name, draw, dots, age, cat, extra_step=None, r=6.5):
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16)
    sh.text(100, 27, "Stip een vinger in de verf en druk in elk rondje een stip.", 6.5)
    draw(sh)
    for x, y in dots: sh.circle_line(x, y, r, "l", "stroke-width:1;stroke-dasharray:2 1.6")
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "tekenles", "difficulty": 1, "minutes": 10,
        "materials": [{"slug": "verf"}, {"slug": "stiften", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Geen verf in huis? Ronde stickers of een dikke stift werken ook.",
            "steps": ["Doe een beetje vingerverf op een bordje.", "Druk met je wijsvinger een stip in elk rondje. Probeer precies in het rondje te blijven.",
                      extra_step or "Laat het drogen en kleur de rest van de tekening in."]}}})

def ring(cx, cy, R, n, a0=0): return [(cx + R * math.cos(a0 + 2 * math.pi * k / n), cy + R * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]
def appelboom(sh):
    sh.rect_r(92, 160, 16, 90, "w"); sh.region("M100 40C40 40 20 100 50 140C70 170 130 170 150 140C180 100 160 40 100 40Z", "g")
stip_sheet("stippen-appelboom", "Stippen: appels in de boom", appelboom, [(70, 80), (100, 70), (130, 82), (60, 112), (90, 104), (120, 110), (145, 118), (80, 140), (112, 140)], "2-4", "natuur", "Rood voor de appels! Kleur daarna de boom en de stam.")
def lieveheer(sh):
    sh.circle_r(100, 70, 22, "x"); sh.ellipse_r(100, 150, 70, 80, "r"); sh.line("M100 90V230"); sh.line("M90 52L80 36M110 52L120 36")
stip_sheet("stippen-lieveheersbeestje", "Stippen: lieveheersbeestje", lieveheer, [(70, 120), (130, 120), (60, 160), (140, 160), (75, 200), (125, 200)], "2-4", "natuur", "Zwarte stippen op de rode vleugels.", r=9)
def rups(sh):
    sh.region("M10 250Q100 230 190 250V270H10Z", "l"); sh.circle_r(170, 150, 18, "g"); sh.dot(164, 146, 2.4); sh.dot(176, 146, 2.4); sh.line("M162 156Q170 162 178 156M164 134L158 118M176 134L182 118")
dots = [(30 + k * 22, 170 + 18 * math.sin(k * .9)) for k in range(6)]
stip_sheet("stippen-rups", "Stippen: maak de rups af", rups, dots, "2-4", "natuur", "Elke stip is een stukje van de rups. Kies steeds een andere kleur!", r=10)
def regenboog(sh):
    for i, R in enumerate((80, 64, 48, 32)): sh.region(f"M{100 - R} 200A{R} {R} 0 0 1 {100 + R} 200H{100 + R - 14}A{R - 14} {R - 14} 0 0 0 {100 - R + 14} 200Z", "-")
    sh.region("M10 205A14 14 0 0 1 36 196A18 18 0 0 1 60 205Z", "-"); sh.region("M140 205A14 14 0 0 1 166 196A18 18 0 0 1 190 205Z", "-")
dts = []
for i, R in enumerate((73, 57, 41)):
    dts += [(100 + R * math.cos(a), 200 - R * math.sin(a)) for a in [math.pi * k / (6 + 2 * (2 - i)) for k in range(1, 6 + 2 * (2 - i))]]
stip_sheet("stippen-regenboog", "Stippen: regenboog", regenboog, dts, "2-4", "natuur", "Elke boog een eigen kleur: rood, oranje en geel.", r=5)
def vis(sh): sh.region(fish_path(96, 140, 60), "-"); sh.dot(50, 132, 4)
stip_sheet("stippen-vis", "Stippen: schubben voor de vis", vis, [(x, y) for x in (80, 100, 120, 140) for y in (120, 140, 160) if not (x == 140 and y != 140)], "2-4", "zee", "Kleur daarna de staart en de vinnen.", r=7.5)
def hart(sh): sh.region(heart_path(100, 140, 80), "-")
stip_sheet("stippen-hart", "Stippen: hartje", hart, [(60, 105), (80, 95), (120, 95), (140, 105), (150, 125), (140, 150), (120, 172), (100, 195), (80, 172), (60, 150), (50, 125), (100, 120), (100, 150)], "2-4", "feest", "Een mooi kaartje voor iemand die je lief vindt!", r=7)
def taart(sh):
    sh.rect_r(40, 150, 120, 70, "k", 6); sh.rect_r(55, 120, 90, 32, "k", 6)
    for x in (75, 100, 125): sh.rect_r(x - 3, 92, 6, 28, "y"); sh.region(f"M{x} 78Q{x + 6} 86 {x} 92Q{x - 6} 86 {x} 78Z", "o")
stip_sheet("stippen-verjaardagstaart", "Stippen: versier de taart", taart, [(55, 175), (80, 175), (105, 175), (130, 175), (150, 175), (70, 200), (95, 200), (120, 200), (145, 200), (70, 136), (95, 136), (120, 136)], "2-4", "feest", "Hoe oud word jij? Zet zoveel kaarsjes erbij als je jaren hebt.", r=6)
def getal(sh):
    sh.text(100, 70, "Stip zoveel als het getal zegt", 7)
    for i in range(5):
        y = 92 + i * 36; sh.text(30, y + 8, str(i + 1), 24); sh.rect_line(52, y - 14, 130, 30, "l", 4, "stroke-width:.7")
stip_sheet("stippen-tellen-tot-5", "Stippen: tel en stip", getal, [], "2-4", "leren", "Tel hardop terwijl je stipt: één, twee, drie …")
