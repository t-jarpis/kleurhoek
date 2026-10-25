"use server";
import { headers } from "next/headers";
import { api } from "@/lib/mail";

const TOPICS = new Set(["nieuwe-platen", "feestdagen", "nieuwsbrief"]);
export type SubscribeState = { status: "idle" | "sent" | "invalid" | "busy" | "error"; email?: string };

/** Aanmelden (ADR 0037): de API stuurt een bevestigingsmail. Zelfde antwoord, of het adres nu bekend is of niet. */
export async function subscribe(market: string, _prev: SubscribeState, form: FormData): Promise<SubscribeState> {
  const h = await headers();
  const email = String(form.get("email") ?? "").trim().slice(0, 254);
  const topics = form.getAll("topics").map(String).filter((t) => TOPICS.has(t));
  const adult = form.get("adult") === "on";
  const started = Number(form.get("started"));
  if (!/^\S+@\S+\.\S+$/.test(email) || !topics.length || !adult || !/^[a-z]{2}-[a-z]{2}$/.test(market)) return { status: "invalid", email };
  const ip = h.get("cf-connecting-ip") ?? h.get("x-forwarded-for")?.split(",")[0]?.trim() ?? null;
  const res = await api("subscribe", {
    method: "POST", ip,
    body: { email, market, topics, adult: true, trap: String(form.get("website") ?? "").slice(0, 200), ...(Number.isFinite(started) && started > 0 ? { elapsedMs: Math.max(0, Date.now() - started) } : {}) },
  });
  if (!res) return { status: "error", email };
  if (res.status === 202) return { status: "sent" };
  if (res.status === 429) return { status: "busy", email };
  if (res.status === 400) return { status: "invalid", email };
  return { status: "error", email };
}
