import { startMockOidc, type MockUser } from "@t-jarpis/auth/testing";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { MemoryTransport } from "../src/modules/messaging/mailer";
import { MessagingScheduler } from "../src/modules/messaging/messaging.scheduler";
import { ADMIN_ORG, AUDIENCE, createTestApp, SITE_ORG } from "./app";

const OWNER: MockUser = { sub: "z-mail-eigenaar", name: "Thijs", email: "thijs@example.test", organizationId: ADMIN_ORG };
const PARENT: MockUser = { sub: "z-mail-ouder", name: "Ouder", email: "Ouder@Example.test", organizationId: SITE_ORG };

let op: Awaited<ReturnType<typeof startMockOidc>>;
let ctx: Awaited<ReturnType<typeof createTestApp>>;
const mail = new MemoryTransport();
const bearer = async (user: MockUser) => ({ authorization: `Bearer ${await op.accessToken(300, user)}` });
const as = async (user: MockUser, method: "GET" | "POST" | "PUT" | "DELETE", url: string, payload?: unknown) =>
  ctx.http.inject({ method, url, headers: await bearer(user), ...(payload !== undefined ? { payload: payload as object } : {}) });
const pub = (method: "GET" | "POST" | "PUT", url: string, payload?: unknown) => ctx.http.inject({ method, url, ...(payload !== undefined ? { payload: payload as object } : {}) });
const run = (now?: Date) => ctx.app.get(MessagingScheduler).run(now);
const linkIn = (html: string, re: RegExp) => decodeURIComponent(re.exec(html)?.[1] ?? "");

beforeAll(async () => {
  op = await startMockOidc({ clientId: "admin", audience: AUDIENCE, user: OWNER });
  ctx = await createTestApp({ oidc: { issuer: op.issuer, bootstrap: [OWNER.sub] }, mail });
});
afterAll(async () => { await ctx.app.close(); await op.close(); });

describe("mail (ADR 0037)", () => {
  let prefToken = "";

  it("meldt aan met bevestiging, zonder te verraden of een adres bekend is", async () => {
    const bad = await pub("POST", "/v1/mail/subscribe", { email: "a@b.test", market: "nl-nl", topics: ["nieuwe-platen"], adult: false });
    expect(bad.statusCode).toBe(400);
    const ok = await pub("POST", "/v1/mail/subscribe", { email: " Juf@School.test ", market: "nl-nl", topics: ["nieuwe-platen", "feestdagen"], adult: true, elapsedMs: 5000 });
    expect(ok.statusCode).toBe(202);
    // Spam: zelfde antwoord, geen mail.
    expect((await pub("POST", "/v1/mail/subscribe", { email: "bot@spam.test", market: "nl-nl", topics: ["nieuwsbrief"], adult: true, trap: "x" })).statusCode).toBe(202);
    await run();
    expect(mail.sent.map((m) => m.to)).toEqual(["juf@school.test"]);
    const confirm = mail.sent[0]!;
    expect(confirm.transactional).toBe(true);
    expect(confirm.unsubscribeUrl).toBeUndefined();
    expect(confirm.subject).toMatch(/Bevestig/);
    const token = linkIn(confirm.html, /mail\/bevestigen\?t=([A-Za-z0-9_-]+)/);
    expect(token.length).toBeGreaterThan(20);
    // Nog een keer aanmelden binnen 10 minuten: geen tweede mail.
    await pub("POST", "/v1/mail/subscribe", { email: "juf@school.test", market: "nl-nl", topics: ["nieuwsbrief"], adult: true });
    await run();
    expect(mail.sent).toHaveLength(1);

    expect((await pub("POST", "/v1/mail/confirm", { token: "x".repeat(30) })).json().status).toBe("invalid");
    expect((await pub("POST", "/v1/mail/confirm", { token })).json().status).toBe("confirmed");
    expect((await pub("POST", "/v1/mail/confirm", { token })).json().status).toBe("invalid");
  });

  it("stuurt een welkomstmail met platen, een afmeldheader en voorkeurlinks", async () => {
    await run();
    // Valt er een feestdag binnen twee weken, dan stuurt die workflow ook iets. Hier gaat het om de welkomstmail.
    const welcome = mail.sent.find((m) => m.subject === "Welkom bij Kleurhoek")!;
    expect(welcome).toBeDefined();
    expect(welcome.unsubscribeUrl).toMatch(/^https:\/\/www\.kleurhoek\.test\/mail\/afmelden\?t=/);
    expect(welcome.html).toMatch(/\/v1\/assets\/plates\/[a-z0-9-]+\/\d+\.png/);
    prefToken = linkIn(welcome.html, /mail\?t=([A-Za-z0-9_.-]+)/);
    const prefs = (await pub("GET", `/v1/mail/preferences?t=${prefToken}`)).json();
    expect(prefs).toMatchObject({ email: "j***@school.test", topics: ["nieuwe-platen", "feestdagen"] });
    // Opnieuw verwerken stuurt niets dubbel.
    const before = mail.sent.length;
    await run();
    expect(mail.sent).toHaveLength(before);
  });

  it("levert een PNG van een plaat voor mails", async () => {
    const plates = (await pub("GET", "/v1/markets/nl-NL/plates")).json().items as { svg: string }[];
    const res = await pub("GET", plates[0]!.svg.replace(/\.svg$/, ".png"));
    expect(res.statusCode).toBe(200);
    expect(res.headers["content-type"]).toBe("image/png");
    expect(res.rawPayload.subarray(1, 4).toString()).toBe("PNG");
  }, 30_000);

  it("verstuurt een campagne alleen aan het gekozen onderwerp, en niet na afmelden", async () => {
    // Een ouder meldt zich aan vanuit het account voor de nieuwsbrief: meteen actief.
    const me = await as(PARENT, "PUT", "/v1/me/mail", { topics: ["nieuwsbrief"], market: "nl-nl" });
    expect(me.json().topics).toEqual(["nieuwsbrief"]);
    await run();
    const sentBefore = mail.sent.length;

    const size = await as(OWNER, "POST", "/v1/admin/mail/campaigns/audience", { topics: ["nieuwsbrief"], markets: null });
    expect(size.json().size).toBe(1);
    const c = (await as(OWNER, "POST", "/v1/admin/mail/campaigns", { name: "Herfst", template: "nieuwsbrief", audience: { topics: ["nieuwsbrief"], markets: null } })).json();
    expect((await as(OWNER, "POST", "/v1/admin/mail/campaigns", { name: "Fout", template: "bevestigen", audience: { topics: ["nieuwsbrief"], markets: null } })).statusCode).toBe(400);
    const sent = await as(OWNER, "POST", `/v1/admin/mail/campaigns/${c.id}/schedule`, { at: null });
    expect(sent.json()).toMatchObject({ status: "sent", recipients: 1 });
    await run();
    expect(mail.sent.slice(sentBefore).map((m) => m.to)).toEqual(["ouder@example.test"]);

    // Afmelden via de link van de juf; daarna stuurt een workflow haar niets meer.
    expect((await pub("POST", "/v1/mail/unsubscribe", { t: prefToken })).json().status).toBe("removed");
    expect((await pub("GET", `/v1/mail/preferences?t=${prefToken}`)).statusCode).toBe(404);
    const overview = (await as(OWNER, "GET", "/v1/admin/mail")).json();
    expect(overview.subscribers.active).toBe(1);
    expect(overview.sending).toEqual({ bulk: true, transactional: true });
  });

  it("bewaart templates en workflows met controle, en geeft een voorbeeld", async () => {
    const t = (await as(OWNER, "GET", "/v1/admin/mail/templates/nieuwe-platen")).json().template;
    const preview = await as(OWNER, "POST", "/v1/admin/mail/preview", { template: { name: t.name, kind: t.kind, subject: t.subject, preheader: t.preheader, blocks: t.blocks }, market: "nl-nl" });
    expect(preview.statusCode).toBe(200);
    expect(preview.json().html).toContain("Nieuw deze week");
    expect((await as(OWNER, "PUT", "/v1/admin/mail/templates/bevestigen", { name: "x", kind: "system", subject: { nl: "x" }, preheader: {}, blocks: [{ id: "a", type: "text", text: { nl: "geen link" } }] })).statusCode).toBe(400);
    expect((await as(OWNER, "DELETE", "/v1/admin/mail/templates/welkom")).statusCode).toBe(400);
    expect((await as(OWNER, "DELETE", "/v1/admin/mail/templates/nieuwe-platen")).statusCode).toBe(409);
    // Een workflow zonder filter op onderwerp mag niet (behalve na aanmelden).
    const noFilter = await as(OWNER, "PUT", "/v1/admin/mail/workflows/test", { name: "Test", enabled: true, trigger: { type: "plates_published", min: 1 }, steps: [{ type: "send", template: "nieuwe-platen" }] });
    expect(noFilter.statusCode).toBe(400);
    const ok = await as(OWNER, "PUT", "/v1/admin/mail/workflows/test", { name: "Test", enabled: false, trigger: { type: "plates_published", min: 1 }, steps: [{ type: "filter", topics: ["nieuwe-platen"] }, { type: "wait", hours: 2 }, { type: "send", template: "nieuwe-platen" }] });
    expect(ok.statusCode).toBe(200);
    expect((await as(OWNER, "GET", "/v1/admin/mail/workflows")).json().workflows.map((w: { slug: string }) => w.slug)).toContain("test");
  });

  it("vergeet het abonnement als het account verdwijnt", async () => {
    expect((await as(PARENT, "DELETE", "/v1/me")).statusCode).toBe(204);
    expect((await as(OWNER, "GET", "/v1/admin/mail")).json().subscribers.active).toBe(0);
  });
});
