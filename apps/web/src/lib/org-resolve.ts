/**
 * Host → organisatie, voor de proxy (ADR 0017). Per host 30 seconden in het geheugen; bij een
 * storing geldt de laatst bekende, en anders Kleurhoek zelf.
 */
const API_URL = process.env.API_URL ?? "http://localhost:3001";
const INGEST_KEY = process.env.INGEST_KEY ?? "";
const TTL_MS = 30_000;
export const DEFAULT_ORG = "kleurhoek";

export interface ResolvedOrg { slug: string; markets: string[] | null }
const cache = new Map<string, { org: ResolvedOrg; at: number }>();

export async function resolveOrg(host: string): Promise<ResolvedOrg> {
  const key = host.toLowerCase();
  const hit = cache.get(key);
  if (hit && Date.now() - hit.at < TTL_MS) return hit.org;
  try {
    const res = await fetch(`${API_URL}/v1/internal/organizations/resolve?host=${encodeURIComponent(key)}`, {
      headers: { "x-ingest-key": INGEST_KEY }, cache: "no-store", signal: AbortSignal.timeout(2000),
    });
    if (!res.ok) throw new Error(`resolve ${res.status}`);
    const body = (await res.json()) as { slug: string; offer: { markets: string[] | null } };
    const org = { slug: body.slug, markets: body.offer.markets };
    if (cache.size > 500) cache.clear();
    cache.set(key, { org, at: Date.now() });
    return org;
  } catch {
    return hit?.org ?? { slug: DEFAULT_ORG, markets: null };
  }
}

/**
 * Paden die niet per organisatie zijn (routes, API-doorgifte, statische bestanden). Van /mail alleen de routes:
 * /mail en /mail/bevestigen zijn pagina's (op kleurhoek.nl zonder marktvoorvoegsel, ADR 0040).
 */
export const SHARED_PATH = /^\/(auth|e|ga|v1|merk|healthz|_next|favicon\.ico|robots\.txt|llms\.txt|indexnow\.txt|sitemap\.xml|sitemap|mail\/(?:events|afmelden|voorkeuren|bevestig))(\/|$)/;
