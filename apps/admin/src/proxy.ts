import { NextResponse, type NextRequest } from "next/server";
import { getBff } from "./lib/auth";
import { EDGE_HEADER, edgeAllowed } from "./lib/edge";

/** Paden zonder sessie: inloggen, statische bestanden. */
const PUBLIC = /^\/(auth\/|_next\/|favicon\.ico$)/;

/**
 * Elke pagina van het admin panel vereist een geldige sessie. Hier wordt ook het access token
 * ververst, want alleen de proxy mag cookies zetten vóór de pagina rendert.
 */
export async function proxy(request: NextRequest) {
  // Eerst: alleen verkeer via Cloudflare (en daarmee Cloudflare Access).
  if (!edgeAllowed(request.nextUrl.pathname, request.headers.get(EDGE_HEADER))) {
    return new NextResponse("Niet toegestaan", { status: 403 });
  }
  if (PUBLIC.test(request.nextUrl.pathname)) return NextResponse.next();
  const bff = getBff();
  if (!bff) {
    if (process.env.NODE_ENV === "production") return new NextResponse("Inloggen is niet ingesteld", { status: 503 });
    return NextResponse.next();
  }
  const { session, setCookies = [] } = await bff.session(request.headers.get("cookie"));
  if (!session) {
    const login = new URL("/auth/login", request.url);
    login.searchParams.set("returnTo", request.nextUrl.pathname + request.nextUrl.search);
    const res = NextResponse.redirect(login, 303);
    for (const c of setCookies) res.headers.append("set-cookie", c);
    return res;
  }
  if (!setCookies.length) return NextResponse.next();
  // Ververste sessie: doorgeven aan de pagina (request) en aan de browser (response).
  const pairs = setCookies.map((c) => c.split(";")[0] ?? "");
  const names = new Set(pairs.map((p) => p.split("=")[0]));
  const fresh = setCookies.filter((c) => !c.includes("Max-Age=0")).map((c) => c.split(";")[0] ?? "");
  const others = (request.headers.get("cookie") ?? "").split(/;\s*/).filter((c) => c && !names.has(c.split("=")[0]));
  const headers = new Headers(request.headers);
  headers.set("cookie", [...others, ...fresh].join("; "));
  const res = NextResponse.next({ request: { headers } });
  for (const c of setCookies) res.headers.append("set-cookie", c);
  return res;
}

// Alles behalve /healthz (health checks van Scaleway).
export const config = { matcher: ["/((?!healthz).*)"] };
