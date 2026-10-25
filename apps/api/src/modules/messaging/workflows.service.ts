import { BadRequestException, Inject, Injectable, Logger, NotFoundException } from "@nestjs/common";
import { and, asc, eq, lte, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { CatalogService } from "../catalog/catalog.service";
import { StorefrontService } from "../storefront/storefront.service";
import { deliveries, subscribers, templates, workflowRuns, workflows } from "./messaging.schema";
import { TOPICS, type MailContext, type Step, type Trigger } from "./messaging.types";

export type Workflow = typeof workflows.$inferSelect;
export interface WorkflowInput { name: string; enabled: boolean; trigger: Trigger; steps: Step[] }
const SLUG = /^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/;
/** Tijdzone van een vaste dag en tijd (alle markten nu in Midden-Europa). */
const ZONE = "Europe/Amsterdam";

/** Het laatste moment vóór `now` waarop een wekelijkse planning (weekdag 0 = zondag, uur in ZONE) viel. */
export function lastScheduled(weekday: number, hour: number, now: Date): Date {
  const parts = Object.fromEntries(new Intl.DateTimeFormat("en-GB", { timeZone: ZONE, weekday: "short", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", hourCycle: "h23" })
    .formatToParts(now).map((p) => [p.type, p.value]));
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(parts.weekday!);
  const offsetMs = now.getTime() - Date.UTC(+parts.year!, +parts.month! - 1, +parts.day!, +parts.hour!, now.getUTCMinutes(), now.getUTCSeconds(), now.getUTCMilliseconds());
  let back = (days - weekday + 7) % 7;
  if (back === 0 && +parts.hour! < hour) back = 7;
  return new Date(Date.UTC(+parts.year!, +parts.month! - 1, +parts.day! - back, hour) + offsetMs);
}

/**
 * Workflows (ADR 0037): aanleiding → stappen. Elke abonnee loopt per aanleiding hooguit één keer door een workflow
 * (uniek op workflow, abonnee en aanleiding), dus herhaald verwerken stuurt niets dubbel.
 */
@Injectable()
export class WorkflowsService {
  private readonly log = new Logger("Workflows");
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env, private readonly store: StorefrontService, private readonly catalog: CatalogService) {}
  private get tenant() { return this.env.TENANT_ID; }

  list(): Promise<Workflow[]> {
    return withTenant(this.db, this.tenant, (tx) => tx.select().from(workflows).where(eq(workflows.tenantId, this.tenant)).orderBy(asc(workflows.name)));
  }

  async get(slug: string): Promise<Workflow | null> {
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select().from(workflows).where(and(eq(workflows.tenantId, this.tenant), eq(workflows.slug, slug))).limit(1));
    return row ?? null;
  }

  async save(slug: string, input: WorkflowInput, actor: string): Promise<Workflow> {
    if (!SLUG.test(slug)) throw new BadRequestException("Code: kleine letters, cijfers en streepjes");
    const problems: string[] = [];
    if (!input.steps.some((s) => s.type === "send")) problems.push("Een workflow heeft minstens één stap Mail sturen");
    const known = new Set((await withTenant(this.db, this.tenant, (tx) => tx.select({ slug: templates.slug }).from(templates).where(eq(templates.tenantId, this.tenant)))).map((t) => t.slug));
    for (const s of input.steps) if (s.type === "send" && !known.has(s.template)) problems.push(`Onbekende template: ${s.template}`);
    if (input.trigger.type !== "subscribed" && !input.steps.some((s) => s.type === "filter" && s.topics?.length)) problems.push("Begin met een filter op onderwerp, zodat alleen wie dat wil de mail krijgt");
    if (problems.length) throw new BadRequestException(problems.join("; "));
    const current = await this.get(slug);
    const values = { name: input.name.trim().slice(0, 80) || slug, enabled: input.enabled, trigger: input.trigger, steps: input.steps, updatedBy: actor, updatedAt: new Date() };
    // Een nieuwe of gewijzigde aanleiding begint vanaf nu (niet met een achterstand van weken).
    const restart = !current || JSON.stringify(current.trigger) !== JSON.stringify(input.trigger) || (!current.enabled && input.enabled);
    await withTenant(this.db, this.tenant, (tx) => current
      ? tx.update(workflows).set({ ...values, ...(restart ? { cursor: new Date() } : {}) }).where(eq(workflows.id, current.id))
      : tx.insert(workflows).values({ tenantId: this.tenant, slug, ...values, cursor: new Date() }));
    return (await this.get(slug))!;
  }

  async remove(slug: string) {
    await withTenant(this.db, this.tenant, async (tx) => {
      const rows = await tx.delete(workflows).where(and(eq(workflows.tenantId, this.tenant), eq(workflows.slug, slug))).returning({ id: workflows.id });
      if (!rows.length) throw new NotFoundException("Onbekende workflow");
      await tx.delete(workflowRuns).where(and(eq(workflowRuns.tenantId, this.tenant), eq(workflowRuns.workflowSlug, slug)));
    });
  }

  /** Een abonnee laten instromen (of alle actieve, eventueel van één markt). */
  private async start(slug: string, occasion: string, context: MailContext, only: { subscriberId?: string; market?: string } = {}, now = new Date()) {
    await withTenant(this.db, this.tenant, (tx) => tx.execute(sql`
      insert into ${workflowRuns} (id, tenant_id, workflow_slug, subscriber_id, occasion, step, due_at, status, context)
      select gen_random_uuid(), ${this.tenant}, ${slug}, s.id, ${occasion}, 0, ${now}, 'waiting', ${JSON.stringify(context)}::jsonb
      from ${subscribers} s
      where s.tenant_id = ${this.tenant} and s.status = 'active'
        ${only.subscriberId ? sql`and s.id = ${only.subscriberId}` : sql``}
        ${only.market ? sql`and s.market = ${only.market}` : sql``}
      on conflict do nothing`));
  }

  /** Na bevestigen: workflows met aanleiding Aanmelding. */
  async onSubscribed(subscriberId: string, now = new Date()) {
    for (const w of (await this.list()).filter((x) => x.enabled && x.trigger.type === "subscribed")) {
      await this.start(w.slug, "aanmelding", { since: new Date(now.getTime() - 60 * 86_400_000).toISOString() }, { subscriberId }, now);
    }
  }

  /** Aanleidingen bekijken: vaste dag, nieuwe platen, feestdag die eraan komt. */
  async tick(now = new Date()) {
    for (const w of (await this.list()).filter((x) => x.enabled)) {
      try {
        const t = w.trigger;
        const cursor = w.cursor ?? now;
        if (t.type === "schedule") {
          const at = lastScheduled(t.weekday, t.hour, now);
          if (at > cursor) {
            await this.start(w.slug, at.toISOString(), { since: cursor.toISOString() }, {}, now);
            await this.setCursor(w.id, at);
          }
        } else if (t.type === "plates_published") {
          const fresh = await this.catalog.publishedSince(this.tenant, cursor);
          if (fresh.length >= t.min) {
            await this.start(w.slug, `platen:${now.toISOString()}`, { since: cursor.toISOString() }, {}, now);
            await this.setCursor(w.id, now);
          }
        } else if (t.type === "holiday_soon") {
          const markets = await withTenant(this.db, this.tenant, (tx) => tx.selectDistinct({ market: subscribers.market }).from(subscribers).where(and(eq(subscribers.tenantId, this.tenant), eq(subscribers.status, "active"))));
          for (const { market } of markets) {
            for (const h of await this.store.upcomingHolidays(market, t.days, now)) {
              await this.start(w.slug, `${h.slug}:${h.date}`, { holiday: h.slug }, { market }, now);
            }
          }
        }
      } catch (e) { this.log.error(`Workflow ${w.slug}: ${e}`); }
    }
  }

  private setCursor(id: string, at: Date) {
    return withTenant(this.db, this.tenant, (tx) => tx.update(workflows).set({ cursor: at }).where(eq(workflows.id, id)));
  }

  /** Doorlopen die aan de beurt zijn een stap verder brengen, tot een wachtstap of het einde. */
  async advance(now = new Date()) {
    const due = await withTenant(this.db, this.tenant, (tx) => tx.select({
      run: workflowRuns, sub: { id: subscribers.id, market: subscribers.market, topics: subscribers.topics },
    }).from(workflowRuns).innerJoin(subscribers, eq(subscribers.id, workflowRuns.subscriberId))
      .where(and(eq(workflowRuns.tenantId, this.tenant), eq(workflowRuns.status, "waiting"), lte(workflowRuns.dueAt, now))).limit(1000));
    if (!due.length) return 0;
    const flows = new Map((await this.list()).map((w) => [w.slug, w]));
    const fresh = new Map<string, number>();
    for (const { run, sub } of due) {
      const w = flows.get(run.workflowSlug);
      let step = run.step, status: "waiting" | "done" | "stopped" = "done", dueAt = now;
      if (!w || !w.enabled) status = "stopped";
      else {
        for (; step < w.steps.length; step++) {
          const s = w.steps[step]!;
          if (s.type === "filter") {
            if ((s.topics?.length && !s.topics.some((x) => sub.topics.includes(x))) || (s.markets?.length && !s.markets.includes(sub.market))) { status = "stopped"; break; }
          } else if (s.type === "require_plates") {
            const key = `${sub.market}|${run.context.since}`;
            if (!fresh.has(key)) fresh.set(key, (await this.store.mailPlates(sub.market, { since: new Date(run.context.since ?? 0) }, 1000, now)).length);
            if (fresh.get(key)! < s.min) { status = "stopped"; break; }
          } else if (s.type === "wait") {
            // Wachten: verder bij de volgende stap, over zoveel uur. Bij hervatten begint de lus daar.
            status = "waiting"; dueAt = new Date(now.getTime() + s.hours * 3_600_000); step++; break;
          } else if (s.type === "send") {
            await withTenant(this.db, this.tenant, (tx) => tx.insert(deliveries).values({
              tenantId: this.tenant, subscriberId: sub.id, source: `wf:${w.slug}:${run.occasion}:${step}`, template: s.template, context: run.context,
            }).onConflictDoNothing());
          }
        }
      }
      await withTenant(this.db, this.tenant, (tx) => tx.update(workflowRuns).set({ step, status, dueAt, updatedAt: now }).where(eq(workflowRuns.id, run.id)));
    }
    return due.length;
  }

  /** Voor het overzicht: per workflow hoeveel lopen er en hoeveel zijn klaar (30 dagen). */
  async runStats(now = new Date()) {
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select({ slug: workflowRuns.workflowSlug, status: workflowRuns.status, n: sql<number>`count(*)::int` }).from(workflowRuns)
      .where(and(eq(workflowRuns.tenantId, this.tenant), sql`${workflowRuns.updatedAt} > ${new Date(now.getTime() - 30 * 86_400_000)}`)).groupBy(workflowRuns.workflowSlug, workflowRuns.status));
    const out: Record<string, Record<string, number>> = {};
    for (const r of rows) (out[r.slug] ??= {})[r.status] = r.n;
    return out;
  }
}

export const isTopic = (t: string): t is (typeof TOPICS)[number] => (TOPICS as readonly string[]).includes(t);
