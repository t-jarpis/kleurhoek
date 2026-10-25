import { NextResponse, type NextRequest } from "next/server";
import { EDGE_HEADER, edgeAllowed, FORWARDED, fromWorker, WORKER_HEADER } from "./lib/edge";
import { bestMarket, LIVE_MARKETS } from "./lib/markets";
import { DEFAULT_ORG, resolveOrg, SHARED_PATH } from "./lib/org-resolve";
import { domainForHost, domainOf, routeFor, siteDomains } from "./lib/sites";
import { blockedPage, CHECK_HEADER, checkKeyValid, currentPolicy, ipAllowed } from "./lib/site-access";

export async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  if (!edgeAllowed(path, request.headers.get(EDGE_HEADER))) {
    return new NextResponse("Niet toegestaan", { status: 403 });
  }
  // Via de Worker van een organisatiedomein: host, IP en land van de bezoeker uit diens headers. Zonder
  // geldig Worker-geheim worden die headers weggegooid, zodat niemand ze zelf kan meesturen.
  const headers = new Headers(request.headers);
  const worker = fromWorker(request.headers.get(WORKER_HEADER));
  for (const h of [WORKER_HEADER, ...Object.values(FORWARDED)]) if (!worker || h === WORKER_HEADER) headers.delete(h);
  if (worker) {
    const ip = request.headers.get(FORWARDED.ip), country = request.headers.get(FORWARDED.country);
    if (ip) headers.set("cf-connecting-ip", ip);
    if (country) headers.set("cf-ipcountry", country);
  }

  // Afgeschermde website: alleen IP-adressen uit de lijst in het admin panel (ADR 0015).
  // Nooit een lijst kunnen ophalen: in productie dicht (503), lokaal open.
  const policy = await currentPolicy();
  if (!policy && process.env.NODE_ENV === "production") return new NextResponse("Even niet bereikbaar", { status: 503, headers: { "retry-after": "30" } });
  const ip = headers.get("cf-connecting-ip");
  // Mailrelay (bezorgmeldingen) en mailprogramma's (afmelden met één klik) komen niet van een toegestaan IP;
  // die routes controleren zelf een sleutel of token (ADR 0037, 0038).
  const machine = request.method === "POST" && /^\/mail\/(events\/[a-z]+|afmelden)$/.test(path);
  if (policy && !machine && !ipAllowed(policy, ip) && !checkKeyValid(request.headers.get(CHECK_HEADER))) return blockedPage(ip);
  headers.delete(CHECK_HEADER);

  // Welke organisatie: de host van het verzoek, of die van het organisatiedomein (via de Worker).
  const host = headers.get(FORWARDED.host) ?? request.headers.get("host") ?? "";
  const org = await resolveOrg(host);
  headers.set("x-kh-org", org.slug);
  headers.set("x-kh-site-host", host.toLowerCase().replace(/:\d+$/, ""));

  // Kleurhoek zelf op een eigen domein (ADR 0040): .nl zonder voorvoegsel, .be met /nl en /fr, .com met /<markt>.
  const domains = siteDomains();
  const domain = org.slug === DEFAULT_ORG ? domainForHost(host, domains) : null;
  if (domain && domains && !SHARED_PATH.test(path)) {
    const best = (candidates: string[]) => bestMarket(headers.get("cf-ipcountry"), request.headers.get("accept-language"), candidates);
    const r = routeFor({ domain, path, live: LIVE_MARKETS, domains, acceptLanguage: request.headers.get("accept-language"), best });
    if (r.kind === "redirect") {
      const res = NextResponse.redirect(r.location + request.nextUrl.search, r.permanent ? 301 : 302);
      // Het adres is al volledig (soms een ander eigen domein): de Worker laat het staan.
      res.headers.set("x-kh-keep-location", "1");
      // De keuze op de beginpagina hangt af van taal en land: niet in een gedeelde cache.
      if (!r.permanent) { res.headers.set("cache-control", "private, no-store"); res.headers.set("vary", "accept-language"); }
      return res;
    }
    const url = request.nextUrl.clone();
    // Onbekend pad: de niet-gevonden-pagina van een markt op dit domein (in de juiste taal).
    const fallback = LIVE_MARKETS.find((m) => domainOf(m) === domain) ?? LIVE_MARKETS[0]!;
    url.pathname = r.kind === "page" ? `/${org.slug}/${r.market}${r.rest}` : `/${org.slug}/${fallback}/_niet-gevonden`;
    return NextResponse.rewrite(url, { request: { headers } });
  }

  // Op "/" kiezen we de beste markt: eerst het land (van Cloudflare), dan de taal van de browser.
  if (path === "/") {
    const markets = org.markets ? LIVE_MARKETS.filter((m) => org.markets!.includes(m)) : LIVE_MARKETS;
    const market = bestMarket(headers.get("cf-ipcountry"), request.headers.get("accept-language"), markets);
    return NextResponse.redirect(new URL(`/${market}`, request.url), 307);
  }
  if (SHARED_PATH.test(path)) return NextResponse.next({ request: { headers } });
  // Pagina's: intern naar /<organisatie>/<pad>, zodat elke organisatie haar eigen (gecachete) pagina's heeft.
  const url = request.nextUrl.clone();
  url.pathname = `/${org.slug}${path}`;
  return NextResponse.rewrite(url, { request: { headers } });
}

// Alles behalve /healthz (health checks van Scaleway).
export const config = { matcher: ["/((?!healthz).*)"] };
