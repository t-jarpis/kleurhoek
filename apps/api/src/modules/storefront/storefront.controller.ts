import { BadRequestException, Controller, Get, NotFoundException, Param, Query, Res } from "@nestjs/common";
import type { FastifyReply } from "fastify";
import { z } from "zod";
import { RateLimit } from "../operations/rate-limit.guard";
import { StorefrontService } from "./storefront.service";

const Slug = z.string().regex(/^[a-z0-9-]{1,64}$/);
const Filter = z.object({
  kind: z.enum(["kleurplaat", "knipplaat", "bouwplaat", "spel", "knutselen"]).optional(),
  category: Slug.optional(), age: z.string().regex(/^[0-9+-]{2,8}$/).optional(), continent: Slug.optional(),
  country: z.string().min(2).max(60).optional(), holiday: Slug.optional(),
}).strict();
const PUBLIC_CACHE = "public, max-age=60, s-maxage=300, stale-while-revalidate=3600";

@Controller("v1")
@RateLimit("public-read")
export class StorefrontController {
  constructor(private readonly store: StorefrontService) {}

  private async market(code: string) {
    const m = await this.store.market(code);
    if (!m) throw new NotFoundException("Onbekende markt");
    return m;
  }

  @Get("markets/:market/plates")
  async plates(@Param("market") code: string, @Query() query: unknown, @Res({ passthrough: true }) res: FastifyReply) {
    const filter = Filter.safeParse(query);
    if (!filter.success) throw new BadRequestException("Ongeldig filter");
    const market = await this.market(code);
    res.header("Cache-Control", PUBLIC_CACHE);
    const items = await this.store.listPlates(market, filter.data);
    return { market: market.code, count: items.length, items };
  }

  @Get("markets/:market/plates/:slug")
  async plate(@Param("market") code: string, @Param("slug") slug: string, @Res({ passthrough: true }) res: FastifyReply) {
    if (!Slug.safeParse(slug).success) throw new NotFoundException();
    const market = await this.market(code);
    const plate = await this.store.plate(market, slug);
    if (!plate) throw new NotFoundException("Plaat niet gevonden");
    res.header("Cache-Control", PUBLIC_CACHE);
    return plate;
  }

  /** Voor de website-route /ga/...: het adres van de partnerlink. De website telt de klik en stuurt door. */
  @Get("markets/:market/products/:product/link")
  async productLink(@Param("market") code: string, @Param("product") product: string, @Query("plate") plate: string | undefined, @Res({ passthrough: true }) res: FastifyReply) {
    if (!/^[a-z0-9-]{2,64}$/.test(product) || (plate !== undefined && !Slug.safeParse(plate).success)) throw new NotFoundException();
    const market = await this.market(code);
    const url = await this.store.productLink(market, product, plate);
    if (!url) throw new NotFoundException("Product niet beschikbaar");
    res.header("Cache-Control", "no-store");
    return { url };
  }

  @Get("markets/:market/taxonomy")
  async taxonomy(@Param("market") code: string, @Res({ passthrough: true }) res: FastifyReply) {
    const market = await this.market(code);
    res.header("Cache-Control", PUBLIC_CACHE);
    return this.store.taxonomy(market);
  }

  @Get("markets/:market/season")
  async season(@Param("market") code: string, @Res({ passthrough: true }) res: FastifyReply) {
    const market = await this.market(code);
    res.header("Cache-Control", "public, max-age=300, s-maxage=900");
    return this.store.season(market);
  }

  /** Versies veranderen nooit, dus het CDN mag ze voor altijd bewaren. */
  @Get("assets/plates/:slug/:file")
  @RateLimit("assets")
  async svg(@Param("slug") slug: string, @Param("file") file: string, @Res() res: FastifyReply) {
    const m = /^(\d{1,6})\.svg$/.exec(file);
    if (!Slug.safeParse(slug).success || !m) throw new NotFoundException();
    const svg = await this.store.svg(slug, Number(m[1]));
    if (!svg) throw new NotFoundException();
    void res.header("Content-Type", "image/svg+xml; charset=utf-8")
      .header("Cache-Control", "public, max-age=31536000, immutable")
      .header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; sandbox")
      .send(svg);
  }
}
