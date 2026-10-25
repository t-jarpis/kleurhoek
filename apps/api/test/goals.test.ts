import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { AggregationScheduler } from "../src/modules/analytics/aggregation.scheduler";
import { AnalyticsService } from "../src/modules/analytics/analytics.service";
import { addMonths, goalAt, GoalsService } from "../src/modules/analytics/goals.service";
import { createTestApp, INGEST_KEY, TENANT } from "./app";

describe("doelen (ADR 0022)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });
  const call = (method: "GET" | "PUT", auth: string, payload?: object) =>
    ctx.http.inject({ method, url: "/v1/admin/analytics/goals", headers: { authorization: `Bearer ${auth}` }, ...(payload ? { payload } : {}) });

  it("rekent tussen tussendoelen recht door en blijft daarna gelijk", () => {
    const ms = [{ month: 0, target: 0, stretch: 0 }, { month: 10, target: 1000, stretch: 2000 }];
    expect(goalAt(ms, 5)).toEqual({ target: 500, stretch: 1000 });
    expect(goalAt(ms, 14)).toEqual({ target: 1000, stretch: 2000 });
    expect(addMonths("2026-11", 2)).toBe("2027-01");
  });

  it("toont standaarddoelen met werkelijke bezoeken, platen en de stand van deze maand", async () => {
    const day = "2026-10-20";
    await ctx.http.inject({ method: "POST", url: "/v1/internal/events", headers: { "x-ingest-key": INGEST_KEY }, payload: [
      { type: "page_view", page: "home", market: "nl-NL", device: "mobile", visitorHash: "aaaaaaaaaaaaaaaa", occurredAt: `${day}T08:00:00.000Z` },
      { type: "page_view", page: "home", market: "nl-NL", device: "mobile", visitorHash: "bbbbbbbbbbbbbbbb", occurredAt: `${day}T09:00:00.000Z` },
    ] });
    await ctx.app.get(AnalyticsService).aggregateDay(TENANT, day);
    const g = await ctx.app.get(GoalsService).get(TENANT, new Date(`${day}T12:00:00Z`));
    expect(g.start).toBe("2026-10");
    const visits = g.metrics.find((m) => m.metric === "visits")!;
    expect(visits.months).toHaveLength(13);
    expect(visits.months[0]).toMatchObject({ month: "2026-10", target: 500, stretch: 1000, actual: 2 });
    expect(visits.months[12]).toMatchObject({ month: "2027-10", target: 10000, actual: null });
    expect(visits.now).toMatchObject({ actual: 2, target: 500, expected: Math.round(500 * 20 / 31), onTrack: false });
    const plates = g.metrics.find((m) => m.metric === "plates")!;
    expect(plates.now!.actual).toBeGreaterThan(0);
  });

  it("slaat eigen doelen op; alleen met het recht om doelen te wijzigen", async () => {
    const body = { start: "2026-11", metrics: {
      visits: [{ month: 0, target: 100, stretch: 200 }, { month: 12, target: 5000, stretch: 9000 }],
      plates: [{ month: 0, target: 66, stretch: 66 }, { month: 12, target: 200, stretch: 300 }],
      clicks: [{ month: 0, target: 5, stretch: 10 }, { month: 12, target: 50, stretch: 100 }],
    } };
    expect((await call("PUT", "analist", body)).statusCode).toBe(403);
    expect((await call("PUT", "beheerder", { ...body, metrics: { ...body.metrics, visits: [{ month: 0, target: 10, stretch: 5 }] } })).statusCode).toBe(400);
    const saved = await call("PUT", "beheerder", body);
    expect(saved.statusCode).toBe(200);
    expect(saved.json()).toMatchObject({ start: "2026-11", custom: true });
    const g = (await call("GET", "analist")).json();
    expect(g.metrics.find((m: { metric: string }) => m.metric === "visits").milestones).toEqual(body.metrics.visits);
  });
  it("haalt na een periode op nul alle dagen in die nog niet zijn opgeteld (ADR 0021)", async () => {
    const analytics = ctx.app.get(AnalyticsService);
    // Vijf dagen terug, maar nooit de vaste dag van de test hierboven (2026-10-20), anders telt die mee.
    let old = new Date(Date.now() - 5 * 86_400_000);
    if (old.toISOString().startsWith("2026-10-20")) old = new Date(old.getTime() - 86_400_000);
    const day = old.toISOString().slice(0, 10);
    await ctx.http.inject({ method: "POST", url: "/v1/internal/events", headers: { "x-ingest-key": INGEST_KEY }, payload: [
      { type: "page_view", page: "home", market: "nl-NL", device: "mobile", visitorHash: "cccccccccccccccc", occurredAt: old.toISOString() },
    ] });
    expect(await analytics.staleDays(TENANT)).toContain(day);
    await ctx.app.get(AggregationScheduler).run();
    expect(await analytics.staleDays(TENANT)).not.toContain(day);
    const o = (await ctx.http.inject({ method: "GET", url: `/v1/admin/analytics/overview?from=${day}&to=${day}`, headers: { authorization: "Bearer analist" } })).json();
    expect(o.totals.visitors).toBe(1);
  });
});
