import { describe, expect, it } from "vitest";
import { hotlinkBlocked, PageLimiter } from "./guard";

describe("tegen scrapers (ADR 0045)", () => {
  const svg = "/v1/assets/plates/kat/1.svg";
  it("blokkeert plaatbestanden als afbeelding op een andere site", () => {
    expect(hotlinkBlocked({ path: svg, dest: "image", referer: "https://kopieer-site.example/pagina", siteHost: "www.kleurhoek.nl" })).toBe(true);
    expect(hotlinkBlocked({ path: svg, dest: "image", referer: "https://www.kleurhoek.be/fr", siteHost: "www.kleurhoek.be" })).toBe(false);
    expect(hotlinkBlocked({ path: svg, dest: "image", referer: "https://school.kleurhoek.nl/", siteHost: "www.kleurhoek.nl" })).toBe(false);
    expect(hotlinkBlocked({ path: svg, dest: "image", referer: "https://kleuren.mijnschool.nl/", siteHost: "kleuren.mijnschool.nl" })).toBe(false);
    expect(hotlinkBlocked({ path: svg, dest: "image", referer: "https://www.google.nl/", siteHost: "www.kleurhoek.nl" })).toBe(false);
    expect(hotlinkBlocked({ path: svg, dest: "document", referer: "https://elders.example/", siteHost: "www.kleurhoek.nl" })).toBe(false);
    expect(hotlinkBlocked({ path: svg, dest: "image", referer: null, siteHost: "www.kleurhoek.nl" })).toBe(false);
    expect(hotlinkBlocked({ path: "/v1/assets/plates/kat/1.png", dest: "image", referer: "https://mail.example/", siteHost: "www.kleurhoek.nl" })).toBe(false);
  });
  it("beperkt pagina's per IP-adres per minuut, niet voor zoekmachines", () => {
    const l = new PageLimiter(3, 60_000);
    const ua = "Mozilla/5.0 Safari";
    expect([1, 2, 3, 4].map(() => l.allow("203.0.113.7", ua, 0))).toEqual([true, true, true, false]);
    expect(l.allow("203.0.113.8", ua, 0)).toBe(true);
    expect(l.allow("203.0.113.7", ua, 61_000)).toBe(true);
    expect([1, 2, 3, 4, 5].every(() => l.allow("66.249.66.1", "Mozilla/5.0 (compatible; Googlebot/2.1)", 0))).toBe(true);
  });
});
