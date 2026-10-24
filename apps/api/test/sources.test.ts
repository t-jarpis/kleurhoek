import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { applyCheck, SourcesService } from "../src/modules/sources/sources.service";
import { checkSource, fingerprint, isPublicAddress, robotsAllows, siteOf, type CheckDeps } from "../src/modules/sources/source-check";
import { createTestApp } from "./app";

/** Nep-internet: per URL een antwoord. Zo praten de tests nooit met echte sites. */
const pages = new Map<string, { status: number; body?: string; type?: string; location?: string }>();
const dns = new Map<string, string[]>([["www.maker.example", ["93.184.216.34"]], ["maker.example", ["93.184.216.34"]], ["intern.example", ["10.0.0.5"]], ["ander.example", ["93.184.216.35"]]]);
const fake: CheckDeps = {
  resolve: async (host) => dns.get(host) ?? [],
  fetch: (async (input: URL | string) => {
    const p = pages.get(String(input)) ?? { status: 404, body: "" };
    return new Response(p.body ?? "", { status: p.status, headers: { "content-type": p.type ?? "text/html; charset=utf-8", ...(p.location ? { location: p.location } : {}) } });
  }) as typeof fetch,
};
const PAGE = "https://www.maker.example/kleurplaten";
const html = (text: string) => `<html><head><title>Kleurplaten | Maker</title><script>var t=${Date.now()}</script></head><body><h1>${text}</h1><img src="x.png"></body></html>`;

let ctx: Awaited<ReturnType<typeof createTestApp>>;
const admin = { authorization: "Bearer beheerder" };
const call = (method: "GET" | "POST" | "PUT" | "DELETE", url: string, payload?: object) => ctx.http.inject({ method, url, headers: admin, ...(payload ? { payload } : {}) });

beforeAll(async () => { ctx = await createTestApp(); ctx.app.get(SourcesService).deps = fake; });
afterAll(async () => { await ctx.app.close(); });

describe("controle-hulpjes", () => {
  it("publieke en privé-adressen", () => {
    for (const ip of ["10.1.2.3", "127.0.0.1", "192.168.1.1", "172.20.0.1", "169.254.169.254", "100.64.0.1", "::1", "fd00::1", "fe80::1", "::ffff:10.0.0.1"]) expect(isPublicAddress(ip), ip).toBe(false);
    for (const ip of ["93.184.216.34", "1.1.1.1", "2606:4700::1111"]) expect(isPublicAddress(ip), ip).toBe(true);
  });
  it("robots.txt: eigen groep gaat voor *, langste regel wint", () => {
    const r = "User-agent: *\nDisallow: /\n\nUser-agent: KleurhoekLinkCheck\nDisallow: /prive\nAllow: /prive/kleurplaten\n";
    expect(robotsAllows(r, "/kleurplaten")).toBe(true);
    expect(robotsAllows(r, "/prive/geheim")).toBe(false);
    expect(robotsAllows(r, "/prive/kleurplaten/x")).toBe(true);
    expect(robotsAllows("User-agent: *\nDisallow: /", "/x", "AndereBot")).toBe(false);
    expect(robotsAllows("User-agent: *\nDisallow:", "/x")).toBe(true);
    expect(robotsAllows("", "/x")).toBe(true);
  });
  it("vingerafdruk negeert scripts en tags, en geeft de titel", () => {
    const a = fingerprint(html("Kleurplaten")), b = fingerprint(html("Kleurplaten"));
    expect(a.hash).toBe(b.hash);
    expect(a.title).toBe("Kleurplaten | Maker");
    expect(fingerprint(html("Andere tekst")).hash).not.toBe(a.hash);
  });
  it("hetzelfde domein met of zonder www", () => {
    expect(siteOf("www.efteling.com")).toBe(siteOf("efteling.com"));
    expect(siteOf("shop.bbc.co.uk")).toBe("bbc.co.uk");
  });
  it("na twee keer 404 of drie fouten offline; veranderde pagina wordt gemarkeerd", () => {
    const base = { failCount: 0, baselineHash: "a", health: "ok" as const, changed: false };
    const gone = { outcome: "gone" as const, httpStatus: 404, finalUrl: null, robotsAllowed: true, contentHash: null, pageTitle: null, note: null };
    expect(applyCheck(base, gone)).toMatchObject({ health: "ok", failCount: 1 });
    expect(applyCheck({ ...base, failCount: 1 }, gone)).toMatchObject({ health: "broken", failCount: 2 });
    expect(applyCheck({ ...base, failCount: 2 }, { ...gone, outcome: "error" })).toMatchObject({ health: "broken" });
    expect(applyCheck(base, { ...gone, outcome: "ok", contentHash: "b" })).toMatchObject({ health: "ok", failCount: 0, changed: true });
  });
  it("praat nooit met een privé-adres of zonder https", async () => {
    expect((await checkSource("https://intern.example/x", fake)).outcome).toBe("blocked");
    expect((await checkSource("http://www.maker.example/x", fake)).outcome).toBe("blocked");
    expect((await checkSource("https://10.0.0.1/x", fake)).outcome).toBe("blocked");
    pages.set("https://www.maker.example/doorsturen", { status: 302, location: "https://intern.example/geheim" });
    expect((await checkSource("https://www.maker.example/doorsturen", fake)).outcome).toBe("blocked");
  });
  it("doorverwijzing naar een ander domein telt als verdwenen", async () => {
    pages.set("https://www.maker.example/oud", { status: 301, location: "https://ander.example/" });
    pages.set("https://ander.example/", { status: 200, body: html("ander") });
    expect((await checkSource("https://www.maker.example/oud", fake)).outcome).toBe("gone");
  });
});

describe("bronnengids", () => {
  it("thema aanmaken, bron toevoegen (direct gecontroleerd), goedkeuren en publiceren", async () => {
    pages.set(PAGE, { status: 200, body: html("Kleurplaten van de maker") });
    pages.set("https://www.maker.example/robots.txt", { status: 200, body: "User-agent: *\nAllow: /", type: "text/plain" });
    expect((await call("POST", "/v1/admin/sources/themes", { slug: "pretpark", name: "Het pretpark", description: "Kleurplaten van het pretpark, bij de maker zelf.", makerName: "Pretpark BV", makerUrl: "https://www.maker.example/" })).statusCode).toBe(201);

    // Publiceren zonder werkende bron mag niet.
    expect((await call("PUT", "/v1/admin/sources/themes/pretpark", { status: "published" })).statusCode).toBe(400);

    const added = await call("POST", "/v1/admin/sources/themes/pretpark/sources", { url: PAGE, title: "Kleurplaten bij het pretpark", basis: "link" });
    expect(added.statusCode).toBe(201);
    const s = added.json();
    expect(s).toMatchObject({ status: "pending", health: "ok", robotsAllowed: true, pageTitle: "Kleurplaten | Maker", live: false });

    // Nog niet goedgekeurd: niet op de site.
    await call("PUT", "/v1/admin/sources/themes/pretpark", { status: "draft" });
    expect((await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/themes" })).json().themes).toEqual([]);

    expect((await call("POST", `/v1/admin/sources/items/${s.id}/approve`)).json()).toMatchObject({ status: "approved", live: true });
    expect((await call("PUT", "/v1/admin/sources/themes/pretpark", { status: "published" })).statusCode).toBe(200);

    const pub = (await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/themes" })).json();
    expect(pub.themes).toEqual([{ slug: "pretpark", name: "Het pretpark", description: "Kleurplaten van het pretpark, bij de maker zelf.", makerName: "Pretpark BV", sourceCount: 1 }]);
    const detail = (await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/themes/pretpark" })).json();
    expect(detail.sources).toEqual([{ title: "Kleurplaten bij het pretpark", description: null, url: PAGE, host: "maker.example", basis: "link" }]);
    // Nooit beeld of inhoud van de maker.
    expect(JSON.stringify(detail)).not.toMatch(/png|<img|Kleurplaten \| Maker/);
  });

  it("licentie vraagt om een notitie", async () => {
    const r = await call("POST", "/v1/admin/sources/themes/pretpark/sources", { url: "https://www.maker.example/meer", title: "Meer", basis: "license" });
    expect(r.statusCode).toBe(400);
  });

  it("een verdwenen bron gaat vanzelf offline en komt in de lijst nakijken", async () => {
    const svc = ctx.app.get(SourcesService);
    const theme = (await call("GET", "/v1/admin/sources/themes/pretpark")).json();
    const id = theme.sources[0].id as string;
    pages.set(PAGE, { status: 404 });
    await svc.check(id);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/themes" })).json().themes).toHaveLength(1);
    await svc.check(id);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/themes" })).json().themes).toEqual([]);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/themes/pretpark" })).statusCode).toBe(404);
    const review = (await call("GET", "/v1/admin/sources/review")).json().sources;
    expect(review.find((s: { id: string }) => s.id === id)).toMatchObject({ health: "broken", checkNote: expect.stringContaining("404") });

    // Terug: na een goede controle weer online.
    pages.set(PAGE, { status: 200, body: html("Kleurplaten van de maker") });
    await svc.check(id);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/themes" })).json().themes).toHaveLength(1);
  });

  it("veranderde pagina blijft online maar wordt gemarkeerd", async () => {
    const svc = ctx.app.get(SourcesService);
    const id = (await call("GET", "/v1/admin/sources/themes/pretpark")).json().sources[0].id as string;
    pages.set(PAGE, { status: 200, body: html("Helemaal nieuwe pagina") });
    await svc.check(id);
    const s = (await call("GET", "/v1/admin/sources/themes/pretpark")).json().sources[0];
    expect(s).toMatchObject({ changed: true, live: true });
  });

  it("alleen met de juiste rechten", async () => {
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/sources/themes", headers: { authorization: "Bearer analist" } })).statusCode).toBe(403);
  });
});
