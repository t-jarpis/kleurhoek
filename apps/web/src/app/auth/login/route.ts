import { getBff } from "@/lib/auth";
import { getOrg } from "@/lib/org";
import { DEFAULT_ORG } from "@/lib/org-resolve";

/** Alleen eigen paden als terugkeeradres (geen //andere-site). */
const safeReturn = (v: string | null) => (v && v.startsWith("/") && !v.startsWith("//") && !v.startsWith("/\\") ? v : "/");

/**
 * Start het inloggen bij Zitadel. `?returnTo=/nl-NL/...` brengt je daarna terug (alleen eigen paden).
 * Staat inloggen uit (admin panel › Toegang, of voor deze organisatie), dan gewoon terug naar de pagina.
 */
export async function GET(request: Request) {
  const bff = getBff(request);
  if (!bff) return new Response("Inloggen staat uit", { status: 404 });
  const org = await getOrg(request.headers.get("x-kh-org") ?? DEFAULT_ORG);
  if (org && !org.features.accounts) {
    const back = safeReturn(new URL(request.url).searchParams.get("returnTo"));
    return new Response(null, { status: 303, headers: { location: back, "cache-control": "no-store" } });
  }
  return bff.login(request);
}
