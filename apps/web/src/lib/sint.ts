import { intocht, SINT_MARKETS, sintDates, sintDoorSlugs } from "@kleurhoek/catalog-data/calendar";

import type { Door } from "./advent";
import type { PlateItem } from "./types";

/**
 * Sinterklaaskalender (ADR 0065): een deurtje per dag van de intocht tot pakjesavond, alleen in de Nederlandstalige
 * markten. Zelfde component als de aftelkalender (ADR 0058), met een ander aantal deurtjes. De teksten staan hier,
 * want de pagina bestaat alleen in het Nederlands.
 */

// Datums en volgorde van de deurtjes komen uit catalog-data, zodat Social en de mail hetzelfde deurtje kennen.
export { intocht, SINT_MARKETS, sintDates };
export const hasSintCalendar = (market: string) => market.toLowerCase() in SINT_MARKETS;

const MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"];
const DAY = 86_400_000;

export const dateLabel = (date: string) => `${Number(date.slice(8, 10))} ${MONTHS[Number(date.slice(5, 7)) - 1]}`;

export function sintDoors(plates: PlateItem[], total: number): Door[] {
  const bySlug = new Map(plates.filter((p) => p.holiday === "sinterklaas").map((p) => [p.slug, p]));
  return sintDoorSlugs([...bySlug.keys()], total).map(({ day, slug }) => ({ day, plate: bySlug.get(slug)! }));
}

/** Welk seizoen, hoeveel deurtjes open, en hoe lang nog. `today` is JJJJ-MM-DD in de tijdzone van de markt. */
export function sintOpen(today: string, market: string) {
  const y = Number(today.slice(0, 4)), m = Number(today.slice(5, 7));
  const year = m >= 11 ? y : y - 1;
  const dates = sintDates(year, market);
  // In november vóór de intocht: nog dicht. Van januari tot en met oktober: vorig jaar, alles open.
  if (m >= 11 && today < dates[0]!) {
    const days = Math.round((Date.parse(dates[0]!) - Date.parse(today)) / DAY);
    return { year, dates, open: 0, today: null as number | null, nightsTo: null as number | null, daysToStart: days };
  }
  const i = dates.indexOf(today);
  if (i < 0) return { year, dates, open: dates.length, today: null, nightsTo: null, daysToStart: null };
  return { year, dates, open: i + 1, today: i + 1, nightsTo: dates.length - 1 - i || null, daysToStart: null };
}

/**
 * Sinterklaasboekjes: alle Sinterklaasplaten van één leeftijd in één boekje (de bestaande boekjespagina). Een
 * leeftijd met minder dan drie platen gaat op in de leeftijd eronder, zodat er geen boekje van één plaat is.
 */
export function sintBooks(plates: PlateItem[], ages: { slug: string; level: number; name: string }[], max = 30) {
  const sint = plates.filter((p) => p.holiday === "sinterklaas");
  const groups: { ages: { slug: string; name: string }[]; slugs: string[] }[] = [];
  for (const age of [...ages].sort((a, b) => a.level - b.level)) {
    const slugs = sint.filter((p) => p.age === age.slug).map((p) => p.slug);
    if (slugs.length) groups.push({ ages: [age], slugs });
  }
  for (let i = groups.length - 1; i > 0; i--) {
    if (groups[i]!.slugs.length >= 3) continue;
    groups[i - 1]!.ages.push(...groups[i]!.ages);
    groups[i - 1]!.slugs.push(...groups[i]!.slugs);
    groups.splice(i, 1);
  }
  return groups.map((g) => ({ label: g.ages.length > 1 ? `Vanaf ${parseInt(g.ages[0]!.slug, 10)} jaar` : g.ages[0]!.name, slugs: g.slugs.slice(0, max) }));
}

/** Op de voorpagina: van 1 november tot en met pakjesavond. */
export function sintTeaser(today: string, market: string): boolean {
  if (!hasSintCalendar(market) || today.slice(5, 7) < "11") return false;
  const dates = sintDates(Number(today.slice(0, 4)), market);
  return today <= dates[dates.length - 1]!;
}

export const SINT_TEXT = {
  nav: "Sinterklaaskalender",
  title: "Sinterklaaskalender",
  lede: "Van de intocht tot pakjesavond elke dag een deurtje met een nieuwe Sinterklaasplaat. Kleur hem online in of print hem.",
  meta: "Gratis Sinterklaaskalender met kleurplaten: van de intocht tot pakjesavond elke dag een nieuwe plaat om te kleuren, te knutselen of te printen.",
  nights: (n: number) => (n === 1 ? "Nog 1 nachtje slapen tot pakjesavond!" : `Nog ${n} nachtjes slapen tot pakjesavond`),
  eve: "Vandaag is het pakjesavond!",
  startsIn: (n: number, date: string) => (n <= 1 ? "Morgen is de intocht: dan gaat het eerste deurtje open." : `Op ${date} is de intocht: dan gaat het eerste deurtje open.`),
  archive: "De kalender van afgelopen Sinterklaas: alle deurtjes zijn open.",
  locked: (d: number, date: string) => `Deurtje ${d}, nog dicht tot ${date}`,
  teaser: "Van de intocht tot pakjesavond elke dag een nieuwe Sinterklaasplaat.",
  mailTitle: "Elke ochtend het deurtje in je mail",
  mailIntro: "Van de intocht tot pakjesavond sturen we je elke ochtend om 7 uur de plaat van die dag. Daarna stopt het vanzelf. Afmelden kan met één klik.",
  teaserCta: "Naar de Sinterklaaskalender",
  bookTitle: "Sinterklaasboekje",
  bookIntro: "Liever alles in één keer? Print alle Sinterklaasplaten voor één leeftijd als boekje, met een voorblad.",
  book: (label: string, n: number) => `${label} (${n} platen)`,
};

/** Cadeaulabels en naamkaartjes (ADR 0067). Alleen Nederlands: de pagina is er alleen in nl-NL en nl-BE. */
export const GIFT_TEXT = {
  nav: "Cadeaulabels met naam",
  title: "Cadeaulabels en naamkaartjes met eigen naam",
  lede: "Typ de namen, kies labels voor de pakjes of naamkaartjes voor aan tafel en print het vel. Daarna kleuren, knippen en ophangen of neerzetten.",
  meta: "Gratis cadeaulabels en naamkaartjes voor pakjesavond, met eigen naam en tekeningetjes om in te kleuren. Print op A4.",
  kind: "Wat wil je maken?",
  labels: "Labels voor de pakjes",
  cards: "Naamkaartjes voor aan tafel",
  names: "Namen",
  namesPlaceholder: "Bijvoorbeeld:\nNoor\nSem",
  namesHint: "Eén naam per regel (of met komma's). Leeg laten mag ook: dan schrijf je zelf.",
  fromLabel: "Van",
  defaultFrom: "Sint en Piet",
  for: "Voor",
  from: "Van",
  print: "Printen",
  privacy: "De namen blijven op dit apparaat: we sturen ze nergens heen en bewaren ze niet.",
  teaser: "Labels voor de pakjes, met de naam erop",
};

