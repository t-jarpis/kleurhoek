"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const data = require("..");

test("elke plaat is compleet en consistent", () => {
  const plates = data.plates();
  const cats = new Set(data.categories().map((c) => c.slug));
  const ages = new Set(data.ages().map((a) => a.slug));
  const conts = new Set(data.continents().map((c) => c.slug));
  const hols = new Set(data.holidays().map((h) => h.slug));
  const slugs = new Set();
  for (const p of plates) {
    assert.ok(!slugs.has(p.slug), `dubbele slug ${p.slug}`); slugs.add(p.slug);
    assert.match(p.slug, /^[a-z0-9-]+$/);
    assert.ok(cats.has(p.category), `${p.slug}: onbekende categorie`);
    assert.ok(ages.has(p.age), `${p.slug}: onbekende leeftijd`);
    if (p.world) assert.ok(conts.has(p.world.continent), `${p.slug}: onbekend werelddeel`);
    if (p.holiday) assert.ok(hols.has(p.holiday), `${p.slug}: onbekende feestdag`);
    const svg = data.plateSvg(p.slug);
    const regions = (svg.match(/class="r"/g) || []).length;
    assert.equal(regions, p.regionCount, `${p.slug}: aantal vlakken`);
    assert.equal(p.colorByNumber.codes.length, p.regionCount, `${p.slug}: kleurcodes`);
    const numbered = [...p.colorByNumber.codes].filter((c) => c !== "-").length;
    assert.equal(p.colorByNumber.labels.length, numbered, `${p.slug}: nummers`);
    assert.ok(p.i18n.nl && p.i18n.nl.name, `${p.slug}: Nederlandse naam`);
    assert.doesNotMatch(svg, /<script|on\w+=/i, `${p.slug}: SVG bevat script`);
  }
  assert.equal(plates.length, 65);
});
