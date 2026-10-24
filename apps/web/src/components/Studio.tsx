"use client";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import type { PlateDetail } from "@/lib/types";
import { messages } from "@/i18n/nl";
import { track } from "@/lib/track";
import { ERASER, FREE_PALETTE, paint, progress, strokeWidth, type Fills, type Line } from "@/lib/studio";
import { fridge } from "@/lib/local";
import { Sheet, sheetPlate } from "./Sheet";

interface Saved { fills: Fills; name: string }
const storageKey = (p: PlateDetail) => `kh:${p.slug}:v${p.version}`;
function load(p: PlateDetail): Saved {
  try { return { fills: {}, name: "", ...JSON.parse(localStorage.getItem(storageKey(p)) ?? "{}") }; } catch { return { fills: {}, name: "" }; }
}

export function Studio({ plate, inner, ageWidth, market, language }: { plate: PlateDetail; inner: string; ageWidth: number; market: string; language: string }) {
  const t = messages(language);
  const [mode, setMode] = useState<"free" | "num">("free");
  const [color, setColor] = useState(FREE_PALETTE[0]!);
  const [fills, setFills] = useState<Fills>({});
  const [undo, setUndo] = useState<{ region: number; prev: string | undefined }[]>([]);
  const [line, setLine] = useState<Line>("auto");
  const [name, setName] = useState("");
  const [learn, setLearn] = useState(false);
  const [sure, setSure] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [printWhat, setPrintWhat] = useState<"kleur" | "leeg">("kleur");
  const colored = useRef(false);
  const wasDone = useRef(false);

  // Werk van dit apparaat terugzetten (alleen in deze browser, geen account nodig).
  // Pas opslaan na het laden: anders overschrijft de lege beginstand het bewaarde werk.
  const [loaded, setLoaded] = useState<string | null>(null);
  useEffect(() => { const s = load(plate); setFills(s.fills); setName(s.name); setLoaded(storageKey(plate)); }, [plate]);
  useEffect(() => {
    if (loaded !== storageKey(plate)) return;
    try { localStorage.setItem(storageKey(plate), JSON.stringify({ fills, name })); } catch { /* opslag vol of geblokkeerd */ }
  }, [plate, fills, name, loaded]);
  useEffect(() => { track({ type: "plate_view", market, plate: plate.slug }); }, [market, plate.slug]);

  const palette = mode === "num" ? plate.colorByNumber.palette : FREE_PALETTE.map((hex, i) => ({ number: i + 1, code: hex, hex, name: hex }));
  const prog = useMemo(() => progress(plate.colorByNumber.labels, plate.colorByNumber.palette, fills), [plate, fills]);

  useEffect(() => {
    if (mode !== "num") return;
    if (prog.done && !wasDone.current) { flash(t.party); track({ type: "plate_completed", market, plate: plate.slug }); }
    wasDone.current = prog.done;
  }, [prog.done, mode, t.party, market, plate.slug]);

  const apply = useCallback((region: number) => {
    setFills((f) => { const { next, prev } = paint(f, region, color); setUndo((u) => [...u, { region, prev }]); return next; });
    if (!colored.current) { colored.current = true; track({ type: "plate_colored", market, plate: plate.slug }); }
  }, [color, market, plate.slug]);

  const switchMode = (m: "free" | "num") => {
    setMode(m);
    wasDone.current = m === "num" && progress(plate.colorByNumber.labels, plate.colorByNumber.palette, fills).done;
    if (m === "num") setColor(plate.colorByNumber.palette[0]?.hex ?? FREE_PALETTE[0]!);
  };

  const sw = strokeWidth(line, ageWidth);
  const hasColor = Object.values(fills).some(Boolean);
  const sheet = useMemo(() => sheetPlate(plate), [plate]);
  const flash = (text: string) => { setToast(text); setTimeout(() => setToast(null), 2600); };
  const toFridge = () => {
    const d = new Date();
    fridge.hang({ slug: plate.slug, version: plate.version, fills, name }, new Intl.DateTimeFormat(market, { day: "numeric", month: "short" }).format(d));
    flash(t.onFridge);
  };

  return (
    <div className="wrap" data-mode="kind">
      <div className="studio">
        <div className="studio-top">
          <Link href={`/${market}`} className="btn">{t.back}</Link>
          <h1>{plate.name}</h1>
        </div>
        <div className="canvas" data-print={hasColor ? printWhat : "kleur"}>
          <Sheet className="sheet sheet-live" plate={sheet} inner={inner} fills={fills} sw={sw} numbers={mode === "num"} name={name} learn={learn} onPick={apply} />
          {/* Leeg printen: dezelfde plaat zonder kleuren; het werk op het scherm blijft staan. */}
          {hasColor && printWhat === "leeg" && (
            <div className="print-copy" aria-hidden="true">
              <Sheet plate={sheet} inner={inner} sw={sw} numbers={mode === "num"} legend={mode === "num"} name={name} learn={learn} />
            </div>
          )}
        </div>
        <aside className="tools">
          <div className="tool">
            <h2>{t.howToColor}</h2>
            <div className="seg" role="group" aria-label={t.howToColor}>
              <button type="button" aria-pressed={mode === "free"} onClick={() => switchMode("free")}>{t.free}</button>
              <button type="button" aria-pressed={mode === "num"} onClick={() => switchMode("num")}>{t.byNumber}</button>
            </div>
            {mode === "num" && (
              <div className="prog"><span>{t.progress(prog.ok, prog.total)}</span><div className="bar"><i style={{ width: `${prog.total ? (prog.ok / prog.total) * 100 : 0}%` }} /></div></div>
            )}
          </div>
          <div className="tool">
            <h2>{mode === "num" ? t.colorPerNumber : t.colors}</h2>
            <div className="pal">
              {palette.map((p) => (
                <button key={p.hex} type="button" className="sw" style={{ "--c": p.hex } as CSSProperties} aria-label={mode === "num" ? `${p.number}: ${p.name}` : p.hex} aria-pressed={color === p.hex} onClick={() => setColor(p.hex)}>
                  {mode === "num" && <span>{p.number}</span>}
                </button>
              ))}
              <button type="button" className="sw eraser" aria-label={t.eraser} aria-pressed={color === ERASER} onClick={() => setColor(ERASER)} />
            </div>
          </div>
          <div className="tool">
            <h2>{t.lines}</h2>
            <div className="seg" role="group" aria-label={t.lines}>
              {(["auto", "dun", "normaal", "dik"] as const).map((l) => (
                <button key={l} type="button" aria-pressed={line === l} onClick={() => setLine(l)}>{{ auto: t.lineAuto, dun: t.lineThin, normaal: t.lineNormal, dik: t.lineThick }[l]}</button>
              ))}
            </div>
          </div>
          <div className="tool">
            <h2>{t.extra}</h2>
            <label className="hint" htmlFor="name">{t.nameHint}</label>
            <input id="name" className="input" maxLength={26} placeholder={t.namePlaceholder} autoComplete="off" value={name} onChange={(e) => setName(e.target.value)} />
            {plate.word && <label className="chk"><input type="checkbox" checked={learn} onChange={(e) => setLearn(e.target.checked)} /> <span>{t.learn}</span></label>}
          </div>
          <div className="row">
            <button type="button" className="btn" onClick={() => { const u = undo.at(-1); if (!u) return; setUndo(undo.slice(0, -1)); setFills((f) => paint(f, u.region, u.prev ?? ERASER).next); }}>{t.undo}</button>
            <button type="button" className="btn" onClick={() => { if (sure) { setFills({}); setUndo([]); setSure(false); } else { setSure(true); setTimeout(() => setSure(false), 2500); } }}>{sure ? t.resetSure : t.reset}</button>
          </div>
          {hasColor && (
            <div className="tool">
              <h2>{t.printWhat}</h2>
              <div className="seg" role="group" aria-label={t.printWhat}>
                <button type="button" aria-pressed={printWhat === "kleur"} onClick={() => setPrintWhat("kleur")}>{t.printColored}</button>
                <button type="button" aria-pressed={printWhat === "leeg"} onClick={() => setPrintWhat("leeg")}>{t.printBlank}</button>
              </div>
            </div>
          )}
          <div className="row">
            <button type="button" className="btn" onClick={toFridge}>{t.toFridge}</button>
            <button type="button" className="btn primary" onClick={() => { track({ type: "print", market, plate: plate.slug }); window.print(); }}>{t.print}</button>
          </div>
        </aside>
      </div>
      {toast && <div className="toast" role="status">{toast}</div>}
    </div>
  );
}
