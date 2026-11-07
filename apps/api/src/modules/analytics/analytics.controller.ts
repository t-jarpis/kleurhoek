import { timingSafeEqual } from "node:crypto";
import { BadRequestException, Body, Controller, Get, HttpCode, Inject, Post, Put, Query, Req, UnauthorizedException, UseGuards, Headers } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { ENV, type Env } from "../../config/env";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "../operations/rate-limit.guard";
import { AnalyticsService, EventBatch } from "./analytics.service";
import { GoalsInput, GoalsService } from "./goals.service";
import { SearchService } from "./search.service";
import { WishesService, WishInput, WishStatusInput } from "./wishes.service";

function sameSecret(a: string | undefined, b: string): boolean {
  if (!a) return false;
  const x = Buffer.from(a), y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

/** Alleen voor de Cloudflare Worker: die heeft het IP-adres al verwijderd en het land toegevoegd. */
@Controller("v1/internal/events")
export class EventIngestController {
  constructor(private readonly analytics: AnalyticsService, @Inject(ENV) private readonly env: Env) {}

  @Post()
  @HttpCode(202)
  @RateLimit("events-ingest")
  async ingest(@Headers("x-ingest-key") key: string | undefined, @Body() body: unknown) {
    if (!sameSecret(key, this.env.INGEST_KEY)) throw new UnauthorizedException();
    const parsed = EventBatch.safeParse(body);
    if (!parsed.success) throw new BadRequestException("Ongeldige events");
    return { accepted: await this.analytics.record(this.env.TENANT_ID, parsed.data) };
  }
}

/** Zoekwoorden zonder resultaat en aanvragen van platen (ADR 0084), via de website (zelfde sleutel als events). */
@Controller("v1/internal/wishes")
export class WishIngestController {
  constructor(private readonly wishes: WishesService, @Inject(ENV) private readonly env: Env) {}

  @Post()
  @HttpCode(202)
  @RateLimit("events-ingest")
  async ingest(@Headers("x-ingest-key") key: string | undefined, @Body() body: unknown) {
    if (!sameSecret(key, this.env.INGEST_KEY)) throw new UnauthorizedException();
    const parsed = WishInput.safeParse(body);
    if (!parsed.success) throw new BadRequestException("Ongeldig zoekwoord");
    return { stored: await this.wishes.record(this.env.TENANT_ID, parsed.data) };
  }
}

const Range = z.object({ from: z.iso.date(), to: z.iso.date(), country: z.string().regex(/^[A-Z]{2}$/).optional() });

@Controller("v1/admin/analytics")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminAnalyticsController {
  constructor(private readonly analytics: AnalyticsService, private readonly goals: GoalsService, private readonly search: SearchService, private readonly wishes: WishesService, @Inject(ENV) private readonly env: Env) {}

  @Get("summary")
  @RequirePermission("analytics.read")
  async summary(@Query() query: unknown) {
    const q = Range.safeParse(query);
    if (!q.success) throw new BadRequestException("Geef from en to op als YYYY-MM-DD");
    return this.analytics.summary(this.env.TENANT_ID, q.data.from, q.data.to, q.data.country);
  }

  /** Dashboard: reeksen over de tijd, vergelijking met de vorige periode en verdelingen (ADR 0020). */
  @Get("overview")
  @RequirePermission("analytics.read")
  async overview(@Query() query: unknown) {
    const q = Range.safeParse(query);
    if (!q.success || q.data.from > q.data.to) throw new BadRequestException("Geef from en to op als YYYY-MM-DD");
    if (Date.parse(q.data.to) - Date.parse(q.data.from) > 400 * 86_400_000) throw new BadRequestException("Hooguit 400 dagen");
    return this.analytics.overview(this.env.TENANT_ID, q.data.from, q.data.to);
  }

  /** Wanneer er gedownload en geprint wordt, per weekdag en uur, en de laatste met tijdstip (ADR 0073). */
  @Get("activity")
  @RequirePermission("analytics.read")
  async activity(@Query() query: unknown) {
    const q = Range.safeParse(query);
    if (!q.success || q.data.from > q.data.to) throw new BadRequestException("Geef from en to op als YYYY-MM-DD");
    return this.analytics.activity(this.env.TENANT_ID, q.data.from, q.data.to);
  }

  /** Nu op de site: laatste 30 minuten (ADR 0034). */
  @Get("realtime")
  @RequirePermission("analytics.read")
  realtime() {
    return this.analytics.realtime(this.env.TENANT_ID);
  }

  /** Winkel: doorkliks per product en plaat, en kandidaten om zelf te leveren. */
  @Get("shop")
  @RequirePermission("shop.read")
  async shop(@Query() query: unknown) {
    const q = Range.safeParse(query);
    if (!q.success || q.data.from > q.data.to) throw new BadRequestException("Geef from en to op als YYYY-MM-DD");
    return this.analytics.shopSummary(this.env.TENANT_ID, q.data.from, q.data.to);
  }

  /** Zoekcijfers van Google en Bing naast de eigen tellingen via zoekmachines (ADR 0041). */
  @Get("search")
  @RequirePermission("seo.read")
  async searchReport(@Query() query: unknown) {
    const q = Range.safeParse(query);
    if (!q.success || q.data.from > q.data.to) throw new BadRequestException("Geef from en to op als YYYY-MM-DD");
    if (Date.parse(q.data.to) - Date.parse(q.data.from) > 500 * 86_400_000) throw new BadRequestException("Hooguit 500 dagen");
    return this.search.report(q.data.from, q.data.to);
  }

  /** Zoekcijfers nu ophalen in plaats van bij de volgende ronde. */
  @Post("search/refresh")
  @HttpCode(202)
  @RequirePermission("seo.manage")
  refreshSearch() {
    if (!this.search.engines().length || !this.env.SEARCH_DOMAINS.length) throw new BadRequestException("Zoekcijfers zijn nog niet ingesteld");
    void this.search.run();
    return { started: true };
  }

  /** Gezocht (ADR 0084): wat bezoekers niet vonden en welke platen ze aanvroegen. */
  @Get("wishes")
  @RequirePermission("analytics.read")
  listWishes(@Query("hidden") hidden?: string) {
    return this.wishes.list(this.env.TENANT_ID, { hidden: hidden === "1" });
  }

  @Put("wishes/status")
  @RequirePermission("analytics.wishes.manage")
  async setWishStatus(@Body() body: unknown, @Req() req: FastifyRequest) {
    const parsed = WishStatusInput.safeParse(body);
    if (!parsed.success) throw new BadRequestException("Geef term en status (open, made of hidden) op");
    await this.wishes.setStatus(this.env.TENANT_ID, req.admin!.subject, parsed.data.term, parsed.data.status);
    return this.wishes.list(this.env.TENANT_ID);
  }

  /** Doelen per maand met de werkelijke cijfers ernaast (ADR 0022). */
  @Get("goals")
  @RequirePermission("analytics.read")
  async getGoals() {
    return this.goals.get(this.env.TENANT_ID);
  }

  @Put("goals")
  @RequirePermission("analytics.goals.manage")
  async saveGoals(@Body() body: unknown, @Req() req: FastifyRequest) {
    const parsed = GoalsInput.safeParse(body);
    if (!parsed.success) throw new BadRequestException(parsed.error.issues.map((i) => i.message).join("; "));
    await this.goals.save(this.env.TENANT_ID, req.admin!.subject, parsed.data);
    return this.goals.get(this.env.TENANT_ID);
  }
}
