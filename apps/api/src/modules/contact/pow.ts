import { createHash, createHmac, randomBytes, timingSafeEqual } from "node:crypto";

/**
 * Onzichtbare rekenpuzzel (proof-of-work, ADR 0048), zonder externe dienst en zonder cookies. De API geeft een
 * opgave: zoek een getal n tot `max` waarvoor sha256(salt + n) gelijk is aan `challenge`. Een browser doet daar
 * een fractie van een seconde over; wie duizenden formulieren verstuurt, betaalt het duizend keer. De opgave is
 * ondertekend (HMAC), verloopt na een uur en is één keer bruikbaar.
 */
export const POW_MAX = 20_000;
const TTL_MS = 3_600_000;

export interface Challenge { algorithm: "SHA-256"; challenge: string; salt: string; max: number; expires: number; signature: string }
export interface Solution { challenge: string; salt: string; number: number; expires: number; signature: string }

const sha = (s: string) => createHash("sha256").update(s).digest("hex");
const sign = (secret: string, challenge: string, salt: string, expires: number) => createHmac("sha256", secret).update(`${challenge}.${salt}.${expires}`).digest("hex");

export function createChallenge(secret: string, now = Date.now(), max = POW_MAX): Challenge {
  const salt = randomBytes(12).toString("hex");
  const n = Math.floor(Math.random() * max);
  const expires = now + TTL_MS;
  const challenge = sha(`${salt}${n}`);
  return { algorithm: "SHA-256", challenge, salt, max, expires, signature: sign(secret, challenge, salt, expires) };
}

/** Wat al gebruikt is (per instance; verloopt vanzelf met de opgave). */
const used = new Map<string, number>();

export function verifySolution(secret: string, s: Solution | undefined, now = Date.now()): "ok" | "missing" | "invalid" {
  if (!s) return "missing";
  if (s.expires < now || s.expires > now + TTL_MS) return "invalid";
  const expected = Buffer.from(sign(secret, s.challenge, s.salt, s.expires), "hex");
  const given = Buffer.from(/^[0-9a-f]{64}$/.test(s.signature) ? s.signature : "", "hex");
  if (given.length !== expected.length || !timingSafeEqual(given, expected)) return "invalid";
  if (sha(`${s.salt}${s.number}`) !== s.challenge) return "invalid";
  for (const [k, exp] of used) if (exp < now) used.delete(k);
  if (used.has(s.challenge)) return "invalid";
  used.set(s.challenge, s.expires);
  return "ok";
}
