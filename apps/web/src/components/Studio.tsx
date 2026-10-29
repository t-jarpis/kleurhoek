"use client";
import { useHref } from "./Base";
import { FavoriteButton } from "./FavoriteButton";
import Link from "next/link";
import { Icon } from "@kleurhoek/theme";
import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type PointerEvent as ReactPointerEvent } from "react";
import type { PlateDetail } from "@/lib/types";
import { messages } from "@/i18n/nl";
import { track } from "@/lib/track";
import { ERASER, FREE_PALETTE, progress, strokeWidth, type Fills, type Line } from "@/lib/studio";
import {
  BRUSHES, composeInner, deriveShared, EMPTY_ART, fillOp, gradientValue, normalizeArt, patternValue, pickColor, replay, roundPoint, strokePath, toShared, undoLast,
  type Art, type Brush, type Pattern, type Stroke, type Tool,
} from "@/lib/atelier";
import { canvasSize, download, drawSvg, playFrames, snapshotSvg, videoType } from "@/lib/export";
import { fridge } from "@/lib/local";
import { ColorMixer, LinePicker, PatternPicker, Range, SunDial, ToolPicker } from "./Atelier";
import { Sheet, sheetPlate } from "./Sheet";
import { TogetherPanel, useTogether } from "./Together";

interface Saved { fills: Fills; name: string; art: Art }
const storageKey = (p: PlateDetail) => `kh:${p.slug}:v${p.version}`;
function load(p: PlateDetail): Saved {
  try {
    const raw = JSON.parse(localStorage.getItem(storageKey(p)) ?? "{}") as Partial<Saved>;
    return { fills: raw.fills && typeof raw.fills === "object" ? raw.fills : {}, name: typeof raw.name === "string" ? raw.name : "", art: normalizeArt(raw.art) };
  } catch { return { fills: {}, name: "", art: EMPTY_ART }; }
}
/** Voorkeuren van dit apparaat voor het Atelier (ADR 0056): aan of uit, en de laatst gebruikte kleuren. */
const ATELIER = "kh:atelier";
const RECENT = "kh:atelier:kleuren";
const readLocal = <T,>(key: string, fallback: T): T => { try { const v = localStorage.getItem(key); return v ? (JSON.parse(v) as T) : fallback; } catch { return fallback; } };
const writeLocal = (key: string, v: unknown) => { try { localStorage.setItem(key, JSON.stringify(v)); return true; } catch { return false; } };

const isBrush = (t: Tool): t is Brush => (BRUSHES as readonly string[]).includes(t);
interface View { s: number; x: number; y: number }
const NO_ZOOM: View = { s: 1, x: 0, y: 0 };
type Pt = { x: number; y: number };

export function Studio({ plate, inner, ageWidth, market, language, accounts = false }: { plate: PlateDetail; inner: string; ageWidth: number; market: string; language: string; accounts?: boolean }) {
  const href = useHref();
  const t = messages(language);
  const [mode, setMode] = useState<"free" | "num">("free");
  const [color, setColor] = useState(FREE_PALETTE[0]!);
  const [fills, setFills] = useState<Fills>({});
  const [art, setArt] = useState<Art>(EMPTY_ART);
  const [line, setLine] = useState<Line>("auto");
  const [name, setName] = useState("");
  const [learn, setLearn] = useState(false);
  const [sure, setSure] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [printWhat, setPrintWhat] = useState<"kleur" | "leeg">("kleur");
  const colored = useRef(false);
  const wasDone = useRef(false);

  // Atelier (ADR 0056).
  const [atelier, setAtelier] = useState(false);
  const [tool, setTool] = useState<Tool>("potlood");
  const [prevTool, setPrevTool] = useState<Tool>("potlood");
  const [size, setSize] = useState(1);
  const [colorA, setColorA] = useState(FREE_PALETTE[0]!);
  const [colorB, setColorB] = useState(FREE_PALETTE[2]!);
  const [well, setWell] = useState<"a" | "b">("a");
  const [pattern, setPattern] = useState<Pattern>("stippen");
  const [recent, setRecent] = useState<string[]>([]);
  const [live, setLive] = useState<{ region: number; brush: Brush; color: string } | null>(null);
  const [view, setView] = useState<View>(NO_ZOOM);
  const [replayOpen, setReplayOpen] = useState(false);
  const svg = useRef<SVGSVGElement>(null);
  const port = useRef<HTMLDivElement>(null);

  const flash = (text: string) => { setToast(text); setTimeout(() => setToast(null), 2600); };

  // Samen kleuren (ADR 0060): in een kamer volgt de plaat uit de gedeelde lijst handelingen.
  const together = useTogether({
    onLog: (confirmed, pending) => {
      const d = deriveShared([...confirmed, ...pending]);
      setFills(d.fills);
      setArt((a) => ({ ...a, ops: d.ops }));
    },
  });
  const shared = together.active;
  const startTogether = () => void together.start(market, plate.slug, plate.version, (id) => toShared(fills, art, id));
  // Meedoen via een link (?samen=CODE).
  useEffect(() => {
    const code = new URLSearchParams(window.location.search).get("samen");
    if (code && /^[A-Za-z]{4}$/.test(code)) together.join(code);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Werk van dit apparaat terugzetten (alleen in deze browser, geen account nodig).
  // Pas opslaan na het laden: anders overschrijft de lege beginstand het bewaarde werk.
  const [loaded, setLoaded] = useState<string | null>(null);
  useEffect(() => {
    const s = load(plate); setFills(s.fills); setName(s.name); setArt(s.art); setLoaded(storageKey(plate));
    setAtelier(readLocal<unknown>(ATELIER, false) === true);
    const r = readLocal<unknown>(RECENT, []);
    setRecent(Array.isArray(r) ? r.filter((x): x is string => typeof x === "string" && /^#[0-9a-f]{6}$/i.test(x)).slice(0, 8) : []);
  }, [plate]);
  const warnedFull = useRef(false);
  useEffect(() => {
    if (loaded !== storageKey(plate)) return;
    const empty = art.ops.length === 0 && !art.sun && art.lines.kind === "inkt";
    if (!writeLocal(storageKey(plate), { fills, name, ...(empty ? {} : { art }) }) && !warnedFull.current) { warnedFull.current = true; flash(t.atelier.full); }
  }, [plate, fills, name, art, loaded]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { track({ type: "plate_view", market, plate: plate.slug }); }, [market, plate.slug]);

  const palette = mode === "num" ? plate.colorByNumber.palette : FREE_PALETTE.map((hex, i) => ({ number: i + 1, code: hex, hex, name: hex }));
  const prog = useMemo(() => progress(plate.colorByNumber.labels, plate.colorByNumber.palette, fills), [plate, fills]);
  const numbers = mode === "num" && !atelier;

  useEffect(() => {
    if (!numbers) return;
    if (prog.done && !wasDone.current) { flash(t.party); track({ type: "plate_completed", market, plate: plate.slug }); }
    wasDone.current = prog.done;
  }, [prog.done, numbers, t.party, market, plate.slug]); // eslint-disable-line react-hooks/exhaustive-deps

  const markColored = useCallback(() => {
    if (!colored.current) { colored.current = true; track({ type: "plate_colored", market, plate: plate.slug }); }
  }, [market, plate.slug]);
  const remember = useCallback((c: string) => setRecent((r) => { const next = [c, ...r.filter((x) => x !== c)].slice(0, 8); writeLocal(RECENT, next); return next; }), []);

  /** Een vlak vullen; in het Atelier ook met verloop of patroon, of de kleur eruit halen met de pipet. */
  const apply = useCallback((region: number) => {
    let value: string | null;
    if (!atelier) value = color === ERASER ? null : color;
    else if (tool === "pipet") {
      const c = pickColor(fills[region]);
      if (c) { (well === "a" ? setColorA : setColorB)(c); setTool(prevTool); }
      return;
    } else if (tool === "verloop") value = gradientValue(colorA, colorB);
    else if (tool === "patroon") value = patternValue(pattern, colorA, colorB);
    else value = colorA;
    const { fills: next, op } = fillOp(fills, region, value);
    if (shared) together.emit(op);
    else { setFills(next); setArt((a) => ({ ...a, ops: [...a.ops, op] })); }
    if (atelier) remember(colorA);
    markColored();
  }, [atelier, color, tool, fills, well, prevTool, colorA, colorB, pattern, markColored, remember, shared, together]);

  const chooseTool = (x: Tool) => { if (x === "pipet" && tool !== "pipet") setPrevTool(tool); setTool(x); };
  const switchMode = (m: "free" | "num") => {
    setMode(m);
    wasDone.current = m === "num" && progress(plate.colorByNumber.labels, plate.colorByNumber.palette, fills).done;
    if (m === "num") setColor(plate.colorByNumber.palette[0]?.hex ?? FREE_PALETTE[0]!);
  };
  const toggleAtelier = () => {
    const next = !atelier;
    setAtelier(next); writeLocal(ATELIER, next);
    if (!next) setView(NO_ZOOM);
    else if (color !== ERASER) setColorA(color);
  };

  const sw = strokeWidth(line, ageWidth);
  const hasColor = Object.values(fills).some(Boolean) || art.ops.some((o) => o.t === "s");
  const sheet = useMemo(() => sheetPlate(plate), [plate]);
  const toFridge = () => {
    const d = new Date();
    fridge.hang({ slug: plate.slug, version: plate.version, fills, name, ...(art.ops.length || art.sun || art.lines.kind !== "inkt" ? { art } : {}) },
      new Intl.DateTimeFormat(market, { day: "numeric", month: "short" }).format(d));
    flash(t.onFridge);
  };
  const undo = () => {
    if (shared) {
      // Samen: alleen je eigen laatste handeling, niet die van de ander.
      const own = [...art.ops].reverse().find((o) => together.mine(o.id));
      if (own?.id) together.emit({ t: "x", ref: own.id });
      return;
    }
    const u = undoLast(art, fills); if (u) { setArt(u.art); setFills(u.fills); }
  };
  const reset = () => {
    if (!sure) { setSure(true); setTimeout(() => setSure(false), 2500); return; }
    if (shared) together.emit({ t: "c" });
    else { setFills({}); setArt((a) => ({ ...a, ops: [] })); }
    setSure(false);
  };

  /* ---------- Inzoomen en schuiven ---------- */
  const clamp = useCallback((v: View): View => {
    const el = port.current; if (!el) return v;
    const s = Math.min(6, Math.max(1, v.s));
    const w = el.clientWidth, h = el.clientHeight;
    return { s, x: Math.min(0, Math.max(w - w * s, v.x)), y: Math.min(0, Math.max(h - h * s, v.y)) };
  }, []);
  const zoomAt = useCallback((factor: number, cx?: number, cy?: number) => setView((v) => {
    const el = port.current; if (!el) return v;
    const px = cx ?? el.clientWidth / 2, py = cy ?? el.clientHeight / 2;
    const s = Math.min(6, Math.max(1, v.s * factor));
    return clamp({ s, x: px - (px - v.x) * (s / v.s), y: py - (py - v.y) * (s / v.s) });
  }), [clamp]);
  // Knijpen op een trackpad of Ctrl + scrollwiel zoomt; scrollen schuift als er ingezoomd is.
  useEffect(() => {
    const el = port.current;
    if (!el || !atelier) return;
    const wheel = (e: WheelEvent) => {
      const r = el.getBoundingClientRect();
      if (e.ctrlKey || e.metaKey) { e.preventDefault(); zoomAt(Math.exp(-e.deltaY * 0.01), e.clientX - r.left, e.clientY - r.top); }
      else if (view.s > 1) { e.preventDefault(); setView((v) => clamp({ ...v, x: v.x - e.deltaX, y: v.y - e.deltaY })); }
    };
    el.addEventListener("wheel", wheel, { passive: false });
    return () => el.removeEventListener("wheel", wheel);
  }, [atelier, zoomAt, clamp, view.s]);

  /* ---------- Tekenen met penselen; twee vingers zoomen en schuiven ---------- */
  const pointers = useRef(new Map<number, Pt>());
  const gesture = useRef<{ dist: number; mid: Pt; view: View; pan?: boolean } | null>(null);
  const draw = useRef<Stroke | null>(null);
  const frame = useRef(0);

  const toSvg = (x: number, y: number): Pt | null => {
    const m = svg.current?.getScreenCTM();
    if (!m) return null;
    const p = new DOMPoint(x, y).matrixTransform(m.inverse());
    return { x: p.x, y: p.y };
  };
  const regionAt = (x: number, y: number): number | null => {
    for (const el of document.elementsFromPoint(x, y)) {
      if (!svg.current?.contains(el)) continue;
      const i = (el as SVGElement).dataset?.i;
      if (i !== undefined && Number(i) < plate.regionCount) return Number(i);
    }
    return null;
  };
  const addPoint = (e: PointerEvent) => {
    const s = draw.current; if (!s) return;
    const p = toSvg(e.clientX, e.clientY); if (!p) return;
    s.pts.push(...roundPoint(p.x, p.y, e.pointerType === "pen" ? e.pressure || 0.5 : 0.5));
  };
  const paintLive = () => {
    cancelAnimationFrame(frame.current);
    frame.current = requestAnimationFrame(() => {
      const s = draw.current; const el = svg.current?.querySelector("[data-live]");
      if (s && el) el.setAttribute("d", strokePath(s));
    });
  };
  const local = (e: ReactPointerEvent): Pt => { const r = port.current!.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; };
  const two = (): [Pt, Pt] => [...pointers.current.values()].slice(0, 2) as [Pt, Pt];

  const onDown = (e: ReactPointerEvent<HTMLDivElement>) => {
    if (!atelier) return;
    pointers.current.set(e.pointerId, local(e));
    if (pointers.current.size === 2) {
      // Tweede vinger: geen streek maar zoomen en schuiven.
      draw.current = null; setLive(null);
      const [a, b] = two();
      gesture.current = { dist: Math.hypot(a.x - b.x, a.y - b.y) || 1, mid: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }, view };
      return;
    }
    if (e.button === 1 || (e.pointerType === "mouse" && e.altKey)) {
      // Schuiven met de middelste muisknop of met Alt ingedrukt.
      e.preventDefault();
      gesture.current = { dist: 1, mid: local(e), view, pan: true };
      e.currentTarget.setPointerCapture(e.pointerId);
      return;
    }
    if (!isBrush(tool) || e.button !== 0) return;
    const region = regionAt(e.clientX, e.clientY);
    if (region === null) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    draw.current = { t: "s", r: region, b: tool, c: colorA, w: size, ...(e.pointerType === "pen" ? { pen: true } : {}), pts: [] };
    addPoint(e.nativeEvent);
    setLive({ region, brush: tool, color: colorA });
  };
  const onMove = (e: ReactPointerEvent<HTMLDivElement>) => {
    if (!atelier) return;
    if (pointers.current.has(e.pointerId)) pointers.current.set(e.pointerId, local(e));
    const g = gesture.current;
    if (g?.pan) { const p = local(e); setView(clamp({ ...g.view, x: g.view.x + p.x - g.mid.x, y: g.view.y + p.y - g.mid.y })); return; }
    if (g && pointers.current.size >= 2) {
      const [a, b] = two();
      const mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
      const s = Math.min(6, Math.max(1, g.view.s * (Math.hypot(a.x - b.x, a.y - b.y) / g.dist)));
      setView(clamp({ s, x: mid.x - (g.mid.x - g.view.x) * (s / g.view.s), y: mid.y - (g.mid.y - g.view.y) * (s / g.view.s) }));
      return;
    }
    if (!draw.current) return;
    const events = e.nativeEvent.getCoalescedEvents?.() ?? [];
    (events.length ? events : [e.nativeEvent]).forEach(addPoint);
    paintLive();
  };
  const onUp = (e: ReactPointerEvent<HTMLDivElement>) => {
    pointers.current.delete(e.pointerId);
    if (gesture.current && (gesture.current.pan || pointers.current.size === 0)) gesture.current = null;
    const s = draw.current;
    if (!s) return;
    draw.current = null;
    if (s.pts.length >= 3) {
      if (shared) together.emit(s);
      else setArt((a) => ({ ...a, ops: [...a.ops, s] }));
      if (s.b !== "gum") remember(s.c);
      markColored();
    }
    setLive(null);
  };

  /* ---------- Afbeelding en time-lapse ---------- */
  const paper = () => (svg.current ? getComputedStyle(svg.current).getPropertyValue("--color-paper").trim() || "white" : "white");
  const saveImage = async () => {
    const s = svg.current; if (!s) return;
    const canvas = document.createElement("canvas");
    Object.assign(canvas, canvasSize(s, 2400));
    await drawSvg(canvas, snapshotSvg(s), paper());
    canvas.toBlob((b) => b && download(b, `kleurhoek-${plate.slug}.png`), "image/png");
  };

  const brush = isBrush(tool);
  return (
    <div className="wrap" data-mode="kind">
      <div className="studio">
        <div className="studio-top">
          <Link href={href()} className="btn">{t.back}</Link>
          <h1>{plate.name}</h1>
          <FavoriteButton slug={plate.slug} market={market} language={language} accounts={accounts} />
        </div>
        <div className="canvas" data-print={hasColor ? printWhat : "kleur"} data-atelier={atelier ? (brush ? "penseel" : "vullen") : undefined}>
          <div ref={port} className="zoomport" onPointerDown={onDown} onPointerMove={onMove} onPointerUp={onUp} onPointerCancel={onUp}>
            <div className="zoomed" style={view.s !== 1 ? { transform: `translate(${view.x}px, ${view.y}px) scale(${view.s})` } : undefined}>
              <Sheet className="sheet sheet-live" plate={sheet} inner={inner} fills={fills} sw={sw} numbers={numbers} name={name} learn={learn}
                onPick={atelier && brush ? undefined : apply} art={art} live={live} svgRef={svg} />
            </div>
            {atelier && (
              <div className="ui-zoombar no-print">
                <button type="button" className="ui-btn ui-iconbtn" aria-label={t.atelier.zoomOut} onClick={() => zoomAt(1 / 1.5)}><Icon name="zoom-out" size={18} /></button>
                <output>{Math.round(view.s * 100)}%</output>
                <button type="button" className="ui-btn ui-iconbtn" aria-label={t.atelier.zoomIn} onClick={() => zoomAt(1.5)}><Icon name="zoom-in" size={18} /></button>
                <button type="button" className="ui-btn ui-iconbtn" aria-label={t.atelier.zoomFit} onClick={() => setView(NO_ZOOM)}><Icon name="fit" size={18} /></button>
              </div>
            )}
          </div>
          {/* Leeg printen: dezelfde plaat zonder kleuren; het werk op het scherm blijft staan. */}
          {hasColor && printWhat === "leeg" && (
            <div className="print-copy" aria-hidden="true">
              <Sheet plate={sheet} inner={inner} sw={sw} numbers={numbers} legend={numbers} name={name} learn={learn} art={{ ...art, ops: [], sun: null }} />
            </div>
          )}
        </div>
        <aside className="tools">
          <div className="tool">
            <button type="button" className="ui-switch" aria-pressed={atelier} onClick={toggleAtelier}>{atelier ? t.atelier.on : t.atelier.off}</button>
            <p className="hint">{t.atelier.hint}</p>
          </div>
          {atelier ? (
            <>
              <ToolPicker t={t} tool={tool} onTool={chooseTool} />
              {brush && (
                <div className="tool">
                  <Range label={t.atelier.size} value={size} min={0.5} max={3} step={0.25} shown={`×${size.toLocaleString(language)}`} onChange={setSize} />
                  {tool !== "gum" && <p className="hint">{t.atelier.pressureHint}</p>}
                </div>
              )}
              {tool === "patroon" && <div className="tool"><PatternPicker t={t} value={pattern} onChange={setPattern} /></div>}
              <div className="tool">
                <h2>{t.colors}</h2>
                <ColorMixer t={t} a={colorA} b={colorB} active={well} onActive={setWell} recent={recent}
                  onChange={(c) => (well === "a" ? setColorA : setColorB)(c)} />
              </div>
              <SunDial t={t} art={art} onArt={setArt} />
              <LinePicker t={t} art={art} onArt={setArt} color={colorA} />
            </>
          ) : (
            <>
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
            </>
          )}
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
            <button type="button" className="btn" onClick={undo} disabled={shared ? !art.ops.some((o) => together.mine(o.id)) : !art.ops.length}>{t.undo}</button>
            <button type="button" className="btn" onClick={reset}>{sure ? t.resetSure : t.reset}</button>
          </div>
          <TogetherPanel t={t} together={together} onStart={startTogether} joinHref={href("/samen")} />
          {atelier && hasColor && (
            <div className="row">
              <button type="button" className="btn" onClick={() => setReplayOpen(true)}><Icon name="play" size={16} /> {t.atelier.replay}</button>
              <button type="button" className="btn" onClick={() => void saveImage()}><Icon name="image" size={16} /> {t.atelier.saveImage}</button>
            </div>
          )}
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
      {replayOpen && svg.current && (
        <Replay t={t} slug={plate.slug} paper={paper()} onClose={() => setReplayOpen(false)}
          frames={() => replay(art, fills).map((st) => snapshotSvg(svg.current!, composeInner(inner, st.art, st.fills, svg.current!.dataset.id ?? "kh")))}
          size={canvasSize(svg.current, 800)} />
      )}
      {toast && <div className="toast" role="status">{toast}</div>}
    </div>
  );
}

/** Time-lapse: het werk speelt zich opnieuw af en wordt tegelijk opgenomen als filmpje (als het apparaat dat kan). */
function Replay({ t, slug, paper, frames, size, onClose }: {
  t: ReturnType<typeof messages>; slug: string; paper: string; frames: () => string[]; size: { width: number; height: number }; onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [video, setVideo] = useState<Blob | null>(null);
  const [busy, setBusy] = useState(true);
  const [run, setRun] = useState(0);
  const type = useMemo(() => videoType(), []);
  useEffect(() => { dialog.current?.showModal(); }, []);
  useEffect(() => {
    const abort = new AbortController();
    setBusy(true); setVideo(null);
    void playFrames(canvas.current!, frames(), paper, { record: type, signal: abort.signal }).then((b) => { if (!abort.signal.aborted) { setVideo(b); setBusy(false); } });
    return () => abort.abort();
  }, [run]); // eslint-disable-line react-hooks/exhaustive-deps
  const ext = type?.includes("mp4") ? "mp4" : "webm";
  return (
    <dialog ref={dialog} className="ui-dialog" aria-labelledby="replay-title" onClose={onClose}>
      <h2 id="replay-title">{t.atelier.replayTitle}</h2>
      <canvas ref={canvas} width={size.width} height={size.height} />
      {!type && <p className="hint">{t.atelier.noVideo}</p>}
      <div className="ui-dialog-actions">
        <button type="button" className="ui-btn" onClick={() => dialog.current?.close()}>{t.atelier.close}</button>
        {!busy && <button type="button" className="ui-btn" onClick={() => setRun((r) => r + 1)}><Icon name="play" size={16} /> {t.atelier.replay}</button>}
        {type && (
          <button type="button" className="ui-btn" data-variant="primary" disabled={!video} onClick={() => video && download(video, `kleurhoek-${slug}.${ext}`)}>
            {busy ? t.atelier.making : t.atelier.saveVideo}
          </button>
        )}
      </div>
    </dialog>
  );
}
