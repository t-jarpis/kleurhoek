import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { AnalyticsService, buckets } from "../src/modules/analytics/analytics.service";
import { and, eq, sql } from "drizzle-orm";
import { DB, type Database } from "../src/db/database";
import { withTenant } from "../src/db/tenant";
import { dailyTotals, events } from "../src/modules/analytics/analytics.schema";
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
    expect(o.series.at(-1)).toMatchObject({ date: day, visitors: 2, pageViews: 4, plateViews: 1, downloads: 1, pdfDownloads: 1, prints: 0 });
    expect(o.totals).toMatchObject({ visitors: 2, pageViews: 4, downloads: 1 });
    expect(o.previous).toEqual({ from: "2026-10-07", to: "2026-10-13" });
    expect(o.pages).toEqual(expect.arrayContaining([{ page: "home", views: 2, visitors: 2 }, { page: "plaat", views: 1, visitors: 1 }, { page: "boekje", views: 1, visitors: 1 }]));
    expect(o.devices).toEqual(expect.arrayContaining([{ device: "mobile", views: 2 }, { device: "desktop", views: 2 }]));
    expect(o.organizations).toEqual(expect.arrayContaining([{ org: "kleurhoek", visitors: 1, views: 2 }, { org: "de-regenboog", visitors: 1, views: 2 }]));
  });

  it("laat zien wanneer er gedownload wordt: weekdag en uur in Nederlandse tijd (ADR 0073)", async () => {
    const svc = ctx.app.get(AnalyticsService);
    // 2026-10-20 is een dinsdag; 09:00 UTC is 11:00 in Amsterdam (zomertijd).
    const a = await svc.activity(TENANT, "2026-10-20", "2026-10-20");
    expect(a.grid).toContainEqual({ weekday: 2, hour: 11, count: expect.any(Number) });
    expect(a.latest[0]).toMatchObject({ type: "pdf_download", plate: "kat", market: "nl-NL", device: "mobile", at: "2026-10-20T09:00:00.000Z" });
    expect(a.limited).toBe(false);
    // Een periode van een jaar: de ruwe events blijven bewaard (ADR 0078), dus de hele periode.
    const y = await svc.activity(TENANT, "2025-10-21", "2026-10-20");
    expect(y).toMatchObject({ from: "2025-10-21", limited: false });
    expect((await admin("/v1/admin/analytics/activity?from=2026-10-20&to=2026-10-20")).statusCode).toBe(200);
  });

  it("toont per download hoe dat bezoek binnenkwam, alleen op dezelfde dag (ADR 0083)", async () => {
    const h = "dddddddddddddddd", other = "eeeeeeeeeeeeeeee";
    expect((await ingest([
      ev("page_view", { page: "plaat", plate: "uil", entry: "be", referrer: "google.com", visitorHash: h, occurredAt: "2026-10-21T07:00:00.000Z" }),
      ev("print", { plate: "uil", visitorHash: h, occurredAt: "2026-10-21T07:05:00.000Z" }),
      ev("print", { plate: "kat", visitorHash: other, occurredAt: "2026-10-21T08:00:00.000Z" }),
    ])).statusCode).toBe(202);
    const a = await ctx.app.get(AnalyticsService).activity(TENANT, "2026-10-21", "2026-10-21");
    expect(a.latest.find((e) => e.plate === "uil")).toMatchObject({ via: { referrer: "google.com", page: "plaat", entry: "be" } });
    expect(a.latest.find((e) => e.plate === "kat")!.via).toBeNull();
    expect(JSON.stringify(a)).not.toContain(h);
  });

  it("laat zien wanneer er online gekleurd en getekend wordt, apart van downloads (ADR 0097)", async () => {
    expect((await ingest([
      ev("plate_colored", { plate: "slak", visitorHash: "ffffffffffffffff", occurredAt: "2026-10-22T18:30:00.000Z" }),
      ev("plate_completed", { plate: "slak", visitorHash: "ffffffffffffffff", occurredAt: "2026-10-22T18:50:00.000Z" }),
      ev("print", { plate: "uil", visitorHash: "ffffffffffffffff", occurredAt: "2026-10-22T19:00:00.000Z" }),
    ])).statusCode).toBe(202);
    const svc = ctx.app.get(AnalyticsService);
    const c = await svc.activity(TENANT, "2026-10-22", "2026-10-22", "colored");
    expect(c.latest.map((e) => e.type)).toEqual(["plate_completed", "plate_colored"]);
    expect(c.grid).toContainEqual({ weekday: 4, hour: 20, count: 2 });
    expect((await svc.activity(TENANT, "2026-10-22", "2026-10-22")).latest.map((e) => e.type)).toEqual(["print"]);
    expect((await admin("/v1/admin/analytics/activity?from=2026-10-22&to=2026-10-22&kind=colored")).statusCode).toBe(200);
    expect((await admin("/v1/admin/analytics/activity?from=2026-10-22&to=2026-10-22&kind=iets")).statusCode).toBe(400);
  });

  it("telt delen en binnenkomen via een gedeelde link, per plaat (ADR 0074)", async () => {
    const day = "2026-10-25", at = `${day}T12:00:00.000Z`;
    expect((await ingest([
      ev("share", { plate: "kat", org: "kleurhoek", visitorHash: "cccccccccccccccc", occurredAt: at }),
      ev("share", { plate: "kat", org: "kleurhoek", visitorHash: "cccccccccccccccc", occurredAt: at }),
      ev("shared_visit", { plate: "kat", org: "kleurhoek", visitorHash: "dddddddddddddddd", occurredAt: at }),
    ])).statusCode).toBe(202);
    await ctx.app.get(AnalyticsService).aggregateDay(TENANT, day);
    const o = (await admin(`/v1/admin/analytics/overview?from=${day}&to=${day}`)).json();
    expect(o.totals).toMatchObject({ shares: 2, sharedVisits: 1 });
    expect(o.topPlates.find((p: { plate: string }) => p.plate === "kat")).toMatchObject({ shares: 2, sharedVisits: 1 });
  });

  it("telt online gekleurd naast helemaal af, en vult oude dagen vanzelf aan (ADR 0077)", async () => {
    const day = "2026-10-26", at = `${day}T12:00:00.000Z`;
    const analytics = ctx.app.get(AnalyticsService);
    await ingest([ev("plate_view", { plate: "kat", org: "kleurhoek", visitorHash: "eeeeeeeeeeeeeeee", occurredAt: at })]);
    await analytics.aggregateDay(TENANT, day);
    expect(await analytics.staleDays(TENANT)).not.toContain(day);
    await ingest([
      ev("plate_colored", { plate: "kat", org: "kleurhoek", visitorHash: "eeeeeeeeeeeeeeee", occurredAt: at }),
      ev("plate_colored", { plate: "vis", org: "kleurhoek", visitorHash: "eeeeeeeeeeeeeeee", occurredAt: at }),
      ev("plate_completed", { plate: "vis", org: "kleurhoek", visitorHash: "eeeeeeeeeeeeeeee", occurredAt: at }),
    ]);
    await analytics.aggregateDay(TENANT, day);
    // Zoals een dag van vóór de kolom: wel kleurmeldingen, nog geen totaal. Die dag moet opnieuw.
    await withTenant(ctx.app.get<Database>(DB), TENANT, (tx) => tx.update(dailyTotals).set({ colored: 0 }).where(and(eq(dailyTotals.tenantId, TENANT), eq(dailyTotals.day, day))));
    expect(await analytics.staleDays(TENANT)).toContain(day);
    await analytics.aggregateDay(TENANT, day);
    expect(await analytics.staleDays(TENANT)).not.toContain(day);
    const o = (await admin(`/v1/admin/analytics/overview?from=${day}&to=${day}`)).json();
    expect(o.totals).toMatchObject({ colored: 2, completions: 1 });
    expect(o.topPlates.find((p: { plate: string }) => p.plate === "kat")).toMatchObject({ colored: 1, completions: 0 });
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

  it("toont wie er de laatste 30 minuten op de site was (ADR 0034)", async () => {
    const now = new Date(), at = (min: number) => new Date(now.getTime() - min * 60_000).toISOString();
    await ingest([
      ev("page_view", { page: "home", visitorHash: "ffffffffffffffff", occurredAt: at(5) }),
      ev("plate_view", { plate: "kat", visitorHash: "ffffffffffffffff", occurredAt: at(4) }),
      ev("page_view", { page: "home", visitorHash: "gggggggggggggggg", occurredAt: at(45) }), // te lang geleden
    ]);
    const r = (await admin("/v1/admin/analytics/realtime")).json();
    expect(r).toMatchObject({ visitors: 1, pageViews: 1, pages: [{ page: "home", views: 1 }], plates: [{ plate: "kat", views: 1 }] });
  });

  it("bewaart ruwe events, maar maakt de bezoekerscode na 90 dagen onherleidbaar (ADR 0078)", async () => {
    const svc = ctx.app.get(AnalyticsService);
    const db = ctx.app.get<Database>(DB);
    const d1 = "2026-06-01", d2 = "2026-06-02";
    await ingest([
      ev("page_view", { page: "home", visitorHash: "hhhhhhhhhhhhhhhh", occurredAt: `${d1}T08:00:00.000Z` }),
      ev("plate_view", { plate: "kat", visitorHash: "hhhhhhhhhhhhhhhh", occurredAt: `${d1}T08:05:00.000Z` }),
      ev("page_view", { page: "home", visitorHash: "iiiiiiiiiiiiiiii", occurredAt: `${d1}T09:00:00.000Z` }),
      ev("page_view", { page: "home", visitorHash: "hhhhhhhhhhhhhhhh", occurredAt: `${d2}T08:00:00.000Z` }),
    ]);
    await svc.aggregateDay(TENANT, d1);
    const before = (await admin(`/v1/admin/analytics/overview?from=${d1}&to=${d1}`)).json().totals;
    const hashes = (d: string) => withTenant(db, TENANT, (tx) => tx.select({ h: events.visitorHash }).from(events)
      .where(and(eq(events.tenantId, TENANT), sql`${events.occurredAt}::date = ${d}::date`)));

    // Nog geen 90 dagen oud: niets aan de hand.
    expect(await svc.anonymizeRawEvents(TENANT, new Date("2026-08-01T12:00:00Z"))).toBe(0);
    // Ruim daarna: beide dagen krijgen nieuwe codes, de events zelf blijven.
    expect(await svc.anonymizeRawEvents(TENANT, new Date("2027-06-01T12:00:00Z"))).toBeGreaterThanOrEqual(2);
    const h1 = (await hashes(d1)).map((r) => r.h!), h2 = (await hashes(d2)).map((r) => r.h!);
    expect(h1).toHaveLength(3);
    expect([...h1, ...h2].every((h) => h.startsWith("~") && !/hhhh|iiii/.test(h))).toBe(true);
    expect(new Set(h1).size).toBe(2); // binnen de dag blijft hetzelfde apparaat herkenbaar
    expect(h2[0]).not.toBe(h1[0]); // over dagen heen niet: elke dag een eigen, weggegooide sleutel
    // Een tweede keer verandert niets meer, en opnieuw tellen geeft dezelfde cijfers.
    expect(await svc.anonymizeRawEvents(TENANT, new Date("2027-06-02T12:00:00Z"))).toBe(0);
    await svc.aggregateDay(TENANT, d1);
    expect((await admin(`/v1/admin/analytics/overview?from=${d1}&to=${d1}`)).json().totals).toEqual(before);
    expect(before).toMatchObject({ visitors: 2, pageViews: 2, plateViews: 1 });
  });
});
