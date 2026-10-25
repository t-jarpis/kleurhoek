import { headers } from "next/headers";
import { indexableHost, SITE_HOST_HEADER } from "@/lib/seo";

/**
 * robots.txt (ADR 0035, 0040). Alleen www.kleurhoek.nl, .be en .com in productie mogen geïndexeerd worden; elk
 * domein wijst naar zijn eigen sitemap. Dev, lokaal en de sites van organisaties schermen alles af.
 * `private`: de Worker haalt .be, .com en organisatiesites op via www.kleurhoek.nl; een gedeelde cache bij
 * Cloudflare zou dan voor elk domein het antwoord van kleurhoek.nl geven.
 */
/**
 * Crawlers die platen verzamelen om AI-modellen te trainen: welkom bij zoeken, niet bij trainen (ADR 0045).
 * Google en Bing zelf blijven welkom; Google-Extended en Applebot-Extended zijn alleen hun trainings-vlag.
 */
const AI_TRAINERS = ["GPTBot", "CCBot", "Google-Extended", "Applebot-Extended", "Bytespider", "ClaudeBot", "anthropic-ai", "cohere-ai", "Meta-ExternalAgent", "Diffbot", "Omgilibot", "ImagesiftBot", "PerplexityBot", "Amazonbot", "AI2Bot", "Timpibot"];

export async function GET() {
  const h = await headers();
  const host = h.get(SITE_HOST_HEADER) ?? h.get("host");
  const body = indexableHost(host)
    ? [...AI_TRAINERS.flatMap((ua) => [`User-agent: ${ua}`, "Disallow: /", ""]), "User-agent: *", "Allow: /",
      ...["account", "boekje", "beheer"].flatMap((p) => [`Disallow: /${p}`, `Disallow: /*/${p}`]),
      "Disallow: /auth/", "Disallow: /ga/", "Disallow: /e/", "", `Sitemap: https://${host!.split(":")[0]}/sitemap.xml`, ""].join("\n")
    : "User-agent: *\nDisallow: /\n";
  return new Response(body, { headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "private, max-age=3600" } });
}
