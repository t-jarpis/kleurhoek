// Zet alle thema's (themes/*) en lettertypen (fonts/*) om naar:
// - generated/theme.css: @font-face voor elk lettertype (de browser laadt alleen wat gebruikt wordt),
//   het standaardthema op :root, en elk thema/lettertype onder :root[data-kh-theme] / [data-kh-font].
//   Zo kan een organisatie in het admin panel een thema en lettertype kiezen zonder nieuwe build.
// - generated/theme.ts en generated/manifest.json: welke thema's en lettertypen er zijn.
// Standaard: theme.config.json (of KLEURHOEK_THEME / KLEURHOEK_FONT). Met --check: faalt als
// generated/ niet actueel is.
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const json = (p) => JSON.parse(readFileSync(p, "utf8"));
const config = json(join(root, "theme.config.json"));

const themes = readdirSync(join(root, "themes")).filter((d) => existsSync(join(root, "themes", d, "tokens.json"))).sort()
  .map((id) => ({ id, tokens: json(join(root, "themes", id, "tokens.json")), meta: json(join(root, "themes", id, "theme.json")) }));
const fonts = readdirSync(join(root, "fonts")).filter((d) => existsSync(join(root, "fonts", d, "font.json"))).sort()
  .map((id) => ({ id, ...json(join(root, "fonts", id, "font.json")) }));

const defaultTheme = process.env.KLEURHOEK_THEME || config.theme;
const theme = themes.find((t) => t.id === defaultTheme);
if (!theme) throw new Error(`Thema '${defaultTheme}' bestaat niet (themes/${defaultTheme})`);
const defaultFont = process.env.KLEURHOEK_FONT || config.font || theme.meta.font;
if (!fonts.some((f) => f.id === defaultFont)) throw new Error(`Lettertype '${defaultFont}' bestaat niet (fonts/${defaultFont})`);

const fontStack = (f) => `"${f.family}", system-ui, -apple-system, "Segoe UI", sans-serif`;

/** Variabelen van één thema: licht, donker en de rest (maten, knoppen …). */
function split(tokens) {
  const light = [], dark = [], rest = [];
  for (const t of [...tokens.color.tokens, ...tokens.shadow.tokens]) {
    if (typeof t.value === "string") rest.push([t.name, t.value]);
    else { light.push([t.name, t.value.light]); dark.push([t.name, t.value.dark]); }
  }
  for (const group of ["spacing", "radius", "modus", "borderWidth", "zIndex", "breakpoint", "duration", "container", "knoppen"]) {
    for (const t of tokens[group]?.tokens ?? []) rest.push([t.name, t.value]);
  }
  rest.push(["font-mono", tokens.type.families.mono]);
  return { light, dark, rest };
}

const vars = (pairs, indent = "  ") => pairs.map(([k, v]) => `${indent}--${k}: ${v};`).join("\n");

/** Een thema onder een selector, met donker via het systeem of geforceerd met data-theme. */
function block(sel, tokens) {
  const { light, dark, rest } = split(tokens);
  const forcedDark = sel === ":root" ? ':root[data-theme="dark"]' : `${sel}[data-theme="dark"]`;
  const autoDark = sel === ":root" ? ':root:not([data-theme="light"])' : `${sel}:not([data-theme="light"])`;
  return `${sel} {\n${vars(rest)}\n${vars(light)}\n  color-scheme: light;\n}
@media (prefers-color-scheme: dark) {\n  ${autoDark} {\n${vars(dark, "    ")}\n    color-scheme: dark;\n  }\n}
${forcedDark} {\n${vars(dark)}\n  color-scheme: dark;\n}`;
}

const fontFaces = fonts.flatMap((f) => f.weights.map((w) =>
  `@font-face { font-family: "${f.family}"; src: url("../fonts/${f.id}/${f.file.replace("{weight}", w)}") format("woff2"); font-weight: ${w}; font-style: normal; font-display: swap; }`)).join("\n");

const css = [
  `/* Gegenereerd door packages/theme/scripts/build.mjs. Niet met de hand wijzigen.\n   Standaard: thema ${theme.id}, lettertype ${defaultFont}. Per organisatie: data-kh-theme en data-kh-font op <html>. */`,
  fontFaces,
  block(":root", theme.tokens),
  `:root { --font-sans: ${fontStack(fonts.find((f) => f.id === defaultFont))}; }`,
  ...themes.filter((t) => t.id !== theme.id).map((t) => block(`:root[data-kh-theme="${t.id}"]`, t.tokens)),
  ...fonts.map((f) => `:root[data-kh-font="${f.id}"] { --font-sans: ${fontStack(f)}; }`),
  "",
].join("\n");

const manifest = {
  defaultTheme: theme.id,
  defaultFont,
  themes: themes.map((t) => ({ id: t.id, name: t.meta.name, description: t.meta.description, font: t.meta.font })),
  fonts: fonts.map((f) => ({ id: f.id, family: f.family })),
};
const ts = `// Gegenereerd door packages/theme/scripts/build.mjs. Niet met de hand wijzigen.
export const activeTheme = ${JSON.stringify({ id: theme.id, name: theme.meta.name, font: defaultFont, logo: theme.meta.logo }, null, 2)} as const;
export const manifest = ${JSON.stringify(manifest, null, 2)} as const;
`;

const out = { "generated/theme.css": css, "generated/theme.ts": ts, "generated/manifest.json": `${JSON.stringify(manifest, null, 2)}\n` };
if (process.argv.includes("--check")) {
  const stale = Object.entries(out).filter(([f, c]) => !existsSync(join(root, f)) || readFileSync(join(root, f), "utf8") !== c).map(([f]) => f);
  if (stale.length) { console.error(`Niet actueel: ${stale.join(", ")}. Draai: pnpm --filter @kleurhoek/theme build`); process.exit(1); }
  console.log(`Thema's ${themes.map((t) => t.id).join(", ")}; lettertypen ${fonts.map((f) => f.id).join(", ")}: generated/ is actueel`);
} else {
  for (const [f, c] of Object.entries(out)) writeFileSync(join(root, f), c);
  console.log(`Gegenereerd: thema's ${themes.map((t) => t.id).join(", ")}; lettertypen ${fonts.map((f) => f.id).join(", ")} (standaard ${theme.id} + ${defaultFont})`);
}
