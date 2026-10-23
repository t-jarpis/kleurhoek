/** Logo van een organisatie, via de API (die alleen intern bereikbaar is). Zelfde URL-vorm als website en admin. */
const API_URL = process.env.API_URL ?? "http://localhost:3001";
const SLUG = /^[a-z0-9-]{1,32}$/;
const VERSION = /^[0-9a-f]{16}$/;

export async function GET(_req: Request, { params }: { params: Promise<{ slug: string; version: string }> }) {
  const { slug, version } = await params;
  if (!SLUG.test(slug) || !VERSION.test(version)) return new Response(null, { status: 404 });
  const res = await fetch(`${API_URL}/v1/organizations/${slug}/logo/${version}`, { cache: "no-store", signal: AbortSignal.timeout(10_000) });
  if (!res.ok) return new Response(null, { status: res.status === 404 ? 404 : 502 });
  return new Response(res.body, {
    headers: {
      "content-type": res.headers.get("content-type") ?? "application/octet-stream",
      "cache-control": "public, max-age=31536000, immutable",
      "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'; sandbox",
      "x-content-type-options": "nosniff",
    },
  });
}
