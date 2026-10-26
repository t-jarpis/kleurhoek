"use server";
import { headers } from "next/headers";
import type { ContactState } from "../contact/actions";
import { powField } from "@/lib/pow";

const API_URL = process.env.API_URL ?? "http://localhost:3001";
const KINDS = new Set(["school", "opvang", "vereniging", "bedrijf", "overig"]);

/**
 * Aanvraag voor een eigen omgeving (ADR 0028). Gaat als contactbericht met onderwerp "organization" en de
 * gegevens van de organisatie naar de inbox; in het admin panel maak je er met één klik de organisatie van.
 */
export async function sendOrgRequest(market: string, _prev: ContactState, form: FormData): Promise<ContactState> {
  const h = await headers();
  const field = (k: string) => String(form.get(k) ?? "").slice(0, 5000).trim();
  const fields = {
    organization: field("organization"), kind: field("kind"), code: field("code").toLowerCase(), children: field("children"),
    orgSite: field("orgSite"), name: field("name"), email: field("email"), message: field("message"),
  };
  const started = Number(field("started"));
  if (fields.organization.length < 2 || !KINDS.has(fields.kind) || !/^\S+@\S+\.\S+$/.test(fields.email) || fields.message.length < 10
    || (fields.code && !/^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/.test(fields.code)) || !/^[a-z]{2}-[a-z]{2}$/i.test(market)) {
    return { status: "invalid", fields };
  }
  const ip = h.get("cf-connecting-ip") ?? h.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "";
  const res = await fetch(`${API_URL}/v1/contact`, {
    method: "POST", cache: "no-store", signal: AbortSignal.timeout(8000),
    headers: { "content-type": "application/json", ...(ip ? { "cf-connecting-ip": ip } : {}) },
    body: JSON.stringify({
      topic: "organization", ...(fields.name ? { name: fields.name } : {}), email: fields.email, message: fields.message,
      org: "kleurhoek", market, trap: field("website"), ...(powField(field("pow")) ? { pow: powField(field("pow")) } : {}),
      ...(Number.isFinite(started) && started > 0 ? { elapsedMs: Math.max(0, Date.now() - started) } : {}),
      details: {
        organization: fields.organization, kind: fields.kind,
        ...(fields.code ? { code: fields.code } : {}), ...(fields.children ? { children: fields.children.slice(0, 40) } : {}),
        ...(fields.orgSite ? { website: fields.orgSite.slice(0, 200) } : {}),
      },
    }),
  }).catch(() => null);
  if (!res) return { status: "error", fields };
  if (res.status === 202) return { status: "sent" };
  if (res.status === 429) return { status: "busy", fields };
  if (res.status === 403) return { status: "closed", fields };
  if (res.status === 400) return { status: "invalid", fields };
  return { status: "error", fields };
}
