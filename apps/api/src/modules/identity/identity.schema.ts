import { index, jsonb, pgSchema, text, timestamp } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const identitySchema = pgSchema("identity");

/** Auditlog: alleen toevoegen, nooit wijzigen. Wordt later vervangen door @t-jarpis/access. */
export const auditEvents = identitySchema.table("audit_events", {
  ...baseColumns(),
  actor: text("actor").notNull(),
  action: text("action").notNull(),
  subject: text("subject").notNull(),
  before: jsonb("before"),
  after: jsonb("after"),
  occurredAt: timestamp("occurred_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => [index("audit_events_tenant_time").on(t.tenantId, t.occurredAt)]);
