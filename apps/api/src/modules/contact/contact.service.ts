import { Inject, Injectable } from "@nestjs/common";
import { and, asc, count, desc, eq, inArray, lt } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { AuditService } from "../identity/audit.service";
import { channels, conversations, messages, STATUSES, type Channel, type ConversationStatus, type Topic } from "./contact.schema";

export class ContactError extends Error {
  constructor(readonly code: "not_found" | "invalid" | "closed", message: string) { super(message); }
}

/** Bewaartermijn: 12 maanden na het laatste bericht (ADR 0024). */
export const RETENTION_DAYS = 365;
const PAGE_SIZE = 50;

export interface ChannelView { slug: Channel; enabled: boolean; connected: boolean; settings: Record<string, string>; updatedBy: string; updatedAt: string | null }

/**
 * Domein Contact: berichten van bezoekers via kanalen (nu het webformulier, later WhatsApp), met een
 * inbox in het admin panel. Persoonsgegevens blijven in dit domein en gaan niet naar analytics of audit.
 */
@Injectable()
export class ContactService {
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env, private readonly audit: AuditService) {}

  private get tenant() { return this.env.TENANT_ID; }

  /** Een nieuw bericht via een kanaal. Geeft het id van het gesprek. */
  async submit(channel: Channel, input: { topic: Topic; name: string | null; email: string | null; phone?: string | null; message: string; org: string; market: string }) {
    if (!(await this.channelEnabled(channel))) throw new ContactError("closed", "Dit kanaal staat uit");
    return withTenant(this.db, this.tenant, async (tx) => {
      const [c] = await tx.insert(conversations).values({
        tenantId: this.tenant, channel, topic: input.topic, name: input.name, email: input.email, phone: input.phone ?? null,
        org: input.org, market: input.market,
      }).returning({ id: conversations.id });
      await tx.insert(messages).values({ tenantId: this.tenant, conversationId: c!.id, direction: "in", body: input.message });
      return c!.id;
    });
  }

  async inbox(filter: { status?: ConversationStatus | undefined; page?: number | undefined }) {
    const page = Math.max(1, filter.page ?? 1);
    return withTenant(this.db, this.tenant, async (tx) => {
      const where = filter.status ? eq(conversations.status, filter.status) : undefined;
      const rows = await tx.select().from(conversations).where(where).orderBy(desc(conversations.lastMessageAt)).limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE);
      const firsts = rows.length ? await tx.select({ conversationId: messages.conversationId, body: messages.body, createdAt: messages.createdAt })
        .from(messages).where(and(inArray(messages.conversationId, rows.map((r) => r.id)), eq(messages.direction, "in"))).orderBy(desc(messages.createdAt)) : [];
      const counts = await tx.select({ status: conversations.status, n: count() }).from(conversations).groupBy(conversations.status);
      const byStatus = Object.fromEntries(STATUSES.map((s) => [s, Number(counts.find((c) => c.status === s)?.n ?? 0)])) as Record<ConversationStatus, number>;
      return {
        page, pageSize: PAGE_SIZE, total: filter.status ? byStatus[filter.status] : Object.values(byStatus).reduce((a, b) => a + b, 0), counts: byStatus,
        conversations: rows.map((r) => ({
          id: r.id, channel: r.channel, topic: r.topic, status: r.status, name: r.name, email: r.email, phone: r.phone, org: r.org, market: r.market,
          lastMessageAt: r.lastMessageAt.toISOString(), createdAt: r.createdAt.toISOString(),
          preview: (firsts.find((m) => m.conversationId === r.id)?.body ?? "").slice(0, 160),
        })),
      };
    });
  }

  async conversation(id: string) {
    return withTenant(this.db, this.tenant, async (tx) => {
      const [c] = await tx.select().from(conversations).where(eq(conversations.id, id)).limit(1);
      if (!c) throw new ContactError("not_found", "Gesprek niet gevonden");
      const list = await tx.select().from(messages).where(eq(messages.conversationId, id)).orderBy(asc(messages.createdAt));
      return {
        id: c.id, channel: c.channel, topic: c.topic, status: c.status, name: c.name, email: c.email, phone: c.phone, org: c.org, market: c.market,
        createdAt: c.createdAt.toISOString(), lastMessageAt: c.lastMessageAt.toISOString(), updatedBy: c.updatedBy,
        messages: list.map((m) => ({ id: m.id, direction: m.direction, body: m.body, author: m.author, createdAt: m.createdAt.toISOString() })),
      };
    });
  }

  async setStatus(actor: string, id: string, status: ConversationStatus) {
    await withTenant(this.db, this.tenant, async (tx) => {
      const [before] = await tx.select({ status: conversations.status }).from(conversations).where(eq(conversations.id, id)).limit(1);
      if (!before) throw new ContactError("not_found", "Gesprek niet gevonden");
      await tx.update(conversations).set({ status, updatedBy: actor, updatedAt: new Date() }).where(eq(conversations.id, id));
      await this.audit.record(tx, this.tenant, { actor, action: "contact.status", subject: `conversation:${id}`, before: before.status, after: status });
    });
    return this.conversation(id);
  }

  /**
   * Interne notitie, of een antwoord vastleggen. Bij het webkanaal stuur je het antwoord zelf per e-mail;
   * hier leg je vast wát je antwoordde. Via WhatsApp gaat een antwoord straks ook echt naar buiten.
   */
  async addMessage(actor: string, id: string, direction: "out" | "note", body: string) {
    await withTenant(this.db, this.tenant, async (tx) => {
      const [c] = await tx.select({ status: conversations.status }).from(conversations).where(eq(conversations.id, id)).limit(1);
      if (!c) throw new ContactError("not_found", "Gesprek niet gevonden");
      await tx.insert(messages).values({ tenantId: this.tenant, conversationId: id, direction, body, author: actor });
      const status: ConversationStatus = direction === "out" ? "answered" : c.status === "new" ? "open" : c.status;
      await tx.update(conversations).set({ status, updatedBy: actor, updatedAt: new Date(), ...(direction === "out" ? { lastMessageAt: new Date() } : {}) }).where(eq(conversations.id, id));
      await this.audit.record(tx, this.tenant, { actor, action: direction === "out" ? "contact.reply" : "contact.note", subject: `conversation:${id}` });
    });
    return this.conversation(id);
  }

  /** Gesprek direct verwijderen (bijvoorbeeld op verzoek van de afzender, AVG). */
  async remove(actor: string, id: string) {
    await withTenant(this.db, this.tenant, async (tx) => {
      const [c] = await tx.select({ id: conversations.id }).from(conversations).where(eq(conversations.id, id)).limit(1);
      if (!c) throw new ContactError("not_found", "Gesprek niet gevonden");
      await tx.delete(messages).where(eq(messages.conversationId, id));
      await tx.delete(conversations).where(eq(conversations.id, id));
      await this.audit.record(tx, this.tenant, { actor, action: "contact.deleted", subject: `conversation:${id}` });
    });
  }

  async unreadCount(): Promise<number> {
    const [r] = await withTenant(this.db, this.tenant, (tx) => tx.select({ n: count() }).from(conversations).where(eq(conversations.status, "new")));
    return Number(r?.n ?? 0);
  }

  /** Verwijdert gesprekken waarvan het laatste bericht ouder is dan de bewaartermijn. */
  async purge(now = new Date()): Promise<number> {
    const before = new Date(now.getTime() - RETENTION_DAYS * 86_400_000);
    return withTenant(this.db, this.tenant, async (tx) => {
      const old = await tx.select({ id: conversations.id }).from(conversations).where(lt(conversations.lastMessageAt, before));
      if (!old.length) return 0;
      const ids = old.map((o) => o.id);
      await tx.delete(messages).where(inArray(messages.conversationId, ids));
      await tx.delete(conversations).where(inArray(conversations.id, ids));
      return ids.length;
    });
  }

  /**
   * Of een kanaal technisch gekoppeld is. WhatsApp volgt als eigen stap (ADR 0024): dan komen token en
   * app-geheim in de secret manager en de webhook in de website. Tot die tijd kan hij niet aan.
   */
  private connected(slug: Channel): boolean {
    return slug === "web";
  }

  async channelList(): Promise<ChannelView[]> {
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select().from(channels));
    return (["web", "whatsapp"] as const).map((slug) => {
      const r = rows.find((x) => x.slug === slug);
      return {
        slug, connected: this.connected(slug), enabled: r ? r.enabled && this.connected(slug) : slug === "web",
        settings: r?.settings ?? {}, updatedBy: r?.updatedBy ?? "systeem", updatedAt: r?.updatedAt.toISOString() ?? null,
      };
    });
  }

  async channelEnabled(slug: Channel): Promise<boolean> {
    return (await this.channelList()).find((c) => c.slug === slug)?.enabled ?? false;
  }

  async updateChannel(actor: string, slug: Channel, change: { enabled?: boolean | undefined; settings?: Record<string, string> | undefined }) {
    if (change.enabled && !this.connected(slug)) throw new ContactError("invalid", "Koppel het kanaal eerst (zie de stappen op deze pagina)");
    await withTenant(this.db, this.tenant, async (tx) => {
      const [before] = await tx.select().from(channels).where(eq(channels.slug, slug)).limit(1);
      const next = { enabled: change.enabled ?? before?.enabled ?? slug === "web", settings: change.settings ?? before?.settings ?? {} };
      if (before) await tx.update(channels).set({ ...next, updatedBy: actor, updatedAt: new Date() }).where(eq(channels.slug, slug));
      else await tx.insert(channels).values({ tenantId: this.tenant, slug, ...next, updatedBy: actor });
      await this.audit.record(tx, this.tenant, { actor, action: "contact.channel.updated", subject: `channel:${slug}`, before: before ? { enabled: before.enabled, settings: before.settings } : null, after: next });
    });
    return this.channelList();
  }
}
