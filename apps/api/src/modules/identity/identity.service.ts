import { Inject, Injectable, type OnModuleInit } from "@nestjs/common";
import { and, asc, count, desc, eq, ilike, inArray, or, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database, type Tx } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { AuditService } from "./audit.service";
import { roles, userRoles, users, type UserKind, type UserStatus } from "./identity.schema";
import { BUILT_IN_ROLES, type Permission } from "./permissions";

export interface Profile { name?: string | undefined; email?: string | undefined; locale?: string | undefined }

export interface UserView {
  id: string;
  kind: UserKind;
  status: UserStatus;
  displayName: string | null;
  email: string | null;
  locale: string | null;
  country: string | null;
  roles: string[];
  createdAt: string;
  lastLoginAt: string | null;
}

export class IdentityError extends Error {
  constructor(readonly code: "not_found" | "self" | "not_admin" | "unknown_role", message: string) { super(message); }
}

/** Hoe vaak het profiel (naam, e-mail) opnieuw bij Zitadel wordt opgehaald. */
const PROFILE_REFRESH_MS = 24 * 60 * 60 * 1000;
/** last_login_at niet bij elk verzoek bijwerken: één schrijfactie per kwartier is genoeg. */
const TOUCH_MS = 15 * 60 * 1000;

type UserRow = typeof users.$inferSelect;

@Injectable()
export class IdentityService implements OnModuleInit {
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env, private readonly audit: AuditService) {}

  private get tenantId() { return this.env.TENANT_ID; }

  async onModuleInit() { await this.syncBuiltInRoles(); }

  /** Ingebouwde rollen aanmaken of bijwerken naar wat de code zegt. */
  async syncBuiltInRoles() {
    const tenantId = this.tenantId;
    await withTenant(this.db, tenantId, (tx) => tx.insert(roles)
      .values(BUILT_IN_ROLES.map((r) => ({ tenantId, slug: r.slug, name: r.name, permissions: r.permissions })))
      .onConflictDoUpdate({ target: [roles.tenantId, roles.slug], set: { name: sql`excluded.name`, permissions: sql`excluded.permissions`, updatedAt: sql`now()` } }));
  }

  /**
   * Zoekt de gebruiker bij een Zitadel-ID, of maakt hem aan (just in time). `loadProfile` wordt alleen
   * aangeroepen als het profiel ontbreekt of verouderd is, zodat Zitadel niet bij elk verzoek gevraagd wordt.
   */
  async provision(input: { subject: string; organizationId: string; kind: UserKind; country?: string | undefined }, loadProfile: () => Promise<Profile | null>): Promise<UserRow> {
    const tenantId = this.tenantId;
    const existing = await withTenant(this.db, tenantId, async (tx) => (await tx.select().from(users).where(eq(users.zitadelSub, input.subject)).limit(1))[0]);
    const now = Date.now();
    const stale = !existing || !existing.lastLoginAt || now - existing.lastLoginAt.getTime() > PROFILE_REFRESH_MS;
    const profile = stale ? await loadProfile() : null;

    if (existing && !stale) {
      if (now - (existing.lastLoginAt?.getTime() ?? 0) > TOUCH_MS) {
        await withTenant(this.db, tenantId, (tx) => tx.update(users).set({ lastLoginAt: new Date() }).where(eq(users.id, existing.id)));
      }
      return existing;
    }

    return withTenant(this.db, tenantId, async (tx) => {
      const values = {
        tenantId, zitadelSub: input.subject, organizationId: input.organizationId, kind: input.kind,
        displayName: profile?.name ?? existing?.displayName ?? null,
        email: profile?.email ?? existing?.email ?? null,
        locale: profile?.locale ?? existing?.locale ?? null,
        country: existing?.country ?? input.country ?? null,
        lastLoginAt: new Date(),
      };
      const [row] = await tx.insert(users).values(values)
        .onConflictDoUpdate({ target: [users.tenantId, users.zitadelSub], set: { displayName: values.displayName, email: values.email, locale: values.locale, lastLoginAt: values.lastLoginAt, updatedAt: sql`now()` } })
        .returning();
      if (!existing) await this.audit.record(tx, tenantId, { actor: input.subject, action: "identity.user.created", subject: `user:${row!.id}`, after: { kind: input.kind } });
      if (!existing && input.kind === "admin" && this.env.ADMIN_BOOTSTRAP_SUBJECTS.includes(input.subject)) {
        await tx.insert(userRoles).values({ tenantId, userId: row!.id, roleSlug: "platformbeheerder", grantedBy: "bootstrap" }).onConflictDoNothing();
        await this.audit.record(tx, tenantId, { actor: "bootstrap", action: "identity.roles.assigned", subject: `user:${row!.id}`, after: { roles: ["platformbeheerder"] } });
      }
      return row!;
    });
  }

  /** Alle permissies van een gebruiker, via zijn rollen. */
  async permissionsOf(userId: string): Promise<Permission[]> {
    const rows = await withTenant(this.db, this.tenantId, (tx) => tx.select({ permissions: roles.permissions })
      .from(userRoles).innerJoin(roles, and(eq(roles.slug, userRoles.roleSlug), eq(roles.tenantId, userRoles.tenantId)))
      .where(eq(userRoles.userId, userId)));
    return [...new Set(rows.flatMap((r) => r.permissions as Permission[]))].sort();
  }

  async listRoles() {
    return withTenant(this.db, this.tenantId, (tx) => tx.select({ slug: roles.slug, name: roles.name, permissions: roles.permissions }).from(roles).orderBy(asc(roles.slug)));
  }

  async listUsers(opts: { kind?: UserKind | undefined; q?: string | undefined; page: number; pageSize: number }): Promise<{ users: UserView[]; total: number }> {
    return withTenant(this.db, this.tenantId, async (tx) => {
      const filters = [
        opts.kind ? eq(users.kind, opts.kind) : undefined,
        opts.q ? or(ilike(users.displayName, `%${escapeLike(opts.q)}%`), ilike(users.email, `%${escapeLike(opts.q)}%`)) : undefined,
      ].filter((f) => f !== undefined);
      const where = filters.length ? and(...filters) : undefined;
      const [{ total } = { total: 0 }] = await tx.select({ total: count() }).from(users).where(where);
      const rows = await tx.select().from(users).where(where).orderBy(desc(users.createdAt)).limit(opts.pageSize).offset((opts.page - 1) * opts.pageSize);
      return { users: await this.views(tx, rows), total };
    });
  }

  async getUser(id: string): Promise<UserView | null> {
    return withTenant(this.db, this.tenantId, async (tx) => {
      const rows = await tx.select().from(users).where(eq(users.id, id)).limit(1);
      return rows.length ? (await this.views(tx, rows))[0]! : null;
    });
  }

  /** Vervangt de rollen van een beheerder. Niet bij jezelf: zo kan niemand zichzelf per ongeluk buitensluiten. */
  async setRoles(actor: { userId: string; subject: string }, userId: string, slugs: string[]): Promise<UserView> {
    if (actor.userId === userId) throw new IdentityError("self", "Je kunt je eigen rollen niet wijzigen");
    const tenantId = this.tenantId;
    await withTenant(this.db, tenantId, async (tx) => {
      const [user] = await tx.select().from(users).where(eq(users.id, userId)).limit(1);
      if (!user) throw new IdentityError("not_found", "Gebruiker bestaat niet");
      if (user.kind !== "admin" && slugs.length) throw new IdentityError("not_admin", "Alleen beheerders kunnen rollen krijgen");
      const wanted = [...new Set(slugs)].sort();
      if (wanted.length) {
        const known = await tx.select({ slug: roles.slug }).from(roles).where(inArray(roles.slug, wanted));
        const missing = wanted.filter((s) => !known.some((k) => k.slug === s));
        if (missing.length) throw new IdentityError("unknown_role", `Onbekende rol: ${missing.join(", ")}`);
      }
      const before = (await tx.select({ slug: userRoles.roleSlug }).from(userRoles).where(eq(userRoles.userId, userId))).map((r) => r.slug).sort();
      await tx.delete(userRoles).where(eq(userRoles.userId, userId));
      if (wanted.length) await tx.insert(userRoles).values(wanted.map((roleSlug) => ({ tenantId, userId, roleSlug, grantedBy: actor.subject })));
      await this.audit.record(tx, tenantId, { actor: actor.subject, action: "identity.roles.assigned", subject: `user:${userId}`, before: { roles: before }, after: { roles: wanted } });
    });
    return (await this.getUser(userId))!;
  }

  async setStatus(actor: { userId: string; subject: string }, userId: string, status: UserStatus): Promise<UserView> {
    if (actor.userId === userId) throw new IdentityError("self", "Je kunt jezelf niet blokkeren");
    const tenantId = this.tenantId;
    await withTenant(this.db, tenantId, async (tx) => {
      const [user] = await tx.select({ status: users.status }).from(users).where(eq(users.id, userId)).limit(1);
      if (!user) throw new IdentityError("not_found", "Gebruiker bestaat niet");
      await tx.update(users).set({ status, updatedAt: new Date() }).where(eq(users.id, userId));
      await this.audit.record(tx, tenantId, { actor: actor.subject, action: "identity.user.status", subject: `user:${userId}`, before: { status: user.status }, after: { status } });
    });
    return (await this.getUser(userId))!;
  }

  /** Recht op vergetelheid: de gebruiker verwijdert zijn eigen account. Het auditlog bewaart alleen het ID. */
  async deleteSelf(userId: string) {
    const tenantId = this.tenantId;
    await withTenant(this.db, tenantId, async (tx) => {
      await tx.delete(users).where(eq(users.id, userId));
      await this.audit.record(tx, tenantId, { actor: `user:${userId}`, action: "identity.user.deleted", subject: `user:${userId}` });
    });
  }

  private async views(tx: Tx, rows: UserRow[]): Promise<UserView[]> {
    if (!rows.length) return [];
    const links = await tx.select({ userId: userRoles.userId, slug: userRoles.roleSlug }).from(userRoles).where(inArray(userRoles.userId, rows.map((r) => r.id)));
    return rows.map((r) => ({
      id: r.id, kind: r.kind, status: r.status, displayName: r.displayName, email: r.email, locale: r.locale, country: r.country,
      roles: links.filter((l) => l.userId === r.id).map((l) => l.slug).sort(),
      createdAt: r.createdAt.toISOString(), lastLoginAt: r.lastLoginAt?.toISOString() ?? null,
    }));
  }
}

function escapeLike(value: string) { return value.replace(/[\\%_]/g, (c) => `\\${c}`); }
