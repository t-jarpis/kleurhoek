import { Inject, Injectable, Logger, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { and, asc, eq, gte, lt, sql } from "drizzle-orm";
import { ENV, type CapacityApp, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { capacityDaily, speedSamples } from "./operations.schema";

/**
 * Prijzen van Scaleway Serverless Containers (excl. btw, november 2026, scaleway.com/en/pricing/serverless):
 * € 1,00 per 100.000 vCPU-seconden en € 0,10 per 100.000 GB-seconden. Alleen voor een schatting van het vaste deel.
 */
export const PRICE_PER_VCPU_SECOND = 0.00001;
export const PRICE_PER_GB_SECOND = 0.000002;
const MONTH_SECONDS = 30 * 86_400;
/** Hoe lang snelheidsmetingen bewaard blijven. */
const SPEED_DAYS = 35;

export type Advice = "omlaag" | "goed" | "omhoog" | "onbekend";
export interface DayRow { day: string; cpuAvg: number | null; cpuP95: number | null; memAvg: number | null; memP95: number | null; instancesMax: number | null }

/** Percentiel (0–100) van een lijst getallen; null bij een lege lijst. */
export function percentile(values: number[], p: number): number | null {
  if (!values.length) return null;
  const s = [...values].sort((a, b) => a - b);
  const i = Math.min(s.length - 1, Math.max(0, Math.ceil((p / 100) * s.length) - 1));
  return s[i]!;
}

/** Wat een container minstens per maand kost als hij altijd `min` keer draait (zonder gratis tegoed). */
export function monthlyBase(a: CapacityApp): number {
  const one = (a.cpu / 1000) * MONTH_SECONDS * PRICE_PER_VCPU_SECOND + (a.memory / 1024) * MONTH_SECONDS * PRICE_PER_GB_SECOND;
  return Math.round(one * a.min * 100) / 100;
}

/**
 * Advies over de maat van een container op basis van de laatste zeven dagen (ADR 0092). Omhoog gaat voor:
 * liever een paar euro meer dan een trage site.
 */
export function advise(a: CapacityApp, days: DayRow[], speedP95: number | null): { advice: Advice; reason: string } {
  const known = days.filter((d) => d.cpuP95 !== null || d.memP95 !== null);
  if (known.length < 3) return { advice: "onbekend", reason: "Nog te weinig cijfers. Na drie dagen metingen volgt een advies." };
  const max = (k: "cpuP95" | "memP95" | "instancesMax") => Math.max(0, ...known.map((d) => d[k] ?? 0));
  const cpu = max("cpuP95"), mem = max("memP95"), inst = max("instancesMax");
  if (mem > 80) return { advice: "omhoog", reason: `Geheugen kwam tot ${Math.round(mem)}% van de grens. Meer geheugen voorkomt herstarts.` };
  if (cpu > 80) return { advice: "omhoog", reason: `De processor zat op drukke momenten op ${Math.round(cpu)}%. Meer rekenkracht houdt de site snel.` };
  if (a.max > 1 && inst >= a.max) return { advice: "omhoog", reason: `Er draaiden ${inst} exemplaren, het maximum. Een hoger maximum vangt pieken op.` };
  if (speedP95 !== null && speedP95 > 1500) return { advice: "goed", reason: `De site is trager dan gewenst (${speedP95} ms). Eerst kijken naar caching, niet kleiner maken.` };
  if (known.length >= 7 && cpu < 30 && mem < 50 && inst <= Math.max(1, a.min)) {
    return { advice: "omlaag", reason: `Een week lang hoogstens ${Math.round(cpu)}% processor en ${Math.round(mem)}% geheugen. Een kleinere maat is waarschijnlijk genoeg.` };
  }
  return { advice: "goed", reason: `Processor tot ${Math.round(cpu)}%, geheugen tot ${Math.round(mem)}%. De maat past.` };
}

interface PromSeries { values: [number, string][] }

/** Capaciteit van de servers (ADR 0092): cijfers uit Scaleway Cockpit en eigen snelheidsmetingen, met een advies. */
@Injectable()
export class CapacityService implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger(CapacityService.name);
  private timer?: NodeJS.Timeout;
  /** Vervangbaar in tests. */
  fetch: typeof fetch = (...args) => fetch(...args);

  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env) {}

  onModuleInit() {
    if (this.env.CAPACITY_INTERVAL_MS === 0) return;
    this.timer = setInterval(() => void this.tick(), this.env.CAPACITY_INTERVAL_MS);
    this.timer.unref();
    setTimeout(() => void this.tick(), 30_000).unref();
  }

  onApplicationShutdown() { clearInterval(this.timer); }

  metricsConfigured() { return Boolean(this.env.COCKPIT_METRICS_URL && this.env.COCKPIT_METRICS_TOKEN && this.env.CAPACITY_APPS.length); }

  /** Eén ronde: snelheid meten en de cijfers van vandaag en gisteren bijwerken. */
  async tick(now = new Date()) {
    try {
      await this.measureSpeed(now);
      if (this.metricsConfigured()) {
        const today = now.toISOString().slice(0, 10);
        const yesterday = new Date(now.getTime() - 86_400_000).toISOString().slice(0, 10);
        await this.importDay(yesterday);
        await this.importDay(today);
      }
    } catch (e) { this.log.error(`Capaciteit bijwerken mislukt: ${e}`); }
  }

  /** Meet hoe snel de site het eerste antwoord geeft, zoals een bezoeker het ziet (met de cache van Cloudflare). */
  async measureSpeed(now = new Date()) {
    const base = this.env.SITE_URL.replace(/\/$/, "");
    const rows: (typeof speedSamples.$inferInsert)[] = [];
    for (const path of this.env.CAPACITY_SPEED_PATHS) {
      const start = performance.now();
      let status = 0;
      try {
        const res = await this.fetch(base + path, { redirect: "manual", signal: AbortSignal.timeout(15_000), headers: { "user-agent": "Kleurhoek-capaciteit/1 (+snelheidsmeting)" } });
        status = res.status;
        await res.body?.cancel();
      } catch { status = 0; }
      rows.push({ tenantId: this.env.TENANT_ID, at: now, path, ms: Math.round(performance.now() - start), status });
    }
    const cutoff = new Date(now.getTime() - SPEED_DAYS * 86_400_000);
    await withTenant(this.db, this.env.TENANT_ID, async (tx) => {
      if (rows.length) await tx.insert(speedSamples).values(rows);
      await tx.delete(speedSamples).where(and(eq(speedSamples.tenantId, this.env.TENANT_ID), lt(speedSamples.at, cutoff)));
    });
  }

  private async range(query: string, start: Date, end: Date): Promise<PromSeries[]> {
    const url = new URL(`${this.env.COCKPIT_METRICS_URL!.replace(/\/$/, "")}/prometheus/api/v1/query_range`);
    url.searchParams.set("query", query);
    url.searchParams.set("start", String(Math.floor(start.getTime() / 1000)));
    url.searchParams.set("end", String(Math.floor(end.getTime() / 1000)));
    url.searchParams.set("step", "300");
    const res = await this.fetch(url, { headers: { authorization: `Bearer ${this.env.COCKPIT_METRICS_TOKEN}` }, signal: AbortSignal.timeout(20_000) });
    if (!res.ok) throw new Error(`Cockpit gaf ${res.status}`);
    const body = await res.json() as { status: string; data?: { result?: PromSeries[] } };
    if (body.status !== "success") throw new Error("Cockpit gaf geen resultaat");
    return body.data?.result ?? [];
  }

  /** Haalt processor, geheugen en aantal exemplaren van één dag op en bewaart de dagtotalen per container. */
  async importDay(day: string) {
    const start = new Date(`${day}T00:00:00Z`), end = new Date(start.getTime() + 86_400_000);
    for (const a of this.env.CAPACITY_APPS) {
      const sel = `{resource_name="${a.container.replace(/["\\]/g, "")}"}`;
      const [cpu, mem] = await Promise.all([
        this.range(`serverless_container_cpu_usage_ratio${sel}`, start, end),
        this.range(`serverless_container_memory_usage_bytes${sel}`, start, end),
      ]);
      // Per tijdstip het drukste exemplaar telt; het aantal reeksen op een tijdstip = aantal exemplaren.
      const byTime = (series: PromSeries[]) => {
        const m = new Map<number, number[]>();
        for (const s of series) for (const [t, v] of s.values) { const n = Number(v); if (Number.isFinite(n)) m.set(t, [...(m.get(t) ?? []), n]); }
        return m;
      };
      const cpuT = byTime(cpu), memT = byTime(mem);
      const cpuPeak = [...cpuT.values()].map((v) => Math.max(...v));
      const limit = a.memory * 1024 * 1024;
      const memPeak = [...memT.values()].map((v) => (Math.max(...v) / limit) * 100);
      const inst = Math.max(0, ...[...cpuT.values(), ...memT.values()].map((v) => v.length));
      const avg = (v: number[]) => (v.length ? v.reduce((x, y) => x + y, 0) / v.length : null);
      const row = {
        cpuAvg: avg(cpuPeak), cpuP95: percentile(cpuPeak, 95),
        memAvg: avg(memPeak), memP95: percentile(memPeak, 95),
        instancesMax: cpuT.size || memT.size ? inst : null,
      };
      await withTenant(this.db, this.env.TENANT_ID, (tx) => tx.insert(capacityDaily)
        .values({ tenantId: this.env.TENANT_ID, day, app: a.app, ...row })
        .onConflictDoUpdate({ target: [capacityDaily.tenantId, capacityDaily.day, capacityDaily.app], set: { ...row, updatedAt: new Date() } }));
    }
  }

  /** Alles voor de capaciteitspagina: per container de maat, dagcijfers, kosten en advies, plus de snelheid. */
  async overview(now = new Date()) {
    const since = new Date(now.getTime() - 30 * 86_400_000).toISOString().slice(0, 10);
    const tenant = this.env.TENANT_ID;
    const { rows, speed } = await withTenant(this.db, tenant, async (tx) => ({
      rows: await tx.select().from(capacityDaily).where(and(eq(capacityDaily.tenantId, tenant), gte(capacityDaily.day, since))).orderBy(asc(capacityDaily.day)),
      speed: await tx.select({
        day: sql<string>`to_char(${speedSamples.at} at time zone 'Europe/Amsterdam', 'YYYY-MM-DD')`,
        path: speedSamples.path,
        p50: sql<number>`round(percentile_cont(0.5) within group (order by ${speedSamples.ms}))::int`,
        p95: sql<number>`round(percentile_cont(0.95) within group (order by ${speedSamples.ms}))::int`,
        failed: sql<number>`(count(*) filter (where ${speedSamples.status} = 0 or ${speedSamples.status} >= 500))::int`,
        total: sql<number>`count(*)::int`,
      }).from(speedSamples).where(and(eq(speedSamples.tenantId, tenant), gte(speedSamples.at, new Date(`${since}T00:00:00Z`))))
        .groupBy(sql`1`, speedSamples.path).orderBy(sql`1`),
    }));
    const weekAgo = new Date(now.getTime() - 7 * 86_400_000).toISOString().slice(0, 10);
    const speedWeek = speed.filter((s) => s.day >= weekAgo).map((s) => s.p95);
    const speedP95 = speedWeek.length ? Math.max(...speedWeek) : null;
    const apps = this.env.CAPACITY_APPS.map((a) => {
      const days: DayRow[] = rows.filter((r) => r.app === a.app).map(({ day, cpuAvg, cpuP95, memAvg, memP95, instancesMax }) => ({ day, cpuAvg, cpuP95, memAvg, memP95, instancesMax }));
      const week = days.filter((d) => d.day >= weekAgo);
      return { ...a, monthlyBase: monthlyBase(a), days, ...advise(a, week, speedP95) };
    });
    return { configured: this.metricsConfigured(), apps, speed, speedP95, paths: this.env.CAPACITY_SPEED_PATHS };
  }
}
