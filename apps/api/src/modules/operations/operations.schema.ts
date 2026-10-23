import { boolean, date, integer, jsonb, pgSchema, text, uniqueIndex } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const operationsSchema = pgSchema("operations");

/** Rate-limitregels, instelbaar in het admin panel. */
export const rateLimits = operationsSchema.table("rate_limits", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  description: text("description").notNull(),
  limit: integer("limit").notNull(),
  windowSeconds: integer("window_seconds").notNull(),
  keyBy: text("key_by", { enum: ["ip", "user", "client"] }).notNull(),
  enabled: boolean("enabled").notNull().default(true),
  updatedBy: text("updated_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("rate_limits_tenant_slug").on(t.tenantId, t.slug)]);

/** Per dag en regel: hoeveel verzoeken doorgelaten en geblokkeerd zijn. */
export const rateLimitStats = operationsSchema.table("rate_limit_stats", {
  ...baseColumns(),
  day: date("day", { mode: "string" }).notNull(),
  ruleSlug: text("rule_slug").notNull(),
  allowed: integer("allowed").notNull().default(0),
  blocked: integer("blocked").notNull().default(0),
}, (t) => [uniqueIndex("rate_limit_stats_unique").on(t.tenantId, t.day, t.ruleSlug)]);

/**
 * Wie de website mag zien (ADR 0015). Eén rij per tenant. Staat `enabled` aan, dan laat de website
 * alleen bezoekers door van wie het IP-adres in een van de CIDR-blokken valt. Het admin panel valt
 * hier niet onder (dat heeft Cloudflare Access).
 */
export const siteAccess = operationsSchema.table("site_access", {
  ...baseColumns(),
  enabled: boolean("enabled").notNull().default(false),
  entries: jsonb("entries").$type<SiteAccessEntry[]>().notNull().default([]),
  updatedBy: text("updated_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("site_access_tenant").on(t.tenantId)]);

export interface SiteAccessEntry { cidr: string; label: string; addedBy: string; addedAt: string }
