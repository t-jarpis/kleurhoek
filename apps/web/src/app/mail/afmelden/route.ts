import { NextResponse } from "next/server";
import { LIVE_MARKETS } from "@/lib/markets";
import { api, TOKEN } from "@/lib/mail";

/**
 * Afmelden (ADR 0037). POST: de één-klik-afmelding van mailprogramma's (RFC 8058, header List-Unsubscribe-Post)
 * en de knop op de voorkeurenpagina. Het token in de link is genoeg; er is geen sessie. GET (iemand opent de link)
 * wijzigt niets en gaat naar de voorkeurenpagina, zodat linkscanners niemand afmelden.
 */
export async function POST(request: Request) {
  const url = new URL(request.url);
  let t = url.searchParams.get("t") ?? "";
  if (!t && request.headers.get("content-type")?.includes("application/json")) t = ((await request.json().catch(() => ({}))) as { t?: string }).t ?? "";
  if (!TOKEN.test(t)) return Response.json({ status: "invalid" }, { status: 400 });
  const res = await api("unsubscribe", { method: "POST", body: { t } });
  return Response.json({ status: res?.ok ? "removed" : "error" }, { status: res?.ok ? 200 : 502, headers: { "cache-control": "no-store" } });
}

export function GET(request: Request) {
  const url = new URL(request.url);
  const t = url.searchParams.get("t") ?? "";
  const target = new URL(`/${LIVE_MARKETS[0] ?? "nl-nl"}/mail`, url);
  if (TOKEN.test(t)) { target.searchParams.set("t", t); target.searchParams.set("afmelden", "1"); }
  return NextResponse.redirect(target, 303);
}
