import { BadRequestException, ConflictException, Controller, ForbiddenException, Get, NotFoundException, Param, ParseUUIDPipe, Post, Query, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { RateLimit } from "../operations/rate-limit.guard";
import { AdminGuard, RequirePermission } from "./admin.guard";
import { ChangesError, ChangesService } from "./changes.service";

function mapError(e: unknown): never {
  if (e instanceof ChangesError) {
    if (e.code === "not_found") throw new NotFoundException(e.message);
    if (e.code === "forbidden") throw new ForbiddenException(e.message);
    if (e.code === "outdated") throw new ConflictException(e.message);
    throw new BadRequestException(e.message);
  }
  throw e;
}

/** Wijzigingen (auditlog) en ongedaan maken (ADR 0066). Terugzetten vraagt daarnaast het recht van het domein. */
@Controller("v1/admin/changes")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class ChangesController {
  constructor(private readonly changes: ChangesService) {}

  @Get()
  @RequirePermission("audit.read")
  async list(@Req() req: FastifyRequest, @Query("before") before?: string) {
    const at = before ? new Date(before) : undefined;
    if (at && Number.isNaN(at.getTime())) throw new BadRequestException("before: geen geldige datum");
    return { items: await this.changes.list(req.admin!, { before: at }) };
  }

  @Post(":id/undo")
  @RequirePermission("audit.read")
  async undo(@Req() req: FastifyRequest, @Param("id", ParseUUIDPipe) id: string) {
    await this.changes.revert(id, req.admin!).catch(mapError);
    return { ok: true };
  }
}
