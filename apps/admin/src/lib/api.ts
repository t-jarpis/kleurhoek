import "server-only";
import { adminToken } from "./session";

const API_URL = process.env.API_URL ?? "http://localhost:3001";

export interface RateLimitRule {
  slug: string; description: string; limit: number; windowSeconds: number; keyBy: "ip" | "user" | "client"; enabled: boolean;
  updatedBy: string; updatedAt: string; days: { day: string; allowed: number; blocked: number }[];
}
export interface Summary {
  topPlates: { plate: string; views: number; downloads: number; prints: number; completions: number }[];
  byCountry: { country: string; pageViews: number; plateViews: number }[];
}
export interface AdminUser {
  id: string; kind: "member" | "admin"; status: "active" | "blocked"; displayName: string | null; email: string | null;
  locale: string | null; country: string | null; roles: string[]; createdAt: string; lastLoginAt: string | null;
}
export interface SiteAccessEntry { cidr: string; label: string; addedBy: string; addedAt: string }
export interface SiteAccess { enabled: boolean; entries: SiteAccessEntry[]; loginEnabled: boolean; updatedBy: string; updatedAt: string }
export interface Role { slug: string; name: string; permissions: string[] }
export interface Me { userId: string; subject: string; permissions: string[] }

export interface Partner {
  slug: string; name: string; enabled: boolean; linkTemplate: string; settings: Record<string, string>;
  allowedHosts: string[]; updatedBy: string; updatedAt: string;
}
export interface Product {
  slug: string; partner: string; url: string; ean: string | null; priceHint: string | null; enabled: boolean;
  markets: string[]; name: string | null; note: string | null; materials: string[]; rank: number;
}
export interface Release { sha: string; previousSha: string | null; kind: "first" | "release" | "rollback"; startedAt: string; notes: { sha: string; date: string; text: string; technical: boolean; public?: string }[] }
export type GoalMetric = "visits" | "plates" | "clicks";
export interface GoalMilestone { month: number; target: number; stretch: number }
export interface Goals {
  start: string; current: string; custom: boolean;
  metrics: { metric: GoalMetric; milestones: GoalMilestone[]; months: { month: string; target: number; stretch: number; actual: number | null }[];
    now: { actual: number; target: number; stretch: number; expected: number; onTrack: boolean } | null }[];
}
/** Een markt (land + taal) en een Amazon-winkel met de markten die hij bedient (ADR 0031). */
export interface MarketInfo { code: string; country: string; language: string; status: "draft" | "live" }
export interface AmazonStore { partner: string; name: string; host: string; markets: string[]; enabled: boolean }
export interface AmazonInput { asin: string; name: string; names?: Record<string, string>; priceHint?: string | null; materials: string[]; stores: string[] }
export interface ProductSuggestion { slug: string; partner: string; url: string; name: string; note: string; materials: string[]; markets: string[] }
export interface ProductInput {
  partner: string; url: string; ean?: string | null; priceHint?: string | null; enabled: boolean;
  markets: string[]; name: string; note?: string | null; materials: string[]; rank?: number;
}
export interface ShopSummary {
  from: string; to: string; previous: { from: string; to: string };
  totals: { materialsViews: number; productClicks: number; clickRate: number };
  products: { product: string; clicks: number; visitors: number; previousVisitors: number; growth: number | null; topPlates: string[] }[];
  plates: { plate: string; materialsViews: number; productClicks: number; clickRate: number }[];
  candidates: ShopSummary["products"];
}

/** Verkopen uit partnerrapporten (ADR 0033). */
export type SalesField = "date" | "subId" | "product" | "items" | "revenue" | "commission" | "currency";
export type SalesMapping = Record<SalesField, string | null>;
export interface SalesRow { day: string; subId: string; product: string; items: number; revenueCents: number; commissionCents: number; currency: string }
export interface SalesPreview { headers: string[]; mapping: SalesMapping; sample: SalesRow[]; total: number; skipped: number; from: string | null; to: string | null; matchedProducts: number; matchedPlates: number; problem: string | null }
export interface SalesReport {
  from: string; to: string;
  byPartner: { partner: string; currency: string; orders: number; items: number; revenueCents: number; commissionCents: number }[];
  byProduct: { product: string; matched: boolean; partner: string; currency: string; orders: number; items: number; commissionCents: number }[];
  byPlate: { plate: string; orders: number; commissionCents: number; currency: string }[];
  coverage: { partner: string; lastDay: string }[];
  imports: { id: string; partner: string; fileName: string; from: string; to: string; rows: number; by: string; at: string }[];
}

export type OrgKind = "platform" | "school" | "opvang" | "vereniging" | "bedrijf" | "overig";
export interface OrgBrand { theme: string | null; font: string | null; colors: { primary: string | null; accent: string | null }; wordmark: string | null; logoVersion: string | null }
export interface OrgOffer { markets: string[] | null; categories: string[] | null; ages: string[] | null; kinds: ("kleurplaat" | "knutselen")[] | null; collections: string[] | null; goals: string[] | null; excluded: string[] }
export interface OrgFeatures { shop: boolean; accounts: boolean; learningFilters: boolean }
/** Collecties (ADR 0036). */
export interface Collection { slug: string; names: Record<string, string>; descriptions: Record<string, string>; plates: string[]; sortOrder: number; updatedBy: string; updatedAt: string }
export interface CollectionPlate { slug: string; name: string; category: string; categoryName: string; kind: string; age: string; goals: string[] }
export interface OrgManager { userId: string; displayName: string | null; email: string | null; since: string }
export interface Organization {
  id: string; slug: string; name: string; kind: OrgKind; active: boolean; isDefault: boolean; hosts: string[];
  brand: OrgBrand; offer: OrgOffer; features: OrgFeatures; updatedBy: string; updatedAt: string; subdomain: string | null;
}
export interface OrgChoices {
  themes: { id: string; name: string; description?: string; font: string }[]; fonts: { id: string; family: string }[]; kinds: OrgKind[];
  hostPattern: string | null; reserved: string[];
  options: { markets: string[]; categories: { slug: string; name: string }[]; ages: { slug: string; name: string }[]; kinds: { slug: "kleurplaat" | "knutselen"; name: string }[]; goals: { slug: string; name: string }[]; collections: { slug: string; name: string; plates: number }[] };
}
export interface OrgInput {
  name?: string; kind?: OrgKind; active?: boolean; hosts?: string[];
  brand?: { theme?: string | null; font?: string | null; colors?: { primary?: string | null; accent?: string | null }; wordmark?: string | null };
  offer?: Partial<OrgOffer>; features?: Partial<OrgFeatures>;
}

export interface OverviewTotals { visitors: number; pageViews: number; plateViews: number; downloads: number; completions: number; prints: number; pdfDownloads: number; materialsViews: number; productClicks: number }
export interface Realtime { since: string; visitors: number; pageViews: number; pages: { page: string; views: number }[]; plates: { plate: string; views: number }[] }
export interface Overview {
  from: string; to: string; bucket: "day" | "week"; previous: { from: string; to: string };
  totals: OverviewTotals; previousTotals: OverviewTotals;
  series: { date: string; visitors: number; pageViews: number; plateViews: number; downloads: number }[];
  pages: { page: string; views: number; visitors: number }[]; devices: { device: string; views: number }[];
  entries: { entry: string; landings: number; visitors: number }[]; referrers: { referrer: string; landings: number }[];
  organizations: { org: string; visitors: number; views: number }[];
  topPlates: Summary["topPlates"]; countries: Summary["byCountry"];
}
export interface AccountStats { total: number; created: number; createdBefore: number; active: number; returning: number; series: { date: string; count: number }[] }


export type ConversationStatus = "new" | "open" | "answered" | "closed";
export type ContactTopic = "question" | "idea" | "bug" | "partnership" | "copyright" | "privacy" | "organization";
export interface OrgRequest { organization: string; kind: "school" | "opvang" | "vereniging" | "bedrijf" | "overig"; code: string | null; children: string | null; website: string | null }
export interface ConversationSummary {
  id: string; channel: "web" | "whatsapp"; topic: ContactTopic; status: ConversationStatus; name: string | null; email: string | null; phone: string | null;
  org: string; market: string; lastMessageAt: string; createdAt: string; preview: string;
}
export interface Inbox { page: number; pageSize: number; total: number; counts: Record<ConversationStatus, number>; conversations: ConversationSummary[] }
export interface Conversation extends Omit<ConversationSummary, "preview"> {
  updatedBy: string | null; details: OrgRequest | null; messages: { id: string; direction: "in" | "out" | "note"; body: string; author: string | null; createdAt: string }[];
}
export interface ContactChannel { slug: "web" | "whatsapp"; enabled: boolean; connected: boolean; settings: Record<string, string>; updatedBy: string; updatedAt: string | null }

export interface Source {
  id: string; themeSlug: string; url: string; host: string; title: string | null; description: string | null;
  basis: "link" | "license"; licenseNote: string | null; licenseDate: string | null;
  status: "pending" | "approved" | "rejected"; health: "unknown" | "ok" | "broken"; changed: boolean;
  httpStatus: number | null; finalUrl: string | null; robotsAllowed: boolean | null; pageTitle: string | null; checkNote: string | null;
  failCount: number; lastCheckedAt: string | null; lastOkAt: string | null; approvedBy: string | null; approvedAt: string | null; live: boolean;
}
export interface Theme {
  slug: string; status: "draft" | "published"; name: string | null; description: string | null; makerName: string; makerUrl: string;
  productSlugs: string[]; sortOrder: number; updatedBy: string; updatedAt: string; counts: { total: number; live: number; attention: number };
}
/** Vindbaarheid (ADR 0035). */
export interface SeoSettings { googleVerification: string | null; bingVerification: string | null; home: Record<string, { title: string | null; description: string | null }> }
export interface SeoOverview { settings: SeoSettings; markets: { market: string; language: string; plates: number; themes: number }[]; indexableHost: string; indexableHosts: string[] }

/** Zoekcijfers (ADR 0041). */
export type SearchEngine = "google" | "bing";
export interface SearchMetric { clicks: number; impressions: number; position: number | null }
export interface SearchReport {
  from: string; to: string;
  configured: { domains: string[]; engines: SearchEngine[] };
  totals: (SearchMetric & { engine: SearchEngine })[];
  sites: (SearchMetric & { site: string; engine: SearchEngine })[];
  series: { day: string; engine: SearchEngine; clicks: number; impressions: number }[];
  queries: (SearchMetric & { key: string })[];
  pages: (SearchMetric & { key: string })[];
  sync: { engine: SearchEngine; site: string; ok: boolean; message: string | null; lastDay: string | null; runAt: string }[];
  own: { engine: string; landings: number; visitors: number }[];
  ownByDomain: { entry: string; landings: number }[];
}

/** Mail (ADR 0037). */
export type MailTopic = "nieuwe-platen" | "feestdagen" | "nieuwsbrief";
export type I18nText = Record<string, string>;
export type MailBlock =
  | { id: string; type: "heading"; text: I18nText }
  | { id: string; type: "text"; text: I18nText }
  | { id: string; type: "button"; label: I18nText; url: string }
  | { id: string; type: "plates"; source: "new" | "holiday" | "collection" | "selected"; collection?: string; slugs?: string[]; max: number; columns: 2 | 3 }
  | { id: string; type: "divider" };
export interface MailTemplate { slug: string; name: string; kind: "system" | "automation" | "campaign"; subject: I18nText; preheader: I18nText; blocks: MailBlock[]; updatedBy: string; updatedAt: string }
export type MailTemplateInput = Pick<MailTemplate, "name" | "kind" | "subject" | "preheader" | "blocks">;
/** Alleen de velden die de API aanneemt (een template uit de lijst heeft ook id, datums …). */
const templateBody = (t: MailTemplateInput): MailTemplateInput => ({ name: t.name, kind: t.kind, subject: t.subject, preheader: t.preheader, blocks: t.blocks });
export type MailTrigger = { type: "subscribed" } | { type: "schedule"; weekday: number; hour: number } | { type: "plates_published"; min: number } | { type: "holiday_soon"; days: number };
export type MailStep = { type: "filter"; topics?: MailTopic[]; markets?: string[] } | { type: "require_plates"; min: number } | { type: "wait"; hours: number } | { type: "send"; template: string };
export interface MailWorkflow { slug: string; name: string; enabled: boolean; trigger: MailTrigger; steps: MailStep[]; cursor: string | null; updatedBy: string; updatedAt: string }
export interface MailCampaign { id: string; name: string; template: string; audience: { topics: MailTopic[]; markets: string[] | null }; status: "draft" | "scheduled" | "sending" | "sent" | "cancelled"; scheduledAt: string | null; sentAt: string | null; recipients: number; createdBy: string; createdAt: string; deliveries: Record<string, number> }
export interface MailOptions { topics: MailTopic[]; markets: string[]; languages: string[]; templates: { slug: string; name: string; kind: string }[]; collections: { slug: string; name: string }[] }
export interface MailOverview {
  sending: { bulk: boolean; transactional: boolean };
  subscribers: { active: number; pending: number; byTopic: Record<string, number>; byMarket: Record<string, number> };
  queue: { queued?: number; sent?: number; failed?: number; expired?: number; errors: { error: string | null; n: number }[] };
  runs: Record<string, Record<string, number>>; options: MailOptions;
}
/** Bezorging (ADR 0038). */
export interface MailCounts { sent: number; delivered: number; deferred: number; soft: number; hard: number; complaints: number; unsubscribes: number }
export type MailHealth = "goed" | "let op" | "slecht" | "te weinig";
export interface MailDeliveryEvent { type: string; provider: string; domain?: string; source: string | null; template?: string | null; reason: string | null; at: string }
export interface MailDeliverability {
  days: number; totals: MailCounts; daily: (MailCounts & { day: string })[]; byDomain: (MailCounts & { domain: string })[];
  bySource: (MailCounts & { source: string | null; template: string | null })[]; recent: MailDeliveryEvent[];
  limits: { bounce: { warn: number; bad: number }; complaint: { warn: number; bad: number } };
  rates: { bounce: number; complaint: number; delivered: number | null }; health: { bounce: MailHealth; complaint: MailHealth };
  providers: Record<string, { last: string; events: number }>; suppressed: Record<string, number>; sending: { bulk: boolean; transactional: boolean };
}
export interface MailSuppressionLookup {
  suppression: { reason: string; detail: string | null; since: string; expiresAt: string | null; by: string } | null;
  events: MailDeliveryEvent[];
}
export interface MailSubscriber { id: string; email: string; market: string; topics: MailTopic[]; status: "pending" | "active"; viaAccount: boolean; consentAt: string; confirmedAt: string | null }

export interface SourceInput { title?: string; description?: string | null; basis?: "link" | "license"; licenseNote?: string | null; licenseDate?: string | null }

export class ApiError extends Error {
  constructor(readonly status: number, message: string) { super(message); }
}

async function call<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { ...init, cache: "no-store", signal: AbortSignal.timeout(15_000), headers: { ...init.headers, authorization: `Bearer ${await adminToken()}`, ...(init.body ? { "content-type": "application/json" } : {}) } });
  if (!res.ok) {
    const body = await res.text();
    let message = body.slice(0, 200);
    try { message = (JSON.parse(body) as { message?: string }).message ?? message; } catch { /* geen JSON */ }
    throw new ApiError(res.status, message);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const adminApi = {
  me: () => call<Me>("/v1/admin/me"),
  rateLimits: () => call<{ rules: RateLimitRule[] }>("/v1/admin/rate-limits").then((r) => r.rules),
  updateRateLimit: (slug: string, body: { limit?: number; windowSeconds?: number; enabled?: boolean }) =>
    call(`/v1/admin/rate-limits/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
  releases: () => call<{ current: string | null; releases: Release[] }>("/v1/admin/releases"),
  goals: () => call<Goals>("/v1/admin/analytics/goals"),
  saveGoals: (body: { start: string; metrics: Record<GoalMetric, GoalMilestone[]> }) => call<Goals>("/v1/admin/analytics/goals", { method: "PUT", body: JSON.stringify(body) }),
  realtime: () => call<Realtime>("/v1/admin/analytics/realtime"),
  overview: (from: string, to: string) => call<Overview>(`/v1/admin/analytics/overview?from=${from}&to=${to}`),
  accountStats: (from: string, to: string) => call<AccountStats>(`/v1/admin/users/stats?from=${from}&to=${to}`),
  summary: (from: string, to: string) => call<Summary>(`/v1/admin/analytics/summary?from=${from}&to=${to}`),
  users: (q: { kind?: string; q?: string; page?: number }) => {
    const p = new URLSearchParams();
    if (q.kind) p.set("kind", q.kind);
    if (q.q) p.set("q", q.q);
    if (q.page) p.set("page", String(q.page));
    return call<{ users: AdminUser[]; total: number; page: number; pageSize: number }>(`/v1/admin/users?${p}`);
  },
  roles: () => call<{ roles: Role[]; permissions: Record<string, string> }>("/v1/admin/roles"),
  setRoles: (id: string, roles: string[]) => call<AdminUser>(`/v1/admin/users/${encodeURIComponent(id)}/roles`, { method: "PUT", body: JSON.stringify({ roles }) }),
  partners: () => call<{ partners: Partner[] }>("/v1/admin/shop/partners").then((r) => r.partners),
  createPartner: (body: { slug: string; name: string; linkTemplate: string; allowedHosts: string[] }) =>
    call<{ slug: string }>("/v1/admin/shop/partners", { method: "POST", body: JSON.stringify(body) }),
  updatePartner: (slug: string, body: { enabled?: boolean; linkTemplate?: string; settings?: Record<string, string> }) =>
    call<Partner>(`/v1/admin/shop/partners/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
  products: () => call<{ products: Product[]; materials: { slug: string; name: string }[]; partners: { slug: string; name: string; enabled: boolean; allowedHosts: string[] }[]; suggestions: ProductSuggestion[]; markets: MarketInfo[]; amazonStores: AmazonStore[] }>("/v1/admin/shop/products"),
  setProductEnabled: (slug: string, enabled: boolean) => call<{ slug: string; enabled: boolean }>(`/v1/admin/shop/products/${encodeURIComponent(slug)}/enabled`, { method: "PUT", body: JSON.stringify({ enabled }) }),
  amazonAdd: (body: AmazonInput) => call<{ asin: string; added: { slug: string; partner: string; url: string }[] }>("/v1/admin/shop/products/amazon", { method: "POST", body: JSON.stringify(body) }),
  importSuggestions: (slugs: string[]) => call<{ added: string[] }>("/v1/admin/shop/products/suggestions", { method: "POST", body: JSON.stringify({ slugs }) }),
  saveProduct: (slug: string, body: ProductInput) => call<{ slug: string }>(`/v1/admin/shop/products/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
  salesPreview: (body: { partner: string; csv: string; fileName?: string; mapping?: SalesMapping }) => call<SalesPreview>("/v1/admin/shop/sales/preview", { method: "POST", body: JSON.stringify(body) }),
  salesImport: (body: { partner: string; csv: string; fileName: string; mapping: SalesMapping }) => call<{ importId: string; from: string; to: string; rows: number }>("/v1/admin/shop/sales/import", { method: "POST", body: JSON.stringify(body) }),
  seo: () => call<SeoOverview>("/v1/admin/seo"),
  searchReport: (from: string, to: string) => call<SearchReport>(`/v1/admin/analytics/search?from=${from}&to=${to}`),
  refreshSearch: () => call<{ started: boolean }>("/v1/admin/analytics/search/refresh", { method: "POST", body: "{}" }),
  saveSeo: (body: SeoSettings) => call<SeoSettings>("/v1/admin/seo", { method: "PUT", body: JSON.stringify(body) }),
  salesReport: (from: string, to: string) => call<SalesReport>(`/v1/admin/shop/sales?from=${from}&to=${to}`),
  shopSummary: (from: string, to: string) => call<ShopSummary>(`/v1/admin/analytics/shop?from=${from}&to=${to}`),
  siteAccess: () => call<SiteAccess>("/v1/admin/site-access"),
  updateSiteAccess: (body: { enabled?: boolean; entries?: { cidr: string; label: string }[]; loginEnabled?: boolean }) =>
    call<SiteAccess>("/v1/admin/site-access", { method: "PUT", body: JSON.stringify(body) }),
  organizations: () => call<{ organizations: Organization[] } & OrgChoices>("/v1/admin/organizations"),
  organization: (slug: string) => call<Organization & OrgChoices>(`/v1/admin/organizations/${encodeURIComponent(slug)}`),
  createOrganization: (body: { slug: string; name: string; kind: OrgKind }) => call<Organization>("/v1/admin/organizations", { method: "POST", body: JSON.stringify(body) }),
  updateOrganization: (slug: string, body: OrgInput) => call<Organization>(`/v1/admin/organizations/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
  setOrganizationLogo: (slug: string, contentType: string, data: string) =>
    call<Organization>(`/v1/admin/organizations/${encodeURIComponent(slug)}/logo`, { method: "PUT", body: JSON.stringify({ contentType, data }) }),
  orgManagers: (slug: string) => call<{ managers: OrgManager[] }>(`/v1/admin/organizations/${encodeURIComponent(slug)}/managers`).then((r) => r.managers),
  addOrgManager: (slug: string, email: string) => call<{ managers: OrgManager[] }>(`/v1/admin/organizations/${encodeURIComponent(slug)}/managers`, { method: "POST", body: JSON.stringify({ email }) }),
  removeOrgManager: (slug: string, userId: string) => call<{ managers: OrgManager[] }>(`/v1/admin/organizations/${encodeURIComponent(slug)}/managers/${encodeURIComponent(userId)}`, { method: "DELETE" }),
  collections: () => call<{ collections: Collection[]; plates: CollectionPlate[]; goals: { slug: string; name: string }[] }>("/v1/admin/collections"),
  saveCollection: (slug: string, body: { names: Record<string, string>; descriptions?: Record<string, string>; plates: string[]; sortOrder?: number }) =>
    call<Collection>(`/v1/admin/collections/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteCollection: (slug: string) => call<void>(`/v1/admin/collections/${encodeURIComponent(slug)}`, { method: "DELETE" }),
  mailOverview: () => call<MailOverview>("/v1/admin/mail"),
  mailDeliverability: (days: number) => call<MailDeliverability>(`/v1/admin/mail/deliverability?days=${days}`),
  mailWebhooks: () => call<{ webhooks: Record<string, string> }>("/v1/admin/mail/deliverability/webhooks").then((r) => r.webhooks),
  mailSuppression: (email: string) => call<MailSuppressionLookup>(`/v1/admin/mail/suppressions?email=${encodeURIComponent(email)}`),
  addMailSuppression: (email: string, detail: string | null) => call<MailSuppressionLookup>("/v1/admin/mail/suppressions", { method: "POST", body: JSON.stringify({ email, ...(detail ? { detail } : {}) }) }),
  removeMailSuppression: (email: string) => call<{ removed: boolean; reason: string | null }>(`/v1/admin/mail/suppressions?email=${encodeURIComponent(email)}`, { method: "DELETE" }),
  mailSubscriber: (email: string) => call<{ subscriber: MailSubscriber | null }>(`/v1/admin/mail/subscribers?email=${encodeURIComponent(email)}`).then((r) => r.subscriber),
  removeMailSubscriber: (id: string) => call<void>(`/v1/admin/mail/subscribers/${encodeURIComponent(id)}`, { method: "DELETE" }),
  mailTemplates: () => call<{ templates: MailTemplate[]; options: MailOptions }>("/v1/admin/mail/templates"),
  mailTemplate: (slug: string) => call<{ template: MailTemplate; options: MailOptions }>(`/v1/admin/mail/templates/${encodeURIComponent(slug)}`),
  saveMailTemplate: (slug: string, body: MailTemplateInput) => call<MailTemplate>(`/v1/admin/mail/templates/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(templateBody(body)) }),
  deleteMailTemplate: (slug: string) => call<void>(`/v1/admin/mail/templates/${encodeURIComponent(slug)}`, { method: "DELETE" }),
  previewMail: (template: MailTemplateInput, market: string) => call<{ subject: string; html: string; text: string; empty: boolean }>("/v1/admin/mail/preview", { method: "POST", body: JSON.stringify({ template: templateBody(template), market }) }),
  testMail: (template: MailTemplateInput, market: string, email: string) => call<{ ok: true }>("/v1/admin/mail/test", { method: "POST", body: JSON.stringify({ template: templateBody(template), market, email }) }),
  mailWorkflows: () => call<{ workflows: MailWorkflow[]; runs: Record<string, Record<string, number>>; options: MailOptions }>("/v1/admin/mail/workflows"),
  saveMailWorkflow: (slug: string, body: Pick<MailWorkflow, "name" | "enabled" | "trigger" | "steps">) => call<MailWorkflow>(`/v1/admin/mail/workflows/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify({ name: body.name, enabled: body.enabled, trigger: body.trigger, steps: body.steps }) }),
  deleteMailWorkflow: (slug: string) => call<void>(`/v1/admin/mail/workflows/${encodeURIComponent(slug)}`, { method: "DELETE" }),
  mailCampaigns: () => call<{ campaigns: MailCampaign[]; options: MailOptions }>("/v1/admin/mail/campaigns"),
  mailAudience: (audience: MailCampaign["audience"]) => call<{ size: number }>("/v1/admin/mail/campaigns/audience", { method: "POST", body: JSON.stringify(audience) }).then((r) => r.size),
  createMailCampaign: (body: Pick<MailCampaign, "name" | "template" | "audience">) => call<MailCampaign>("/v1/admin/mail/campaigns", { method: "POST", body: JSON.stringify(body) }),
  scheduleMailCampaign: (id: string, at: string | null) => call<MailCampaign>(`/v1/admin/mail/campaigns/${encodeURIComponent(id)}/schedule`, { method: "POST", body: JSON.stringify({ at }) }),
  cancelMailCampaign: (id: string) => call<MailCampaign>(`/v1/admin/mail/campaigns/${encodeURIComponent(id)}/cancel`, { method: "POST" }),
  deleteOrganization: (slug: string) => call<void>(`/v1/admin/organizations/${encodeURIComponent(slug)}`, { method: "DELETE" }),
  removeOrganizationLogo: (slug: string) => call<Organization>(`/v1/admin/organizations/${encodeURIComponent(slug)}/logo`, { method: "DELETE" }),
  inbox: (q: { status?: ConversationStatus; page?: number }) => {
    const p = new URLSearchParams();
    if (q.status) p.set("status", q.status);
    if (q.page) p.set("page", String(q.page));
    return call<Inbox>(`/v1/admin/contact/conversations?${p}`);
  },
  unread: () => call<{ count: number }>("/v1/admin/contact/unread").then((r) => r.count),
  conversation: (id: string) => call<Conversation>(`/v1/admin/contact/conversations/${encodeURIComponent(id)}`),
  setConversationStatus: (id: string, status: ConversationStatus) => call<Conversation>(`/v1/admin/contact/conversations/${encodeURIComponent(id)}/status`, { method: "PUT", body: JSON.stringify({ status }) }),
  addConversationMessage: (id: string, direction: "out" | "note", body: string) => call<Conversation>(`/v1/admin/contact/conversations/${encodeURIComponent(id)}/messages`, { method: "POST", body: JSON.stringify({ direction, body }) }),
  deleteConversation: (id: string) => call<void>(`/v1/admin/contact/conversations/${encodeURIComponent(id)}`, { method: "DELETE" }),
  contactChannels: () => call<{ channels: ContactChannel[] }>("/v1/admin/contact/channels").then((r) => r.channels),
  updateContactChannel: (slug: string, body: { enabled?: boolean; settings?: Record<string, string> }) => call(`/v1/admin/contact/channels/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
  themes: () => call<{ themes: Theme[] }>("/v1/admin/sources/themes").then((r) => r.themes),
  theme: (slug: string) => call<Theme & { sources: Source[] }>(`/v1/admin/sources/themes/${encodeURIComponent(slug)}`),
  createTheme: (body: { slug: string; name: string; description: string; makerName: string; makerUrl: string }) => call<Theme>("/v1/admin/sources/themes", { method: "POST", body: JSON.stringify(body) }),
  updateTheme: (slug: string, body: { name?: string; description?: string; makerName?: string; makerUrl?: string; status?: "draft" | "published"; productSlugs?: string[] }) =>
    call<Theme>(`/v1/admin/sources/themes/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
  addSource: (theme: string, body: { url: string; title: string; description?: string | null; basis: "link" | "license"; licenseNote?: string | null; licenseDate?: string | null }) =>
    call<Source>(`/v1/admin/sources/themes/${encodeURIComponent(theme)}/sources`, { method: "POST", body: JSON.stringify(body) }),
  updateSource: (id: string, body: SourceInput) => call<Source>(`/v1/admin/sources/items/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(body) }),
  sourceAction: (id: string, action: "check" | "approve" | "reject") => call(`/v1/admin/sources/items/${encodeURIComponent(id)}/${action}`, { method: "POST" }),
  deleteSource: (id: string) => call<void>(`/v1/admin/sources/items/${encodeURIComponent(id)}`, { method: "DELETE" }),
  sourceReview: () => call<{ sources: Source[] }>("/v1/admin/sources/review").then((r) => r.sources),
  setStatus: (id: string, status: "active" | "blocked") => call<AdminUser>(`/v1/admin/users/${encodeURIComponent(id)}/status`, { method: "PUT", body: JSON.stringify({ status }) }),
};

/** Nette foutmelding voor een pagina. */
export function describe(error: unknown): { title: string; text: string } {
  if (error instanceof ApiError && error.status === 401) return { title: "Geen toegang", text: "Je account is (nog) niet actief in het admin panel. Vraag een platformbeheerder om je te activeren." };
  if (error instanceof ApiError && error.status === 403) return { title: "Geen rechten", text: "Je rol geeft geen toegang tot deze pagina. Vraag een platformbeheerder om een rol." };
  return { title: "Geen verbinding met de API", text: (error as Error).message };
}
