"""Batch 38: rekenen in context (verhaaltjessommen, geld, tijd, kommagetallen, procenten, temperatuur)."""
import random
from lib_gen import *
from shapes import star_path

def vragen(slug, name, intro, items, age, diff, steps, unit_w=36):
    """items: (vraag, antwoord-tekst)."""
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else cap(name.split(": ", 1)[-1]), 16)
        sh.text(100, 28, intro, 6.2)
        y = 44; step = min(36, 220 / len(items))
        for i, (q, a) in enumerate(items):
            sh.text(14, y, f"{i + 1}.", 7, "start")
            lines = wrap(q, 46)
            for k, ln in enumerate(lines): sh.text(22, y + k * 8, ln, 7, "start")
            by = y + len(lines) * 8 - 3
            sh.text(120, by + 7.5, "Antwoord:", 6.5, "end") if False else None
            sh.raw(f'<rect class="ans" x="{186 - unit_w}" y="{by - 1}" width="{unit_w}" height="11" rx="2"/>')
            if ans: sh.text(186 - unit_w / 2, by + 7.5, a, 7)
            y += max(step, len(lines) * 8 + 16)
        return sh
    write(OUT, slug, page(False), {"category": "leren", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 20, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": steps + ["Kijk na met het antwoordblad."]}}}, [("antwoorden", "Antwoorden", page(True))])
def wrap(t, n):
    out, cur = [], ""
    for w in t.split():
        if len(cur) + len(w) + 1 > n: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return out + [cur]

# verhaaltjessommen (antwoorden worden uitgerekend)
vs1 = [("Sam heeft 4 knikkers. Hij krijgt er 3 bij. Hoeveel knikkers heeft hij nu?", 4 + 3), ("Er zitten 9 vogels op een tak. Er vliegen er 5 weg. Hoeveel blijven er zitten?", 9 - 5),
       ("Mila heeft 6 stickers en Daan heeft er 6. Hoeveel stickers hebben ze samen?", 6 + 6), ("In een doos zitten 12 eieren. Mama gebruikt er 4 voor een taart. Hoeveel eieren zijn er nog?", 12 - 4),
       ("Op het plein staan 8 fietsen. Er komen er 7 bij. Hoeveel fietsen staan er nu?", 8 + 7), ("Je hebt 15 snoepjes en geeft er 6 weg. Hoeveel houd je over?", 15 - 6)]
vragen("verhaaltjessommen-tot-20", "Verhaaltjessommen tot 20", "Lees het verhaaltje goed. Moet je erbij doen of eraf halen?", [(q, str(a)) for q, a in vs1], "6-9", 2,
       ["Lees het verhaaltje en kijk wat er gevraagd wordt.", "Komt er iets bij (erbij, krijgt, samen)? Dan tel je op. Gaat er iets weg (weg, gebruikt, geeft)? Dan haal je eraf.", "Schrijf het antwoord in het hokje."], 24)
vs2 = [("Een klas heeft 4 tafels met 6 kinderen aan elke tafel. Hoeveel kinderen zijn er?", "24"), ("Je koopt 3 ijsjes van 2 euro. Hoeveel betaal je?", "€ 6"),
       ("Oma bakt 24 koekjes en verdeelt ze eerlijk over 4 kleinkinderen. Hoeveel krijgt ieder?", "6"), ("Een trein vertrekt om 9:15 en rijdt 45 minuten. Hoe laat komt hij aan?", "10:00"),
       ("Een boek heeft 120 bladzijden. Je hebt er 75 gelezen. Hoeveel moet je nog?", "45"), ("Een pak sap is 1 liter. Je schenkt 4 bekers van 200 milliliter. Hoeveel milliliter is er over?", "200 ml")]
assert 4 * 6 == 24 and 3 * 2 == 6 and 24 // 4 == 6 and 120 - 75 == 45 and 1000 - 4 * 200 == 200
vragen("verhaaltjessommen-groep-5", "Verhaaltjessommen: keer, delen en tijd", "Is het keer, delen, erbij of eraf? Reken op kladpapier.", vs2, "9+", 3,
       ["Lees het verhaal twee keer en onderstreep de getallen.", "Bedenk welke som erbij hoort en reken die uit op kladpapier.", "Vergeet de eenheid niet: euro, minuten of milliliter."], 30)

# wisselgeld
r = random.Random(38)
geld = []
for prijs, betaald in [(3.50, 5), (7.25, 10), (12.80, 20), (4.95, 10), (1.40, 2), (16.30, 20)]:
    geld.append((f"Iets kost € {prijs:.2f}".replace(".", ",") + f". Je betaalt met € {betaald}. Hoeveel krijg je terug?", f"€ {betaald - prijs:.2f}".replace(".", ",")))
vragen("rekenen-wisselgeld", "Rekenen met geld: wisselgeld", "Tel op vanaf de prijs tot het bedrag dat je betaalt.", geld, "9+", 2,
       ["Begin bij de prijs en tel op tot een rond bedrag: van € 3,50 naar € 4 is 50 cent.", "Tel daarna verder tot wat je betaalt: van € 4 naar € 5 is € 1. Samen € 1,50.", "Schrijf het met een komma: euro's voor de komma, centen erachter."], 30)

# tijdsduur
def hm(m): return f"{m // 60}:{m % 60:02d}"
td = []
for s, e in [(8 * 60 + 30, 9 * 60 + 15), (13 * 60, 14 * 60 + 40), (10 * 60 + 45, 12 * 60 + 5), (15 * 60 + 20, 17 * 60), (7 * 60 + 50, 8 * 60 + 25), (18 * 60 + 35, 20 * 60 + 10)]:
    d = e - s; td.append((f"Van {hm(s)} tot {hm(e)}. Hoe lang duurt dat?", (f"{d // 60} uur " if d >= 60 else "") + (f"{d % 60} min" if d % 60 else "").strip() or "0"))
vragen("rekenen-hoe-lang-duurt-het", "Klokrekenen: hoe lang duurt het?", "Reken uit hoeveel tijd er tussen de twee tijden zit.", td, "9+", 3,
       ["Tel eerst de minuten tot het volgende hele uur.", "Tel daarna de hele uren, en tot slot de minuten van het laatste stukje.", "Tel alles bij elkaar op. 60 minuten is 1 uur."], 46)

# kommagetallen
kg = []
for a, b, op in [(2.5, 1.3, "+"), (4.75, 2.25, "+"), (6.4, 2.8, "−"), (10.0, 3.6, "−"), (1.25, 0.5, "+"), (8.1, 0.9, "−"), (3.45, 4.55, "+"), (12.5, 7.75, "−")]:
    res = round(a + b if op == "+" else a - b, 2)
    fm = lambda v: (f"{v:.2f}".rstrip("0").rstrip(".") if v % 1 else f"{int(v)}").replace(".", ",")
    kg.append((f"{fm(a)} {op} {fm(b)}", fm(res)))
vragen("rekenen-kommagetallen", "Rekenen: kommagetallen", "Zet de komma's onder elkaar en reken zoals altijd.", [(q + " =", a) for q, a in kg], "9+", 2,
           ["Schrijf de getallen onder elkaar, komma onder komma.", "Vul lege plekjes aan met een 0: 2,5 is 2,50.", "Reken van rechts naar links en zet de komma op dezelfde plek in je antwoord."], 28)

# procenten
pc = []
for p, n in [(50, 40), (25, 80), (10, 70), (20, 150), (75, 12), (5, 200), (30, 60), (100, 37)]:
    pc.append((f"{p}% van {n}", str(p * n // 100)))
    assert p * n % 100 == 0
vragen("rekenen-procenten", "Rekenen: procenten", "Procent betekent 'van de honderd'. 50% is de helft.", [(q + " =", a) for q, a in pc], "12+", 2,
           ["50% is de helft, 25% is een kwart, 10% is een tiende.", "Reken eerst 1% of 10% uit en vermenigvuldig dan: 30% van 60 is 3 × 6 = 18."], 28)

# temperatuur en negatieve getallen
tp = [("Het is 3 graden en het wordt 5 graden kouder. Hoe koud is het dan?", "-2 °C"), ("'s Nachts was het -4 graden. Overdag 6 graden warmer. Hoeveel is het overdag?", "2 °C"),
      ("Het is -1 graad en het wordt 3 graden kouder.", "-4 °C"), ("Het verschil tussen -5 en 5 graden?", "10 graden"), ("Het is 0 graden en het wordt 7 graden kouder.", "-7 °C"), ("Van -8 naar -2 graden: hoeveel warmer?", "6 graden")]
assert 3 - 5 == -2 and -4 + 6 == 2 and -1 - 3 == -4 and 5 - (-5) == 10 and 0 - 7 == -7 and -2 - (-8) == 6
vragen("rekenen-temperatuur-onder-nul", "Rekenen onder nul: temperatuur", "Kouder is omlaag, warmer is omhoog op de thermometer.", tp, "9+", 3,
       ["Zoek de begintemperatuur op de getallenlijn.", "Kouder? Ga zoveel stapjes naar beneden. Warmer? Ga omhoog.", "Onder nul schrijf je een min: -3 °C is 3 graden onder nul."], 34)
