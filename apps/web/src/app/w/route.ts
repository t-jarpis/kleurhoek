import type { NextRequest } from "next/server";
import { normalizeMarket, wish } from "@/lib/ingest";

/**
 * Gezocht (ADR 0084): een zoekwoord zonder resultaat (miss) of een aanvraag voor een plaat (request). Alleen het
 * woord en de markt; de API maakt het woord gelijk en weigert e-mailadressen, webadressen en nummers.
 */
export async function POST(req: NextRequest) {
  let body: { term?: unknown; market?: unknown; kind?: unknown };
  try { body = JSON.parse(await req.text()); } catch { return new Response(null, { status: 400 }); }
  const market = normalizeMarket(body.market);
  if (typeof body.term !== "string" || body.term.length > 80 || (body.kind !== "miss" && body.kind !== "request") || !market) return new Response(null, { status: 400 });
  await wish(req, { term: body.term, market, kind: body.kind });
  return new Response(null, { status: 204, headers: { "cache-control": "no-store" } });
}
