"""Batch 33: puzzels en codes voor 9+ en 12+ (alles met antwoordblad, oplossingen gecontroleerd)."""
import itertools, random
from lib_gen import *

def roman(n):
    out = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v: out += s; n -= v
    return out
def romeins():
    to_dec = [roman(n) for n in (3, 8, 14, 19, 24, 40, 49, 2026)]
    to_rom = [6, 11, 29, 44, 90, 150]
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Romeinse cijfers", 16)
        sh.text(100, 27, "I = 1   V = 5   X = 10   L = 50   C = 100   D = 500   M = 1000", 7)
        sh.text(100, 37, "Klein vóór groot? Dan haal je het eraf: IV = 4, IX = 9.", 5.6)
        sh.text(20, 54, "Wat staat er? Schrijf het gewone getal.", 7, "start")
        for i, r in enumerate(to_dec):
            x, y = 20 + (i % 2) * 90, 68 + (i // 2) * 18
            sh.text(x, y, r, 9, "start"); sh.text(x + 46, y, "=", 9); sh.raw(f'<rect class="ans" x="{x + 52}" y="{y - 10}" width="28" height="13" rx="2"/>')
            if ans: sh.text(x + 66, y, str({roman(n): n for n in range(1, 3000)}[r]), 8)
        sh.text(20, 152, "En andersom: schrijf in Romeinse cijfers.", 7, "start")
        for i, n in enumerate(to_rom):
            x, y = 20 + (i % 2) * 90, 166 + (i // 2) * 18
            sh.text(x, y, str(n), 9, "start"); sh.text(x + 22, y, "=", 9); sh.raw(f'<rect class="ans" x="{x + 28}" y="{y - 10}" width="50" height="13" rx="2"/>')
            if ans: sh.text(x + 53, y, roman(n), 8)
        sh.text(100, 250, "Extra: schrijf je geboortejaar in Romeinse cijfers.", 6.5)
        return sh
    write(OUT, "romeinse-cijfers", page(False), {"category": "leren", "age": "9+", "kind": "werkblad", "difficulty": 2, "minutes": 15, "materials": POTLOOD,
        "i18n": {"nl": {"name": "Romeinse cijfers lezen en schrijven", "steps": ["Lees de tekens van links naar rechts en tel ze op: XVI = 10 + 5 + 1 = 16.", "Staat een kleiner teken vóór een groter, dan trek je het af: XL = 50 − 10 = 40.", "Kijk na met het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
romeins()

def cijfercode():
    msgs = ["IK BEN EEN SPION", "KOM NAAR DE BOOM", "DE SCHAT LIGT IN HET ZAND"]
    def enc(w): return " ".join(str(ord(c) - 64) for c in w)
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Geheimschrift met cijfers", 16)
        sh.text(100, 27, "Elke letter is een getal: A = 1, B = 2 … Z = 26. Ontcijfer de berichten!", 6)
        for k in range(26):
            x, y = 14 + (k % 13) * 13.6, 38 + (k // 13) * 16
            sh.rect_line(x, y, 12.6, 14, "l", 2, "stroke-width:.5"); sh.text(x + 6.3, y + 6, chr(65 + k), 6); sh.text(x + 6.3, y + 12.4, str(k + 1), 5)
        y = 84
        for m in msgs:
            for w in m.split():
                pass
            sh.text(16, y, " / ".join(enc(w) for w in m.split()), 6.2, "start")
            sh.seg(16, y + 12, 184, y + 12, "guide")
            if ans: sh.text(16, y + 10, m, 8, "start")
            y += 34
        sh.text(100, 196, "Nu jij: schrijf zelf een geheim bericht in cijfers voor een vriend.", 6.5)
        for k in range(3): sh.seg(16, 214 + k * 16, 184, 214 + k * 16, "guide")
        return sh
    write(OUT, "geheimschrift-cijfercode", page(False), {"category": "leren", "age": "6-9", "kind": "werkblad", "difficulty": 2, "minutes": 15, "materials": POTLOOD,
        "i18n": {"nl": {"name": "Geheimschrift: letters als cijfers", "steps": ["Zoek elk getal op in de tabel en schrijf de letter op.", "De schuine streep / betekent: hier begint een nieuw woord.", "Schrijf daarna zelf een geheim bericht. Antwoorden staan op het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
cijfercode()

MORSE = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--",
         "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--.."}
def morse():
    msgs = ["HALLO", "HELP", "ZON EN MAAN", "KOM SNEL"]
    def draw_code(sh, x, y, code, size=1.6):
        for c in code:
            if c == ".": sh.dot(x + size, y, size); x += size * 2 + 2.4
            else: sh.raw(f'<rect x="{f(x)}" y="{f(y - size)}" width="{f(size * 4)}" height="{f(size * 2)}" rx="{f(size)}" style="fill:#222"/>'); x += size * 4 + 2.4
        return x
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Morsecode ontcijferen", 16)
        sh.text(100, 27, "Een stip is kort, een streep is lang. Tussen letters zit een | .", 6.5)
        for k, (ch, code) in enumerate(MORSE.items()):
            x, y = 14 + (k % 4) * 46, 42 + (k // 4) * 11
            sh.text(x, y + 2, ch, 7, "start"); draw_code(sh, x + 8, y, code, 1.3)
        y = 134
        for m in msgs:
            x = 16
            for w_i, w in enumerate(m.split()):
                for ch in w:
                    x = draw_code(sh, x, y, MORSE[ch], 1.15); sh.text(x + .5, y + 2, "|", 5); x += 4.5
                x += 6
            sh.seg(16, y + 12, 184, y + 12, "guide")
            if ans: sh.text(16, y + 10, m, 8, "start")
            y += 28
        return sh
    write(OUT, "morsecode-ontcijferen", page(False), {"category": "leren", "age": "9+", "kind": "werkblad", "difficulty": 2, "minutes": 20, "materials": POTLOOD,
        "i18n": {"nl": {"name": "Morsecode ontcijferen", "steps": ["Morsecode bestaat uit korte (stip) en lange (streep) tekens.", "Zoek elke groep tekens op in de tabel en schrijf de letter op.", "Een grotere ruimte betekent een nieuw woord. Probeer daarna zelf te seinen met een zaklamp: kort en lang licht!"]}}},
        [("antwoorden", "Antwoorden", page(True))])
morse()

# ---------- binaire puzzel (6x6) ----------
def binairo_valid(g, n):
    rows = ["".join(r) for r in g]; cols = ["".join(g[r][c] for r in range(n)) for c in range(n)]
    for line in rows + cols:
        if line.count("0") != n // 2 or "000" in line or "111" in line: return False
    return len(set(rows)) == n and len(set(cols)) == n
def binairo_solutions(puz, n, limit=2):
    cnt = [0]; g = [row[:] for row in puz]; cells = [(r, c) for r in range(n) for c in range(n) if g[r][c] == "."]
    def ok_partial(r, c):
        row = g[r]; col = [g[i][c] for i in range(n)]
        for line in (row, col):
            s = "".join(line)
            if "000" in s or "111" in s or s.count("0") > n // 2 or s.count("1") > n // 2: return False
        if "." not in row and sum(1 for rr in g if rr == row) > 1: return False
        return True
    def rec(i):
        if cnt[0] >= limit: return
        if i == len(cells):
            if binairo_valid(g, n): cnt[0] += 1
            return
        r, c = cells[i]
        for v in "01":
            g[r][c] = v
            if ok_partial(r, c): rec(i + 1)
            g[r][c] = "."
    rec(0); return cnt[0]
def binairo(slug, name, n, seed, age, diff):
    rng = random.Random(seed)
    lines = ["".join(p) for p in itertools.product("01", repeat=n) if p.count("0") == n // 2 and "000" not in "".join(p) and "111" not in "".join(p)]
    def gen():
        while True:
            g = [list(rng.choice(lines)) for _ in range(n)]
            if binairo_valid(g, n): return g
    puzzles = []
    for k in range(2):
        sol = gen(); puz = [row[:] for row in sol]
        cells = [(r, c) for r in range(n) for c in range(n)]; rng.shuffle(cells)
        for r, c in cells:
            keep = puz[r][c]; puz[r][c] = "."
            if binairo_solutions(puz, n) != 1: puz[r][c] = keep
        assert binairo_solutions(puz, n) == 1
        puzzles.append((puz, sol))
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else cap(name.split(": ", 1)[-1]), 16)
        if not ans:
            for i, t in enumerate(["Vul elk vakje met 0 of 1:", "1. Nooit drie dezelfde cijfers naast of onder elkaar.", f"2. In elke rij en kolom evenveel nullen als enen ({n // 2} van elk).", "3. Geen twee rijen zijn hetzelfde, en geen twee kolommen."]):
                sh.text(20, 30 + i * 8, t, 6.2, "start")
        cell = 14
        for k, (p, s) in enumerate(puzzles):
            x0, y0 = 100 - n * cell / 2, 66 + k * (n * cell + 22)
            for i in range(n + 1):
                sh.seg(x0 + i * cell, y0, x0 + i * cell, y0 + n * cell, "l", "stroke-width:.8"); sh.seg(x0, y0 + i * cell, x0 + n * cell, y0 + i * cell, "l", "stroke-width:.8")
            for r in range(n):
                for c in range(n):
                    v = (s if ans else p)[r][c]
                    if v != ".": sh.text(x0 + c * cell + cell / 2, y0 + r * cell + cell * .7, v, 9, weight=700 if p[r][c] != "." else 400)
        return sh
    write(OUT, slug, page(False), {"category": "leren", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 25, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": ["Zoek eerst twee gelijke cijfers naast elkaar: de vakjes ervoor en erna moeten het andere cijfer zijn.", "Zit er een gat tussen twee gelijke cijfers (0 . 0)? Dan moet daar het andere cijfer.", "Tel per rij: zijn er al genoeg nullen? Dan is de rest één. Er is precies één oplossing."]}}},
        [("antwoorden", "Antwoorden", page(True))])
binairo("binaire-puzzel-6x6", "Binaire puzzel: 6 bij 6", 6, 331, "12+", 3)

# ---------- logische puzzel ----------
def logisch():
    names = ["Sara", "Daan", "Mila"]; pets = ["hond", "kat", "konijn"]; colors = ["rood", "blauw", "groen"]
    clues = ["Daan heeft geen hond.", "Het kind met de kat houdt van blauw.", "Mila houdt van rood.", "Sara heeft geen konijn.", "Het kind dat van groen houdt, heeft geen kat.", "Mila heeft geen hond."]
    sols = []
    for pp in itertools.permutations(pets):
        for cc in itertools.permutations(colors):
            P = dict(zip(names, pp)); Cc = dict(zip(names, cc))
            ok = P["Daan"] != "hond" and all(Cc[n] == "blauw" for n in names if P[n] == "kat") and Cc["Mila"] == "rood" and P["Sara"] != "konijn" \
                 and all(P[n] != "kat" for n in names if Cc[n] == "groen") and P["Mila"] != "hond"
            if ok: sols.append((P, Cc))
    assert len(sols) == 1, sols
    P, Cc = sols[0]
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else "Logische puzzel: huisdieren", 15)
        sh.text(100, 27, "Drie kinderen, drie huisdieren, drie kleuren. Wie heeft wat?", 6.2)
        for i, c in enumerate(clues): sh.text(20, 44 + i * 10, f"{i + 1}. {c}", 7, "start")
        x0, y0, w = 50, 110, 22
        heads = pets + colors
        for j, h in enumerate(heads): sh.text(x0 + j * w + w / 2, y0 - 4, h, 5.4)
        for i, nme in enumerate(names):
            sh.text(x0 - 4, y0 + i * w + w * .62, nme, 7, "end")
            for j, h in enumerate(heads):
                sh.rect_line(x0 + j * w, y0 + i * w, w, w, "l", 0, "stroke-width:.7")
                if ans:
                    yes = (P[nme] == h) if j < 3 else (Cc[nme] == h)
                    sh.text(x0 + j * w + w / 2, y0 + i * w + w * .68, "✓" if yes else "×", 9)
        sh.seg(x0 + 3 * w, y0 - 10, x0 + 3 * w, y0 + 3 * w, "l", "stroke-width:1.8")
        sh.text(100, 196, "Zet een × waar het niet kan en een ✓ waar het wel moet.", 6.5)
        for i, nme in enumerate(names):
            if not ans: sh.text(30, 216 + i * 14, f"{nme} heeft een ............. en houdt van .............", 7, "start")
            if ans: sh.text(30, 216 + i * 14 - 1, f"{nme} heeft een {P[nme]} en houdt van {Cc[nme]}", 7, "start") if False else None
        if ans:
            for i, nme in enumerate(names): sh.text(100, 216 + i * 14, f"{nme} heeft een {P[nme]} en houdt van {Cc[nme]}.", 7)
        return sh
    write(OUT, "logische-puzzel-huisdieren", page(False), {"category": "leren", "age": "9+", "kind": "werkblad", "difficulty": 3, "minutes": 20, "materials": POTLOOD,
        "i18n": {"nl": {"name": "Logische puzzel: wie heeft welk huisdier?", "steps": ["Lees de tips één voor één.", "Zet in het rooster een × als iets niet kan en een ✓ als het zeker is.", "Elk kind heeft precies één huisdier en één kleur. Heb je in een rij een ✓? Dan zijn de andere vakjes in die rij en kolom ×.", "Vul onderaan het antwoord in en kijk na."]}}},
        [("antwoorden", "Antwoorden", page(True))])
logisch()
