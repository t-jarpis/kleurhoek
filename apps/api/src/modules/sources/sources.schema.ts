import { boolean, date, index, integer, pgSchema, text, timestamp, uniqueIndex } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const sourcesSchema = pgSchema("sources");

/**
 * Bronnengids (ADR 0025): thema's waar mensen naar zoeken (een pretpark, een tekenfilm) met links naar
 * de kleurplaten bij de maker zelf. Naam en beschrijving (eigen tekst) staan in Lokalisatie (entity "theme").
 * We tonen nooit beeld of inhoud van de maker; alleen een link.
 */
export const themes = sourcesSchema.table("themes", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  status: text("status", { enum: ["draft", "published"] }).notNull().default("draft"),
  makerName: text("maker_name").notNull(),
  /** Homepage van de maker (https). */
  makerUrl: text("maker_url").notNull(),
  /** Producten uit de winkel bij dit thema (ADR 0011): echte producten, met partnerlink. */
  productSlugs: text("product_slugs").array().notNull().default([]),
  sortOrder: integer("sort_order").notNull().default(0),
  updatedBy: text("updated_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("themes_tenant_slug").on(t.tenantId, t.slug)]);

/** link = alleen een link (geen toestemming nodig); license = de maker gaf schriftelijk toestemming. */
export const BASES = ["link", "license"] as const;
export const SOURCE_STATUSES = ["pending", "approved", "rejected"] as const;
export const HEALTH = ["unknown", "ok", "broken"] as const;

/**
 * Eén pagina bij de maker. Komt pas online na goedkeuring in het admin panel en gaat vanzelf offline
 * als de controle hem niet meer vindt. Titel en beschrijving (eigen tekst) in Lokalisatie (entity "source").
 */
export const sources = sourcesSchema.table("sources", {
  ...baseColumns(),
  themeSlug: text("theme_slug").notNull(),
  url: text("url").notNull(),
  basis: text("basis", { enum: BASES }).notNull().default("link"),
  licenseNote: text("license_note"),
  licenseDate: date("license_date", { mode: "string" }),
  status: text("status", { enum: SOURCE_STATUSES }).notNull().default("pending"),
  health: text("health", { enum: HEALTH }).notNull().default("unknown"),
  /** De pagina is anders dan bij de goedkeuring: even nakijken (blijft wel online). */
  changed: boolean("changed").notNull().default(false),
  httpStatus: integer("http_status"),
  finalUrl: text("final_url"),
  robotsAllowed: boolean("robots_allowed"),
  /** Paginatitel bij de maker, als hulp bij het invullen (wordt nooit getoond). */
  pageTitle: text("page_title"),
  checkNote: text("check_note"),
  contentHash: text("content_hash"),
  /** Vingerafdruk van de pagina op het moment van goedkeuren. */
  baselineHash: text("baseline_hash"),
  failCount: integer("fail_count").notNull().default(0),
  lastCheckedAt: timestamp("last_checked_at", { withTimezone: true }),
  lastOkAt: timestamp("last_ok_at", { withTimezone: true }),
  approvedBy: text("approved_by"),
  approvedAt: timestamp("approved_at", { withTimezone: true }),
  sortOrder: integer("sort_order").notNull().default(0),
}, (t) => [
  uniqueIndex("sources_tenant_url").on(t.tenantId, t.url),
  index("sources_tenant_theme").on(t.tenantId, t.themeSlug),
  index("sources_tenant_checked").on(t.tenantId, t.status, t.lastCheckedAt),
]);
