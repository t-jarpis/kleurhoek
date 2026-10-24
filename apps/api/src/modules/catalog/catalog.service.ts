import { BadRequestException, Inject, Injectable, NotFoundException } from "@nestjs/common";
import { GOALS, learningGoals, plateTexts, type LearningGoal } from "@kleurhoek/catalog-data";
import { and, asc, eq, inArray } from "drizzle-orm";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { ages, categories, collections, continents, materials, plateMaterials, plates, plateVersions, type ColorByNumber, type PlateKind, type PlatePage } from "./catalog.schema";

export interface PlateSummary {
  slug: string; category: string; age: string;
  continent: string | null; depictedCountry: string | null; holiday: string | null;
  sortOrder: number; version: number; regionCount: number;
  kind: PlateKind; height: number; minutes: number | null; adultHelp: boolean; paperGsm: number | null; difficulty: number | null;
  /** Leerdoelen (ADR 0036), afgeleid uit soort, onderwerp en naam. */
  goals: LearningGoal[];
}
export interface PlateMaterialRef { slug: string; optional: boolean }
export interface PlateDetail extends PlateSummary { svg: string; colorByNumber: ColorByNumber; pages: PlatePage[] }
export interface Taxonomy {
  categories: { slug: string; color: string }[];
  ages: { slug: string; level: number; strokeWidth: number }[];
  continents: { slug: string; color: string }[];
}

export { KIND_GROUPS, type KindGroup } from "./catalog.schema";
export { GOALS, type LearningGoal };

/** Collectie (ADR 0036): naam en omschrijving per taal, platen op volgorde. */
export interface Collection { slug: string; names: Record<string, string>; descriptions: Record<string, string>; plates: string[]; sortOrder: number; updatedBy: string; updatedAt: string }
export interface CollectionInput { names: Record<string, string>; descriptions?: Record<string, string> | undefined; plates: string[]; sortOrder?: number | undefined }

const withGoals = <T extends Omit<PlateSummary, "goals">>(p: T): T & { goals: LearningGoal[] } =>
  ({ ...p, goals: learningGoals({ slug: p.slug, kind: p.kind, category: p.category, holiday: p.holiday, continent: p.continent }) });
export type { PlateKind } from "./catalog.schema";

/** Publieke interface van het domein Catalogus. Andere domeinen gebruiken alleen deze service. */
@Injectable()
export class CatalogService {
  constructor(@Inject(DB) private readonly db: Database) {}

  private readonly summary = {
    slug: plates.slug, category: plates.categorySlug, age: plates.ageSlug,
    continent: plates.continentSlug, depictedCountry: plates.depictedCountry, holiday: plates.holidaySlug,
    sortOrder: plates.sortOrder, version: plateVersions.version, regionCount: plateVersions.regionCount,
    kind: plates.kind, height: plateVersions.height, minutes: plates.minutes, adultHelp: plates.adultHelp, paperGsm: plates.paperGsm, difficulty: plates.difficulty,
  };

  listPublished(tenantId: string): Promise<PlateSummary[]> {
    return withTenant(this.db, tenantId, (tx) =>
      tx.select(this.summary).from(plates)
        .innerJoin(plateVersions, eq(plates.currentVersionId, plateVersions.id))
        .where(and(eq(plates.tenantId, tenantId), eq(plates.status, "published")))
        .orderBy(asc(plates.sortOrder))).then((rows) => rows.map(withGoals));
  }

  async getPublished(tenantId: string, slug: string): Promise<PlateDetail | null> {
    const rows = await withTenant(this.db, tenantId, (tx) =>
      tx.select({ ...this.summary, svg: plateVersions.svg, colorByNumber: plateVersions.colorByNumber, pages: plateVersions.pages }).from(plates)
        .innerJoin(plateVersions, eq(plates.currentVersionId, plateVersions.id))
        .where(and(eq(plates.tenantId, tenantId), eq(plates.slug, slug), eq(plates.status, "published")))
        .limit(1));
    return rows[0] ? withGoals(rows[0]) : null;
  }

  private readonly textCache = new Map<string, string[]>();

  /**
   * De te vertalen teksten per gepubliceerde plaat (tekening en extra pagina's, ADR 0029). Per versie in het
   * geheugen: een versie verandert nooit, dus alleen nieuwe versies worden opgehaald.
   */
  async publishedTexts(tenantId: string, list?: PlateSummary[]): Promise<Map<string, string[]>> {
    const all = list ?? await this.listPublished(tenantId);
    const key = (slug: string, version: number) => `${tenantId}:${slug}@${version}`;
    const todo = all.filter((p) => !this.textCache.has(key(p.slug, p.version)));
    for (let i = 0; i < todo.length; i += 200) {
      const part = todo.slice(i, i + 200);
      const rows = await withTenant(this.db, tenantId, (tx) =>
        tx.select({ slug: plates.slug, version: plateVersions.version, svg: plateVersions.svg, pages: plateVersions.pages }).from(plates)
          .innerJoin(plateVersions, eq(plates.currentVersionId, plateVersions.id))
          .where(and(eq(plates.tenantId, tenantId), inArray(plates.slug, part.map((p) => p.slug)))));
      for (const r of rows) this.textCache.set(key(r.slug, r.version), plateTexts(r.svg, ...r.pages.map((pg) => pg.svg)));
    }
    return new Map(all.map((p) => [p.slug, this.textCache.get(key(p.slug, p.version)) ?? []]));
  }

  /** De SVG van een specifieke versie. Versies veranderen nooit, dus het CDN mag ze voor altijd cachen. */
  async getSvg(tenantId: string, slug: string, version: number): Promise<string | null> {
    const rows = await withTenant(this.db, tenantId, (tx) =>
      tx.select({ svg: plateVersions.svg }).from(plateVersions)
        .innerJoin(plates, eq(plates.id, plateVersions.plateId))
        .where(and(eq(plates.tenantId, tenantId), eq(plates.slug, slug), eq(plates.status, "published"), eq(plateVersions.version, version)))
        .limit(1));
    return rows[0]?.svg ?? null;
  }

  /** Wat je nodig hebt voor een plaat, in volgorde. */
  materialsOf(tenantId: string, slug: string): Promise<PlateMaterialRef[]> {
    return withTenant(this.db, tenantId, (tx) =>
      tx.select({ slug: plateMaterials.materialSlug, optional: plateMaterials.optional }).from(plateMaterials)
        .innerJoin(plates, eq(plates.id, plateMaterials.plateId))
        .where(and(eq(plates.tenantId, tenantId), eq(plates.slug, slug)))
        .orderBy(asc(plateMaterials.sortOrder)));
  }

  /** Wanneer elke gepubliceerde plaat erbij kwam (voor de doelen in het admin panel, ADR 0022). */
  publishedDates(tenantId: string): Promise<Date[]> {
    return withTenant(this.db, tenantId, async (tx) =>
      (await tx.select({ at: plates.createdAt }).from(plates).where(and(eq(plates.tenantId, tenantId), eq(plates.status, "published")))).map((r) => r.at));
  }

  /** Alle materialen, voor het koppelen aan producten in het admin panel. */
  materials(tenantId: string): Promise<string[]> {
    return withTenant(this.db, tenantId, async (tx) =>
      (await tx.select({ slug: materials.slug }).from(materials).where(eq(materials.tenantId, tenantId)).orderBy(asc(materials.sortOrder))).map((m) => m.slug));
  }

  taxonomy(tenantId: string): Promise<Taxonomy> {
    return withTenant(this.db, tenantId, async (tx) => ({
      categories: await tx.select({ slug: categories.slug, color: categories.color }).from(categories).where(eq(categories.tenantId, tenantId)).orderBy(asc(categories.sortOrder)),
      ages: await tx.select({ slug: ages.slug, level: ages.level, strokeWidth: ages.strokeWidth }).from(ages).where(eq(ages.tenantId, tenantId)).orderBy(asc(ages.sortOrder)),
      continents: await tx.select({ slug: continents.slug, color: continents.color }).from(continents).where(eq(continents.tenantId, tenantId)).orderBy(asc(continents.sortOrder)),
    }));
  }

  // ---------- Collecties (ADR 0036) ----------

  private collectionCache = new Map<string, { at: number; list: Collection[] }>();

  async collections(tenantId: string, fresh = false): Promise<Collection[]> {
    const hit = this.collectionCache.get(tenantId);
    if (!fresh && hit && Date.now() - hit.at < 30_000) return hit.list;
    const rows = await withTenant(this.db, tenantId, (tx) => tx.select().from(collections).where(eq(collections.tenantId, tenantId)).orderBy(asc(collections.sortOrder), asc(collections.slug)));
    const list = rows.map((r) => ({ slug: r.slug, names: r.names, descriptions: r.descriptions, plates: r.plates, sortOrder: r.sortOrder, updatedBy: r.updatedBy, updatedAt: r.updatedAt.toISOString() }));
    this.collectionCache.set(tenantId, { at: Date.now(), list });
    return list;
  }

  /** De platen in de gekozen collecties samen, of null als er geen keuze is (dan telt de collectie niet mee). */
  async collectionPlates(tenantId: string, slugs: string[] | null): Promise<Set<string> | null> {
    if (!slugs) return null;
    const list = await this.collections(tenantId);
    return new Set(list.filter((c) => slugs.includes(c.slug)).flatMap((c) => c.plates));
  }

  /** Collectie maken of bijwerken. Platen moeten bestaan; dubbele worden weggelaten, de volgorde blijft. */
  async saveCollection(tenantId: string, slug: string, input: CollectionInput, actor: string): Promise<Collection> {
    if (!/^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/.test(slug)) throw new BadRequestException("Code: kleine letters, cijfers en streepjes");
    const names = Object.fromEntries(Object.entries(input.names).map(([k, v]) => [k, v.trim()]).filter(([, v]) => v));
    if (!names.nl) throw new BadRequestException("Geef de collectie een Nederlandse naam");
    const known = new Set((await withTenant(this.db, tenantId, (tx) => tx.select({ slug: plates.slug }).from(plates).where(eq(plates.tenantId, tenantId)))).map((r) => r.slug));
    const unknown = input.plates.filter((p) => !known.has(p));
    if (unknown.length) throw new BadRequestException(`Onbekende platen: ${unknown.slice(0, 10).join(", ")}${unknown.length > 10 ? " …" : ""}`);
    const list = [...new Set(input.plates)];
    const descriptions = Object.fromEntries(Object.entries(input.descriptions ?? {}).map(([k, v]) => [k, v.trim()]).filter(([, v]) => v));
    await withTenant(this.db, tenantId, (tx) => tx.insert(collections).values({ tenantId, slug, names, descriptions, plates: list, sortOrder: input.sortOrder ?? 0, updatedBy: actor })
      .onConflictDoUpdate({ target: [collections.tenantId, collections.slug], set: { names, descriptions, plates: list, ...(input.sortOrder !== undefined ? { sortOrder: input.sortOrder } : {}), updatedBy: actor, updatedAt: new Date() } }));
    this.collectionCache.delete(tenantId);
    return (await this.collections(tenantId, true)).find((c) => c.slug === slug)!;
  }

  async deleteCollection(tenantId: string, slug: string): Promise<void> {
    const rows = await withTenant(this.db, tenantId, (tx) => tx.delete(collections).where(and(eq(collections.tenantId, tenantId), eq(collections.slug, slug))).returning({ slug: collections.slug }));
    if (!rows.length) throw new NotFoundException("Onbekende collectie");
    this.collectionCache.delete(tenantId);
  }
}
