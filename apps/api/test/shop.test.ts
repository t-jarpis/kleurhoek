import * as source from "@kleurhoek/catalog-data";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { seed } from "../src/db/seed";
import { DB, type Database } from "../src/db/database";
import { withTenant } from "../src/db/tenant";
import { AnalyticsService, isCandidate } from "../src/modules/analytics/analytics.service";
import { auditEvents } from "../src/modules/identity/identity.schema";
import { asinFrom, buildLink, checkProductUrl, normalizeProductUrl, ShopService } from "../src/modules/shop/shop.service";
import { createTestApp, INGEST_KEY, TENANT } from "./app";

let ctx: Awaited<ReturnType<typeof createTestApp>>;
const admin = { authorization: "Bearer beheerder" };
const BOL_URL = "https://www.bol.com/nl/nl/p/kinderschaar-met-ronde-punt/9200000000001/";

beforeAll(async () => { ctx = await createTestApp(); });
afterAll(async () => { await ctx.app.close(); });

describe("doorverwijzingen bouwen", () => {
  it("vult het bol-sjabloon met site-ID, gecodeerde URL en bron", () => {
    const link = buildLink("https://partner.bol.com/click/click?p=2&t=url&s={siteId}&url={url}&f=TXL&name={subId}", { siteId: "12345" }, BOL_URL, "kleurhoek-lampion-maken");
    const u = new URL(link!);
    expect(u.host).toBe("partner.bol.com");
    expect(u.searchParams.get("s")).toBe("12345");
    expect(u.searchParams.get("url")).toBe(BOL_URL);
    expect(u.searchParams.get("name")).toBe("kleurhoek-lampion-maken");
  });
  it("geeft niets als een instelling ontbreekt of het resultaat geen https is", () => {
    expect(buildLink("https://partner.bol.com/click?s={siteId}&url={url}", {}, BOL_URL, "x")).toBeNull();
    expect(buildLink("{url}", {}, "javascript:alert(1)", "x")).toBeNull();
    expect(buildLink("{url}", {}, "https://winkel.example/schaar", "x")).toBe("https://winkel.example/schaar");
  });
  it("plakt bij Amazon de tag achter de productpagina", () => {
    expect(buildLink("{url}?tag={tag}", { tag: "kleurhoek-21" }, "https://www.amazon.de/dp/B000TEST01", "x")).toBe("https://www.amazon.de/dp/B000TEST01?tag=kleurhoek-21");
    expect(buildLink("{url}?tag={tag}", { tag: "" }, "https://www.amazon.de/dp/B000TEST01", "x")).toBeNull();
    // Productlink met eigen parameters (bijv. variant ?th=1) of al een (andere) tag: één "?", onze tag.
    expect(buildLink("{url}?tag={tag}", { tag: "kleurhoek-21" }, "https://www.amazon.nl/dp/B000TEST01?th=1&psc=1", "x")).toBe("https://www.amazon.nl/dp/B000TEST01?th=1&psc=1&tag=kleurhoek-21");
    expect(buildLink("{url}?tag={tag}", { tag: "kleurhoek-21" }, "https://www.amazon.nl/dp/B000TEST01?tag=iemand-anders-21", "x")).toBe("https://www.amazon.nl/dp/B000TEST01?tag=kleurhoek-21");
    expect(buildLink("{url}?tag={tag}", { tag: "kleurhoek-21" }, "javascript:alert(1)", "x")).toBeNull();
  });
  it("maakt Amazon-links netjes, ook korte deellinks uit de app", async () => {
    const follow = async (u: string) => (u === "https://amzn.eu/d/abc123" ? "https://www.amazon.nl/-/nl/Faber-Castell-kleurpotloden/dp/B00ABCDE12/ref=sr_1_3?keywords=x&th=1" : null);
    expect(await normalizeProductUrl("https://amzn.eu/d/abc123", follow)).toBe("https://www.amazon.nl/dp/B00ABCDE12");
    expect(await normalizeProductUrl("https://amazon.nl/dp/b00abcde12?tag=iemand-21", follow)).toBe("https://www.amazon.nl/dp/B00ABCDE12");
    expect(await normalizeProductUrl("https://www.amazon.de/gp/product/B00ABCDE12/ref=x", follow)).toBe("https://www.amazon.de/dp/B00ABCDE12");
    expect(await normalizeProductUrl("https://bol.com/nl/nl/p/schaar/123/", follow)).toBe("https://www.bol.com/nl/nl/p/schaar/123/");
    expect(await normalizeProductUrl("https://amzn.eu/d/onbekend", follow)).toBe("https://amzn.eu/d/onbekend");
    expect(await normalizeProductUrl("https://winkel.example/x?y=1", follow)).toBe("https://winkel.example/x?y=1");
  });

  it("accepteert alleen https-producten op de domeinen van de partner", () => {
    expect(checkProductUrl(BOL_URL, ["www.bol.com"])).toBeNull();
    expect(checkProductUrl("https://evil.example/x", ["www.bol.com"])).toMatch(/hoort niet/);
    expect(checkProductUrl("http://www.bol.com/x", ["www.bol.com"])).toMatch(/https/);
    expect(checkProductUrl("https://user:pw@www.bol.com/x", ["www.bol.com"])).toMatch(/https/);
  });
  it("noemt een product kandidaat bij genoeg bezoekers en geen daling", () => {
    expect(isCandidate({ visitors: 25, growth: 0.1 })).toBe(true);
    expect(isCandidate({ visitors: 25, growth: -0.3 })).toBe(false);
    expect(isCandidate({ visitors: 5, growth: null })).toBe(false);
  });
});

describe("knutselwerk in de catalogus", () => {
  it("geeft de lampion als bouwplaat met stappen, papier en materialen", async () => {
    const r = await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates/lampion-maken" });
    expect(r.statusCode).toBe(200);
    const p = r.json();
    expect(p).toMatchObject({ kind: "bouwplaat", height: 270, minutes: 30, adultHelp: true, paperGsm: 160 });
    expect(p.steps.length).toBeGreaterThan(3);
    expect(p.materials.map((m: { slug: string }) => m.slug)).toEqual(["kleurpotloden", "kinderschaar", "lijmstift", "stevig-papier", "led-lampionstokje"]);
    expect(p.materials.every((m: { product: unknown }) => m.product === null)).toBe(true);
  });
  it("filtert op soort", async () => {
    const r = await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates?kind=knutselen" });
    const crafts = source.plates().filter((p) => source.KIND_GROUPS[p.kind] === "knutselen").map((p) => p.slug).sort();
    expect(r.json().items.map((i: { slug: string }) => i.slug).sort()).toEqual(crafts);
    expect(crafts).toContain("lampion-maken");
    const learn = await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates?kind=leren" });
    expect(learn.json().items.map((i: { slug: string }) => i.slug).sort()).toEqual(source.plates().filter((p) => ["spel", "werkblad"].includes(p.kind)).map((p) => p.slug).sort());
  });
  it("de seed is aanvullend en draait veilig opnieuw", async () => {
    const db = ctx.app.get<Database>(DB);
    expect(await seed(db, TENANT)).toEqual({ plates: 0 });
  });
  it("de SVG van een knutselplaat krijgt de stijl voor knip- en vouwlijnen", async () => {
    const r = await ctx.http.inject({ method: "GET", url: "/v1/assets/plates/lampion-maken/1.svg" });
    expect(r.body).toContain(".cut{");
    expect(r.body).toContain('viewBox="0 0 200 270"');
  });
});

describe("winkel", () => {
  it("bol staat uit tot het site-ID is ingevuld", async () => {
    const r = await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/partners/bol", headers: admin, payload: { enabled: true } });
    expect(r.statusCode).toBe(400);
    expect(r.json().message).toMatch(/instellingen/);
  });

  it("weigert een sjabloon zonder https of zonder {url}", async () => {
    for (const linkTemplate of ["http://partner.bol.com/?u={url}", "https://partner.bol.com/zonder"]) {
      const r = await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/partners/bol", headers: admin, payload: { linkTemplate } });
      expect(r.statusCode).toBe(400);
    }
  });

  it("zonder winkelrecht geen toegang", async () => {
    // De nep-analist heeft geen shop.read (zie test/app.ts).
    const r = await ctx.http.inject({ method: "GET", url: "/v1/admin/shop/partners", headers: { authorization: "Bearer analist" } });
    expect(r.statusCode).toBe(403);
  });

  it("koppelt bol, voegt een product toe en toont het bij de lampion", async () => {
    const partner = await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/partners/bol", headers: admin, payload: { enabled: true, settings: { siteId: "12345" } } });
    expect(partner.statusCode).toBe(200);

    const bad = await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/products/schaar", headers: admin, payload: { partner: "bol", url: "https://evil.example/schaar", enabled: true, markets: ["nl-NL"], name: "Schaar", materials: ["kinderschaar"] } });
    expect(bad.statusCode).toBe(400);

    const saved = await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/products/kinderschaar-rond", headers: admin, payload: {
      partner: "bol", url: BOL_URL, enabled: true, markets: ["nl-NL"], name: "Kinderschaar met ronde punt", note: "Voor kleine handen", priceHint: "ca. € 4", materials: ["kinderschaar"],
    } });
    expect(saved.statusCode).toBe(200);

    const list = (await ctx.http.inject({ method: "GET", url: "/v1/admin/shop/products", headers: admin })).json();
    expect(list.products[0]).toMatchObject({ slug: "kinderschaar-rond", name: "Kinderschaar met ronde punt", materials: ["kinderschaar"] });
    expect(list.materials.find((m: { slug: string }) => m.slug === "kinderschaar").name).toBe("Kinderschaar");

    const plate = (await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates/lampion-maken" })).json();
    const scissors = plate.materials.find((m: { slug: string }) => m.slug === "kinderschaar");
    expect(scissors.product).toMatchObject({ slug: "kinderschaar-rond", name: "Kinderschaar met ronde punt", partner: "bol", priceHint: "ca. € 4" });

    const link = await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/products/kinderschaar-rond/link?plate=lampion-maken" });
    expect(link.headers["cache-control"]).toBe("no-store");
    const target = new URL(link.json().url);
    expect(target.host).toBe("partner.bol.com");
    expect(target.searchParams.get("name")).toBe("kleurhoek-lampion-maken");

    const audit = await withTenant(ctx.app.get<Database>(DB), TENANT, (tx) => tx.select().from(auditEvents));
    expect(audit.map((a) => a.action)).toEqual(expect.arrayContaining(["shop.partner.updated", "shop.product.created"]));
  });

  it("geen doorverwijzing als de partner uitstaat of het product onbekend is", async () => {
    expect((await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/products/bestaat-niet/link" })).statusCode).toBe(404);
    await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/partners/bol", headers: admin, payload: { enabled: false } });
    expect((await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/products/kinderschaar-rond/link" })).statusCode).toBe(404);
    const plate = (await ctx.http.inject({ method: "GET", url: "/v1/markets/nl-NL/plates/lampion-maken" })).json();
    expect(plate.materials.every((m: { product: unknown }) => m.product === null)).toBe(true);
    await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/partners/bol", headers: admin, payload: { enabled: true } });
  });

  it("telt doorkliks per product en plaat, en berekent de klikratio", async () => {
    const day = "2026-10-20";
    const ev = (type: string, extra: Record<string, string> = {}, visitor = "v".repeat(20)) =>
      ({ type, market: "nl-NL", country: "NL", device: "desktop", visitorHash: visitor, occurredAt: `${day}T10:00:00Z`, plate: "lampion-maken", ...extra });
    const batch = [
      ...Array.from({ length: 10 }, (_, i) => ev("materials_view", {}, `bezoeker-${String(i).padStart(10, "0")}`)),
      ev("product_click", { product: "kinderschaar-rond" }, "bezoeker-0000000001"),
      ev("product_click", { product: "kinderschaar-rond" }, "bezoeker-0000000002"),
      ev("product_click", { product: "kinderschaar-rond" }, "bezoeker-0000000002"),
    ];
    const r = await ctx.http.inject({ method: "POST", url: "/v1/internal/events", headers: { "x-ingest-key": INGEST_KEY }, payload: batch });
    expect(r.statusCode).toBe(202);
    await ctx.app.get(AnalyticsService).aggregateDay(TENANT, day);

    const s = (await ctx.http.inject({ method: "GET", url: `/v1/admin/analytics/shop?from=${day}&to=${day}`, headers: admin })).json();
    expect(s.products).toEqual([expect.objectContaining({ product: "kinderschaar-rond", clicks: 3, visitors: 2, topPlates: ["lampion-maken"] })]);
    expect(s.plates[0]).toMatchObject({ plate: "lampion-maken", materialsViews: 10, productClicks: 3 });
    expect(s.totals.clickRate).toBeCloseTo(0.3);
    expect(s.candidates).toEqual([]);
  });

  it("voegt een eigen partner toe (bijv. Pipoos via Daisycon), eerst uitgeschakeld", async () => {
    const bad = await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/partners", headers: admin, payload: { slug: "pipoos", name: "Pipoos", linkTemplate: "https://ds1.nl/c/?si={siteId}&dl={url}", allowedHosts: [] } });
    expect(bad.statusCode).toBe(400);
    const ok = await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/partners", headers: admin, payload: { slug: "pipoos", name: "Pipoos", linkTemplate: "https://ds1.nl/c/?si={siteId}&dl={url}&ws={subId}", allowedHosts: ["www.pipoos.com"] } });
    expect(ok.statusCode).toBe(201);
    const dup = await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/partners", headers: admin, payload: { slug: "pipoos", name: "Pipoos", linkTemplate: "{url}", allowedHosts: ["www.pipoos.com"] } });
    expect(dup.statusCode).toBe(400);
    const list = (await ctx.http.inject({ method: "GET", url: "/v1/admin/shop/partners", headers: admin })).json().partners;
    expect(list.find((p: { slug: string }) => p.slug === "pipoos")).toMatchObject({ enabled: false, allowedHosts: ["www.pipoos.com"] });
    expect(list.map((p: { slug: string }) => p.slug)).toEqual(expect.arrayContaining(["amazon-nl", "amazon-de"]));
  });

  it("kiest per markt het product met de hoogste voorkeur", async () => {
    await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/partners/amazon-de", headers: admin, payload: { enabled: true, settings: { tag: "kleurhoek-21" } } });
    const save = (slug: string, body: Record<string, unknown>) => ctx.http.inject({ method: "PUT", url: `/v1/admin/shop/products/${slug}`, headers: admin, payload: { enabled: true, name: slug, materials: ["lijmstift"], ...body } });
    expect((await save("lijm-de", { partner: "amazon-de", url: "https://www.amazon.de/dp/B000LIJM01", markets: ["de-DE"], rank: 1 })).statusCode).toBe(200);
    expect((await save("lijm-nl-goed", { partner: "bol", url: "https://www.bol.com/nl/nl/p/lijm/1/", markets: ["nl-NL"], rank: 1 })).statusCode).toBe(200);
    expect((await save("lijm-nl-best", { partner: "bol", url: "https://www.bol.com/nl/nl/p/lijm/2/", markets: ["nl-NL"], rank: 0 })).statusCode).toBe(200);
    const shop = ctx.app.get(ShopService);
    expect((await shop.forMaterials("nl-NL", "nl", ["lijmstift"])).get("lijmstift")?.slug).toBe("lijm-nl-best");
    expect((await shop.forMaterials("de-DE", "nl", ["lijmstift"])).get("lijmstift")?.slug).toBe("lijm-de");
    expect(await shop.link("de-DE", "lijm-de", "x")).toBe("https://www.amazon.de/dp/B000LIJM01?tag=kleurhoek-21");
    expect(await shop.link("nl-NL", "lijm-de", "x")).toBeNull();
  });
  it("stelt producten voor en voegt ze met één verzoek toe", async () => {
    const before = (await ctx.http.inject({ method: "GET", url: "/v1/admin/shop/products", headers: admin })).json();
    const open = before.suggestions.map((s: { slug: string }) => s.slug);
    expect(open).toContain("faber-castell-colour-grip-12");
    expect(open).not.toContain("lijm-nl-best");
    const res = await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/products/suggestions", headers: admin, payload: { slugs: ["faber-castell-colour-grip-12", "bestaat-niet"] } });
    expect(res.statusCode).toBe(201);
    expect(res.json()).toEqual({ added: ["faber-castell-colour-grip-12"] });
    const after = (await ctx.http.inject({ method: "GET", url: "/v1/admin/shop/products", headers: admin })).json();
    expect(after.products.find((p: { slug: string }) => p.slug === "faber-castell-colour-grip-12")).toMatchObject({ partner: "amazon-nl", url: "https://www.amazon.nl/dp/B0007OECNU", materials: ["kleurpotloden"], enabled: true });
    expect(after.suggestions.map((s: { slug: string }) => s.slug)).not.toContain("faber-castell-colour-grip-12");
    // Nog een keer toevoegen doet niets.
    expect((await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/products/suggestions", headers: admin, payload: { slugs: ["faber-castell-colour-grip-12"] } })).json()).toEqual({ added: [] });
  });

  it("haalt een ASIN uit een link, een korte link of los (ADR 0031)", async () => {
    const follow = async () => "https://www.amazon.de/-/dp/B00ABCDE12?ref=x";
    expect(await asinFrom("b00abcde12")).toBe("B00ABCDE12");
    expect(await asinFrom("https://www.amazon.fr/Crayola-Feutres/dp/B00ABCDE12/ref=sr_1")).toBe("B00ABCDE12");
    expect(await asinFrom("https://amzn.eu/d/abc123", follow)).toBe("B00ABCDE12");
    expect(await asinFrom("https://www.bol.com/nl/p/x/920000/")).toBeNull();
    expect(await asinFrom("hallo")).toBeNull();
  });

  it("voegt één ASIN toe voor meerdere Amazon-winkels, met markten en namen per taal", async () => {
    const res = await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/products/amazon", headers: admin, payload: {
      asin: "https://www.amazon.nl/dp/B0STEMPEL1?tag=iemand-21", name: "Stempelset dieren", names: { de: "Tierstempel-Set" },
      materials: ["stempels"], stores: ["amazon-nl", "amazon-de"],
    } });
    expect(res.statusCode).toBe(201);
    expect(res.json().added).toEqual([
      { slug: "stempelset-dieren-amazon-nl", partner: "amazon-nl", url: "https://www.amazon.nl/dp/B0STEMPEL1" },
      { slug: "stempelset-dieren-amazon-de", partner: "amazon-de", url: "https://www.amazon.de/dp/B0STEMPEL1" },
    ]);
    const list = (await ctx.http.inject({ method: "GET", url: "/v1/admin/shop/products", headers: admin })).json();
    expect(list.products.find((p: { slug: string }) => p.slug === "stempelset-dieren-amazon-de")).toMatchObject({ markets: ["de-DE", "de-AT", "de-CH", "de-LU"], materials: ["stempels"], enabled: true });
    expect(list.amazonStores.map((s: { partner: string }) => s.partner)).toContain("amazon-pl");
    const names = (await ctx.http.inject({ method: "GET", url: "/v1/admin/shop/products?language=de", headers: admin })).json();
    expect(names.products.find((p: { slug: string }) => p.slug === "stempelset-dieren-amazon-de").name).toBe("Tierstempel-Set");
    const bad = await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/products/amazon", headers: admin, payload: { asin: "geen", name: "X y", materials: ["stempels"], stores: ["amazon-nl"] } });
    expect(bad.statusCode).toBe(400);
  });

  it("zet een product aan en uit vanuit de lijst", async () => {
    const off = await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/products/stempelset-dieren-amazon-nl/enabled", headers: admin, payload: { enabled: false } });
    expect(off.json()).toEqual({ slug: "stempelset-dieren-amazon-nl", enabled: false });
    const list = (await ctx.http.inject({ method: "GET", url: "/v1/admin/shop/products", headers: admin })).json();
    expect(list.products.find((p: { slug: string }) => p.slug === "stempelset-dieren-amazon-nl").enabled).toBe(false);
    expect((await ctx.http.inject({ method: "PUT", url: "/v1/admin/shop/products/bestaat-niet/enabled", headers: admin, payload: { enabled: true } })).statusCode).toBe(404);
  });
});
