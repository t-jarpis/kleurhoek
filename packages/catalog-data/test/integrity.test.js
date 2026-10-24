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
  const mats = new Set(data.materials().map((m) => m.slug));
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
    assert.ok(data.KINDS.includes(p.kind), `${p.slug}: onbekende soort`);
    assert.match(svg, new RegExp(`viewBox="0 0 200 ${p.height}"`), `${p.slug}: hoogte klopt niet met de SVG`);
    for (const m of p.materials) assert.ok(mats.has(m.slug), `${p.slug}: onbekend materiaal ${m.slug}`);
    if (p.kind !== "kleurplaat") assert.ok(p.i18n.nl.steps?.length, `${p.slug}: ${p.kind} zonder stappen`);
    // Knippen hoort bij deze soorten; vouwen bij vouwbladen (ADR 0027).
    if (["knipplaat", "bouwplaat", "sjabloon", "kaart"].includes(p.kind)) assert.match(svg, /class="cut"/, `${p.slug}: ${p.kind} zonder kniplijn`);
    if (p.kind === "vouwblad") assert.match(svg, /class="fold"/, `${p.slug}: vouwblad zonder vouwlijn`);
    assert.ok(p.difficulty === null || [1, 2, 3].includes(p.difficulty), `${p.slug}: moeilijkheid 1, 2 of 3`);
    if (p.kind === "werkblad" && /antwoord/i.test(p.i18n.nl.steps?.join(" ") ?? "")) assert.ok(p.pages.some((x) => x.role === "antwoorden"), `${p.slug}: werkblad noemt antwoorden maar heeft geen antwoordblad`);
    assert.equal((p.i18n.nl.pageTitles ?? []).length, p.pages.length, `${p.slug}: titel per extra pagina`);
    p.pages.forEach((page, i) => {
      const extra = data.pageSvg(p.slug, i + 2);
      assert.match(extra, new RegExp(`viewBox="0 0 200 ${page.height}"`), `${p.slug}: hoogte pagina ${i + 2}`);
      assert.doesNotMatch(extra, /<script|on\w+=|href=/i, `${p.slug}: pagina ${i + 2} bevat script of link`);
    });
  }
  assert.ok(plates.length >= 218, `${plates.length} platen`);
  assert.ok(plates.some((p) => p.kind !== "kleurplaat"), "minstens één knutselwerk");
});
