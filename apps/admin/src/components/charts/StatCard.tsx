import { delta, num } from "./format";

/** StatCard met trend t.o.v. de vorige periode. `upIsGood` bepaalt de kleur, niet de richting zelf. */
export function StatCard({ label, value, before, period, upIsGood = true, note }: {
  label: string; value: number; before?: number; period: string; upIsGood?: boolean; note?: string;
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
      {note && <p className="ui-stat-note">{note}</p>}
    </div>
  );
}
