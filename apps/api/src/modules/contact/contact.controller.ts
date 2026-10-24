import { BadRequestException, Body, Controller, Delete, ForbiddenException, Get, HttpCode, NotFoundException, Param, Post, Put, Query, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "../operations/rate-limit.guard";
import { CHANNELS, REQUEST_ORG_KINDS, STATUSES, TOPICS } from "./contact.schema";
import { ContactError, ContactService } from "./contact.service";

/** Webformulier. `trap` is een verborgen veld (moet leeg blijven), `elapsedMs` hoe lang het formulier open stond. */
export const ContactForm = z.object({
  topic: z.enum(TOPICS),
  name: z.string().trim().max(80).optional().transform((v) => v || null),
  email: z.email().trim().toLowerCase().max(200),
  message: z.string().trim().min(10, "Schrijf minstens een paar woorden").max(4000),
  org: z.string().regex(/^[a-z0-9-]{1,32}$/),
  market: z.string().regex(/^[a-z]{2}-[A-Za-z]{2}$/).transform((m) => `${m.slice(0, 2)}-${m.slice(3).toUpperCase()}`),
  trap: z.string().max(200).optional(),
  elapsedMs: z.number().int().min(0).optional(),
  /** Alleen bij onderwerp "organization": de aanvraag voor een eigen omgeving (ADR 0028). */
  details: z.object({
    organization: z.string().trim().min(2, "Naam van de organisatie").max(120),
    kind: z.enum(REQUEST_ORG_KINDS),
    code: z.string().trim().toLowerCase().regex(/^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/, "Adres: kleine letters, cijfers en streepjes").optional().transform((v) => v || null),
    children: z.string().trim().max(40).optional().transform((v) => v || null),
    website: z.string().trim().max(200).optional().transform((v) => v || null),
  }).strict().optional(),
}).strict().refine((f) => (f.topic === "organization") === Boolean(f.details), { message: "Gegevens van de organisatie horen bij een aanvraag voor een eigen omgeving", path: ["details"] });

/** Zichtbaar spam: verborgen veld ingevuld, te snel verstuurd of vol links. We doen alsof het lukte. */
export function looksLikeSpam(f: { trap?: string | undefined; elapsedMs?: number | undefined; message: string }): boolean {
  if (f.trap) return true;
  if (f.elapsedMs !== undefined && f.elapsedMs < 3000) return true;
  return (f.message.match(/https?:\/\//gi) ?? []).length > 3;
}

function parse<T>(schema: z.ZodType<T>, value: unknown): T {
  const r = schema.safeParse(value);
  if (!r.success) throw new BadRequestException(r.error.issues.map((i) => `${i.path.join(".") || "body"}: ${i.message}`).join("; "));
  return r.data;
}
function mapError(e: unknown): never {
  if (e instanceof ContactError) {
    if (e.code === "not_found") throw new NotFoundException(e.message);
    if (e.code === "closed") throw new ForbiddenException(e.message);
    throw new BadRequestException(e.message);
  }
  throw e;
}
const Id = z.uuid();

/** Alleen via de website (die stuurt het IP van de bezoeker mee voor de rate limit). */
@Controller("v1/contact")
export class ContactController {
  constructor(private readonly contact: ContactService) {}

  @Post()
  @HttpCode(202)
  @RateLimit("contact-submit")
  async submit(@Body() body: unknown) {
    const f = parse(ContactForm, body);
    if (looksLikeSpam(f)) return { ok: true };
    await this.contact.submit("web", { topic: f.topic, name: f.name, email: f.email, message: f.message, org: f.org, market: f.market, details: f.details ?? null }).catch(mapError);
    return { ok: true };
  }
}

const InboxQuery = z.object({ status: z.enum(STATUSES).optional(), page: z.coerce.number().int().min(1).max(1000).optional() }).strict();
const StatusBody = z.object({ status: z.enum(STATUSES) }).strict();
const MessageBody = z.object({ direction: z.enum(["out", "note"]), body: z.string().trim().min(1).max(8000) }).strict();
const ChannelBody = z.object({ enabled: z.boolean().optional(), settings: z.record(z.string().regex(/^[a-zA-Z]{1,32}$/), z.string().max(120)).optional() }).strict();

@Controller("v1/admin/contact")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminContactController {
  constructor(private readonly contact: ContactService) {}

  @Get("conversations")
  @RequirePermission("contact.read")
  async inbox(@Query() query: unknown) { return this.contact.inbox(parse(InboxQuery, query)); }

  @Get("unread")
  @RequirePermission("contact.read")
  async unread() { return { count: await this.contact.unreadCount() }; }

  @Get("conversations/:id")
  @RequirePermission("contact.read")
  async conversation(@Param("id") id: string) {
    if (!Id.safeParse(id).success) throw new NotFoundException();
    return this.contact.conversation(id).catch(mapError);
  }

  @Put("conversations/:id/status")
  @RequirePermission("contact.manage")
  async status(@Param("id") id: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    if (!Id.safeParse(id).success) throw new NotFoundException();
    return this.contact.setStatus(req.admin!.subject, id, parse(StatusBody, body).status).catch(mapError);
  }

  @Post("conversations/:id/messages")
  @RequirePermission("contact.manage")
  async message(@Param("id") id: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    if (!Id.safeParse(id).success) throw new NotFoundException();
    const b = parse(MessageBody, body);
    return this.contact.addMessage(req.admin!.subject, id, b.direction, b.body).catch(mapError);
  }

  @Delete("conversations/:id")
  @HttpCode(204)
  @RequirePermission("contact.manage")
  async remove(@Param("id") id: string, @Req() req: FastifyRequest) {
    if (!Id.safeParse(id).success) throw new NotFoundException();
    await this.contact.remove(req.admin!.subject, id).catch(mapError);
  }

  @Get("channels")
  @RequirePermission("contact.read")
  async channels() { return { channels: await this.contact.channelList() }; }

  @Put("channels/:slug")
  @RequirePermission("contact.manage")
  async updateChannel(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    const s = z.enum(CHANNELS).safeParse(slug);
    if (!s.success) throw new NotFoundException();
    return { channels: await this.contact.updateChannel(req.admin!.subject, s.data, parse(ChannelBody, body)).catch(mapError) };
  }
}
