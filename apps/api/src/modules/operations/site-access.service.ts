import { BlockList, isIP } from "node:net";
import { Inject, Injectable } from "@nestjs/common";
import { eq } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { AuditService } from "../identity/audit.service";
import { siteAccess, type SiteAccessEntry } from "./operations.schema";

export const MAX_ENTRIES = 50;

/** Normaliseert "1.2.3.4", "1.2.3.0/24", "2a02:a:b::1" of "2a02:a:b::/64" tot een CIDR, of null als het ongeldig is. */
export function normalizeCidr(input: string): string | null {
  const [addr = "", bits, ...rest] = input.trim().split("/");
  if (rest.length) return null;
  const family = isIP(addr);
  if (!family) return null;
  const max = family === 4 ? 32 : 128;
  const prefix = bits === undefined ? max : Number(bits);
  if (!Number.isInteger(prefix) || prefix < (family === 4 ? 8 : 32) || prefix > max || (bits !== undefined && !/^\d+$/.test(bits))) return null;
  const list = new BlockList();
  try { list.addSubnet(addr, prefix, family === 4 ? "ipv4" : "ipv6"); } catch { return null; }
  return `${addr.toLowerCase()}/${prefix}`;
}

export interface SiteAccessState { enabled: boolean; entries: SiteAccessEntry[]; updatedBy: string; updatedAt: string }

@Injectable()
export class SiteAccessService {
  constructor(
    @Inject(DB) private readonly db: Database,
    @Inject(ENV) private readonly env: Env,
    private readonly audit: AuditService,
  ) {}

  async get(): Promise<SiteAccessState> {
    const tenantId = this.env.TENANT_ID;
    const [row] = await withTenant(this.db, tenantId, (tx) => tx.select().from(siteAccess).where(eq(siteAccess.tenantId, tenantId)).limit(1));
    if (!row) return { enabled: false, entries: [], updatedBy: "systeem", updatedAt: new Date(0).toISOString() };
    return { enabled: row.enabled, entries: row.entries, updatedBy: row.updatedBy, updatedAt: row.updatedAt.toISOString() };
  }

  /** Slaat de nieuwe stand op en legt de wijziging vast in het auditlog, in dezelfde transactie. */
  async update(change: { enabled?: boolean | undefined; entries?: { cidr: string; label: string }[] | undefined }, actor: string): Promise<SiteAccessState> {
    const tenantId = this.env.TENANT_ID;
    const before = await this.get();
    const now = new Date().toISOString();
    const entries = change.entries === undefined ? before.entries : change.entries.map((e) => {
      const cidr = normalizeCidr(e.cidr)!;
      const existing = before.entries.find((b) => b.cidr === cidr);
      return existing ? { ...existing, label: e.label } : { cidr, label: e.label, addedBy: actor, addedAt: now };
    });
    const enabled = change.enabled ?? before.enabled;
    await withTenant(this.db, tenantId, async (tx) => {
      await tx.insert(siteAccess).values({ tenantId, enabled, entries, updatedBy: actor })
        .onConflictDoUpdate({ target: siteAccess.tenantId, set: { enabled, entries, updatedBy: actor, updatedAt: new Date() } });
      await this.audit.record(tx, tenantId, {
        actor, action: "operations.access.update", subject: "site_access",
        before: { enabled: before.enabled, cidrs: before.entries.map((e) => e.cidr) },
        after: { enabled, cidrs: entries.map((e) => e.cidr) },
      });
    });
    return this.get();
  }
}
