"""Dino's in de illustratiestijl (ADR 0090). OUT=/tmp/illu python3 illu_dinos.py"""
import json
import os

from illu import (C, D, L, L2, O, R, blob, cloud, codes, eye, fern, flower, reset, scales, smooth, tuft)

OUT = os.environ.get("OUT", "/tmp/illu")


def dino_met_ijsje():
    reset()
    el = []
    el += [cloud(18, 34, 1.0), cloud(150, 26, 0.8)]
    el += [R(smooth([(96, 168), (120, 138), (150, 128), (180, 132), (204, 146), (204, 172)], closed=False) + " Z", "l")]
    el += [R("M4 172 Q20 132 31 99 Q34 92 42 92 L52 92 Q60 92 63 99 Q72 132 88 172 Z", "w")]
    el += [R(smooth([(33, 96), (47, 93), (61, 96), (60, 104), (57, 108), (55, 102), (53, 118), (50, 121), (48, 106), (45, 112),
                     (42, 113), (40, 104), (37, 109), (34, 104)]), "o")]
    el += [L2("M22 146 Q27 144 30 148 M64 128 Q68 127 70 131 M40 156 Q46 153 50 157 M68 154 Q72 152 75 156 M30 124 Q33 122 36 125")]
    el += [cloud(38, 86, 0.42, "z"), cloud(50, 72, 0.32, "z")]
    el += [R(smooth([(0, 170), (40, 164), (90, 168), (140, 172), (200, 164), (200, 200), (0, 200)], closed=False) + " Z", "g")]
    # staart: dik bij het lijf, opgekruld aan het eind, met ronde rugplaatjes en schubben
    for x, y, h in ((144, 146, 15), (162, 146, 14), (177, 138, 11)):
        el += [R(smooth([(x - 7, y), (x - 4, y - h * .7), (x, y - h), (x + 4, y - h * .7), (x + 7, y)]), "o")]
    el += [O(smooth([(122, 132), (142, 141), (162, 141), (177, 133), (185, 120), (183, 110), (190, 112), (194, 124), (189, 142),
                     (173, 156), (150, 163), (128, 163), (116, 158)]), "t")]
    el += [scales([(140, 152), (150, 155), (160, 154), (170, 150), (179, 143), (186, 132)]), L2("M128 150 Q150 158 176 146")]
    # kroontje
    el += [R(smooth([(86, 46), (88, 30), (98, 38)]), "o"), R(smooth([(97, 40), (104, 22), (111, 40)]), "o"),
           R(smooth([(110, 38), (120, 30), (120, 46)]), "o")]
    # lijf, buik, dijen, voeten
    el += [O(smooth([(80, 98), (70, 116), (66, 138), (70, 156), (84, 168), (100, 170), (116, 168), (128, 156), (132, 136),
                     (126, 114), (116, 98)]), "t")]
    el += [R(blob(99, 144, 16, 21, 10), "y")]
    el += [L2("M86 132 Q99 129 112 132 M84 143 Q99 140 114 143 M86 154 Q99 152 112 154"),
           L2("M73 122 Q75 120 77 122 M70 136 Q72 134 74 136 M123 120 Q125 118 127 120 M127 134 Q129 132 131 134")]
    el += [O(blob(78, 156, 13, 12, 10, rot=.3), "t"), O(blob(120, 156, 13, 12, 10, rot=-.3), "t")]
    el += [L2("M70 150 Q74 146 80 147 M128 150 Q124 146 118 147")]
    for fx in (78, 120):
        el += [O(blob(fx, 170, 14, 7, 10), "t"), C(fx - 8, 173, 2.6, "y"), C(fx, 175, 2.6, "y"), C(fx + 8, 173, 2.6, "y")]
    # hoofd met blije ogen die naar het ijsje kijken
    el += [O(smooth([(64, 70), (68, 50), (84, 38), (104, 34), (124, 38), (138, 52), (142, 70), (134, 88), (116, 98), (90, 98),
                     (72, 90)]), "t")]
    el += eye(88, 64, (1.5, 2.5)) + eye(118, 64, (-1.5, 2.5))
    el += [L2("M80 50 Q87 46 94 49 M112 49 Q119 46 126 50")]
    el += [R(blob(76, 81, 5.5, 3.2, 8), "k"), R(blob(130, 81, 5.5, 3.2, 8), "k")]
    el += [D(100, 78, 1.2), D(106, 78, 1.2)]
    el += [R("M93 84 Q103 87.5 113 84 Q111 96 103 96 Q95 96 93 84 Z", "r"), R("M98 93 Q103 89 108 93 Q103 96.5 98 93 Z", "m")]
    el += [L2("M128 44 Q130 42 132 44 M134 56 Q136 54 138 56 M72 56 Q74 54 76 56")]
    # ijsje
    el += [R(smooth([(90, 112), (112, 112), (104, 136), (101, 140), (98, 136)]), "w")]
    el += [L2("M93 117 L106 127 M96 113 L109 122 M108 114 L95 127 M110 118 L99 132")]
    el += [R(smooth([(86, 113), (86, 105), (92, 99), (101, 96), (110, 99), (116, 105), (116, 113), (112, 115), (110, 121), (107, 115),
                     (99, 116), (96, 122), (93, 115)]), "k")]
    el += [L2("M92 105 Q95 101 99 100")]
    el += [O(blob(88, 123, 6.5, 5.5, 9), "t"), O(blob(114, 123, 6.5, 5.5, 9), "t")]
    el += [L2("M84 125 L86 127 M90 127.5 L91 129"), L2("M118 125 L116 127 M112 127.5 L111 129")]
    # grond
    el += fern(16, 198, 26, 150, 5, 9, "l")
    el += [R(blob(178, 182, 6, 4, 9, .08), "z"), R(blob(186, 186, 4, 3, 9, .08), "z")]
    el += flower(42, 190, "k", "y") + flower(152, 190, "p", "y")
    el += [tuft(58, 176), tuft(140, 181), tuft(10, 182, 7), tuft(176, 192, 7), tuft(96, 190, 6)]
    el += [R(blob(64, 186, 7, 4.5, 9, .08), "z"), R(blob(124, 191, 5, 3.5, 9, .08), "z")]
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">' + "".join(el) + "</svg>"
    names = {
        "nl": ("Babydino met een ijsje", "de dino", "Hoeveel bloemetjes zie je?"),
        "de": ("Babydino mit Eis", "der Dino", "Wie viele Blümchen siehst du?"),
        "fr": ("Bébé dino et sa glace", "le dino", "Combien de petites fleurs vois-tu ?"),
        "en": ("Baby dino with an ice cream", "the dino", "How many little flowers can you see?"),
        "es": ("Bebé dino con un helado", "el dino", "¿Cuántas florecitas ves?"),
        "it": ("Dino cucciolo con il gelato", "il dino", "Quanti fiorellini vedi?"),
        "pl": ("Mały dinozaur z lodami", "dinozaur", "Ile kwiatków widzisz?"),
        "pt": ("Bebé dinossauro com um gelado", "o dino", "Quantas florzinhas vês?"),
        "sv": ("Dinobebis med glass", "en dino", "Hur många små blommor ser du?"),
        "da": ("Dinobaby med is", "dinoen", "Hvor mange små blomster kan du se?"),
        "nb": ("Dinobaby med is", "dinoen", "Hvor mange små blomster ser du?"),
        "fi": ("Dinovauva ja jäätelö", "dino", "Montako pientä kukkaa näet?"),
        "cs": ("Malý dinosaurus se zmrzlinou", "dino", "Kolik kytiček vidíš?"),
        "sk": ("Malý dinosaurus so zmrzlinou", "dino", "Koľko kvietkov vidíš?"),
        "hu": ("Dínóbébi fagyival", "a dínó", "Hány kis virágot látsz?"),
        "ro": ("Pui de dinozaur cu înghețată", "dinozaurul", "Câte floricele vezi?"),
        "el": ("Μωρό δεινοσαυράκι με παγωτό", "ο δεινόσαυρος", "Πόσα λουλουδάκια βλέπεις;"),
        "bg": ("Бебе динозавър със сладолед", "динозавърът", "Колко цветенца виждаш?"),
        "hr": ("Mali dinosaur sa sladoledom", "dinosaur", "Koliko cvjetića vidiš?"),
        "sl": ("Dinozavrček s sladoledom", "dino", "Koliko rožic vidiš?"),
        "et": ("Dinobeebi jäätisega", "dino", "Mitu lillekest sa näed?"),
        "lv": ("Dinozaurēns ar saldējumu", "dinozaurs", "Cik ziediņus tu redzi?"),
        "lt": ("Dinozauriukas su ledais", "dinozauras", "Kiek gėlyčių matai?"),
        "uk": ("Динозаврик з морозивом", "динозавр", "Скільки квіточок ти бачиш?"),
        "tr": ("Dondurmalı bebek dinozor", "dino", "Kaç tane küçük çiçek görüyorsun?"),
        "sr": ("Mali dinosaurus sa sladoledom", "dino", "Koliko cvetića vidiš?"),
        "mk": ("Бебе диносаурус со сладолед", "диносаурусот", "Колку цветчиња гледаш?"),
        "sq": ("Dinozaur i vogël me akullore", "dinozauri", "Sa lule të vogla sheh?"),
        "is": ("Risaeðluungi með ís", "risaeðlan", "Hvað sérðu mörg lítil blóm?"),
    }
    meta = {"category": "dinos", "age": "6-9", "world": None, "holiday": None, "codes": codes(),
            "i18n": {k: {"name": n, "word": w, "countQuestion": q} for k, (n, w, q) in names.items()}}
    return "dino-met-ijsje", svg, meta


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for slug, svg, meta in [dino_met_ijsje()]:
        open(os.path.join(OUT, f"{slug}.svg"), "w").write(svg + "\n")
        json.dump(meta, open(os.path.join(OUT, f"{slug}.json"), "w"), ensure_ascii=False, indent=1)
        print(slug, len(meta["codes"]), "vlakken")
