"use strict";
const test = require("node:test");
const assert = require("node:assert");
const { plateTexts, localizeSvg, isNeutral } = require("../text-layer");

const svg = '<svg viewBox="0 0 200 280"><text class="tx" x="100" y="16" font-size="11" text-anchor="middle">School</text>'
  + '<text class="tip" x="37" y="274">knippen</text><text class="tx" x="5" y="5" font-size="6">3 + 4 =</text>'
  + '<text class="tx" x="5" y="9" font-size="6">A</text><text class="tx" x="5" y="9" font-size="6">Kip &amp; ei</text></svg>';

test("neutrale teksten (cijfers, sommen, één letter) hoeven niet vertaald", () => {
  assert.ok(isNeutral("3 + 4 ="));
  assert.ok(isNeutral("A"));
  assert.ok(!isNeutral("knippen"));
  assert.deepStrictEqual(plateTexts(svg), ["School", "knippen", "Kip & ei"]);
});

test("vertaalt, verkleint een langere tekst en meldt wat ontbreekt", () => {
  const dict = { School: "Schule", knippen: "ausschneiden" };
  const { svg: out, missing, scaled } = localizeSvg(svg, (t) => dict[t]);
  assert.match(out, />Schule<\/text>/);
  assert.match(out, /class="tip" x="37" y="274" style="font-size:[\d.]+px">ausschneiden</);
  assert.deepStrictEqual(missing, ["Kip & ei"]);
  assert.strictEqual(scaled.length, 1);
  assert.ok(scaled[0].to < 6);
});

test("escapet de vertaling", () => {
  const { svg: out } = localizeSvg(svg, (t) => (t === "Kip & ei" ? "Huhn & Ei <3" : t));
  assert.match(out, />Huhn &amp; Ei &lt;3</);
});
