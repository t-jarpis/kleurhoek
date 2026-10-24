import { num } from "./format";

/** GoalCard uit het design system (ADR 0022): stand deze maand t.o.v. het doel, met balk en status in tekst. */
export function GoalCard({ label, actual, target, stretch, expected, onTrack, cumulative = false }: {
  label: string; actual: number; target: number; stretch: number; expected: number; onTrack: boolean; cumulative?: boolean;
}) {
  const pct = (v: number) => `${target > 0 ? Math.min(100, (v / target) * 100) : 100}%`;
  return (
    <div className="ui-stat ui-goal">
      <span>{label}</span>
      <strong>{num(actual)}</strong>
      <p className="ui-goal-of">van {num(target)} doel{cumulative ? "" : " deze maand"} (ambitie {num(stretch)})</p>
      <div className="ui-goal-bar" aria-hidden="true"><i style={{ width: pct(actual) }} /><b style={{ left: pct(expected) }} /></div>
      {onTrack
        ? <p className="ui-stat-delta" data-dir="good"><b>▲ Op koers</b> <span>{cumulative ? (actual >= target ? "doel gehaald" : `nog ${num(target - actual)} te gaan`) : `verwacht ${num(expected)} op deze dag`}</span></p>
        : <p className="ui-stat-delta" data-dir="bad"><b>▼ Achter</b> <span>{cumulative ? `nog ${num(target - actual)} te gaan` : `verwacht ${num(expected)} op deze dag`}</span></p>}
    </div>
  );
}
