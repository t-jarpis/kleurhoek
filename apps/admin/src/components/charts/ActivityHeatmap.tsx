import { num } from "./format";

/** Uit de API (ADR 0073): aantallen per weekdag (1 = maandag) en uur, Nederlandse tijd. */
export interface Activity {
  from: string; to: string; limited: boolean; timeZone: string;
  grid: { weekday: number; hour: number; count: number }[];
  /** `via`: binnenkomst van hetzelfde bezoek op dezelfde dag (ADR 0083); null als die er niet is. */
  latest: { at: string; type: "pdf_download" | "print"; plate: string; market: string; device: string; via?: { referrer: string; page: string; entry: string } | null }[];
}

const DAYS = ["ma", "di", "wo", "do", "vr", "za", "zo"];
const DAY_NAMES = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"];
const HOURS = Array.from({ length: 24 }, (_, h) => h);

/** ActivityHeatmap uit het design system: een tabel met per weekdag en uur hoe vaak er gedownload of geprint is. */
export function ActivityHeatmap({ grid, caption }: { grid: Activity["grid"]; caption: string }) {
  const at = new Map(grid.map((c) => [`${c.weekday}-${c.hour}`, c.count]));
  const max = Math.max(1, ...grid.map((c) => c.count));
  const total = grid.reduce((s, c) => s + c.count, 0);
  if (!total) return <p className="lead">Nog geen downloads of prints in deze periode.</p>;
  return (
    <>
      <table className="ui-heatmap">
        <caption className="visually-hidden">{caption}</caption>
        <thead><tr><th scope="col"><span className="visually-hidden">Dag</span></th>{HOURS.map((h) => <th key={h} scope="col">{h}</th>)}</tr></thead>
        <tbody>{DAYS.map((d, i) => (
          <tr key={d}><th scope="row" title={DAY_NAMES[i]}>{d}</th>{HOURS.map((h) => {
            const n = at.get(`${i + 1}-${h}`) ?? 0;
            const label = `${DAY_NAMES[i]} ${h}:00–${h + 1}:00: ${num(n)}`;
            return <td key={h} title={label} {...(n ? { style: { "--heat": (n / max).toFixed(2) } as React.CSSProperties } : { "data-zero": "" })}><span className="visually-hidden">{label}</span></td>;
          })}</tr>
        ))}</tbody>
      </table>
      <div className="ui-heatmap-legend" aria-hidden="true">Minder {[0, 0.25, 0.5, 0.75, 1].map((v) => <i key={v} style={{ "--heat": v } as React.CSSProperties} />)} Meer</div>
    </>
  );
}
