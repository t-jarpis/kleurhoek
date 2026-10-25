import { getBff, noStore, sameOrigin, withCookie } from "@/lib/auth";

const API_URL = process.env.API_URL ?? "http://localhost:3001";

async function withSession(request: Request, work: (accessToken: string) => Promise<Response>) {
  const bff = getBff(request);
  if (!bff) return new Response(null, { status: 404 });
  const { session, setCookies } = await bff.session(request.headers.get("cookie"));
  if (!session) return withCookie(Response.json({ error: "niet ingelogd" }, { status: 401, headers: noStore }), setCookies);
  return withCookie(await work(session.accessToken), setCookies);
}

/** Het eigen account, opgehaald bij de API met het access token uit de sessie. */
export async function GET(request: Request) {
  return withSession(request, async (token) => {
    const res = await fetch(`${API_URL}/v1/me`, { headers: { authorization: `Bearer ${token}`, accept: "application/json" }, cache: "no-store" });
    if (!res.ok) return Response.json({ error: "account niet beschikbaar" }, { status: res.status === 401 ? 401 : 502, headers: noStore });
    return Response.json(await res.json(), { headers: noStore });
  });
}

/** Account verwijderen. Daarna logt de pagina uit (POST /auth/logout). */
export async function DELETE(request: Request) {
  if (!sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  return withSession(request, async (token) => {
    const res = await fetch(`${API_URL}/v1/me`, { method: "DELETE", headers: { authorization: `Bearer ${token}` }, cache: "no-store" });
    return new Response(null, { status: res.ok ? 204 : 502, headers: noStore });
  });
}
