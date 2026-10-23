import { describe, expect, it } from "vitest";
import { buildPolicy, ipAllowed } from "./site-access";

describe("ipAllowed", () => {
  const p = buildPolicy(true, ["203.0.113.7/32", "198.51.100.0/24", "2001:db8:1::/64"]);
  it("laat alles door als de lijst uit staat", () => {
    expect(ipAllowed(buildPolicy(false, []), null)).toBe(true);
  });
  it("laat alleen adressen uit de lijst door", () => {
    expect(ipAllowed(p, "203.0.113.7")).toBe(true);
    expect(ipAllowed(p, "203.0.113.8")).toBe(false);
    expect(ipAllowed(p, "198.51.100.200")).toBe(true);
    expect(ipAllowed(p, "2001:db8:1::abcd")).toBe(true);
    expect(ipAllowed(p, "2001:db8:2::1")).toBe(false);
  });
  it("weigert zonder of met ongeldig IP", () => {
    expect(ipAllowed(p, null)).toBe(false);
    expect(ipAllowed(p, "geen-ip")).toBe(false);
  });
});
