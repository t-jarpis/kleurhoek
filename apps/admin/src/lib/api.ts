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
  return res.json() as Promise<T>;
}

export const adminApi = {
  me: () => call<Me>("/v1/admin/me"),
  rateLimits: () => call<{ rules: RateLimitRule[] }>("/v1/admin/rate-limits").then((r) => r.rules),
  updateRateLimit: (slug: string, body: { limit?: number; windowSeconds?: number; enabled?: boolean }) =>
    call(`/v1/admin/rate-limits/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(body) }),
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
  products: () => call<{ products: Product[]; materials: { slug: string; name: string }[]; partners: { slug: string; name: string; enabled: boolean }[] }>("/v1/admin/shop/products"),
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
  removeOrganizationLogo: (slug: string) => call<Organization>(`/v1/admin/organizations/${encodeURIComponent(slug)}/logo`, { method: "DELETE" }),
  setStatus: (id: string, status: "active" | "blocked") => call<AdminUser>(`/v1/admin/users/${encodeURIComponent(id)}/status`, { method: "PUT", body: JSON.stringify({ status }) }),
};

/** Nette foutmelding voor een pagina. */
export function describe(error: unknown): { title: string; text: string } {
  if (error instanceof ApiError && error.status === 401) return { title: "Geen toegang", text: "Je account is (nog) niet actief in het admin panel. Vraag een platformbeheerder om je te activeren." };
  if (error instanceof ApiError && error.status === 403) return { title: "Geen rechten", text: "Je rol geeft geen toegang tot deze pagina. Vraag een platformbeheerder om een rol." };
  return { title: "Geen verbinding met de API", text: (error as Error).message };
}
