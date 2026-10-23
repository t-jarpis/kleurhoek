import { describe, expect, it, vi } from "vitest";

vi.mock("next/headers", () => ({ cookies: async () => ({ get: () => undefined, set: () => undefined }) }));

describe("versleutelde stap-cookie", () => {
  it("leest terug wat erin ging en weigert gewijzigde of verlopen waarden", async () => {
    process.env.LOGIN_SECRET = "s".repeat(40);
    const { seal, unseal } = await import("@/lib/state");
    const token = seal({ ar: "V2_1234567", org: "kleurhoek", back: "https://dev.kleurhoek.nl", step: "code", sid: "1", st: "geheim" });
    expect(unseal(token)).toMatchObject({ ar: "V2_1234567", step: "code", st: "geheim" });
    const tampered = token.slice(0, -2) + (token.endsWith("A") ? "BB" : "AA");
    expect(unseal(tampered)).toBeNull();
    vi.useFakeTimers(); vi.setSystemTime(Date.now() + 16 * 60_000);
    expect(unseal(token)).toBeNull();
    vi.useRealTimers();
    process.env.LOGIN_SECRET = "t".repeat(40);
    expect(unseal(token)).toBeNull();
  });
});

describe("terug na uitloggen", () => {
  it("alleen naar eigen domeinen", async () => {
    const { allowedReturn } = await import("@/lib/return");
    expect(allowedReturn("https://dev.kleurhoek.nl/nl-nl")).toBe("https://dev.kleurhoek.nl/nl-nl");
    expect(allowedReturn("https://school-dev.kleurhoek.nl/")).toBe("https://school-dev.kleurhoek.nl/");
    expect(allowedReturn("https://kleurhoek.nl.evil.example/")).toBeNull();
    expect(allowedReturn("http://dev.kleurhoek.nl/")).toBeNull();
    expect(allowedReturn("javascript:alert(1)")).toBeNull();
    expect(allowedReturn(null)).toBeNull();
  });
});

describe("WebAuthn-omzetting", () => {
  it("base64url heen en terug, ook met de publicKey-omhulling van Zitadel", async () => {
    const { fromB64, toB64, requestOptions } = await import("@/lib/webauthn");
    const bytes = new Uint8Array([0, 255, 62, 63, 1]).buffer;
    expect(toB64(fromB64(toB64(bytes)!))).toBe(toB64(bytes));
    const o = requestOptions({ publicKey: { challenge: "AP8-Pw", rpId: "kleurhoek.nl", allowCredentials: [{ type: "public-key", id: "AQ" }] } });
    expect(new Uint8Array(o.challenge as ArrayBuffer)).toEqual(new Uint8Array([0, 255, 62, 63]));
    expect(o.rpId).toBe("kleurhoek.nl");
    expect(new Uint8Array(o.allowCredentials![0]!.id as ArrayBuffer)).toEqual(new Uint8Array([1]));
  });
});
