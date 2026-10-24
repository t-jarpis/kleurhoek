import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { BadRequestException, ConflictException, Inject, Injectable, Logger, NotFoundException, type OnModuleInit } from "@nestjs/common";
import { and, asc, eq } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { accentProblem, HEX, primaryProblem } from "../../shared/contrast";
import { GOALS } from "@kleurhoek/catalog-data";
import { AuditService } from "../identity/audit.service";
import { IdentityService } from "../identity/identity.service";
import { CatalogService } from "../catalog/catalog.service";
import type { SelfOffer } from "./offer";
import { organizationLogos, organizationManagers, organizations, type OrgBrand, type OrgFeatures, type OrgKind, type OrgOffer, type OrgSeo } from "./organizations.schema";

/** Thema's en lettertypen die @kleurhoek/theme levert (generated/manifest.json). */
const manifest = JSON.parse(readFileSync(createRequire(__filename).resolve("@kleurhoek/theme/manifest.json"), "utf8")) as {
  defaultTheme: string; defaultFont: string; themes: { id: string; name: string }[]; fonts: { id: string; family: string }[];
};
export const THEMES = manifest.themes;
export const FONTS = manifest.fonts;

export const SLUG = /^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/;
export const HOST = /^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$/;
/** Subdomeinen die al een functie hebben. */
export const RESERVED = new Set(["www", "dev", "admin", "admin-dev", "login", "login-dev", "api", "mail", "smtp", "status", "static", "cdn", "kleurhoek", "beheer", "test", "staging"]);
export const LOGO_TYPES = ["image/png", "image/webp", "image/jpeg", "image/svg+xml"] as const;
export const LOGO_MAX_BYTES = 256 * 1024;

export const DEFAULT_SLUG = "kleurhoek";
const emptyBrand = (): OrgBrand => ({ theme: null, font: null, colors: { primary: null, accent: null }, wordmark: null, logoVersion: null });
const allOffer = (): OrgOffer => ({ markets: null, categories: null, ages: null, kinds: null, collections: null, goals: null, excluded: [] });
const defaultFeatures = (): OrgFeatures => ({ shop: true, accounts: true, learningFilters: false });

export interface Organization {
  id: string; slug: string; name: string; kind: OrgKind; active: boolean; isDefault: boolean; hosts: string[];
  brand: OrgBrand; offer: OrgOffer; features: OrgFeatures; seo: OrgSeo; updatedBy: string; updatedAt: string;
}
export const emptySeo = (): OrgSeo => ({ googleVerification: null, bingVerification: null, home: {} });
/** Wat de website, het admin panel en de inlogpagina van een organisatie mogen weten. */
export interface PublicOrganization {
  slug: string; name: string; kind: OrgKind; isDefault: boolean; brand: OrgBrand; offer: OrgOffer; features: OrgFeatures;
  logo: string | null;
  /** Alleen bij Kleurhoek zelf; organisaties worden niet geïndexeerd (ADR 0035). */
  seo: OrgSeo | null;
}

export interface OrgInput {
  name?: string | undefined; kind?: OrgKind | undefined; active?: boolean | undefined; hosts?: string[] | undefined;
  brand?: { theme?: string | null | undefined; font?: string | null | undefined; colors?: { primary?: string | null | undefined; accent?: string | null | undefined } | undefined; wordmark?: string | null | undefined } | undefined;
  offer?: Partial<OrgOffer> | undefined; features?: Partial<OrgFeatures> | undefined;
}

const TTL_MS = 30_000;

@Injectable()
export class OrganizationsService implements OnModuleInit {
  private readonly log = new Logger(OrganizationsService.name);
  private cache: { at: number; orgs: Organization[] } | null = null;

  constructor(
    @Inject(DB) private readonly db: Database,
    @Inject(ENV) private readonly env: Env,
    private readonly audit: AuditService,
    private readonly identity: IdentityService,
    private readonly catalog: CatalogService,
  ) {}

  private get tenant() { return this.env.TENANT_ID; }

  async onModuleInit() {
    // Kleurhoek zelf bestaat altijd: de standaardorganisatie voor de eigen domeinen en onbekende hosts.
    await withTenant(this.db, this.tenant, (tx) => tx.insert(organizations).values({
      tenantId: this.tenant, slug: DEFAULT_SLUG, name: "Kleurhoek", kind: "platform", isDefault: true,
      brand: emptyBrand(), offer: allOffer(), features: defaultFeatures(),
    }).onConflictDoNothing());
  }

  private toModel(r: typeof organizations.$inferSelect): Organization {
    return {
      id: r.id, slug: r.slug, name: r.name, kind: r.kind, active: r.active, isDefault: r.isDefault, hosts: r.hosts,
      brand: { ...emptyBrand(), ...r.brand, colors: { ...emptyBrand().colors, ...r.brand.colors } },
      offer: { ...allOffer(), ...r.offer }, features: { ...defaultFeatures(), ...r.features },
      seo: { ...emptySeo(), ...(r.seo ?? {}) },
      updatedBy: r.updatedBy, updatedAt: r.updatedAt.toISOString(),
    };
  }

  async list(fresh = false): Promise<Organization[]> {
    if (!fresh && this.cache && Date.now() - this.cache.at < TTL_MS) return this.cache.orgs;
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select().from(organizations).where(eq(organizations.tenantId, this.tenant)).orderBy(asc(organizations.name)));
    const orgs = rows.map((r) => this.toModel(r));
    this.cache = { at: Date.now(), orgs };
    return orgs;
  }

  async get(slug: string): Promise<Organization | null> {
    return (await this.list()).find((o) => o.slug === slug) ?? null;
  }

  async defaultOrg(): Promise<Organization> {
    const orgs = await this.list();
    return orgs.find((o) => o.isDefault) ?? orgs[0]!;
  }

  /** Host van een verzoek → organisatie. Vaste hosts eerst, dan het subdomeinpatroon, anders Kleurhoek zelf. */
  async resolve(host: string): Promise<Organization> {
    const h = host.toLowerCase().replace(/:\d+$/, "").replace(/\.$/, "");
    const orgs = (await this.list()).filter((o) => o.active);
    const exact = orgs.find((o) => o.hosts.includes(h));
    if (exact) return exact;
    const pattern = this.env.ORG_HOST_PATTERN;
    if (pattern) {
      const [pre, post] = pattern.split("{slug}") as [string, string];
      if (h.startsWith(pre) && h.endsWith(post)) {
        const slug = h.slice(pre.length, h.length - post.length);
        const bySlug = orgs.find((o) => o.slug === slug && !o.isDefault);
        if (bySlug) return bySlug;
      }
    }
    return this.defaultOrg();
  }

  /** Het subdomein van een organisatie volgens het patroon, of null. */
  subdomain(slug: string): string | null {
    return this.env.ORG_HOST_PATTERN ? this.env.ORG_HOST_PATTERN.replace("{slug}", slug) : null;
  }

  toPublic(o: Organization): PublicOrganization {
    return { slug: o.slug, name: o.name, kind: o.kind, isDefault: o.isDefault, brand: o.brand, offer: o.offer, features: o.features, logo: o.brand.logoVersion ? `/v1/organizations/${o.slug}/logo/${o.brand.logoVersion}` : null, seo: o.isDefault ? o.seo : null };
  }

  private validate(input: OrgInput, current: Organization | null, all: Organization[]) {
    const problems: string[] = [];
    if (input.name !== undefined && (input.name.trim().length < 2 || input.name.length > 80)) problems.push("Naam: 2 tot 80 tekens");
    for (const h of input.hosts ?? []) {
      if (!HOST.test(h)) problems.push(`Ongeldig domein: ${h}`);
      const other = all.find((o) => o.id !== current?.id && o.hosts.includes(h));
      if (other) problems.push(`${h} hoort al bij ${other.name}`);
    }
    const b = input.brand;
    if (b?.theme && !THEMES.some((t) => t.id === b.theme)) problems.push(`Onbekend thema: ${b.theme}`);
    if (b?.font && !FONTS.some((f) => f.id === b.font)) problems.push(`Onbekend lettertype: ${b.font}`);
    for (const [key, check] of [["primary", primaryProblem], ["accent", accentProblem]] as const) {
      const v = b?.colors?.[key];
      if (v == null) continue;
      if (!HEX.test(v)) { problems.push(`Kleur ${key}: gebruik #rrggbb`); continue; }
      const p = check(v);
      if (p) problems.push(p);
    }
    if (b?.wordmark != null && (b.wordmark.length > 30 || /[<>]/.test(b.wordmark))) problems.push("Woordmerk: maximaal 30 tekens");
    if (problems.length) throw new BadRequestException(problems.join("; "));
  }

  /** Collecties en leerdoelen in een aanbod moeten bestaan (ADR 0036). */
  private async validateOffer(offer: Partial<OrgOffer> | undefined) {
    if (!offer) return;
    const problems: string[] = [];
    if (offer.collections) {
      const known = new Set((await this.catalog.collections(this.tenant)).map((c) => c.slug));
      for (const c of offer.collections) if (!known.has(c)) problems.push(`Onbekende collectie: ${c}`);
      if (!offer.collections.length) problems.push("Kies minstens één collectie, of laat alle platen toe");
    }
    if (offer.goals) {
      for (const g of offer.goals) if (!(GOALS as string[]).includes(g)) problems.push(`Onbekend leerdoel: ${g}`);
      if (!offer.goals.length) problems.push("Kies minstens één leerdoel, of laat alle leerdoelen toe");
    }
    if (problems.length) throw new BadRequestException(problems.join("; "));
  }

  private merge(o: Organization, input: OrgInput): Organization {
    return {
      ...o,
      ...(input.name !== undefined ? { name: input.name.trim() } : {}),
      ...(input.kind !== undefined ? { kind: input.kind } : {}),
      ...(input.active !== undefined ? { active: input.active } : {}),
      ...(input.hosts !== undefined ? { hosts: [...new Set(input.hosts.map((h) => h.toLowerCase()))] } : {}),
      brand: input.brand ? {
        ...o.brand,
        ...(input.brand.theme !== undefined ? { theme: input.brand.theme } : {}),
        ...(input.brand.font !== undefined ? { font: input.brand.font } : {}),
        ...(input.brand.wordmark !== undefined ? { wordmark: input.brand.wordmark?.trim() || null } : {}),
        colors: { ...o.brand.colors, ...Object.fromEntries(Object.entries(input.brand.colors ?? {}).filter(([, v]) => v !== undefined).map(([k, v]) => [k, v ? v.toLowerCase() : null])) },
      } : o.brand,
      offer: input.offer ? { ...o.offer, ...Object.fromEntries(Object.entries(input.offer).filter(([, v]) => v !== undefined)) } : o.offer,
      features: input.features ? { ...o.features, ...Object.fromEntries(Object.entries(input.features).filter(([, v]) => v !== undefined)) } : o.features,
    };
  }

  async create(slug: string, input: OrgInput & { name: string; kind: OrgKind }, actor: string): Promise<Organization> {
    // Eindigt een code op -dev, dan zou {code}.kleurhoek.nl in productie bij de Worker als dev-adres gelden.
    if (!SLUG.test(slug) || RESERVED.has(slug) || slug.endsWith("-dev")) throw new BadRequestException("Code: kleine letters, cijfers en streepjes (2–32), geen gereserveerd woord en niet eindigend op -dev");
    const all = await this.list(true);
    if (all.some((o) => o.slug === slug)) throw new ConflictException(`Er is al een organisatie met code ${slug}`);
    const base: Organization = {
      id: "", slug, name: input.name, kind: input.kind, active: true, isDefault: false, hosts: [], brand: emptyBrand(), offer: allOffer(),
      features: { shop: input.kind === "platform", accounts: false, learningFilters: input.kind === "school" || input.kind === "opvang" }, seo: emptySeo(), updatedBy: actor, updatedAt: "",
    };
    this.validate(input, null, all);
    await this.validateOffer(input.offer);
    const next = this.merge(base, input);
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.insert(organizations).values({ tenantId: this.tenant, slug, name: next.name, kind: next.kind, active: next.active, hosts: next.hosts, brand: next.brand, offer: next.offer, features: next.features, updatedBy: actor });
      await this.audit.record(tx, this.tenant, { actor, action: "organizations.create", subject: `organization:${slug}`, after: { name: next.name, kind: next.kind } });
    });
    this.cache = null;
    return (await this.get(slug))!;
  }

  async update(slug: string, input: OrgInput, actor: string): Promise<Organization> {
    const all = await this.list(true);
    const current = all.find((o) => o.slug === slug);
    if (!current) throw new NotFoundException("Onbekende organisatie");
    if (current.isDefault && input.active === false) throw new BadRequestException("Kleurhoek zelf kan niet uit");
    this.validate(input, current, all);
    await this.validateOffer(input.offer);
    const next = this.merge(current, input);
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.update(organizations).set({ name: next.name, kind: next.kind, active: next.active, hosts: next.hosts, brand: next.brand, offer: next.offer, features: next.features, updatedBy: actor, updatedAt: new Date() })
        .where(and(eq(organizations.tenantId, this.tenant), eq(organizations.id, current.id)));
      await this.audit.record(tx, this.tenant, { actor, action: "organizations.update", subject: `organization:${slug}`, before: { ...current, updatedAt: undefined }, after: { ...next, updatedAt: undefined } });
    });
    this.cache = null;
    return (await this.get(slug))!;
  }

  /** Vindbaarheid van Kleurhoek zelf (ADR 0035). Verificatiecodes zijn de "content"-waarde uit de meta-tag. */
  async saveSeo(seo: OrgSeo, actor: string): Promise<OrgSeo> {
    const problems: string[] = [];
    const TOKEN = /^[A-Za-z0-9_-]{10,100}$/;
    for (const [k, v] of [["Google", seo.googleVerification], ["Bing", seo.bingVerification]] as const) if (v && !TOKEN.test(v)) problems.push(`${k}-code: alleen letters, cijfers, - en _ (10 tot 100 tekens)`);
    for (const [market, h] of Object.entries(seo.home)) {
      if (!/^[a-z]{2}-[A-Z]{2}$/.test(market)) problems.push(`Onbekende markt: ${market}`);
      if (h.title && h.title.length > 70) problems.push(`${market}: titel hooguit 70 tekens`);
      if (h.description && h.description.length > 170) problems.push(`${market}: beschrijving hooguit 170 tekens`);
    }
    if (problems.length) throw new BadRequestException(problems.join("; "));
    const org = await this.defaultOrg();
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.update(organizations).set({ seo, updatedBy: actor, updatedAt: new Date() }).where(and(eq(organizations.tenantId, this.tenant), eq(organizations.id, org.id)));
      await this.audit.record(tx, this.tenant, { actor, action: "seo.update", subject: `organization:${org.slug}`, before: org.seo, after: seo });
    });
    this.cache = null;
    return seo;
  }

  async setLogo(slug: string, contentType: string, data: Buffer | null, actor: string): Promise<Organization> {
    const org = await this.get(slug);
    if (!org) throw new NotFoundException("Onbekende organisatie");
    let version: string | null = null;
    if (data) {
      if (!(LOGO_TYPES as readonly string[]).includes(contentType)) throw new BadRequestException("Logo: PNG, WebP, JPEG of SVG");
      if (data.length > LOGO_MAX_BYTES) throw new BadRequestException("Logo: maximaal 256 kB");
      if (contentType === "image/svg+xml" && /<script|\son[a-z]+\s*=|javascript:|<foreignObject|<iframe|<!entity/i.test(data.toString("utf8"))) {
        throw new BadRequestException("Dit SVG-bestand bevat scripts of verwijzingen die niet zijn toegestaan");
      }
      version = createHash("sha256").update(data).digest("hex").slice(0, 16);
    }
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.delete(organizationLogos).where(and(eq(organizationLogos.tenantId, this.tenant), eq(organizationLogos.organizationId, org.id)));
      if (data && version) await tx.insert(organizationLogos).values({ tenantId: this.tenant, organizationId: org.id, contentType, sha256: version, data });
      await tx.update(organizations).set({ brand: { ...org.brand, logoVersion: version }, updatedBy: actor, updatedAt: new Date() }).where(eq(organizations.id, org.id));
      await this.audit.record(tx, this.tenant, { actor, action: "organizations.logo", subject: `organization:${slug}`, before: { logo: org.brand.logoVersion }, after: { logo: version } });
    });
    this.cache = null;
    this.log.log(`Logo van ${slug} ${version ? "gezet" : "verwijderd"} door ${actor}`);
    return (await this.get(slug))!;
  }

  /**
   * Organisatie verwijderen (met haar logo). Kleurhoek zelf kan niet weg. Dagtotalen van analytics
   * blijven staan onder de oude code; een nieuwe organisatie met dezelfde code telt daar dus bij op.
   */
  async remove(slug: string, actor: string): Promise<void> {
    const org = await this.get(slug);
    if (!org) throw new NotFoundException("Onbekende organisatie");
    if (org.isDefault) throw new BadRequestException("Kleurhoek zelf kan niet worden verwijderd");
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.delete(organizationLogos).where(and(eq(organizationLogos.tenantId, this.tenant), eq(organizationLogos.organizationId, org.id)));
      await tx.delete(organizations).where(and(eq(organizations.tenantId, this.tenant), eq(organizations.id, org.id)));
      await this.audit.record(tx, this.tenant, { actor, action: "organizations.delete", subject: `organization:${slug}`, before: { name: org.name, kind: org.kind, hosts: org.hosts } });
    });
    this.cache = null;
    this.log.log(`Organisatie ${slug} verwijderd door ${actor}`);
  }

  async logo(slug: string): Promise<{ contentType: string; data: Buffer; version: string } | null> {
    const org = await this.get(slug);
    if (!org?.brand.logoVersion) return null;
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select().from(organizationLogos).where(and(eq(organizationLogos.tenantId, this.tenant), eq(organizationLogos.organizationId, org.id))).limit(1));
    return row ? { contentType: row.contentType, data: Buffer.from(row.data), version: row.sha256 } : null;
  }

  // ---------- Beheerders van een organisatie (ADR 0036) ----------

  /** Beheerders met naam en e-mailadres. Accounts die niet meer bestaan vallen weg. */
  async managers(slug: string): Promise<{ userId: string; displayName: string | null; email: string | null; since: string }[]> {
    const org = await this.get(slug);
    if (!org) throw new NotFoundException("Onbekende organisatie");
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select().from(organizationManagers)
      .where(and(eq(organizationManagers.tenantId, this.tenant), eq(organizationManagers.organizationId, org.id))).orderBy(asc(organizationManagers.createdAt)));
    const users = new Map((await this.identity.getUsers(rows.map((r) => r.userId))).map((u) => [u.id, u]));
    return rows.filter((r) => users.has(r.userId)).map((r) => ({ userId: r.userId, displayName: users.get(r.userId)!.displayName, email: users.get(r.userId)!.email, since: r.createdAt.toISOString() }));
  }

  /** Een websiteaccount beheerder maken. Het account moet al bestaan: de persoon logt eerst één keer in op de site. */
  async addManager(slug: string, email: string, actor: string) {
    const org = await this.get(slug);
    if (!org) throw new NotFoundException("Onbekende organisatie");
    if (org.isDefault) throw new BadRequestException("Kleurhoek zelf heeft geen beheerders op de site; gebruik het admin panel");
    const user = await this.identity.findMemberByEmail(email);
    if (!user) throw new BadRequestException("Geen account met dit e-mailadres. Laat de persoon eerst één keer inloggen op de site.");
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.insert(organizationManagers).values({ tenantId: this.tenant, organizationId: org.id, userId: user.id, createdBy: actor }).onConflictDoNothing();
      await this.audit.record(tx, this.tenant, { actor, action: "organizations.manager.add", subject: `organization:${slug}`, after: { userId: user.id } });
    });
    return this.managers(slug);
  }

  async removeManager(slug: string, userId: string, actor: string) {
    const org = await this.get(slug);
    if (!org) throw new NotFoundException("Onbekende organisatie");
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.delete(organizationManagers).where(and(eq(organizationManagers.tenantId, this.tenant), eq(organizationManagers.organizationId, org.id), eq(organizationManagers.userId, userId)));
      await this.audit.record(tx, this.tenant, { actor, action: "organizations.manager.remove", subject: `organization:${slug}`, before: { userId } });
    });
    return this.managers(slug);
  }

  /** De organisaties die een websiteaccount mag beheren (alleen actieve). */
  async managedBy(userId: string): Promise<Organization[]> {
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select({ organizationId: organizationManagers.organizationId }).from(organizationManagers)
      .where(and(eq(organizationManagers.tenantId, this.tenant), eq(organizationManagers.userId, userId))));
    const ids = new Set(rows.map((r) => r.organizationId));
    return (await this.list()).filter((o) => ids.has(o.id) && o.active);
  }

  /** Een account verdwijnt: ook als beheerder (privacy, ADR 0002). */
  async forgetUser(userId: string) {
    await withTenant(this.db, this.tenant, (tx) => tx.delete(organizationManagers).where(and(eq(organizationManagers.tenantId, this.tenant), eq(organizationManagers.userId, userId))));
  }

  /**
   * Een beheerder van de organisatie stelt zelf collecties, leerdoelen en uitgezette platen in. Markten, onderwerpen,
   * huisstijl en functies blijven bij Kleurhoek.
   */
  async saveSelfOffer(slug: string, userId: string, input: SelfOffer): Promise<Organization> {
    const org = (await this.managedBy(userId)).find((o) => o.slug === slug);
    if (!org) throw new NotFoundException("Onbekende organisatie");
    await this.validateOffer(input);
    const published = new Set((await this.catalog.listPublished(this.tenant)).map((p) => p.slug));
    const excluded = [...new Set(input.excluded)].filter((s) => published.has(s));
    const offer: OrgOffer = { ...org.offer, collections: input.collections, goals: input.goals, excluded };
    await withTenant(this.db, this.tenant, async (tx) => {
      await tx.update(organizations).set({ offer, updatedBy: `user:${userId}`, updatedAt: new Date() }).where(and(eq(organizations.tenantId, this.tenant), eq(organizations.id, org.id)));
      await this.audit.record(tx, this.tenant, { actor: `user:${userId}`, action: "organizations.offer.self", subject: `organization:${slug}`, before: org.offer, after: offer });
    });
    this.cache = null;
    return (await this.get(slug))!;
  }
}
