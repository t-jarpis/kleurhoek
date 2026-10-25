import { Inject, Injectable } from "@nestjs/common";
import { and, count, eq, lt, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { DeliverabilityService } from "./deliverability/deliverability.service";
import { deliveries, subscribers } from "./messaging.schema";
import { SYSTEM_TEMPLATES, TOPICS, type Topic } from "./messaging.types";
import { bump } from "./stats";
import { hashToken, newConfirmToken, readPreferenceToken } from "./tokens";

export type Subscriber = typeof subscribers.$inferSelect;
export const normEmail = (e: string) => e.trim().toLowerCase();
const onlyTopics = (t: string[]) => TOPICS.filter((x) => t.includes(x));
/** Zo lang mag een aanmelding onbevestigd blijven. */
const PENDING_DAYS = 7;

/** Gemaskeerd adres voor de voorkeurenpagina: a***@voorbeeld.nl. */
export const maskEmail = (e: string) => e.replace(/^(.)[^@]*(@.*)$/, "$1***$2");

/**
 * Abonnees (ADR 0037). Aanmelden met bevestiging; een actief abonnement verandert nooit zonder bevestiging of
 * geldige voorkeurlink. Antwoorden verraden niet of een adres al bekend is.
 */
@Injectable()
export class SubscribersService {
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env, private readonly delivery: DeliverabilityService) {}
  private get tenant() { return this.env.TENANT_ID; }

  /**
   * Aanmelden via de site. Nieuw of nog onbevestigd: een bevestigingsmail (hooguit eens per 10 minuten).
   * Al actief: niets (de mail zou anders te misbruiken zijn om iemands onderwerpen te wijzigen).
   */
  async subscribe(input: { email: string; market: string; topics: Topic[] }, now = new Date()): Promise<void> {
    const email = normEmail(input.email);
    const topics = onlyTopics(input.topics);
    if (!topics.length) return;
    // Hard gebounced of gepauzeerd: een bevestigingsmail komt toch niet aan (ADR 0038). Na een klacht wel: wie zich
    // bewust opnieuw aanmeldt en bevestigt, komt van de lijst.
    const blocked = await this.delivery.suppressed(email, now);
    if (blocked && blocked !== "complaint") return;
    await withTenant(this.db, this.tenant, async (tx) => {
      const [existing] = await tx.select().from(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.organization, "kleurhoek"), eq(subscribers.email, email))).limit(1);
      if (existing?.status === "active") return;
      if (existing?.confirmSentAt && now.getTime() - existing.confirmSentAt.getTime() < 10 * 60_000) return;
      const { token, hash } = newConfirmToken();
      const values = { market: input.market, topics, confirmTokenHash: hash, confirmSentAt: now, consentAt: now, updatedAt: now };
      const [row] = existing
        ? await tx.update(subscribers).set(values).where(eq(subscribers.id, existing.id)).returning({ id: subscribers.id })
        : await tx.insert(subscribers).values({ tenantId: this.tenant, email, status: "pending", ...values }).returning({ id: subscribers.id });
      await tx.insert(deliveries).values({ tenantId: this.tenant, subscriberId: row!.id, source: `system:confirm:${now.getTime()}`, template: SYSTEM_TEMPLATES.confirm, transactional: true, context: { token } });
    });
  }

  /** Bevestigen met het token uit de mail. Geeft de abonnee terug als dat nu gebeurde (voor de welkomstworkflow). */
  async confirm(token: string, now = new Date()): Promise<Subscriber | null> {
    if (!/^[A-Za-z0-9_-]{20,64}$/.test(token)) return null;
    return withTenant(this.db, this.tenant, async (tx) => {
      const [row] = await tx.update(subscribers).set({ status: "active", confirmedAt: now, confirmTokenHash: null, updatedAt: now })
        .where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.confirmTokenHash, hashToken(token)), eq(subscribers.status, "pending"), sql`${subscribers.confirmSentAt} > ${new Date(now.getTime() - PENDING_DAYS * 86_400_000)}`))
        .returning();
      if (row) await bump(tx, this.tenant, "subscribed", 1, now);
      return row ?? null;
    }).then(async (row) => { if (row) await this.delivery.unsuppress(row.email, ["complaint"]); return row; });
  }

  /** Abonnee bij een voorkeurlink. */
  async byToken(token: string): Promise<Subscriber | null> {
    const id = readPreferenceToken(this.env.MAIL_SECRET, token);
    if (!id) return null;
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select().from(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.id, id))).limit(1));
    return row?.status === "active" ? row : null;
  }

  /** Onderwerpen of markt wijzigen; geen onderwerpen meer = afmelden. */
  async update(id: string, change: { topics: Topic[]; market?: string | undefined }): Promise<"updated" | "removed"> {
    const topics = onlyTopics(change.topics);
    if (!topics.length) { await this.remove(id); return "removed"; }
    await withTenant(this.db, this.tenant, (tx) => tx.update(subscribers).set({ topics, ...(change.market ? { market: change.market } : {}), updatedAt: new Date() })
      .where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.id, id))));
    return "updated";
  }

  /** Afmelden: de rij verdwijnt, met de wachtrij en workflows van deze abonnee. Alleen de teller blijft. */
  async remove(id: string, metric = "unsubscribed"): Promise<boolean> {
    return withTenant(this.db, this.tenant, async (tx) => {
      const rows = await tx.delete(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.id, id))).returning({ status: subscribers.status });
      if (rows[0]?.status === "active") await bump(tx, this.tenant, metric);
      return rows.length > 0;
    });
  }

  // ---------- Websiteaccount (Account › Mail) ----------

  async forUser(userId: string): Promise<Subscriber | null> {
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select().from(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.userId, userId))).limit(1));
    return row ?? null;
  }

  /**
   * Aanmelden vanuit het account: het adres is bij het inloggen al bevestigd, dus meteen actief.
   * Geeft de abonnee terug als hij nieuw actief werd (voor de welkomstworkflow).
   */
  async setForUser(userId: string, email: string, market: string, topicsIn: Topic[], now = new Date()): Promise<{ subscriber: Subscriber | null; started: boolean }> {
    const topics = onlyTopics(topicsIn);
    const mine = await this.forUser(userId);
    // Bewust aangezet vanuit het account, met een adres dat bij het inloggen werkte: van de blokkeerlijst af.
    if (topics.length) await this.delivery.unsuppress(email, ["hard_bounce", "soft_bounce", "complaint"]);
    if (!topics.length) { if (mine) await this.remove(mine.id); return { subscriber: null, started: false }; }
    return withTenant(this.db, this.tenant, async (tx) => {
      const addr = normEmail(email);
      const [same] = mine ? [mine] : await tx.select().from(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.organization, "kleurhoek"), eq(subscribers.email, addr))).limit(1);
      const started = same?.status !== "active";
      const values = { email: addr, market, topics, status: "active" as const, userId, confirmTokenHash: null, confirmedAt: same?.confirmedAt ?? now, consentAt: same?.consentAt ?? now, updatedAt: now };
      const [row] = same
        ? await tx.update(subscribers).set(values).where(eq(subscribers.id, same.id)).returning()
        : await tx.insert(subscribers).values({ tenantId: this.tenant, ...values }).returning();
      if (started) await bump(tx, this.tenant, "subscribed", 1, now);
      return { subscriber: row!, started };
    });
  }

  /** Account verwijderd: ook het abonnement (privacy, ADR 0002). */
  async forgetUser(userId: string) {
    const mine = await this.forUser(userId);
    if (mine) await this.remove(mine.id);
  }

  // ---------- Onderhoud en beheer ----------

  /** Onbevestigde aanmeldingen opruimen. */
  async purgePending(now = new Date()) {
    await withTenant(this.db, this.tenant, (tx) => tx.delete(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.status, "pending"), lt(subscribers.consentAt, new Date(now.getTime() - PENDING_DAYS * 86_400_000)))));
  }

  /** Aantallen voor het overzicht; geen adressen. */
  async counts() {
    return withTenant(this.db, this.tenant, async (tx) => {
      const byStatus = await tx.select({ status: subscribers.status, n: count() }).from(subscribers).where(eq(subscribers.tenantId, this.tenant)).groupBy(subscribers.status);
      const byTopic = await tx.select({ topic: sql<string>`unnest(${subscribers.topics})`, n: sql<number>`count(*)::int` }).from(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.status, "active"))).groupBy(sql`1`);
      const byMarket = await tx.select({ market: subscribers.market, n: count() }).from(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.status, "active"))).groupBy(subscribers.market);
      return {
        active: byStatus.find((s) => s.status === "active")?.n ?? 0, pending: byStatus.find((s) => s.status === "pending")?.n ?? 0,
        byTopic: Object.fromEntries(byTopic.map((t) => [t.topic, t.n])), byMarket: Object.fromEntries(byMarket.map((m) => [m.market, m.n])),
      };
    });
  }

  /** Eén adres opzoeken (op exact adres; geen lijst om door te bladeren). */
  async find(email: string) {
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select({
      id: subscribers.id, email: subscribers.email, market: subscribers.market, topics: subscribers.topics, status: subscribers.status,
      viaAccount: sql<boolean>`${subscribers.userId} is not null`, consentAt: subscribers.consentAt, confirmedAt: subscribers.confirmedAt,
    }).from(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.email, normEmail(email)))).limit(1));
    return row ?? null;
  }
}
