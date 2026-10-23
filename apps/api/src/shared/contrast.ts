/**
 * Contrast volgens WCAG 2.2, voor de huisstijl van organisaties. Zelfde regels als in
 * @kleurhoek/theme (brand.ts); de API is de bewaker, de website past alleen goedgekeurde kleuren toe.
 */
export const HEX = /^#[0-9a-f]{6}$/;
const lum = (hex: string) => {
  const n = Number.parseInt(hex.slice(1), 16);
  const [r, g, b] = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => { const s = v / 255; return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4; }) as [number, number, number];
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
export const contrast = (a: string, b: string) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p) as [number, number]; return (x + 0.05) / (y + 0.05); };
const LIGHT_BACKGROUNDS = ["#f6f6f4", "#ffffff"];
const onText = (hex: string) => Math.max(contrast(hex, "#ffffff"), contrast(hex, "#18181b"));

/** Foutmelding als de kleur niet voldoet, anders null. */
export function primaryProblem(hex: string): string | null {
  const bg = Math.min(...LIGHT_BACKGROUNDS.map((b) => contrast(hex, b)));
  if (bg < 3) return `Primaire kleur is te licht tegen de achtergrond (${bg.toFixed(1).replace(".", ",")}:1, minstens 3:1)`;
  if (onText(hex) < 4.5) return `Tekst op de primaire kleur is slecht leesbaar (${onText(hex).toFixed(1).replace(".", ",")}:1, minstens 4,5:1)`;
  return null;
}
export function accentProblem(hex: string): string | null {
  const bg = Math.min(...LIGHT_BACKGROUNDS.map((b) => contrast(hex, b)));
  return bg < 4.5 ? `Accentkleur (links) is slecht leesbaar (${bg.toFixed(1).replace(".", ",")}:1, minstens 4,5:1)` : null;
}
