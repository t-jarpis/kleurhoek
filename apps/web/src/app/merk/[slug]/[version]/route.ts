/** Logo van een organisatie via het eigen domein (de API is niet publiek). Per versie onveranderlijk. */
const API_URL = process.env.API_URL ?? "http://localhost:3001";

export async function GET(_: Request, { params }: { params: Promise<{ slug: string; version: string }> }) {
  const { slug, version } = await params;
  if (!/^[a-z0-9-]{1,32}$/.test(slug) || !/^[0-9a-f]{16}$/.test(version)) return new Response("Niet gevonden", { status: 404 });
  const upstream = await fetch(`${API_URL}/v1/organizations/${slug}/logo/${version}`, { cache: "no-store" });
  if (!upstream.ok) return new Response(null, { status: upstream.status === 404 ? 404 : 502 });
  return new Response(upstream.body, {
    headers: {
      "content-type": upstream.headers.get("content-type") ?? "application/octet-stream",
      "cache-control": "public, max-age=31536000, immutable",
      "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'; sandbox",
      "x-content-type-options": "nosniff",
    },
  });
}
