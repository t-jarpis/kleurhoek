import { describe, expect, it } from "vitest";
import { decodeFills, encodeFills, shareUrl, whatsappUrl } from "./share";

const plain = (v: string | undefined) => (v && v.startsWith("#") ? v : v ? "#123456" : null);

describe("delen", () => {
  it("zet vlakkleuren in een korte code en weer terug", () => {
    const fills = { 0: "#E2483D", 1: "#f2c618", 3: "#e2483d" };
    const k = encodeFills(fills, 5, plain)!;
    expect(k).toBe("e2483d.f2c618~01-0");
    expect(decodeFills(k, 5)).toEqual({ 0: "#e2483d", 1: "#f2c618", 3: "#e2483d" });
  });
  it("neemt de eigen tekst (vlak na de laatste) en verloop als effen kleur mee zoals de pipet", () => {
    expect(encodeFills({ 0: "#000000", 2: "#ffffff" }, 2, plain)).toBe("000000~0");
    expect(encodeFills({ 0: "verloop:#111111" }, 1, plain)).toBe("123456~0");
  });
  it("geeft niets bij een lege plaat", () => {
    expect(encodeFills({}, 4, plain)).toBeNull();
  });
  it("weigert kapotte of te lange codes", () => {
    expect(decodeFills("e2483d~0", 0)).toBeNull();
    expect(decodeFills("e2483d~1", 3)).toBeNull();
    expect(decodeFills("zzzzzz~0", 3)).toBeNull();
    expect(decodeFills("<script>", 3)).toBeNull();
    expect(decodeFills(null, 3)).toBeNull();
  });
  it("bouwt deellinks zonder andere parameters", () => {
    expect(shareUrl("https://www.kleurhoek.nl/platen/kat?samen=ABCD#x")).toBe("https://www.kleurhoek.nl/platen/kat?d=1");
    expect(shareUrl("https://www.kleurhoek.nl/platen/kat", "e2483d~0")).toBe("https://www.kleurhoek.nl/platen/kat?k=e2483d%7E0&d=1");
    expect(whatsappUrl("Kijk!", "https://x.nl/a")).toBe("https://wa.me/?text=Kijk%21+https%3A%2F%2Fx.nl%2Fa");
  });
});
