import { Inject, Injectable } from "@nestjs/common";
import { and, desc, eq, gte, lt, lte, sql } from "drizzle-orm";
import { z } from "zod";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { dailyPages, dailyProductClicks, dailySources, dailyTotals, dailyVisitors, EVENT_TYPES, events } from "./analytics.schema";

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
  /** Soort pagina (home, plaat, boekje …), nooit een adres of zoekterm (ADR 0020). */
  page: z.string().regex(/^[a-z][a-z0-9-]{1,31}$/).optional(),
  org: z.string().regex(/^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/).optional(),
  /** Binnenkomst (ADR 0032): domein en hostnaam van de verwijzer, nooit een pad of zoekterm. */
  entry: z.enum(["nl", "be", "com"]).optional(),
  referrer: z.string().max(100).regex(/^$|^([a-z0-9-]{1,63}\.)+[a-z]{2,24}$/).optional(),
}).strict();
export const EventBatch = z.array(EventInput).min(1).max(100);
export type EventInput = z.infer<typeof EventInput>;

@Injectable()
export class AnalyticsService {
  constructor(@Inject(DB) private readonly db: Database) {}

  async record(tenantId: string, batch: EventInput[], now = new Date()): Promise<number> {
    await withTenant(this.db, tenantId, (tx) => tx.insert(events).values(batch.map((e) => ({
      tenantId, type: e.type, plateSlug: e.plate ?? null, productSlug: e.product ?? null, market: e.market, country: e.country ?? null,
      device: e.device, visitorHash: e.visitorHash ?? null, page: e.page ?? null, org: e.org ?? null,
      entryDomain: e.entry ?? null, referrer: e.entry ? (e.referrer ?? "") : null,
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

      // Pagina's (ADR 0020): weergaven en bezoekers per soort pagina, organisatie, markt en apparaat.
      const inDay = and(eq(events.tenantId, tenantId), gte(events.occurredAt, start), lt(events.occurredAt, end));
      const org = sql<string>`coalesce(${events.org}, '${sql.raw(DEFAULT_ORG)}')`;
      const pages = await tx.select({
        org, page: sql<string>`coalesce(${events.page}, 'home')`, market: events.market, device: events.device,
        views: sql<number>`count(*)::int`, visitors: sql<number>`count(distinct ${events.visitorHash})::int`,
      }).from(events).where(and(inDay, eq(events.type, "page_view"))).groupBy(sql`1`, sql`2`, events.market, events.device);
      await tx.delete(dailyPages).where(and(eq(dailyPages.tenantId, tenantId), eq(dailyPages.day, day)));
      if (pages.length) await tx.insert(dailyPages).values(pages.map((r) => ({ tenantId, day, ...r })));

      // Binnenkomsten (ADR 0032): per domein en verwijzende site.
      const landings = await tx.select({
        org, entryDomain: sql<string>`${events.entryDomain}`, referrer: sql<string>`coalesce(${events.referrer}, '')`,
        landings: sql<number>`count(*)::int`, visitors: sql<number>`count(distinct ${events.visitorHash})::int`,
      }).from(events).where(and(inDay, eq(events.type, "page_view"), sql`${events.entryDomain} is not null`)).groupBy(sql`1`, sql`2`, sql`3`);
      await tx.delete(dailySources).where(and(eq(dailySources.tenantId, tenantId), eq(dailySources.day, day)));
      if (landings.length) await tx.insert(dailySources).values(landings.map((r) => ({ tenantId, day, ...r })));

      // Unieke bezoekers per organisatie en voor de hele site ('*'), over alle soorten events.
      const perOrg = await tx.select({ org, visitors: sql<number>`count(distinct ${events.visitorHash})::int` })
        .from(events).where(inDay).groupBy(sql`1`);
      const [all] = await tx.select({ visitors: sql<number>`count(distinct ${events.visitorHash})::int` }).from(events).where(inDay);
      await tx.delete(dailyVisitors).where(and(eq(dailyVisitors.tenantId, tenantId), eq(dailyVisitors.day, day)));
      const visitorRows = [...perOrg, ...(all && all.visitors ? [{ org: ALL_ORGS, visitors: all.visitors }] : [])].filter((r) => r.visitors > 0);
      if (visitorRows.length) await tx.insert(dailyVisitors).values(visitorRows.map((r) => ({ tenantId, day, ...r })));
    });
  }

  /**
   * Dagen waarvan de dagtotalen achterlopen: er kwamen events bij na de laatste keer optellen, of er is
   * nog niet opgeteld. Nodig omdat de API naar nul schaalt: na een stille periode wordt alles ingehaald.
   */
  async staleDays(tenantId: string): Promise<string[]> {
    return withTenant(this.db, tenantId, async (tx) => {
      const day = sql<string>`to_char(${events.occurredAt} at time zone 'UTC', 'YYYY-MM-DD')`;
      const raw = await tx.select({ day, last: sql<Date>`max(${events.createdAt})` }).from(events).where(eq(events.tenantId, tenantId)).groupBy(sql`1`);
      if (!raw.length) return [];
      const done = new Map((await tx.select({ day: sql<string>`${dailyTotals.day}::text`, at: sql<Date>`max(${dailyTotals.createdAt})` })
        .from(dailyTotals).where(and(eq(dailyTotals.tenantId, tenantId), gte(dailyTotals.day, raw.reduce((m, r) => (r.day < m ? r.day : m), raw[0]!.day))))
        .groupBy(dailyTotals.day)).map((r) => [r.day, new Date(r.at).getTime()]));
      return raw.filter((r) => !done.has(r.day) || new Date(r.last).getTime() >= done.get(r.day)!).map((r) => r.day).sort();
    });
  }

  /** Ruwe events na 90 dagen weg; daarna bestaan alleen de dagtotalen nog (ADR 0002). */
  async purgeRawEvents(tenantId: string, now = new Date()): Promise<void> {
    const cutoff = new Date(now.getTime() - RAW_EVENT_DAYS * 86_400_000);
    await withTenant(this.db, tenantId, (tx) => tx.delete(events).where(and(eq(events.tenantId, tenantId), lt(events.occurredAt, cutoff))));
  }

  /**
   * Overzicht voor het dashboard (ADR 0020): reeksen per dag (tot 92 dagen) of per week, totalen met
   * de vorige periode van gelijke lengte, en verdelingen over pagina's, platen, apparaten, landen en
   * organisaties. Bezoekers zijn per dag uniek; over meerdere dagen is het een som ("bezoeken per dag").
   */
  async overview(tenantId: string, from: string, to: string) {
    const days = Math.round((Date.parse(to) - Date.parse(from)) / 86_400_000) + 1;
    const prevTo = shiftDay(from, -1), prevFrom = shiftDay(from, -days);
    const bucket = days > 92 ? "week" : "day";
    const { topPlates, byCountry } = await this.summary(tenantId, from, to);
    const b = (col: unknown) => (bucket === "week" ? sql<string>`to_char(date_trunc('week', ${col}::date), 'YYYY-MM-DD')` : sql<string>`to_char(${col}::date, 'YYYY-MM-DD')`);
    return withTenant(this.db, tenantId, async (tx) => {
      const range = (a: string, z: string) => and(eq(dailyTotals.tenantId, tenantId), gte(dailyTotals.day, a), lte(dailyTotals.day, z));
      const totals = (a: string, z: string) => tx.select({
        pageViews: sql<number>`coalesce(sum(${dailyTotals.pageViews}), 0)::int`, plateViews: sql<number>`coalesce(sum(${dailyTotals.plateViews}), 0)::int`,
        downloads: sql<number>`coalesce(sum(${dailyTotals.downloads} + ${dailyTotals.prints}), 0)::int`, completions: sql<number>`coalesce(sum(${dailyTotals.completions}), 0)::int`,
      }).from(dailyTotals).where(range(a, z)).then((r) => r[0]!);
      const visitors = (a: string, z: string) => tx.select({ visitors: sql<number>`coalesce(sum(${dailyVisitors.visitors}), 0)::int` })
        .from(dailyVisitors).where(and(eq(dailyVisitors.tenantId, tenantId), eq(dailyVisitors.org, ALL_ORGS), gte(dailyVisitors.day, a), lte(dailyVisitors.day, z))).then((r) => r[0]!.visitors);
      const pagesIn = and(eq(dailyPages.tenantId, tenantId), gte(dailyPages.day, from), lte(dailyPages.day, to));

      const [current, previous, visitorsNow, visitorsBefore] = [await totals(from, to), await totals(prevFrom, prevTo), await visitors(from, to), await visitors(prevFrom, prevTo)];
      const seriesTotals = await tx.select({
        date: b(dailyTotals.day), pageViews: sql<number>`sum(${dailyTotals.pageViews})::int`, plateViews: sql<number>`sum(${dailyTotals.plateViews})::int`,
        downloads: sql<number>`sum(${dailyTotals.downloads} + ${dailyTotals.prints})::int`,
      }).from(dailyTotals).where(range(from, to)).groupBy(sql`1`);
      const seriesVisitors = await tx.select({ date: b(dailyVisitors.day), visitors: sql<number>`sum(${dailyVisitors.visitors})::int` })
        .from(dailyVisitors).where(and(eq(dailyVisitors.tenantId, tenantId), eq(dailyVisitors.org, ALL_ORGS), gte(dailyVisitors.day, from), lte(dailyVisitors.day, to))).groupBy(sql`1`);
      const byDate = new Map(seriesTotals.map((r) => [r.date, r]));
      const vByDate = new Map(seriesVisitors.map((r) => [r.date, r.visitors]));
      const series = buckets(from, to, bucket).map((date) => ({
        date, visitors: vByDate.get(date) ?? 0, pageViews: byDate.get(date)?.pageViews ?? 0,
        plateViews: byDate.get(date)?.plateViews ?? 0, downloads: byDate.get(date)?.downloads ?? 0,
      }));

      const sum = (col: typeof dailyPages.views | typeof dailyPages.visitors) => sql<number>`sum(${col})::int`;
      const pages = await tx.select({ page: dailyPages.page, views: sum(dailyPages.views), visitors: sum(dailyPages.visitors) })
        .from(dailyPages).where(pagesIn).groupBy(dailyPages.page).orderBy(desc(sum(dailyPages.views)));
      const devices = await tx.select({ device: dailyPages.device, views: sum(dailyPages.views) })
        .from(dailyPages).where(pagesIn).groupBy(dailyPages.device).orderBy(desc(sum(dailyPages.views)));
      const orgViews = await tx.select({ org: dailyPages.org, views: sum(dailyPages.views) }).from(dailyPages).where(pagesIn).groupBy(dailyPages.org);
      const orgVisitors = await tx.select({ org: dailyVisitors.org, visitors: sql<number>`sum(${dailyVisitors.visitors})::int` })
        .from(dailyVisitors).where(and(eq(dailyVisitors.tenantId, tenantId), gte(dailyVisitors.day, from), lte(dailyVisitors.day, to), sql`${dailyVisitors.org} <> ${ALL_ORGS}`)).groupBy(dailyVisitors.org);
      // Binnenkomsten (ADR 0032): per domein en per verwijzende site (top 15, de rest samen).
      const sourcesIn = and(eq(dailySources.tenantId, tenantId), gte(dailySources.day, from), lte(dailySources.day, to));
      const sumL = sql<number>`sum(${dailySources.landings})::int`;
      const entries = await tx.select({ entry: dailySources.entryDomain, landings: sumL, visitors: sql<number>`sum(${dailySources.visitors})::int` })
        .from(dailySources).where(sourcesIn).groupBy(dailySources.entryDomain).orderBy(desc(sumL));
      const refs = await tx.select({ referrer: dailySources.referrer, landings: sumL })
        .from(dailySources).where(sourcesIn).groupBy(dailySources.referrer).orderBy(desc(sumL));
      const referrers = [...refs.slice(0, 15), ...(refs.length > 15 ? [{ referrer: "*", landings: refs.slice(15).reduce((n, r) => n + r.landings, 0) }] : [])];
      const ov = new Map(orgViews.map((o) => [o.org, o.views]));
      const organizations = orgVisitors.map((o) => ({ org: o.org, visitors: o.visitors, views: ov.get(o.org) ?? 0 })).sort((x, y) => y.visitors - x.visitors);
      return {
        from, to, bucket, previous: { from: prevFrom, to: prevTo },
        totals: { visitors: visitorsNow, ...current }, previousTotals: { visitors: visitorsBefore, ...previous },
        series, pages, devices, organizations, entries, referrers, topPlates: topPlates.slice(0, 10), countries: byCountry.slice(0, 10),
      };
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

export const RAW_EVENT_DAYS = 90;
export const DEFAULT_ORG = "kleurhoek";
/** Rij met de unieke bezoekers van de hele site (alle organisaties samen). */
export const ALL_ORGS = "*";

export const shiftDay = (day: string, n: number) => new Date(Date.parse(`${day}T00:00:00Z`) + n * 86_400_000).toISOString().slice(0, 10);

/** Alle dagen of weken (maandag) in de periode, ook zonder data, zodat een grafiek geen gaten overslaat. */
export function buckets(from: string, to: string, bucket: "day" | "week"): string[] {
  const out: string[] = [];
  let d = from;
  if (bucket === "week") { const wd = (new Date(`${from}T00:00:00Z`).getUTCDay() + 6) % 7; d = shiftDay(from, -wd); }
  for (; d <= to; d = shiftDay(d, bucket === "week" ? 7 : 1)) out.push(d);
  return out;
}

/**
 * Kandidaat om zelf te leveren: genoeg unieke bezoekers om iets over te zeggen, en niet dalend.
 * Grove vuistregel; de drempel staat hier zodat hij later instelbaar kan worden.
 */
export const CANDIDATE_MIN_VISITORS = 20;
export function isCandidate(p: { visitors: number; growth: number | null }): boolean {
  return p.visitors >= CANDIDATE_MIN_VISITORS && (p.growth === null || p.growth >= 0);
}
