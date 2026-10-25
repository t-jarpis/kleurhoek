"use client";
import { useMemo, useRef, useState, type KeyboardEvent, type PointerEvent } from "react";
import { num } from "./format";
import world from "./world-110m.json";

/**
 * WorldMap uit het design system: bezoek per land op een wereldkaart. Natural Earth 1:110m (publiek domein, via
 * world-atlas) in de projectie Equal Earth, vooraf omgezet naar SVG-paden per ISO-landcode (world-110m.json).
 * Vijf stappen dekking (kwantielen); aanwijzen of focussen toont een tip, klikken of Enter zet een land vast.
 */
const MAP = world as { viewBox: string; europe: string; countries: Record<string, string> };
const VIEWS = { wereld: MAP.viewBox, europa: MAP.europe } as const;
type View = keyof typeof VIEWS;

export function WorldMap({ items, label = "Weergaven" }: { items: { country: string; value: number }[]; label?: string }) {
  const [view, setView] = useState<View>("wereld");
  const [hover, setHover] = useState<{ code: string; x: number; y: number } | null>(null);
  const [pinned, setPinned] = useState<{ code: string; x: number; y: number } | null>(null);
  const box = useRef<HTMLDivElement>(null);
  const name = useMemo(() => { try { return new Intl.DisplayNames(["nl"], { type: "region" }); } catch { return null; } }, []);
  const countryName = (c: string) => { try { return name?.of(c) ?? c; } catch { return c; } };

  const { values, total, level, bounds } = useMemo(() => {
    const values = new Map(items.filter((i) => i.country && i.value > 0).map((i) => [i.country.toUpperCase(), i.value]));
    const sorted = [...values.values()].sort((a, b) => a - b);
    const total = sorted.reduce((s, v) => s + v, 0);
    // Kwantielen: elke stap ongeveer evenveel landen, zodat ook kleine verschillen zichtbaar zijn.
    const level = (v: number) => Math.min(5, Math.max(1, Math.ceil((sorted.filter((x) => x <= v).length / sorted.length) * 5)));
    return { values, total, level, bounds: sorted.length ? [sorted.at(0)!, sorted.at(-1)!] as const : null };
  }, [items]);

  const at = (e: { clientX: number; clientY: number }) => {
    const r = box.current?.getBoundingClientRect();
    return r ? { x: e.clientX - r.left, y: e.clientY - r.top } : { x: 0, y: 0 };
  };
  const centre = (el: SVGPathElement) => {
    const b = el.getBoundingClientRect();
    return at({ clientX: b.left + b.width / 2, clientY: b.top + b.height / 2 });
  };
  const toggle = (code: string, pos: { x: number; y: number }) => setPinned((p) => (p?.code === code ? null : { code, ...pos }));
  const shown = pinned ?? hover;
  const tipValue = shown ? values.get(shown.code) ?? 0 : 0;

  return (
    <div className="ui-worldmap" ref={box} onKeyDown={(e) => { if (e.key === "Escape") setPinned(null); }}>
      <div className="ui-worldmap-head">
        <p className="lead" style={{ margin: 0 }}>{values.size === 1 ? "1 land" : `${values.size} landen`} met bezoek</p>
        <div className="ui-seg" role="group" aria-label="Uitsnede">
          {(["wereld", "europa"] as const).map((v) => (
            <button key={v} type="button" aria-pressed={view === v} onClick={() => { setView(v); setPinned(null); setHover(null); }}>{v === "wereld" ? "Wereld" : "Europa"}</button>
          ))}
        </div>
      </div>
      <svg viewBox={VIEWS[view]} role="group" aria-label="Wereldkaart met bezoek per land" onPointerLeave={() => setHover(null)}>
        {Object.entries(MAP.countries).map(([code, d]) => {
          const v = values.get(code);
          if (!v) return <path key={code} d={d} aria-hidden="true" />;
          const share = total ? Math.round((v / total) * 100) : 0;
          return (
            <path key={code} d={d} data-level={level(v)} data-active={pinned?.code === code ? "true" : undefined} tabIndex={0} role="button"
              aria-pressed={pinned?.code === code} aria-label={`${countryName(code)}: ${num(v)} ${label.toLowerCase()} (${share}%)`}
              onPointerMove={(e: PointerEvent<SVGPathElement>) => setHover({ code, ...at(e) })}
              onClick={(e) => toggle(code, at(e))}
              onFocus={(e) => setHover({ code, ...centre(e.currentTarget) })}
              onBlur={() => setHover(null)}
              onKeyDown={(e: KeyboardEvent<SVGPathElement>) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(code, centre(e.currentTarget)); } }} />
          );
        })}
      </svg>
      {shown && (
        <div className="ui-chart-tip" role="status" style={{ left: `clamp(0px, ${shown.x + 12}px, calc(100% - 180px))`, top: Math.max(shown.y - 72, 0) }}>
          <b>{countryName(shown.code)}</b>
          <span>{label} <b>{num(tipValue)}</b></span>
          <span>Aandeel <b>{total ? `${Math.round((tipValue / total) * 100)}%` : "—"}</b></span>
        </div>
      )}
      {bounds && (
        <div className="ui-worldmap-scale" aria-hidden="true">
          <ol><li className="none" /></ol><span>geen bezoek</span><span className="from">{num(bounds[0])}</span><ol><li /><li /><li /><li /><li /></ol><span>{num(bounds[1])}</span>
        </div>
      )}
    </div>
  );
}
