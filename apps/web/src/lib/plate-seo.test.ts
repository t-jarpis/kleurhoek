import { describe, expect, it } from "vitest";
import { messages } from "../i18n/nl";
import { kindFor } from "../i18n/plate-meta";
import { plateExtra } from "./plate-seo";
import type { Taxonomy } from "./types";

const taxonomy = { categories: [{ slug: "dinos", name: "Dino's" }], ages: [{ slug: "4-6", name: "4–6 jaar" }], continents: [], holidays: [], goals: [] } as unknown as Taxonomy;

describe("titels en beschrijvingen van platen (ADR 0085)", () => {
  const t = messages("nl-nl");
  it("zet de soort achter de naam, zoals mensen zoeken, met gratis printen", () => {
    expect(t.plateTitle("Fruitsmoothie", kindFor("Fruitsmoothie", t.kindNames.kleurplaat!))).toBe("Fruitsmoothie kleurplaat – gratis printen");
  });
  it("noemt de soort niet twee keer", () => {
    const kind = kindFor("Kaart: welkom thuis!", t.kindNames.kaart!);
    expect(kind).toBe("");
    expect(t.plateTitle("Kaart: welkom thuis!", kind)).toBe("Kaart: welkom thuis! – gratis printen");
    expect(t.metaPlate("Kaart: welkom thuis!", kind)).toBe("Kaart: welkom thuis!: gratis online inkleuren of printen op A4.");
    expect(t.metaPlateTitle("Kaart: welkom thuis!", kind)).toBe("Kaart: welkom thuis!");
  });
  it("voegt onderwerp, leeftijd en andere namen toe aan de beschrijving", () => {
    const d = t.metaPlate("Dino met lange nek", "Kleurplaat", plateExtra({ category: "dinos", age: "4-6", also: ["langnek", "brachiosaurus"] }, taxonomy));
    expect(d).toBe("Kleurplaat Dino met lange nek: gratis online inkleuren of printen op A4. Dino's · 4–6 jaar. Ook bekend als: langnek, brachiosaurus.");
  });
  it("werkt in elke taal en zonder soort", () => {
    const en = messages("en-gb");
    expect(en.plateTitle("Cat", "Colouring page")).toBe("Cat – colouring page, free to print");
    expect(messages("en-us").metaPlate("Cat", "", { also: ["kitty"] })).toBe("Cat: color in online or print on letter paper for free. Also known as: kitty.");
  });
});
