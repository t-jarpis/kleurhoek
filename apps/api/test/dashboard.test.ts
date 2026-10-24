import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { AnalyticsService, buckets } from "../src/modules/analytics/analytics.service";
import { createTestApp, INGEST_KEY, TENANT } from "./app";

describe("dashboard: pagina's, tijdreeksen en accounts (ADR 0020)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });

  const ev = (type: string, extra: Record<string, unknown>) => ({ type, market: "nl-NL", device: "mobile", country: "NL", ...extra });
  const ingest = (batch: unknown[]) => ctx.http.inject({ method: "POST", url: "/v1/internal/events", headers: { "x-ingest-key": INGEST_KEY }, payload: batch as object[] });
  const admin = (url: string, auth = "Bearer analist") => ctx.http.inject({ method: "GET", url, headers: { authorization: auth } });

  it("slaat de soort pagina en de organisatie op, maar geen adressen", async () => {
    expect((await ingest([ev("page_view", { page: "/nl-nl/platen/kat?x=1" })])).statusCode).toBe(400);
    expect((await ingest([ev("page_view", { page: "home", org: "Kleurhoek" })])).statusCode).toBe(400);
    const day = "2026-10-20", at = (h: number) => `${day}T${String(h).padStart(2, "0")}:00:00.000Z`;
    const r = await ingest([
      ev("page_view", { page: "home", org: "kleurhoek", visitorHash: "aaaaaaaaaaaaaaaa", occurredAt: at(8) }),
      ev("page_view", { page: "plaat", org: "kleurhoek", plate: "kat", visitorHash: "aaaaaaaaaaaaaaaa", occurredAt: at(8) }),
      ev("plate_view", { plate: "kat", org: "kleurhoek", visitorHash: "aaaaaaaaaaaaaaaa", occurredAt: at(8) }),
      ev("pdf_download", { plate: "kat", org: "kleurhoek", visitorHash: "aaaaaaaaaaaaaaaa", occurredAt: at(9) }),
      ev("page_view", { page: "home", org: "de-regenboog", device: "desktop", visitorHash: "bbbbbbbbbbbbbbbb", occurredAt: at(10) }),
      ev("page_view", { page: "boekje", org: "de-regenboog", device: "desktop", visitorHash: "bbbbbbbbbbbbbbbb", occurredAt: at(10) }),
    ]);
    expect(r.statusCode).toBe(202);
    await ctx.app.get(AnalyticsService).aggregateDay(TENANT, day);

    const o = (await admin(`/v1/admin/analytics/overview?from=2026-10-14&to=${day}`)).json();
    expect(o.bucket).toBe("day");
    expect(o.series).toHaveLength(7);
    expect(o.series.at(-1)).toMatchObject({ date: day, visitors: 2, pageViews: 4, plateViews: 1, downloads: 1 });
    expect(o.totals).toMatchObject({ visitors: 2, pageViews: 4, downloads: 1 });
    expect(o.previous).toEqual({ from: "2026-10-07", to: "2026-10-13" });
    expect(o.pages).toEqual(expect.arrayContaining([{ page: "home", views: 2, visitors: 2 }, { page: "plaat", views: 1, visitors: 1 }, { page: "boekje", views: 1, visitors: 1 }]));
    expect(o.devices).toEqual(expect.arrayContaining([{ device: "mobile", views: 2 }, { device: "desktop", views: 2 }]));
    expect(o.organizations).toEqual(expect.arrayContaining([{ org: "kleurhoek", visitors: 1, views: 2 }, { org: "de-regenboog", visitors: 1, views: 2 }]));
  });

  it("groepeert per week bij een lange periode en vult lege weken", () => {
    expect(buckets("2026-10-01", "2026-10-20", "week")).toEqual(["2026-09-28", "2026-10-05", "2026-10-12", "2026-10-19"]);
    expect(buckets("2026-10-19", "2026-10-21", "day")).toEqual(["2026-10-19", "2026-10-20", "2026-10-21"]);
  });

  it("geeft accountcijfers alleen als tellingen, met analytics.read", async () => {
    const r = await admin("/v1/admin/users/stats?from=2026-10-14&to=2026-10-20");
    expect(r.statusCode).toBe(200);
    expect(r.json()).toMatchObject({ total: expect.any(Number), created: expect.any(Number), active: expect.any(Number), returning: expect.any(Number), series: expect.any(Array) });
    expect(JSON.stringify(r.json())).not.toMatch(/@|email/);
    expect((await admin("/v1/admin/users/stats?from=2026-10-20&to=2026-10-14")).statusCode).toBe(400);
  });

  it("telt binnenkomsten per domein en verwijzende site, zonder paden (ADR 0032)", async () => {
    expect((await ingest([ev("page_view", { page: "home", entry: "be", referrer: "google.com/search?q=x" })])).statusCode).toBe(400);
    expect((await ingest([ev("page_view", { page: "home", entry: "de" })])).statusCode).toBe(400);
    const day = "2026-10-22", at = (h: number) => `${day}T${String(h).padStart(2, "0")}:00:00.000Z`;
    await ingest([
      ev("page_view", { page: "home", entry: "be", referrer: "google.com", visitorHash: "cccccccccccccccc", occurredAt: at(8) }),
      ev("page_view", { page: "plaat", visitorHash: "cccccccccccccccc", occurredAt: at(8) }), // daarna: geen binnenkomst
      ev("page_view", { page: "home", entry: "nl", referrer: "", visitorHash: "dddddddddddddddd", occurredAt: at(9) }),
      ev("page_view", { page: "home", entry: "nl", referrer: "pinterest.com", visitorHash: "eeeeeeeeeeeeeeee", occurredAt: at(9) }),
    ]);
    await ctx.app.get(AnalyticsService).aggregateDay(TENANT, day);
    const o = (await admin(`/v1/admin/analytics/overview?from=${day}&to=${day}`)).json();
    expect(o.entries).toEqual([{ entry: "nl", landings: 2, visitors: 2 }, { entry: "be", landings: 1, visitors: 1 }]);
    expect(o.referrers).toEqual(expect.arrayContaining([{ referrer: "google.com", landings: 1 }, { referrer: "pinterest.com", landings: 1 }, { referrer: "", landings: 1 }]));
  });

  it("gooit ruwe events na 90 dagen weg, dagtotalen blijven", async () => {
    const svc = ctx.app.get(AnalyticsService);
    await svc.purgeRawEvents(TENANT, new Date("2027-02-01T00:00:00Z"));
    await svc.aggregateDay(TENANT, "2026-10-21"); // andere dag: raakt 20 oktober niet
    const o = (await admin("/v1/admin/analytics/overview?from=2026-10-20&to=2026-10-20")).json();
    expect(o.totals.pageViews).toBe(4);
  });
});
