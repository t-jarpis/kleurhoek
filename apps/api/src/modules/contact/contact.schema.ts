import { boolean, index, jsonb, pgSchema, text, timestamp, uniqueIndex, uuid } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const contactSchema = pgSchema("contact");

/** Kanalen waarlangs berichten binnenkomen. Web = het formulier op de site; WhatsApp volgt (ADR 0024). */
export const CHANNELS = ["web", "whatsapp"] as const;
export type Channel = (typeof CHANNELS)[number];

export const TOPICS = ["question", "idea", "bug", "partnership", "copyright", "privacy"] as const;
export type Topic = (typeof TOPICS)[number];

export const STATUSES = ["new", "open", "answered", "closed"] as const;
export type ConversationStatus = (typeof STATUSES)[number];

/**
 * Een gesprek met één afzender, via één kanaal. Bevat persoonsgegevens (naam, e-mail, telefoon): alleen
 * zichtbaar met contact.read, en 12 maanden na het laatste bericht verwijderd (ADR 0024).
 */
export const conversations = contactSchema.table("conversations", {
  ...baseColumns(),
  channel: text("channel", { enum: CHANNELS }).notNull(),
  topic: text("topic", { enum: TOPICS }).notNull(),
  status: text("status", { enum: STATUSES }).notNull().default("new"),
  name: text("name"),
  email: text("email"),
  /** Telefoonnummer (E.164) bij WhatsApp. */
  phone: text("phone"),
  /** Organisatie en markt van de site waar het bericht vandaan kwam. */
  org: text("org").notNull(),
  market: text("market").notNull(),
  lastMessageAt: timestamp("last_message_at", { withTimezone: true }).notNull().defaultNow(),
  updatedBy: text("updated_by"),
}, (t) => [index("conversations_tenant_status").on(t.tenantId, t.status, t.lastMessageAt)]);

/** in = van de afzender, out = ons antwoord, note = interne notitie (nooit naar buiten). */
export const DIRECTIONS = ["in", "out", "note"] as const;

export const messages = contactSchema.table("messages", {
  ...baseColumns(),
  conversationId: uuid("conversation_id").notNull(),
  direction: text("direction", { enum: DIRECTIONS }).notNull(),
  body: text("body").notNull(),
  /** Beheerder (Zitadel-subject) bij out/note; leeg bij in. */
  author: text("author"),
  /** Id bij het kanaal (WhatsApp-bericht-id), om dubbele aflevering te herkennen. */
  externalId: text("external_id"),
}, (t) => [index("messages_conversation").on(t.tenantId, t.conversationId, t.createdAt)]);

/**
 * Instellingen per kanaal (geen geheimen: tokens staan in de secret manager, ADR 0024). Een kanaal
 * zonder rij staat uit, behalve web (standaard aan).
 */
export const channels = contactSchema.table("channels", {
  ...baseColumns(),
  slug: text("slug", { enum: CHANNELS }).notNull(),
  enabled: boolean("enabled").notNull().default(false),
  settings: jsonb("settings").$type<Record<string, string>>().notNull().default({}),
  updatedBy: text("updated_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("channels_tenant_slug").on(t.tenantId, t.slug)]);
