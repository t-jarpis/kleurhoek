import { Inject, Injectable, Logger } from "@nestjs/common";
import { and, asc, eq, inArray, lt, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { CatalogService } from "../catalog/catalog.service";
import { StorefrontService } from "../storefront/storefront.service";
import { classifySmtpError } from "./deliverability/feedback";
import { DeliverabilityService } from "./deliverability/deliverability.service";
import { MAIL_TRANSPORT, messageIdFor, type MailTransport } from "./mailer";
import { deliveries, subscribers } from "./messaging.schema";
import type { Block, MailContext, Topic } from "./messaging.types";
import { renderMail, type RenderedMail, type RenderPlate } from "./render";
import { bump } from "./stats";
import { TemplatesService, type TemplateInput } from "./templates.service";
import { preferenceToken } from "./tokens";

/** Na zoveel pogingen geven we het op. */
const MAX_ATTEMPTS = 4;
/** Een mail die zo lang wacht (versturen stond uit), gaat niet meer weg: hij is niet meer actueel. */
const EXPIRE_HOURS = 72;

export interface Recipient { id: string; email: string; market: string; topics: Topic[] }

/**
 * Wachtrij en opmaak (ADR 0037). Mails worden pas bij versturen gemaakt, met de platen die op dat moment in de
 * markt van de abonnee zichtbaar zijn. Hooguit MAIL_RATE_PER_MINUTE per minuut; mislukt = later opnieuw.
 */
@Injectable()
export class OutboxService {
  private readonly log = new Logger("Mail");

  constructor(
    @Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env,
    @Inject(MAIL_TRANSPORT) private readonly transport: MailTransport,
    private readonly templates: TemplatesService, private readonly store: StorefrontService, private readonly catalog: CatalogService,
    private readonly delivery: DeliverabilityService,
  ) {}
  private get tenant() { return this.env.TENANT_ID; }

  sending() { return { bulk: this.transport.enabled(false), transactional: this.transport.enabled(true) }; }

  /** Links voor een abonnee. */
  links(r: { id: string; market: string }, context: MailContext = {}) {
    const site = this.env.SITE_URL.replace(/\/$/, "");
    const t = preferenceToken(this.env.MAIL_SECRET, r.id);
    return {
      site: `${site}/${r.market}`,
      preferences: `${site}/${r.market}/mail?t=${t}`,
      unsubscribe: `${site}/${r.market}/mail?t=${t}&afmelden=1`,
      oneClick: `${site}/mail/afmelden?t=${t}`,
      confirm: context.token ? `${site}/${r.market}/mail/bevestigen?t=${context.token}` : undefined,
    };
  }

  /** Platen per platenblok, in de markt van de abonnee. */
  private async platesFor(blocks: Block[], market: string, context: MailContext): Promise<Record<string, RenderPlate[]>> {
    const site = this.env.SITE_URL.replace(/\/$/, "");
    const out: Record<string, RenderPlate[]> = {};
    for (const b of blocks) {
      if (b.type !== "plates") continue;
      let pick: { slugs?: string[]; holiday?: string; since?: Date } = {};
      if (b.source === "new") pick = context.plates ? { slugs: context.plates } : { since: new Date(context.since ?? Date.now() - 14 * 86_400_000) };
      else if (b.source === "holiday") pick = context.holiday ? { holiday: context.holiday } : { slugs: [] };
      else if (b.source === "selected") pick = { slugs: b.slugs ?? [] };
      else pick = { slugs: (await this.catalog.collections(this.tenant)).find((c) => c.slug === b.collection)?.plates ?? [] };
      let plates = await this.store.mailPlates(market, pick, b.max);
      // Niets nieuws sinds de vorige keer: dan de nieuwste platen (een welkomstmail is nooit leeg).
      if (!plates.length && b.source === "new" && !context.plates) plates = await this.store.mailPlates(market, { since: new Date(0) }, b.max);
      out[b.id] = plates.map((p) => ({ name: p.name, url: `${site}/${market}/platen/${p.slug}`, image: `${site}${p.image}` }));
    }
    return out;
  }

  /** Een mail maken voor een abonnee (of een voorbeeld). */
  async compose(template: TemplateInput, r: Recipient, context: MailContext, transactional: boolean): Promise<RenderedMail & { oneClick: string; empty: boolean }> {
    const links = this.links(r, context);
    const plates = await this.platesFor(template.blocks, r.market, context);
    const mail = renderMail({ subject: template.subject, preheader: template.preheader, blocks: template.blocks, language: r.market.slice(0, 2), plates, links, topics: r.topics, transactional });
    // Een mail met platenblokken waarin niets staat (bijvoorbeeld geen feestplaten in deze markt) gaat niet weg.
    const blocks = Object.values(plates);
    return { ...mail, oneClick: links.oneClick, empty: blocks.length > 0 && blocks.every((l) => l.length === 0) };
  }

  /** Wachtrij afwerken: een portie per keer, oudste eerst. */
  async process(now = new Date()): Promise<{ sent: number; failed: number }> {
    await withTenant(this.db, this.tenant, (tx) => tx.update(deliveries).set({ status: "expired", context: {}, updatedAt: now })
      .where(and(eq(deliveries.tenantId, this.tenant), eq(deliveries.status, "queued"), lt(deliveries.createdAt, new Date(now.getTime() - EXPIRE_HOURS * 3_600_000)))));
    const kinds = [this.transport.enabled(true) ? true : null, this.transport.enabled(false) ? false : null].filter((k): k is boolean => k !== null);
    if (!kinds.length) return { sent: 0, failed: 0 };
    const batch = Math.max(1, Math.ceil(this.env.MAIL_RATE_PER_MINUTE * Math.max(this.env.MAIL_INTERVAL_MS, 20_000) / 60_000));
    const due = await withTenant(this.db, this.tenant, (tx) => tx.select({
      id: deliveries.id, source: deliveries.source, template: deliveries.template, context: deliveries.context, transactional: deliveries.transactional, attempts: deliveries.attempts,
      subscriberId: subscribers.id, email: subscribers.email, market: subscribers.market, topics: subscribers.topics, status: subscribers.status,
    }).from(deliveries).innerJoin(subscribers, eq(subscribers.id, deliveries.subscriberId))
      .where(and(eq(deliveries.tenantId, this.tenant), eq(deliveries.status, "queued"), inArray(deliveries.transactional, kinds)))
      .orderBy(asc(deliveries.transactional), asc(deliveries.createdAt)).limit(batch));
    let sent = 0, failed = 0;
    const cache = new Map<string, TemplateInput | null>();
    for (const d of due) {
      // Bulkmail alleen naar actieve abonnees; een bevestigingsmail juist naar een onbevestigde.
      if (!d.transactional && d.status !== "active") { await this.finish(d.id, "expired", "Abonnee niet actief", now); continue; }
      // Geblokkeerd adres (bounce, klacht): niets meer sturen, ook geen bevestigingsmail na een harde bounce (ADR 0038).
      const blocked = await this.delivery.suppressed(d.email, now);
      if (blocked && !(d.transactional && blocked === "complaint")) { await this.finish(d.id, "expired", `Adres geblokkeerd (${blocked})`, now); continue; }
      if (!cache.has(d.template)) cache.set(d.template, await this.templates.get(d.template));
      const template = cache.get(d.template);
      if (!template) { await this.finish(d.id, "failed", `Template ${d.template} bestaat niet`, now); failed++; continue; }
      try {
        const mail = await this.compose(template, { id: d.subscriberId, email: d.email, market: d.market, topics: d.topics }, d.context, d.transactional);
        if (mail.empty) { await this.finish(d.id, "expired", "Geen platen om te tonen", now); continue; }
        await this.transport.send({ to: d.email, subject: mail.subject, html: mail.html, text: mail.text, transactional: d.transactional, ref: d.id, ...(d.transactional ? {} : { unsubscribeUrl: mail.oneClick }) });
        await this.finish(d.id, "sent", null, now, messageIdFor(d.id, this.env.MAIL_FROM));
        await withTenant(this.db, this.tenant, (tx) => this.delivery.sent(tx, { id: d.id, source: d.source, template: d.template }, d.email, now));
        sent++;
      } catch (e) {
        // Permanent geweigerd door de ontvanger (5xx op RCPT TO): harde bounce, niet opnieuw proberen.
        const c = classifySmtpError(e);
        if (c.kind === "hard_bounce") {
          await this.finish(d.id, "failed", c.reason, now);
          await this.delivery.apply("smtp", { type: "hard_bounce", email: d.email, messageId: null, ref: d.id, reason: c.reason, occurredAt: now });
          failed++;
          continue;
        }
        const attempts = d.attempts + 1;
        this.log.warn(`Mail ${d.id} mislukt (${attempts}): ${String(e).slice(0, 200)}`);
        await withTenant(this.db, this.tenant, (tx) => tx.update(deliveries).set({ attempts, error: String(e).slice(0, 500), status: attempts >= MAX_ATTEMPTS ? "failed" : "queued", updatedAt: now }).where(eq(deliveries.id, d.id)));
        failed++;
      }
    }
    if (sent) await withTenant(this.db, this.tenant, (tx) => bump(tx, this.tenant, "sent", sent, now));
    return { sent, failed };
  }

  private async finish(id: string, status: "sent" | "failed" | "expired", error: string | null, now: Date, messageId?: string) {
    // Het bevestigingstoken hoeft na versturen niet meer in de wachtrij te staan.
    await withTenant(this.db, this.tenant, (tx) => tx.update(deliveries).set({ status, error, context: sql`${deliveries.context} - 'token'`, ...(status === "sent" ? { sentAt: now, messageId: messageId ?? null } : {}), updatedAt: now }).where(eq(deliveries.id, id)));
  }

  /** Stand van de wachtrij voor het overzicht. */
  async queueStats(now = new Date()) {
    return withTenant(this.db, this.tenant, async (tx) => {
      const rows = await tx.select({ status: deliveries.status, n: sql<number>`count(*)::int` }).from(deliveries)
        .where(and(eq(deliveries.tenantId, this.tenant), sql`${deliveries.updatedAt} > ${new Date(now.getTime() - 7 * 86_400_000)} or ${deliveries.status} = 'queued'`)).groupBy(deliveries.status);
      const errors = await tx.select({ error: deliveries.error, n: sql<number>`count(*)::int` }).from(deliveries)
        .where(and(eq(deliveries.tenantId, this.tenant), eq(deliveries.status, "failed"), sql`${deliveries.updatedAt} > ${new Date(now.getTime() - 7 * 86_400_000)}`)).groupBy(deliveries.error).limit(5);
      return { ...Object.fromEntries(rows.map((r) => [r.status, r.n])), errors };
    });
  }

  /** Direct één mail sturen (testmail uit het admin panel), buiten de wachtrij. */
  async sendTest(template: TemplateInput, to: string, market: string, context: MailContext) {
    if (!this.transport.enabled(false)) throw new Error("Versturen staat uit: er is geen MAIL_SMTP_URL ingesteld");
    const mail = await this.compose(template, { id: "00000000-0000-7000-8000-000000000000", email: to, market, topics: ["nieuwsbrief"] }, context, false);
    await this.transport.send({ to, subject: `[Test] ${mail.subject}`, html: mail.html, text: mail.text, transactional: false });
  }
}
