import { BadRequestException, Body, Controller, Get, Inject, NotFoundException, Param, Post, Put, Query, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { ENV, type Env } from "../../config/env";
import { CatalogService } from "../catalog/catalog.service";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { LocalizationService } from "../localization/localization.service";
import { RateLimit } from "../operations/rate-limit.guard";
import { ShopError, ShopService } from "./shop.service";
import { PRODUCT_SUGGESTIONS } from "./shop.suggestions";

const Language = z.object({ language: z.string().regex(/^[a-z]{2}$/).default("nl") });
const PartnerBody = z.object({
  enabled: z.boolean().optional(),
  linkTemplate: z.string().min(5).max(500).optional(),
  settings: z.record(z.string(), z.string().max(64)).optional(),
}).strict();
const NewPartnerBody = z.object({
  slug: z.string(),
  name: z.string().trim().min(2).max(60),
  linkTemplate: z.string().min(5).max(500),
  allowedHosts: z.array(z.string().trim().toLowerCase()).min(1).max(10),
}).strict();
const ProductBody = z.object({
  partner: z.string().regex(/^[a-z0-9-]{2,32}$/),
  url: z.string().max(1000),
  ean: z.string().regex(/^\d{8,14}$/).nullish(),
  priceHint: z.string().max(40).nullish(),
  enabled: z.boolean(),
  markets: z.array(z.string().regex(/^[a-z]{2}-[A-Z]{2}$/)).min(1).max(50),
  name: z.string().trim().min(2).max(120),
  note: z.string().trim().max(200).nullish(),
  materials: z.array(z.string().regex(/^[a-z0-9-]{1,64}$/)).max(20),
  rank: z.number().int().min(0).max(99).optional(),
}).strict();
const ImportBody = z.object({ slugs: z.array(z.string().regex(/^[a-z0-9-]{2,64}$/)).min(1).max(50) }).strict();

function parse<T>(schema: z.ZodType<T>, value: unknown): T {
  const r = schema.safeParse(value);
  if (!r.success) throw new BadRequestException(r.error.issues.map((i) => `${i.path.join(".") || "body"}: ${i.message}`).join("; "));
  return r.data;
}
function mapError(e: unknown): never {
  if (e instanceof ShopError) throw e.code === "not_found" ? new NotFoundException(e.message) : new BadRequestException(e.message);
  throw e;
}

/** Winkelbeheer: koppelingen met partners (bijv. je bol-site-ID) en producten bij materialen. */
@Controller("v1/admin/shop")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminShopController {
  constructor(
    private readonly shop: ShopService,
    private readonly catalog: CatalogService,
    private readonly i18n: LocalizationService,
    @Inject(ENV) private readonly env: Env,
  ) {}

  @Get("partners")
  @RequirePermission("shop.read")
  async partners() { return { partners: await this.shop.partners() }; }

  @Post("partners")
  @RequirePermission("shop.manage")
  async createPartner(@Body() body: unknown, @Req() req: FastifyRequest) {
    return { slug: await this.shop.createPartner(req.admin!.subject, parse(NewPartnerBody, body)).catch(mapError) };
  }

  @Put("partners/:slug")
  @RequirePermission("shop.manage")
  async updatePartner(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    return this.shop.updatePartner(req.admin!.subject, slug, parse(PartnerBody, body)).catch(mapError);
  }

  @Get("products")
  @RequirePermission("shop.read")
  async products(@Query() query: unknown) {
    const { language } = parse(Language, query);
    const [products, materialSlugs, partners] = await Promise.all([this.shop.products(language), this.catalog.materials(this.env.TENANT_ID), this.shop.partners()]);
    const names = await this.i18n.translate(this.env.TENANT_ID, "material", language, materialSlugs);
    return {
      products,
      materials: materialSlugs.map((slug) => ({ slug, name: names.get(slug)?.name ?? slug })),
      partners: partners.map((p) => ({ slug: p.slug, name: p.name, enabled: p.enabled, allowedHosts: p.allowedHosts })),
      suggestions: this.openSuggestions(products.map((p) => p.slug), materialSlugs, partners.map((p) => p.slug)),
    };
  }

  /** Voorstellen die nog niet zijn toegevoegd en waarvan partner en materialen bestaan. */
  private openSuggestions(existing: string[], materials: string[], partners: string[]) {
    const have = new Set(existing), known = new Set(materials), partnerSet = new Set(partners);
    return PRODUCT_SUGGESTIONS.filter((s) => !have.has(s.slug) && partnerSet.has(s.partner) && s.materials.every((m) => known.has(m)));
  }

  /** Voorgestelde producten toevoegen (zichtbaar). Bestaande producten met dezelfde code blijven ongemoeid. */
  @Post("products/suggestions")
  @RequirePermission("shop.manage")
  async importSuggestions(@Query() query: unknown, @Body() body: unknown, @Req() req: FastifyRequest) {
    const { language } = parse(Language, query);
    const { slugs } = parse(ImportBody, body);
    const [products, materialSlugs, partners] = await Promise.all([this.shop.products(language), this.catalog.materials(this.env.TENANT_ID), this.shop.partners()]);
    const open = this.openSuggestions(products.map((p) => p.slug), materialSlugs, partners.map((p) => p.slug));
    const picked = open.filter((s) => slugs.includes(s.slug));
    const added: string[] = [];
    for (const s of picked) {
      added.push(await this.shop.saveProduct(req.admin!.subject, language, { slug: s.slug, partner: s.partner, url: s.url, enabled: true, markets: s.markets, name: s.name, note: s.note, materials: s.materials }).catch(mapError));
    }
    return { added };
  }

  @Put("products/:slug")
  @RequirePermission("shop.manage")
  async saveProduct(@Param("slug") slug: string, @Query() query: unknown, @Body() body: unknown, @Req() req: FastifyRequest) {
    const { language } = parse(Language, query);
    const input = parse(ProductBody, body);
    const known = new Set(await this.catalog.materials(this.env.TENANT_ID));
    const unknown = input.materials.filter((m) => !known.has(m));
    if (unknown.length) throw new BadRequestException(`Onbekend materiaal: ${unknown.join(", ")}`);
    return { slug: await this.shop.saveProduct(req.admin!.subject, language, { slug, ...input }).catch(mapError) };
  }
}
