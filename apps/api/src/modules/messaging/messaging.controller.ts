import { BadRequestException, Body, Controller, Delete, Get, HttpCode, NotFoundException, Param, Post, Put, Query, Req, ServiceUnavailableException, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { z } from "zod";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { IdentityService } from "../identity/identity.service";
import { MemberGuard } from "../identity/member.guard";
import { CatalogService } from "../catalog/catalog.service";
import { LocalizationService } from "../localization/localization.service";
import { RateLimit } from "../operations/rate-limit.guard";
import { StorefrontService } from "../storefront/storefront.service";
import { CampaignsService } from "./campaigns.service";
import { DeliverabilityService } from "./deliverability/deliverability.service";
import { PROVIDERS, type Provider } from "./deliverability/feedback";
import { TOPICS } from "./messaging.types";
import { OutboxService } from "./outbox.service";
import { maskEmail, SubscribersService } from "./subscribers.service";
import { TemplatesService } from "./templates.service";
import { Audience, CampaignBody, Market, parse, Subscribe, TemplateBody, Topic, WorkflowBody } from "./validation";
import { WorkflowsService } from "./workflows.service";
import { ENV, type Env } from "../../config/env";
import { Inject } from "@nestjs/common";

const Token = z.string().regex(/^[A-Za-z0-9_.-]{20,80}$/);
const SLUG = /^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/;

/**
 * Aanmelden, bevestigen, voorkeuren en afmelden (ADR 0037). Alleen via de website (geen publieke ingang naar de
 * API). Antwoorden verraden niet of een adres al bekend is.
 */
@Controller("v1/mail")
export class MailController {
  constructor(private readonly subs: SubscribersService, private readonly workflows: WorkflowsService, private readonly store: StorefrontService) {}

  @Post("subscribe")
  @RateLimit("contact-submit")
  @HttpCode(202)
  async subscribe(@Body() body: unknown) {
    const f = parse(Subscribe, body);
    // Spam (verborgen veld, te snel): doen alsof het lukte.
    if (f.trap || (f.elapsedMs !== undefined && f.elapsedMs < 2000)) return { ok: true };
    if (!(await this.store.market(f.market))) throw new NotFoundException("Onbekende markt");
    await this.subs.subscribe({ email: f.email, market: f.market, topics: f.topics });
    return { ok: true };
  }

  @Post("confirm")
  @RateLimit("public-read")
  @HttpCode(200)
  async confirm(@Body() body: unknown) {
    const { token } = parse(z.object({ token: Token }).strict(), body);
    const sub = await this.subs.confirm(token);
    if (sub) await this.workflows.onSubscribed(sub.id);
    return { status: sub ? "confirmed" : "invalid" };
  }

  @Get("preferences")
  @RateLimit("public-read")
  async preferences(@Query("t") t: string | undefined) {
    const sub = t && Token.safeParse(t).success ? await this.subs.byToken(t) : null;
    if (!sub) throw new NotFoundException("Deze link werkt niet meer");
    return { email: maskEmail(sub.email), market: sub.market, topics: sub.topics, topicsAll: TOPICS };
  }

  @Put("preferences")
  @RateLimit("public-read")
  async update(@Body() body: unknown) {
    const f = parse(z.object({ t: Token, topics: z.array(Topic).max(3), market: Market.optional() }).strict(), body);
    const sub = await this.subs.byToken(f.t);
    if (!sub) throw new NotFoundException("Deze link werkt niet meer");
    if (f.market && !(await this.store.market(f.market))) throw new NotFoundException("Onbekende markt");
    return { status: await this.subs.update(sub.id, { topics: f.topics, market: f.market }) };
  }

  /** Afmelden (ook de één-klik-afmelding uit de mailheader, RFC 8058, via de website). */
  @Post("unsubscribe")
  @RateLimit("public-read")
  @HttpCode(200)
  async unsubscribe(@Body() body: unknown) {
    const { t } = parse(z.object({ t: Token }).strict(), body);
    const sub = await this.subs.byToken(t);
    if (sub) await this.subs.remove(sub.id);
    return { status: "removed" };
  }
}

/** Mail vanuit het eigen account: meteen actief, want het adres is bij het inloggen al bevestigd. */
@Controller("v1/me/mail")
@UseGuards(MemberGuard)
export class MeMailController {
  constructor(private readonly subs: SubscribersService, private readonly identity: IdentityService, private readonly workflows: WorkflowsService, private readonly store: StorefrontService) {}

  @Get()
  async get(@Req() req: FastifyRequest) {
    const sub = await this.subs.forUser(req.member!.userId);
    return { topics: sub?.topics ?? [], market: sub?.market ?? null, topicsAll: TOPICS };
  }

  @Put()
  async put(@Body() body: unknown, @Req() req: FastifyRequest) {
    const f = parse(z.object({ topics: z.array(Topic).max(3), market: Market }).strict(), body);
    const user = await this.identity.getUser(req.member!.userId);
    if (!user?.email) throw new NotFoundException("Geen e-mailadres bij dit account");
    if (!(await this.store.market(f.market))) throw new NotFoundException("Onbekende markt");
    const { subscriber, started } = await this.subs.setForUser(req.member!.userId, user.email, f.market, f.topics);
    if (subscriber && started) await this.workflows.onSubscribed(subscriber.id);
    return { topics: subscriber?.topics ?? [], market: subscriber?.market ?? null, topicsAll: TOPICS };
  }
}

/**
 * Meldingen van de relay over bezorging (ADR 0038): afgeleverd, bounce, spamklacht, afgemeld. Via de website
 * (/mail/events/<bron>?key=…), met een geheime sleutel per bron in het adres.
 */
@Controller("v1/mail/events")
export class MailEventsController {
  constructor(private readonly delivery: DeliverabilityService) {}

  @Post(":provider")
  @HttpCode(200)
  async receive(@Param("provider") provider: string, @Query("key") key: string | undefined, @Body() body: unknown) {
    if (!(PROVIDERS as readonly string[]).includes(provider) || !this.delivery.keyValid(provider as Provider, key)) throw new NotFoundException();
    // SNS (Scaleway) stuurt JSON als text/plain.
    let data = body;
    if (typeof body === "string") { try { data = JSON.parse(body); } catch { throw new BadRequestException("Geen JSON"); } }
    return this.delivery.ingest(provider as Provider, data);
  }
}

/** Mail in het admin panel (ADR 0037). Adressen alleen met mail.manage, en alleen op exact adres. */
@Controller("v1/admin/mail")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminMailController {
  constructor(
    private readonly subs: SubscribersService, private readonly templates: TemplatesService, private readonly workflows: WorkflowsService,
    private readonly campaigns: CampaignsService, private readonly outbox: OutboxService, private readonly i18n: LocalizationService,
    private readonly catalog: CatalogService, private readonly store: StorefrontService, @Inject(ENV) private readonly env: Env,
    private readonly delivery: DeliverabilityService,
  ) {}

  /** Keuzes voor de editors: onderwerpen, markten, templates, collecties. */
  private async options() {
    const [markets, templates, collections] = await Promise.all([this.i18n.liveMarkets(this.env.TENANT_ID), this.templates.list(), this.catalog.collections(this.env.TENANT_ID)]);
    return {
      topics: TOPICS, markets, languages: [...new Set(markets.map((m) => m.slice(0, 2)))],
      templates: templates.map((t) => ({ slug: t.slug, name: t.name, kind: t.kind })),
      collections: collections.map((c) => ({ slug: c.slug, name: c.names.nl ?? c.slug })),
    };
  }

  @Get()
  @RequirePermission("mail.read")
  async overview() {
    const [subscribers, queue, runs, options] = await Promise.all([this.subs.counts(), this.outbox.queueStats(), this.workflows.runStats(), this.options()]);
    return { sending: this.outbox.sending(), subscribers, queue, runs, options };
  }

  /** Bezorging (ADR 0038): afgeleverd, bounces en klachten per dag, mailprovider en bron; webhookadressen. */
  @Get("deliverability")
  @RequirePermission("mail.read")
  async deliverability(@Query("days") days: string | undefined) {
    const d = [7, 30, 90].includes(Number(days)) ? Number(days) : 30;
    const report = await this.delivery.report(d);
    // Webhookadressen bevatten een geheim: alleen voor wie mail mag beheren.
    return { ...report, sending: this.outbox.sending() };
  }

  @Get("deliverability/webhooks")
  @RequirePermission("mail.manage")
  webhooks() { return { webhooks: this.delivery.webhookUrls() }; }

  @Get("suppressions")
  @RequirePermission("mail.manage")
  async lookupSuppression(@Query("email") email: string | undefined) {
    if (!email || !z.string().email().safeParse(email.trim()).success) throw new BadRequestException("Vul een geldig e-mailadres in");
    return this.delivery.lookup(email.trim().toLowerCase());
  }

  @Post("suppressions")
  @RequirePermission("mail.manage")
  async addSuppression(@Body() body: unknown, @Req() req: FastifyRequest) {
    const { email, detail } = parse(z.object({ email: z.string().trim().toLowerCase().email().max(254), detail: z.string().trim().max(200).optional() }).strict(), body);
    await this.delivery.suppress(email, req.admin!.subject, detail ?? null);
    return this.delivery.lookup(email);
  }

  @Delete("suppressions")
  @RequirePermission("mail.manage")
  async removeSuppression(@Query("email") email: string | undefined) {
    if (!email || !z.string().email().safeParse(email.trim()).success) throw new BadRequestException("Vul een geldig e-mailadres in");
    const was = await this.delivery.unsuppress(email.trim().toLowerCase());
    return { removed: Boolean(was), reason: was };
  }

  @Get("subscribers")
  @RequirePermission("mail.manage")
  async findSubscriber(@Query("email") email: string | undefined) {
    if (!email || !z.string().email().safeParse(email.trim()).success) return { subscriber: null };
    return { subscriber: await this.subs.find(email) };
  }

  @Delete("subscribers/:id")
  @RequirePermission("mail.manage")
  @HttpCode(204)
  async removeSubscriber(@Param("id") id: string) {
    if (!z.uuid().safeParse(id).success || !(await this.subs.remove(id, "removed_by_admin"))) throw new NotFoundException();
  }

  // ---------- Templates ----------

  @Get("templates")
  @RequirePermission("mail.read")
  async listTemplates() {
    const [list, options] = await Promise.all([this.templates.list(), this.options()]);
    return { templates: list, options };
  }

  @Get("templates/:slug")
  @RequirePermission("mail.read")
  async getTemplate(@Param("slug") slug: string) {
    const t = SLUG.test(slug) ? await this.templates.get(slug) : null;
    if (!t) throw new NotFoundException("Onbekende template");
    return { template: t, options: await this.options() };
  }

  @Put("templates/:slug")
  @RequirePermission("mail.manage")
  async saveTemplate(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    return this.templates.save(slug, parse(TemplateBody, body), req.admin!.subject);
  }

  @Delete("templates/:slug")
  @RequirePermission("mail.manage")
  @HttpCode(204)
  async removeTemplate(@Param("slug") slug: string) { await this.templates.remove(slug); }

  /** Voorbeeld van een (nog niet opgeslagen) template in een markt, met voorbeeldplaten en -links. */
  @Post("preview")
  @RequirePermission("mail.read")
  @HttpCode(200)
  async preview(@Body() body: unknown) {
    const f = parse(z.object({ template: TemplateBody, market: Market, holiday: z.string().max(64).optional() }).strict(), body);
    this.templates.validate(f.template);
    const holiday = f.holiday ?? (await this.store.upcomingHolidays(f.market, 60))[0]?.slug;
    const mail = await this.outbox.compose(f.template, { id: "00000000-0000-7000-8000-000000000000", email: "voorbeeld@kleurhoek.nl", market: f.market, topics: ["nieuwe-platen", "feestdagen"] },
      { since: new Date(Date.now() - 14 * 86_400_000).toISOString(), holiday, token: "voorbeeld-token-voorbeeld" }, f.template.kind === "system" && f.template.blocks.some((b) => JSON.stringify(b).includes("{{bevestigen}}")));
    return { subject: mail.subject, html: mail.html, text: mail.text, empty: mail.empty };
  }

  @Post("test")
  @RequirePermission("mail.manage")
  @HttpCode(200)
  async test(@Body() body: unknown) {
    const f = parse(z.object({ template: TemplateBody, market: Market, email: z.string().trim().email().max(254) }).strict(), body);
    try { await this.outbox.sendTest(f.template, f.email, f.market, { since: new Date(Date.now() - 14 * 86_400_000).toISOString() }); }
    catch (e) { throw new ServiceUnavailableException(String(e instanceof Error ? e.message : e)); }
    return { ok: true };
  }

  // ---------- Workflows ----------

  @Get("workflows")
  @RequirePermission("mail.read")
  async listWorkflows() {
    const [list, runs, options] = await Promise.all([this.workflows.list(), this.workflows.runStats(), this.options()]);
    return { workflows: list, runs, options };
  }

  @Put("workflows/:slug")
  @RequirePermission("mail.manage")
  async saveWorkflow(@Param("slug") slug: string, @Body() body: unknown, @Req() req: FastifyRequest) {
    return this.workflows.save(slug, parse(WorkflowBody, body), req.admin!.subject);
  }

  @Delete("workflows/:slug")
  @RequirePermission("mail.manage")
  @HttpCode(204)
  async removeWorkflow(@Param("slug") slug: string) { await this.workflows.remove(slug); }

  // ---------- Campagnes ----------

  @Get("campaigns")
  @RequirePermission("mail.read")
  async listCampaigns() {
    const [list, options] = await Promise.all([this.campaigns.list(), this.options()]);
    return { campaigns: await Promise.all(list.map(async (c) => ({ ...c, deliveries: c.status === "sent" || c.status === "sending" ? await this.campaigns.deliveryStats(c.id) : {} }))), options };
  }

  @Post("campaigns/audience")
  @RequirePermission("mail.read")
  @HttpCode(200)
  async audience(@Body() body: unknown) {
    return { size: await this.campaigns.audienceSize(parse(Audience, body)) };
  }

  @Post("campaigns")
  @RequirePermission("mail.manage")
  async createCampaign(@Body() body: unknown, @Req() req: FastifyRequest) {
    return this.campaigns.create(parse(CampaignBody, body), req.admin!.subject);
  }

  @Put("campaigns/:id")
  @RequirePermission("mail.manage")
  async updateCampaign(@Param("id") id: string, @Body() body: unknown) {
    if (!z.uuid().safeParse(id).success) throw new NotFoundException();
    return this.campaigns.update(id, parse(CampaignBody, body));
  }

  @Post("campaigns/:id/schedule")
  @RequirePermission("mail.manage")
  @HttpCode(200)
  async schedule(@Param("id") id: string, @Body() body: unknown) {
    if (!z.uuid().safeParse(id).success) throw new NotFoundException();
    const { at } = parse(z.object({ at: z.iso.datetime({ offset: true }).nullable() }).strict(), body);
    return this.campaigns.schedule(id, at ? new Date(at) : null);
  }

  @Post("campaigns/:id/cancel")
  @RequirePermission("mail.manage")
  @HttpCode(200)
  async cancel(@Param("id") id: string) {
    if (!z.uuid().safeParse(id).success) throw new NotFoundException();
    return this.campaigns.cancel(id);
  }
}
