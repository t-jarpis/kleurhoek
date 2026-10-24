import { Controller, Get, Inject, UseGuards } from "@nestjs/common";
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
