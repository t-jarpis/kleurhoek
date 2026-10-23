import { NextResponse, type NextRequest } from "next/server";
import { orgForRedirect } from "@/lib/org";
import { writeFlow } from "@/lib/state";
import { zitadel } from "@/lib/zitadel";

export const dynamic = "force-dynamic";
const AUTH_REQUEST = /^V2_[0-9]{6,32}$/;

/**
 * Zitadel stuurt de browser hierheen met ?authRequest=V2_… (login v2 met een eigen base URI, ADR 0018).
 * We halen het verzoek op, bepalen de organisatie (huisstijl) uit de redirect-URI en beginnen de stappen.
 */
export async function GET(request: NextRequest) {
  const id = request.nextUrl.searchParams.get("authRequest") ?? "";
  const page = new URL("/inloggen", request.url);
  if (!AUTH_REQUEST.test(id)) return NextResponse.redirect(new URL("/inloggen?fout=verlopen", request.url), 303);
  try {
    const ar = await zitadel.authRequest(id);
    const org = await orgForRedirect(ar.redirectUri);
    const hint = ar.loginHint && /^[^\s@]+@[^\s@]+$/.test(ar.loginHint) ? ar.loginHint : undefined;
    await writeFlow({ ar: id, org: org.slug, back: new URL(ar.redirectUri).origin, step: "email", ...(hint ? { email: hint } : {}) });
  } catch {
    return NextResponse.redirect(new URL("/inloggen?fout=verlopen", request.url), 303);
  }
  return NextResponse.redirect(page, 303);
}
