import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { normalizeCidr } from "../src/modules/operations/site-access.service";
import { createTestApp, INGEST_KEY } from "./app";

describe("normalizeCidr", () => {
  it("accepteert losse adressen en blokken, IPv4 en IPv6", () => {
    expect(normalizeCidr("203.0.113.7")).toBe("203.0.113.7/32");
    expect(normalizeCidr(" 203.0.113.0/24 ")).toBe("203.0.113.0/24");
    expect(normalizeCidr("2A02:A46:1::/64")).toBe("2a02:a46:1::/64");
    expect(normalizeCidr("2a02:a46:1::5")).toBe("2a02:a46:1::5/128");
  });
  it("weigert onzin en te brede blokken", () => {
    for (const bad of ["", "abc", "1.2.3", "1.2.3.4/33", "1.2.3.4/4", "0.0.0.0/0", "::/0", "1.2.3.4/x", "1.2.3.4/24/1"]) expect(normalizeCidr(bad)).toBeNull();
  });
});

describe("toegang tot de website", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });

  const put = (payload: unknown, auth = "Bearer beheerder") =>
    ctx.http.inject({ method: "PUT", url: "/v1/admin/site-access", payload: payload as object, headers: { authorization: auth } });
  const internal = (key = INGEST_KEY) => ctx.http.inject({ method: "GET", url: "/v1/internal/site-access", headers: { "x-ingest-key": key } });

  it("staat standaard uit", async () => {
    expect((await internal()).json()).toEqual({ enabled: false, cidrs: [], loginEnabled: true });
  });

  it("mag niet aan met een lege lijst, en alleen met het juiste recht", async () => {
    expect((await put({ enabled: true })).statusCode).toBe(400);
    expect((await put({ enabled: true, entries: [{ cidr: "203.0.113.7", label: "Thuis" }] }, "Bearer analist")).statusCode).toBe(403);
    expect((await put({ entries: [{ cidr: "nonsens", label: "x" }] })).statusCode).toBe(400);
  });

  it("slaat op, normaliseert en geeft de website alleen de blokken", async () => {
    const r = await put({ enabled: true, entries: [{ cidr: "203.0.113.7", label: "Thuis" }, { cidr: "2001:db8:1::/64", label: "Thuis IPv6" }] });
    expect(r.statusCode).toBe(200);
    expect(r.json()).toMatchObject({ enabled: true, updatedBy: "user-beheerder", entries: [{ cidr: "203.0.113.7/32", label: "Thuis", addedBy: "user-beheerder" }, { cidr: "2001:db8:1::/64" }] });
    expect((await internal()).json()).toEqual({ enabled: true, cidrs: ["203.0.113.7/32", "2001:db8:1::/64"], loginEnabled: true });
    expect((await ctx.http.inject({ method: "GET", url: "/v1/admin/site-access", headers: { authorization: "Bearer analist" } })).statusCode).toBe(403);
  });

  it("weigert de interne route zonder geldige sleutel", async () => {
    expect((await internal("fout")).statusCode).toBe(401);
  });

  it("zet inloggen op de website uit en weer aan (ADR 0042)", async () => {
    const org = async () => (await ctx.http.inject({ method: "GET", url: "/v1/internal/organizations/kleurhoek", headers: { "x-ingest-key": INGEST_KEY } })).json().features.accounts;
    const before = await org();
    expect((await put({ loginEnabled: false }, "Bearer analist")).statusCode).toBe(403);
    const r = await put({ loginEnabled: false });
    expect(r.statusCode).toBe(200);
    expect(r.json().loginEnabled).toBe(false);
    expect((await internal()).json().loginEnabled).toBe(false);
    expect(await org()).toBe(false);
    await put({ loginEnabled: true });
    expect(await org()).toBe(before);
  });
});
