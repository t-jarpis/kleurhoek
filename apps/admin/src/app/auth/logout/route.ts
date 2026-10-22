import { getBff, sameOrigin } from "@/lib/auth";

/** Alleen via fetch POST vanaf het panel zelf. Geeft het Zitadel-adres terug (CSP: form-action 'self'). */
export async function POST(request: Request) {
  const bff = getBff();
  if (!bff) return new Response(null, { status: 404 });
  if (!sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  const res = await bff.logout(request);
  const headers = new Headers({ "cache-control": "no-store" });
  for (const cookie of res.headers.getSetCookie()) headers.append("set-cookie", cookie);
  return Response.json({ location: res.headers.get("location") ?? "/" }, { headers });
}
