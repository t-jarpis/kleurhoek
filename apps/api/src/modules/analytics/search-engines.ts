// Ophalen van zoekcijfers bij Google Search Console en Bing Webmaster Tools (ADR 0041). Alleen lezen; geen
// bibliotheken van de zoekmachines, gewoon hun HTTP-API's. `fetch` is in te voegen, zodat dit goed te testen is.
import { createSign } from "node:crypto";

export type Engine = "google" | "bing";
export type Kind = "total" | "query" | "page";
export interface SearchRow { day: string; engine: Engine; site: string; kind: Kind; key: string; clicks: number; impressions: number; position: number | null }
export type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

const TIMEOUT = 30_000;
const b64url = (s: string | Buffer) => Buffer.from(s).toString("base64url");
/** Adres zonder schema en zonder slash aan het eind (behalve de wortel). */
export const pageKey = (url: string) => url.replace(/^https?:\/\//, "").replace(/(.)\/$/, "$1");

// ---------- Google ----------

export interface GoogleKey { client_email: string; private_key: string }

/** Leest de sleutel van het serviceaccount (JSON, eventueel base64). Ongeldig → null. */
export function parseGoogleKey(raw: string | undefined): GoogleKey | null {
  if (!raw) return null;
  for (const text of [raw, Buffer.from(raw, "base64").toString("utf8")]) {
    try {
      const k = JSON.parse(text) as Partial<GoogleKey>;
      if (typeof k.client_email === "string" && typeof k.private_key === "string" && k.private_key.includes("PRIVATE KEY")) return { client_email: k.client_email, private_key: k.private_key };
    } catch { /* volgende vorm proberen */ }
  }
  return null;
}

/** Ondertekende JWT voor de OAuth-tokenruil van een serviceaccount (alleen-lezen Search Console). */
export function googleAssertion(key: GoogleKey, now = Date.now()): string {
  const iat = Math.floor(now / 1000);
  const head = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const body = b64url(JSON.stringify({
    iss: key.client_email, scope: "https://www.googleapis.com/auth/webmasters.readonly",
    aud: "https://oauth2.googleapis.com/token", iat, exp: iat + 3600,
  }));
  const sig = createSign("RSA-SHA256").update(`${head}.${body}`).sign(key.private_key);
  return `${head}.${body}.${b64url(sig)}`;
}

async function googleToken(key: GoogleKey, f: Fetch): Promise<string> {
  const res = await f("https://oauth2.googleapis.com/token", {
    method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer", assertion: googleAssertion(key) }).toString(),
    signal: AbortSignal.timeout(TIMEOUT),
  });
  const json = (await res.json().catch(() => ({}))) as { access_token?: string; error_description?: string; error?: string };
  if (!res.ok || !json.access_token) throw new Error(`Google-sleutel geweigerd: ${json.error_description ?? json.error ?? res.status}`);
  return json.access_token;
}

interface GoogleRow { keys: string[]; clicks: number; impressions: number; position: number }

/**
 * Cijfers van één domein-property (sc-domain:kleurhoek.nl) tussen twee dagen: totaal per dag, per zoekterm en
 * per pagina. Per soort hooguit `cap` rijen (in pagina's van 25.000).
 */
export async function googleRows(key: GoogleKey, domain: string, from: string, to: string, f: Fetch, cap = 100_000): Promise<SearchRow[]> {
  const token = await googleToken(key, f);
  const site = `sc-domain:${domain}`;
  const out: SearchRow[] = [];
  for (const [kind, dims] of [["total", ["date"]], ["query", ["date", "query"]], ["page", ["date", "page"]]] as const) {
    for (let start = 0; start < cap; start += 25_000) {
      const res = await f(`https://searchconsole.googleapis.com/webmasters/v3/sites/${encodeURIComponent(site)}/searchAnalytics/query`, {
        method: "POST", headers: { authorization: `Bearer ${token}`, "content-type": "application/json" },
        body: JSON.stringify({ startDate: from, endDate: to, dimensions: dims, rowLimit: 25_000, startRow: start, dataState: "final" }),
        signal: AbortSignal.timeout(TIMEOUT),
      });
      if (res.status === 403) throw new Error(`Geen toegang tot ${site} in Search Console: voeg het serviceaccount ${key.client_email} toe als gebruiker`);
      if (!res.ok) throw new Error(`Search Console ${res.status}`);
      const rows = ((await res.json()) as { rows?: GoogleRow[] }).rows ?? [];
      for (const r of rows) {
        out.push({
          day: r.keys[0]!, engine: "google", site: domain, kind,
          key: kind === "total" ? "" : kind === "page" ? pageKey(r.keys[1]!) : r.keys[1]!.slice(0, 300),
          clicks: Math.round(r.clicks), impressions: Math.round(r.impressions), position: Number.isFinite(r.position) ? r.position : null,
        });
      }
      if (rows.length < 25_000) break;
    }
  }
  return out;
}

// ---------- Bing ----------

/** Bing geeft datums als "/Date(1729814400000-0700)/"; wij willen de kalenderdag (UTC). */
export function bingDay(value: string): string | null {
  const m = /\/Date\((-?\d+)([+-]\d{4})?\)\//.exec(value);
  return m ? new Date(Number(m[1])).toISOString().slice(0, 10) : null;
}

interface BingRow { Date: string; Clicks: number; Impressions: number; Query?: string; AvgImpressionPosition?: number; AvgClickPosition?: number }

/**
 * Cijfers van één site in Bing Webmaster Tools (https://www.<domein>/). Bing geeft totalen per dag en zoektermen
 * en pagina's per week (de datum is dan het begin van die periode). Alleen rijen vanaf `from`.
 */
export async function bingRows(apiKey: string, domain: string, from: string, f: Fetch): Promise<SearchRow[]> {
  const siteUrl = `https://www.${domain}/`;
  const call = async (method: string) => {
    const res = await f(`https://ssl.bing.com/webmaster/api.svc/json/${method}?siteUrl=${encodeURIComponent(siteUrl)}&apikey=${encodeURIComponent(apiKey)}`, { signal: AbortSignal.timeout(TIMEOUT) });
    if (res.status === 401 || res.status === 403) throw new Error("Bing-sleutel geweigerd");
    if (!res.ok) throw new Error(`Bing ${method} ${res.status}${res.status === 400 ? ` (staat ${siteUrl} in Bing Webmaster Tools?)` : ""}`);
    return ((await res.json()) as { d?: BingRow[] }).d ?? [];
  };
  const out: SearchRow[] = [];
  const push = (kind: Kind, r: BingRow, key: string) => {
    const day = bingDay(r.Date);
    if (!day || day < from) return;
    const pos = r.AvgImpressionPosition && r.AvgImpressionPosition > 0 ? r.AvgImpressionPosition : null;
    out.push({ day, engine: "bing", site: domain, kind, key, clicks: r.Clicks ?? 0, impressions: r.Impressions ?? 0, position: pos });
  };
  for (const r of await call("GetRankAndTrafficStats")) push("total", r, "");
  for (const r of await call("GetQueryStats")) if (r.Query) push("query", r, r.Query.slice(0, 300));
  for (const r of await call("GetPageStats")) if (r.Query) push("page", r, pageKey(r.Query));
  return merge(out);
}

/** Dubbele rijen (zelfde dag, soort en sleutel) optellen; positie gewogen naar vertoningen. */
export function merge(rows: SearchRow[]): SearchRow[] {
  const m = new Map<string, SearchRow & { w: number }>();
  for (const r of rows) {
    const k = `${r.day}|${r.engine}|${r.site}|${r.kind}|${r.key}`;
    const cur = m.get(k);
    if (!cur) { m.set(k, { ...r, w: r.position !== null ? r.position * r.impressions : 0 }); continue; }
    cur.clicks += r.clicks; cur.impressions += r.impressions;
    if (r.position !== null) cur.w += r.position * r.impressions;
    cur.position = cur.impressions ? cur.w / cur.impressions : cur.position;
  }
  return [...m.values()].map(({ w: _w, ...r }) => r);
}
