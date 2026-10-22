"use strict";
const fs = require("node:fs");
const path = require("node:path");
const read = (f) => JSON.parse(fs.readFileSync(path.join(__dirname, f), "utf8"));
module.exports = {
  plates: () => read("plates.json"),
  categories: () => read("categories.json"),
  ages: () => read("ages.json"),
  continents: () => read("continents.json"),
  holidays: () => read("holidays.json"),
  seasons: () => read("seasons.json"),
  colors: () => read("colors.json"),
  plateSvg: (slug) => fs.readFileSync(path.join(__dirname, "plates", `${slug}.svg`), "utf8").trim(),
};
