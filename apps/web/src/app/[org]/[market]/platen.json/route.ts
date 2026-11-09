import { api, NotFound } from "@/lib/api";
import { LIVE_MARKETS } from "@/lib/markets";
import { getOrg } from "@/lib/org";

/**
 * Alle platen van deze organisatie en markt voor zoeken en filters op de voorpagina (ADR 0099). Bewaard zoals de
 * pagina's (ISR, ADR 0093): bij het eerste verzoek gemaakt, dezelfde tags als de API-aanroep, en via `getOrg`
 * hoogstens een halve minuut achter op het admin panel.
 */
export const revalidate = 300;
/** Leeg: niets bij de build, wel bewaren na het eerste verzoek (ADR 0093). */
export function generateStaticParams() { return []; }

const missing = () => Response.json({ items: [] }, { status: 404, headers: { "x-robots-tag": "noindex" } });

export async function GET(_request: Request, { params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org || !LIVE_MARKETS.includes(market) || (org.offer.markets && !org.offer.markets.includes(market))) return missing();
  try {
    const items = await api.plates(market, slug);
    return Response.json({ items }, { headers: { "x-robots-tag": "noindex" } });
  } catch (e) {
    if (e instanceof NotFound) return missing();
    throw e;
  }
}
