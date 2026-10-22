import "server-only";
import { createHash, createHmac } from "node:crypto";

/**
 * Eén event doorgeven aan de API, zonder IP-adres of user agent op te slaan: alleen land, soort
 * apparaat en een bezoekershash met een dagelijks wisselend zout (ADR 0002). Gebruikt door /e en /ga.
 */
const API_URL = process.env.API_URL ?? "http://localhost:3001";
const INGEST_KEY = process.env.INGEST_KEY ?? "dev-only-ingest-key-change-me-0000000000";
const SALT_SECRET = process.env.ANALYTICS_SALT_SECRET ?? "dev-only-salt";

export function device(ua: string): "mobile" | "tablet" | "desktop" | "other" {
  if (/ipad|tablet/i.test(ua)) return "tablet";
  if (/mobi|android|iphone/i.test(ua)) return "mobile";
  if (/mozilla|chrome|safari|firefox/i.test(ua)) return "desktop";
  return "other";
}

/** `nl-nl` of `nl-NL` naar `nl-NL`; null als het geen markt is. */
export function normalizeMarket(value: unknown): string | null {
  return typeof value === "string" && /^[a-z]{2}-[a-z]{2}$/i.test(value) ? `${value.slice(0, 2).toLowerCase()}-${value.slice(3).toUpperCase()}` : null;
}

export async function ingest(req: Request, event: { type: string; market: string; plate?: string | undefined; product?: string | undefined }) {
  const ua = req.headers.get("user-agent") ?? "";
  const ip = req.headers.get("cf-connecting-ip") ?? req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "";
  const country = (req.headers.get("cf-ipcountry") ?? process.env.DEV_COUNTRY ?? "").toUpperCase();
  const day = new Date().toISOString().slice(0, 10);
  const salt = createHmac("sha256", SALT_SECRET).update(day).digest();
  const visitorHash = createHash("sha256").update(salt).update(ip).update(ua).digest("base64url").slice(0, 32);
  const body = {
    type: event.type, market: event.market, device: device(ua), visitorHash,
    ...(event.plate ? { plate: event.plate } : {}), ...(event.product ? { product: event.product } : {}),
    ...(/^[A-Z]{2}$/.test(country) ? { country } : {}),
  };
  try {
    await fetch(`${API_URL}/v1/internal/events`, { method: "POST", headers: { "content-type": "application/json", "x-ingest-key": INGEST_KEY }, body: JSON.stringify([body]), signal: AbortSignal.timeout(2000) });
  } catch { /* tellen mag nooit de site breken */ }
}
