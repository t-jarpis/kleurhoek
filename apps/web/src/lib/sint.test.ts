import { describe, expect, it } from "vitest";
import type { PlateItem } from "./types";
import { hasSintCalendar, intocht, sintDates, sintDoors, sintOpen, sintTeaser } from "./sint";

const plate = (slug: string, holiday: string | null = "sinterklaas") => ({ slug, holiday, name: slug, svg: `/v1/assets/plates/${slug}/1.svg` }) as unknown as PlateItem;

describe("Sinterklaaskalender (ADR 0065)", () => {
  it("de intocht is de eerste zaterdag na 11 november", () => {
    expect(intocht(2023)).toBe("2023-11-18");
    expect(intocht(2024)).toBe("2024-11-16");
    expect(intocht(2025)).toBe("2025-11-15");
    expect(intocht(2026)).toBe("2026-11-14");
  });
  it("loopt tot pakjesavond: 5 december in Nederland, 6 december in België", () => {
    expect(sintDates(2026, "nl-nl")).toHaveLength(22);
    expect(sintDates(2026, "nl-nl").at(-1)).toBe("2026-12-05");
    expect(sintDates(2026, "nl-BE").at(-1)).toBe("2026-12-06");
    expect(hasSintCalendar("de-de")).toBe(false);
  });
  it("opent elke dag een deurtje en telt de nachtjes", () => {
    expect(sintOpen("2026-11-01", "nl-nl")).toMatchObject({ open: 0, daysToStart: 13 });
    expect(sintOpen("2026-11-14", "nl-nl")).toMatchObject({ open: 1, today: 1, nightsTo: 21 });
    expect(sintOpen("2026-12-05", "nl-nl")).toMatchObject({ open: 22, today: 22, nightsTo: null });
    expect(sintOpen("2026-12-20", "nl-nl")).toMatchObject({ open: 22, today: null });
    expect(sintOpen("2027-03-01", "nl-nl")).toMatchObject({ year: 2026, open: 22, today: null });
  });
  it("begint met de intocht en eindigt met pakjesavond", () => {
    const plates = [plate("kat", null), plate("pakjesavond"), plate("schoen"), plate("stoomboot-komt-aan"), plate("piet-met-de-zak")];
    const doors = sintDoors(plates, 22);
    expect(doors[0]!.plate.slug).toBe("stoomboot-komt-aan");
    expect(doors.at(-1)).toMatchObject({ day: 22, plate: { slug: "pakjesavond" } });
    expect(doors.map((d) => d.plate.slug)).not.toContain("kat");
  });
  it("de voorpagina wijst ernaar tot en met pakjesavond", () => {
    expect(sintTeaser("2026-11-02", "nl-nl")).toBe(true);
    expect(sintTeaser("2026-12-06", "nl-nl")).toBe(false);
    expect(sintTeaser("2026-12-06", "nl-be")).toBe(true);
    expect(sintTeaser("2026-11-02", "fr-fr")).toBe(false);
  });
});
