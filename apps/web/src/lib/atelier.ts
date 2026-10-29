import { getStroke } from "perfect-freehand";
import type { Fills } from "./studio";

/**
 * Atelier (ADR 0056): de uitgebreide kleurstudio voor wie graag tekent. Pure logica, los van React, zodat hij
 * te testen is en dezelfde code het scherm, de afdruk, de koelkast, de afbeelding en de time-lapse maakt.
 *
 * Het werk is een lijst handelingen (vullen en streken) in de volgorde waarin ze gedaan zijn. Ongedaan maken
 * haalt de laatste weg, de time-lapse speelt ze opnieuw af. Alles blijft op het apparaat.
 */

export const BRUSHES = ["potlood", "stift", "waterverf", "airbrush", "gum"] as const;
export type Brush = (typeof BRUSHES)[number];
export const FILL_TOOLS = ["vullen", "verloop", "patroon", "pipet"] as const;
export type FillTool = (typeof FILL_TOOLS)[number];
export type Tool = Brush | FillTool;
export const PATTERNS = ["stippen", "strepen", "ruitjes", "golfjes"] as const;
export type Pattern = (typeof PATTERNS)[number];

/** Een streek: in welk vlak hij begon (daar blijft hij binnen), penseel, kleur, dikte en punten x, y, druk. */
export interface Stroke { t: "s"; r: number; b: Brush; c: string; w: number; pen?: boolean; pts: number[]; id?: string }
/** Een vlak vullen; `p` is wat er eerst stond, voor ongedaan maken en de time-lapse. */
export interface FillOp { t: "f"; r: number; v: string | null; p: string | null; id?: string }
export type Op = Stroke | FillOp;
/** De zon: uit welke richting het licht komt (graden, 0 = rechts, 90 = onder) en hoe sterk (0–1). */
export interface Sun { a: number; s: number }
export type LineKind = "inkt" | "sepia" | "kleur" | "geen";
export interface Lines { kind: LineKind; c?: string }
export interface Art { ops: Op[]; sun: Sun | null; lines: Lines }

export const EMPTY_ART: Art = { ops: [], sun: null, lines: { kind: "inkt" } };
export const DEFAULT_SUN: Sun = { a: 225, s: 0.6 };
/** Lijnkleur sepia: inhoud van de tekening, geen stijl van de site. */
export const SEPIA = /* theme-allow */ "#704214";

interface BrushSpec { size: number; opacity: number; thinning: number; fx?: "korrel" | "verf" | "spray" }
export const BRUSH: Record<Brush, BrushSpec> = {
  potlood: { size: 2.2, opacity: 0.88, thinning: 0.55, fx: "korrel" },
  stift: { size: 4, opacity: 1, thinning: 0.15 },
  waterverf: { size: 11, opacity: 0.3, thinning: 0.35, fx: "verf" },
  airbrush: { size: 18, opacity: 0.13, thinning: 0, fx: "spray" },
  gum: { size: 9, opacity: 1, thinning: 0.2 },
};

/* ---------- Vullingen: effen, verloop of patroon, als tekst in dezelfde kleurenlijst als altijd ---------- */

export type FillValue = { kind: "effen"; a: string } | { kind: "verloop"; a: string; b: string } | { kind: "patroon"; pattern: Pattern; a: string; b: string };
const HEX = /^#[0-9a-f]{6}$/i;

export const gradientValue = (a: string, b: string) => `g:${a}:${b}`;
export const patternValue = (pattern: Pattern, a: string, b: string) => `p:${pattern}:${a}:${b}`;

export function parseFill(v: string | undefined | null): FillValue | null {
  if (!v) return null;
  const parts = v.split(":");
  if (parts[0] === "g" && HEX.test(parts[1] ?? "") && HEX.test(parts[2] ?? "")) return { kind: "verloop", a: parts[1]!, b: parts[2]! };
  if (parts[0] === "p" && (PATTERNS as readonly string[]).includes(parts[1] ?? "") && HEX.test(parts[2] ?? "") && HEX.test(parts[3] ?? ""))
    return { kind: "patroon", pattern: parts[1] as Pattern, a: parts[2]!, b: parts[3]! };
  return HEX.test(v) ? { kind: "effen", a: v } : null;
}

/** De kleur die de pipet uit een vlak haalt. */
export const pickColor = (v: string | undefined | null) => parseFill(v)?.a ?? null;

/** Wat er in `fill` van een vlak komt: een kleur, of een verwijzing naar het verloop of patroon van dat vlak. */
export function fillCss(v: string | undefined, id: string, region: number): string {
  const f = parseFill(v);
  if (!f) return "";
  return f.kind === "effen" ? f.a : `url(#${id}-f${region})`;
}

/** Heeft deze vulling een eigen definitie nodig (verloop of patroon)? */
const needsDef = (v: string | undefined) => { const f = parseFill(v); return f !== null && f.kind !== "effen"; };

function fillDef(f: FillValue, id: string, region: number, sun: Sun | null): string {
  const fid = `${id}-f${region}`;
  if (f.kind === "verloop") {
    // Het verloop loopt mee met de zon als die aan staat, anders van boven naar beneden.
    const [x1, y1, x2, y2] = sun ? direction(sun.a) : [0.5, 0, 0.5, 1];
    return `<linearGradient id="${fid}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"><stop offset="0" stop-color="${f.b}"/><stop offset="1" stop-color="${f.a}"/></linearGradient>`;
  }
  if (f.kind === "patroon") {
    const bg = `<rect width="8" height="8" fill="${f.b}"/>`;
    const fg = {
      stippen: `<circle cx="2" cy="2" r="1.2" fill="${f.a}"/><circle cx="6" cy="6" r="1.2" fill="${f.a}"/>`,
      strepen: `<path d="M-2 2 L2 -2 M0 8 L8 0 M6 10 L10 6" stroke="${f.a}" stroke-width="1.6"/>`,
      ruitjes: `<path d="M0 4 H8 M4 0 V8" stroke="${f.a}" stroke-width="1.1"/>`,
      golfjes: `<path d="M0 4 Q2 1.5 4 4 T8 4" fill="none" stroke="${f.a}" stroke-width="1.2"/>`,
    }[f.pattern];
    return `<pattern id="${fid}" width="8" height="8" patternUnits="userSpaceOnUse">${bg}${fg}</pattern>`;
  }
  return "";
}

/* ---------- Streken ---------- */

/** Een streek als vlak, met dikte die meegaat met druk en snelheid. */
export function strokePath(s: Stroke): string {
  const spec = BRUSH[s.b];
  const pts: [number, number, number][] = [];
  for (let i = 0; i + 2 < s.pts.length; i += 3) pts.push([s.pts[i]!, s.pts[i + 1]!, s.pts[i + 2]!]);
  if (!pts.length) return "";
  const outline = getStroke(pts, { size: spec.size * s.w, thinning: spec.thinning, smoothing: 0.55, streamline: 0.35, simulatePressure: !s.pen, last: true });
  return pathFromOutline(outline);
}

function pathFromOutline(points: number[][]): string {
  if (points.length < 3) return "";
  const r = (n: number) => Math.round(n * 100) / 100;
  let d = `M${r(points[0]![0]!)} ${r(points[0]![1]!)} Q`;
  for (let i = 0; i < points.length; i++) {
    const [x0, y0] = points[i]!; const [x1, y1] = points[(i + 1) % points.length]!;
    d += `${r(x0!)} ${r(y0!)} ${r((x0! + x1!) / 2)} ${r((y0! + y1!) / 2)} `;
  }
  return `${d}Z`;
}

/** Punten afronden voor de opslag: genoeg voor een vel van 200 breed, en veel kleiner. */
export function roundPoint(x: number, y: number, p: number): [number, number, number] {
  return [Math.round(x * 10) / 10, Math.round(y * 10) / 10, Math.round(p * 100) / 100];
}

/* ---------- De zon ---------- */

/** Van een richting naar begin- en eindpunt van een verloop over een vorm (0–1). */
function direction(angle: number): [number, number, number, number] {
  const rad = (angle * Math.PI) / 180;
  const dx = Math.cos(rad) / 2; const dy = Math.sin(rad) / 2;
  const r = (n: number) => Math.round(n * 1000) / 1000;
  return [r(0.5 + dx), r(0.5 + dy), r(0.5 - dx), r(0.5 - dy)];
}

function sunDef(id: string, sun: Sun): string {
  const [x1, y1, x2, y2] = direction(sun.a);
  const s = Math.max(0, Math.min(1, sun.s));
  const light = "#ffffff", dark = "#1b1530"; // theme-allow: licht en schaduw in de tekening
  return `<linearGradient id="${id}-sun" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"><stop offset="0" stop-color="${light}" stop-opacity="${(0.6 * s).toFixed(3)}"/><stop offset="0.42" stop-color="${light}" stop-opacity="0"/><stop offset="0.58" stop-color="${dark}" stop-opacity="0"/><stop offset="1" stop-color="${dark}" stop-opacity="${(0.5 * s).toFixed(3)}"/></linearGradient>`;
}

/* ---------- Alles samen: de plaat met het werk erin ---------- */

const FILTERS = (id: string) => [
  // Potlood: korrel van het papier, de kleur valt deels weg.
  `<filter id="${id}-fx-korrel" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="3" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.6 1.25" result="a"/><feComposite in="SourceGraphic" in2="a" operator="in"/></filter>`,
  // Waterverf: zachte, grillige rand.
  `<filter id="${id}-fx-verf" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.08" numOctaves="2" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="2.4" result="d"/><feGaussianBlur in="d" stdDeviation="0.7"/></filter>`,
  // Airbrush: een zachte nevel.
  `<filter id="${id}-fx-spray" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.2"/></filter>`,
].join("");

/** Alleen de streken die er nog zijn, per vlak, in volgorde. */
export function strokesByRegion(art: Art): Map<number, Stroke[]> {
  const by = new Map<number, Stroke[]>();
  for (const op of art.ops) if (op.t === "s") by.set(op.r, [...(by.get(op.r) ?? []), op]);
  return by;
}

function regionArt(strokes: Stroke[], id: string, region: number): { markup: string; defs: string } {
  let acc = ""; let defs = "";
  strokes.forEach((s, k) => {
    const d = strokePath(s);
    if (!d) return;
    if (s.b === "gum") {
      // De gum haalt weg wat eronder ligt; wat erna komt, blijft staan.
      const mid = `${id}-m${region}-${k}`;
      defs += `<mask id="${mid}" maskUnits="userSpaceOnUse" x="-50" y="-50" width="300" height="2000"><rect x="-50" y="-50" width="300" height="2000" fill="white"/><path d="${d}" fill="black"/></mask>`;
      acc = `<g mask="url(#${mid})">${acc}</g>`;
      return;
    }
    const spec = BRUSH[s.b];
    acc += `<path d="${d}" fill="${s.c}" fill-opacity="${spec.opacity}"${spec.fx ? ` filter="url(#${id}-fx-${spec.fx})"` : ""}/>`;
  });
  return { markup: acc, defs };
}

/** Een kopie van een vlak zonder nummer, id of klasse, voor de zon en de omlijning erboven. */
const dup = (tag: string, cls: string, extra = "") => tag
  .replace(/\s(?:class|data-i|id|style)="[^"]*"/g, "")
  .replace(/\/>$/, ` class="${cls}" pointer-events="none"${extra}/>`);

const REGION = /<(rect|circle|ellipse|path|polygon)\b[^>]*\bdata-i="(\d+)"[^>]*\/>/g;

/**
 * De binnenkant van de plaat met het werk erin. Elk vlak houdt zijn plek in de tekening: de streken van een vlak
 * komen direct ná dat vlak, dus wat erboven getekend is (ogen op een hoofd) blijft erboven. Een kopie van het
 * vlak geeft licht en schaduw van de zon, een tweede kopie tekent de lijn weer scherp over de streken.
 * `live`: het vlak waar nu getekend wordt, met een lege streek die tijdens het tekenen wordt bijgewerkt.
 */
export function composeInner(inner: string, art: Art, fills: Fills, id: string, live?: { region: number; brush: Brush; color: string }): string {
  const by = strokesByRegion(art);
  let defs = FILTERS(id);
  if (art.sun) defs += sunDef(id, art.sun);
  const body = inner.replace(REGION, (tag, _el, n: string) => {
    const region = Number(n);
    const strokes = by.get(region) ?? [];
    const fill = fills[region];
    if (needsDef(fill)) defs += fillDef(parseFill(fill)!, id, region, art.sun);
    const isLive = live?.region === region;
    const lit = !!art.sun && (!!fill || strokes.length > 0 || isLive);
    // De vulkleur staat er ook zelf in, zodat een afbeelding of filmpje van deze tekst klopt zonder de pagina.
    const css = fillCss(fill, id, region);
    const own = tag.replace(/\/>$/, ` id="${id}-r${region}"${css ? ` style="fill:${css}"` : ""}/>`);
    if (!strokes.length && !lit && !isLive) return own;
    let out = own;
    if (strokes.length || isLive) {
      const { markup, defs: d } = regionArt(strokes, id, region);
      defs += `<clipPath id="${id}-c${region}"><use href="#${id}-r${region}"/></clipPath>` + d;
      const liveSpec = live && isLive ? BRUSH[live.brush] : null;
      const livePath = liveSpec ? `<path data-live="1" d="" fill="${live!.brush === "gum" ? "var(--color-paper)" : live!.color}" fill-opacity="${live!.brush === "gum" ? 0.6 : liveSpec.opacity}"${liveSpec.fx && live!.brush !== "gum" ? ` filter="url(#${id}-fx-${liveSpec.fx})"` : ""}/>` : "";
      out += `<g clip-path="url(#${id}-c${region})" pointer-events="none">${markup}${livePath}</g>`;
    }
    if (lit) out += dup(tag, "kh-sun", ` fill="url(#${id}-sun)"`);
    out += dup(tag, "kh-ro");
    return out;
  });
  // Vlakken buiten de tekening zelf (de naam onder de plaat) met een verloop of patroon.
  for (const [k, v] of Object.entries(fills)) {
    const region = Number(k);
    if (needsDef(v) && !defs.includes(`id="${id}-f${region}"`)) defs += fillDef(parseFill(v)!, id, region, art.sun);
  }
  return `<defs>${defs}</defs>${body}`;
}

/** Heeft dit werk iets nodig dat de gewone plaat niet heeft? */
export function hasArt(art: Art | undefined, fills: Fills): boolean {
  return !!art && (art.ops.some((o) => o.t === "s") || !!art.sun || art.lines.kind !== "inkt") || Object.values(fills).some((v) => needsDef(v));
}

/** De lijnkleur van de plaat, of null voor de gewone inkt. */
export function inkOf(lines: Lines): string | null {
  return lines.kind === "sepia" ? SEPIA : lines.kind === "kleur" && lines.c && HEX.test(lines.c) ? lines.c : null;
}

/* ---------- Handelingen ---------- */

/** Een vlak vullen, als handeling die ongedaan kan worden. */
export function fillOp(fills: Fills, region: number, value: string | null): { fills: Fills; op: FillOp } {
  const next = { ...fills };
  const prev = fills[region] ?? null;
  if (value === null) delete next[region]; else next[region] = value;
  return { fills: next, op: { t: "f", r: region, v: value, p: prev } };
}

/** De laatste handeling terugdraaien. */
export function undoLast(art: Art, fills: Fills): { art: Art; fills: Fills } | null {
  const op = art.ops.at(-1);
  if (!op) return null;
  const ops = art.ops.slice(0, -1);
  if (op.t === "s") return { art: { ...art, ops }, fills };
  const next = { ...fills };
  if (op.p === null) delete next[op.r]; else next[op.r] = op.p;
  return { art: { ...art, ops }, fills: next };
}

/**
 * Time-lapse: het werk stap voor stap opnieuw. Geeft voor elk beeld de kleuren en de streken tot dan toe; een
 * lange streek groeit over een paar beelden, zodat je hem ziet ontstaan. Kleuren van vóór het Atelier (zonder
 * handeling) staan er vanaf het eerste beeld.
 */
export function replay(art: Art, fills: Fills, maxFrames = 180): { art: Art; fills: Fills }[] {
  const base = { ...fills };
  for (let i = art.ops.length - 1; i >= 0; i--) {
    const op = art.ops[i]!;
    if (op.t === "f") { if (op.p === null) delete base[op.r]; else base[op.r] = op.p; }
  }
  // Stappen: na handeling i (heel), of handeling i als deel van een streek.
  const steps: { upto: number; part?: Stroke }[] = [];
  art.ops.forEach((op, i) => {
    if (op.t === "s") {
      const points = op.pts.length / 3;
      const parts = Math.min(6, Math.ceil(points / 10));
      for (let k = 1; k < parts; k++) steps.push({ upto: i, part: { ...op, pts: op.pts.slice(0, Math.max(3, Math.round((points * k) / parts)) * 3) } });
    }
    steps.push({ upto: i + 1 });
  });
  const frames = Math.max(1, Math.min(maxFrames, steps.length));
  const out: { art: Art; fills: Fills }[] = [{ art: { ...art, ops: [] }, fills: { ...base } }];
  let cur = { ...base };
  let done = 0;
  for (let f = 1; f <= frames && steps.length; f++) {
    const step = steps[Math.round((f / frames) * steps.length) - 1]!;
    for (; done < step.upto; done++) {
      const op = art.ops[done]!;
      if (op.t === "f") { cur = { ...cur }; if (op.v === null) delete cur[op.r]; else cur[op.r] = op.v; }
    }
    const ops = art.ops.slice(0, step.upto);
    out.push({ art: { ...art, ops: step.part ? [...ops, step.part] : ops }, fills: { ...cur } });
  }
  return out;
}

/* ---------- Samen kleuren (ADR 0060) ---------- */

/** Een handeling in een gedeelde kamer: vullen of een streek, of iets ongedaan maken (x) of opnieuw beginnen (c). */
export type SharedOp = (Op & { id: string }) | { t: "x"; id: string; ref: string } | { t: "c"; id: string };

/** De plaat uit de gedeelde lijst: ongedaan gemaakte handelingen eruit, alles vóór "opnieuw" weg. */
export function deriveShared(log: SharedOp[]): { ops: Op[]; fills: Fills } {
  let ops: Op[] = [];
  for (const op of log) {
    if (op.t === "c") ops = [];
    else if (op.t === "x") ops = ops.filter((o) => o.id !== op.ref);
    else ops.push(op);
  }
  const fills: Fills = {};
  for (const op of ops) if (op.t === "f") { if (op.v === null) delete fills[op.r]; else fills[op.r] = op.v; }
  return { ops, fills };
}

/** Het werk dat er al was als handelingen, om een kamer mee te beginnen. */
export function toShared(fills: Fills, art: Art, id: () => string): SharedOp[] {
  const strokes = art.ops.filter((o): o is Stroke => o.t === "s");
  return [
    ...Object.entries(fills).filter(([, v]) => !!v).map(([r, v]) => ({ t: "f" as const, r: Number(r), v, p: null, id: id() })),
    ...strokes.map((s) => ({ ...s, id: id() })),
  ];
}

/* ---------- Opslag ---------- */

const isNum = (x: unknown): x is number => typeof x === "number" && Number.isFinite(x);
const isColor = (x: unknown): x is string => typeof x === "string" && HEX.test(x);

/** Werk uit de opslag van het apparaat, met alles wat niet klopt eruit gefilterd. */
export function normalizeArt(raw: unknown): Art {
  if (!raw || typeof raw !== "object") return EMPTY_ART;
  const r = raw as Partial<Art>;
  const ops: Op[] = Array.isArray(r.ops) ? r.ops.filter((o): o is Op => {
    if (!o || typeof o !== "object" || !isNum((o as Op).r)) return false;
    if (o.t === "s") return (BRUSHES as readonly string[]).includes(o.b) && isColor(o.c) && isNum(o.w) && Array.isArray(o.pts) && o.pts.every(isNum);
    if (o.t === "f") return (o.v === null || typeof o.v === "string") && (o.p === null || typeof o.p === "string");
    return false;
  }) : [];
  const sun = r.sun && isNum(r.sun.a) && isNum(r.sun.s) ? { a: r.sun.a, s: r.sun.s } : null;
  const kinds: LineKind[] = ["inkt", "sepia", "kleur", "geen"];
  const lines: Lines = r.lines && kinds.includes(r.lines.kind) ? { kind: r.lines.kind, ...(isColor(r.lines.c) ? { c: r.lines.c } : {}) } : { kind: "inkt" };
  return { ops, sun, lines };
}

/* ---------- Kleuren ---------- */

export function hexToHsl(hex: string): [number, number, number] {
  const n = parseInt(hex.slice(1), 16);
  const r = ((n >> 16) & 255) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2;
  if (max === min) return [0, 0, Math.round(l * 100)];
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  const h = max === r ? (g - b) / d + (g < b ? 6 : 0) : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return [Math.round(h * 60), Math.round(s * 100), Math.round(l * 100)];
}

export function hslToHex(h: number, s: number, l: number): string {
  const S = s / 100, L = l / 100;
  const k = (n: number) => (n + h / 30) % 12;
  const a = S * Math.min(L, 1 - L);
  const f = (n: number) => Math.round(255 * (L - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)))));
  return `#${[f(0), f(8), f(4)].map((x) => x.toString(16).padStart(2, "0")).join("")}`;
}

/** Kleuren die bij een kleur passen: de tegenkleur, twee buren en twee uit de driehoek. */
export function harmony(hex: string): string[] {
  const [h, s, l] = hexToHsl(hex);
  return [180, -30, 30, 120, 240].map((d) => hslToHex((h + d + 360) % 360, s, l));
}

/** Lichter en donkerder van dezelfde kleur, voor licht en schaduw met de hand. */
export function shades(hex: string): string[] {
  const [h, s, l] = hexToHsl(hex);
  return [-30, -15, 15, 30].map((d) => hslToHex(h, s, Math.max(4, Math.min(96, l + d))));
}

/** Sfeerpaletten: inhoud van het Atelier, geen stijl van de site. */
export const MOODS: Record<string, string[]> = /* theme-allow */ {
  zonsondergang: ["#ffcf6b", "#ff9a5a", "#f2635f", "#c2417a", "#6d2e83", "#2e2157"], // theme-allow
  bos: ["#e3e8b5", "#9cc46b", "#4e9a4a", "#2f6b3a", "#7a5232", "#3c2a1e"], // theme-allow
  pastel: ["#ffd6e0", "#ffe9b8", "#d9f2c4", "#c6e6fb", "#e0d4fb", "#fbe3cf"], // theme-allow
  zee: ["#e9f6f7", "#9fdde0", "#3cb4c4", "#1f7aa6", "#18406b", "#f2d7a0"], // theme-allow
  nacht: ["#0f1630", "#24305e", "#45528f", "#8a8fc7", "#f3e9a5", "#c8c8d6"], // theme-allow
};
