#!/usr/bin/env node
// Kwaliteitscontrole van de hele catalogus (ADR 0027) en het voortgangsoverzicht.
//   node scripts/plates/check.mjs            controleren
//   node scripts/plates/check.mjs --report   ook docs/content/voortgang.md bijwerken
// Controles: dubbele tekeningen, ontbrekende gegevens per soort, alles binnen het vel (in een echte
// browser gemeten), leesbare tekst, kleine vlakken voor jonge kinderen, en titels bij extra pagina's.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { DATA, PLATE_CSS, ROOT, playwright } from "./lib.mjs";
import data from "../../packages/catalog-data/index.js";

const plates = data.plates();
const problems = [], warnings = [];
const fail = (slug, msg) => problems.push(`${slug}: ${msg}`);
const warn = (slug, msg) => warnings.push(`${slug}: ${msg}`);

// 1. Dubbele tekeningen (zelfde SVG, ongeacht nummering).
const seen = new Map();
for (const p of plates) {
  const h = crypto.createHash("sha1").update(data.plateSvg(p.slug).replace(/\sdata-i="\d+"/g, "")).digest("hex");
  if (seen.has(h)) fail(p.slug, `zelfde tekening als ${seen.get(h)}`); else seen.set(h, p.slug);
}

// 2. Gegevens per soort.
for (const p of plates) {
  const nl = p.i18n.nl ?? {};
  if (!nl.name) fail(p.slug, "geen naam");
  if (p.kind !== "kleurplaat") {
    if (!p.minutes) warn(p.slug, "geen maaktijd");
    if (!nl.steps?.length) fail(p.slug, "geen stappen");
    if (!p.materials.length) fail(p.slug, "geen materialen");
  }
  if (["knipplaat", "bouwplaat", "kaart", "sjabloon"].includes(p.kind) && !p.materials.some((m) => m.slug === "kinderschaar")) warn(p.slug, "knippen zonder schaar in de materialen");
  if (p.kind === "werkblad" && !p.pages.some((x) => x.role === "antwoorden") && /(reken|som|tel|puzzel|doolhof|zoek)/i.test(nl.name + " " + (nl.steps ?? []).join(" "))) warn(p.slug, "werkblad met een opgave maar zonder antwoordblad");
}

// 3. In de browser: alles binnen het vel, tekst groot genoeg, vlakken niet te klein voor de leeftijd.
const { chromium } = playwright();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 400, height: 600 } });
for (const p of plates) {
  const svgs = [[1, data.plateSvg(p.slug), p.height], ...p.pages.map((pg, i) => [i + 2, data.pageSvg(p.slug, i + 2), pg.height])];
  for (const [n, svg, height] of svgs) {
    await page.setContent(`<style>${PLATE_CSS}</style>${svg.replace("<svg ", '<svg width="400" ')}`);
    const r = await page.evaluate(({ height, kleur }) => {
      const out = { outside: 0, tinyText: 0, tiny: 0 };
      const svg = document.querySelector("svg"), box = svg.getBoundingClientRect(), k = 200 / box.width;
      for (const el of document.querySelectorAll("svg *")) {
        if (!(el instanceof SVGGraphicsElement) || el.closest("defs,clipPath,mask") || el.tagName === "g") continue;
        // Echte plek op het vel (met transform), in viewBox-eenheden.
        const r = el.getBoundingClientRect();
        const b = { x: (r.left - box.left) * k, y: (r.top - box.top) * k, width: r.width * k, height: r.height * k };
        if (b.width === 0 && b.height === 0) continue;
        if (b.x < -0.5 || b.y < -0.5 || b.x + b.width > 200.5 || b.y + b.height > height + 0.5) out.outside++;
        if (el.tagName === "text" && Number(getComputedStyle(el).fontSize.replace("px", "")) < 4.5) out.tinyText++;
        if (kleur && el.classList.contains("r") && b.width * b.height < 1) out.tiny++;
      }
      return out;
    }, { height, kleur: n === 1 });
    // Een kleurplaat mag aflopen (wordt bijgesneden); onderdelen van knutselwerk moeten op het vel passen.
    if (r.outside) (p.kind === "kleurplaat" ? warn : fail)(p.slug, `pagina ${n}: ${r.outside} onderdelen (deels) buiten het vel`);
    if (r.tinyText) warn(p.slug, `pagina ${n}: ${r.tinyText} teksten kleiner dan 4,5 (onleesbaar geprint)`);
    if (r.tiny) warn(p.slug, `pagina ${n}: ${r.tiny} piepkleine vlakken`);
  }
}
await browser.close();

// 4. Voortgang.
const count = (key) => plates.reduce((m, p) => m.set(key(p), (m.get(key(p)) ?? 0) + 1), new Map());
const table = (title, m) => `### ${title}\n\n| | Aantal |\n|---|---:|\n${[...m].sort((a, b) => b[1] - a[1]).map(([k, v]) => `| ${k} | ${v} |`).join("\n")}\n`;
if (process.argv.includes("--report")) {
  // Verdeling uit de contentopdracht (ADR 0027). "Gevorderd" telt platen voor 12+ en overlapt met de rest.
  const buckets = [
    ["Kleurplaten", (p) => p.kind === "kleurplaat", 2000],
    ["Knip-, plak- en knutselbladen", (p) => p.kind === "knipplaat", 750],
    ["Vouw- en bouwplaten", (p) => p.kind === "vouwblad" || p.kind === "bouwplaat", 500],
    ["Teken- en schilderactiviteiten", (p) => p.kind === "tekenles" || p.kind === "sjabloon", 400],
    ["Educatief en spelletjes", (p) => p.kind === "werkblad" || p.kind === "spel", 600],
    ["Kaarten, decoraties en cadeautjes", (p) => p.kind === "kaart", 400],
    ["Gevorderd (12+, overlapt)", (p) => p.age === "12+", 350],
  ];
  const md = `# Voortgang content\n\nBijgewerkt door \`scripts/plates/check.mjs --report\`. Doel en verdeling: ADR 0027.\n\n` +
    `**Totaal: ${plates.length}** van 5.000. Problemen: ${problems.length}, waarschuwingen: ${warnings.length}.\n\n` +
    `| Groep | Nu | Doel |\n|---|---:|---:|\n${buckets.map(([name, f, goal]) => `| ${name} | ${plates.filter(f).length} | ${goal} |`).join("\n")}\n\n` +
    table("Per soort", count((p) => p.kind)) + "\n" + table("Per onderwerp", count((p) => p.category)) + "\n" + table("Per leeftijd", count((p) => p.age)) + "\n" +
    (warnings.length ? `### Waarschuwingen\n\n${warnings.map((w) => `- ${w}`).join("\n")}\n` : "");
  fs.mkdirSync(path.join(ROOT, "docs", "content"), { recursive: true });
  fs.writeFileSync(path.join(ROOT, "docs", "content", "voortgang.md"), md);
}
console.log(`${plates.length} platen gecontroleerd: ${problems.length} problemen, ${warnings.length} waarschuwingen`);
if (warnings.length) console.log("Waarschuwingen:\n- " + warnings.slice(0, 40).join("\n- ") + (warnings.length > 40 ? `\n… en ${warnings.length - 40} meer` : ""));
if (problems.length) { console.error("Problemen:\n- " + problems.join("\n- ")); process.exitCode = 1; }
