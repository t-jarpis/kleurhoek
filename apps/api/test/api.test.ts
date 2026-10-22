import { loadEnv } from "../src/config/env";
import * as source from "@kleurhoek/catalog-data";
import { and, eq } from "drizzle-orm";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { DB, type Database } from "../src/db/database";
import { withTenant } from "../src/db/tenant";
import { auditEvents } from "../src/modules/identity/identity.schema";
import { plateRules } from "../src/modules/availability/availability.schema";
import { plates } from "../src/modules/catalog/catalog.schema";
import { AnalyticsService } from "../src/modules/analytics/analytics.service";
import { StorefrontService } from "../src/modules/storefront/storefront.service";
import { createTestApp, INGEST_KEY, TENANT } from "./app";

let ctx: Awaited<ReturnType<typeof createTestApp>>;
let db: Database;
const get = (url: string, headers: Record<string, string> = {}) => ctx.http.inject({ method: "GET", url, headers });

beforeAll(async () => { ctx = await createTestApp(); db = ctx.app.get(DB); });
afterAll(async () => { await ctx.app.close(); });

describe("website-API", () => {
  it("health is ok, met beveiligingsheaders", async () => {
    const r = await get("/health");
    expect(r.statusCode).toBe(200);
    expect(r.headers["x-content-type-options"]).toBe("nosniff");
    expect(r.headers["cache-control"]).toBe("no-store");
  });

  it("geeft alle platen voor nl-NL, met cache-headers voor het CDN", async () => {
    const r = await get("/v1/markets/nl-nl/plates");
    expect(r.statusCode).toBe(200);
    expect(r.json().count).toBe(source.plates().length);
    expect(r.headers["cache-control"]).toContain("s-maxage");
    expect(r.json().items[0]).toMatchObject({ slug: "kat", name: "Kat op een kussen", svg: "/v1/assets/plates/kat/1.svg" });
  });

  it("filtert op leeftijd, werelddeel, land en feestdag", async () => {
    const expected = source.plates().filter((p) => p.age === "2-4").length;
    expect((await get("/v1/markets/nl-NL/plates?age=2-4")).json().count).toBe(expected);
    const nl = (await get("/v1/markets/nl-NL/plates?category=wereld&continent=europa&country=Nederland")).json();
    expect(nl.items.map((p: { slug: string }) => p.slug).sort()).toEqual(["kroon", "lampion", "molen", "schoen"]);
    expect((await get("/v1/markets/nl-NL/plates?holiday=divali")).json().items.map((p: { slug: string }) => p.slug)).toEqual(["divali"]);
  });

  it("geeft details met kleur-op-nummer en kleurnamen", async () => {
    const r = await get("/v1/markets/nl-NL/plates/kat");
    expect(r.statusCode).toBe(200);
    const p = r.json();
    expect(p).toMatchObject({ word: "de kat", countQuestion: "Hoeveel snorharen tel je?" });
    expect(p.colorByNumber.palette[0]).toMatchObject({ number: 1, code: "p", name: "paars" });
    expect(p.colorByNumber.labels).toHaveLength(13);
  });

  it("serveert de SVG met een vaste cache en een strikte CSP", async () => {
    const r = await get("/v1/assets/plates/kat/1.svg");
    expect(r.statusCode).toBe(200);
    expect(r.headers["content-type"]).toContain("image/svg+xml");
    expect(r.headers["cache-control"]).toContain("immutable");
    expect(r.headers["content-security-policy"]).toContain("sandbox");
    expect(r.body.startsWith("<svg")).toBe(true);
    expect((await get("/v1/assets/plates/kat/2.svg")).statusCode).toBe(404);
  });

  it("weigert onbekende markten en ongeldige filters", async () => {
    expect((await get("/v1/markets/de-DE/plates")).statusCode).toBe(404);
    expect((await get("/v1/markets/nl-NL/plates?age=<script>")).statusCode).toBe(400);
    expect((await get("/v1/markets/nl-NL/plates?foo=1")).statusCode).toBe(400);
  });

  it("geeft taxonomie en seizoen in de taal van de markt", async () => {
    const t = (await get("/v1/markets/nl-NL/taxonomy")).json();
    expect(t.categories.map((c: { name: string }) => c.name)).toContain("Wereld");
    expect(t.holidays[0]).toEqual({ slug: "oudnieuw", name: "Oud en nieuw" });
    const store = ctx.app.get(StorefrontService);
    const market = (await store.market("nl-NL"))!;
    const s = await store.season(market, new Date("2026-10-22T10:00:00Z"));
    expect(s.active.map((a) => a.slug)).toEqual(["herfst", "halloween", "divali"]);
    expect(s.soon.map((a) => a.slug)).toEqual(expect.arrayContaining(["sintmaarten", "sinterklaas", "chanoeka"]));
  });

  it("verbergt een plaat met een beschikbaarheidsregel voor een ander land", async () => {
    await withTenant(db, TENANT, (tx) => tx.insert(plateRules).values({ tenantId: TENANT, plateSlug: "kroon", mode: "only_in", countries: ["BE"] }));
    expect((await get("/v1/markets/nl-NL/plates/kroon")).statusCode).toBe(404);
    expect((await get("/v1/markets/nl-NL/plates")).json().count).toBe(source.plates().length - 1);
    await withTenant(db, TENANT, (tx) => tx.delete(plateRules).where(eq(plateRules.plateSlug, "kroon")));
  });
});

describe("row-level security", () => {
  const OTHER = "0192f6a0-0000-7000-8000-0000000000ff";

  it("toont geen data van een andere tenant, ook niet met een fout in de query", async () => {
    await withTenant(db, OTHER, (tx) => tx.insert(plates).values({ tenantId: OTHER, slug: "geheim", categorySlug: "dieren", ageSlug: "2-4", status: "published" }));
    const seen = await withTenant(db, TENANT, (tx) => tx.select({ slug: plates.slug }).from(plates).where(eq(plates.slug, "geheim")));
    expect(seen).toEqual([]);
    const own = await withTenant(db, OTHER, (tx) => tx.select({ slug: plates.slug }).from(plates));
    expect(own.map((p) => p.slug)).toEqual(["geheim"]);
  });

  it("weigert schrijven met een andere tenant_id dan de sessie", async () => {
    await expect(withTenant(db, TENANT, (tx) => tx.insert(plates).values({ tenantId: OTHER, slug: "inbraak", categorySlug: "dieren", ageSlug: "2-4" }))).rejects.toThrow();
  });
});

describe("analytics", () => {
  const post = (body: unknown, key?: string) => ctx.http.inject({ method: "POST", url: "/v1/internal/events", payload: body as object, headers: key ? { "x-ingest-key": key } : {} });
  const ev = (type: string, plate?: string) => ({ type, plate, market: "nl-NL", country: "NL", device: "mobile", visitorHash: "abcdefghijklmnop", occurredAt: "2026-10-21T12:00:00Z" });

  it("accepteert events alleen met de juiste sleutel en geldige inhoud", async () => {
    expect((await post([ev("page_view")])).statusCode).toBe(401);
    expect((await post([ev("page_view")], "x".repeat(40))).statusCode).toBe(401);
    expect((await post([{ ...ev("page_view"), ip: "1.2.3.4" }], INGEST_KEY)).statusCode).toBe(400);
    const r = await post([ev("page_view"), ev("plate_view", "kat"), ev("pdf_download", "kat"), ev("print", "uil")], INGEST_KEY);
    expect(r.statusCode).toBe(202);
    expect(r.json()).toEqual({ accepted: 4 });
  });

  it("maakt dagtotalen en toont ze alleen aan beheerders met het recht", async () => {
    await ctx.app.get(AnalyticsService).aggregateDay(TENANT, "2026-10-21");
    const url = "/v1/admin/analytics/summary?from=2026-10-21&to=2026-10-21";
    expect((await get(url)).statusCode).toBe(401);
    const r = await get(url, { authorization: "Bearer analist" });
    expect(r.statusCode).toBe(200);
    expect(r.json().topPlates[0]).toMatchObject({ plate: "kat", views: 1, downloads: 1 });
    expect(r.json().byCountry[0]).toMatchObject({ country: "NL", pageViews: 1 });
  });
});

describe("rate limiting", () => {
  it("is alleen in te stellen met het recht, en wordt gelogd", async () => {
    const put = (auth: string) => ctx.http.inject({ method: "PUT", url: "/v1/admin/rate-limits/public-read", payload: { limit: 3 }, headers: { authorization: auth } });
    expect((await put("Bearer analist")).statusCode).toBe(403);
    expect((await ctx.http.inject({ method: "PUT", url: "/v1/admin/rate-limits/public-read", payload: { limit: 0 }, headers: { authorization: "Bearer beheerder" } })).statusCode).toBe(400);
    const r = await put("Bearer beheerder");
    expect(r.statusCode).toBe(200);
    expect(r.json()).toMatchObject({ slug: "public-read", limit: 3 });
    const log = await withTenant(db, TENANT, (tx) => tx.select().from(auditEvents).where(and(eq(auditEvents.action, "operations.ratelimit.update"))));
    expect(log[0]).toMatchObject({ actor: "user-beheerder", subject: "rate_limit:public-read", before: expect.objectContaining({ limit: 300 }), after: expect.objectContaining({ limit: 3 }) });
  });

  it("blokkeert met 429 en Retry-After boven de limiet, per bezoeker", async () => {
    const hit = (ip: string) => get("/v1/markets/nl-NL/taxonomy", { "cf-connecting-ip": ip });
    for (let i = 0; i < 3; i++) expect((await hit("203.0.113.7")).statusCode).toBe(200);
    const blocked = await hit("203.0.113.7");
    expect(blocked.statusCode).toBe(429);
    expect(Number(blocked.headers["retry-after"])).toBeGreaterThan(0);
    expect(blocked.json().message).toContain("Probeer het over");
    expect((await hit("198.51.100.1")).statusCode).toBe(200);
  });

  it("toont regels en geblokkeerde verzoeken in het admin panel", async () => {
    const r = await get("/v1/admin/rate-limits", { authorization: "Bearer analist" });
    expect(r.statusCode).toBe(200);
    const rule = r.json().rules.find((x: { slug: string }) => x.slug === "public-read");
    expect(rule).toMatchObject({ limit: 3, enabled: true, updatedBy: "user-beheerder" });
    expect(rule.days.at(-1).blocked).toBeGreaterThanOrEqual(1);
  });
});

describe("configuratie", () => {
  it("weigert een dev-beheerderstoken in productie", async () => {
    expect(() => loadEnv({ NODE_ENV: "production", DATABASE_URL: "postgres://x@localhost/db", INGEST_KEY: "k".repeat(40), ADMIN_DEV_TOKEN: "t".repeat(40) })).toThrow(/niet toegestaan/);
    expect(() => loadEnv({ NODE_ENV: "production", INGEST_KEY: "k".repeat(40) })).toThrow(/DATABASE_URL/);
  });
});
