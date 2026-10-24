#!/usr/bin/env node
// Controle van één taal (ADR 0029): welke platen zijn in deze taal te zien, welke teksten ontbreken nog
// in de woordenlijst, en past de vertaalde tekst nog op het vel (niet buiten de rand, niet kleiner dan 4,5).
//
// Gebruik: node scripts/plates/check-lang.mjs <taal> [--missing <bestand.json>] [--too-long <bestand.json>] [--slug <slug>]
//   --missing schrijft de bronteksten die nog geen vertaling hebben naar een JSON-lijst (voor het vertalen).
//   --too-long <bestand.json> schrijft vertalingen die te klein zouden worden, met het maximale aantal tekens.
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
const tooLong = new Map();
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
    // Teksten tellen die buiten het vel vallen of te klein zijn, met transform meegerekend (zoals check.mjs).
    const measure = async (markup) => {
      await page.setContent(`<style>${PLATE_CSS}</style>${markup.replace("<svg ", '<svg width="400" ')}`);
      return page.evaluate((h) => {
        let outside = 0, tiny = 0, overlap = 0;
        const svg = document.querySelector("svg"), box = svg.getBoundingClientRect(), k = 200 / box.width;
        const boxes = [];
        for (const el of document.querySelectorAll("text")) {
          const r = el.getBoundingClientRect();
          const b = { x: (r.left - box.left) * k, y: (r.top - box.top) * k, w: r.width * k, h: r.height * k };
          if (b.x < -0.5 || b.y < -0.5 || b.x + b.w > 200.5 || b.y + b.h > h + 0.5) outside++;
          if (parseFloat(getComputedStyle(el).fontSize) < 4.5) tiny++;
          boxes.push(b);
        }
        // Teksten die elkaar raken (een beetje marge: letters hebben lucht boven en onder).
        for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
          const a = boxes[i], c = boxes[j];
          const dx = Math.min(a.x + a.w, c.x + c.w) - Math.max(a.x, c.x), dy = Math.min(a.y + a.h, c.y + c.h) - Math.max(a.y, c.y);
          if (dx > 0.5 && dy > Math.min(a.h, c.h) * 0.35) overlap++;
        }
        return { outside, tiny, overlap };
      }, height);
    };
    const before = await measure(svg), after = await measure(local);
    // Alleen wat de vertaling erger maakt telt; wat in de brontaal al zo is, meldt check.mjs.
    const r = { outside: after.outside - before.outside, tiny: after.tiny - before.tiny, overlap: after.overlap - before.overlap };
    if (r.overlap > 0) { problems.push(`${p.slug}: pagina ${n + 1}: ${r.overlap} teksten raken elkaar in ${lang}; kies een kortere vertaling`); for (const x of scaled) tooLong.set(x.source, { translation: x.text, maxChars: Math.floor(x.text.length * x.to / x.from) }); }
    if (r.outside > 0) problems.push(`${p.slug}: pagina ${n + 1}: ${r.outside} teksten buiten het vel in ${lang}`);
    if (r.tiny > 0) for (const x of scaled) if (x.to < 4.5) tooLong.set(x.source, { translation: x.text, maxChars: Math.floor(x.text.length * x.to / 4.5) });
    if (r.tiny > 0) warnings.push(`${p.slug}: pagina ${n + 1}: ${r.tiny} teksten kleiner dan 4,5 in ${lang}; kies een kortere vertaling`);
  }
}
await browser.close();

const long = opt("--too-long");
if (long) fs.writeFileSync(path.resolve(long), JSON.stringify(Object.fromEntries(tooLong), null, 2) + "\n");
const out = opt("--missing");
if (out) fs.writeFileSync(path.resolve(out), JSON.stringify([...missingAll.keys()].sort(), null, 2) + "\n");
console.log(`${lang}: ${named} platen met naam, ${ready} volledig vertaald; woordenlijst ${Object.keys(glossary).length} teksten, ${missingAll.size} nog te vertalen. ${problems.length} problemen, ${warnings.length} waarschuwingen.`);
if (problems.length) console.log("Problemen:\n- " + problems.join("\n- "));
if (warnings.length) console.log("Waarschuwingen:\n- " + warnings.slice(0, 50).join("\n- ") + (warnings.length > 50 ? `\n… en ${warnings.length - 50} meer` : ""));
if (problems.length) process.exitCode = 1;
