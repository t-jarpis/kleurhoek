import { NextResponse, type NextRequest } from "next/server";
import { z } from "zod";
import { t } from "@/lib/i18n";
import { clearFlow, readFlow, writeFlow } from "@/lib/state";
import { passkeyChallenge, zitadel, ZitadelError } from "@/lib/zitadel";

export const dynamic = "force-dynamic";

const Body = z.discriminatedUnion("action", [
  z.object({ action: z.literal("login-start") }),
  z.object({ action: z.literal("login-finish"), credential: z.record(z.string(), z.unknown()) }),
  z.object({ action: z.literal("register-start") }),
  z.object({ action: z.literal("register-finish"), passkeyId: z.string().max(64), credential: z.record(z.string(), z.unknown()) }),
]);

const fail = (status: number, message: string) => NextResponse.json({ message }, { status });

/**
 * Passkeys (WebAuthn) met het hoofddomein als RP-ID, zodat één passkey op alle Kleurhoek-adressen werkt.
 * De browser praat alleen met deze route; Zitadel controleert de handtekening.
 */
export async function POST(request: NextRequest) {
  if (request.headers.get("sec-fetch-site") && request.headers.get("sec-fetch-site") !== "same-origin") return fail(403, "Niet toegestaan");
  const flow = await readFlow();
  if (!flow?.uid) return fail(409, t(flow?.lang).errExpired);
  const m = t(flow.lang);
  const body = Body.safeParse(await request.json().catch(() => null));
  if (!body.success) return fail(400, "Ongeldig verzoek");
  try {
    switch (body.data.action) {
      case "login-start": {
        const s = flow.sid
          ? { sessionId: flow.sid, ...(await zitadel.setSession(flow.sid, { challenges: passkeyChallenge() })) }
          : await zitadel.createSession(flow.uid, passkeyChallenge());
        await writeFlow({ ...flow, sid: s.sessionId, st: s.sessionToken, error: undefined });
        const options = (s.challenges as { webAuthN?: { publicKeyCredentialRequestOptions?: unknown } } | undefined)?.webAuthN?.publicKeyCredentialRequestOptions;
        return NextResponse.json({ options });
      }
      case "login-finish": {
        if (!flow.sid) return fail(409, m.errRestart);
        const { sessionToken } = await zitadel.setSession(flow.sid, { checks: { webAuthN: { credentialAssertionData: body.data.credential } } });
        const url = await zitadel.finalize(flow.ar, flow.sid, sessionToken);
        await clearFlow();
        return NextResponse.json({ redirect: url });
      }
      case "register-start": {
        if (flow.step !== "offer" || !flow.sid) return fail(409, m.errRestart);
        const r = await zitadel.passkeyRegistration(flow.uid);
        return NextResponse.json({ passkeyId: r.passkeyId, options: r.publicKeyCredentialCreationOptions });
      }
      case "register-finish": {
        if (flow.step !== "offer" || !flow.sid || !flow.st) return fail(409, m.errRestart);
        await zitadel.verifyPasskey(flow.uid, body.data.passkeyId, body.data.credential, deviceName(request.headers.get("user-agent")));
        const url = await zitadel.finalize(flow.ar, flow.sid, flow.st);
        await clearFlow();
        return NextResponse.json({ redirect: url });
      }
    }
  } catch (e) {
    return fail(e instanceof ZitadelError && e.invalid ? 400 : 502, e instanceof ZitadelError && e.invalid ? m.pkBadPasskey : m.pkNoConnection);
  }
}

/** Naam voor de passkey in het overzicht van de gebruiker: alleen het soort apparaat, geen versies. */
function deviceName(ua: string | null): string {
  const u = ua ?? "";
  const os = /iPhone|iPad/.test(u) ? "iPhone of iPad" : /Android/.test(u) ? "Android" : /Mac OS X/.test(u) ? "Mac" : /Windows/.test(u) ? "Windows" : "apparaat";
  return `Kleurhoek op ${os}`;
}
