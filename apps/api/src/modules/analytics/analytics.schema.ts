import { date, index, integer, pgSchema, text, timestamp, uniqueIndex } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const analyticsSchema = pgSchema("analytics");

export const EVENT_TYPES = ["page_view", "plate_view", "plate_colored", "plate_completed", "pdf_download", "print", "signup", "login"] as const;
export type EventType = (typeof EVENT_TYPES)[number];

/** Ruwe events zonder persoonsgegevens. Bewaartermijn 90 dagen (zie ADR 0002). */
export const events = analyticsSchema.table("events", {
  ...baseColumns(),
  type: text("type", { enum: EVENT_TYPES }).notNull(),
  plateSlug: text("plate_slug"),
  market: text("market").notNull(),
  country: text("country"),
  device: text("device", { enum: ["mobile", "tablet", "desktop", "other"] }).notNull(),
  /** Hash met een dagelijks wisselend zout: niet over dagen heen te volgen. */
  visitorHash: text("visitor_hash"),
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
  uniqueVisitors: integer("unique_visitors").notNull().default(0),
}, (t) => [uniqueIndex("daily_totals_unique").on(t.tenantId, t.day, t.plateSlug, t.market, t.country)]);
