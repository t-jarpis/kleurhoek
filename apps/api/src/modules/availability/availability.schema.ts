import { sql } from "drizzle-orm";
import { boolean, date, integer, jsonb, pgSchema, text, uniqueIndex } from "drizzle-orm/pg-core";
import type { HolidayOverride } from "./availability.domain";
import { baseColumns } from "../../shared/columns";

export const availabilitySchema = pgSchema("availability");

/** Waar een plaat zichtbaar is. Geen regel = overal waar hij vertaald is. */
export const plateRules = availabilitySchema.table("plate_rules", {
  ...baseColumns(),
  plateSlug: text("plate_slug").notNull(),
  mode: text("mode", { enum: ["everywhere_except", "only_in"] }).notNull(),
  countries: text("countries").array().notNull().default(sql`'{}'::text[]`),
  validFrom: date("valid_from", { mode: "string" }),
  validTo: date("valid_to", { mode: "string" }),
}, (t) => [uniqueIndex("plate_rules_tenant_plate").on(t.tenantId, t.plateSlug)]);

export const holidays = availabilitySchema.table("holidays", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  sortOrder: integer("sort_order").notNull(),
  countries: text("countries").array().notNull(),
  fixedMonth: integer("fixed_month"),
  fixedDay: integer("fixed_day"),
  leadDays: integer("lead_days").notNull().default(0),
  afterDays: integer("after_days").notNull().default(0),
  approximate: boolean("approximate").notNull().default(false),
  label: text("label"),
  /** Afwijkende datum of omschrijving per land (ADR 0040). */
  overrides: jsonb("overrides").$type<Record<string, HolidayOverride>>().notNull().default({}),
}, (t) => [uniqueIndex("holidays_tenant_slug").on(t.tenantId, t.slug)]);

/** Datums van feestdagen zonder vaste datum, per jaar ingevuld. */
export const holidayDates = availabilitySchema.table("holiday_dates", {
  ...baseColumns(),
  holidaySlug: text("holiday_slug").notNull(),
  year: integer("year").notNull(),
  date: date("date", { mode: "string" }).notNull(),
}, (t) => [uniqueIndex("holiday_dates_unique").on(t.tenantId, t.holidaySlug, t.year)]);

export const seasons = availabilitySchema.table("seasons", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  countries: text("countries").array().notNull(),
  fromMonth: integer("from_month").notNull(),
  fromDay: integer("from_day").notNull(),
  toMonth: integer("to_month").notNull(),
  toDay: integer("to_day").notNull(),
  plateSlugs: text("plate_slugs").array().notNull(),
}, (t) => [uniqueIndex("seasons_tenant_slug").on(t.tenantId, t.slug)]);
