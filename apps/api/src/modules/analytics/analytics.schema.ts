import { date, index, integer, jsonb, pgSchema, text, timestamp, uniqueIndex } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const analyticsSchema = pgSchema("analytics");

export const EVENT_TYPES = [
  "page_view", "plate_view", "plate_colored", "plate_completed", "pdf_download", "print", "signup", "login",
  // Winkel: de lijst "Wat heb je nodig" is in beeld geweest, en iemand klikte door naar een product.
  "materials_view", "product_click",
] as const;
export type EventType = (typeof EVENT_TYPES)[number];

/** Ruwe events zonder persoonsgegevens. Bewaartermijn 90 dagen (zie ADR 0002). */
export const events = analyticsSchema.table("events", {
  ...baseColumns(),
  type: text("type", { enum: EVENT_TYPES }).notNull(),
  plateSlug: text("plate_slug"),
  productSlug: text("product_slug"),
  market: text("market").notNull(),
  country: text("country"),
  device: text("device", { enum: ["mobile", "tablet", "desktop", "other"] }).notNull(),
  /** Hash met een dagelijks wisselend zout: niet over dagen heen te volgen. */
  visitorHash: text("visitor_hash"),
  /** Soort pagina bij page_view (home, plaat, boekje, account …): geen adres, geen zoekterm (ADR 0020). */
  page: text("page"),
  /** Organisatie waarvan de site bekeken werd (ADR 0017); leeg bij oude events. */
  org: text("org"),
  occurredAt: timestamp("occurred_at", { withTimezone: true }).notNull(),
}, (t) => [index("events_tenant_time").on(t.tenantId, t.occurredAt)]);

/** Dagtotalen per plaat, markt en land. plate_slug '' = de hele site. */
export const dailyTotals = analyticsSchema.table("daily_totals", {
  ...baseColumns(),
  day: date("day", { mode: "string" }).notNull(),
  plateSlug: text("plate_slug").notNull(),
  market: text("market").notNull(),
  country: text("country").notNull(),
  pageViews: integer("page_views").notNull().default(0),
  plateViews: integer("plate_views").notNull().default(0),
  downloads: integer("downloads").notNull().default(0),
  prints: integer("prints").notNull().default(0),
  completions: integer("completions").notNull().default(0),
  materialsViews: integer("materials_views").notNull().default(0),
  productClicks: integer("product_clicks").notNull().default(0),
  uniqueVisitors: integer("unique_visitors").notNull().default(0),
}, (t) => [uniqueIndex("daily_totals_unique").on(t.tenantId, t.day, t.plateSlug, t.market, t.country)]);

/** Doorkliks naar producten per dag, product, bronplaat, markt en land. Basis voor "zelf gaan leveren?". */
export const dailyProductClicks = analyticsSchema.table("daily_product_clicks", {
  ...baseColumns(),
  day: date("day", { mode: "string" }).notNull(),
  productSlug: text("product_slug").notNull(),
  plateSlug: text("plate_slug").notNull(),
  market: text("market").notNull(),
  country: text("country").notNull(),
  clicks: integer("clicks").notNull().default(0),
  uniqueVisitors: integer("unique_visitors").notNull().default(0),
}, (t) => [uniqueIndex("daily_product_clicks_unique").on(t.tenantId, t.day, t.productSlug, t.plateSlug, t.market, t.country)]);

/**
 * Paginaweergaven per dag, organisatie, soort pagina, markt en apparaat (ADR 0020). Blijft na de 90 dagen
 * van de ruwe events, zodat grafieken over langere tijd kunnen. Bezoekers = unieke bezoekers die dag
 * (niet op te tellen over dagen: elke dag een nieuw zout).
 */
export const dailyPages = analyticsSchema.table("daily_pages", {
  ...baseColumns(),
  day: date("day", { mode: "string" }).notNull(),
  org: text("org").notNull(),
  page: text("page").notNull(),
  market: text("market").notNull(),
  device: text("device").notNull(),
  views: integer("views").notNull().default(0),
  visitors: integer("visitors").notNull().default(0),
}, (t) => [uniqueIndex("daily_pages_unique").on(t.tenantId, t.day, t.org, t.page, t.market, t.device)]);

/** Unieke bezoekers per dag en organisatie over de hele site (wel per dag, niet over dagen op te tellen). */
export const dailyVisitors = analyticsSchema.table("daily_visitors", {
  ...baseColumns(),
  day: date("day", { mode: "string" }).notNull(),
  org: text("org").notNull(),
  visitors: integer("visitors").notNull().default(0),
}, (t) => [uniqueIndex("daily_visitors_unique").on(t.tenantId, t.day, t.org)]);

/** Een tussendoel: zoveel maanden na de start, het doel (realistisch) en de ambitie. */
export interface GoalMilestone { month: number; target: number; stretch: number }

/**
 * Doelen per meetwaarde (ADR 0022): bezoeken per maand, platen online, doorkliks naar winkels. Tussen
 * de tussendoelen loopt de lijn recht; na het laatste blijft hij gelijk.
 */
export const goals = analyticsSchema.table("goals", {
  ...baseColumns(),
  metric: text("metric").notNull(),
  /** Eerste maand van de doelen, YYYY-MM. */
  startMonth: text("start_month").notNull(),
  milestones: jsonb("milestones").$type<GoalMilestone[]>().notNull(),
}, (t) => [uniqueIndex("goals_tenant_metric").on(t.tenantId, t.metric)]);
