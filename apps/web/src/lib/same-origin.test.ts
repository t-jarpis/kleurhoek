import { describe, expect, it } from "vitest";
import { sameOrigin } from "./same-origin";

const req = (headers: Record<string, string>) => new Request("https://www.kleurhoek.nl/auth/logout", { method: "POST", headers });

describe("sameOrigin", () => {
  it("accepteert alleen verzoeken van de eigen site", () => {
    expect(sameOrigin(req({ "sec-fetch-site": "same-origin" }))).toBe(true);
    expect(sameOrigin(req({ "sec-fetch-site": "cross-site", origin: "https://www.kleurhoek.nl" }))).toBe(false);
    expect(sameOrigin(req({ "sec-fetch-site": "same-site" }))).toBe(false);
    expect(sameOrigin(req({ origin: "https://www.kleurhoek.nl" }))).toBe(true);
    expect(sameOrigin(req({ origin: "https://evil.example" }))).toBe(false);
    expect(sameOrigin(req({}))).toBe(false);
  });
});
