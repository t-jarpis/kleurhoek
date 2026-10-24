import { Inject, Injectable } from "@nestjs/common";
import { and, asc, desc, eq, inArray, isNull, lt, ne, or } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { AuditService } from "../identity/audit.service";
import { LocalizationService } from "../localization/localization.service";
import { checkSource, checkSourceUrl, defaultDeps, type CheckDeps, type CheckResult } from "./source-check";
import { sources, themes } from "./sources.schema";

export class SourcesError extends Error {
  constructor(readonly code: "not_found" | "invalid", message: string) { super(message); }
}

const SLUG = /^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/;
/** Na zoveel mislukte controles op rij gaat een bron offline (404/410 telt dubbel zwaar: na 2). */
export const MAX_FAILS = 3;
export const RECHECK_HOURS = 24;

type SourceRow = typeof sources.$inferSelect;

/** Nieuwe gezondheid van een bron na een controle. Puur, zodat het te testen is. */
export function applyCheck(prev: Pick<SourceRow, "failCount" | "baselineHash" | "health" | "changed">, r: CheckResult) {
  if (r.outcome === "ok") {
    return { health: "ok" as const, failCount: 0, changed: prev.changed || Boolean(prev.baselineHash && r.contentHash && r.contentHash !== prev.baselineHash) };
  }
  const failCount = prev.failCount + 1;
  const broken = r.outcome === "blocked" || (r.outcome === "gone" && failCount >= 2) || failCount >= MAX_FAILS;
  return { health: broken ? "broken" as const : prev.health === "unknown" ? "unknown" as const : prev.health, failCount, changed: prev.changed };
}

export interface SourceView {
  id: string; themeSlug: string; url: string; host: string; title: string | null; description: string | null;
  basis: "link" | "license"; licenseNote: string | null; licenseDate: string | null;
  status: "pending" | "approved" | "rejected"; health: "unknown" | "ok" | "broken"; changed: boolean;
  httpStatus: number | null; finalUrl: string | null; robotsAllowed: boolean | null; pageTitle: string | null; checkNote: string | null;
  failCount: number; lastCheckedAt: string | null; lastOkAt: string | null; approvedBy: string | null; approvedAt: string | null;
  /** Staat deze bron nu op de site? */
  live: boolean;
}
export interface ThemeView {
  slug: string; status: "draft" | "published"; name: string | null; description: string | null; makerName: string; makerUrl: string;
  productSlugs: string[]; sortOrder: number; updatedBy: string; updatedAt: string;
  counts: { total: number; live: number; attention: number };
}

const isLive = (s: Pick<SourceRow, "status" | "health">) => s.status === "approved" && s.health === "ok";
const needsAttention = (s: Pick<SourceRow, "status" | "health" | "changed">) => s.status === "pending" || (s.status === "approved" && (s.health === "broken" || s.changed));

/**
 * Domein Bronnen (ADR 0025). Thema's met links naar kleurplaten bij de maker zelf. Alles gaat via
 * goedkeuring in het admin panel, en een controle (dagelijks) haalt verdwenen bronnen vanzelf offline.
 */
@Injectable()
export class SourcesService {
  constructor(
    @Inject(DB) private readonly db: Database,
    @Inject(ENV) private readonly env: Env,
    private readonly i18n: LocalizationService,
    private readonly audit: AuditService,
  ) {}

  /** Te overschrijven in tests: zo praten tests nooit met het internet. */
  deps: CheckDeps = defaultDeps;

  private get tenant() { return this.env.TENANT_ID; }

  private async sourceViews(rows: SourceRow[], language: string): Promise<SourceView[]> {
    const tr = await this.i18n.translate(this.tenant, "source", language, rows.map((r) => r.id));
    return rows.map((r) => ({
      id: r.id, themeSlug: r.themeSlug, url: r.url, host: new URL(r.url).hostname.replace(/^www\./, ""),
      title: tr.get(r.id)?.title ?? null, description: tr.get(r.id)?.description ?? null,
      basis: r.basis, licenseNote: r.licenseNote, licenseDate: r.licenseDate, status: r.status, health: r.health, changed: r.changed,
      httpStatus: r.httpStatus, finalUrl: r.finalUrl, robotsAllowed: r.robotsAllowed, pageTitle: r.pageTitle, checkNote: r.checkNote,
      failCount: r.failCount, lastCheckedAt: r.lastCheckedAt?.toISOString() ?? null, lastOkAt: r.lastOkAt?.toISOString() ?? null,
      approvedBy: r.approvedBy, approvedAt: r.approvedAt?.toISOString() ?? null, live: isLive(r),
    }));
  }

  // ---------- admin: thema's ----------

  async themeList(language: string): Promise<ThemeView[]> {
    const [rows, srcs] = await withTenant(this.db, this.tenant, async (tx) => [
      await tx.select().from(themes).orderBy(asc(themes.sortOrder), asc(themes.slug)),
      await tx.select({ themeSlug: sources.themeSlug, status: sources.status, health: sources.health, changed: sources.changed }).from(sources),
    ] as const);
    const tr = await this.i18n.translate(this.tenant, "theme", language, rows.map((r) => r.slug));
    return rows.map((r) => {
      const mine = srcs.filter((s) => s.themeSlug === r.slug && s.status !== "rejected");
      return {
        slug: r.slug, status: r.status, name: tr.get(r.slug)?.name ?? null, description: tr.get(r.slug)?.description ?? null,
        makerName: r.makerName, makerUrl: r.makerUrl, productSlugs: r.productSlugs, sortOrder: r.sortOrder, updatedBy: r.updatedBy, updatedAt: r.updatedAt.toISOString(),
        counts: { total: mine.length, live: mine.filter(isLive).length, attention: mine.filter(needsAttention).length },
      };
    });
  }

  async theme(slug: string, language: string) {
    const t = (await this.themeList(language)).find((x) => x.slug === slug);
    if (!t) throw new SourcesError("not_found", "Onbekend thema");
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select().from(sources).where(eq(sources.themeSlug, slug)).orderBy(asc(sources.sortOrder), asc(sources.createdAt)));
    return { ...t, sources: await this.sourceViews(rows, language) };
  }

  async createTheme(actor: string, language: string, input: { slug: string; name: string; description: string; makerName: string; makerUrl: string }) {
    if (!SLUG.test(input.slug)) throw new SourcesError("invalid", "Gebruik kleine letters, cijfers en streepjes voor de code");
    const maker = checkSourceUrl(input.makerUrl);
    if ("problem" in maker) throw new SourcesError("invalid", `Website van de maker: ${maker.problem}`);
    await withTenant(this.db, this.tenant, async (tx) => {
      const [exists] = await tx.select({ slug: themes.slug }).from(themes).where(eq(themes.slug, input.slug)).limit(1);
      if (exists) throw new SourcesError("invalid", "Die code bestaat al");
      const [max] = await tx.select({ o: themes.sortOrder }).from(themes).orderBy(desc(themes.sortOrder)).limit(1);
      await tx.insert(themes).values({ tenantId: this.tenant, slug: input.slug, makerName: input.makerName, makerUrl: maker.url.href, sortOrder: (max?.o ?? 0) + 1, updatedBy: actor });
      await this.audit.record(tx, this.tenant, { actor, action: "sources.theme.created", subject: `theme:${input.slug}`, after: { makerName: input.makerName, makerUrl: maker.url.href } });
    });
    await this.i18n.save(this.tenant, "theme", input.slug, language, { name: input.name, description: input.description });
    return this.theme(input.slug, language);
  }

  async updateTheme(actor: string, slug: string, language: string, change: {
    name?: string | undefined; description?: string | undefined; makerName?: string | undefined; makerUrl?: string | undefined;
    status?: "draft" | "published" | undefined; productSlugs?: string[] | undefined; sortOrder?: number | undefined;
  }) {
    const current = await this.theme(slug, language);
    let makerUrl = current.makerUrl;
    if (change.makerUrl !== undefined) {
      const m = checkSourceUrl(change.makerUrl);
      if ("problem" in m) throw new SourcesError("invalid", `Website van de maker: ${m.problem}`);
      makerUrl = m.url.href;
    }
    const name = change.name ?? current.name, description = change.description ?? current.description;
    if (change.status === "published" && (!name || !description)) throw new SourcesError("invalid", "Geef het thema eerst een naam en beschrijving");
    if (change.status === "published" && !current.sources.some((s) => s.live)) throw new SourcesError("invalid", "Keur eerst minstens één bron goed die werkt");
    const next = {
      makerName: change.makerName ?? current.makerName, makerUrl, status: change.status ?? current.status,
      productSlugs: change.productSlugs ?? current.productSlugs, sortOrder: change.sortOrder ?? current.sortOrder,
    };
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.update(themes).set({ ...next, updatedBy: actor, updatedAt: new Date() }).where(eq(themes.slug, slug));
      await this.audit.record(tx, this.tenant, {
        actor, action: "sources.theme.updated", subject: `theme:${slug}`,
        before: { makerName: current.makerName, makerUrl: current.makerUrl, status: current.status, productSlugs: current.productSlugs }, after: next,
      });
    });
    if (change.name !== undefined || change.description !== undefined) await this.i18n.save(this.tenant, "theme", slug, language, { name, description });
    return this.theme(slug, language);
  }

  // ---------- admin: bronnen ----------

  private async row(id: string): Promise<SourceRow> {
    const [r] = await withTenant(this.db, this.tenant, (tx) => tx.select().from(sources).where(eq(sources.id, id)).limit(1));
    if (!r) throw new SourcesError("not_found", "Onbekende bron");
    return r;
  }

  async addSource(actor: string, themeSlug: string, language: string, input: {
    url: string; title: string; description?: string | null | undefined; basis: "link" | "license"; licenseNote?: string | null | undefined; licenseDate?: string | null | undefined;
  }) {
    const parsed = checkSourceUrl(input.url);
    if ("problem" in parsed) throw new SourcesError("invalid", parsed.problem);
    if (input.basis === "license" && !input.licenseNote) throw new SourcesError("invalid", "Leg bij een licentie vast wat de maker toestond (en waar dat staat)");
    await this.theme(themeSlug, language);
    const id = await withTenant(this.db, this.tenant, async (tx) => {
      const [dupe] = await tx.select({ id: sources.id }).from(sources).where(eq(sources.url, parsed.url.href)).limit(1);
      if (dupe) throw new SourcesError("invalid", "Deze link staat er al in");
      const [r] = await tx.insert(sources).values({
        tenantId: this.tenant, themeSlug, url: parsed.url.href, basis: input.basis,
        licenseNote: input.licenseNote ?? null, licenseDate: input.licenseDate ?? null,
      }).returning({ id: sources.id });
      await this.audit.record(tx, this.tenant, { actor, action: "sources.source.created", subject: `source:${r!.id}`, after: { themeSlug, url: parsed.url.href, basis: input.basis } });
      return r!.id;
    });
    await this.i18n.save(this.tenant, "source", id, language, { title: input.title, description: input.description ?? null });
    await this.check(id);
    return (await this.sourceViews([await this.row(id)], language))[0]!;
  }

  async updateSource(actor: string, id: string, language: string, change: {
    title?: string | undefined; description?: string | null | undefined; basis?: "link" | "license" | undefined; licenseNote?: string | null | undefined; licenseDate?: string | null | undefined;
  }) {
    const before = await this.row(id);
    const next = {
      basis: change.basis ?? before.basis,
      licenseNote: change.licenseNote !== undefined ? change.licenseNote : before.licenseNote,
      licenseDate: change.licenseDate !== undefined ? change.licenseDate : before.licenseDate,
    };
    if (next.basis === "license" && !next.licenseNote) throw new SourcesError("invalid", "Leg bij een licentie vast wat de maker toestond");
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.update(sources).set({ ...next, updatedAt: new Date() }).where(eq(sources.id, id));
      await this.audit.record(tx, this.tenant, { actor, action: "sources.source.updated", subject: `source:${id}`, before: { basis: before.basis, licenseNote: before.licenseNote }, after: next });
    });
    if (change.title !== undefined || change.description !== undefined) {
      const cur = (await this.i18n.translate(this.tenant, "source", language, [id])).get(id) ?? {};
      await this.i18n.save(this.tenant, "source", id, language, { title: change.title ?? cur.title ?? null, description: change.description !== undefined ? change.description : cur.description ?? null });
    }
    return (await this.sourceViews([await this.row(id)], language))[0]!;
  }

  /** Goedkeuren kan alleen als de laatste controle goed was; de huidige pagina wordt de maatstaf. */
  async approve(actor: string, id: string, language: string) {
    const r = await this.row(id);
    if (r.health !== "ok" || r.robotsAllowed === false) throw new SourcesError("invalid", "De laatste controle was niet goed: controleer eerst opnieuw");
    const title = (await this.i18n.translate(this.tenant, "source", language, [id])).get(id)?.title;
    if (!title) throw new SourcesError("invalid", "Geef de bron eerst een eigen titel");
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.update(sources).set({ status: "approved", changed: false, baselineHash: r.contentHash, approvedBy: actor, approvedAt: new Date(), updatedAt: new Date() }).where(eq(sources.id, id));
      await this.audit.record(tx, this.tenant, { actor, action: "sources.source.approved", subject: `source:${id}`, before: { status: r.status }, after: { status: "approved", basis: r.basis } });
    });
    return (await this.sourceViews([await this.row(id)], language))[0]!;
  }

  async reject(actor: string, id: string, language: string) {
    const r = await this.row(id);
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.update(sources).set({ status: "rejected", updatedAt: new Date() }).where(eq(sources.id, id));
      await this.audit.record(tx, this.tenant, { actor, action: "sources.source.rejected", subject: `source:${id}`, before: { status: r.status }, after: { status: "rejected" } });
    });
    return (await this.sourceViews([await this.row(id)], language))[0]!;
  }

  async remove(actor: string, id: string) {
    const r = await this.row(id);
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.delete(sources).where(eq(sources.id, id));
      await this.audit.record(tx, this.tenant, { actor, action: "sources.source.deleted", subject: `source:${id}`, before: { url: r.url, themeSlug: r.themeSlug } });
    });
  }

  /** Bronnen die aandacht vragen: nieuw, kapot of veranderd. */
  async review(language: string) {
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select().from(sources)
      .where(or(eq(sources.status, "pending"), and(eq(sources.status, "approved"), or(eq(sources.health, "broken"), eq(sources.changed, true)))))
      .orderBy(asc(sources.createdAt)));
    return this.sourceViews(rows, language);
  }

  /** Eén bron controleren en het resultaat opslaan. */
  async check(id: string, now = new Date()): Promise<CheckResult> {
    const r = await this.row(id);
    const result = await checkSource(r.url, this.deps);
    const next = applyCheck(r, result);
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.update(sources).set({
        ...next, httpStatus: result.httpStatus, finalUrl: result.finalUrl, robotsAllowed: result.robotsAllowed,
        pageTitle: result.pageTitle ?? r.pageTitle, checkNote: result.note, lastCheckedAt: now,
        ...(result.contentHash ? { contentHash: result.contentHash } : {}),
        ...(result.outcome === "ok" ? { lastOkAt: now } : {}),
      }).where(eq(sources.id, id));
      if (r.health !== "broken" && next.health === "broken") {
        await this.audit.record(tx, this.tenant, { actor: "bronnencontrole", action: "sources.source.offline", subject: `source:${id}`, after: { note: result.note } });
      }
    });
    return result;
  }

  /** Bronnen waarvan de laatste controle langer dan een dag geleden is (ook kapotte: die kunnen terugkomen). */
  async due(limit: number, now = new Date()): Promise<string[]> {
    const before = new Date(now.getTime() - RECHECK_HOURS * 3_600_000);
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select({ id: sources.id }).from(sources)
      .where(and(ne(sources.status, "rejected"), or(isNull(sources.lastCheckedAt), lt(sources.lastCheckedAt, before))))
      .orderBy(asc(sources.lastCheckedAt)).limit(limit));
    return rows.map((r) => r.id);
  }

  // ---------- website ----------

  /** Gepubliceerde thema's met minstens één werkende, goedgekeurde bron. */
  async published(language: string): Promise<(ThemeView & { sources: SourceView[] })[]> {
    const list = (await this.themeList(language)).filter((t) => t.status === "published" && t.name && t.counts.live > 0);
    if (!list.length) return [];
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select().from(sources)
      .where(and(inArray(sources.themeSlug, list.map((t) => t.slug)), eq(sources.status, "approved"), eq(sources.health, "ok")))
      .orderBy(asc(sources.sortOrder), asc(sources.createdAt)));
    const views = (await this.sourceViews(rows, language)).filter((s) => s.title);
    return list.map((t) => ({ ...t, sources: views.filter((s) => s.themeSlug === t.slug) })).filter((t) => t.sources.length);
  }
}
