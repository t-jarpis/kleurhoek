"""Batch 16: woorden schrijven en rekenen met plaatjes."""
import math, random
from lib_gen import *
from shapes import heart_path, star_path, fish_path, leaf_path

def woorden(slug, name, words, age, intro="Trek de woorden over en schrijf ze daarna zelf.", icons=None):
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 18)
    sh.text(100, 29, intro, 6.5)
    y = 40; step = 222 / len(words)
    for i, w in enumerate(words):
        sh.line(f"M14 {y + 20}H186", "guide"); sh.line(f"M14 {y + 7}H186", "guide", "stroke-dasharray:3 3"); sh.line(f"M14 {y + 13}H186", "guide", "stroke-dasharray:3 3")
        sh.text(18, y + 20, w, 17, "start", "tx")
        sh.text(96, y + 20, w, 20, "start", "trace")
        y += step
    write(OUT, slug, sh, {"category": "leren", "age": age, "kind": "werkblad", "difficulty": 2, "minutes": 15, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": name, "steps": ["Lees het woord vooraan hardop.", "Trek het stippelwoord ernaast over, letter voor letter.", "Schrijf het daarna nog een keer zelf op de lijn eronder of op de achterkant."]}}})
woorden("schrijven-woorden-dieren", "Schrijven: woorden met dieren", ["kat", "hond", "vis", "koe", "uil", "eend", "paard"], "6-9")
woorden("schrijven-woorden-kleuren", "Schrijven: kleuren", ["rood", "geel", "blauw", "groen", "roze", "paars", "bruin"], "6-9")
woorden("schrijven-getallen-in-woorden", "Schrijven: getallen in woorden", ["een", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht", "negen", "tien"], "6-9")
woorden("schrijven-seizoenen-en-weer", "Schrijven: seizoenen en weer", ["lente", "zomer", "herfst", "winter", "zon", "regen", "sneeuw"], "6-9")

# ---------- rekenen met plaatjes ----------
def icon(sh, kind, x, y, s=4.8):
    if kind == "appel": sh.circle_r(x, y + 1, s, "r"); sh.region(f"M{x} {y - s + 1}Q{x + 4} {y - s - 5} {x + 7} {y - s - 3}Q{x + 4} {y - s + 1} {x} {y - s + 1}Z", "g")
    elif kind == "ster": sh.region(star_path(x, y, s * 1.2, s * .5), "y")
    elif kind == "vis": sh.region(fish_path(x - 2, y, s * 1.1), "o")
    elif kind == "hart": sh.region(heart_path(x, y, s), "m")
    elif kind == "blad": sh.region(leaf_path(x, y, s * .7, s), "g")
def som_plaatjes(slug, name, sums, op, age, diff):
    kinds = ["ster", "hart", "blad", "ster", "hart", "blad", "ster", "hart"]
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else cap(name.split(": ", 1)[-1]), 16)
        sh.text(100, 27, "Tel de plaatjes en schrijf het antwoord in het hokje." if op == "+" else "Streep de plaatjes door die weggaan en tel wat er over is.", 6)
        for i, (a, b) in enumerate(sums):
            y = 46 + i * 28; k = kinds[i % len(kinds)]
            if op == "+":
                for j in range(a): icon(sh, k, 18 + j * 12.5, y)
                x = 18 + a * 12.5 - 1; sh.text(x, y + 4, "+", 10)
                for j in range(b): icon(sh, k, x + 10 + j * 12.5, y)
                ex = x + 10 + b * 11
                res = a + b
            else:
                for j in range(a):
                    icon(sh, k, 18 + j * 12.5, y)
                    if j >= a - b: sh.line(f"M{18 + j * 12.5 - 6} {y + 6}L{18 + j * 12.5 + 6} {y - 6}", "l", "stroke-width:1.6") if ans else None
                ex = 18 + a * 11
                res = a - b
            sh.text(146, y + 4, f"{a} {'+' if op == '+' else '−'} {b} =", 9, "start")
            sh.raw(f'<rect class="ans" x="176" y="{y - 7}" width="16" height="14" rx="2"/>')
            if ans: sh.text(184, y + 4, str(res), 9)
        return sh
    write(OUT, slug, page(False), {"category": "leren", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 10, "materials": [{"slug": "potlood"}, {"slug": "kleurpotloden", "optional": True}],
        "i18n": {"nl": {"name": name, "steps": (["Tel eerst de plaatjes links, dan de plaatjes rechts.", "Tel ze daarna allemaal samen: dat is het antwoord."] if op == "+" else
                                                ["Tel alle plaatjes in de rij.", "Streep er zoveel door als het tweede getal zegt (van rechts af).", "Tel wat er over is: dat is het antwoord."]) + ["Kijk samen na met het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
som_plaatjes("optellen-met-plaatjes-tot-5", "Optellen met plaatjes tot 5", [(1, 2), (2, 2), (3, 1), (1, 4), (2, 3), (4, 1), (1, 1), (3, 2)], "+", "4-6", 1)
som_plaatjes("optellen-met-plaatjes-tot-10", "Optellen met plaatjes tot 10", [(3, 4), (5, 2), (4, 4), (6, 3), (2, 7), (5, 4), (3, 6), (4, 5)], "+", "4-6", 2)
som_plaatjes("aftrekken-met-plaatjes", "Aftrekken met plaatjes", [(5, 2), (4, 1), (7, 3), (6, 4), (8, 5), (3, 2), (9, 4), (6, 6)], "−", "6-9", 1)

# ---------- meer of minder ----------
def meer_minder():
    r = random.Random(21)
    pairs = [(3, 5), (6, 2), (4, 4), (7, 5), (1, 3), (8, 6)]
    def group(sh, n, x0, y, k):
        for j in range(n): icon(sh, k, x0 + (j % 4) * 13, y - 5 + (j // 4) * 12, 4)
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Waar zijn er meer?", 16)
        sh.text(100, 27, "Zet een kruisje bij het vak met de meeste plaatjes.", 5.6)
        for i, (a, b) in enumerate(pairs):
            y = 50 + i * 36; k = ["ster", "hart", "blad", "ster", "hart", "blad"][i]
            sh.rect_line(16, y - 14, 70, 30, "l", 4, "stroke-width:.7"); sh.rect_line(114, y - 14, 70, 30, "l", 4, "stroke-width:.7")
            group(sh, a, 26, y, k); group(sh, b, 124, y, k)
            if ans:
                for side, ok in ((16, a >= b), (114, b >= a)):
                    if ok: sh.line(f"M{side + 60} {y - 10}l8 8m0 -8l-8 8", "l", "stroke-width:1.6")
        return sh
    write(OUT, "meer-of-minder-plaatjes", page(False), {"category": "leren", "age": "2-4", "kind": "werkblad", "difficulty": 1, "minutes": 10, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": "Waar zijn er meer?", "steps": ["Tel de plaatjes in het linker vak en in het rechter vak.", "Zet een kruisje in het vak met de meeste.", "Zijn er evenveel? Dan krijgen ze allebei een kruisje."]}}},
        [("antwoorden", "Antwoorden", page(True))])
meer_minder()
