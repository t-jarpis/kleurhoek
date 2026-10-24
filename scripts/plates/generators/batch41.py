"""Batch 41: taalwerkbladen (met antwoordblad)."""
import random
from lib_gen import *

def lijst(slug, name, intro, items, age, diff, steps, box_w=50):
    def page(ans):
        sh = Sheet(); title(sh, "Antwoorden" if ans else cap(name.split(": ", 1)[-1]), 16)
        sh.text(100, 28, intro, 6.4)
        two = box_w >= 80
        step = min(36 if two else 21, 226 / len(items))
        for i, (q, a) in enumerate(items):
            y = 46 + i * step
            sh.text(14, y, f"{i + 1}.", 7, "start"); sh.text(26, y, q, 8.5, "start")
            if two:
                sh.seg(26, y + 15, 184, y + 15, "guide")
                if ans: sh.text(28, y + 13, a, 8, "start")
            else:
                sh.seg(184 - box_w, y + 1.5, 184, y + 1.5, "guide")
                if ans: sh.text(184 - box_w / 2, y, a, 8)
        return sh
    write(OUT, slug, page(False), {"category": "leren", "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 15, "materials": POTLOOD,
        "i18n": {"nl": {"name": name, "steps": steps + ["Kijk na met het antwoordblad."]}}}, [("antwoorden", "Antwoorden", page(True))])

lijst("taal-meervoud-maken", "Taal: één en meer", "Schrijf hoe je het zegt als er meer zijn.",
      [("één boek", "boeken"), ("één kat", "katten"), ("één huis", "huizen"), ("één appel", "appels"), ("één boom", "bomen"), ("één fiets", "fietsen"),
       ("één tafel", "tafels"), ("één vis", "vissen"), ("één schoen", "schoenen"), ("één kind", "kinderen")], "6-9", 2,
      ["Zeg het woord hardop met 'twee' ervoor: twee boek…?", "De meeste woorden krijgen -en of -s. Soms verandert er nog iets: huis wordt huizen.", "Schrijf het woord voor meer dan één op de lijn."])
lijst("taal-verkleinwoorden", "Taal: verkleinwoorden", "Maak het klein: schrijf het verkleinwoord.",
      [("huis", "huisje"), ("boom", "boompje"), ("bal", "balletje"), ("vis", "visje"), ("stoel", "stoeltje"), ("raam", "raampje"),
       ("kat", "katje"), ("ster", "sterretje"), ("koe", "koetje"), ("bloem", "bloemetje")], "6-9", 2,
      ["Zeg het woord hardop met 'een klein' ervoor.", "Er komt -je, -tje, -pje of -etje achter: huis wordt huisje, boom wordt boompje.", "Schrijf het verkleinwoord op de lijn."])
lijst("taal-de-of-het", "Taal: de of het?", "Schrijf de of het voor elk woord.",
      [("... huis", "het"), ("... tafel", "de"), ("... boek", "het"), ("... stoel", "de"), ("... paard", "het"), ("... hond", "de"),
       ("... meisje", "het"), ("... raam", "het"), ("... school", "de"), ("... water", "het")], "9+", 2,
      ["Zeg het woord hardop met de en met het ervoor: wat klinkt goed?", "Tip: verkleinwoorden (meisje, katje) krijgen altijd het.", "Weet je het niet? Zoek het op in een woordenboek."], 24)
lijst("taal-rijmwoorden", "Taal: rijmwoorden", "Bedenk een woord dat rijmt. Er kan meer goed zijn!",
      [("kat", "mat, rat, bad"), ("boom", "droom, room"), ("vis", "mis, kies? nee: lis"), ("maan", "baan, staan"), ("bed", "pet, net"), ("muis", "huis, kruis"),
       ("zon", "ton, bon"), ("taart", "kaart, paard"), ("beer", "peer, keer"), ("bal", "val, stal")][:0] or
      [("kat", "mat, rat"), ("boom", "droom, room"), ("maan", "baan, staan"), ("bed", "pet, net"), ("muis", "huis, kruis"), ("zon", "ton, bon"),
       ("taart", "kaart, paard"), ("beer", "peer, keer"), ("bal", "val, stal"), ("roos", "doos, boos")], "6-9", 1,
      ["Zeg het woord hardop en luister naar het eind.", "Verander de eerste letter: kat wordt mat, rat, gat …", "Schrijf een rijmwoord op de lijn. Het antwoordblad geeft voorbeelden."], 50)
r = random.Random(41)
def alfa():
    groepen = [["vis", "appel", "maan"], ["kat", "beer", "zon", "huis"], ["tafel", "deur", "lamp", "bed"], ["peer", "ijs", "nest", "fiets", "uil"], ["oma", "egel", "giraf", "raket", "wolk"]]
    items = []
    for g in groepen:
        sh = g[:]; r.shuffle(sh)
        items.append((", ".join(sh), ", ".join(sorted(g))))
    return items
lijst("taal-alfabetische-volgorde", "Taal: op alfabetische volgorde", "Zet de woorden op volgorde van het alfabet (a, b, c …).", alfa(), "6-9", 2,
      ["Kijk naar de eerste letter van elk woord.", "Welke letter komt het eerst in het alfabet? Dat woord schrijf je eerst.", "Schrijf zo alle woorden op volgorde."], 84)
def zinnen():
    zs = ["De kat slaapt op de bank.", "Ik eet een appel.", "Wij gaan naar school.", "Het regent buiten.", "Mijn broer speelt voetbal.", "De vogel zingt in de boom."]
    items = []
    for z in zs:
        w = z.rstrip(".").split(); sh = w[:]
        while sh == w: r.shuffle(sh)
        items.append((" / ".join(x.lower() if i else x.lower() for i, x in enumerate(sh)), z))
    return items
lijst("taal-zinnen-maken", "Taal: maak een zin", "Zet de woorden op volgorde. Hoofdletter en punt niet vergeten!", zinnen(), "6-9", 2,
      ["Lees alle woorden.", "Zoek wie of wat iets doet, en wat er gebeurt.", "Schrijf de zin op de lijn, met een hoofdletter aan het begin en een punt aan het eind."], 84)
