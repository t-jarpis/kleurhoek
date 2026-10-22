import { Injectable } from "@nestjs/common";
import { auditEvents } from "./identity.schema";
import type { Tx } from "../../db/database";

@Injectable()
export class AuditService {
  /** Schrijft een audit-event binnen de transactie van de wijziging zelf: geen wijziging zonder spoor. */
  async record(tx: Tx, tenantId: string, e: { actor: string; action: string; subject: string; before?: unknown; after?: unknown }) {
    await tx.insert(auditEvents).values({ tenantId, actor: e.actor, action: e.action, subject: e.subject, before: e.before ?? null, after: e.after ?? null });
  }
}
