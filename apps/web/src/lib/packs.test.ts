import { describe, expect, it } from "vitest";
import { packs, packSlug } from "./packs";
import type { PlateItem, PlateKind, Taxonomy } from "./types";

const plate = (slug: string, kind: PlateKind, category = "dieren", age = "4-6", goals: string[] = []): PlateItem => ({ slug, name: slug, category, age, world: null, holiday: null, svg: `/${slug}.svg`, kind, goals });
const taxonomy: Taxonomy = {
  categories: [{ slug: "dieren", color: "#000", name: "Dieren" }, { slug: "ruimte", color: "#000", name: "Ruimte" }],
  ages: [{ slug: "9+", level: 4, strokeWidth: 2, name: "9+ jaar", hint: null }, { slug: "4-6", level: 2, strokeWidth: 3, name: "4-6 jaar", hint: null }],
  continents: [], holidays: [], goals: [{ slug: "tellen", name: "Tellen tot 10" }], learningFilters: true,
};

describe("lespakketten (ADR 0059)", () => {
  it("maakt een pakket met eerst kleuren, dan leren en knutselen", () => {
    const set = [plate("a", "werkblad", "dieren", "4-6", ["tellen"]), plate("b", "kleurplaat"), plate("c", "knipplaat"), plate("d", "kleurplaat"), plate("e", "spel"), plate("f", "kleurplaat")];
    const [p] = packs(set, taxonomy);
    expect(p!.slug).toBe("dieren-4-6");
    expect(p!.plates.map((x) => x.kind)).toEqual(["kleurplaat", "kleurplaat", "kleurplaat", "werkblad", "spel", "knipplaat"]);
    expect(p!.goals).toEqual(["Tellen tot 10"]);
  });
  it("slaat te kleine of eenzijdige sets over", () => {
    expect(packs([plate("a", "kleurplaat"), plate("b", "kleurplaat"), plate("c", "werkblad")], taxonomy)).toEqual([]);
    expect(packs(Array.from({ length: 6 }, (_, i) => plate(`k${i}`, "kleurplaat")), taxonomy)).toEqual([]);
  });
  it("heeft een veilig adres voor 9+", () => expect(packSlug("ruimte", "9+")).toBe("ruimte-9plus"));
});
