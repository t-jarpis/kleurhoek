import { describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));
vi.mock("./markets", async (orig) => ({ ...(await orig<typeof import("./markets")>()), LIVE_MARKETS: ["nl-nl"] }));
vi.mock("./api", () => ({
  api: {
    plates: async () => [{ slug: "kat", name: "Kat", category: "dieren", age: "4-6", world: null, holiday: null, svg: "/v1/assets/plates/kat/1.svg", kind: "kleurplaat", goals: [] }],
    themes: async () => [],
    taxonomy: async () => null,
  },
}));
const { marketSitemap } = await import("./sitemap");

describe("sitemap met afbeeldingen (ADR 0085)", () => {
  it("zet bij elke plaat de lijntekening en de ingekleurde PNG, en alleen bij platen", async () => {
    const xml = await marketSitemap("nl-nl");
    expect(xml).toContain('xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"');
    expect(xml).toMatch(/<loc>[^<]*\/platen\/kat<\/loc>.*<image:image><image:loc>[^<]*\/v1\/assets\/plates\/kat\/1\.png\?r=\d+<\/image:loc><\/image:image>/);
    expect(xml).toMatch(/<image:loc>[^<]*\/v1\/assets\/plates\/kat\/1\.kleur\.png\?r=\d+<\/image:loc>/);
    expect((xml.match(/<image:image>/g) ?? []).length).toBe(2);
  });
});
