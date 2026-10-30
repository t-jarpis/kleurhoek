import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { sql } from "drizzle-orm";
import { DB, type Database } from "../src/db/database";
import { MemoryTransport } from "../src/modules/messaging/mailer";
import { atLocal, SocialService } from "../src/modules/social/social.service";
import { createTestApp } from "./app";

const ADMIN = "https://admin.kleurhoek.test";
let ctx: Awaited<ReturnType<typeof createTestApp>>;
let social: SocialService;
const mail = new MemoryTransport();
const calls: { method: string; url: string; body: string }[] = [];
const as = (url: string, payload?: object, method: "GET" | "POST" | "PUT" = payload ? "POST" : "GET") =>
  ctx.http.inject({ method, url, headers: { authorization: "Bearer beheerder" }, ...(payload ? { payload } : {}) });

/** Nep-Pinterest en nep-Meta: alleen wat de koppeling gebruikt. */
const fake = async (url: string, init?: RequestInit): Promise<Response> => {
  const body = typeof init?.body === "string" ? init.body : "";
  calls.push({ method: init?.method ?? "GET", url, body });
  const ok = (v: unknown) => new Response(JSON.stringify(v), { status: 200, headers: { "content-type": "application/json" } });
  if (url.endsWith("/v5/oauth/token")) return ok({ access_token: "pin-access-geheim", refresh_token: "pin-refresh-geheim", expires_in: 2_592_000, refresh_token_expires_in: 31_536_000 });
  if (url.endsWith("/v5/user_account")) return ok({ username: "kleurhoek" });
  if (url.includes("/v5/boards?")) return ok({ items: [{ id: "b-1", name: "Kleurplaten dieren" }], bookmark: null });
  if (url.endsWith("/v5/boards")) return ok({ id: `b-${calls.length}` });
  if (url.endsWith("/v5/pins")) return ok({ id: `p-${calls.length}` });
  if (url.includes("/oauth/access_token")) return ok({ access_token: url.includes("fb_exchange_token") ? "meta-long" : "meta-short" });
  if (url.includes("/me/accounts")) return ok({ data: [{ id: "page-1", name: "Kleurhoek", access_token: "page-geheim", instagram_business_account: { id: "ig-1", username: "kleurhoek.nl" } }] });
  if (url.includes("/page-1/photos")) return ok({ id: "ph-1", post_id: "page-1_42" });
  if (url.includes("/ig-1/media_publish")) return ok({ id: "ig-media-1" });
  if (url.includes("/ig-1/media")) return ok({ id: "container-1" });
  if (url.includes("/container-1?")) return ok({ status_code: "FINISHED" });
  if (url.includes("/ig-media-1?")) return ok({ permalink: "https://www.instagram.com/p/abc/" });
  return new Response("{}", { status: 404 });
};

beforeAll(async () => {
  Object.assign(process.env, { SOCIAL_INTERVAL_MS: "0", ADMIN_URL: ADMIN, PINTEREST_APP_ID: "pin-app", PINTEREST_APP_SECRET: "pin-secret", META_APP_ID: "meta-app", META_APP_SECRET: "meta-secret" });
  ctx = await createTestApp({ mail });
  social = ctx.app.get(SocialService);
  social.fetch = fake;
});
afterAll(async () => {
  for (const k of ["SOCIAL_INTERVAL_MS", "ADMIN_URL", "PINTEREST_APP_ID", "PINTEREST_APP_SECRET", "META_APP_ID", "META_APP_SECRET"]) delete process.env[k];
  await ctx.app.close();
});

const state = (url: string) => new URL(url).searchParams.get("state")!;

describe("social (ADR 0063)", () => {
  it("koppelt Pinterest en Meta via OAuth en bewaart de sleutels versleuteld", async () => {
    expect((await as(`/v1/admin/social/connect/pinterest?redirectUri=${encodeURIComponent("https://evil.example/social/koppel/pinterest")}`)).statusCode).toBe(400);
    const pinRedirect = `${ADMIN}/social/koppel/pinterest`;
    const { url } = (await as(`/v1/admin/social/connect/pinterest?redirectUri=${encodeURIComponent(pinRedirect)}`)).json();
    expect(url).toContain("https://www.pinterest.com/oauth/");
    expect((await as("/v1/admin/social/connect/pinterest", { code: "c", state: "verzonnen.state.x.y", redirectUri: pinRedirect })).statusCode).toBe(400);
    expect((await as("/v1/admin/social/connect/pinterest", { code: "c", state: state(url), redirectUri: pinRedirect })).json()).toEqual({ connected: ["pinterest"] });

    const metaRedirect = `${ADMIN}/social/koppel/meta`;
    const meta = (await as(`/v1/admin/social/connect/meta?redirectUri=${encodeURIComponent(metaRedirect)}`)).json().url;
    expect((await as("/v1/admin/social/connect/meta", { code: "c", state: state(meta), redirectUri: metaRedirect })).json()).toMatchObject({ connected: ["facebook", "instagram"], instagram: "kleurhoek.nl" });

    const overview = (await as("/v1/admin/social")).json();
    expect(overview.channels.map((c: { kind: string; connected: boolean; account: string }) => [c.kind, c.connected, c.account])).toEqual([["pinterest", true, "kleurhoek"], ["facebook", true, "Kleurhoek"], ["instagram", true, "@kleurhoek.nl"]]);
    const raw = await ctx.app.get<Database>(DB).execute(sql`select token from social.channels`) as unknown as { rows: { token: string }[] };
    expect(raw.rows).toHaveLength(3);
    for (const r of raw.rows) expect(r.token).not.toMatch(/geheim|access/);
  });

  it("maakt voorstellen: pins per dag, en op maandag en woensdag een post over de eerstvolgende feestdag", async () => {
    const now = new Date("2026-11-02T04:30:00Z"); // maandag, 5:30 in Nederland
    expect(await social.generate(now)).toBeGreaterThan(0);
    expect(await social.generate(now)).toBe(0); // geen dubbele voorstellen
    const list = (await as("/v1/admin/social/posts?status=voorstel")).json().posts as { channel: string; source: string; image: string; scheduledAt: string; body: string; board: string | null }[];
    const pins = list.filter((p) => p.channel === "pinterest");
    expect(pins).toHaveLength(15);
    expect(pins.every((p) => p.image.endsWith(".png?r=2") && p.board)).toBe(true);
    const feed = list.filter((p) => p.channel !== "pinterest");
    expect(feed.map((p) => p.channel).sort()).toEqual(["delen", "delen", "facebook", "facebook", "instagram", "instagram"]);
    expect(feed.every((p) => p.source === "feestdag")).toBe(true);
    expect(feed.find((p) => p.channel === "instagram")!.image).toMatch(/\.jpg\?r=2$/);
    expect(feed.find((p) => p.channel === "facebook")!.body).toMatch(/over \d+ dagen|morgen/);
    expect(new Date(feed[0]!.scheduledAt).toISOString()).toBe(atLocal("2026-11-02", "19:30").toISOString());
  });

  it("mailt de voorstellen één keer per ochtend", async () => {
    await as("/v1/admin/social/settings", { notifyEmail: "thijs@example.test", pinsPerDay: 5, feedDays: [1, 3, 5], feedTime: "19:30" }, "PUT");
    expect(await social.digest(new Date("2026-11-02T05:30:00Z"))).toBe(false); // 6:30, nog te vroeg
    expect(await social.digest(new Date("2026-11-02T06:30:00Z"))).toBe(true);
    expect(await social.digest(new Date("2026-11-02T09:00:00Z"))).toBe(false);
    expect(mail.sent.at(-1)!.subject).toMatch(/21 voorstellen/);
    expect(mail.sent.at(-1)!.html).toContain(`${ADMIN}/social`);
  });

  it("plaatst alleen wat is goedgekeurd, op het geplande moment", async () => {
    const all = (await as("/v1/admin/social/posts?status=voorstel")).json().posts as { id: string; channel: string; scheduledAt: string }[];
    const monday = all.filter((p) => p.scheduledAt.startsWith("2026-11-02"));
    const pins = monday.filter((p) => p.channel === "pinterest");
    const skip = pins.at(-1)!;
    await as("/v1/admin/social/posts/decide", { ids: [skip.id], approve: false });
    await as("/v1/admin/social/posts/decide", { ids: monday.filter((p) => p !== skip).map((p) => p.id), approve: true });
    calls.length = 0;
    expect(await social.publishDue(new Date("2026-11-02T10:00:00Z"))).toBe(1); // alleen de pin van 8:30 is aan de beurt
    expect(await social.publishDue(new Date("2026-11-02T23:00:00Z"))).toBe(3 + 2);
    expect(calls.filter((c) => c.url.endsWith("/v5/pins"))).toHaveLength(4);
    expect(calls.some((c) => c.url.includes("/page-1/photos") && c.body.includes(".jpg"))).toBe(true);
    expect(calls.some((c) => c.url.includes("/ig-1/media_publish"))).toBe(true);
    const done = (await as("/v1/admin/social/posts?status=geplaatst")).json().posts as { channel: string; externalUrl: string }[];
    expect(done.find((p) => p.channel === "instagram")!.externalUrl).toBe("https://www.instagram.com/p/abc/");
    // De tekst om te delen wordt niet geplaatst; Thijs deelt hem zelf en vinkt hem af.
    const share = (await as("/v1/admin/social/posts?status=goedgekeurd&channel=delen")).json().posts[0];
    expect((await as(`/v1/admin/social/posts/${share.id}/shared`, {})).statusCode).toBe(204);
  });

  it("probeert een mislukte post drie keer", async () => {
    const [p] = (await as("/v1/admin/social/posts?status=voorstel&channel=pinterest")).json().posts as { id: string }[];
    await as("/v1/admin/social/posts/decide", { ids: [p!.id], approve: true });
    social.fetch = async (url, init) => (url.endsWith("/v5/pins") ? new Response(JSON.stringify({ message: "Ongeldige afbeelding" }), { status: 400 }) : fake(url, init));
    for (let i = 0; i < 3; i++) await social.publishDue(new Date("2026-11-05T23:00:00Z"));
    social.fetch = fake;
    const failed = (await as("/v1/admin/social/posts?status=mislukt")).json().posts;
    expect(failed).toHaveLength(1);
    expect(failed[0].error).toContain("Ongeldige afbeelding");
  });
});
