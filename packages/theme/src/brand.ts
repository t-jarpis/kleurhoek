import { contrast, HEX, mix, onColor } from "./color";

/**
 * Huisstijl van een organisatie (ADR 0017). Alleen deze kleuren zijn per organisatie te kiezen; de
 * rest komt uit het thema. Elke kleur wordt gecontroleerd (contrast) en geldt in donker alleen als
 * hij daar ook leesbaar is.
 */
export interface BrandColors { primary?: string | null; accent?: string | null }
export interface Brand { theme?: string | null; font?: string | null; colors?: BrandColors | null; wordmark?: string | null }

/** Achtergronden van het thema waar de kleuren tegen moeten werken (Studio: bg en surface, licht/donker). */
export const BACKGROUNDS = { light: ["#f6f6f4", "#ffffff"], dark: ["#141416", "#1e1e21"] } as const;
export const MIN_TEXT = 4.5;
export const MIN_UI = 3;

/** Verhouding zoals een Nederlandse lezer hem verwacht: 4,5 in plaats van 4.5. */
export const ratio = (n: number) => n.toFixed(1).replace(".", ",");

export interface ColorCheck { ok: boolean; light: number; dark: number; message?: string }

/** Primair: knoppen en gekozen filters. Moet als vlak opvallen (3:1) en er moet tekst op kunnen (4,5:1). */
export function checkPrimary(hex: string): ColorCheck {
  const light = Math.min(...BACKGROUNDS.light.map((b) => contrast(hex, b)));
  const dark = Math.min(...BACKGROUNDS.dark.map((b) => contrast(hex, b)));
  const onText = contrast(hex, onColor(hex));
  const ok = light >= MIN_UI && onText >= MIN_TEXT;
  return { ok, light, dark, ...(ok ? {} : { message: light < MIN_UI ? `Te licht tegen de achtergrond (${ratio(light)}:1, minstens 3:1)` : `Tekst op deze kleur is slecht leesbaar (${ratio(onText)}:1)` }) };
}

/** Accent: links en focus. Moet als tekst leesbaar zijn (4,5:1). */
export function checkAccent(hex: string): ColorCheck {
  const light = Math.min(...BACKGROUNDS.light.map((b) => contrast(hex, b)));
  const dark = Math.min(...BACKGROUNDS.dark.map((b) => contrast(hex, b)));
  const ok = light >= MIN_TEXT;
  return { ok, light, dark, ...(ok ? {} : { message: `Links in deze kleur zijn slecht leesbaar (${ratio(light)}:1, minstens 4,5:1)` }) };
}

const decl = (pairs: [string, string][]) => pairs.map(([k, v]) => `--${k}:${v}`).join(";");

/**
 * CSS met de kleuren van een organisatie, bovenop het thema. Leeg als er niets te veranderen is.
 * Alleen geldige, goedgekeurde kleuren komen erin; in donker alleen als ze daar ook werken.
 * Met `scope` (een selector) gelden de kleuren alleen daarbinnen, bijvoorbeeld voor een voorbeeld in beheer.
 */
export function brandCss(colors: BrandColors | null | undefined, scope?: string): string {
  const light: [string, string][] = [];
  const dark: [string, string][] = [];
  const p = colors?.primary?.toLowerCase();
  if (p && HEX.test(p) && checkPrimary(p).ok) {
    const set: [string, string][] = [
      ["color-primary", p], ["color-primary-hover", mix(p, onColor(p) === "#ffffff" ? "#000000" : "#ffffff", 0.18)],
      ["color-text-on-primary", onColor(p)], ["color-border-strong", p],
    ];
    light.push(...set);
    if (checkPrimary(p).dark >= MIN_UI) dark.push(...set);
  }
  const a = colors?.accent?.toLowerCase();
  if (a && HEX.test(a) && checkAccent(a).ok) {
    light.push(["color-accent", a], ["color-accent-hover", mix(a, "#000000", 0.15)], ["color-focus", a], ["color-accent-soft", mix(a, "#ffffff", 0.88)]);
    if (checkAccent(a).dark >= MIN_TEXT) dark.push(["color-accent", a], ["color-accent-hover", mix(a, "#ffffff", 0.2)], ["color-focus", a], ["color-accent-soft", mix(a, "#141416", 0.8)]);
  }
  if (!light.length) return "";
  const inner = scope ? ` ${scope}` : "";
  const out = [`${scope ?? ":root"}{${decl(light)}}`];
  if (dark.length) out.push(`@media (prefers-color-scheme: dark){:root:not([data-theme="light"])${inner}{${decl(dark)}}}`, `:root[data-theme="dark"]${inner}{${decl(dark)}}`);
  return out.join("");
}
