"use client";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { longDate, niceScale, num, shortDate, tick } from "./format";

export interface Series { key: string; label: string; color: string; values: number[] }

const H = 240, L = 44, R = 12, T = 12, B = 28;

/**
 * Chart uit het design system (ADR 0020): lijnen (verloop) of staven (aantallen) over de tijd, één
 * y-as, legenda bij twee of meer reeksen, aanwijzen met muis, vinger of pijltjestoetsen, en dezelfde
 * cijfers als tabel. Kleuren komen als CSS-variabelen (var(--chart-1) …), nooit als hex.
 */
export function TimeChart({ title, dates, series, bucket, kind = "line" }: {
  title: string; dates: string[]; series: Series[]; bucket: "day" | "week"; kind?: "line" | "bar";
}) {
  const id = useId();
  const [active, setActive] = useState<number | null>(null);
  // De grafiek tekent op zijn echte breedte, zodat labels altijd even groot zijn (niet meeschalen).
  const box = useRef<HTMLDivElement>(null);
  const [W, setW] = useState(720);
  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => { if (e) setW(Math.max(280, Math.round(e.contentRect.width))); });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const max = Math.max(0, ...series.flatMap((s) => s.values));
  const ticks = niceScale(max);
  const top = ticks.at(-1) || 1;
  const n = dates.length;
  const slot = (W - L - R) / Math.max(n, 1);
  const x = (i: number) => (kind === "bar" ? L + slot * i + slot / 2 : L + (n <= 1 ? (W - L - R) / 2 : ((W - L - R) * i) / (n - 1)));
  const y = (v: number) => T + (H - T - B) * (1 - v / top);
  const labelEvery = Math.max(1, Math.ceil(n / Math.max(2, Math.floor((W - L - R) / 72))));
  const paths = useMemo(() => series.map((s) => s.values.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join(" ")), [series, n, top, W]); // eslint-disable-line react-hooks/exhaustive-deps
  const barW = Math.min(24, Math.max(2, slot / series.length - 2));

  function pick(clientX: number, rect: DOMRect) {
    const px = ((clientX - rect.left) / rect.width) * W;
    const i = kind === "bar" ? Math.floor((px - L) / slot) : Math.round(((px - L) / (W - L - R)) * (n - 1));
    setActive(Math.min(n - 1, Math.max(0, i)));
  }
  const a = active;
  const tipLeft = a === null ? 0 : (x(a) / W) * 100;

  return (
    <figure className="ui-chart">
      <div className="ui-chart-head">
        <h3 id={`${id}-t`}>{title}</h3>
        {series.length > 1 && (
          <ul className="ui-legend">{series.map((s) => <li key={s.key}><i style={{ ["--sw" as string]: s.color }} data-shape={kind === "bar" ? "bar" : undefined} />{s.label}</li>)}</ul>
        )}
      </div>
      <div ref={box} style={{ position: "relative" }}>
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-labelledby={`${id}-t`} tabIndex={0}
          onPointerMove={(e) => pick(e.clientX, e.currentTarget.getBoundingClientRect())} onPointerLeave={() => setActive(null)}
          onKeyDown={(e) => {
            if (e.key === "ArrowRight") setActive((v) => Math.min(n - 1, (v ?? -1) + 1));
            else if (e.key === "ArrowLeft") setActive((v) => Math.max(0, (v ?? n) - 1));
            else if (e.key === "Escape") setActive(null);
          }} onBlur={() => setActive(null)}>
          {ticks.map((t) => <line key={t} className={t === 0 ? "ui-chart-axis" : "ui-chart-grid"} x1={L} x2={W - R} y1={y(t)} y2={y(t)} />)}
          {ticks.map((t) => <text key={`l${t}`} x={L - 8} y={y(t) + 4} textAnchor="end">{tick(t)}</text>)}
          {dates.map((d, i) => (i % labelEvery === 0 || i === n - 1) && (i === n - 1 || n - 1 - i >= labelEvery / 2) ? <text key={d} x={x(i)} y={H - 8} textAnchor="middle">{shortDate(d)}</text> : null)}
          {kind === "line" ? series.map((s, k) => (
            <g key={s.key}>
              {/* Vlak alleen bij één reeks: twee vlakken over elkaar worden modderig. */}
              {series.length === 1 && <path className="ui-chart-area" fill={s.color} d={`${paths[k]} L${x(n - 1)} ${y(0)} L${x(0)} ${y(0)} Z`} />}
              <path className="ui-chart-line" stroke={s.color} d={paths[k]} />
            </g>
          )) : series.map((s, k) => s.values.map((v, i) => {
            const bx = x(i) - (series.length * (barW + 2) - 2) / 2 + k * (barW + 2), by = y(v), h = y(0) - by;
            const r = Math.min(4, h, barW / 2);
            return v > 0 ? <path key={`${s.key}${i}`} fill={s.color} opacity={a === null || a === i ? 1 : 0.55}
              d={`M${bx} ${y(0)} V${by + r} Q${bx} ${by} ${bx + r} ${by} H${bx + barW - r} Q${bx + barW} ${by} ${bx + barW} ${by + r} V${y(0)} Z`} /> : null;
          }))}
          {a !== null && kind === "line" && (
            <g>
              <line className="ui-chart-cross" x1={x(a)} x2={x(a)} y1={T} y2={y(0)} />
              {series.map((s) => <circle key={s.key} className="ui-chart-dot" cx={x(a)} cy={y(s.values[a] ?? 0)} r={5} fill={s.color} />)}
            </g>
          )}
        </svg>
        {a !== null && (
          <div className="ui-chart-tip" role="status" style={{ left: `clamp(0px, calc(${tipLeft}% + 12px), calc(100% - 180px))`, top: 8 }}>
            <b>{longDate(dates[a]!, bucket)}</b>
            {series.map((s) => <span key={s.key}>{s.label} <b>{num(s.values[a] ?? 0)}</b></span>)}
          </div>
        )}
      </div>
      <details>
        <summary className="lead">Toon als tabel</summary>
        <table>
          <thead><tr><th>{bucket === "week" ? "Week" : "Dag"}</th>{series.map((s) => <th key={s.key} className="num">{s.label}</th>)}</tr></thead>
          <tbody>{dates.map((d, i) => <tr key={d}><td>{longDate(d, bucket)}</td>{series.map((s) => <td key={s.key} className="num">{num(s.values[i] ?? 0)}</td>)}</tr>)}</tbody>
        </table>
      </details>
    </figure>
  );
}
