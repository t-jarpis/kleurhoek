import { timingSafeEqual } from "node:crypto";
import { BadRequestException, Body, Controller, Delete, Get, Headers, HttpCode, Inject, NotFoundException, Param, Post, Put, Query, Req, Res, UnauthorizedException, UseGuards } from "@nestjs/common";
import type { FastifyReply, FastifyRequest } from "fastify";
import { z } from "zod";
import { ENV, type Env } from "../../config/env";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "../operations/rate-limit.guard";
import { ages, categories, GOALS, goalName } from "@kleurhoek/catalog-data";
import { CatalogService } from "../catalog/catalog.service";
import { MemberGuard } from "../identity/member.guard";
import { LocalizationService } from "../localization/localization.service";
import { ORG_KINDS } from "./organizations.schema";
import { FONTS, LOGO_MAX_BYTES, OrganizationsService, RESERVED, SLUG, THEMES } from "./organizations.service";

const Color = z.string().regex(/^#[0-9a-fA-F]{6}$/, "Kleur als #rrggbb").nullable().optional();
const List = (item: z.ZodString) => z.array(item).max(50).nullable().optional();
const Slugish = z.string().regex(/^[a-z0-9-]{1,64}$/);
const Input = z.object({
  name: z.string().min(2).max(80).optional(),
  kind: z.enum(ORG_KINDS).optional(),
  active: z.boolean().optional(),
  hosts: z.array(z.string().max(253)).max(10).optional(),
  brand: z.object({
    theme: z.string().max(40).nullable().optional(), font: z.string().max(40).nullable().optional(),
    colors: z.object({ primary: Color, accent: Color }).strict().optional(),
    wordmark: z.string().max(30).nullable().optional(),
  }).strict().optional(),
  offer: z.object({
    markets: List(z.string().regex(/^[a-z]{2}-[a-z]{2}$/i).transform((m) => m.toLowerCase()) as unknown as z.ZodString), categories: List(Slugish), ages: List(z.string().regex(/^[0-9+-]{2,8}$/)),
    kinds: z.array(z.enum(["kleurplaat", "knutselen"])).max(2).nullable().optional(),
    collections: List(Slugish), goals: z.array(z.enum(GOALS as [string, ...string[]])).max(20).nullable().optional(),
    excluded: z.array(Slugish).max(2000).optional(),
  }).strict().optional(),
  features: z.object({ shop: z.boolean().optional(), accounts: z.boolean().optional(), learningFilters: z.boolean().optional() }).strict().optional(),
}).strict();
const SelfOfferInput = z.object({
  collections: z.array(Slugish).max(50).nullable(), goals: z.array(z.enum(GOALS as [string, ...string[]])).max(20).nullable(), excluded: z.array(Slugish).max(2000),
}).strict();
const Manager = z.object({ email: z.string().trim().email().max(254) }).strict();
const Create = Input.extend({ slug: z.string(), name: z.string().min(2).max(80), kind: z.enum(ORG_KINDS) });
const Logo = z.object({ contentType: z.string().max(40), data: z.string().max(Math.ceil(LOGO_MAX_BYTES * 1.4)) }).strict();

const parse = <T>(schema: z.ZodType<T>, body: unknown): T => {
  const r = schema.safeParse(body);
  if (!r.success) throw new BadRequestException(r.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; "));
  return r.data;
};

@Controller("v1/admin/organizations")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminOrganizationsController {
  constructor(private readonly orgs: OrganizationsService, private readonly i18n: LocalizationService, private readonly catalog: CatalogService, @Inject(ENV) private readonly env: Env) {}

  /** Keuzes voor het beheer: thema's, lettertypen, soorten en wat er in het aanbod kan. */
  private async choices() {
    const name = (i: Record<string, { name: string }>) => i.nl?.name ?? Object.values(i)[0]?.name ?? "";
    return {
      themes: THEMES, fonts: FONTS, kinds: ORG_KINDS,
      // Adresvorm van een subdomein in deze omgeving, voor de hint bij het aanmaken.
      hostPattern: this.env.ORG_HOST_PATTERN ?? null,
      reserved: [...RESERVED],
      options: {
        markets: await this.i18n.liveMarkets(this.env.TENANT_ID),
        categories: categories().sort((a, b) => a.order - b.order).map((c) => ({ slug: c.slug, name: name(c.i18n) })),
        ages: ages().sort((a, b) => a.order - b.order).map((a) => ({ slug: a.slug, name: name(a.i18n) })),
        kinds: [{ slug: "kleurplaat", name: "Kleurplaten" }, { slug: "knutselen", name: "Knutselplaten" }],
        goals: GOALS.map((g) => ({ slug: g, name: goalName(g, "nl") })),
        collections: (await this.catalog.collections(this.env.TENANT_ID)).map((c) => ({ slug: c.slug, name: c.names.nl ?? c.slug, plates: c.plates.length })),
      },
    };
  }

  @Get()
  @RequirePermission("organizations.read")
  async list() {
    const orgs = await this.orgs.list(true);
    return { organizations: orgs.map((o) => ({ ...o, subdomain: o.isDefault ? null : this.orgs.subdomain(o.slug) })), ...(await this.choices()) };
  }

  @Get(":slug")
  @RequirePermission("organizations.read")
  async get(@Param("slug") slug: string) {
    const o = await this.orgs.get(slug);
    if (!o) throw new NotFoundException("Onbekende organisatie");
    return { ...o, subdomain: o.isDefault ? null : this.orgs.subdomain(o.slug), ...(await this.choices()) };
  }

  @Post()
  @RequirePermission("organizations.manage")
  async create(@Body() body: unknown, @Req() req: FastifyRequest) {
    const { slug, ...input } = parse(Create, body);
    return this.orgs.create(slug, input, req.admin!.subject);
  }

  @Put(":slug")
  @RequirePermission("organizations.manage")
  async update(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    return this.orgs.update(slug, parse(Input, body), req.admin!.subject);
  }

  @Delete(":slug")
  @RequirePermission("organizations.manage")
  @HttpCode(204)
  async remove(@Param("slug") slug: string, @Req() req: FastifyRequest) {
    if (!SLUG.test(slug)) throw new NotFoundException("Onbekende organisatie");
    await this.orgs.remove(slug, req.admin!.subject);
  }

  /** Beheerders op de site van de organisatie (ADR 0036): websiteaccounts die het aanbod zelf mogen bijstellen. */
  @Get(":slug/managers")
  @RequirePermission("organizations.read")
  async managers(@Param("slug") slug: string) {
    return { managers: await this.orgs.managers(slug) };
  }

  @Post(":slug/managers")
  @RequirePermission("organizations.manage")
  async addManager(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    return { managers: await this.orgs.addManager(slug, parse(Manager, body).email, req.admin!.subject) };
  }

  @Delete(":slug/managers/:userId")
  @RequirePermission("organizations.manage")
  async removeManager(@Param("slug") slug: string, @Param("userId") userId: string, @Req() req: FastifyRequest) {
    if (!/^[0-9a-f-]{36}$/.test(userId)) throw new NotFoundException();
    return { managers: await this.orgs.removeManager(slug, userId, req.admin!.subject) };
  }

  @Put(":slug/logo")
  @RequirePermission("organizations.manage")
  async setLogo(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    const { contentType, data } = parse(Logo, body);
    return this.orgs.setLogo(slug, contentType, Buffer.from(data, "base64"), req.admin!.subject);
  }

  @Delete(":slug/logo")
  @RequirePermission("organizations.manage")
  async removeLogo(@Param("slug") slug: string, @Req() req: FastifyRequest) {
    return this.orgs.setLogo(slug, "", null, req.admin!.subject);
  }
}

function sameSecret(a: string | undefined, b: string): boolean {
  if (!a) return false;
  const x = Buffer.from(a), y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

@Controller("v1")
export class OrganizationsController {
  constructor(private readonly orgs: OrganizationsService, @Inject(ENV) private readonly env: Env) {}

  /** Voor website en inlogpagina: welke organisatie hoort bij deze host (met huisstijl en aanbod). */
  @Get("internal/organizations/resolve")
  @RateLimit("events-ingest")
  async resolve(@Headers("x-ingest-key") key: string | undefined, @Query("host") host: string | undefined) {
    if (!sameSecret(key, this.env.INGEST_KEY)) throw new UnauthorizedException();
    if (!host || host.length > 253) throw new BadRequestException("host ontbreekt");
    return this.orgs.toPublic(await this.orgs.resolve(host));
  }

  /** Voor de website: een organisatie op code (de proxy heeft de host al omgezet). */
  @Get("internal/organizations/:slug")
  @RateLimit("events-ingest")
  async bySlug(@Headers("x-ingest-key") key: string | undefined, @Param("slug") slug: string) {
    if (!sameSecret(key, this.env.INGEST_KEY)) throw new UnauthorizedException();
    const o = SLUG.test(slug) ? await this.orgs.get(slug) : null;
    if (!o || !o.active) throw new NotFoundException();
    return this.orgs.toPublic(o);
  }

  /** Logo per versie: verandert nooit, dus het CDN mag het voor altijd bewaren. SVG in een zandbak. */
  @Get("organizations/:slug/logo/:version")
  @RateLimit("assets")
  async logo(@Param("slug") slug: string, @Param("version") version: string, @Res() res: FastifyReply) {
    if (!SLUG.test(slug) || !/^[0-9a-f]{16}$/.test(version)) throw new NotFoundException();
    const logo = await this.orgs.logo(slug);
    if (!logo || logo.version !== version) throw new NotFoundException();
    void res.header("Content-Type", logo.contentType)
      .header("Cache-Control", "public, max-age=31536000, immutable")
      .header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; sandbox")
      .header("X-Content-Type-Options", "nosniff")
      .send(logo.data);
  }
}

/**
 * Beheer door de organisatie zelf (ADR 0036): een websiteaccount dat beheerder is van een school, bso of bibliotheek
 * stelt daar collecties, leerdoelen en uitgezette platen in. Alleen voor de eigen organisatie.
 */
@Controller("v1/me/organizations")
@UseGuards(MemberGuard)
export class MeOrganizationsController {
  constructor(private readonly orgs: OrganizationsService, private readonly catalog: CatalogService, private readonly i18n: LocalizationService, @Inject(ENV) private readonly env: Env) {}

  @Get()
  async list(@Req() req: FastifyRequest) {
    return { organizations: (await this.orgs.managedBy(req.member!.userId)).map((o) => ({ slug: o.slug, name: o.name, kind: o.kind })) };
  }

  /** Het eigen aanbod met de keuzes en de platen die binnen de grenzen van Kleurhoek vallen, in de gevraagde taal. */
  @Get(":slug")
  async get(@Param("slug") slug: string, @Query("language") language: string | undefined, @Req() req: FastifyRequest) {
    const org = (await this.orgs.managedBy(req.member!.userId)).find((o) => o.slug === slug);
    if (!org) throw new NotFoundException("Onbekende organisatie");
    const lang = language && /^[a-z]{2}$/.test(language) ? language : "nl";
    const tenant = this.env.TENANT_ID;
    const [all, collections] = await Promise.all([this.catalog.listPublished(tenant), this.catalog.collections(tenant)]);
    const o = org.offer;
    // Binnen de vaste grenzen (onderwerpen, leeftijden, soort); collecties, leerdoelen en uitzetten kiest de beheerder hier.
    const inBounds = all.filter((p) => (!o.categories || o.categories.includes(p.category)) && (!o.ages || o.ages.includes(p.age))
      && (!o.kinds || o.kinds.includes(p.kind === "kleurplaat" ? "kleurplaat" : "knutselen")));
    const names = await this.i18n.translate(tenant, "plate", lang, inBounds.map((p) => p.slug));
    const fallback = lang === "nl" ? names : await this.i18n.translate(tenant, "plate", "nl", inBounds.map((p) => p.slug));
    return {
      slug: org.slug, name: org.name, kind: org.kind,
      offer: { collections: o.collections, goals: o.goals, excluded: o.excluded },
      goals: GOALS.map((g) => ({ slug: g, name: goalName(g, lang) })),
      collections: collections.map((c) => ({ slug: c.slug, name: c.names[lang] ?? c.names.nl ?? c.slug, description: c.descriptions[lang] ?? c.descriptions.nl ?? null, plates: c.plates })),
      plates: inBounds.map((p) => ({ slug: p.slug, name: names.get(p.slug)?.name ?? fallback.get(p.slug)?.name ?? p.slug, category: p.category, kind: p.kind, age: p.age, goals: p.goals })),
    };
  }

  @Put(":slug")
  async save(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    const o = await this.orgs.saveSelfOffer(slug, req.member!.userId, parse(SelfOfferInput, body));
    return { offer: { collections: o.offer.collections, goals: o.offer.goals, excluded: o.offer.excluded } };
  }
}
