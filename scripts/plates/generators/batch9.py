"""Batch 9: rekenen en taal (werkbladen met antwoorden)."""
import random
from lib_gen import *
from shapes import heart_path, star_path

rnd = random.Random(909)
def uniq(fn, n):
    out, seen = [], set()
    while len(out) < n:
        q = fn()
        if q[0] not in seen: seen.add(q[0]); out.append(q)
    return out
def add100():
    a = rnd.randint(11, 79); b = rnd.randint(5, 99 - a); return (f"{a} + {b}", a + b)
def sub100():
    a = rnd.randint(30, 99); b = rnd.randint(5, a - 5); return (f"{a} − {b}", a - b)
def add1000():
    a = rnd.randint(1, 8) * 100 + rnd.choice([0, 10, 20, 50]); b = rnd.randint(1, (990 - a) // 100) * 100 + rnd.choice([0, 30, 40]); b = min(b, 1000 - a); return (f"{a} + {b}", a + b)
sums_sheet("rekenen-optellen-tot-100", "Rekenen: optellen tot 100", uniq(add100, 12), "6-9", 2, "Tel op en schrijf het antwoord in het hokje.",
           ["Splits het tweede getal in tientallen en eenheden: 34 + 25 = 34 + 20 + 5.", "Eerst de tientallen erbij (54), dan de eenheden (59)."], box_w=22)
sums_sheet("rekenen-aftrekken-tot-100", "Rekenen: aftrekken tot 100", uniq(sub100, 12), "6-9", 3, "Haal eraf en schrijf het antwoord in het hokje.",
           ["Splits het tweede getal: 72 − 27 = 72 − 20 − 7.", "Eerst de tientallen eraf (52), dan de eenheden (45)."], box_w=22)
sums_sheet("rekenen-optellen-tot-1000", "Rekenen: optellen met honderdtallen", uniq(add1000, 12), "9+", 2, "Tel de honderdtallen en tientallen bij elkaar op.",
           ["Kijk eerst naar de honderden: 300 + 400 = 700.", "Tel daarna de tientallen erbij: 320 + 440 = 760."], box_w=24, box_x=63)
def cmp_():
    a, b = rnd.randint(10, 99), rnd.randint(10, 99)
    if rnd.random() < .12: b = a
    return (str(a), "<" if a < b else (">" if a > b else "="), str(b))
cmps = []
seen = set()
while len(cmps) < 12:
    a, s, b = cmp_()
    if (a, b) in seen: continue
    seen.add((a, b)); cmps.append((a, s, b))
def cmp_sheet():
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Groter, kleiner of gelijk?", 16)
        sh.text(100, 30, "Zet in elk hokje <, > of =. De open bek wijst naar het grootste getal.", 6)
        for i, (a, s, b) in enumerate(cmps):
            col, row = i % 2, i // 2; x, y = 26 + col * 90, 52 + row * 30
            sh.text(x, y + 9, a, 11, "start"); sh.raw(f'<rect class="ans" x="{x + 20}" y="{y - 1}" width="16" height="14" rx="2"/>'); sh.text(x + 42, y + 9, b, 11, "start")
            if ans: sh.text(x + 28, y + 9.5, s, 10)
        sh.poly_r(star_pts(100, 250, 14, 6), "y"); sh.text(100, 274, "Alles af? Kleur de ster!", 6.5)
        return sh
    write(OUT, "rekenen-groter-kleiner", page(False), {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 1, "minutes": 10, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": "Rekenen: groter, kleiner of gelijk", "steps": ["Kijk eerst naar de tientallen: welk getal heeft er meer?", "Zijn de tientallen gelijk? Kijk dan naar de eenheden.", "Schrijf < als het linkergetal kleiner is, > als het groter is en = als ze gelijk zijn.", "Kijk samen na met het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
cmp_sheet()
sums_sheet("rekenen-dubbelen", "Rekenen: dubbelen", [(f"dubbel {n}", 2 * n) for n in [4, 7, 2, 10, 6, 9, 3, 8, 5, 12, 15, 25]], "6-9", 1, "Dubbel betekent twee keer zoveel.",
           ["Dubbel 6 is 6 + 6.", "Weet je het niet? Tel twee keer hetzelfde getal op je vingers."], box_w=20, box_x=64)
sums_sheet("rekenen-halveren", "Rekenen: de helft", [(f"{n} : 2", n // 2) for n in [8, 14, 4, 20, 12, 18, 6, 16, 10, 24, 30, 50]], "6-9", 2, "De helft van 14 schrijf je als 14 : 2. Hoeveel is het?",
           ["De helft van 10 is 5, want 5 + 5 = 10.", "Twijfel je? Controleer met dubbelen: is het antwoord dubbel weer het getal?"], box_w=18)

# ---------- rekenpiramides ----------
def piramides():
    r = random.Random(31)
    pyrs = []
    for k in range(4):
        base = [r.randint(1, 9 if k < 2 else 20) for _ in range(4)]
        rows = [base]
        while len(rows[-1]) > 1: rows.append([rows[-1][i] + rows[-1][i + 1] for i in range(len(rows[-1]) - 1)])
        # zichtbaar: onderste rij + soms één bovenste getal in plaats van een onderste (puzzel)
        show = {(0, i) for i in range(4)}
        if k >= 2: show.discard((0, 1)); show.add((1, 0))
        pyrs.append((rows, show))
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Rekenpiramides", 16)
        sh.text(100, 27, "Elk blok is de som van de twee blokken eronder.", 6.5)
        for k, (rows, show) in enumerate(pyrs):
            ox = 20 + (k % 2) * 88; oy = 50 + (k // 2) * 110; w = 20; h = 18
            for lvl, row in enumerate(rows):
                for i, v in enumerate(row):
                    x = ox + i * w + lvl * w / 2; y = oy + (3 - lvl) * h
                    given = (lvl, i) in show
                    sh.rect_r(x, y, w, h, "y" if given else "-")
                    if given or ans: sh.text(x + w / 2, y + h * .68, str(v), 7.5 if v < 100 else 6.5, weight=None if given else 400)
        sh.text(100, 268, "Tip: bij de laatste twee reken je terug met aftrekken.", 6)
        return sh
    write(OUT, "rekenpiramides", page(False), {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 2, "minutes": 15, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": "Rekenpiramides", "steps": ["Begin onderaan: tel twee blokken naast elkaar op en schrijf het antwoord in het blok erboven.", "Werk zo verder tot je bovenaan bent.", "Bij de laatste twee mist er een getal onderaan: reken terug met aftrekken.", "Kijk na met het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
piramides()

# ---------- getallenlijn ----------
def getallenlijn():
    lines = [(0, 1, [3, 6, 8]), (10, 1, [12, 15, 19]), (0, 2, [4, 10, 16]), (0, 5, [10, 25, 40]), (20, 10, [40, 70, 100]), (50, 5, [60, 75, 90])]
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Getallenlijn", 16)
        sh.text(100, 27, "Welke getallen ontbreken? Schrijf ze in de lege hokjes.", 6.5)
        for r_, (start, step, missing) in enumerate(lines):
            y = 58 + r_ * 36
            sh.seg(14, y, 186, y, "l", "stroke-width:1.2"); sh.line(f"M182 {y - 3}L187 {y}L182 {y + 3}")
            for i in range(11):
                v = start + i * step; x = 20 + i * 16
                sh.seg(x, y - 4, x, y + 4)
                if v in missing:
                    sh.raw(f'<rect class="ans" x="{x - 7}" y="{y + 6}" width="14" height="11" rx="2"/>')
                    if ans: sh.text(x, y + 14.5, str(v), 6 if v < 100 else 5)
                else: sh.text(x, y + 14.5, str(v), 6 if v < 100 else 5)
        return sh
    write(OUT, "getallenlijn-invullen", page(False), {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 2, "minutes": 10, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": "Getallenlijn invullen", "steps": ["Kijk naar twee getallen naast elkaar: hoeveel komt er steeds bij? Dat is de sprong.", "Tel vanaf het getal voor het lege hokje één sprong verder.", "Kijk na met het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
getallenlijn()

# ---------- dagen en maanden ----------
def dagen_maanden():
    dagen = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
    maanden = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]
    hide_d = {1, 4, 6}; hide_m = {2, 5, 7, 10}
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Dagen en maanden", 16)
        sh.text(100, 27, "Schrijf de ontbrekende dagen en maanden op de lijntjes.", 6.5)
        sh.text(20, 46, "De dagen van de week", 8, "start")
        for i, d in enumerate(dagen):
            y = 60 + i * 13; sh.text(24, y, f"{i + 1}.", 7, "start")
            if i in hide_d:
                sh.seg(36, y + 1, 110, y + 1, "guide")
                if ans: sh.text(38, y, d, 7.5, "start")
            else: sh.text(38, y, d, 7.5, "start")
        sh.text(20, 162, "De maanden van het jaar", 8, "start")
        for i, m in enumerate(maanden):
            col, row = i // 6, i % 6; x = 24 + col * 88; y = 176 + row * 13
            sh.text(x, y, f"{i + 1}.", 7, "start")
            if i in hide_m:
                sh.seg(x + 12, y + 1, x + 80, y + 1, "guide")
                if ans: sh.text(x + 14, y, m, 7.5, "start")
            else: sh.text(x + 14, y, m, 7.5, "start")
        sh.text(100, 268, "Extra: welke dag is het vandaag? En in welke maand ben jij jarig?", 6)
        return sh
    write(OUT, "dagen-en-maanden", page(False), {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 1, "minutes": 10, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": "Dagen en maanden op volgorde", "steps": ["Zeg de dagen van de week hardop, te beginnen bij maandag.", "Welke dag mist er? Schrijf hem op het lijntje.", "Doe hetzelfde met de maanden, te beginnen bij januari.", "Kijk na met het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
dagen_maanden()

# ---------- hoofdletters en kleine letters ----------
def letters_koppelen():
    left = list("ABDEGHMRT"); right = [c.lower() for c in left]
    r = random.Random(5); order = right[:]; r.shuffle(order)
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Grote en kleine letters", 16)
        sh.text(100, 27, "Trek een lijn van de hoofdletter naar dezelfde kleine letter.", 6.5)
        for i, c in enumerate(left):
            y = 50 + i * 24
            sh.text(52, y + 6, c, 16); sh.dot(70, y, 2.4)
            j = order.index(c.lower()); sh.dot(130, 50 + j * 24, 2.4)
            if ans: sh.seg(70, y, 130, 50 + j * 24, "l", "stroke-width:1.2")
        for j, c in enumerate(order): sh.text(150, 50 + j * 24 + 6, c, 16)
        return sh
    write(OUT, "letters-groot-en-klein", page(False), {"category": "leren", "age": "4-6", "kind": "werkblad", "difficulty": 1, "minutes": 10, "materials": [{"slug": "potlood"}],
        "i18n": {"nl": {"name": "Grote en kleine letters koppelen", "steps": ["Zeg de hoofdletter hardop.", "Zoek rechts dezelfde letter, maar dan klein.", "Trek een lijn van stip naar stip. Kijk daarna na met het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
letters_koppelen()

# ---------- tellen tot 5 ----------
def tellen5():
    r = random.Random(8)
    rows = [(n, kind) for n, kind in zip([3, 1, 5, 2, 4, 3], ["ster", "hart", "bal", "ster", "hart", "bal"])]
    def icon(sh, kind, x, y):
        if kind == "ster": sh.region(star_path(x, y, 9, 4), "y")
        elif kind == "hart": sh.region(heart_path(x, y, 8), "r")
        else: sh.circle_r(x, y, 7, "b")
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Tel en kleur", 16)
        sh.text(100, 27, "Tel de plaatjes en zet een rondje om het goede getal.", 6.5)
        for i, (n, kind) in enumerate(rows):
            y = 54 + i * 36
            for k in range(n): icon(sh, kind, 22 + k * 18, y)
            sh.rect_line(10, y - 15, 104, 30, "l", 4, "stroke-width:.6")
            for k in range(1, 6):
                x = 124 + (k - 1) * 14; sh.text(x, y + 5, str(k), 11)
                if ans and k == n: sh.circle_line(x, y + 1, 7)
        return sh
    write(OUT, "tellen-tot-5-plaatjes", page(False), {"category": "leren", "age": "2-4", "kind": "werkblad", "difficulty": 1, "minutes": 10, "materials": [{"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": "Tellen tot 5 met plaatjes", "steps": ["Wijs elk plaatje aan en tel hardop: één, twee, drie …", "Zet een rondje om het getal dat je hebt geteld.", "Kleur daarna de plaatjes in."]}}},
        [("antwoorden", "Antwoorden", page(True))])
tellen5()
