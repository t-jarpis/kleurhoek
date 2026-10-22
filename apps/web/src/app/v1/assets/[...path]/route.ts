/**
 * SVG's van platen via het eigen domein. De API heeft geen publieke ingang; Cloudflare cachet deze
 * antwoorden (ze zijn per versie onveranderlijk), dus de API ziet elke SVG maar een paar keer.
 */
const API_URL = process.env.API_URL ?? "http://localhost:3001";
const SAFE = /^[a-z0-9-]{1,64}$/;

export async function GET(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  // Alleen /v1/assets/plates/<slug>/<versie>.svg; niets anders van de API is zo bereikbaar.
  if (path.length !== 3 || path[0] !== "plates" || !SAFE.test(path[1] ?? "") || !/^\d{1,6}\.svg$/.test(path[2] ?? "")) {
    return new Response("Niet gevonden", { status: 404 });
  }
  // Het IP van de bezoeker gaat mee, zodat de rate limit van de API per bezoeker telt en niet per website-server.
  const ip = request.headers.get("cf-connecting-ip");
  const upstream = await fetch(`${API_URL}/v1/assets/${path.join("/")}`, { cache: "no-store", headers: ip ? { "cf-connecting-ip": ip } : {} });
  if (!upstream.ok) return new Response(null, { status: upstream.status === 404 ? 404 : 502 });
  return new Response(upstream.body, {
    status: 200,
    headers: {
      "content-type": "image/svg+xml; charset=utf-8",
      "cache-control": upstream.headers.get("cache-control") ?? "public, max-age=31536000, immutable",
      "x-content-type-options": "nosniff",
      "content-security-policy": upstream.headers.get("content-security-policy") ?? "default-src 'none'; style-src 'unsafe-inline'; sandbox",
    },
  });
}
