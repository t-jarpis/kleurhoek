import { getBff, noStore, sameOrigin } from "@/lib/auth";

/**
 * Uitloggen: alleen via fetch POST vanaf onze eigen pagina, zodat een andere site je niet stiekem
 * kan uitloggen. We geven het Zitadel-adres terug in plaats van te redirecten; zo blijft
 * `form-action 'self'` in de CSP gewoon gelden.
 */
export async function POST(request: Request) {
  const bff = getBff();
  if (!bff) return new Response("Inloggen staat uit", { status: 404 });
  if (!sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  const res = await bff.logout(request);
  const headers = new Headers(noStore);
  for (const cookie of res.headers.getSetCookie()) headers.append("set-cookie", cookie);
  return Response.json({ location: res.headers.get("location") ?? "/" }, { headers });
}
