import { markFor, MARKET, siteDomains } from "@/lib/sites";

/** Plaatjes om te delen: /v1/pins/<markt>/<plaat>.png voor Pinterest (ADR 0057), .jpg (4:5) voor Instagram en Facebook (ADR 0063). */
const API_URL = process.env.API_URL ?? "http://localhost:3001";

export async function GET(request: Request, { params }: { params: Promise<{ market: string; file: string }> }) {
  const { market, file } = await params;
  const m = /^([a-z0-9-]{1,64})\.(png|jpg)$/.exec(file);
  if (!MARKET.test(market) || !m) return new Response("Niet gevonden", { status: 404 });
  const ip = request.headers.get("cf-connecting-ip");
  const domain = markFor(market, siteDomains());
  const upstream = await fetch(`${API_URL}/v1/markets/${market}/plates/${m[1]}/${m[2] === "png" ? "pin.png" : "post.jpg"}?domain=${encodeURIComponent(domain)}`, { cache: "no-store", headers: ip ? { "cf-connecting-ip": ip } : {} });
  if (!upstream.ok) return new Response(null, { status: upstream.status === 404 ? 404 : 502 });
  return new Response(upstream.body, {
    status: 200,
    headers: { "content-type": m[2] === "png" ? "image/png" : "image/jpeg", "cache-control": upstream.headers.get("cache-control") ?? "public, max-age=86400", "x-content-type-options": "nosniff" },
  });
}
