/**
 * Spamscore voor het contactformulier (ADR 0048). Geen captcha: een bericht met een hoge score komt in de map
 * Spam in de inbox, zonder melding, en is met één klik terug te zetten. Niets wordt weggegooid.
 */
export const SPAM_THRESHOLD = 3;

/** Verkooppraat die bij Kleurhoek niet thuishoort: SEO, marketing, webdesign, links, offertes. */
const PITCH: [RegExp, number, string][] = [
  [/\b(seo|aeo|geo)\b/i, 2, "SEO-aanbod"],
  [/search engine optimi[sz]ation|answer engine|generative engine|zoekmachineoptimalisatie/i, 2, "SEO-aanbod"],
  [/\brank(ing|s)?\b[^.]{0,40}\b(google|search)|first page (of|on) google|eerste pagina van google|top of google/i, 2, "Google-ranking"],
  [/back ?links?|link ?building|guest ?posts?|sponsored (post|article)|gastblog/i, 2, "Links of gastblogs"],
  [/\b(quote|price ?list|pricing|proposal|offerte|prijslijst)\b/i, 1, "Offerte of prijslijst"],
  [/(digital|online) marketing|marketing agency|web ?design (services|agency)|app development|lead generation|qualified (traffic|leads)|more (traffic|leads|sales)|online visibility|brand visibility/i, 2, "Marketingaanbod"],
  [/\b(outsourc\w*|white[- ]label|virtual assistant|our services|free (audit|consultation|trial)|(15|30)[- ]min(ute)? call|schedule a (call|meeting)|book a (call|demo))\b/i, 1, "Diensten aangeboden"],
  [/\b(crypto|bitcoin|forex|casino|betting|loan|viagra|cbd)\b/i, 3, "Bekende spamwoorden"],
  [/\breply\s+["']?(stop|no|unsubscribe)|to opt out|unsubscribe\b/i, 2, "Massamail"],
];

/** "Hey team kleurhoek.com": de domeinnaam als aanhef is typisch voor een sjabloon dat duizenden sites afloopt. */
const TEMPLATE_GREETING = /\b(hi|hey|hello|dear|hallo|beste)\b[^\n]{0,20}\bkleurhoek\.(com|nl|be)\b/i;

export interface SpamInput { message: string; name: string | null; email: string; pow: "ok" | "missing" | "invalid" }

export function spamScore(f: SpamInput): { score: number; reasons: string[] } {
  const reasons = new Set<string>();
  let score = 0;
  const add = (n: number, why: string) => { score += n; reasons.add(why); };
  for (const [re, n, why] of PITCH) if (re.test(f.message)) add(n, why);
  if (TEMPLATE_GREETING.test(f.message)) add(2, "Domeinnaam als aanhef");
  const links = (f.message.match(/https?:\/\/|www\./gi) ?? []).length;
  if (links) add(Math.min(links, 3), "Links in het bericht");
  if (f.name && /https?:\/\/|www\.|\.(com|net|io)\b/i.test(f.name)) add(2, "Link als naam");
  if (f.pow === "missing") add(3, "Formulier niet via de site verstuurd");
  if (f.pow === "invalid") add(3, "Ongeldige controle van de browser");
  return { score, reasons: [...reasons] };
}
