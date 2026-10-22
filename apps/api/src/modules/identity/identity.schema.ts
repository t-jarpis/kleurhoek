import { index, jsonb, pgSchema, text, timestamp, uniqueIndex, uuid } from "drizzle-orm/pg-core";
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

export type UserKind = "member" | "admin";
export type UserStatus = "active" | "blocked";

/**
 * Gebruikers van de site (member) en beheerders (admin). Zitadel is de bron voor wie iemand is;
 * hier staat alleen wat de site zelf nodig heeft. Geen wachtwoorden, geen geboortedatum.
 */
export const users = identitySchema.table("users", {
  ...baseColumns(),
  /** `sub` uit Zitadel. */
  zitadelSub: text("zitadel_sub").notNull(),
  organizationId: text("organization_id").notNull(),
  kind: text("kind").$type<UserKind>().notNull(),
  status: text("status").$type<UserStatus>().notNull().default("active"),
  displayName: text("display_name"),
  email: text("email"),
  locale: text("locale"),
  /** Land van eerste aanmelding (Cloudflare), voor markt-statistiek. */
  country: text("country"),
  lastLoginAt: timestamp("last_login_at", { withTimezone: true }),
}, (t) => [
  uniqueIndex("users_tenant_sub").on(t.tenantId, t.zitadelSub),
  index("users_tenant_kind").on(t.tenantId, t.kind, t.createdAt),
]);

export const roles = identitySchema.table("roles", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  name: text("name").notNull(),
  permissions: text("permissions").array().notNull(),
}, (t) => [uniqueIndex("roles_tenant_slug").on(t.tenantId, t.slug)]);

export const userRoles = identitySchema.table("user_roles", {
  ...baseColumns(),
  userId: uuid("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  roleSlug: text("role_slug").notNull(),
  grantedBy: text("granted_by").notNull(),
}, (t) => [uniqueIndex("user_roles_unique").on(t.tenantId, t.userId, t.roleSlug)]);
