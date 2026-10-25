import { BadRequestException, ConflictException, Inject, Injectable, NotFoundException, type OnModuleInit } from "@nestjs/common";
import { and, asc, eq } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { DEFAULT_TEMPLATES, DEFAULT_WORKFLOWS } from "./defaults";
import { campaigns, templates, workflows } from "./messaging.schema";
import { PLATE_SOURCES, SYSTEM_TEMPLATES, type Block, type I18nText, type TemplateKind } from "./messaging.types";

export type Template = typeof templates.$inferSelect;
export interface TemplateInput { name: string; kind: TemplateKind; subject: I18nText; preheader: I18nText; blocks: Block[] }

const SLUG = /^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/;
const SYSTEM = new Set<string>(Object.values(SYSTEM_TEMPLATES));

/** Templates (ADR 0037): blokken met tekst per taal. Vaste templates zijn te bewerken, niet te verwijderen. */
@Injectable()
export class TemplatesService implements OnModuleInit {
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env) {}
  private get tenant() { return this.env.TENANT_ID; }

  /**
   * Startinhoud neerzetten. Een template dat nog niemand in het admin panel heeft aangepast (bijgewerkt door
   * "systeem") volgt de tekst in de code; een aangepast template wordt nooit overschreven.
   */
  async onModuleInit() {
    await withTenant(this.db, this.tenant, async (tx) => {
      for (const d of DEFAULT_TEMPLATES) {
        await tx.insert(templates).values({ tenantId: this.tenant, ...d })
          .onConflictDoUpdate({ target: [templates.tenantId, templates.slug], set: { subject: d.subject, preheader: d.preheader, blocks: d.blocks, updatedAt: new Date() }, setWhere: eq(templates.updatedBy, "systeem") });
      }
      for (const w of DEFAULT_WORKFLOWS) await tx.insert(workflows).values({ tenantId: this.tenant, ...w }).onConflictDoNothing();
    });
  }

  list(): Promise<Template[]> {
    return withTenant(this.db, this.tenant, (tx) => tx.select().from(templates).where(eq(templates.tenantId, this.tenant)).orderBy(asc(templates.kind), asc(templates.name)));
  }

  async get(slug: string): Promise<Template | null> {
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select().from(templates).where(and(eq(templates.tenantId, this.tenant), eq(templates.slug, slug))).limit(1));
    return row ?? null;
  }

  /** Controle op inhoud: een onderwerp in het Nederlands, unieke blok-id's, geldige knoppen en platenblokken. */
  validate(input: TemplateInput): void {
    const problems: string[] = [];
    if (!input.subject.nl?.trim()) problems.push("Geef een onderwerp in het Nederlands");
    if (!input.blocks.length) problems.push("Een template heeft minstens één blok");
    const ids = new Set<string>();
    for (const b of input.blocks) {
      if (ids.has(b.id)) problems.push(`Blok-id ${b.id} komt twee keer voor`);
      ids.add(b.id);
      if (b.type === "button" && !/^(https?:\/\/|mailto:|\{\{\s*(site|voorkeuren|bevestigen)\s*\}\})/.test(b.url.trim())) problems.push("Een knop linkt naar https://…, mailto: of {{site}}");
      if (b.type === "plates" && !PLATE_SOURCES.includes(b.source)) problems.push("Onbekende bron voor platen");
      if (b.type === "plates" && b.source === "collection" && !b.collection) problems.push("Kies een collectie voor het platenblok");
      if (b.type === "plates" && b.source === "selected" && !b.slugs?.length) problems.push("Kies platen voor het platenblok");
    }
    if (problems.length) throw new BadRequestException(problems.join("; "));
  }

  async save(slug: string, input: TemplateInput, actor: string): Promise<Template> {
    if (!SLUG.test(slug)) throw new BadRequestException("Code: kleine letters, cijfers en streepjes");
    this.validate(input);
    const current = await this.get(slug);
    // Een vaste template blijft vast; een andere kan niet tot vaste template worden gemaakt.
    const kind: TemplateKind = SYSTEM.has(slug) ? "system" : input.kind === "system" ? "campaign" : input.kind;
    if (SYSTEM.has(slug) && slug === SYSTEM_TEMPLATES.confirm && !JSON.stringify(input.blocks).includes("{{bevestigen}}")) {
      throw new BadRequestException("De bevestigingsmail heeft een knop of link met {{bevestigen}} nodig");
    }
    const values = { name: input.name.trim().slice(0, 80) || slug, kind, subject: input.subject, preheader: input.preheader, blocks: input.blocks, updatedBy: actor, updatedAt: new Date() };
    await withTenant(this.db, this.tenant, (tx) => current
      ? tx.update(templates).set(values).where(eq(templates.id, current.id))
      : tx.insert(templates).values({ tenantId: this.tenant, slug, ...values }));
    return (await this.get(slug))!;
  }

  /** Verwijderen kan niet bij een vaste template, of als een workflow of campagne hem nog gebruikt. */
  async remove(slug: string): Promise<void> {
    if (SYSTEM.has(slug)) throw new BadRequestException("Een vaste template kan niet weg");
    await withTenant(this.db, this.tenant, async (tx) => {
      const flows = await tx.select({ slug: workflows.slug, steps: workflows.steps }).from(workflows).where(eq(workflows.tenantId, this.tenant));
      const usedBy = flows.filter((f) => f.steps.some((s) => s.type === "send" && s.template === slug)).map((f) => f.slug);
      const camps = await tx.select({ name: campaigns.name }).from(campaigns).where(and(eq(campaigns.tenantId, this.tenant), eq(campaigns.template, slug)));
      if (usedBy.length || camps.some(() => true)) throw new ConflictException(`In gebruik bij ${[...usedBy.map((s) => `workflow ${s}`), ...camps.map((c) => `campagne ${c.name}`)].join(", ")}`);
      const rows = await tx.delete(templates).where(and(eq(templates.tenantId, this.tenant), eq(templates.slug, slug))).returning({ id: templates.id });
      if (!rows.length) throw new NotFoundException("Onbekende template");
    });
  }
}
