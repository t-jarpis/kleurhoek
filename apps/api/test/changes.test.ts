import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { SocialService } from "../src/modules/social/social.service";
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

  const call = (method: "GET" | "PUT" | "POST", url: string, payload?: unknown) => ctx.http.inject({ method, url, headers: admin, ...(payload === undefined ? {} : { payload: payload as object }) });
  const undo = async (action: string, subject: string) => {
    const c = (await changes()).find((x) => x.action === action && x.subject === subject)!;
    expect(c.undo).toBe("ja");
    return call("POST", `/v1/admin/changes/${c.id}/undo`);
  };

  it("social: instellingen en een goedgekeurde post terug, een geplaatste post niet", async () => {
    await call("PUT", "/v1/admin/social/settings", { notifyEmail: null, pinsPerDay: 5, feedDays: [1, 3, 5], feedTime: "19:30" });
    await call("PUT", "/v1/admin/social/settings", { notifyEmail: null, pinsPerDay: 9, feedDays: [2], feedTime: "08:00" });
    expect((await undo("social.settings", "social:instellingen")).statusCode).toBe(201);
    expect(await ctx.app.get(SocialService).settings()).toMatchObject({ pinsPerDay: 5, feedDays: [1, 3, 5] });

    await ctx.app.get(SocialService).generate(new Date("2026-03-02T06:00:00Z"));
    const open = (await call("GET", "/v1/admin/social/posts?status=voorstel")).json().posts as { id: string; channel: string }[];
    // Zonder gekoppelde kanalen worden het teksten om zelf te delen; die kun je als geplaatst markeren.
    const [a, b] = open.filter((p) => p.channel === "delen");
    await call("POST", "/v1/admin/social/posts/decide", { ids: [a!.id, b!.id], approve: true });
    expect((await undo("social.post.decide", `social-post:${a!.id}`)).statusCode).toBe(201);
    const status = async (id: string) => ((await call("GET", "/v1/admin/social/posts")).json().posts as { id: string; status: string }[]).find((p) => p.id === id)!.status;
    expect(await status(a!.id)).toBe("voorstel");
    expect(await status(b!.id)).toBe("goedgekeurd");
    // Intussen geplaatst: terugzetten kan niet meer.
    expect((await call("POST", `/v1/admin/social/posts/${b!.id}/shared`)).statusCode).toBe(204);
    const c = (await changes()).find((x) => x.action === "social.post.decide" && x.subject === `social-post:${b!.id}`)!;
    expect((await call("POST", `/v1/admin/changes/${c.id}/undo`)).statusCode).toBe(409);
  });

  it("organisatie: instellingen terug, het aanbod dat de organisatie zelf instelt ook", async () => {
    await call("POST", "/v1/admin/organizations", { slug: "school-terug", name: "School Terug", kind: "school" });
    await call("PUT", "/v1/admin/organizations/school-terug", { name: "Andere naam", hosts: ["platen.terug.nl"] });
    expect((await undo("organizations.update", "organization:school-terug")).statusCode).toBe(201);
    const org = (await call("GET", "/v1/admin/organizations")).json().organizations.find((o: { slug: string }) => o.slug === "school-terug");
    expect(org).toMatchObject({ name: "School Terug", hosts: [] });
  });
});
