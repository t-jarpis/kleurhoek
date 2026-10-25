import { getBff } from "@/lib/auth";
import { getOrg } from "@/lib/org";
import { DEFAULT_ORG } from "@/lib/org-resolve";

export async function GET(request: Request) {
  const bff = getBff(request);
  if (!bff) return new Response("Inloggen staat uit", { status: 404 });
  // Inloggen uitgezet terwijl iemand bij de inlogpagina was: geen nieuwe sessie (admin panel › Toegang).
  const org = await getOrg(request.headers.get("x-kh-org") ?? DEFAULT_ORG);
  if (org && !org.features.accounts) return new Response(null, { status: 303, headers: { location: "/", "cache-control": "no-store" } });
  return bff.callback(request);
}
