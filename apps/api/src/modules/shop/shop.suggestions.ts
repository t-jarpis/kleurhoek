/**
 * Voorgestelde producten per materiaal (Amazon.nl), gezocht op 24 oktober 2026. Alleen een startpunt:
 * de beheerder voegt ze toe in het admin panel en controleert prijs en beschikbaarheid. De links zijn de
 * productpagina's zonder verwijzingen; de tracking-ID komt er pas bij de doorklik bij (sjabloon van de partner).
 */
export interface ProductSuggestion { slug: string; partner: string; url: string; name: string; note: string; materials: string[]; markets: string[] }

export const PRODUCT_SUGGESTIONS: ProductSuggestion[] = [
  { slug: "faber-castell-colour-grip-12", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B0007OECNU", name: "Faber-Castell Colour Grip kleurpotloden, 12 stuks", note: "Driekantig, goed vast te houden voor kleine handen", materials: ["kleurpotloden"], markets: ["nl-NL"] },
  { slug: "stabilo-trio-scribbi-14", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B01N2OB5Z8", name: "STABILO Trio Scribbi viltstiften, 14 kleuren", note: "Meeverende punt die niet indrukt", materials: ["stiften"], markets: ["nl-NL"] },
  { slug: "crayola-waskrijtjes-extra-dik-8", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B0002HYYBC", name: "Crayola waskrijtjes extra dik, 8 stuks", note: "Vanaf 1 jaar", materials: ["waskrijtjes"], markets: ["nl-NL"] },
  { slug: "fiskars-kinderschaar-4-jaar", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B005OA8V5M", name: "Fiskars kinderschaar, 13 cm", note: "Vanaf 4 jaar, met ronde punt", materials: ["kinderschaar"], markets: ["nl-NL"] },
  { slug: "pritt-lijmstift-2x11", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B005644KAQ", name: "Pritt lijmstift, 2 × 11 g", note: "Kindvriendelijk, zonder oplosmiddel", materials: ["lijmstift"], markets: ["nl-NL"] },
  { slug: "tesafilm-standaard-10", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B000TK0OZC", name: "tesafilm plakband, 10 rollen", note: "Transparant, 10 m × 15 mm", materials: ["plakband"], markets: ["nl-NL"] },
  { slug: "tekenblok-a4-160-gram", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B0GXWJ626L", name: "Tekenblok A4, 160 gram", note: "Stevig papier voor knutselplaten, 25 vellen", materials: ["stevig-papier"], markets: ["nl-NL"] },
  { slug: "led-lampionstokjes-10", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B0875PQWND", name: "Lampionstokjes met ledlampje, 10 stuks", note: "Veilig licht, geen kaarsje nodig", materials: ["led-lampionstokje"], markets: ["nl-NL"] },
  { slug: "splitpennen-200", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B08PDC2TWJ", name: "Splitpennen voor papier, 200 stuks", note: "Voor bewegende delen, met opbergdoos", materials: ["splitpennen"], markets: ["nl-NL"] },
];
