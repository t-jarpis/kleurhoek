import { getBff, noStore, withCookie } from "@/lib/auth";

/**
 * Wie is er ingelogd? Pagina's blijven cachebaar voor iedereen; de accountknop vraagt dit los op.
 * Geeft alleen een voornaam terug, nooit tokens.
 */
export async function GET(request: Request) {
  const bff = getBff();
  if (!bff) return Response.json({ enabled: false, user: null }, { headers: noStore });
  const { session, setCookie } = await bff.session(request.headers.get("cookie"));
  const user = session ? { name: session.name?.split(" ")[0] ?? null } : null;
  return withCookie(Response.json({ enabled: true, user }, { headers: noStore }), setCookie);
}
