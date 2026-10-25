import { describe, expect, it } from "vitest";
import { inCountry, isVisible, nextOccurrence, seasonFor, type HolidayDef } from "./availability.domain";

const h = (over: Partial<HolidayDef>): HolidayDef => ({ slug: "x", sortOrder: 0, countries: ["NL"], fixed: null, dates: {}, leadDays: 0, afterDays: 0, approximate: false, label: null, ...over });

describe("isVisible", () => {
  it("toont een plaat zonder regel overal", () => expect(isVisible(undefined, "DE", "2026-10-22")).toBe(true));
  it("only_in toont alleen in de genoemde landen", () => {
    const rule = { plateSlug: "kroon", mode: "only_in" as const, countries: ["NL"], validFrom: null, validTo: null };
    expect(isVisible(rule, "NL", "2026-04-20")).toBe(true);
    expect(isVisible(rule, "be", "2026-04-20")).toBe(false);
  });
  it("everywhere_except verbergt in de genoemde landen", () => {
    const rule = { plateSlug: "p", mode: "everywhere_except" as const, countries: ["US"], validFrom: null, validTo: null };
    expect(isVisible(rule, "US", "2026-01-01")).toBe(false);
    expect(isVisible(rule, "NL", "2026-01-01")).toBe(true);
  });
  it("respecteert begin- en einddatum", () => {
    const rule = { plateSlug: "p", mode: "everywhere_except" as const, countries: [], validFrom: "2026-12-01", validTo: "2026-12-26" };
    expect(isVisible(rule, "NL", "2026-11-30")).toBe(false);
    expect(isVisible(rule, "NL", "2026-12-24")).toBe(true);
    expect(isVisible(rule, "NL", "2026-12-27")).toBe(false);
  });
});

describe("nextOccurrence", () => {
  it("vaste datum dit jaar of volgend jaar", () => {
    expect(nextOccurrence(h({ fixed: [12, 5] }), "2026-10-22")).toBe("2026-12-05");
    expect(nextOccurrence(h({ fixed: [4, 27] }), "2026-10-22")).toBe("2027-04-27");
  });
  it("telt de dagen erna nog mee", () => {
    expect(nextOccurrence(h({ fixed: [12, 25], afterDays: 1 }), "2026-12-26")).toBe("2026-12-25");
  });
  it("wisselende datum uit de tabel, null als het jaar ontbreekt", () => {
    const divali = h({ dates: { 2026: "2026-11-08", 2027: "2027-10-29" } });
    expect(nextOccurrence(divali, "2026-11-09")).toBe("2027-10-29");
    expect(nextOccurrence(h({ dates: { 2026: "2026-03-20" } }), "2026-10-22")).toBeNull();
  });
});

describe("seasonFor", () => {
  const holidays = [
    h({ slug: "halloween", fixed: [10, 31], leadDays: 14 }),
    h({ slug: "divali", dates: { 2026: "2026-11-08" }, leadDays: 21 }),
    h({ slug: "sintmaarten", fixed: [11, 11], leadDays: 18 }),
    h({ slug: "kerst", fixed: [12, 25], leadDays: 24 }),
    h({ slug: "thanksgiving", countries: ["US"], dates: { 2026: "2026-11-26" }, leadDays: 14 }),
  ];
  const spans = [{ slug: "herfst", countries: ["NL"], from: [9, 22] as [number, number], to: [11, 20] as [number, number], plateSlugs: ["egel"] }];

  it("geeft op 22 oktober in NL het juiste seizoen", () => {
    const v = seasonFor(holidays, spans, "NL", "2026-10-22");
    expect(v.active.map((x) => x.slug)).toEqual(["halloween", "divali"]);
    expect(v.soon.map((x) => x.slug)).toEqual(["sintmaarten"]); // Kerst (64 dagen) valt buiten de horizon van 60
    expect(v.spans.map((x) => x.slug)).toEqual(["herfst"]);
  });
  it("toont geen feestdagen van een ander land", () => {
    expect(seasonFor(holidays, spans, "NL", "2026-11-20").active.map((x) => x.slug)).not.toContain("thanksgiving");
    expect(seasonFor(holidays, spans, "US", "2026-11-20").active.map((x) => x.slug)).toEqual(["thanksgiving"]);
  });
});

describe("feestdagen per land (ADR 0040)", () => {
  const sint: HolidayDef = { slug: "sinterklaas", sortOrder: 0, countries: ["NL", "BE"], fixed: [12, 5], dates: {}, leadDays: 24, afterDays: 0, approximate: false, label: null, overrides: { BE: { fixed: [12, 6] } } };
  const vader: HolidayDef = { slug: "vaderdag", sortOrder: 1, countries: ["NL", "BE"], fixed: null, dates: { 2026: "2026-06-21" }, leadDays: 14, afterDays: 0, approximate: false, label: null, overrides: { BE: { dates: { "2026": "2026-06-14" } } } };
  const koning: HolidayDef = { slug: "koningsdag", sortOrder: 2, countries: ["NL"], fixed: [4, 27], dates: {}, leadDays: 21, afterDays: 0, approximate: false, label: null };
  it("gebruikt de datum van het land", () => {
    expect(nextOccurrence(inCountry(sint, "BE"), "2026-11-20")).toBe("2026-12-06");
    expect(nextOccurrence(inCountry(sint, "NL"), "2026-11-20")).toBe("2026-12-05");
    expect(nextOccurrence(inCountry(vader, "be"), "2026-06-01")).toBe("2026-06-14");
  });
  it("toont alleen feestdagen van het land", () => {
    const be = seasonFor([sint, vader, koning], [], "BE", "2026-04-20");
    expect([...be.active, ...be.soon].map((h) => h.slug)).not.toContain("koningsdag");
    expect(seasonFor([sint], [], "BE", "2026-12-01").active[0]!.date).toBe("2026-12-06");
  });
  it("geeft alle feestdagen in een land zonder kalender (kleurhoek.com)", () => {
    const fi = seasonFor([sint, koning], [], "FI", "2026-04-20");
    expect(fi.active.map((h) => h.slug)).toContain("koningsdag");
  });
});
