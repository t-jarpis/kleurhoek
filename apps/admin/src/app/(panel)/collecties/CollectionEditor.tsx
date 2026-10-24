"use client";
import { useActionState, useMemo, useState } from "react";
import type { Collection, CollectionPlate } from "@/lib/api";
import { saveCollection, type CollectionState } from "./actions";

const LANGS = [["nl", "Nederlands"], ["de", "Duits"], ["en", "Engels"], ["fr", "Frans"], ["es", "Spaans"], ["it", "Italiaans"], ["pl", "Pools"]] as const;
const norm = (s: string) => s.toLocaleLowerCase("nl").normalize("NFD").replace(/\p{Diacritic}/gu, "");

/** Collectie bewerken (design system: CollectionEditor): namen per taal en platen zoeken en kiezen. */
export function CollectionEditor({ collection, plates, goals, canManage }: {
  collection: Collection | null; plates: CollectionPlate[]; goals: { slug: string; name: string }[]; canManage: boolean;
}) {
  const [state, action, pending] = useActionState<CollectionState, FormData>(saveCollection, { error: null });
  const [chosen, setChosen] = useState<string[]>(collection?.plates ?? []);
  const [q, setQ] = useState("");
  const [goal, setGoal] = useState("");
  const [onlyChosen, setOnlyChosen] = useState(false);
  const bySlug = useMemo(() => new Map(plates.map((p) => [p.slug, p])), [plates]);
  const query = norm(q.trim());
  const listed = (onlyChosen ? chosen.map((s) => bySlug.get(s)).filter((p): p is CollectionPlate => !!p) : plates)
    .filter((p) => (!goal || p.goals.includes(goal)) && (!query || norm(p.name).includes(query) || p.slug.includes(query) || norm(p.categoryName).includes(query)))
    .slice(0, 300);
  const toggle = (slug: string) => setChosen((c) => (c.includes(slug) ? c.filter((x) => x !== slug) : [...c, slug]));

  return (
    <form action={action} className="stack">
      <input type="hidden" name="plates" value={JSON.stringify(chosen)} />
      <fieldset disabled={!canManage || pending} className="stack" style={{ border: 0, padding: 0, margin: 0 }}>
        {state.error && <div className="ui-callout" data-tone="danger" role="alert"><p>{state.error}</p></div>}
        {collection ? <input type="hidden" name="slug" value={collection.slug} /> : (
          <label className="field"><span>Code</span><input name="slug" required pattern="[a-z0-9][a-z0-9\-]{0,62}[a-z0-9]" className="mono" spellCheck={false} autoComplete="off" placeholder="rekenen-groep-3" /><small>Kleine letters, cijfers en streepjes. Staat niet op de site.</small></label>
        )}
        <label className="field"><span>Naam (Nederlands)</span><input name="name-nl" required maxLength={80} defaultValue={collection?.names.nl ?? ""} /></label>
        <label className="field"><span>Omschrijving (Nederlands)</span><textarea name="description-nl" rows={2} maxLength={300} defaultValue={collection?.descriptions.nl ?? ""} /><small>Voor de beheerder van een school: waarvoor is deze collectie bedoeld?</small></label>
        <details>
          <summary>Andere talen</summary>
          <div className="stack">
            {LANGS.filter(([l]) => l !== "nl").map(([l, name]) => (
              <div key={l} className="grid-form">
                <label className="field"><span>Naam ({name})</span><input name={`name-${l}`} maxLength={80} defaultValue={collection?.names[l] ?? ""} lang={l} /></label>
                <label className="field"><span>Omschrijving ({name})</span><input name={`description-${l}`} maxLength={300} defaultValue={collection?.descriptions[l] ?? ""} lang={l} /></label>
              </div>
            ))}
          </div>
        </details>
        <fieldset className="field">
          <legend>Platen ({chosen.length} gekozen)</legend>
          <div className="toolbar">
            <label className="field"><span className="visually-hidden">Zoek een plaat</span><input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Zoek op naam, code of onderwerp" /></label>
            <label className="field"><span className="visually-hidden">Leerdoel</span>
              <select value={goal} onChange={(e) => setGoal(e.target.value)}><option value="">Alle leerdoelen</option>{goals.map((g) => <option key={g.slug} value={g.slug}>{g.name}</option>)}</select>
            </label>
            <label className="check"><input type="checkbox" checked={onlyChosen} onChange={(e) => setOnlyChosen(e.target.checked)} /> Alleen gekozen</label>
          </div>
          {listed.length === 0 ? <p className="lead">Geen platen gevonden.</p> : (
            <ul className="ui-offer-list">
              {listed.map((p) => {
                const on = chosen.includes(p.slug);
                return (
                  <li key={p.slug} className="ui-offer-row" {...(on ? {} : { "data-off": "" })}>
                    <span>{p.name}<small>{p.categoryName} · {p.kind} · <code>{p.slug}</code></small></span>
                    <button type="button" className="ui-switch" aria-pressed={on} onClick={() => toggle(p.slug)}>{on ? "In collectie" : "Niet in collectie"}<span className="visually-hidden">: {p.name}</span></button>
                  </li>
                );
              })}
            </ul>
          )}
          <small>Hooguit 300 platen tegelijk in beeld; zoek of filter om er meer te vinden. De volgorde is de volgorde van kiezen.</small>
        </fieldset>
        {canManage && <div><button type="submit" className="ui-btn" data-variant="primary">{pending ? "Opslaan…" : "Collectie opslaan"}</button></div>}
      </fieldset>
    </form>
  );
}
