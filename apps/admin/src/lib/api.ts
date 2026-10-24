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
export interface SiteAccess { enabled: boolean; entries: SiteAccessEntry[]; updatedBy: string; updatedAt: string }
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
export interface Release { sha: string; previousSha: string | null; kind: "first" | "release" | "rollback"; startedAt: string; notes: { sha: string; date: string; text: string; technical: boolean }[] }
export type GoalMetric = "visits" | "plates" | "clicks";
export interface GoalMilestone { month: number; target: number; stretch: number }
export interface Goals {
  start: string; current: string; custom: boolean;
  metrics: { metric: GoalMetric; milestones: GoalMilestone[]; months: { month: string; target: number; stretch: number; actual: number | null }[];
    now: { actual: number; target: number; stretch: number; expected: number; onTrack: boolean } | null }[];
}
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

export type OrgKind = "platform" | "school" | "opvang" | "vereniging" | "bedrijf" | "overig";
export interface OrgBrand { theme: string | null; font: string | null; colors: { primary: string | null; accent: string | null }; wordmark: string | null; logoVersion: string | null }
export interface OrgOffer { markets: string[] | null; categories: string[] | null; ages: string[] | null; kinds: ("kleurplaat" | "knutselen")[] | null }
export interface Organization {
  id: string; slug: string; name: string; kind: OrgKind; active: boolean; isDefault: boolean; hosts: string[];
  brand: OrgBrand; offer: OrgOffer; features: { shop: boolean; accounts: boolean }; updatedBy: string; updatedAt: string; subdomain: string | null;
}
export interface OrgChoices {
  themes: { id: string; name: string; description?: string; font: string }[]; fonts: { id: string; family: string }[]; kinds: OrgKind[];
  hostPattern: string | null; reserved: string[];
  options: { markets: string[]; categories: { slug: string; name: string }[]; ages: { slug: string; name: string }[]; kinds: { slug: "kleurplaat" | "knutselen"; name: string }[] };
}
export interface OrgInput {
  name?: string; kind?: OrgKind; active?: boolean; hosts?: string[];
  brand?: { theme?: string | null; font?: string | null; colors?: { primary?: string | null; accent?: string | null }; wordmark?: string | null };
  offer?: Partial<OrgOffer>; features?: { shop?: boolean; accounts?: boolean };
}

export interface OverviewTotals { visitors: number; pageViews: number; plateViews: number; downloads: number; completions: number }
export interface Overview {
  from: string; to: string; bucket: "day" | "week"; previous: { from: string; to: string };
  totals: OverviewTotals; previousTotals: OverviewTotals;
  series: { date: string; visitors: number; pageViews: number; plateViews: number; downloads: number }[];
  pages: { page: string; views: number; visitors: number }[]; devices: { device: string; views: number }[];
  organizations: { org: string; visitors: number; views: number }[];
  topPlates: Summary["topPlates"]; countries: Summary["byCountry"];
}
export interface AccountStats { total: number; created: number; createdBefore: number; active: number; returning: number; series: { date: string; count: number }[] }


export type ConversationStatus = "new" | "open" | "answered" | "closed";
export type ContactTopic = "question" | "idea" | "bug" | "partnership" | "copyright" | "privacy";
export interface ConversationSummary {
  id: string; channel: "web" | "whatsapp"; topic: ContactTopic; status: ConversationStatus; name: string | null; email: string | null; phone: string | null;
  org: string; market: string; lastMessageAt: string; createdAt: string; preview: string;
}
export interface Inbox { page: number; pageSize: number; total: number; counts: Record<ConversationStatus, number>; conversations: ConversationSummary[] }
export interface Conversation extends Omit<ConversationSummary, "preview"> {
  updatedBy: string | null; messages: { id: string; direction: "in" | "out" | "note"; body: string; author: string | null; createdAt: string }[];
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
  products: () => call<{ products: Product[]; materials: { slug: string; name: string }[]; partners: { slug: string; name: string; enabled: boolean; allowedHosts: string[] }[]; suggestions: ProductSuggestion[] }>("/v1/admin/shop/products"),
  importSuggestions: (slugs: string[]) => call<{ added: string[] }>("/v1/admin/shop/products/suggestions", { method: "POST", body: JSON.stringify({ slugs }) }),
  saveProduct: (slug: string, body: ProductInput) => call<{ slug: string }>(`/v1/admin/shop/products/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
  shopSummary: (from: string, to: string) => call<ShopSummary>(`/v1/admin/analytics/shop?from=${from}&to=${to}`),
  siteAccess: () => call<SiteAccess>("/v1/admin/site-access"),
  updateSiteAccess: (body: { enabled?: boolean; entries?: { cidr: string; label: string }[] }) =>
    call<SiteAccess>("/v1/admin/site-access", { method: "PUT", body: JSON.stringify(body) }),
  organizations: () => call<{ organizations: Organization[] } & OrgChoices>("/v1/admin/organizations"),
  organization: (slug: string) => call<Organization & OrgChoices>(`/v1/admin/organizations/${encodeURIComponent(slug)}`),
  createOrganization: (body: { slug: string; name: string; kind: OrgKind }) => call<Organization>("/v1/admin/organizations", { method: "POST", body: JSON.stringify(body) }),
  updateOrganization: (slug: string, body: OrgInput) => call<Organization>(`/v1/admin/organizations/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
  setOrganizationLogo: (slug: string, contentType: string, data: string) =>
    call<Organization>(`/v1/admin/organizations/${encodeURIComponent(slug)}/logo`, { method: "PUT", body: JSON.stringify({ contentType, data }) }),
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
