import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { ENV, type CapacityApp, type Env } from "../src/config/env";
import { advise, CapacityService, monthlyBase, percentile, type DayRow } from "../src/modules/operations/capacity.service";
import { createTestApp } from "./app";

const WEB: CapacityApp = { app: "web", container: "kleurhoek-web", cpu: 560, memory: 1024, min: 1, max: 10 };
const day = (d: string, cpu: number, mem: number, inst = 1): DayRow => ({ day: d, cpuAvg: cpu / 2, cpuP95: cpu, memAvg: mem / 2, memP95: mem, instancesMax: inst });
const week = (cpu: number, mem: number, inst = 1) => Array.from({ length: 7 }, (_, i) => day(`2026-11-0${i + 1}`, cpu, mem, inst));

describe("capaciteit (ADR 0092)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });

  it("rekent percentielen en vaste kosten", () => {
    expect(percentile([], 95)).toBeNull();
    expect(percentile(Array.from({ length: 100 }, (_, i) => i + 1), 95)).toBe(95);
    // 0,56 vCPU en 1 GB, altijd aan: 0,56 × 2.592.000 × 0,00001 + 2.592.000 × 0,000002 ≈ € 19,70
    expect(monthlyBase(WEB)).toBe(19.7);
    expect(monthlyBase({ ...WEB, min: 0 })).toBe(0);
  });

  it("adviseert alleen met genoeg cijfers en kiest bij twijfel voor snelheid", () => {
    expect(advise(WEB, week(10, 20).slice(0, 2), null).advice).toBe("onbekend");
    expect(advise(WEB, week(10, 20), null).advice).toBe("omlaag");
    expect(advise(WEB, week(10, 20).slice(0, 5), null).advice).toBe("goed");
    expect(advise(WEB, week(10, 85), null).advice).toBe("omhoog");
    expect(advise(WEB, week(90, 20), null).advice).toBe("omhoog");
    expect(advise(WEB, week(10, 20, 10), null).advice).toBe("omhoog");
    expect(advise(WEB, week(10, 20), 2000).advice).toBe("goed");
    expect(advise(WEB, week(50, 60), null).advice).toBe("goed");
  });

  it("leest Cockpit, meet de snelheid en toont alles in het admin panel", async () => {
    const env = ctx.app.get<Env>(ENV);
    Object.assign(env, { COCKPIT_METRICS_URL: "https://metrics.cockpit.test", COCKPIT_METRICS_TOKEN: "t", CAPACITY_APPS: [WEB] });
    const svc = ctx.app.get(CapacityService);
    const calls: string[] = [];
    const t0 = Date.parse("2026-11-07T00:00:00Z") / 1000;
    svc.fetch = (async (input: string | URL) => {
      const url = new URL(String(input));
      calls.push(url.pathname);
      if (url.pathname.endsWith("/query_range")) {
        const q = url.searchParams.get("query")!;
        expect(q).toContain('resource_name="kleurhoek-web"');
        // Twee exemplaren; per tijdstip telt het drukste.
        const cpu = q.startsWith("serverless_container_cpu");
        const series = [0, 1].map((n) => ({ values: Array.from({ length: 20 }, (_, i) => [t0 + i * 300, String(cpu ? (n ? 40 : 10) : (n ? 512 : 256) * 1024 * 1024)]) }));
        return new Response(JSON.stringify({ status: "success", data: { result: series } }));
      }
      return new Response("ok", { status: 200 });
    }) as typeof fetch;

    await svc.importDay("2026-11-07");
    await svc.importDay("2026-11-07"); // tweede keer werkt bij, geen dubbele rij
    await svc.measureSpeed(new Date("2026-11-07T12:00:00Z"));
    expect(calls.filter((c) => c === "/prometheus/api/v1/query_range")).toHaveLength(4);

    const res = await ctx.http.inject({ method: "GET", url: "/v1/admin/capacity", headers: { authorization: "Bearer beheerder" } });
    expect(res.statusCode).toBe(200);
    const body = res.json() as { configured: boolean; apps: { app: string; days: DayRow[]; advice: string; monthlyBase: number }[]; speed: { path: string; total: number }[] };
    expect(body.configured).toBe(true);
    const web = body.apps[0]!;
    expect(web.days).toHaveLength(1);
    expect(web.days[0]).toMatchObject({ day: "2026-11-07", cpuP95: 40, memP95: 50, instancesMax: 2 });
    expect(web.advice).toBe("onbekend");
    expect(web.monthlyBase).toBe(19.7);
    expect(body.speed.map((s) => s.path).sort()).toEqual(["/", "/platen/sinterklaas"]);

    const denied = await ctx.http.inject({ method: "GET", url: "/v1/admin/capacity", headers: { authorization: "Bearer analist" } });
    expect(denied.statusCode).toBe(403);
    Object.assign(env, { COCKPIT_METRICS_URL: undefined, COCKPIT_METRICS_TOKEN: undefined, CAPACITY_APPS: [] });
  });

  it("meldt een fout van Cockpit", async () => {
    const env = ctx.app.get<Env>(ENV);
    Object.assign(env, { COCKPIT_METRICS_URL: "https://metrics.cockpit.test", COCKPIT_METRICS_TOKEN: "t", CAPACITY_APPS: [WEB] });
    const svc = ctx.app.get(CapacityService);
    svc.fetch = (async () => new Response("nee", { status: 401 })) as typeof fetch;
    await expect(svc.importDay("2026-11-06")).rejects.toThrow("Cockpit gaf 401");
    Object.assign(env, { COCKPIT_METRICS_URL: undefined, COCKPIT_METRICS_TOKEN: undefined, CAPACITY_APPS: [] });
  });
});
