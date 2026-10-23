import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { createTestApp, INGEST_KEY } from "./app";

const PNG = Buffer.from("89504e470d0a1a0a0000000d4948445200000001000000010806000000", "hex");

describe("organisaties (whitelabel)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  beforeAll(async () => { process.env.ORG_HOST_PATTERN = "{slug}-dev.kleurhoek.nl"; ctx = await createTestApp(); });
  afterAll(async () => { delete process.env.ORG_HOST_PATTERN; await ctx.app.close(); });

  const admin = (method: "GET" | "POST" | "PUT" | "DELETE", url: string, payload?: unknown, auth = "Bearer beheerder") =>
    ctx.http.inject({ method, url, ...(payload ? { payload: payload as object } : {}), headers: { authorization: auth } });
  const resolve = (host: string) => ctx.http.inject({ method: "GET", url: `/v1/internal/organizations/resolve?host=${host}`, headers: { "x-ingest-key": INGEST_KEY } });

  it("heeft Kleurhoek zelf als standaard, ook voor onbekende hosts", async () => {
    const r = await resolve("dev.kleurhoek.nl");
    expect(r.json()).toMatchObject({ slug: "kleurhoek", isDefault: true, features: { shop: true } });
    expect((await resolve("onbekend.example.nl")).json().slug).toBe("kleurhoek");
    expect((await ctx.http.inject({ method: "GET", url: "/v1/internal/organizations/resolve?host=x.nl" })).statusCode).toBe(401);
  });

  it("geeft het beheer de keuzes: thema's, lettertypen en wat er in het aanbod kan", async () => {
    const r = (await admin("GET", "/v1/admin/organizations")).json();
    expect(r.fonts.map((f: { id: string }) => f.id)).toEqual(expect.arrayContaining(["manrope", "nunito"]));
    expect(r.options.categories.length).toBeGreaterThan(3);
    expect(r.options.categories[0]).toMatchObject({ slug: expect.any(String), name: expect.any(String) });
    expect(r.options.kinds.map((k: { slug: string }) => k.slug)).toEqual(["kleurplaat", "knutselen"]);
    expect(r.options.markets).toContain("nl-nl");
    expect(r.organizations[0].offer).toHaveProperty("categories");
  });

  it("maakt een school aan met eigen huisstijl, aanbod en zonder winkel", async () => {
    expect((await admin("POST", "/v1/admin/organizations", { slug: "admin", name: "Fout", kind: "school" })).statusCode).toBe(400);
    expect((await admin("POST", "/v1/admin/organizations", { slug: "school-dev", name: "Fout", kind: "school" })).statusCode).toBe(400);
    expect((await admin("POST", "/v1/admin/organizations", { slug: "de-regenboog", name: "De Regenboog", kind: "school" }, "Bearer analist")).statusCode).toBe(403);
    const r = await admin("POST", "/v1/admin/organizations", {
      slug: "de-regenboog", name: "Basisschool De Regenboog", kind: "school",
      brand: { font: "nunito", colors: { primary: "#1f5f8b" }, wordmark: "regenboog" },
      offer: { categories: ["dieren"], kinds: ["kleurplaat"] },
    });
    expect(r.statusCode).toBe(201);
    expect(r.json()).toMatchObject({ slug: "de-regenboog", features: { shop: false }, brand: { font: "nunito", colors: { primary: "#1f5f8b" } } });
    expect((await admin("POST", "/v1/admin/organizations", { slug: "de-regenboog", name: "Dubbel", kind: "school" })).statusCode).toBe(409);
  });

  it("weigert kleuren met te weinig contrast en onbekende lettertypen", async () => {
    const r = await admin("PUT", "/v1/admin/organizations/de-regenboog", { brand: { colors: { primary: "#ffee00" } } });
    expect(r.statusCode).toBe(400);
    expect(r.json().message).toMatch(/te licht/);
    expect((await admin("PUT", "/v1/admin/organizations/de-regenboog", { brand: { font: "comic-sans" } })).statusCode).toBe(400);
    expect((await admin("PUT", "/v1/admin/organizations/de-regenboog", { brand: { colors: { accent: "#9db4ff" } } })).json().message).toMatch(/Accentkleur/);
  });

  it("vindt de school via het subdomein en een eigen domein", async () => {
    expect((await resolve("de-regenboog-dev.kleurhoek.nl")).json()).toMatchObject({ slug: "de-regenboog", name: "Basisschool De Regenboog" });
    await admin("PUT", "/v1/admin/organizations/de-regenboog", { hosts: ["platen.deregenboog.nl"] });
    expect((await resolve("platen.deregenboog.nl")).json().slug).toBe("de-regenboog");
    // Een domein hoort bij één organisatie.
    await admin("POST", "/v1/admin/organizations", { slug: "opvang-zon", name: "Opvang Zon", kind: "opvang" });
    expect((await admin("PUT", "/v1/admin/organizations/opvang-zon", { hosts: ["platen.deregenboog.nl"] })).statusCode).toBe(400);
  });

  it("toont alleen het aanbod van de school, zonder winkel", async () => {
    const all = (await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates" })).json().items;
    const school = (await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates?org=de-regenboog" })).json().items;
    expect(school.length).toBeGreaterThan(0);
    expect(school.length).toBeLessThan(all.length);
    expect(school.every((p: { category: string; kind: string }) => p.category === "dieren" && p.kind === "kleurplaat")).toBe(true);
    const tax = (await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/taxonomy?org=de-regenboog" })).json();
    expect(tax.categories.map((c: { slug: string }) => c.slug)).toEqual(["dieren"]);
    const knutsel = await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates/lampion-maken?org=de-regenboog" });
    expect(knutsel.statusCode).toBe(404);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates?org=bestaat-niet" })).statusCode).toBe(404);
  });

  it("slaat een logo op en levert het per versie, met een zandbak voor SVG", async () => {
    const r = await admin("PUT", "/v1/admin/organizations/de-regenboog/logo", { contentType: "image/png", data: PNG.toString("base64") });
    expect(r.statusCode).toBe(200);
    const logo = (await resolve("de-regenboog-dev.kleurhoek.nl")).json().logo as string;
    expect(logo).toMatch(/^\/v1\/organizations\/de-regenboog\/logo\/[0-9a-f]{16}$/);
    const img = await ctx.http.inject({ method: "GET", url: logo });
    expect(img.statusCode).toBe(200);
    expect(img.headers["content-type"]).toBe("image/png");
    expect(img.headers["content-security-policy"]).toMatch(/sandbox/);
    const evil = Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"></svg>').toString("base64");
    expect((await admin("PUT", "/v1/admin/organizations/de-regenboog/logo", { contentType: "image/svg+xml", data: evil })).statusCode).toBe(400);
  });

  it("legt wijzigingen vast en laat Kleurhoek zelf niet uitzetten", async () => {
    expect((await admin("PUT", "/v1/admin/organizations/kleurhoek", { active: false })).statusCode).toBe(400);
    const list = (await admin("GET", "/v1/admin/organizations")).json();
    expect(list.fonts.map((f: { id: string }) => f.id)).toContain("nunito");
    expect(list.organizations.find((o: { slug: string }) => o.slug === "de-regenboog").subdomain).toBe("de-regenboog-dev.kleurhoek.nl");
  });
});
