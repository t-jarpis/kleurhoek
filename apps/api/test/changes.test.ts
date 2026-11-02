import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { createTestApp } from "./app";

/** Wijzigingen en ongedaan maken (ADR 0066). */
describe("wijzigingen ongedaan maken", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });
  const admin = { authorization: "Bearer beheerder" };
  const changes = async () => (await ctx.http.inject({ method: "GET", url: "/v1/admin/changes", headers: admin })).json().items as { id: string; action: string; subject: string; undo: string; label: string | null }[];
  const rule = async () => (await ctx.http.inject({ method: "GET", url: "/v1/admin/rate-limits", headers: admin })).json().rules.find((r: { slug: string }) => r.slug === "contact-challenge") as { limit: number };

  it("alleen met het recht om wijzigingen te zien", async () => {
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/changes", headers: { authorization: "Bearer analist" } })).statusCode).toBe(403);
  });

  it("zet een rate limit terug, en daarna kan het niet nog eens", async () => {
    const original = (await rule()).limit;
    expect((await ctx.http.inject({ method: "PUT", url: "/v1/admin/rate-limits/contact-challenge", payload: { limit: original + 7 }, headers: admin })).statusCode).toBe(200);
    const change = (await changes()).find((c) => c.action === "operations.ratelimit.update" && c.subject === "rate_limit:contact-challenge")!;
    expect(change).toMatchObject({ undo: "ja", label: "Rate limit" });
    expect((await ctx.http.inject({ method: "POST", url: `/v1/admin/changes/${change.id}/undo`, headers: admin })).statusCode).toBe(201);
    expect((await rule()).limit).toBe(original);
    const after = await changes();
    expect(after[0]).toMatchObject({ action: "undo:operations.ratelimit.update", subject: "rate_limit:contact-challenge", undo: "nee" });
    expect(after.find((c) => c.id === change.id)!.undo).toBe("verouderd");
    expect((await ctx.http.inject({ method: "POST", url: `/v1/admin/changes/${change.id}/undo`, headers: admin })).statusCode).toBe(409);
  });

  it("alleen de laatste wijziging van iets kan terug", async () => {
    const original = (await rule()).limit;
    for (const n of [1, 2]) await ctx.http.inject({ method: "PUT", url: "/v1/admin/rate-limits/contact-challenge", payload: { limit: original + n }, headers: admin });
    const list = (await changes()).filter((c) => c.subject === "rate_limit:contact-challenge" && c.action === "operations.ratelimit.update");
    expect(list[0]!.undo).toBe("ja");
    expect(list[1]!.undo).toBe("verouderd");
  });
});
