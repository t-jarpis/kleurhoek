import * as source from "@kleurhoek/catalog-data";
import { eq } from "drizzle-orm";
import type { Database } from "./database";
import { withTenant } from "./tenant";
import { ages, categories, continents, plates, plateVersions } from "../modules/catalog/catalog.schema";
import { markets, translations, type EntityType } from "../modules/localization/localization.schema";
import { holidayDates, holidays, seasons } from "../modules/availability/availability.schema";

type Tr = { entityType: EntityType; entityKey: string; language: string; fields: Record<string, string | null> };

/** Zet de catalogus uit @kleurhoek/catalog-data in de database. Idempotent: bestaande platen worden overgeslagen. */
export async function seed(db: Database, tenantId: string): Promise<{ plates: number }> {
  return withTenant(db, tenantId, async (tx) => {
    const existing = await tx.select({ id: plates.id }).from(plates).where(eq(plates.tenantId, tenantId)).limit(1);
    if (existing.length) return { plates: 0 };

    await tx.insert(markets).values({ tenantId, code: "nl-NL", country: "NL", language: "nl", status: "live", paperSize: "A4", minAccountAge: 16 });

    const cats = source.categories();
    const ageList = source.ages();
    const conts = source.continents();
    const hols = source.holidays();
    const seas = source.seasons();
    await tx.insert(categories).values(cats.map((c) => ({ tenantId, slug: c.slug, sortOrder: c.order, color: c.color })));
    await tx.insert(ages).values(ageList.map((a) => ({ tenantId, slug: a.slug, sortOrder: a.order, level: a.level, strokeWidth: a.strokeWidth })));
    await tx.insert(continents).values(conts.map((c) => ({ tenantId, slug: c.slug, sortOrder: c.order, color: c.color })));
    await tx.insert(holidays).values(hols.map((h) => ({
      tenantId, slug: h.slug, sortOrder: h.order, countries: h.countries,
      fixedMonth: h.fixed?.[0] ?? null, fixedDay: h.fixed?.[1] ?? null,
      leadDays: h.leadDays, afterDays: h.afterDays, approximate: h.approximate, label: h.label,
    })));
    const dates = hols.flatMap((h) => Object.entries(h.dates ?? {}).map(([year, date]) => ({ tenantId, holidaySlug: h.slug, year: Number(year), date })));
    if (dates.length) await tx.insert(holidayDates).values(dates);
    await tx.insert(seasons).values(seas.map((s) => ({
      tenantId, slug: s.slug, countries: s.countries, fromMonth: s.from[0], fromDay: s.from[1], toMonth: s.to[0], toDay: s.to[1], plateSlugs: s.plates,
    })));

    const tr: Tr[] = [];
    const add = (entityType: EntityType, entityKey: string, i18n: Record<string, Record<string, unknown>>) => {
      for (const [language, fields] of Object.entries(i18n)) tr.push({ entityType, entityKey, language, fields: fields as Record<string, string | null> });
    };
    cats.forEach((c) => add("category", c.slug, c.i18n));
    ageList.forEach((a) => add("age", a.slug, a.i18n));
    conts.forEach((c) => add("continent", c.slug, c.i18n));
    hols.forEach((h) => add("holiday", h.slug, h.i18n));
    seas.forEach((s) => add("season", s.slug, s.i18n));
    source.colors().forEach((c) => add("color", c.code, c.i18n));

    const list = source.plates();
    for (const p of list) {
      const [plate] = await tx.insert(plates).values({
        tenantId, slug: p.slug, categorySlug: p.category, ageSlug: p.age,
        continentSlug: p.world?.continent ?? null, depictedCountry: p.world?.country ?? null,
        holidaySlug: p.holiday, status: "published", sortOrder: p.order,
      }).returning({ id: plates.id });
      const [version] = await tx.insert(plateVersions).values({
        tenantId, plateId: plate!.id, version: 1, svg: source.plateSvg(p.slug),
        regionCount: p.regionCount, colorByNumber: p.colorByNumber, createdBy: "migratie-prototype",
      }).returning({ id: plateVersions.id });
      await tx.update(plates).set({ currentVersionId: version!.id }).where(eq(plates.id, plate!.id));
      add("plate", p.slug, p.i18n);
    }
    await tx.insert(translations).values(tr.map((t) => ({ tenantId, ...t, status: "reviewed" as const })));
    return { plates: list.length };
  });
}
