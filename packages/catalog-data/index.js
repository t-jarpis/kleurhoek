"use strict";
const fs = require("node:fs");
const path = require("node:path");
const read = (f) => JSON.parse(fs.readFileSync(path.join(__dirname, f), "utf8"));

/** Standaard voor kleurplaten: zonder knip- of bouwwerk, met potloden (stiften mag ook). */
const DEFAULT_MATERIALS = [{ slug: "kleurpotloden" }, { slug: "stiften", optional: true }];
const normalize = (p) => ({
  kind: "kleurplaat", height: 200, minutes: null, adultHelp: false, paperGsm: null, difficulty: null, pages: [],
  ...p,
  materials: (p.materials ?? DEFAULT_MATERIALS).map((m) => ({ optional: false, ...m })),
});

module.exports = {
  KINDS: ["kleurplaat", "knipplaat", "bouwplaat", "spel", "vouwblad", "werkblad", "sjabloon", "kaart", "tekenles"],
  /** Groepen voor het filter op de site: kleurplaten, knutselen, leren en spelen, tekenen. */
  KIND_GROUPS: { kleurplaat: "kleurplaten", knipplaat: "knutselen", bouwplaat: "knutselen", vouwblad: "knutselen", kaart: "knutselen", spel: "leren", werkblad: "leren", tekenles: "tekenen", sjabloon: "tekenen" },
  plates: () => read("plates.json").map(normalize),
  categories: () => read("categories.json"),
  ages: () => read("ages.json"),
  continents: () => read("continents.json"),
  holidays: () => read("holidays.json"),
  seasons: () => read("seasons.json"),
  colors: () => read("colors.json"),
  materials: () => read("materials.json"),
  plateSvg: (slug) => fs.readFileSync(path.join(__dirname, "plates", `${slug}.svg`), "utf8").trim(),
  /** Extra pagina n (2, 3 …) van een plaat: plates/<slug>.p<n>.svg. */
  pageSvg: (slug, n) => fs.readFileSync(path.join(__dirname, "plates", `${slug}.p${n}.svg`), "utf8").trim(),
};
