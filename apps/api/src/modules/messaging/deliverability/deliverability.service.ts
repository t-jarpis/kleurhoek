import { createHmac, timingSafeEqual } from "node:crypto";
import { Inject, Injectable, Logger } from "@nestjs/common";
import { and, desc, eq, gte, isNotNull, isNull, lt, or, sql } from "drizzle-orm";
import { ENV, type Env } from "../../../config/env";
import { DB, type Database, type Tx } from "../../../db/database";
import { withTenant } from "../../../db/tenant";
import { deliveries, deliveryEvents, subscribers, suppressions, type DeliveryEventType } from "../messaging.schema";
import { bump } from "../stats";
import { domainOf, parseFeedback, PROVIDERS, type Feedback, type Provider } from "./feedback";

/** Na zoveel soft bounces (zonder aflevering ertussen) binnen 30 dagen stoppen we tijdelijk. */
export const SOFT_LIMIT = 3;
const SOFT_PAUSE_DAYS = 90;
const KEEP_EVENTS_DAYS = 180;
/** Grenzen voor de gezondheid (gangbare eisen van Gmail en Yahoo voor bulkverzenders). */
export const LIMITS = { bounce: { warn: 0.02, bad: 0.05 }, complaint: { warn: 0.001, bad: 0.003 } };

type Health = "goed" | "let op" | "slecht" | "te weinig";
const health = (rate: number, sent: number, l: { warn: number; bad: number }): Health => (sent < 50 ? "te weinig" : rate >= l.bad ? "slecht" : rate >= l.warn ? "let op" : "goed");

/**
 * Bezorging (ADR 0038): meldingen over afgeleverde, gebouncede en als spam gemelde mails, uit elke bron, en wat we
 * ermee doen. Harde bounce of klacht: abonnee weg en adres geblokkeerd; herhaalde soft bounce: 90 dagen pauze.
 * Inzicht per dag, mailprovider en bron staat in het eigen admin panel; de relay is alleen een doorgeefluik.
 */
@Injectable()
export class DeliverabilityService {
  private readonly log = new Logger("Bezorging");

  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env) {}
  private get tenant() { return this.env.TENANT_ID; }

  /** Hash van een adres met een geheim: de lijsten bevatten zo geen adressen en zijn niet terug te rekenen. */
  hash(email: string) { return createHmac("sha256", this.env.MAIL_SECRET).update(`addr:${email.trim().toLowerCase()}`).digest("hex"); }

  /** Sleutel in het webhookadres per bron. */
  webhookKey(provider: Provider) { return createHmac("sha256", this.env.MAIL_SECRET).update(`webhook:${provider}`).digest("base64url").slice(0, 32); }
  webhookUrls() {
    const site = this.env.SITE_URL.replace(/\/$/, "");
    return Object.fromEntries(PROVIDERS.map((p) => [p, `${site}/mail/events/${p}?key=${this.webhookKey(p)}`])) as Record<Provider, string>;
  }
  keyValid(provider: Provider, key: string | undefined) {
    const want = this.webhookKey(provider);
    return typeof key === "string" && key.length === want.length && timingSafeEqual(Buffer.from(key), Buffer.from(want));
  }

  // ---------- Blokkeerlijst ----------

  /** Geblokkeerd? Geeft de reden, of null. */
  async suppressed(email: string, now = new Date()): Promise<string | null> {
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select({ reason: suppressions.reason }).from(suppressions)
      .where(and(eq(suppressions.tenantId, this.tenant), eq(suppressions.emailHash, this.hash(email)), or(isNull(suppressions.expiresAt), gte(suppressions.expiresAt, now)))).limit(1));
    return row?.reason ?? null;
  }

  private async suppressTx(tx: Tx, email: string, reason: "hard_bounce" | "soft_bounce" | "complaint" | "manual", detail: string | null, by: string, expiresAt: Date | null) {
    await tx.insert(suppressions).values({ tenantId: this.tenant, emailHash: this.hash(email), domain: domainOf(email), reason, detail, expiresAt, createdBy: by })
      .onConflictDoUpdate({ target: [suppressions.tenantId, suppressions.emailHash], set: { reason, detail, expiresAt, createdBy: by, updatedAt: new Date() } });
  }

  async suppress(email: string, by: string, detail: string | null = null) {
    await withTenant(this.db, this.tenant, async (tx) => {
      await this.suppressTx(tx, email, "manual", detail, by, null);
      await this.dropSubscriber(tx, email, "suppressed");
    });
  }

  /** Van de lijst halen (beheer, of iemand meldt zich bewust opnieuw aan). Geeft de oude reden. */
  async unsuppress(email: string, only?: ("hard_bounce" | "soft_bounce" | "complaint" | "manual")[]): Promise<string | null> {
    return withTenant(this.db, this.tenant, async (tx) => {
      const rows = await tx.delete(suppressions).where(and(eq(suppressions.tenantId, this.tenant), eq(suppressions.emailHash, this.hash(email)),
        ...(only ? [sql`${suppressions.reason} in (${sql.join(only.map((r) => sql`${r}`), sql`, `)})`] : []))).returning({ reason: suppressions.reason });
      return rows[0]?.reason ?? null;
    });
  }

  private async dropSubscriber(tx: Tx, email: string, metric: string) {
    const rows = await tx.delete(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.email, email))).returning({ status: subscribers.status });
    if (rows.some((r) => r.status === "active")) await bump(tx, this.tenant, metric);
  }

  // ---------- Meldingen ----------

  /** Een mail is afgegeven aan SMTP. */
  async sent(tx: Tx, d: { id: string; source: string; template: string }, email: string, now: Date) {
    await tx.insert(deliveryEvents).values({ tenantId: this.tenant, type: "sent", provider: "smtp", emailHash: this.hash(email), domain: domainOf(email), deliveryId: d.id, source: d.source, template: d.template, occurredAt: now });
  }

  /** Webhook van een relay. Geeft terug wat er verwerkt is; een bevestigingslink (Scaleway) wordt gevolgd. */
  async ingest(provider: Provider, body: unknown): Promise<{ processed: number; ignored: number; confirmed?: boolean }> {
    const parsed = parseFeedback(provider, body);
    if ("confirmUrl" in parsed) {
      const res = await fetch(parsed.confirmUrl, { redirect: "error", signal: AbortSignal.timeout(10_000) }).catch(() => null);
      this.log.log(`Webhook ${provider} bevestigd: ${res?.ok ? "ja" : "nee"}`);
      return { processed: 0, ignored: 0, confirmed: Boolean(res?.ok) };
    }
    for (const f of parsed.events) await this.apply(provider, f);
    return { processed: parsed.events.length, ignored: parsed.ignored };
  }

  /** Eén melding vastleggen en afhandelen. */
  async apply(provider: Provider | "smtp", f: Feedback) {
    await withTenant(this.db, this.tenant, async (tx) => {
      const delivery = await this.findDelivery(tx, f);
      await tx.insert(deliveryEvents).values({
        tenantId: this.tenant, type: f.type as DeliveryEventType, provider, emailHash: this.hash(f.email), domain: domainOf(f.email),
        deliveryId: delivery?.id ?? null, source: delivery?.source ?? null, template: delivery?.template ?? null, reason: f.reason, occurredAt: f.occurredAt,
      });
      await bump(tx, this.tenant, `mail_${f.type}`, 1, f.occurredAt);
      if (f.type === "hard_bounce" || f.type === "complaint") {
        await this.suppressTx(tx, f.email, f.type, f.reason, provider, null);
        await this.dropSubscriber(tx, f.email, f.type === "complaint" ? "complained" : "bounced");
      } else if (f.type === "soft_bounce") {
        const since = new Date(f.occurredAt.getTime() - 30 * 86_400_000);
        const recent = await tx.select({ type: deliveryEvents.type }).from(deliveryEvents)
          .where(and(eq(deliveryEvents.tenantId, this.tenant), eq(deliveryEvents.emailHash, this.hash(f.email)), gte(deliveryEvents.occurredAt, since), sql`${deliveryEvents.type} in ('soft_bounce', 'delivered')`))
          .orderBy(desc(deliveryEvents.occurredAt)).limit(SOFT_LIMIT);
        if (recent.length >= SOFT_LIMIT && recent.every((r) => r.type === "soft_bounce")) {
          await this.suppressTx(tx, f.email, "soft_bounce", f.reason, provider, new Date(f.occurredAt.getTime() + SOFT_PAUSE_DAYS * 86_400_000));
          await this.dropSubscriber(tx, f.email, "bounced");
        }
      } else if (f.type === "unsubscribe") {
        await this.dropSubscriber(tx, f.email, "unsubscribed");
      }
    });
  }

  /** De mail bij een melding: op onze verwijzing, dan op Message-ID, dan de laatste mail aan dit adres (14 dagen). */
  private async findDelivery(tx: Tx, f: Feedback) {
    const cols = { id: deliveries.id, source: deliveries.source, template: deliveries.template };
    if (f.ref) { const [d] = await tx.select(cols).from(deliveries).where(and(eq(deliveries.tenantId, this.tenant), eq(deliveries.id, f.ref))).limit(1); if (d) return d; }
    if (f.messageId) { const [d] = await tx.select(cols).from(deliveries).where(and(eq(deliveries.tenantId, this.tenant), eq(deliveries.messageId, f.messageId))).limit(1); if (d) return d; }
    const [e] = await tx.select({ id: deliveryEvents.deliveryId, source: deliveryEvents.source, template: deliveryEvents.template }).from(deliveryEvents)
      .where(and(eq(deliveryEvents.tenantId, this.tenant), eq(deliveryEvents.emailHash, this.hash(f.email)), eq(deliveryEvents.type, "sent"), isNotNull(deliveryEvents.deliveryId), gte(deliveryEvents.occurredAt, new Date(f.occurredAt.getTime() - 14 * 86_400_000))))
      .orderBy(desc(deliveryEvents.occurredAt)).limit(1);
    return e?.id ? { id: e.id, source: e.source ?? "", template: e.template ?? "" } : null;
  }

  // ---------- Inzicht ----------

  async report(days: number, now = new Date()) {
    const from = new Date(now.getTime() - days * 86_400_000);
    return withTenant(this.db, this.tenant, async (tx) => {
      const where = and(eq(deliveryEvents.tenantId, this.tenant), gte(deliveryEvents.occurredAt, from));
      const n = (t: string) => sql<number>`count(*) filter (where ${deliveryEvents.type} = ${t})::int`;
      const counts = { sent: n("sent"), delivered: n("delivered"), deferred: n("deferred"), soft: n("soft_bounce"), hard: n("hard_bounce"), complaints: n("complaint"), unsubscribes: n("unsubscribe") };
      const [totals] = await tx.select(counts).from(deliveryEvents).where(where);
      const daily = await tx.select({ day: sql<string>`to_char(${deliveryEvents.occurredAt} at time zone 'Europe/Amsterdam', 'YYYY-MM-DD')`, ...counts }).from(deliveryEvents).where(where).groupBy(sql`1`).orderBy(sql`1`);
      const byDomain = await tx.select({ domain: deliveryEvents.domain, ...counts }).from(deliveryEvents).where(where).groupBy(deliveryEvents.domain).orderBy(desc(n("sent"))).limit(12);
      const bySource = await tx.select({ source: deliveryEvents.source, template: sql<string | null>`max(${deliveryEvents.template})`, ...counts }).from(deliveryEvents).where(and(where, isNotNull(deliveryEvents.source))).groupBy(deliveryEvents.source).orderBy(desc(n("sent"))).limit(20);
      const recent = await tx.select({ type: deliveryEvents.type, provider: deliveryEvents.provider, domain: deliveryEvents.domain, source: deliveryEvents.source, template: deliveryEvents.template, reason: deliveryEvents.reason, at: deliveryEvents.occurredAt })
        .from(deliveryEvents).where(and(where, sql`${deliveryEvents.type} in ('soft_bounce', 'hard_bounce', 'complaint', 'unsubscribe', 'deferred')`)).orderBy(desc(deliveryEvents.occurredAt)).limit(50);
      const providers = await tx.select({ provider: deliveryEvents.provider, last: sql<string>`max(${deliveryEvents.occurredAt})`, n: sql<number>`count(*)::int` }).from(deliveryEvents)
        .where(and(eq(deliveryEvents.tenantId, this.tenant), sql`${deliveryEvents.provider} <> 'smtp'`)).groupBy(deliveryEvents.provider);
      const blocked = await tx.select({ reason: suppressions.reason, n: sql<number>`count(*)::int` }).from(suppressions)
        .where(and(eq(suppressions.tenantId, this.tenant), or(isNull(suppressions.expiresAt), gte(suppressions.expiresAt, now)))).groupBy(suppressions.reason);
      const t = totals!;
      const bounceRate = t.sent ? (t.hard + t.soft) / t.sent : 0;
      const complaintRate = t.sent ? t.complaints / t.sent : 0;
      return {
        days, totals: t, daily, byDomain, bySource, recent, limits: LIMITS,
        rates: { bounce: bounceRate, complaint: complaintRate, delivered: t.sent ? t.delivered / t.sent : null },
        health: { bounce: health(bounceRate, t.sent, LIMITS.bounce), complaint: health(complaintRate, t.sent, LIMITS.complaint) },
        providers: Object.fromEntries(providers.map((p) => [p.provider, { last: p.last, events: p.n }])),
        suppressed: Object.fromEntries(blocked.map((b) => [b.reason, b.n])),
      };
    });
  }

  /** Stand van één adres (beheer, op exact adres). */
  async lookup(email: string, now = new Date()) {
    const h = this.hash(email);
    return withTenant(this.db, this.tenant, async (tx) => {
      const [s] = await tx.select({ reason: suppressions.reason, detail: suppressions.detail, since: suppressions.createdAt, expiresAt: suppressions.expiresAt, by: suppressions.createdBy }).from(suppressions)
        .where(and(eq(suppressions.tenantId, this.tenant), eq(suppressions.emailHash, h))).limit(1);
      const events = await tx.select({ type: deliveryEvents.type, provider: deliveryEvents.provider, source: deliveryEvents.source, reason: deliveryEvents.reason, at: deliveryEvents.occurredAt })
        .from(deliveryEvents).where(and(eq(deliveryEvents.tenantId, this.tenant), eq(deliveryEvents.emailHash, h))).orderBy(desc(deliveryEvents.occurredAt)).limit(30);
      return { suppression: s && (!s.expiresAt || s.expiresAt > now) ? s : null, events };
    });
  }

  /** Oude meldingen en verlopen blokkades opruimen. */
  async purge(now = new Date()) {
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.delete(deliveryEvents).where(and(eq(deliveryEvents.tenantId, this.tenant), lt(deliveryEvents.occurredAt, new Date(now.getTime() - KEEP_EVENTS_DAYS * 86_400_000))));
      await tx.delete(suppressions).where(and(eq(suppressions.tenantId, this.tenant), isNotNull(suppressions.expiresAt), lt(suppressions.expiresAt, now)));
    });
  }
}
