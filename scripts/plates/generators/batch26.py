"""Batch 26: reken- en letterspellen om te knippen."""
import random
from lib_gen import *
from shapes import heart_path, star_path

def kaartjes(sh, items, cols, rows, x0, y0, w, h, draw):
    for i, it in enumerate(items):
        x, y = x0 + (i % cols) * w, y0 + (i // cols) * h
        sh.rect_line(x + 1, y + 1, w - 2, h - 2, "cut", 3)
        draw(sh, it, x + w / 2, y + h / 2)

def rekenbingo():
    rng = random.Random(81)
    nums = list(range(1, 21))
    cards = [sorted(rng.sample(nums, 9)) for _ in range(4)]
    for c in cards: rng.shuffle(c)
    sh = Sheet(); title(sh, "Rekenbingo tot 20", 16)
    for k, c in enumerate(cards):
        ox, oy = 14 + (k % 2) * 90, 30 + (k // 2) * 94
        sh.rect_line(ox, oy, 82, 82, "cut", 4)
        for i, n in enumerate(c):
            x, y = ox + 14 + (i % 3) * 27, oy + 14 + (i // 3) * 27
            sh.rect_line(x - 12, y - 12, 24, 24, "l", 3, "stroke-width:.6"); sh.text(x, y + 4, str(n), 11)
    sh.text(100, 226, "De sommen voor de spelleider staan op de tweede bladzijde.", 6)
    sh.legend(["cut"], 276)
    sums = []
    for n in nums:
        a = rng.randint(0, n); sums.append((f"{a} + {n - a}" if rng.random() < .6 or n < 3 else f"{n + rng.randint(1, 5)} − {0}", n))
    sums = []
    for n in nums:
        if rng.random() < .6:
            a = rng.randint(0, n); sums.append((f"{a} + {n - a}", n))
        else:
            b = rng.randint(1, 6); sums.append((f"{n + b} − {b}", n))
    for q, a in sums: assert eval(q.replace("−", "-")) == a
    pg = Sheet(); title(pg, "Somkaartjes", 16)
    kaartjes(pg, sums, 4, 5, 12, 30, 44, 46, lambda s, it, x, y: s.text(x, y + 3, it[0], 9))
    pg.legend(["cut"], 276)
    write(OUT, "rekenbingo-tot-20", sh, {"category": "leren", "age": "6-9", "kind": "spel", "difficulty": 2, "minutes": 20,
        "materials": [{"slug": "kinderschaar"}, {"slug": "potlood", "optional": True}],
        "i18n": {"nl": {"name": "Rekenbingo tot 20", "steps": [
            "Knip de vier bingokaarten en de twintig somkaartjes uit.",
            "Elke speler krijgt een bingokaart en een handje knoopjes of muntjes.",
            "De spelleider trekt een somkaartje en leest de som voor. Wie het antwoord op zijn kaart heeft, legt er een knoopje op.",
            "Drie op een rij is bingo! Controleer samen of de sommen kloppen."]}}}, [("extra", "Somkaartjes", pg)])
rekenbingo()

def letterbingo():
    rng = random.Random(82)
    letters = list("abdeghijklmnoprstuvwz")[:20]
    cards = [rng.sample(letters, 9) for _ in range(4)]
    sh = Sheet(); title(sh, "Letterbingo", 16)
    for k, c in enumerate(cards):
        ox, oy = 14 + (k % 2) * 90, 30 + (k // 2) * 94
        sh.rect_line(ox, oy, 82, 82, "cut", 4)
        for i, ch in enumerate(c):
            x, y = ox + 14 + (i % 3) * 27, oy + 14 + (i // 3) * 27
            sh.rect_line(x - 12, y - 12, 24, 24, "l", 3, "stroke-width:.6"); sh.text(x, y + 5, ch, 14)
    sh.text(100, 226, "De trekkaartjes met hoofdletters staan op de tweede bladzijde.", 6)
    sh.legend(["cut"], 276)
    pg = Sheet(); title(pg, "Trekkaartjes", 16)
    kaartjes(pg, [c.upper() for c in letters], 4, 5, 12, 30, 44, 46, lambda s, it, x, y: s.text(x, y + 7, it, 20))
    pg.legend(["cut"], 276)
    write(OUT, "letterbingo", sh, {"category": "leren", "age": "4-6", "kind": "spel", "difficulty": 1, "minutes": 20,
        "materials": [{"slug": "kinderschaar"}],
        "i18n": {"nl": {"name": "Letterbingo: hoofdletter en kleine letter", "steps": [
            "Knip de bingokaarten en de trekkaartjes uit.",
            "De spelleider trekt een kaartje met een hoofdletter en zegt de klank.",
            "Wie dezelfde kleine letter op zijn kaart heeft, legt er een knoopje op.",
            "Drie op een rij is bingo!"]}}}, [("extra", "Trekkaartjes", pg)])
letterbingo()

def memory_tafels():
    rng = random.Random(83)
    pairs = []
    seen = set()
    while len(pairs) < 12:
        a, b = rng.randint(2, 9), rng.randint(2, 9)
        if a * b in seen: continue
        seen.add(a * b); pairs.append((f"{a} × {b}", str(a * b)))
    items = [p[0] for p in pairs] + [p[1] for p in pairs]
    rng.shuffle(items)
    sh = Sheet(); title(sh, "Memory: tafels", 16)
    kaartjes(sh, items, 4, 6, 12, 28, 44, 40, lambda s, it, x, y: s.text(x, y + 4, it, 11 if "×" in it else 14))
    sh.legend(["cut"], 276)
    ans = Sheet(); title(ans, "Welke horen bij elkaar?", 16)
    for i, (q, a) in enumerate(pairs):
        ans.text(60, 46 + i * 18, q, 10, "start"); ans.text(110, 46 + i * 18, "=", 10); ans.text(124, 46 + i * 18, a, 10, "start")
    write(OUT, "memory-tafels", sh, {"category": "leren", "age": "6-9", "kind": "spel", "difficulty": 2, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kinderschaar"}, {"slug": "stevig-papier", "optional": True}],
        "i18n": {"nl": {"name": "Memory met de tafels", "printNote": "Op dik papier kun je niet door de kaartjes heen kijken.", "steps": [
            "Knip de 24 kaartjes uit en leg ze omgekeerd op tafel.",
            "Draai om de beurt twee kaartjes om. Hoort de som bij het antwoord? Dan mag je ze houden en nog een keer.",
            "Horen ze niet bij elkaar? Draai ze terug. Wie aan het eind de meeste paren heeft, wint.",
            "Twijfel? Op de tweede bladzijde staan alle paren."]}}}, [("antwoorden", "Alle paren", ans)])
memory_tafels()

def kwartet():
    shapes_ = [("rondjes", lambda s, x, y, c: s.circle_r(x, y, 4.5, c)), ("sterren", lambda s, x, y, c: s.region(star_path(x, y, 5.5, 2.4), c)),
               ("harten", lambda s, x, y, c: s.region(heart_path(x, y, 4.6), c)), ("vierkanten", lambda s, x, y, c: s.rect_r(x - 4, y - 4, 8, 8, c)),
               ("driehoeken", lambda s, x, y, c: s.poly_r([(x, y - 5), (x + 5, y + 4), (x - 5, y + 4)], c)), ("ruiten", lambda s, x, y, c: s.poly_r([(x, y - 5.5), (x + 4, y), (x, y + 5.5), (x - 4, y)], c))]
    counts = [1, 2, 3, 4]
    cards = [(sn, d, n) for sn, d in shapes_ for n in counts]
    sh = Sheet(); title(sh, "Kwartet: vormen", 16)
    def draw(s, it, x, y):
        sn, d, n = it
        s.text(x, y - 13, sn, 5.5)
        pos = {1: [(0, 0)], 2: [(-7, 0), (7, 0)], 3: [(-11, 0), (0, 0), (11, 0)], 4: [(-6, -6), (6, -6), (-6, 6), (6, 6)]}[n]
        for dx, dy in pos: d(s, x + dx, y + dy + 1, "-")
        for k, m in enumerate(counts): s.text(x - 12 + k * 8, y + 17, str(m), 4.8 if m != n else 6, weight=None if m != n else 800)
    kaartjes(sh, cards, 4, 6, 12, 28, 44, 40, draw)
    sh.legend(["cut"], 276)
    write(OUT, "kwartet-vormen", sh, {"category": "vormen", "age": "4-6", "kind": "spel", "difficulty": 1, "minutes": 20, "paperGsm": 160,
        "materials": [{"slug": "kinderschaar"}, {"slug": "kleurpotloden"}],
        "i18n": {"nl": {"name": "Kwartet met vormen", "printNote": "Op dik papier kun je niet door de kaartjes heen kijken.", "steps": [
            "Kleur elke soort vorm in een eigen kleur (alle sterren geel, alle harten rood …) en knip de 24 kaartjes uit.",
            "Een kwartet is een soort vorm met 1, 2, 3 en 4 vormen. Onderaan elk kaartje zie je welke er bij het kwartet horen.",
            "Deel alle kaartjes. Vraag om de beurt een ander om een kaartje dat je mist: 'Mag ik van jou drie sterren?'",
            "Heb je een kwartet compleet? Leg het neer. Wie de meeste kwartetten heeft, wint."]}}})
kwartet()
