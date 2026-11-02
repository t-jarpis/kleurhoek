import { Injectable } from "@nestjs/common";
import type { Tx } from "../../db/database";
import type { Permission } from "./permissions";

/**
 * Ongedaan maken (ADR 0066). Een domein meldt hier per auditactie hoe hij de toestand van vóór de wijziging
 * terugzet. Identity bewaakt de rest: alleen de laatste wijziging van iets, alleen met het recht van dat domein,
 * en het terugzetten komt zelf ook in het auditlog. `apply` draait in de transactie van het ongedaan maken.
 */
export interface UndoHandler {
  permission: Permission;
  /** Wat er gewijzigd is, voor in het admin panel ("Vindbaarheid", "Rate limit"). */
  label: string;
  apply(tx: Tx, tenantId: string, subject: string, before: unknown): Promise<void>;
  /** Na de transactie, bijvoorbeeld een cache verversen. */
  afterCommit?(): Promise<void>;
}

@Injectable()
export class UndoRegistry {
  private readonly handlers = new Map<string, UndoHandler>();
  register(action: string, handler: UndoHandler) { this.handlers.set(action, handler); }
  get(action: string): UndoHandler | undefined { return this.handlers.get(action); }
}
