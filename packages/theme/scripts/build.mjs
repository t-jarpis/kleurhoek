// Zet het actieve thema (theme.config.json of KLEURHOEK_THEME) om naar generated/theme.css en
// generated/theme.ts. Componenten lezen alleen de CSS-variabelen; een andere stijl is dus een andere
// map in themes/ en dit script opnieuw draaien. Met --check: faalt als generated/ niet actueel is.
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const config = JSON.parse(readFileSync(join(root, "theme.config.json"), "utf8"));
const name = process.env.KLEURHOEK_THEME || config.theme;
const dir = join(root, "themes", name);
if (!existsSync(dir)) throw new Error(`Thema '${name}' bestaat niet (themes/${name})`);
const tokens = JSON.parse(readFileSync(join(dir, "tokens.json"), "utf8"));
const theme = JSON.parse(readFileSync(join(dir, "theme.json"), "utf8"));
// Lettertype: los te kiezen (fonts/<naam>), standaard dat van het thema.
const fontName = process.env.KLEURHOEK_FONT || config.font || theme.font;
const fontDir = join(root, "fonts", fontName);
if (!existsSync(join(fontDir, "font.json"))) throw new Error(`Lettertype '${fontName}' bestaat niet (fonts/${fontName}/font.json)`);
const font = JSON.parse(readFileSync(join(fontDir, "font.json"), "utf8"));

const light = [], dark = [], rest = [];
for (const t of tokens.color.tokens) {
  if (typeof t.value === "string") rest.push([t.name, t.value]);
  else { light.push([t.name, t.value.light]); dark.push([t.name, t.value.dark]); }
}
for (const t of tokens.shadow.tokens) {
  if (typeof t.value === "string") rest.push([t.name, t.value]);
  else { light.push([t.name, t.value.light]); dark.push([t.name, t.value.dark]); }
}
for (const group of ["spacing", "radius", "modus", "borderWidth", "zIndex", "breakpoint", "duration", "container", "knoppen"]) {
  for (const t of tokens[group]?.tokens ?? []) rest.push([t.name, t.value]);
}
rest.push(["font-sans", `"${font.family}", system-ui, -apple-system, "Segoe UI", sans-serif`], ["font-mono", tokens.type.families.mono]);

const vars = (pairs, indent = "  ") => pairs.map(([k, v]) => `${indent}--${k}: ${v};`).join("\n");
const fonts = font.weights.map((w) =>
  `@font-face { font-family: "${font.family}"; src: url("../fonts/${fontName}/${font.file.replace("{weight}", w)}") format("woff2"); font-weight: ${w}; font-style: normal; font-display: swap; }`).join("\n");

const css = `/* Gegenereerd door packages/theme/scripts/build.mjs uit themes/${name} met lettertype ${fontName}. Niet met de hand wijzigen. */
${fonts}
:root {
${vars(rest)}
${vars(light)}
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
${vars(dark, "    ")}
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
${vars(dark)}
  color-scheme: dark;
}
`;
const ts = `// Gegenereerd door packages/theme/scripts/build.mjs uit themes/${name}. Niet met de hand wijzigen.
export const activeTheme = ${JSON.stringify({ id: name, name: theme.name, font: font.family, logo: theme.logo }, null, 2)} as const;
`;

const out = { "generated/theme.css": css, "generated/theme.ts": ts };
if (process.argv.includes("--check")) {
  const stale = Object.entries(out).filter(([f, c]) => !existsSync(join(root, f)) || readFileSync(join(root, f), "utf8") !== c).map(([f]) => f);
  if (stale.length) { console.error(`Niet actueel: ${stale.join(", ")}. Draai: pnpm --filter @kleurhoek/theme build`); process.exit(1); }
  console.log(`Thema ${name}: generated/ is actueel`);
} else {
  for (const [f, c] of Object.entries(out)) writeFileSync(join(root, f), c);
  console.log(`Thema ${name} met ${font.family} gegenereerd (${rest.length + light.length} variabelen)`);
}
