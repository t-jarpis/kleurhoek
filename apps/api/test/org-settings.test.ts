import { startMockOidc, type MockUser } from "@t-jarpis/auth/testing";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { ADMIN_ORG, AUDIENCE, createTestApp, SITE_ORG } from "./app";

const OWNER: MockUser = { sub: "z-eigenaar", name: "Thijs", email: "thijs@example.test", organizationId: ADMIN_ORG };
const TEACHER: MockUser = { sub: "z-juf", name: "Juf Anna", email: "Anna@School.example", organizationId: SITE_ORG };
const PARENT: MockUser = { sub: "z-ouder2", name: "Ouder", email: "ouder2@example.test", organizationId: SITE_ORG };

let op: Awaited<ReturnType<typeof startMockOidc>>;
let ctx: Awaited<ReturnType<typeof createTestApp>>;
const bearer = async (user: MockUser) => ({ authorization: `Bearer ${await op.accessToken(300, user)}` });
const call = async (user: MockUser, method: "GET" | "POST" | "PUT" | "DELETE", url: string, payload?: unknown) =>
  ctx.http.inject({ method, url, headers: await bearer(user), ...(payload !== undefined ? { payload: payload as object } : {}) });
const plates = async (org: string) => (await ctx.http.inject({ method: "GET", url: `/v1/markets/nl-NL/plates?org=${org}` })).json().items as { slug: string; goals: string[] }[];

beforeAll(async () => {
  op = await startMockOidc({ clientId: "admin", audience: AUDIENCE, user: OWNER });
  ctx = await createTestApp({ oidc: { issuer: op.issuer, bootstrap: [OWNER.sub] } });
});
afterAll(async () => { await ctx.app.close(); await op.close(); });

describe("instellingen per organisatie (ADR 0036)", () => {
  let picks: string[] = [];

  it("geeft elke plaat leerdoelen en kent collecties", async () => {
    const all = await plates("kleurhoek");
    expect(all.every((p) => p.goals.length > 0)).toBe(true);
    const list = (await call(OWNER, "GET", "/v1/admin/collections")).json();
    expect(list.goals.map((g: { slug: string }) => g.slug)).toContain("rekenen");
    picks = list.plates.filter((p: { goals: string[] }) => p.goals.includes("rekenen")).slice(0, 3).map((p: { slug: string }) => p.slug);
    expect(picks.length).toBe(3);
    expect((await call(OWNER, "PUT", "/v1/admin/collections/rekenen-start", { names: { nl: "" }, plates: picks })).statusCode).toBe(400);
    expect((await call(OWNER, "PUT", "/v1/admin/collections/rekenen-start", { names: { nl: "Rekenen" }, plates: ["bestaat-niet"] })).statusCode).toBe(400);
    const saved = await call(OWNER, "PUT", "/v1/admin/collections/rekenen-start", { names: { nl: "Rekenen voor beginners", de: "Rechnen für Anfänger" }, plates: [...picks, picks[0]] });
    expect(saved.statusCode).toBe(200);
    expect(saved.json().plates).toEqual(picks);
  });

  it("beperkt een school tot een collectie en zet het filter Leerdoel aan", async () => {
    const r = await call(OWNER, "POST", "/v1/admin/organizations", { slug: "obs-de-linde", name: "OBS De Linde", kind: "school", offer: { collections: ["rekenen-start"] } });
    expect(r.statusCode).toBe(201);
    expect(r.json().features.learningFilters).toBe(true);
    expect((await plates("obs-de-linde")).map((p) => p.slug).sort()).toEqual([...picks].sort());
    const tax = (await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/taxonomy?org=obs-de-linde" })).json();
    expect(tax.learningFilters).toBe(true);
    expect(tax.goals).toContainEqual({ slug: "rekenen", name: "Rekenen en getallen" });
    expect((await call(OWNER, "PUT", "/v1/admin/organizations/obs-de-linde", { offer: { collections: ["onbekend"] } })).statusCode).toBe(400);
    // In gebruik: niet weg te halen.
    expect((await call(OWNER, "DELETE", "/v1/admin/collections/rekenen-start")).statusCode).toBe(409);
  });

  it("laat een leerkracht het aanbod van de eigen school bijstellen, en niets anders", async () => {
    expect((await call(TEACHER, "GET", "/v1/me")).statusCode).toBe(200);
    expect((await call(OWNER, "POST", "/v1/admin/organizations/obs-de-linde/managers", { email: "niemand@example.test" })).statusCode).toBe(400);
    expect((await call(OWNER, "POST", "/v1/admin/organizations/kleurhoek/managers", { email: "anna@school.example" })).statusCode).toBe(400);
    const add = await call(OWNER, "POST", "/v1/admin/organizations/obs-de-linde/managers", { email: "anna@school.example" });
    expect(add.json().managers).toMatchObject([{ displayName: "Juf Anna" }]);

    expect((await call(TEACHER, "GET", "/v1/me/organizations")).json().organizations).toEqual([{ slug: "obs-de-linde", name: "OBS De Linde", kind: "school" }]);
    const mine = (await call(TEACHER, "GET", "/v1/me/organizations/obs-de-linde?language=de")).json();
    expect(mine.collections.find((c: { slug: string }) => c.slug === "rekenen-start").name).toBe("Rechnen für Anfänger");
    expect(mine.plates.length).toBeGreaterThan(picks.length);

    const save = await call(TEACHER, "PUT", "/v1/me/organizations/obs-de-linde", { collections: ["rekenen-start"], goals: null, excluded: [picks[0], "bestaat-niet"] });
    expect(save.json().offer.excluded).toEqual([picks[0]]);
    expect((await plates("obs-de-linde")).map((p) => p.slug)).not.toContain(picks[0]);
    // Markten of huisstijl kan de leerkracht niet aanpassen; andere scholen ook niet.
    expect((await call(TEACHER, "PUT", "/v1/me/organizations/obs-de-linde", { collections: null, goals: null, excluded: [], offer: { markets: [] } })).statusCode).toBe(400);
    expect((await call(PARENT, "GET", "/v1/me/organizations/obs-de-linde")).statusCode).toBe(404);
    expect((await call(TEACHER, "GET", "/v1/me/organizations/kleurhoek")).statusCode).toBe(404);
    expect((await call(OWNER, "GET", "/v1/me/organizations")).statusCode).toBe(401);
  });

  it("filtert op leerdoelen en vergeet de beheerder als het account weg is", async () => {
    await call(TEACHER, "PUT", "/v1/me/organizations/obs-de-linde", { collections: null, goals: ["taal"], excluded: [] });
    const list = await plates("obs-de-linde");
    expect(list.length).toBeGreaterThan(0);
    expect(list.every((p) => p.goals.includes("taal"))).toBe(true);
    expect((await call(TEACHER, "DELETE", "/v1/me")).statusCode).toBe(204);
    expect((await call(OWNER, "GET", "/v1/admin/organizations/obs-de-linde/managers")).json().managers).toEqual([]);
  });
});
