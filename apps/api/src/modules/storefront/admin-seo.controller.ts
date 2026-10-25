import { BadRequestException, Body, Controller, Get, Put, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "../operations/rate-limit.guard";
import { OrganizationsService } from "../organizations/organizations.service";
import { StorefrontService } from "./storefront.service";

const Seo = z.object({
  googleVerification: z.string().trim().max(100).nullable(),
  bingVerification: z.string().trim().max(100).nullable(),
  home: z.record(z.string().regex(/^[a-z]{2}-[A-Z]{2}$/), z.object({ title: z.string().trim().max(70).nullable(), description: z.string().trim().max(170).nullable() })),
}).strict();

/**
 * Vindbaarheid (ADR 0035): instellingen en de stand per markt. Alleen Kleurhoek zelf op het productiedomein
 * wordt geïndexeerd; dev en organisaties krijgen noindex. Dit leest wat in de sitemap komt.
 */
@Controller("v1/admin/seo")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminSeoController {
  constructor(private readonly store: StorefrontService, private readonly orgs: OrganizationsService) {}

  @Get()
  @RequirePermission("seo.read")
  async get() {
    const org = await this.orgs.defaultOrg();
    const codes = await this.store.liveMarkets();
    const markets = [];
    for (const code of codes) {
      const market = await this.store.market(code);
      if (!market) continue;
      const [plates, themes] = await Promise.all([this.store.listPlates(market, {}), this.store.themes(market)]);
      markets.push({ market: market.code, language: market.language, plates: plates.length, themes: themes.length });
    }
    // Per land een domein (ADR 0040): kleurhoek.nl, .be (nl en fr) en .com (overige markten).
    return { settings: org.seo, markets, indexableHost: "www.kleurhoek.nl", indexableHosts: ["www.kleurhoek.nl", "www.kleurhoek.be", "www.kleurhoek.com"] };
  }

  @Put()
  @RequirePermission("seo.manage")
  async save(@Body() body: unknown, @Req() req: FastifyRequest) {
    const r = Seo.safeParse(body);
    if (!r.success) throw new BadRequestException(r.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; "));
    const clean = (v: string | null) => (v && v.trim() ? v.trim() : null);
    return this.orgs.saveSeo({
      googleVerification: clean(r.data.googleVerification), bingVerification: clean(r.data.bingVerification),
      home: Object.fromEntries(Object.entries(r.data.home).map(([k, h]) => [k, { title: clean(h.title), description: clean(h.description) }])),
    }, req.admin!.subject);
  }
}
