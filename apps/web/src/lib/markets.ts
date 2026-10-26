/**
 * Markten die live staan (ADR 0040, 0044): Nederland, België (Nederlands en Frans) en het Verenigd Koninkrijk
 * (Engels, op kleurhoek.com/en-gb). De code is de bron: een nieuwe markt gaat live met de release, zonder
 * infra-run. Alleen bij uitzondering te beperken met MARKETS_ONLY (tijdens het draaien, niet bij het bouwen: één
 * image voor dev en prod). MARKETS_OVERRIDE en MARKETS worden bewust niet gelezen: Terraform zette daar de oude lijst
 * in, waardoor nieuwe markten op productie 404 gaven tot de volgende infra-run (ADR 0049).
 */
export const DEFAULT_MARKETS = "nl-nl,nl-be,fr-be,en-gb,de-de,de-at,de-ch,fr-fr,fr-ch,en-us,en-ie,es-es,it-it,pl-pl";
export const LIVE_MARKETS = (process.env.MARKETS_ONLY || DEFAULT_MARKETS).split(",").map((m) => m.trim().toLowerCase()).filter(Boolean);

export function bestMarket(country: string | null, acceptLanguage: string | null, live: string[] = LIVE_MARKETS): string {
  const LIVE = live.length ? live : LIVE_MARKETS;
  // Geen markt voor het land en geen taal die we hebben: Engels als internationale standaard (ADR 0044).
  const fallback = LIVE.find((m) => m.startsWith("en-")) ?? LIVE[0] ?? "nl-nl";
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
