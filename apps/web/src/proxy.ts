import { NextResponse, type NextRequest } from "next/server";
import { bestMarket } from "./lib/markets";

/** Op "/" kiezen we de beste markt: eerst het land (van Cloudflare), dan de taal van de browser. */
export function proxy(request: NextRequest) {
  const market = bestMarket(request.headers.get("cf-ipcountry"), request.headers.get("accept-language"));
  return NextResponse.redirect(new URL(`/${market}`, request.url), 307);
}

export const config = { matcher: "/" };
