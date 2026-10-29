import { describe, expect, it } from "vitest";
import { adventDoors, doorOrder, openUntil } from "./advent";
import type { PlateItem } from "./types";

const plate = (slug: string, holiday: string | null = null, category = "feest"): PlateItem => ({ slug, name: slug, category, age: "4-6", world: null, holiday, svg: `/${slug}.svg`, kind: "kleurplaat", goals: [] });
const winter = ["sneeuwpop", "ijsbeer", "muts-en-wanten", "pinguins", "sleetje-trekken", "schaatser", "poolvos", "iglo", "noorderlicht", "winterjas", "sneeuwuil", "skier", "hert"].map((s) => plate(s, null, "natuur"));
const nl = [...winter, plate("pakjesboot", "sinterklaas"), plate("schoen-zetten", "sinterklaas"), plate("kerstboom-versieren", "kerst"), plate("kerstsokken", "kerst"), plate("kerstmarkt", "kerst"),
  ...Array.from({ length: 12 }, (_, i) => plate(`dier-${i}`, null, "dieren"))];

describe("aftelkalender (ADR 0058)", () => {
  it("heeft 24 verschillende platen, Sinterklaas eerst en de mooiste kerstplaat op 24 december", () => {
    const { doors, target } = adventDoors(nl, 2026);
    expect(target).toBe("kerst");
    expect(doors.map((d) => d.day)).toEqual(Array.from({ length: 24 }, (_, i) => i + 1));
    expect(new Set(doors.map((d) => d.plate.slug)).size).toBe(24);
    expect(doors[0]!.plate.holiday).toBe("sinterklaas");
    expect(doors[23]!.plate.slug).toBe("kerstboom-versieren");
  });
  it("telt af naar oud en nieuw waar geen kerst is", () => {
    const tr = [...winter, plate("aftellen-naar-nieuwjaar", "oudnieuw"), ...Array.from({ length: 12 }, (_, i) => plate(`d-${i}`, null, "dieren"))];
    const { doors, target } = adventDoors(tr, 2026);
    expect(target).toBe("oudnieuw");
    expect(doors.at(-1)!.plate.slug).toBe("aftellen-naar-nieuwjaar");
    expect(doors.every((d) => d.plate.holiday !== "sinterklaas")).toBe(true);
  });
  it("opent in december één deurtje per dag", () => {
    expect(openUntil("2026-11-20")).toMatchObject({ open: 0, daysToStart: 11 });
    expect(openUntil("2026-12-05")).toMatchObject({ open: 5, nightsTo: 20 });
    expect(openUntil("2026-12-28")).toMatchObject({ open: 24, nightsTo: null });
    expect(openUntil("2026-12-28", "oudnieuw")).toMatchObject({ nightsTo: 4 });
    expect(openUntil("2027-03-01")).toMatchObject({ year: 2026, open: 24 });
  });
  it("zet de deurtjes door elkaar, elk jaar anders", () => {
    expect([...doorOrder(2026)].sort((a, b) => a - b)).toEqual(Array.from({ length: 24 }, (_, i) => i + 1));
    expect(doorOrder(2026)).not.toEqual(doorOrder(2027));
  });
});
