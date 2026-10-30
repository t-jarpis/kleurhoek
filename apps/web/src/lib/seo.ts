import type { Metadata } from "next";
import { LIVE_MARKETS } from "./markets";
import type { Org } from "./org";
import { marketUrl, siteDomains } from "./sites";

/**
 * Vindbaarheid (ADR 0035). Alleen Kleurhoek zelf op het productiedomein wordt geïndexeerd; dev, lokaal en de
 * sites van organisaties krijgen noindex en een robots.txt die alles afschermt.
 */
export const PRODUCTION_SITE = "https://www.kleurhoek.nl";
export const SITE = (process.env.SITE_URL ?? "").replace(/\/$/, "");

export function indexable(org: Org | null): boolean {
  return SITE === PRODUCTION_SITE && !!org?.isDefault;
}

/** Volledig adres van een pagina in een markt, op het eigen domein van die markt (ADR 0040). */
export const pageUrl = (market: string, path: string) => marketUrl(market, path, siteDomains(), SITE);

/**
 * Versie van de PNG-plaatjes (ADR 0062). Ophogen als de PNG's anders getekend worden: de adressen zijn verder per
 * plaatversie eeuwig gecachet bij Cloudflare, en ?r= geeft dan een nieuw adres.
 */
export const PNG_REV = "2";
export const pngOf = (svgPath: string) => `${svgPath.replace(/\.svg$/, ".png")}?r=${PNG_REV}`;
export const pinOf = (market: string, slug: string) => `/v1/pins/${market}/${slug}.png?r=${PNG_REV}`;

/** Volledig adres van een bestand op het domein van een markt, bijvoorbeeld een plaat-PNG voor og:image (ADR 0055). */
export function absolute(market: string, path: string): string {
  const home = pageUrl(market, "");
  return /^https?:\/\//.test(home) ? `${new URL(home).origin}${path}` : `${SITE}${path}`;
}

/** Normale markt-code zoals in hreflang: nl-NL. */
export const hreflang = (market: string) => `${market.slice(0, 2)}-${market.slice(3).toUpperCase()}`;

/**
 * Canonieke URL en taalversies voor een pad dat in elke live markt bestaat (bijv. "/themas"), elk op het eigen
 * domein van de markt (ADR 0040). De beginpagina krijgt x-default: kleurhoek.com kiest daar de beste markt. Voor
 * platen geeft de sitemap de taalversies, omdat niet elke plaat in elke markt staat.
 */
export function pageMeta(org: Org | null, market: string, path: string, allMarkets = true): Pick<Metadata, "alternates"> {
  if (!indexable(org)) return {};
  const domains = siteDomains();
  const languages = allMarkets && LIVE_MARKETS.length > 1 ? {
    ...Object.fromEntries(LIVE_MARKETS.map((m) => [hreflang(m), pageUrl(m, path)])),
    ...(path === "" && domains ? { "x-default": `${domains.com}/` } : {}),
  } : undefined;
  return { alternates: { canonical: pageUrl(market, path), ...(languages ? { languages } : {}) } };
}

/** Het adres waarop de bezoeker de site opvroeg; de proxy zet dat in deze header. */
export const SITE_HOST_HEADER = "x-kh-site-host";

/** De productiehosts van Kleurhoek zelf: www.kleurhoek.nl, .be en .com (ADR 0035, 0040). */
export function productionHosts(): string[] {
  if (SITE !== PRODUCTION_SITE) return [];
  const domains = siteDomains();
  return (domains ? Object.values(domains) : [PRODUCTION_SITE]).map((o) => new URL(o).host);
}

/** Vraag naar robots.txt of sitemap.xml: alleen de productieadressen van Kleurhoek zelf. */
export function indexableHost(host: string | null): boolean {
  return productionHosts().includes((host ?? "").toLowerCase().split(":")[0]!);
}

/** Gestructureerde gegevens als script-tag-inhoud; `<` gecodeerd zodat tekst nooit de tag kan sluiten. */
export const jsonLd = (data: unknown) => JSON.stringify(data).replace(/</g, "\\u003c");
