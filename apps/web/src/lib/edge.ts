/**
 * Alleen verkeer via Cloudflare: Cloudflare zet de header `x-kleurhoek-edge` op elk verzoek
 * (envs/zone in Terraform), en de container weigert verzoeken zonder de juiste waarde. Zo komt
 * niemand via de standaard-hostnaam van Scaleway langs de WAF, rate limits en Access heen.
 * Zonder EDGE_SECRET (lokaal, docker compose) staat de controle uit. /healthz is altijd open voor
 * de health checks van Scaleway.
 */
export const EDGE_HEADER = "x-kleurhoek-edge";

export function edgeAllowed(pathname: string, header: string | null, secret = process.env.EDGE_SECRET): boolean {
  if (!secret || pathname === "/healthz") return true;
  return header !== null && sameString(header, secret);
}

/** Vergelijking in constante tijd (geen vroegtijdige stop bij het eerste verschil). */
function sameString(a: string, b: string): boolean {
  let diff = a.length ^ b.length;
  for (let i = 0; i < b.length; i++) diff |= (a.charCodeAt(i) || 0) ^ b.charCodeAt(i);
  return diff === 0;
}

/**
 * Organisatiedomeinen ({code}.kleurhoek.nl) lopen via een Cloudflare Worker (ADR 0017). Die geeft de
 * oorspronkelijke host, het IP-adres en het land mee, plus een eigen geheim. Alleen met dat geheim
 * vertrouwen we die headers; anders kon iedereen een andere host of een toegestaan IP-adres opgeven.
 * Zonder ORG_WORKER_SECRET: lokaal wel vertrouwen (testen), in productie nooit.
 */
export const WORKER_HEADER = "x-kh-worker";
export const FORWARDED = { host: "x-kh-host", ip: "x-kh-client-ip", country: "x-kh-country" } as const;

export function fromWorker(header: string | null, secret = process.env.ORG_WORKER_SECRET, production = process.env.NODE_ENV === "production"): boolean {
  if (!secret) return !production;
  return header !== null && sameString(header, secret);
}
