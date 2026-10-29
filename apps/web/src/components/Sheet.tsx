"use client";
import { useEffect, useId, useMemo, useRef, type CSSProperties, type MouseEvent, type Ref } from "react";
import { composeInner, EMPTY_ART, fillCss, hasArt, inkOf, type Art, type Brush } from "@/lib/atelier";
import { layout, type Fills, type Label } from "@/lib/studio";
import { useMark } from "./Base";

export interface SheetPlate {
  name: string;
  /** Hoogte van de tekening; kleurplaten 200, knutselplaten vaak hoger. */
  height?: number;
  regionCount: number;
  word: string | null;
  countQuestion: string | null;
  labels: Label[];
  palette: { number: number; hex: string }[];
}

/**
 * Eén vel: de plaat met kleuren en wat er optioneel bij hoort (nummers, tekst, leerblad,
 * kleurenlijst). Gebruikt door de kleurstudio, de koelkast en het boekje.
 */
export function Sheet({ plate, inner, fills = {}, sw, numbers = false, legend = false, name = "", learn = false, onPick, className = "sheet", marked = true, art, live, svgRef }: {
  plate: SheetPlate; inner: string; fills?: Fills; sw: number; numbers?: boolean; legend?: boolean; name?: string; learn?: boolean;
  onPick?: (region: number) => void; className?: string; marked?: boolean;
  /** Werk uit het Atelier (ADR 0056): streken, zon, lijnkleur, verlopen en patronen. */
  art?: Art;
  /** Het vlak waarin nu getekend wordt; de streek zelf zet de kleurstudio in `[data-live]`. */
  live?: { region: number; brush: Brush; color: string } | null;
  svgRef?: Ref<SVGSVGElement>;
}) {
  const group = useRef<SVGGElement>(null);
  const id = `kh${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const composed = useMemo(() => {
    const a = art ?? EMPTY_ART;
    return live || hasArt(a, fills) ? composeInner(inner, a, fills, id, live ?? undefined) : inner;
  }, [inner, art, fills, id, live]);
  const ink = art ? inkOf(art.lines) : null;
  // Herkomst onder het vel (PlateMark): een eigen strook, niet op een eigen omgeving van een organisatie.
  const site = useMark();
  const mark = marked ? site : null;
  const MARK_H = 8;
  // De plaat zelf is statische SVG; React raakt die niet aan, alleen de vulkleur van de vlakken.
  useEffect(() => {
    group.current?.querySelectorAll<SVGElement>("[data-i]").forEach((el) => { const i = Number(el.dataset.i); el.style.fill = fillCss(fills[i], id, i); });
  }, [fills, composed, id]);

  const L = layout({ name, learn, word: plate.word, question: plate.countQuestion, legend: legend ? plate.palette.length : 0, height: plate.height ?? 200 });
  const hexByNumber = new Map(plate.palette.map((p) => [p.number, p.hex.toLowerCase()]));
  const click = onPick ? (e: MouseEvent<SVGSVGElement>) => {
    const el = (e.target as Element).closest<SVGElement>("[data-i]");
    if (el?.dataset.i) onPick(Number(el.dataset.i));
  } : undefined;
  const x0 = 100 - (L.legendStep * (plate.palette.length - 1)) / 2;

  return (
    <svg ref={svgRef} data-id={id} className={className} viewBox={`0 0 200 ${L.height + (mark ? MARK_H : 0)}`} style={{ "--sw": sw, ...(ink ? { "--plate-ink": ink } : {}) } as CSSProperties}
      data-lines={art?.lines.kind === "geen" ? "geen" : undefined} onClick={click} role="img" aria-label={plate.name}>
      <g ref={group} data-inner="" dangerouslySetInnerHTML={{ __html: composed }} />
      {numbers && (
        <g aria-hidden="true">
          {plate.labels.filter((l) => fills[l.region]?.toLowerCase() !== hexByNumber.get(l.number)).map((l) => (
            <text key={l.region} className="num" x={l.x} y={l.y} fontSize={l.size}>{l.number}</text>
          ))}
        </g>
      )}
      {L.nameY !== null && (
        <text className="r nm" data-i={plate.regionCount} x={100} y={L.nameY + 28} textAnchor="middle" fontSize={L.nameSize} style={{ fill: fillCss(fills[plate.regionCount], id, plate.regionCount) }}>{name}</text>
      )}
      {L.learnY !== null && plate.word && (
        <g>
          <path className="guide" d={`M14 ${L.learnY + 12} L186 ${L.learnY + 12} M14 ${L.learnY + 36} L186 ${L.learnY + 36}`} strokeDasharray="3 3" />
          <path className="guide" d={`M14 ${L.learnY + 24} L186 ${L.learnY + 24}`} />
          <text className="trace" x={100} y={L.learnY + 36} textAnchor="middle" fontSize={L.wordSize}>{plate.word}</text>
          {L.questionY !== null && (<><text className="q" x={14} y={L.questionY + 14} fontSize={9}>{plate.countQuestion}</text><rect className="ans" x={160} y={L.questionY} width={26} height={20} rx={4} /></>)}
        </g>
      )}
      {L.legendY !== null && (
        <g aria-hidden="true">
          {plate.palette.map((p, j) => (
            <g key={p.number}>
              <circle className="lg" cx={x0 + j * L.legendStep} cy={L.legendY! + 10} r={7} fill={p.hex} />
              <text className="lgt" x={x0 + j * L.legendStep} y={L.legendY! + 27}>{p.number}</text>
            </g>
          ))}
        </g>
      )}
      {mark && <text className="kh-mark" x={100} y={L.height + MARK_H - 2.5} textAnchor="middle" aria-hidden="true">{mark}</text>}
    </svg>
  );
}

/** Van PlateDetail naar wat een vel nodig heeft. */
export function sheetPlate(p: { name: string; height: number; regionCount: number; word: string | null; countQuestion: string | null; colorByNumber: { labels: Label[]; palette: { number: number; hex: string }[] } }): SheetPlate {
  return { name: p.name, height: p.height, regionCount: p.regionCount, word: p.word, countQuestion: p.countQuestion, labels: p.colorByNumber.labels, palette: p.colorByNumber.palette };
}
