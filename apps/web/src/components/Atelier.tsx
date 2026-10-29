"use client";
import { Icon, type IconName } from "@kleurhoek/theme";
import { useEffect, useRef, useState, type CSSProperties, type KeyboardEvent, type PointerEvent } from "react";
import type { Messages } from "@/i18n/nl";
import { BRUSHES, DEFAULT_SUN, FILL_TOOLS, harmony, hexToHsl, hslToHex, MOODS, PATTERNS, shades, type Art, type LineKind, type Pattern, type Tool } from "@/lib/atelier";

/**
 * Het gereedschap van het Atelier (ADR 0056): penselen, vullen, kleuren mengen, de zon en de lijnen. Alleen de
 * bediening; de kleurstudio houdt het werk bij en tekent het.
 */

const ICON: Record<Tool, IconName> = {
  potlood: "pencil", stift: "marker", waterverf: "brush", airbrush: "spray", gum: "eraser",
  vullen: "bucket", verloop: "gradient", patroon: "pattern", pipet: "eyedropper",
};

export function ToolPicker({ t, tool, onTool }: { t: Messages; tool: Tool; onTool: (t: Tool) => void }) {
  const group = (label: string, tools: readonly Tool[]) => (
    <div className="tool">
      <h2>{label}</h2>
      <div className="ui-tools" role="group" aria-label={label}>
        {tools.map((x) => (
          <button key={x} type="button" className="ui-tool" aria-pressed={tool === x} onClick={() => onTool(x)}>
            <Icon name={ICON[x]} size={24} />{t.atelier.tools[x]}
          </button>
        ))}
      </div>
    </div>
  );
  return <>{group(t.atelier.brushes, BRUSHES)}{group(t.atelier.fill, FILL_TOOLS)}</>;
}

export function Range({ label, value, min, max, step, shown, onChange }: { label: string; value: number; min: number; max: number; step: number; shown: string; onChange: (v: number) => void }) {
  return (
    <label className="ui-range">{label} <output>{shown}</output>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} />
    </label>
  );
}

export function PatternPicker({ t, value, onChange }: { t: Messages; value: Pattern; onChange: (p: Pattern) => void }) {
  return (
    <div className="seg" role="group" aria-label={t.atelier.tools.patroon}>
      {PATTERNS.map((p) => <button key={p} type="button" aria-pressed={value === p} onClick={() => onChange(p)}>{t.atelier.patterns[p]}</button>)}
    </div>
  );
}

const HEX = /^#[0-9a-f]{6}$/i;

/** Elke kleur kiezen: twee vakjes, schuifjes, hexcode en rijen met kleuren die passen. */
export function ColorMixer({ t, a, b, active, onActive, onChange, recent }: {
  t: Messages; a: string; b: string; active: "a" | "b"; onActive: (w: "a" | "b") => void; onChange: (hex: string) => void; recent: string[];
}) {
  const value = active === "a" ? a : b;
  const [hsl, setHsl] = useState(() => hexToHsl(value));
  const [text, setText] = useState(value);
  const [mood, setMood] = useState<keyof typeof MOODS>("zonsondergang");
  // Komt de kleur van buiten (pipet, vakje), dan volgen de schuifjes; zelf schuiven houdt de tint vast bij grijs.
  useEffect(() => {
    setText(value);
    setHsl((cur) => (hslToHex(...cur) === value.toLowerCase() ? cur : hexToHsl(value)));
  }, [value]);
  const [h, s, l] = hsl;
  const set = (next: [number, number, number]) => { setHsl(next); onChange(hslToHex(...next)); };
  const row = (label: string, colors: string[]) => (
    <div>
      <div className="ui-mixer-label">{label}</div>
      <div className="ui-minis">
        {colors.map((c, i) => <button key={`${c}${i}`} type="button" className="ui-mini" style={{ "--c": c } as CSSProperties} aria-label={c} onClick={() => onChange(c)} />)}
      </div>
    </div>
  );
  return (
    <div className="ui-mixer">
      <div className="ui-mixer-wells">
        <button type="button" className="ui-mixer-well" style={{ "--c": a } as CSSProperties} aria-pressed={active === "a"} aria-label={`${t.atelier.colorA} ${a}`} onClick={() => onActive("a")} />
        <button type="button" className="ui-mixer-well" style={{ "--c": b } as CSSProperties} aria-pressed={active === "b"} aria-label={`${t.atelier.colorB} ${b}`} onClick={() => onActive("b")} />
        <input className="ui-input" value={text} maxLength={7} spellCheck={false} aria-label={t.atelier.hex}
          onChange={(e) => { const v = e.target.value.trim(); setText(v); if (HEX.test(v)) onChange(v.toLowerCase()); }} />
      </div>
      <label className="ui-mixer-label">{t.atelier.hue}
        <input type="range" min={0} max={359} value={h} onChange={(e) => set([Number(e.target.value), s, l])}
          style={{ "--track": `linear-gradient(90deg, ${[0, 60, 120, 180, 240, 300, 360].map((x) => `hsl(${x} ${Math.max(s, 40)}% ${Math.min(Math.max(l, 35), 65)}%)`).join(",")})` } as CSSProperties} />
      </label>
      <label className="ui-mixer-label">{t.atelier.saturation}
        <input type="range" min={0} max={100} value={s} onChange={(e) => set([h, Number(e.target.value), l])}
          style={{ "--track": `linear-gradient(90deg, hsl(${h} 0% ${l}%), hsl(${h} 100% ${l}%))` } as CSSProperties} />
      </label>
      <label className="ui-mixer-label">{t.atelier.lightness}
        <input type="range" min={0} max={100} value={l} onChange={(e) => set([h, s, Number(e.target.value)])}
          style={{ "--track": `linear-gradient(90deg, hsl(${h} ${s}% 0%), hsl(${h} ${s}% 50%), hsl(${h} ${s}% 100%))` } as CSSProperties} />
      </label>
      {row(t.atelier.matching, harmony(value))}
      {row(t.atelier.shades, shades(value))}
      {recent.length > 0 && row(t.atelier.recent, recent)}
      <div>
        <div className="ui-mixer-label">{t.atelier.mood}</div>
        <div className="seg" role="group" aria-label={t.atelier.mood}>
          {(Object.keys(MOODS) as (keyof typeof MOODS)[]).map((m) => (
            <button key={m} type="button" aria-pressed={mood === m} onClick={() => setMood(m)}>{t.atelier.moods[m as keyof Messages["atelier"]["moods"]]}</button>
          ))}
        </div>
      </div>
      {row(t.atelier.moods[mood as keyof Messages["atelier"]["moods"]], MOODS[mood]!)}
    </div>
  );
}

/** De zon: sleep het zonnetje rond; pijltjestoetsen draaien hem per 15 graden. */
export function SunDial({ t, art, onArt }: { t: Messages; art: Art; onArt: (a: Art) => void }) {
  const dial = useRef<HTMLDivElement>(null);
  const sun = art.sun ?? DEFAULT_SUN;
  const on = !!art.sun;
  const set = (a: number, s = sun.s) => onArt({ ...art, sun: { a: ((Math.round(a) % 360) + 360) % 360, s } });
  const fromPointer = (e: PointerEvent<HTMLDivElement>) => {
    const r = dial.current!.getBoundingClientRect();
    set((Math.atan2(e.clientY - (r.top + r.height / 2), e.clientX - (r.left + r.width / 2)) * 180) / Math.PI);
  };
  const key = (e: KeyboardEvent<HTMLDivElement>) => {
    const step = { ArrowRight: 15, ArrowDown: 15, ArrowLeft: -15, ArrowUp: -15 }[e.key];
    if (step) { e.preventDefault(); set(sun.a + step); } else if (e.key === "Home") { e.preventDefault(); set(225); }
  };
  const rad = (sun.a * Math.PI) / 180;
  const words = t.atelier.directions[Math.round(sun.a / 45) % 8]!;
  return (
    <div className="tool">
      <h2>{t.atelier.sun}</h2>
      <button type="button" className="ui-switch" aria-pressed={on} onClick={() => onArt({ ...art, sun: on ? null : sun })}>{t.atelier.sun}</button>
      <p className="hint">{t.atelier.sunHint}</p>
      {on && (
        <div className="ui-sundial-row">
          <div ref={dial} className="ui-sundial" role="slider" tabIndex={0} aria-label={t.atelier.sunDirection} aria-valuemin={0} aria-valuemax={359}
            aria-valuenow={sun.a} aria-valuetext={words} onKeyDown={key}
            onPointerDown={(e) => { e.currentTarget.setPointerCapture(e.pointerId); fromPointer(e); }}
            onPointerMove={(e) => { if (e.currentTarget.hasPointerCapture(e.pointerId)) fromPointer(e); }}>
            <span className="ui-sundial-sun" style={{ left: `${50 + 40 * Math.cos(rad)}%`, top: `${50 + 40 * Math.sin(rad)}%` }}><Icon name="sun" size={20} /></span>
          </div>
          <Range label={t.atelier.sunStrength} value={sun.s} min={0.1} max={1} step={0.05} shown={`${Math.round(sun.s * 100)}%`} onChange={(v) => set(sun.a, v)} />
        </div>
      )}
    </div>
  );
}

/** Lijnkleur: zwart, sepia, een eigen kleur (de kleur die nu gekozen is) of helemaal geen lijnen. */
export function LinePicker({ t, art, onArt, color }: { t: Messages; art: Art; onArt: (a: Art) => void; color: string }) {
  const kinds: LineKind[] = ["inkt", "sepia", "kleur", "geen"];
  return (
    <div className="tool">
      <h2>{t.atelier.lineColor}</h2>
      <div className="seg" role="group" aria-label={t.atelier.lineColor}>
        {kinds.map((k) => (
          <button key={k} type="button" aria-pressed={art.lines.kind === k}
            onClick={() => onArt({ ...art, lines: k === "kleur" ? { kind: k, c: color } : { kind: k } })}>{t.atelier.lineKinds[k]}</button>
        ))}
      </div>
    </div>
  );
}
