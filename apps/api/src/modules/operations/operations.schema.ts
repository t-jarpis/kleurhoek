import { boolean, date, index, integer, jsonb, pgSchema, real, text, timestamp, uniqueIndex } from "drizzle-orm/pg-core";
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
  /** Inloggen op de website (ouders, leerkrachten, beheerders van scholen). Uit = geen knop en geen nieuwe logins. */
  loginEnabled: boolean("login_enabled").notNull().default(true),
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

/**
 * Capaciteit per dag en container (ADR 0092): processor en geheugen uit Scaleway Cockpit, als percentage van
 * wat de container mag gebruiken. Gemiddeld en op de drukste momenten (p95), plus het grootste aantal exemplaren.
 */
export const capacityDaily = operationsSchema.table("capacity_daily", {
  ...baseColumns(),
  day: date("day", { mode: "string" }).notNull(),
  app: text("app").notNull(),
  cpuAvg: real("cpu_avg"),
  cpuP95: real("cpu_p95"),
  memAvg: real("mem_avg"),
  memP95: real("mem_p95"),
  instancesMax: integer("instances_max"),
}, (t) => [uniqueIndex("capacity_daily_unique").on(t.tenantId, t.day, t.app)]);

/** Hoe snel de site antwoordt, gemeten zoals een bezoeker (ADR 0092): tijd tot het eerste antwoord per controle. */
export const speedSamples = operationsSchema.table("speed_samples", {
  ...baseColumns(),
  at: timestamp("at", { withTimezone: true }).notNull(),
  path: text("path").notNull(),
  ms: integer("ms").notNull(),
  status: integer("status").notNull(),
}, (t) => [index("speed_samples_tenant_at").on(t.tenantId, t.at)]);
