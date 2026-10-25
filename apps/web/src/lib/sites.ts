/**
 * Domeinen per land (ADR 0040). Elke markt woont op één domein, met een vast voorvoegsel:
 *   kleurhoek.nl   nl-nl op de wortel          www.kleurhoek.nl/platen/kat
 *   kleurhoek.be   nl-be op /nl, fr-be op /fr  www.kleurhoek.be/fr/platen/chat
 *   kleurhoek.com  elke andere markt op /<markt> www.kleurhoek.com/de-de/platen/katze
 * Geen doorsturen op browsertaal, behalve op de beginpagina van een meertalig domein (Google raadt dat af voor
 * diepe links). Lokaal, op organisatiesites en zonder domeinconfiguratie blijft het oude schema: /<markt>/…
 * Pure functies: werkt in de proxy, op de server en in tests.
 */

export type DomainKey = "nl" | "be" | "com";
export type Domains = Record<DomainKey, string>;
export const DOMAIN_KEYS: DomainKey[] = ["nl", "be", "com"];
export const MARKET = /^[a-z]{2}-[a-z]{2}$/;

export function domainOf(market: string): DomainKey {
  if (market === "nl-nl") return "nl";
  if (market.endsWith("-be")) return "be";
  return "com";
}

/** Voorvoegsel van een markt op haar eigen domein: "" voor nl-nl, "/fr" voor fr-be, "/de-de" op .com. */
export function prefixOf(market: string): string {
  const d = domainOf(market);
  return d === "nl" ? "" : d === "be" ? `/${market.slice(0, 2)}` : `/${market}`;
}

/**
 * De domeinen van deze omgeving, uit SITE_DOMAINS (JSON: { "nl": "https://www.kleurhoek.nl", "be": …, "com": … }).
 * Terraform zet die zodra de domeinen per land bestaan. Zonder (lokaal, of nog niet uitgerold) geldt het oude
 * schema met /<markt>.
 */
export function siteDomains(env: Record<string, string | undefined> = process.env): Domains | null {
  if (!env.SITE_DOMAINS) return null;
  try {
    const d = JSON.parse(env.SITE_DOMAINS) as Partial<Domains>;
    if (DOMAIN_KEYS.every((k) => typeof d[k] === "string" && /^https?:\/\/[^/]+$/.test(d[k]!))) return d as Domains;
  } catch { /* ongeldig: oude schema */ }
  return null;
}

const hostOf = (origin: string) => new URL(origin).host.toLowerCase();

/** Bij welk domein hoort deze host (zonder poort)? */
export function domainForHost(host: string | null, domains: Domains | null): DomainKey | null {
  if (!host || !domains) return null;
  const h = host.toLowerCase().replace(/:\d+$/, "");
  return DOMAIN_KEYS.find((k) => hostOf(domains[k]).replace(/:\d+$/, "") === h) ?? null;
}

/** Pad binnen de site voor een markt: met domeinen het voorvoegsel, anders /<markt>. */
export const basePath = (market: string, mapped: boolean) => (mapped ? prefixOf(market) : `/${market}`);

/** Volledig adres van een pagina in een markt (voor canonical, hreflang, sitemap, taalwisselaar). */
export function marketUrl(market: string, path: string, domains: Domains | null, fallbackOrigin: string): string {
  return domains ? `${domains[domainOf(market)]}${prefixOf(market)}${path}` : `${fallbackOrigin}/${market}${path}`;
}

/** Talen uit Accept-Language, op volgorde (alleen de eerste twee letters). */
export const browserLanguages = (acceptLanguage: string | null) =>
  (acceptLanguage ?? "").split(",").map((l) => l.split(";")[0]!.trim().slice(0, 2).toLowerCase()).filter(Boolean);

export type Route =
  | { kind: "page"; market: string; rest: string }
  | { kind: "redirect"; location: string; permanent: boolean }
  | { kind: "missing" };

/**
 * Wat doet de proxy met een pagina-adres op een van de eigen domeinen? `live` zijn de markten die live staan;
 * `best` kiest bij een beginpagina de beste markt (land en browsertaal).
 */
export function routeFor(input: {
  domain: DomainKey; path: string; live: string[]; domains: Domains;
  acceptLanguage: string | null; best: (candidates: string[]) => string;
}): Route {
  const { domain, path, live, domains } = input;
  const here = live.filter((m) => domainOf(m) === domain);
  const segs = path.split("/").filter(Boolean);
  const first = segs[0] ?? "";
  const restAfter = (n: number) => (segs.length > n ? `/${segs.slice(n).join("/")}` : "");
  const to = (market: string, rest: string, permanent: boolean): Route => ({ kind: "redirect", location: marketUrl(market, rest, domains, ""), permanent });

  // Oud schema (/nl-nl/…, /nl-be/…): blijvend naar het nieuwe adres, ook als dat op een ander domein is.
  if (MARKET.test(first) && live.includes(first) && !(domain === "com" && domainOf(first) === "com")) return to(first, restAfter(1), true);

  if (domain === "nl") {
    return here.includes("nl-nl") ? { kind: "page", market: "nl-nl", rest: path === "/" ? "" : path } : (path === "/" ? to(input.best(live), "", false) : { kind: "missing" });
  }

  if (domain === "be") {
    const byLang = (lang: string) => here.find((m) => m.startsWith(`${lang}-`));
    if (/^[a-z]{2}$/.test(first) && byLang(first)) return { kind: "page", market: byLang(first)!, rest: restAfter(1) };
    if (!here.length) return to(input.best(live), "", false);
    // Beginpagina: de browsertaal kiest (tijdelijk, 302); zonder voorkeur Nederlands.
    if (segs.length === 0) {
      const lang = browserLanguages(input.acceptLanguage).find((l) => byLang(l));
      return to(byLang(lang ?? "nl") ?? here[0]!, "", false);
    }
    // Een pad zonder taal (oude link): naar de Nederlandstalige versie.
    return to(byLang("nl") ?? here[0]!, path, true);
  }

  // .com: elke markt in een eigen map; de beginpagina kiest de beste markt over alle domeinen.
  if (MARKET.test(first) && here.includes(first)) return { kind: "page", market: first, rest: restAfter(1) };
  if (segs.length === 0) return to(input.best(live), "", false);
  return { kind: "missing" };
}

/** Link binnen de markt: `link("", "/platen/kat")` → "/platen/kat"; `link("", "")` → "/"; `link("/fr", "?x=1")` → "/fr?x=1". */
export const link = (base: string, path = "") => (path === "" || /^[?#]/.test(path) ? (base || "/") + path : base + path);

/** Naam van een markt in haar eigen taal: "Nederland", "België · Nederlands", "Belgique · Français". */
export function marketLabel(market: string): string {
  const [lang = "nl", country = ""] = market.split("-");
  const region = new Intl.DisplayNames([lang], { type: "region" }).of(country.toUpperCase()) ?? country;
  // Alleen bij een land met meer talen op de site ook de taal.
  if (!["be", "ch", "ca"].includes(country)) return region;
  const language = new Intl.DisplayNames([lang], { type: "language" }).of(lang) ?? lang;
  return `${region} · ${language.charAt(0).toUpperCase()}${language.slice(1)}`;
}

/** Een markt in de taalkeuze: waar haar beginpagina is (absoluut op een eigen domein, anders /<markt>). */
export interface SiteEntry { market: string; root: string; label: string }
export function siteEntries(markets: string[], domains: Domains | null): SiteEntry[] {
  return markets.map((m) => ({ market: m, root: domains ? `${domains[domainOf(m)]}${prefixOf(m)}` : `/${m}`, label: marketLabel(m) }));
}

/** Het domein voor onder een vel (PlateMark): kleurhoek.nl, kleurhoek.be of kleurhoek.com, zonder www. */
export function markFor(market: string, domains: Domains | null): string {
  if (!domains) return "kleurhoek.nl";
  return new URL(domains[domainOf(market)]).host.replace(/^www\./, "");
}
