import "server-only";
import { createHash, createHmac } from "node:crypto";
import { isBot } from "./bots";

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

/** Bezoekershash met het zout van vandaag (UTC); null voor bots. Het IP-adres en de browser zelf gaan nergens heen. */
export function visitorHash(req: Request): string | null {
  const ua = req.headers.get("user-agent") ?? "";
  if (isBot(ua)) return null;
  const ip = req.headers.get("cf-connecting-ip") ?? req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "";
  const day = new Date().toISOString().slice(0, 10);
  const salt = createHmac("sha256", SALT_SECRET).update(day).digest();
  return createHash("sha256").update(salt).update(ip).update(ua).digest("base64url").slice(0, 32);
}

export async function ingest(req: Request, event: { type: string; market: string; plate?: string | undefined; product?: string | undefined; page?: string | undefined; entry?: string | undefined; ref?: string | undefined }) {
  const ua = req.headers.get("user-agent") ?? "";
  const hash = visitorHash(req);
  if (!hash) return;
  const country = (req.headers.get("cf-ipcountry") ?? process.env.DEV_COUNTRY ?? "").toUpperCase();
  const body = {
    type: event.type, market: event.market, device: device(ua), visitorHash: hash,
    ...(event.plate ? { plate: event.plate } : {}), ...(event.product ? { product: event.product } : {}),
    ...(event.page ? { page: event.page } : {}),
    ...(event.entry ? { entry: event.entry, referrer: event.ref ?? "" } : {}),
    // Organisatie van de site (de proxy zet x-kh-org, ADR 0017).
    ...(/^[a-z0-9-]{1,32}$/.test(req.headers.get("x-kh-org") ?? "") ? { org: req.headers.get("x-kh-org")! } : {}),
    ...(/^[A-Z]{2}$/.test(country) ? { country } : {}),
  };
  await send(JSON.stringify([body]), event.type);
}

/**
 * Naar de API, met twee nieuwe pogingen als dat mislukt (ADR 0082): bij een hapering van de API (503, time-out)
 * ging een telling anders stil verloren. Lukt het na drie keer niet, dan één regel in de log, zonder
 * bezoekersgegevens. Een 4xx is een fout in het event zelf: niet opnieuw proberen.
 */
export async function send(json: string, type: string, waits = [300, 1200], path = "/v1/internal/events"): Promise<boolean> {
  let last = "";
  for (let attempt = 0; attempt <= waits.length; attempt++) {
    if (attempt) await new Promise((r) => setTimeout(r, waits[attempt - 1]));
    try {
      const res = await fetch(`${API_URL}${path}`, { method: "POST", headers: { "content-type": "application/json", "x-ingest-key": INGEST_KEY }, body: json, signal: AbortSignal.timeout(3000) });
      if (res.ok) return true;
      last = `HTTP ${res.status}`;
      if (res.status >= 400 && res.status < 500 && res.status !== 429) break;
    } catch (e) { last = (e as Error)?.name ?? "fout"; } // tellen mag nooit de site breken
  }
  console.warn(`Telling ${type} niet doorgegeven aan de API (${last})`);
  return false;
}

/** Zoekwoord zonder resultaat of aanvraag van een plaat (ADR 0084). Zelfde hash en retries als events. */
export async function wish(req: Request, w: { term: string; market: string; kind: "miss" | "request" }): Promise<void> {
  const hash = visitorHash(req);
  if (!hash) return;
  await send(JSON.stringify({ ...w, visitorHash: hash }), `zoekwoord (${w.kind})`, [300, 1200], "/v1/internal/wishes");
}
