import { BadRequestException, Inject, Injectable, NotFoundException } from "@nestjs/common";
import { and, desc, eq, lte, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { campaigns, deliveries, subscribers, templates } from "./messaging.schema";
import { TOPICS, type Audience, type MailContext } from "./messaging.types";

export type Campaign = typeof campaigns.$inferSelect;
export interface CampaignInput { name: string; template: string; audience: Audience; context?: MailContext | undefined }

/**
 * Campagnes (ADR 0037): een nieuwsbrief of losse mail aan een groep abonnees, nu of op een tijdstip. Versturen zet
 * de mails in de wachtrij; wie zich intussen afmeldt, krijgt hem niet meer.
 */
@Injectable()
export class CampaignsService {
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env) {}
  private get tenant() { return this.env.TENANT_ID; }

  list(): Promise<Campaign[]> {
    return withTenant(this.db, this.tenant, (tx) => tx.select().from(campaigns).where(eq(campaigns.tenantId, this.tenant)).orderBy(desc(campaigns.createdAt)).limit(100));
  }

  async get(id: string): Promise<Campaign | null> {
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select().from(campaigns).where(and(eq(campaigns.tenantId, this.tenant), eq(campaigns.id, id))).limit(1));
    return row ?? null;
  }

  private async check(input: CampaignInput) {
    const problems: string[] = [];
    if (input.name.trim().length < 2) problems.push("Geef de campagne een naam");
    if (!input.audience.topics.length || input.audience.topics.some((t) => !TOPICS.includes(t))) problems.push("Kies minstens één onderwerp");
    const [t] = await withTenant(this.db, this.tenant, (tx) => tx.select({ slug: templates.slug, kind: templates.kind }).from(templates).where(and(eq(templates.tenantId, this.tenant), eq(templates.slug, input.template))).limit(1));
    if (!t) problems.push("Onbekende template");
    else if (t.kind === "system") problems.push("Een vaste template (bevestigen, welkom) kan niet als campagne");
    if (problems.length) throw new BadRequestException(problems.join("; "));
  }

  async create(input: CampaignInput, actor: string): Promise<Campaign> {
    await this.check(input);
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.insert(campaigns).values({ tenantId: this.tenant, name: input.name.trim(), template: input.template, audience: input.audience, context: input.context ?? {}, createdBy: actor }).returning());
    return row!;
  }

  async update(id: string, input: CampaignInput): Promise<Campaign> {
    const c = await this.get(id);
    if (!c) throw new NotFoundException("Onbekende campagne");
    if (c.status !== "draft" && c.status !== "scheduled") throw new BadRequestException("Een verstuurde campagne kan niet meer veranderen");
    await this.check(input);
    await withTenant(this.db, this.tenant, (tx) => tx.update(campaigns).set({ name: input.name.trim(), template: input.template, audience: input.audience, context: input.context ?? {}, updatedAt: new Date() }).where(eq(campaigns.id, id)));
    return (await this.get(id))!;
  }

  /** Hoeveel abonnees een publiek nu telt. */
  async audienceSize(a: Audience): Promise<number> {
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select({ n: sql<number>`count(*)::int` }).from(subscribers).where(and(
      eq(subscribers.tenantId, this.tenant), eq(subscribers.status, "active"), sql`${subscribers.topics} && ${sql.raw(`ARRAY[${a.topics.filter((t) => TOPICS.includes(t)).map((t) => `'${t}'`).join(",")}]::text[]`)}`,
      a.markets?.length ? sql`${subscribers.market} in ${a.markets}` : undefined)));
    return row?.n ?? 0;
  }

  /** Plannen (of nu versturen: `at` leeg). */
  async schedule(id: string, at: Date | null, now = new Date()): Promise<Campaign> {
    const c = await this.get(id);
    if (!c) throw new NotFoundException("Onbekende campagne");
    if (c.status !== "draft" && c.status !== "scheduled") throw new BadRequestException("Deze campagne is al verstuurd of geannuleerd");
    await withTenant(this.db, this.tenant, (tx) => tx.update(campaigns).set({ status: "scheduled", scheduledAt: at ?? now, updatedAt: now }).where(eq(campaigns.id, id)));
    await this.tick(now);
    return (await this.get(id))!;
  }

  async cancel(id: string): Promise<Campaign> {
    const c = await this.get(id);
    if (!c) throw new NotFoundException("Onbekende campagne");
    await withTenant(this.db, this.tenant, async (tx) => {
      if (c.status === "scheduled" || c.status === "draft") await tx.update(campaigns).set({ status: "cancelled", updatedAt: new Date() }).where(eq(campaigns.id, id));
      // Al in de wachtrij maar nog niet weg: niet meer sturen.
      if (c.status === "sent" || c.status === "sending") await tx.update(deliveries).set({ status: "expired", error: "Campagne geannuleerd", updatedAt: new Date() })
        .where(and(eq(deliveries.tenantId, this.tenant), eq(deliveries.source, `campaign:${id}`), eq(deliveries.status, "queued")));
    });
    return (await this.get(id))!;
  }

  /** Geplande campagnes die aan de beurt zijn in de wachtrij zetten. */
  async tick(now = new Date()) {
    const due = await withTenant(this.db, this.tenant, (tx) => tx.select().from(campaigns).where(and(eq(campaigns.tenantId, this.tenant), eq(campaigns.status, "scheduled"), lte(campaigns.scheduledAt, now))));
    for (const c of due) {
      await withTenant(this.db, this.tenant, async (tx) => {
        // Eerst de status, zodat een tweede verwerker dezelfde campagne niet oppakt.
        const [mine] = await tx.update(campaigns).set({ status: "sending", updatedAt: now }).where(and(eq(campaigns.id, c.id), eq(campaigns.status, "scheduled"))).returning({ id: campaigns.id });
        if (!mine) return;
        const topics = sql.raw(`ARRAY[${c.audience.topics.filter((t) => TOPICS.includes(t)).map((t) => `'${t}'`).join(",")}]::text[]`);
        const res = await tx.execute(sql`
          insert into ${deliveries} (id, tenant_id, subscriber_id, source, template, context, transactional, status)
          select gen_random_uuid(), ${this.tenant}, s.id, ${`campaign:${c.id}`}, ${c.template}, ${JSON.stringify(c.context)}::jsonb, false, 'queued'
          from ${subscribers} s
          where s.tenant_id = ${this.tenant} and s.status = 'active' and s.topics && ${topics}
            ${c.audience.markets?.length ? sql`and s.market in ${c.audience.markets}` : sql``}
          on conflict do nothing`);
        const n = (res as unknown as { rowCount?: number; affectedRows?: number }).rowCount ?? (res as unknown as { affectedRows?: number }).affectedRows ?? 0;
        await tx.update(campaigns).set({ status: "sent", sentAt: now, recipients: n, updatedAt: now }).where(eq(campaigns.id, c.id));
      });
    }
  }

  /** Per campagne: verstuurd, in de wachtrij, mislukt. */
  async deliveryStats(id: string) {
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select({ status: deliveries.status, n: sql<number>`count(*)::int` }).from(deliveries)
      .where(and(eq(deliveries.tenantId, this.tenant), eq(deliveries.source, `campaign:${id}`))).groupBy(deliveries.status));
    return Object.fromEntries(rows.map((r) => [r.status, r.n]));
  }
}
