import { describe, expect, it } from "vitest";
import { bestMarket } from "./markets";

const live = ["nl-nl", "nl-be", "fr-be", "en-gb"];

describe("beste markt (ADR 0040, 0044)", () => {
  it("kiest op land en browsertaal", () => {
    expect(bestMarket("BE", "fr-BE,fr", live)).toBe("fr-be");
    expect(bestMarket("NL", "nl", live)).toBe("nl-nl");
    expect(bestMarket("FI", "fi,en;q=0.8", live)).toBe("en-gb");
    expect(bestMarket("DE", "de,nl;q=0.5", live)).toBe("nl-nl");
  });
  it("valt terug op Engels als land en taal niet bestaan", () => {
    expect(bestMarket("ES", "es-ES,es", live)).toBe("en-gb");
    expect(bestMarket(null, null, live)).toBe("en-gb");
    expect(bestMarket("BE", "es", live)).toBe("nl-be");
    expect(bestMarket("ES", "es", ["nl-nl", "nl-be"])).toBe("nl-nl");
  });
});
