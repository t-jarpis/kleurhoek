"use strict";
/**
 * Leerdoelen (ADR 0036): algemene doelen waarop een school, bso of bibliotheek kan filteren. Ze volgen uit wat een
 * plaat is (soort, onderwerp, feestdag, wereld) en uit de naam (slug) voor rekenen en taal. Geen invoer per plaat:
 * een nieuwe plaat krijgt ze vanzelf. Uitzonderingen per plaat staan in goals-overrides.json.
 */
const GOALS = ["rekenen", "taal", "motoriek", "knutselen", "ruimtelijk", "tekenen", "wereld", "seizoenen", "samenspelen"];

/** Namen per taal. Kort, zoals op een filterknop. */
const GOAL_NAMES = {
  nl: { rekenen: "Rekenen en getallen", taal: "Taal en letters", motoriek: "Fijne motoriek", knutselen: "Knippen, vouwen en plakken", ruimtelijk: "Vormen, ruimte en logica", tekenen: "Tekenen en creativiteit", wereld: "Wereld en natuur", seizoenen: "Feestdagen en seizoenen", samenspelen: "Samen spelen" },
  de: { rekenen: "Rechnen und Zahlen", taal: "Sprache und Buchstaben", motoriek: "Feinmotorik", knutselen: "Schneiden, Falten und Kleben", ruimtelijk: "Formen, Raum und Logik", tekenen: "Zeichnen und Kreativität", wereld: "Welt und Natur", seizoenen: "Feste und Jahreszeiten", samenspelen: "Gemeinsam spielen" },
  en: { rekenen: "Maths and numbers", taal: "Language and letters", motoriek: "Fine motor skills", knutselen: "Cutting, folding and gluing", ruimtelijk: "Shapes, space and logic", tekenen: "Drawing and creativity", wereld: "World and nature", seizoenen: "Holidays and seasons", samenspelen: "Playing together" },
  fr: { rekenen: "Calcul et nombres", taal: "Langue et lettres", motoriek: "Motricité fine", knutselen: "Découper, plier et coller", ruimtelijk: "Formes, espace et logique", tekenen: "Dessin et créativité", wereld: "Monde et nature", seizoenen: "Fêtes et saisons", samenspelen: "Jouer ensemble" },
  es: { rekenen: "Cálculo y números", taal: "Lengua y letras", motoriek: "Motricidad fina", knutselen: "Recortar, doblar y pegar", ruimtelijk: "Formas, espacio y lógica", tekenen: "Dibujo y creatividad", wereld: "Mundo y naturaleza", seizoenen: "Fiestas y estaciones", samenspelen: "Jugar juntos" },
  it: { rekenen: "Calcolo e numeri", taal: "Lingua e lettere", motoriek: "Motricità fine", knutselen: "Ritagliare, piegare e incollare", ruimtelijk: "Forme, spazio e logica", tekenen: "Disegno e creatività", wereld: "Mondo e natura", seizoenen: "Feste e stagioni", samenspelen: "Giocare insieme" },
  pl: { rekenen: "Liczenie i liczby", taal: "Język i litery", motoriek: "Motoryka mała", knutselen: "Wycinanie, składanie i klejenie", ruimtelijk: "Kształty, przestrzeń i logika", tekenen: "Rysowanie i kreatywność", wereld: "Świat i przyroda", seizoenen: "Święta i pory roku", samenspelen: "Wspólna zabawa" },
};
/** Naam van een leerdoel in een taal, met Engels en dan Nederlands als terugval. */
const goalName = (goal, language) => (GOAL_NAMES[language] ?? GOAL_NAMES.en)[goal] ?? GOAL_NAMES.nl[goal] ?? goal;

const MATH = /(^|-)(rekenen|reken|tellen|tel|tafels?|getal|getallen|getallenlijn|sudoku|geld|breuken|klokkijken|klok|piramides?|rekenpiramides|dubbelen|halveren|splitsen|groter|dobbelrace|domino|cijfers|cijfercode|optellen|aftrekken|sommen|verhaaltjessommen|rekenbingo|meer-of-minder|getallentrein|stippen|binaire)(-|$)/;
const LANGUAGE = /(^|-)(taal|letters?|schrijven|woord|woorden|woordzoeker|rijm|rijmwoorden|geheimschrift|morsecode|alfabet|alfabetische|lezen|letterslinger|letterbingo|kamertje|engels|verhalendobbelsteen)(-|$)|^dagen-en-maanden$/;
const SPATIAL = /(^|-)(doolhof|tangram|patronen|schaduw|puzzel|symmetrie|spiegel|vormen|kubus|balk|prisma|achtvlak|pixelkunst|verschillen|logische|binaire|andere-helft|sorteren)(-|$)/;
const FINE_MOTOR = /(^|-)(verbind-de-punten|doolhof|overtrekken|knippen|schrijven|pixelkunst|plakken)(-|$)/;
const SOCIAL = /(^|-)(emotie|emotiedobbelsteen|samen|vriendschap)(-|$)/;

const NATURE = new Set(["dieren", "natuur", "zee", "wereld", "ruimte", "boerderij", "dinos"]);

/** @param {{ slug: string; kind: string; category: string; holiday?: string | null; continent?: string | null }} p */
function learningGoals(p, overrides = {}) {
  const goals = new Set();
  const k = p.kind;
  if (["kleurplaat", "knipplaat", "vouwblad", "bouwplaat", "tekenles", "sjabloon"].includes(k) || FINE_MOTOR.test(p.slug)) goals.add("motoriek");
  if (["knipplaat", "bouwplaat", "vouwblad", "kaart"].includes(k)) goals.add("knutselen");
  if (["bouwplaat", "vouwblad"].includes(k) || p.category === "vormen" || p.category === "patronen" || SPATIAL.test(p.slug)) goals.add("ruimtelijk");
  if (["tekenles", "sjabloon"].includes(k) || /teken/.test(p.slug)) goals.add("tekenen");
  if (k === "spel" || SOCIAL.test(p.slug)) goals.add("samenspelen");
  if (MATH.test(p.slug)) goals.add("rekenen");
  if (LANGUAGE.test(p.slug)) goals.add("taal");
  if (NATURE.has(p.category) || p.continent) goals.add("wereld");
  if (p.holiday || p.category === "feest") goals.add("seizoenen");
  const o = overrides[p.slug];
  if (o) { for (const g of o.add ?? []) goals.add(g); for (const g of o.remove ?? []) goals.delete(g); }
  return GOALS.filter((g) => goals.has(g));
}

module.exports = { GOALS, GOAL_NAMES, goalName, learningGoals };
