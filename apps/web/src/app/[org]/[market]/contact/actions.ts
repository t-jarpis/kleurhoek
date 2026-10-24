"use server";
import { headers } from "next/headers";

const API_URL = process.env.API_URL ?? "http://localhost:3001";
const TOPICS = new Set(["question", "idea", "bug", "partnership", "copyright", "privacy"]);

export type ContactState = { status: "idle" | "sent" | "invalid" | "busy" | "closed" | "error"; fields?: Record<string, string> };

/**
 * Stuurt het formulier door naar de API (domein Contact, ADR 0024). Het IP-adres gaat alleen mee voor de
 * rate limit en wordt nergens opgeslagen. De API controleert alles opnieuw.
 */
export async function sendContact(market: string, _prev: ContactState, form: FormData): Promise<ContactState> {
  const h = await headers();
  const field = (k: string) => String(form.get(k) ?? "").slice(0, 5000);
  const fields = { topic: field("topic"), name: field("name").trim(), email: field("email").trim(), message: field("message").trim() };
  const started = Number(field("started"));
  if (!TOPICS.has(fields.topic) || !/^\S+@\S+\.\S+$/.test(fields.email) || fields.message.length < 10 || !/^[a-z]{2}-[a-z]{2}$/i.test(market)) {
    return { status: "invalid", fields };
  }
  const ip = h.get("cf-connecting-ip") ?? h.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "";
  const org = /^[a-z0-9-]{1,32}$/.test(h.get("x-kh-org") ?? "") ? h.get("x-kh-org")! : "kleurhoek";
  const res = await fetch(`${API_URL}/v1/contact`, {
    method: "POST", cache: "no-store", signal: AbortSignal.timeout(8000),
    headers: { "content-type": "application/json", ...(ip ? { "cf-connecting-ip": ip } : {}) },
    body: JSON.stringify({
      topic: fields.topic, ...(fields.name ? { name: fields.name } : {}), email: fields.email, message: fields.message,
      org, market, trap: field("website"), ...(Number.isFinite(started) && started > 0 ? { elapsedMs: Math.max(0, Date.now() - started) } : {}),
    }),
  }).catch(() => null);
  if (!res) return { status: "error", fields };
  if (res.status === 202) return { status: "sent" };
  if (res.status === 429) return { status: "busy", fields };
  if (res.status === 403) return { status: "closed", fields };
  if (res.status === 400) return { status: "invalid", fields };
  return { status: "error", fields };
}
