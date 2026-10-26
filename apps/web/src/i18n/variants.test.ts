import { describe, expect, it } from "vitest";
import { messages } from "./nl";

describe("tekstvarianten per markt (ADR 0047)", () => {
  it("geeft en-US Amerikaanse spelling en Letter-papier", () => {
    const us = messages("en-us");
    expect(us.metaPlate("Cat", us.kindNames.kleurplaat!)).toBe("Coloring page Cat: color in online or print on letter paper for free.");
    expect(messages("en-gb").kindNames.kleurplaat).toBe("Colouring page");
    expect(messages("en").kindNames.kleurplaat).toBe("Colouring page");
  });
  it("schrijft voor de-CH geen ß en valt anders terug op de taal", () => {
    expect(JSON.stringify(Object.values(messages("de-ch")).filter((v) => typeof v === "string"))).not.toContain("ß");
    expect(messages("es-es")).toBe(messages("es"));
    expect(messages("xx")).toBe(messages("nl"));
  });
  it("maakt titels voor platen en thema's in de taal van de markt", () => {
    const de = messages("de-de");
    expect(de.metaPlateTitle("Katze", de.kindNames.kleurplaat!)).toBe("Katze – Malvorlage");
    expect(messages("fr-fr").metaThemeTitle("Paris")).toBe("Coloriages Paris");
  });
});
