import { createHash, createHmac, randomBytes, timingSafeEqual } from "node:crypto";

/**
 * Links in mails (ADR 0037). Afmelden en voorkeuren: id van de abonnee plus een HMAC, zodat de link zonder
 * inloggen werkt en niets in de database hoeft. Bevestigen: een willekeurig token, alleen de hash staat opgeslagen.
 */
const b64 = (b: Buffer) => b.toString("base64url");

export function preferenceToken(secret: string, subscriberId: string): string {
  const id = b64(Buffer.from(subscriberId.replace(/-/g, ""), "hex"));
  return `${id}.${b64(createHmac("sha256", secret).update(`pref:${subscriberId}`).digest()).slice(0, 32)}`;
}

/** Het id uit een voorkeurtoken, of null als het niet klopt. */
export function readPreferenceToken(secret: string, token: string): string | null {
  const m = /^([A-Za-z0-9_-]{22})\.([A-Za-z0-9_-]{32})$/.exec(token);
  if (!m) return null;
  const hex = Buffer.from(m[1]!, "base64url").toString("hex");
  if (hex.length !== 32) return null;
  const id = `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  const expected = Buffer.from(preferenceToken(secret, id).split(".")[1]!);
  const given = Buffer.from(m[2]!);
  return expected.length === given.length && timingSafeEqual(expected, given) ? id : null;
}

export function newConfirmToken(): { token: string; hash: string } {
  const token = b64(randomBytes(24));
  return { token, hash: hashToken(token) };
}
export const hashToken = (token: string) => createHash("sha256").update(token).digest("hex");
