/** Pure logica van de kleurstudio, los van React zodat hij te testen is. */

export const FREE_PALETTE = ["#e2483d", "#ff8a3d", "#f2c618", "#9bd34a", "#2fa45a", "#3ec7c1", "#4fa3f0", "#2f5bd3", "#7b5bd6", "#d0479b", "#f59fc4", "#a0673d", "#7a7f87", "#222222"];
export const ERASER = "eraser";
export type Line = "auto" | "dun" | "normaal" | "dik";
const LINE_SW: Record<Exclude<Line, "auto">, number> = { dun: 1.7, normaal: 2.4, dik: 3.4 };

export function strokeWidth(line: Line, ageWidth: number): number {
  return line === "auto" ? ageWidth : LINE_SW[line];
}

export interface Label { region: number; number: number; x: number; y: number; size: number }
export type Fills = Record<number, string>;

/** Hoeveel genummerde vlakken de juiste kleur hebben. */
export function progress(labels: Label[], palette: { number: number; hex: string }[], fills: Fills) {
  const hex = new Map(palette.map((p) => [p.number, p.hex.toLowerCase()]));
  const ok = labels.filter((l) => fills[l.region]?.toLowerCase() === hex.get(l.number)).length;
  return { ok, total: labels.length, done: labels.length > 0 && ok === labels.length };
}

/** Een vlak kleuren of gummen. Geeft de nieuwe stand en wat er eerst stond (voor ongedaan maken). */
export function paint(fills: Fills, region: number, color: string): { next: Fills; prev: string | undefined } {
  const next = { ...fills };
  const prev = fills[region];
  if (color === ERASER) delete next[region]; else next[region] = color;
  return { next, prev };
}

/** Hoogte van het tekenvlak: de plaat plus tekst en leerblad als die aan staan. */
export function layout(opts: { name: string; learn: boolean; word: string | null; question: string | null }) {
  let y = 200;
  const nameY = opts.name ? y : null; if (opts.name) y += 40;
  const learnY = opts.learn && opts.word ? y : null; if (learnY !== null) y += 46;
  const questionY = learnY !== null && opts.question ? y : null; if (questionY !== null) y += 28;
  return { height: y, nameY, learnY, questionY, nameSize: Math.min(26, 320 / Math.max(opts.name.length, 4)), wordSize: opts.word ? Math.min(30, 330 / opts.word.length) : 0 };
}
