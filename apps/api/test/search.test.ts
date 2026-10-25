import { generateKeyPairSync } from "node:crypto";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { bingDay, merge, pageKey, parseGoogleKey } from "../src/modules/analytics/search-engines";
import { SearchService, searchEngineOf } from "../src/modules/analytics/search.service";
import { createTestApp } from "./app";

const { privateKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
const KEY = JSON.stringify({ client_email: "kleurhoek@project.iam.gserviceaccount.com", private_key: privateKey.export({ type: "pkcs8", format: "pem" }) });

describe("zoekmachines: hulpfuncties (ADR 0041)", () => {
  it("leest sleutels, datums en adressen", () => {
    expect(parseGoogleKey(KEY)?.client_email).toContain("@");
    expect(parseGoogleKey(Buffer.from(KEY).toString("base64"))).not.toBeNull();
    expect(parseGoogleKey("{}")).toBeNull();
    expect(bingDay("/Date(1761350400000-0700)/")).toBe("2025-10-25");
    expect(pageKey("https://www.kleurhoek.be/fr/")).toBe("www.kleurhoek.be/fr");
    expect(searchEngineOf("www.google.be")).toBe("Google");
    expect(searchEngineOf("kleurhoek.nl")).toBeNull();
  });
  it("telt dubbele rijen op met gewogen positie", () => {
    const r = merge([
      { day: "2026-10-01", engine: "bing", site: "kleurhoek.nl", kind: "query", key: "kleurplaat", clicks: 1, impressions: 10, position: 2 },
      { day: "2026-10-01", engine: "bing", site: "kleurhoek.nl", kind: "query", key: "kleurplaat", clicks: 2, impressions: 30, position: 6 },
    ]);
    expect(r).toHaveLength(1);
    expect(r[0]).toMatchObject({ clicks: 3, impressions: 40, position: 5 });
  });
});

describe("zoekcijfers ophalen en tonen", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  const admin = { authorization: "Bearer beheerder" };
  const calls: string[] = [];
  beforeAll(async () => {
    process.env.SEARCH_DOMAINS = "kleurhoek.nl";
    process.env.GOOGLE_SEARCH_KEY = KEY;
    process.env.BING_WEBMASTER_KEY = "bing-test-key";
    process.env.SEARCH_IMPORT_INTERVAL_MS = "0";
    ctx = await createTestApp();
    const search = ctx.app.get(SearchService);
    search.fetch = async (url, init) => {
      calls.push(url);
      const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
      if (url.startsWith("https://oauth2.googleapis.com/token")) return json({ access_token: "t" });
      if (url.includes("searchconsole")) {
        const dims = (JSON.parse(String(init?.body)) as { dimensions: string[] }).dimensions;
        if (dims.length === 1) return json({ rows: [{ keys: ["2026-10-20"], clicks: 12, impressions: 300, position: 8 }] });
        if (dims[1] === "query") return json({ rows: [{ keys: ["2026-10-20", "kleurplaat kat"], clicks: 7, impressions: 100, position: 4 }] });
        return json({ rows: [{ keys: ["2026-10-20", "https://www.kleurhoek.nl/platen/kat"], clicks: 9, impressions: 120, position: 5 }] });
      }
      if (url.includes("GetRankAndTrafficStats")) return json({ d: [{ Date: "/Date(1792454400000)/", Clicks: 3, Impressions: 50 }] });
      if (url.includes("GetQueryStats")) return json({ d: [{ Date: "/Date(1792454400000)/", Query: "kleurplaat kat", Clicks: 1, Impressions: 20, AvgImpressionPosition: 6 }] });
      if (url.includes("GetPageStats")) return json({ d: [] });
      return json({}, 404);
    };
    await search.run(new Date("2026-10-25T12:00:00Z"));
  });
  afterAll(async () => {
    await ctx.app.close();
    for (const k of ["SEARCH_DOMAINS", "GOOGLE_SEARCH_KEY", "BING_WEBMASTER_KEY", "SEARCH_IMPORT_INTERVAL_MS"]) delete process.env[k];
  });

  it("haalt cijfers op bij Google en Bing en telt ze op", async () => {
    expect(calls.some((c) => c.includes(encodeURIComponent("sc-domain:kleurhoek.nl")))).toBe(true);
    expect(calls.some((c) => c.includes(encodeURIComponent("https://www.kleurhoek.nl/")))).toBe(true);
    const r = (await ctx.http.inject({ method: "GET", url: "/v1/admin/analytics/search?from=2026-10-01&to=2026-10-25", headers: admin })).json();
    expect(r.configured).toEqual({ domains: ["kleurhoek.nl"], engines: ["google", "bing"] });
    expect(r.totals.find((t: { engine: string }) => t.engine === "google")).toMatchObject({ clicks: 12, impressions: 300 });
    expect(r.totals.find((t: { engine: string }) => t.engine === "bing")).toMatchObject({ clicks: 3, impressions: 50 });
    expect(r.queries[0]).toMatchObject({ key: "kleurplaat kat", clicks: 8, impressions: 120 });
    expect(r.queries[0].position).toBeCloseTo(4.33, 1);
    expect(r.pages[0]).toMatchObject({ key: "www.kleurhoek.nl/platen/kat", clicks: 9 });
    expect(r.sync.every((s: { ok: boolean }) => s.ok)).toBe(true);
  });

  it("vervangt recente dagen bij een volgende ronde (geen dubbele tellingen)", async () => {
    await ctx.app.get(SearchService).run(new Date("2026-10-26T12:00:00Z"));
    const r = (await ctx.http.inject({ method: "GET", url: "/v1/admin/analytics/search?from=2026-10-01&to=2026-10-25", headers: admin })).json();
    expect(r.totals.find((t: { engine: string }) => t.engine === "google")).toMatchObject({ clicks: 12 });
  });

  it("vraagt beheerrechten om nu op te halen", async () => {
    const res = await ctx.http.inject({ method: "POST", url: "/v1/admin/analytics/search/refresh", headers: { authorization: "Bearer analist" } });
    expect([401, 403]).toContain(res.statusCode);
  });
});
