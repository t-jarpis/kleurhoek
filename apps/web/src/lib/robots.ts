/**
 * Crawlers die platen verzamelen om AI-modellen te trainen: welkom bij zoeken, niet bij trainen (ADR 0045).
 * Google en Bing zelf blijven welkom; Google-Extended en Applebot-Extended zijn alleen hun trainings-vlag.
 */
export const AI_TRAINERS = ["GPTBot", "CCBot", "Google-Extended", "Applebot-Extended", "Bytespider", "ClaudeBot", "anthropic-ai", "cohere-ai", "Meta-ExternalAgent", "Diffbot", "Omgilibot", "ImagesiftBot", "Amazonbot", "AI2Bot", "Timpibot"];
/**
 * Zoek- en assistentbots van AI-diensten: zij halen een pagina op als iemand iets vraagt, of bouwen een zoekindex
 * waarin de bron met link wordt genoemd. Welkom, net als Google en Bing (ADR 0055). ChatGPT en Copilot zoeken
 * daarnaast via Bing, Claude via Brave; die vallen onder *.
 */
export const AI_SEARCH = ["OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "DuckAssistBot", "MistralAI-User", "Applebot", "bingbot"];
const PRIVATE = [...["account", "boekje", "beheer"].flatMap((p) => [`Disallow: /${p}`, `Disallow: /*/${p}`]), "Disallow: /auth/", "Disallow: /ga/", "Disallow: /e/"];

/** De inhoud van robots.txt voor een domein dat geïndexeerd mag worden. */
export function robots(host: string): string {
  return [...AI_TRAINERS.flatMap((ua) => [`User-agent: ${ua}`, "Disallow: /", ""]),
    ...AI_SEARCH.map((ua) => `User-agent: ${ua}`), "Allow: /", ...PRIVATE, "",
    "User-agent: *", "Allow: /", ...PRIVATE, "", `Sitemap: https://${host}/sitemap.xml`, ""].join("\n");
}

