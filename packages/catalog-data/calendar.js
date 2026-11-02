"use strict";
/**
 * Sinterklaaskalender (ADR 0065): datums en volgorde van de deurtjes. Gedeeld door de site (de kalender), de API
 * (Social en de dagelijkse mail) en tests, zodat iedereen hetzelfde deurtje van de dag kent. Geen bestanden lezen:
 * dit mag ook in de browser.
 */
const DAY = 86400000;
const utc = (y, m, d) => Date.UTC(y, m - 1, d);
const iso = (t) => new Date(t).toISOString().slice(0, 10);

/** Pakjesavond per markt: in Nederland 5 december, in België de ochtend van 6 december. */
const SINT_MARKETS = { "nl-nl": 5, "nl-be": 6 };

/** De intocht: de eerste zaterdag na 11 november (Sint-Maarten). */
function intocht(year) {
  let t = utc(year, 11, 12);
  while (new Date(t).getUTCDay() !== 6) t += DAY;
  return iso(t);
}

/** Alle datums van de kalender, van de intocht tot en met pakjesavond. */
function sintDates(year, market) {
  const eve = utc(year, 12, SINT_MARKETS[String(market).toLowerCase()] ?? 5);
  const out = [];
  for (let t = Date.parse(intocht(year)); t <= eve; t += DAY) out.push(iso(t));
  return out;
}

/** Deze platen eerst, in deze volgorde; de intocht vooraan en pakjesavond als laatste. */
const SINT_FIRST = ["stoomboot-komt-aan", "intocht-van-sinterklaas", "sint-en-piet-zwaaien", "sinterklaas-portret", "roetveegpiet-zwaait",
  "pakjesboot-in-de-haven", "sint-rijdt-op-zijn-paard", "amerigo-en-de-wortel", "schoen-bij-de-kachel", "piet-maakt-muziek",
  "stapel-cadeautjes", "sinterklaas-leest-voor", "warme-chocolademelk",
  "schoen-zetten", "piet-met-de-zak", "pepernotenbakkerij", "chocoladeletter", "sinterklaas-op-het-dak", "mijter-om-op-te-zetten",
  "piet-in-de-schoorsteen", "het-grote-boek", "pieten-op-het-dak", "surprise-maken", "schoen", "sinterklaas", "pakjesboot",
  "sinterklaas-glas-in-lood", "sinterklaaskaart-schoen", "surprise-mijterdoosje", "harmonica-uitnodiging-pakjesavond"];
const SINT_LAST = "pakjesavond";

/** Deurtjes: van de zichtbare Sinterklaasplaten (slugs) welke achter welk deurtje (1..total) zit. */
function sintDoorSlugs(slugs, total) {
  const rank = (s) => { const i = SINT_FIRST.indexOf(s); return i < 0 ? 99 : i; };
  const hasLast = slugs.includes(SINT_LAST);
  const rest = slugs.filter((s) => s !== SINT_LAST).sort((a, b) => rank(a) - rank(b));
  const list = [...rest.slice(0, hasLast ? total - 1 : total), ...(hasLast ? [SINT_LAST] : [])];
  // Te weinig platen: de laatste plek blijft pakjesavond, de rest schuift op.
  return list.map((slug, i) => ({ day: i === list.length - 1 && hasLast ? total : i + 1, slug }));
}

/** Het deurtje van een datum (JJJJ-MM-DD), of null buiten de kalender. */
function sintDoorOn(date, market) {
  const dates = sintDates(Number(date.slice(0, 4)), market);
  const i = dates.indexOf(date);
  return i < 0 ? null : { door: i + 1, total: dates.length };
}

module.exports = { SINT_MARKETS, intocht, sintDates, SINT_FIRST, SINT_LAST, sintDoorSlugs, sintDoorOn };
