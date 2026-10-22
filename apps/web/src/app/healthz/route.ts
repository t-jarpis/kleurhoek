/** Voor de health checks van Scaleway. Geen afhankelijkheden: zegt alleen dat het proces draait. */
export const dynamic = "force-dynamic";
export function GET() {
  return new Response("ok", { headers: { "cache-control": "no-store" } });
}
