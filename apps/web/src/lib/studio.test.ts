import { describe, expect, it } from "vitest";
import { ERASER, layout, paint, progress, strokeWidth } from "./studio";

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
});
