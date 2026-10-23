import { NextResponse, type NextRequest } from "next/server";
import { allowedReturn } from "@/lib/return";
import { clearFlow } from "@/lib/state";

export const dynamic = "force-dynamic";

/** Zitadel stuurt hierheen bij uitloggen zonder id_token_hint (login v2); wij ruimen op en sturen terug. */
export async function GET(request: NextRequest) {
  await clearFlow();
  const target = allowedReturn(request.nextUrl.searchParams.get("post_logout_redirect"));
  return NextResponse.redirect(target ?? new URL("/uitgelogd", request.url), 303);
}
