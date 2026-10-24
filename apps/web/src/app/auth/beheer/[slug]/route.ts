import { revalidateTag } from "next/cache";
import { getBff, noStore, sameOrigin, withCookie } from "@/lib/auth";

const API_URL = process.env.API_URL ?? "http://localhost:3001";
const SLUG = /^[a-z0-9-]{2,32}$/;

async function withSession(request: Request, work: (accessToken: string) => Promise<Response>) {
  const bff = getBff();
  if (!bff) return new Response(null, { status: 404 });
  const { session, setCookies } = await bff.session(request.headers.get("cookie"));
  if (!session) return withCookie(Response.json({ error: "niet ingelogd" }, { status: 401, headers: noStore }), setCookies);
  return withCookie(await work(session.accessToken), setCookies);
}

/** Aanbod van de eigen organisatie, met keuzes en platen in de taal van de pagina (ADR 0036). */
export async function GET(request: Request, { params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  if (!SLUG.test(slug)) return new Response(null, { status: 404 });
  const language = new URL(request.url).searchParams.get("language") ?? "nl";
  return withSession(request, async (token) => {
    const res = await fetch(`${API_URL}/v1/me/organizations/${slug}?language=${/^[a-z]{2}$/.test(language) ? language : "nl"}`, { headers: { authorization: `Bearer ${token}`, accept: "application/json" }, cache: "no-store" });
    return new Response(res.ok ? await res.text() : null, { status: res.ok ? 200 : res.status === 404 ? 404 : 502, headers: { ...noStore, "content-type": "application/json" } });
  });
}

export async function PUT(request: Request, { params }: { params: Promise<{ slug: string }> }) {
  if (!sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  const { slug } = await params;
  if (!SLUG.test(slug)) return new Response(null, { status: 404 });
  const body = await request.text();
  if (body.length > 100_000) return new Response(null, { status: 413 });
  return withSession(request, async (token) => {
    const res = await fetch(`${API_URL}/v1/me/organizations/${slug}`, { method: "PUT", headers: { authorization: `Bearer ${token}`, "content-type": "application/json" }, body, cache: "no-store" });
    // Direct zichtbaar op de site: de gecachete lijsten van deze organisatie vervallen.
    if (res.ok) revalidateTag(`org:${slug}`, { expire: 0 });
    return new Response(await res.text(), { status: res.status, headers: { ...noStore, "content-type": "application/json" } });
  });
}
