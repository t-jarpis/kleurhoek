import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { SiteFooter } from "@/components/SiteFooter";
import { SisterFooterLink, SisterSite } from "@/components/SisterSite";
import { messages } from "@/i18n/nl";
import { DEFAULT_MARKETS } from "./markets";
import { DENKHOEK_MARKETS, denkhoekFor } from "./sister-sites";

const ALL = DEFAULT_MARKETS.split(",");

describe("Denkhoek als zustersite (ADR 0098)", () => {
  it("staat alleen in de Nederlandstalige markten", () => {
    expect(denkhoekFor("nl-nl")?.url).toBe("https://www.denkhoek.nl/");
    expect(denkhoekFor("nl-BE")?.footer).toBe("Ook van ons: Denkhoek – gratis puzzels");
    for (const m of ["fr-be", "en-gb", "de-de", "fr-fr", "en-us"]) expect(denkhoekFor(m), m).toBeNull();
    expect(ALL.filter((m) => denkhoekFor(m))).toEqual(["nl-nl", "nl-be"]);
  });
  it("elke markt in de lijst is live en heeft een tekst in zijn taal", () => {
    for (const m of DENKHOEK_MARKETS) {
      expect(ALL, m).toContain(m);
      expect(denkhoekFor(m), m).not.toBeNull();
    }
  });
  it("is een gewone link: nieuw tabblad, noopener, geen nofollow of tracking-parameters", () => {
    const site = denkhoekFor("nl-nl");
    for (const html of [renderToStaticMarkup(createElement(SisterSite, { site })), renderToStaticMarkup(createElement(SisterFooterLink, { site }))]) {
      expect(html).toContain('href="https://www.denkhoek.nl/"');
      expect(html).toContain('target="_blank"');
      expect(html).toContain('rel="noopener"');
      expect(html).not.toMatch(/nofollow|noreferrer|utm_|\?via=/);
    }
  });
  it("toont niets in een andere markt", () => {
    expect(renderToStaticMarkup(createElement(SisterSite, { site: denkhoekFor("fr-be") }))).toBe("");
    expect(renderToStaticMarkup(createElement(SisterFooterLink, { site: denkhoekFor("de-de") }))).toBe("");
  });
  it("de tegel heeft een kop, het beeldmerk is decoratief en de kleuren zijn tokens", () => {
    const html = renderToStaticMarkup(createElement(SisterSite, { site: denkhoekFor("nl-be") }));
    expect(html).toContain('<aside class="kh-sister no-print" aria-labelledby="kh-sister-title">');
    expect(html).toContain('<h2 id="kh-sister-title">Zin in een puzzel?</h2>');
    expect(html).toContain('<span class="kh-logo-mark" aria-hidden="true">');
    expect(html.match(/background:var\(--krijt-[a-z]+\)/g)).toHaveLength(4);
  });
});

describe("voettekst", () => {
  it("wijst alleen op Kleurhoek zelf en in nl-NL en nl-BE naar Denkhoek", () => {
    const footer = (market: string, own: boolean) => renderToStaticMarkup(createElement(SiteFooter, { base: "", t: messages(market), market, own }));
    expect(footer("nl-nl", true)).toContain("Ook van ons: Denkhoek – gratis puzzels");
    expect(footer("nl-be", true)).toContain("https://www.denkhoek.nl/");
    expect(footer("nl-nl", false)).not.toContain("denkhoek");
    expect(footer("fr-be", true)).not.toContain("denkhoek");
    expect(footer("en-gb", true)).not.toContain("denkhoek");
  });
});
