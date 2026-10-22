import { Inject, Injectable } from "@nestjs/common";
import { and, desc, eq, gte, lt, lte, sql } from "drizzle-orm";
import { z } from "zod";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { dailyProductClicks, dailyTotals, EVENT_TYPES, events } from "./analytics.schema";

/** Eén event zoals de Cloudflare Worker het aanlevert: zonder IP-adres, land al ingevuld. */
export const EventInput = z.object({
  type: z.enum(EVENT_TYPES),
  plate: z.string().regex(/^[a-z0-9-]{1,64}$/).optional(),
  product: z.string().regex(/^[a-z0-9-]{2,64}$/).optional(),
  market: z.string().regex(/^[a-z]{2}-[A-Z]{2}$/),
  country: z.string().regex(/^[A-Z]{2}$/).optional(),
  device: z.enum(["mobile", "tablet", "desktop", "other"]),
  visitorHash: z.string().regex(/^[A-Za-z0-9_-]{16,64}$/).optional(),
  occurredAt: z.iso.datetime().optional(),
}).strict();
export const EventBatch = z.array(EventInput).min(1).max(100);
export type EventInput = z.infer<typeof EventInput>;

@Injectable()
export class AnalyticsService {
  constructor(@Inject(DB) private readonly db: Database) {}

  async record(tenantId: string, batch: EventInput[], now = new Date()): Promise<number> {
    await withTenant(this.db, tenantId, (tx) => tx.insert(events).values(batch.map((e) => ({
      tenantId, type: e.type, plateSlug: e.plate ?? null, productSlug: e.product ?? null, market: e.market, country: e.country ?? null,
      device: e.device, visitorHash: e.visitorHash ?? null,
      occurredAt: e.occurredAt ? new Date(e.occurredAt) : now,
    }))));
    return batch.length;
  }

  /** Maakt de dagtotalen van één dag opnieuw uit de ruwe events. Idempotent; draait elk uur in een worker. */
  async aggregateDay(tenantId: string, day: string): Promise<void> {
    const start = new Date(`${day}T00:00:00Z`);
    const end = new Date(start.getTime() + 86_400_000);
    await withTenant(this.db, tenantId, async (tx) => {
      const count = (type: string) => sql<number>`count(*) filter (where ${events.type} = ${type})::int`;
      const rows = await tx.select({
        plate: sql<string>`coalesce(${events.plateSlug}, '')`, market: events.market, country: sql<string>`coalesce(${events.country}, '')`,
        pageViews: count("page_view"), plateViews: count("plate_view"), downloads: count("pdf_download"),
        prints: count("print"), completions: count("plate_completed"),
        materialsViews: count("materials_view"), productClicks: count("product_click"),
        uniqueVisitors: sql<number>`count(distinct ${events.visitorHash})::int`,
      }).from(events)
        .where(and(eq(events.tenantId, tenantId), gte(events.occurredAt, start), lt(events.occurredAt, end)))
        .groupBy(sql`1`, events.market, sql`3`);
      await tx.delete(dailyTotals).where(and(eq(dailyTotals.tenantId, tenantId), eq(dailyTotals.day, day)));
      if (rows.length) await tx.insert(dailyTotals).values(rows.map((r) => ({ tenantId, day, plateSlug: r.plate, market: r.market, country: r.country, pageViews: r.pageViews, plateViews: r.plateViews, downloads: r.downloads, prints: r.prints, completions: r.completions, materialsViews: r.materialsViews, productClicks: r.productClicks, uniqueVisitors: r.uniqueVisitors })));

      const clicks = await tx.select({
        product: sql<string>`${events.productSlug}`, plate: sql<string>`coalesce(${events.plateSlug}, '')`, market: events.market,
        country: sql<string>`coalesce(${events.country}, '')`,
        clicks: sql<number>`count(*)::int`, uniqueVisitors: sql<number>`count(distinct ${events.visitorHash})::int`,
      }).from(events)
        .where(and(eq(events.tenantId, tenantId), eq(events.type, "product_click"), sql`${events.productSlug} is not null`, gte(events.occurredAt, start), lt(events.occurredAt, end)))
        .groupBy(events.productSlug, sql`2`, events.market, sql`4`);
      await tx.delete(dailyProductClicks).where(and(eq(dailyProductClicks.tenantId, tenantId), eq(dailyProductClicks.day, day)));
      if (clicks.length) await tx.insert(dailyProductClicks).values(clicks.map((c) => ({ tenantId, day, productSlug: c.product, plateSlug: c.plate, market: c.market, country: c.country, clicks: c.clicks, uniqueVisitors: c.uniqueVisitors })));
    });
  }

  /** Voor het admin panel: top-platen en totalen per land in een periode. */
  summary(tenantId: string, from: string, to: string, country?: string) {
    const where = and(eq(dailyTotals.tenantId, tenantId), gte(dailyTotals.day, from), lte(dailyTotals.day, to), ...(country ? [eq(dailyTotals.country, country)] : []));
    return withTenant(this.db, tenantId, async (tx) => ({
      topPlates: await tx.select({
        plate: dailyTotals.plateSlug,
        views: sql<number>`sum(${dailyTotals.plateViews})::int`, downloads: sql<number>`sum(${dailyTotals.downloads})::int`,
        prints: sql<number>`sum(${dailyTotals.prints})::int`, completions: sql<number>`sum(${dailyTotals.completions})::int`,
      }).from(dailyTotals).where(and(where, sql`${dailyTotals.plateSlug} <> ''`))
        .groupBy(dailyTotals.plateSlug).orderBy(desc(sql`sum(${dailyTotals.downloads}) + sum(${dailyTotals.prints})`)).limit(20),
      byCountry: await tx.select({ country: dailyTotals.country, pageViews: sql<number>`sum(${dailyTotals.pageViews})::int`, plateViews: sql<number>`sum(${dailyTotals.plateViews})::int` })
        .from(dailyTotals).where(where).groupBy(dailyTotals.country).orderBy(desc(sql`sum(${dailyTotals.pageViews})`)),
    }));
  }

  /**
   * Winkelcijfers voor het admin panel: welke producten worden aangeklikt, vanaf welke platen, en
   * welke zijn kandidaat om zelf te gaan leveren (veel unieke bezoekers, groeiend).
   */
  async shopSummary(tenantId: string, from: string, to: string) {
    const days = Math.round((Date.parse(to) - Date.parse(from)) / 86_400_000) + 1;
    const prevTo = new Date(Date.parse(from) - 86_400_000).toISOString().slice(0, 10);
    const prevFrom = new Date(Date.parse(from) - days * 86_400_000).toISOString().slice(0, 10);
    return withTenant(this.db, tenantId, async (tx) => {
      const byProduct = (a: string, b: string) => tx.select({
        product: dailyProductClicks.productSlug,
        clicks: sql<number>`sum(${dailyProductClicks.clicks})::int`,
        visitors: sql<number>`sum(${dailyProductClicks.uniqueVisitors})::int`,
      }).from(dailyProductClicks).where(and(eq(dailyProductClicks.tenantId, tenantId), gte(dailyProductClicks.day, a), lte(dailyProductClicks.day, b)))
        .groupBy(dailyProductClicks.productSlug);
      const [current, previous] = [await byProduct(from, to), await byProduct(prevFrom, prevTo)];
      const sources = await tx.select({
        product: dailyProductClicks.productSlug, plate: dailyProductClicks.plateSlug, clicks: sql<number>`sum(${dailyProductClicks.clicks})::int`,
      }).from(dailyProductClicks).where(and(eq(dailyProductClicks.tenantId, tenantId), gte(dailyProductClicks.day, from), lte(dailyProductClicks.day, to)))
        .groupBy(dailyProductClicks.productSlug, dailyProductClicks.plateSlug).orderBy(desc(sql`sum(${dailyProductClicks.clicks})`));
      const plates = await tx.select({
        plate: dailyTotals.plateSlug,
        materialsViews: sql<number>`sum(${dailyTotals.materialsViews})::int`, productClicks: sql<number>`sum(${dailyTotals.productClicks})::int`,
      }).from(dailyTotals).where(and(eq(dailyTotals.tenantId, tenantId), gte(dailyTotals.day, from), lte(dailyTotals.day, to), sql`${dailyTotals.plateSlug} <> ''`))
        .groupBy(dailyTotals.plateSlug).having(sql`sum(${dailyTotals.materialsViews}) + sum(${dailyTotals.productClicks}) > 0`)
        .orderBy(desc(sql`sum(${dailyTotals.productClicks})`)).limit(20);

      const prev = new Map(previous.map((p) => [p.product, p]));
      const products = current.map((p) => {
        const before = prev.get(p.product);
        const growth = before && before.visitors > 0 ? (p.visitors - before.visitors) / before.visitors : null;
        return { ...p, previousVisitors: before?.visitors ?? 0, growth, topPlates: sources.filter((s) => s.product === p.product).slice(0, 3).map((s) => s.plate) };
      }).sort((a, b) => b.visitors - a.visitors || b.clicks - a.clicks);
      const totals = plates.reduce((t, p) => ({ materialsViews: t.materialsViews + p.materialsViews, productClicks: t.productClicks + p.productClicks }), { materialsViews: 0, productClicks: 0 });
      return {
        from, to, previous: { from: prevFrom, to: prevTo },
        totals: { ...totals, clickRate: totals.materialsViews ? totals.productClicks / totals.materialsViews : 0 },
        products,
        plates: plates.map((p) => ({ ...p, clickRate: p.materialsViews ? p.productClicks / p.materialsViews : 0 })),
        candidates: products.filter((p) => isCandidate(p)).slice(0, 10),
      };
    });
  }
}

/**
 * Kandidaat om zelf te leveren: genoeg unieke bezoekers om iets over te zeggen, en niet dalend.
 * Grove vuistregel; de drempel staat hier zodat hij later instelbaar kan worden.
 */
export const CANDIDATE_MIN_VISITORS = 20;
export function isCandidate(p: { visitors: number; growth: number | null }): boolean {
  return p.visitors >= CANDIDATE_MIN_VISITORS && (p.growth === null || p.growth >= 0);
}
