import { describe, expect, it } from "vitest";
import { edgeAllowed } from "./edge";

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
