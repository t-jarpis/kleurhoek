import * as source from "@kleurhoek/catalog-data";
import { and, eq, inArray, sql } from "drizzle-orm";
import type { Database, Tx } from "./database";
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
function chunks<T>(list: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < list.length; i += size) out.push(list.slice(i, i + size));
  return out;
}

export async function seed(db: Database, tenantId: string): Promise<{ plates: number }> {
  return withTenant(db, tenantId, async (tx) => {
    // Nederland, België in het Nederlands en Frans (ADR 0040) en het Verenigd Koninkrijk (ADR 0044). Bestaande markten blijven zoals ze in het admin panel staan.
    await tx.insert(markets).values([
      { tenantId, code: "nl-NL", country: "NL", language: "nl", status: "live" as const, paperSize: "A4" as const, minAccountAge: 16 },
      { tenantId, code: "nl-BE", country: "BE", language: "nl", status: "live" as const, paperSize: "A4" as const, minAccountAge: 13 },
      { tenantId, code: "fr-BE", country: "BE", language: "fr", status: "live" as const, paperSize: "A4" as const, minAccountAge: 13 },
      // Engels voor het Verenigd Koninkrijk op kleurhoek.com/en-gb (ADR 0044); digitale toestemming vanaf 13 (UK GDPR).
      { tenantId, code: "en-GB", country: "GB", language: "en", status: "live" as const, paperSize: "A4" as const, minAccountAge: 13 },
    ]).onConflictDoNothing();

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
    // Feestdagen zijn niet te bewerken in het admin panel: catalog-data is de bron, dus bijwerken (landen, datums).
    await tx.insert(holidays).values(hols.map((h) => ({
      tenantId, slug: h.slug, sortOrder: h.order, countries: h.countries,
      fixedMonth: h.fixed?.[0] ?? null, fixedDay: h.fixed?.[1] ?? null,
      leadDays: h.leadDays, afterDays: h.afterDays, approximate: h.approximate, label: h.label, overrides: h.overrides ?? {},
    }))).onConflictDoUpdate({
      target: [holidays.tenantId, holidays.slug],
      set: {
        sortOrder: sql`excluded.sort_order`, countries: sql`excluded.countries`, fixedMonth: sql`excluded.fixed_month`, fixedDay: sql`excluded.fixed_day`,
        leadDays: sql`excluded.lead_days`, afterDays: sql`excluded.after_days`, approximate: sql`excluded.approximate`, label: sql`excluded.label`,
        overrides: sql`excluded.overrides`, updatedAt: sql`now()`,
      },
    });
    const dates = hols.flatMap((h) => Object.entries(h.dates ?? {}).map(([year, date]) => ({ tenantId, holidaySlug: h.slug, year: Number(year), date })));
    if (dates.length) await tx.insert(holidayDates).values(dates).onConflictDoUpdate({ target: [holidayDates.tenantId, holidayDates.holidaySlug, holidayDates.year], set: { date: sql`excluded.date`, updatedAt: sql`now()` } });
    await tx.insert(seasons).values(seas.map((s) => ({
      tenantId, slug: s.slug, countries: s.countries, fromMonth: s.from[0], fromDay: s.from[1], toMonth: s.to[0], toDay: s.to[1], plateSlugs: s.plates,
    }))).onConflictDoUpdate({ target: [seasons.tenantId, seasons.slug], set: { countries: sql`excluded.countries`, updatedAt: sql`now()` } });
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
    const newMaterials: (typeof plateMaterials.$inferInsert)[] = [];
    for (const p of list) {
      let plateId = existing.get(p.slug);
      if (!plateId) {
        const [plate] = await tx.insert(plates).values({
          tenantId, slug: p.slug, categorySlug: p.category, ageSlug: p.age,
          continentSlug: p.world?.continent ?? null, depictedCountry: p.world?.country ?? null,
          holidaySlug: p.holiday, status: "published", sortOrder: p.order,
          kind: p.kind, minutes: p.minutes, adultHelp: p.adultHelp, paperGsm: p.paperGsm, difficulty: p.difficulty,
        }).returning({ id: plates.id });
        plateId = plate!.id;
        const [version] = await tx.insert(plateVersions).values({
          tenantId, plateId, version: 1, svg: source.plateSvg(p.slug), height: p.height,
          regionCount: p.regionCount, colorByNumber: p.colorByNumber, createdBy: "catalog-data",
          pages: p.pages.map((page, i) => ({ role: page.role, height: page.height, svg: source.pageSvg(p.slug, i + 2) })),
        }).returning({ id: plateVersions.id });
        await tx.update(plates).set({ currentVersionId: version!.id }).where(inArray(plates.id, [plateId]));
        added++;
        // Materialen alleen voor nieuwe platen: wat er in het admin panel is weggehaald, komt niet terug.
        newMaterials.push(...p.materials.map((m, i) => ({ tenantId, plateId: plateId!, materialSlug: m.slug, optional: m.optional, sortOrder: i })));
      }
      add("plate", p.slug, p.i18n);
    }
    // In blokken: één insert met duizenden rijen loopt tegen de parametergrens van Postgres aan,
    // en losse inserts per plaat maken elke koude start trager.
    for (const part of chunks(newMaterials, 2000)) await tx.insert(plateMaterials).values(part).onConflictDoNothing();
    for (const part of chunks(tr, 1000)) await tx.insert(translations).values(part.map((t) => ({ tenantId, ...t, status: "reviewed" as const }))).onConflictDoNothing();
    await syncGlossaries(tx, tenantId);
    return { plates: added };
  });
}

/**
 * Woordenlijsten voor de teksten in platen (ADR 0029). Anders dan de rest wél bijgewerkt als de tekst in
 * catalog-data verandert: een verbeterde vertaling moet op de site komen. Alleen wat anders is wordt geschreven.
 */
async function syncGlossaries(tx: Tx, tenantId: string) {
  for (const language of source.textLanguages()) {
    const want = source.texts(language);
    const have = new Map((await tx.select({ key: translations.entityKey, fields: translations.fields }).from(translations)
      .where(and(eq(translations.tenantId, tenantId), eq(translations.entityType, "text"), eq(translations.language, language))))
      .map((r) => [r.key, r.fields.text ?? null]));
    const rows = Object.entries(want).filter(([k, v]) => v && have.get(k) !== v)
      .map(([k, v]) => ({ tenantId, entityType: "text" as const, entityKey: k, language, fields: { text: v }, status: "reviewed" as const }));
    for (const part of chunks(rows, 1000)) {
      await tx.insert(translations).values(part).onConflictDoUpdate({
        target: [translations.tenantId, translations.entityType, translations.entityKey, translations.language],
        set: { fields: sql`excluded.fields`, updatedAt: sql`now()` },
      });
    }
  }
}
