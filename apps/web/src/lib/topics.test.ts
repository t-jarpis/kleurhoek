import { describe, expect, it } from "vitest";
import { messages } from "../i18n/nl";
import { inTopic, topics, topicTitle } from "./topics";
import type { PlateItem, Taxonomy } from "./types";

const plate = (p: Partial<PlateItem>): PlateItem => ({ slug: "x", name: "X", category: "dieren", age: "3-5", world: null, holiday: null, svg: "/x.svg", kind: "kleurplaat", goals: [], ...p });
const taxonomy: Taxonomy = {
  categories: [{ slug: "dieren", color: "#000", name: "Dieren" }, { slug: "ruimte", color: "#000", name: "Ruimte" }],
  ages: [{ slug: "3-5", level: 1, strokeWidth: 3, name: "3-5 jaar", hint: null }], continents: [{ slug: "europa", color: "#000", name: "Europa" }],
  holidays: [{ slug: "kerst", name: "Kerst" }], goals: [], learningFilters: false,
};
const plates = [plate({ slug: "kat" }), plate({ slug: "boom", holiday: "kerst", kind: "knipplaat", world: { continent: "europa", country: null } })];

describe("onderwerppagina's (ADR 0055)", () => {
  it("maakt alleen pagina's voor onderwerpen met platen", () => {
    const g = topics(plates, taxonomy, messages("nl-nl"));
    expect(g.onderwerp.map((x) => [x.path, x.count])).toEqual([["/onderwerp/dieren", 2]]);
    expect(g.feestdag.map((x) => x.path)).toEqual(["/feestdag/kerst"]);
    expect(g.soort.map((x) => x.slug)).toEqual(["kleurplaat", "knutselen"]);
    expect(g.werelddeel.map((x) => x.count)).toEqual([1]);
  });
  it("groepeert soorten zoals het filter", () => {
    expect(inTopic(plates[1]!, "soort", "knutselen")).toBe(true);
    expect(inTopic(plates[0]!, "soort", "knutselen")).toBe(false);
  });
  it("heeft in elke markt een kop in de eigen taal", () => {
    expect(topicTitle(messages("nl-nl"), { dim: "onderwerp", slug: "dieren", name: "Dieren" })).toBe("Kleurplaten dieren");
    expect(topicTitle(messages("en-gb"), { dim: "soort", slug: "kleurplaat", name: "x" })).not.toBe("x");
  });
});
