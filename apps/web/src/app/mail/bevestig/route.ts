import { sameOrigin } from "@/lib/same-origin";
import { api, TOKEN } from "@/lib/mail";

/** Aanmelding bevestigen (ADR 0037). De pagina doet dit met JavaScript, zodat linkscanners in mailprogramma's niet bevestigen. */
export async function POST(request: Request) {
  if (!sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  const { t } = (await request.json().catch(() => ({}))) as { t?: string };
  if (!t || !TOKEN.test(t)) return Response.json({ status: "invalid" });
  const res = await api("confirm", { method: "POST", body: { token: t } });
  return Response.json(res?.ok ? await res.json() : { status: "error" }, { headers: { "cache-control": "no-store" } });
}
