/** Interfaceteksten. Andere talen volgen als eigen bestand met dezelfde sleutels. */
export const nl = {
  lede: "Zelf getekende kleurplaten om online in te kleuren of te printen.",
  surprise: "Verras me",
  topic: "Onderwerp", all: "Alles", continent: "Werelddeel", wholeWorld: "Hele wereld", country: "Land",
  whole: (c: string) => `Heel ${c}`, holiday: "Feestdag", allHolidays: "Alle feestdagen",
  age: "Leeftijd", allAges: "Alle leeftijden", years: "jaar", yr: "jr",
  seasonNow: "Nu in het seizoen", soon: "Binnenkort", almostParty: "Bijna feest",
  emptyTitle: "Sjors zoekt nog", emptyText: "Er zijn nog geen platen voor deze combinatie. Kies een ander onderwerp of een andere leeftijd.", showAll: "Toon alle platen",
  note: "Alle platen zijn speciaal voor Kleurhoek getekend. Geen reclame, geen tracking-cookies.",
  back: "← Alle platen", howToColor: "Zo kleur je", free: "Vrij kleuren", byNumber: "Kleur op nummer",
  colors: "Kleuren", colorPerNumber: "Kleur bij elk nummer", eraser: "Gum", lines: "Lijnen",
  lineAuto: "Passend", lineThin: "Dun", lineNormal: "Normaal", lineThick: "Dik",
  extra: "Extra op de plaat", nameHint: "Tekst in bolle letters, die je ook kunt inkleuren", namePlaceholder: "Bijv. Fijne verjaardag, Sam!",
  learn: "Leerblad: woord om over te trekken en een telvraag",
  undo: "Ongedaan maken", reset: "Opnieuw", resetSure: "Zeker? Tik nog eens", print: "Printen",
  progress: (ok: number, total: number) => (ok === total ? "Alles goed gekleurd!" : `${ok} van ${total} vlakken goed`),
  party: "Helemaal goed! Oki is trots op je.",
  months: ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"],
  weekdays: ["zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"],
  around: "rond",
  login: "Inloggen", account: "Mijn account", logout: "Uitloggen", loading: "Even laden…",
  accountError: "Je account kan nu niet geladen worden. Probeer het later opnieuw.",
  name: "Naam", email: "E-mail", memberSince: "Lid sinds",
  accountPrivacy: "We bewaren alleen je naam en e-mailadres. Inloggen gaat via je eigen Google-, Apple- of Microsoft-account of een e-mailcode; we kennen geen wachtwoord.",
  deleteAccount: "Account verwijderen", deleteSure: "Zeker weten? Tik nog eens",
} as const;

export type Messages = typeof nl;
const all: Record<string, Messages> = { nl };
export const messages = (language: string): Messages => all[language] ?? nl;
