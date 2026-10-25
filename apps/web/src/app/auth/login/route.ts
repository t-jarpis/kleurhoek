import { getBff } from "@/lib/auth";

/** Start het inloggen bij Zitadel. `?returnTo=/nl-NL/...` brengt je daarna terug (alleen eigen paden). */
export async function GET(request: Request) {
  const bff = getBff(request);
  if (!bff) return new Response("Inloggen staat uit", { status: 404 });
  return bff.login(request);
}
