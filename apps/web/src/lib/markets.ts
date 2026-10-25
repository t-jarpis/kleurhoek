/**
 * Markten die live staan (ADR 0040): Nederland en België (Nederlands en Frans). Op de server te overschrijven met
 * MARKETS (tijdens het draaien, niet bij het bouwen: één image voor dev en prod).
 */
export const DEFAULT_MARKETS = "nl-nl,nl-be,fr-be";
export const LIVE_MARKETS = (process.env.MARKETS ?? DEFAULT_MARKETS).split(",").map((m) => m.trim().toLowerCase()).filter(Boolean);

export function bestMarket(country: string | null, acceptLanguage: string | null, live: string[] = LIVE_MARKETS): string {
  const LIVE = live.length ? live : LIVE_MARKETS;
  const fallback = LIVE[0] ?? "nl-nl";
  const c = (country ?? "").toLowerCase();
  const langs = (acceptLanguage ?? "").split(",").map((l) => l.split(";")[0]!.trim().slice(0, 2).toLowerCase()).filter(Boolean);
  const byCountry = LIVE.filter((m) => m.endsWith(`-${c}`));
  for (const lang of langs) {
    const hit = byCountry.find((m) => m.startsWith(`${lang}-`)) ?? LIVE.find((m) => m.startsWith(`${lang}-`));
    if (hit) return hit;
  }
  return byCountry[0] ?? fallback;
}

export function marketLanguage(market: string): string { return market.slice(0, 2); }
