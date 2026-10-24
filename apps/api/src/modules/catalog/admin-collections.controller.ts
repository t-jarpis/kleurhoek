import { BadRequestException, Body, ConflictException, Controller, Delete, Get, HttpCode, Inject, NotFoundException, Param, Put, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { categories, goalName, GOALS } from "@kleurhoek/catalog-data";
import { z } from "zod";
import { ENV, type Env } from "../../config/env";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { LocalizationService } from "../localization/localization.service";
import { RateLimit } from "../operations/rate-limit.guard";
import { OrganizationsService } from "../organizations/organizations.service";
import { CatalogService } from "./catalog.service";

const SLUG = /^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/;
const Lang = z.string().regex(/^[a-z]{2}$/);
const Input = z.object({
  names: z.record(Lang, z.string().max(80)),
  descriptions: z.record(Lang, z.string().max(300)).optional(),
  plates: z.array(z.string().regex(/^[a-z0-9-]{1,64}$/)).max(500),
  sortOrder: z.number().int().min(0).max(10_000).optional(),
}).strict();

/**
 * Collecties (ADR 0036): samengestelde reeksen platen, om het aanbod van een organisatie op te beperken. Beheer met
 * het recht catalog.manage; lezen met organizations.read, zodat ook wie organisaties inricht ze kan kiezen.
 */
@Controller("v1/admin/collections")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminCollectionsController {
  constructor(private readonly catalog: CatalogService, private readonly i18n: LocalizationService, private readonly orgs: OrganizationsService, @Inject(ENV) private readonly env: Env) {}

  private get tenant() { return this.env.TENANT_ID; }

  @Get()
  @RequirePermission("organizations.read")
  async list() {
    const [collections, plates] = await Promise.all([this.catalog.collections(this.tenant, true), this.catalog.listPublished(this.tenant)]);
    const names = await this.i18n.translate(this.tenant, "plate", "nl", plates.map((p) => p.slug));
    const cat = new Map(categories().map((c) => [c.slug, c.i18n.nl?.name ?? c.slug]));
    return {
      collections,
      // Alle gepubliceerde platen, om uit te kiezen (met naam, onderwerp, soort en leerdoelen voor het zoeken).
      plates: plates.map((p) => ({ slug: p.slug, name: names.get(p.slug)?.name ?? p.slug, category: p.category, categoryName: cat.get(p.category) ?? p.category, kind: p.kind, age: p.age, goals: p.goals })),
      goals: GOALS.map((g) => ({ slug: g, name: goalName(g, "nl") })),
    };
  }

  @Put(":slug")
  @RequirePermission("catalog.manage")
  async save(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    if (!SLUG.test(slug)) throw new BadRequestException("Code: kleine letters, cijfers en streepjes");
    const r = Input.safeParse(body);
    if (!r.success) throw new BadRequestException(r.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; "));
    return this.catalog.saveCollection(this.tenant, slug, r.data, req.admin!.subject);
  }

  @Delete(":slug")
  @RequirePermission("catalog.manage")
  @HttpCode(204)
  async remove(@Param("slug") slug: string) {
    if (!SLUG.test(slug)) throw new NotFoundException();
    // Een organisatie die alleen deze collectie toont, zou anders ineens niets meer laten zien.
    const users = (await this.orgs.list(true)).filter((o) => o.offer.collections?.includes(slug));
    if (users.length) throw new ConflictException(`Deze collectie is in gebruik bij ${users.map((o) => o.name).join(", ")}. Haal hem daar eerst weg.`);
    await this.catalog.deleteCollection(this.tenant, slug);
  }
}
