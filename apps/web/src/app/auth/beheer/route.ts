import { getBff, noStore, withCookie } from "@/lib/auth";

const API_URL = process.env.API_URL ?? "http://localhost:3001";

/** De organisaties die het ingelogde account mag beheren (ADR 0036). Niet ingelogd: lege lijst. */
export async function GET(request: Request) {
  const bff = getBff();
  if (!bff) return Response.json({ organizations: [] }, { headers: noStore });
  const { session, setCookies } = await bff.session(request.headers.get("cookie"));
  if (!session) return withCookie(Response.json({ organizations: [] }, { headers: noStore }), setCookies);
  const res = await fetch(`${API_URL}/v1/me/organizations`, { headers: { authorization: `Bearer ${session.accessToken}`, accept: "application/json" }, cache: "no-store" });
  return withCookie(res.ok ? Response.json(await res.json(), { headers: noStore }) : Response.json({ organizations: [] }, { headers: noStore }), setCookies);
}
