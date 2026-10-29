import { markFor, MARKET, siteDomains } from "@/lib/sites";

/** Pinterest-plaatje van een plaat (ADR 0057): /v1/pins/<markt>/<plaat>.png, via de API. */
const API_URL = process.env.API_URL ?? "http://localhost:3001";

export async function GET(request: Request, { params }: { params: Promise<{ market: string; file: string }> }) {
  const { market, file } = await params;
  const m = /^([a-z0-9-]{1,64})\.png$/.exec(file);
  if (!MARKET.test(market) || !m) return new Response("Niet gevonden", { status: 404 });
  const ip = request.headers.get("cf-connecting-ip");
  const domain = markFor(market, siteDomains());
  const upstream = await fetch(`${API_URL}/v1/markets/${market}/plates/${m[1]}/pin.png?domain=${encodeURIComponent(domain)}`, { cache: "no-store", headers: ip ? { "cf-connecting-ip": ip } : {} });
  if (!upstream.ok) return new Response(null, { status: upstream.status === 404 ? 404 : 502 });
  return new Response(upstream.body, {
    status: 200,
    headers: { "content-type": "image/png", "cache-control": upstream.headers.get("cache-control") ?? "public, max-age=86400", "x-content-type-options": "nosniff" },
  });
}
