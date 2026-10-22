import { describe, expect, it } from "vitest";
import { BOOK_MAX, ERASER, FRIDGE_MAX, hang, layout, paint, parseBook, progress, strokeWidth, togglePick } from "./studio";

describe("kleurstudio", () => {
  it("telt goed gekleurde nummers, ongevoelig voor hoofdletters", () => {
    const labels = [{ region: 0, number: 1, x: 0, y: 0, size: 5 }, { region: 2, number: 2, x: 0, y: 0, size: 5 }];
    const palette = [{ number: 1, hex: "#E2483D" }, { number: 2, hex: "#2fa45a" }];
    expect(progress(labels, palette, { 0: "#e2483d" })).toEqual({ ok: 1, total: 2, done: false });
    expect(progress(labels, palette, { 0: "#e2483d", 2: "#2fa45a" }).done).toBe(true);
  });
  it("gummen verwijdert een kleur en onthoudt de vorige", () => {
    expect(paint({ 3: "#fff000" }, 3, ERASER)).toEqual({ next: {}, prev: "#fff000" });
    expect(paint({}, 1, "#000").next).toEqual({ 1: "#000" });
  });
  it("maakt ruimte voor tekst en leerblad", () => {
    expect(layout({ name: "", learn: false, word: "de kat", question: null }).height).toBe(200);
    const l = layout({ name: "Sam", learn: true, word: "de kat", question: "Hoeveel?" });
    expect(l).toMatchObject({ height: 314, nameY: 200, learnY: 240, questionY: 286 });
  });
  it("kiest de lijndikte bij de leeftijd tenzij anders gekozen", () => {
    expect(strokeWidth("auto", 3.4)).toBe(3.4);
    expect(strokeWidth("dun", 3.4)).toBe(1.7);
  });
  it("begint onder een hogere knutselplaat", () => {
    expect(layout({ name: "Sam", learn: false, word: null, question: null, height: 270 })).toMatchObject({ nameY: 270, height: 310 });
  });
  it("maakt ruimte voor een kleurenlijst onderaan", () => {
    const l = layout({ name: "", learn: false, word: null, question: null, legend: 6 });
    expect(l).toMatchObject({ height: 232, legendY: 200 });
    expect(l.legendStep).toBeCloseTo(26);
  });
  it("de koelkast houdt het nieuwste werk en hooguit 24 platen", () => {
    const item = (n: number) => ({ id: String(n), slug: "kat", version: 1, fills: {}, name: "", date: "" });
    let list = Array.from({ length: FRIDGE_MAX }, (_, i) => item(i));
    list = hang(list, item(99));
    expect(list).toHaveLength(FRIDGE_MAX);
    expect(list[0]!.id).toBe("99");
    expect(list.at(-1)!.id).toBe(String(FRIDGE_MAX - 2));
  });
  it("leest de platen voor het boekje veilig uit de URL", () => {
    expect(parseBook("kat,vis,kat,../etc,UIL, slak")).toEqual(["kat", "vis", "slak"]);
    expect(parseBook(undefined)).toEqual([]);
    expect(parseBook(Array.from({ length: 50 }, (_, i) => `p${i}`).join(","))).toHaveLength(BOOK_MAX);
  });
  it("zet platen aan en uit in de keuze", () => {
    expect(togglePick(["kat"], "vis")).toEqual(["kat", "vis"]);
    expect(togglePick(["kat", "vis"], "kat")).toEqual(["vis"]);
  });
});
