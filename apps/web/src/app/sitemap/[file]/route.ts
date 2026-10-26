import { headers } from "next/headers";
import { LIVE_MARKETS } from "@/lib/markets";
import { indexableHost, SITE_HOST_HEADER } from "@/lib/seo";
import { marketSitemap, XML } from "@/lib/sitemap";
import { domainForHost, domainOf, siteDomains } from "@/lib/sites";

export const revalidate = 3600;

/** /sitemap/<markt>.xml (ADR 0050): de sitemap van één markt, alleen op het domein van die markt. */
export async function GET(_req: Request, { params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  const h = await headers();
  const host = h.get(SITE_HOST_HEADER) ?? h.get("host");
  const market = /^([a-z]{2}-[a-z]{2})\.xml$/.exec(file)?.[1];
  const domain = domainForHost(host, siteDomains());
  if (!indexableHost(host) || !market || !LIVE_MARKETS.includes(market) || (domain && domainOf(market) !== domain)) return new Response("Not found", { status: 404 });
  return new Response(await marketSitemap(market), { headers: XML });
}
