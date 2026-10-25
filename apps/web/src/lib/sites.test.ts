import { describe, expect, it } from "vitest";
import { basePath, domainForHost, marketUrl, prefixOf, routeFor, siteDomains, type Domains } from "./sites";

const PROD = JSON.stringify({ nl: "https://www.kleurhoek.nl", be: "https://www.kleurhoek.be", com: "https://www.kleurhoek.com" });
const prod = siteDomains({ SITE_DOMAINS: PROD })!;
const live = ["nl-nl", "nl-be", "fr-be"];
const r = (domain: "nl" | "be" | "com", path: string, accept: string | null = null, markets = live) =>
  routeFor({ domain, path, live: markets, domains: prod, acceptLanguage: accept, best: (c) => c[0]! });

describe("domeinen per land (ADR 0040)", () => {
  it("leest de domeinen uit SITE_DOMAINS; zonder (of ongeldig) het oude schema", () => {
    expect(prod).toEqual({ nl: "https://www.kleurhoek.nl", be: "https://www.kleurhoek.be", com: "https://www.kleurhoek.com" });
    expect(siteDomains({ SITE_URL: "https://www.kleurhoek.nl" })).toBeNull();
    expect(siteDomains({ SITE_DOMAINS: "{\"nl\":\"x\"}" })).toBeNull();
    const own: Domains = { nl: "http://nl.localhost:3000", be: "http://be.localhost:3000", com: "http://com.localhost:3000" };
    expect(siteDomains({ SITE_DOMAINS: JSON.stringify(own) })).toEqual(own);
    expect(domainForHost("WWW.kleurhoek.be", prod)).toBe("be");
    expect(domainForHost("school.kleurhoek.nl", prod)).toBeNull();
  });

  it("geeft elke markt een vast adres", () => {
    expect(prefixOf("nl-nl")).toBe("");
    expect(prefixOf("fr-be")).toBe("/fr");
    expect(prefixOf("de-de")).toBe("/de-de");
    expect(marketUrl("fr-be", "/platen/kat", prod, "")).toBe("https://www.kleurhoek.be/fr/platen/kat");
    expect(marketUrl("nl-nl", "", null, "http://localhost:3000")).toBe("http://localhost:3000/nl-nl");
    expect(basePath("nl-be", true)).toBe("/nl");
    expect(basePath("nl-be", false)).toBe("/nl-be");
  });

  it("toont op .nl Nederland zonder voorvoegsel en stuurt oude adressen blijvend door", () => {
    expect(r("nl", "/")).toEqual({ kind: "page", market: "nl-nl", rest: "" });
    expect(r("nl", "/platen/kat")).toEqual({ kind: "page", market: "nl-nl", rest: "/platen/kat" });
    expect(r("nl", "/nl-nl/platen/kat")).toEqual({ kind: "redirect", location: "https://www.kleurhoek.nl/platen/kat", permanent: true });
    expect(r("nl", "/fr-be")).toEqual({ kind: "redirect", location: "https://www.kleurhoek.be/fr", permanent: true });
  });

  it("kiest op de beginpagina van .be de browsertaal, maar nooit bij diepe links", () => {
    expect(r("be", "/", "fr-BE,fr;q=0.9,nl;q=0.5")).toEqual({ kind: "redirect", location: "https://www.kleurhoek.be/fr", permanent: false });
    expect(r("be", "/", "en-US")).toEqual({ kind: "redirect", location: "https://www.kleurhoek.be/nl", permanent: false });
    expect(r("be", "/fr/platen/kat", "nl-BE")).toEqual({ kind: "page", market: "fr-be", rest: "/platen/kat" });
    expect(r("be", "/platen/kat")).toEqual({ kind: "redirect", location: "https://www.kleurhoek.be/nl/platen/kat", permanent: true });
    expect(r("be", "/", "fr", ["nl-nl"])).toEqual({ kind: "redirect", location: "https://www.kleurhoek.nl", permanent: false });
  });

  it("zet op .com elke markt in een eigen map en kiest bij de beginpagina de beste markt", () => {
    expect(r("com", "/", null, ["de-de", "nl-nl"])).toEqual({ kind: "redirect", location: "https://www.kleurhoek.com/de-de", permanent: false });
    expect(r("com", "/de-de/platen/kat", null, ["de-de"])).toEqual({ kind: "page", market: "de-de", rest: "/platen/kat" });
    expect(r("com", "/nl-be/platen/kat")).toEqual({ kind: "redirect", location: "https://www.kleurhoek.be/nl/platen/kat", permanent: true });
    expect(r("com", "/onzin")).toEqual({ kind: "missing" });
  });
});

describe("link", () => {
  it("maakt links met en zonder voorvoegsel", async () => {
    const { link } = await import("./sites");
    expect(link("", "")).toBe("/");
    expect(link("", "?onderwerp=feest#platen")).toBe("/?onderwerp=feest#platen");
    expect(link("/fr", "")).toBe("/fr");
    expect(link("/fr", "/platen/chat")).toBe("/fr/platen/chat");
    expect(link("/nl-nl", "/mail")).toBe("/nl-nl/mail");
  });
});
