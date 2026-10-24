#!/usr/bin/env node
// Conceptplaten toevoegen aan packages/catalog-data: nummert de vlakken, berekent de posities voor
// kleur-op-nummer in een echte browser en schrijft plates/<slug>.svg en de regel in plates.json.
// Een nieuwe slug komt achteraan; een bestaande (met --vervang) houdt zijn plek.
//
// Gebruik: node scripts/plates/ingest.mjs <map-met-concepten> [slug ...] [--vervang]
// Een slug die al bestaat wordt alleen vervangen met --vervang (anders een fout): zo overschrijf je nooit
// per ongeluk een bestaande plaat.
//
// Concept = <slug>.svg + <slug>.json:
//   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"> … class="r" (vlak), "l" (lijn),
//   "dot" (zwart), knutselwerk ook "cut", "fold", "glue", "tip" … </svg>
//   { "category": "dieren", "age": "4-6", "world": null, "holiday": null, "codes": "rrgy-…",
//     "kind": "kleurplaat", "height": 200, "minutes": null, "adultHelp": false, "paperGsm": null,
//     "materials": [{ "slug": "kinderschaar" }], "i18n": { "nl": { "name": "…", "word": null,
//     "countQuestion": null, "steps": ["…"], "printNote": "…" } } }
//   codes: één letter per vlak (colors.json), "-" = geen nummer.
//   Optioneel (ADR 0027): "difficulty": 1|2|3, en extra pagina's als <slug>.p2.svg, <slug>.p3.svg … met
//   "pages": [{ "role": "extra" | "antwoorden", "height": 280 }] en i18n.nl.pageTitles: ["…"] in dezelfde volgorde.
import fs from "node:fs";
import path from "node:path";
import { DATA, LABELS_JS, PLATE_CSS, legendKeys, numberRegions, playwright, regionCount, COLORS } from "./lib.mjs";
import data from "../../packages/catalog-data/index.js";
const { KINDS } = data;

const args = process.argv.slice(2);
const replaceOk = args.includes("--vervang");
const [dir, ...only] = args.filter((a) => a !== "--vervang");
if (!dir) { console.error("Gebruik: ingest.mjs <map> [slug ...]"); process.exit(1); }
const slugs = (only.length ? only : fs.readdirSync(dir).filter((f) => f.endsWith(".svg") && !/\.p\d+\.svg$/.test(f)).map((f) => f.slice(0, -4))).sort();

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
  if (!KINDS.includes(kind)) { errors.push(`${slug}: onbekende soort ${kind}`); continue; }
  if (kind !== "kleurplaat" && !meta.i18n?.nl?.steps?.length) { errors.push(`${slug}: ${kind} zonder stappen`); continue; }
  if (["knipplaat", "bouwplaat", "sjabloon", "kaart"].includes(kind) && !/class="cut"/.test(svg)) { errors.push(`${slug}: ${kind} zonder kniplijn`); continue; }
  if (kind === "vouwblad" && !/class="fold"/.test(svg)) { errors.push(`${slug}: vouwblad zonder vouwlijn`); continue; }
  if (meta.difficulty != null && ![1, 2, 3].includes(meta.difficulty)) { errors.push(`${slug}: moeilijkheid 1, 2 of 3`); continue; }
  const pages = meta.pages ?? [];
  if ((meta.i18n?.nl?.pageTitles ?? []).length !== pages.length) { errors.push(`${slug}: titel per extra pagina (i18n.nl.pageTitles)`); continue; }
  const pageSvgs = [];
  let pageError = null;
  pages.forEach((pg, i) => {
    const f = path.join(dir, `${slug}.p${i + 2}.svg`);
    if (!fs.existsSync(f)) { pageError = `${slug}: ${slug}.p${i + 2}.svg ontbreekt`; return; }
    const p = fs.readFileSync(f, "utf8").trim().replace(/\s*\n\s*/g, " ");
    if (/<script|on\w+=|href=/i.test(p)) pageError = `${slug}: pagina ${i + 2} bevat script of link`;
    else if (!p.includes(`viewBox="0 0 200 ${pg.height}"`)) pageError = `${slug}: pagina ${i + 2} viewBox moet 0 0 200 ${pg.height} zijn`;
    else if (!["extra", "antwoorden"].includes(pg.role)) pageError = `${slug}: pagina ${i + 2} rol extra of antwoorden`;
    pageSvgs.push(p);
  });
  if (pageError) { errors.push(pageError); continue; }

  await page.setContent(`<style>${PLATE_CSS}</style>${svg.replace("<svg ", '<svg width="400" ')}`);
  const { labels } = await page.evaluate(`(${LABELS_JS})(${JSON.stringify(codes)})`);
  const entry = {
    slug, order: 0, category: meta.category, age: meta.age, world: meta.world ?? null, holiday: meta.holiday ?? null,
    ...(kind !== "kleurplaat" || meta.materials ? {
      kind, height, minutes: meta.minutes ?? null, adultHelp: meta.adultHelp ?? false, paperGsm: meta.paperGsm ?? null,
      ...(meta.difficulty ? { difficulty: meta.difficulty } : {}),
      ...(pages.length ? { pages: pages.map((pg) => ({ role: pg.role, height: pg.height })) } : {}),
      ...(meta.materials ? { materials: meta.materials } : {}),
    } : {}),
    regionCount: n,
    colorByNumber: { codes, palette: legendKeys(codes).map((code) => ({ code, hex: COLORS[code] })), labels },
    i18n: meta.i18n,
  };
  const at = list.findIndex((p) => p.slug === slug);
  if (at >= 0 && !replaceOk) { errors.push(`${slug}: bestaat al; kies een andere slug of gebruik --vervang`); continue; }
  if (at >= 0) { entry.order = list[at].order; list[at] = entry; replaced++; }
  else { entry.order = Math.max(-1, ...list.map((p) => p.order)) + 1; list.push(entry); added++; }
  fs.writeFileSync(path.join(DATA, "plates", `${slug}.svg`), svg + "\n");
  pageSvgs.forEach((p, i) => fs.writeFileSync(path.join(DATA, "plates", `${slug}.p${i + 2}.svg`), p + "\n"));
}
await browser.close();
fs.writeFileSync(platesFile, JSON.stringify(list, null, 2) + "\n");
console.log(`${added} toegevoegd, ${replaced} vervangen, totaal ${list.length} platen`);
if (errors.length) { console.error("Niet toegevoegd:\n- " + errors.join("\n- ")); process.exitCode = 1; }
