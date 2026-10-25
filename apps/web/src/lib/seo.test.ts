import { afterEach, describe, expect, it, vi } from "vitest";

const DOMAINS = (sub: string) => JSON.stringify({ nl: `https://${sub}.kleurhoek.nl`, be: `https://${sub}.kleurhoek.be`, com: `https://${sub}.kleurhoek.com` });
async function load(site: string) {
  vi.resetModules();
  vi.stubEnv("SITE_URL", site);
  vi.stubEnv("SITE_DOMAINS", DOMAINS(new URL(site).hostname.split(".")[0]!));
  return import("./seo");
}
const org = (isDefault: boolean) => ({ isDefault }) as Parameters<Awaited<ReturnType<typeof load>>["indexable"]>[0];

afterEach(() => vi.unstubAllEnvs());

describe("vindbaarheid (ADR 0035)", () => {
  it("indexeert alleen Kleurhoek zelf op het productiedomein", async () => {
    const prod = await load("https://www.kleurhoek.nl");
    expect(prod.indexable(org(true))).toBe(true);
    expect(prod.indexable(org(false))).toBe(false);
    expect(prod.indexableHost("www.kleurhoek.nl")).toBe(true);
    expect(prod.indexableHost("www.kleurhoek.be")).toBe(true);
    expect(prod.indexableHost("www.kleurhoek.com")).toBe(true);
    expect(prod.indexableHost("school.kleurhoek.nl")).toBe(false);
    const dev = await load("https://dev.kleurhoek.nl");
    expect(dev.indexable(org(true))).toBe(false);
    expect(dev.indexableHost("dev.kleurhoek.nl")).toBe(false);
  });
  it("geeft canonical en taalversies alleen als de pagina geïndexeerd wordt", async () => {
    const prod = await load("https://www.kleurhoek.nl");
    expect(prod.pageMeta(org(true), "nl-nl", "/themas").alternates?.canonical).toBe("https://www.kleurhoek.nl/themas");
    // Elke markt op haar eigen domein (ADR 0040), x-default op de beginpagina naar kleurhoek.com.
    const home = prod.pageMeta(org(true), "fr-be", "").alternates!;
    expect(home.canonical).toBe("https://www.kleurhoek.be/fr");
    expect(home.languages).toMatchObject({ "nl-NL": "https://www.kleurhoek.nl", "nl-BE": "https://www.kleurhoek.be/nl", "x-default": "https://www.kleurhoek.com/" });
    expect(prod.pageMeta(org(false), "nl-nl", "/themas")).toEqual({});
    expect(prod.hreflang("nl-be")).toBe("nl-BE");
    expect(prod.jsonLd({ a: "</script>" })).not.toContain("</");
  });
});
