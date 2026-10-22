import { NextResponse, type NextRequest } from "next/server";
import { EDGE_HEADER, edgeAllowed } from "./lib/edge";
import { bestMarket } from "./lib/markets";

export function proxy(request: NextRequest) {
  if (!edgeAllowed(request.nextUrl.pathname, request.headers.get(EDGE_HEADER))) {
    return new NextResponse("Niet toegestaan", { status: 403 });
  }
  // Op "/" kiezen we de beste markt: eerst het land (van Cloudflare), dan de taal van de browser.
  if (request.nextUrl.pathname === "/") {
    const market = bestMarket(request.headers.get("cf-ipcountry"), request.headers.get("accept-language"));
    return NextResponse.redirect(new URL(`/${market}`, request.url), 307);
  }
  return NextResponse.next();
}

// Alles behalve /healthz (health checks van Scaleway).
export const config = { matcher: ["/((?!healthz).*)"] };
