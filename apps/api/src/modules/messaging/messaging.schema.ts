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
}, (t) => [
  uniqueIndex("deliveries_once").on(t.tenantId, t.source, t.subscriberId),
  index("deliveries_queue").on(t.tenantId, t.status, t.createdAt),
]);

/** Tellers per dag zonder persoonsgegevens: aanmeldingen, afmeldingen, verstuurd (ADR 0037). */
export const mailStats = messagingSchema.table("daily_stats", {
  ...baseColumns(),
  day: date("day").notNull(),
  metric: text("metric").notNull(),
  value: integer("value").notNull().default(0),
}, (t) => [uniqueIndex("daily_stats_day_metric").on(t.tenantId, t.day, t.metric)]);
