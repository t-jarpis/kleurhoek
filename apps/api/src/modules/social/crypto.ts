import { createCipheriv, createDecipheriv, createHash, createHmac, randomBytes, timingSafeEqual } from "node:crypto";

/** Sleutels van gekoppelde kanalen versleutelen (AES-256-GCM) en de OAuth-state ondertekenen (ADR 0063). */
const key = (secret: string) => createHash("sha256").update(`kleurhoek-social:${secret}`).digest();

export function seal(secret: string, value: unknown): string {
  const iv = randomBytes(12);
  const c = createCipheriv("aes-256-gcm", key(secret), iv);
  const data = Buffer.concat([c.update(JSON.stringify(value), "utf8"), c.final()]);
  return [iv, c.getAuthTag(), data].map((b) => b.toString("base64url")).join(".");
}

export function open<T>(secret: string, sealed: string): T | null {
  try {
    const [iv, tag, data] = sealed.split(".").map((p) => Buffer.from(p, "base64url"));
    const d = createDecipheriv("aes-256-gcm", key(secret), iv!);
    d.setAuthTag(tag!);
    return JSON.parse(Buffer.concat([d.update(data!), d.final()]).toString("utf8")) as T;
  } catch { return null; }
}

/** OAuth-state: kanaal en tijdstip, ondertekend; 15 minuten geldig. */
export function signState(secret: string, kind: string, now = Date.now()): string {
  const body = `${kind}.${now.toString(36)}.${randomBytes(6).toString("base64url")}`;
  return `${body}.${createHmac("sha256", key(secret)).update(body).digest("base64url")}`;
}

export function checkState(secret: string, kind: string, state: string, now = Date.now()): boolean {
  const i = state.lastIndexOf(".");
  if (i < 0) return false;
  const body = state.slice(0, i), sig = Buffer.from(state.slice(i + 1));
  const want = Buffer.from(createHmac("sha256", key(secret)).update(body).digest("base64url"));
  if (sig.length !== want.length || !timingSafeEqual(sig, want)) return false;
  const [k, t] = body.split(".");
  return k === kind && now - parseInt(t ?? "", 36) < 15 * 60_000;
}
