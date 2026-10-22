import { integer, jsonb, pgSchema, real, text, uniqueIndex, uuid } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const catalogSchema = pgSchema("catalog");

export interface ColorByNumber {
  /** Per vlak een kleurcode, '-' = wit laten. */
  codes: string;
  palette: { code: string; hex: string }[];
  /** Vooraf berekende posities van de nummers (viewBox 0 0 200 200). */
  labels: { region: number; number: number; x: number; y: number; size: number }[];
}

export const categories = catalogSchema.table("categories", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  sortOrder: integer("sort_order").notNull(),
  color: text("color").notNull(),
}, (t) => [uniqueIndex("categories_tenant_slug").on(t.tenantId, t.slug)]);

export const ages = catalogSchema.table("ages", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  sortOrder: integer("sort_order").notNull(),
  level: integer("level").notNull(),
  strokeWidth: real("stroke_width").notNull(),
}, (t) => [uniqueIndex("ages_tenant_slug").on(t.tenantId, t.slug)]);

export const continents = catalogSchema.table("continents", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  sortOrder: integer("sort_order").notNull(),
  color: text("color").notNull(),
}, (t) => [uniqueIndex("continents_tenant_slug").on(t.tenantId, t.slug)]);

export const plates = catalogSchema.table("plates", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  categorySlug: text("category_slug").notNull(),
  ageSlug: text("age_slug").notNull(),
  /** Wat de plaat afbeeldt (geen zichtbaarheidsregel: dat is het domein Beschikbaarheid). */
  continentSlug: text("continent_slug"),
  depictedCountry: text("depicted_country"),
  holidaySlug: text("holiday_slug"),
  status: text("status", { enum: ["draft", "published", "archived"] }).notNull().default("draft"),
  sortOrder: integer("sort_order").notNull().default(0),
  currentVersionId: uuid("current_version_id"),
}, (t) => [uniqueIndex("plates_tenant_slug").on(t.tenantId, t.slug)]);

export const plateVersions = catalogSchema.table("plate_versions", {
  ...baseColumns(),
  plateId: uuid("plate_id").notNull().references(() => plates.id, { onDelete: "cascade" }),
  version: integer("version").notNull(),
  svg: text("svg").notNull(),
  regionCount: integer("region_count").notNull(),
  colorByNumber: jsonb("color_by_number").$type<ColorByNumber>().notNull(),
  createdBy: text("created_by").notNull(),
}, (t) => [uniqueIndex("plate_versions_plate_version").on(t.plateId, t.version)]);
