"use client";
import { useActionState, useState } from "react";
import type { AmazonStore } from "@/lib/api";
import { amazonAdd, type AmazonState } from "../actions";

const LANGUAGE_NAMES: Record<string, string> = { de: "Duits", fr: "Frans", en: "Engels", es: "Spaans", it: "Italiaans", pl: "Pools", sv: "Zweeds" };
const COUNTRY_NAMES: Record<string, string> = { NL: "Nederland", BE: "België", DE: "Duitsland", AT: "Oostenrijk", CH: "Zwitserland", LU: "Luxemburg", FR: "Frankrijk", IT: "Italië", ES: "Spanje", PL: "Polen", SE: "Zweden", GB: "Verenigd Koninkrijk", IE: "Ierland" };

/** AmazonQuickAdd (DS, ADR 0031): één ASIN of link wordt een product per gekozen Amazon-winkel. */
export function AmazonQuickAdd({ stores, materials }: { stores: AmazonStore[]; materials: { slug: string; name: string }[] }) {
  const [state, action, pending] = useActionState<AmazonState, FormData>(amazonAdd, null);
  const v = state?.values;
  const [picked, setPicked] = useState<string[]>((v?.store as string[] | undefined) ?? ["amazon-nl"]);
  const languages = [...new Set(stores.filter((s) => picked.includes(s.partner)).flatMap((s) => s.markets.map((m) => m.slice(0, 2))))].filter((l) => l !== "nl");
  const countries = (s: AmazonStore) => [...new Set(s.markets.map((m) => COUNTRY_NAMES[m.slice(3)] ?? m.slice(3)))].join(", ");
  return (
    <form action={action} className="grid-form" key={state?.added ? JSON.stringify(state.added) : "amazon"}>
      {state?.error && <div className="err wide" role="alert"><p>{state.error}</p></div>}
      {state?.added && (
        <div className="note wide" role="status">
          <p>Toegevoegd voor {state.added.length} {state.added.length === 1 ? "winkel" : "winkels"}. Controleer of het product in elke winkel bestaat:</p>
          <ul>{state.added.map((a) => <li key={a.slug}><a href={a.url} target="_blank" rel="noopener noreferrer">{a.url}<span className="visually-hidden"> (opent in nieuw tabblad)</span></a></li>)}</ul>
        </div>
      )}
      <label className="field wide"><span>Amazon-link of ASIN</span>
        <input name="asin" required defaultValue={String(v?.asin ?? "")} placeholder="amazon.nl/dp/B0007OECNU, amzn.eu/d/… of B0007OECNU" />
        <small>Eén ASIN is meestal in elke Amazon-winkel hetzelfde product.</small>
      </label>
      <label className="field"><span>Naam (Nederlands)</span><input name="name" required minLength={2} maxLength={120} defaultValue={String(v?.name ?? "")} /></label>
      <label className="field"><span>Prijsindicatie</span><input name="priceHint" maxLength={40} placeholder="ca. € 5" defaultValue={String(v?.priceHint ?? "")} /><small>Mag leeg.</small></label>
      {languages.map((l) => (
        <label className="field" key={l}><span>Naam in het {LANGUAGE_NAMES[l] ?? l}</span>
          <input name={`name:${l}`} maxLength={120} defaultValue={String(v?.[`name:${l}`] ?? "")} /><small>Leeg: de Nederlandse naam.</small></label>
      ))}
      <fieldset className="field wide"><legend>Bij materialen</legend>
        <div className="checks">{materials.map((m) => (
          <label key={m.slug} className="ui-check"><input type="checkbox" name="material" value={m.slug} defaultChecked={(v?.material as string[] | undefined)?.includes(m.slug)} /> {m.name}</label>
        ))}</div>
      </fieldset>
      <fieldset className="field wide"><legend>Winkels en landen</legend>
        <div className="checks">{stores.map((s) => (
          <label key={s.partner} className="ui-check">
            <input type="checkbox" name="store" value={s.partner} checked={picked.includes(s.partner)}
              onChange={(e) => setPicked((p) => (e.target.checked ? [...p, s.partner] : p.filter((x) => x !== s.partner)))} />
            {" "}{countries(s)} · {s.name}{!s.enabled && <span className="ui-hint"> (partner staat nog uit)</span>}
          </label>
        ))}</div>
      </fieldset>
      <div className="wide"><button className="ui-btn" data-variant="primary" type="submit" aria-disabled={pending || undefined} disabled={pending}>
        {pending ? "Toevoegen…" : `Toevoegen voor ${picked.length} ${picked.length === 1 ? "winkel" : "winkels"}`}
      </button></div>
    </form>
  );
}
