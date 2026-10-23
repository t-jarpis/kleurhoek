import { ingest, normalizeMarket } from "@/lib/ingest";

const API_URL = process.env.API_URL ?? "http://localhost:3001";
const SLUG = /^[a-z0-9-]{2,64}$/;

/**
 * Doorklikken naar een product: telt de klik (zonder cookies) en stuurt door naar de partnerlink.
 * Het adres komt altijd uit de API, nooit uit de URL: zo kan niemand deze route als open
 * doorverwijzing misbruiken. Voorbeeld: /ga/kinderschaar-rond?plaat=lampion-maken&m=nl-nl
 */
export async function GET(request: Request, { params }: { params: Promise<{ product: string }> }) {
  const { product } = await params;
  const q = new URL(request.url).searchParams;
  const market = normalizeMarket(q.get("m"));
  const plate = q.get("plaat") ?? undefined;
  if (!SLUG.test(product) || !market || (plate !== undefined && !/^[a-z0-9-]{1,64}$/.test(plate))) return new Response("Niet gevonden", { status: 404 });

  // De organisatie (van de proxy) bepaalt of de winkel aan staat; zonder winkel geeft de API 404.
  const org = request.headers.get("x-kh-org") ?? "kleurhoek";
  const qs = new URLSearchParams({ org, ...(plate ? { plate } : {}) });
  const res = await fetch(`${API_URL}/v1/markets/${market}/products/${product}/link?${qs}`, { cache: "no-store", signal: AbortSignal.timeout(3000) }).catch(() => null);
  if (!res?.ok) return new Response("Dit product is niet (meer) beschikbaar.", { status: 404, headers: { "cache-control": "no-store" } });
  const { url } = (await res.json()) as { url: string };
  if (!url.startsWith("https://")) return new Response(null, { status: 502 });

  await ingest(request, { type: "product_click", market, plate, product });
  return new Response(null, { status: 302, headers: { location: url, "cache-control": "no-store", "referrer-policy": "no-referrer", "x-robots-tag": "noindex" } });
}
