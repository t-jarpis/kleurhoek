import { startMockOidc, type MockUser } from "@t-jarpis/auth/testing";
import { eq } from "drizzle-orm";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { DB, type Database } from "../src/db/database";
import { withTenant } from "../src/db/tenant";
import { auditEvents, users } from "../src/modules/identity/identity.schema";
import { ADMIN_ORG, AUDIENCE, createTestApp, SITE_ORG, TENANT } from "./app";

const OWNER: MockUser = { sub: "z-owner", name: "Thijs", email: "thijs@example.test", organizationId: ADMIN_ORG, locale: "nl" };
const COLLEAGUE: MockUser = { sub: "z-collega", name: "Collega", email: "collega@example.test", organizationId: ADMIN_ORG };
const PARENT: MockUser = { sub: "z-ouder", name: "Ouder", email: "ouder@example.test", organizationId: SITE_ORG };
const STRANGER: MockUser = { sub: "z-vreemd", organizationId: "org-andere-site" };

let op: Awaited<ReturnType<typeof startMockOidc>>;
let ctx: Awaited<ReturnType<typeof createTestApp>>;
let db: Database;
const bearer = async (user: MockUser, ttl = 300) => ({ authorization: `Bearer ${await op.accessToken(ttl, user)}` });

beforeAll(async () => {
  op = await startMockOidc({ clientId: "admin", audience: AUDIENCE, user: OWNER });
  ctx = await createTestApp({ oidc: { issuer: op.issuer, bootstrap: [OWNER.sub] } });
  db = ctx.app.get(DB);
});
afterAll(async () => { await ctx.app.close(); await op.close(); });

describe("beheerders via Zitadel", () => {
  it("maakt de eigenaar bij de eerste login platformbeheerder (bootstrap)", async () => {
    const res = await ctx.http.inject({ method: "GET", url: "/v1/admin/me", headers: await bearer(OWNER) });
    expect(res.statusCode).toBe(200);
    expect(res.json().permissions).toContain("identity.roles.assign");
    const [row] = await withTenant(db, TENANT, (tx) => tx.select().from(users).where(eq(users.zitadelSub, OWNER.sub)));
    expect(row).toMatchObject({ kind: "admin", displayName: "Thijs", email: "thijs@example.test", locale: "nl" });
  });

  it("laat een nieuwe beheerder zonder rol binnen, maar zonder rechten", async () => {
    const me = await ctx.http.inject({ method: "GET", url: "/v1/admin/me", headers: await bearer(COLLEAGUE) });
    expect(me.json().permissions).toEqual([]);
    const limits = await ctx.http.inject({ method: "GET", url: "/v1/admin/rate-limits", headers: await bearer(COLLEAGUE) });
    expect(limits.statusCode).toBe(403);
  });

  it("weigert tokens van een andere organisatie, verlopen of zonder token", async () => {
    for (const headers of [await bearer(PARENT), await bearer(STRANGER), await bearer(OWNER, -120), {}, { authorization: "Bearer rommel" }]) {
      const res = await ctx.http.inject({ method: "GET", url: "/v1/admin/me", headers });
      expect(res.statusCode).toBe(401);
    }
  });

  it("kent rollen toe, met auditspoor, en de rechten werken direct", async () => {
    const list = await ctx.http.inject({ method: "GET", url: "/v1/admin/users?kind=admin", headers: await bearer(OWNER) });
    expect(list.statusCode).toBe(200);
    const colleague = list.json().users.find((u: { email: string }) => u.email === COLLEAGUE.email);
    expect(colleague.roles).toEqual([]);

    const put = await ctx.http.inject({ method: "PUT", url: `/v1/admin/users/${colleague.id}/roles`, headers: await bearer(OWNER), payload: { roles: ["analist"] } });
    expect(put.statusCode).toBe(200);
    expect(put.json().roles).toEqual(["analist"]);

    const limits = await ctx.http.inject({ method: "GET", url: "/v1/admin/rate-limits", headers: await bearer(COLLEAGUE) });
    expect(limits.statusCode).toBe(200);
    const manage = await ctx.http.inject({ method: "PUT", url: "/v1/admin/rate-limits/admin", headers: await bearer(COLLEAGUE), payload: { limit: 1 } });
    expect(manage.statusCode).toBe(403);

    const audit = await withTenant(db, TENANT, (tx) => tx.select().from(auditEvents).where(eq(auditEvents.action, "identity.roles.assigned")));
    expect(audit.map((a) => a.after)).toContainEqual({ roles: ["analist"] });
  });

  it("weigert onbekende rollen, rollen voor websitegebruikers en wijzigingen aan jezelf", async () => {
    const owner = await withTenant(db, TENANT, async (tx) => (await tx.select().from(users).where(eq(users.zitadelSub, OWNER.sub)))[0]!);
    const self = await ctx.http.inject({ method: "PUT", url: `/v1/admin/users/${owner.id}/roles`, headers: await bearer(OWNER), payload: { roles: [] } });
    expect(self.statusCode).toBe(403);

    const colleague = await withTenant(db, TENANT, async (tx) => (await tx.select().from(users).where(eq(users.zitadelSub, COLLEAGUE.sub)))[0]!);
    const unknown = await ctx.http.inject({ method: "PUT", url: `/v1/admin/users/${colleague.id}/roles`, headers: await bearer(OWNER), payload: { roles: ["koning"] } });
    expect(unknown.statusCode).toBe(400);

    await ctx.http.inject({ method: "GET", url: "/v1/me", headers: await bearer(PARENT) });
    const parent = await withTenant(db, TENANT, async (tx) => (await tx.select().from(users).where(eq(users.zitadelSub, PARENT.sub)))[0]!);
    const member = await ctx.http.inject({ method: "PUT", url: `/v1/admin/users/${parent.id}/roles`, headers: await bearer(OWNER), payload: { roles: ["analist"] } });
    expect(member.statusCode).toBe(409);
  });

  it("een geblokkeerde beheerder komt er niet meer in", async () => {
    const colleague = await withTenant(db, TENANT, async (tx) => (await tx.select().from(users).where(eq(users.zitadelSub, COLLEAGUE.sub)))[0]!);
    const block = await ctx.http.inject({ method: "PUT", url: `/v1/admin/users/${colleague.id}/status`, headers: await bearer(OWNER), payload: { status: "blocked" } });
    expect(block.json().status).toBe("blocked");
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/me", headers: await bearer(COLLEAGUE) })).statusCode).toBe(401);
    await ctx.http.inject({ method: "PUT", url: `/v1/admin/users/${colleague.id}/status`, headers: await bearer(OWNER), payload: { status: "active" } });
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/me", headers: await bearer(COLLEAGUE) })).statusCode).toBe(200);
  });
});

describe("websitegebruikers", () => {
  it("maakt het account aan bij de eerste aanroep en geeft het profiel", async () => {
    const res = await ctx.http.inject({ method: "GET", url: "/v1/me", headers: { ...(await bearer(PARENT)), "cf-ipcountry": "BE" } });
    expect(res.statusCode).toBe(200);
    expect(res.json()).toMatchObject({ displayName: "Ouder", email: "ouder@example.test" });
  });

  it("weigert beheerders en andere sites op /v1/me", async () => {
    expect((await ctx.http.inject({ method: "GET", url: "/v1/me", headers: await bearer(OWNER) })).statusCode).toBe(401);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/me", headers: await bearer(STRANGER) })).statusCode).toBe(401);
  });

  it("zoekt websitegebruikers in het admin panel", async () => {
    const res = await ctx.http.inject({ method: "GET", url: "/v1/admin/users?kind=member&q=ouder", headers: await bearer(OWNER) });
    expect(res.json()).toMatchObject({ total: 1, users: [{ email: "ouder@example.test", kind: "member" }] });
    const pct = await ctx.http.inject({ method: "GET", url: "/v1/admin/users?q=%25", headers: await bearer(OWNER) });
    expect(pct.json().total).toBe(0);
  });

  it("verwijdert het eigen account (recht op vergetelheid)", async () => {
    const del = await ctx.http.inject({ method: "DELETE", url: "/v1/me", headers: await bearer(PARENT) });
    expect(del.statusCode).toBe(204);
    const left = await withTenant(db, TENANT, (tx) => tx.select().from(users).where(eq(users.zitadelSub, PARENT.sub)));
    expect(left).toHaveLength(0);
    const audit = await withTenant(db, TENANT, (tx) => tx.select().from(auditEvents).where(eq(auditEvents.action, "identity.user.deleted")));
    expect(audit).toHaveLength(1);
    expect(JSON.stringify(audit[0])).not.toContain("ouder@example.test");
  });
});

describe("tenants", () => {
  it("gebruikers van een andere tenant zijn onzichtbaar", async () => {
    const other = "0192f6a0-0000-7000-8000-000000000999";
    const rows = await withTenant(db, other, (tx) => tx.select().from(users));
    expect(rows).toHaveLength(0);
  });
});
