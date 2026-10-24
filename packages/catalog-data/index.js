"use strict";
const fs = require("node:fs");
const path = require("node:path");
const read = (f) => JSON.parse(fs.readFileSync(path.join(__dirname, f), "utf8"));
const textLayer = require("./text-layer");
const goals = require("./goals");
let overrides;

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
  /** Leerdoelen (ADR 0036). */
  GOALS: goals.GOALS,
  goalName: goals.goalName,
  learningGoals: (p) => goals.learningGoals(p, overrides ??= read("goals-overrides.json")),
  categories: () => read("categories.json"),
  ages: () => read("ages.json"),
  continents: () => read("continents.json"),
  holidays: () => read("holidays.json"),
  seasons: () => read("seasons.json"),
  colors: () => read("colors.json"),
  materials: () => read("materials.json"),
  plateSvg: (slug) => fs.readFileSync(path.join(__dirname, "plates", `${slug}.svg`), "utf8").trim(),
  /** Extra pagina n (2, 3 …) van een plaat: plates/<slug>.p<n>.svg. */
  /** Talen met een woordenlijst voor de teksten in platen (texts/<taal>.json). */
  textLanguages: () => (fs.existsSync(path.join(__dirname, "texts")) ? fs.readdirSync(path.join(__dirname, "texts")) : []).filter((f) => /^[a-z]{2}\.json$/.test(f)).map((f) => f.slice(0, 2)).sort(),
  /** Woordenlijst bronzin (nl) → vertaling voor de teksten in platen (ADR 0029). */
  texts: (language) => (fs.existsSync(path.join(__dirname, "texts", `${language}.json`)) ? read(`texts/${language}.json`) : {}),
  ...textLayer,
  pageSvg: (slug, n) => fs.readFileSync(path.join(__dirname, "plates", `${slug}.p${n}.svg`), "utf8").trim(),
};
