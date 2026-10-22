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
  // Amazon heeft per land een eigen partnerprogramma en eigen tracking-ID. Vooral voor markten buiten Nederland.
  {
    slug: "amazon-nl",
    name: "Amazon.nl",
    enabled: false,
    linkTemplate: "{url}?tag={tag}",
    settings: { tag: "" },
    allowedHosts: ["www.amazon.nl"],
  },
  {
    slug: "amazon-de",
    name: "Amazon.de",
    enabled: false,
    linkTemplate: "{url}?tag={tag}",
    settings: { tag: "" },
    allowedHosts: ["www.amazon.de"],
  },
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
