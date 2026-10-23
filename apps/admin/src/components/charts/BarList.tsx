import { num } from "./format";

/** BarList uit het design system: ranglijst met balken, hooguit 10 regels, de rest als "Overig". */
export function BarList({ items, total, empty = "Nog geen gegevens in deze periode." }: { items: { label: string; value: number }[]; total?: number; empty?: string }) {
  if (!items.length) return <p className="lead">{empty}</p>;
  const sorted = [...items].sort((a, b) => b.value - a.value);
  const shown = sorted.length > 10 ? [...sorted.slice(0, 9), { label: "Overig", value: sorted.slice(9).reduce((s, i) => s + i.value, 0) }] : sorted;
  const max = Math.max(...shown.map((i) => i.value), 1);
  const sum = total ?? sorted.reduce((s, i) => s + i.value, 0);
  return (
    <ul className="ui-barlist">
      {shown.map((i) => (
        <li key={i.label}>
          <span>{i.label}</span>
          <span className="ui-barlist-track" aria-hidden="true"><span className="ui-barlist-bar" style={{ display: "block", width: `${(i.value / max) * 100}%` }} /></span>
          <span className="ui-barlist-value">{num(i.value)}{sum > 0 && <small>{Math.round((i.value / sum) * 100)}%</small>}</span>
        </li>
      ))}
    </ul>
  );
}
