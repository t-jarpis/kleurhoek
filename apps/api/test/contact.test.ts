import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { eq } from "drizzle-orm";
import { DB, type Database } from "../src/db/database";
import { withTenant } from "../src/db/tenant";
import { looksLikeSpam } from "../src/modules/contact/contact.controller";
import { conversations } from "../src/modules/contact/contact.schema";
import { ContactService } from "../src/modules/contact/contact.service";
import { auditEvents } from "../src/modules/identity/identity.schema";
import { createTestApp, TENANT } from "./app";

let ctx: Awaited<ReturnType<typeof createTestApp>>;
let db: Database;
const admin = { authorization: "Bearer beheerder" };
const form = (over: Record<string, unknown> = {}) => ({
  topic: "question", name: "Sam", email: "Sam@Example.nl", message: "Hoi! Kunnen jullie ook een plaat van een tractor maken?",
  org: "kleurhoek", market: "nl-nl", trap: "", elapsedMs: 12_000, ...over,
});
const send = (body: unknown, ip = "203.0.113.10") => ctx.http.inject({ method: "POST", url: "/v1/contact", payload: body as object, headers: { "cf-connecting-ip": ip } });

beforeAll(async () => { ctx = await createTestApp(); db = ctx.app.get(DB); });
afterAll(async () => { await ctx.app.close(); });

describe("spamfilter", () => {
  it("herkent het verborgen veld, te snel versturen en veel links", () => {
    expect(looksLikeSpam({ message: "Gewone vraag" })).toBe(false);
    expect(looksLikeSpam({ message: "x", trap: "http://spam" })).toBe(true);
    expect(looksLikeSpam({ message: "x", elapsedMs: 800 })).toBe(true);
    expect(looksLikeSpam({ message: "https://a https://b https://c https://d" })).toBe(true);
  });
});

describe("contactformulier", () => {
  it("slaat een bericht op als nieuw gesprek, e-mail in kleine letters", async () => {
    const r = await send(form());
    expect(r.statusCode).toBe(202);
    const inbox = (await ctx.http.inject({ method: "GET", url: "/v1/admin/contact/conversations", headers: admin })).json();
    expect(inbox.counts.new).toBe(1);
    expect(inbox.conversations[0]).toMatchObject({ channel: "web", topic: "question", status: "new", email: "sam@example.nl", market: "nl-NL", preview: expect.stringContaining("tractor") });
  });

  it("doet bij spam alsof het lukte, maar bewaart niets", async () => {
    const before = (await ctx.http.inject({ method: "GET", url: "/v1/admin/contact/unread", headers: admin })).json().count;
    expect((await send(form({ trap: "ik ben een bot" }), "203.0.113.11")).statusCode).toBe(202);
    expect((await send(form({ elapsedMs: 500 }), "203.0.113.11")).statusCode).toBe(202);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/contact/unread", headers: admin })).json().count).toBe(before);
  });

  it("weigert ongeldige invoer", async () => {
    expect((await send(form({ email: "geen-mail" }), "203.0.113.12")).statusCode).toBe(400);
    expect((await send(form({ message: "kort" }), "203.0.113.12")).statusCode).toBe(400);
    expect((await send(form({ topic: "reclame" }), "203.0.113.12")).statusCode).toBe(400);
    expect((await send({ ...form(), extra: 1 }, "203.0.113.12")).statusCode).toBe(400);
  });

  it("begrenst het aantal berichten per bezoeker (5 per uur)", async () => {
    const codes = [];
    for (let i = 0; i < 6; i++) codes.push((await send(form({ trap: "x" }), "203.0.113.99")).statusCode);
    expect(codes.slice(0, 5).every((c) => c === 202)).toBe(true);
    expect(codes[5]).toBe(429);
  });
});

describe("inbox", () => {
  it("is alleen voor wie contact.read heeft", async () => {
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/contact/conversations", headers: { authorization: "Bearer analist" } })).statusCode).toBe(403);
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/contact/conversations" })).statusCode).toBe(401);
  });

  it("notitie, antwoord vastleggen en status, met auditregel zonder persoonsgegevens", async () => {
    const inbox = (await ctx.http.inject({ method: "GET", url: "/v1/admin/contact/conversations?status=new", headers: admin })).json();
    const id = inbox.conversations[0].id as string;
    let c = (await ctx.http.inject({ method: "POST", url: `/v1/admin/contact/conversations/${id}/messages`, headers: admin, payload: { direction: "note", body: "Goed idee voor de volgende ronde" } })).json();
    expect(c.status).toBe("open");
    c = (await ctx.http.inject({ method: "POST", url: `/v1/admin/contact/conversations/${id}/messages`, headers: admin, payload: { direction: "out", body: "Dank je! Hij komt eraan." } })).json();
    expect(c.status).toBe("answered");
    expect(c.messages.map((m: { direction: string }) => m.direction)).toEqual(["in", "note", "out"]);
    c = (await ctx.http.inject({ method: "PUT", url: `/v1/admin/contact/conversations/${id}/status`, headers: admin, payload: { status: "closed" } })).json();
    expect(c.status).toBe("closed");
    const audit = await withTenant(db, TENANT, (tx) => tx.select().from(auditEvents).where(eq(auditEvents.subject, `conversation:${id}`)));
    expect(audit.map((a) => a.action).sort()).toEqual(["contact.note", "contact.reply", "contact.status"]);
    expect(JSON.stringify(audit)).not.toContain("example.nl");
  });

  it("kan een gesprek verwijderen (AVG-verzoek)", async () => {
    await send(form({ email: "weg@example.nl" }), "203.0.113.13");
    const inbox = (await ctx.http.inject({ method: "GET", url: "/v1/admin/contact/conversations?status=new", headers: admin })).json();
    const id = inbox.conversations.find((c: { email: string }) => c.email === "weg@example.nl").id;
    expect((await ctx.http.inject({ method: "DELETE", url: `/v1/admin/contact/conversations/${id}`, headers: admin })).statusCode).toBe(204);
    expect((await ctx.http.inject({ method: "GET", url: `/v1/admin/contact/conversations/${id}`, headers: admin })).statusCode).toBe(404);
  });

  it("ruimt gesprekken op na 12 maanden", async () => {
    await send(form({ email: "oud@example.nl" }), "203.0.113.14");
    await withTenant(db, TENANT, (tx) => tx.update(conversations).set({ lastMessageAt: new Date("2020-01-01") }).where(eq(conversations.email, "oud@example.nl")));
    expect(await ctx.app.get(ContactService).purge()).toBe(1);
    const left = await withTenant(db, TENANT, (tx) => tx.select().from(conversations).where(eq(conversations.email, "oud@example.nl")));
    expect(left).toHaveLength(0);
  });
});

describe("kanalen", () => {
  it("web staat aan, WhatsApp is nog niet gekoppeld en kan niet aan", async () => {
    const list = (await ctx.http.inject({ method: "GET", url: "/v1/admin/contact/channels", headers: admin })).json().channels;
    expect(list).toEqual([
      expect.objectContaining({ slug: "web", enabled: true, connected: true }),
      expect.objectContaining({ slug: "whatsapp", enabled: false, connected: false }),
    ]);
    expect((await ctx.http.inject({ method: "PUT", url: "/v1/admin/contact/channels/whatsapp", headers: admin, payload: { enabled: true } })).statusCode).toBe(400);
  });

  it("webformulier uit = berichten worden geweigerd", async () => {
    await ctx.http.inject({ method: "PUT", url: "/v1/admin/contact/channels/web", headers: admin, payload: { enabled: false } });
    expect((await send(form(), "203.0.113.15")).statusCode).toBe(403);
    await ctx.http.inject({ method: "PUT", url: "/v1/admin/contact/channels/web", headers: admin, payload: { enabled: true } });
    expect((await send(form(), "203.0.113.15")).statusCode).toBe(202);
  });
});

describe("aanvraag eigen omgeving", () => {
  const details = { organization: "Basisschool De Regenboog", kind: "school", code: "De-Regenboog", children: "ongeveer 200" };
  it("bewaart de gegevens van de organisatie bij het gesprek", async () => {
    expect((await send(form({ topic: "organization", details, message: "Wij willen graag een eigen omgeving voor onze school." }), "203.0.113.20")).statusCode).toBe(202);
    const inbox = (await ctx.http.inject({ method: "GET", url: "/v1/admin/contact/conversations?status=new", headers: admin })).json();
    const id = inbox.conversations.find((c: { topic: string }) => c.topic === "organization").id;
    const c = (await ctx.http.inject({ method: "GET", url: `/v1/admin/contact/conversations/${id}`, headers: admin })).json();
    expect(c.details).toEqual({ organization: "Basisschool De Regenboog", kind: "school", code: "de-regenboog", children: "ongeveer 200", website: null });
  });
  it("vraagt gegevens bij een aanvraag, en weigert ze bij andere onderwerpen", async () => {
    expect((await send(form({ topic: "organization" }), "203.0.113.21")).statusCode).toBe(400);
    expect((await send(form({ details }), "203.0.113.21")).statusCode).toBe(400);
    expect((await send(form({ topic: "organization", details: { ...details, code: "geen spaties" } }), "203.0.113.21")).statusCode).toBe(400);
  });
});
