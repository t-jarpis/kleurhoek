import type { PlateItem } from "./types";

/**
 * Aftelkalender (ADR 0058): 24 deurtjes in december, elk met een plaat. Waar Sinterklaas (of Nikolaus, Mikołaj …)
 * gevierd wordt, beginnen de eerste dagen met Sinterklaas; daarna wisselen kerst en winter elkaar af, met de
 * mooiste kerstplaat op 24 december. Waar geen kerst gevierd wordt, telt de kalender af naar oud en nieuw.
 * De kalender gebruikt alleen platen die in die markt zichtbaar zijn, dus feestdagen en taal kloppen vanzelf.
 */

/** Winterplaten om tussen de feestplaten te zetten, in deze volgorde (eigen keuze, nagekeken). */
export const ADVENT_FILL = [
  "sneeuwpop", "ijsbeer", "muts-en-wanten", "pinguins", "sleetje-trekken", "sneeuwvlok-knippen", "schaatser", "poolvos",
  "sneeuwballen-gooien", "iglo", "tekenles-sneeuwpop", "noorderlicht", "winterjas", "sneeuwuil", "skier", "pinguin-koker",
  "raamhangers-ster-en-maan", "sterrenhemel-vallende-ster", "tekenles-pinguin", "mandala-ster", "popupkaart-ster",
  "doolhof-pinguin-ijsschots", "pixelkunst-pinguin", "hert", "uil-met-veren", "volgorde-sneeuwpop-smelt",
  "verbind-de-punten-kerstboom", "pixelkunst-kerstboom", "spiegeltekenen-kerstboom", "patroon-sterren",
];
/** Op 24 december liefst een van deze. */
const CHRISTMAS_EVE = ["kerstboom-versieren", "kerstboom", "kerstmarkt", "kerstsokken"];
const NEW_YEAR_EVE = ["aftellen-naar-nieuwjaar", "vuurwerk-boven-de-stad"];

export type AdventTarget = "kerst" | "oudnieuw";
export interface Door { day: number; plate: PlateItem }

const byOrder = (a: PlateItem[], first: string[]) => [...a].sort((x, y) => {
  const i = first.indexOf(x.slug), j = first.indexOf(y.slug);
  return (i < 0 ? 99 : i) - (j < 0 ? 99 : j);
});

/** Een vaste maar per jaar andere volgorde. */
function seeded<T>(list: T[], seed: number): T[] {
  const out = [...list];
  let s = seed;
  for (let i = out.length - 1; i > 0; i--) {
    s = (s * 1103515245 + 12345) % 2147483648;
    const j = s % (i + 1);
    [out[i], out[j]] = [out[j]!, out[i]!];
  }
  return out;
}

export function adventDoors(plates: PlateItem[], year: number): { doors: Door[]; target: AdventTarget } {
  const used = new Set<string>();
  const take = (p: PlateItem | undefined) => { if (p && !used.has(p.slug)) { used.add(p.slug); return p; } return undefined; };
  const of = (h: string) => plates.filter((p) => p.holiday === h);
  const christmas = of("kerst");
  const target: AdventTarget = christmas.length ? "kerst" : "oudnieuw";
  const days = new Map<number, PlateItem>();

  // Sinterklaas op de eerste dagen (hooguit vijf), zoals het in die landen ook gaat.
  of("sinterklaas").slice(0, 5).forEach((p, i) => { const t = take(p); if (t) days.set(i + 1, t); });
  // De mooiste plaat op 24 december.
  const eve = target === "kerst" ? byOrder(christmas, CHRISTMAS_EVE)[0] : byOrder([...of("oudnieuw")], NEW_YEAR_EVE)[0];
  const e = take(eve); if (e) days.set(24, e);
  // Kerst (of nieuwjaar) en chanoeka om en om met winter, van achteren naar voren.
  const fest = [...(target === "kerst" ? christmas : of("oudnieuw")), ...of("chanoeka")].filter((p) => !used.has(p.slug));
  const index = new Map(plates.map((p) => [p.slug, p]));
  const fill = seeded(ADVENT_FILL, year).map((s) => index.get(s)).filter((p): p is PlateItem => !!p);
  const spare = plates.filter((p) => ["natuur", "dieren"].includes(p.category));
  let f = 0, k = 0;
  for (let day = 23; day >= 1; day--) {
    if (days.has(day)) continue;
    const wantFest = (24 - day) % 2 === 1 && k < fest.length;
    let p = wantFest ? take(fest[k++]) : undefined;
    while (!p && f < fill.length) p = take(fill[f++]);
    while (!p && k < fest.length) p = take(fest[k++]);
    for (let i = 0; !p && i < spare.length; i++) p = take(spare[i]);
    if (p) days.set(day, p);
  }
  return { doors: [...days.entries()].sort((a, b) => a[0] - b[0]).map(([day, plate]) => ({ day, plate })), target };
}

/**
 * Welke deurtjes open mogen op een datum (JJJJ-MM-DD, in de tijdzone van de markt). In november nog geen, in
 * december tot en met vandaag, daarna en de rest van het jaar alle 24 (de kalender van afgelopen december).
 */
export function openUntil(today: string, target: AdventTarget = "kerst"): { year: number; open: number; nightsTo: number | null; daysToStart: number | null } {
  const [y, m, d] = today.split("-").map(Number) as [number, number, number];
  if (m === 12) {
    const nights = (target === "kerst" ? 25 : 32) - d;
    return { year: y, open: Math.min(24, d), nightsTo: nights > 0 ? nights : null, daysToStart: null };
  }
  if (m === 11) return { year: y, open: 0, nightsTo: null, daysToStart: 31 - d };
  return { year: m < 11 ? y - 1 : y, open: 24, nightsTo: null, daysToStart: null };
}

/** De volgorde van de deurtjes op de kalender: door elkaar, zoals bij een echte aftelkalender. */
export const doorOrder = (year: number) => seeded(Array.from({ length: 24 }, (_, i) => i + 1), year * 7 + 3);
