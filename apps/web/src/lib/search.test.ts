import { describe, expect, it } from "vitest";
import { fold, matcher, worthKeeping } from "./search";

describe("zoeken in het raster (ADR 0084)", () => {
  it("negeert hoofdletters, accenten en leestekens", () => {
    expect(fold("Éénhoorn!")).toBe("eenhoorn");
    expect(matcher("EENHOORN")!("Eénhoorn in het bos")).toBe(true);
  });
  it("vindt elk woord, ook enkelvoud bij meervoud", () => {
    const m = matcher("paarden kerst")!;
    expect(m("Paard met slee · Kerstmis")).toBe(true);
    expect(m("Paard in de wei")).toBe(false);
    expect(matcher("dinosaurussen")!("Dinosaurus")).toBe(true);
  });
  it("niets te zoeken is geen filter", () => { expect(matcher("  ?! ")).toBeNull(); });
  it("bewaart geen e-mail, adres of nummer", () => {
    expect(worthKeeping("draak")).toBe(true);
    expect(worthKeeping("ab")).toBe(false);
    expect(worthKeeping("piet@mail.nl")).toBe(false);
    expect(worthKeeping("0612345678")).toBe(false);
    expect(worthKeeping("www.x.nl")).toBe(false);
  });
});
