import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { normalizeTerm, WishesService } from "../src/modules/analytics/wishes.service";
import { createTestApp, INGEST_KEY, TENANT } from "./app";

describe("gezocht: zoekwoorden en aanvragen (ADR 0084)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });
  const wish = (term: string, kind: "miss" | "request", visitor: string, key = INGEST_KEY) =>
    ctx.http.inject({ method: "POST", url: "/v1/internal/wishes", headers: { "x-ingest-key": key }, payload: { term, market: "nl-NL", kind, visitorHash: visitor.padEnd(16, "x") } });
  const admin = (auth: string, method: "GET" | "PUT" = "GET", payload?: object, query = "") =>
    ctx.http.inject({ method, url: method === "GET" ? `/v1/admin/analytics/wishes${query}` : "/v1/admin/analytics/wishes/status", headers: { authorization: `Bearer ${auth}` }, ...(payload ? { payload } : {}) });

  it("maakt zoekwoorden gelijk en bewaart niets persoonlijks", () => {
    expect(normalizeTerm("  Éénhoorn!! ")).toBe("eenhoorn");
    expect(normalizeTerm("Brandweer   AUTO")).toBe("brandweer auto");
    expect(normalizeTerm("jan@example.nl")).toBeNull();
    expect(normalizeTerm("www.site.nl")).toBeNull();
    expect(normalizeTerm("06 12345678")).toBeNull();
    expect(normalizeTerm("a")).toBeNull();
    expect(normalizeTerm("x".repeat(41))).toBeNull();
    expect(normalizeTerm("123")).toBeNull();
  });

  it("telt bezoekers één keer per dag en toont gemiste woorden en aanvragen", async () => {
    expect((await wish("eenhoorn", "miss", "a", "fout")).statusCode).toBe(401);
    expect((await wish("Eenhoorn", "miss", "a")).json()).toEqual({ stored: true });
    await wish("eenhoorn", "miss", "a");
    await wish("eenhoorn", "miss", "b");
    await wish("draak", "request", "c");
    await wish("eénhoorn", "miss", "d");
    const list = (await admin("analist")).json();
    expect(list.terms.map((t: { term: string }) => t.term).sort()).toEqual(["draak", "eenhoorn"]);
    expect(list.terms).toContainEqual(expect.objectContaining({ term: "eenhoorn", missed: 3, requested: 0, markets: ["nl-NL"], status: "open" }));
    expect((await wish("mail@x.nl", "request", "e")).json()).toEqual({ stored: false });
  });

  it("zet een woord op gemaakt of verborgen, met audit en ongedaan maken", async () => {
    expect((await admin("analist", "PUT", { term: "draak", status: "hidden" })).statusCode).toBe(403);
    const res = await admin("beheerder", "PUT", { term: "draak", status: "hidden" });
    expect(res.statusCode).toBe(200);
    expect(res.json().terms.map((t: { term: string }) => t.term)).not.toContain("draak");
    expect((await admin("analist", "GET", undefined, "?hidden=1")).json().terms).toContainEqual(expect.objectContaining({ term: "draak", status: "hidden" }));
    await ctx.app.get(WishesService).setStatus(TENANT, "beheerder", "draak", "made");
    const made = (await ctx.app.get(WishesService).list(TENANT)).terms.find((t) => t.term === "draak");
    expect(made?.status).toBe("made");
  });

  it("haalt de bezoekerscode na 90 dagen weg maar houdt de aantallen", async () => {
    const svc = ctx.app.get(WishesService);
    await svc.record(TENANT, { term: "zeepaardje", market: "nl-NL", kind: "request", visitorHash: "oldvisitor000000" }, new Date("2026-01-01T10:00:00Z"));
    await svc.anonymize(TENANT, new Date("2026-06-01T10:00:00Z"));
    expect((await svc.list(TENANT)).terms).toContainEqual(expect.objectContaining({ term: "zeepaardje", requested: 1 }));
  });
});
