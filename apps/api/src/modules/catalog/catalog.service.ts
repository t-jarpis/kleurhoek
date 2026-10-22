import { Inject, Injectable } from "@nestjs/common";
import { and, asc, eq } from "drizzle-orm";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { ages, categories, continents, plates, plateVersions, type ColorByNumber } from "./catalog.schema";

export interface PlateSummary {
  slug: string; category: string; age: string;
  continent: string | null; depictedCountry: string | null; holiday: string | null;
  sortOrder: number; version: number; regionCount: number;
}
export interface PlateDetail extends PlateSummary { svg: string; colorByNumber: ColorByNumber }
export interface Taxonomy {
  categories: { slug: string; color: string }[];
  ages: { slug: string; level: number; strokeWidth: number }[];
  continents: { slug: string; color: string }[];
}

/** Publieke interface van het domein Catalogus. Andere domeinen gebruiken alleen deze service. */
@Injectable()
export class CatalogService {
  constructor(@Inject(DB) private readonly db: Database) {}

  private readonly summary = {
    slug: plates.slug, category: plates.categorySlug, age: plates.ageSlug,
    continent: plates.continentSlug, depictedCountry: plates.depictedCountry, holiday: plates.holidaySlug,
    sortOrder: plates.sortOrder, version: plateVersions.version, regionCount: plateVersions.regionCount,
  };

  listPublished(tenantId: string): Promise<PlateSummary[]> {
    return withTenant(this.db, tenantId, (tx) =>
      tx.select(this.summary).from(plates)
        .innerJoin(plateVersions, eq(plates.currentVersionId, plateVersions.id))
        .where(and(eq(plates.tenantId, tenantId), eq(plates.status, "published")))
        .orderBy(asc(plates.sortOrder)));
  }

  async getPublished(tenantId: string, slug: string): Promise<PlateDetail | null> {
    const rows = await withTenant(this.db, tenantId, (tx) =>
      tx.select({ ...this.summary, svg: plateVersions.svg, colorByNumber: plateVersions.colorByNumber }).from(plates)
        .innerJoin(plateVersions, eq(plates.currentVersionId, plateVersions.id))
        .where(and(eq(plates.tenantId, tenantId), eq(plates.slug, slug), eq(plates.status, "published")))
        .limit(1));
    return rows[0] ?? null;
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

  taxonomy(tenantId: string): Promise<Taxonomy> {
    return withTenant(this.db, tenantId, async (tx) => ({
      categories: await tx.select({ slug: categories.slug, color: categories.color }).from(categories).where(eq(categories.tenantId, tenantId)).orderBy(asc(categories.sortOrder)),
      ages: await tx.select({ slug: ages.slug, level: ages.level, strokeWidth: ages.strokeWidth }).from(ages).where(eq(ages.tenantId, tenantId)).orderBy(asc(ages.sortOrder)),
      continents: await tx.select({ slug: continents.slug, color: continents.color }).from(continents).where(eq(continents.tenantId, tenantId)).orderBy(asc(continents.sortOrder)),
    }));
  }
}
