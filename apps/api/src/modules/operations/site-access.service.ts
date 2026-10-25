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

export interface SiteAccessState { enabled: boolean; entries: SiteAccessEntry[]; loginEnabled: boolean; updatedBy: string; updatedAt: string }

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
    if (!row) return { enabled: false, entries: [], loginEnabled: true, updatedBy: "systeem", updatedAt: new Date(0).toISOString() };
    return { enabled: row.enabled, entries: row.entries, loginEnabled: row.loginEnabled, updatedBy: row.updatedBy, updatedAt: row.updatedAt.toISOString() };
  }

  /** Staat inloggen op de website aan? (Kort in het geheugen: elke organisatie vraagt dit bij elke websitepagina.) */
  private loginCache: { value: boolean; at: number } | null = null;
  async loginEnabled(): Promise<boolean> {
    if (this.loginCache && Date.now() - this.loginCache.at < 5_000) return this.loginCache.value;
    const value = (await this.get()).loginEnabled;
    this.loginCache = { value, at: Date.now() };
    return value;
  }

  /** Slaat de nieuwe stand op en legt de wijziging vast in het auditlog, in dezelfde transactie. */
  async update(change: { enabled?: boolean | undefined; entries?: { cidr: string; label: string }[] | undefined; loginEnabled?: boolean | undefined }, actor: string): Promise<SiteAccessState> {
    const tenantId = this.env.TENANT_ID;
    const before = await this.get();
    const now = new Date().toISOString();
    const entries = change.entries === undefined ? before.entries : change.entries.map((e) => {
      const cidr = normalizeCidr(e.cidr)!;
      const existing = before.entries.find((b) => b.cidr === cidr);
      return existing ? { ...existing, label: e.label } : { cidr, label: e.label, addedBy: actor, addedAt: now };
    });
    const enabled = change.enabled ?? before.enabled;
    const loginEnabled = change.loginEnabled ?? before.loginEnabled;
    await withTenant(this.db, tenantId, async (tx) => {
      await tx.insert(siteAccess).values({ tenantId, enabled, entries, loginEnabled, updatedBy: actor })
        .onConflictDoUpdate({ target: siteAccess.tenantId, set: { enabled, entries, loginEnabled, updatedBy: actor, updatedAt: new Date() } });
      await this.audit.record(tx, tenantId, {
        actor, action: change.loginEnabled !== undefined && change.loginEnabled !== before.loginEnabled ? "operations.login.update" : "operations.access.update", subject: "site_access",
        before: { enabled: before.enabled, cidrs: before.entries.map((e) => e.cidr), loginEnabled: before.loginEnabled },
        after: { enabled, cidrs: entries.map((e) => e.cidr), loginEnabled },
      });
    });
    this.loginCache = null;
    return this.get();
  }
}
