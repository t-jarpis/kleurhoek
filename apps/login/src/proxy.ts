import { NextResponse, type NextRequest } from "next/server";
import { EDGE_HEADER, edgeAllowed } from "./lib/edge";

/** Alleen verkeer via Cloudflare (geheime header), zoals website en admin. */
export function proxy(request: NextRequest) {
  if (!edgeAllowed(request.nextUrl.pathname, request.headers.get(EDGE_HEADER))) return new NextResponse("Niet toegestaan", { status: 403 });
  return NextResponse.next();
}

export const config = { matcher: ["/((?!healthz|_next/static).*)"] };
