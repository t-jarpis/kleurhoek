import { BadRequestException, Body, ConflictException, Controller, ForbiddenException, Get, NotFoundException, Param, ParseUUIDPipe, Put, Query, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { RateLimit } from "../operations/rate-limit.guard";
import { AdminGuard, RequireAdmin, RequirePermission } from "./admin.guard";
import { IdentityError, IdentityService } from "./identity.service";
import { PERMISSIONS } from "./permissions";

const ListQuery = z.object({
  kind: z.enum(["member", "admin"]).optional(),
  q: z.string().trim().min(1).max(100).optional(),
  page: z.coerce.number().int().min(1).max(10_000).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(25),
});
const RolesBody = z.object({ roles: z.array(z.string().regex(/^[a-z][a-z0-9-]{1,40}$/)).max(20) }).strict();
const StatusBody = z.object({ status: z.enum(["active", "blocked"]) }).strict();

function parse<T>(schema: z.ZodType<T>, value: unknown): T {
  const r = schema.safeParse(value);
  if (!r.success) throw new BadRequestException(r.error.issues.map((i) => `${i.path.join(".") || "body"}: ${i.message}`).join("; "));
  return r.data;
}

function mapError(error: unknown): never {
  if (error instanceof IdentityError) {
    if (error.code === "not_found") throw new NotFoundException(error.message);
    if (error.code === "self") throw new ForbiddenException(error.message);
    if (error.code === "not_admin") throw new ConflictException(error.message);
    throw new BadRequestException(error.message);
  }
  throw error;
}

@Controller("v1/admin")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminUsersController {
  constructor(private readonly identity: IdentityService) {}

  /** Wie ben ik in het admin panel, en wat mag ik? Gebruikt om het menu te tonen. */
  @Get("me")
  @RequireAdmin()
  async me(@Req() req: FastifyRequest) {
    return { userId: req.admin!.userId, subject: req.admin!.subject, permissions: req.admin!.permissions };
  }

  @Get("users")
  @RequirePermission("identity.users.read")
  async list(@Query() query: unknown) {
    const q = parse(ListQuery, query);
    const { users, total } = await this.identity.listUsers(q);
    return { users, total, page: q.page, pageSize: q.pageSize };
  }

  @Get("roles")
  @RequirePermission("identity.users.read")
  async roles() {
    return { roles: await this.identity.listRoles(), permissions: PERMISSIONS };
  }

  @Put("users/:id/roles")
  @RequirePermission("identity.roles.assign")
  async setRoles(@Param("id", new ParseUUIDPipe()) id: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    const { roles } = parse(RolesBody, body);
    return this.identity.setRoles(req.admin!, id, roles).catch(mapError);
  }

  @Put("users/:id/status")
  @RequirePermission("identity.users.block")
  async setStatus(@Param("id", new ParseUUIDPipe()) id: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    const { status } = parse(StatusBody, body);
    return this.identity.setStatus(req.admin!, id, status).catch(mapError);
  }
}
