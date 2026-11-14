"use client";
import { usePrint } from "@/lib/print";
import { useState } from "react";
import { GIFT_TEXT as T } from "@/lib/sint";

/**
 * Cadeaulabels en naamkaartjes met eigen naam (ADR 0067, design system: GiftLabels). Alles gebeurt in de browser:
 * de naam gaat nergens heen en wordt niet bewaard. Printen op A4; de tekeningetjes zijn om zelf in te kleuren.
 */
type Kind = "labels" | "kaartjes";
type Motif = "mijter" | "pakje" | "schoen" | "boot" | "baret" | "pepernoten";
const MOTIFS: Motif[] = ["mijter", "pakje", "schoen", "boot", "baret", "pepernoten"];
const MAX = 24;

/** Een tekeningetje in een vak van 40 × 40, alleen lijnen en vlakken (class r) om in te kleuren. */
function Art({ motif }: { motif: Motif }) {
  switch (motif) {
    case "mijter":
      return <g><path className="r" d="M8 38C6 26 12 12 20 4C28 12 34 26 32 38Z" /><rect className="r" x="7" y="33" width="26" height="6" rx="1.5" /><path className="r" d="M18.5 12h3v6h5v3h-5v10h-3V21h-5v-3h5Z" /></g>;
    case "pakje":
      return <g><rect className="r" x="6" y="16" width="28" height="22" rx="1" /><rect className="r" x="4" y="11" width="32" height="7" rx="1" /><rect className="r" x="17.5" y="11" width="5" height="27" /><path className="r" d="M20 11C12 3 7 8 12 11ZM20 11C28 3 33 8 28 11Z" /></g>;
    case "schoen":
      return <g><path className="r" d="M24 30L30 6L34 8L28 31Z" /><path className="r" d="M31 6Q28 0 31 -2Q33 3 32 6Q35 1 39 1Q37 6 32 8Z" /><path className="r" d="M3 38V28Q3 22 9 22H20Q24 22 27 26L35 28Q39 30 38 38Z" /><rect className="r" x="2" y="36" width="37" height="3" rx="1.5" /></g>;
    case "boot":
      return <g><path className="r" d="M2 26H38L34 36H6Z" /><rect className="r" x="8" y="17" width="22" height="9" rx="1" /><rect className="r" x="22" y="6" width="5" height="11" /><circle className="r" cx="13" cy="21.5" r="2" /><circle className="r" cx="19" cy="21.5" r="2" /></g>;
    case "baret":
      return <g><path className="r" d="M22 12C26 4 34 2 37 5C32 6 28 9 25 14Z" /><path className="r" d="M4 22C2 12 30 8 34 18Q20 18 4 22Z" /><circle className="r" cx="26" cy="15" r="2.4" /><path className="r" d="M8 22Q20 19 31 21L30 26Q20 24 9 27Z" /></g>;
    default:
      return <g>{[[10, 28], [20, 30], [30, 27], [15, 19], [25, 20], [20, 10]].map(([x, y]) => <circle key={`${x}-${y}`} className="r" cx={x} cy={y} r="5" />)}</g>;
  }
}

/** Naam in het vak laten passen: een letter is ongeveer 0,6 keer zo breed als hoog, dus kleiner bij lange namen. */
const fit = (name: string, width: number, max: number) => Math.min(max, width / (Math.max(3, name.length) * 0.6));

function Label({ x, y, name, from, motif }: { x: number; y: number; name: string; from: string; motif: Motif }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <rect className="cut" x="0" y="0" width="90" height="56" rx="6" />
      <circle className="cut" cx="82" cy="8" r="2.2" />
      <g transform="translate(6 9) scale(0.95)"><Art motif={motif} /></g>
      <text className="kh-label-small" x="48" y="17">{T.for}</text>
      <text className="kh-label-name" x="48" y="33" fontSize={fit(name, 40, 11)}>{name}</text>
      {from && <text className="kh-label-small" x="48" y="46">{T.from} {from}</text>}
    </g>
  );
}

function Card({ x, y, name, motif }: { x: number; y: number; name: string; motif: Motif }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <rect className="cut" x="0" y="0" width="90" height="80" rx="3" />
      <line className="fold" x1="0" y1="40" x2="90" y2="40" />
      {/* Twee keer hetzelfde: de bovenste helft staat op zijn kop, zodat de naam na het vouwen aan beide kanten rechtop staat. */}
      {[0, 180].map((turn) => (
        <g key={turn} transform={turn ? "rotate(180 45 20)" : "translate(0 40)"}>
          <g transform="translate(5 5) scale(0.75)"><Art motif={motif} /></g>
          <text className="kh-label-name" x="63" y="24" textAnchor="middle" fontSize={fit(name, 46, 12)}>{name}</text>
        </g>
      ))}
    </g>
  );
}

export function GiftLabels() {
  const [kind, setKind] = useState<Kind>("labels");
  const printer = usePrint();
  const [names, setNames] = useState("");
  const [from, setFrom] = useState(T.defaultFrom);
  const list = names.split(/[\n,]/).map((n) => n.trim().slice(0, MAX)).filter(Boolean);
  const shown = list.length ? list : [""];
  const per = kind === "labels" ? 8 : 6;
  const cells = Array.from({ length: per }, (_, i) => ({ name: shown[i % shown.length]!, motif: MOTIFS[i % MOTIFS.length]! }));
  return (
    <div className="kh-labels">
      <form className="kh-labels-form no-print" onSubmit={(e) => { e.preventDefault(); printer.print(); }}>
        <fieldset className="ui-seg" aria-label={T.kind}>
          {(["labels", "kaartjes"] as const).map((k) => (
            <label key={k}><input type="radio" name="kind" value={k} checked={kind === k} onChange={() => setKind(k)} /> {k === "labels" ? T.labels : T.cards}</label>
          ))}
        </fieldset>
        <div className="ui-field">
          <label htmlFor="kh-names">{T.names}</label>
          <textarea id="kh-names" className="ui-input" rows={3} value={names} onChange={(e) => setNames(e.target.value)} placeholder={T.namesPlaceholder} maxLength={400} autoComplete="off" />
          <span className="ui-hint">{T.namesHint}</span>
        </div>
        {kind === "labels" && (
          <div className="ui-field">
            <label htmlFor="kh-from">{T.fromLabel}</label>
            <input id="kh-from" className="ui-input" value={from} onChange={(e) => setFrom(e.target.value.slice(0, MAX))} maxLength={MAX} autoComplete="off" />
          </div>
        )}
        <p className="ui-hint">{T.privacy}</p>
        <div className="row"><button type="submit" className="ui-btn" data-variant="primary" aria-busy={printer.busy} aria-disabled={printer.busy}>{printer.busy ? `${T.print}…` : T.print}</button></div>
      </form>
      <div className="kh-labels-sheet">
        <svg viewBox="0 0 210 297" role="img" aria-label={kind === "labels" ? T.labels : T.cards}>
          {kind === "labels"
            ? cells.map((c, i) => <Label key={i} x={12 + (i % 2) * 96} y={14 + Math.floor(i / 2) * 68} name={c.name} from={from} motif={c.motif} />)
            : cells.map((c, i) => <Card key={i} x={12 + (i % 2) * 96} y={12 + Math.floor(i / 2) * 92} name={c.name} motif={c.motif} />)}
        </svg>
      </div>
    </div>
  );
}
