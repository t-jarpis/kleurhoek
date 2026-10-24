import { Inject, Injectable } from "@nestjs/common";
import { and, eq, gte, lte, sql } from "drizzle-orm";
import { z } from "zod";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { CatalogService } from "../catalog/catalog.service";
import { AuditService } from "../identity/audit.service";
import { dailyProductClicks, dailyVisitors, goals, type GoalMilestone } from "./analytics.schema";
import { ALL_ORGS } from "./analytics.service";

export const GOAL_METRICS = ["visits", "plates", "clicks"] as const;
export type GoalMetric = (typeof GOAL_METRICS)[number];

/**
 * Startwaarden (ADR 0022), op basis van vergelijkbare Nederlandse kleurplatensites: na een jaar 10.000
 * bezoeken per maand als doel en 30.000 als ambitie; 300 tot 500 platen; 100 doorkliks per maand is
 * ongeveer 10 verkopen (de drempel voor productfoto's van Amazon).
 */
export const DEFAULT_GOALS: Record<GoalMetric, GoalMilestone[]> = {
  visits: [{ month: 0, target: 500, stretch: 1000 }, { month: 3, target: 1200, stretch: 2500 }, { month: 6, target: 3000, stretch: 6000 }, { month: 12, target: 10000, stretch: 30000 }],
  plates: [{ month: 0, target: 66, stretch: 66 }, { month: 6, target: 180, stretch: 250 }, { month: 12, target: 300, stretch: 500 }],
  clicks: [{ month: 0, target: 10, stretch: 20 }, { month: 6, target: 40, stretch: 100 }, { month: 12, target: 100, stretch: 300 }],
};

const Month = z.string().regex(/^\d{4}-(0[1-9]|1[0-2])$/);
const Milestones = z.array(z.object({
  month: z.number().int().min(0).max(60),
  target: z.number().int().min(0).max(100_000_000),
  stretch: z.number().int().min(0).max(100_000_000),
}).strict()).min(1).max(12)
  .refine((m) => new Set(m.map((x) => x.month)).size === m.length, "Elke maand maar één keer")
  .refine((m) => m.every((x) => x.stretch >= x.target), "De ambitie is minstens het doel");
export const GoalsInput = z.object({ start: Month, metrics: z.object({ visits: Milestones, plates: Milestones, clicks: Milestones }).strict() }).strict();
export type GoalsInput = z.infer<typeof GoalsInput>;

/** YYYY-MM plus n maanden. */
export function addMonths(month: string, n: number): string {
  const [y, m] = month.split("-").map(Number) as [number, number];
  const t = y * 12 + (m - 1) + n;
  return `${Math.floor(t / 12)}-${String((t % 12) + 1).padStart(2, "0")}`;
}
export function monthsBetween(a: string, b: string): number {
  const [ya, ma] = a.split("-").map(Number) as [number, number];
  const [yb, mb] = b.split("-").map(Number) as [number, number];
  return (yb * 12 + mb) - (ya * 12 + ma);
}
function lastDay(month: string): string {
  const [y, m] = month.split("-").map(Number) as [number, number];
  return `${month}-${String(new Date(Date.UTC(y, m, 0)).getUTCDate()).padStart(2, "0")}`;
}

/** Doel en ambitie voor maand i na de start: recht tussen de tussendoelen, daarna gelijk. */
export function goalAt(milestones: GoalMilestone[], i: number): { target: number; stretch: number } {
  const ms = [...milestones].sort((a, b) => a.month - b.month);
  const first = ms[0]!, last = ms.at(-1)!;
  if (i <= first.month) return { target: first.target, stretch: first.stretch };
  if (i >= last.month) return { target: last.target, stretch: last.stretch };
  const k = ms.findIndex((m) => m.month >= i);
  const a = ms[k - 1]!, b = ms[k]!, f = (i - a.month) / (b.month - a.month);
  return { target: Math.round(a.target + (b.target - a.target) * f), stretch: Math.round(a.stretch + (b.stretch - a.stretch) * f) };
}

@Injectable()
export class GoalsService {
  constructor(@Inject(DB) private readonly db: Database, private readonly catalog: CatalogService, private readonly audit: AuditService) {}

  async get(tenantId: string, today = new Date()) {
    const current = today.toISOString().slice(0, 7);
    const day = today.getUTCDate(), daysInMonth = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth() + 1, 0)).getUTCDate();
    const { rows, firstDay } = await withTenant(this.db, tenantId, async (tx) => ({
      rows: await tx.select().from(goals).where(eq(goals.tenantId, tenantId)),
      firstDay: (await tx.select({ d: sql<string | null>`min(${dailyVisitors.day})::text` }).from(dailyVisitors)
        .where(and(eq(dailyVisitors.tenantId, tenantId), eq(dailyVisitors.org, ALL_ORGS))))[0]?.d ?? null,
    }));
    const saved = new Map(rows.map((r) => [r.metric, r]));
    // Zonder opgeslagen doelen: start in de eerste maand met bezoekers (of nu).
    const start = rows[0]?.startMonth ?? firstDay?.slice(0, 7) ?? current;
    const count = Math.max(13, monthsBetween(start, current) + 1);
    const months = Array.from({ length: count }, (_, i) => addMonths(start, i));
    const from = `${start}-01`, to = lastDay(months.at(-1)!);

    const [visits, clicks, published] = await Promise.all([
      withTenant(this.db, tenantId, (tx) => tx.select({ m: sql<string>`to_char(${dailyVisitors.day}, 'YYYY-MM')`, n: sql<number>`sum(${dailyVisitors.visitors})::int` })
        .from(dailyVisitors).where(and(eq(dailyVisitors.tenantId, tenantId), eq(dailyVisitors.org, ALL_ORGS), gte(dailyVisitors.day, from), lte(dailyVisitors.day, to))).groupBy(sql`1`)),
      withTenant(this.db, tenantId, (tx) => tx.select({ m: sql<string>`to_char(${dailyProductClicks.day}, 'YYYY-MM')`, n: sql<number>`sum(${dailyProductClicks.clicks})::int` })
        .from(dailyProductClicks).where(and(eq(dailyProductClicks.tenantId, tenantId), gte(dailyProductClicks.day, from), lte(dailyProductClicks.day, to))).groupBy(sql`1`)),
      this.catalog.publishedDates(tenantId),
    ]);
    const byMonth = (r: { m: string; n: number }[]) => new Map(r.map((x) => [x.m, x.n]));
    const actual: Record<GoalMetric, (month: string) => number> = {
      visits: ((m) => (k: string) => m.get(k) ?? 0)(byMonth(visits)),
      clicks: ((m) => (k: string) => m.get(k) ?? 0)(byMonth(clicks)),
      plates: (k) => published.filter((d) => d.toISOString().slice(0, 7) <= k).length,
    };

    return {
      start, current, custom: rows.length > 0,
      metrics: GOAL_METRICS.map((metric) => {
        const milestones = saved.get(metric)?.milestones ?? DEFAULT_GOALS[metric];
        const series = months.map((month, i) => ({ month, ...goalAt(milestones, i), actual: month > current ? null : actual[metric](month) }));
        const now = series.find((s) => s.month === current);
        // Per maand opgeteld (bezoeken, doorkliks): deze maand naar rato vergelijken. Platen: stand nu.
        const share = metric === "plates" ? 1 : day / daysInMonth;
        const expected = now ? Math.round(now.target * share) : 0;
        return { metric, milestones, months: series, now: now ? { actual: now.actual ?? 0, target: now.target, stretch: now.stretch, expected, onTrack: (now.actual ?? 0) >= expected } : null };
      }),
    };
  }

  async save(tenantId: string, actor: string, input: GoalsInput): Promise<void> {
    await withTenant(this.db, tenantId, async (tx) => {
      const before = await tx.select({ metric: goals.metric, startMonth: goals.startMonth, milestones: goals.milestones }).from(goals).where(eq(goals.tenantId, tenantId));
      for (const metric of GOAL_METRICS) {
        const values = { startMonth: input.start, milestones: input.metrics[metric] };
        await tx.insert(goals).values({ tenantId, metric, ...values })
          .onConflictDoUpdate({ target: [goals.tenantId, goals.metric], set: { ...values, updatedAt: new Date() } });
      }
      await this.audit.record(tx, tenantId, { actor, action: "analytics.goals.updated", subject: "goals", before: before.length ? before : null, after: input });
    });
  }
}
