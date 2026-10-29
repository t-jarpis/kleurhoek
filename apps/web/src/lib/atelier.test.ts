import { describe, expect, it } from "vitest";
import { composeInner, deriveShared, EMPTY_ART, toShared, type SharedOp, fillCss, fillOp, gradientValue, harmony, hexToHsl, hslToHex, normalizeArt, parseFill, patternValue, pickColor, replay, strokePath, undoLast, type Art, type Stroke } from "./atelier";

const INNER = `<rect class="r" data-i="0" x="0" y="0" width="100" height="100"/><circle class="r" data-i="1" cx="50" cy="50" r="20"/><path class="l" d="M0 0 L10 10"/>`;
const stroke = (r: number, b: Stroke["b"] = "potlood"): Stroke => ({ t: "s", r, b, c: "#ff0000", w: 1, pts: [10, 10, 0.5, 20, 20, 0.5, 30, 25, 0.5] });

describe("Atelier (ADR 0056)", () => {
  it("leest effen kleuren, verlopen en patronen, en negeert onzin", () => {
    expect(parseFill("#aabbcc")).toEqual({ kind: "effen", a: "#aabbcc" });
    expect(parseFill(gradientValue("#000000", "#ffffff"))).toEqual({ kind: "verloop", a: "#000000", b: "#ffffff" });
    expect(parseFill(patternValue("stippen", "#111111", "#eeeeee"))?.kind).toBe("patroon");
    expect(parseFill("javascript:alert(1)")).toBeNull();
    expect(parseFill("p:bom:#111111:#eeeeee")).toBeNull();
    expect(fillCss(gradientValue("#000000", "#ffffff"), "s1", 4)).toBe("url(#s1-f4)");
    expect(pickColor(patternValue("strepen", "#123456", "#eeeeee"))).toBe("#123456");
  });

  it("zet streken direct na hun vlak, binnen dat vlak, met de lijn er weer over", () => {
    const art: Art = { ...EMPTY_ART, ops: [stroke(0)] };
    const out = composeInner(INNER, art, {}, "s1");
    const rect = out.indexOf('data-i="0"'), clip = out.indexOf('clip-path="url(#s1-c0)"'), circle = out.indexOf('data-i="1"');
    expect(rect).toBeGreaterThan(-1);
    expect(clip).toBeGreaterThan(rect);
    expect(circle).toBeGreaterThan(clip);
    expect(out).toContain('<clipPath id="s1-c0"><use href="#s1-r0"/></clipPath>');
    expect(out).toContain('class="kh-ro" pointer-events="none"');
    // De kopieën hebben geen nummer, zodat tikken altijd het echte vlak raakt.
    expect(out.match(/data-i="0"/g)).toHaveLength(1);
  });

  it("geeft licht en schaduw van de zon aan gekleurde vlakken", () => {
    const art: Art = { ...EMPTY_ART, sun: { a: 225, s: 0.6 } };
    const out = composeInner(INNER, art, { 1: "#00ff00" }, "s1");
    expect(out).toContain('id="s1-sun"');
    expect(out.match(/class="kh-sun"/g)).toHaveLength(1);
  });

  it("de gum haalt alleen weg wat eronder ligt", () => {
    const art: Art = { ...EMPTY_ART, ops: [stroke(0), stroke(0, "gum"), stroke(0, "stift")] };
    const out = composeInner(INNER, art, {}, "s1");
    const mask = out.indexOf('mask="url(#s1-m0-1)"');
    expect(mask).toBeGreaterThan(-1);
    // De stiftstreek na de gum staat buiten het masker.
    expect(out.lastIndexOf('fill="#ff0000" fill-opacity="1"')).toBeGreaterThan(out.indexOf("</g>", mask));
  });

  it("maakt van punten een vlak, ook zonder pen", () => {
    expect(strokePath(stroke(0))).toMatch(/^M[\d.]+ [\d.]+ Q.*Z$/);
    expect(strokePath({ ...stroke(0), pts: [] })).toBe("");
  });

  it("maakt vullen en streken ongedaan in de goede volgorde", () => {
    let fills = {}; let art: Art = EMPTY_ART;
    const a = fillOp(fills, 1, "#111111"); fills = a.fills; art = { ...art, ops: [...art.ops, a.op] };
    art = { ...art, ops: [...art.ops, stroke(1)] };
    const b = fillOp(fills, 1, "#222222"); fills = b.fills; art = { ...art, ops: [...art.ops, b.op] };
    let u = undoLast(art, fills)!; expect(u.fills[1]).toBe("#111111");
    u = undoLast(u.art, u.fills)!; expect(u.art.ops).toHaveLength(1);
    u = undoLast(u.art, u.fills)!; expect(u.fills[1]).toBeUndefined();
    expect(undoLast(u.art, u.fills)).toBeNull();
  });

  it("speelt het werk af van leeg tot klaar", () => {
    const a = fillOp({ 0: "#999999" }, 1, "#111111");
    const art: Art = { ...EMPTY_ART, ops: [a.op, stroke(1), stroke(0)] };
    const frames = replay(art, a.fills);
    expect(frames[0]!.fills).toEqual({ 0: "#999999" });
    expect(frames[0]!.art.ops).toHaveLength(0);
    expect(frames.at(-1)!.fills).toEqual(a.fills);
    expect(frames.at(-1)!.art.ops).toHaveLength(3);
    expect(replay({ ...EMPTY_ART, ops: Array.from({ length: 500 }, () => stroke(0)) }, {}, 60)).toHaveLength(61);
    // Een lange streek groeit over een paar beelden.
    const long: Stroke = { ...stroke(0), pts: Array.from({ length: 60 }, (_, i) => [i, i, 0.5]).flat() };
    const grow = replay({ ...EMPTY_ART, ops: [long] }, {});
    expect(grow.length).toBeGreaterThan(3);
    expect((grow[1]!.art.ops[0] as Stroke).pts.length).toBeLessThan(long.pts.length);
  });

  it("bouwt een gedeelde plaat op uit de lijst van beide apparaten", () => {
    const log: SharedOp[] = [
      { t: "f", id: "a:1", r: 1, v: "#111111", p: null },
      { ...stroke(1), id: "b:1" },
      { t: "f", id: "b:2", r: 1, v: "#222222", p: null },
      { t: "x", id: "b:3", ref: "b:2" },
    ];
    expect(deriveShared(log).fills).toEqual({ 1: "#111111" });
    expect(deriveShared(log).ops).toHaveLength(2);
    expect(deriveShared([...log, { t: "c", id: "a:2" }, { t: "f", id: "a:3", r: 2, v: "#333333", p: null }]).fills).toEqual({ 2: "#333333" });
    let n = 0;
    const start = toShared({ 4: "#444444" }, { ...EMPTY_ART, ops: [stroke(4), { t: "f", r: 4, v: "#444444", p: null }] }, () => `a:${++n}`);
    expect(start.map((o) => o.t)).toEqual(["f", "s"]);
    expect(deriveShared(start).fills).toEqual({ 4: "#444444" });
  });

  it("vertrouwt de opslag niet blind", () => {
    const art = normalizeArt({ ops: [stroke(0), { t: "s", r: 0, b: "kwast", c: "#fff", w: 1, pts: [] }, { t: "f", r: 1, v: "#111111", p: null }], sun: { a: "x" }, lines: { kind: "geen" } });
    expect(art.ops).toHaveLength(2);
    expect(art.sun).toBeNull();
    expect(art.lines.kind).toBe("geen");
    expect(normalizeArt("rommel")).toEqual(EMPTY_ART);
  });

  it("rekent kleuren heen en terug en vindt passende kleuren", () => {
    expect(hslToHex(...hexToHsl("#3366cc"))).toBe("#3366cc");
    expect(harmony("#ff0000")[0]).toBe("#00ffff");
  });
});
