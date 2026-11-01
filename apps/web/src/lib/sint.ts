import type { Door } from "./advent";
import type { PlateItem } from "./types";

/**
 * Sinterklaaskalender (ADR 0065): een deurtje per dag van de intocht tot pakjesavond, alleen in de Nederlandstalige
 * markten. Zelfde component als de aftelkalender (ADR 0058), met een ander aantal deurtjes. De teksten staan hier,
 * want de pagina bestaat alleen in het Nederlands.
 */

/** Pakjesavond per markt: in Nederland 5 december, in België de ochtend van 6 december. */
export const SINT_MARKETS: Record<string, number> = { "nl-nl": 5, "nl-be": 6 };
export const hasSintCalendar = (market: string) => market.toLowerCase() in SINT_MARKETS;

const MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"];
const DAY = 86_400_000;
const utc = (y: number, m: number, d: number) => Date.UTC(y, m - 1, d);
const iso = (t: number) => new Date(t).toISOString().slice(0, 10);

/** De intocht: de eerste zaterdag na 11 november (Sint-Maarten). */
export function intocht(year: number): string {
  let t = utc(year, 11, 12);
  while (new Date(t).getUTCDay() !== 6) t += DAY;
  return iso(t);
}

/** Alle datums van de kalender, van de intocht tot en met pakjesavond. */
export function sintDates(year: number, market: string): string[] {
  const eve = utc(year, 12, SINT_MARKETS[market.toLowerCase()] ?? 5);
  const out: string[] = [];
  for (let t = Date.parse(intocht(year)); t <= eve; t += DAY) out.push(iso(t));
  return out;
}

export const dateLabel = (date: string) => `${Number(date.slice(8, 10))} ${MONTHS[Number(date.slice(5, 7)) - 1]}`;

/** Deze platen eerst, in deze volgorde; de intocht vooraan en pakjesavond als laatste. */
const FIRST = ["stoomboot-komt-aan", "intocht-van-sinterklaas", "sint-en-piet-zwaaien", "sinterklaas-portret", "roetveegpiet-zwaait",
  "pakjesboot-in-de-haven", "sint-rijdt-op-zijn-paard", "amerigo-en-de-wortel", "schoen-bij-de-kachel", "piet-maakt-muziek",
  "stapel-cadeautjes", "sinterklaas-leest-voor", "warme-chocolademelk",
  "schoen-zetten", "piet-met-de-zak", "pepernotenbakkerij", "chocoladeletter", "sinterklaas-op-het-dak", "mijter-om-op-te-zetten",
  "piet-in-de-schoorsteen", "het-grote-boek", "pieten-op-het-dak", "surprise-maken", "schoen", "sinterklaas", "pakjesboot",
  "sinterklaas-glas-in-lood", "sinterklaaskaart-schoen", "surprise-mijterdoosje", "harmonica-uitnodiging-pakjesavond"];
const LAST = "pakjesavond";

export function sintDoors(plates: PlateItem[], total: number): Door[] {
  const sint = plates.filter((p) => p.holiday === "sinterklaas");
  const rank = (s: string) => { const i = FIRST.indexOf(s); return i < 0 ? 99 : i; };
  const last = sint.find((p) => p.slug === LAST);
  const rest = sint.filter((p) => p !== last).sort((a, b) => rank(a.slug) - rank(b.slug));
  const list = [...rest.slice(0, last ? total - 1 : total), ...(last ? [last] : [])];
  // Te weinig platen: de laatste plek blijft pakjesavond, de rest schuift op.
  return list.map((plate, i) => ({ day: i === list.length - 1 && last ? total : i + 1, plate }));
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
  teaserCta: "Naar de Sinterklaaskalender",
};
