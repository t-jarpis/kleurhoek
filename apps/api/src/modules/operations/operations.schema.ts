import { boolean, date, index, integer, jsonb, pgSchema, text, timestamp, uniqueIndex } from "drizzle-orm/pg-core";
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

/**
 * Eén regel releasenotes: een commit, met de Nederlandse tekst uit de trailer Release-note als die er is.
 * `public`: tekst voor bezoekers uit de trailer Public-note (ADR 0030); alleen die komt op de website.
 */
export interface ReleaseNote { sha: string; date: string; text: string; technical: boolean; public?: string }

/**
 * Releases van deze omgeving (ADR 0023): de API legt bij het opstarten vast welke versie draait, zodra
 * die anders is dan de vorige. De notes zijn de commits sinds de vorige release.
 */
export const releases = operationsSchema.table("releases", {
  ...baseColumns(),
  sha: text("sha").notNull(),
  previousSha: text("previous_sha"),
  /** first = eerste in deze omgeving, release = nieuwe versie, rollback = terug naar een eerdere versie. */
  kind: text("kind", { enum: ["first", "release", "rollback"] }).notNull(),
  notes: jsonb("notes").$type<ReleaseNote[]>().notNull(),
  startedAt: timestamp("started_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => [index("releases_tenant_started").on(t.tenantId, t.startedAt)]);
