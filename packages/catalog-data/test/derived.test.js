"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { plates, COUNTRY_CODES, countryName } = require("..");

test("elk land bij een plaat heeft een ISO-code (ADR 0094)", () => {
  const missing = [...new Set(plates().map((p) => p.world?.country).filter(Boolean))].filter((c) => !COUNTRY_CODES[c]);
  assert.deepEqual(missing, []);
});

test("landnamen in de taal van de markt", () => {
  assert.equal(countryName("Verenigde Staten", "en"), "United States");
  assert.equal(countryName("Brazilië", "de"), "Brasilien");
  assert.equal(countryName("Brazilië", "nl"), "Brazilië");
  assert.equal(countryName("Atlantis", "en"), "Atlantis");
});

test("leeftijd van kleurplaten volgt uit het aantal vlakken (ADR 0094)", () => {
  const { ageFor } = require("..");
  const wrong = plates().filter((p) => { const a = ageFor(p); return a && a !== p.age; }).map((p) => `${p.slug}: ${p.age} ≠ ${ageFor(p)}`);
  assert.deepEqual(wrong, []);
});
