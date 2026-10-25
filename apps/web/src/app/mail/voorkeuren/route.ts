import { sameOrigin } from "@/lib/same-origin";
import { api, TOKEN } from "@/lib/mail";

const noStore = { "cache-control": "private, no-store" };

/** Voorkeuren bij een link uit een mail (ADR 0037). */
export async function GET(request: Request) {
  const t = new URL(request.url).searchParams.get("t") ?? "";
  if (!TOKEN.test(t)) return Response.json({ error: "ongeldig" }, { status: 404, headers: noStore });
  const res = await api(`preferences?t=${encodeURIComponent(t)}`);
  if (!res) return Response.json({ error: "storing" }, { status: 502, headers: noStore });
  return new Response(await res.text(), { status: res.status, headers: { ...noStore, "content-type": "application/json" } });
}

export async function PUT(request: Request) {
  if (!sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  const body = (await request.json().catch(() => null)) as { t?: string; topics?: string[] } | null;
  if (!body?.t || !TOKEN.test(body.t) || !Array.isArray(body.topics)) return Response.json({ error: "ongeldig" }, { status: 400, headers: noStore });
  const res = await api("preferences", { method: "PUT", body: { t: body.t, topics: body.topics.slice(0, 3) } });
  if (!res) return Response.json({ error: "storing" }, { status: 502, headers: noStore });
  return new Response(await res.text(), { status: res.status, headers: { ...noStore, "content-type": "application/json" } });
}
