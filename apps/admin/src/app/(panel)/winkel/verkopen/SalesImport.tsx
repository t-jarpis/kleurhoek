"use client";
import { useActionState } from "react";
import { salesStep, type SalesState } from "../actions";

const FIELDS = [
  ["date", "Datum", true], ["subId", "Sub-ID of tracking-ID", false], ["product", "Product (ASIN of EAN)", false],
  ["items", "Aantal", false], ["revenue", "Omzet", false], ["commission", "Commissie", true], ["currency", "Valuta", false],
] as const;
const money = (cents: number, currency: string) => new Intl.NumberFormat("nl-NL", { style: "currency", currency }).format(cents / 100);

/** SalesImport (DS, ADR 0033): bestand kiezen, kolommen controleren, voorbeeld, importeren. */
export function SalesImport({ partners }: { partners: { slug: string; name: string }[] }) {
  const [state, action, pending] = useActionState<SalesState, FormData>(salesStep, null);
  const p = state?.preview;
  return (
    <form action={action} className="stack" key={state?.done ? "klaar" : "rapport"}>
      {state?.done && <p className="note" role="status">Ingelezen: {state.done.rows} rijen, {state.done.from} t/m {state.done.to}. De cijfers staan nu bij Overzicht.</p>}
      {state?.error && <div className="ui-callout" data-tone="danger" role="alert"><p>{state.error}</p></div>}
      {!p ? (
        <div className="grid-form">
          <label className="field"><span>Partner</span>
            <select name="partner" required defaultValue={state?.partner ?? ""}>
              <option value="" disabled>Kies een partner</option>
              {partners.map((x) => <option key={x.slug} value={x.slug}>{x.name}</option>)}
            </select></label>
          <div className="field wide"><span>Rapport</span>
            <div className="ui-upload"><div className="ui-upload-body">
              <label className="ui-btn">Kies bestand<input type="file" name="file" accept=".csv,text/csv,text/plain" required /></label>
              <small>CSV uit je partneraccount, hooguit 900 kB. Opnieuw inlezen voor dezelfde partner en periode vervangt de vorige cijfers.</small>
            </div></div></div>
          <div className="wide"><button className="ui-btn" data-variant="primary" type="submit" disabled={pending}>{pending ? "Bezig…" : "Bekijken"}</button></div>
        </div>
      ) : (
        <>
          <input type="hidden" name="partner" value={state!.partner} />
          <input type="hidden" name="fileName" value={state!.fileName} />
          <input type="hidden" name="csv" value={state!.csv} />
          <div className="grid-form">
            {FIELDS.map(([f, label, required]) => (
              <label key={f} className="field"><span>{label}</span>
                <select name={`map:${f}`} defaultValue={p.mapping[f] ?? ""} required={required}>
                  {!required && <option value="">Niet in dit bestand</option>}
                  {required && !p.mapping[f] && <option value="" disabled>Kies een kolom</option>}
                  {p.headers.map((h) => <option key={h} value={h}>{h}</option>)}
                </select></label>
            ))}
          </div>
          {p.problem ? <div className="ui-callout" data-tone="danger" role="alert"><p>{p.problem}</p></div> : (
            <p className="lead">{p.from} t/m {p.to} · {p.total} rijen{p.skipped ? ` (${p.skipped} overgeslagen, zoals totaalregels)` : ""} · {p.matchedProducts} met een bekend product, {p.matchedPlates} met een plaat.</p>
          )}
          {p.sample.length > 0 && (
            <div className="ui-table-wrap" tabIndex={0} role="region" aria-labelledby="si-cap">
              <table className="ui-table"><caption id="si-cap">Eerste rijen</caption>
                <thead><tr><th>Datum</th><th>Sub-ID</th><th>Product</th><th className="num">Aantal</th><th className="num">Omzet</th><th className="num">Commissie</th></tr></thead>
                <tbody>{p.sample.map((r, i) => (
                  <tr key={i}><td>{r.day}</td><td>{r.subId || "—"}</td><td>{r.product || "—"}</td><td className="num">{r.items}</td><td className="num">{money(r.revenueCents, r.currency)}</td><td className="num">{money(r.commissionCents, r.currency)}</td></tr>
                ))}</tbody></table>
            </div>
          )}
          <div className="checks">
            <button className="ui-btn" data-variant="primary" type="submit" name="intent" value="import" disabled={pending || !!p.problem}>{pending ? "Bezig…" : "Importeren"}</button>
            <button className="ui-btn" type="submit" name="intent" value="preview" disabled={pending}>Opnieuw bekijken</button>
            <a className="ui-btn" data-variant="quiet" href="/winkel/verkopen">Ander bestand</a>
          </div>
        </>
      )}
    </form>
  );
}
