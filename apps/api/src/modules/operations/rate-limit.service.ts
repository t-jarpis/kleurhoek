import { createHash } from "node:crypto";
import { Inject, Injectable, Logger, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { and, asc, eq, gte, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { AuditService } from "../identity/audit.service";
import { rateLimits, rateLimitStats } from "./operations.schema";
import { RATE_LIMIT_STORE, type RateLimitStore } from "./rate-limit.store";

export interface RateLimitRule { slug: string; description: string; limit: number; windowSeconds: number; keyBy: "ip" | "user" | "client"; enabled: boolean }
export interface RateLimitDecision { allowed: boolean; limit: number; windowSeconds: number; remaining: number; resetSeconds: number }

/** Standaardregels. Worden bij de start aangemaakt als ze nog niet bestaan; daarna beheerd in het admin panel. */
export const DEFAULT_RULES: RateLimitRule[] = [
  { slug: "public-read", description: "Platen en pagina-data bekijken", limit: 300, windowSeconds: 60, keyBy: "ip", enabled: true },
  { slug: "assets", description: "SVG-bestanden van platen", limit: 600, windowSeconds: 60, keyBy: "ip", enabled: true },
  { slug: "events-ingest", description: "Analytics-events van de Cloudflare Worker", limit: 6000, windowSeconds: 60, keyBy: "client", enabled: true },
  { slug: "contact-challenge", description: "Rekenpuzzel voor het contactformulier", limit: 30, windowSeconds: 3600, keyBy: "ip", enabled: true },
  { slug: "contact-submit", description: "Contactformulier versturen", limit: 5, windowSeconds: 3600, keyBy: "ip", enabled: true },
  { slug: "admin", description: "Admin panel", limit: 120, windowSeconds: 60, keyBy: "user", enabled: true },
  { slug: "api-default", description: "Overige API-verzoeken", limit: 120, windowSeconds: 60, keyBy: "ip", enabled: true },
];

const REFRESH_MS = 30_000;
const FLUSH_MS = 60_000;

@Injectable()
export class RateLimitService implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger(RateLimitService.name);
  private rules = new Map<string, RateLimitRule>(DEFAULT_RULES.map((r) => [r.slug, r]));
  private loadedAt = 0;
  private counters = new Map<string, { allowed: number; blocked: number }>();
  private timer?: NodeJS.Timeout;

  constructor(
    @Inject(DB) private readonly db: Database,
    @Inject(ENV) private readonly env: Env,
    @Inject(RATE_LIMIT_STORE) private readonly store: RateLimitStore,
    private readonly audit: AuditService,
  ) {}

  async onModuleInit() {
    await this.ensureDefaults();
    await this.refresh();
    this.timer = setInterval(() => void this.flush().catch((e) => this.log.error(e)), FLUSH_MS);
    this.timer.unref();
  }

  async onApplicationShutdown() {
    clearInterval(this.timer);
    await this.flush().catch(() => undefined);
  }

  private async ensureDefaults() {
    const tenantId = this.env.TENANT_ID;
    await withTenant(this.db, tenantId, (tx) =>
      tx.insert(rateLimits).values(DEFAULT_RULES.map((r) => ({ tenantId, ...r }))).onConflictDoNothing());
  }

  /** Haalt regels opnieuw op uit de database. Wijzigingen in het admin panel werken binnen 30 seconden. */
  async refresh() {
    const tenantId = this.env.TENANT_ID;
    const rows = await withTenant(this.db, tenantId, (tx) => tx.select().from(rateLimits).where(eq(rateLimits.tenantId, tenantId)));
    this.rules = new Map(rows.map((r) => [r.slug, { slug: r.slug, description: r.description, limit: r.limit, windowSeconds: r.windowSeconds, keyBy: r.keyBy, enabled: r.enabled }]));
    this.loadedAt = Date.now();
  }

  /**
   * Telt een verzoek mee en beslist of het door mag. De sleutel (IP-adres, gebruiker of client)
   * wordt gehasht, zodat er geen ruwe IP-adressen in het geheugen of in Redis staan.
   */
  async check(ruleSlug: string, identity: string, now = Date.now()): Promise<RateLimitDecision | null> {
    if (now - this.loadedAt > REFRESH_MS) await this.refresh().catch((e) => this.log.warn(`Regels verversen mislukt: ${e}`));
    const rule = this.rules.get(ruleSlug) ?? this.rules.get("api-default");
    if (!rule || !rule.enabled) return null;
    const key = `${rule.slug}:${createHash("sha256").update(`${this.env.TENANT_ID}|${identity}`).digest("base64url").slice(0, 22)}`;
    const { count, resetAt } = await this.store.hit(key, rule.windowSeconds * 1000, now);
    const allowed = count <= rule.limit;
    const c = this.counters.get(rule.slug) ?? { allowed: 0, blocked: 0 };
    if (allowed) c.allowed += 1; else c.blocked += 1;
    this.counters.set(rule.slug, c);
    return { allowed, limit: rule.limit, windowSeconds: rule.windowSeconds, remaining: Math.max(0, rule.limit - count), resetSeconds: Math.max(1, Math.ceil((resetAt - now) / 1000)) };
  }

  /** Schrijft de tellers als dagtotalen weg. */
  async flush(now = new Date()) {
    if (!this.counters.size) return;
    const pending = this.counters;
    this.counters = new Map();
    const tenantId = this.env.TENANT_ID;
    const day = now.toISOString().slice(0, 10);
    await withTenant(this.db, tenantId, async (tx) => {
      for (const [ruleSlug, c] of pending) {
        await tx.insert(rateLimitStats).values({ tenantId, day, ruleSlug, allowed: c.allowed, blocked: c.blocked })
          .onConflictDoUpdate({
            target: [rateLimitStats.tenantId, rateLimitStats.day, rateLimitStats.ruleSlug],
            set: { allowed: sql`${rateLimitStats.allowed} + ${c.allowed}`, blocked: sql`${rateLimitStats.blocked} + ${c.blocked}`, updatedAt: sql`now()` },
          });
      }
    });
  }

  /** Voor het admin panel: alle regels met doorgelaten en geblokkeerde verzoeken van de afgelopen dagen. */
  async overview(days = 7, now = new Date()) {
    await this.flush(now);
    const tenantId = this.env.TENANT_ID;
    const from = new Date(now.getTime() - (days - 1) * 86_400_000).toISOString().slice(0, 10);
    return withTenant(this.db, tenantId, async (tx) => {
      const rules = await tx.select().from(rateLimits).where(eq(rateLimits.tenantId, tenantId)).orderBy(asc(rateLimits.slug));
      const stats = await tx.select().from(rateLimitStats).where(and(eq(rateLimitStats.tenantId, tenantId), gte(rateLimitStats.day, from))).orderBy(asc(rateLimitStats.day));
      return rules.map((r) => ({
        slug: r.slug, description: r.description, limit: r.limit, windowSeconds: r.windowSeconds, keyBy: r.keyBy, enabled: r.enabled,
        updatedBy: r.updatedBy, updatedAt: r.updatedAt.toISOString(),
        days: stats.filter((s) => s.ruleSlug === r.slug).map((s) => ({ day: s.day, allowed: s.allowed, blocked: s.blocked })),
      }));
    });
  }

  /** Wijzigt een regel en legt de wijziging vast in het auditlog, in dezelfde transactie. */
  async update(slug: string, change: { limit?: number | undefined; windowSeconds?: number | undefined; enabled?: boolean | undefined }, actor: string) {
    const tenantId = this.env.TENANT_ID;
    const result = await withTenant(this.db, tenantId, async (tx) => {
      const [before] = await tx.select().from(rateLimits).where(and(eq(rateLimits.tenantId, tenantId), eq(rateLimits.slug, slug))).limit(1);
      if (!before) return null;
      const set = Object.fromEntries(Object.entries(change).filter(([, v]) => v !== undefined));
      const [after] = await tx.update(rateLimits).set({ ...set, updatedBy: actor, updatedAt: new Date() })
        .where(eq(rateLimits.id, before.id)).returning();
      await this.audit.record(tx, tenantId, {
        actor, action: "operations.ratelimit.update", subject: `rate_limit:${slug}`,
        before: { limit: before.limit, windowSeconds: before.windowSeconds, enabled: before.enabled },
        after: { limit: after!.limit, windowSeconds: after!.windowSeconds, enabled: after!.enabled },
      });
      return after!;
    });
    if (result) await this.refresh();
    return result;
  }
}
