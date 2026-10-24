import { timingSafeEqual } from "node:crypto";
import { BlockList, isIP } from "node:net";

/**
 * Afgeschermde website (ADR 0015): staat de IP-lijst in het admin panel aan, dan laat de proxy alleen
 * bezoekers door van wie het IP-adres (van Cloudflare, `cf-connecting-ip`) in de lijst valt. De lijst
 * wordt elke 30 seconden opgehaald; bij een storing blijft de laatst bekende lijst gelden. Is er nog
 * nooit een lijst opgehaald, dan gaat de deur dicht (503), behalve /healthz.
 */
const API_URL = process.env.API_URL ?? "http://localhost:3001";
const INGEST_KEY = process.env.INGEST_KEY ?? "";
const TTL_MS = 30_000;

interface Policy { enabled: boolean; list: BlockList }
let cached: { policy: Policy; at: number } | null = null;
let inflight: Promise<void> | null = null;

export function buildPolicy(enabled: boolean, cidrs: string[]): Policy {
  const list = new BlockList();
  for (const c of cidrs) {
    const [addr = "", bits = ""] = c.split("/");
    const family = isIP(addr);
    if (!family) continue;
    try { list.addSubnet(addr, Number(bits), family === 4 ? "ipv4" : "ipv6"); } catch { /* ongeldig blok overslaan */ }
  }
  return { enabled, list };
}

export function ipAllowed(policy: Policy, ip: string | null): boolean {
  if (!policy.enabled) return true;
  if (!ip) return false;
  const family = isIP(ip);
  if (!family) return false;
  return policy.list.check(ip, family === 4 ? "ipv4" : "ipv6");
}

async function refresh() {
  const res = await fetch(`${API_URL}/v1/internal/site-access`, { headers: { "x-ingest-key": INGEST_KEY }, cache: "no-store", signal: AbortSignal.timeout(2000) });
  if (!res.ok) throw new Error(`site-access ${res.status}`);
  const body = (await res.json()) as { enabled: boolean; cidrs: string[] };
  cached = { policy: buildPolicy(body.enabled, body.cidrs), at: Date.now() };
}

/** De huidige lijst, of null als die nog nooit opgehaald kon worden. */
export async function currentPolicy(): Promise<Policy | null> {
  if (!cached || Date.now() - cached.at > TTL_MS) {
    inflight ??= refresh().catch(() => undefined).finally(() => { inflight = null; });
    if (!cached) await inflight;
  }
  return cached?.policy ?? null;
}

/**
 * De automatische rooktest na een deploy (GitHub Actions) draait vanaf wisselende IP-adressen. Met de
 * geheime controlesleutel in `x-kh-check` mag hij toch langs de IP-lijst. Zonder sleutel (lokaal, of
 * nog niet ingesteld) geeft dit altijd false.
 */
export const CHECK_HEADER = "x-kh-check";
export function checkKeyValid(given: string | null, expected = process.env.SITE_CHECK_KEY ?? ""): boolean {
  if (expected.length < 32 || !given) return false;
  const a = Buffer.from(given), b = Buffer.from(expected);
  return a.length === b.length && timingSafeEqual(a, b);
}

export function blockedPage(ip: string | null): Response {
  const html = `<!doctype html><html lang="nl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Afgeschermd</title><body style="font-family:system-ui,sans-serif;max-width:32rem;margin:15vh auto;padding:0 1rem;line-height:1.5"><h1 style="font-size:1.25rem">Deze omgeving is afgeschermd</h1><p>Alleen bekende IP-adressen hebben toegang. Jouw adres: <code>${ip ? ip.replace(/[^0-9a-fA-F:.]/g, "") : "onbekend"}</code></p></body></html>`;
  return new Response(html, { status: 403, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex" } });
}
