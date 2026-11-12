/**
 * Resultaatplaatje "Zo wordt het" bij bouwplaten (ADR 0100). Het staat als geneste `<svg class="kh-result">` in een
 * vel van de plaat (vel 1 of een extra vel), zodat het mee geprint wordt. Voor de plaatpagina halen we het eruit als
 * losse SVG met een eigen viewBox en een alt-tekst. Geen plaatje: null.
 */
const RESULT = /<svg class="kh-result"([^>]*)>([\s\S]*?)<\/svg>/;

const attr = (s: string) => s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");

export function resultSvg(svgs: string[], alt: string): string | null {
  for (const svg of svgs) {
    const m = RESULT.exec(svg);
    if (!m) continue;
    const viewBox = /\sviewBox="(-?[\d.]+ -?[\d.]+ [\d.]+ [\d.]+)"/.exec(m[1]!)?.[1];
    if (!viewBox) continue;
    const sw = /--sw:\s*([\d.]+)/.exec(m[1]!)?.[1];
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${viewBox}"${sw ? ` style="--sw:${sw}"` : ""} role="img" aria-label="${attr(alt)}">${m[2]}</svg>`;
  }
  return null;
}
