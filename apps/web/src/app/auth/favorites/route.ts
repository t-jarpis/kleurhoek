import { getBff, noStore, sameOrigin, withCookie } from "@/lib/auth";

const API_URL = process.env.API_URL ?? "http://localhost:3001";

/** Favorieten van het ingelogde account (ADR 0039). Niet ingelogd: 401, dan bewaart de site ze alleen op het apparaat. */
async function withSession(request: Request, work: (token: string) => Promise<Response>) {
  const bff = getBff(request);
  if (!bff) return new Response(null, { status: 401, headers: noStore });
  const { session, setCookies } = await bff.session(request.headers.get("cookie"));
  if (!session) return withCookie(new Response(null, { status: 401, headers: noStore }), setCookies);
  return withCookie(await work(session.accessToken), setCookies);
}
const pass = async (res: Response) => new Response(res.ok ? await res.text() : null, { status: res.ok ? 200 : res.status === 401 ? 401 : 502, headers: { ...noStore, "content-type": "application/json" } });

export async function GET(request: Request) {
  return withSession(request, async (token) => pass(await fetch(`${API_URL}/v1/me/favorites`, { headers: { authorization: `Bearer ${token}` }, cache: "no-store" })));
}

/** De favorieten van dit apparaat samenvoegen met het account (na inloggen). */
export async function POST(request: Request) {
  if (!sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  const body = await request.text();
  if (body.length > 40_000) return new Response(null, { status: 413 });
  return withSession(request, async (token) => pass(await fetch(`${API_URL}/v1/me/favorites`, { method: "POST", headers: { authorization: `Bearer ${token}`, "content-type": "application/json" }, body, cache: "no-store" })));
}
