"""Batch 23: dobbelstenen om te bouwen (kubus uit polyhedra, met plaatjes op de vlakken)."""
import math
from lib_gen import *
import polyhedra as ph
from shapes import heart_path, star_path, cloud_path, fish_path, leaf_path

CUBE = ph.prism(4, math.sqrt(2) / 2, 1)
def dice(slug, name, sub, faces_draw, codes, cat, age, steps_use):
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16); sh.text(100, 27, sub, 6.5)
    sc, polys = ph.draw(sh, *CUBE, codes, (20, 36, 160, 222))
    for poly, fd in zip(polys, faces_draw):
        cx = sum(x for x, _ in poly) / 4; cy = sum(y for _, y in poly) / 4
        side = math.dist(poly[0], poly[1])
        fd(sh, cx, cy, side)
    sh.legend(["cut", "fold", "glue"], 274)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "bouwplaat", "difficulty": 2, "minutes": 25, "paperGsm": 160, "adultHelp": True,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": name, "printNote": "Op stevig papier (160 gram) rolt hij het best.", "steps": [
            "Kleur de vlakken in en knip de bouwplaat uit langs de doorgetrokken lijnen; de grijze flapjes blijven eraan.",
            "Vouw alle stippellijnen en flapjes naar binnen.",
            "Plak de flapjes één voor één vast tot er een dobbelsteen ontstaat. Het laatste vlak sluit je als een deksel."] + steps_use}}})

def face(expr):
    def d(sh, x, y, s):
        r = s * .3; cy = y - s * .08
        sh.circle_line(x, cy, r, "l", "stroke-width:1.3")
        e = r * .38
        if expr == "blij":
            sh.dot(x - e, cy - e * .4, 1.5); sh.dot(x + e, cy - e * .4, 1.5); sh.line(f"M{f(x - e)} {f(cy + e * .5)}Q{f(x)} {f(cy + e * 1.4)} {f(x + e)} {f(cy + e * .5)}")
        elif expr == "verdrietig":
            sh.dot(x - e, cy - e * .4, 1.5); sh.dot(x + e, cy - e * .4, 1.5); sh.line(f"M{f(x - e)} {f(cy + e * 1.1)}Q{f(x)} {f(cy + e * .3)} {f(x + e)} {f(cy + e * 1.1)}")
            sh.line(f"M{f(x + e)} {f(cy)}q1 3 0 4", "l", "stroke-width:.8")
        elif expr == "boos":
            sh.dot(x - e, cy - e * .2, 1.5); sh.dot(x + e, cy - e * .2, 1.5); sh.line(f"M{f(x - e * 1.4)} {f(cy - e)}L{f(x - e * .3)} {f(cy - e * .6)}M{f(x + e * 1.4)} {f(cy - e)}L{f(x + e * .3)} {f(cy - e * .6)}")
            sh.line(f"M{f(x - e)} {f(cy + e)}H{f(x + e)}")
        elif expr == "bang":
            sh.circle_line(x - e, cy - e * .4, 2.2); sh.circle_line(x + e, cy - e * .4, 2.2); sh.line(f"M{f(x - e)} {f(cy + e)}l{f(e / 2)} -2l{f(e / 2)} 2l{f(e / 2)} -2l{f(e / 2)} 2")
        elif expr == "verbaasd":
            sh.dot(x - e, cy - e * .4, 1.5); sh.dot(x + e, cy - e * .4, 1.5); sh.circle_line(x, cy + e * .8, e * .45)
            sh.line(f"M{f(x - e * 1.3)} {f(cy - e * 1.2)}q{f(e * .4)} -2 {f(e * .8)} 0M{f(x + e * .5)} {f(cy - e * 1.2)}q{f(e * .4)} -2 {f(e * .8)} 0")
        elif expr == "moe":
            sh.line(f"M{f(x - e * 1.3)} {f(cy - e * .3)}h{f(e * .8)}M{f(x + e * .5)} {f(cy - e * .3)}h{f(e * .8)}"); sh.line(f"M{f(x - e * .6)} {f(cy + e)}h{f(e * 1.2)}")
            sh.text(x + r * .9, cy - r * .8, "z", 6, "start")
        sh.text(x, y + s * .36, expr, 6.5)
    return d
dice("emotiedobbelsteen", "Bouwplaat: emotiedobbelsteen", "Gooi, kijk welk gevoel boven ligt en vertel erover.",
     [face(e) for e in ("blij", "verdrietig", "boos", "bang", "verbaasd", "moe")], "ybrpto", "leren", "4-6",
     ["Gooi de dobbelsteen. Welk gevoel ligt boven?", "Doe het gezicht na, of vertel wanneer jij je zo voelde. Er is geen fout antwoord."])

def act(txt, draw):
    def d(sh, x, y, s):
        draw(sh, x, y - s * .16, s * .2)
        words = txt.split(" | ")
        for k, w in enumerate(words): sh.text(x, y + s * .2 + k * 6.5, w, 6)
    return d
def jump(sh, x, y, r): sh.circle_line(x, y - r * .7, r * .3); sh.line(f"M{x} {f(y - r * .4)}V{f(y + r * .3)}M{f(x - r * .6)} {f(y - r * .6)}L{x} {f(y - r * .2)}L{f(x + r * .6)} {f(y - r * .6)}M{f(x - r * .4)} {f(y + r * .9)}L{x} {f(y + r * .3)}L{f(x + r * .4)} {f(y + r * .9)}")
def spin(sh, x, y, r): sh.line(f"M{f(x + r)} {y}A{r} {r} 0 1 1 {x} {f(y - r)}"); sh.line(f"M{f(x - 2)} {f(y - r - 3)}L{x} {f(y - r)}L{f(x - 2)} {f(y - r + 3)}")
def clap(sh, x, y, r): sh.region(f"M{f(x - r * .6)} {f(y + r)}V{f(y - r * .5)}Q{f(x - r * .6)} {f(y - r)} {f(x - r * .2)} {f(y - r)}V{f(y + r)}Z", "k"); sh.region(f"M{f(x + r * .6)} {f(y + r)}V{f(y - r * .5)}Q{f(x + r * .6)} {f(y - r)} {f(x + r * .2)} {f(y - r)}V{f(y + r)}Z", "k")
def leg(sh, x, y, r): sh.circle_line(x, y - r * .7, r * .3); sh.line(f"M{x} {f(y - r * .4)}V{f(y + r * .3)}M{f(x - r * .7)} {f(y - r * .2)}H{f(x + r * .7)}M{x} {f(y + r * .3)}V{f(y + r)}M{x} {f(y + r * .3)}L{f(x + r * .6)} {f(y + r * .2)}")
def toes(sh, x, y, r): sh.circle_line(x - r * .3, y + r * .4, r * .25); sh.line(f"M{f(x - r * .1)} {f(y + r * .3)}Q{f(x + r * .3)} {f(y - r)} {f(x + r * .7)} {f(y + r)}M{f(x)} {f(y + r * .2)}L{f(x + r * .4)} {f(y + r)}")
def dance(sh, x, y, r):
    sh.line(f"M{f(x - r * .4)} {f(y + r * .6)}V{f(y - r * .6)}L{f(x + r * .5)} {f(y - r * .8)}V{f(y + r * .4)}"); sh.circle_r(x - r * .6, y + r * .6, r * .22, "x"); sh.circle_r(x + r * .3, y + r * .4, r * .22, "x")
dice("bewegingsdobbelsteen", "Bouwplaat: bewegingsdobbelsteen", "Gooi en doe wat er boven ligt. Lekker bewegen!",
     [act("spring | 5 keer", jump), act("draai | een rondje", spin), act("klap | 3 keer", clap), act("sta op | één been", leg), act("raak je | tenen", toes), act("doe een | dansje", dance)],
     "golbym", "sport", "4-6", ["Gooi de dobbelsteen en doe de opdracht die boven ligt.", "Spelen jullie met meer kinderen? Om de beurt gooien; de rest doet mee!"])

def pic(draw):
    def d(sh, x, y, s): draw(sh, x, y, s * .32)
    return d
def huis(sh, x, y, r): sh.poly_r([(x - r, y), (x, y - r), (x + r, y)], "r"); sh.rect_r(x - r * .8, y, r * 1.6, r, "y"); sh.rect_r(x - r * .2, y + r * .4, r * .4, r * .6, "w")
def boom(sh, x, y, r): sh.rect_r(x - r * .15, y, r * .3, r, "w"); sh.circle_r(x, y - r * .2, r * .7, "g")
def raket(sh, x, y, r):
    sh.region(f"M{f(x - r * .4)} {f(y + r * .7)}V{f(y - r * .2)}Q{x} {f(y - r * 1.2)} {f(x + r * .4)} {f(y - r * .2)}V{f(y + r * .7)}Z", "r"); sh.circle_r(x, y - r * .1, r * .2, "b")
    sh.poly_r([(x - r * .4, y + r * .2), (x - r * .8, y + r * .9), (x - r * .4, y + r * .7)], "o"); sh.poly_r([(x + r * .4, y + r * .2), (x + r * .8, y + r * .9), (x + r * .4, y + r * .7)], "o")
def vis(sh, x, y, r): sh.region(fish_path(x - r * .2, y, r * .9), "o")
def ster(sh, x, y, r): sh.region(star_path(x, y, r, r * .45), "y")
def sleutel(sh, x, y, r): sh.circle_line(x - r * .5, y, r * .35); sh.line(f"M{f(x - r * .15)} {y}H{f(x + r)}M{f(x + r * .6)} {y}V{f(y + r * .3)}M{f(x + r * .85)} {y}V{f(y + r * .3)}")
dice("verhalendobbelsteen", "Bouwplaat: verhalendobbelsteen", "Gooi en verzin een verhaal met het plaatje dat boven ligt.",
     [pic(huis), pic(boom), pic(raket), pic(vis), pic(ster), pic(sleutel)], "------", "leren", "6-9",
     ["Gooi de dobbelsteen en begin een verhaal met het plaatje dat boven ligt: 'Er was eens een sleutel …'", "Gooi nog een keer en laat dat plaatje ook in je verhaal voorkomen. Zo gaat het verhaal steeds verder."])
