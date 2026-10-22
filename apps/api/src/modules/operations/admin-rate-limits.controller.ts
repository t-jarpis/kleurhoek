import { BadRequestException, Body, Controller, Get, NotFoundException, Param, Put, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "./rate-limit.guard";
import { RateLimitService } from "./rate-limit.service";

const UpdateBody = z.object({
  limit: z.number().int().min(1).max(1_000_000).optional(),
  windowSeconds: z.number().int().min(1).max(86_400).optional(),
  enabled: z.boolean().optional(),
}).strict().refine((b) => Object.keys(b).length > 0, "Geef minstens één veld op");

@Controller("v1/admin/rate-limits")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminRateLimitsController {
  constructor(private readonly limits: RateLimitService) {}

  @Get()
  @RequirePermission("operations.ratelimit.read")
  async list() { return { rules: await this.limits.overview() }; }

  @Put(":slug")
  @RequirePermission("operations.ratelimit.manage")
  async update(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    const parsed = UpdateBody.safeParse(body);
    if (!parsed.success) throw new BadRequestException(parsed.error.issues.map((i) => i.message).join("; "));
    const updated = await this.limits.update(slug, parsed.data, req.admin!.subject);
    if (!updated) throw new NotFoundException(`Onbekende regel: ${slug}`);
    return { slug: updated.slug, limit: updated.limit, windowSeconds: updated.windowSeconds, enabled: updated.enabled };
  }
}
