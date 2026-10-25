import { headers } from "next/headers";
import { api } from "@/lib/api";
import { LIVE_MARKETS } from "@/lib/markets";
import { DEFAULT_ORG } from "@/lib/org-resolve";
import { hreflang, indexableHost, pageUrl, SITE_HOST_HEADER } from "@/lib/seo";
import { domainForHost, domainOf, siteDomains } from "@/lib/sites";

export const revalidate = 3600;

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/**
 * Eén adres met zijn taalversies (hreflang, ook op de andere domeinen). Alleen de adressen van dit domein komen
 * in deze sitemap (`mine`); x-default wijst naar de beginpagina van kleurhoek.com als die er is.
 */
function entry(byMarket: Map<string, string>, mine: (market: string) => boolean, xDefault: string | null): string[] {
  const alts = [...byMarket].map(([m, url]) => `<xhtml:link rel="alternate" hreflang="${hreflang(m)}" href="${esc(url)}"/>`);
  const def = byMarket.size > 1 ? [`<xhtml:link rel="alternate" hreflang="x-default" href="${esc(xDefault ?? [...byMarket.values()][0]!)}"/>`] : [];
  return [...byMarket].filter(([m]) => mine(m)).map(([, url]) => `<url><loc>${esc(url)}</loc>${byMarket.size > 1 ? alts.join("") + def.join("") : ""}</url>`);
}

/**
 * sitemap.xml (ADR 0035): per live markt de vaste pagina's, alle platen en de thema's, met taalversies. Alleen
 * op de productiedomeinen, per domein de eigen adressen (ADR 0040); elders bestaat hij niet.
 */
export async function GET() {
  const h = await headers();
  const host = h.get(SITE_HOST_HEADER) ?? h.get("host");
  if (!indexableHost(host)) return new Response("Not found", { status: 404 });
  const domains = siteDomains();
  const domain = domainForHost(host, domains);
  const mine = (m: string) => !domain || domainOf(m) === domain;
  const groups = new Map<string, Map<string, string>>();
  const add = (key: string, market: string, path: string) => {
    const g = groups.get(key) ?? new Map<string, string>();
    g.set(market, pageUrl(market, path));
    groups.set(key, g);
  };
  for (const market of LIVE_MARKETS) {
    for (const p of ["", "/themas", "/contact", "/disclaimer", "/eigen-omgeving"]) add(`page:${p}`, market, p);
    const [plates, themes] = await Promise.all([
      api.plates(market, DEFAULT_ORG).catch(() => []), api.themes(market, DEFAULT_ORG).catch(() => []),
    ]);
    for (const p of plates) add(`plate:${p.slug}`, market, `/platen/${p.slug}`);
    for (const t of themes) add(`theme:${t.slug}`, market, `/themas/${t.slug}`);
  }
  const urls = [...groups].flatMap(([key, g]) => entry(g, mine, key === "page:" && domains ? `${domains.com}/` : null));
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${urls.join("\n")}\n</urlset>\n`;
  return new Response(xml, { headers: { "content-type": "application/xml; charset=utf-8", "cache-control": "private, max-age=3600" } });
}
