import { headers } from "next/headers";
import { LIVE_MARKETS } from "@/lib/markets";
import { indexableHost, SITE_HOST_HEADER } from "@/lib/seo";
import { sitemapIndex, XML } from "@/lib/sitemap";
import { domainForHost, domainOf, siteDomains } from "@/lib/sites";

export const revalidate = 3600;

/**
 * sitemap.xml (ADR 0035, 0050): een index met per markt van dit domein een eigen sitemap (/sitemap/<markt>.xml).
 * Alleen op de productiedomeinen (ADR 0040); elders bestaat hij niet.
 */
export async function GET() {
  const h = await headers();
  const host = h.get(SITE_HOST_HEADER) ?? h.get("host");
  if (!indexableHost(host)) return new Response("Not found", { status: 404 });
  const domains = siteDomains();
  const domain = domainForHost(host, domains);
  const markets = LIVE_MARKETS.filter((m) => !domain || domainOf(m) === domain);
  return new Response(sitemapIndex(`https://${host!.split(":")[0]}`, markets), { headers: XML });
}
