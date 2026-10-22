import { NextResponse, type NextRequest } from "next/server";
import { getBff } from "./lib/auth";

/**
 * Elke pagina van het admin panel vereist een geldige sessie. Hier wordt ook het access token
 * ververst, want alleen de proxy mag cookies zetten vóór de pagina rendert.
 */
export async function proxy(request: NextRequest) {
  const bff = getBff();
  if (!bff) {
    if (process.env.NODE_ENV === "production") return new NextResponse("Inloggen is niet ingesteld", { status: 503 });
    return NextResponse.next();
  }
  const { session, setCookie } = await bff.session(request.headers.get("cookie"));
  if (!session) {
    const login = new URL("/auth/login", request.url);
    login.searchParams.set("returnTo", request.nextUrl.pathname + request.nextUrl.search);
    const res = NextResponse.redirect(login, 303);
    if (setCookie) res.headers.append("set-cookie", setCookie);
    return res;
  }
  if (!setCookie) return NextResponse.next();
  // Ververste sessie: doorgeven aan de pagina (request) en aan de browser (response).
  const fresh = setCookie.split(";")[0] ?? "";
  const [name] = fresh.split("=");
  const others = (request.headers.get("cookie") ?? "").split(/;\s*/).filter((c) => c && !c.startsWith(`${name}=`));
  const headers = new Headers(request.headers);
  headers.set("cookie", [...others, fresh].join("; "));
  const res = NextResponse.next({ request: { headers } });
  res.headers.append("set-cookie", setCookie);
  return res;
}

export const config = { matcher: ["/((?!auth/|_next/|healthz|favicon\\.ico).*)"] };
