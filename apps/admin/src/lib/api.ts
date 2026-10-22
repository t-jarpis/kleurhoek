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
export interface Role { slug: string; name: string; permissions: string[] }
export interface Me { userId: string; subject: string; permissions: string[] }

export class ApiError extends Error {
  constructor(readonly status: number, message: string) { super(message); }
}

async function call<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { ...init, cache: "no-store", headers: { ...init.headers, authorization: `Bearer ${await adminToken()}`, "content-type": "application/json" } });
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
  setStatus: (id: string, status: "active" | "blocked") => call<AdminUser>(`/v1/admin/users/${encodeURIComponent(id)}/status`, { method: "PUT", body: JSON.stringify({ status }) }),
};

/** Nette foutmelding voor een pagina. */
export function describe(error: unknown): { title: string; text: string } {
  if (error instanceof ApiError && error.status === 401) return { title: "Geen toegang", text: "Je account is (nog) niet actief in het admin panel. Vraag een platformbeheerder om je te activeren." };
  if (error instanceof ApiError && error.status === 403) return { title: "Geen rechten", text: "Je rol geeft geen toegang tot deze pagina. Vraag een platformbeheerder om een rol." };
  return { title: "Geen verbinding met de API", text: (error as Error).message };
}
