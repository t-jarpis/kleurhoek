import { Inject, Injectable } from "@nestjs/common";
import { and, desc, eq, gte, lt, lte, sql } from "drizzle-orm";
import { z } from "zod";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { dailyTotals, EVENT_TYPES, events } from "./analytics.schema";

/** Eén event zoals de Cloudflare Worker het aanlevert: zonder IP-adres, land al ingevuld. */
export const EventInput = z.object({
  type: z.enum(EVENT_TYPES),
  plate: z.string().regex(/^[a-z0-9-]{1,64}$/).optional(),
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
      tenantId, type: e.type, plateSlug: e.plate ?? null, market: e.market, country: e.country ?? null,
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
        uniqueVisitors: sql<number>`count(distinct ${events.visitorHash})::int`,
      }).from(events)
        .where(and(eq(events.tenantId, tenantId), gte(events.occurredAt, start), lt(events.occurredAt, end)))
        .groupBy(sql`1`, events.market, sql`3`);
      await tx.delete(dailyTotals).where(and(eq(dailyTotals.tenantId, tenantId), eq(dailyTotals.day, day)));
      if (rows.length) await tx.insert(dailyTotals).values(rows.map((r) => ({ tenantId, day, plateSlug: r.plate, market: r.market, country: r.country, pageViews: r.pageViews, plateViews: r.plateViews, downloads: r.downloads, prints: r.prints, completions: r.completions, uniqueVisitors: r.uniqueVisitors })));
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
}
