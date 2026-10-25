import { index, integer, jsonb, pgSchema, text, timestamp, uniqueIndex, uuid, boolean, date } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";
import type { Audience, Block, I18nText, MailContext, Step, TemplateKind, Topic, Trigger } from "./messaging.types";

export const messagingSchema = pgSchema("messaging");

/**
 * Abonnees (ADR 0037): alleen een e-mailadres, de markt (taal) en de onderwerpen. Aanmelden met bevestiging
 * (double opt-in) en de verklaring 16 jaar of ouder (ADR 0002). Afmelden verwijdert de rij.
 */
export const subscribers = messagingSchema.table("subscribers", {
  ...baseColumns(),
  email: text("email").notNull(),
  market: text("market").notNull(),
  organization: text("organization").notNull().default("kleurhoek"),
  topics: text("topics").array().$type<Topic[]>().notNull().default([]),
  status: text("status", { enum: ["pending", "active"] }).notNull().default("pending"),
  /** Gekoppeld websiteaccount (aangemeld via Account); dan geen bevestiging nodig. */
  userId: uuid("user_id"),
  confirmTokenHash: text("confirm_token_hash"),
  confirmSentAt: timestamp("confirm_sent_at", { withTimezone: true }),
  consentAt: timestamp("consent_at", { withTimezone: true }).notNull(),
  confirmedAt: timestamp("confirmed_at", { withTimezone: true }),
}, (t) => [
  uniqueIndex("subscribers_email").on(t.tenantId, t.organization, t.email),
  index("subscribers_status").on(t.tenantId, t.status),
]);

export const templates = messagingSchema.table("templates", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  name: text("name").notNull(),
  kind: text("kind").$type<TemplateKind>().notNull(),
  subject: jsonb("subject").$type<I18nText>().notNull(),
  preheader: jsonb("preheader").$type<I18nText>().notNull().default({}),
  blocks: jsonb("blocks").$type<Block[]>().notNull(),
  updatedBy: text("updated_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("templates_slug").on(t.tenantId, t.slug)]);

export const workflows = messagingSchema.table("workflows", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  name: text("name").notNull(),
  enabled: boolean("enabled").notNull().default(false),
  trigger: jsonb("trigger").$type<Trigger>().notNull(),
  steps: jsonb("steps").$type<Step[]>().notNull(),
  /** Tot wanneer de aanleiding al bekeken is (nieuwe platen, schema, feestdag). */
  cursor: timestamp("cursor", { withTimezone: true }),
  updatedBy: text("updated_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("workflows_slug").on(t.tenantId, t.slug)]);

/** Eén abonnee in één doorloop van een workflow. Uniek per aanleiding, dus nooit twee keer dezelfde mail. */
export const workflowRuns = messagingSchema.table("workflow_runs", {
  ...baseColumns(),
  workflowSlug: text("workflow_slug").notNull(),
  subscriberId: uuid("subscriber_id").notNull().references(() => subscribers.id, { onDelete: "cascade" }),
  occasion: text("occasion").notNull(),
  step: integer("step").notNull().default(0),
  dueAt: timestamp("due_at", { withTimezone: true }).notNull(),
  status: text("status", { enum: ["waiting", "done", "stopped"] }).notNull().default("waiting"),
  context: jsonb("context").$type<MailContext>().notNull().default({}),
}, (t) => [
  uniqueIndex("workflow_runs_once").on(t.tenantId, t.workflowSlug, t.subscriberId, t.occasion),
  index("workflow_runs_due").on(t.tenantId, t.status, t.dueAt),
]);

export const campaigns = messagingSchema.table("campaigns", {
  ...baseColumns(),
  name: text("name").notNull(),
  template: text("template").notNull(),
  audience: jsonb("audience").$type<Audience>().notNull(),
  context: jsonb("context").$type<MailContext>().notNull().default({}),
  status: text("status", { enum: ["draft", "scheduled", "sending", "sent", "cancelled"] }).notNull().default("draft"),
  scheduledAt: timestamp("scheduled_at", { withTimezone: true }),
  sentAt: timestamp("sent_at", { withTimezone: true }),
  recipients: integer("recipients").notNull().default(0),
  createdBy: text("created_by").notNull(),
});

/**
 * Uitgaande mails (wachtrij). `source` zegt waar hij vandaan komt; samen met de abonnee uniek, zodat een herhaalde
 * verwerking niets dubbel stuurt. De inhoud wordt pas bij verzenden gemaakt.
 */
export const deliveries = messagingSchema.table("deliveries", {
  ...baseColumns(),
  subscriberId: uuid("subscriber_id").notNull().references(() => subscribers.id, { onDelete: "cascade" }),
  source: text("source").notNull(),
  template: text("template").notNull(),
  context: jsonb("context").$type<MailContext>().notNull().default({}),
  transactional: boolean("transactional").notNull().default(false),
  status: text("status", { enum: ["queued", "sent", "failed", "expired"] }).notNull().default("queued"),
  attempts: integer("attempts").notNull().default(0),
  error: text("error"),
  sentAt: timestamp("sent_at", { withTimezone: true }),
  /** Message-ID die wij meegeven (<id@domein>): daarmee koppelen we meldingen van de relay terug (ADR 0038). */
  messageId: text("message_id"),
}, (t) => [
  uniqueIndex("deliveries_once").on(t.tenantId, t.source, t.subscriberId),
  index("deliveries_queue").on(t.tenantId, t.status, t.createdAt),
  index("deliveries_message_id").on(t.tenantId, t.messageId),
]);

/** Tellers per dag zonder persoonsgegevens: aanmeldingen, afmeldingen, verstuurd (ADR 0037). */
export const mailStats = messagingSchema.table("daily_stats", {
  ...baseColumns(),
  day: date("day").notNull(),
  metric: text("metric").notNull(),
  value: integer("value").notNull().default(0),
}, (t) => [uniqueIndex("daily_stats_day_metric").on(t.tenantId, t.day, t.metric)]);

// ---------- Bezorging (ADR 0038) ----------

export const DELIVERY_EVENT_TYPES = ["sent", "delivered", "deferred", "soft_bounce", "hard_bounce", "complaint", "unsubscribe"] as const;
export type DeliveryEventType = (typeof DELIVERY_EVENT_TYPES)[number];

/**
 * Wat er met een mail gebeurde, van welke bron ook (SMTP-antwoord, webhook van een relay, later een eigen
 * mailserver). Geen e-mailadres: alleen een hash (voor koppelen en blokkeren) en het domein van de ontvanger
 * (voor inzicht per mailprovider). 180 dagen bewaard.
 */
export const deliveryEvents = messagingSchema.table("delivery_events", {
  ...baseColumns(),
  type: text("type").$type<DeliveryEventType>().notNull(),
  /** Waar de melding vandaan kwam: smtp, brevo, scaleway, generic. */
  provider: text("provider").notNull(),
  emailHash: text("email_hash").notNull(),
  domain: text("domain").notNull(),
  deliveryId: uuid("delivery_id"),
  /** Bron van de mail (campaign:…, workflow:…, system:…), overgenomen van de mail; blijft als de abonnee weg is. */
  source: text("source"),
  template: text("template"),
  /** Reden zoals de ontvangende server of relay die gaf, ingekort; adressen eruit gefilterd. */
  reason: text("reason"),
  occurredAt: timestamp("occurred_at", { withTimezone: true }).notNull(),
}, (t) => [
  index("delivery_events_time").on(t.tenantId, t.occurredAt),
  index("delivery_events_email").on(t.tenantId, t.emailHash, t.occurredAt),
]);

/**
 * Adressen waar we niet meer naar sturen: hard gebounced, spamklacht, herhaald soft gebounced of handmatig.
 * Alleen een hash van het adres, zodat de lijst zelf geen adressen bevat.
 */
export const suppressions = messagingSchema.table("suppressions", {
  ...baseColumns(),
  emailHash: text("email_hash").notNull(),
  domain: text("domain").notNull(),
  reason: text("reason", { enum: ["hard_bounce", "soft_bounce", "complaint", "manual"] }).notNull(),
  detail: text("detail"),
  /** Leeg = blijvend. */
  expiresAt: timestamp("expires_at", { withTimezone: true }),
  createdBy: text("created_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("suppressions_email").on(t.tenantId, t.emailHash)]);
