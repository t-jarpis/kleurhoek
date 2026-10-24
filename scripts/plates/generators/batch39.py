"""Batch 39: creatieve tekenopdrachten."""
import math, random
from lib_gen import *

MAT = [{"slug": "potlood"}, {"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}]
def opdracht(slug, name, sub, draw, age, diff, steps, cat="vormen", minutes=20):
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16); sh.text(100, 27, sub, 6.5); draw(sh)
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "tekenles", "difficulty": diff, "minutes": minutes, "materials": MAT,
        "i18n": {"nl": {"name": name, "steps": steps}}})

def rondjes(sh):
    for i in range(12):
        x, y = 40 + (i % 3) * 60, 60 + (i // 3) * 58
        sh.circle_line(x, y, 16, "l", "stroke-width:1.2")
opdracht("maak-er-iets-van-rondjes", "Tekenopdracht: maak er iets van (rondjes)", "Maak van elk rondje iets anders: een zon, een bal …", rondjes, "4-6", 1,
         ["Kijk naar een rondje: waar lijkt het op? Een bal, een appel, een klok, een uil?", "Teken er iets omheen of in, zodat het dat ding wordt.", "Probeer alle twaalf rondjes iets anders te maken. Kleur ze daarna in."])
def krabbels(sh):
    r = random.Random(39)
    for i in range(6):
        x, y = 50 + (i % 2) * 100, 64 + (i // 2) * 74
        sh.rect_line(x - 44, y - 32, 88, 66, "l", 4, "stroke-width:.6")
        pts = [(x + r.uniform(-32, 32), y + r.uniform(-22, 22)) for _ in range(5)]
        sh.line(f"M{f(pts[0][0])} {f(pts[0][1])}" + "".join(f"Q{f(pts[k][0])} {f(pts[k][1])} {f((pts[k][0] + pts[k + 1][0]) / 2)} {f((pts[k][1] + pts[k + 1][1]) / 2)}" for k in range(1, 4)), "l", "stroke-width:1.4")
opdracht("maak-er-iets-van-krabbels", "Tekenopdracht: wat wordt deze krabbel?", "Maak van elke krabbel een tekening.", krabbels, "6-9", 2,
         ["Draai het papier rond: zie je ergens een dier, een gezicht of een voertuig in?", "Gebruik de krabbel als deel van je tekening en teken de rest erbij.", "Geef elke tekening een naam."])
def droomhuis(sh):
    sh.rect_line(14, 36, 172, 180, "l", 6, "stroke-width:1")
    for i, t in enumerate(["Hoeveel verdiepingen?", "Een glijbaan of een toren?", "Wie woont er nog meer?", "Wat staat er in de tuin?"]):
        sh.text(18 + (i % 2) * 90, 230 + (i // 2) * 14, "• " + t, 6.5, "start")
opdracht("teken-je-droomhuis", "Tekenopdracht: mijn droomhuis", "Hoe ziet het huis eruit waar jij het liefst zou wonen?", droomhuis, "6-9", 1,
         ["Bedenk eerst: een boomhut, een kasteel, een huis onder water of in de ruimte?", "Teken de buitenkant groot in het kader. Gebruik de vragen onderaan als je vastzit.", "Kleur je huis in en vertel er iemand over."], "thuis")
def superheld(sh):
    sh.rect_line(14, 36, 110, 196, "l", 6, "stroke-width:1")
    sh.circle_line(69, 70, 14, "guide"); sh.line("M69 84V150M69 100L44 122M69 100L94 122M69 150L50 200M69 150L88 200", "guide")
    for i, t in enumerate(["Naam:", "Superkracht:", "Zwakke plek:", "Hulpje:"]):
        y = 50 + i * 40; sh.text(130, y, t, 7, "start"); sh.seg(130, y + 14, 186, y + 14, "guide")
opdracht("ontwerp-je-eigen-superheld", "Tekenopdracht: ontwerp je eigen superheld", "Teken een held die nog niemand kent, met een eigen pak.", superheld, "6-9", 2,
         ["Gebruik het grijze poppetje als hulp voor de houding.", "Teken het pak, een cape, een masker of iets wat alleen jouw held heeft.", "Vul rechts in hoe je held heet en wat hij of zij kan."], "sprookjes")
def doos(sh):
    sh.poly_r([(40, 150), (100, 175), (160, 150), (160, 230), (100, 255), (40, 230)], "w")
    sh.line("M100 175V255"); sh.poly_r([(40, 150), (100, 125), (160, 150), (100, 175)], "-")
    sh.poly_r([(40, 150), (20, 118), (80, 95), (100, 125)], "w"); sh.poly_r([(160, 150), (180, 118), (120, 95), (100, 125)], "w")
opdracht("teken-wat-er-in-de-doos-zit", "Tekenopdracht: wat zit er in de doos?", "De doos is open. Wat springt, kruipt of zweeft eruit?", doos, "4-6", 1,
         ["Bedenk wat er in de doos zit: een dier, een cadeau, een monstertje, een regenboog?", "Teken het zo dat het uit de doos komt, boven de klepjes.", "Kleur de doos en wat erin zat."], "feest")
def weerweek(sh):
    dagen = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
    for i, d in enumerate(dagen):
        x, y = 14 + (i % 2) * 88, 38 + (i // 2) * 58
        if i == 6: x = 58
        sh.rect_line(x, y, 84, 52, "l", 4, "stroke-width:.8"); sh.text(x + 4, y + 8, d, 6.5, "start")
opdracht("teken-het-weer-van-de-week", "Tekenopdracht: het weer van deze week", "Kijk elke dag naar buiten en teken het weer.", weerweek, "4-6", 1,
         ["Kijk elke dag even naar buiten: schijnt de zon, regent het, is het bewolkt of waait het?", "Teken het weer in het vak van die dag.", "Aan het eind van de week: welk weer kwam het vaakst?"], "natuur", 10)
def strip(sh):
    for i in range(6):
        x, y = 14 + (i % 2) * 88, 36 + (i // 2) * 78
        sh.rect_line(x, y, 84, 72, "l", 2, "stroke-width:1.2")
        if i in (0, 3, 4): sh.line(f"M{x + 8} {y + 8}H{x + 50}Q{x + 54} {y + 8} {x + 54} {y + 12}V{y + 20}Q{x + 54} {y + 24} {x + 50} {y + 24}H{x + 22}L{x + 16} {y + 30}V{y + 24}H{x + 12}Q{x + 8} {y + 24} {x + 8} {y + 20}Z", "l", "stroke-width:.8")
    sh.text(14, 274, "Titel: ..............................................", 7, "start")
opdracht("strip-tekenen", "Tekenopdracht: teken je eigen strip", "Zes vakjes, één verhaal. Wat gebeurt er?", strip, "9+", 2,
         ["Bedenk een kort verhaal met een begin, iets wat misgaat en een einde.", "Teken in elk vak één moment. Schrijf in de tekstballonnen wat de figuren zeggen.", "Geef je strip een titel."], "sprookjes", 30)
def vlag(sh):
    for i in range(4):
        x, y = 14 + (i % 2) * 90, 40 + (i // 2) * 110
        sh.seg(x + 4, y, x + 4, y + 100, "l", "stroke-width:1.6"); sh.rect_line(x + 6, y + 2, 76, 50, "l", 0, "stroke-width:1")
        sh.text(x + 6, y + 62, ["mijn familie", "mijn klas", "mijn club", "een verzonnen land"][i], 6.5, "start")
opdracht("ontwerp-je-eigen-vlag", "Tekenopdracht: ontwerp je eigen vlag", "Wat vertelt jouw vlag met kleuren en tekens?", vlag, "9+", 2,
         ["Bedenk waar de vlag voor is en wat erbij past: een dier, een ster, strepen, een kleur.", "Houd het eenvoudig: goede vlaggen kun je van ver herkennen.", "Ontwerp er vier en kies je favoriet."], "wereld")
