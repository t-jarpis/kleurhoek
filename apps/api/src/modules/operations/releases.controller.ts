import { Controller, Get, Inject, Res, UseGuards } from "@nestjs/common";
import type { FastifyReply } from "fastify";
import { ENV, type Env } from "../../config/env";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "./rate-limit.guard";
import { ReleasesService } from "./releases.service";

/** Releasenotes per uitrol in deze omgeving (ADR 0023). */
@Controller("v1/admin/releases")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminReleasesController {
  constructor(private readonly releases: ReleasesService, @Inject(ENV) private readonly env: Env) {}

  @Get()
  @RequirePermission("releases.read")
  async list() {
    return { current: this.env.BUILD_SHA ?? null, releases: await this.releases.list() };
  }
}

/** Wat is er nieuw (ADR 0080): alleen de teksten voor bezoekers (Public-note), voor de website. */
@Controller("v1/news")
@RateLimit("public-read")
export class PublicNewsController {
  constructor(private readonly releases: ReleasesService) {}

  @Get()
  async list(@Res({ passthrough: true }) res: FastifyReply) {
    res.header("Cache-Control", "public, max-age=300, s-maxage=600");
    return { items: await this.releases.publicNotes() };
  }
}
