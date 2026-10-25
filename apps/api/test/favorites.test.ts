import { startMockOidc, type MockUser } from "@t-jarpis/auth/testing";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { ADMIN_ORG, AUDIENCE, createTestApp, SITE_ORG } from "./app";

const OWNER: MockUser = { sub: "z-fav-eigenaar", name: "Thijs", email: "thijs@example.test", organizationId: ADMIN_ORG };
const PARENT: MockUser = { sub: "z-fav-ouder", name: "Ouder", email: "ouder@example.test", organizationId: SITE_ORG };
const OTHER: MockUser = { sub: "z-fav-ander", name: "Ander", email: "ander@example.test", organizationId: SITE_ORG };

let op: Awaited<ReturnType<typeof startMockOidc>>;
let ctx: Awaited<ReturnType<typeof createTestApp>>;
const call = async (user: MockUser, method: "GET" | "POST" | "PUT" | "DELETE", url: string, payload?: unknown) =>
  ctx.http.inject({ method, url, headers: { authorization: `Bearer ${await op.accessToken(300, user)}` }, ...(payload !== undefined ? { payload: payload as object } : {}) });

beforeAll(async () => {
  op = await startMockOidc({ clientId: "admin", audience: AUDIENCE, user: OWNER });
  ctx = await createTestApp({ oidc: { issuer: op.issuer, bootstrap: [OWNER.sub] } });
});
afterAll(async () => { await ctx.app.close(); await op.close(); });

describe("favorieten (ADR 0039)", () => {
  let slugs: string[] = [];
  it("bewaart favorieten per account, alleen bestaande platen, zonder dubbele", async () => {
    slugs = (await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates" })).json().items.slice(0, 3).map((p: { slug: string }) => p.slug);
    expect((await call(PARENT, "GET", "/v1/me/favorites")).json()).toEqual({ slugs: [] });
    // Na inloggen: de favorieten van het apparaat erbij.
    expect((await call(PARENT, "POST", "/v1/me/favorites", { slugs: [slugs[0], slugs[1], "bestaat-niet", slugs[0]] })).json()).toEqual({ slugs: [slugs[0], slugs[1]] });
    expect((await call(PARENT, "PUT", `/v1/me/favorites/${slugs[2]}`)).json().slugs).toEqual(slugs);
    expect((await call(PARENT, "PUT", `/v1/me/favorites/${slugs[2]}`)).json().slugs).toEqual(slugs);
    expect((await call(PARENT, "DELETE", `/v1/me/favorites/${slugs[1]}`)).json().slugs).toEqual([slugs[0], slugs[2]]);
    expect((await call(OTHER, "GET", "/v1/me/favorites")).json().slugs).toEqual([]);
  });
  it("is alleen voor websiteaccounts en verdwijnt met het account", async () => {
    expect((await call(OWNER, "GET", "/v1/me/favorites")).statusCode).toBe(401);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/me/favorites" })).statusCode).toBe(401);
    expect((await call(PARENT, "DELETE", "/v1/me")).statusCode).toBe(204);
    expect((await call(PARENT, "GET", "/v1/me/favorites")).json().slugs).toEqual([]);
  });
});
