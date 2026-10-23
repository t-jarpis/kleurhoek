import "server-only";
import { redirect } from "next/navigation";
import { clearFlow, readFlow, writeFlow, type Flow } from "./state";
import { otpChallenge, zitadel, ZitadelError } from "./zitadel";

export const RESEND_AFTER_MS = 30_000;

/** Huidige stap; zonder geldige stap terug naar de foutpagina (verlopen of nooit begonnen). */
export async function current(): Promise<Flow> {
  const flow = await readFlow();
  if (!flow) redirect("/inloggen?fout=verlopen");
  return flow!;
}

/** Een stap opslaan en de pagina opnieuw tonen. */
export async function go(flow: Flow, patch: Partial<Flow>): Promise<never> {
  const { error: _e, ...rest } = flow;
  await writeFlow({ ...rest, ...patch });
  redirect("/inloggen");
}

/** Melding tonen zonder van stap te wisselen. */
export const fail = (flow: Flow, error: string) => go(flow, { error });

/** Sessie koppelen aan het auth request en terug naar de site. */
export async function finish(flow: Flow): Promise<never> {
  if (!flow.sid || !flow.st) return fail(flow, "Er ging iets mis. Begin opnieuw.");
  let url: string;
  try {
    url = await zitadel.finalize(flow.ar, flow.sid, flow.st);
  } catch (e) {
    await clearFlow();
    redirect(`/inloggen?fout=${e instanceof ZitadelError && e.status === 400 ? "verlopen" : "storing"}`);
  }
  await clearFlow();
  redirect(url!);
}

/** Na inloggen met een code: eerst een passkey voorstellen als die er nog niet is, anders klaar. */
export async function afterLogin(flow: Flow): Promise<never> {
  if (!flow.passkey) return go(flow, { step: "offer" });
  return finish(flow);
}

/**
 * Een e-mailcode sturen voor deze gebruiker. Zitadel staat dat alleen toe als "code per e-mail" bij
 * de gebruiker aanstaat; dat zetten we hier zo nodig aan (alleen met een bevestigd adres).
 */
export async function sendLoginCode(flow: Flow, uid: string, verified: boolean, methods: string[]): Promise<never> {
  if (!verified) {
    await zitadel.resendEmailCode(uid);
    return go(flow, { step: "verify", uid, sentAt: Date.now() });
  }
  if (!methods.includes("AUTHENTICATION_METHOD_TYPE_OTP_EMAIL")) {
    await zitadel.addOtpEmail(uid).catch((e) => { if (!(e instanceof ZitadelError && e.exists)) throw e; });
  }
  const s = flow.sid && flow.uid === uid
    ? { sessionId: flow.sid, sessionToken: (await zitadel.setSession(flow.sid, { challenges: otpChallenge })).sessionToken }
    : await zitadel.createSession(uid, otpChallenge);
  return go(flow, { step: "code", uid, sid: s.sessionId, st: s.sessionToken, sentAt: Date.now() });
}
