import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { createTestApp } from "./app";

describe("vindbaarheid (ADR 0035)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  const admin = { authorization: "Bearer beheerder" };
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });

  it("toont de stand per markt en bewaart instellingen; alleen Kleurhoek zelf deelt ze met de website", async () => {
    const r = (await ctx.http.inject({ method: "GET", url: "/v1/admin/seo", headers: admin })).json();
    expect(r.indexableHost).toBe("www.kleurhoek.nl");
    expect(r.markets[0]).toMatchObject({ market: "nl-NL", language: "nl" });
    expect(r.markets[0].plates).toBeGreaterThan(0);
    const bad = await ctx.http.inject({ method: "PUT", url: "/v1/admin/seo", headers: admin, payload: { googleVerification: "<script>", bingVerification: null, home: {} } });
    expect(bad.statusCode).toBe(400);
    const ok = await ctx.http.inject({ method: "PUT", url: "/v1/admin/seo", headers: admin, payload: {
      googleVerification: "abcDEF123_-xyz", bingVerification: "", home: { "nl-NL": { title: "Kleurplaten om te printen", description: "Gratis eigen kleurplaten." } },
    } });
    expect(ok.json()).toMatchObject({ googleVerification: "abcDEF123_-xyz", bingVerification: null });
    const analist = await ctx.http.inject({ method: "PUT", url: "/v1/admin/seo", headers: { authorization: "Bearer analist" }, payload: { googleVerification: null, bingVerification: null, home: {} } });
    expect(analist.statusCode).toBe(403);
  });
});
