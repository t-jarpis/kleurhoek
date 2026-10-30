import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { TogetherService } from "../src/modules/together/together.service";
import { createTestApp } from "./app";
import { PlateImages } from "../src/modules/storefront/plate-images";

let ctx: Awaited<ReturnType<typeof createTestApp>>;
beforeAll(async () => { process.env.TOGETHER_CLEANUP_MS = "0"; ctx = await createTestApp(); });
afterAll(async () => { await ctx.app.close(); });
const req = (method: "GET" | "POST", url: string, payload?: object) => ctx.http.inject({ method, url, ...(payload ? { payload } : {}) });

describe("samen kleuren (ADR 0060)", () => {
  let code = "";
  it("maakt een kamer met een code van vier letters", async () => {
    const res = await req("POST", "/v1/together/rooms", { market: "nl-nl", slug: "kat", version: 1 });
    expect(res.statusCode).toBe(201);
    code = res.json().code;
    expect(code).toMatch(/^[A-HJ-NP-Z]{4}$/);
    expect((await req("GET", `/v1/together/rooms/${code.toLowerCase()}`)).json()).toMatchObject({ code, market: "nl-nl", slug: "kat", version: 1 });
    expect((await req("GET", "/v1/together/rooms/ZZZZ")).statusCode).toBe(404);
  });

  it("deelt handelingen tussen twee apparaten, in volgorde", async () => {
    const send = await req("POST", `/v1/together/rooms/${code}/ops`, { client: "opa12345", ops: [{ t: "f", id: "opa12345:1", r: 3, v: "#ff0000", p: null }, { t: "s", id: "opa12345:2", r: 3, b: "stift", c: "#00ff00", w: 1, pts: [1, 2, 0.5, 3, 4, 0.5] }] });
    expect(send.statusCode).toBe(200);
    const got = (await req("GET", `/v1/together/rooms/${code}/ops?client=kind1234&after=0&wait=0`)).json();
    expect(got.ops.map((o: { op: { t: string } }) => o.op.t)).toEqual(["f", "s"]);
    expect(got.ops[0].client).toBe("opa12345");
    expect(got.others).toBe(0);
    // Opa vraagt ook: nu is het kind er.
    const opa = (await req("GET", `/v1/together/rooms/${code}/ops?client=opa12345&after=${got.last}&wait=0`)).json();
    expect(opa).toMatchObject({ ops: [], others: 1, last: got.last });
  });

  it("weigert alles wat geen kleurhandeling is", async () => {
    const bad = [
      { client: "opa12345", ops: [{ t: "f", id: "opa12345:3", r: 1, v: "javascript:alert(1)" }] },
      { client: "opa12345", ops: [{ t: "s", id: "opa12345:4", r: 1, b: "bom", c: "#000000", w: 1, pts: [] }] },
      { client: "OPA", ops: [{ t: "c", id: "opa12345:5" }] },
      { client: "opa12345", ops: [{ t: "f", id: "opa12345:6", r: 1, v: "#000000", extra: 1 }] },
    ];
    for (const b of bad) expect((await req("POST", `/v1/together/rooms/${code}/ops`, b)).statusCode).toBe(400);
  });

  it("stopt pas als er een half uur niemand meer is", async () => {
    const svc = ctx.app.get(TogetherService);
    await svc.age(code, 29 * 60_000);
    expect(await svc.cleanup()).toBe(0);
    expect((await req("GET", `/v1/together/rooms/${code}`)).statusCode).toBe(200);
    await svc.age(code, 31 * 60_000);
    expect((await req("GET", `/v1/together/rooms/${code}`)).statusCode).toBe(404);
    expect(await svc.cleanup()).toBe(1);
  });
});

describe("Pinterest-plaatje (ADR 0057)", () => {
  it("maakt een staand, ingekleurd plaatje met alleen een bekend domein", async () => {
    const slug = (await req("GET", "/v1/markets/nl-NL/plates")).json().items.find((p: { kind: string }) => p.kind === "kleurplaat").slug;
    const res = await req("GET", `/v1/markets/nl-NL/plates/${slug}/pin.png?domain=evil.example`);
    expect(res.statusCode).toBe(200);
    expect(res.headers["content-type"]).toBe("image/png");
    const png = res.rawPayload;
    expect(png.readUInt32BE(16)).toBe(1000);
    expect(png.readUInt32BE(20)).toBe(1500);
    expect((await req("GET", "/v1/markets/nl-NL/plates/bestaat-niet/pin.png")).statusCode).toBe(404);
    // 4:5 als JPEG voor Instagram en Facebook (ADR 0063).
    const jpg = await req("GET", `/v1/markets/nl-NL/plates/${slug}/post.jpg`);
    expect(jpg.headers["content-type"]).toBe("image/jpeg");
    expect(jpg.rawPayload.subarray(0, 3).toString("hex")).toBe("ffd8ff");
    expect((await req("GET", `/v1/markets/nl-NL/plates/${slug}/iets.gif`)).statusCode).toBe(404);
    // De naam en het domein staan erop: resvg tekent tekst (in productie ging dat mis met de native versie).
    const images = ctx.app.get(PlateImages);
    expect(images.textWorks()).toBe(true);
    expect(images.textWorks(["ПППП", "дддд"])).toBe(true);
    expect(images.textWorks(["ŁŁŁŁ", "őőőő"])).toBe(true);
    expect(images.textWorks(["ΣΣΣΣ", "ωωωω"])).toBe(true);
  }, 30_000);
});
