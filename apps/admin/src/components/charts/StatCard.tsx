import { delta, num } from "./format";

/**
 * StatCard met trend t.o.v. de vorige periode. `upIsGood` bepaalt de kleur, niet de richting zelf.
 * `trend`: de reeks per dag (of week) over de periode; vanaf twee punten een sparkline onder de trend (ADR 0096).
 */
export function StatCard({ label, value, before, period, upIsGood = true, note, trend }: {
  label: string; value: number; before?: number; period: string; upIsGood?: boolean; note?: string; trend?: number[];
}) {
  const d = before === undefined ? null : delta(value, before);
  const dir = d?.pct === null || d?.pct === undefined || d.pct === 0 ? undefined : (d.pct > 0) === upIsGood ? "good" : "bad";
  return (
    <div className="ui-stat">
      <span>{label}</span>
      <strong>{num(value)}</strong>
      {d && (d.pct !== null
        ? <p className="ui-stat-delta" data-dir={dir}><b>{d.pct > 0 ? "▲" : d.pct < 0 ? "▼" : "="} {d.pct > 0 ? "+" : ""}{d.pct}%</b> <span>t.o.v. {period}</span></p>
        : <p className="ui-stat-delta"><b>{d.isNew ? "nieuw" : "geen vergelijking"}</b> <span>t.o.v. {period}</span></p>)}
      {trend && trend.length > 1 && <Sparkline values={trend} />}
      {note && <p className="ui-stat-note">{note}</p>}
    </div>
  );
}

const SW = 100, SH = 36, PAD = 2;

/** Alleen de vorm van het verloop: y van 0 tot het hoogste punt, geen assen (design system: StatCard › Sparkline). */
export function Sparkline({ values }: { values: number[] }) {
  const max = Math.max(...values, 0);
  const x = (i: number) => (SW * i) / (values.length - 1);
  const y = (v: number) => (max ? PAD + (SH - PAD) * (1 - v / max) : SH);
  const line = values.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join(" ");
  const label = `Per periode: van ${num(values[0]!)} naar ${num(values.at(-1)!)}, hoogste ${num(max)}`;
  return (
    <svg className="ui-stat-spark" viewBox={`0 0 ${SW} ${SH}`} preserveAspectRatio="none" role="img" aria-label={label}>
      <path className="ui-stat-spark-area" d={`M0 ${SH} ${line.replace(/^M/, "L")} L${SW} ${SH} Z`} />
      <path className="ui-stat-spark-line" d={line} />
    </svg>
  );
}
