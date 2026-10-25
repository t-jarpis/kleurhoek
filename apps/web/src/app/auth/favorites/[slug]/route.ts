import { getBff, noStore, sameOrigin, withCookie } from "@/lib/auth";

const API_URL = process.env.API_URL ?? "http://localhost:3001";
const SLUG = /^[a-z0-9-]{1,64}$/;

async function change(request: Request, slug: string, method: "PUT" | "DELETE") {
  if (!sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  if (!SLUG.test(slug)) return new Response(null, { status: 404 });
  const bff = getBff();
  if (!bff) return new Response(null, { status: 401, headers: noStore });
  const { session, setCookies } = await bff.session(request.headers.get("cookie"));
  if (!session) return withCookie(new Response(null, { status: 401, headers: noStore }), setCookies);
  const res = await fetch(`${API_URL}/v1/me/favorites/${slug}`, { method, headers: { authorization: `Bearer ${session.accessToken}` }, cache: "no-store" });
  return withCookie(new Response(res.ok ? await res.text() : null, { status: res.ok ? 200 : 502, headers: { ...noStore, "content-type": "application/json" } }), setCookies);
}

/** Eén favoriet toevoegen of weghalen (ADR 0039). */
export async function PUT(request: Request, { params }: { params: Promise<{ slug: string }> }) { return change(request, (await params).slug, "PUT"); }
export async function DELETE(request: Request, { params }: { params: Promise<{ slug: string }> }) { return change(request, (await params).slug, "DELETE"); }
