import { headers } from "next/headers";
import { llmsTxt } from "@/lib/llms";
import { LIVE_MARKETS } from "@/lib/markets";
import { indexableHost, SITE_HOST_HEADER } from "@/lib/seo";
import { domainForHost, domainOf, siteDomains } from "@/lib/sites";

export const revalidate = 3600;

/** llms.txt (ADR 0055): per domein de markten en onderwerppagina's, alleen op de productiedomeinen (ADR 0040). */
export async function GET() {
  const h = await headers();
  const host = h.get(SITE_HOST_HEADER) ?? h.get("host");
  if (!indexableHost(host)) return new Response("Not found", { status: 404 });
  const domain = domainForHost(host, siteDomains());
  const markets = LIVE_MARKETS.filter((m) => !domain || domainOf(m) === domain);
  return new Response(await llmsTxt(markets), { headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "private, max-age=3600" } });
}
