import { createHash } from "node:crypto";
import { lookup } from "node:dns/promises";
import { isIP } from "node:net";

/**
 * Controle van een bron bij de maker (ADR 0024). We halen alleen de HTML-pagina op om te zien of hij er
 * nog is en of hij veranderd is. We bewaren een vingerafdruk en de paginatitel, nooit de inhoud of
 * afbeeldingen. We volgen robots.txt en praten nooit met adressen in een privénetwerk (SSRF).
 */
export const USER_AGENT = "KleurhoekLinkCheck/1.0 (+https://www.kleurhoek.nl/nl-nl/disclaimer)";
const MAX_BYTES = 1_500_000;
const MAX_REDIRECTS = 4;
const TIMEOUT_MS = 10_000;

export interface CheckResult {
  outcome: "ok" | "gone" | "error" | "blocked";
  httpStatus: number | null;
  finalUrl: string | null;
  robotsAllowed: boolean | null;
  contentHash: string | null;
  pageTitle: string | null;
  note: string | null;
}

export interface CheckDeps {
  fetch: typeof fetch;
  resolve: (host: string) => Promise<string[]>;
}

export const defaultDeps: CheckDeps = {
  fetch: (input, init) => fetch(input, init),
  resolve: async (host) => (await lookup(host, { all: true })).map((a) => a.address),
};

/** Geen loopback, privé-, link-local-, CGNAT- of multicastadressen. */
export function isPublicAddress(ip: string): boolean {
  const v = isIP(ip);
  if (v === 4) {
    const [a, b] = ip.split(".").map(Number) as [number, number];
    if (a === 0 || a === 10 || a === 127 || a >= 224) return false;
    if (a === 169 && b === 254) return false;
    if (a === 172 && b >= 16 && b <= 31) return false;
    if (a === 192 && b === 168) return false;
    if (a === 100 && b >= 64 && b <= 127) return false;
    if (a === 192 && b === 0) return false;
    if (a === 198 && (b === 18 || b === 19)) return false;
    return true;
  }
  if (v === 6) {
    const x = ip.toLowerCase();
    if (x === "::" || x === "::1") return false;
    if (x.startsWith("::ffff:")) return isPublicAddress(x.slice(7));
    if (/^f[cd]/.test(x) || /^fe[89ab]/.test(x) || x.startsWith("ff")) return false;
    return true;
  }
  return false;
}

/** Een bron moet https zijn, op een gewone hostnaam (geen IP-adres, geen poort, geen inlog in de URL). */
export function checkSourceUrl(raw: string): { url: URL } | { problem: string } {
  let u: URL;
  try { u = new URL(raw.trim()); } catch { return { problem: "Dit is geen geldig adres" }; }
  if (u.protocol !== "https:") return { problem: "Alleen https-adressen" };
  if (u.username || u.password) return { problem: "Geen inloggegevens in het adres" };
  if (u.port) return { problem: "Geen poortnummer in het adres" };
  if (isIP(u.hostname.replace(/^\[|\]$/g, "")) || !/^[a-z0-9.-]+\.[a-z]{2,}$/i.test(u.hostname)) return { problem: "Gebruik de domeinnaam van de maker" };
  u.hash = "";
  return { url: u };
}

/** Ruwe vergelijking van het "eigen" domein: www.efteling.com en efteling.com horen bij elkaar. */
export function siteOf(host: string): string {
  const parts = host.toLowerCase().replace(/\.$/, "").split(".");
  const twoLevel = /^(co|com|org|net|ac|gov)\.[a-z]{2}$/.test(parts.slice(-2).join("."));
  return parts.slice(twoLevel ? -3 : -2).join(".");
}

/** robots.txt: de regels voor onze user agent, anders die voor *. Langste overeenkomst wint (Allow bij gelijk). */
export function robotsAllows(robots: string, path: string, agent = "KleurhoekLinkCheck"): boolean {
  const groups: { agents: string[]; rules: { allow: boolean; path: string }[] }[] = [];
  let current: (typeof groups)[number] | null = null;
  let lastWasAgent = false;
  for (const line of robots.split(/\r?\n/)) {
    const m = /^\s*([A-Za-z-]+)\s*:\s*(.*?)\s*(?:#.*)?$/.exec(line);
    if (!m) continue;
    const key = m[1]!.toLowerCase(), value = m[2]!;
    if (key === "user-agent") {
      if (!current || !lastWasAgent) { current = { agents: [], rules: [] }; groups.push(current); }
      current.agents.push(value.toLowerCase());
      lastWasAgent = true;
    } else if ((key === "allow" || key === "disallow") && current) {
      lastWasAgent = false;
      if (value) current.rules.push({ allow: key === "allow", path: value });
    } else lastWasAgent = false;
  }
  const mine = groups.filter((g) => g.agents.some((a) => a !== "*" && agent.toLowerCase().includes(a)));
  const rules = (mine.length ? mine : groups.filter((g) => g.agents.includes("*"))).flatMap((g) => g.rules);
  let best: { allow: boolean; len: number } | null = null;
  for (const r of rules) {
    const pattern = new RegExp("^" + r.path.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*").replace(/\\\$$/, "$"));
    if (!pattern.test(path)) continue;
    const len = r.path.length;
    if (!best || len > best.len || (len === best.len && r.allow)) best = { allow: r.allow, len };
  }
  return best ? best.allow : true;
}

/** Vingerafdruk van de zichtbare tekst (zonder scripts, stijlen en tags), plus de paginatitel. */
export function fingerprint(html: string): { hash: string; title: string | null } {
  const title = /<title[^>]*>([\s\S]*?)<\/title>/i.exec(html)?.[1]?.replace(/\s+/g, " ").trim().slice(0, 200) || null;
  const text = html
    .replace(/<(script|style|noscript|svg|template)[\s\S]*?<\/\1>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&[a-z#0-9]+;/gi, " ")
    .replace(/\d{6,}/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
  return { hash: createHash("sha256").update(text).digest("hex").slice(0, 32), title: title ? decodeEntities(title) : null };
}

function decodeEntities(s: string) {
  return s.replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;/g, " ");
}

async function assertPublic(host: string, deps: CheckDeps) {
  const addresses = await deps.resolve(host);
  if (!addresses.length || !addresses.every(isPublicAddress)) throw new Blocked(`${host} wijst naar een privé-adres`);
}
class Blocked extends Error {}

async function readLimited(res: Response): Promise<string> {
  if (!res.body) return "";
  const reader = res.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    chunks.push(value);
    if (size >= MAX_BYTES) { await reader.cancel(); break; }
  }
  return new TextDecoder().decode(Buffer.concat(chunks));
}

/** Eén GET met eigen afhandeling van doorverwijzingen (elke stap: https en een publiek adres). */
async function get(url: URL, deps: CheckDeps, accept: string): Promise<{ res: Response; url: URL }> {
  let current = url;
  for (let hop = 0; hop <= MAX_REDIRECTS; hop++) {
    await assertPublic(current.hostname, deps);
    const res = await deps.fetch(current, { redirect: "manual", signal: AbortSignal.timeout(TIMEOUT_MS), headers: { "user-agent": USER_AGENT, accept } });
    const loc = res.status >= 300 && res.status < 400 ? res.headers.get("location") : null;
    if (!loc) return { res, url: current };
    await res.body?.cancel();
    const next = new URL(loc, current);
    if (next.protocol !== "https:") throw new Blocked("Doorverwijzing naar een adres zonder https");
    current = next;
  }
  throw new Blocked("Te veel doorverwijzingen");
}

export async function checkSource(raw: string, deps: CheckDeps = defaultDeps): Promise<CheckResult> {
  const parsed = checkSourceUrl(raw);
  const empty = { httpStatus: null, finalUrl: null, robotsAllowed: null, contentHash: null, pageTitle: null };
  if ("problem" in parsed) return { outcome: "blocked", ...empty, note: parsed.problem };
  const url = parsed.url;
  try {
    let robotsAllowed = true;
    try {
      const r = await get(new URL("/robots.txt", url), deps, "text/plain");
      if (r.res.ok) robotsAllowed = robotsAllows(await readLimited(r.res), url.pathname + url.search);
      else await r.res.body?.cancel();
    } catch (e) { if (e instanceof Blocked) throw e; /* geen robots.txt = alles mag */ }
    if (!robotsAllowed) return { outcome: "blocked", ...empty, robotsAllowed: false, note: "robots.txt van de maker staat controle niet toe" };

    const { res, url: final } = await get(url, deps, "text/html,application/xhtml+xml");
    const base = { httpStatus: res.status, finalUrl: final.href, robotsAllowed };
    if (res.status === 404 || res.status === 410) { await res.body?.cancel(); return { outcome: "gone", ...base, contentHash: null, pageTitle: null, note: `Pagina bestaat niet meer (${res.status})` }; }
    if (!res.ok) { await res.body?.cancel(); return { outcome: "error", ...base, contentHash: null, pageTitle: null, note: `De site gaf foutcode ${res.status}` }; }
    if (siteOf(final.hostname) !== siteOf(url.hostname)) {
      await res.body?.cancel();
      return { outcome: "gone", ...base, contentHash: null, pageTitle: null, note: `Doorverwezen naar een ander domein (${final.hostname})` };
    }
    const type = res.headers.get("content-type") ?? "";
    if (!/html/i.test(type)) {
      await res.body?.cancel();
      return { outcome: "ok", ...base, contentHash: `type:${type.split(";")[0]}:${res.headers.get("content-length") ?? ""}`, pageTitle: null, note: "Geen HTML-pagina (bijvoorbeeld een pdf): alleen bereikbaarheid gecontroleerd" };
    }
    const { hash, title } = fingerprint(await readLimited(res));
    return { outcome: "ok", ...base, contentHash: hash, pageTitle: title, note: null };
  } catch (e) {
    if (e instanceof Blocked) return { outcome: "blocked", ...empty, note: e.message };
    return { outcome: "error", ...empty, note: e instanceof Error && e.name === "TimeoutError" ? "Geen antwoord binnen 10 seconden" : "Niet bereikbaar" };
  }
}
