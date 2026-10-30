import { headers } from "next/headers";
import { INDEXNOW_KEY } from "@/lib/indexnow";
import { indexableHost, SITE_HOST_HEADER } from "@/lib/seo";

/** De IndexNow-sleutel (ADR 0061), alleen op de productiedomeinen (ADR 0040). */
export async function GET() {
  const h = await headers();
  if (!indexableHost(h.get(SITE_HOST_HEADER) ?? h.get("host"))) return new Response("Not found", { status: 404 });
  return new Response(INDEXNOW_KEY, { headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "public, max-age=86400" } });
}
