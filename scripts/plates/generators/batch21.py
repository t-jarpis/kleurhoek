"""Batch 21: sudoku's 9x9 en sudoku met plaatjes."""
import random
from lib_gen import *
from sudokit import make, grid, solve
from shapes import heart_path, star_path

def sudoku9(slug, name, givens, age, diff, seed, intro):
    rng = random.Random(seed)
    ps = [make(9, 3, 3, givens, rng) for _ in range(2)]
    for p, s in ps: assert sum(v != 0 for row in p for v in row) <= givens + 6
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else cap(name.split(": ", 1)[-1]), 16)
        if not ans: sh.text(100, 27, intro, 6)
        for k, (p, s) in enumerate(ps):
            x, y = 45, 40 + k * 122
            sh.text(x, y - 3, f"Puzzel {k + 1}", 6, "start")
            grid(sh, x, y, 110 / 9, 9, 3, 3, s if ans else p, p if ans else None)
        return sh
    write(OUT, slug, page(False), {"category": "leren", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 30, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": [
            "Elke rij, elke kolom en elk vak van 3 bij 3 krijgt de cijfers 1 tot en met 9, elk precies één keer.",
            "Zoek een rij, kolom of vak met veel cijfers en kijk welk cijfer er nog maar op één plek kan.",
            "Schrijf met potlood, dan kun je gummen. Vast? Kijk op het antwoordblad."]}}}, [("antwoorden", "Antwoorden", page(True))])
sudoku9("sudoku-9x9-makkelijk", "Sudoku: 9 bij 9, makkelijk", 38, "9+", 2, 91, "Vul de cijfers 1 tot en met 9 in. Deze twee zijn een goede start.")
sudoku9("sudoku-9x9-gemiddeld", "Sudoku: 9 bij 9, gemiddeld", 30, "12+", 3, 92, "Minder hulpcijfers: zoek steeds de plek waar maar één cijfer past.")

def plaatjes():
    rng = random.Random(44)
    ps = [make(4, 2, 2, 8, rng) for _ in range(4)]
    def sym(sh, v, x, y, s):
        if v == 1: sh.circle_r(x, y, s * .75, "r")
        elif v == 2: sh.region(star_path(x, y, s * .95, s * .42), "y")
        elif v == 3: sh.region(heart_path(x, y, s * .8), "m")
        else: sh.rect_r(x - s * .7, y - s * .7, s * 1.4, s * 1.4, "b")
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Sudoku met plaatjes", 16)
        if not ans: sh.text(100, 27, "In elke rij, kolom en dik vak komt elk plaatje één keer.", 6.5)
        cell = 20
        for k, (p, s) in enumerate(ps):
            x0 = 14 + (k % 2) * 92; y0 = 40 + (k // 2) * 96
            for i in range(5):
                sh.seg(x0 + i * cell, y0, x0 + i * cell, y0 + 4 * cell, "l", "stroke-width:%s" % (1.6 if i % 2 == 0 else .6))
                sh.seg(x0, y0 + i * cell, x0 + 4 * cell, y0 + i * cell, "l", "stroke-width:%s" % (1.6 if i % 2 == 0 else .6))
            for r in range(4):
                for c in range(4):
                    v = (s if ans else p)[r][c]
                    if v: sym(sh, v, x0 + c * cell + cell / 2, y0 + r * cell + cell / 2, 7)
        sh.text(100, 236, "Deze vier plaatjes gebruik je:", 6.5)
        for i in range(4): sym(sh, i + 1, 64 + i * 24, 250, 7)
        return sh
    write(OUT, "sudoku-met-plaatjes", page(False), {"category": "leren", "age": "4-6", "kind": "werkblad", "difficulty": 1, "minutes": 15,
        "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": "Sudoku met plaatjes", "steps": [
            "Er zijn vier plaatjes: een rondje, een ster, een hartje en een vierkantje.",
            "In elke rij, elke kolom en elk vak met een dikke rand komt elk plaatje precies één keer.",
            "Teken het plaatje dat mist in het lege hokje. Kleur ze daarna in. Kijk na met het antwoordblad."]}}}, [("antwoorden", "Antwoorden", page(True))])
plaatjes()
