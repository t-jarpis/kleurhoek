import { timingSafeEqual } from "node:crypto";
import { BadRequestException, Body, Controller, Get, Headers, Inject, Put, Req, UnauthorizedException, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { ENV, type Env } from "../../config/env";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "./rate-limit.guard";
import { MAX_ENTRIES, normalizeCidr, SiteAccessService } from "./site-access.service";

const Entry = z.object({
  cidr: z.string().max(64).refine((v) => normalizeCidr(v) !== null, "Ongeldig IP-adres of CIDR-blok (minimaal /8 voor IPv4, /32 voor IPv6)"),
  label: z.string().trim().min(1, "Geef een omschrijving").max(80),
});
const UpdateBody = z.object({
  enabled: z.boolean().optional(),
  entries: z.array(Entry).max(MAX_ENTRIES).optional(),
}).strict().refine((b) => Object.keys(b).length > 0, "Geef minstens één veld op");

@Controller("v1/admin/site-access")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminSiteAccessController {
  constructor(private readonly access: SiteAccessService) {}

  @Get()
  @RequirePermission("operations.access.read")
  get() { return this.access.get(); }

  @Put()
  @RequirePermission("operations.access.manage")
  async update(@Body() body: unknown, @Req() req: FastifyRequest) {
    const parsed = UpdateBody.safeParse(body);
    if (!parsed.success) throw new BadRequestException(parsed.error.issues.map((i) => i.message).join("; "));
    const { enabled, entries } = parsed.data;
    const next = entries ?? (await this.access.get()).entries;
    if ((enabled ?? (await this.access.get()).enabled) && next.length === 0) {
      throw new BadRequestException("Voeg eerst minstens één IP-adres toe; anders kan niemand de website meer zien");
    }
    return this.access.update({ enabled, entries }, req.admin!.subject);
  }
}

function sameSecret(a: string | undefined, b: string): boolean {
  if (!a) return false;
  const x = Buffer.from(a), y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

/** Voor de website (proxy): alleen de stand en de CIDR-blokken, geen namen. */
@Controller("v1/internal/site-access")
export class InternalSiteAccessController {
  constructor(private readonly access: SiteAccessService, @Inject(ENV) private readonly env: Env) {}

  @Get()
  @RateLimit("events-ingest")
  async get(@Headers("x-ingest-key") key: string | undefined) {
    if (!sameSecret(key, this.env.INGEST_KEY)) throw new UnauthorizedException();
    const s = await this.access.get();
    return { enabled: s.enabled, cidrs: s.entries.map((e) => e.cidr) };
  }
}
