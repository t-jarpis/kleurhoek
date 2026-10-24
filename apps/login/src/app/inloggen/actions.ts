"use server";
import { redirect } from "next/navigation";
import { z } from "zod";
import { afterLogin, current, fail, finish, go, RESEND_AFTER_MS, sendLoginCode } from "@/lib/flow-actions";
import { t } from "@/lib/i18n";
import { clearFlow } from "@/lib/state";
import { zitadel, ZitadelError } from "@/lib/zitadel";

const ORG = () => process.env.SITE_ORG_ID ?? "";
const Email = z.string().trim().toLowerCase().email().max(200);
const Code = z.string().trim().regex(/^[A-Za-z0-9]{4,12}$/);

/** Stap 1: e-mailadres. Bestaat het account, dan een passkey of een code; anders zeggen we niets. */
export async function submitEmail(formData: FormData) {
  const flow = await current();
  const email = Email.safeParse(formData.get("email"));
  if (!email.success) return fail(flow, t(flow.lang).errEmail);
  try {
    const user = await zitadel.findUser(email.data, ORG());
    // Onbekend adres: zelfde vervolgscherm, er gaat niets de deur uit (niemand kan zo achterhalen wie een account heeft).
    if (!user) return go(flow, { step: "code", email: email.data, uid: undefined, sid: undefined, st: undefined, passkey: false, sentAt: Date.now() });
    const methods = await zitadel.methods(user.userId);
    const passkey = methods.includes("AUTHENTICATION_METHOD_TYPE_PASSKEY");
    const next = { ...flow, email: email.data, passkey };
    if (passkey) return go(next, { step: "passkey", uid: user.userId });
    return await sendLoginCode(next, user.userId, user.verified, methods);
  } catch (e) {
    if (isRedirect(e)) throw e;
    return fail(flow, t(flow.lang).errOutage);
  }
}

/** Stap 2: de code uit de e-mail. */
export async function submitCode(formData: FormData) {
  const flow = await current();
  const code = Code.safeParse(formData.get("code"));
  if (!code.success || !flow.sid) return fail(flow, t(flow.lang).errCode);
  try {
    const { sessionToken } = await zitadel.setSession(flow.sid, { checks: { otpEmail: { code: code.data } } });
    return await afterLogin({ ...flow, st: sessionToken });
  } catch (e) {
    if (isRedirect(e)) throw e;
    return fail(flow, e instanceof ZitadelError && e.invalid ? t(flow.lang).errCode : t(flow.lang).errOutage);
  }
}

/** Opnieuw sturen, hooguit eens per 30 seconden. */
export async function resend() {
  const flow = await current();
  if (flow.sentAt && Date.now() - flow.sentAt < RESEND_AFTER_MS) return fail(flow, t(flow.lang).errWait);
  try {
    if (flow.step === "verify" && flow.uid) { await zitadel.resendEmailCode(flow.uid); return go(flow, { sentAt: Date.now() }); }
    if (flow.uid) {
      const methods = await zitadel.methods(flow.uid);
      return await sendLoginCode(flow, flow.uid, true, methods);
    }
    return go(flow, { sentAt: Date.now() });
  } catch (e) {
    if (isRedirect(e)) throw e;
    return fail(flow, t(flow.lang).errOutage);
  }
}

/** Van passkey naar code. */
export async function useCode() {
  const flow = await current();
  if (!flow.uid) return go(flow, { step: "email" });
  try {
    return await sendLoginCode(flow, flow.uid, true, await zitadel.methods(flow.uid));
  } catch (e) {
    if (isRedirect(e)) throw e;
    return fail(flow, t(flow.lang).errOutage);
  }
}

export async function startRegister() {
  const flow = await current();
  return go(flow, { step: "register" });
}

const Register = z.object({ email: Email, name: z.string().trim().min(1).max(60).regex(/^[^<>]+$/), adult: z.literal("on") });

/** Account maken: naam, e-mail en de bevestiging dat je volwassen bent (accounts alleen voor ouders, ADR 0002). */
export async function submitRegister(formData: FormData) {
  const flow = await current();
  const r = Register.safeParse(Object.fromEntries(formData));
  if (!r.success) return fail({ ...flow, step: "register" }, r.error.issues.some((i) => i.path[0] === "adult") ? t(flow.lang).errAdult : t(flow.lang).errRegister);
  try {
    const uid = await zitadel.addHuman(ORG(), r.data.email, r.data.name, flow.lang);
    return go(flow, { step: "verify", email: r.data.email, uid, passkey: false, sentAt: Date.now() });
  } catch (e) {
    if (isRedirect(e)) throw e;
    // Bestaat het adres al, dan gewoon inloggen met een code: zelfde scherm, geen hint dat het account bestond.
    if (e instanceof ZitadelError && e.exists) {
      const user = await zitadel.findUser(r.data.email, ORG()).catch(() => null);
      if (user) return await sendLoginCode({ ...flow, email: r.data.email }, user.userId, user.verified, await zitadel.methods(user.userId)).catch((x) => { if (isRedirect(x)) throw x; return fail(flow, t(flow.lang).errOutage); });
    }
    return fail(flow, t(flow.lang).errOutage);
  }
}

/** E-mailadres bevestigen met de code; dat is meteen het bewijs voor deze keer inloggen. */
export async function submitVerify(formData: FormData) {
  const flow = await current();
  const code = Code.safeParse(formData.get("code"));
  if (!code.success || !flow.uid) return fail(flow, t(flow.lang).errCode);
  try {
    await zitadel.verifyEmail(flow.uid, code.data);
    await zitadel.addOtpEmail(flow.uid).catch((e) => { if (!(e instanceof ZitadelError && e.exists)) throw e; });
    const s = await zitadel.createSession(flow.uid);
    return await afterLogin({ ...flow, sid: s.sessionId, st: s.sessionToken });
  } catch (e) {
    if (isRedirect(e)) throw e;
    return fail(flow, e instanceof ZitadelError && e.invalid ? t(flow.lang).errCode : t(flow.lang).errOutage);
  }
}

/** Geen passkey nu: inloggen afronden. */
export async function skipOffer() {
  return finish(await current());
}

export async function backToEmail() {
  const flow = await current();
  return go(flow, { step: "email", uid: undefined, sid: undefined, st: undefined, passkey: false });
}

/** Afbreken: de site krijgt "geweigerd" terug en toont gewoon de pagina weer. */
export async function cancel() {
  const flow = await current();
  let url = flow.back ?? "/";
  try { url = await zitadel.deny(flow.ar); } catch { /* verlopen: dan gewoon terug */ }
  await clearFlow();
  redirect(url);
}

/** redirect() werkt met een speciale fout; die moet door. */
function isRedirect(e: unknown): boolean {
  return typeof e === "object" && e !== null && "digest" in e && String((e as { digest: unknown }).digest).startsWith("NEXT_REDIRECT");
}
