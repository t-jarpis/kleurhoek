/**
 * Tegen scrapers (ADR 0045), in de website-proxy. Puur en zonder opslag: geen IP-adressen op schijf.
 * - Hotlinking: andere sites mogen onze plaatbestanden (SVG) niet in hun eigen pagina tonen.
 * - Paginalimiet per IP-adres: een mens haalt dit nooit (een hele klas achter één adres ook niet), een scraper wel.
 */

const OWN = /(^|\.)kleurhoek\.(nl|be|com)$|^localhost$|(^|\.)localhost$/;
/** Zoekmachines tonen afbeeldingen soms vanaf hun eigen pagina; dat mag. */
const SEARCH = /(^|\.)(google\.[a-z.]+|bing\.com|duckduckgo\.com|ecosia\.org|yahoo\.com|qwant\.com|startpage\.com|brave\.com)$/;
const PLATE_FILE = /^\/v1\/assets\/plates\/.+\.svg$/;

export function hotlinkBlocked(input: { path: string; dest: string | null; referer: string | null; siteHost: string }): boolean {
  if (!PLATE_FILE.test(input.path) || !input.referer) return false;
  // Alleen als de browser zegt dat het als afbeelding in een pagina komt; rechtstreeks openen blijft werken.
  if (input.dest !== "image") return false;
  let host: string;
  try { host = new URL(input.referer).hostname.toLowerCase(); } catch { return false; }
  return host !== input.siteHost && !OWN.test(host) && !SEARCH.test(host);
}

/** Zoekmachines die we graag zien, op naam in de user agent: geen paginalimiet. */
const GOOD_CRAWLER = /googlebot|bingbot|duckduckbot|applebot|yandexbot|google-inspectiontool/i;

export const PAGES_PER_MINUTE = 300;

/** Paginaweergaven per IP-adres per minuut, in het geheugen van deze instantie. */
export class PageLimiter {
  private hits = new Map<string, { n: number; start: number }>();
  constructor(private readonly limit = PAGES_PER_MINUTE, private readonly windowMs = 60_000) {}

  /** true = mag; false = te veel. */
  allow(ip: string | null, ua: string, now = Date.now()): boolean {
    if (!ip || GOOD_CRAWLER.test(ua)) return true;
    if (this.hits.size > 20_000) for (const [k, v] of this.hits) if (now - v.start > this.windowMs) this.hits.delete(k);
    const cur = this.hits.get(ip);
    if (!cur || now - cur.start > this.windowMs) { this.hits.set(ip, { n: 1, start: now }); return true; }
    cur.n++;
    return cur.n <= this.limit;
  }
}
