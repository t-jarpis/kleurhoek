import { timingSafeEqual } from "node:crypto";
import { BadRequestException, Body, Controller, Get, HttpCode, Inject, Post, Query, UnauthorizedException, UseGuards, Headers } from "@nestjs/common";
import { z } from "zod";
import { ENV, type Env } from "../../config/env";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { RateLimit } from "../operations/rate-limit.guard";
import { AnalyticsService, EventBatch } from "./analytics.service";

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

const Range = z.object({ from: z.iso.date(), to: z.iso.date(), country: z.string().regex(/^[A-Z]{2}$/).optional() });

@Controller("v1/admin/analytics")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminAnalyticsController {
  constructor(private readonly analytics: AnalyticsService, @Inject(ENV) private readonly env: Env) {}

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

  /** Winkel: doorkliks per product en plaat, en kandidaten om zelf te leveren. */
  @Get("shop")
  @RequirePermission("shop.read")
  async shop(@Query() query: unknown) {
    const q = Range.safeParse(query);
    if (!q.success || q.data.from > q.data.to) throw new BadRequestException("Geef from en to op als YYYY-MM-DD");
    return this.analytics.shopSummary(this.env.TENANT_ID, q.data.from, q.data.to);
  }
}
