"""Proef met een plaat uit een beeldmodel (ADR 0091). OUT=/tmp/proef python3 beeldmodel_proef.py

De bron (lijntekening, gemaakt met ChatGPT en nagekeken) staat in scripts/plates/bronnen/. trace.py zet hem om naar
vlakken; de kleurcodes hieronder volgen de volgorde van trace.py (groot naar klein) bij --kier 21.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT", "/tmp/proef")
SLUG = "dino-likt-aan-een-ijsje"

colors = {}
def kleur(code, *ix):
    for i in ix:
        colors[i] = code

kleur("b", 0)
kleur("l", 1, 41, 74, 40, 75)
kleur("g", 2, 3, 6, 7, 8, 20, 44, 56, 43, 27, 23, 19, 57)
kleur("z", 4, 30, 21, 60, 24, 55)
kleur("w", 5)
kleur("o", 15, 16, 17, 18, 22, 29, 35, 48, 28, 42, 71, 58, 72, 61, 62, 63, 64, 65, 66, 67, 68, 77, 80)
kleur("y", 10, 13, 14, 25, 70, 69)
kleur("k", 11, 12, 81, 39, 38, 37, 73, 79, 45, 54, 78)
kleur("m", 9, 59)
kleur("r", 33, 50, 53, 46, 34, 36)
kleur("p", 52, 51, 47, 31, 32)
kleur("-", 26, 49, 76)

names = {
    "nl": ("Dino likt aan een ijsje", "de dino", "Hoeveel bloemen zie je?"),
    "de": ("Dino schleckt ein Eis", "der Dino", "Wie viele Blumen siehst du?"),
    "fr": ("Dino qui lèche une glace", "le dino", "Combien de fleurs vois-tu ?"),
    "en": ("Dino licking an ice cream", "the dino", "How many flowers can you see?"),
    "es": ("Dino lamiendo un helado", "el dino", "¿Cuántas flores ves?"),
    "it": ("Dino che lecca un gelato", "il dino", "Quanti fiori vedi?"),
    "pl": ("Dinozaur liże loda", "dinozaur", "Ile kwiatów widzisz?"),
    "pt": ("Dino a lamber um gelado", "o dino", "Quantas flores vês?"),
    "sv": ("Dino som slickar på en glass", "en dino", "Hur många blommor ser du?"),
    "da": ("Dino slikker på en is", "dinoen", "Hvor mange blomster kan du se?"),
    "nb": ("Dino slikker på en is", "dinoen", "Hvor mange blomster ser du?"),
    "fi": ("Dino nuolee jäätelöä", "dino", "Montako kukkaa näet?"),
    "cs": ("Dino líže zmrzlinu", "dino", "Kolik kytek vidíš?"),
    "sk": ("Dino líže zmrzlinu", "dino", "Koľko kvetov vidíš?"),
    "hu": ("Dínó fagyit nyalogat", "a dínó", "Hány virágot látsz?"),
    "ro": ("Dino linge o înghețată", "dinozaurul", "Câte flori vezi?"),
    "el": ("Δεινοσαυράκι γλείφει παγωτό", "ο δεινόσαυρος", "Πόσα λουλούδια βλέπεις;"),
    "bg": ("Динозавърче ближе сладолед", "динозавърът", "Колко цветя виждаш?"),
    "hr": ("Dino liže sladoled", "dinosaur", "Koliko cvjetova vidiš?"),
    "sl": ("Dino liže sladoled", "dino", "Koliko rož vidiš?"),
    "et": ("Dino limpsib jäätist", "dino", "Mitu lille sa näed?"),
    "lv": ("Dinozaurs laiza saldējumu", "dinozaurs", "Cik ziedus tu redzi?"),
    "lt": ("Dinozauriukas laižo ledus", "dinozauras", "Kiek gėlių matai?"),
    "uk": ("Динозаврик лиже морозиво", "динозавр", "Скільки квітів ти бачиш?"),
    "tr": ("Dondurma yalayan dino", "dino", "Kaç tane çiçek görüyorsun?"),
    "sr": ("Dino liže sladoled", "dino", "Koliko cvetova vidiš?"),
    "mk": ("Диносаурус лиже сладолед", "диносаурусот", "Колку цвеќиња гледаш?"),
    "sq": ("Dinozauri lëpin akullore", "dinozauri", "Sa lule sheh?"),
    "is": ("Risaeðla sleikir ís", "risaeðlan", "Hvað sérðu mörg blóm?"),
}

os.makedirs(OUT, exist_ok=True)
svg = os.path.join(OUT, f"{SLUG}.svg")
subprocess.run([sys.executable, os.path.join(HERE, "trace.py"), os.path.join(HERE, "..", "bronnen", f"{SLUG}.png"), svg, "--kier", "21"], check=True)
n = open(svg).read().count('class="r"')
assert n == len(colors), f"{n} vlakken maar {len(colors)} kleuren: kier of bron veranderd?"
meta = {"category": "dinos", "age": "6-9", "world": None, "holiday": None, "codes": "".join(colors[i] for i in range(n)),
        "i18n": {k: {"name": a, "word": b, "countQuestion": c} for k, (a, b, c) in names.items()}}
json.dump(meta, open(os.path.join(OUT, f"{SLUG}.json"), "w"), ensure_ascii=False, indent=1)
print(SLUG, n, "vlakken")
