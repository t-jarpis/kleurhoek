import { boolean, integer, jsonb, pgSchema, real, text, uniqueIndex, uuid } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const catalogSchema = pgSchema("catalog");

export interface ColorByNumber {
  /** Per vlak een kleurcode, '-' = wit laten. */
  codes: string;
  palette: { code: string; hex: string }[];
  /** Vooraf berekende posities van de nummers (viewBox 0 0 200 hoogte). */
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

/** Soort werkje. Kleurplaten zijn de basis; knip- en bouwplaten en spellen zijn knutselwerk (ADR 0010). */
export const PLATE_KINDS = ["kleurplaat", "knipplaat", "bouwplaat", "spel", "vouwblad", "werkblad", "sjabloon", "kaart", "tekenles"] as const;
/** Groepen voor het filter op de site (ADR 0027). */
export const KIND_GROUPS = { kleurplaat: "kleurplaten", knipplaat: "knutselen", bouwplaat: "knutselen", vouwblad: "knutselen", kaart: "knutselen", spel: "leren", werkblad: "leren", tekenles: "tekenen", sjabloon: "tekenen" } as const;
export type KindGroup = (typeof KIND_GROUPS)[keyof typeof KIND_GROUPS];
/** Extra pagina bij een plaatversie: antwoordblad of extra vel (onderdelen, stappen). Titel in de vertaling (pageTitles). */
export interface PlatePage { role: "antwoorden" | "extra"; height: number; svg: string }
export type PlateKind = (typeof PLATE_KINDS)[number];

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
  kind: text("kind", { enum: PLATE_KINDS }).notNull().default("kleurplaat"),
  /** Hoe lang het ongeveer duurt, in minuten. */
  minutes: integer("minutes"),
  /** Een volwassene moet helpen (schaar, mesje). */
  adultHelp: boolean("adult_help").notNull().default(false),
  /** Papieradvies in grammen per m², bijvoorbeeld 160 voor bouwplaten. */
  paperGsm: integer("paper_gsm"),
  /** 1 makkelijk, 2 gemiddeld, 3 uitdagend (ADR 0027); los van de leeftijd. */
  difficulty: integer("difficulty"),
}, (t) => [uniqueIndex("plates_tenant_slug").on(t.tenantId, t.slug)]);

/** Wat je nodig hebt om iets te maken: potloden, schaar, lijm. Namen staan in Lokalisatie. */
export const materials = catalogSchema.table("materials", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  sortOrder: integer("sort_order").notNull().default(0),
}, (t) => [uniqueIndex("materials_tenant_slug").on(t.tenantId, t.slug)]);

export const plateMaterials = catalogSchema.table("plate_materials", {
  ...baseColumns(),
  plateId: uuid("plate_id").notNull().references(() => plates.id, { onDelete: "cascade" }),
  materialSlug: text("material_slug").notNull(),
  optional: boolean("optional").notNull().default(false),
  sortOrder: integer("sort_order").notNull().default(0),
}, (t) => [uniqueIndex("plate_materials_unique").on(t.tenantId, t.plateId, t.materialSlug)]);

export const plateVersions = catalogSchema.table("plate_versions", {
  ...baseColumns(),
  plateId: uuid("plate_id").notNull().references(() => plates.id, { onDelete: "cascade" }),
  version: integer("version").notNull(),
  svg: text("svg").notNull(),
  regionCount: integer("region_count").notNull(),
  /** Hoogte van de tekening in de viewBox (breedte is altijd 200). */
  height: integer("height").notNull().default(200),
  colorByNumber: jsonb("color_by_number").$type<ColorByNumber>().notNull(),
  /** Pagina 2, 3 … (ADR 0027). */
  pages: jsonb("pages").$type<PlatePage[]>().notNull().default([]),
  createdBy: text("created_by").notNull(),
}, (t) => [uniqueIndex("plate_versions_plate_version").on(t.plateId, t.version)]);

/**
 * Collecties (ADR 0036): een samengestelde reeks platen, bijvoorbeeld "Rekenen groep 3" of "Herfst op school".
 * Organisaties kunnen hun aanbod beperken tot een of meer collecties. Naam per taal; platen op volgorde.
 */
export const collections = catalogSchema.table("collections", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  names: jsonb("names").$type<Record<string, string>>().notNull(),
  descriptions: jsonb("descriptions").$type<Record<string, string>>().notNull().default({}),
  plates: text("plates").array().notNull().default([]),
  sortOrder: integer("sort_order").notNull().default(0),
  updatedBy: text("updated_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("collections_tenant_slug").on(t.tenantId, t.slug)]);
