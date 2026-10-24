import { headers } from "next/headers";
import { api } from "@/lib/api";
import { LIVE_MARKETS } from "@/lib/markets";
import { DEFAULT_ORG } from "@/lib/org-resolve";
import { hreflang, indexableHost, SITE } from "@/lib/seo";

export const revalidate = 3600;

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/** Eén adres met zijn taalversies (hreflang) en x-default naar de eerste markt. */
function entry(byMarket: Map<string, string>): string[] {
  const alts = [...byMarket].map(([m, url]) => `<xhtml:link rel="alternate" hreflang="${hreflang(m)}" href="${esc(url)}"/>`);
  const first = [...byMarket.values()][0]!;
  const def = byMarket.size > 1 ? [`<xhtml:link rel="alternate" hreflang="x-default" href="${esc(first)}"/>`] : [];
  return [...byMarket.values()].map((url) => `<url><loc>${esc(url)}</loc>${byMarket.size > 1 ? alts.join("") + def.join("") : ""}</url>`);
}

/**
 * sitemap.xml (ADR 0035): per live markt de vaste pagina's, alle platen en de thema's, met taalversies. Alleen
 * op www.kleurhoek.nl in productie; elders bestaat hij niet.
 */
export async function GET() {
  if (!indexableHost((await headers()).get("host"))) return new Response("Not found", { status: 404 });
  const groups = new Map<string, Map<string, string>>();
  const add = (key: string, market: string, path: string) => {
    const g = groups.get(key) ?? new Map<string, string>();
    g.set(market, `${SITE}/${market}${path}`);
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
  const urls = [...groups.values()].flatMap(entry);
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${urls.join("\n")}\n</urlset>\n`;
  return new Response(xml, { headers: { "content-type": "application/xml; charset=utf-8", "cache-control": "public, max-age=3600" } });
}
