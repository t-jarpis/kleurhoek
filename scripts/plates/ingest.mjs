#!/usr/bin/env node
// Conceptplaten toevoegen aan packages/catalog-data: nummert de vlakken, berekent de posities voor
// kleur-op-nummer in een echte browser en schrijft plates/<slug>.svg en de regel in plates.json.
// Een bestaande slug wordt vervangen (zelfde volgorde), een nieuwe komt achteraan.
//
// Gebruik: node scripts/plates/ingest.mjs <map-met-concepten> [slug ...]
//
// Concept = <slug>.svg + <slug>.json:
//   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"> … class="r" (vlak), "l" (lijn),
//   "dot" (zwart), knutselwerk ook "cut", "fold", "glue", "tip" … </svg>
//   { "category": "dieren", "age": "4-6", "world": null, "holiday": null, "codes": "rrgy-…",
//     "kind": "kleurplaat", "height": 200, "minutes": null, "adultHelp": false, "paperGsm": null,
//     "materials": [{ "slug": "kinderschaar" }], "i18n": { "nl": { "name": "…", "word": null,
//     "countQuestion": null, "steps": ["…"], "printNote": "…" } } }
//   codes: één letter per vlak (colors.json), "-" = geen nummer.
import fs from "node:fs";
import path from "node:path";
import { DATA, LABELS_JS, PLATE_CSS, legendKeys, numberRegions, playwright, regionCount, COLORS } from "./lib.mjs";

const [dir, ...only] = process.argv.slice(2);
if (!dir) { console.error("Gebruik: ingest.mjs <map> [slug ...]"); process.exit(1); }
const slugs = (only.length ? only : fs.readdirSync(dir).filter((f) => f.endsWith(".svg")).map((f) => f.slice(0, -4))).sort();

const platesFile = path.join(DATA, "plates.json");
const list = JSON.parse(fs.readFileSync(platesFile, "utf8"));
const { chromium } = playwright();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
const errors = [];
let added = 0, replaced = 0;

for (const slug of slugs) {
  if (!/^[a-z0-9-]+$/.test(slug)) { errors.push(`${slug}: slug mag alleen a-z, 0-9 en - bevatten`); continue; }
  const raw = fs.readFileSync(path.join(dir, `${slug}.svg`), "utf8").trim().replace(/\s*\n\s*/g, " ");
  const meta = JSON.parse(fs.readFileSync(path.join(dir, `${slug}.json`), "utf8"));
  const svg = numberRegions(raw);
  const n = regionCount(svg), codes = meta.codes ?? "";
  const kind = meta.kind ?? "kleurplaat", height = meta.height ?? 200;
  if (/<script|on\w+=|href=/i.test(svg)) { errors.push(`${slug}: script, event of link in SVG`); continue; }
  if (!svg.includes(`viewBox="0 0 200 ${height}"`)) { errors.push(`${slug}: viewBox moet 0 0 200 ${height} zijn`); continue; }
  if (codes.length !== n) { errors.push(`${slug}: ${n} vlakken maar ${codes.length} kleurcodes`); continue; }
  if ([...codes].some((c) => c !== "-" && !COLORS[c])) { errors.push(`${slug}: onbekende kleurcode`); continue; }
  if (kind !== "kleurplaat" && (!/class="cut"/.test(svg) || !meta.i18n?.nl?.steps?.length)) { errors.push(`${slug}: knutselwerk zonder kniplijn of stappen`); continue; }

  await page.setContent(`<style>${PLATE_CSS}</style>${svg.replace("<svg ", '<svg width="400" ')}`);
  const { labels } = await page.evaluate(`(${LABELS_JS})(${JSON.stringify(codes)})`);
  const entry = {
    slug, order: 0, category: meta.category, age: meta.age, world: meta.world ?? null, holiday: meta.holiday ?? null,
    ...(kind !== "kleurplaat" || meta.materials ? {
      kind, height, minutes: meta.minutes ?? null, adultHelp: meta.adultHelp ?? false, paperGsm: meta.paperGsm ?? null,
      ...(meta.materials ? { materials: meta.materials } : {}),
    } : {}),
    regionCount: n,
    colorByNumber: { codes, palette: legendKeys(codes).map((code) => ({ code, hex: COLORS[code] })), labels },
    i18n: meta.i18n,
  };
  const at = list.findIndex((p) => p.slug === slug);
  if (at >= 0) { entry.order = list[at].order; list[at] = entry; replaced++; }
  else { entry.order = Math.max(-1, ...list.map((p) => p.order)) + 1; list.push(entry); added++; }
  fs.writeFileSync(path.join(DATA, "plates", `${slug}.svg`), svg + "\n");
}
await browser.close();
fs.writeFileSync(platesFile, JSON.stringify(list, null, 2) + "\n");
console.log(`${added} toegevoegd, ${replaced} vervangen, totaal ${list.length} platen`);
if (errors.length) { console.error("Niet toegevoegd:\n- " + errors.join("\n- ")); process.exitCode = 1; }
