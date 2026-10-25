import { Inject, Injectable, Logger, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { and, desc, eq, gte, lte, max, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { dailySources, searchStats, searchSync } from "./analytics.schema";
import { bingRows, googleRows, parseGoogleKey, type Engine, type Fetch, type SearchRow } from "./search-engines";

const DAY = 86_400_000;
const iso = (ms: number) => new Date(ms).toISOString().slice(0, 10);
/** Eerste keer: zoveel dagen terug (Google bewaart 16 maanden, Bing 6). Daarna de laatste dagen opnieuw. */
const BACKFILL_DAYS = 180;
const REFRESH_DAYS = 5;

/** Verwijzers die zoekmachines zijn, met een leesbare naam (eigen tellingen, ADR 0032). */
const SEARCH_REFERRERS: [RegExp, string][] = [
  [/(^|\.)google\.[a-z.]+$/, "Google"], [/(^|\.)bing\.com$/, "Bing"], [/(^|\.)duckduckgo\.com$/, "DuckDuckGo"],
  [/(^|\.)ecosia\.org$/, "Ecosia"], [/(^|\.)search\.yahoo\.com$|(^|\.)yahoo\.com$/, "Yahoo"], [/(^|\.)qwant\.com$/, "Qwant"],
  [/(^|\.)startpage\.com$/, "Startpage"], [/(^|\.)search\.brave\.com$/, "Brave"], [/(^|\.)yandex\.[a-z]+$/, "Yandex"],
];
export const searchEngineOf = (referrer: string) => SEARCH_REFERRERS.find(([re]) => re.test(referrer))?.[1] ?? null;

/**
 * Zoekcijfers (ADR 0041): haalt vertoningen, klikken en posities op bij Google en Bing en zet ze naast onze eigen
 * tellingen van bezoekers die via een zoekmachine binnenkwamen.
 */
@Injectable()
export class SearchService implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger(SearchService.name);
  private timer?: NodeJS.Timeout;
  fetch: Fetch = (url, init) => fetch(url, init);

  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env) {}

  onModuleInit() {
    if (!this.env.SEARCH_IMPORT_INTERVAL_MS || !this.env.SEARCH_DOMAINS.length || !this.engines().length) return;
    this.timer = setInterval(() => void this.run(), this.env.SEARCH_IMPORT_INTERVAL_MS);
    this.timer.unref();
    setTimeout(() => void this.run(), 30_000).unref();
  }

  onApplicationShutdown() { clearInterval(this.timer); }

  engines(): Engine[] {
    return [...(parseGoogleKey(this.env.GOOGLE_SEARCH_KEY) ? ["google" as const] : []), ...(this.env.BING_WEBMASTER_KEY ? ["bing" as const] : [])];
  }

  /** Alles ophalen wat nieuw is. Per zoekmachine en domein apart: een fout bij de één houdt de ander niet tegen. */
  async run(now = new Date()): Promise<void> {
    const tenantId = this.env.TENANT_ID;
    const google = parseGoogleKey(this.env.GOOGLE_SEARCH_KEY);
    for (const domain of this.env.SEARCH_DOMAINS) {
      for (const engine of this.engines()) {
        try {
          const last = await withTenant(this.db, tenantId, async (tx) => (await tx.select({ d: max(searchStats.day) }).from(searchStats)
            .where(and(eq(searchStats.tenantId, tenantId), eq(searchStats.engine, engine), eq(searchStats.site, domain))))[0]?.d ?? null);
          const from = last ? iso(Date.parse(last) - REFRESH_DAYS * DAY) : iso(now.getTime() - BACKFILL_DAYS * DAY);
          const to = iso(now.getTime() - DAY);
          const rows = engine === "google" ? await googleRows(google!, domain, from, to, this.fetch) : await bingRows(this.env.BING_WEBMASTER_KEY!, domain, from, this.fetch);
          await this.store(tenantId, engine, domain, from, rows);
          await this.status(tenantId, engine, domain, true, `${rows.length} rijen`, rows.reduce<string | null>((m, r) => (!m || r.day > m ? r.day : m), last));
        } catch (e) {
          const message = e instanceof Error ? e.message : String(e);
          this.log.warn(`Zoekcijfers ${engine} ${domain}: ${message}`);
          await this.status(tenantId, engine, domain, false, message.slice(0, 300), null).catch(() => undefined);
        }
      }
    }
  }

  /** Vervangt de cijfers vanaf `from`: zoekmachines stellen recente dagen nog bij. */
  private async store(tenantId: string, engine: Engine, site: string, from: string, rows: SearchRow[]) {
    await withTenant(this.db, tenantId, async (tx) => {
      await tx.delete(searchStats).where(and(eq(searchStats.tenantId, tenantId), eq(searchStats.engine, engine), eq(searchStats.site, site), gte(searchStats.day, from)));
      for (let i = 0; i < rows.length; i += 1000) {
        await tx.insert(searchStats).values(rows.slice(i, i + 1000).map((r) => ({ tenantId, ...r }))).onConflictDoNothing();
      }
    });
  }

  private async status(tenantId: string, engine: Engine, site: string, ok: boolean, message: string, lastDay: string | null) {
    await withTenant(this.db, tenantId, (tx) => tx.insert(searchSync).values({ tenantId, engine, site, ok, message, lastDay, runAt: new Date() })
      .onConflictDoUpdate({ target: [searchSync.tenantId, searchSync.engine, searchSync.site], set: { ok, message, ...(lastDay ? { lastDay } : {}), runAt: new Date(), updatedAt: new Date() } }));
  }

  /** Overzicht voor het admin panel: zoekmachines (vertoningen, klikken, positie) en eigen tellingen. */
  async report(from: string, to: string) {
    const tenantId = this.env.TENANT_ID;
    return withTenant(this.db, tenantId, async (tx) => {
      const inRange = (kind: "total" | "query" | "page") => and(eq(searchStats.tenantId, tenantId), eq(searchStats.kind, kind), gte(searchStats.day, from), lte(searchStats.day, to));
      const clicks = sql<number>`coalesce(sum(${searchStats.clicks}), 0)::int`;
      const impressions = sql<number>`coalesce(sum(${searchStats.impressions}), 0)::int`;
      const position = sql<number | null>`(sum(${searchStats.position} * ${searchStats.impressions}) / nullif(sum(case when ${searchStats.position} is null then 0 else ${searchStats.impressions} end), 0))::real`;
      const totals = await tx.select({ engine: searchStats.engine, clicks, impressions, position }).from(searchStats).where(inRange("total")).groupBy(searchStats.engine);
      const sites = await tx.select({ site: searchStats.site, engine: searchStats.engine, clicks, impressions, position }).from(searchStats).where(inRange("total")).groupBy(searchStats.site, searchStats.engine).orderBy(searchStats.site);
      const series = await tx.select({ day: searchStats.day, engine: searchStats.engine, clicks, impressions }).from(searchStats).where(inRange("total")).groupBy(searchStats.day, searchStats.engine).orderBy(searchStats.day);
      const queries = await tx.select({ key: searchStats.key, clicks, impressions, position }).from(searchStats).where(inRange("query")).groupBy(searchStats.key).orderBy(desc(clicks), desc(impressions)).limit(50);
      const pages = await tx.select({ key: searchStats.key, clicks, impressions, position }).from(searchStats).where(inRange("page")).groupBy(searchStats.key).orderBy(desc(clicks), desc(impressions)).limit(50);
      const sync = await tx.select({ engine: searchSync.engine, site: searchSync.site, ok: searchSync.ok, message: searchSync.message, lastDay: searchSync.lastDay, runAt: searchSync.runAt })
        .from(searchSync).where(eq(searchSync.tenantId, tenantId)).orderBy(searchSync.site, searchSync.engine);
      // Eigen tellingen: binnenkomsten met een zoekmachine als verwijzer, per zoekmachine en per domein.
      const refs = await tx.select({ referrer: dailySources.referrer, entry: dailySources.entryDomain, landings: sql<number>`sum(${dailySources.landings})::int`, visitors: sql<number>`sum(${dailySources.visitors})::int` })
        .from(dailySources).where(and(eq(dailySources.tenantId, tenantId), gte(dailySources.day, from), lte(dailySources.day, to), sql`${dailySources.referrer} <> ''`))
        .groupBy(dailySources.referrer, dailySources.entryDomain);
      const own = new Map<string, { engine: string; landings: number; visitors: number }>();
      const ownByDomain = new Map<string, number>();
      for (const r of refs) {
        const engine = searchEngineOf(r.referrer);
        if (!engine) continue;
        const cur = own.get(engine) ?? { engine, landings: 0, visitors: 0 };
        cur.landings += r.landings; cur.visitors += r.visitors;
        own.set(engine, cur);
        ownByDomain.set(r.entry, (ownByDomain.get(r.entry) ?? 0) + r.landings);
      }
      return {
        from, to,
        configured: { domains: this.env.SEARCH_DOMAINS, engines: this.engines() },
        totals, sites, series, queries, pages, sync,
        own: [...own.values()].sort((a, b) => b.landings - a.landings),
        ownByDomain: [...ownByDomain].map(([entry, landings]) => ({ entry, landings })).sort((a, b) => b.landings - a.landings),
      };
    });
  }
}

