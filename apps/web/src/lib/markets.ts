/**
 * Markten die live staan (ADR 0040, 0044): Nederland, België (Nederlands en Frans) en het Verenigd Koninkrijk
 * (Engels, op kleurhoek.com/en-gb). De code is de bron: een nieuwe markt gaat live met de release, zonder
 * infra-run. Alleen bij uitzondering te beperken met MARKETS_ONLY (tijdens het draaien, niet bij het bouwen: één
 * image voor dev en prod). MARKETS_OVERRIDE en MARKETS worden bewust niet gelezen: Terraform zette daar de oude lijst
 * in, waardoor nieuwe markten op productie 404 gaven tot de volgende infra-run (ADR 0049).
 */
export const DEFAULT_MARKETS = "nl-nl,nl-be,fr-be,en-gb,de-de,de-at,de-ch,fr-fr,fr-ch,en-us,en-ie,es-es,it-it,pl-pl,en-ca,en-au,en-nz,fr-ca,fr-lu,de-lu,de-li,it-ch,es-mx,es-ar,es-co,es-us,pt-br,pt-pt,sv-se,da-dk,nb-no,fi-fi";
export const LIVE_MARKETS = (process.env.MARKETS_ONLY || DEFAULT_MARKETS).split(",").map((m) => m.trim().toLowerCase()).filter(Boolean);

/** Markt voor een taal in een land zonder eigen markt (ADR 0050): Frans uit Senegal → fr-fr, Spaans uit Chili → es-mx. */
const HOME_MARKET: Record<string, string> = { nl: "nl-nl", fr: "fr-fr", de: "de-de", en: "en-gb", es: "es-es", it: "it-it", pl: "pl-pl", pt: "pt-br", sv: "sv-se", da: "da-dk", nb: "nb-no", fi: "fi-fi" };
const LATAM = new Set(["mx", "gt", "hn", "sv", "ni", "cr", "pa", "cu", "do", "pr", "ve", "co", "ec", "pe", "bo", "cl", "ar", "uy", "py"]);

export function bestMarket(country: string | null, acceptLanguage: string | null, live: string[] = LIVE_MARKETS): string {
  const LIVE = live.length ? live : LIVE_MARKETS;
  // Geen markt voor het land en geen taal die we hebben: Engels als internationale standaard (ADR 0044).
  const fallback = LIVE.find((m) => m.startsWith("en-")) ?? LIVE[0] ?? "nl-nl";
  const c = (country ?? "").toLowerCase();
  const langs = (acceptLanguage ?? "").split(",").map((l) => l.split(";")[0]!.trim().slice(0, 2).toLowerCase()).map((l) => (l === "no" || l === "nn" ? "nb" : l)).filter(Boolean);
  const byCountry = LIVE.filter((m) => m.endsWith(`-${c}`));
  for (const lang of langs) {
    const home = LATAM.has(c) && lang === "es" ? "es-mx" : HOME_MARKET[lang];
    const hit = byCountry.find((m) => m.startsWith(`${lang}-`)) ?? (home && LIVE.includes(home) ? home : undefined) ?? LIVE.find((m) => m.startsWith(`${lang}-`));
    if (hit) return hit;
  }
  return byCountry[0] ?? fallback;
}

export function marketLanguage(market: string): string { return market.slice(0, 2); }

/** Markten die op Letter-papier printen (ADR 0046, 0050): VS, Canada, Mexico en Colombia. Gelijk aan paperSize in de API. */
export const isLetter = (market: string) => /-(us|ca|mx|co)$/.test(market);
