import "server-only";

/** Huisstijl van de organisatie waarvoor iemand inlogt (ADR 0017/0018), zoals de API die geeft. */
export interface Org {
  slug: string; name: string; isDefault: boolean;
  brand: { theme: string | null; font: string | null; colors: { primary: string | null; accent: string | null }; wordmark: string | null; logoVersion: string | null };
  features: { shop: boolean; accounts: boolean };
}

const API_URL = () => process.env.API_URL ?? "http://localhost:3001";
const headers = () => ({ "x-ingest-key": process.env.INGEST_KEY ?? "" });

export const FALLBACK: Org = {
  slug: "kleurhoek", name: "Kleurhoek", isDefault: true,
  brand: { theme: null, font: null, colors: { primary: null, accent: null }, wordmark: null, logoVersion: null },
  features: { shop: true, accounts: true },
};

/** De organisatie bij de site waar iemand na het inloggen naartoe gaat (host van de redirect-URI). */
export async function orgForRedirect(redirectUri: string): Promise<Org> {
  let host: string;
  try { host = new URL(redirectUri).host.toLowerCase(); } catch { return FALLBACK; }
  const res = await fetch(`${API_URL()}/v1/internal/organizations/resolve?host=${encodeURIComponent(host)}`, { headers: headers(), cache: "no-store", signal: AbortSignal.timeout(5000) }).catch(() => null);
  return res?.ok ? ((await res.json()) as Org) : FALLBACK;
}

export async function getOrg(slug: string): Promise<Org> {
  if (!/^[a-z0-9-]{1,32}$/.test(slug)) return FALLBACK;
  const res = await fetch(`${API_URL()}/v1/internal/organizations/${slug}`, { headers: headers(), next: { revalidate: 30 }, signal: AbortSignal.timeout(5000) }).catch(() => null);
  return res?.ok ? ((await res.json()) as Org) : FALLBACK;
}

export const logoSrc = (org: Org) => (org.brand.logoVersion ? `/merk/${org.slug}/${org.brand.logoVersion}` : null);
