import * as source from "@kleurhoek/catalog-data";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { DB, type Database } from "../src/db/database";
import { withTenant } from "../src/db/tenant";
import { markets } from "../src/modules/localization/localization.schema";
import { ZONES } from "../src/shared/dates";
import { createTestApp, TENANT } from "./app";

/** Feesten die in elk land met een markt in de kalender staan (eventueel met een eigen datum). */
const EVERYWHERE = ["oudnieuw", "chinees", "valentijn", "holi", "suikerfeest", "moederdag", "offerfeest", "vaderdag", "school", "halloween", "divali", "chanoeka", "verjaardag"];
/** Bewust niet overal (ADR 0053): Kerst en Pasen staan niet in de Turkse kalender. */
const CHRISTIAN = ["kerst", "pasen"];
const NOT_CHRISTIAN = new Set(["TR"]);

describe("elk land met een markt heeft een volledige kalender (ADR 0054)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  let countries: string[] = [];
  beforeAll(async () => {
    ctx = await createTestApp();
    const rows = await withTenant(ctx.app.get<Database>(DB), TENANT, (tx) => tx.select({ country: markets.country }).from(markets));
    countries = [...new Set(rows.map((r) => r.country))].sort();
  });
  afterAll(async () => { await ctx.app.close(); });

  it("tijdzone, seizoen, eerste schooldag en de algemene feesten", () => {
    expect(countries.length).toBeGreaterThan(50);
    const holidays = new Map(source.holidays().map((h) => [h.slug, h]));
    const seasons = source.seasons();
    const gaps: string[] = [];
    for (const c of countries) {
      if (!ZONES[c]) gaps.push(`${c}: geen tijdzone`);
      if (!seasons.some((s) => s.countries.includes(c))) gaps.push(`${c}: geen seizoen`);
      if (c !== "NL" && !holidays.get("school")!.overrides?.[c]) gaps.push(`${c}: geen eerste schooldag`);
      for (const slug of EVERYWHERE) if (!holidays.get(slug)!.countries.includes(c)) gaps.push(`${c}: ${slug} ontbreekt`);
      for (const slug of CHRISTIAN) if (!NOT_CHRISTIAN.has(c) && !holidays.get(slug)!.countries.includes(c)) gaps.push(`${c}: ${slug} ontbreekt`);
    }
    expect(gaps).toEqual([]);
  });
});
