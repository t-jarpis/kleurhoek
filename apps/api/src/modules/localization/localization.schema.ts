import { integer, jsonb, pgSchema, text, uniqueIndex } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const localizationSchema = pgSchema("localization");

/** Een markt = land + taal, bijvoorbeeld nl-NL of fr-BE. */
export const markets = localizationSchema.table("markets", {
  ...baseColumns(),
  code: text("code").notNull(),
  country: text("country").notNull(),
  language: text("language").notNull(),
  status: text("status", { enum: ["draft", "live"] }).notNull().default("draft"),
  paperSize: text("paper_size", { enum: ["A4", "Letter"] }).notNull().default("A4"),
  minAccountAge: integer("min_account_age").notNull().default(16),
}, (t) => [uniqueIndex("markets_tenant_code").on(t.tenantId, t.code)]);

export const ENTITY_TYPES = ["plate", "category", "age", "continent", "holiday", "season", "color", "material", "product", "ui"] as const;
export type EntityType = (typeof ENTITY_TYPES)[number];

/** Vertaalde velden per ding en taal. Velden verschillen per soort (naam, woord, telvraag, hint). */
export const translations = localizationSchema.table("translations", {
  ...baseColumns(),
  entityType: text("entity_type", { enum: ENTITY_TYPES }).notNull(),
  entityKey: text("entity_key").notNull(),
  language: text("language").notNull(),
  fields: jsonb("fields").$type<Record<string, string | null>>().notNull(),
  status: text("status", { enum: ["draft", "reviewed"] }).notNull().default("draft"),
}, (t) => [uniqueIndex("translations_unique").on(t.tenantId, t.entityType, t.entityKey, t.language)]);
