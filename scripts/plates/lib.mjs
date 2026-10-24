// Gedeelde hulpjes voor de plaat-scripts (ingest en preview). Draait buiten de apps: alleen Node + Playwright.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
export const DATA = path.join(ROOT, "packages", "catalog-data");

/** Playwright uit de repo of uit een globale installatie (npm i -g playwright). */
export function playwright() {
  const require = createRequire(import.meta.url);
  for (const id of ["playwright", "/opt/npm-tools/node_modules/playwright", "/usr/local/lib/node_modules/playwright", "/opt/homebrew/lib/node_modules/playwright"]) {
    try { return require(id); } catch { /* volgende */ }
  }
  throw new Error("Playwright niet gevonden. Installeer het met: npm i -g playwright && npx playwright install chromium");
}

export const COLORS = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(DATA, "colors.json"), "utf8")).map((c) => [c.code, c.hex]));
export const AGES = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(DATA, "ages.json"), "utf8")).map((a) => [a.slug, a.strokeWidth]));

/** Volgorde van de kleuren in de legenda: in volgorde van eerste voorkomen (zelfde als het prototype). */
export const legendKeys = (codes) => [...new Set(codes.replace(/-/g, ""))];

/** Vlakken nummeren: class="r" krijgt data-i in documentvolgorde. Bestaande data-i wordt eerst weggehaald. */
export function numberRegions(svg) {
  let i = 0;
  return svg.replace(/\sdata-i="\d+"/g, "").replace(/class="r"/g, () => `class="r" data-i="${i++}"`);
}

export const regionCount = (svg) => (svg.match(/class="r"/g) || []).length;

/** CSS die de site nabootst (globals.css), zodat een preview er net zo uitziet als op Kleurhoek. */
export const PLATE_CSS = `
  svg .r { fill: #fff; stroke: #1d1d1f; stroke-width: var(--sw, 2.4); stroke-linejoin: round; }
  svg .l { fill: none; stroke: #1d1d1f; stroke-width: var(--sw, 2.4); stroke-linecap: round; stroke-linejoin: round; }
  svg .dot { fill: #1d1d1f; }
  svg .cut { fill: none; stroke: #1d1d1f; stroke-width: 1; stroke-dasharray: 4 3; }
  svg .fold { fill: none; stroke: #1d1d1f; stroke-width: .8; stroke-dasharray: 1 2.5; }
  svg .glue { fill: #e9e6df; stroke: #9a948a; stroke-width: .6; }
  svg .tip { font: 600 6px system-ui, sans-serif; fill: #6b6760; }
  svg .tx { font-family: system-ui, sans-serif; font-weight: 700; fill: #1d1d1f; }
  svg .guide { stroke: #c9c4bb; stroke-width: .7; fill: none; }
  svg .num { font: 800 10px system-ui, sans-serif; fill: #1d1d1f; text-anchor: middle; dominant-baseline: central; paint-order: stroke; stroke: #fff; stroke-width: 1.4; }
`;

/**
 * Posities voor kleur-op-nummer, in de browser berekend (zelfde algoritme als het prototype): per vlak
 * het punt dat het verst van de rand ligt, zonder de vlakken die erbovenop liggen en zonder stippen.
 */
export const LABELS_JS = `(codes) => {
  const svg = document.querySelector('svg'), regs = [...svg.querySelectorAll('.r')];
  const inv = regs.map(r => r.getScreenCTM().inverse()), box = regs.map(r => r.getBoundingClientRect());
  const svgInv = svg.getScreenCTM().inverse(), scale = 200 / svg.getBoundingClientRect().width;
  const pt = svg.createSVGPoint();
  const dots = [...svg.querySelectorAll('.dot')], dinv = dots.map(d => d.getScreenCTM().inverse());
  const onDot = (x, y) => dots.some((d, k) => { pt.x = x; pt.y = y; return d.isPointInFill(pt.matrixTransform(dinv[k])); });
  const inside = (j, x, y) => { pt.x = x; pt.y = y; return regs[j].isPointInFill(pt.matrixTransform(inv[j])); };
  const keys = [...new Set(codes.replace(/-/g, ''))], out = [], hidden = [];
  regs.forEach((r, i) => {
    const key = codes[i]; if (!key || key === '-') return;
    const b = box[i], G = 20, cells = [];
    const later = []; for (let j = i + 1; j < regs.length; j++) { const o = box[j]; if (o.right > b.left && o.left < b.right && o.bottom > b.top && o.top < b.bottom) later.push(j); }
    for (let gx = 0; gx < G; gx++) for (let gy = 0; gy < G; gy++) {
      const x = b.left + (gx + .5) * b.width / G, y = b.top + (gy + .5) * b.height / G;
      cells.push({ x, y, v: inside(i, x, y) && !later.some(j => inside(j, x, y)) && !onDot(x, y) });
    }
    const vis = cells.filter(c => c.v), blk = cells.filter(c => !c.v);
    let best = null, bd = -1;
    vis.forEach(c => { let d = Math.min(c.x - b.left, b.right - c.x, c.y - b.top, b.bottom - c.y);
      for (const o of blk) { const e = Math.hypot(o.x - c.x, o.y - c.y); if (e < d) d = e; }
      if (d > bd) { bd = d; best = c; } });
    if (!best) { hidden.push(i); best = { x: b.left + b.width / 2, y: b.top + b.height / 2 }; bd = 4; }
    pt.x = best.x; pt.y = best.y; const q = pt.matrixTransform(svgInv);
    out.push({ region: i, number: keys.indexOf(key) + 1, x: +q.x.toFixed(1), y: +q.y.toFixed(1), size: +Math.max(4.5, Math.min(13, bd * scale * 1.15)).toFixed(1) });
  });
  return { labels: out, hidden };
}`;
