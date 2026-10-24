import type { Metadata } from "next";
import { LIVE_MARKETS } from "./markets";
import type { Org } from "./org";

/**
 * Vindbaarheid (ADR 0035). Alleen Kleurhoek zelf op het productiedomein wordt geïndexeerd; dev, lokaal en de
 * sites van organisaties krijgen noindex en een robots.txt die alles afschermt.
 */
export const PRODUCTION_SITE = "https://www.kleurhoek.nl";
export const SITE = (process.env.SITE_URL ?? "").replace(/\/$/, "");

export function indexable(org: Org | null): boolean {
  return SITE === PRODUCTION_SITE && !!org?.isDefault;
}

/** Normale markt-code zoals in hreflang: nl-NL. */
export const hreflang = (market: string) => `${market.slice(0, 2)}-${market.slice(3).toUpperCase()}`;

/**
 * Canonieke URL en taalversies voor een pad dat in elke live markt bestaat (bijv. "/themas"). Voor platen geeft de
 * sitemap de taalversies, omdat niet elke plaat in elke markt staat.
 */
export function pageMeta(org: Org | null, market: string, path: string, allMarkets = true): Pick<Metadata, "alternates"> {
  if (!indexable(org)) return {};
  const languages = allMarkets && LIVE_MARKETS.length > 1 ? Object.fromEntries(LIVE_MARKETS.map((m) => [hreflang(m), `${SITE}/${m}${path}`])) : undefined;
  return { alternates: { canonical: `${SITE}/${market}${path}`, ...(languages ? { languages } : {}) } };
}

/** Vraag naar robots.txt of sitemap.xml: alleen het productieadres van Kleurhoek zelf (ADR 0035). */
export function indexableHost(host: string | null): boolean {
  return SITE === PRODUCTION_SITE && (host ?? "").toLowerCase().split(":")[0] === new URL(PRODUCTION_SITE).host;
}

/** Gestructureerde gegevens als script-tag-inhoud; `<` gecodeerd zodat tekst nooit de tag kan sluiten. */
export const jsonLd = (data: unknown) => JSON.stringify(data).replace(/</g, "\\u003c");
