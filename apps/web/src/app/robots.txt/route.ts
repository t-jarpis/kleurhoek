import { headers } from "next/headers";
import { indexableHost, SITE } from "@/lib/seo";

/**
 * robots.txt (ADR 0035). Alleen www.kleurhoek.nl in productie mag geïndexeerd worden; dev, lokaal en de sites
 * van organisaties (eigen adres of subdomein) schermen alles af.
 */
export async function GET() {
  const host = (await headers()).get("host");
  const body = indexableHost(host)
    ? ["User-agent: *", "Allow: /", "Disallow: /*/account", "Disallow: /*/boekje", "Disallow: /auth/", "Disallow: /ga/", "Disallow: /e/", "", `Sitemap: ${SITE}/sitemap.xml`, ""].join("\n")
    : "User-agent: *\nDisallow: /\n";
  return new Response(body, { headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "public, max-age=3600" } });
}
