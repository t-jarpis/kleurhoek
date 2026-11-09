/**
 * Zustersite Denkhoek (ADR 0098): Kleurhoek wijst in de voettekst en met één tegel op de voorpagina naar Denkhoek,
 * gratis puzzels van dezelfde maker. Alleen in markten die hieronder staan, en alleen op Kleurhoek zelf (niet op de
 * eigen omgeving van een organisatie).
 *
 * Denkhoek is er nu alleen in het Nederlands. Komt er een taal bij: de markt aan DENKHOEK_MARKETS toevoegen en de
 * teksten (met het adres in die taal) aan DENKHOEK_TEXT. De teksten staan hier en niet in i18n/, net als die van de
 * Sinterklaaskalender (ADR 0065): ze worden alleen getoond in de talen die hier staan, en zo hoeven de andere 28
 * taalbestanden geen lege sleutels te krijgen.
 */

/** Wat de voettekst en de tegel nodig hebben. `blocks` = het beeldmerk van Denkhoek als krijt-tokens. */
export type SisterSite = {
  name: string;
  url: string;
  blocks: readonly string[];
  footer: string;
  title: string;
  text: string;
  cta: string;
};

type SisterText = Omit<SisterSite, "name" | "blocks">;

/** Markten waarin Kleurhoek naar Denkhoek wijst: nl-NL (kleurhoek.nl) en nl-BE (kleurhoek.be/nl). */
export const DENKHOEK_MARKETS: readonly string[] = ["nl-nl", "nl-be"];

/** Teksten en adres per taal. Een markt zonder tekst in zijn taal toont niets. */
const DENKHOEK_TEXT: Record<string, SisterText> = {
  nl: {
    url: "https://www.denkhoek.nl/",
    footer: "Ook van ons: Denkhoek – gratis puzzels",
    title: "Zin in een puzzel?",
    text: "Op Denkhoek, ook van ons, staan gratis sudoku's, doolhoven, woordzoekers, rekenpuzzels en meer. Online spelen of printen, zonder account.",
    cta: "Naar Denkhoek",
  },
};

/** Beeldmerk van Denkhoek: vier blokjes in de krijtkleuren, net als het logo daar. */
const DENKHOEK_BLOCKS = ["krijt-blauw", "krijt-teal", "krijt-paars", "krijt-amber"] as const;

/** Denkhoek voor deze markt, of null als Kleurhoek er in deze markt niet naar wijst. */
export function denkhoekFor(market: string): SisterSite | null {
  const m = market.toLowerCase();
  if (!DENKHOEK_MARKETS.includes(m)) return null;
  const text = DENKHOEK_TEXT[m.slice(0, 2)];
  return text ? { name: "Denkhoek", blocks: DENKHOEK_BLOCKS, ...text } : null;
}

/** Een gewone link naar een eigen site: geen nofollow, geen tracking-parameters; Denkhoek telt zelf de verwijzer. */
export const SISTER_LINK = { target: "_blank", rel: "noopener" } as const;
