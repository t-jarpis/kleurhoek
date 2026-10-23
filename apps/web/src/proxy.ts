import { NextResponse, type NextRequest } from "next/server";
import { EDGE_HEADER, edgeAllowed } from "./lib/edge";
import { bestMarket, LIVE_MARKETS } from "./lib/markets";
import { resolveOrg, SHARED_PATH } from "./lib/org-resolve";
import { blockedPage, currentPolicy, ipAllowed } from "./lib/site-access";

/** Header waarin de Cloudflare Worker de oorspronkelijke host van een organisatiedomein meegeeft (ADR 0017). */
const ORIGINAL_HOST = "x-kh-host";

export async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  if (!edgeAllowed(path, request.headers.get(EDGE_HEADER))) {
    return new NextResponse("Niet toegestaan", { status: 403 });
  }
  // Afgeschermde website: alleen IP-adressen uit de lijst in het admin panel (ADR 0015).
  // Nooit een lijst kunnen ophalen: in productie dicht (503), lokaal open.
  const policy = await currentPolicy();
  if (!policy && process.env.NODE_ENV === "production") return new NextResponse("Even niet bereikbaar", { status: 503, headers: { "retry-after": "30" } });
  const ip = request.headers.get("cf-connecting-ip");
  if (policy && !ipAllowed(policy, ip)) return blockedPage(ip);

  // Welke organisatie: de host van het verzoek, of die van het organisatiedomein (via de Worker).
  const host = request.headers.get(ORIGINAL_HOST) ?? request.headers.get("host") ?? "";
  const org = await resolveOrg(host);
  const headers = new Headers(request.headers);
  headers.set("x-kh-org", org.slug);

  // Op "/" kiezen we de beste markt: eerst het land (van Cloudflare), dan de taal van de browser.
  if (path === "/") {
    const markets = org.markets ? LIVE_MARKETS.filter((m) => org.markets!.includes(m)) : LIVE_MARKETS;
    const market = bestMarket(request.headers.get("cf-ipcountry"), request.headers.get("accept-language"), markets);
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
