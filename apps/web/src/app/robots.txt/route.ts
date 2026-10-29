import { headers } from "next/headers";
import { robots } from "@/lib/robots";
import { indexableHost, SITE_HOST_HEADER } from "@/lib/seo";

/**
 * robots.txt (ADR 0035, 0040). Alleen www.kleurhoek.nl, .be en .com in productie mogen geïndexeerd worden; elk
 * domein wijst naar zijn eigen sitemap. Dev, lokaal en de sites van organisaties schermen alles af.
 * `private`: de Worker haalt .be, .com en organisatiesites op via www.kleurhoek.nl; een gedeelde cache bij
 * Cloudflare zou dan voor elk domein het antwoord van kleurhoek.nl geven.
 */
export async function GET() {
  const h = await headers();
  const host = h.get(SITE_HOST_HEADER) ?? h.get("host");
  const body = indexableHost(host) ? robots(host!.split(":")[0]!) : "User-agent: *\nDisallow: /\n";
  return new Response(body, { headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "private, max-age=3600" } });
}
