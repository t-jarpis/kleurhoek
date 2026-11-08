"use strict";
/**
 * Leeftijd uit de tekening zelf (ADR 0094): het aantal vlakken bepaalt de leeftijd van een kleurplaat.
 * Andere soorten (knippen, bouwen, werkbladen) en platen zonder vlakken houden hun eigen leeftijd.
 */
const AGE_BANDS = [
  { age: "2-4", max: 12 },
  { age: "4-6", max: 30 },
  { age: "6-9", max: 80 },
  { age: "9+", max: 200 },
  { age: "12+", max: Infinity },
];

/** De leeftijd die bij een plaat hoort, of null als de regel niet geldt. */
function ageFor(p) {
  if ((p.kind ?? "kleurplaat") !== "kleurplaat" || !p.regionCount) return null;
  return AGE_BANDS.find((b) => p.regionCount <= b.max).age;
}

module.exports = { AGE_BANDS, ageFor };
