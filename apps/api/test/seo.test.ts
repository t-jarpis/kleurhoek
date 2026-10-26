import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { OrganizationsService } from "../src/modules/organizations/organizations.service";
import { createTestApp } from "./app";

describe("vindbaarheid (ADR 0035)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  const admin = { authorization: "Bearer beheerder" };
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });

  it("vult de voorpagina per markt standaard in (ADR 0047)", async () => {
    const r = (await ctx.http.inject({ method: "GET", url: "/v1/admin/seo", headers: admin })).json();
    expect(r.settings.home["de-DE"].title).toContain("Ausmalbilder");
    expect(r.settings.home["en-US"].title).toContain("coloring");
    expect(Object.keys(r.settings.home)).toHaveLength(28);
  });

  it("toont de stand per markt en bewaart instellingen; alleen Kleurhoek zelf deelt ze met de website", async () => {
    const r = (await ctx.http.inject({ method: "GET", url: "/v1/admin/seo", headers: admin })).json();
    expect(r.indexableHost).toBe("www.kleurhoek.nl");
    const nl = r.markets.find((m: { market: string }) => m.market === "nl-NL");
    expect(nl).toMatchObject({ market: "nl-NL", language: "nl" });
    expect(nl.plates).toBeGreaterThan(0);
    const bad = await ctx.http.inject({ method: "PUT", url: "/v1/admin/seo", headers: admin, payload: { googleVerification: "<script>", bingVerification: null, home: {} } });
    expect(bad.statusCode).toBe(400);
    const ok = await ctx.http.inject({ method: "PUT", url: "/v1/admin/seo", headers: admin, payload: {
      googleVerification: "abcDEF123_-xyz", bingVerification: "", home: { "nl-NL": { title: "Kleurplaten om te printen", description: "Gratis eigen kleurplaten." } },
    } });
    expect(ok.json()).toMatchObject({ googleVerification: "abcDEF123_-xyz", bingVerification: null });
    const analist = await ctx.http.inject({ method: "PUT", url: "/v1/admin/seo", headers: { authorization: "Bearer analist" }, payload: { googleVerification: null, bingVerification: null, home: {} } });
    expect(analist.statusCode).toBe(403);
  });

  it("laat ingevulde teksten staan bij een nieuwe start", async () => {
    const orgs = ctx.app.get(OrganizationsService);
    await orgs.fillSeoDefaults();
    const r = (await ctx.http.inject({ method: "GET", url: "/v1/admin/seo", headers: admin })).json();
    expect(r.settings.home["nl-NL"].title).toBe("Kleurplaten om te printen");
  });
});
