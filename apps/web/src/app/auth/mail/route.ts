import { getBff, noStore, sameOrigin, withCookie } from "@/lib/auth";

const API_URL = process.env.API_URL ?? "http://localhost:3001";

async function withSession(request: Request, work: (token: string) => Promise<Response>) {
  const bff = getBff(request);
  if (!bff) return new Response(null, { status: 404 });
  const { session, setCookies } = await bff.session(request.headers.get("cookie"));
  if (!session) return withCookie(Response.json({ error: "niet ingelogd" }, { status: 401, headers: noStore }), setCookies);
  return withCookie(await work(session.accessToken), setCookies);
}

/** Mail vanuit het eigen account (ADR 0037): meteen actief, het adres is al bevestigd bij het inloggen. */
export async function GET(request: Request) {
  return withSession(request, async (token) => {
    const res = await fetch(`${API_URL}/v1/me/mail`, { headers: { authorization: `Bearer ${token}` }, cache: "no-store" });
    return new Response(res.ok ? await res.text() : null, { status: res.ok ? 200 : 502, headers: { ...noStore, "content-type": "application/json" } });
  });
}

export async function PUT(request: Request) {
  if (!sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  const body = (await request.json().catch(() => null)) as { topics?: unknown; market?: unknown } | null;
  if (!body || !Array.isArray(body.topics) || typeof body.market !== "string") return new Response(null, { status: 400 });
  return withSession(request, async (token) => {
    const res = await fetch(`${API_URL}/v1/me/mail`, { method: "PUT", headers: { authorization: `Bearer ${token}`, "content-type": "application/json" }, body: JSON.stringify({ topics: body.topics, market: body.market }), cache: "no-store" });
    return new Response(await res.text(), { status: res.status, headers: { ...noStore, "content-type": "application/json" } });
  });
}
