import { Inject, Injectable } from "@nestjs/common";
import { and, desc, eq, lt, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import type { AdminPrincipal } from "./admin.guard";
import { AuditService } from "./audit.service";
import { auditEvents } from "./identity.schema";
import { UndoRegistry } from "./undo";

export class ChangesError extends Error {
  constructor(readonly code: "not_found" | "forbidden" | "not_undoable" | "outdated", message: string) { super(message); }
}

export interface Change {
  id: string; at: string; actor: string; action: string; subject: string; label: string | null;
  before: unknown; after: unknown; undo: "ja" | "geen-recht" | "verouderd" | "nee";
}

/** Het auditlog voor het admin panel, met ongedaan maken waar een domein dat aanbiedt (ADR 0066). */
@Injectable()
export class ChangesService {
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env, private readonly audit: AuditService, private readonly undo: UndoRegistry) {}

  private get tenant() { return this.env.TENANT_ID; }

  async list(admin: AdminPrincipal, opts: { before?: Date | undefined; limit?: number } = {}): Promise<Change[]> {
    const limit = opts.limit ?? 50;
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select({
      id: auditEvents.id, at: auditEvents.occurredAt, actor: auditEvents.actor, action: auditEvents.action, subject: auditEvents.subject,
      before: auditEvents.before, after: auditEvents.after,
      // Bewust volledig gekwalificeerd: in een subquery verwijst een kale kolomnaam naar de binnenste tabel.
      latest: sql<boolean>`not exists (select 1 from identity.audit_events b where b.tenant_id = audit_events.tenant_id and b.subject = audit_events.subject and b.occurred_at > audit_events.occurred_at)`,
    }).from(auditEvents)
      .where(and(eq(auditEvents.tenantId, this.tenant), opts.before ? lt(auditEvents.occurredAt, opts.before) : undefined))
      .orderBy(desc(auditEvents.occurredAt)).limit(limit));
    return rows.map((r) => {
      const h = this.undo.get(r.action);
      const undo = !h || r.before === null ? "nee" : !admin.permissions.includes(h.permission) ? "geen-recht" : !r.latest ? "verouderd" : "ja";
      return { id: r.id, at: r.at.toISOString(), actor: r.actor, action: r.action, subject: r.subject, label: h?.label ?? null, before: r.before, after: r.after, undo };
    });
  }

  /** Zet de toestand van vóór deze wijziging terug. Alleen als er daarna niets meer aan hetzelfde is gewijzigd. */
  async revert(id: string, admin: AdminPrincipal): Promise<void> {
    let handler: ReturnType<UndoRegistry["get"]>;
    await withTenant(this.db, this.tenant, async (tx) => {
      const [row] = await tx.select().from(auditEvents).where(and(eq(auditEvents.tenantId, this.tenant), eq(auditEvents.id, id))).limit(1);
      if (!row) throw new ChangesError("not_found", "Onbekende wijziging");
      handler = this.undo.get(row.action);
      if (!handler || row.before === null) throw new ChangesError("not_undoable", "Deze wijziging kan niet ongedaan worden gemaakt");
      if (!admin.permissions.includes(handler.permission)) throw new ChangesError("forbidden", "Je hebt niet het recht om dit terug te zetten");
      const [later] = await tx.select({ id: auditEvents.id }).from(auditEvents)
        .where(and(eq(auditEvents.tenantId, this.tenant), eq(auditEvents.subject, row.subject), sql`${auditEvents.occurredAt} > ${row.occurredAt}`)).limit(1);
      if (later) throw new ChangesError("outdated", "Er is daarna nog iets aan gewijzigd; maak eerst die wijziging ongedaan");
      await handler.apply(tx, this.tenant, row.subject, row.before);
      await this.audit.record(tx, this.tenant, { actor: admin.subject, action: `undo:${row.action}`, subject: row.subject, before: row.after, after: row.before });
    });
    await handler!.afterCommit?.();
  }
}
