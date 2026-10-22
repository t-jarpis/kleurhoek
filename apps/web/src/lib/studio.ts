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
export function layout(opts: { name: string; learn: boolean; word: string | null; question: string | null; legend?: number }) {
  let y = 200;
  const nameY = opts.name ? y : null; if (opts.name) y += 40;
  const learnY = opts.learn && opts.word ? y : null; if (learnY !== null) y += 46;
  const questionY = learnY !== null && opts.question ? y : null; if (questionY !== null) y += 28;
  const legendY = opts.legend ? y : null; if (legendY !== null) y += 32;
  return {
    height: y, nameY, learnY, questionY, legendY,
    nameSize: Math.min(26, 320 / Math.max(opts.name.length, 4)),
    wordSize: opts.word ? Math.min(30, 330 / opts.word.length) : 0,
    legendStep: opts.legend ? Math.min(26, 184 / opts.legend) : 0,
  };
}

/** Werk dat op de koelkast hangt: een momentopname van de kleuren, alleen op dit apparaat. */
export interface FridgeItem { id: string; slug: string; version: number; fills: Fills; name: string; date: string }
export const FRIDGE_MAX = 24;

/** Nieuw werk komt vooraan; de oudste valt eraf als de koelkast vol is. */
export function hang(list: FridgeItem[], item: FridgeItem): FridgeItem[] {
  return [item, ...list].slice(0, FRIDGE_MAX);
}

export const BOOK_MAX = 30;
const SLUG = /^[a-z0-9-]{1,64}$/;

/** Platen voor het boekje uit de URL: alleen geldige namen, geen dubbele, hooguit 30. */
export function parseBook(value: string | string[] | undefined): string[] {
  const raw = Array.isArray(value) ? value.join(",") : value ?? "";
  return [...new Set(raw.split(",").map((s) => s.trim()).filter((s) => SLUG.test(s)))].slice(0, BOOK_MAX);
}

/** Een plaat aan- of uitzetten in de keuze voor het boekje. */
export function togglePick(list: string[], slug: string): string[] {
  return list.includes(slug) ? list.filter((s) => s !== slug) : [...list, slug].slice(0, BOOK_MAX);
}
