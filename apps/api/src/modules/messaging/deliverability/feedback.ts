/**
 * Bezorgmeldingen lezen (ADR 0038). Elke bron (SMTP-antwoord, webhook van een relay, later een eigen mailserver)
 * wordt hetzelfde soort melding, zodat afhandeling en inzicht nergens van een dienst afhangen. Pure functies: geen
 * database, geen site-kennis; kan zo naar het platform als een tweede site mail stuurt.
 */
export const FEEDBACK_TYPES = ["delivered", "deferred", "soft_bounce", "hard_bounce", "complaint", "unsubscribe"] as const;
export type FeedbackType = (typeof FEEDBACK_TYPES)[number];
export const PROVIDERS = ["brevo", "scaleway", "generic"] as const;
export type Provider = (typeof PROVIDERS)[number];

export interface Feedback {
  type: FeedbackType;
  email: string;
  /** Message-ID zoals wij die meegaven, zonder < >. */
  messageId: string | null;
  /** Onze verwijzing naar de mail (header X-Mail-Ref). */
  ref: string | null;
  reason: string | null;
  occurredAt: Date;
}
export type ParseResult = { events: Feedback[]; ignored: number } | { confirmUrl: string };

const EMAIL = /^[^\s@<>]{1,64}@[^\s@<>]{1,253}$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** Reden zonder e-mailadressen, ingekort: wat de ontvangende server zei is nuttig, het adres niet. */
export function cleanReason(raw: unknown): string | null {
  if (typeof raw !== "string" || !raw.trim()) return null;
  return raw.replace(/[^\s<>()"';,]+@[^\s<>()"';,]+/g, "[adres]").replace(/\s+/g, " ").trim().slice(0, 300);
}
export const cleanMessageId = (v: unknown) => (typeof v === "string" && v.trim() ? v.trim().replace(/^<|>$/g, "").slice(0, 300) : null);
const time = (...vals: unknown[]): Date => {
  for (const v of vals) {
    if (typeof v === "number" && Number.isFinite(v)) return new Date(v > 1e12 ? v : v * 1000);
    if (typeof v === "string" && v) { const d = new Date(v); if (!Number.isNaN(d.getTime())) return d; }
  }
  return new Date();
};
const obj = (v: unknown): Record<string, unknown> | null => (v && typeof v === "object" && !Array.isArray(v) ? (v as Record<string, unknown>) : null);
const list = (body: unknown): Record<string, unknown>[] => (Array.isArray(body) ? body : [body]).map(obj).filter((x): x is Record<string, unknown> => !!x);

function make(type: FeedbackType | null, email: unknown, rest: Partial<Feedback> & { occurredAt: Date }): Feedback | null {
  if (!type || typeof email !== "string" || !EMAIL.test(email.trim())) return null;
  return { type, email: email.trim().toLowerCase(), messageId: rest.messageId ?? null, ref: rest.ref && UUID.test(rest.ref) ? rest.ref.toLowerCase() : null, reason: rest.reason ?? null, occurredAt: rest.occurredAt };
}

// ---------- Brevo (transactionele en marketingwebhooks) ----------
const BREVO: Record<string, FeedbackType> = {
  delivered: "delivered", deferred: "deferred", soft_bounce: "soft_bounce", hard_bounce: "hard_bounce",
  invalid_email: "hard_bounce", blocked: "hard_bounce", spam: "complaint", complaint: "complaint", unsubscribed: "unsubscribe", unsubscribe: "unsubscribe",
};
function brevo(body: unknown): ParseResult {
  let ignored = 0;
  const events: Feedback[] = [];
  for (const e of list(body)) {
    const type = BREVO[String(e.event ?? "")] ?? null;
    const f = make(type, e.email, {
      messageId: cleanMessageId(e["message-id"]), reason: cleanReason(e.reason),
      occurredAt: time(e.ts_epoch, e.ts_event, e.date_event, e.date),
    });
    if (f) events.push(f); else ignored++;
  }
  return { events, ignored };
}

// ---------- Scaleway Transactional Email (via Topics and Events, SNS-formaat) ----------
const SCALEWAY: Record<string, FeedbackType> = {
  email_delivered: "delivered", email_deferred: "deferred", email_dropped: "hard_bounce", email_mailbox_not_found: "hard_bounce",
  email_blocklisted: "hard_bounce", email_spam: "soft_bounce",
};
/** Alleen bevestigingslinks van Scaleway zelf volgen (anders kan iemand de API een willekeurig adres laten ophalen). */
export const SCALEWAY_CONFIRM_HOST = /^https:\/\/[a-z0-9.-]+\.(scw\.cloud|scaleway\.com)\//;
function scaleway(body: unknown): ParseResult {
  const outer = obj(body);
  if (outer?.Type === "SubscriptionConfirmation") {
    const url = String(outer.SubscribeURL ?? "");
    return SCALEWAY_CONFIRM_HOST.test(url) ? { confirmUrl: url } : { events: [], ignored: 1 };
  }
  let payload: unknown = body;
  if (outer?.Type === "Notification" && typeof outer.Message === "string") {
    try { payload = JSON.parse(outer.Message); } catch { return { events: [], ignored: 1 }; }
  }
  let ignored = 0;
  const events: Feedback[] = [];
  for (const e of list(payload)) {
    const headers = Array.isArray(e.email_headers) ? (e.email_headers as { key?: string; value?: string }[]) : [];
    const header = (name: string) => headers.find((h) => h.key?.toLowerCase() === name)?.value ?? null;
    const type = SCALEWAY[String(e.type ?? "")] ?? null;
    const reason = cleanReason(e.email_response_message ?? e.email_error) ?? (e.type === "email_spam" ? "Geweigerd als spam door de ontvangende server" : null);
    const f = make(type, e.email_to, {
      messageId: cleanMessageId(header("message-id")), ref: header("x-mail-ref"), reason,
      occurredAt: time(e.created_at, e.email_sent_at),
    });
    if (f) events.push(f); else ignored++;
  }
  return { events, ignored };
}

// ---------- Eigen formaat (eigen mailserver, scripts, tests) ----------
function generic(body: unknown): ParseResult {
  const root = obj(body);
  const items = Array.isArray(root?.events) ? root!.events : body;
  let ignored = 0;
  const events: Feedback[] = [];
  for (const e of list(items)) {
    const type = (FEEDBACK_TYPES as readonly string[]).includes(String(e.type)) ? (e.type as FeedbackType) : null;
    const f = make(type, e.email, { messageId: cleanMessageId(e.messageId), ref: typeof e.ref === "string" ? e.ref : null, reason: cleanReason(e.reason), occurredAt: time(e.occurredAt) });
    if (f) events.push(f); else ignored++;
  }
  return { events, ignored };
}

export function parseFeedback(provider: Provider, body: unknown): ParseResult {
  return provider === "brevo" ? brevo(body) : provider === "scaleway" ? scaleway(body) : generic(body);
}

/**
 * Een fout bij het afgeven aan SMTP. Alleen een permanente weigering van de ontvanger (5xx op RCPT TO) is een
 * harde bounce; een 5xx op iets anders (inloggen, afzender) is ons eigen probleem en mag de ontvanger niet blokkeren.
 */
export function classifySmtpError(e: unknown): { kind: "hard_bounce" | "retry"; reason: string } {
  const err = (e ?? {}) as { responseCode?: number; command?: string; response?: string; message?: string; rejected?: unknown[] };
  const reason = cleanReason(err.response ?? err.message ?? String(e)) ?? "Onbekende fout";
  const rcpt = typeof err.command === "string" && /^RCPT/i.test(err.command);
  if (rcpt && typeof err.responseCode === "number" && err.responseCode >= 500) return { kind: "hard_bounce", reason };
  return { kind: "retry", reason };
}

/** Domein van de ontvanger (gmail.com, hotmail.com …), voor inzicht per mailprovider. */
export const domainOf = (email: string) => (email.split("@")[1] ?? "").toLowerCase().slice(0, 253);
