import { createHash, createHmac } from "node:crypto";
import type { NextRequest } from "next/server";

/**
 * Analytics-ingang (zelfde contract als de Cloudflare Worker): voegt het land toe, maakt een
 * bezoekershash met een dagelijks wisselend zout en stuurt door naar de API. Het IP-adres en de
 * user agent worden nergens opgeslagen.
 */
const API_URL = process.env.API_URL ?? "http://localhost:3001";
const INGEST_KEY = process.env.INGEST_KEY ?? "dev-only-ingest-key-change-me-0000000000";
const SALT_SECRET = process.env.ANALYTICS_SALT_SECRET ?? "dev-only-salt";
const TYPES = new Set(["page_view", "plate_view", "plate_colored", "plate_completed", "pdf_download", "print"]);

function device(ua: string): "mobile" | "tablet" | "desktop" | "other" {
  if (/ipad|tablet/i.test(ua)) return "tablet";
  if (/mobi|android|iphone/i.test(ua)) return "mobile";
  if (/mozilla|chrome|safari|firefox/i.test(ua)) return "desktop";
  return "other";
}

export async function POST(req: NextRequest) {
  let body: { type?: unknown; market?: unknown; plate?: unknown };
  try { body = JSON.parse(await req.text()); } catch { return new Response(null, { status: 400 }); }
  const market = typeof body.market === "string" && /^[a-z]{2}-[a-z]{2}$/i.test(body.market) ? `${body.market.slice(0, 2).toLowerCase()}-${body.market.slice(3).toUpperCase()}` : null;
  if (typeof body.type !== "string" || !TYPES.has(body.type) || !market) return new Response(null, { status: 400 });
  const plate = typeof body.plate === "string" && /^[a-z0-9-]{1,64}$/.test(body.plate) ? body.plate : undefined;

  const ua = req.headers.get("user-agent") ?? "";
  const ip = req.headers.get("cf-connecting-ip") ?? req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "";
  const country = (req.headers.get("cf-ipcountry") ?? process.env.DEV_COUNTRY ?? "").toUpperCase();
  const day = new Date().toISOString().slice(0, 10);
  const salt = createHmac("sha256", SALT_SECRET).update(day).digest();
  const visitorHash = createHash("sha256").update(salt).update(ip).update(ua).digest("base64url").slice(0, 32);

  const event = { type: body.type, market, device: device(ua), visitorHash, ...(plate ? { plate } : {}), ...(/^[A-Z]{2}$/.test(country) ? { country } : {}) };
  try {
    await fetch(`${API_URL}/v1/internal/events`, { method: "POST", headers: { "content-type": "application/json", "x-ingest-key": INGEST_KEY }, body: JSON.stringify([event]) });
  } catch { /* tellen mag nooit de site breken */ }
  return new Response(null, { status: 204, headers: { "cache-control": "no-store" } });
}
