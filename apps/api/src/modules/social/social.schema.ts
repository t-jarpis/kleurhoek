import { integer, jsonb, pgSchema, text, timestamp, uniqueIndex } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const socialSchema = pgSchema("social");

/**
 * Kanalen (ADR 0063): Pinterest, een Facebook-pagina en een Instagram-account. De sleutels die we na het koppelen
 * krijgen, staan versleuteld in `token` (AES-256-GCM met SOCIAL_SECRET); de app-sleutels zelf staan in de
 * omgeving, nooit in de database.
 */
export const socialChannels = socialSchema.table("channels", {
  ...baseColumns(),
  kind: text("kind").notNull(),
  account: text("account"),
  externalId: text("external_id"),
  token: text("token"),
  settings: jsonb("settings").$type<Record<string, unknown>>().notNull().default({}),
  enabled: integer("enabled").notNull().default(1),
  connectedAt: timestamp("connected_at", { withTimezone: true }),
  error: text("error"),
}, (t) => [uniqueIndex("channels_kind").on(t.tenantId, t.kind)]);

/**
 * Posts: een voorstel dat na goedkeuring op het geplande moment wordt geplaatst. `key` voorkomt dubbele voorstellen
 * (dezelfde plaat twee keer op Pinterest, twee posts op één dag). Kanaal "delen" wordt niet geplaatst: dat deelt
 * Thijs zelf in groepen en WhatsApp.
 */
export const socialPosts = socialSchema.table("posts", {
  ...baseColumns(),
  channel: text("channel").notNull(),
  status: text("status").notNull().default("voorstel"),
  key: text("key").notNull(),
  source: text("source").notNull(),
  market: text("market").notNull(),
  plateSlug: text("plate_slug"),
  title: text("title").notNull(),
  body: text("body").notNull(),
  link: text("link").notNull(),
  image: text("image").notNull(),
  board: text("board"),
  scheduledAt: timestamp("scheduled_at", { withTimezone: true }).notNull(),
  decidedAt: timestamp("decided_at", { withTimezone: true }),
  decidedBy: text("decided_by"),
  publishedAt: timestamp("published_at", { withTimezone: true }),
  externalUrl: text("external_url"),
  attempts: integer("attempts").notNull().default(0),
  error: text("error"),
}, (t) => [uniqueIndex("posts_key").on(t.tenantId, t.channel, t.key)]);

/** Instellingen van het domein (één rij): wie de dagelijkse mail krijgt, hoeveel pins per dag, welke dagen een post. */
export const socialSettings = socialSchema.table("settings", {
  ...baseColumns(),
  value: jsonb("value").$type<Record<string, unknown>>().notNull().default({}),
  digestSentOn: text("digest_sent_on"),
  generatedOn: text("generated_on"),
}, (t) => [uniqueIndex("settings_tenant").on(t.tenantId)]);
