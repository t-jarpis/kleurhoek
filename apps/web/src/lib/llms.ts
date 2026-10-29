import { messages } from "@/i18n/nl";
import { api } from "@/lib/api";
import { DEFAULT_ORG } from "@/lib/org-resolve";
import { pageUrl } from "@/lib/seo";
import { marketLabel } from "@/lib/sites";
import { DIMENSIONS, topics, topicTitle } from "@/lib/topics";
import { packs } from "@/lib/packs";

/**
 * llms.txt (ADR 0055): een korte kaart van de site voor AI-assistenten, volgens het voorstel op llmstxt.org.
 * Per markt van dit domein de beginpagina en de onderwerppagina's, met hun titel in de taal van die markt. Geen
 * vervanging van de sitemap; wel een snelle ingang voor een assistent die moet kiezen welke pagina hij noemt.
 */
export async function llmsTxt(markets: string[]): Promise<string> {
  const sections = await Promise.all(markets.map(async (market) => {
    const t = messages(market);
    const [plates, taxonomy] = await Promise.all([api.plates(market, DEFAULT_ORG).catch(() => []), api.taxonomy(market, DEFAULT_ORG).catch(() => null)]);
    const groups = taxonomy ? topics(plates, taxonomy, t) : null;
    const lines = [`## ${marketLabel(market)} (${market})`, "", `- [Kleurhoek](${pageUrl(market, "")}): ${t.lede}`];
    if (groups) for (const d of DIMENSIONS) for (const x of groups[d]) lines.push(`- [${topicTitle(t, x)}](${pageUrl(market, x.path)}): ${x.count}`);
    lines.push(`- [${t.advent.nav}](${pageUrl(market, "/aftelkalender")}): ${t.advent.lede}`, `- [${t.together.title}](${pageUrl(market, "/samen")}): ${t.together.lede}`);
    if (taxonomy) for (const p of packs(plates, taxonomy)) lines.push(`- [${t.packs.packTitle(p.category.name, p.age.name)}](${pageUrl(market, `/lespakketten/${p.slug}`)}): ${p.plates.length}`);
    return lines.join("\n");
  }));
  return [
    "# Kleurhoek",
    "",
    "> Free printable colouring pages, crafts, drawing and learning sheets for children, in 29 languages. Every page is an own design made with the help of AI, and every page is checked before it is published. No account needed for children; no tracking cookies.",
    "",
    "Each sheet has its own page (/platen/<slug>) that prints on A4 or Letter. Topic pages group sheets by subject, holiday, age, kind and continent; lesson packs (for teachers) combine colouring pages, worksheets and crafts per topic and age; an advent calendar opens one sheet per day in December; two people can colour the same sheet together on two screens with a four-letter code; the number after each link is how many sheets it has. Holiday pages only exist in countries that celebrate that holiday.",
    "",
    ...sections.flatMap((s) => [s, ""]),
  ].join("\n");
}
