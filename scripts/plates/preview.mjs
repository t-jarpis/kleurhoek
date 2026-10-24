#!/usr/bin/env node
// Contactvel van conceptplaten: per plaat de lege lijntekening (lijndikte van de leeftijd) en de
// ingekleurde versie met nummers. Meldt ook fouten (aantal vlakken, onzichtbare vlakken).
//
// Gebruik: node scripts/plates/preview.mjs <map-met-concepten> <uit.png> [slug ...]
//   Een concept is <slug>.svg (met class="r" voor vlakken) plus <slug>.json (zie ingest.mjs).
import fs from "node:fs";
import path from "node:path";
import { AGES, COLORS, LABELS_JS, PLATE_CSS, numberRegions, playwright, regionCount } from "./lib.mjs";

const [dir, out, ...only] = process.argv.slice(2);
if (!dir || !out) { console.error("Gebruik: preview.mjs <map> <uit.png> [slug ...]"); process.exit(1); }

const slugs = (only.length ? only : fs.readdirSync(dir).filter((f) => f.endsWith(".svg")).map((f) => f.slice(0, -4))).sort();
const items = slugs.map((slug) => {
  const svg = numberRegions(fs.readFileSync(path.join(dir, `${slug}.svg`), "utf8").trim());
  const meta = JSON.parse(fs.readFileSync(path.join(dir, `${slug}.json`), "utf8"));
  return { slug, svg, meta };
});

const { chromium } = playwright();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
const problems = [], notes = [];
const cells = [];
for (const { slug, svg, meta } of items) {
  const n = regionCount(svg), codes = meta.codes ?? "";
  if (codes.length !== n) problems.push(`${slug}: ${n} vlakken maar ${codes.length} kleurcodes`);
  const bad = [...codes].filter((c) => c !== "-" && !COLORS[c]);
  if (bad.length) problems.push(`${slug}: onbekende kleurcode(s) ${[...new Set(bad)].join("")}`);
  const height = Number(/viewBox="0 0 200 (\d+)"/.exec(svg)?.[1] ?? 0);
  if (height !== (meta.height ?? 200)) problems.push(`${slug}: viewBox-hoogte ${height} ≠ height ${meta.height ?? 200}`);
  await page.setContent(`<style>${PLATE_CSS}</style>${svg.replace("<svg ", '<svg width="400" ')}`);
  const { labels, hidden } = await page.evaluate(`(${LABELS_JS})(${JSON.stringify(codes)})`);
  if (hidden.length) problems.push(`${slug}: vlak(ken) ${hidden.join(", ")} zijn helemaal bedekt`);
  const tiny = labels.filter((l) => l.size <= 4.5).map((l) => l.region);
  if (tiny.length) notes.push(`${slug}: kleine vlakken (klein nummer): ${tiny.join(", ")}`);
  const sw = AGES[meta.age] ?? 2.4;
  const colored = svg.replace(/class="r" data-i="(\d+)"/g, (m, i) => { const c = COLORS[codes[+i]]; return c ? `${m} style="fill:${c}"` : m; })
    .replace("</svg>", `${labels.map((l) => `<text class="num" x="${l.x}" y="${l.y}" font-size="${l.size}">${l.number}</text>`).join("")}</svg>`);
  const nums = svg.replace("</svg>", `${labels.map((l) => `<text class="num" x="${l.x}" y="${l.y}" font-size="${l.size}">${l.number}</text>`).join("")}</svg>`);
  cells.push(`<figure style="--sw:${sw}"><div class="pair"><div>${svg}</div><div>${nums}</div><div>${colored}</div></div><figcaption>${slug} · ${meta.i18n?.nl?.name ?? "?"} · ${meta.age} · ${n} vlakken</figcaption></figure>`);
}
const html = `<style>${PLATE_CSS}
  body { margin: 0; padding: 12px; font: 13px system-ui; background: #f3f1ec; display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; width: 1176px; }
  figure { margin: 0; background: #fff; padding: 8px; border-radius: 8px; }
  .pair { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; align-items: start; }
  .pair svg { width: 100%; height: auto; display: block; border: 1px solid #eee; }
  figcaption { margin-top: 4px; color: #444; }
</style>${cells.join("")}`;
await page.setViewportSize({ width: 1200, height: 800 });
await page.setContent(html);
await page.screenshot({ path: out, fullPage: true });
await browser.close();
console.log(`${items.length} platen → ${out}`);
if (notes.length) console.log("Info:\n- " + notes.join("\n- "));
if (problems.length) { console.log("Let op:\n- " + problems.join("\n- ")); process.exitCode = 2; }
