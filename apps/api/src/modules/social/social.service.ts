import { Inject, Injectable, Logger } from "@nestjs/common";
import { and, asc, desc, eq, gte, inArray, lte, lt, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { MAIL_TRANSPORT, type MailTransport } from "../messaging/mailer";
import { StorefrontService } from "../storefront/storefront.service";
import { ApiProblem, Meta, Pinterest, type Fetch, type Tokens } from "./adapters";
import { checkState, open, seal, signState } from "./crypto";
import { socialChannels as channels, socialPosts as posts, socialSettings as settings } from "./social.schema";
import { boardOf, feedText, HERFST, pinText, WINTER, type FeedKind, type PlateInfo } from "./texts";

export const CHANNELS = ["pinterest", "facebook", "instagram"] as const;
export type ChannelKind = (typeof CHANNELS)[number];
export type PostChannel = ChannelKind | "delen";
export type PostStatus = "voorstel" | "goedgekeurd" | "geplaatst" | "mislukt" | "afgewezen";
export const TZ = "Europe/Amsterdam";
const MARKET = "nl-nl";
const IMAGE_REV = "2";
const MAX_ATTEMPTS = 3;

export interface SocialSettings {
  /** Wie elke ochtend de voorstellen in de mail krijgt. */
  notifyEmail: string | null;
  /** Nieuwe pins per dag. */
  pinsPerDay: number;
  /** Dagen met een post op Facebook, Instagram en om te delen (1 = maandag … 7 = zondag). */
  feedDays: number[];
  /** Hoe laat de post komt (lokale tijd). */
  feedTime: string;
}
export const DEFAULT_SETTINGS: SocialSettings = { notifyEmail: null, pinsPerDay: 5, feedDays: [1, 3, 5], feedTime: "19:30" };
const PIN_TIMES = ["08:30", "12:00", "15:30", "19:00", "20:30", "10:15", "13:45", "17:15", "21:30", "07:30"];

// ---------- Tijd in Nederland ----------

/** Datum (JJJJ-MM-DD) in Nederland. */
export const localDay = (d: Date) => new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" }).format(d);
const localHour = (d: Date) => Number(new Intl.DateTimeFormat("en-GB", { timeZone: TZ, hour: "2-digit", hourCycle: "h23" }).format(d));
/** Het moment waarop het in Nederland `day` om `time` is. */
export function atLocal(day: string, time: string): Date {
  const [y, m, d] = day.split("-").map(Number) as [number, number, number];
  const [h, mi] = time.split(":").map(Number) as [number, number];
  const wanted = Date.UTC(y, m - 1, d, h, mi);
  let t = wanted;
  for (let i = 0; i < 2; i++) {
    const parts = Object.fromEntries(new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date(t)).map((p) => [p.type, p.value]));
    const shown = Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day), Number(parts.hour), Number(parts.minute));
    t += wanted - shown;
  }
  return new Date(t);
}
const addDays = (day: string, n: number) => new Date(Date.parse(`${day}T12:00:00Z`) + n * 86_400_000).toISOString().slice(0, 10);
const weekday = (day: string) => ((new Date(`${day}T12:00:00Z`).getUTCDay() + 6) % 7) + 1;

/**
 * Social (ADR 0063): maakt elke dag voorstellen voor Pinterest, Facebook, Instagram en om zelf te delen, mailt Thijs
 * de voorstellen, en plaatst wat hij goedkeurt op het geplande moment. Een eigen domein met een eigen schema; platen
 * komen van de Etalage (StorefrontService), mail via de wachtrij van Berichten (MAIL_TRANSPORT).
 */
@Injectable()
export class SocialService {
  private readonly log = new Logger(SocialService.name);
  fetch: Fetch = (url, init) => fetch(url, init);

  constructor(
    @Inject(DB) private readonly db: Database,
    @Inject(ENV) private readonly env: Env,
    @Inject(MAIL_TRANSPORT) private readonly mail: MailTransport,
    private readonly store: StorefrontService,
  ) {}
  private get tenant() { return this.env.TENANT_ID; }
  private tx<T>(fn: Parameters<typeof withTenant<T>>[2]) { return withTenant(this.db, this.tenant, fn); }

  private pinterest() { return this.env.PINTEREST_APP_ID && this.env.PINTEREST_APP_SECRET ? new Pinterest(this.fetch, this.env.PINTEREST_APP_ID, this.env.PINTEREST_APP_SECRET) : null; }
  private meta() { return this.env.META_APP_ID && this.env.META_APP_SECRET ? new Meta(this.fetch, this.env.META_APP_ID, this.env.META_APP_SECRET) : null; }
  private available(kind: ChannelKind) { return kind === "pinterest" ? !!this.pinterest() : !!this.meta(); }

  // ---------- Instellingen ----------

  async settings(): Promise<SocialSettings & { generatedOn: string | null; digestSentOn: string | null }> {
    const [row] = await this.tx((tx) => tx.select().from(settings).where(eq(settings.tenantId, this.tenant)));
    return { ...DEFAULT_SETTINGS, ...(row?.value as Partial<SocialSettings> | undefined), generatedOn: row?.generatedOn ?? null, digestSentOn: row?.digestSentOn ?? null };
  }

  private async setSettings(patch: Partial<{ value: Record<string, unknown>; generatedOn: string; digestSentOn: string }>) {
    await this.tx((tx) => tx.insert(settings).values({ tenantId: this.tenant, value: patch.value ?? {}, ...patch }).onConflictDoUpdate({ target: settings.tenantId, set: { ...patch, updatedAt: new Date() } }));
  }

  async saveSettings(s: SocialSettings) {
    const { generatedOn: _g, digestSentOn: _d, ...current } = await this.settings();
    await this.setSettings({ value: { ...current, ...s } });
    return this.settings();
  }

  // ---------- Kanalen koppelen ----------

  async overview() {
    const rows = await this.tx((tx) => tx.select().from(channels).where(eq(channels.tenantId, this.tenant)));
    const counts = await this.tx((tx) => tx.select({ status: posts.status, channel: posts.channel, n: sql<number>`count(*)::int` }).from(posts).where(eq(posts.tenantId, this.tenant)).groupBy(posts.status, posts.channel));
    return {
      channels: CHANNELS.map((kind) => {
        const r = rows.find((c) => c.kind === kind);
        return { kind, available: this.available(kind), connected: !!r?.token, account: r?.account ?? null, enabled: r ? r.enabled === 1 : true, connectedAt: r?.connectedAt?.toISOString() ?? null, error: r?.error ?? null };
      }),
      counts,
      settings: await this.settings(),
      redirectBase: `${this.env.ADMIN_URL.replace(/\/$/, "")}/social/koppel`,
    };
  }

  private checkRedirect(redirectUri: string) {
    if (!redirectUri.startsWith(`${this.env.ADMIN_URL.replace(/\/$/, "")}/social/koppel/`)) throw new ApiProblem("Onbekend terugkeeradres", 400);
  }

  connectUrl(kind: "pinterest" | "meta", redirectUri: string) {
    this.checkRedirect(redirectUri);
    const state = signState(this.env.SOCIAL_SECRET, kind);
    const api = kind === "pinterest" ? this.pinterest() : this.meta();
    if (!api) throw new ApiProblem(`${kind === "pinterest" ? "Pinterest" : "Meta"} is nog niet ingesteld: de app-sleutels ontbreken`, 400);
    return api.authorizeUrl(redirectUri, state);
  }

  private async saveChannel(kind: ChannelKind, v: { account: string; externalId: string; tokens: Tokens }) {
    const token = seal(this.env.SOCIAL_SECRET, v.tokens);
    const now = new Date();
    await this.tx((tx) => tx.insert(channels).values({ tenantId: this.tenant, kind, account: v.account, externalId: v.externalId, token, connectedAt: now, error: null })
      .onConflictDoUpdate({ target: [channels.tenantId, channels.kind], set: { account: v.account, externalId: v.externalId, token, connectedAt: now, error: null, updatedAt: now } }));
  }

  async connect(kind: "pinterest" | "meta", code: string, state: string, redirectUri: string) {
    this.checkRedirect(redirectUri);
    if (!checkState(this.env.SOCIAL_SECRET, kind, state)) throw new ApiProblem("Koppelen verlopen of ongeldig; probeer het opnieuw", 400);
    if (kind === "pinterest") {
      const api = this.pinterest();
      if (!api) throw new ApiProblem("Pinterest is nog niet ingesteld", 400);
      const tokens = await api.exchange(code, redirectUri);
      const account = await api.account(tokens);
      await this.saveChannel("pinterest", { account, externalId: account, tokens });
      return { connected: ["pinterest"] };
    }
    const api = this.meta();
    if (!api) throw new ApiProblem("Meta is nog niet ingesteld", 400);
    const pages = await api.pages(code, redirectUri);
    if (!pages.length) throw new ApiProblem("Geen Facebook-pagina gevonden. Maak eerst een pagina voor Kleurhoek en geef de app toegang tot die pagina.", 400);
    const page = pages.find((p) => /kleurhoek/i.test(p.name)) ?? pages[0]!;
    await this.saveChannel("facebook", { account: page.name, externalId: page.id, tokens: { access: page.token } });
    const connected: ChannelKind[] = ["facebook"];
    if (page.instagram) {
      await this.saveChannel("instagram", { account: `@${page.instagram.username}`, externalId: page.instagram.id, tokens: { access: page.token } });
      connected.push("instagram");
    }
    return { connected, page: page.name, instagram: page.instagram?.username ?? null };
  }

  async disconnect(kind: ChannelKind) {
    await this.tx((tx) => tx.update(channels).set({ token: null, account: null, externalId: null, connectedAt: null, updatedAt: new Date() }).where(and(eq(channels.tenantId, this.tenant), eq(channels.kind, kind))));
  }

  async setEnabled(kind: ChannelKind, enabled: boolean) {
    await this.tx((tx) => tx.insert(channels).values({ tenantId: this.tenant, kind, enabled: enabled ? 1 : 0 })
      .onConflictDoUpdate({ target: [channels.tenantId, channels.kind], set: { enabled: enabled ? 1 : 0, updatedAt: new Date() } }));
  }

  private async channel(kind: ChannelKind) {
    const [r] = await this.tx((tx) => tx.select().from(channels).where(and(eq(channels.tenantId, this.tenant), eq(channels.kind, kind))));
    if (!r?.token || r.enabled !== 1) return null;
    const tokens = open<Tokens>(this.env.SOCIAL_SECRET, r.token);
    return tokens ? { ...r, tokens } : null;
  }

  // ---------- Posts ----------

  async list(filter: { status?: PostStatus[] | undefined; channel?: PostChannel | undefined; limit?: number | undefined }) {
    const rows = await this.tx((tx) => tx.select().from(posts).where(and(
      eq(posts.tenantId, this.tenant),
      filter.status?.length ? inArray(posts.status, filter.status) : undefined,
      filter.channel ? eq(posts.channel, filter.channel) : undefined,
    )).orderBy(filter.status?.includes("geplaatst") ? desc(posts.publishedAt) : asc(posts.scheduledAt), asc(posts.channel)).limit(filter.limit ?? 200));
    return rows.map((p) => ({
      id: p.id, channel: p.channel as PostChannel, status: p.status as PostStatus, source: p.source, plateSlug: p.plateSlug, title: p.title, body: p.body,
      link: p.link, image: p.image, board: p.board, scheduledAt: p.scheduledAt.toISOString(), publishedAt: p.publishedAt?.toISOString() ?? null,
      externalUrl: p.externalUrl, error: p.error, attempts: p.attempts, decidedBy: p.decidedBy,
    }));
  }

  async update(id: string, patch: { title?: string | undefined; body?: string | undefined; scheduledAt?: Date | undefined }) {
    const res = await this.tx((tx) => tx.update(posts).set({ ...patch, updatedAt: new Date() })
      .where(and(eq(posts.tenantId, this.tenant), eq(posts.id, id), inArray(posts.status, ["voorstel", "goedgekeurd", "mislukt"]))).returning({ id: posts.id }));
    if (!res.length) throw new ApiProblem("Post niet gevonden of al geplaatst", 404);
  }

  /** Goedkeuren of afwijzen. Een mislukte post opnieuw goedkeuren probeert hem opnieuw. */
  async decide(ids: string[], approve: boolean, actor: string) {
    if (!ids.length) return 0;
    const res = await this.tx((tx) => tx.update(posts).set({ status: approve ? "goedgekeurd" : "afgewezen", decidedAt: new Date(), decidedBy: actor, attempts: 0, error: null, updatedAt: new Date() })
      .where(and(eq(posts.tenantId, this.tenant), inArray(posts.id, ids), inArray(posts.status, ["voorstel", "goedgekeurd", "mislukt"]))).returning({ id: posts.id }));
    return res.length;
  }

  /** Een tekst om te delen is gedeeld (dat doet Thijs zelf). */
  async shared(id: string, actor: string) {
    const res = await this.tx((tx) => tx.update(posts).set({ status: "geplaatst", publishedAt: new Date(), decidedBy: actor, updatedAt: new Date() })
      .where(and(eq(posts.tenantId, this.tenant), eq(posts.id, id), eq(posts.channel, "delen"))).returning({ id: posts.id }));
    if (!res.length) throw new ApiProblem("Post niet gevonden", 404);
  }

  // ---------- Voorstellen maken ----------

  private async plates() {
    const market = await this.store.market(MARKET);
    if (!market) return { list: [] as PlateInfo[], market: null };
    const [items, tax] = await Promise.all([this.store.listPlates(market, {}), this.store.taxonomy(market)]);
    const cat = new Map(tax.categories.map((c) => [c.slug, c.name ?? c.slug]));
    const age = new Map(tax.ages.map((a) => [a.slug, a.name ?? a.slug]));
    return {
      market,
      list: items.map((p): PlateInfo => ({ slug: p.slug, name: p.name ?? p.slug, category: p.category, categoryName: cat.get(p.category) || p.category, age: p.age, ageName: age.get(p.age) || p.age, holiday: p.holiday, kind: p.kind })),
    };
  }

  private url(path: string) { return `${this.env.SITE_URL.replace(/\/$/, "")}${path}`; }
  private image(slug: string, format: "png" | "jpg") { return this.url(`/v1/pins/${MARKET}/${slug}.${format}?r=${IMAGE_REV}`); }

  private async insert(rows: (typeof posts.$inferInsert)[]) {
    if (!rows.length) return 0;
    const res = await this.tx((tx) => tx.insert(posts).values(rows).onConflictDoNothing().returning({ id: posts.id }));
    return res.length;
  }

  /** Voorstellen voor vandaag en de twee dagen erna. Dubbele voorstellen worden overgeslagen, dus herhalen kan. */
  async generate(now = new Date()) {
    const s = await this.settings();
    const { list, market } = await this.plates();
    if (!market || !list.length) return 0;
    const pinterest = await this.channel("pinterest");
    const facebook = await this.channel("facebook");
    const instagram = await this.channel("instagram");
    const today = localDay(now);
    const days = [0, 1, 2].map((n) => addDays(today, n));
    const season = await this.store.season(market, undefined, now);
    const soon = [...season.active.filter((a) => a.kind === "holiday"), ...season.soon] as { slug: string; name: string; date?: string }[];
    let made = 0;

    // Pinterest: elke dag een paar platen die er nog niet op staan; feestdagen die eraan komen en het seizoen eerst.
    if (pinterest && s.pinsPerDay > 0) {
      const done = new Set((await this.tx((tx) => tx.select({ slug: posts.plateSlug }).from(posts).where(and(eq(posts.tenantId, this.tenant), eq(posts.channel, "pinterest"))))).map((r) => r.slug));
      const month = Number(today.slice(5, 7));
      const seasonal = (p: PlateInfo) => (month >= 9 && month <= 11 && HERFST.has(p.slug)) || ((month === 12 || month <= 2) && WINTER.has(p.slug));
      const upcoming = new Set(soon.map((h) => h.slug));
      const order = list.filter((p) => !done.has(p.slug)).map((p, i) => ({ p, rank: (p.holiday && upcoming.has(p.holiday) ? 0 : seasonal(p) ? 1 : p.holiday ? 3 : 2) * 10_000 + i }))
        .sort((a, b) => a.rank - b.rank).map((x) => x.p);
      const existing = await this.tx((tx) => tx.select({ at: posts.scheduledAt }).from(posts).where(and(eq(posts.tenantId, this.tenant), eq(posts.channel, "pinterest"), gte(posts.scheduledAt, atLocal(days[0]!, "00:00")))));
      let k = 0;
      for (const day of days) {
        const taken = existing.filter((e) => localDay(e.at) === day).length;
        const times = PIN_TIMES.slice(0, Math.min(s.pinsPerDay, PIN_TIMES.length)).sort().slice(taken);
        for (const time of times) {
          const p = order[k++];
          if (!p) break;
          const at = atLocal(day, time);
          if (at < now) continue;
          const t = pinText(p);
          made += await this.insert([{ tenantId: this.tenant, channel: "pinterest", key: `pin:${MARKET}:${p.slug}`, source: "plaat", market: MARKET, plateSlug: p.slug, title: t.title, body: t.description, link: this.url(`/platen/${p.slug}`), image: this.image(p.slug, "png"), board: boardOf(p), scheduledAt: at }]);
        }
      }
    }

    // Facebook, Instagram en delen: op de gekozen dagen één post, dezelfde inhoud in drie vormen.
    const recent = new Set((await this.tx((tx) => tx.select({ slug: posts.plateSlug }).from(posts).where(and(eq(posts.tenantId, this.tenant), inArray(posts.channel, ["facebook", "instagram", "delen"]), gte(posts.scheduledAt, new Date(now.getTime() - 60 * 86_400_000)))))).map((r) => r.slug).filter((x): x is string => !!x));
    for (const day of days) {
      if (!s.feedDays.includes(weekday(day))) continue;
      const at = atLocal(day, s.feedTime);
      if (at < now) continue;
      const choice = this.feedChoice(day, list, soon, recent);
      if (!choice) continue;
      recent.add(choice.plate.slug);
      const t = feedText(choice.kind, { day, link: this.url(choice.path), plate: choice.plate, holidayName: choice.holidayName, days: choice.days, door: choice.door });
      const base = { tenantId: this.tenant, key: `feed:${day}`, source: choice.kind, market: MARKET, plateSlug: choice.plate.slug, title: t.title, link: this.url(choice.path), image: this.image(choice.plate.slug, "jpg"), scheduledAt: at };
      made += await this.insert([
        ...(facebook ? [{ ...base, channel: "facebook", body: t.facebook }] : []),
        ...(instagram ? [{ ...base, channel: "instagram", body: t.instagram }] : []),
        { ...base, channel: "delen", body: t.share },
      ]);
    }
    await this.setSettings({ generatedOn: today });
    return made;
  }

  private feedChoice(day: string, list: PlateInfo[], soon: { slug: string; name: string; date?: string }[], recent: Set<string>): { kind: FeedKind; plate: PlateInfo; path: string; holidayName?: string; days?: number; door?: number } | null {
    const fresh = (pred: (p: PlateInfo) => boolean) => list.find((p) => pred(p) && !recent.has(p.slug)) ?? list.find(pred);
    const [, m, d] = day.split("-").map(Number) as [number, number, number];
    if (m === 12 && d <= 24) {
      const plate = fresh((p) => p.holiday === "kerst" || WINTER.has(p.slug));
      if (plate) return { kind: "aftelkalender", plate, path: "/aftelkalender", door: d };
    }
    const until = (date?: string) => (date ? Math.round((Date.parse(`${date}T12:00:00Z`) - Date.parse(`${day}T12:00:00Z`)) / 86_400_000) : -1);
    const holiday = soon.map((h) => ({ ...h, days: until(h.date) })).filter((h) => h.days >= 1 && h.days <= 14).sort((a, b) => a.days - b.days)
      .find((h) => list.some((p) => p.holiday === h.slug));
    if (holiday) {
      const plate = fresh((p) => p.holiday === holiday.slug && p.kind === "kleurplaat") ?? fresh((p) => p.holiday === holiday.slug)!;
      return { kind: "feestdag", plate, path: `/feestdag/${holiday.slug}`, holidayName: holiday.name, days: holiday.days };
    }
    const wd = weekday(day);
    if (wd === 1) {
      const cats = [...new Set(list.filter((p) => p.kind === "werkblad").map((p) => p.category))];
      const week = Math.floor(Date.parse(`${day}T12:00:00Z`) / (7 * 86_400_000));
      const category = cats[week % Math.max(1, cats.length)];
      const plate = category ? fresh((p) => p.category === category && p.kind === "kleurplaat") : undefined;
      if (plate) return { kind: "lespakket", plate, path: "/lespakketten" };
    }
    if (wd === 5) {
      const plate = fresh((p) => ["knipplaat", "bouwplaat", "vouwblad"].includes(p.kind) && !p.holiday);
      if (plate) return { kind: "knutselen", plate, path: `/platen/${plate.slug}` };
    }
    const plate = fresh((p) => p.kind === "kleurplaat" && !p.holiday);
    return plate ? { kind: "plaat", plate, path: `/platen/${plate.slug}` } : null;
  }

  // ---------- Plaatsen ----------

  /** Goedgekeurde posts waarvan het moment is aangebroken. */
  async publishDue(now = new Date()) {
    const due = await this.tx((tx) => tx.select().from(posts).where(and(eq(posts.tenantId, this.tenant), eq(posts.status, "goedgekeurd"), lte(posts.scheduledAt, now), lt(posts.attempts, MAX_ATTEMPTS), inArray(posts.channel, [...CHANNELS])))
      .orderBy(asc(posts.scheduledAt)).limit(10));
    let done = 0;
    for (const p of due) {
      try {
        const r = await this.publish(p);
        await this.tx((tx) => tx.update(posts).set({ status: "geplaatst", publishedAt: new Date(), externalUrl: r.url, error: null, updatedAt: new Date() }).where(eq(posts.id, p.id)));
        done++;
      } catch (e) {
        const attempts = p.attempts + 1;
        const message = e instanceof Error ? e.message : String(e);
        this.log.warn(`Plaatsen op ${p.channel} mislukt (${attempts}/${MAX_ATTEMPTS}): ${message}`);
        await this.tx((tx) => tx.update(posts).set({ attempts, error: message.slice(0, 500), status: attempts >= MAX_ATTEMPTS ? "mislukt" : "goedgekeurd", updatedAt: new Date() }).where(eq(posts.id, p.id)));
      }
    }
    return done;
  }

  private async publish(p: typeof posts.$inferSelect) {
    const kind = p.channel as ChannelKind;
    const ch = await this.channel(kind);
    if (!ch) throw new ApiProblem(`${kind} is niet gekoppeld of staat uit`);
    if (kind === "pinterest") {
      const api = this.pinterest();
      if (!api) throw new ApiProblem("Pinterest is niet ingesteld");
      let tokens = ch.tokens;
      // Toegangssleutel bijna verlopen: eerst vernieuwen (Pinterest geeft er een nieuwe vernieuwingssleutel bij).
      if (tokens.expiresAt && tokens.expiresAt - Date.now() < 86_400_000) {
        tokens = await api.refresh(tokens);
        await this.tx((tx) => tx.update(channels).set({ token: seal(this.env.SOCIAL_SECRET, tokens), updatedAt: new Date() }).where(eq(channels.id, ch.id)));
      }
      const boards = (ch.settings.boards ?? {}) as Record<string, string>;
      const name = p.board ?? "Kleurplaten";
      const boardId = await api.board(tokens, name, boards);
      if (!boards[name]) await this.tx((tx) => tx.update(channels).set({ settings: { ...ch.settings, boards: { ...boards, [name]: boardId } }, updatedAt: new Date() }).where(eq(channels.id, ch.id)));
      return api.pin(tokens, { boardId, title: p.title, description: p.body, link: p.link, image: p.image, alt: p.title });
    }
    const api = this.meta();
    if (!api) throw new ApiProblem("Meta is niet ingesteld");
    return kind === "facebook"
      ? api.facebook(ch.externalId!, ch.tokens.access, { message: p.body, image: p.image })
      : api.instagram(ch.externalId!, ch.tokens.access, { caption: p.body, image: p.image });
  }

  // ---------- De ochtendmail ----------

  /** Eén mail per dag (vanaf 7 uur) met de voorstellen die op goedkeuring wachten. */
  async digest(now = new Date()) {
    const s = await this.settings();
    const today = localDay(now);
    if (!s.notifyEmail || s.digestSentOn === today || localHour(now) < 7 || !this.mail.enabled(true)) return false;
    const open = await this.list({ status: ["voorstel"] });
    if (!open.length) return false;
    const link = `${this.env.ADMIN_URL.replace(/\/$/, "")}/social`;
    const label: Record<string, string> = { pinterest: "Pinterest", facebook: "Facebook", instagram: "Instagram", delen: "Om te delen" };
    const when = (iso: string) => new Intl.DateTimeFormat("nl-NL", { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", timeZone: TZ }).format(new Date(iso));
    const esc = (t: string) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const rows = open.slice(0, 30).map((p) => `<tr><td style="padding:6px 8px;vertical-align:top"><img src="${esc(p.image)}" width="64" alt="" style="border-radius:6px"></td><td style="padding:6px 8px;vertical-align:top;font:14px/1.4 sans-serif"><b>${label[p.channel]}</b> · ${when(p.scheduledAt)}<br>${esc(p.title)}</td></tr>`).join("");
    await this.mail.send({
      to: s.notifyEmail, transactional: true,
      subject: `${open.length} ${open.length === 1 ? "voorstel" : "voorstellen"} voor social media`,
      text: `Er ${open.length === 1 ? "staat 1 voorstel" : `staan ${open.length} voorstellen`} klaar om goed te keuren:\n\n${open.slice(0, 30).map((p) => `- ${label[p.channel]} (${when(p.scheduledAt)}): ${p.title}`).join("\n")}\n\nGoedkeuren: ${link}`,
      html: `<p style="font:15px/1.5 sans-serif">Er ${open.length === 1 ? "staat 1 voorstel" : `staan ${open.length} voorstellen`} klaar om goed te keuren.</p><table>${rows}</table><p style="font:15px/1.5 sans-serif"><a href="${link}" style="display:inline-block;padding:10px 16px;background:#1d1b22;color:#fff;border-radius:8px;text-decoration:none">Bekijken en goedkeuren</a></p>`,
    });
    await this.setSettings({ digestSentOn: today });
    return true;
  }

  /** Eén ronde: voorstellen (één keer per dag, vanaf 5 uur), plaatsen wat klaarstaat en de ochtendmail. */
  async tick(now = new Date()) {
    const s = await this.settings();
    if (s.generatedOn !== localDay(now) && localHour(now) >= 5) await this.generate(now);
    await this.publishDue(now);
    await this.digest(now);
  }
}
