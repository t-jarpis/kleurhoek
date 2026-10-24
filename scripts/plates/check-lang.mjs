#!/usr/bin/env node
// Controle van één taal (ADR 0029): welke platen zijn in deze taal te zien, welke teksten ontbreken nog
// in de woordenlijst, en past de vertaalde tekst nog op het vel (niet buiten de rand, niet kleiner dan 4,5).
//
// Gebruik: node scripts/plates/check-lang.mjs <taal> [--missing <bestand.json>] [--slug <slug>]
//   --missing schrijft de bronteksten die nog geen vertaling hebben naar een JSON-lijst (voor het vertalen).
import fs from "node:fs";
import path from "node:path";
import { PLATE_CSS, playwright } from "./lib.mjs";
import data from "../../packages/catalog-data/index.js";

const args = process.argv.slice(2);
const lang = args[0];
if (!lang || !/^[a-z]{2}$/.test(lang) || lang === data.SOURCE_LANGUAGE) { console.error("Gebruik: check-lang.mjs <taal> (niet nl)"); process.exit(1); }
const opt = (name) => { const i = args.indexOf(name); return i > 0 ? args[i + 1] : null; };
const only = opt("--slug");

const glossary = data.texts(lang);
const plates = data.plates().filter((p) => !only || p.slug === only);
const problems = [], warnings = [];
const missingAll = new Map();
let named = 0, ready = 0;

const { chromium } = playwright();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 400, height: 600 } });

for (const p of plates) {
  const tr = p.i18n?.[lang];
  const svgs = [data.plateSvg(p.slug), ...p.pages.map((_, i) => data.pageSvg(p.slug, i + 2))];
  const texts = data.plateTexts(...svgs);
  for (const t of texts) if (!glossary[t]) missingAll.set(t, (missingAll.get(t) ?? 0) + 1);
  if (!tr?.name) continue;
  named++;
  if (p.languageBound) { problems.push(`${p.slug}: taalgebonden plaat heeft toch een naam in ${lang}`); continue; }
  if (p.kind !== "kleurplaat" && !(tr.steps ?? []).length) problems.push(`${p.slug}: stappen ontbreken in ${lang}`);
  if ((tr.pageTitles ?? []).length !== p.pages.length) problems.push(`${p.slug}: paginatitels ontbreken in ${lang}`);
  const missing = texts.filter((t) => !glossary[t]);
  if (missing.length) { warnings.push(`${p.slug}: ${missing.length} teksten nog niet vertaald (niet zichtbaar)`); continue; }
  ready++;
  for (const [n, svg] of svgs.entries()) {
    const { svg: local, scaled } = data.localizeSvg(svg, (t) => glossary[t]);
    if (!scaled.length) continue;
    const height = Number(/viewBox="0 0 200 (\d+)"/.exec(local)?.[1] ?? 200);
    await page.setContent(`<style>${PLATE_CSS}</style>${local.replace("<svg ", '<svg width="400" ')}`);
    const r = await page.evaluate((h) => {
      let outside = 0, tiny = 0;
      for (const el of document.querySelectorAll("text")) {
        const b = el.getBBox();
        const size = parseFloat(getComputedStyle(el).fontSize);
        if (b.x < -0.5 || b.y < -0.5 || b.x + b.width > 200.5 || b.y + b.height > h + 0.5) outside++;
        if (size < 4.5) tiny++;
      }
      return { outside, tiny };
    }, height);
    if (r.outside) problems.push(`${p.slug}: pagina ${n + 1}: ${r.outside} teksten buiten het vel in ${lang}`);
    if (r.tiny) warnings.push(`${p.slug}: pagina ${n + 1}: ${r.tiny} teksten kleiner dan 4,5 in ${lang}; kies een kortere vertaling`);
  }
}
await browser.close();

const out = opt("--missing");
if (out) fs.writeFileSync(path.resolve(out), JSON.stringify([...missingAll.keys()].sort(), null, 2) + "\n");
console.log(`${lang}: ${named} platen met naam, ${ready} volledig vertaald; woordenlijst ${Object.keys(glossary).length} teksten, ${missingAll.size} nog te vertalen. ${problems.length} problemen, ${warnings.length} waarschuwingen.`);
if (problems.length) console.log("Problemen:\n- " + problems.join("\n- "));
if (warnings.length) console.log("Waarschuwingen:\n- " + warnings.slice(0, 50).join("\n- ") + (warnings.length > 50 ? `\n… en ${warnings.length - 50} meer` : ""));
if (problems.length) process.exitCode = 1;
