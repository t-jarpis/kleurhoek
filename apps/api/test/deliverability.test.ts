import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { DeliverabilityService } from "../src/modules/messaging/deliverability/deliverability.service";
import { classifySmtpError, cleanReason, parseFeedback } from "../src/modules/messaging/deliverability/feedback";
import { MemoryTransport, type OutgoingMail } from "../src/modules/messaging/mailer";
import { MessagingScheduler } from "../src/modules/messaging/messaging.scheduler";
import { SubscribersService } from "../src/modules/messaging/subscribers.service";
import { createTestApp } from "./app";

/** Weigert één adres zoals een ontvangende server dat doet (550 op RCPT TO). */
class Picky extends MemoryTransport {
  override async send(mail: OutgoingMail) {
    if (mail.to.startsWith("bestaat-niet@")) throw Object.assign(new Error("Can't send mail"), { responseCode: 550, command: "RCPT TO", response: "550 5.1.1 <bestaat-niet@voorbeeld.test>: user unknown" });
    if (mail.to.startsWith("config@")) throw Object.assign(new Error("auth"), { responseCode: 535, command: "AUTH PLAIN", response: "535 Authentication failed" });
    return super.send(mail);
  }
}

describe("meldingen lezen (ADR 0038)", () => {
  it("leest Brevo, Scaleway (SNS) en het eigen formaat", () => {
    const b = parseFeedback("brevo", { event: "hard_bounce", email: "A@B.test", "message-id": "<abc@kleurhoek.nl>", reason: "550 user a@b.test unknown", ts_event: 1_790_000_000 });
    expect(b).toEqual({ events: [{ type: "hard_bounce", email: "a@b.test", messageId: "abc@kleurhoek.nl", ref: null, reason: "550 user [adres] unknown", occurredAt: new Date(1_790_000_000_000) }], ignored: 0 });
    expect((parseFeedback("brevo", [{ event: "spam", email: "x@y.test" }, { event: "opened", email: "x@y.test" }]) as { events: unknown[]; ignored: number }).ignored).toBe(1);
    const sns = parseFeedback("scaleway", { Type: "Notification", Message: JSON.stringify({ type: "email_mailbox_not_found", email_to: "p@q.test", created_at: "2026-10-25T10:00:00Z", email_headers: [{ key: "X-Mail-Ref", value: "0192f6a0-0000-7000-8000-0000000000aa" }], email_response_message: "mailbox not found" }) });
    expect(sns).toMatchObject({ events: [{ type: "hard_bounce", email: "p@q.test", ref: "0192f6a0-0000-7000-8000-0000000000aa", reason: "mailbox not found" }] });
    expect(parseFeedback("scaleway", { Type: "SubscriptionConfirmation", SubscribeURL: "https://sns.mnq.fr-par.scaleway.com/confirm?x=1" })).toEqual({ confirmUrl: "https://sns.mnq.fr-par.scaleway.com/confirm?x=1" });
    expect(parseFeedback("scaleway", { Type: "SubscriptionConfirmation", SubscribeURL: "http://169.254.169.254/" })).toEqual({ events: [], ignored: 1 });
    expect(parseFeedback("generic", { events: [{ type: "complaint", email: "c@d.test" }, { type: "kapot", email: "c@d.test" }] })).toMatchObject({ events: [{ type: "complaint" }], ignored: 1 });
  });

  it("noemt alleen een weigering van de ontvanger een harde bounce", () => {
    expect(classifySmtpError({ responseCode: 550, command: "RCPT TO", response: "550 no such user" }).kind).toBe("hard_bounce");
    expect(classifySmtpError({ responseCode: 535, command: "AUTH PLAIN" }).kind).toBe("retry");
    expect(classifySmtpError({ responseCode: 451, command: "RCPT TO" }).kind).toBe("retry");
    expect(cleanReason("rejected <x.y@z.nl> because")).toBe("rejected <[adres]> because");
  });
});

describe("bezorging in het platform (ADR 0038)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  const mail = new Picky();
  const admin = { authorization: "Bearer beheerder" };
  const run = () => ctx.app.get(MessagingScheduler).run();
  const subscribe = async (email: string) => {
    await ctx.http.inject({ method: "POST", url: "/v1/mail/subscribe", payload: { email, market: "nl-nl", topics: ["nieuwsbrief"], adult: true, elapsedMs: 5000 } });
    await run();
    const confirm = [...mail.sent].reverse().find((m) => m.to === email);
    const token = decodeURIComponent(/mail\/bevestigen\?t=([A-Za-z0-9_-]+)/.exec(confirm?.html ?? "")?.[1] ?? "");
    if (token) await ctx.http.inject({ method: "POST", url: "/v1/mail/confirm", payload: { token } });
    await run();
  };
  const hook = (provider: string, payload: unknown, key?: string) => {
    const k = key ?? new URL(ctx.app.get(DeliverabilityService).webhookUrls()[provider as "brevo"]).searchParams.get("key")!;
    return ctx.http.inject({ method: "POST", url: `/v1/mail/events/${provider}?key=${k}`, payload: payload as object });
  };
  const active = async (email: string) => (await ctx.app.get(SubscribersService).find(email))?.status === "active";

  beforeAll(async () => { ctx = await createTestApp({ mail }); });
  afterAll(async () => { await ctx.app.close(); });

  it("geeft elke mail een eigen Message-ID en legt het versturen vast", async () => {
    await subscribe("lezer@gmail.test");
    expect(await active("lezer@gmail.test")).toBe(true);
    const welcome = mail.sent.find((m) => m.to === "lezer@gmail.test" && !m.transactional)!;
    expect(welcome.ref).toMatch(/^[0-9a-f-]{36}$/);
    const r = (await ctx.http.inject({ method: "GET", url: "/v1/admin/mail/deliverability?days=7", headers: admin })).json();
    expect(r.totals.sent).toBeGreaterThanOrEqual(2);
    expect(r.byDomain.map((d: { domain: string }) => d.domain)).toContain("gmail.test");
  });

  it("weigert webhooks zonder geldige sleutel en verwerkt een harde bounce van Brevo", async () => {
    const welcome = mail.sent.find((m) => m.to === "lezer@gmail.test" && !m.transactional)!;
    expect((await hook("brevo", { event: "hard_bounce", email: "lezer@gmail.test" }, "x".repeat(32))).statusCode).toBe(404);
    expect((await hook("onbekend", {}, "x".repeat(32))).statusCode).toBe(404);
    const res = await hook("brevo", { event: "hard_bounce", email: "lezer@gmail.test", "message-id": `<${welcome.ref}@kleurhoek.localhost>`, reason: "550 5.1.1 user unknown" });
    expect(res.json()).toEqual({ processed: 1, ignored: 0 });
    expect(await active("lezer@gmail.test")).toBe(false);
    const lookup = (await ctx.http.inject({ method: "GET", url: "/v1/admin/mail/suppressions?email=Lezer@gmail.test", headers: admin })).json();
    expect(lookup.suppression).toMatchObject({ reason: "hard_bounce", by: "brevo" });
    expect(lookup.events.map((e: { type: string }) => e.type)).toContain("hard_bounce");
    // Opnieuw aanmelden: geen bevestigingsmail meer naar een adres dat niet bestaat.
    const before = mail.sent.length;
    await subscribe("lezer@gmail.test");
    expect(mail.sent.length).toBe(before);
    const r = (await ctx.http.inject({ method: "GET", url: "/v1/admin/mail/deliverability?days=7", headers: admin })).json();
    expect(r.totals.hard).toBe(1);
    expect(r.recent[0]).toMatchObject({ type: "hard_bounce", provider: "brevo", domain: "gmail.test", reason: "550 5.1.1 user unknown" });
    expect(r.recent[0].source).toMatch(/^wf:welkom:/);
    expect(JSON.stringify(r)).not.toContain("lezer@");
  });

  it("verwerkt een spamklacht van Scaleway en pauzeert na drie soft bounces", async () => {
    await subscribe("klager@outlook.test");
    await hook("scaleway", { Type: "Notification", Message: JSON.stringify({ type: "email_spam", email_to: "iemand@ergens.test" }) });
    await hook("generic", { type: "complaint", email: "klager@outlook.test" });
    expect(await active("klager@outlook.test")).toBe(false);
    await subscribe("vol@hotmail.test");
    for (let i = 0; i < 2; i++) await hook("brevo", { event: "soft_bounce", email: "vol@hotmail.test", reason: "mailbox full" });
    expect(await active("vol@hotmail.test")).toBe(true);
    await hook("brevo", { event: "soft_bounce", email: "vol@hotmail.test", reason: "mailbox full" });
    expect(await active("vol@hotmail.test")).toBe(false);
    const s = (await ctx.http.inject({ method: "GET", url: "/v1/admin/mail/suppressions?email=vol@hotmail.test", headers: admin })).json().suppression;
    expect(s.reason).toBe("soft_bounce");
    expect(new Date(s.expiresAt).getTime()).toBeGreaterThan(Date.now() + 80 * 86_400_000);
  });

  it("ziet een 550 bij het afgeven als harde bounce, maar een eigen configuratiefout niet", async () => {
    await subscribe("bestaat-niet@voorbeeld.test");
    const s = (await ctx.http.inject({ method: "GET", url: "/v1/admin/mail/suppressions?email=bestaat-niet@voorbeeld.test", headers: admin })).json().suppression;
    expect(s).toMatchObject({ reason: "hard_bounce", by: "smtp" });
    await ctx.http.inject({ method: "POST", url: "/v1/mail/subscribe", payload: { email: "config@voorbeeld.test", market: "nl-nl", topics: ["nieuwsbrief"], adult: true, elapsedMs: 5000 } });
    await run();
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/mail/suppressions?email=config@voorbeeld.test", headers: admin })).json().suppression).toBeNull();
  });

  it("laat beheer een adres blokkeren en weer vrijgeven", async () => {
    expect((await ctx.http.inject({ method: "POST", url: "/v1/admin/mail/suppressions", headers: { authorization: "Bearer analist" }, payload: { email: "a@b.test" } })).statusCode).toBe(403);
    await ctx.http.inject({ method: "POST", url: "/v1/admin/mail/suppressions", headers: admin, payload: { email: "Stop@Mij.test", detail: "Gevraagd per mail" } });
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/mail/suppressions?email=stop@mij.test", headers: admin })).json().suppression.reason).toBe("manual");
    expect((await ctx.http.inject({ method: "DELETE", url: "/v1/admin/mail/suppressions?email=stop@mij.test", headers: admin })).json()).toEqual({ removed: true, reason: "manual" });
    const hooks = (await ctx.http.inject({ method: "GET", url: "/v1/admin/mail/deliverability/webhooks", headers: admin })).json().webhooks;
    expect(hooks.brevo).toMatch(/\/mail\/events\/brevo\?key=[A-Za-z0-9_-]{32}$/);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/mail/deliverability/webhooks", headers: { authorization: "Bearer analist" } })).statusCode).toBe(403);
  });
});
