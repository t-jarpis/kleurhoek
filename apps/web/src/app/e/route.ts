import type { NextRequest } from "next/server";
import { ingest, normalizeMarket } from "@/lib/ingest";

/**
 * Analytics-ingang (zelfde contract als de Cloudflare Worker). Het IP-adres en de user agent
 * worden nergens opgeslagen; zie lib/ingest.ts. Doorkliks naar producten tellen we in /ga.
 */
const TYPES = new Set(["page_view", "plate_view", "plate_colored", "plate_completed", "pdf_download", "print", "materials_view"]);

export async function POST(req: NextRequest) {
  let body: { type?: unknown; market?: unknown; plate?: unknown };
  try { body = JSON.parse(await req.text()); } catch { return new Response(null, { status: 400 }); }
  const market = normalizeMarket(body.market);
  if (typeof body.type !== "string" || !TYPES.has(body.type) || !market) return new Response(null, { status: 400 });
  const plate = typeof body.plate === "string" && /^[a-z0-9-]{1,64}$/.test(body.plate) ? body.plate : undefined;
  await ingest(req, { type: body.type, market, plate });
  return new Response(null, { status: 204, headers: { "cache-control": "no-store" } });
}
