import { describe, expect, it } from "vitest";
import { edgeAllowed, fromWorker } from "./edge";

const secret = "s".repeat(48);

describe("edgeAllowed", () => {
  it("laat alles door zonder EDGE_SECRET (lokaal)", () => {
    expect(edgeAllowed("/nl-nl", null, undefined)).toBe(true);
    expect(edgeAllowed("/nl-nl", null, "")).toBe(true);
  });
  it("vereist de juiste header als EDGE_SECRET gezet is", () => {
    expect(edgeAllowed("/nl-nl", null, secret)).toBe(false);
    expect(edgeAllowed("/nl-nl", "fout", secret)).toBe(false);
    expect(edgeAllowed("/nl-nl", `${secret}x`, secret)).toBe(false);
    expect(edgeAllowed("/nl-nl", secret.slice(1), secret)).toBe(false);
    expect(edgeAllowed("/nl-nl", secret, secret)).toBe(true);
  });
  it("houdt /healthz open voor de health checks", () => {
    expect(edgeAllowed("/healthz", null, secret)).toBe(true);
  });
});

describe("fromWorker", () => {
  it("vertrouwt de Worker alleen met het juiste geheim", () => {
    expect(fromWorker("geheim-van-de-worker", "geheim-van-de-worker", true)).toBe(true);
    expect(fromWorker("fout", "geheim-van-de-worker", true)).toBe(false);
    expect(fromWorker(null, "geheim-van-de-worker", true)).toBe(false);
  });
  it("zonder geheim: lokaal wel, in productie nooit", () => {
    expect(fromWorker(null, undefined, false)).toBe(true);
    expect(fromWorker("x", undefined, true)).toBe(false);
  });
});
