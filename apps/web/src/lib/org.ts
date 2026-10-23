import "server-only";

/** Organisatie zoals de API die aan de website geeft (ADR 0017). */
export interface Org {
  slug: string; name: string; kind: string; isDefault: boolean;
  brand: { theme: string | null; font: string | null; colors: { primary: string | null; accent: string | null }; wordmark: string | null; logoVersion: string | null };
  offer: { markets: string[] | null; categories: string[] | null; ages: string[] | null; kinds: string[] | null };
  features: { shop: boolean; accounts: boolean };
  logo: string | null;
}

const API_URL = process.env.API_URL ?? "http://localhost:3001";
const INGEST_KEY = process.env.INGEST_KEY ?? "";

/** De organisatie op code; gecachet (30 s) zodat wijzigingen in het admin panel snel zichtbaar zijn. */
export async function getOrg(slug: string): Promise<Org | null> {
  const res = await fetch(`${API_URL}/v1/internal/organizations/${encodeURIComponent(slug)}`, {
    headers: { "x-ingest-key": INGEST_KEY }, next: { revalidate: 30, tags: [`org:${slug}`] },
  }).catch(() => null);
  if (!res?.ok) return null;
  return res.json() as Promise<Org>;
}

/** Adres van het logo via de eigen website (de API is niet publiek). */
export const logoSrc = (org: Org) => (org.brand.logoVersion ? `/merk/${org.slug}/${org.brand.logoVersion}` : null);
