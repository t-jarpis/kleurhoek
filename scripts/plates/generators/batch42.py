"""Batch 42: klassieke bordspellen om te printen (dammen, molenspel, reversi, schaken)."""
import math
from lib_gen import *

MAT = [{"slug": "kinderschaar"}, {"slug": "kleurpotloden", "optional": True}, {"slug": "stevig-papier", "optional": True}]
def board(sh, n, x0, y0, s, dark="z"):
    for r in range(n):
        for c in range(n):
            if (r + c) % 2: sh.raw(f'<rect x="{f(x0 + c * s)}" y="{f(y0 + r * s)}" width="{f(s)}" height="{f(s)}" style="fill:#9aa0a8"/>')
    sh.rect_line(x0, y0, n * s, n * s, "l", 0, "stroke-width:1.4")
def stukken(sh, cols, rows, x0, y0, r, labels=None):
    for i in range(cols * rows):
        x = x0 + (i % cols) * (2 * r + 3); y = y0 + (i // cols) * (2 * r + 3)
        sh.raw(f'<circle class="cut" cx="{f(x + r)}" cy="{f(y + r)}" r="{f(r)}"/>'); sh.circle_line(x + r, y + r, r * .7, "l", "stroke-width:.6")
        if labels: labels(sh, x + r, y + r, i)

def dammen():
    sh = Sheet(); title(sh, "Dammen", 16)
    board(sh, 10, 20, 30, 16)
    pg = Sheet(); title(pg, "Damschijven", 16); pg.text(100, 27, "Kleur 20 schijven donker en 20 licht. Knip ze uit.", 6.5)
    stukken(pg, 8, 5, 18, 40, 9.5); pg.legend(["cut"], 276)
    write(OUT, "dambord-met-schijven", sh, {"category": "vormen", "age": "9+", "kind": "spel", "difficulty": 2, "minutes": 30, "materials": MAT,
        "i18n": {"nl": {"name": "Dambord met schijven", "printNote": "Plak het bord op karton, dan blijft het plat.", "steps": [
            "Kleur op blad 2 twintig schijven donker en twintig licht en knip ze uit. Ook knopen of muntjes werken.",
            "Leg ieder je twintig schijven op de donkere velden van de eerste vier rijen aan jouw kant.",
            "Om de beurt schuif je één schijf schuin vooruit naar een leeg donker veld. Staat er een schijf van de ander schuin voor je en is het veld erachter leeg? Dan spring je eroverheen en sla je hem: dat moet.",
            "Kom je aan de overkant? Dan wordt je schijf een dam (leg er een tweede op): die mag schuin over meer velden. Wie geen schijven meer heeft of niet meer kan zetten, verliest."]}}},
        [("extra", "Damschijven", pg)])
dammen()

def molenspel():
    sh = Sheet(); title(sh, "Molenspel", 16)
    c = (100, 130); R = [80, 54, 28]
    for r in R: sh.rect_line(c[0] - r, c[1] - r, 2 * r, 2 * r, "l", 0, "stroke-width:1.6")
    for a, b in (((0, -80), (0, -28)), ((0, 28), (0, 80)), ((-80, 0), (-28, 0)), ((28, 0), (80, 0))):
        sh.seg(c[0] + a[0], c[1] + a[1], c[0] + b[0], c[1] + b[1], "l", "stroke-width:1.6")
    pts = [(dx * r, dy * r) for r in R for dx, dy in ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))]
    assert len(pts) == 24
    for dx, dy in pts: sh.circle_r(c[0] + dx, c[1] + dy, 4, "-")
    for i in range(18):
        x = 24 + (i % 9) * 18; y = 236 + (i // 9) * 18
        sh.raw(f'<circle class="cut" cx="{x}" cy="{y}" r="7"/>')
    sh.text(100, 226, "Knip 18 stenen: kleur 9 in jouw kleur en 9 in een andere.", 6)
    sh.legend(["cut"], 276)
    write(OUT, "molenspel", sh, {"category": "vormen", "age": "9+", "kind": "spel", "difficulty": 2, "minutes": 30, "materials": MAT,
        "i18n": {"nl": {"name": "Molenspel (negen stenen)", "steps": [
            "Ieder heeft negen stenen. Om de beurt zet je een steen op een leeg rondje.",
            "Drie stenen van jou op één rechte lijn is een molen: dan mag je een steen van de ander van het bord halen (niet uit een molen, tenzij het niet anders kan).",
            "Staan alle stenen op het bord? Dan schuif je om de beurt een steen langs een lijn naar een leeg rondje ernaast, en maak je zo nieuwe molens.",
            "Wie nog maar twee stenen heeft of niet meer kan schuiven, verliest."]}}})
molenspel()

def reversi():
    sh = Sheet(); title(sh, "Reversi", 16)
    sh.raw('<rect x="36" y="30" width="128" height="128" style="fill:#cfe3d4"/>')
    for i in range(9): sh.seg(36 + i * 16, 30, 36 + i * 16, 158, "l", "stroke-width:.8"); sh.seg(36, 30 + i * 16, 164, 30 + i * 16, "l", "stroke-width:.8")
    for r, cc, k in ((3, 3, "-"), (4, 4, "-"), (3, 4, "x"), (4, 3, "x")):
        x, y = 36 + cc * 16 + 8, 30 + r * 16 + 8
        sh.raw(f'<circle cx="{x}" cy="{y}" r="6" style="fill:{"#222" if k == "x" else "#fff"};stroke:#222;stroke-width:1"/>')
    pg = Sheet(); title(pg, "Reversi-stenen", 16); pg.text(100, 27, "Knip elk paartje uit, vouw dubbel en plak dicht.", 5.6)
    for i in range(32):
        x = 22 + (i % 8) * 21; y = 44 + (i // 8) * 44
        pg.raw(f'<circle class="cut" cx="{x}" cy="{y}" r="9"/>'); pg.raw(f'<circle cx="{x}" cy="{y + 19}" r="9" style="fill:#555;stroke:#222"/>'); pg.seg(x - 9, y + 9.5, x + 9, y + 9.5, "fold")
    pg.text(100, 230, "Zo heb je 32 stenen: wit aan de ene kant, zwart aan de andere.", 6); pg.legend(["cut", "fold"], 276)
    write(OUT, "reversi-bord", sh, {"category": "vormen", "age": "9+", "kind": "spel", "difficulty": 2, "minutes": 30, "materials": MAT + [{"slug": "lijmstift"}],
        "i18n": {"nl": {"name": "Reversi: bord en stenen", "steps": [
            "Maak de stenen van blad 2: knip elk paartje uit, vouw dubbel en plak dicht. Zo is de ene kant wit en de andere zwart.",
            "Begin met twee witte en twee zwarte stenen in het midden, zoals op het bord getekend.",
            "Om de beurt leg je een steen met jouw kleur boven zo dat je stenen van de ander insluit (recht of schuin). Alle ingesloten stenen draai je om naar jouw kleur.",
            "Kun je niet? Dan pas je. Is het bord vol, dan wint wie de meeste stenen heeft."]}}},
        [("extra", "Reversi-stenen", pg)])
reversi()

def schaken():
    sh = Sheet(); title(sh, "Schaakbord", 16)
    board(sh, 8, 36, 30, 16)
    for i in range(8): sh.text(36 + i * 16 + 8, 166, "abcdefgh"[i], 6); sh.text(30, 30 + i * 16 + 10, str(8 - i), 6)
    names = [("koning", "K"), ("dame", "D"), ("toren", "T"), ("toren", "T"), ("loper", "L"), ("loper", "L"), ("paard", "P"), ("paard", "P")] + [("pion", "")] * 8
    def piece(s, x, y, nm, letter, dark):
        fill = "#555" if dark else "#fff"
        s.raw(f'<rect class="cut" x="{f(x - 9)}" y="{f(y - 11)}" width="18" height="22" rx="2"/>')
        s.raw(f'<path d="M{f(x - 6)} {f(y + 8)}H{f(x + 6)}L{f(x + 4)} {f(y + 4)}H{f(x - 4)}Z" style="fill:{fill};stroke:#222;stroke-width:.8"/>')
        s.raw(f'<circle cx="{f(x)}" cy="{f(y - 2)}" r="5" style="fill:{fill};stroke:#222;stroke-width:.8"/>')
        if letter: s.raw(f'<text x="{f(x)}" y="{f(y)}" font-size="6" text-anchor="middle" style="fill:{"#fff" if dark else "#222"};font-weight:800">{letter}</text>')
    for side, dark in ((0, False), (1, True)):
        for i, (nm, l) in enumerate(names):
            x = 22 + (i % 8) * 22; y = 186 + side * 48 + (i // 8) * 24
            piece(sh, x, y, nm, l, dark)
    sh.text(100, 274, "K koning · D dame · T toren · L loper · P paard · zonder letter: pion", 5.6)
    sh.legend(["cut"], 280 - 1) if False else None
    write(OUT, "schaakbord-met-stukken", sh, {"category": "vormen", "age": "9+", "kind": "spel", "difficulty": 3, "minutes": 30, "materials": MAT,
        "i18n": {"nl": {"name": "Schaakbord met stukken om te knippen", "printNote": "Plak het vel eerst op karton, dan staan de stukken steviger.", "steps": [
            "Knip de 32 kaartjes uit: 16 witte en 16 grijze. Op elk stuk staat een letter (K, D, T, L, P); de pionnen hebben geen letter.",
            "Leg het bord neer met rechtsonder een wit veld. Zet de pionnen op de tweede rij, en op de eerste rij: toren, paard, loper, dame, koning, loper, paard, toren. De dame staat op haar eigen kleur.",
            "Wit begint. Ken je de regels nog niet? Begin met alleen pionnen: wie het eerst de overkant haalt, wint."]}}})
schaken()
