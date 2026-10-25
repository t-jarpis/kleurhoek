import { BadRequestException, Body, Controller, Delete, Get, Param, Post, Put, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { MemberGuard } from "../identity/member.guard";
import { EngagementService, MAX_FAVORITES } from "./engagement.service";

const Slug = z.string().regex(/^[a-z0-9-]{1,64}$/);
const Slugs = z.object({ slugs: z.array(Slug).max(MAX_FAVORITES) }).strict();

/** Favorieten van het eigen account (ADR 0039). */
@Controller("v1/me/favorites")
@UseGuards(MemberGuard)
export class FavoritesController {
  constructor(private readonly engagement: EngagementService) {}

  @Get()
  async list(@Req() req: FastifyRequest) { return { slugs: await this.engagement.favorites(req.member!.userId) }; }

  /** Meerdere tegelijk toevoegen (samenvoegen met wat er op het apparaat stond). */
  @Post()
  async merge(@Body() body: unknown, @Req() req: FastifyRequest) {
    const r = Slugs.safeParse(body);
    if (!r.success) throw new BadRequestException("Ongeldige lijst");
    return { slugs: await this.engagement.add(req.member!.userId, r.data.slugs) };
  }

  @Put(":slug")
  async add(@Param("slug") slug: string, @Req() req: FastifyRequest) {
    if (!Slug.safeParse(slug).success) throw new BadRequestException("Ongeldige plaat");
    return { slugs: await this.engagement.add(req.member!.userId, [slug]) };
  }

  @Delete(":slug")
  async remove(@Param("slug") slug: string, @Req() req: FastifyRequest) {
    if (!Slug.safeParse(slug).success) throw new BadRequestException("Ongeldige plaat");
    return { slugs: await this.engagement.remove(req.member!.userId, [slug]) };
  }
}
