"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const data = require("..");

test("elke plaat heeft minstens één leerdoel", () => {
  for (const p of data.plates()) {
    const g = data.learningGoals({ slug: p.slug, kind: p.kind, category: p.category, holiday: p.holiday, continent: p.world?.continent ?? null });
    assert.ok(g.length > 0, p.slug);
    for (const x of g) assert.ok(data.GOALS.includes(x));
  }
});

test("rekenen en taal komen uit de naam", () => {
  const g = (slug, kind = "werkblad", category = "leren") => data.learningGoals({ slug, kind, category });
  assert.ok(g("rekenen-tafel-van-3").includes("rekenen"));
  assert.ok(g("woordzoeker-dieren").includes("taal"));
  assert.ok(!g("kasteel", "kleurplaat", "sprookjes").includes("rekenen"));
});

test("overrides in goals-overrides.json bestaan als plaat en als doel", () => {
  const o = require("../goals-overrides.json");
  const slugs = new Set(data.plates().map((p) => p.slug));
  for (const [slug, v] of Object.entries(o)) {
    assert.ok(slugs.has(slug), slug);
    for (const x of [...(v.add ?? []), ...(v.remove ?? [])]) assert.ok(data.GOALS.includes(x), x);
  }
});

test("elk leerdoel heeft een naam in elke taal", () => {
  const { GOAL_NAMES } = require("../goals");
  for (const [lang, names] of Object.entries(GOAL_NAMES)) for (const g of data.GOALS) assert.ok(names[g], `${lang}:${g}`);
});
