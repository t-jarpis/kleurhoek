#!/usr/bin/env node
// Na een kleine reparatie aan een bestaande tekening (plates/<slug>.svg met de hand bijgewerkt, zelfde vlakken):
// de posities voor kleur-op-nummer opnieuw berekenen. Kleurcodes, teksten en volgorde blijven staan.
//   node scripts/plates/relabel.mjs <slug> [slug ...]
import fs from "node:fs";
import path from "node:path";
import { DATA, LABELS_JS, PLATE_CSS, playwright, regionCount } from "./lib.mjs";

const slugs = process.argv.slice(2);
if (!slugs.length) { console.error("Gebruik: relabel.mjs <slug> [slug ...]"); process.exit(1); }
const file = path.join(DATA, "plates.json");
const list = JSON.parse(fs.readFileSync(file, "utf8"));
const { chromium } = playwright();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
const errors = [];
for (const slug of slugs) {
  const p = list.find((x) => x.slug === slug);
  if (!p) { errors.push(`${slug}: onbekend`); continue; }
  const svg = fs.readFileSync(path.join(DATA, "plates", `${slug}.svg`), "utf8").trim();
  if (regionCount(svg) !== p.regionCount) { errors.push(`${slug}: aantal vlakken veranderd; gebruik ingest.mjs --vervang`); continue; }
  await page.setContent(`<style>${PLATE_CSS}</style>${svg.replace("<svg ", '<svg width="400" ')}`);
  const { labels } = await page.evaluate(`(${LABELS_JS})(${JSON.stringify(p.colorByNumber.codes)})`);
  p.colorByNumber.labels = labels;
}
await browser.close();
fs.writeFileSync(file, JSON.stringify(list, null, 2) + "\n");
console.log(`${slugs.length - errors.length} platen opnieuw genummerd`);
if (errors.length) { console.error(errors.join("\n")); process.exitCode = 1; }
