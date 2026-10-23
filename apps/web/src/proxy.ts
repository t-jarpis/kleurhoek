import { NextResponse, type NextRequest } from "next/server";
import { EDGE_HEADER, edgeAllowed } from "./lib/edge";
import { bestMarket } from "./lib/markets";
import { blockedPage, currentPolicy, ipAllowed } from "./lib/site-access";

export async function proxy(request: NextRequest) {
  if (!edgeAllowed(request.nextUrl.pathname, request.headers.get(EDGE_HEADER))) {
    return new NextResponse("Niet toegestaan", { status: 403 });
  }
  // Afgeschermde website: alleen IP-adressen uit de lijst in het admin panel (ADR 0015).
  // Nooit een lijst kunnen ophalen: in productie dicht (503), lokaal open.
  const policy = await currentPolicy();
  if (!policy && process.env.NODE_ENV === "production") return new NextResponse("Even niet bereikbaar", { status: 503, headers: { "retry-after": "30" } });
  const ip = request.headers.get("cf-connecting-ip");
  if (policy && !ipAllowed(policy, ip)) return blockedPage(ip);
  // Op "/" kiezen we de beste markt: eerst het land (van Cloudflare), dan de taal van de browser.
  if (request.nextUrl.pathname === "/") {
    const market = bestMarket(request.headers.get("cf-ipcountry"), request.headers.get("accept-language"));
    return NextResponse.redirect(new URL(`/${market}`, request.url), 307);
  }
  return NextResponse.next();
}

// Alles behalve /healthz (health checks van Scaleway).
export const config = { matcher: ["/((?!healthz).*)"] };
