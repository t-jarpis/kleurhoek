import { headers } from "next/headers";
import { indexableHost, SITE_HOST_HEADER } from "@/lib/seo";

/**
 * robots.txt (ADR 0035, 0040). Alleen www.kleurhoek.nl, .be en .com in productie mogen geïndexeerd worden; elk
 * domein wijst naar zijn eigen sitemap. Dev, lokaal en de sites van organisaties schermen alles af.
 */
export async function GET() {
  const h = await headers();
  const host = h.get(SITE_HOST_HEADER) ?? h.get("host");
  const body = indexableHost(host)
    ? ["User-agent: *", "Allow: /",
      ...["account", "boekje", "beheer"].flatMap((p) => [`Disallow: /${p}`, `Disallow: /*/${p}`]),
      "Disallow: /auth/", "Disallow: /ga/", "Disallow: /e/", "", `Sitemap: https://${host!.split(":")[0]}/sitemap.xml`, ""].join("\n")
    : "User-agent: *\nDisallow: /\n";
  return new Response(body, { headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "public, max-age=3600" } });
}
