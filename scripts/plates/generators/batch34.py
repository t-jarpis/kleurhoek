"""Batch 34: Engelse woordjes koppelen (met antwoordblad)."""
import random
from lib_gen import *
from pixelkit import HEX

def koppel(slug, name, pairs, age, diff, seed, cat="leren", colors=None):
    rng = random.Random(seed); order = list(range(len(pairs))); rng.shuffle(order)
    while any(order[i] == i for i in range(len(order))): rng.shuffle(order)
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else cap(name.split(": ", 1)[-1]), 16)
        if not ans: sh.text(100, 27, "Trek een lijn naar het Engelse woord.", 6.5)
        sh.text(46, 44, "Nederlands", 7); sh.text(154, 44, "Engels", 7)
        step = min(22, 220 / len(pairs))
        for i, (nl, en) in enumerate(pairs):
            y = 58 + i * step
            if colors: sh.raw(f'<circle cx="16" cy="{f(y - 2.5)}" r="4.5" style="fill:{HEX.get(colors[i], "#fff")};stroke:#222;stroke-width:.8"/>')
            sh.text(26 if colors else 20, y, nl, 9, "start"); sh.dot(82, y - 2.5, 2)
            j = order.index(i); y2 = 58 + j * step
            if ans: sh.seg(82, y - 2.5, 118, y2 - 2.5, "l", "stroke-width:1.1")
        for j, i in enumerate(order):
            y = 58 + j * step; sh.dot(118, y - 2.5, 2); sh.text(126, y, pairs[i][1], 9, "start")
        return sh
    write(OUT, slug, page(False), {"category": cat, "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 10, "materials": [{"slug": "potlood"}] + ([{"slug": "kleurpotloden"}] if colors else []),
        "i18n": {"nl": {"name": name, "steps": ["Lees het Nederlandse woord.", "Zoek rechts het Engelse woord dat hetzelfde betekent en trek een lijn.", "Zeg het Engelse woord hardop. Kijk na met het antwoordblad."]}}},
        [("antwoorden", "Antwoorden", page(True))])
koppel("engels-dieren", "Engelse woordjes: dieren", [("kat", "cat"), ("hond", "dog"), ("vis", "fish"), ("vogel", "bird"), ("koe", "cow"), ("paard", "horse"), ("varken", "pig"), ("eend", "duck"), ("muis", "mouse"), ("konijn", "rabbit")], "6-9", 1, 341, "dieren")
koppel("engels-kleuren", "Engelse woordjes: kleuren", [("rood", "red"), ("blauw", "blue"), ("geel", "yellow"), ("groen", "green"), ("oranje", "orange"), ("paars", "purple"), ("roze", "pink"), ("bruin", "brown"), ("zwart", "black"), ("wit", "white")], "6-9", 1, 342,
       colors=["r", "n", "y", "g", "o", "p", "m", "w", "x", "-"])
koppel("engels-getallen", "Engelse woordjes: getallen tot tien", [("een", "one"), ("twee", "two"), ("drie", "three"), ("vier", "four"), ("vijf", "five"), ("zes", "six"), ("zeven", "seven"), ("acht", "eight"), ("negen", "nine"), ("tien", "ten")], "6-9", 1, 343)
koppel("engels-lichaam", "Engelse woordjes: je lichaam", [("hoofd", "head"), ("hand", "hand"), ("voet", "foot"), ("oog", "eye"), ("oor", "ear"), ("neus", "nose"), ("mond", "mouth"), ("arm", "arm"), ("been", "leg"), ("haar", "hair")], "9+", 2, 344)
koppel("engels-eten", "Engelse woordjes: eten en drinken", [("appel", "apple"), ("brood", "bread"), ("kaas", "cheese"), ("melk", "milk"), ("water", "water"), ("ei", "egg"), ("banaan", "banana"), ("soep", "soup"), ("taart", "cake"), ("ijsje", "ice cream")], "9+", 2, 345, "eten")
