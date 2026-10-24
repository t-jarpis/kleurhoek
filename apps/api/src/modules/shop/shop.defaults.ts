/**
 * Amazon-winkels in Europa en de markten (land + taal) die ze bedienen (ADR 0031). Eén ASIN is meestal in
 * alle winkels hetzelfde product; het admin panel maakt er per winkel een product van.
 */
export const AMAZON_STORES = [
  { partner: "amazon-nl", name: "Amazon.nl", host: "www.amazon.nl", markets: ["nl-NL"] },
  { partner: "amazon-be", name: "Amazon.com.be", host: "www.amazon.com.be", markets: ["nl-BE", "fr-BE"] },
  { partner: "amazon-de", name: "Amazon.de", host: "www.amazon.de", markets: ["de-DE", "de-AT", "de-CH", "de-LU"] },
  { partner: "amazon-fr", name: "Amazon.fr", host: "www.amazon.fr", markets: ["fr-FR", "fr-LU", "fr-CH"] },
  { partner: "amazon-it", name: "Amazon.it", host: "www.amazon.it", markets: ["it-IT"] },
  { partner: "amazon-es", name: "Amazon.es", host: "www.amazon.es", markets: ["es-ES"] },
  { partner: "amazon-pl", name: "Amazon.pl", host: "www.amazon.pl", markets: ["pl-PL"] },
  { partner: "amazon-se", name: "Amazon.se", host: "www.amazon.se", markets: ["sv-SE"] },
  { partner: "amazon-uk", name: "Amazon.co.uk", host: "www.amazon.co.uk", markets: ["en-GB", "en-IE"] },
] as const;

/**
 * Partners die er standaard zijn. bol staat uit tot de eigenaar zijn site-ID invult in het admin panel.
 * Controleer het sjabloon in je bol-partneraccount (Linkbuilder); het is daar aan te passen.
 */
export interface PartnerDefaults { slug: string; name: string; enabled: boolean; linkTemplate: string; settings: Record<string, string>; allowedHosts: string[] }

export const DEFAULT_PARTNERS: PartnerDefaults[] = [
  {
    slug: "bol",
    name: "bol",
    enabled: false,
    linkTemplate: "https://partner.bol.com/click/click?p=2&t=url&s={siteId}&url={url}&f=TXL&name={subId}",
    settings: { siteId: "" },
    allowedHosts: ["www.bol.com", "bol.com"],
  },
  // Amazon heeft per land een eigen winkel, partnerprogramma en tracking-ID (ADR 0031). Elke winkel staat uit
  // tot de tracking-ID is ingevuld.
  ...AMAZON_STORES.map((s) => ({
    slug: s.partner, name: s.name, enabled: false, linkTemplate: "{url}?tag={tag}", settings: { tag: "" }, allowedHosts: [s.host],
  })),
  {
    slug: "direct",
    name: "Winkel zonder partnerprogramma",
    enabled: true,
    linkTemplate: "{url}",
    settings: {},
    // Leeg = elke https-winkel; per product controleert het admin panel de URL.
    allowedHosts: [],
  },
];
