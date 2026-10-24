import { afterEach, describe, expect, it, vi } from "vitest";

async function load(site: string) {
  vi.resetModules();
  vi.stubEnv("SITE_URL", site);
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
    expect(prod.indexableHost("school.kleurhoek.nl")).toBe(false);
    const dev = await load("https://dev.kleurhoek.nl");
    expect(dev.indexable(org(true))).toBe(false);
    expect(dev.indexableHost("dev.kleurhoek.nl")).toBe(false);
  });
  it("geeft canonical en taalversies alleen als de pagina geïndexeerd wordt", async () => {
    const prod = await load("https://www.kleurhoek.nl");
    expect(prod.pageMeta(org(true), "nl-nl", "/themas").alternates?.canonical).toBe("https://www.kleurhoek.nl/nl-nl/themas");
    expect(prod.pageMeta(org(false), "nl-nl", "/themas")).toEqual({});
    expect(prod.hreflang("nl-be")).toBe("nl-BE");
    expect(prod.jsonLd({ a: "</script>" })).not.toContain("</");
  });
});
