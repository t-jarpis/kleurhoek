/**
 * Bots, crawlers, previews en geautomatiseerde browsers (ook onze eigen rooktests) tellen niet mee. Zoekmachines
 * voeren JavaScript uit en zouden anders als bezoeker in de cijfers staan. Alleen herkenning op de user agent;
 * die wordt nergens bewaard (ADR 0002).
 */
const BOT = /bot\b|bot\/|crawl|spider|slurp|headless|lighthouse|pagespeed|ptst|playwright|puppeteer|selenium|phantom|preview|inspectiontool|facebookexternalhit|embedly|quora link|whatsapp|python|curl|wget|httpclient|okhttp|go-http|java\/|node-fetch|axios|monitor|uptime|pingdom|statuscake|datadog|ahrefs|semrush|mj12|dotbot|petal|bytespider|gptbot|claude|anthropic|perplexity|ccbot/i;
export const isBot = (ua: string) => !ua.trim() || BOT.test(ua);
