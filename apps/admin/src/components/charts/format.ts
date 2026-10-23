/** Getallen en datums voor grafieken (nl-NL). Compact vanaf 10.000: 12,9K. */
const nf = new Intl.NumberFormat("nl-NL");
const compact = new Intl.NumberFormat("nl-NL", { notation: "compact", maximumFractionDigits: 1 });
export const num = (n: number) => (Math.abs(n) >= 10_000 ? compact.format(n) : nf.format(n));
export const tick = (n: number) => (Math.abs(n) >= 1000 ? compact.format(n) : nf.format(n));

const MONTHS = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"];
const DAYS = ["zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"];
/** Datum uit YYYY-MM-DD zonder tijdzone-verschuiving. */
export function shortDate(iso: string): string {
  const [, m, d] = iso.split("-").map(Number);
  return `${d} ${MONTHS.at((m ?? 1) - 1)}`;
}
export function longDate(iso: string, bucket: "day" | "week"): string {
  const date = new Date(`${iso}T12:00:00Z`);
  if (bucket === "week") return `Week van ${shortDate(iso)}`;
  const day = DAYS.at(date.getUTCDay()) ?? "";
  return `${day.charAt(0).toUpperCase()}${day.slice(1)} ${shortDate(iso)}`;
}

/** Ronde schaal: maximum en 4 stappen (0, ¼, ½, ¾, max) op een "mooi" getal. */
/** Aantallen: hele stappen (nooit 0,25 account). */
export function niceScale(max: number): number[] {
  if (max <= 0) return [0, 1, 2, 3, 4];
  const raw = max / 4, mag = 10 ** Math.floor(Math.log10(raw));
  const step = Math.max(1, ([1, 2, 2.5, 5, 10].find((s) => s * mag >= raw) ?? 10) * mag);
  return [0, 1, 2, 3, 4].map((i) => Math.round(i * step * 100) / 100);
}

/** Verandering t.o.v. de vorige periode: null als er geen vergelijking is. */
export function delta(now: number, before: number): { pct: number | null; isNew: boolean } {
  if (before === 0) return { pct: null, isNew: now > 0 };
  return { pct: Math.round(((now - before) / before) * 100), isNew: false };
}
