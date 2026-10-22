import * as source from "@kleurhoek/catalog-data";
import { inArray } from "drizzle-orm";
import type { Database } from "./database";
import { withTenant } from "./tenant";
import { ages, categories, continents, materials, plateMaterials, plates, plateVersions } from "../modules/catalog/catalog.schema";
import { markets, translations, type EntityType } from "../modules/localization/localization.schema";
import { holidayDates, holidays, seasons } from "../modules/availability/availability.schema";
import { DEFAULT_PARTNERS } from "../modules/shop/shop.defaults";
import { partners } from "../modules/shop/shop.schema";

type Tr = { entityType: EntityType; entityKey: string; language: string; fields: Record<string, string | null> };

/**
 * Zet de catalogus uit @kleurhoek/catalog-data in de database. Idempotent en aanvullend: wat er al
 * staat blijft staan (ook als het in het admin panel is aangepast), nieuwe platen, materialen en
 * vertalingen komen erbij. Zo kan de seed na elke deploy veilig opnieuw draaien.
 */
export async function seed(db: Database, tenantId: string): Promise<{ plates: number }> {
  return withTenant(db, tenantId, async (tx) => {
    await tx.insert(markets).values({ tenantId, code: "nl-NL", country: "NL", language: "nl", status: "live", paperSize: "A4", minAccountAge: 16 }).onConflictDoNothing();

    const cats = source.categories();
    const ageList = source.ages();
    const conts = source.continents();
    const hols = source.holidays();
    const seas = source.seasons();
    const mats = source.materials();
    await tx.insert(categories).values(cats.map((c) => ({ tenantId, slug: c.slug, sortOrder: c.order, color: c.color }))).onConflictDoNothing();
    await tx.insert(ages).values(ageList.map((a) => ({ tenantId, slug: a.slug, sortOrder: a.order, level: a.level, strokeWidth: a.strokeWidth }))).onConflictDoNothing();
    await tx.insert(continents).values(conts.map((c) => ({ tenantId, slug: c.slug, sortOrder: c.order, color: c.color }))).onConflictDoNothing();
    await tx.insert(materials).values(mats.map((m) => ({ tenantId, slug: m.slug, sortOrder: m.order }))).onConflictDoNothing();
    await tx.insert(holidays).values(hols.map((h) => ({
      tenantId, slug: h.slug, sortOrder: h.order, countries: h.countries,
      fixedMonth: h.fixed?.[0] ?? null, fixedDay: h.fixed?.[1] ?? null,
      leadDays: h.leadDays, afterDays: h.afterDays, approximate: h.approximate, label: h.label,
    }))).onConflictDoNothing();
    const dates = hols.flatMap((h) => Object.entries(h.dates ?? {}).map(([year, date]) => ({ tenantId, holidaySlug: h.slug, year: Number(year), date })));
    if (dates.length) await tx.insert(holidayDates).values(dates).onConflictDoNothing();
    await tx.insert(seasons).values(seas.map((s) => ({
      tenantId, slug: s.slug, countries: s.countries, fromMonth: s.from[0], fromDay: s.from[1], toMonth: s.to[0], toDay: s.to[1], plateSlugs: s.plates,
    }))).onConflictDoNothing();
    await tx.insert(partners).values(DEFAULT_PARTNERS.map((p) => ({ tenantId, ...p }))).onConflictDoNothing();

    const tr: Tr[] = [];
    const add = (entityType: EntityType, entityKey: string, i18n: Record<string, Record<string, unknown>>) => {
      for (const [language, fields] of Object.entries(i18n)) {
        const flat: Record<string, string | null> = {};
        for (const [k, v] of Object.entries(fields)) flat[k] = Array.isArray(v) ? v.join("\n") : (v as string | null | undefined) ?? null;
        tr.push({ entityType, entityKey, language, fields: flat });
      }
    };
    cats.forEach((c) => add("category", c.slug, c.i18n));
    ageList.forEach((a) => add("age", a.slug, a.i18n));
    conts.forEach((c) => add("continent", c.slug, c.i18n));
    hols.forEach((h) => add("holiday", h.slug, h.i18n));
    seas.forEach((s) => add("season", s.slug, s.i18n));
    mats.forEach((m) => add("material", m.slug, m.i18n));
    source.colors().forEach((c) => add("color", c.code, c.i18n));

    const list = source.plates();
    const existing = new Map((await tx.select({ id: plates.id, slug: plates.slug }).from(plates).where(inArray(plates.slug, list.map((p) => p.slug)))).map((r) => [r.slug, r.id]));
    let added = 0;
    for (const p of list) {
      let plateId = existing.get(p.slug);
      if (!plateId) {
        const [plate] = await tx.insert(plates).values({
          tenantId, slug: p.slug, categorySlug: p.category, ageSlug: p.age,
          continentSlug: p.world?.continent ?? null, depictedCountry: p.world?.country ?? null,
          holidaySlug: p.holiday, status: "published", sortOrder: p.order,
          kind: p.kind, minutes: p.minutes, adultHelp: p.adultHelp, paperGsm: p.paperGsm,
        }).returning({ id: plates.id });
        plateId = plate!.id;
        const [version] = await tx.insert(plateVersions).values({
          tenantId, plateId, version: 1, svg: source.plateSvg(p.slug), height: p.height,
          regionCount: p.regionCount, colorByNumber: p.colorByNumber, createdBy: "catalog-data",
        }).returning({ id: plateVersions.id });
        await tx.update(plates).set({ currentVersionId: version!.id }).where(inArray(plates.id, [plateId]));
        added++;
      }
      await tx.insert(plateMaterials).values(p.materials.map((m, i) => ({ tenantId, plateId: plateId!, materialSlug: m.slug, optional: m.optional, sortOrder: i }))).onConflictDoNothing();
      add("plate", p.slug, p.i18n);
    }
    await tx.insert(translations).values(tr.map((t) => ({ tenantId, ...t, status: "reviewed" as const }))).onConflictDoNothing();
    return { plates: added };
  });
}
