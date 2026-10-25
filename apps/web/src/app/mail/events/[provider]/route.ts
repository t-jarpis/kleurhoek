/**
 * Meldingen over bezorging van de mailrelay (ADR 0038): afgeleverd, bounce, spamklacht. De API heeft geen publieke
 * ingang, dus de website geeft ze door. De sleutel in het adres controleert de API; hier alleen vorm en grootte.
 */
const API_URL = process.env.API_URL ?? "http://localhost:3001";
const PROVIDER = /^(brevo|scaleway|generic)$/;
const KEY = /^[A-Za-z0-9_-]{32}$/;

export async function POST(request: Request, { params }: { params: Promise<{ provider: string }> }) {
  const { provider } = await params;
  const key = new URL(request.url).searchParams.get("key") ?? "";
  if (!PROVIDER.test(provider) || !KEY.test(key)) return new Response(null, { status: 404 });
  const body = await request.text();
  if (body.length > 1_000_000) return new Response(null, { status: 413 });
  // SNS (Scaleway) stuurt JSON als text/plain; de API leest beide.
  const type = request.headers.get("content-type")?.includes("json") ? "application/json" : "text/plain";
  const res = await fetch(`${API_URL}/v1/mail/events/${provider}?key=${encodeURIComponent(key)}`, { method: "POST", headers: { "content-type": type }, body, cache: "no-store" }).catch(() => null);
  if (!res) return new Response(null, { status: 502 });
  return new Response(await res.text(), { status: res.status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
}
