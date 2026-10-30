import { BadRequestException, Body, Controller, Get, HttpCode, NotFoundException, Param, Post, Put, Query, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { ApiProblem } from "./adapters";
import { CHANNELS, SocialService } from "./social.service";

const Status = z.enum(["voorstel", "goedgekeurd", "geplaatst", "mislukt", "afgewezen"]);
const Channel = z.enum(["pinterest", "facebook", "instagram", "delen"]);
const Ids = z.object({ ids: z.array(z.string().uuid()).min(1).max(500), approve: z.boolean() }).strict();
const Change = z.object({ title: z.string().trim().min(1).max(100).optional(), body: z.string().trim().min(1).max(2200).optional(), scheduledAt: z.string().datetime({ offset: true }).optional() }).strict();
const Settings = z.object({
  notifyEmail: z.string().email().max(200).nullable(),
  pinsPerDay: z.number().int().min(0).max(10),
  feedDays: z.array(z.number().int().min(1).max(7)).max(7),
  feedTime: z.string().regex(/^([01]\d|2[0-3]):[0-5]\d$/),
}).strict();
const Connect = z.object({ code: z.string().min(1).max(2000), state: z.string().min(10).max(300), redirectUri: z.string().url().max(500) }).strict();
const Kind = z.enum(["pinterest", "meta"]);

const parse = <T>(schema: z.ZodType<T>, v: unknown): T => {
  const r = schema.safeParse(v);
  if (!r.success) throw new BadRequestException(r.error.issues[0]?.message ?? "Ongeldig verzoek");
  return r.data;
};
const map = (e: unknown): never => {
  if (e instanceof ApiProblem) throw e.status === 404 ? new NotFoundException(e.message) : new BadRequestException(e.message);
  throw e;
};

/** Social media in het admin panel (ADR 0063): voorstellen goedkeuren, kanalen koppelen, instellingen. */
@Controller("v1/admin/social")
@UseGuards(AdminGuard)
export class SocialController {
  constructor(private readonly social: SocialService) {}

  @Get()
  @RequirePermission("social.read")
  overview() { return this.social.overview(); }

  @Get("posts")
  @RequirePermission("social.read")
  async posts(@Query("status") status: string | undefined, @Query("channel") channel: string | undefined) {
    return { posts: await this.social.list({ status: status ? parse(z.array(Status), status.split(",")) : undefined, channel: channel ? parse(Channel, channel) : undefined }) };
  }

  @Put("posts/:id")
  @RequirePermission("social.manage")
  @HttpCode(204)
  async update(@Param("id") id: string, @Body() body: unknown) {
    const c = parse(Change, body);
    await this.social.update(parse(z.string().uuid(), id), { title: c.title, body: c.body, scheduledAt: c.scheduledAt ? new Date(c.scheduledAt) : undefined }).catch(map);
  }

  @Post("posts/decide")
  @RequirePermission("social.manage")
  @HttpCode(200)
  async decide(@Body() body: unknown, @Req() req: FastifyRequest) {
    const b = parse(Ids, body);
    return { changed: await this.social.decide(b.ids, b.approve, req.admin!.subject) };
  }

  @Post("posts/:id/shared")
  @RequirePermission("social.manage")
  @HttpCode(204)
  async shared(@Param("id") id: string, @Req() req: FastifyRequest) { await this.social.shared(parse(z.string().uuid(), id), req.admin!.subject).catch(map); }

  @Post("generate")
  @RequirePermission("social.manage")
  @HttpCode(200)
  async generate() { return { made: await this.social.generate() }; }

  @Put("settings")
  @RequirePermission("social.manage")
  saveSettings(@Body() body: unknown) { return this.social.saveSettings(parse(Settings, body)); }

  @Get("connect/:kind")
  @RequirePermission("social.manage")
  connectUrl(@Param("kind") kind: string, @Query("redirectUri") redirectUri: string | undefined) {
    try { return { url: this.social.connectUrl(parse(Kind, kind), parse(z.string().url(), redirectUri)) }; } catch (e) { return map(e); }
  }

  @Post("connect/:kind")
  @RequirePermission("social.manage")
  @HttpCode(200)
  async connect(@Param("kind") kind: string, @Body() body: unknown) {
    const b = parse(Connect, body);
    return this.social.connect(parse(Kind, kind), b.code, b.state, b.redirectUri).catch(map);
  }

  @Put("channels/:kind")
  @RequirePermission("social.manage")
  @HttpCode(204)
  async channel(@Param("kind") kind: string, @Body() body: unknown) {
    const k = parse(z.enum(CHANNELS), kind);
    const b = parse(z.object({ enabled: z.boolean().optional(), connected: z.literal(false).optional() }).strict(), body);
    if (b.connected === false) await this.social.disconnect(k);
    if (b.enabled !== undefined) await this.social.setEnabled(k, b.enabled);
  }
}
