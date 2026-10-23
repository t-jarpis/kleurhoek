import "server-only";
import { createCipheriv, createDecipheriv, createHash, randomBytes } from "node:crypto";
import { cookies } from "next/headers";

/**
 * Waar een bezoeker is in het inloggen, in één versleutelde cookie (AES-256-GCM). Zo hoeft de
 * inlogpagina niets op te slaan en kan de browser niets aanpassen. Leeft hooguit 15 minuten.
 * Het sessietoken van Zitadel staat erin; daarom HttpOnly, Secure en __Host- in productie.
 */
export type Step = "email" | "code" | "register" | "verify" | "passkey" | "offer";
export interface Flow {
  ar: string;            // auth request van Zitadel
  org: string;           // organisatie (huisstijl)
  back: string | null;   // terug naar de site (zonder in te loggen)
  step: Step;
  email?: string;
  uid?: string;          // gebruiker in Zitadel
  sid?: string; st?: string; // sessie en het laatste sessietoken
  passkey?: boolean;     // gebruiker heeft een passkey
  sentAt?: number;       // laatste code verstuurd (ms)
  error?: string;
}

const MAX_AGE = 15 * 60;
const secure = () => process.env.NODE_ENV === "production";
const name = () => (secure() ? "__Host-kh_login" : "kh_login");

function key(): Buffer {
  const secret = process.env.LOGIN_SECRET;
  if (!secret || secret.length < 32) {
    if (process.env.NODE_ENV === "production") throw new Error("LOGIN_SECRET ontbreekt (minstens 32 tekens)");
    return createHash("sha256").update("alleen-lokaal-niet-gebruiken").digest();
  }
  return createHash("sha256").update(secret).digest();
}

export function seal(flow: Flow): string {
  const iv = randomBytes(12);
  const c = createCipheriv("aes-256-gcm", key(), iv);
  const body = Buffer.concat([c.update(JSON.stringify({ ...flow, exp: Date.now() + MAX_AGE * 1000 }), "utf8"), c.final()]);
  return Buffer.concat([iv, c.getAuthTag(), body]).toString("base64url");
}

export function unseal(token: string | undefined): Flow | null {
  if (!token) return null;
  try {
    const raw = Buffer.from(token, "base64url");
    const d = createDecipheriv("aes-256-gcm", key(), raw.subarray(0, 12));
    d.setAuthTag(raw.subarray(12, 28));
    const data = JSON.parse(Buffer.concat([d.update(raw.subarray(28)), d.final()]).toString("utf8")) as Flow & { exp: number };
    if (typeof data.exp !== "number" || data.exp < Date.now()) return null;
    const { exp: _exp, ...flow } = data;
    return flow;
  } catch {
    return null;
  }
}

export async function readFlow(): Promise<Flow | null> {
  return unseal((await cookies()).get(name())?.value);
}

/** Alleen in een server action of route handler. */
export async function writeFlow(flow: Flow): Promise<void> {
  (await cookies()).set(name(), seal(flow), { httpOnly: true, secure: secure(), sameSite: "lax", path: "/", maxAge: MAX_AGE });
}

export async function clearFlow(): Promise<void> {
  (await cookies()).set(name(), "", { httpOnly: true, secure: secure(), sameSite: "lax", path: "/", maxAge: 0 });
}
