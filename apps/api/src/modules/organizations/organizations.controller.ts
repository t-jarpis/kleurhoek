import { timingSafeEqual } from "node:crypto";
import { BadRequestException, Body, Controller, Delete, Get, Headers, Inject, NotFoundException, Param, Post, Put, Query, Req, Res, UnauthorizedException, UseGuards } from "@nestjs/common";
import type { FastifyReply, FastifyRequest } from "fastify";
import { z } from "zod";
import { ENV, type Env } from "../../config/env";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "../operations/rate-limit.guard";
import { ages, categories } from "@kleurhoek/catalog-data";
import { LocalizationService } from "../localization/localization.service";
import { ORG_KINDS } from "./organizations.schema";
import { FONTS, LOGO_MAX_BYTES, OrganizationsService, SLUG, THEMES } from "./organizations.service";

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
  }).strict().optional(),
  features: z.object({ shop: z.boolean().optional(), accounts: z.boolean().optional() }).strict().optional(),
}).strict();
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
  constructor(private readonly orgs: OrganizationsService, private readonly i18n: LocalizationService, @Inject(ENV) private readonly env: Env) {}

  /** Keuzes voor het beheer: thema's, lettertypen, soorten en wat er in het aanbod kan. */
  private async choices() {
    const name = (i: Record<string, { name: string }>) => i.nl?.name ?? Object.values(i)[0]?.name ?? "";
    return {
      themes: THEMES, fonts: FONTS, kinds: ORG_KINDS,
      options: {
        markets: await this.i18n.liveMarkets(this.env.TENANT_ID),
        categories: categories().sort((a, b) => a.order - b.order).map((c) => ({ slug: c.slug, name: name(c.i18n) })),
        ages: ages().sort((a, b) => a.order - b.order).map((a) => ({ slug: a.slug, name: name(a.i18n) })),
        kinds: [{ slug: "kleurplaat", name: "Kleurplaten" }, { slug: "knutselen", name: "Knutselplaten" }],
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
