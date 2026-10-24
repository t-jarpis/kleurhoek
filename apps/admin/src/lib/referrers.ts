/** Verwijzende sites groeperen (ADR 0032, 0034): alleen op hostnaam, zonder pad of zoekterm. */
export type RefKind = "direct" | "search" | "social" | "mail" | "other";
const SEARCH = /(^|\.)(google|bing|duckduckgo|ecosia|yahoo|startpage|qwant|yandex|baidu|brave|search)\.[a-z.]+$/;
const SOCIAL = /(^|\.)(pinterest|facebook|fb|instagram|tiktok|youtube|x|twitter|t|linkedin|reddit|whatsapp|threads|snapchat|bsky)\.[a-z.]+$/;
const MAIL = /(^|\.)(mail|outlook|gmail|webmail)\.|(^|\.)(outlook|live|hotmail)\.com$/;

export function refKind(host: string): RefKind {
  if (!host || host === "*") return host === "*" ? "other" : "direct";
  if (SEARCH.test(host)) return "search";
  if (SOCIAL.test(host)) return "social";
  if (MAIL.test(host)) return "mail";
  return "other";
}
export const REF_KIND_LABEL: Record<RefKind, string> = { direct: "Direct of onbekend", search: "Zoekmachines", social: "Sociale media", mail: "E-mail", other: "Andere sites" };
