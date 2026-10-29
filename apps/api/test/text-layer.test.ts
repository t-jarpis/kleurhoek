import * as source from "@kleurhoek/catalog-data";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { DB, type Database } from "../src/db/database";
import { withTenant } from "../src/db/tenant";
import { markets } from "../src/modules/localization/localization.schema";
import { LocalizationService } from "../src/modules/localization/localization.service";
import { createTestApp, TENANT } from "./app";

// Tekstlaag (ADR 0029): teksten in de plaat worden per taal vervangen; een plaat is pas zichtbaar als alles vertaald is.
let ctx: Awaited<ReturnType<typeof createTestApp>>;
const get = (url: string) => ctx.http.inject({ method: "GET", url });
const SLUG = "lampion-maken";

beforeAll(async () => {
  ctx = await createTestApp();
  const db = ctx.app.get<Database>(DB);
  await withTenant(db, TENANT, (tx) => tx.insert(markets).values({ tenantId: TENANT, code: "ga-ZZ", country: "ZZ", language: "ga", status: "live" }).onConflictDoNothing());
  const i18n = ctx.app.get(LocalizationService);
  const p = source.plates().find((x) => x.slug === SLUG)!;
  await i18n.save(TENANT, "plate", SLUG, "ga", { name: "Lyhty", word: null, countQuestion: null, steps: "Ausschneiden.\nKleben.", pageTitles: p.pages.map(() => "Seite").join("\n") || null });
  await i18n.save(TENANT, "plate", "kat", "ga", { name: "Kissa", word: null, countQuestion: null });
  const texts = source.plateTexts(source.plateSvg(SLUG), ...p.pages.map((_, i) => source.pageSvg(SLUG, i + 2)));
  expect(texts.length).toBeGreaterThan(0);
  for (const t of texts) await i18n.save(TENANT, "text", t, "ga", { text: t === "knippen" ? "leikkaa" : `FI ${t}` });
});
afterAll(async () => { await ctx.app.close(); });

describe("tekstlaag", () => {
  it("toont alleen platen met naam én alle teksten vertaald, met een adres per taal", async () => {
    const items = (await get("/v1/markets/ga-ZZ/plates")).json().items as { slug: string; svg: string }[];
    const lampion = items.find((i) => i.slug === SLUG);
    expect(lampion?.svg).toMatch(new RegExp(`^/v1/assets/plates/${SLUG}/1\\.ga-[0-9a-f]{8}\\.svg$`));
    // "kat" heeft geen tekst in de tekening: met een naam is hij zichtbaar, op het gewone adres.
    expect(items.find((i) => i.slug === "kat")?.svg).toBe("/v1/assets/plates/kat/1.svg");
    expect(items).toHaveLength(2);
  });

  it("serveert de vertaalde SVG", async () => {
    const path = (await get(`/v1/markets/ga-ZZ/plates/${SLUG}`)).json().svg as string;
    const r = await get(path);
    expect(r.statusCode).toBe(200);
    expect(r.body).toContain(">leikkaa</text>");
    expect(r.body).not.toContain(">knippen</text>");
    expect((await get(`/v1/assets/plates/${SLUG}/1.ga-zzzz.svg`)).statusCode).toBe(404);
  });
});
