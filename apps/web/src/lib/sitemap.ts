import { api } from "@/lib/api";
import { LIVE_MARKETS } from "@/lib/markets";
import { DEFAULT_ORG } from "@/lib/org-resolve";
import { hreflang, pageUrl } from "@/lib/seo";
import { siteDomains } from "@/lib/sites";

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
export const XML = { "content-type": "application/xml; charset=utf-8", "cache-control": "private, max-age=3600" };

/** Paden van één markt: vaste pagina's, platen en thema's (ADR 0035). */
async function paths(market: string): Promise<string[]> {
  const [plates, themes] = await Promise.all([api.plates(market, DEFAULT_ORG).catch(() => []), api.themes(market, DEFAULT_ORG).catch(() => [])]);
  return [...["", "/themas", "/contact", "/disclaimer", "/eigen-omgeving"], ...plates.map((p) => `/platen/${p.slug}`), ...themes.map((t) => `/themas/${t.slug}`)];
}

/** Welke markten welk pad hebben; een uur bewaard, want elke marktsitemap heeft de taalversies van alle markten nodig. */
let cache: { at: number; byPath: Promise<Map<string, string[]>> } | null = null;
function byPath(): Promise<Map<string, string[]>> {
  if (cache && Date.now() - cache.at < 3_600_000) return cache.byPath;
  const p = (async () => {
    const out = new Map<string, string[]>();
    for (const market of LIVE_MARKETS) for (const path of await paths(market)) out.set(path, [...(out.get(path) ?? []), market]);
    return out;
  })();
  p.catch(() => { cache = null; });
  cache = { at: Date.now(), byPath: p };
  return p;
}

/**
 * Sitemap van één markt (ADR 0035, 0050): elk adres met zijn taalversies op alle domeinen en x-default op de
 * beginpagina. Per markt een eigen bestand, zodat het onder de grens van 50.000 adressen en 50 MB blijft.
 */
export async function marketSitemap(market: string): Promise<string> {
  const domains = siteDomains();
  const urls: string[] = [];
  for (const [path, markets] of await byPath()) {
    if (!markets.includes(market)) continue;
    const alts = markets.length > 1 ? markets.map((m) => `<xhtml:link rel="alternate" hreflang="${hreflang(m)}" href="${esc(pageUrl(m, path))}"/>`).join("")
      + `<xhtml:link rel="alternate" hreflang="x-default" href="${esc(path === "" && domains ? `${domains.com}/` : pageUrl(markets[0]!, path))}"/>` : "";
    urls.push(`<url><loc>${esc(pageUrl(market, path))}</loc>${alts}</url>`);
  }
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${urls.join("\n")}\n</urlset>\n`;
}

/** Index met per markt van dit domein een eigen sitemap. */
export function sitemapIndex(origin: string, markets: string[]): string {
  const items = markets.map((m) => `<sitemap><loc>${esc(`${origin}/sitemap/${m}.xml`)}</loc></sitemap>`).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${items}\n</sitemapindex>\n`;
}
