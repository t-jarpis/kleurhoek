import { de } from "./de";
import { en } from "./en";
import { es } from "./es";
import { fr } from "./fr";
import { it } from "./it";
import { pl } from "./pl";
import { pt } from "./pt";
import { sv } from "./sv";
import { da } from "./da";
import { nb } from "./nb";
import { fi } from "./fi";
import { cs } from "./cs";
import { sk } from "./sk";
import { hu } from "./hu";
import { ro } from "./ro";
import { el } from "./el";
import { bg } from "./bg";
import { hr } from "./hr";
import { sl } from "./sl";
import { et } from "./et";
import { lv } from "./lv";
import { lt } from "./lt";
import { uk } from "./uk";
import { tr } from "./tr";
import { sr } from "./sr";
import { mk } from "./mk";
import { sq } from "./sq";
import { is } from "./is";
import { latamSpanish } from "./es-419";

/** Interfaceteksten. Andere talen staan als eigen bestand met dezelfde sleutels ernaast. */
export const nl = {
  lede: "Eigen kleurplaten om online in te kleuren of te printen.",
  surprise: "Verras me",
  topic: "Onderwerp", all: "Alles", continent: "Werelddeel", wholeWorld: "Hele wereld", country: "Land",
  whole: (c: string) => `Heel ${c}`, holiday: "Feestdag", allHolidays: "Alle feestdagen",
  age: "Leeftijd", allAges: "Alle leeftijden", years: "jaar", yr: "jr",
  seasonNow: "Nu in het seizoen", soon: "Binnenkort", almostParty: "Bijna feest",
  emptyTitle: "Sjors zoekt nog", emptyText: "Er zijn nog geen platen voor deze combinatie. Kies een ander onderwerp of een andere leeftijd.", showAll: "Toon alle platen",
  note: "Alle platen zijn speciaal voor Kleurhoek gemaakt.",
  back: "← Alle platen", howToColor: "Zo kleur je", free: "Vrij kleuren", byNumber: "Kleur op nummer",
  colors: "Kleuren", colorPerNumber: "Kleur bij elk nummer", eraser: "Gum", lines: "Lijnen",
  lineAuto: "Passend", lineThin: "Dun", lineNormal: "Normaal", lineThick: "Dik",
  extra: "Extra op de plaat", nameHint: "Tekst in bolle letters, die je ook kunt inkleuren", namePlaceholder: "Bijv. Fijne verjaardag, Sam!",
  learn: "Leerblad: woord om over te trekken en een telvraag",
  undo: "Ongedaan maken", reset: "Opnieuw", resetSure: "Zeker? Tik nog eens", print: "Printen", printWhat: "Printen", printColored: "Ingekleurd", printBlank: "Leeg",
  progress: (ok: number, total: number) => (ok === total ? "Alles goed gekleurd!" : `${ok} van ${total} vlakken goed`),
  party: "Helemaal goed! Oki is trots op je.",
  months: ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"],
  weekdays: ["zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"],
  around: "rond",
  login: "Inloggen", account: "Mijn account", logout: "Uitloggen", loading: "Even laden…",
  accountError: "Je account kan nu niet geladen worden. Probeer het later opnieuw.",
  name: "Naam", email: "E-mail", memberSince: "Lid sinds",
  accountPrivacy: "We bewaren alleen je naam, je e-mailadres en je favorieten. Inloggen gaat via je eigen Google-, Apple- of Microsoft-account of een e-mailcode; we kennen geen wachtwoord.",
  toFridge: "Op de koelkast", onFridge: "Opgehangen op de koelkast",
  fridge: "Mijn koelkast", fridgeText: "Platen die je hebt opgehangen. Ze blijven op dit apparaat. Tik op een plaat om verder te kleuren.",
  takeOff: "Haal eraf", takeOffSure: "Zeker?",
  makeBook: "Maak een boekje", picking: "Platen kiezen…", stop: "Stoppen", viewBook: "Bekijk boekje",
  picked: (n: number) => (n === 1 ? "1 plaat gekozen" : `${n} platen gekozen`), pickHint: "Tik op platen om ze in je boekje te zetten.",
  book: "Jouw kleurboekje", backToPicking: "← Platen kiezen", cover: "Voorblad", bookOwner: "Van wie is het boekje?", bookOwnerPlaceholder: "Bijv. Sam",
  sheetKind: "Soort platen", bookNumbers: "Kleur op nummer, met kleurenlijst onderaan", bookLearn: "Leerblad met woord en telvraag",
  bookInfo: (n: number) => `Voorblad en ${n} ${n === 1 ? "plaat" : "platen"}, elk op een eigen A4.`, printBook: "Boekje printen",
  remove: (name: string) => `${name} weghalen`, page: (n: number) => `Blad ${n}`, myBook: "Mijn kleurboek", of: "van",
  bookCount: (n: number) => `${n} kleurplaten · Kleurhoek`, bookEmpty: "Nog geen platen gekozen. Ga terug en tik op de platen die je wilt.",
  kind: "Soort", allKinds: "Alles", kindColoring: "Kleurplaten", kindCrafts: "Knutselen", kindLearn: "Leren en spelen", kindDrawing: "Tekenen",
  kindNames: { kleurplaat: "Kleurplaat", knipplaat: "Knipplaat", bouwplaat: "Bouwplaat", spel: "Spel", vouwblad: "Vouwen", werkblad: "Werkblad", sjabloon: "Sjabloon", kaart: "Kaart", tekenles: "Tekenles" } as Record<string, string>,
  difficulty: ["", "makkelijk", "gemiddeld", "uitdagend"] as const, morePages: "Meer pagina's", howItWorks: "Zo werkt het", answers: "Antwoorden (voor ouders)", printPage: (n: number | string) => `Print pagina ${n}`,
  forParents: "Voor ouders", howToMake: "Zo maak je het", whatYouNeed: "Wat heb je nodig", optional: "mag ook",
  aboutMinutes: (n: number) => `ongeveer ${n} minuten`, adultHelp: "met hulp van een volwassene", paper: (g: number) => `papier van ${g} gram`,
  atPartner: (p: string) => `bij ${p}`,
  partnerDisclosure: "Partnerlinks: als je via deze links iets koopt, krijgt Kleurhoek een kleine vergoeding van de winkel. Jij betaalt hetzelfde. Zo blijven de platen gratis.",
  deleteAccount: "Account verwijderen", deleteSure: "Zeker weten? Tik nog eens",
  disclaimer: "Disclaimer", contact: "Contact", themes: "Thema's bij de maker",
  contactTitle: "Contact", contactLede: "Een vraag, een idee voor een plaat of iets wat niet werkt? Laat het ons weten. We reageren meestal binnen een paar werkdagen.",
  contactTopic: "Waar gaat het over?",
  contactTopics: { question: "Een vraag", idea: "Idee voor een plaat", bug: "Er werkt iets niet", partnership: "Samenwerken", copyright: "Auteursrecht", privacy: "Privacy en mijn gegevens" } as Record<string, string>,
  contactName: "Je naam", contactNameHint: "Mag ook leeg blijven", contactEmail: "Je e-mailadres", contactEmailHint: "Alleen om je te antwoorden",
  contactMessage: "Je bericht", contactSend: "Versturen", contactSending: "Versturen…",
  contactPrivacy: "We gebruiken je gegevens alleen om je te antwoorden en bewaren je bericht hooguit 12 maanden. Ben je jonger dan 16? Vraag dan een ouder om dit formulier in te vullen.",
  contactThanks: "Bedankt! We hebben je bericht ontvangen.", contactThanksText: "We antwoorden via e-mail. Kijk ook even in je map met ongewenste mail.",
  contactError: "Versturen lukte niet. Controleer je gegevens en probeer het opnieuw.", contactTooMany: "Je hebt al een paar berichten gestuurd. Probeer het over een uur opnieuw.",
  contactClosed: "Het contactformulier staat even uit. Probeer het later opnieuw.",
  themesTitle: "Thema's bij de maker", themesLede: "Kleurplaten van bekende figuren en plekken mogen we niet zelf maken of kopiëren. Veel makers bieden ze wel gratis aan op hun eigen site. Hier vind je de links, door ons nagekeken.",
  themesEmpty: "Er staan nog geen thema's klaar. Kom binnenkort terug!", themeSources: (n: number) => (n === 1 ? "1 link" : `${n} links`),
  byMaker: (m: string) => `van ${m}`, toMaker: "Bekijk bij de maker", allThemes: "← Alle thema's",
  marketsLabel: "Land en taal", langHint: "Deze pagina bestaat ook in het Nederlands.", langRead: "Lees in het Nederlands", close: "Sluiten",
  showMore: "Meer platen", shownOf: (n: number, total: number) => `${n.toLocaleString("nl-NL")} van ${total.toLocaleString("nl-NL")} platen`,
  themeNotice: (m: string) => `Deze kleurplaten zijn van ${m} en staan op hun eigen website. Kleurhoek linkt er alleen naar; wij hebben er geen invloed op.`,
  ownSpace: "Eigen omgeving", ownHint: "Voor een school, opvang of vereniging?", ownHintLink: "Vraag een eigen omgeving aan",
  ownTitle: "Kleurhoek voor je school, opvang of vereniging",
  ownLede: "Een eigen versie van Kleurhoek, met jullie naam, kleuren en precies de platen die passen bij waar jullie ze voor gebruiken. De tekeningen en het onderhoud komen van ons.",
  ownCta: "Vraag een eigen omgeving aan",
  ownForWho: "Voor wie",
  ownForWhoText: "Basisscholen, kinderopvang en bso, verenigingen, bibliotheken en bedrijven met een hoek voor kinderen, zoals een wachtkamer of een evenement.",
  ownBenefitsTitle: "Wat je krijgt",
  ownBenefits: [
    ["Een eigen adres", "Jullie omgeving staat op een eigen adres, zoals deregenboog.kleurhoek.nl. Een eigen domein kan ook."],
    ["Jullie huisstijl", "Jullie naam of logo en eigen kleuren. We zorgen dat alles goed leesbaar blijft."],
    ["Zonder onze naam op de platen", "Op onze eigen site staat kleurhoek.nl klein onder elke plaat, ook op papier. In jullie omgeving niet."],
    ["Het aanbod dat past", "Kies de onderwerpen, leeftijden, leerdoelen en soorten werkjes, of stel een eigen collectie samen."],
    ["Alleen de platen", "Als jullie dat willen zonder winkel- en partnerlinks, zodat alleen de platen overblijven."],
    ["Zelf bij te stellen", "Via Beheer op jullie eigen site zetten jullie leerdoelen, collecties en losse platen zelf aan of uit."],
    ["Alleen voor wie het adres heeft", "Jullie omgeving staat niet in zoekmachines. Wie het adres heeft, kan meteen aan de slag."],
  ] as [string, string][],
  ownStepsTitle: "Zo werkt het",
  ownSteps: [
    "Je vult het formulier hieronder in.",
    "We nemen binnen een paar werkdagen contact op, bespreken wat jullie nodig hebben en wat het kost.",
    "We zetten jullie omgeving klaar en je krijgt het adres. Daarna kunnen jullie meteen aan de slag.",
  ],
  ownFormTitle: "Aanvraag indienen",
  orgName: "Naam van de organisatie", orgKind: "Soort organisatie",
  orgKinds: { school: "School", opvang: "Kinderopvang of bso", vereniging: "Vereniging", bedrijf: "Bedrijf", overig: "Anders" } as Record<string, string>,
  orgCode: "Gewenst adres", orgCodeHint: "Wordt {host}. Kleine letters, cijfers en streepjes.", orgCodeExample: "jouw-naam", and: "en",
  // Onderwerppagina's en kruimelpad (ADR 0055).
  crumbs: "Kruimelpad",
  topicGroups: { onderwerp: "Per onderwerp", feestdag: "Per feestdag", leeftijd: "Per leeftijd", soort: "Per soort", werelddeel: "Per werelddeel" },
  topicH1: {
    onderwerp: (n: string) => `Kleurplaten ${n.toLowerCase()}`,
    feestdag: (n: string) => `Kleurplaten ${n}`,
    leeftijd: (n: string) => `Kleurplaten voor ${n}`,
    werelddeel: (n: string) => `Kleurplaten ${n}`,
  },
  kindH1: { kleurplaat: "Kleurplaten", knutselen: "Knutselplaten en bouwplaten", leren: "Werkbladen en spelletjes", tekenen: "Tekenlessen en sjablonen" },
  topicIntro: (title: string, count: number) => `${title}: ${count} gratis platen om te printen op A4 of online in te kleuren. Alle platen zijn speciaal voor Kleurhoek gemaakt.`,
  topicMeta: (title: string, count: number) => `${title}: ${count} gratis platen om te printen of online in te kleuren, per leeftijd.`,
  moreIn: (name: string) => `Meer ${name.toLowerCase()}`,
  seeAll: (n: number) => `Bekijk alle ${n}`,
  atelier: {
    name: "Atelier", on: "Atelier aan", off: "Atelier uit",
    hint: "Meer gereedschap voor wie graag tekent: penselen die binnen de lijnen blijven, elke kleur, licht en schaduw.",
    brushes: "Penselen", fill: "Vullen",
    tools: { potlood: "Potlood", stift: "Stift", waterverf: "Waterverf", airbrush: "Airbrush", gum: "Gum", vullen: "Vullen", verloop: "Verloop", patroon: "Patroon", pipet: "Pipet" },
    patterns: { stippen: "Stippen", strepen: "Strepen", ruitjes: "Ruitjes", golfjes: "Golfjes" },
    size: "Dikte", pressureHint: "Met een pen wordt de streek dikker als je harder drukt.",
    colorA: "Kleur", colorB: "Tweede kleur", hue: "Tint", saturation: "Verzadiging", lightness: "Licht", hex: "Hexcode",
    matching: "Past erbij", shades: "Lichter en donkerder", recent: "Laatst gebruikt", mood: "Sfeer",
    moods: { zonsondergang: "Zonsondergang", bos: "Bos", pastel: "Pastel", zee: "Zee", nacht: "Nacht" },
    sun: "Zon", sunHint: "Sleep de zon rond: elk gekleurd vlak krijgt licht aan die kant en schaduw aan de andere.",
    sunDirection: "Richting van het licht", sunStrength: "Kracht",
    directions: ["rechts", "rechtsonder", "onder", "linksonder", "links", "linksboven", "boven", "rechtsboven"],
    lineColor: "Lijnkleur", lineKinds: { inkt: "Zwart", sepia: "Sepia", kleur: "Eigen kleur", geen: "Geen lijnen" },
    zoomIn: "Inzoomen", zoomOut: "Uitzoomen", zoomFit: "Hele plaat",
    replay: "Terugkijken", replayTitle: "Zo heb je het gemaakt", saveVideo: "Opslaan als filmpje", saveImage: "Opslaan als afbeelding", close: "Sluiten",
    making: "Bezig…", noVideo: "Dit apparaat kan geen filmpje maken. Opslaan als afbeelding kan wel.",
    full: "Dit werk past niet meer op dit apparaat. Sla het op als afbeelding.",
  },
  pinSave: "Bewaar op Pinterest",
  pinHint: "Met een ingekleurd voorbeeld, zodat je hem later makkelijk terugvindt.",
  advent: {
    nav: "Aftelkalender",
    title: { kerst: "Aftelkalender naar kerst", oudnieuw: "Aftelkalender naar oud en nieuw" },
    lede: "Elke dag in december gaat er een deurtje open met een nieuwe plaat. Kleur hem online in of print hem.",
    meta: "Gratis aftelkalender met kleurplaten: elke dag in december een nieuwe plaat om te kleuren, te knutselen of te printen.",
    nights: { kerst: (n: number) => (n === 1 ? "Nog 1 nachtje tot kerst!" : `Nog ${n} nachtjes tot kerst`), oudnieuw: (n: number) => (n === 1 ? "Nog 1 nachtje tot oud en nieuw!" : `Nog ${n} nachtjes tot oud en nieuw`) },
    startsIn: (n: number) => (n <= 1 ? "Morgen gaat het eerste deurtje open." : `Over ${n} dagen gaat het eerste deurtje open.`),
    archive: "De kalender van afgelopen december: alle deurtjes zijn open.",
    door: (d: number) => `Deurtje ${d}`,
    locked: (d: number) => `Deurtje ${d}, nog dicht tot ${d} december`,
    openDoor: (d: number) => `Deurtje ${d} openen`,
    teaser: "Elke dag in december een nieuwe plaat achter een deurtje.",
    teaserCta: "Naar de aftelkalender",
  },
  packs: {
    nav: "Lespakketten",
    title: "Lespakketten",
    lede: "Kant-en-klare sets per onderwerp en leeftijd: kleurplaten om mee te beginnen, daarna werkbladen en iets om te knutselen. Print alles in één keer als boekje.",
    meta: "Gratis lespakketten met kleurplaten, werkbladen en knutselplaten per onderwerp en leeftijd, voor school en thuis.",
    packTitle: (topic: string, age: string) => `Lespakket ${topic.toLowerCase()}, ${age}`,
    packMeta: (topic: string, age: string, n: number) => `Gratis lespakket ${topic.toLowerCase()} voor ${age}: ${n} platen om te kleuren, te leren en te knutselen. In één keer te printen.`,
    intro: (n: number) => `${n} platen in deze volgorde: eerst kleuren, dan leren en knutselen.`,
    forTeacher: "Voor de leerkracht",
    teacherText: "Begin met een kleurplaat als rustige start. De werkbladen oefenen de leerdoelen hieronder; de knutselplaat is voor het eind van de les of erbij in de hoek. Elke plaat heeft op zijn eigen pagina uitleg en wat je nodig hebt.",
    goals: "Leerdoelen",
    contents: "In dit pakket",
    printAll: "Print het hele pakket",
    plates: (n: number) => (n === 1 ? "1 plaat" : `${n} platen`),
    forAge: (age: string) => `Voor ${age}`,
  },
  together: {
    nav: "Samen kleuren",
    button: "Samen kleuren",
    title: "Samen kleuren",
    lede: "Kleur dezelfde plaat tegelijk op twee schermen, bijvoorbeeld met opa en oma op afstand. Je hebt geen account nodig en we bewaren niets.",
    meta: "Kleur samen dezelfde kleurplaat op twee schermen, op afstand en zonder account.",
    start: "Begin samen",
    join: "Doe mee",
    code: "Code",
    codeHint: "Vul de code van vier letters in die de ander ziet.",
    share: "Geef deze code aan wie meedoet",
    copyLink: "Kopieer link",
    copied: "Link gekopieerd",
    stop: "Stoppen",
    waiting: "Wachten op de ander…",
    others: (n: number) => (n === 1 ? "1 ander kleurt mee" : `${n} anderen kleuren mee`),
    notFound: "Deze code bestaat niet (meer). Vraag een nieuwe.",
    expires: "Kleurt er 30 minuten niemand, dan stopt het samen kleuren vanzelf. Je werk blijft op dit apparaat staan.",
    offline: "Even geen verbinding. We proberen het opnieuw.",
    replace: "Je doet mee met de plaat van de ander. Wat je zelf op deze plaat had gekleurd, wordt vervangen.",
    howTitle: "Zo werkt het",
    how: ["Open een plaat en tik op Samen kleuren.", "Geef de code of de link aan wie meedoet.", "Die vult de code hier in of opent de link. Wat de een kleurt, ziet de ander meteen."],
  },
  metaPlateTitle: (name: string, kind: string) => `${name} – ${kind.toLowerCase()}`,
  metaThemeTitle: (name: string) => `Kleurplaten ${name}`,
  metaTheme: (name: string, maker: string) => `Kleurplaten van ${name}, gratis bij ${maker}.`,
  metaPlate: (name: string, kind: string) => `${kind} ${name}: gratis online inkleuren of printen op A4.`,
  mlTitle: "Mail mij als er iets nieuws is", mlIntro: "Nieuwe platen, op tijd voor een feestdag, of af en toe een nieuwsbrief. Afmelden kan met één klik.", mlEmail: "E-mailadres", mlTopics: "Waarover?", mlTopicNames: {"nieuwe-platen": "Nieuwe platen (hooguit één keer per week)", "feestdagen": "Platen voor een feestdag die eraan komt", "nieuwsbrief": "De nieuwsbrief (af en toe)"} as Record<string, string>, mlAdult: "Ik ben 16 jaar of ouder", mlSubmit: "Aanmelden", mlSending: "Aanmelden…", mlPrivacy: "We gebruiken je adres alleen voor deze mails.", mlCheckTitle: "Kijk in je mail", mlCheckText: "We hebben je een mail gestuurd. Klik op de knop daarin om je aanmelding te bevestigen.", mlError: "Dat lukte niet. Controleer je e-mailadres, kies een onderwerp en zet het vinkje.", mlBusy: "Even te vaak geprobeerd. Probeer het straks opnieuw.", mlConfirming: "Je aanmelding wordt bevestigd…", mlConfirmed: "Je bent aangemeld", mlConfirmedText: "Je krijgt voortaan onze mails. Afmelden kan onderaan elke mail.", mlConfirmInvalid: "Deze link werkt niet meer. Meld je opnieuw aan; de link in de mail werkt 7 dagen.", mlPrefsTitle: "Je mail-instellingen", mlPrefsFor: "Voor", mlSave: "Opslaan", mlSaved: "Opgeslagen.", mlUnsubscribe: "Afmelden voor alle mails", mlUnsubscribeSure: "Weet je het zeker? Klik nog een keer om je af te melden.", mlUnsubscribed: "Je bent afgemeld", mlUnsubscribedText: "Je krijgt geen mails meer van ons, en je adres is verwijderd.", mlLinkInvalid: "Deze link werkt niet meer. Gebruik de link onderaan je laatste mail.", mlAccount: "Mail", mlAccountHint: "Kies welke mails je op je e-mailadres wilt krijgen. Niets aangevinkt: geen mails.",
  favSave: "Bewaar", favSaved: "Favoriet", favorites: "Favorieten", favLoginLink: "Log in", favLoginHint: "om je favorieten op al je apparaten te bewaren.", accBenefitsTitle: "Wat je met een account kunt", accFavorites: "Bekijk je favorieten",
  accBenefits: [["Favorieten op al je apparaten", "Bewaar platen met het hartje. Ze staan dan op je telefoon, tablet en computer."], ["Mail die je zelf kiest", "Een seintje bij nieuwe platen of een feestdag, of af en toe de nieuwsbrief."], ["Kleuren kan altijd zonder", "Kinderen kleuren en printen gewoon zonder in te loggen."]] as [string, string][],
  mgFooter: "Beheer",
  goal: "Leerdoel", allGoals: "Alle leerdoelen", mgTitle: (name: string) => `Aanbod van ${name}`, mgIntro: "Kies wat er op jullie site staat. Wijzigingen zijn binnen een paar minuten zichtbaar voor iedereen op de site.", mgGoals: "Leerdoelen", mgGoalsHint: "Alleen platen met minstens één van deze leerdoelen. Niets aangevinkt: alle leerdoelen.", mgCollections: "Collecties", mgCollectionsHint: "Alleen platen uit deze collecties. Niets aangevinkt: alle platen.", mgPlates: "Losse platen", mgPlatesHint: "Zet platen uit die je niet wilt tonen.", mgSearch: "Zoek een plaat", mgShown: "Zichtbaar", mgHidden: "Verborgen", mgSave: "Opslaan", mgSaving: "Opslaan…", mgSaved: "Opgeslagen.", mgError: "Opslaan lukte niet. Probeer het opnieuw.", mgNotManager: "Je bent geen beheerder van deze site. Vraag Kleurhoek om je toe te voegen.", mgLink: (name: string) => `Aanbod van ${name} beheren`, mgCount: (n: number, total: number) => `${n} van ${total} platen zichtbaar`, mgNoMatch: "Geen platen gevonden.", mgPlatesIn: "platen",
  orgChildren: "Aantal kinderen", orgChildrenHint: "Een schatting is genoeg", orgSite: "Website van de organisatie",
  orgMessage: "Wat zouden jullie graag willen?", orgMessagePlaceholder: "Bijvoorbeeld: voor groep 1 tot en met 4, met ons logo, zonder knutselwerk.",
  orgSend: "Aanvraag versturen", optionalField: "mag leeg",
  orgThanks: "Bedankt voor je aanvraag!", orgThanksText: "We nemen binnen een paar werkdagen contact met je op via e-mail.",
  themeProducts: "Spullen bij dit thema", toShop: "Bekijk in de winkel",
  metaDisclaimer: "Wat je met de kleurplaten van Kleurhoek mag doen, hoe we naar andere sites linken en hoe je ons iets meldt.",
  metaContact: "Stuur Kleurhoek een vraag, een idee voor een kleurplaat of een melding.",
  metaThemes: "Kleurplaten van bekende figuren en plekken, gratis bij de makers zelf. Door Kleurhoek nagekeken.",
  metaOwnTitle: "Eigen omgeving voor je school of opvang",
  metaOwn: "Een eigen versie van Kleurhoek met jullie naam, kleuren en aanbod. Vraag hem aan.",
  metaBook: "Kleurboekje",

} as const;

/** Zelfde vorm als nl, maar met gewone strings: elke taal vult dezelfde sleutels met eigen tekst. */
type Widen<T> = T extends string ? string
  : T extends (...a: infer A) => infer R ? (...a: A) => Widen<R>
  : T extends readonly unknown[] ? { readonly [K in keyof T]: Widen<T[K]> }
  : T extends object ? { [K in keyof T]: Widen<T[K]> } : T;
export type Messages = Widen<typeof nl>;
// Elke taal een eigen bestand met dezelfde sleutels (ADR 0029). Alleen type-imports terug naar nl.ts.
const all: Record<string, Messages> = { nl, de, en, es, fr, it, pl, pt, sv, da, nb, fi, cs, sk, hu, ro, el, bg, hr, sl, et, lv, lt, uk, tr, sr, mk, sq, is };

/** Zelfde teksten met een andere schrijfwijze: elke tekst (ook wat een functie teruggeeft) gaat door `fix`. */
function variant<T>(value: T, fix: (s: string) => string): T {
  if (typeof value === "string") return fix(value) as T;
  if (typeof value === "function") return ((...a: unknown[]) => variant((value as (...a: unknown[]) => unknown)(...a), fix)) as T;
  if (Array.isArray(value)) return value.map((v) => variant(v, fix)) as T;
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, variant(v, fix)])) as T;
  return value;
}
/** Amerikaanse spelling en Letter-papier voor en-US (ADR 0047). */
export const usSpelling = (s: string) => s
  .replace(/([Cc])olour/g, "$1olor").replace(/([Ff])avourite/g, "$1avorite").replace(/([Oo])rganisation/g, "$1rganization")
  .replace(/on A4\b/g, "on letter paper").replace(/A4 sheet/g, "letter-size sheet").replace(/\bA4\b/g, "letter");
/** Zwitsers Duits schrijft geen ß (ADR 0047). */
export const swissSpelling = (s: string) => s.replace(/ß/g, "ss");
// Varianten per markt: de sleutel is de marktcode, de taal is de terugval.
all["en-us"] = variant(en, usSpelling);
all["de-ch"] = variant(de, swissSpelling);
all["de-li"] = all["de-ch"];
// Letter-papier in Canada (ADR 0050); Canadees Engels houdt de Britse spelling.
all["en-ca"] = variant(en, (s) => s.replace(/on A4\b/g, "on letter paper").replace(/A4 sheet/g, "letter-size sheet").replace(/\bA4\b/g, "letter"));
all["fr-ca"] = variant(fr, (s) => s.replace(/\bA4\b/g, "format lettre"));
// Spaans voor Latijns-Amerika en de VS: ustedes in plaats van vosotros (ADR 0050).
all["es-mx"] = latamSpanish(es, true);
all["es-co"] = all["es-mx"];
all["es-us"] = all["es-mx"];
all["es-ar"] = latamSpanish(es, false);

/** Teksten voor een markt ("en-us") of een taal ("en"). Een markt zonder eigen variant krijgt zijn taal. */
export const messages = (marketOrLanguage: string): Messages => {
  const k = marketOrLanguage.toLowerCase();
  return all[k] ?? all[k.slice(0, 2)] ?? nl;
};
