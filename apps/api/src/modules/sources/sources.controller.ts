import { BadRequestException, Body, Controller, Delete, Get, HttpCode, NotFoundException, Param, Post, Put, Query, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "../operations/rate-limit.guard";
import { BASES } from "./sources.schema";
import { SourcesError, SourcesService } from "./sources.service";

const Language = z.object({ language: z.string().regex(/^[a-z]{2}$/).default("nl") });
const Slug = z.string().regex(/^[a-z0-9-]{1,64}$/);
const Id = z.uuid();
const ThemeBody = z.object({
  slug: z.string(), name: z.string().trim().min(2).max(80), description: z.string().trim().min(10).max(600),
  makerName: z.string().trim().min(2).max(80), makerUrl: z.string().max(500),
}).strict();
const ThemeChange = z.object({
  name: z.string().trim().min(2).max(80).optional(), description: z.string().trim().min(10).max(600).optional(),
  makerName: z.string().trim().min(2).max(80).optional(), makerUrl: z.string().max(500).optional(),
  status: z.enum(["draft", "published"]).optional(), sortOrder: z.number().int().min(0).max(10_000).optional(),
  productSlugs: z.array(z.string().regex(/^[a-z0-9-]{2,64}$/)).max(12).optional(),
}).strict();
const SourceBody = z.object({
  url: z.string().max(1000), title: z.string().trim().min(2).max(120), description: z.string().trim().max(400).nullish(),
  basis: z.enum(BASES), licenseNote: z.string().trim().max(1000).nullish(), licenseDate: z.iso.date().nullish(),
}).strict();
const SourceChange = SourceBody.omit({ url: true }).partial().strict();

function parse<T>(schema: z.ZodType<T>, value: unknown): T {
  const r = schema.safeParse(value);
  if (!r.success) throw new BadRequestException(r.error.issues.map((i) => `${i.path.join(".") || "body"}: ${i.message}`).join("; "));
  return r.data;
}
function mapError(e: unknown): never {
  if (e instanceof SourcesError) throw e.code === "not_found" ? new NotFoundException(e.message) : new BadRequestException(e.message);
  throw e;
}
const id = (v: string) => { if (!Id.safeParse(v).success) throw new NotFoundException(); return v; };
const slug = (v: string) => { if (!Slug.safeParse(v).success) throw new NotFoundException(); return v; };

/** Beheer van de Bronnengids (ADR 0024). */
@Controller("v1/admin/sources")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminSourcesController {
  constructor(private readonly sources: SourcesService) {}

  @Get("themes")
  @RequirePermission("sources.read")
  async themes(@Query() q: unknown) { return { themes: await this.sources.themeList(parse(Language, q).language) }; }

  @Post("themes")
  @RequirePermission("sources.manage")
  async createTheme(@Query() q: unknown, @Body() body: unknown, @Req() req: FastifyRequest) {
    return this.sources.createTheme(req.admin!.subject, parse(Language, q).language, parse(ThemeBody, body)).catch(mapError);
  }

  @Get("themes/:slug")
  @RequirePermission("sources.read")
  async theme(@Param("slug") s: string, @Query() q: unknown) { return this.sources.theme(slug(s), parse(Language, q).language).catch(mapError); }

  @Put("themes/:slug")
  @RequirePermission("sources.manage")
  async updateTheme(@Param("slug") s: string, @Query() q: unknown, @Body() body: unknown, @Req() req: FastifyRequest) {
    return this.sources.updateTheme(req.admin!.subject, slug(s), parse(Language, q).language, parse(ThemeChange, body)).catch(mapError);
  }

  @Post("themes/:slug/sources")
  @RequirePermission("sources.manage")
  async addSource(@Param("slug") s: string, @Query() q: unknown, @Body() body: unknown, @Req() req: FastifyRequest) {
    return this.sources.addSource(req.admin!.subject, slug(s), parse(Language, q).language, parse(SourceBody, body)).catch(mapError);
  }

  @Get("review")
  @RequirePermission("sources.read")
  async review(@Query() q: unknown) { return { sources: await this.sources.review(parse(Language, q).language) }; }

  @Put("items/:id")
  @RequirePermission("sources.manage")
  async updateSource(@Param("id") i: string, @Query() q: unknown, @Body() body: unknown, @Req() req: FastifyRequest) {
    return this.sources.updateSource(req.admin!.subject, id(i), parse(Language, q).language, parse(SourceChange, body)).catch(mapError);
  }

  @Post("items/:id/check")
  @RequirePermission("sources.manage")
  async check(@Param("id") i: string) {
    await this.sources.check(id(i)).catch(mapError);
    return { ok: true };
  }

  @Post("items/:id/approve")
  @RequirePermission("sources.manage")
  async approve(@Param("id") i: string, @Query() q: unknown, @Req() req: FastifyRequest) {
    return this.sources.approve(req.admin!.subject, id(i), parse(Language, q).language).catch(mapError);
  }

  @Post("items/:id/reject")
  @RequirePermission("sources.manage")
  async reject(@Param("id") i: string, @Query() q: unknown, @Req() req: FastifyRequest) {
    return this.sources.reject(req.admin!.subject, id(i), parse(Language, q).language).catch(mapError);
  }

  @Delete("items/:id")
  @HttpCode(204)
  @RequirePermission("sources.manage")
  async remove(@Param("id") i: string, @Req() req: FastifyRequest) { await this.sources.remove(req.admin!.subject, id(i)).catch(mapError); }
}
