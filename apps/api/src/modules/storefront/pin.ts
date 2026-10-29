/**
 * Staand plaatje voor Pinterest (ADR 0057): de plaat ingekleurd met de kleuren van "kleuren op nummer", met de
 * naam eronder en het domein. 1000 × 1500 (2:3), zoals Pinterest het liefst heeft. Geen merklogo van Pinterest.
 */
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/** De vlakken krijgen hun kleur uit "kleuren op nummer". */
export function colorIn(svg: string, labels: { region: number; number: number }[], palette: { hex: string }[]): string {
  const byRegion = new Map(labels.map((l) => [l.region, palette[l.number - 1]?.hex]));
  return svg.replace(/<(rect|circle|ellipse|path|polygon)\b([^>]*?)\bdata-i="(\d+)"([^>]*?)\/>/g, (tag, el: string, a: string, n: string, b: string) => {
    const hex = byRegion.get(Number(n));
    return hex && /^#[0-9a-f]{6}$/i.test(hex) ? `<${el}${a}data-i="${n}"${b} style="fill:${hex}"/>` : tag;
  });
}

/** Naam over hooguit twee regels, met een kleinere letter als hij lang is. */
export function titleLines(name: string): { lines: string[]; size: number } {
  for (const size of [72, 62, 54, 46]) {
    const max = Math.floor(880 / (size * 0.56));
    const lines: string[] = [];
    let cur = "";
    for (const w of name.split(/\s+/)) {
      if (!cur) cur = w;
      else if ((cur + " " + w).length <= max) cur += " " + w;
      else { lines.push(cur); cur = w; }
    }
    if (cur) lines.push(cur);
    if (lines.length <= 2 && lines.every((l) => l.length <= max)) return { lines, size };
  }
  const max = Math.floor(880 / (46 * 0.56));
  return { lines: [name.slice(0, max - 1) + "…"], size: 46 };
}

export function pinSvg(plateSvg: string, name: string, domain: string): string {
  const vb = /viewBox="([\d.\s-]+)"/.exec(plateSvg)?.[1]?.split(/\s+/).map(Number) ?? [0, 0, 200, 200];
  const [, , w = 200, h = 200] = vb;
  const boxW = 860, boxH = 1060;
  const scale = Math.min(boxW / w, boxH / h);
  const pw = w * scale, ph = h * scale;
  const px = (1000 - pw) / 2, py = 70 + (boxH - ph) / 2;
  const inner = plateSvg.replace(/^<svg[^>]*>/, "").replace(/<\/svg>\s*$/, "");
  const style = /<style>[\s\S]*?<\/style>/.exec(plateSvg)?.[0] ?? "";
  const { lines, size } = titleLines(name);
  const ty = 1260 - ((lines.length - 1) * size * 1.1) / 2;
  /* Kleuren van het plaatje zelf (papier, inkt), niet van de site. */
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1500" viewBox="0 0 1000 1500">${style}`
    + `<rect width="1000" height="1500" fill="#fbf6ec"/><rect x="40" y="40" width="920" height="1120" rx="36" fill="#ffffff"/>`
    + `<g transform="translate(${px.toFixed(1)} ${py.toFixed(1)}) scale(${scale.toFixed(4)})">${inner.replace(/<style>[\s\S]*?<\/style>/, "")}</g>`
    + lines.map((l, i) => `<text x="500" y="${(ty + i * size * 1.1).toFixed(0)}" text-anchor="middle" font-family="Nunito" font-weight="700" font-size="${size}" fill="#1d1b22">${esc(l)}</text>`).join("")
    + `<text x="500" y="1440" text-anchor="middle" font-family="Nunito" font-weight="700" font-size="38" fill="#6b6475">${esc(domain)}</text></svg>`;
}
